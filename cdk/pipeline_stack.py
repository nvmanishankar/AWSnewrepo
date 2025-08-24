from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_glue as glue,
    aws_s3_notifications as s3n,
    CfnOutput
)
from constructs import Construct


class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Buckets
        raw_bucket = s3.Bucket(self, "RawBucket",
                               versioned=True,
                               removal_policy=None)

        curated_bucket = s3.Bucket(self, "CuratedBucket",
                                   versioned=True,
                                   removal_policy=None)

        # Lambda Function
        lambda_fn = _lambda.Function(
            self, "MoveRawToCuratedLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda")
        )

        # Permissions
        raw_bucket.grant_read(lambda_fn)
        curated_bucket.grant_write(lambda_fn)

        # Event: Trigger Lambda when object is uploaded to Raw bucket
        notification = s3n.LambdaDestination(lambda_fn)
        raw_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)

        # IAM Role for Glue
        glue_role = iam.Role(
            self, "GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ]
        )
        raw_bucket.grant_read(glue_role)
        curated_bucket.grant_read_write(glue_role)

        # Glue Job
        glue_job = glue.CfnJob(
            self, "GlueETLJob",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                python_version="3",
                script_location=f"s3://{raw_bucket.bucket_name}/scripts/glue_job.py"
            ),
            default_arguments={
                "--TempDir": f"s3://{raw_bucket.bucket_name}/tmp/"
            },
            max_retries=1,
            max_capacity=2
        )

        # Outputs
        CfnOutput(self, "RawBucketName", value=raw_bucket.bucket_name)
        CfnOutput(self, "CuratedBucketName", value=curated_bucket.bucket_name)
        CfnOutput(self, "LambdaFunctionName", value=lambda_fn.function_name)
        CfnOutput(self, "GlueJobName", value=glue_job.ref)
