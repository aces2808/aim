from aws_cdk import (
    Stack,
    Tags,
    aws_ec2 as ec2,
    CfnOutput,
)
from constructs import Construct
from typing import Dict, Any, Optional
from . import config, get_project_env


class CapstoneVpc(Stack):
    """
    VPC Stack with Dependency Injection pattern.
    Configuration can be injected for better testability and flexibility.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_name: str = "epocket",
        stage: str = "dev",
        cfg: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dependency Injection: Use provided config or load default
        self.cfg = cfg if cfg is not None else config()

        # Initialize project variables from config helper
        self.project_env = get_project_env(project_name, stage)

        # ── Stack-level tags (propagate to every resource in this stack) ─────
        Tags.of(self).add("Project", project_name)
        Tags.of(self).add("Environment", stage)
        Tags.of(self).add("ManagedBy", "cdk")
        Tags.of(self).add("Stack", "privatenetwork")

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            f"{self.project_env}-vpc",  # Logical ID for CloudFormation
            vpc_name=f"{self.project_env}-vpc",  # Name tag for the VPC
            ip_addresses=ec2.IpAddresses.cidr(self.cfg["VPC"]["cidr_block"]),
            max_azs=self.cfg["VPC"]["max_azs"],
            # Create public subnets manually
            subnet_configuration=[],
            create_internet_gateway=False,
            nat_gateways=0,
        )

        # Create Internet Gateway and attach to VPC
        igw = ec2.CfnInternetGateway(self, f"{self.project_env}-igw", tags=[{"key": "Name", "value": f"{self.project_env}-igw"}])
        ec2.CfnVPCGatewayAttachment(self, f"{self.project_env}-vpc-igw-attachment", vpc_id=self.vpc.vpc_id, internet_gateway_id=igw.ref)

        # Create route table for public subnets
        public_route_table = ec2.CfnRouteTable(
            self,
            f"{self.project_env}-public-rt",
            vpc_id=self.vpc.vpc_id,
            tags=[{"key": "Name", "value": f"{self.project_env}-public-rt"}],
        )

        # Create route to Internet Gateway in the public route table
        ec2.CfnRoute(
            self,
            f"{self.project_env}-public-route",
            route_table_id=public_route_table.ref,
            destination_cidr_block=self.cfg["RouteTable"]["public_route_destination"],
            gateway_id=igw.ref,
        )

        # Create public subnets and associate them with the public route table
        pubsubnet1 = ec2.CfnSubnet(
            self,
            f"{self.project_env}-pubsubnet1",
            vpc_id=self.vpc.vpc_id,
            cidr_block=self.cfg["Subnets"]["pubsubnet1_cidr"],
            availability_zone=self.cfg["Subnets"]["pubsubnet1_az"],
            map_public_ip_on_launch=self.cfg["Subnets"]["map_public_ip_on_launch"],
            tags=[{"key": "Name", "value": f"{self.project_env}-pubsubnet1"}],
        )

        pubsubnet2 = ec2.CfnSubnet(
            self,
            f"{self.project_env}-pubsubnet2",
            vpc_id=self.vpc.vpc_id,
            cidr_block=self.cfg["Subnets"]["pubsubnet2_cidr"],
            availability_zone=self.cfg["Subnets"]["pubsubnet2_az"],
            map_public_ip_on_launch=self.cfg["Subnets"]["map_public_ip_on_launch"],
            tags=[{"key": "Name", "value": f"{self.project_env}-pubsubnet2"}],
        )

        ec2.CfnSubnetRouteTableAssociation(
            self,
            f"{self.project_env}-pubsubnet1-rt-assoc",
            subnet_id=pubsubnet1.ref,
            route_table_id=public_route_table.ref,
        )

        ec2.CfnSubnetRouteTableAssociation(
            self,
            f"{self.project_env}-pubsubnet2-rt-assoc",
            subnet_id=pubsubnet2.ref,
            route_table_id=public_route_table.ref,
        )

        # ── Private Subnets (no internet route — Fargate + RDS) ──────────────
        private_route_table = ec2.CfnRouteTable(
            self,
            f"{self.project_env}-private-rt",
            vpc_id=self.vpc.vpc_id,
            tags=[{"key": "Name", "value": f"{self.project_env}-private-rt"}],
        )

        privsubnet1 = ec2.CfnSubnet(
            self,
            f"{self.project_env}-privsubnet1",
            vpc_id=self.vpc.vpc_id,
            cidr_block=self.cfg["Subnets"]["privsubnet1_cidr"],
            availability_zone=self.cfg["Subnets"]["privsubnet1_az"],
            map_public_ip_on_launch=False,
            tags=[{"key": "Name", "value": f"{self.project_env}-privsubnet1"}],
        )

        privsubnet2 = ec2.CfnSubnet(
            self,
            f"{self.project_env}-privsubnet2",
            vpc_id=self.vpc.vpc_id,
            cidr_block=self.cfg["Subnets"]["privsubnet2_cidr"],
            availability_zone=self.cfg["Subnets"]["privsubnet2_az"],
            map_public_ip_on_launch=False,
            tags=[{"key": "Name", "value": f"{self.project_env}-privsubnet2"}],
        )

        ec2.CfnSubnetRouteTableAssociation(
            self,
            f"{self.project_env}-privsubnet1-rt-assoc",
            subnet_id=privsubnet1.ref,
            route_table_id=private_route_table.ref,
        )

        ec2.CfnSubnetRouteTableAssociation(
            self,
            f"{self.project_env}-privsubnet2-rt-assoc",
            subnet_id=privsubnet2.ref,
            route_table_id=private_route_table.ref,
        )

        # ── VPC Endpoint Security Group ───────────────────────────────────────
        # Shared SG for all interface endpoints — Fargate tasks must have outbound
        # 443 to this SG to reach ECR, Secrets Manager, CloudWatch, and ECS APIs.
        endpoint_sg = ec2.CfnSecurityGroup(
            self,
            f"{self.project_env}-endpoint-sg",
            group_description="Allow HTTPS from private subnets to VPC Interface Endpoints",
            vpc_id=self.vpc.vpc_id,
            security_group_ingress=[
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    from_port=443,
                    to_port=443,
                    cidr_ip=self.cfg["Subnets"]["privsubnet1_cidr"],
                    description="HTTPS from private subnet 1",
                ),
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    from_port=443,
                    to_port=443,
                    cidr_ip=self.cfg["Subnets"]["privsubnet2_cidr"],
                    description="HTTPS from private subnet 2",
                ),
            ],
            tags=[{"key": "Name", "value": f"{self.project_env}-endpoint-sg"}],
        )

        # ── VPC Gateway Endpoint: S3 (free, needed for ECR image layer pulls) ─
        ec2.CfnVPCEndpoint(
            self,
            f"{self.project_env}-s3-endpoint",
            vpc_id=self.vpc.vpc_id,
            service_name=f"com.amazonaws.{self.region}.s3",
            vpc_endpoint_type="Gateway",
            route_table_ids=[private_route_table.ref],
        )

        # ── VPC Interface Endpoints (replaces NAT Gateway for PoC cost saving) ─
        interface_endpoint_services = [
            ("ecr-api", f"com.amazonaws.{self.region}.ecr.api"),
            ("ecr-dkr", f"com.amazonaws.{self.region}.ecr.dkr"),
            ("secretsmanager", f"com.amazonaws.{self.region}.secretsmanager"),
            ("logs", f"com.amazonaws.{self.region}.logs"),
            ("ecs", f"com.amazonaws.{self.region}.ecs"),
            ("ecs-agent", f"com.amazonaws.{self.region}.ecs-agent"),
            ("ecs-telemetry", f"com.amazonaws.{self.region}.ecs-telemetry"),
        ]

        for short_name, service_name in interface_endpoint_services:
            ec2.CfnVPCEndpoint(
                self,
                f"{self.project_env}-{short_name}-endpoint",
                vpc_id=self.vpc.vpc_id,
                service_name=service_name,
                vpc_endpoint_type="Interface",
                subnet_ids=[privsubnet1.ref, privsubnet2.ref],
                security_group_ids=[endpoint_sg.ref],
                private_dns_enabled=True,
            )

        # ── Outputs ───────────────────────────────────────────────────────────

        CfnOutput(
            self,
            self.cfg["Outputs"]["vpc_id_output_id"],
            value=self.vpc.vpc_id,
            description=self.cfg["Outputs"]["vpc_id_description"],
            export_name=f"{project_name}-{stage}:{self.project_env}-vpc",
        )

        CfnOutput(
            self,
            self.cfg["Outputs"]["pubsubnet1_id_output_id"],
            value=pubsubnet1.ref,
            description=self.cfg["Outputs"]["pubsubnet1_id_description"],
            export_name=f"{project_name}-{stage}:{self.project_env}-pubsubnet1",
        )

        CfnOutput(
            self,
            "PublicSubnet1Az",
            value=pubsubnet1.attr_availability_zone,
            description="Public Subnet 1 Availability Zone",
            export_name=f"{project_name}-{stage}:{self.project_env}-pubsubnet1-az",
        )

        CfnOutput(
            self,
            self.cfg["Outputs"]["pubsubnet2_id_output_id"],
            value=pubsubnet2.ref,
            description=self.cfg["Outputs"]["pubsubnet2_id_description"],
            export_name=f"{project_name}-{stage}:{self.project_env}-pubsubnet2",
        )

        CfnOutput(
            self,
            "PublicSubnet2Az",
            value=pubsubnet2.attr_availability_zone,
            description="Public Subnet 2 Availability Zone",
            export_name=f"{project_name}-{stage}:{self.project_env}-pubsubnet2-az",
        )

        CfnOutput(
            self,
            self.cfg["Outputs"]["privsubnet1_id_output_id"],
            value=privsubnet1.ref,
            description=self.cfg["Outputs"]["privsubnet1_id_description"],
            export_name=f"{project_name}-{stage}:{self.project_env}-privsubnet1",
        )

        CfnOutput(
            self,
            self.cfg["Outputs"]["privsubnet2_id_output_id"],
            value=privsubnet2.ref,
            description=self.cfg["Outputs"]["privsubnet2_id_description"],
            export_name=f"{project_name}-{stage}:{self.project_env}-privsubnet2",
        )

        CfnOutput(
            self,
            self.cfg["Outputs"]["endpoint_sg_output_id"],
            value=endpoint_sg.ref,
            description=self.cfg["Outputs"]["endpoint_sg_description"],
            export_name=f"{project_name}-{stage}:{self.project_env}-endpoint-sg",
        )
