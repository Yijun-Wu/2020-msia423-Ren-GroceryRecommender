import os
import sys
import config
import logging.config
import boto3
import botocore

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def write_to_s3(S3_PUBLIC_KEY, S3_SECRET_KEY, FILE_LOCATION, S3_BUCKET):
    """ Upload data to S3 bucket
    Args:
        S3_PUBLIC_KEY, S3_SECRET_KEY, S3_BUCKET: user credentials
        FILE_LOCATION: data file location
    """

    # check for invalid credentials in config
    try:
        s3 = boto3.client('s3', aws_access_key_id=S3_PUBLIC_KEY, aws_secret_access_key=S3_SECRET_KEY)
        s3.upload_file(FILE_LOCATION, S3_BUCKET, "food_display_table.csv")
        logger.info("Upload data to S3")
    except botocore.exceptions.NoCredentialsError as e:
        logger.error("Invalid credentials for S3")
        sys.exit(1)


# Call the function created above to write data into S3 bucket
write_to_s3(config.S3_PUBLIC_KEY, config.S3_SECRET_KEY, config.FILE_LOCATION, config.S3_BUCKET)