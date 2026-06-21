provider "aws" {
    region = "us-east-1"
  
}

#Subnet Group for database

resource "aws_db_subnet_group" "rds_subnet_grp" {
  name = "${var.environment}-db-subnet-group"

  subnet_ids =  var.subnet_ids

  tags = {
    Name = "${var.environment}-rds_subnet-group" 
  }
}

resource "aws_db_instance" "MySql" {
  identifier             = var.db_name
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = var.environment == "prod" ? "db.t4g.micro" : "db.t4g.micro"

  allocated_storage      = 20

  username               = var.db_user
  password               = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_grp.name

  vpc_security_group_ids = var.security_group_ids

  publicly_accessible    = false

  skip_final_snapshot    = true

  tags = {
    Name = "${var.environment}-mysqldb"
  }


}