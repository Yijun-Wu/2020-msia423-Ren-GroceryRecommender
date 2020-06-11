import pandas as pd
import logging
from itertools import combinations, groupby
from collections import Counter

logger = logging.getLogger(__name__)

def freq(df):
    """ Calculate frequency counts for items
    Inputs:
        df: orders dataframe
    Returns:
        freq: new df with frequency counts
    """
    try:
        # value_counts() yield counts of unique values
        freq = df.value_counts().rename("freq")
    except Exception as e:
        logger.warning('Could not generate freq due to invalid input')
        raise Exception('Invalid input')
    return freq


def support(df, df_freq):
    """ Calculate support (popularity of an item) for items, which is number of transactions containing a specific items divided by total number of transactions
    Inputs:
        df: orders dataframe
        df_freq: frequency counts df
    Returns:
        df_freq: new df with support added
    """
    try:
        # number of unique orders
        count_unique = len(set(df.index))
        # multiply by 100 to get percentage
        df_freq['support']  = df_freq['freq'] / count_unique * 100
    except Exception as e:
        logger.warning('Could not generate support due to invalid input')
        raise Exception('Invalid input')
    return df_freq


def generate_pairs(df):
    """ Generates pairs of items
    Inputs:
        df: orders dataframe
    Returns:
        Use yield instead of return to generate all possible combinations of 2 elements in array given,
        Help to avoid costing lots of storage in memory by iterating over a sequence of pairs
    """
    try:
        # Reset index of dataframe to default
        df = df.reset_index().values
        # Group by index number
        for ind, order_num in groupby(df, lambda x: x[0]):
            # Extract list of order number
            item_list = []
            for item in order_num:
                item_list.append(item[1])
            for item_pair in combinations(item_list, 2):
                yield item_pair
    except Exception as e:
        logger.warning('Could not generate pairs due to invalid input')
        raise Exception('Invalid input')


def merge_item_stats(item_pairs, stats):
    """ Append stats (frequency, support) to each associated item
    Inputs:
        item_pairs: pairs of items generated
        stats: calculated frequency and support for items
    Returns:
        merge_df: merged dataframe of item pairs with stats
    """
    try:
        merge_df = item_pairs.merge(stats.rename(columns = {'freq': 'freq_A', 'support': 'support_A'}),
                                    left_on = 'itemA',
                                    right_index = True)
        merge_df = merge_df.merge(stats.rename(columns = {'freq': 'freq_B', 'support': 'support_B'}),
                                    left_on = 'itemB',
                                    right_index = True)
    except Exception as e:
        logger.warning('Could not append stats to items due to invalid input')
        raise Exception('Invalid input')
    return merge_df


def merge_item_name(ac_rules, item_name):
    """ Append item names to corresponding items
    Inputs:
        ac_rules: dataframe with associate rules of pairs
        item_name: dataframe with item id associated to item name
    Returns:

    """
    try:
        columns = ['item_A', 'item_B', 'freq_AB', 'support_AB', 'freq_A', 'support_A', 'freq_B', 'support_B',
                   'confidence_AtoB', 'confidence_BtoA', 'lift']
        ac_rules = ac_rules.merge(item_name.rename(columns={'item_name': 'item_A'}),
                                  left_on='itemA',
                                  right_on='item_id')
        ac_rules = ac_rules.merge(item_name.rename(columns={'item_name': 'item_B'}),
                                  left_on='itemB',
                                  right_on='item_id')
    except Exception as e:
        logger.warning('Could not append names to items due to invalid input')
        raise Exception('Invalid input')
    return ac_rules[columns]



def update_filter_support(items, min_support):
    """ Filter orders by minimum support and number of items
        Inputs:
            items: raw data of orders
            min_support: minimum confidence constraint that's applied to frequent itemsets in order to form rules
        Returns:
            items: filtered items above minimum support
            filtered_orders: filtered orders with >= 2 items
     """
    try:
        logger.info("Starting with total items: " + str(len(items)))
        # Calculate frequency and support for items
        stats = freq(items).to_frame("freq")
        stats = support(items, stats)

        # Filter out items below min support
        filtered = stats[stats['support'] >= min_support].index
        items = items[items.isin(filtered)]
        logger.info("After filtering out items below min support, remaining items: " + str(len(items)))

        # Filter out orders that have less than 2 items
        order_size = freq(items.index)
        filtered_orders = order_size[order_size >= 2].index
        items = items[items.index.isin(filtered_orders)]
        logger.info("After filtering out orders that have less than 2 items: " + str(len(items)))
    except Exception as e:
        logger.error(e)
        raise Exception('Invalid input')
    return items, filtered_orders


