#!/bin/bash
# Show instances with a public IP address.
aws ec2 describe-instances --query "Reservations[*].Instances[?PublicIpAddress!='' && PublicIpAddress != null] | []" --output json > results/publichosts.json
