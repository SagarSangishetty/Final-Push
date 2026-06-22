data "aws_subnets" "cluster_private_subnet" {
    filter {
      name = "tag:Tier"
      values = [ "private" ]
    }
  
}

data "aws_vpc" "cluster_vpc" {
    filter {
     name =  "tag:Name"
     values = [ "${var.project}-${var.environment}-vpc" ]

    }
    
}

