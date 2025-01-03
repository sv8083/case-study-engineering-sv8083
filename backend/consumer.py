import io
from kafka import KafkaConsumer
import boto3
import csv
from datetime import datetime
from models import create_engine, sessionmaker, get_session, Prices
from utils import download_s3_fileobj
# Kafka setup
consumer = KafkaConsumer(
    'pricing-topic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='pricing-group'
)

# S3 setup
s3_client = boto3.client('s3')


def process_csv_to_db(file_path, country_id):
    session = get_session(country_id)
    with open(file_path, 'ro') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            price_record = {
                "store_id": row["Store ID"],
                "sku": row["SKU"],
                "product_name": row["Product Name"],
                "price": float(row["Price"]),
                "date": row["Date"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            session.execute(Prices.insert().values(price_record))
        session.commit()
    session.close()

for message in consumer:
    msg = eval(message.value.decode('utf-8'))
    upload_id = msg["payload"]["upload_id"]
    country_id = msg["payload"]["country_id"]
    session = get_session(country_id)
    file_name = f"{upload_id}.csv"
    file_path = f"/tmp/{file_name}"
    # Download file from S3
    _file = io.BytesIO()
    download_s3_fileobj(_file, f"/{upload_id}/file.csv")
    _file.seek(0)
    # Process and insert into database
    process_csv_to_db(_file, country_id)
