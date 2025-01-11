 # VPC
resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "osama-VPC"
  }
}

# elastic IP
resource "aws_eip" "eip" {
  domain   = "vpc"
}

# internet gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name = "osama-IGW"
  }
}

# NAT in public subnet
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.eip.id
  subnet_id     = aws_subnet.public_subnets[1].id
  tags = {
    Name = "osama-NAT"
  }

  depends_on = [aws_internet_gateway.igw]
}

# ----------------------------- Public ------------------------------------------------------------------#

# public subnets
resource "aws_subnet" "public_subnets" {
  count             = length(var.public_subnets)
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = var.public_subnets[count.index].subnets_cidr
  availability_zone = var.public_subnets[count.index].availability_zone
  tags = {
    Name = "osama_public_subnet_${count.index}"
  }
}

# public route table 
resource "aws_route_table" "public-rt" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

# Assign the public route table to public subnets
resource "aws_route_table_association" "public-rta" {
  count          = length(aws_subnet.public_subnets)
  subnet_id      = aws_subnet.public_subnets[count.index].id
  route_table_id = aws_route_table.public-rt.id
}
# ----------------------------- Private ------------------------------------------------------------------#

# private subnets
resource "aws_subnet" "private_subnets" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = var.private_subnets[count.index].subnets_cidr
  availability_zone = var.private_subnets[count.index].availability_zone
  tags = {
    Name = "osama_private_subnet_${count.index}"
  }
}

# private route table 
resource "aws_route_table" "private-rt" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
}

# Assign the private route table to private subnets
resource "aws_route_table_association" "private-rta" {
  count          = length(aws_subnet.private_subnets)
  subnet_id      = aws_subnet.private_subnets[count.index].id   
  route_table_id = aws_route_table.private-rt.id
}