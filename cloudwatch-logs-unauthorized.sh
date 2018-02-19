#!/bin/sh
# Show UnauthoredOperation and AccessDenied log messages logged to the default CloudTrail log group
# This is useful if you've installes the CIS Security Benchmark for AWS.
aws --profile dev logs filter-log-events --log-group-name CloudTrail/DefaultLogGroup --filter-pattern "{ ($.errorCode = "*UnauthorizedOperation") || ($.errorCode = "AccessDenied*") }" --start-time=`gdate "+%s" --date="1 days ago"` --query "events[].message" --output text
