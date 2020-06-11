import os
from os import path

S3_BUCKET = "nw-jren-s3-1"
S3_PUBLIC_KEY = os.environ.get("AWS_Access_Key_Id")
S3_SECRET_KEY = os.environ.get("AWS_Secret_Key")

PROJECT_HOME = path.dirname(path.dirname(path.abspath(__file__)))
LOGGING_CONFIG = path.join(PROJECT_HOME, 'config', 'logging', 'local.conf')
FILE_LOCATION1 = path.join(PROJECT_HOME,'data/external/order_products__prior.csv')
FILE_NAME1 = "order_products__prior.csv"
FILE_LOCATION2 = path.join(PROJECT_HOME,'data/external/products.csv')
FILE_NAME2 = "products.csv"

LOCAL_DB_PATH = path.dirname(path.dirname(path.abspath(__file__)))+'/data/Recommendation.db'
DATABASE_PATH = path.join(PROJECT_HOME, 'data/msia423_db.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:////data/Recommendation.db'

RDS_FLAG = False
# REC_DATA_PATH = 'data/external/test.csv'
