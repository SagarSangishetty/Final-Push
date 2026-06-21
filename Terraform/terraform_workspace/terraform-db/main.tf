provider "aws" {
    region = "us-east-1"
  
}


module "Database" {
  source = "../module/db"

  db_name            = var.db_name
  db_user            = var.db_user
  db_password        = var.db_password
  environment        = var.environment

  security_group_ids = [
    data.aws_security_group.rds_sg.id
  ]

  subnet_ids         = data.aws_subnets.private_subnet.ids

  
}
  
