variable "db_name" {
    description = "Database name details"
}

variable "db_user" {
    description = "Database User name"
}

variable "subnet_ids" {
    type = list(string)
    description = "Private subnet ip to fetch"
}

variable "security_group_ids" {
  type = list(string)
}


variable "db_password" {
  sensitive = true
}


variable "environment" {
    description = "Enviromnet details"
}