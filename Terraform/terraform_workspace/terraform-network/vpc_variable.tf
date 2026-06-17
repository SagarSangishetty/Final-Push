variable "vpc_cidr" {
    description = "Cidr value for vpc"
  
}

variable "public_subnet_cidr" {
    description = "Cidr for Public Subnet"
  
}

variable "availability_zone" {
    description = "Avaliability zone details"
  
}

variable "environment" {
    description = "Define the environment"
  
}

variable "ssh_allowed_cidr" {
    type = list(string)
    description = "Allowed Cird block"
  
}