import boto3

from app.core.config import get_settings


class AWSClientFactory:
    def __init__(self) -> None:
        self.settings = get_settings()

    def client(self, service_name: str, region_name: str | None = None):
        return boto3.client(service_name, region_name=region_name or self.settings.aws_region)


class AWSOperations:
    def __init__(self, factory: AWSClientFactory | None = None) -> None:
        self.factory = factory or AWSClientFactory()

    def start_instance(self, instance_id: str, region: str) -> dict:
        response = self.factory.client("ec2", region).start_instances(InstanceIds=[instance_id])
        return {"provider": "aws", "operation": "start_instance", "response": response}

    def stop_instance(self, instance_id: str, region: str) -> dict:
        response = self.factory.client("ec2", region).stop_instances(InstanceIds=[instance_id])
        return {"provider": "aws", "operation": "stop_instance", "response": response}

    def run_iam_audit(self) -> list[dict]:
        iam = self.factory.client("iam")
        users = iam.list_users().get("Users", [])
        findings: list[dict] = []
        for user in users:
            name = user["UserName"]
            devices = iam.list_mfa_devices(UserName=name).get("MFADevices", [])
            keys = iam.list_access_keys(UserName=name).get("AccessKeyMetadata", [])
            if not devices:
                findings.append({
                    "severity": "high",
                    "title": f"{name} has no MFA device",
                    "detail": "Interactive IAM users must be protected with MFA.",
                    "remediation": "Enable MFA and rotate credentials after enforcing the policy.",
                })
            for key in keys:
                if key["Status"] == "Inactive":
                    findings.append({
                        "severity": "medium",
                        "title": f"{name} has an inactive access key",
                        "detail": key["AccessKeyId"],
                        "remediation": "Delete unused access keys after confirming no workload depends on them.",
                    })
        return findings

    def create_vpc(self, cidr: str, name: str, region: str) -> dict:
        ec2 = self.factory.client("ec2", region)
        vpc = ec2.create_vpc(CidrBlock=cidr)
        ec2.create_tags(Resources=[vpc["Vpc"]["VpcId"]], Tags=[{"Key": "Name", "Value": name}])
        return vpc["Vpc"]

    def put_waf_rate_rule(self, name: str, rate_limit: int) -> dict:
        waf = self.factory.client("wafv2", "us-east-1")
        return {
            "provider": "aws",
            "service": "wafv2",
            "name": name,
            "rate_limit": rate_limit,
            "scope": "REGIONAL",
            "client_ready": waf.meta.service_model.service_name,
        }
