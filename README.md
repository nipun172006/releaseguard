# ReleaseGuard

**Deployment readiness and release-risk control center.**

ReleaseGuard helps engineering teams decide whether a software release is safe to deploy. It records release metadata, evaluates operational readiness checks, calculates a transparent readiness score and risk level, and tracks the release from draft through deployment or rollback.

The project is a DevSecOps capstone built around React, FastAPI, PostgreSQL, Docker, GitHub Actions, Trivy, GHCR, Terraform, AWS EKS, Kubernetes, Helm, ArgoCD, Prometheus, and Grafana.

The approved product definition is documented in [docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md).

## Project status

- [x] Step 1 — Product definition and scope
- [x] Step 2 — Environment and account preflight
- [x] Step 3 — Repository and application bootstrap
- [x] Step 4 — Backend and database
- [ ] Step 5 — Automated tests
- [ ] Step 6 — Frontend
- [ ] Step 7 — Docker and local stack
- [ ] Step 8 — CI/CD and security scanning
- [ ] Step 9 — Terraform and AWS EKS
- [ ] Step 10 — Kubernetes and Helm
- [ ] Step 11 — ArgoCD GitOps
- [ ] Step 12 — Prometheus and Grafana
- [ ] Step 13 — Evidence, documentation, and presentation

## Runnable application

The current ReleaseGuard foundation includes:

- A FastAPI service with database-aware `/ready` and interactive `/docs` endpoints.
- PostgreSQL persistence managed through versioned Alembic migrations.
- Release create, list, search, filter, retrieve, update, delete, statistics, and readiness APIs.
- Deterministic readiness scoring, risk classification, blocker explanations, and lifecycle enforcement.
- A React and TypeScript interface that performs a real backend health check.
- Pinned Python and JavaScript dependency trees.
- Secret-safe example environment files and repository ignore rules.
- Local runtime baselines of Python 3.12 and Node.js 22.

## Repository layout

```text
releaseguard/
├── backend/    FastAPI application and Python dependencies
├── frontend/   React, TypeScript, and Vite application
└── docs/       Product, setup, and delivery documentation
```

See [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) for the exact commands and an explanation of the structure.
