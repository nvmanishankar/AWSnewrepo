import sys
from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession

args = getResolvedOptions(sys.argv, ["RAW_BUCKET", "CURATED_BUCKET"])
RAW_BUCKET = args["RAW_BUCKET"]
CURATED_BUCKET = args["CURATED_BUCKET"]

# Optional (when triggered via Lambda)
INPUT_KEY = None
if "--INPUT_KEY" in sys.argv:
    idx = sys.argv.index("--INPUT_KEY") + 1
    if idx < len(sys.argv):
        INPUT_KEY = sys.argv[idx]

spark = SparkSession.builder.getOrCreate()

if INPUT_KEY:
    input_path = f"s3://{RAW_BUCKET}/{INPUT_KEY}"
else:
    input_path = f"s3://{RAW_BUCKET}/input/"

output_path = f"s3://{CURATED_BUCKET}/output/"

print(f"Reading CSV from: {input_path}")
df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(input_path)
)

print(f"Writing Parquet to: {output_path}")
(
    df.coalesce(1)
    .write.mode("overwrite")
    .parquet(output_path)
)

print("Done.")
