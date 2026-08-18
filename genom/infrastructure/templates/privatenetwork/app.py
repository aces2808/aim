#!/usr/bin/env python3
import os

import aws_cdk as cdk

from privatenetwork.capstone_vpc import CapstoneVpc
from privatenetwork import config, get_project_env


app = cdk.App()

# Load configuration
cfg = config()

# Get project environment from config
project_name = cfg.get("DEFAULT", {}).get("project_name", "epocket")
environment = cfg.get("DEFAULT", {}).get("environment", "dev")
project_env = get_project_env(project_name, environment)

CapstoneVpc(
    app,
    f"{project_env}-vpc",
    project_name=project_name,
    stage=environment,
    cfg=cfg,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
