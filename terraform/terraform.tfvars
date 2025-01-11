# providers values 
profile = "osama"
region  = "us-east-1"

# network-module values
vpc_cidr = "10.0.0.0/16"

ec2_type = "m5.large"

ec2_ami_id = "ami-0e2c8caa4b6378d8c" #ubuntu AMI

public_key_path = "~/.ssh/jenkins-ec2.pub"

public_subnets = [
  { subnets_cidr = "10.0.1.0/24"
  availability_zone = "us-east-1a" },
  { subnets_cidr = "10.0.2.0/24"
  availability_zone = "us-east-1b" }
]
