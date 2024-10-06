import json
import boto3
import requests
import tempfile
import asyncio
from bs4 import BeautifulSoup
from botocore.exceptions import ClientError
import s3_utils

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("genieverse_posts")

s3_client = boto3.client("s3")
bucket_name = "lemon8--use1-az4--x-s3"  # Replace with your bucket name


def scrape_content(id, href):

    try:
        # Specify the path in S3
        s3_object_name = f"{id}.html"

        if s3_utils.check_file_exists(bucket_name, s3_object_name):
            print(f"File {s3_object_name} already exists in S3")
            return False

        response = requests.get(f"https://www.lemon8-app.com{href}")

        html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")

        content = soup.select_one("#article-content article")

        text = content.get_text(separator=" ", strip=True)

        if text is None or len(text) == 0:
            return False
        else:
            if content is not None:
                with tempfile.NamedTemporaryFile(
                    delete=True, suffix=".html", mode="w+", encoding="utf-8"
                ) as temp_file:
                    temp_file.write(str(content))
                    print(f"File {id}.html created")

                    # Move the cursor to the beginning of the file
                    temp_file.seek(0)

                    # Read the content back
                    file_content = temp_file.read()

                    if file_content is None or len(file_content) == 0:
                        return False

                    temp_file_path = temp_file.name

                    s3_client.upload_file(temp_file_path, bucket_name, s3_object_name)
                    print(f"File {s3_object_name} uploaded to S3")

                    table.update_item(
                        Key={"id": id},
                        UpdateExpression="SET original_text = :val",
                        ExpressionAttributeValues={":val": text},
                        ReturnValues="UPDATED_NEW",
                    )

                    print(f"content of {href} has saved to db")
            else:
                return False

        return True

    except Exception as e:
        print(e)
        return False


async def lambda_handler():

    try:
        response = table.scan()

        items = response.get("Items", [])

        for item in items:
            id = item["id"]
            if id is None or len(id) == 0:
                continue

            href = item["href"]
            if href is None or len(href) == 0:
                continue

            scrape_content(id, href)

            await asyncio.sleep(0.2)

    except ClientError as e:
        print(e)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }


# asyncio.run(lambda_handler())
