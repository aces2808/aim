import aws_cdk as core
import aws_cdk.assertions as assertions

from infrastructure.templates.privatenetwork.privatenetwork.capstone_vpc import PrivatenetworkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in privatenetwork/privatenetwork_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PrivatenetworkStack(app, "privatenetwork")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
