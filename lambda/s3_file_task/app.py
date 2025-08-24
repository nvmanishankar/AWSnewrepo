import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Event:", event)
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    target_bucket = os.environ.get('CURATED_BUCKET')

    if not target_bucket:
        target_bucket = source_bucket.replace("raw", "curated")

    copy_source = {'Bucket': source_bucket, 'Key': file_key}

    s3.copy_object(CopySource=copy_source, Bucket=target_bucket, Key=file_key)
    print(f"File {file_key} moved from {source_bucket} → {target_bucket}")

    return {"status": "success", "file": file_key}
