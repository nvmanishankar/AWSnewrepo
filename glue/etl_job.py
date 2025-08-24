import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from raw S3
datasource = glueContext.create_dynamic_frame.from_options(
    "s3",
    {"paths": ["s3://your-raw-bucket/"]},
    format="json"
)

# Transform
applymapping = ApplyMapping.apply(frame=datasource, mappings=[("field1","string","field1","string")])

# Write to curated bucket
glueContext.write_dynamic_frame.from_options(
    frame=applymapping,
    connection_type="s3",
    connection_options={"path": "s3://your-curated-bucket/"},
    format="parquet"
)

job.commit()
