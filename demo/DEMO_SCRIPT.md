# ReleaseGuard demo script

Target length: **6–8 minutes**. Keep the presentation, repository, GitHub Actions, terminal, Prometheus, and Grafana open before recording. The AWS environment is already safely destroyed, so use the saved AWS screenshots instead of creating resources again.

## Before recording

From the repository root, prepare the local evidence tabs:

```bash
kubectl config current-context
kubectl get application releaseguard -n argocd
kubectl get pods,services,ingress -n releaseguard
docker compose ps
```

Open these pages:

- Application: <http://127.0.0.1:5173>
- Prometheus target: <http://127.0.0.1:9090/targets?pool=releaseguard-backend>
- Grafana: <http://127.0.0.1:3000>
- GitHub Actions: <https://github.com/nipun172006/releaseguard/actions>

If the local services or port-forwards are no longer running, restart only the required local service. Do not recreate AWS resources.

## 1. Project overview and architecture — 60 seconds

Show slides 1–3.

Say:

> ReleaseGuard is a deployment-readiness and release-risk control center. It records five readiness checks, calculates an explainable risk score, identifies blockers, and controls the release lifecycle. A React frontend talks through Nginx to a FastAPI backend and PostgreSQL. The DevSecOps path adds GitHub Actions, Trivy, GHCR, Terraform, EKS, Helm, Argo CD, Prometheus, and Grafana.

## 2. Application and codebase — 60 seconds

Show the dashboard, create or open a release, and point to `frontend/`, `backend/`, `helm/`, `terraform/`, `.github/workflows/`, and `monitoring/` in the repository.

Say:

> The frontend gives the team a clear release decision, while the backend owns validation, scoring, risk rules, lifecycle transitions, health checks, and metrics. Infrastructure and deployment configuration are version controlled beside the application, so the whole system is reproducible.

## 3. Tests, security, and CI/CD — 75 seconds

Show the GitHub Actions workflow and the successful run for commit `9f67199`. Point out backend tests, the 90 percent coverage gate, frontend lint and build, Docker image builds, Trivy scans, and GHCR publishing.

Say:

> Every push must pass 23 backend tests, the coverage gate, frontend checks, container builds, and Trivy scanning. Only a successful main-branch run publishes backend and frontend images to GHCR. The images use the full Git commit SHA, which makes each deployment traceable and immutable.

## 4. Terraform and AWS evidence — 75 seconds

Show `terraform/main.tf`, then the saved screenshots for the Terraform plan, VPC, active EKS cluster, and healthy worker.

Say:

> Terraform created a VPC, two public subnets, IAM roles, an EKS control plane, managed add-ons, and one Free-Tier-eligible worker in Mumbai. I used a deliberately small learning architecture without a NAT gateway or cloud load balancer to control cost. The application was deployed successfully to the cluster and accessed with a temporary port-forward.

## 5. Helm, Kubernetes, and Argo CD — 60 seconds

Show:

```bash
kubectl get application releaseguard -n argocd
kubectl get pods,services,ingress -n releaseguard
```

Then show `helm/releaseguard/values.yaml` and `argocd/application.yaml`.

Say:

> Helm packages the Kubernetes Deployments, Services, Secret, probes, and Ingress. Argo CD continuously compares the cluster with Git. The application reached Synced and Healthy, and a drift test proved that self-healing restored the declared replica count.

## 6. Observability — 60 seconds

Show the Prometheus target page with `1 / 1 up`, then the populated Grafana dashboard.

Say:

> FastAPI exposes request-count and request-duration metrics. Prometheus scrapes the backend every 15 seconds, and the target is UP. Grafana uses the provisioned Prometheus data source to display total requests, request rate, and average response duration.

## 7. Cleanup and conclusion — 45 seconds

Show `demo/evidence/terraform-destroy.png` and the final slide.

Say:

> After collecting evidence, I destroyed the complete temporary AWS environment. Terraform state is empty, and independent AWS CLI checks confirm there is no ReleaseGuard EKS cluster, worker instance, or VPC remaining. This project taught me how application development, automated quality gates, immutable containers, infrastructure as code, GitOps, and observability work together in one secure delivery workflow.

## Final recording check

- Your voice is audible throughout.
- No passwords, tokens, `.env` contents, or AWS credentials are visible.
- The Prometheus target clearly reads `UP`.
- Grafana panels contain data.
- The cleanup evidence is shown.
- The exported MP4 opens and plays before you commit it.
