#!/usr/bin/env python3
from aws_cdk import App
from cdk.pipeline_stack import PipelineStack  # import stack from /cdk folder

app = App()
PipelineStack(app, "PipelineStack")
app.synth()
