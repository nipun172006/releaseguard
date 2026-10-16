variable "aws_region" {
  description = "AWS region in which ReleaseGuard infrastructure will be created."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Short project name used in resource names and tags."
  type        = string
  default     = "releaseguard"
}

variable "environment" {
  description = "Environment name used in resource names and tags."
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "Name of the Amazon EKS cluster."
  type        = string
  default     = "releaseguard-eks"
}

variable "kubernetes_version" {
  description = "Kubernetes control-plane version for Amazon EKS."
  type        = string
  default     = "1.35"
}

variable "vpc_cidr" {
  description = "Private IPv4 address range used by the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Two availability zones used to keep the cluster resilient."
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR ranges for the two internet-facing subnets."
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "node_instance_type" {
  description = "EC2 instance type used by the EKS managed node group."
  type        = string
  default     = "t3.large"
}

variable "node_min_size" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 1
}

variable "node_desired_size" {
  description = "Number of worker nodes Terraform initially requests."
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 2
}
