import boto3
from botocore.exceptions import NoCredentialsError
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def get_s3_client_region(s3_client):
    return s3_client.meta.region_name

def upload_to_s3(file_path, bucket_name, s3_key):
    print("Now, uploading is in progress.")
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        region = get_s3_client_region(s3_client)
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        #console_url = f"https://{region}.console.aws.amazon.com/s3/object/{bucket_name}?region={region}&prefix={s3_key}"
        return s3_url
    except NoCredentialsError:
        raise Exception("Credentials not available")