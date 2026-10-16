# Argo CD GitOps

Argo CD makes Git the source of truth for the Kubernetes deployment. Instead of a person repeatedly running `helm upgrade`, Argo CD reads the ReleaseGuard chart from GitHub, renders the Kubernetes resources, and compares them with the cluster.

The single `argocd/application.yaml` resource connects four things:

- the public ReleaseGuard GitHub repository;
- the `main` branch;
- the chart in `helm/releaseguard`; and
- the `releaseguard` namespace in the current cluster.

Automated sync applies committed changes. Self-heal restores a managed resource if somebody changes it manually in the cluster. Pruning removes a managed resource when its manifest is removed from Git.

## Local installation

Install the pinned non-high-availability Argo CD release. This is the smaller official installation and is appropriate for Minikube:

```bash
kubectl create namespace argocd
kubectl apply --namespace argocd --server-side --force-conflicts \
  --filename https://raw.githubusercontent.com/argoproj/argo-cd/v3.5.5/manifests/install.yaml
kubectl wait --namespace argocd --for=condition=Ready pods --all --timeout=5m
```

Bootstrap the ReleaseGuard application once:

```bash
kubectl apply --filename argocd/application.yaml
```

After that first command, application changes are delivered through Git rather than by manually editing Kubernetes resources.

## Verify synchronization

```bash
kubectl get applications --namespace argocd
kubectl get application releaseguard --namespace argocd \
  --output=jsonpath='{.status.sync.status}{" / "}{.status.health.status}{"\n"}'
```

The expected result is `Synced / Healthy`.

The local Application uses `values-local.yaml`, whose images are already loaded into Minikube. The default `values.yaml` points to the public, immutable Git-SHA image tags in GHCR and will be used for the later EKS deployment.

Self-healing was verified locally by changing the backend Deployment from two replicas to one. Argo CD detected the cluster drift, ran an automated sync, and restored the Git-defined two replicas. This is the practical difference between storing YAML in Git and operating a GitOps reconciliation loop.

## Open the user interface

Argo CD is deliberately kept behind a ClusterIP Service, so installing it does not create a paid cloud load balancer. For local access:

```bash
kubectl port-forward --namespace argocd service/argocd-server 8081:443
```

Open `https://localhost:8081`. The initial username is `admin`; obtain the temporary password without storing it in Git:

```bash
argocd admin initial-password --namespace argocd
```

The browser may warn about Argo CD's local self-signed certificate. This certificate is only for the local demonstration and must not be treated as a production TLS setup.
