#------------------------------------- EC2 security group ------------------------------
resource "aws_security_group" "sg" {
  vpc_id = var.sg_vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080     # open port (8080) for jenkins CI/CD
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9000     #SonarQubr
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22    # allow ssh to configure instance with ansible to install dependencies
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ec2_sg"
  }
}

#Create Key Pair
resource "aws_key_pair" "key_pair" {
  key_name   = "jenkins-ivolve"
  public_key = file(var.public_key_path)
}

#------------------------------------------- EC2 instance -------------------------------------------
resource "aws_instance" "jenkins_ec2" {
  ami                         = var.ec2_ami_id
  instance_type               = var.ec2_type
  subnet_id                   = var.ec2_subnet_id   
  key_name                    = aws_key_pair.key_pair.key_name  
  security_groups             = [aws_security_group.sg.id]
  associate_public_ip_address = true
  iam_instance_profile        = var.instance_profile
  
  tags = {
      Name = "jenkins_EC2"
    }
   

  provisioner "local-exec" {
    when        = create
    on_failure  = continue
    command = "echo ${self.public_ip} >> ec2-ip.txt"
 }
}