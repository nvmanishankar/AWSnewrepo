from aws_cdk import (
    # ... existing imports
    aws_glue as glue,
)

# ... earlier code ...

# IAM Role for Glue already created as glue_role

glue_job = glue.CfnJob(
    self,
    "GlueETLJob",
    name="GlueETLJob-oOHNNIurJy4O",  # keep the same name or omit to let CDK name it
    role=glue_role.role_arn,
    glue_version="4.0",  # modern Glue (Spark 3.x, Python 3)
    command=glue.CfnJob.JobCommandProperty(
        name="glueetl",
        python_version="3",
        script_location=f"s3://{raw_bucket.bucket_name}/scripts/glue_job.py",
    ),
    default_arguments={
        "--job-language": "python",
        "--enable-metrics": "true",
        # optional: "--enable-continuous-cloudwatch-log": "true",
    },
    worker_type="G.1X",         # use workers instead of max_capacity
    number_of_workers=2,        # e.g. 2 DPUs
    execution_property=glue.CfnJob.ExecutionPropertyProperty(
        max_concurrent_runs=1
    ),
    max_retries=1,
    description="CSV to Parquet from raw/input to curated/output",
)
