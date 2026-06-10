// Manages subdomains for the CVSS.

data "aws_route53_zone" "cvss" {
  provider     = aws.route-53
  name         = "clinicalgenome.org"
  private_zone = false
}

resource "aws_route53_record" "cvss" {
  provider = aws.route-53
  zone_id  = data.aws_route53_zone.cvss.id
  name     = "${terraform.workspace == "prod" ? "cvss" : "cvss-test"}.clinicalgenome.org"
  type     = "A"
  ttl      = 300

  records = [
    aws_lightsail_static_ip.cvss.ip_address
  ]
}
