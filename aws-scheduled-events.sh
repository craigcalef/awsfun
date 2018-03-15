#!/bin/bash
aws ec2 describe-instance-status --query "InstanceStatuses[?Events!=null].[Events, InstanceId]"
