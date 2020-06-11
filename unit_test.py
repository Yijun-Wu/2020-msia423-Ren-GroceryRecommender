from collections import Counter

import pytest
import logging
import pandas as pd
import numpy as np
from src.market_basket_analysis import freq, support, generate_pairs, merge_item_stats, merge_item_name, association_rules, update_filter_support
from src.scores import get_recommendation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.debug("test")

# Generate test data set
raw_data = [[2,33120,1,1], [2,28985,2,1], [2,9327,3,0], [2,45918,4,1], [2,30035,5,0]]
test_cut = pd.DataFrame(raw_data, columns = ['order_id', 'product_id', 'add_to_cart_order', 'reordered'])
# Convert from DataFrame to a Series, with order_id as index and item_id as value
test_cut = test_cut.set_index('order_id')['product_id'].rename('item_id')
orders = pd.read_csv('data/external/orders.csv')
prior = pd.read_csv('data/external/order_products__prior.csv')
products = pd.read_csv('data/external/products.csv')

# happy test for function 'freq'
def test_freq_happy():
    """ Happy test for function 'freq'
        Return value of the function should be equal to manually calculated expected output
        Function: Calculate frequency counts for items
    """
    dat = np.array([1, 1, 1, 1, 1])
    expected_output = pd.Series(dat, index=[9327, 45918, 30035, 28985, 33120]).rename("freq")
    output = freq(test_cut)
    assert expected_output.equals(output)

# unhappy test for function 'freq'
def test_freq_unhappy():
    """ Unhappy test for function 'freq'
        The input value is invalid so it should raise an exception error
    """
    expected_output = None
    with pytest.raises(Exception):
        output = freq(raw_data)

# happy test for function 'support'
def test_support_happy():
    """ Happy test for function 'support'
        Return value of the function should be equal to manually calculated expected output
        Function: Calculate support for items, which is percentage of transactions containing a specific items
    """
    data = [[1, 100.0], [1, 100.0], [1, 100.0], [1, 100.0], [1, 100.0]]
    expected_output = pd.DataFrame(data, index=[9327, 45918, 30035, 28985, 33120], columns=['freq', 'support'])
    freq_res = freq(test_cut).to_frame("freq")
    output = support(test_cut, freq_res)

    assert expected_output.equals(output)

# unhappy test for function 'support'
def test_support_unhappy():
    """ Unhappy test for function 'function'
        The input value is invalid so it should raise an exception error
    """
    expected_output = None
    freq_res = freq(test_cut).to_frame("freq")
    with pytest.raises(Exception):
        output = support(raw_data, freq_res)

# happy test for function 'update_filter_support'
def test_update_filter_support_happy():
    """ Happy test for function 'update_filter_support'
        Return value of the function should be equal to manually calculated expected output
        Function: Filter orders by minimum support and number of items
    """
    output, filtered_orders = update_filter_support(test_cut, 0.01)
    data = np.array([33120, 28985, 9327, 45918, 30035])
    expected_output = pd.Series(data, index=[2, 2, 2, 2, 2])
    expected_output2 = list([2])

    assert expected_output.equals(output) and expected_output2 == filtered_orders.tolist()

# unhappy test for function 'update_filter_support'
def test_update_filter_support_unhappy():
    """ Unhappy test for function 'update_filter_support'
        The input value is invalid so it should raise an exception error
    """
    expected_output = None
    with pytest.raises(Exception):
        output = update_filter_support(raw_data, 0.01)

