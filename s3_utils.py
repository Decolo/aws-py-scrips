
import boto3
from botocore.exceptions import ClientError

bucket = "lemon8--use1-az4--x-s3"

s3_client = boto3.client("s3")


def upload_file_to_s3(file_name, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(response)
        return True
    except ClientError as e:
        print(e)
        return False

def get_file_content(file_name):
    try:
        if file_name is None:
            raise ValueError("file name is None")

        response = s3_client.get_object(Bucket=bucket, Key=file_name)

        file_content = response["Body"].read().decode("utf-8")

        return file_content
    except ValueError as e:
        print(f"get file content {e}")
        return None

def delete_file(file_name):
    try:
        if file_name is None:
            raise ValueError("file name is None")

        s3_client.delete_object(Bucket=bucket, Key=file_name)

        return True
    except ValueError as e:
        print(f"delete file {e}")
        return False

def modify_file(file_name, modified_content):
    try:
        if file_name is None:
            raise ValueError("file name is None")

        s3_client.put_object(Bucket=bucket, Key=file_name, Body=modified_content)

        return True
    except ValueError as e:
        print(f"modify file {e}")
        return False

def list_all_files():
    continuation_token = None
    all_objects = []

    while True:
        if continuation_token:
            response = s3_client.list_objects_v2(
                Bucket=bucket, ContinuationToken=continuation_token
            )
        else:
            response = s3_client.list_objects_v2(Bucket=bucket)

        if "Contents" in response:
            for obj in response["Contents"]:
                all_objects.append(obj["Key"])
                # print(obj['Key'] + '\n')

        if response.get("IsTruncated"):
            continuation_token = response.get("NextContinuationToken")
        else:
            break

    return all_objects

def check_file_exists(bucket_name, file_name):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_name)
        return True  # File exists
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False  # File does not exist
        else:
            raise