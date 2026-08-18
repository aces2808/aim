from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    Tags,
)
from constructs import Construct
from typing import Dict, Any, Optional
from . import config, get_project_env

class CapstoneWebApp(Stack):
    """
    Static Website Stack with Dependency Injection pattern.
    Configuration can be injected for better testability and flexibility.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_name: str = "agriyard",
        stage: str = "dev",
        cfg: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dependency Injection: Use provided config or load default
        self.cfg = cfg if cfg is not None else config()

        # Initialize project variables from config helper
        self.project_env = get_project_env(project_name, stage)

        # S3 Bucket for static website hosting
        website_bucket = s3.Bucket(
            self,
            f"{self.project_env}-website-bucket",
            bucket_name=f"{self.project_env}-website-bucket",
            # Security: Allow CloudFront OAC access
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                ignore_public_acls=True,
                block_public_policy=False,  # Allow bucket policy for OAC
                restrict_public_buckets=False,  # Allow bucket policy for OAC
            ),
            # Bucket management - configured for complete destruction
            removal_policy=RemovalPolicy.DESTROY,  # Allow bucket to be destroyed
            auto_delete_objects=True,  # Automatically delete all objects before destroying bucket
        )

        # Add tags to S3 bucket
        Tags.of(website_bucket).add("Name", f"{self.project_env}-website-bucket")

        # CloudFront Origin Access Control (OAC) - Modern replacement for OAI
        origin_access_control = cloudfront.CfnOriginAccessControl(
            self,
            "OriginAccessControl",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                description=self.cfg["CloudFront"]["oac_description"],
                name=f"{self.project_env}-oac",
                origin_access_control_origin_type="s3",
                signing_behavior="always",
                signing_protocol="sigv4",
            ),
        )

        # Ensure OAC can be destroyed
        origin_access_control.apply_removal_policy(RemovalPolicy.DESTROY)

        # CloudFront Distribution
        distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(bucket=website_bucket, origin_id=f"{self.project_env}-origin"),
                # Security: Redirect HTTP to HTTPS
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                # Caching: Use CloudFront's managed caching policy optimized for SPA
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED_FOR_UNCOMPRESSED_OBJECTS,
                # Compression
                compress=True,
                # Allow common HTTP methods
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
            ),
            # Default document for root requests
            default_root_object=self.cfg["S3"]["default_root_object"],
            # Error handling for Single Page Applications (SPA)
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path=self.cfg["S3"]["error_page_path"],
                    ttl=Duration.minutes(self.cfg["Timeouts"]["error_response_ttl_minutes"]),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path=self.cfg["S3"]["error_page_path"],
                    ttl=Duration.minutes(self.cfg["Timeouts"]["error_response_ttl_minutes"]),
                ),
            ],
            # Additional settings
            enable_ipv6=True,
            price_class=getattr(cloudfront.PriceClass, self.cfg["CloudFront"]["price_class"]),
            comment=self.cfg["CloudFront"]["comment"],
        )

        # Ensure CloudFront distribution can be destroyed and configure OAC
        cfn_distribution = distribution.node.default_child
        cfn_distribution.apply_removal_policy(RemovalPolicy.DESTROY)
        cfn_distribution.add_property_override("DistributionConfig.Origins.0.OriginAccessControlId", origin_access_control.get_att("Id"))

        # Add tags to CloudFront distribution
        Tags.of(distribution).add("Name", f"{self.project_env}-cloudfront-distribution")

        # Update the bucket policy with the actual distribution ARN
        bucket_policy_updated = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    sid=f"{self.project_env}-cloudfront-policy",
                    effect=iam.Effect.ALLOW,
                    principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                    actions=[self.cfg["IAM"]["policy_action"]],
                    resources=[f"{website_bucket.bucket_arn}/*"],
                    conditions={"StringEquals": {"AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"}},
                )
            ]
        )

        # Apply the updated bucket policy
        bucket_policy = s3.CfnBucketPolicy(
            self, "WebsiteBucketPolicy", bucket=website_bucket.bucket_name, policy_document=bucket_policy_updated.to_json()
        )

        # Ensure bucket policy can be destroyed
        bucket_policy.apply_removal_policy(RemovalPolicy.DESTROY)

        # Outputs for easy reference
        CfnOutput(self, "BucketName", value=website_bucket.bucket_name, description=self.cfg["Outputs"]["bucket_name_description"])
        CfnOutput(self, "DistributionId", value=distribution.distribution_id, description=self.cfg["Outputs"]["distribution_id_description"])
        CfnOutput(
            self,
            "DistributionDomainName",
            value=distribution.distribution_domain_name,
            description=self.cfg["Outputs"]["distribution_domain_description"],
        )
        CfnOutput(
            self, "WebsiteURL", value=f"https://{distribution.distribution_domain_name}", description=self.cfg["Outputs"]["website_url_description"]
        )
