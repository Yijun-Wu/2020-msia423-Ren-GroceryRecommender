import argparse
import logging

import src.download_s3 as d3
import src.market_basket_analysis as mba
import src.scores as sc
import src.recommender_db as db
import src.upload_s3 as u3

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('run-reproducibility')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Acquire, generate rules, test scores, and store to RDS from orders data")
    subparsers = parser.add_subparsers()

    # Upload data to S3 bucket
    sb_upload = subparsers.add_parser("upload", description="upload data to S3")
    sb_upload.add_argument('--config', help='path to yaml file with configurations')
    sb_upload.add_argument('--s3bucket', help='S3 bucket name')
    sb_upload.add_argument('--input1', default=None, help='prior orders data')
    sb_upload.add_argument('--input2', default=None, help='orders data')
    sb_upload.add_argument('--input3', default=None, help='products data')
    sb_upload.set_defaults(func=u3.upload_to_s3)

    # Acquire data from S3 bucket
    sb_dataset = subparsers.add_parser("acquire", description="download data from S3")
    sb_dataset.add_argument('--config', help='path to yaml file with configurations')
    sb_dataset.add_argument('--s3bucket', help='S3 bucket name')
    sb_dataset.add_argument('--output1', default=None, help='prior orders data')
    sb_dataset.add_argument('--output2', default=None, help='orders data')
    sb_dataset.add_argument('--output3', default=None, help='products data')
    sb_dataset.set_defaults(func=d3.download_s3)

    # Generate recommendation table based association rules of market basket analysis on all data
    sb_rules = subparsers.add_parser("generate_rules", description="generate rules")
    sb_rules.add_argument('--input1', default=None, help='prior orders data')
    sb_rules.add_argument('--input2', default=None, help='products data')
    sb_rules.add_argument('--output', default=None, help='recommendations generated')
    sb_rules.set_defaults(func=mba.run_analysis)

    # Evaluate scores of recommendation model on test data (after generating rules from train data)
    sb_scores = subparsers.add_parser("get_scores", description="calculate test scores on rules generated")
    sb_scores.add_argument('--input1', default=None, help='prior orders data')
    sb_scores.add_argument('--input2', default=None, help='orders data')
    sb_scores.add_argument('--input3', default=None, help='products data')
    sb_scores.add_argument('--output', default=None, help='recommendations generated')
    sb_scores.set_defaults(func=sc.run_scores)

    # Store generated recommendations into RDS
    sb_rds = subparsers.add_parser("store_RDS", description="store recommendations table into RDS")
    sb_rds.add_argument('--input', default=None, help='recommendation table') # 'data/external/recommendations.csv
    sb_rds.add_argument("--truncate", "-t", default=False,
                        help="If given, delete current records from recommendation table so that table can be recreated without problem with unique id ")
    sb_rds.add_argument("--rds", "-r", default=True,
                        help="If true, store table into RDS database, otherwise the database would be created locally ")
    sb_rds.set_defaults(func=db.create_rec_db)


    args = parser.parse_args()
    args.func(args)


