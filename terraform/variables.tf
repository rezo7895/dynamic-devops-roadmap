# provider variables 
variable "profile" {
  type = string
}
variable "region" {
  type = string
}

variable "ec2_type" {
  description = "ec2 instance type"
  type        = string
}

#EC2 module variable
variable "public_key_path" {
  description = "path of public key which will be used in EC2 key pair"
  type 	      = string
}

variable "ec2_ami_id" {
  description = "ID of the EC2 instance AMI"
  type        = string
}


# network-module variables
variable "vpc_cidr" {}

variable "public_subnets" {
  type = list(object({
    subnets_cidr      = string
    availability_zone = string
  }))
}

# variable "private_subnets" {
#   type = list(object({
#     subnets_cidr      = string
#     availability_zone = string
#   }))
# }