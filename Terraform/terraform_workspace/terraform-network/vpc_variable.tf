variable "vpc_cidr" {
    description = "Cidr value for vpc"
  
}

variable "public_subnet_cidrs" {
  type = list(string)
}

variable "private_subnet_cidrs" {
  type = list(string)
}

variable "availability_zones" {
  type = list(string)
}

variable "environment" {
    description = "Define the environment"
  
}

variable "ssh_allowed_cidr" {
    type = list(string)
    description = "Allowed Cird block"
  
}

