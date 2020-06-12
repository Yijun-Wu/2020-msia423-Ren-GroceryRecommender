import pandas as pd
import logging
import numpy as np
from src.market_basket_analysis import merge_item_name, association_rules

logger = logging.getLogger(__name__)

def get_recommendation(train_rules_final, name):
    """ Generate top 5 recommendations for an item
       Input:
           train_rules_final: association rules generated from training data
           name: item name
        Returns:
           rec_table: recommendations table
           top_n: number of recommendations given
    """
    try:
        column_names = ["item_name", "recommendation1", "recommendation2", "recommendation3", "recommendation4", "recommendation5"]
        ls = []
        # find all pairs related to current item
        pairs = train_rules_final[train_rules_final.item_B == name].sort_values('lift', ascending=False)
        # if there's less than 5 pairs, choose number of pairs as top n recommendations, otherwise choose top 5
        top_n = 5 if len(pairs) >= 5 else len(pairs)
        pairs = pairs.head(top_n)
        a = pairs['item_A'].to_list()
        a.insert(0, name)
        # construct a list: item, rec1, rec2, rec3, rec4, rec5
        row = a + ['NA'] * (6 - top_n - 1)
        # list of list
        ls.append(row)
        rec_table = pd.DataFrame(ls, columns=column_names)
    except Exception as e:
        logger.warning('Could not generate recommendations due to invalid input')
        raise Exception('Invalid input')
    return rec_table, top_n


def test_scores(test_order, train_rules_final):
    """ Calculate the test score of recommendations generated for test data
       Give 5 recommendations for each item in order, and compare if there's a match with the following 4 items, so on and so forth.
       If there's a match, add 1 to score, then divided by total number of recommendations made to current order,
       that is to say, calculate the fraction of matched recommendation.
       Input:
           test_order: test data
           train_rules_final: association rules generated from training data
        Returns:
           scores: average score by each order
    """
    try:
        scores = []
        for item in test_order.groupby('order_id')['item_name']:
            # get the current order and change it to list structure
            curr_order = item[1].tolist()
            # initialize the total score
            total_score = 0
            # count how many items is contained in the database
            num_item = 0
            for i in range(len(curr_order)):
                if curr_order[i] in train_rules_final.item_B.tolist():
                    num_item += 1
                    # get the recommendation list of the current item
                    recommendations, _ = get_recommendation(train_rules_final, curr_order[i])
                    recommendations = recommendations.values.tolist()[0]
                    # check if the recommendation is contained in the remaining list
                    following_items = curr_order[i:]
                    for item in recommendations:
                        if item in following_items:
                            total_score += 1

            if not num_item == 0:
                count = 0
                if num_item > 5:
                    count += (num_item - 5) * 5
                    num_item = 5
                for n in range(num_item + 1):
                    count += n
                scores.append(total_score / count)
    except Exception as e:
        logger.warning('Could not calculate scores for test dataset due to invalid input')
        raise Exception('Invalid input')
    return scores


def run_scores(args):
    """ Generate test score of recommendations generated for test data
      Input:
          orders: orders dataframe
          prior: prior orders dataframe
          products: products dataframe
       Returns:
          scores: average score by each order
       """

    try:
        prior = pd.read_csv(args.input1)
        orders = pd.read_csv(args.input2)
        products = pd.read_csv(args.input3)
        logger.info("Datasets read in successfully")

        # Do a 80:20 train/test split on data
        train_data = prior.head(int(len(prior)*(80/100)))
        test_data = prior[len(train_data):]
        logger.info("Size of training data: "+ str(len(train_data)))
        logger.info("Size of testing data: "+ str(len(test_data)))

        # Convert from DataFrame to a Series, with order_id as index and item_id as value
        train_data = train_data.set_index('order_id')['product_id'].rename('item_id')
        rules = association_rules(train_data, 0.01)
        products = products.rename(columns={'product_id': 'item_id', 'product_name': 'item_name'})
        train_rules_final = merge_item_name(rules, products).sort_values('lift', ascending=False)
        products = products.rename(columns={'item_id': 'product_id'})
        logger.info("Training rules generated")

        logger.info(train_rules_final.head())
        # Prior orders with user_id, product_id, product_name
        test_order = pd.merge(test_data, products, how='left', on='product_id')
        test_order = pd.merge(test_order, orders, how='left', on='order_id')

        logger.info("Test data ready and calculating scores now ...")

        scores = np.nanmean(test_scores(test_order, train_rules_final))
        logger.info("Score from test data is: "+ str(scores))

        with open(args.output, 'w') as f:
            f.write("Test score is: ")
            f.write(str(scores))
        logger.info("Test score saved to file: " + args.output)

    except Exception as e:
        logger.warning('Could not generate scores for test dataset due to invalid input')
        raise Exception('Invalid input')
    return scores
