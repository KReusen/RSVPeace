resource "aws_dynamodb_table" "rsvpeace" {
  name         = "${local.project_name}_${var.env}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "event_slug"
  range_key    = "details"

  attribute {
    name = "event_slug"
    type = "S"
  }

  attribute {
    name = "details"
    type = "S"
  }

  tags = merge({ Name = "${local.project_name}_${var.env}" }, local.tags)
}