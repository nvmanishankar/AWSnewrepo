import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Check if file exists
    try:
        s3.head_object(Bucket=bucket_name, Key=key)
        return {"status": "error", "message": "File already exists"}
    except:
        # File doesn't exist → create dummy file or process
        s3.put_object(Bucket=bucket_name, Key="new_file.txt", Body=b"Hello World!")

    # Move example: copy then delete
    copy_source = {'Bucket': bucket_name, 'Key': key}
    s3.copy_object(Bucket=bucket_name, Key="moved/"+key, CopySource=copy_source)
    s3.delete_object(Bucket=bucket_name, Key=key)

    return {"status": "success"}
