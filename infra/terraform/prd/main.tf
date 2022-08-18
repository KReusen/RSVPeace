module "main" {
  source      = "../modules/main"
  env         = "prd"
  domain_name = var.domain_name
}