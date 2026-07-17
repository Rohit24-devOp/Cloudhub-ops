"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.String(), primary_key=True), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("is_verified", sa.Boolean(), nullable=False), sa.Column("two_factor_enabled", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("organizations", sa.Column("id", sa.String(), primary_key=True), sa.Column("name", sa.String(160), nullable=False, unique=True), sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id")), sa.Column("settings", sa.JSON(), nullable=False))
    op.create_table("aws_accounts", sa.Column("id", sa.String(), primary_key=True), sa.Column("organization_id", sa.String(), sa.ForeignKey("organizations.id")), sa.Column("name", sa.String(140), nullable=False), sa.Column("account_id", sa.String(32), nullable=False), sa.Column("region", sa.String(40), nullable=False), sa.Column("external_id", sa.String(120), nullable=False))
    op.create_table("iam_findings", sa.Column("id", sa.String(), primary_key=True), sa.Column("account_id", sa.String(), nullable=False), sa.Column("severity", sa.String(30), nullable=False), sa.Column("title", sa.String(240), nullable=False), sa.Column("detail", sa.Text(), nullable=False), sa.Column("remediation", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("ec2_instances", sa.Column("id", sa.String(), primary_key=True), sa.Column("account_id", sa.String(), nullable=True), sa.Column("name", sa.String(140), nullable=False), sa.Column("instance_type", sa.String(40), nullable=False), sa.Column("region", sa.String(40), nullable=False), sa.Column("status", sa.String(40), nullable=False))
    op.create_table("deployments", sa.Column("id", sa.String(), primary_key=True), sa.Column("service", sa.String(140), nullable=False), sa.Column("branch", sa.String(120), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("logs", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("pipelines", sa.Column("id", sa.String(), primary_key=True), sa.Column("repository", sa.String(220), nullable=False), sa.Column("provider", sa.String(40), nullable=False), sa.Column("stages", sa.JSON(), nullable=False))
    op.create_table("reports", sa.Column("id", sa.String(), primary_key=True), sa.Column("report_type", sa.String(60), nullable=False), sa.Column("format", sa.String(20), nullable=False), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("notifications", sa.Column("id", sa.String(), primary_key=True), sa.Column("title", sa.String(180), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("read", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("audit_logs", sa.Column("id", sa.String(), primary_key=True), sa.Column("actor_id", sa.String(), nullable=True), sa.Column("action", sa.String(160), nullable=False), sa.Column("resource", sa.String(220), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("security_findings", sa.Column("id", sa.String(), primary_key=True), sa.Column("source", sa.String(80), nullable=False), sa.Column("severity", sa.String(30), nullable=False), sa.Column("title", sa.String(220), nullable=False), sa.Column("status", sa.String(40), nullable=False))
    op.create_table("cloudwatch_metrics", sa.Column("id", sa.String(), primary_key=True), sa.Column("namespace", sa.String(120), nullable=False), sa.Column("metric_name", sa.String(120), nullable=False), sa.Column("dimensions", sa.JSON(), nullable=False), sa.Column("datapoints", sa.JSON(), nullable=False))
    op.create_table("cost_reports", sa.Column("id", sa.String(), primary_key=True), sa.Column("month", sa.String(20), nullable=False), sa.Column("total_usd", sa.Numeric(12, 2), nullable=False), sa.Column("services", sa.JSON(), nullable=False))
    op.create_table("settings", sa.Column("id", sa.String(), primary_key=True), sa.Column("scope", sa.String(80), nullable=False), sa.Column("key", sa.String(120), nullable=False), sa.Column("value", sa.JSON(), nullable=False))
    op.create_table("refresh_tokens", sa.Column("id", sa.String(), primary_key=True), sa.Column("user_id", sa.String(), sa.ForeignKey("users.id")), sa.Column("token_hash", sa.String(255), nullable=False), sa.Column("expires_at", sa.DateTime(), nullable=False), sa.Column("revoked", sa.Boolean(), nullable=False))
    op.create_table("sessions", sa.Column("id", sa.String(), primary_key=True), sa.Column("user_id", sa.String(), sa.ForeignKey("users.id")), sa.Column("ip_address", sa.String(60), nullable=False), sa.Column("user_agent", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade():
    for table in ["sessions", "refresh_tokens", "settings", "cost_reports", "cloudwatch_metrics", "security_findings", "audit_logs", "notifications", "reports", "pipelines", "deployments", "ec2_instances", "iam_findings", "aws_accounts", "organizations", "users"]:
        op.drop_table(table)
