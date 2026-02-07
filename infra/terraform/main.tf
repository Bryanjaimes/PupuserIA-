# Gateway El Salvador — AWS Infrastructure (Terraform)
#
# This will define:
#   - VPC & networking
#   - RDS (PostgreSQL + PostGIS)
#   - ElastiCache (Redis)
#   - ECS/Fargate for backend services
#   - SageMaker endpoints for AI inference
#   - S3 for assets and model artifacts
#   - CloudFront CDN
#   - Route53 DNS
#   - IAM roles and policies

terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }

  backend "s3" {
    bucket = "gateway-es-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "GatewayElSalvador"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# TODO: Add resource definitions as we deploy