# happy test for function 'merge_item_stats'
def test_merge_item_stats_happy():
    """ Happy test for function 'merge_item_stats'
        Return value of the function should be equal to manually calculated expected output
        Function: Append stats (frequency, support) to each associated item
    """
    items, filtered_orders = update_filter_support(test_cut, 0.01)
    # Recalculate frequency and support for items in filtered data frame
    stats = freq(items).to_frame("freq")
    stats = support(items, stats)

    # Get item pairs generator
    pairs_generated = generate_pairs(items)
    # Calculate item pair frequency and support ('Counter' keeps track of how many times equivalent values for pairs are added)
    item_pairs = pd.Series(Counter(pairs_generated)).rename("freq").to_frame("freq_AB")
    item_pairs['support_AB'] = item_pairs['freq_AB'] / len(filtered_orders) * 100

    # Filter out item pairs below min support
    filtered_pairs = item_pairs[item_pairs['support_AB'] >= 0.01]
    logger.info("Number of item pairs with support larger than 0.01 " + str(len(filtered_pairs)))

    # Construct association rules table and calculate confidence and lift
    filtered_pairs = filtered_pairs.reset_index().rename(columns={'level_0': 'itemA', 'level_1': 'itemB'})
    output = merge_item_stats(filtered_pairs, stats)

    data = [[33120, 28985, 1, 100.0, 1, 100.0, 1, 100.0], [33120, 9327, 1, 100.0, 1, 100.0, 1, 100.0], [28985, 9327, 1, 100.0, 1, 100.0, 1, 100.0],
            [33120, 45918, 1, 100.0, 1, 100.0, 1, 100.0], [28985, 45918, 1, 100.0, 1, 100.0, 1, 100.0], [9327, 45918, 1, 100.0, 1, 100.0, 1, 100.0],
            [33120, 30035, 1, 100.0, 1, 100.0, 1, 100.0], [28985, 30035, 1, 100.0, 1, 100.0, 1, 100.0],
            [9327, 30035, 1, 100.0, 1, 100.0, 1, 100.0], [45918, 30035, 1, 100.0, 1, 100.0, 1, 100.0]]
    expected_output = pd.DataFrame(data, index=[0, 1, 4, 2, 5, 7, 3, 6, 8, 9], columns=['itemA', 'itemB', 'freq_AB', 'support_AB', 'freq_A', 'support_A', 'freq_B',
                                                                                        'support_B'])
    assert expected_output.equals(output)

# unhappy test for function 'merge_item_stats'
def test_merge_item_stats_unhappy():
    """ Unhappy test for function 'merge_item_stats'
        The input value is invalid so it should raise an exception error
    """
    expected_output = None
    stats = freq(test_cut).to_frame("freq")
    stats = support(test_cut, stats)
    with pytest.raises(Exception):
        output = merge_item_stats(raw_data, stats)

