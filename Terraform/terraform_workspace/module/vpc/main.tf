# Defining Local Variables

locals {
  common_tags = {
    Environment = var.environment
    ManagedBy = "Terraform"

  }
}

#Creating Resource 

resource "aws_vpc" "vpc" {
    cidr_block = var.vpc_cidr
    enable_dns_hostnames = true
    enable_dns_support = true

    tags = merge(local.common_tags, {
        Name = "${var.environment}-vpc"
        
    })  
}

resource "aws_subnet" "public-subnet" {
    vpc_id = aws_vpc.vpc.id
    cidr_block = var.public_subnet_cidr
    availability_zone = var.availability_zone
    map_public_ip_on_launch = true

    tags = merge(local.common_tags, {
        Name        = "${var.environment}-public-subnet"
        
    })  
}

resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.vpc.id

    tags = merge(local.common_tags, {
      Name        = "${var.environment}-igw"
      
    })
  
}

resource "aws_route_table" "rt" {
    vpc_id = aws_vpc.vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw.id
    }

    tags = merge(local.common_tags, {
      Name = "${var.environment}-public-route-table"
      
    })
  
}

resource "aws_route_table_association" "public-assoc" {
    subnet_id = aws_subnet.public-subnet.id
    route_table_id = aws_route_table.rt.id
  
}

resource "aws_security_group" "web_sg" {
  vpc_id = aws_vpc.vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidr
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidr
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.ssh_allowed_cidr
  }

  tags = merge(local.common_tags, {
    Name        = "${var.environment}-web-sg"
    
  })
}

