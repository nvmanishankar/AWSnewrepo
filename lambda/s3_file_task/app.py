import boto3
import os

s3 = boto3.client("s3")
curated_bucket = os.environ["CURATED_BUCKET"]

def lambda_handler(event, context):
    print("Event:", event)

    bucket_name = event["detail"]["requestParameters"]["bucketName"]
    key = event["detail"]["requestParameters"]["key"]

    # Move file Raw → Curated
    copy_source = {"Bucket": bucket_name, "Key": key}
    s3.copy_object(Bucket=curated_bucket, Key=key, CopySource=copy_source)
    s3.delete_object(Bucket=bucket_name, Key=key)

    return {"status": "success", "file": key}
