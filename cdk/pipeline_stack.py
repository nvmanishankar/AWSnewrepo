from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_glue as glue,
)
from constructs import Construct

class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Buckets
        raw_bucket = s3.Bucket(self, "RawBucket")
        curated_bucket = s3.Bucket(self, "CuratedBucket")

        # IAM Role for Lambda
        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ],
        )

        # Lambda Function
        lambda_fn = _lambda.Function(
            self,
            "MoveFileLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            role=lambda_role,
            environment={
                "CURATED_BUCKET": curated_bucket.bucket_name,
            },
        )

        # EventBridge Rule to trigger Lambda on S3 Object Create
        rule = events.Rule(
            self,
            "S3EventRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["AWS API Call via CloudTrail"],
                detail={"eventName": ["PutObject"], "requestParameters": {"bucketName": [raw_bucket.bucket_name]}},
            ),
        )
        rule.add_target(targets.LambdaFunction(lambda_fn))

        # IAM Role for Glue
        glue_role = iam.Role(
            self,
            "GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ],
        )

        # Glue Job
        glue_job = glue.CfnJob(
            self,
            "GlueETLJob",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                python_version="3",
                script_location=f"s3://{raw_bucket.bucket_name}/scripts/glue_job.py",
            ),
            default_arguments={
                "--TempDir": f"s3://{raw_bucket.bucket_name}/tmp/",
                "--job-language": "python",
            },
            max_retries=1,
            max_capacity=2,
        )
