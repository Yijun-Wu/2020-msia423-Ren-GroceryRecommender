import logging
import pandas as pd
import numpy as np
import sys
from itertools import combinations, groupby
from collections import Counter
from IPython.display import display
from src.market_basket_analysis import run_analysis

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('run-reproducibility')

from src.market_basket_analysis import freq, support, generate_pairs, merge_item_stats, merge_item_name, association_rules

if __name__ == '__main__':
    orders = pd.read_csv('data/external/order_products__prior.csv')
    products = pd.read_csv('data/external/products.csv')
    rec_table = run_analysis(orders, products)
    # write to csv
    rec_table.to_csv("data/external/recommendations.csv")


