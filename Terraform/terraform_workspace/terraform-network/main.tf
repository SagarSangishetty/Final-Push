provider "aws" {
    region = "us-east-1"
  
}

module "vpc" {
    source = "../module/vpc"
    vpc_cidr = var.vpc_cidr
    public_subnet_cidr = var.public_subnet_cidr
    availability_zone = var.availability_zone
    environment = var.environment
    ssh_allowed_cidr = var.ssh_allowed_cidr
}

