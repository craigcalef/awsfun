#!/bin/bash
instanceid=$(aws ec2 describe-instances --filter "Name=tag:Name,Values=$1"  --query "Reservations[].Instances[].InstanceId" --output text)
aws ec2 create-tags --resources $instanceid --tags $2
