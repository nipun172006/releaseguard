output "aws_region" {
  description = "AWS region containing the infrastructure."
  value       = var.aws_region
}

output "vpc_id" {
  description = "ID of the VPC created for ReleaseGuard."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the two public subnets."
  value       = module.vpc.public_subnets
}

output "cluster_name" {
  description = "Name of the EKS cluster."
  value       = var.cluster_name
}

output "cluster_endpoint" {
  description = "API endpoint used by kubectl to communicate with EKS."
  value       = module.eks.cluster_endpoint
}

output "managed_node_groups" {
  description = "Logical names of the EKS managed node groups."
  value       = keys(module.eks.eks_managed_node_groups)
}

output "configure_kubectl_command" {
  description = "Command that adds this EKS cluster to the local kubeconfig."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}"
}
