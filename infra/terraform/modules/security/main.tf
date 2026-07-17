variable "project_name" { type = string }
variable "vpc_id" { type = string }

resource "aws_security_group" "instance" {
  name        = "${var.project_name}-instance-sg"
  description = "Application instance security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "instance_security_group_id" { value = aws_security_group.instance.id }