def association_rules(items, min_support):
    """ Generate associations rules for item pairs
        Inputs:
            items: raw data of orders
            min_support: minimum confidence constraint that's applied to frequent itemsets in order to form rules
        Returns:
            filtered pairs rules with lift in descending order
    """
    try:
        items, filtered_orders = update_filter_support(items, min_support)

        # Recalculate frequency and support for items in filtered dataframe
        stats = freq(items).to_frame("freq")
        stats = support(items, stats)

        # Get item pairs generator
        pairs_generated = generate_pairs(items)
        # Calculate item pair frequency and support ('Counter' keeps track of how many times equivalent values for pairs are added)
        item_pairs = pd.Series(Counter(pairs_generated)).rename("freq").to_frame("freq_AB")
        item_pairs['support_AB'] = item_pairs['freq_AB'] / len(filtered_orders) * 100

        print("Item pairs: {:31d}".format(len(item_pairs)))

        # Filter out item pairs below min support
        filtered_pairs = item_pairs[item_pairs['support_AB'] >= min_support]

        print("Item pairs with support >= {}: {:10d}\n".format(min_support, len(filtered_pairs)))

        # Construct association rules table and calculate confidence and lift
        filtered_pairs = filtered_pairs.reset_index().rename(columns={'level_0': 'itemA', 'level_1': 'itemB'})
        filtered_pairs = merge_item_stats(filtered_pairs, stats)

        filtered_pairs['confidence_AtoB'] = filtered_pairs['support_AB'] / filtered_pairs['support_A']
        filtered_pairs['confidence_BtoA'] = filtered_pairs['support_AB'] / filtered_pairs['support_B']
        filtered_pairs['lift'] = filtered_pairs['support_AB'] / (
                    filtered_pairs['support_A'] * filtered_pairs['support_B'])
    except Exception as e:
        logger.error(e)
        raise Exception('Invalid input')

    # Return association rules sorted by lift in descending order
    # Larger lift implies increase in the ratio of sale of B when A is sold
    return filtered_pairs.sort_values('lift', ascending=False)


def run_analysis(orders, products):
    """ Create top 5 recommendations table with generated association rules
       Inputs:
           orders: orders dataframe
           products: products dataframe
       Returns:
           rec_table: table of recommendations for each item
    """
    try:
        # Convert from DataFrame to a Series, with order_id as index and item_id as value
        orders = orders.set_index('order_id')['product_id'].rename('item_id')
        # generate association rules
        rules = association_rules(orders, 0.01)
        products = products.rename(columns={'product_id': 'item_id', 'product_name': 'item_name'})
        rules_final = merge_item_name(rules, products).sort_values('lift', ascending=False)
        # pick top 5 recommendations for each unique item
        unique_B = rules_final.item_B.unique()
        column_names = ["item_name", "recommendation1", "recommendation2", "recommendation3", "recommendation4",
                        "recommendation5"]
        ls = []
        for i in range(len(unique_B)):
            # find all pairs related to current item
            pairs = rules_final[rules_final.item_B == unique_B[i]].sort_values('lift', ascending=False)
            # if there's less than pairs, choose number of pairs as top n recommendations, otherwise choose top 5
            top_n = 5 if len(pairs) >= 5 else len(pairs)
            pairs = pairs.head(top_n)
            a = pairs['item_A'].to_list()
            a.insert(0, unique_B[i])
            # construct a list: item, rec1, rec2, rec3, rec4, rec5
            row = a + ['NA'] * (6 - top_n - 1)
            # list of list
            ls.append(row)
        rec_table = pd.DataFrame(ls, columns=column_names)
    except Exception as e:
        logger.error(e)
        raise Exception('Invalid input')
    return rec_table
