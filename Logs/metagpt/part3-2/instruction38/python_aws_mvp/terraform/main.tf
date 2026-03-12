terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
}

provider "aws" {
  region                  = var.aws_region
  access_key              = var.aws_access_key_id
  secret_key              = var.aws_secret_access_key
  profile                 = var.aws_profile
}

# S3 Bucket for file uploads
resource "aws_s3_bucket" "uploads" {
  bucket = var.s3_bucket_name
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Environment = var.environment
    Project     = "python_aws_mvp"
  }
}

# IAM Role for EC2/Backend
resource "aws_iam_role" "backend_role" {
  name = "${var.project_name}-backend-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# IAM Policy for S3 access
resource "aws_iam_policy" "s3_policy" {
  name        = "${var.project_name}-s3-policy-${var.environment}"
  description = "Allow backend to access S3 bucket for uploads"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.uploads.arn,
          "${aws_s3_bucket.uploads.arn}/*"
        ]
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "backend_s3_attach" {
  role       = aws_iam_role.backend_role.name
  policy_arn = aws_iam_policy.s3_policy.arn
}

# EC2 Instance for Python backend (for MVP, single instance)
resource "aws_instance" "backend" {
  ami                    = var.ec2_ami_id
  instance_type          = var.ec2_instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.backend_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.backend_profile.name

  tags = {
    Name        = "${var.project_name}-backend-${var.environment}"
    Environment = var.environment
    Project     = "python_aws_mvp"
  }

  user_data = <<-EOF
    #!/bin/bash
    cd /home/ec2-user/app
    export ENVIRONMENT=${var.environment}
    export AWS_S3_BUCKET=${var.s3_bucket_name}
    export STRIPE_API_KEY=${var.stripe_api_key}
    export SENTRY_DSN=${var.sentry_dsn}
    export JWT_SECRET_KEY=${var.jwt_secret_key}
    # Start backend (assume using uvicorn)
    nohup uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
  EOF
}

# IAM Instance Profile for EC2
resource "aws_iam_instance_profile" "backend_profile" {
  name = "${var.project_name}-backend-profile-${var.environment}"
  role = aws_iam_role.backend_role.name
}

# Security Group for backend
resource "aws_security_group" "backend_sg" {
  name        = "${var.project_name}-backend-sg-${var.environment}"
  description = "Allow HTTP/HTTPS traffic to backend"
  vpc_id      = var.vpc_id

  ingress {
    description      = "Allow HTTP"
    from_port        = 8000
    to_port          = 8000
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    description      = "Allow HTTPS"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    description      = "Allow all outbound"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Project     = "python_aws_mvp"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/python_aws_mvp/${var.environment}/app"
  retention_in_days = 14

  tags = {
    Environment = var.environment
    Project     = "python_aws_mvp"
  }
}

# Outputs
output "s3_bucket_name" {
  value = aws_s3_bucket.uploads.bucket
}

output "backend_instance_public_ip" {
  value = aws_instance.backend.public_ip
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.app_logs.name
}