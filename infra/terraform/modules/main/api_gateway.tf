resource "aws_apigatewayv2_api" "api" {
  name          = "rsvpeace-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "call_rsvpeace" {
  api_id             = aws_apigatewayv2_api.api.id
  integration_type   = "AWS_PROXY"
  description        = "Call rsvpeace lambda"
  integration_method = "POST" # This is required to be POST in combination with AWS_PROXY, but our route is overwriting this
  integration_uri    = aws_lambda_function.rsvpeace_handler.invoke_arn
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.call_rsvpeace.id}"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id = aws_apigatewayv2_api.api.id
  name   = var.env
}

resource "aws_apigatewayv2_deployment" "deployment" {
  api_id = aws_apigatewayv2_api.api.id

  triggers = {
    redeployment = sha1(join(",", tolist([
      jsonencode(aws_apigatewayv2_integration.call_rsvpeace),
      jsonencode(aws_apigatewayv2_route.route)
    ])))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_apigatewayv2_domain_name" "domain_name" {
  domain_name = "*.${var.domain_name}"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_route53_record" "route53_to_apigw" {
  name    = aws_apigatewayv2_domain_name.domain_name.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.hosted_zone.zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.domain_name.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.domain_name.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_apigatewayv2_api_mapping" "api_mapping" {
  api_id      = aws_apigatewayv2_api.api.id
  domain_name = aws_apigatewayv2_domain_name.domain_name.id
  stage       = aws_apigatewayv2_stage.stage.id
}
