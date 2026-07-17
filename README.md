# CloudOps Hub

> Provision, secure, monitor and deploy AWS infrastructure from one intelligent platform.

CloudOps Hub is a production-oriented cloud operations SaaS built for **CodTech IT Solutions**. It gives cloud teams one workspace for AWS security reviews, EC2 operations, VPC planning, WAF controls, deployment tracking, reports, notifications, and infrastructure automation.

![CloudOps Hub](https://img.shields.io/badge/CloudOps-Hub-ffe17c?style=for-the-badge&labelColor=101820)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-61dafb?style=for-the-badge&logo=react&logoColor=101820)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Boto3-ff9900?style=for-the-badge&logo=amazonaws&logoColor=101820)

## What Is Included

| Area | Implementation |
| --- | --- |
| Frontend | React, TypeScript, Vite, TanStack Query, Axios, Lucide icons, responsive SaaS dashboard UI |
| Backend | FastAPI, SQLAlchemy models, Pydantic schemas, JWT access tokens, refresh tokens, RBAC, rate limiting, structured logging |
| Database | Normalized schema for users, organizations, AWS accounts, IAM findings, EC2 instances, deployments, reports, notifications, audit logs, security findings, CloudWatch metrics, cost reports, settings, sessions, refresh tokens |
| AWS | Boto3 service layer for IAM audit, EC2 actions, VPC creation, and WAF operations |
| DevOps | Dockerfiles, Docker Compose, GitHub Actions backend/frontend/docker pipeline |
| IaC | Terraform VPC, subnet, internet gateway, route table, security group, and EC2 modules |
| Documentation | Architecture guide, deployment guide, OpenAPI docs through FastAPI Swagger |

## Product Modules

| Module | Status | Backend coverage |
| --- | --- | --- |
| Authentication | Implemented | Register, login, refresh tokens, JWT auth, sessions |
| Dashboard | Implemented | Security score, EC2 count, findings, cost, deployment status |
| IAM Audit | Implemented | Boto3 IAM scan adapter, persisted findings, security score |
| EC2 Management | Implemented | Create/list/start/stop/restart/terminate tracked instances |
| VPC Builder | Implemented | Validated VPC design endpoint and Terraform VPC module |
| Cloud Security WAF | Implemented | Web ACL configuration endpoint and Boto3 WAF adapter |
| Deployment Center | Implemented | Deployment records, logs, status history |
| Reports | Implemented | Report creation endpoint and report database model |
| Notifications | Implemented | Notification persistence and read model |
| Organization/Admin | Scaffolded | Users, organizations, roles, audit logs, settings tables |

## Architecture

```mermaid
flowchart LR
  UI["React + TypeScript UI"] --> API["FastAPI API"]
  API --> DB["PostgreSQL / SQLAlchemy"]
  API --> Redis["Redis cache + Celery broker"]
  API --> AWS["AWS APIs via Boto3"]
  API --> Logs["Structured JSON logs"]
  Actions["GitHub Actions"] --> Docker["Docker images"]
  Terraform["Terraform modules"] --> AWS
```

## Database Design

```mermaid
erDiagram
  USERS ||--o{ ORGANIZATIONS : owns
  ORGANIZATIONS ||--o{ AWS_ACCOUNTS : connects
  AWS_ACCOUNTS ||--o{ IAM_FINDINGS : produces
  AWS_ACCOUNTS ||--o{ EC2_INSTANCES : tracks
  USERS ||--o{ SESSIONS : creates
  USERS ||--o{ REFRESH_TOKENS : receives
  USERS ||--o{ AUDIT_LOGS : writes
  DEPLOYMENTS ||--o{ PIPELINES : relates
  REPORTS ||--o{ COST_REPORTS : summarizes
```

## Run The Existing Local App

This keeps the previously built single-process demo running:

```bash
npm start
```

Open `http://localhost:3000`.

## Run The Production Stack With Docker

```bash
docker compose up --build
```

Open:

- Frontend: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/api/health`

Default local workspace login is created from the frontend button:

- Email: `admin@codtechitsolutions.com`
- Password: `cloudops-secure-123`

## Run Backend Manually

```bash
cd apps/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Run Frontend Manually

```bash
cd apps/frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API Modules

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/me`
- `GET /api/dashboard`
- `GET /api/instances`
- `POST /api/instances`
- `POST /api/instances/{instance_id}/{action}`
- `POST /api/iam/audit`
- `POST /api/vpcs`
- `PUT /api/waf`
- `GET /api/deployments`
- `POST /api/deployments`
- `POST /api/reports`
- `GET /api/notifications`

## Environment Variables

Create `.env` files from the examples when running outside Docker:

```bash
CLOUDOPS_DATABASE_URL=postgresql+psycopg://cloudops:cloudops-local@localhost:5432/cloudops
CLOUDOPS_REDIS_URL=redis://localhost:6379/0
CLOUDOPS_JWT_SECRET=replace-with-a-long-random-secret
CLOUDOPS_CORS_ORIGINS=http://localhost:5173,http://localhost:8080
CLOUDOPS_AWS_REGION=ap-south-1
```

## Project Structure

```text
.
|-- apps/
|   |-- backend/          FastAPI, SQLAlchemy, Alembic, Boto3
|   `-- frontend/         React, TypeScript, Vite
|-- docs/                 Architecture and deployment guides
|-- infra/terraform/      AWS infrastructure modules
|-- docker-compose.yml    PostgreSQL, Redis, backend, frontend
|-- server.js             Existing lightweight Node app
|-- index.html            Existing landing and dashboard shell
`-- .github/workflows/    CI/CD pipeline
```

## CI/CD

The workflow validates:

- Legacy Node app syntax
- Backend tests with Pytest
- Frontend tests and production build
- Docker image builds

Pipeline file: `.github/workflows/ci-cd.yml`

## Terraform

The Terraform modules live in `infra/terraform`:

- `modules/vpc`: VPC, public/private subnets, internet gateway, public route table
- `modules/security`: application security group
- `modules/ec2`: Amazon Linux EC2 instance

Run:

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## Quality Gates

Backend:

```bash
cd apps/backend
pip install -r requirements.txt
pytest tests
```

Frontend:

```bash
cd apps/frontend
npm install
npm run test
npm run build
```

## Security

Production deployments must replace the local JWT secret, use managed PostgreSQL and Redis, set HTTPS at the edge, configure least-privilege AWS IAM roles, and store secrets in AWS Secrets Manager or the deployment platform secret store.

## Important AWS Note

The application includes Boto3 adapters for AWS operations. Live AWS calls require valid credentials or an instance/task role with least-privilege policies. For safety, local development can still use the persisted database workflows without touching a real AWS account.

Built for **CodTech IT Solutions**.
