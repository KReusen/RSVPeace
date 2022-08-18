data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_iam" {
  name               = "${local.lambda_function_name}_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
  tags               = local.tags
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "${local.lambda_function_name}_policy"
  policy = data.aws_iam_policy_document.lambda_policies_document.json
}

data "aws_iam_policy_document" "lambda_policies_document" {
  statement {
    sid = "${local.sid_friendly_lambda_function_name}CloudwatchLogsPermissions"
    actions = [
      "logs:CreateLogGroup*",
      "logs:CreateLogStream*",
      "logs:PutLogEvents*"
    ]
    resources = ["${aws_cloudwatch_log_group.lambda_logs.arn}*"]
  }

  statement {
    sid = "${local.sid_friendly_lambda_function_name}DynamoDBPermissions"
    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:UpdateItem"
    ]
    resources = [
      aws_dynamodb_table.rsvpeace.arn
    ]
  }
}

resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_iam.id
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id   = "AllowExecutionFromAPIGateway"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.rsvpeace_handler.function_name
  principal      = "apigateway.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
}