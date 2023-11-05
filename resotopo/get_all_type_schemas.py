import boto3
import json

# Initialize a session using Amazon CloudFormation.
client = boto3.client('cloudformation')

def list_all_types():
    # Initialize an empty list to hold the types.
    all_types = []

    # Paginate through the results.
    paginator = client.get_paginator('list_types')
    for page in paginator.paginate():
        all_types.extend(page['TypeSummaries'])

    return all_types

# Get all CloudFormation types.
types = list_all_types()
open("resource_types.json", "w").write(json.dumps(types))

# Print the types.
for type_summary in types:
    print(f"Type: {type_summary['TypeName']}")
    print(f"  ARN: {type_summary['TypeArn']}")
    print(f"  Kind: {type_summary['Type']}")
    print(f"  Last Updated: {type_summary.get('TimeCreated', 'N/A')}\n")

print(f"Total Types: {len(types)}")
