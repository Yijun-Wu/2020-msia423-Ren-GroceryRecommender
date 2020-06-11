import logging
import pandas as pd
import numpy as np
logger = logging.getLogger(__name__)
from src.scores import run_scores

if __name__ == '__main__':
    # import data
    orders = pd.read_csv('data/external/orders.csv')
    prior = pd.read_csv('data/external/order_products__prior.csv')
    products = pd.read_csv('data/external/products.csv')

    print(run_scores(orders, prior, products))


