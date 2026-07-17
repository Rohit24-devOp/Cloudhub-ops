# Deployment Guide

## Local Docker

```bash
docker compose up --build
```

Open the frontend at `http://localhost:8080` and the API documentation at `http://localhost:8000/docs`.

## Environment

Set these variables in production:

```bash
CLOUDOPS_DATABASE_URL=postgresql+psycopg://user:password@host:5432/cloudops
CLOUDOPS_REDIS_URL=redis://redis:6379/0
CLOUDOPS_JWT_SECRET=<strong-secret>
CLOUDOPS_CORS_ORIGINS=https://your-domain.example
AWS_REGION=ap-south-1
```

## Terraform

Configure the S3 backend in `infra/terraform/main.tf`, then run:

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```
