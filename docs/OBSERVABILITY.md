# Prometheus and Grafana

ReleaseGuard exposes Prometheus-formatted application metrics at `GET /metrics`. The backend records the total number of HTTP requests and their duration. Requests made by Prometheus to `/metrics` are excluded so monitoring traffic does not inflate the application numbers.

Prometheus collects those measurements every 15 seconds. Grafana queries Prometheus and presents the pre-provisioned **ReleaseGuard Application Metrics** dashboard containing total requests, request rate, and average request duration.

## Why the monitoring installation is small

The local values install one Prometheus server and one Grafana server for application-level monitoring. Alertmanager, Pushgateway, node-exporter, kube-state-metrics, and persistent volumes are disabled because this environment does not use them. This keeps Minikube resource-conscious.

## Install

```bash
kubectl create namespace monitoring

helm upgrade --install prometheus \
  oci://ghcr.io/prometheus-community/charts/prometheus \
  --version 29.37.0 \
  --namespace monitoring \
  --values monitoring/prometheus-values.yaml \
  --wait --timeout 5m

helm upgrade --install grafana \
  oci://ghcr.io/grafana-community/helm-charts/grafana \
  --version 14.0.0 \
  --namespace monitoring \
  --values monitoring/grafana-values.yaml \
  --wait --timeout 5m
```

Both Services remain internal `ClusterIP` resources, so they do not create cloud load balancers.

## Verify

Confirm the backend output:

```bash
kubectl port-forward --namespace releaseguard service/backend 8000:8000
curl http://localhost:8000/metrics
```

Open Prometheus and visit **Status → Target health**. The `releaseguard-backend` target must show `UP`:

```bash
kubectl port-forward --namespace monitoring service/prometheus-server 9090:80
```

Open Grafana and select **Dashboards → ReleaseGuard → ReleaseGuard Application Metrics**:

```bash
kubectl port-forward --namespace monitoring service/grafana 3000:80
```

The username is `admin`. Retrieve the generated local password without committing it:

```bash
kubectl get secret grafana --namespace monitoring \
  --output jsonpath='{.data.admin-password}' | base64 --decode
```

## Local-data limitation

Prometheus and Grafana use temporary storage in this learning setup. Their collected data and local settings are lost if their pods are replaced. The dashboard and data-source definitions remain safe because Helm recreates them from the committed values files.
