# ReleaseGuard submission guide

This folder contains the editable project presentation and verified evidence for the final DevSecOps submission.

## Ready artifacts

- `ReleaseGuard-DevSecOps-Capstone-v2.pptx` — 10-slide editable presentation.
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
- `evidence/ghcr-backend.png` — public backend image with immutable commit-SHA tag.
- `evidence/ghcr-frontend.png` — public frontend image with immutable commit-SHA tag.
- `evidence/prometheus-target-up.png` — healthy `releaseguard-backend` scrape target.
- `evidence/grafana-dashboard.png` — populated application-metrics dashboard.
- `evidence/docker-compose.png` — healthy local database, backend, and frontend containers.
- `evidence/tests-passed.png` — 24 passing backend tests with the 90% coverage gate satisfied.

The AWS resources have already been destroyed. Do **not** recreate them for the video; show the saved evidence instead.

## Evidence status

The required screenshots are complete. Browser evidence is cropped to the application or service UI, and desktop command evidence is cropped to the Terminal window.

## Final video

Record a narrated MP4 using the order and wording in [DEMO_SCRIPT.md](DEMO_SCRIPT.md). Put the exported file in this folder, for example:

```text
demo/ReleaseGuard-Demo.mp4
```

Before submission, confirm that the repository is public, the MP4 plays with audible narration, and the Google Form contains the correct repository link.
