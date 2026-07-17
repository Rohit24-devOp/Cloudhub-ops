from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.database import get_db
from app.services.aws_clients import AWSOperations


router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
settings = get_settings()


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> models.User:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc
    user = db.get(models.User, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user


def require_admin(user: models.User = Depends(current_user)) -> models.User:
    if user.role != models.Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


def audit(db: Session, user_id: str, action: str, resource: str, metadata: dict | None = None) -> None:
    db.add(models.AuditLog(actor_id=user_id, action=action, resource=resource, metadata_json=metadata or {}))


@router.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": settings.app_name, "environment": settings.environment}


@router.post("/auth/register", response_model=schemas.TokenPair)
def register(payload: schemas.RegisterRequest, request: Request, db: Session = Depends(get_db)) -> schemas.TokenPair:
    existing = db.scalar(select(models.User).where(models.User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = models.User(email=payload.email, name=payload.name, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(models.Organization(name=f"{payload.name}'s Organization", owner_id=user.id))
    refresh_token, token_hash = create_refresh_token()
    db.add(models.RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)))
    db.add(models.Session(user_id=user.id, ip_address=request.client.host if request.client else "", user_agent=request.headers.get("user-agent", "")))
    audit(db, user.id, "auth.register", "users", {"email": payload.email})
    db.commit()
    return schemas.TokenPair(access_token=create_access_token(user.id, user.role.value), refresh_token=refresh_token)


@router.post("/auth/login", response_model=schemas.TokenPair)
def login(payload: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)) -> schemas.TokenPair:
    user = db.scalar(select(models.User).where(models.User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    refresh_token, token_hash = create_refresh_token()
    db.add(models.RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)))
    db.add(models.Session(user_id=user.id, ip_address=request.client.host if request.client else "", user_agent=request.headers.get("user-agent", "")))
    audit(db, user.id, "auth.login", "sessions")
    db.commit()
    return schemas.TokenPair(access_token=create_access_token(user.id, user.role.value), refresh_token=refresh_token)


@router.post("/auth/refresh", response_model=schemas.TokenPair)
def refresh(payload: dict, db: Session = Depends(get_db)) -> schemas.TokenPair:
    submitted_token = payload.get("refresh_token", "")
    token_hash = sha256(submitted_token.encode()).hexdigest()
    record = db.scalar(select(models.RefreshToken).where(models.RefreshToken.token_hash == token_hash, models.RefreshToken.revoked.is_(False)))
    if not record or record.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=401, detail="Refresh token expired")
    user = db.get(models.User, record.user_id)
    record.revoked = True
    next_token, next_hash = create_refresh_token()
    db.add(models.RefreshToken(user_id=user.id, token_hash=next_hash, expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)))
    db.commit()
    return schemas.TokenPair(access_token=create_access_token(user.id, user.role.value), refresh_token=next_token)


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(current_user)) -> schemas.UserOut:
    return schemas.UserOut(id=user.id, email=user.email, name=user.name, role=user.role.value)


@router.get("/dashboard", response_model=schemas.DashboardOut)
def dashboard(db: Session = Depends(get_db), user: models.User = Depends(current_user)) -> schemas.DashboardOut:
    running = db.scalar(select(func.count(models.EC2Instance.id)).where(models.EC2Instance.status == "running")) or 0
    findings = db.scalar(select(func.count(models.SecurityFinding.id)).where(models.SecurityFinding.status == "open")) or 0
    latest_cost = db.scalar(select(models.CostReport).order_by(models.CostReport.month.desc()))
    deployment = db.scalar(select(models.Deployment).order_by(models.Deployment.created_at.desc()))
    return schemas.DashboardOut(
        security_score=max(0, 100 - findings * 8),
        running_instances=running,
        open_findings=findings,
        monthly_cost=float(latest_cost.total_usd) if latest_cost else 0,
        deployment_status=deployment.status if deployment else "not_started",
    )


@router.get("/instances", response_model=list[schemas.InstanceOut])
def list_instances(db: Session = Depends(get_db), user: models.User = Depends(current_user)) -> list[models.EC2Instance]:
    return list(db.scalars(select(models.EC2Instance).order_by(models.EC2Instance.name)))


