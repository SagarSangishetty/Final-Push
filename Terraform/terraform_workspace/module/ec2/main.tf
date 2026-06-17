
#Creating basic Ec2 instance

locals {
  instance = {
    app1 = {
        instance_type = var.environment == "dev" ? "t3.micro" : "t3.small"
    }
    
    app2 = {
        instance_type = var.environment == "dev" ? "t3.micro" : "t3.small"
    }

    app3 = {
        instance_type = var.environment == "dev" ? "t3.micro" : "t3.small"
    }
  }
}


resource "aws_instance" "example" {
    for_each = local.instance
    ami = var.ami_value
    subnet_id = var.subnet_id
    instance_type = each.value.instance_type
    vpc_security_group_ids = [ var.sg ]
    key_name = var.key_name

tags = {
    Name = "${var.environment}-${each.key}"
    }
}


