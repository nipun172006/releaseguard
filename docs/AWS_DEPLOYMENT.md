# Verified AWS deployment

ReleaseGuard was deployed to a temporary Terraform-managed Amazon EKS environment in `ap-south-1` on 16 October 2026. The environment is intentionally short-lived so that final-project evidence can be captured and the resources can then be destroyed.

## Infrastructure evidence

Terraform created and managed:

- VPC `vpc-07d8a22b6d817ee0b` with CIDR `10.20.0.0/16`.
- Public subnets `subnet-05ca12a2baa7a7867` and `subnet-0c6c7906c46177358` in two availability zones.
- EKS cluster `releaseguard-eks` running Kubernetes `1.35`.
- Managed node group `releaseguard-eks-nodes-73341352949edd9eab6db030f5`.
- One healthy `m7i-flex.large` worker, instance `i-0ba775360e1f04fb2`.
- Standard VPC CNI, CoreDNS, and kube-proxy EKS add-ons.

The successful apply ended with:

```text
Apply complete! Resources: 3 added, 0 changed, 0 destroyed.
```

Only three resources appear in that final retry because the VPC, EKS control plane, IAM resources, networking, and VPC CNI had already completed during the initial apply.

## Application evidence

The repository's Helm chart was installed directly on EKS:

```bash
helm upgrade --install releaseguard helm/releaseguard \
  --namespace releaseguard \
  --create-namespace \
  --wait --timeout 8m
```

The verified cloud workload contained two available frontend replicas, two available backend replicas, one PostgreSQL pod, three ClusterIP Services, and live EndpointSlices. The API returned:

```json
{"status":"healthy","service":"ReleaseGuard API","environment":"production"}
```

For the demonstration, a local port-forward exposes the cloud frontend without creating a chargeable AWS load balancer:

```bash
kubectl port-forward -n releaseguard svc/frontend 5174:8080
```

## Failure found and corrected

The first node-group request used `t3.large`. This account's AWS Free plan rejected it even though promotional credits remained. The Auto Scaling activity log reported:

```text
InvalidParameterCombination - The specified instance type is not eligible for Free Tier.
```

The failed node group launched no EC2 instance. It was removed, the instance types accepted for this account were queried with the AWS CLI, and the configuration was changed to `m7i-flex.large`. AWS accepted the replacement request in `ap-south-1`, and the worker became healthy in about one minute. This records what happened in this temporary, credits-funded evidence run; it is not a universal free-tier guarantee.

This is why the instance type is a Terraform variable: account eligibility, pricing, and regional availability can change, while the infrastructure design remains the same.

## Verified safe teardown

After the AWS console and workload evidence were recorded, Terraform planned the destruction of all 46 managed resources:

```bash
cd terraform
terraform plan -destroy
terraform destroy
```

The first destroy run removed the EKS node group, control plane, IAM resources, subnets, security groups, and add-ons. A transient DNS lookup failure stopped the command before the final internet gateway and VPC deletion. Running the same destroy command again removed those final two resources and reported:

```text
Destroy complete! Resources: 2 destroyed.
```

Cleanup was then verified with four independent checks:

- `terraform state list` returned no managed resources.
- `aws eks list-clusters --region ap-south-1` returned no ReleaseGuard cluster.
- the `Project=releaseguard` VPC query returned an empty list.
- the running/stopped EC2 query returned no ReleaseGuard worker instances.

The verification is saved in [the Terraform destroy evidence screenshot](../demo/evidence/terraform-destroy.png). Terraform state files and saved plans are intentionally ignored by Git because they are local operational data.
