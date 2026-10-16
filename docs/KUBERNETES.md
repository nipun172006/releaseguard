# Kubernetes and Helm

ReleaseGuard uses Kubernetes to run the application as separate database, backend, and frontend workloads. Helm packages those Kubernetes objects into one configurable release.

## Why both Kubernetes YAML and Helm are present

`k8s/namespace.yaml` creates a dedicated `releaseguard` namespace. A namespace keeps the project's resources separate from other workloads in the same cluster.

`helm/releaseguard/` contains the application chart. `Chart.yaml` describes the package, `values.yaml` stores settings that may change, and `templates/` converts those settings into Kubernetes resources.

The chart creates:

- one PostgreSQL Deployment and ClusterIP Service;
- two backend replicas behind a ClusterIP Service;
- two frontend replicas behind a ClusterIP Service;
- one Secret for the demo database password; and
- one Ingress that sends `/api` to the backend and `/` to the frontend.

ClusterIP keeps application services internal to Kubernetes. Ingress is the single HTTP entry point and performs path-based routing.

## Local Minikube deployment

Start Minikube and enable its Nginx ingress controller:

```bash
minikube start
minikube addons enable ingress
kubectl apply -f k8s/namespace.yaml
```

Build native local images and load them into Minikube. The tag below is the
application commit currently referenced by `values-local.yaml`:

```bash
docker build -t releaseguard-backend:0a8ae30 backend
docker build -t releaseguard-frontend:0a8ae30 frontend
minikube image load releaseguard-backend:0a8ae30
minikube image load releaseguard-frontend:0a8ae30
```

Validate and install the chart:

```bash
helm lint helm/releaseguard --values helm/releaseguard/values-local.yaml
helm upgrade --install releaseguard helm/releaseguard \
  --namespace releaseguard \
  --values helm/releaseguard/values-local.yaml \
  --wait \
  --timeout 5m
```

Verify the result:

```bash
kubectl get pods -n releaseguard
kubectl get services -n releaseguard
kubectl get ingress -n releaseguard
helm list -n releaseguard
```

For a simple local browser check without changing DNS, forward the frontend Service:

```bash
kubectl port-forward -n releaseguard service/frontend 5173:8080
```

Then open `http://localhost:5173`. The Minikube ingress is tested separately to prove the path-routing requirement.

## Image configuration

`values.yaml` uses public GHCR images with an immutable full Git commit tag, which is appropriate for EKS. `values-local.yaml` overrides only the frontend and backend image locations so Minikube can use the copies loaded from this laptop.

## Configuration and secrets

The password in `values.yaml` is an obvious local-demo value, not a real credential. For a temporary external cluster, override it without committing the value:

```bash
helm upgrade --install releaseguard helm/releaseguard \
  --namespace releaseguard \
  --set-string database.password='temporary-password'
```

A production system would use an external secret manager and persistent PostgreSQL storage. The capstone chart intentionally uses temporary `emptyDir` database storage so it stays understandable and does not require an additional cloud storage driver. Data is lost if the database Pod is replaced.

## Uninstall

```bash
helm uninstall releaseguard --namespace releaseguard
kubectl delete -f k8s/namespace.yaml
```
