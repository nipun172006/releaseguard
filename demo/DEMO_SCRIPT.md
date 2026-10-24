# ReleaseGuard demo script

Target length: **7–8 minutes**. The official order is presentation, codebase, live CI/CD push, Terraform and AWS, Argo CD, Kubernetes, Prometheus, and Grafana. The AWS environment is already safely destroyed, so use the saved evidence instead of creating resources again.

## Before recording

1. Replace `not recorded yet` in [`RECORDING_NOTE.md`](RECORDING_NOTE.md) with the real recording date, but do not commit it yet. This is the small truthful change that will trigger the pipeline during the recording.
2. Close unrelated browser tabs, chat windows, notifications, and any page that exposes a password, token, account ID, or `.env` value.
3. Open the presentation, repository, GitHub Actions, application, Prometheus, Grafana, and evidence folder in the order used below.
4. Make sure the local Kubernetes context and required port-forwards are running. Do not recreate AWS.

Useful checks from the repository root:

```bash
git status --short
kubectl config current-context
kubectl get application releaseguard -n argocd
kubectl get pods,services,ingress -n releaseguard
```

Open these pages:

- Application: <http://127.0.0.1:5173>
- Prometheus target: <http://127.0.0.1:9090/targets?pool=releaseguard-backend>
- Grafana: <http://127.0.0.1:3000>
- GitHub Actions: <https://github.com/nipun172006/releaseguard/actions/workflows/ci-cd.yml>

If a monitoring page is unavailable, start its port-forward in a separate terminal:

```bash
kubectl port-forward --namespace monitoring service/prometheus-server 9090:80
kubectl port-forward --namespace monitoring service/grafana 3000:80
```

## 1. Present all slides — 75 seconds

Show all 10 slides in slideshow mode. Spend only a few seconds on each slide so the presentation is completed before the live demonstration.

Say:

> ReleaseGuard is a deployment-readiness and release-risk control center. It records five readiness checks, calculates an explainable score and risk level, identifies blockers, and controls a release from draft to a final outcome. The application uses React, FastAPI, and PostgreSQL. Around it, the DevSecOps workflow uses GitHub Actions, Trivy, GHCR, Terraform, Amazon EKS, Helm, Argo CD, Prometheus, and Grafana. I will now show how these parts work together and the verified evidence from the temporary AWS deployment.

## 2. Application and codebase — 60 seconds

Show the dashboard. Open a production release with incomplete checks, point out its score, risk, and blockers, then complete the checks and show the safe lifecycle actions. Briefly show `frontend/`, `backend/`, `.github/workflows/`, `terraform/`, `helm/`, `argocd/`, and `monitoring/` in GitHub.

Say:

> The frontend gives the team one clear release decision. The FastAPI backend owns validation, scoring, risk rules, lifecycle transitions, health checks, and metrics, while PostgreSQL stores release records. A production release cannot become ready until every mandatory check passes. The infrastructure and deployment files live beside the application, so the complete system is version controlled and reproducible.

## 3. Trigger and explain CI/CD — 90 seconds

Show the prepared change first:

```bash
git diff -- demo/RECORDING_NOTE.md
git add demo/RECORDING_NOTE.md
git commit -m "docs: record final demo"
git push origin main
```

Open GitHub Actions and show the new run starting. Explain the job graph, then continue the demo while it runs. Return to it in the final section.

Say:

> This real push automatically starts the CI/CD workflow. The backend job creates a test PostgreSQL service, runs migrations, executes 24 tests, and enforces at least 90 percent coverage. The frontend job runs linting and creates the production build. Only after both quality jobs pass does the matrix build the two Docker images, scan them with Trivy for fixable high and critical vulnerabilities, and publish successful main-branch images to GHCR using the full Git commit SHA. That immutable tag connects each image to its exact source revision.

## 4. Terraform and AWS evidence — 60 seconds

Show `terraform/main.tf`, `terraform plan`, and these saved screenshots: VPC, active EKS cluster, healthy worker, and EKS-hosted application.

Say:

> Terraform created the AWS foundation in Mumbai: one VPC, two public subnets in different availability zones, an internet gateway, IAM roles, an EKS control plane, managed add-ons, and one worker. I kept one worker and avoided a NAT gateway and cloud load balancer to reduce temporary credit usage. This was a learning architecture rather than a production high-availability design. The application was successfully deployed to EKS and reached through a temporary port-forward.

## 5. Helm, Kubernetes, and Argo CD — 60 seconds

Show the saved Kubernetes and Argo CD evidence, then briefly show `helm/releaseguard/values.yaml` and `argocd/application.yaml`. If the local cluster is running, also show:

```bash
kubectl get application releaseguard -n argocd
kubectl get pods,services,ingress -n releaseguard
```

Say:

> Helm packages the PostgreSQL, backend, and frontend Deployments together with their Services, Secret, health probes, and Ingress. Kubernetes keeps the requested replicas running and connects them through internal Services. Argo CD continuously compares the cluster with the Helm configuration in Git. The application reached Synced and Healthy, and a drift test proved self-healing by restoring a manually changed replica count.

## 6. Prometheus and Grafana — 60 seconds

Show the Prometheus target with `1 / 1 up`, then the populated **ReleaseGuard Application Metrics** Grafana dashboard.

Say:

> FastAPI exposes Prometheus-formatted request counters and duration measurements at the metrics endpoint. Prometheus scrapes the backend every 15 seconds, and this target is UP. Grafana reads that data through its provisioned Prometheus data source and displays total requests, request rate, and average request duration. This provides visibility after deployment instead of treating deployment as the end of the workflow.

## 7. Pipeline result, cleanup, and conclusion — 45 seconds

Return to GitHub Actions and show the live run green. If it is still running, wait for it to finish; use the recorder's pause feature if necessary, then resume on the completed run. This makes the push-to-result path visible end to end. Then show `demo/evidence/terraform-destroy.png`.

Say:

> The pushed change has passed the same automated quality and security gates used for every release. After collecting the cloud evidence, I destroyed all Terraform-managed resources. Terraform state is empty, and independent AWS CLI checks confirmed that the ReleaseGuard EKS cluster, worker, and VPC were removed. ReleaseGuard demonstrates how application logic, tests, secure containers, infrastructure as code, Kubernetes, GitOps, and observability form one traceable delivery workflow.

## Final recording check

- All 10 slides appear before the live walkthrough.
- The recording includes the real push and the resulting GitHub Actions run.
- Your voice is clear, and the mouse movement is slow enough to follow.
- No passwords, tokens, `.env` contents, account IDs, unrelated tabs, or notifications are visible.
- Prometheus clearly shows the backend target as `UP`.
- Grafana panels contain data.
- Terraform cleanup evidence is shown.
- The exported MP4 opens and plays before you commit it to `demo/`.
