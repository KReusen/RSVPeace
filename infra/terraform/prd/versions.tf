terraform {
  required_version = "~> 1.2"

  backend "s3" {
    encrypt = true
  }

  required_providers {
    aws = {
      version = "~> 4.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.2.0"
    }
  }
}