import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def uid() -> str:
    return str(uuid.uuid4())


class Role(str, enum.Enum):
    admin = "admin"
    engineer = "engineer"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.admin)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(160), unique=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    settings: Mapped[dict] = mapped_column(JSON, default=dict)


class AWSAccount(Base):
    __tablename__ = "aws_accounts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(140))
    account_id: Mapped[str] = mapped_column(String(32), index=True)
    region: Mapped[str] = mapped_column(String(40), default="ap-south-1")
    external_id: Mapped[str] = mapped_column(String(120), default=uid)


class IAMFinding(Base):
    __tablename__ = "iam_findings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    account_id: Mapped[str] = mapped_column(String, default="")
    severity: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(240))
    detail: Mapped[str] = mapped_column(Text)
    remediation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EC2Instance(Base):
    __tablename__ = "ec2_instances"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("aws_accounts.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(140))
    instance_type: Mapped[str] = mapped_column(String(40))
    region: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="pending")


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    service: Mapped[str] = mapped_column(String(140))
    branch: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="queued")
    logs: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Pipeline(Base):
    __tablename__ = "pipelines"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    repository: Mapped[str] = mapped_column(String(220))
    provider: Mapped[str] = mapped_column(String(40), default="github")
    stages: Mapped[list] = mapped_column(JSON, default=list)


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    report_type: Mapped[str] = mapped_column(String(60))
    format: Mapped[str] = mapped_column(String(20))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(160))
    resource: Mapped[str] = mapped_column(String(220))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SecurityFinding(Base):
    __tablename__ = "security_findings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    source: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(220))
    status: Mapped[str] = mapped_column(String(40), default="open")


class CloudWatchMetric(Base):
    __tablename__ = "cloudwatch_metrics"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    namespace: Mapped[str] = mapped_column(String(120))
    metric_name: Mapped[str] = mapped_column(String(120))
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict)
    datapoints: Mapped[list] = mapped_column(JSON, default=list)


class CostReport(Base):
    __tablename__ = "cost_reports"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    month: Mapped[str] = mapped_column(String(20), index=True)
    total_usd: Mapped[float] = mapped_column(Numeric(12, 2))
    services: Mapped[dict] = mapped_column(JSON, default=dict)


class Setting(Base):
    __tablename__ = "settings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    scope: Mapped[str] = mapped_column(String(80))
    key: Mapped[str] = mapped_column(String(120))
    value: Mapped[dict] = mapped_column(JSON, default=dict)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(255), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    ip_address: Mapped[str] = mapped_column(String(60), default="")
    user_agent: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
