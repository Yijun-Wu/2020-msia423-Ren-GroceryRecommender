import os
from os import path

# Getting the parent directory of this file. That will function as the project home.
PROJECT_HOME = path.dirname(path.dirname(path.abspath(__file__)))
LOGGING_CONFIG = path.join(PROJECT_HOME, 'config', 'logging', 'local.conf')
S3_BUCKET = "nw-jren-s3-1"

DATABASE_PATH = path.join(PROJECT_HOME, 'data/msia423_db.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)

DB_FLAG = "RDS"
