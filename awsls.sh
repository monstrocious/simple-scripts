#!/bin/bash

#Prints All EC2 instances in your region


#Make sure your instance has an ec2:describe* role IAM"
# {
#            "Effect": "Allow",
#            "Action": "ec2:Describe*",
#            "Resource": "*"
#        },



aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType,PrivateIpAddress,PublicIpAddress,Tags[?Key==`Name`].Value[]]' --output json | tr -d '\n[] "' | perl -pe 's/i-/\ni-/g' | tr ',' '\t' | sed -e 's/null/None/g' | grep '^i-' | column -t
