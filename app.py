#!/usr/bin/env python3
import aws_cdk as cdk
from cdk.pipeline_stack import PipelineStack


app = cdk.App()

PipelineStack(
    app,
    "PipelineStack",
    env=cdk.Environment(
        account="681090449810",
        region="eu-north-1"
    ),
)

app.synth()
