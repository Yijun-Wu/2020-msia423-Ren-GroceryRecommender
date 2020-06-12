import os
import sys
import logging
import boto3
import botocore
import yaml

logger = logging.getLogger(__name__)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

def download_s3(args):
    """ Download datasets from S3 bucket
    Args:
        S3_PUBLIC_KEY, S3_SECRET_KEY, S3_BUCKET: user credentials
        FILE_LOCATION: data file location
    """

    # access configuration variables from yaml
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    config = config['download_s3']

    # download datasets from S3 bucket
    try:
        logger.info(os.environ.get("AWS_Access_Key_Id"))
        logger.info(os.environ.get("AWS_Secret_Key"))
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get("AWS_Access_Key_Id"), aws_secret_access_key=os.environ.get("AWS_Secret_Key"))
        logger.info("AWS S3 Credentials Valid")
        logger.info("good")
        logger.info(os.environ.get("AWS_Access_Key_Id"))
        logger.info(os.environ.get("AWS_Secret_Key"))
        try:
            s3.download_file(args.s3bucket, config['FILE_NAME1'], args.output1)
            s3.download_file(args.s3bucket, config['FILE_NAME2'], args.output2)
            s3.download_file(args.s3bucket, config['FILE_NAME3'], args.output3)
            logger.info("Files downloaded from S3 successfully")
        except boto3.exceptions.S3DownloadFailedError as e:
            logger.error("Error: File was not downloaded from S3 bucket. Please provide valid S3 bucket name.")
    except botocore.exceptions.NoCredentialsError as e:
        logger.error("AWS S3 credentials Invalid")
        sys.exit(1)



