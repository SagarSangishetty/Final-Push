output "public-ip" {
    value = {
        for name, instance in aws_instance.example :
        name => instance.public_ip
    }
  
}