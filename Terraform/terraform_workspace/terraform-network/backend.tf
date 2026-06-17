terraform {
  backend "s3" {
    bucket       = "shettysagar-tf-statefile-bucket"
    key          = "network/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true   # S3-native locking, no DynamoDB needed
  }
}