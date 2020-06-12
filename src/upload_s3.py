import sys
import logging.config
import boto3
import botocore

logger = logging.getLogger(__name__)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

def upload_to_s3(S3_PUBLIC_KEY, S3_SECRET_KEY, FILE_LOCATION1, FILE_NAME1, FILE_LOCATION2, FILE_NAME2, S3_BUCKET):
    """ Upload data to S3 bucket
    Args:
        S3_PUBLIC_KEY, S3_SECRET_KEY, S3_BUCKET: user credentials
        FILE_LOCATION: data file location
    """

    try:
        s3 = boto3.client('s3', aws_access_key_id=S3_PUBLIC_KEY, aws_secret_access_key=S3_SECRET_KEY)
        logger.info("AWS S3 Credentials Valid")
        try:
            s3.upload_file(FILE_LOCATION1, S3_BUCKET, FILE_NAME1)
            s3.upload_file(FILE_LOCATION2, S3_BUCKET, FILE_NAME2)
            logger.info("Files uploaded to S3 successfully")
        except boto3.exceptions.S3UploadFailedError as e:
            logger.error("Error: File was not uploaded to S3 bucket. Please provide valid S3 bucket name.")
    except botocore.exceptions.NoCredentialsError as e:
        logger.error("AWS S3 credentials Invalid")
        sys.exit(1)


upload_to_s3(config.S3_PUBLIC_KEY, config.S3_SECRET_KEY, config.FILE_LOCATION1, config.FILE_NAME1, config.FILE_LOCATION2, config.FILE_NAME2, config.S3_BUCKET)