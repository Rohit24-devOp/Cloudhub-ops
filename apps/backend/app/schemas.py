from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str


class InstanceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    instance_type: str = "t3.medium"
    region: str = "ap-south-1"


class InstanceOut(BaseModel):
    id: str
    name: str
    instance_type: str
    region: str
    status: str

    class Config:
        from_attributes = True


class DeploymentCreate(BaseModel):
    service: str = Field(min_length=2, max_length=140)
    branch: str = "main"


class DeploymentOut(BaseModel):
    id: str
    service: str
    branch: str
    status: str
    logs: str
    created_at: datetime

    class Config:
        from_attributes = True


class WAFConfig(BaseModel):
    name: str = "cloudops-web-acl"
    managed_rules: list[str] = ["AWSManagedRulesCommonRuleSet"]
    rate_limit: int = Field(default=2000, ge=100, le=20000000)
    blocked_countries: list[str] = []


class VPCDesign(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    cidr: str = "10.0.0.0/16"
    public_subnets: list[str] = ["10.0.1.0/24"]
    private_subnets: list[str] = ["10.0.11.0/24"]
    enable_nat_gateway: bool = True


class ReportCreate(BaseModel):
    report_type: str
    format: str = "pdf"


class DashboardOut(BaseModel):
    security_score: int
    running_instances: int
    open_findings: int
    monthly_cost: float
    deployment_status: str
