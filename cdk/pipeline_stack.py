from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
from constructs import Construct

class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Raw S3 bucket
        raw_bucket = s3.Bucket(self, "RawBucket")

        # Curated S3 bucket
        curated_bucket = s3.Bucket(self, "CuratedBucket")

        # Lambda for file operations
        file_lambda = _lambda.Function(
            self, "FileOpsLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="app.lambda_handler",
            code=_lambda.Code.from_asset("lambda/s3_file_task")

        )

        # Permissions to access S3
        raw_bucket.grant_read_write(file_lambda)
        curated_bucket.grant_read_write(file_lambda)

        # EventBridge rule for new object in raw bucket
        rule = events.Rule(
            self, "S3UploadRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["AWS API Call via CloudTrail"],
                detail={
                    "eventSource": ["s3.amazonaws.com"],
                    "eventName": ["PutObject"]
        }
    )
)
        rule.add_target(targets.LambdaFunction(file_lambda))

        rule.add_target(targets.LambdaFunction(file_lambda))

        # Step Function for orchestration (simple example)
        step_lambda_task = tasks.LambdaInvoke(
            self, "LambdaTask",
            lambda_function=file_lambda,
            output_path="$.Payload"
        )

        definition = step_lambda_task

        sfn.StateMachine(
            self, "PipelineStateMachine",
            definition=definition
        )