# happy test for function 'association_rules'
def test_association_rules_happy():
    """ Happy test for function 'association_rules'
        Return value of the function should be equal to manually calculated expected output
        Function: Generate associations rules for item pairs
    """
    output = association_rules(test_cut, 0.01)
    data = [[33120, 28985, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [33120, 9327, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [28985, 9327, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [33120, 45918, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [28985, 45918, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [9327, 45918, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [33120, 30035, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [28985, 30035, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [9327, 30035, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            [45918, 30035, 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01]]
    expected_output = pd.DataFrame(data, index=[0, 1, 4, 2, 5, 7, 3, 6, 8, 9],
                                   columns=['itemA', 'itemB', 'freq_AB', 'support_AB', 'freq_A', 'support_A', 'freq_B',
                                            'support_B', 'confidence_AtoB', 'confidence_BtoA', 'lift'])
    assert expected_output.equals(output)

# unhappy test for function 'association_rules'
def test_association_rules_unhappy():
    """ Unhappy test for function 'association_rules'
        The input value is invalid so it should raise an exception error
    """
    expected_output = None
    with pytest.raises(Exception):
        output = association_rules(raw_data, 0.01)

# happy test for function 'merge_item_name'
def test_merge_item_name_happy():
    """ Happy test for function 'merge_item_name'
        Return value of the function should be equal to manually calculated expected output
        Function: Append item names to corresponding items
    """
    rules = association_rules(test_cut, 0.01)
    products_df = products.rename(columns={'product_id': 'item_id', 'product_name': 'item_name'})
    output = merge_item_name(rules, products_df).sort_values('lift', ascending=False)

    data = [['Organic Egg Whites', 'Michigan Organic Kale', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Organic Egg Whites', 'Garlic Powder', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Michigan Organic Kale', 'Garlic Powder', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Organic Egg Whites', 'Coconut Butter', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Michigan Organic Kale', 'Coconut Butter', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Garlic Powder', 'Coconut Butter', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Organic Egg Whites', 'Natural Sweetener', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Michigan Organic Kale', 'Natural Sweetener', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Garlic Powder', 'Natural Sweetener', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01],
            ['Coconut Butter', 'Natural Sweetener', 1, 100.0, 1, 100.0, 1, 100.0, 1.0, 1.0, 0.01]]
    expected_output = pd.DataFrame(data, index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                                   columns=['item_A', 'item_B', 'freq_AB', 'support_AB', 'freq_A', 'support_A', 'freq_B',
                                            'support_B', 'confidence_AtoB', 'confidence_BtoA', 'lift'])
    assert expected_output.equals(output)

# unhappy test for function 'merge_item_name'
def test_merge_item_name_unhappy():
    """ Unhappy test for function 'merge_item_name'
        The input value is invalid so it should raise an exception error
    """
    expected_output = None
    rules = association_rules(test_cut, 0.01)
    with pytest.raises(Exception):
        output = merge_item_name(rules, raw_data).sort_values('lift', ascending=False)

# happy test for function 'get_recommendation'
def test_get_recommendation_happy():
    """ Happy test for function 'get_recommendation'
        Return value of the function should be equal to manually calculated expected output
        Function: Generate top 5 recommendations for an item
    """
    rules = association_rules(test_cut, 0.01)
    products_df = products.rename(columns={'product_id': 'item_id', 'product_name': 'item_name'})
    train_rules_final = merge_item_name(rules, products_df).sort_values('lift', ascending=False)
    table, count = get_recommendation(train_rules_final, "Garlic Powder")
    data = [['Garlic Powder', 'Organic Egg Whites', 'Michigan Organic Kale', 'NA', 'NA', 'NA']]
    expected_output = pd.DataFrame(data, index=[0], columns=['item_name', 'recommendation1', 'recommendation2', 'recommendation3',
                                            'recommendation4', 'recommendation5'])
    assert expected_output.equals(table) and count == 2

# unhappy test for function 'get_recommendation'
def test_get_recommendation_unhappy():
    """ Unhappy test for function 'get_recommendation'
        The input value is invalid so it should raise an exception error
    """
    expected_output = None
    with pytest.raises(Exception):
        output = get_recommendation(test_cut, "Garlic Powder")

# # happy test for function 'test_scores'
# def test_test_scores_happy():
#     """ Happy test for function 'test_scores'
#         Return value of the function should be equal to manually calculated expected output
#         Function: Calculate the test score of recommendations generated for test data
#     """
#     train_data = prior[:25947591]
#     test_data = prior[25947591:]
#     # Convert from DataFrame to a Series, with order_id as index and item_id as value
#     train_data = train_data.set_index('order_id')['product_id'].rename('item_id')
#     rules = association_rules(train_data, 0.01)
#     products_df = products.rename(columns={'product_id': 'item_id', 'product_name': 'item_name'})
#     train_rules_final = merge_item_name(rules, products_df).sort_values('lift', ascending=False)
#
#     test_order = pd.merge(test_data, products, how='left', on='product_id')
#     test_order = pd.merge(test_order, orders, how='left', on='order_id')
#
#     output = test_scores(test_order, train_rules_final)
#
#     print(output)
#
# # unhappy test for function 'test_scores'
# def test_test_scores_unhappy():
#     """ Unhappy test for function 'test_scores'
#         The input value is invalid so it should raise an exception error
#     """
#     expected_output = None
#     with pytest.raises(Exception):
#         output = test_scores(orders, raw_data)