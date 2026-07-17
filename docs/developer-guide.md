# Developer Guide

## Backend Flow

1. Routes live in `apps/backend/app/api.py`.
2. Request and response contracts live in `apps/backend/app/schemas.py`.
3. Database entities live in `apps/backend/app/models.py`.
4. AWS integrations live in `apps/backend/app/services/aws_clients.py`.

Add new modules by creating a Pydantic schema, SQLAlchemy model if persistence is required, route handler, and focused test.

## Frontend Flow

The React app uses TanStack Query for API reads and mutations. API calls are centralized through the Axios client in `apps/frontend/src/main.tsx`.

For larger production work, split `main.tsx` into:

- `src/api`
- `src/components`
- `src/features`
- `src/routes`
- `src/styles`

## Security Rules

- Never commit AWS keys.
- Keep AWS calls on the backend only.
- Use JWT access tokens for short sessions and refresh tokens for continuity.
- Log administrative changes through `audit_logs`.
- Use IAM roles and AWS Secrets Manager in production.
