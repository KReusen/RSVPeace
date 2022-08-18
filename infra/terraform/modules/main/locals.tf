locals {
  project_name = "rsvpeace"
  tags = {
    Project     = local.project_name
    Environment = var.env
  }
  lambda_function_name              = "${local.project_name}_${var.env}"
  sid_friendly_lambda_function_name = replace(title(local.lambda_function_name), "_", "")
}