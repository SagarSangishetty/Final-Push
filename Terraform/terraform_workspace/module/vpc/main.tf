# Defining Local Variables

locals {
  common_tags = {
    Environment = var.environment
    ManagedBy = "Terraform"

  }
}

#### Creating VPC #####

resource "aws_vpc" "vpc" {
    cidr_block = var.vpc_cidr
    enable_dns_hostnames = true
    enable_dns_support = true

    tags = merge(local.common_tags, {
        Name = "${var.environment}-vpc"
        
    })  
}

##### Creating Public Subnet #####

resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.environment}-public-subnet-${count.index + 1}"
  })
}

##### Creating Private Subnet #####

resource "aws_subnet" "private" {
  count = 2

  vpc_id            = aws_vpc.vpc.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(local.common_tags, {
    Name = "${var.environment}-private-subnet-${count.index + 1}"
  })
}

##### Creating Internet Gateway #####

resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.vpc.id

    tags = merge(local.common_tags, {
      Name        = "${var.environment}-igw"
      
    })
  
}

##### Allocate an Elastic IP for the NAT Gateway #####

resource "aws_eip" "nat_eip" {
  domain = "vpc"
  tags = merge(local.common_tags, {
    Name = "${var.environment}-nat-gateway-eip"
  })
}

##### Creating Nat Gateway #####

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public[0].id

  depends_on = [aws_internet_gateway.igw]
}

##### Defining Public Route table & Route #####

resource "aws_route_table" "public_rt" {
    vpc_id = aws_vpc.vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw.id
    }

    tags = merge(local.common_tags, {
      Name = "${var.environment}-public-route-table"
      
    })
  
}

##### Defining Private Route table & Route #####

resource "aws_route_table" "private_rt" {
    vpc_id = aws_vpc.vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        nat_gateway_id =  aws_nat_gateway.nat.id
    }

    tags = merge(local.common_tags, {
      Name = "${var.environment}-private-route-table"
      
    })
  
}

##### Associate with Public Subnets ######

resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

###### Associate with Private Subnets #####

resource "aws_route_table_association" "private" {
  count = 2

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private_rt.id
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

resource "aws_security_group" "rds_sg" {
  vpc_id = aws_vpc.vpc.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    security_groups =  [aws_security_group.web_sg.id]
  }
    tags = merge(local.common_tags, {
      Name = "${var.environment}-rds_sg"
    })
}