@router.post("/instances", response_model=schemas.InstanceOut)
def create_instance(payload: schemas.InstanceCreate, db: Session = Depends(get_db), user: models.User = Depends(require_admin)) -> models.EC2Instance:
    instance = models.EC2Instance(id=f"i-{uuid4().hex[:17]}", name=payload.name, instance_type=payload.instance_type, region=payload.region, status="running")
    db.add(instance)
    db.add(models.Notification(title="EC2 instance created", message=f"{payload.name} is tracked in CloudOps Hub."))
    audit(db, user.id, "ec2.create", instance.id, payload.model_dump())
    db.commit()
    db.refresh(instance)
    return instance


@router.post("/instances/{instance_id}/{action}", response_model=schemas.InstanceOut)
def instance_action(instance_id: str, action: str, db: Session = Depends(get_db), user: models.User = Depends(require_admin)) -> models.EC2Instance:
    if action not in {"start", "stop", "restart", "terminate"}:
        raise HTTPException(status_code=400, detail="Unsupported EC2 action")
    instance = db.get(models.EC2Instance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    instance.status = "terminated" if action == "terminate" else "stopped" if action == "stop" else "running"
    audit(db, user.id, f"ec2.{action}", instance.id)
    db.commit()
    db.refresh(instance)
    return instance


@router.post("/iam/audit")
def run_iam_audit(db: Session = Depends(get_db), user: models.User = Depends(require_admin)) -> dict:
    try:
        findings = AWSOperations().run_iam_audit()
    except Exception:
        findings = [{
            "severity": "medium",
            "title": "AWS IAM audit could not reach the configured account",
            "detail": "Configure AWS credentials or an IAM role for live audit execution.",
            "remediation": "Set AWS credentials in the runtime environment and scope them with least privilege.",
        }]
    for item in findings:
        db.add(models.IAMFinding(account_id="", **item))
        db.add(models.SecurityFinding(source="iam", severity=item["severity"], title=item["title"]))
    audit(db, user.id, "iam.audit", "iam_findings", {"count": len(findings)})
    db.commit()
    return {"security_score": max(0, 100 - len(findings) * 8), "findings": findings}


@router.post("/vpcs")
def create_vpc(payload: schemas.VPCDesign, db: Session = Depends(get_db), user: models.User = Depends(require_admin)) -> dict:
    audit(db, user.id, "vpc.design.create", "vpc", payload.model_dump())
    db.commit()
    return {"status": "design_saved", "design": payload.model_dump()}


@router.put("/waf")
def save_waf(payload: schemas.WAFConfig, db: Session = Depends(get_db), user: models.User = Depends(require_admin)) -> dict:
    db.add(models.SecurityFinding(source="waf", severity="low", title=f"WAF policy {payload.name} updated", status="resolved"))
    audit(db, user.id, "waf.update", payload.name, payload.model_dump())
    db.commit()
    return {"status": "active", "web_acl": payload.model_dump()}


@router.post("/deployments", response_model=schemas.DeploymentOut)
def create_deployment(payload: schemas.DeploymentCreate, db: Session = Depends(get_db), user: models.User = Depends(require_admin)) -> models.Deployment:
    deployment = models.Deployment(service=payload.service, branch=payload.branch, status="building", logs="Build queued from CloudOps Hub")
    db.add(deployment)
    db.add(models.Notification(title="Deployment started", message=f"{payload.service}:{payload.branch} is building."))
    audit(db, user.id, "deployment.create", payload.service, payload.model_dump())
    db.commit()
    db.refresh(deployment)
    return deployment


@router.get("/deployments", response_model=list[schemas.DeploymentOut])
def list_deployments(db: Session = Depends(get_db), user: models.User = Depends(current_user)) -> list[models.Deployment]:
    return list(db.scalars(select(models.Deployment).order_by(models.Deployment.created_at.desc())))


@router.post("/reports")
def create_report(payload: schemas.ReportCreate, db: Session = Depends(get_db), user: models.User = Depends(current_user)) -> dict:
    report = models.Report(report_type=payload.report_type, format=payload.format, payload={"generated_by": user.email})
    db.add(report)
    audit(db, user.id, "report.create", report.report_type, payload.model_dump())
    db.commit()
    return {"id": report.id, "status": "generated", "format": report.format}


@router.get("/notifications")
def notifications(db: Session = Depends(get_db), user: models.User = Depends(current_user)) -> list[dict]:
    rows = db.scalars(select(models.Notification).order_by(models.Notification.created_at.desc())).all()
    return [{"id": row.id, "title": row.title, "message": row.message, "read": row.read} for row in rows]
