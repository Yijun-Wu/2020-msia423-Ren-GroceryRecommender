import os
from os import path

S3_BUCKET = "nw-jren-s3-1"
S3_PUBLIC_KEY = os.environ.get("AWS_Access_Key_Id")
S3_SECRET_KEY = os.environ.get("AWS_Secret_Key")

PROJECT_HOME = path.dirname(path.dirname(path.abspath(__file__)))
LOGGING_CONFIG = path.join(PROJECT_HOME, 'config', 'logging', 'local.conf')
FILE_LOCATION = path.join(PROJECT_HOME,'data/external/food_display_table.csv')

DATABASE_PATH = path.join(PROJECT_HOME, 'data/msia423_db.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)

DB_FLAG = "RDS"
