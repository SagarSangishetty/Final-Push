data "aws_subnets" "private_subnet" {
    filter {
        name = "tag:Name"
        values = [
                    "${var.environment}-private-subnet-1",
                    "${var.environment}-private-subnet-2"
        ]
        
    }
  
}

data "aws_security_group" "rds_sg" {
    filter {
      name = "tag:Name"
      values = ["${var.environment}-rds_sg"]
    }
  
}