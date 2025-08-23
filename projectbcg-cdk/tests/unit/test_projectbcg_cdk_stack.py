import aws_cdk as core
import aws_cdk.assertions as assertions

from projectbcg_cdk.projectbcg_cdk_stack import ProjectbcgCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in projectbcg_cdk/projectbcg_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ProjectbcgCdkStack(app, "projectbcg-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
