import boto3
from bs4 import BeautifulSoup
from botocore.exceptions import ClientError
import uuid

import s3_utils
import db_utils

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("genieverse_posts")


def update_item_text_by_id(id, text):
    try:
        table.update_item(
            Key={"id": id},
            UpdateExpression="SET original_text = :val",
            ExpressionAttributeValues={":val": text},
            ReturnValues="UPDATED_NEW",
        )

        return True
    except ClientError as e:
        print(f"Update item text error: {e}")
        return False


def insert_item_no_repeat_href(item_data):
    try:
        item_data["id"] = str(uuid.uuid4())
        table.put_item(Item=item_data, ConditionExpression="attribute_not_exists(href)")

        return item_data["id"]
    except ClientError as e:
        print(e)
        return None


def delete_item_by_href(id, href):
    try:
        table.delete_item(Key={"id": id, "href": href})
        return True
    except ClientError as e:
        print(f"Error: {e}")
        return False


def extract_text_2_db(items):
    for item in items:
        if item is None:
            continue

        id = item.replace(".html", "")

        if id is None:
            continue

        exist = db_utils.check_existance_by_id(id)

        if not exist:
            print(f"{id} not exist in dynomodb")
            continue

        html_content = s3_utils.get_file_content(item)

        soup = BeautifulSoup(html_content, "html.parser")

        text = soup.get_text(separator=" ", strip=True)

        print(f"extracted: {item}")

        result = update_item_text_by_id(id, text)

        if result:
            print(f"Updated: {id}")
        else:
            print(f"Failed to update: {id}")


def delete_item_with_condition():
    response = table.scan()

    items = response["Items"]
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    for item in items:
        if item is None:
            continue

        id = item["id"]

        if "original_text" not in item:
            db_utils.delete_item_by_id(id)
            print(f"Deleted: {id}")
        else:
            original_text = item.get("original_text")

            if original_text is None or len(original_text.strip()) == 0:
                db_utils.delete_item_by_id(id)
                print(f"Deleted: {id}")
            else:
                continue

# delete_item_with_condition()
