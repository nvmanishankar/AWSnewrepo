import os
import json
import boto3

glue = boto3.client("glue")

GLUE_JOB_NAME = os.environ["GLUE_JOB_NAME"]
RAW_BUCKET = os.environ["RAW_BUCKET"]
CURATED_BUCKET = os.environ["CURATED_BUCKET"]


def lambda_handler(event, context):
    # Expecting S3 Put event (from S3 notification)
    print("Event:", json.dumps(event))

    records = event.get("Records", [])
    if not records:
        return {"status": "ignored", "reason": "no S3 records"}

    rec = records[0]
    bucket = rec["s3"]["bucket"]["name"]
    key = rec["s3"]["object"]["key"]

    if not key.startswith("input/"):
        print(f"Skipping key (no input/): {key}")
        return {"status": "skipped", "key": key}

    args = {
        "--RAW_BUCKET": RAW_BUCKET,
        "--CURATED_BUCKET": CURATED_BUCKET,
        "--INPUT_KEY": key,  # process just this file
    }
    print(f"Starting Glue job: {GLUE_JOB_NAME} with args: {args}")

    response = glue.start_job_run(JobName=GLUE_JOB_NAME, Arguments=args)
    run_id = response["JobRunId"]
    print(f"Started Glue job run: {run_id}")

    return {"status": "started", "glueRunId": run_id, "key": key}
