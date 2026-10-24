# ReleaseGuard AWS infrastructure

This folder creates the AWS foundation used by ReleaseGuard:

- one VPC in `ap-south-1`;
- two public subnets across two availability zones;
- one internet gateway;
- one Amazon EKS control plane; and
- one managed node group containing one `m7i-flex.large` worker node.

The design follows the course's module-based Terraform structure. It stays intentionally small: there is no NAT gateway, remote state backend, custom KMS key, extra node group, or cluster autoscaling add-on.

## Why this learning cluster uses public subnets

The course reference places worker nodes in private subnets and uses a NAT gateway for outbound traffic. That is a good production pattern, but a NAT gateway has an hourly charge. This short-lived learning cluster instead places its single worker node in the public subnets and does not create a NAT gateway. The EKS security group still controls inbound traffic to the node.

The VPC still spans two availability zones because EKS expects a multi-zone network and the grading rubric requires at least two public subnets. One `m7i-flex.large` node provided enough memory for the application, Argo CD, Prometheus, and Grafana during the credits-funded evidence run while avoiding the cost of a second worker. The request was accepted for this account in `ap-south-1`, but eligibility, pricing, and availability can vary by account and region. This trades high availability for lower cost and is appropriate only for a temporary student environment.

## What each file does

- `versions.tf` sets the Terraform and AWS provider requirements and selects the AWS region.
- `variables.tf` declares all values that may change between environments.
- `main.tf` declares the VPC and EKS modules and the shared resource tags.
- `outputs.tf` prints useful IDs and the command for connecting `kubectl`.
- `terraform.tfvars.example` documents safe example values. It must never contain AWS credentials.

Terraform loads every `.tf` file in this directory together. Splitting the configuration only makes it easier for humans to understand and maintain.

## Before running Terraform

Install Terraform, AWS CLI, and kubectl, then authenticate the AWS CLI:

```bash
aws login
aws sts get-caller-identity
```

Terraform reads the temporary AWS CLI session automatically. AWS keys are not stored in this repository.

## Validate and preview

Run these commands from this folder:

```bash
terraform fmt -recursive
terraform init
terraform validate
terraform plan -out=releaseguard.tfplan
```

`terraform init` downloads the pinned modules and provider. `terraform validate` checks that the configuration is internally valid. `terraform plan` compares the desired configuration with AWS and previews every proposed change without creating anything.

## Create and connect to the cluster

Only apply after reviewing the saved plan:

```bash
terraform apply releaseguard.tfplan
aws eks update-kubeconfig --region ap-south-1 --name releaseguard-eks
kubectl get nodes
```

The saved plan makes sure `apply` uses the exact changes that were reviewed.

## Cost warning and cleanup

The EKS control plane, EC2 worker node, EBS volume, public IPv4 address, and any load balancer can consume AWS credits or incur hourly charges. Exact prices can change. Build and test locally first, create this cluster only for the final evidence window, and then remove it:

```bash
terraform destroy
```

Wait for Terraform to report that destruction is complete before closing the terminal. Terraform state and saved plan files are local working data and are excluded from Git.
