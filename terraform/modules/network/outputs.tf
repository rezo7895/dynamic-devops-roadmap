output "vpc_id" {
    value = aws_vpc.vpc.id
}

# all public subnets ID
output "public_subnets_id" {
    value = aws_subnet.public_subnets[*].id
}
