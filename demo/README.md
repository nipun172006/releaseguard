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

The AWS resources have already been destroyed. Do **not** recreate them for the video; show the saved evidence instead.

## Manual screenshots still required

Capture these yourself so the final evidence set covers every grading category. Save each PNG in `demo/evidence/` with the suggested filename.

1. **Tests — `tests-passed.png`**
   - Open the successful GitHub Actions run or run `cd backend && .venv/bin/python -m pytest` if the local test database is available.
   - Capture the passing test count and the coverage result.
2. **Git history — `git-commits.png`**
   - Open <https://github.com/nipun172006/releaseguard/commits/main/>.
   - Capture the recent meaningful commits.
3. **Docker Compose — `docker-compose.png`**
   - Run `docker compose ps` from the repository root.
   - Capture the healthy frontend, backend, and database containers.
4. **CI/CD and Trivy — `github-actions.png`**
   - Open <https://github.com/nipun172006/releaseguard/actions> and select the successful run for commit `9f67199`.
   - Capture the green test, build, Trivy scan, and publish jobs.
5. **GHCR packages — `ghcr-packages.png`**
   - Open the repository's Packages section.
   - Capture both `releaseguard-backend` and `releaseguard-frontend` images.
6. **Prometheus — `prometheus-target-up.png`**
   - Open <http://127.0.0.1:9090/targets?pool=releaseguard-backend>.
   - Capture `releaseguard-backend`, `1 / 1 up`, and state `UP` in one image.
7. **Grafana — `grafana-dashboard.png`**
   - Open <http://127.0.0.1:3000> and select **ReleaseGuard Application Metrics**.
   - Generate a little traffic by refreshing <http://127.0.0.1:5173> several times, then capture the three populated panels.

If a local page does not open, check whether its port-forward is still running before changing any configuration.

## Final video

Record a narrated MP4 using the order and wording in [DEMO_SCRIPT.md](DEMO_SCRIPT.md). Put the exported file in this folder, for example:

```text
demo/ReleaseGuard-Demo.mp4
```

Before submission, confirm that the repository is public, the MP4 plays with audible narration, and the Google Form contains the correct repository link.
