vpc_cidr = "10.0.0.0/16"
environment = "dev"
ssh_allowed_cidr = ["0.0.0.0/0"]

public_subnet_cidrs = [
  "10.0.1.0/24",
  "10.0.2.0/24"
]

private_subnet_cidrs = [
  "10.0.3.0/24",
  "10.0.4.0/24"
]

availability_zones = [
  "us-east-1a",
  "us-east-1b"
]