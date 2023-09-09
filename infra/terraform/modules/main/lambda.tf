data "archive_file" "zipped_lambda_code" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../src/"
  output_path = "${path.module}/../../../../.dist/packaged_lambda.zip"
}

resource "aws_lambda_function" "rsvpeace_handler" {
  description      = "Shows rsvp forms to invited attendees"
  filename         = data.archive_file.zipped_lambda_code.output_path
  function_name    = local.lambda_function_name
  role             = aws_iam_role.lambda_iam.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.zipped_lambda_code.output_base64sha256
  runtime          = "python3.11"
  memory_size      = 128
  timeout          = 5
  architectures    = ["arm64"]

  environment {
    variables = {
      LOG_LEVEL      = "DEBUG"
      ENVIRONMENT    = var.env
      RSVPEACE_TABLE = aws_dynamodb_table.rsvpeace.name
    }
  }

  tags = local.tags
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = 14

  tags = local.tags
}
