'''
    Module to extract the top-K packages based on GR model Baseline

'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))
from itertools import product
from statistics import mean
import time
import pandas as pd
from collections import defaultdict
import numpy as np
from model import DataHelper as dh
from parameters import common_parameters as p
import math
from model import Arguments
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

LOGS_PATH = p.LOGS_PATH
kitems = p.top_k_items
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
packages_path = p.PACKAGES_PATH
num_packages = p.num_packages


def mae_aggregation():
    print('Balanced preference for G=', balanced_preference)
    temp_pref_u_P = pref_u_P
    sum_pref = pref_u_P.sum()
    temp_pref_u_P['percentage'] = temp_pref_u_P.divide(sum_pref, axis=0)
    percentage_data = temp_pref_u_P['percentage']
    percentage_data = percentage_data.to_dict()
    temp_pref_u_P['difference'] = abs(temp_pref_u_P['percentage'] - balanced_preference)
    mae_score = temp_pref_u_P['difference'].mean()

    return mae_score



def find_package_fairness(row):
    global G
    item1 = int(row['c1_item'])
    item2 = int(row['c2_item'])
    fair = 0
    for user in G:
        c1 = item1 in c1_top_rated_items[user]
        c2 = item2  in c2_top_rated_items[user]
        result = c1 or c2
        fair = fair + result
    fair_score = fair / len(G)

    return fair_score

def get_index_series(index_list):
    idx_list = []
    for i in index_list:
        idx = i[0]
        idx_list.append(idx)

    return idx_list


def final_packages(row):
    item1 = int(row['c1_item'])
    item2 = int(row['c2_item'])
    package = (item1, item2)
    top_packages.append(package)


###############################################################
if __name__ == "__main__":
    print("GR model")

    Arguments.create_parser(sys.argv, globals())  # globals(): pass the global vars from one module to another
    print("kitems:", kitems)
    top_k = int(kitems)

    filename = temp_path+'Extract_User_Preferences.obj'
    data = dh.load_Data(filename)
    ratings_c1 = data[0]
    ratings_c2 = data[1]

    '''
        Extract users
    '''
    G = list(ratings_c1.index)
    print('[INFO] Users', G)
    g_size = len(G)

    '''
        Extract top rated items for each user
    '''
    c1_top_rated_items = defaultdict(list)
    c2_top_rated_items = defaultdict(list)

    c1_total_top_rated_items = p.top_k_items[ 0 ]
    c2_total_top_rated_items = p.top_k_items[ 0 ]

    for user in G:
        # Category 1
        x_top = ratings_c1.loc[user].sort_values(ascending=False)[:c1_total_top_rated_items]
        x = x_top.index.labels[0].tolist()
        x = [x+1 for x in x]
        c1_top_rated_items[user] = x

        # Category 2
        x_top = ratings_c2.loc[user].sort_values(ascending=False)[:c2_total_top_rated_items]
        x = x_top.index.labels[0].tolist()
        x = [x + 1 for x in x]
        c2_top_rated_items[user] = x

    print( '[INFO] Top %d (fixed) rated items for each user in each category' % (p.top_k_items[ 0 ]) )
    print('[INFO] Category 1')
    print(c1_top_rated_items)
    print('[INFO] Category 2')
    print(c2_top_rated_items)

    '''
        Load initial ratings for Category 1
    '''
    print('[INFO] Loding initial C1 ratings')
    matrix_filename = data_path+"M_u_i_dataset.1.txt"
    M_u_i = dh.read_file_to_df(matrix_filename)
    c1_ratings = pd.DataFrame(M_u_i)
    index = [x + 1 for x in c1_ratings.index]
    columns = [x + 1 for x in c1_ratings.columns]
    c1_ratings = c1_ratings.set_index([index])
    c1_ratings.columns = [columns]
    c1_initial_ratings = c1_ratings.loc[G]

    '''
        Load initial ratings for Category 2
    '''
    print('[INFO] Loding initial C2 ratings')
    matrix_filename = data_path+"M_u_i_dataset.2.txt"
    M_u_i = dh.read_file_to_df(matrix_filename)
    c2_ratings = pd.DataFrame(M_u_i)
    index = [x + 1 for x in c2_ratings.index]
    columns = [x + 1 for x in c2_ratings.columns]
    c2_ratings = c2_ratings.set_index([index])
    c2_ratings.columns = [columns]
    c2_initial_ratings = c2_ratings.loc[G]

    print('[INFO] Calculating Expertiness per user in C1')
    c1_initial_ratings.replace(0.0,np.NaN, inplace=True)
    c1_count = c1_initial_ratings.count(axis=1)
    c1_total_rated_items = c1_count.sum()
    c1_expertiness = c1_count / c1_total_rated_items

    del c1_initial_ratings
    del c1_ratings
    del c1_count

    print('[INFO] Calculating Expertiness per user in C2')
    c2_initial_ratings.replace(0.0, np.NaN, inplace=True)
    c2_count = c2_initial_ratings.count(axis=1)
    c2_total_rated_items = c2_count.sum()
    c2_expertiness = c2_count / c2_total_rated_items
    print(c2_expertiness)

    del c2_initial_ratings
    del c2_ratings
    del c2_count

    '''
        Multiply preference X pct_user
    '''
    func = lambda x: np.asarray(x) * np.asarray(c1_expertiness)
    ratings_c1 = ratings_c1.apply(lambda col: col * c1_expertiness)
    ratings_c2 = ratings_c2.apply(lambda col: col * c2_expertiness)

    '''
        Create the I2G for each category
    '''
    print('[INFO] Generating I2G for each category')
    ### Category 1
    I2G_c1 = ratings_c1.sum(axis=0)
    I2G_c1.sort_values(ascending=False, inplace=True)
    I2G_c1 = I2G_c1[:top_k]

    ### Category 2
    I2G_c2 = ratings_c2.sum(axis=0)
    I2G_c2.sort_values(ascending=False, inplace=True)
    I2G_c2 = I2G_c2[:top_k]

    '''
        Generate packages
    '''
    print('[INFO] Generating Packages using the top-%d I2G items from each category' % top_k)
    I2G_c1_index = list(I2G_c1.index.values)
    I2G_c2_index = list(I2G_c2.index.values)
    I2G_c1_index = get_index_series(I2G_c1_index)
    I2G_c2_index = get_index_series(I2G_c2_index)
    packages = list(product(I2G_c1_index, I2G_c2_index))
    print('[INFO] We formed %d packages' % len(packages))
    print('[INFO] Packages')
    print(packages)

    '''
        Calculate P2G
    '''
    print('[INFO] Calculating P2G (Multiplying I2G value for each category)')
    cols = ['c1_item', 'c2_item', 'g_score'] #g_score is P2G
    df = pd.DataFrame(columns=cols)

    for package in packages:
        c1_item = package[0]
        c2_item = package[1]
        value1 = I2G_c1.loc[c1_item][0]
        value2 = I2G_c2.loc[c2_item][0]
        package_group_score = value1 * value2
        row = [c1_item, c2_item, package_group_score]
        df = df.append(pd.Series(row, index=cols), ignore_index=True)

    df = df.astype({"c1_item": int, "c2_item": int, "g_score": float})
    pd.options.display.precision = 10

    '''
        Calculate the fairness of each package
    '''
    df['fairness'] = df.apply(find_package_fairness, axis=1)

    '''
        Calculate the SCORE_fairness
    '''
    print('[INFO] Calculate the Score_final for each package')
    df['score_f'] = df['g_score'] * df['fairness']
    df.sort_values(by=['score_f'], ascending=False, inplace=True)

    '''
        Pick the top-k packages
    '''
    print('[INFO] Pick the final top-%d packages' % num_packages)
    df_packages = df[:num_packages]
    top_packages = []
    df_packages.apply(final_packages, axis=1)

    '''
        Export packages for next stage
    '''
    data = top_packages
    dh.save_data(data, packages_path+'GRmodel_top_Packages.obj')
    print( "Top {} Packages:".format( num_packages ) )
    print( top_packages )
    dh.save_top_packages_list( packages_path + "GRmodel_top_packages.txt", top_packages )

    '''
        Calculate Error    
    '''
    print('[INFO] Calculate Balance Error')
    '''
        Load the dense matrix
    '''
    filename = temp_path+'Build_Dense_Matrix.' + str(1) + '.obj'
    data = dh.load_Data(filename)
    '''
        Load importance information
    '''
    importance_c1 = data[3]

    '''
        Load the dense matrix
    '''
    filename = temp_path+'Build_Dense_Matrix.' + str(2) + '.obj'
    data = dh.load_Data(filename)
    ratings_G = data[0]
    '''
        Load importance information
    '''
    importance_c2 = data[3]


    balanced_preference = 1 / ratings_G.shape[0]
    top_k_total_error = 0
    mae_percentage_data = []
    for p in top_packages:
        item_c1 = [p[0]]
        item_c2 = [p[1]]
        p1 = importance_c1.loc[:, item_c1]
        p2 = importance_c2.loc[:, item_c2]
        pref_u_P = pd.concat([p1, p2], axis=1)
        pref_u_P = pref_u_P.sum(axis=1)

        '''
            Calculate Percentage
        '''

        error_G_P = mae_aggregation()
        print('error_G_P=', error_G_P)
        top_k_total_error = top_k_total_error + error_G_P

    print('Total error for the top %d recommended packages %f' % (int(num_packages), top_k_total_error))
    print('Sum of errors=' + str(top_k_total_error))
