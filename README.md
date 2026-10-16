# ReleaseGuard

[![CI/CD](https://github.com/nipun172006/releaseguard/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/nipun172006/releaseguard/actions/workflows/ci-cd.yml)

**Deployment readiness and release-risk control center.**

ReleaseGuard helps an engineering team decide whether a software release is safe to deploy. It records release metadata and five readiness checks, calculates an explainable score and risk level, identifies blockers, and enforces a release lifecycle from `DRAFT` through deployment, success, failure, or rollback.

This DevSecOps capstone demonstrates the complete path from application code to a secure CI pipeline, immutable container images, Terraform-managed AWS infrastructure, Helm-managed Kubernetes, Argo CD GitOps, and Prometheus/Grafana observability.

![ReleaseGuard dashboard](demo/evidence/eks-application.png)

## Core features

- Create, search, filter, edit, and delete release records.
- Track automated tests, security scanning, approval, backup, and rollback evidence.
- Calculate a deterministic readiness score from 0 to 100.
- Classify `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` release risk with human-readable blockers.
- Enforce valid lifecycle transitions and reject unsafe changes.
- Expose liveness, database-aware readiness, OpenAPI documentation, and Prometheus metrics.
- Visualize deployment activity and readiness through a responsive React dashboard.

The complete product rules are documented in [docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md).

## Architecture

```mermaid
flowchart LR
    Developer[Developer] --> GitHub[GitHub repository]
    GitHub --> Actions[GitHub Actions]
    Actions --> Tests[Tests + 90% coverage]
    Tests --> Build[Build Docker images]
    Build --> Trivy[Trivy security gate]
    Trivy --> GHCR[GHCR Git-SHA images]

    GitHub --> Argo[Argo CD]
    GHCR --> EKS[AWS EKS]
    Argo --> Helm[Helm chart]
    Helm --> EKS

    Terraform[Terraform] --> VPC[AWS VPC + subnets]
    Terraform --> EKS

    EKS --> Frontend[React + Nginx]
    Frontend --> Backend[FastAPI]
    Backend --> PostgreSQL[(PostgreSQL)]
    Backend --> Metrics[/metrics]
    Metrics --> Prometheus[Prometheus]
    Prometheus --> Grafana[Grafana]
```

The browser reaches the Nginx frontend. Nginx serves the compiled React files and proxies `/api`, `/health`, `/ready`, `/metrics`, and `/docs` to FastAPI. FastAPI owns the release rules and stores data in PostgreSQL. In Kubernetes, internal `ClusterIP` Services connect the three workloads and an Ingress provides path-based entry.

## Technology stack

| Layer | Tools | Purpose |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite, Nginx | Dashboard and production web serving |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Alembic | API, business rules, persistence, migrations |
| Database | PostgreSQL 17 | Release data |
| Testing | pytest, HTTPX, pytest-cov | Unit and API integration tests with coverage gate |
| Containers | Docker, Docker Compose | Reproducible non-root images and local stack |
| CI/CD | GitHub Actions, Trivy, GHCR | Test, build, scan, and publish immutable images |
| Infrastructure | Terraform, AWS VPC, Amazon EKS | Reproducible cloud infrastructure |
| Platform | Kubernetes, Helm, Nginx Ingress | Workload scheduling and configuration |
| GitOps | Argo CD | Automated sync, pruning, and self-healing |
| Observability | Prometheus, Grafana | Metrics collection and dashboards |

## Repository layout

```text
releaseguard/
├── .github/workflows/     CI/CD pipeline
├── backend/               FastAPI, migrations, and 23 tests
├── frontend/              React dashboard and Nginx image
├── terraform/             AWS VPC and EKS infrastructure
├── k8s/                   Namespace bootstrap manifest
├── helm/releaseguard/     Application Helm chart
├── argocd/                Argo CD Application manifest
├── monitoring/            Prometheus and Grafana values
├── docs/                  Detailed implementation notes
├── demo/                  Presentation and submission evidence
└── compose.yaml           Local three-service stack
```

## Run locally with Docker Compose

Requirements: Docker Desktop with Compose.

```bash
git clone https://github.com/nipun172006/releaseguard.git
cd releaseguard
cp .env.example .env
```

Replace both `CHANGE_ME_LOCAL_ONLY` values in `.env` with the same URL-safe local password, then run:

```bash
docker compose up --build --detach --wait
```

Open:

- Dashboard: `http://localhost:5173`
- Direct API: `http://localhost:8000`
- OpenAPI documentation: `http://localhost:5173/docs`
- Database-aware readiness: `http://localhost:5173/ready`
- Prometheus metrics: `http://localhost:8000/metrics`

Inspect or stop the stack:

```bash
docker compose ps
docker compose logs --follow
docker compose down
```

`docker compose down` keeps PostgreSQL data. `docker compose down --volumes` also deletes the local database volume and should be used only when that data is no longer needed.

Detailed manual Python and Node.js setup is in [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md). The container design is in [docs/DOCKER.md](docs/DOCKER.md).

## Automated tests

The backend has 23 tests covering readiness scoring, risk rules, validation, CRUD, filters, statistics, lifecycle enforcement, liveness, and database readiness. The test fixtures require a database whose name ends in `_test` and roll each test back to keep test data isolated.

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock.txt
export RELEASEGUARD_TEST_DATABASE_URL='postgresql+psycopg://releaseguard:LOCAL_PASSWORD@localhost:5432/releaseguard_test'
.venv/bin/python -m pytest
```

The suite fails when application coverage drops below 90%.

## CI/CD and security

`.github/workflows/ci-cd.yml` runs on pushes to `main`, pull requests, and manual dispatches. Its ordered gates are:

1. Start PostgreSQL and run migrations, tests, and the 90% coverage gate.
2. Run frontend linting and create the production Vite build.
3. Build backend and frontend Docker images.
4. Scan the runtime images with Trivy for fixable `HIGH` and `CRITICAL` vulnerabilities.
5. Publish only successful `main` builds to GHCR with immutable full Git commit SHA tags.

Published image format:

```text
ghcr.io/nipun172006/releaseguard-backend:<git-sha>
ghcr.io/nipun172006/releaseguard-frontend:<git-sha>
```

No registry password is stored in the repository. The workflow uses GitHub's short-lived `GITHUB_TOKEN` and grants `packages: write` only to the image job. See [docs/CI_CD.md](docs/CI_CD.md).

## Terraform and AWS EKS

The Terraform configuration in `terraform/` creates:

- one VPC with CIDR `10.20.0.0/16`;
- two public subnets in separate availability zones;
- one internet gateway;
- one Amazon EKS 1.35 control plane; and
- one managed `m7i-flex.large` worker node.

The learning environment intentionally avoids a NAT gateway and cloud load balancer to reduce cost. It is suitable for temporary evidence collection, not a production high-availability design.

```bash
cd terraform
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out=releaseguard.tfplan
terraform apply releaseguard.tfplan
aws eks update-kubeconfig --region ap-south-1 --name releaseguard-eks
kubectl get nodes
```

The real evidence run created the VPC and active EKS cluster, deployed ReleaseGuard, verified a Ready worker node and running application, and then destroyed all 46 Terraform-managed resources. See [docs/AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md) and [terraform/README.md](terraform/README.md).

## Kubernetes and Helm

The Helm chart creates one PostgreSQL Deployment, two backend replicas, two frontend replicas, internal Services, health probes, a Secret, and an Ingress. Validate and deploy it with:

```bash
kubectl apply -f k8s/namespace.yaml
helm lint helm/releaseguard --values helm/releaseguard/values-local.yaml
helm upgrade --install releaseguard helm/releaseguard \
  --namespace releaseguard \
  --values helm/releaseguard/values-local.yaml \
  --wait --timeout 5m

kubectl get pods,services,ingress -n releaseguard
```

The default values use public GHCR images with immutable SHA tags. `values-local.yaml` switches Minikube to locally loaded images. See [docs/KUBERNETES.md](docs/KUBERNETES.md).

## Argo CD GitOps

`argocd/application.yaml` connects the public repository and Helm chart to the `releaseguard` namespace. Automated sync applies Git changes, pruning removes deleted resources, and self-heal reverses manual cluster drift.

```bash
kubectl apply -f argocd/application.yaml
kubectl get application releaseguard -n argocd \
  -o jsonpath='{.status.sync.status}{" / "}{.status.health.status}{"\n"}'
```

The verified result was `Synced / Healthy`. A drift test manually changed the backend from two replicas to one; Argo CD detected the difference and restored two replicas from Git. See [docs/ARGOCD.md](docs/ARGOCD.md).

## Prometheus and Grafana

FastAPI exposes request count and duration metrics at `/metrics`. Prometheus scrapes the backend every 15 seconds, and Grafana provisions the **ReleaseGuard Application Metrics** dashboard with total requests, request rate, and average request duration.

```bash
helm upgrade --install prometheus \
  oci://ghcr.io/prometheus-community/charts/prometheus \
  --version 29.37.0 --namespace monitoring --create-namespace \
  --values monitoring/prometheus-values.yaml --wait

helm upgrade --install grafana \
  oci://ghcr.io/grafana-community/helm-charts/grafana \
  --version 14.0.0 --namespace monitoring \
  --values monitoring/grafana-values.yaml --wait
```

The `releaseguard-backend` Prometheus target was verified `UP`, the Grafana data source passed its health check, and dashboard queries returned data. See [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md).

## Evidence and presentation

- [10-slide editable project presentation](demo/ReleaseGuard-DevSecOps-Capstone-v2.pptx)
- [Timed final-video narration script](demo/DEMO_SCRIPT.md)
- [Manual screenshot and submission checklist](demo/README.md)
- [AWS VPC evidence](demo/evidence/aws-vpc.png)
- [AWS EKS cluster evidence](demo/evidence/aws-eks-cluster.png)
- [AWS EKS worker evidence](demo/evidence/aws-eks-worker.png)
- [Terraform plan evidence](demo/evidence/terraform-plan.png)
- [Verified Terraform destroy evidence](demo/evidence/terraform-destroy.png)
- [Kubernetes and Helm evidence](demo/evidence/eks-kubernetes-helm.png)
- [EKS-hosted application evidence](demo/evidence/eks-application.png)
- [Git commit history](demo/evidence/git-commits.png)
- [Successful GitHub Actions pipeline](demo/evidence/github-actions.png)
- [Backend GHCR package](demo/evidence/ghcr-backend.png)
- [Frontend GHCR package](demo/evidence/ghcr-frontend.png)
- [Prometheus target health](demo/evidence/prometheus-target-up.png)

The narrated MP4 walkthrough is the final user-recorded submission artifact. Its demo order is: presentation, codebase, GitHub Actions, Terraform and AWS, Argo CD, Kubernetes resources, Prometheus target, Grafana dashboard, and teardown evidence.

## Known limitations

- Authentication and organization-level authorization are outside the capstone scope.
- The application records deployment decisions but does not execute external deployments.
- The learning Helm chart stores PostgreSQL data in `emptyDir`; replacing the database Pod loses demo data.
- Prometheus and Grafana also use temporary local storage.
- The AWS example uses one public-subnet worker to control cost and is not production high availability.
- The Helm Secret contains an obvious demo placeholder; production should use AWS Secrets Manager or another external secret system.
- TLS, DNS, alerting, autoscaling, and a remote Terraform state backend are future improvements.

## Safe cleanup

Local Kubernetes resources:

```bash
helm uninstall releaseguard --namespace releaseguard
kubectl delete -f k8s/namespace.yaml
```

AWS infrastructure:

```bash
cd terraform
terraform destroy
```

Always wait for Terraform to report successful destruction and verify that no ReleaseGuard EKS cluster, worker instance, or VPC remains before closing the evidence session.

## Project status

- [x] Application, API, database, and frontend
- [x] Automated tests and 90% coverage gate
- [x] Docker and Docker Compose
- [x] GitHub Actions, Trivy, and GHCR
- [x] Terraform VPC and AWS EKS evidence deployment
- [x] Kubernetes and Helm
- [x] Argo CD GitOps
- [x] Prometheus and Grafana
- [x] Documentation and presentation
- [ ] Narrated MP4 walkthrough and final submission form
