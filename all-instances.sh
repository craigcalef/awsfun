#!/bin/bash
for D in `aws ec2 describe-regions --query "Regions[*].RegionName" --output text`; do 
	echo $D
	aws ec2 describe-instances --region $D > results/$D.json
done
