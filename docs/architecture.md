# CloudOps Hub Architecture

CloudOps Hub is organized as a production-style SaaS monorepo.

```mermaid
flowchart LR
  Browser["React / Vite UI"] --> API["FastAPI API"]
  API --> Postgres["PostgreSQL"]
  API --> Redis["Redis cache and queues"]
  API --> AWS["AWS APIs through Boto3"]
  API --> Logs["Structured logs"]
  CI["GitHub Actions"] --> Docker["Docker images"]
  Terraform["Terraform"] --> AWS
```

Core layers:

- `api`: route handlers, authorization, validation, pagination boundaries.
- `services`: AWS and business workflow logic.
- `models`: normalized SQLAlchemy entities.
- `schemas`: Pydantic request and response contracts.
- `database`: SQLAlchemy session and Alembic migration support.
- `infra`: Docker Compose and Terraform for deployable infrastructure.
