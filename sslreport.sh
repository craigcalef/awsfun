#!/bin/bash
# Generate a report of instances in specified regions and the subject of the SSL certificates
# they are using on the default HTTPS port.
for R in $1; do 
	aws ec2 describe-instances --region $R --query "Reservations[*].Instances[?PublicIpAddress!='' && PublicIpAddress != null] | [].[PublicIpAddress, InstanceId, Tags[?Key=='Name'].Value | [0]]" --output text > /tmp/hosts.tsv
    for D in `cut -f1 /tmp/hosts.tsv`; do 
		openssl s_client -connect $D:443 -showcerts > /tmp/sclient.out < /dev/null 
    	grep -q subject /tmp/sclient.out && (grep $D /tmp/hosts.tsv | tr -d "\n"; echo -en '\t' ; grep subject /tmp/sclient.out )
    done
done
rm -f /tmp/hosts.tsv /tmp/sclient.out
