
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0516089d963059a51"
  instance_type = "t3.micro"

  tags = {
    Name = "lab-instance"
  }
}

output "public_ip" {
  value = aws_instance.web.public_ip
}
