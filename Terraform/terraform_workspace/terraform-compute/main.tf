provider "aws" {
    region = "us-east-1"
  
}

module "ec2_instance" {
    source = "../module/ec2"
        ami_value = var.ami_value
        subnet_id = data.aws_subnet.public.id
        sg = data.aws_security_group.sg-ec2.id
        key_name = var.key_name
        environment = var.environment
}

output "Public-IP" {
    value = module.ec2_instance.public-ip
}


