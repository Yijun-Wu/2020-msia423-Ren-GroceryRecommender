import sys
import logging.config
import boto3
import botocore
import os
import yaml

logger = logging.getLogger(__name__)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

def upload_to_s3(args):
    """ Upload data to S3 bucket
    Args:
        S3_PUBLIC_KEY, S3_SECRET_KEY, S3_BUCKET: user credentials
        FILE_LOCATION: data file location
    """
    # access configuration variables from yaml
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['upload_to_s3']

    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=S3_SECRET_KEY)
        logger.info("AWS S3 Credentials Valid")
        try:
            s3.upload_file(args.input1, args.s3bucket, config['FILE_NAME1'])
            s3.upload_file(args.input2, args.s3bucket, config['FILE_NAME2'])
            s3.upload_file(args.input3, args.s3bucket, config['FILE_NAME3'])
            logger.info("Files uploaded to S3 successfully")
        except boto3.exceptions.S3UploadFailedError as e:
            logger.error("Error: File was not uploaded to S3 bucket. Please provide valid S3 bucket name.")
    except botocore.exceptions.NoCredentialsError as e:
        logger.error("AWS S3 credentials Invalid")
        sys.exit(1)

