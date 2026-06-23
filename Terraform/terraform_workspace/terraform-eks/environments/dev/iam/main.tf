module "iam" {
  source = "../../../modules/iam"

  project           = var.project
  environment       = var.environment
  oidc_provider_arn = data.aws_iam_openid_connect_provider.oidc.arn  # ← from eks module
  oidc_provider_url = data.aws_iam_openid_connect_provider.oidc.url  # ← from eks module
}