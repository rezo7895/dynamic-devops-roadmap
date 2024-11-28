resource "aws_s3_bucket" "terraform_state" {
  bucket = "project-remote-statefile"
  lifecycle {
    # prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "enable" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "project-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}

#  terraform {
#      backend "s3" {
#          bucket         = "project-remote-statefile"
#          key            = "terraform.tfstate"
#          region         = "us-east-1"
#          dynamodb_table = "project-locks"
#          encrypt        = true
#      }
#  }