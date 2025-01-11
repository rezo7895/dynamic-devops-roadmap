provider "aws" {
  profile  = var.profile
  region   = var.region
}

module "network" {
  source       = "./modules/network"
  vpc_cidr     = var.vpc_cidr
  public_subnets  = var.public_subnets

}

module "ec2" {
  source            = "./modules/ec2"
  sg_vpc_id         = module.network.vpc_id
  ec2_ami_id	      = var.ec2_ami_id
  public_key_path   = var.public_key_path
  ec2_subnet_id     = module.network.public_subnets_id[0]
  ec2_type  	      = var.ec2_type
  instance_profile  = module.eks.eks_profile
}

module "ecr" {
  source = "./modules/ecr"
}

module "eks" {
  source                 = "./modules/eks"
  eni_subnet_ids         = module.network.private_subnets_id
  nodegroup_subnets_id   = module.network.private_subnets_id
}

#Output to retrive EC2 instance public IP
output "ec2_public_ip" {
  value = module.ec2.ec2_public_ip
}
