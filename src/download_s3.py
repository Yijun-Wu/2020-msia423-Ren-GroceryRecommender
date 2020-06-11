import os
import sys
import logging
import boto3
import botocore

logger = logging.getLogger(__name__)

def download_s3(S3_PUBLIC_KEY, S3_SECRET_KEY, FILE_LOCATION1, FILE_LOCATION2, FILE_LOCATION3, FILE_NAME1, FILE_NAME2, FILE_NAME3, S3_BUCKET):
    """ Download data from S3 bucket
    Args:
        S3_PUBLIC_KEY, S3_SECRET_KEY, S3_BUCKET: user credentials
        FILE_LOCATION: data file location
    """

    try:
        s3 = boto3.client('s3', aws_access_key_id=S3_PUBLIC_KEY, aws_secret_access_key=S3_SECRET_KEY)
        logger.info("AWS S3 Credentials Valid")
        try:
            s3.download_file(S3_BUCKET, FILE_NAME1, FILE_LOCATION1)
            s3.download_file(S3_BUCKET, FILE_NAME2, FILE_LOCATION2)
            s3.download_file(S3_BUCKET, FILE_NAME3, FILE_LOCATION3)
            logger.info("Files downloaded from S3 successfully")
        except boto3.exceptions.S3UploadFailedError as e:
            logger.error("Error: File was not downloaded from S3 bucket. Please provide valid S3 bucket name.")
    except botocore.exceptions.NoCredentialsError as e:
        logger.error("AWS S3 credentials Invalid")
        sys.exit(1)

# if __name__ == '__main__':
#     download_s3(S3_PUBLIC_KEY, S3_SECRET_KEY, FILE_LOCATION1, FILE_LOCATION2,
#                 FILE_LOCATION3, FILE_NAME1, FILE_NAME2, FILE_NAME3, S3_BUCKET):
#


