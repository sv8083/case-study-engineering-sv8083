from decouple import config
import os
from loguru import logger as app_logger
from pydantic import HttpUrl
from pydantic_settings import BaseSettings

from concurrent.futures import ThreadPoolExecutor
import pkg_resources

class Settings(BaseSettings):
    VERSION: str = "o.0.o"
    # Directory settings
    LOG_DIR: str = './logs'
    BASE_DIR: str = os.path.dirname(os.path.dirname(__file__))
    # S3 + KMS settings
    S3_IP_UPLOAD_PATH: str = config("S3_IP_UPLOAD_PATH")
    S3_BUCKET: str = config("S3_BUCKET_NAME")
    S3_REGION: str = config("S3_REGION")
    S3_ACCESS_KEY: str = config("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = config("S3_SECRET_KEY")

    #
    GENERAL_HTTP_400: dict = {
        401: {
            "content": {
                "application/json": {"example": {"detail": "Not Authenticated"}}
            }
        },
        403: {
            "content": {"application/json": {"example": {"detail": "Not Authorized"}}}
        },
        404: {"content": {"application/json": {"example": {"detail": "Not Found"}}}},
        405: {
            "content": {"application/json": {"example": {"detail": "Method not allowed"}}}
        },
    }
    LOG_FORMAT: str = "{time: YYYY-MM-DD HH:mm:ss.SSS} |  | {level} | {function} | {message}"
    DATABASE_URL_US: str = "sqlite:///./us_prices.db"
    DATABASE_URL_INDIA: str = "sqlite:///./india_prices.db"
    #
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        case_sensitive = True


settings = Settings()

app_logger.configure(
    handlers=[
        {
            "sink": os.path.join(settings.LOG_DIR, f"application.log"),
            "level": "DEBUG",
            "colorize": False,
            "format": settings.LOG_FORMAT,
            "rotation": "00:00",
            "compression": "zip",
        },
        {
            "sink": os.path.join(settings.LOG_DIR, f"trace.log"),
            "level": "TRACE",
            "colorize": False,
            "format": settings.LOG_FORMAT,
            "rotation": "10MB",
            "compression": "zip",
        },
    ]
)