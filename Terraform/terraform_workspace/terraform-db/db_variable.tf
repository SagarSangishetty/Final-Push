variable "db_name" {
    description = "Database name details"
}

variable "db_user" {
    description = "Database User name"
}


variable "db_password" {
  sensitive = true
}



variable "environment" {
    description = "Environment details"
}