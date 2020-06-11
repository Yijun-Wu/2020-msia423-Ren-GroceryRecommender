import argparse
import logging
import yaml
import pandas as pd
import os

import src.download_s3 as d3
import src.market_basket_analysis as mba
import src.scores as sc
import src.recommender_db as db

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('run-reproducibility')

from src.download_s3 import download_s3
# from src.recommender_db import
from src.market_basket_analysis import freq, support, generate_pairs, merge_item_stats, merge_item_name, association_rules, run_analysis
from src.scores import get_recommendation, test_scores, run_scores


if __name__ == '__main__':



    parser = argparse.ArgumentParser(description="Acquire, generate rules, test scores, and store to RDS from orders data")
    subparsers = parser.add_subparsers()

    # Acquire data from URL
    sb_dataset = subparsers.add_parser("acquire", description="download data from S3")
    sb_dataset.add_argument('--config', help='path to yaml file with configurations')
    sb_dataset.add_argument('--filename1', default='order_products__prior.csv', help='prior orders data')
    sb_dataset.add_argument('--filename2', default='order.csv', help='orders data')
    sb_dataset.add_argument('--filename3', default='products.csv', help='products data')
    sb_dataset.add_argument('--output1', default='data/external/order_products__prior.csv', help='prior orders data')
    sb_dataset.add_argument('--output2', default='data/external/order.csv', help='orders data')
    sb_dataset.add_argument('--output3', default='data/external/products.csv', help='products data')
    sb_dataset.set_defaults(func=d3.download_s3)


    # Generate association rules
    sb_rules = subparsers.add_parser("generate_rules", description="generate rules")
    sb_rules.add_argument('--config', help='path to yaml file with configurations')
    sb_rules.add_argument('--input1', default='data/external/order_products__prior.csv', help='prior orders data')
    sb_rules.add_argument('--input2', default='data/external/products.csv', help='products data')
    sb_rules.add_argument('--output', default='data/external/recommendations.csv', help='recommendations generated')
    sb_rules.set_defaults(func=mba.run_analysis)

    # Evaluate scores of rules on test data
    sb_scores = subparsers.add_parser("get_scores", description="calculate test scores on rules generated")
    sb_scores.add_argument('--config', help='path to yaml file with configurations')
    sb_scores.add_argument('--input1', default='data/external/order_products__prior.csv', help='prior orders data')
    sb_scores.add_argument('--input2', default='data/external/order.csv', help='orders data')
    sb_scores.add_argument('--input3', default='data/external/products.csv', help='products data')
    sb_scores.add_argument('--output', default='data/external/test_score.csv', help='recommendations generated')
    sb_scores.set_defaults(func=sc.run_scores)

    # Store generated rules into RDS
    sb_rds = subparsers.add_parser("store_RDS", description="store recommendations table into RDS")
    sb_rds.add_argument("--truncate", "-t", default=False, action="store_true",
                        help="If given, delete current records from recommendation table so that table can be recreated without problem with unique id ")
    sb_rds.add_argument("--rds", "-r", default=False, action="store_true",
                        help="If true, store table into RDS database, otherwise the database would be created locally ")
    sb_rds.set_defaults(func=db.create_db)


    args = parser.parse_args()
    args.func(args)


