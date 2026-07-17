# API Documentation

FastAPI generates OpenAPI and Swagger automatically.

Local URLs:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Core Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/health` | GET | Service health check |
| `/api/auth/register` | POST | Create user, organization, session, access token, refresh token |
| `/api/auth/login` | POST | Authenticate existing user |
| `/api/auth/refresh` | POST | Rotate refresh token and issue a new access token |
| `/api/me` | GET | Current authenticated user |
| `/api/dashboard` | GET | Operations summary |
| `/api/instances` | GET/POST | List or create EC2 tracked instances |
| `/api/instances/{id}/{action}` | POST | Start, stop, restart, or terminate instance state |
| `/api/iam/audit` | POST | Run IAM audit through Boto3 adapter |
| `/api/vpcs` | POST | Save VPC design payload |
| `/api/waf` | PUT | Save WAF Web ACL configuration |
| `/api/deployments` | GET/POST | List or start deployments |
| `/api/reports` | POST | Generate report records |
| `/api/notifications` | GET | List notifications |
