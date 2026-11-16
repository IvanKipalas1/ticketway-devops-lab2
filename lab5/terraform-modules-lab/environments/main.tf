
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

module "vpc" {
  source = "../../modules/vpc"

  environment    = "dev"
  vpc_cidr       = "10.0.0.0/16"
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
}

module "web_server" {
  source = "../../modules/ec2"

  environment   = "dev"
  vpc_id        = module.vpc.vpc_id
  subnet_id     = module.vpc.public_subnet_ids[0]
  instance_type = "t3.micro"
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "web_server_ip" {
  value = module.web_server.public_ip
}
