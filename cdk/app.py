from aws_cdk import core as cdk
from my_project.my_stack import MyStack

app = cdk.App()

MyStack(app, "MyStack",
    env=cdk.Environment(
        account="681090449810",
        region="eu-north-1"
    )
)

app.synth()
