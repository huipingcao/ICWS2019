'''
    Module to calculate the POC and aPOC
'''

import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

import pandas as pd
from collections import defaultdict
import numpy as np
import sys
from model import DataHelper as dh
from model import Arguments
from parameters import common_parameters as p

outputfile = ""
G = []
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH

###############################################################
if __name__ == "__main__":
    print("Get_POC")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another

    if not G:
        print("G is empty")
        sys.exit(0)

    POC = defaultdict(list)

    '''
        Load ratings for Category 1
    '''
    matrix_filename = data_path + "M_u_i_dataset.1.txt"
    M_u_i = dh.read_file_to_df(matrix_filename)
    ratings = pd.DataFrame(M_u_i)

    index = [x + 1 for x in ratings.index]
    columns = [x + 1 for x in ratings.columns]
    ratings = ratings.set_index([index])
    ratings.columns = [columns]

    '''
        Extract submatrix for G
    '''
    ratings_G_1 = ratings.loc[G]
    ratings_G_1 = ratings_G_1.replace(0, np.nan)
    ratings_G_1.index.name = 'user_id'

    '''
        Load ratings for Category 2
    '''
    matrix_filename = data_path+"M_u_i_dataset.2.txt"
    M_u_i = dh.read_file_to_df(matrix_filename)

    ratings = pd.DataFrame(M_u_i)
    index = [x + 1 for x in ratings.index]
    columns = [x + 1 for x in ratings.columns]
    ratings = ratings.set_index([index])
    ratings.columns = [columns]

    '''
            Extract submatrix for G
    '''
    ratings_G_2 = ratings.loc[G]
    ratings_G_2 = ratings_G_2.replace(0, np.nan)
    ratings_G_2.index.name = 'user_id'

    '''
        Count the number of ratings for Cat1 per user
    '''
    cat1_rated = len(ratings_G_1.columns) - ratings_G_1.isnull().sum(axis=1)

    '''
        Count the number of ratings for Cat2 per user
    '''
    cat2_rated = len(ratings_G_2.columns) - ratings_G_2.isnull().sum(axis=1)

    '''
        Add the number of ratings for both categories
    '''
    total_rated_items = pd.DataFrame(dict(c1 = cat1_rated, c2 = cat2_rated)).reset_index()
    total_rated_items['totals'] = total_rated_items['c1'] + total_rated_items['c2']
    total_rated_items['c1'] = total_rated_items['c1'] / total_rated_items['totals']
    total_rated_items['c2'] = total_rated_items['c2'] / total_rated_items['totals']
    POC = total_rated_items.set_index('user_id').T.to_dict('list')

    '''
        Calculate AdjustedPOC
    '''
    total_rated_items_adj = pd.DataFrame(dict(c1=cat1_rated, c2=cat2_rated)).reset_index()
    total_rated_items_adj['c1'] = total_rated_items_adj['c1'] / len(ratings_G_1.columns)
    total_rated_items_adj['c2'] = total_rated_items_adj['c2'] / len(ratings_G_2.columns)
    total_rated_items_adj['c1'] = total_rated_items_adj['c1'] * total_rated_items['c1']
    total_rated_items_adj['c2'] = total_rated_items_adj['c2'] * total_rated_items['c2']
    total_rated_items_adj['totals'] = total_rated_items_adj['c1'] + total_rated_items_adj['c2']
    total_rated_items_adj['c1'] = total_rated_items_adj['c1'] / total_rated_items_adj['totals']
    total_rated_items_adj['c2'] = total_rated_items_adj['c2'] / total_rated_items_adj['totals']
    POC_adj = total_rated_items_adj.set_index('user_id').T.to_dict('list')

    # Export data from this module
    data = [POC, total_rated_items, POC_adj, total_rated_items_adj]
    dh.save_data(data, temp_path+'Find_POC.obj')

