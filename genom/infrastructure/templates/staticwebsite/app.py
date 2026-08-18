#!/usr/bin/env python3
import os

import aws_cdk as cdk

from staticwebsite.capstone_webapp import CapstoneWebApp
from staticwebsite import config, get_project_env


app = cdk.App()

# Load configuration
cfg = config()

# Get project environment from config
project_name = cfg.get("DEFAULT", {}).get("project_name", "agriyard")
environment = cfg.get("DEFAULT", {}).get("environment", "dev")
project_env = get_project_env(project_name, environment)

CapstoneWebApp(
    app,
    f"{project_env}-static-website",
    project_name=project_name,
    stage=environment,
    cfg=cfg,  # Inject configuration
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    # env=cdk.Environment(account='123456789012', region='us-east-1'),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

app.synth()
