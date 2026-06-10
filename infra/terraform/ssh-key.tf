// Adds our SSH key for Ansible.

resource "aws_lightsail_key_pair" "cvss" {
  name       = "ansible-key-cvss-${terraform.workspace}"
  public_key = file("~/.ssh/cvss_ansible_${terraform.workspace}_ed25519.pub")
}