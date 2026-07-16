# CloudOps Hub

CloudOps Hub is a browser-based cloud operations application created with CodTech IT Solutions.

## Included services

- AWS IAM Security Audit: security score, MFA and access-key findings, compliance controls.
- Simple VPC Design: visual VPC architecture designer with public/private subnets and gateway topology.
- Cloud Security (AWS WAF): managed-rule setup and blocked-request analytics.
- Cloud-Native CI/CD: GitHub Actions validates the client app and deploys it to GitHub Pages when pushed to `main`.

## Run locally

Open `index.html` in a browser. Select **Log in** or **Start free trial** and use any email/password to enter demo mode.

## AWS integration

The current version is a functional frontend demonstration; AWS changes are not sent to a live account. To enable live provisioning, use a backend with AWS IAM roles, temporary credentials, audit logging, and least-privilege permissions. Never put long-lived AWS secrets in the browser or repository.
