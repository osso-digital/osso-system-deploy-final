# api/midias.py
import boto3
import os
from datetime import datetime

SPACES_KEY = os.getenv("DO_SPACES_KEY")
SPACES_SECRET = os.getenv("DO_SPACES_SECRET")
SPACES_REGION = os.getenv("DO_SPACES_REGION", "sfo2")
SPACES_BUCKET = os.getenv("DO_SPACES_BUCKET")

s3 = boto3.client(
    "s3",
    region_name=SPACES_REGION,
    endpoint_url=f"https://{SPACES_REGION}.digitaloceanspaces.com",
    aws_access_key_id=SPACES_KEY,
    aws_secret_access_key=SPACES_SECRET
)

def create_presigned_upload(filename, content_type="image/jpeg", expires_in=3600):
    key = f"uploads/{datetime.utcnow().strftime('%Y%m%d')}/{filename}"

    upload_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': SPACES_BUCKET,
            'Key': key,
            'ContentType': content_type
        },
        ExpiresIn=expires_in
    )

    public_url = f"https://{SPACES_BUCKET}.{SPACES_REGION}.digitaloceanspaces.com/{key}"

    return {
        "upload_url": upload_url,
        "public_url": public_url,
        "storage_key": key
    }
