import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Initialize Glue job
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Load data from S3
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": ["s3://your-bucket-name/raw/sales_data.csv"]},
    format="csv",
    format_options={"withHeader": True}
)

# Basic Transformation (Example: convert data types and remove nulls)
transformed = datasource.drop_null_fields()

# Optionally, rename columns or apply mappings
mapped = ApplyMapping.apply(frame=transformed, mappings=[
    ("order_id", "string", "order_id", "string"),
    ("product", "string", "product", "string"),
    ("category", "string", "category", "string"),
    ("amount", "string", "amount", "double"),
    ("region", "string", "region", "string"),
    ("order_date", "string", "order_date", "string")
])

# Write the transformed data back to S3 in Parquet format
output_path = "s3://your-bucket-name/processed/sales_data_parquet/"
glueContext.write_dynamic_frame.from_options(
    frame=mapped,
    connection_type="s3",
    connection_options={"path": output_path},
    format="parquet"
)

# Commit the job
job.commit()
