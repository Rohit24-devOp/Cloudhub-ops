# ⚡ CloudOps Hub

> **Provision, secure, monitor and deploy AWS infrastructure from one intelligent platform.**

CloudOps Hub is a full-stack cloud operations dashboard built by **CodTech IT Solutions**. It combines an enterprise-inspired Neo-Brutalist interface with a secure Node.js API, authenticated sessions, and persistent operational data.

![CloudOps Hub](https://img.shields.io/badge/CloudOps-Hub-ffe17c?style=for-the-badge&labelColor=171e19)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-16a34a?style=for-the-badge&logo=node.js&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-171e19?style=for-the-badge&logo=githubactions)

## ✨ What it does

| Capability | Included workflow |
| --- | --- |
| 🔐 IAM Security Audit | Security score, IAM findings, MFA/access-key checks, and on-demand audit runs. |
| 🖥️ EC2 Management | Create instances and start/stop them through authenticated API endpoints. |
| 🗺️ VPC Designer | Visual public/private subnet topology with persistent VPC creation. |
| 🛡️ AWS WAF | Web ACL rule controls and blocked-request analytics. |
| 🚀 Cloud-Native CI/CD | Deployment records, deployment UI, and a GitHub Actions validation/deploy workflow. |
| 📊 Operations Dashboard | Live metrics, deployments, notifications, security posture, and cloud-cost overview. |

## 🧱 Architecture

```text
Browser UI
    │ fetch + session cookie
    ▼
Node.js HTTP API  ────  JSON persistence layer
    │                         │
    ├─ Authentication          └─ data/cloudops.json
    ├─ EC2 operations
    ├─ IAM audits
    ├─ VPC / WAF configuration
    └─ Deployment records
```

## 🚀 Run locally

**Prerequisite:** Node.js 18 or newer.

```bash
git clone https://github.com/Rohit24-devOp/Cloudhub-ops.git
cd Cloudhub-ops
npm start
```

Open [http://localhost:3000](http://localhost:3000), select **Start free trial**, and create an account with an email and password of at least eight characters.

> Do not open `index.html` directly. The app needs the Node.js server because the dashboard uses authenticated API requests.

## 🔌 API overview

| Route | Description |
| --- | --- |
| `POST /api/auth/register` | Create an account and session |
| `POST /api/auth/login` | Sign in and receive a session cookie |
| `POST /api/auth/logout` | End the active session |
| `GET /api/dashboard` | Retrieve dashboard metrics and resources |
| `GET/POST /api/instances` | List or launch EC2 instances |
| `POST /api/instances/:id/:action` | Start, stop, restart, or terminate an instance |
| `GET/POST /api/iam/audit` | Read or run an IAM audit |
| `GET/POST /api/vpcs` | List or create VPC designs |
| `GET/PUT /api/waf` | Read or update Web ACL rules |
| `GET/POST /api/deployments` | Track or trigger deployments |

## 🔒 Security note

This project persists local CloudOps Hub data and intentionally **does not call a live AWS account**. A production deployment should integrate AWS SDK clients on the server only, using IAM roles, short-lived credentials, least-privilege policies, audit logs, and a production database. Never expose AWS secrets in the browser or commit them to Git.

## ⚙️ CI/CD

The included GitHub Actions workflow validates the server and client JavaScript on pushes and pull requests. It can also publish the static site to GitHub Pages.

```bash
npm test
```

## 🗂️ Project structure

```text
.
├── .github/workflows/ci-cd.yml  # GitHub Actions pipeline
├── data/cloudops.json           # Created automatically at runtime
├── index.html                   # Marketing page + application shell
├── main.js                      # API-backed client application
├── server.js                    # Node.js API server and static host
└── style.css                    # Neo-Brutalist design system
```

---

Built with purpose by **CodTech IT Solutions**.
