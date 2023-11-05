import datetime
import boto3
import json

def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

# Initialize a session using Amazon CloudFormation.
client = boto3.client('cloudformation')

def list_all_types():
    # Initialize an empty list to hold the types.
    all_types = []

    # Initialize pagination token to None to fetch the first page.
    next_token = None
    
    while True:
        # Call the ListTypes API.
        if next_token:
            response = client.list_types(Type="RESOURCE", Visibility="PUBLIC", NextToken=next_token)
        else:
            response = client.list_types(Type="RESOURCE", Visibility="PUBLIC")
    

        # Extract and append TypeSummaries from the response.
        all_types.extend(response['TypeSummaries'])

        # Check if there are more pages to retrieve.
        next_token = response.get('NextToken')
        if not next_token:
            break

    return all_types

# Get all CloudFormation types.
types = list_all_types()
open("resource_types.json", "w").write(json.dumps(types, default=serialize_datetime))

# Print the types.
for type_summary in types:
    print(f"Type: {type_summary['TypeName']}")
    print(f"  ARN: {type_summary['TypeArn']}")
    print(f"  Kind: {type_summary['Type']}")
    print(f"  Last Updated: {type_summary.get('TimeCreated', 'N/A')}\n")

print(f"Total Types: {len(types)}")
