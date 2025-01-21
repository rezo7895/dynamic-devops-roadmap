#Output to retrive EC2 instance ID
output "ec2_public_ip" {
  value = aws_instance.jenkins_ec2.public_ip
}