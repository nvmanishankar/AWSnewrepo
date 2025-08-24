from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_s3 as s3,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
    aws_glue as glue,
    aws_s3_deployment as s3deploy,
)
from constructs import Construct


class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ------------------------------------------------------------------
        # Buckets (keep WITHOUT explicit names to avoid replacement errors)
        # ------------------------------------------------------------------
        raw_bucket = s3.Bucket(self, "RawBucket")
        curated_bucket = s3.Bucket(self, "CuratedBucket")

        # ------------------------------------------------------------------
        # Upload the Glue script to RAW bucket under scripts/
        # Local file: glue/etl_job.py  ->  s3://raw/scripts/etl_job.py
        # ------------------------------------------------------------------
        s3deploy.BucketDeployment(
            self,
            "DeployGlueScript",
            destination_bucket=raw_bucket,
            destination_key_prefix="scripts",
            sources=[s3deploy.Source.asset("glue")],  # deploys whole folder
        )

        # ------------------------------------------------------------------
        # Glue role & policy
        # ------------------------------------------------------------------
        glue_role = iam.Role(
            self,
            "GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
            ],
        )
        # S3 permissions for Glue
        raw_bucket.grant_read(glue_role)
        curated_bucket.grant_read_write(glue_role)

        # ------------------------------------------------------------------
        # Glue Job (named exactly "GlueETLJob")
        # ------------------------------------------------------------------
        glue_job = glue.CfnJob(
            self,
            "GlueETLJob",
            name="GlueETLJob",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                python_version="3",
                script_location=f"s3://{raw_bucket.bucket_name}/scripts/etl_job.py",
            ),
            default_arguments={
                "--job-language": "python",
                "--RAW_BUCKET": raw_bucket.bucket_name,
                "--CURATED_BUCKET": curated_bucket.bucket_name,
                "--TempDir": f"s3://{raw_bucket.bucket_name}/tmp/",
            },
            glue_version="4.0",
            worker_type="G.1X",
            number_of_workers=2,
            max_retries=1,
        )

        # ------------------------------------------------------------------
        # Lambda role & permissions
        # ------------------------------------------------------------------
        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            ],
        )
        raw_bucket.grant_read(lambda_role)
        curated_bucket.grant_read_write(lambda_role)
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["glue:StartJobRun"],
                resources=["*"],  # you can tighten to the specific job ARN later
            )
        )

        # ------------------------------------------------------------------
        # Lambda function (triggered by S3 put under input/)
        # ------------------------------------------------------------------
        lambda_fn = _lambda.Function(
            self,
            "TriggerGlueLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="app.lambda_handler",
            code=_lambda.Code.from_asset("lambda/s3_file_task"),
            role=lambda_role,
            environment={
                "GLUE_JOB_NAME": "GlueETLJob",
                "RAW_BUCKET": raw_bucket.bucket_name,
                "CURATED_BUCKET": curated_bucket.bucket_name,
            },
            timeout=Duration.seconds(60),
        )
        # make sure Glue Job is created before Lambda may try to call it
        lambda_fn.node.add_dependency(glue_job)

        # S3 -> Lambda notification for uploads under input/
        raw_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT,
            s3n.LambdaDestination(lambda_fn),
            s3.NotificationKeyFilter(prefix="input/"),
        )

        # Outputs
        CfnOutput(self, "RawBucketName", value=raw_bucket.bucket_name)
        CfnOutput(self, "CuratedBucketName", value=curated_bucket.bucket_name)
        CfnOutput(self, "LambdaName", value=lambda_fn.function_name)
