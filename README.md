# ReleaseGuard

[![CI/CD](https://github.com/nipun172006/releaseguard/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/nipun172006/releaseguard/actions/workflows/ci-cd.yml)

**Deployment readiness and release-risk control center.**

ReleaseGuard helps engineering teams decide whether a software release is safe to deploy. It records release metadata, evaluates operational readiness checks, calculates a transparent readiness score and risk level, and tracks the release from draft through deployment or rollback.

The project is a DevSecOps capstone built around React, FastAPI, PostgreSQL, Docker, GitHub Actions, Trivy, GHCR, Terraform, AWS EKS, Kubernetes, Helm, ArgoCD, Prometheus, and Grafana.

The approved product definition is documented in [docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md).

## Project status

- [x] Step 1 — Product definition and scope
- [x] Step 2 — Environment and account preflight
- [x] Step 3 — Repository and application bootstrap
- [x] Step 4 — Backend and database
- [x] Step 5 — Automated tests
- [x] Step 6 — Frontend
- [x] Step 7 — Docker and local stack
- [x] Step 8 — CI/CD and security scanning
- [ ] Step 9 — Terraform and AWS EKS
- [x] Step 10 — Kubernetes and Helm
- [x] Step 11 — ArgoCD GitOps
- [ ] Step 12 — Prometheus and Grafana
- [ ] Step 13 — Evidence, documentation, and presentation

## Runnable application

The current ReleaseGuard foundation includes:

- A FastAPI service with database-aware `/ready` and interactive `/docs` endpoints.
- PostgreSQL persistence managed through versioned Alembic migrations.
- Release create, list, search, filter, retrieve, update, delete, statistics, and readiness APIs.
- Deterministic readiness scoring, risk classification, blocker explanations, and lifecycle enforcement.
- A 23-test backend suite with real PostgreSQL integration and a 90% coverage gate.
- A responsive React and TypeScript control center with statistics, server-backed filters, complete release CRUD, readiness controls, and lifecycle actions.
- Production-style, non-root backend and frontend images orchestrated with PostgreSQL through Docker Compose.
- An ordered GitHub Actions pipeline that tests, builds, scans both images with Trivy, and publishes verified Git-SHA tags to GHCR.
- A validated, cost-conscious Terraform plan for a two-subnet AWS VPC, EKS cluster, and managed worker node group.
- A Helm-managed Kubernetes deployment with isolated namespace, two frontend replicas, two backend replicas, PostgreSQL, ClusterIP Services, health probes, and path-based Ingress routing.
- An Argo CD Application with automated synchronization, pruning, and verified self-healing from the public Git repository.
- Pinned Python and JavaScript dependency trees.
- Secret-safe example environment files and repository ignore rules.
- Local runtime baselines of Python 3.12 and Node.js 22.

## Repository layout

```text
releaseguard/
├── backend/      FastAPI application, migrations, tests, and Docker image
├── frontend/     React application and Nginx production image
├── docs/         Product, setup, and delivery documentation
├── terraform/    AWS VPC and EKS infrastructure as code
├── k8s/          Kubernetes namespace bootstrap manifest
├── helm/         ReleaseGuard application Helm chart
├── argocd/       GitOps Application bootstrap manifest
├── monitoring/   Prometheus and Grafana Helm values
└── compose.yaml  Complete local three-service stack
```

See [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) for manual development, [docs/DOCKER.md](docs/DOCKER.md) for the container workflow, [docs/FRONTEND.md](docs/FRONTEND.md) for the dashboard architecture, [docs/CI_CD.md](docs/CI_CD.md) for the delivery and security gates, [terraform/README.md](terraform/README.md) for the AWS infrastructure design and commands, [docs/KUBERNETES.md](docs/KUBERNETES.md) for Kubernetes and Helm, [docs/ARGOCD.md](docs/ARGOCD.md) for GitOps, and [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) for Prometheus and Grafana.
