import os
import traceback

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

try:
    client = boto3.client(
        "sts",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ.get("AWS_REGION", "eu-west-3"),
        config=Config(connect_timeout=5, read_timeout=5, retries={"max_attempts": 1}),
    )
    identity = client.get_caller_identity()
    print("Account:", identity["Account"])
    print("Arn:", identity["Arn"])
except Exception:
    traceback.print_exc()
