from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from settings import settings

Base = declarative_base()
# SQLite database setup
engine_us = create_engine(settings.DATABASE_URL_US)
engine_india = create_engine(settings.DATABASE_URL_INDIA)

# Create tables if not exist
Base.metadata.create_all(bind=engine_us)
Base.metadata.create_all(bind=engine_india)

SessionLocalUS = sessionmaker(autocommit=False, autoflush=False, bind=engine_us)
SessionLocalIndia = sessionmaker(autocommit=False, autoflush=False, bind=engine_india)

# Utility function to get the correct session based on country
def get_session(country_id: str) -> Session:
    if country_id == "US":
        return SessionLocalUS()
    elif country_id == "IN":
        return SessionLocalIndia()
    else:
        raise Exception("Invalid country_id")

class Prices(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), nullable=False)
    sku = Column(String(50), nullable=False)
    product_name = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
