import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("genieverse_posts")

def check_existance_by_id(id):
    try:
        response = table.get_item(Key={"id": id})

        if "Item" in response:
            return True
        else:
            return False
    except ClientError as e:
        print(f"Check existance error: {e}")
        return False

def delete_item_by_id(id):
    try:
        table.delete_item(Key={"id": id})
        return True
    except ClientError as e:
        print(f"Error: {e}")
        return False
