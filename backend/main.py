from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from utils import generate_s3_presigned_url
from models import Prices, get_session
from pydantic import BaseModel
from typing import Optional, List

from settings import settings, app_logger
import redis
import uuid

from datetime import date, datetime
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# FastAPI app
app = FastAPI()
try:
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
except NoBrokersAvailable:
    app_logger.critical("Workers not available")

# Redis setup for tracking uploads
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Pydatnic Models for requests
class PricingUpdate(BaseModel):
    store_id: Optional[str] = None
    sku: Optional[str] = None
    product_name: Optional[str] = None
    price: Optional[float] = None
    date: Optional[str] = None




@app.post("/upload-request")
def upload_request(
    country_id: str = Query('IN'),
):
    upload_id = str(uuid.uuid4())
    presigned_url = generate_s3_presigned_url(f"/{upload_id}/file.csv")
    redis_client.set(upload_id, f"{country_id}", ex=3600)
    return {"upload_id": upload_id, "presigned_url": presigned_url}


@app.post("/confirm")
def confirm_upload(upload_id: str = Query(...)):
    country_id = redis_client.get(upload_id)
    message = {
        "id": "1712-01-0004",
        "spec_version": "1.0",
        "type": "com.file.process",
        "retries": 0,
        "source_time": "2024-12-17T17:31:00Z",
        "content_type": "application/json",
        "traceparent": "trace-123",
        "payload": {
                "upload_id": upload_id, "country_id": country_id}
        }
    if country_id:
        redis_client.delete(upload_id)
        producer.send('pricing-topic', value=str(message).encode('utf-8'))
        return {"message": "Upload confirmed"}
    else:
        raise HTTPException(status_code=404, detail="Invalid or expired upload_id")


@app.get("/pricing-feeds")
def get_pricing_feeds(
    store_id: str = Query(None),
    sku: str = Query(None),
    name: str = Query(None),
    price: float = Query(None),
    country_id: str = Query('IN'),
):
    session = get_session(country_id)
    try:
        query = session.filter(Prices)
        if store_id:
            query = query.filter(Prices.store_id == store_id)
        if sku:
            query = query.filter(Prices.sku == sku)
        if name:
            query = query.filter(Prices.product_name.ilike(f"%{name}%"))
        if price is not None:
            query = query.filter(Prices.price == price)

        results = session.execute(query).scalars().all()
        return results
    finally:
        session.close()


@app.get("/pricing-feeds/{price_id}")
def get_price_detail(price_id: int, country_id: str = Query('IN')):
    session = get_session(country_id)
    try:
        query = session.query(Prices).filter(Prices.id == price_id)
        result = session.execute(query).scalar_one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="Price record not found")
        return result
    finally:
        session.close()


@app.patch("/pricing-feeds/{price_id}")
def update_pricing(price_id: int, payload: PricingUpdate, country_id: str = Query('IN')):
    session = get_session(country_id)
    try:
        query = session.query(Prices).where(Prices.id == price_id).update(**payload.dict(exclude_unset=True))
        session.execute(query)
        session.commit()
        return {"message": "Record updated successfully"}
    except Exception:
        raise HTTPException(status_code=404, detail="Price record not found")
    finally:
        session.close()
