# ReleaseGuard project artifacts

This folder contains the editable project presentation and the evidence captured while validating the delivery workflow.

## Ready artifacts

- [`VIDEO.md`](VIDEO.md) — link to the presentation and project demonstration.
- `ReleaseGuard-DevSecOps-Capstone.pptx` — 10-slide editable presentation.
- `evidence/aws-vpc.png` — temporary AWS VPC.
- `evidence/aws-eks-cluster.png` — active EKS control plane.
- `evidence/aws-eks-worker.png` — healthy managed worker.
- `evidence/terraform-plan.png` — Terraform execution plan.
- `evidence/terraform-destroy.png` — verified cleanup of Terraform state, EKS, EC2, and VPC.
- `evidence/eks-kubernetes-helm.png` — Helm release and Kubernetes resources.
- `evidence/eks-application.png` — application running through the EKS port-forward.
- `evidence/local-kubernetes-argocd.png` — local Kubernetes resources and Argo CD health.
- `evidence/backend-metrics.png` — application Prometheus metrics.
- `evidence/git-commits.png` — meaningful Git history and passing commit checks.
- `evidence/github-actions.png` — successful tests, frontend checks, image builds, security scans, and publishing.
- `evidence/trivy-scan.png` — successful HIGH/CRITICAL vulnerability scans for both runtime images.
- `evidence/ghcr-backend.png` — public backend image with immutable commit-SHA tag.
- `evidence/ghcr-frontend.png` — public frontend image with immutable commit-SHA tag.
- `evidence/prometheus-target-up.png` — healthy `releaseguard-backend` scrape target.
- `evidence/grafana-dashboard.png` — populated application-metrics dashboard.
- `evidence/docker-compose.png` — healthy local database, backend, and frontend containers.
- `evidence/tests-passed.png` — 24 passing backend tests with the 90% coverage gate satisfied.

The temporary AWS resources were destroyed after verification. The screenshots preserve the deployment and cleanup results.

## Evidence notes

Browser images focus on the application or service UI. Command-line evidence focuses on the relevant terminal output.
