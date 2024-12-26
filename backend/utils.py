import boto3
from botocore.client import Config
from settings import settings

def get_s3_client(client = False):
    """
    ... Returns S3 client with system credentials
    """
    return boto3.client(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4"),
    )

def generate_s3_path(*args) -> str:
    """Generate full URL from list of arguments, starting from base s3 URL

    Returns:
        (str): S3 URL
    """
    return settings.S3_UPLOAD_PATH.strip("/") + "".join(f"/{str(x)}" for x in args)

def generate_s3_presigned_url(
    s3_path: str,
):
    s3_client = get_s3_client()
    _url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': 'pricing-feeds', 'Key': s3_path},
        ExpiresIn=3600
    )
    return _url
