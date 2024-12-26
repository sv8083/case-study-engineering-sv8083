import io
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

def download_s3_fileobj(s3_file, s3_url):
    _s3 = get_s3_client()
    _s3.download_fileobj(settings.S3_BUCKET, s3_url, s3_file)
    return s3_file


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
