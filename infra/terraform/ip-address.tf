// Attaches a static IP address to the Lightsail instance.

resource "aws_lightsail_static_ip_attachment" "cvss" {
  provider       = aws.stanford-clingen-projects
  instance_name  = aws_lightsail_instance.cvss.id
  static_ip_name = aws_lightsail_static_ip.cvss.id
}

resource "aws_lightsail_static_ip" "cvss" {
  name     = "cvss-ip-${terraform.workspace}"
  provider = aws.stanford-clingen-projects
}
