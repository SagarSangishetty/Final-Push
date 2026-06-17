data "aws_subnet" "public" {
  filter {
    name   = "tag:Name"
    values = ["${var.environment}-public-subnet"]
  }
}

data "aws_security_group" "sg-ec2" {
  filter {
    name = "tag:Name"
    values = ["${var.environment}-web-sg"]
  }
  
}