import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Glue boilerplate
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Read data from curated bucket
input_path = "s3://<YOUR-CURATED-BUCKET>/"
df = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [input_path]},
    format="json"
)

# Transform (basic example: drop nulls)
df_clean = DropNullFields.apply(frame=df)

# Write output
output_path = "s3://<YOUR-CURATED-BUCKET>/processed/"
glueContext.write_dynamic_frame.from_options(
    frame=df_clean,
    connection_type="s3",
    connection_options={"path": output_path},
    format="parquet"
)

job.commit()
