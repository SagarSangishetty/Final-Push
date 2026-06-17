terraform {
  backend "s3" {
    bucket = "shettysagar-tf-statefile-bucket"
    key = "compute/terraform.tfstate"  # isolation the key so that destroy will not impact the backend bucket & db
    region = "us-east-1"
    use_lockfile = true  
  }


}