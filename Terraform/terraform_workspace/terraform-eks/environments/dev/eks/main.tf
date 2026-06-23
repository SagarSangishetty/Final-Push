# environments/dev/main.tf
module "eks" {
  source = "../../../modules/eks"

  project             = var.project
  environment         = var.environment
  cluster_name        = var.cluster_name
  cluster_version     = var.cluster_version
  vpc_id              = data.aws_vpc.cluster_vpc.id          # ← from vpc data output
  private_subnet_ids  = data.aws_subnets.cluster_private_subnet.ids  # ← from vpc data output
  node_instance_type  = var.node_instance_type
  node_desired_size   = var.node_desired_size
  node_min_size       = var.node_min_size
  node_max_size       = var.node_max_size
  allowed_cidr_blocks = var.allowed_cidr_blocks
}