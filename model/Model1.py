'''
    Module to extract the top-K packages based on Model 1

'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))
import pandas as pd
from scipy.stats.mstats import gmean
import numpy as np
from model import DataHelper as dh
from parameters import common_parameters as p
from  itertools import product
from model import Arguments
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

outputfile = ""
aggregation = p.agg_function
pt = p.pt
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
packages_path = p.PACKAGES_PATH
num_packages = p.num_packages


df_agg = pd.DataFrame()

def find_package_probs(row):
    global  df_agg
    a = row['item_c1']
    b = row['item_c2']
    percentages = mae_percentage_data

    for p in percentages:
        if a == p[0] and b == p[1]:
            vals_dict = p[2]
            temp = pd.DataFrame(vals_dict,index=[0])
            df_agg = pd.concat([df_agg, temp])

def find_score():
    diff_df = abs(df_agg - balanced_pref)
    diff_df_avg = diff_df.mean(axis=1)
    score = diff_df_avg.sum()
    return score

def geom_mean():
    return gmean(pref_u_P)


def mae_aggregation():
    temp_pref_u_P = pref_u_P
    sum_pref = pref_u_P.sum()
    temp_pref_u_P['percentage'] = temp_pref_u_P.divide(sum_pref, axis=0)
    percentage_data = temp_pref_u_P['percentage']
    percentage_data = percentage_data.to_dict()
    temp_pref_u_P['difference'] = abs(temp_pref_u_P['percentage'] - balanced_pref)
    mae_score = temp_pref_u_P['difference'].mean()
    data = (item_c1, item_c2,percentage_data)
    mae_percentage_data.append(data)

    return  mae_score


def agg_function():
    global aggregation

    if aggregation == 0:
        result = pref_u_P.mean()
        mae_aggregation()
        return result

    elif aggregation == 1:
        result = pref_u_P.max()
        mae_aggregation()
        return result

    elif aggregation == 2:
        result = pref_u_P.min()
        mae_aggregation()
        return result

    elif aggregation == 3:
        result = geom_mean()
        mae_aggregation()
        return result

    elif aggregation == 4:
        result = pref_u_P.sum()
        mae_aggregation()
        return result

    else:
        return mae_aggregation()


###############################################################
if __name__ == "__main__":
    print("Model 1")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another
    dh.print_agg_method(aggregation)

    '''
        Load data from Build_Dense_Matrix
        CAT 1
    '''
    filename = temp_path+'Build_Dense_Matrix.1.obj'
    data = dh.load_Data(filename)
    ratings_c1 = data[0]
    top_k_c1 = data[2]
    prob_u_i_c1 = data[3]
    importance_u_i_c1 = data[4]
    print('Top C1')
    print(top_k_c1)

    '''
        Load data from Build_Dense_Matrix
        CAT 2
    '''
    filename = temp_path+'Build_Dense_Matrix.2.obj'
    data = dh.load_Data(filename)
    ratings_c2 = data[0]
    top_k_c2 = data[2]
    prob_u_i_c2 = data[3]
    importance_u_i_c2 = data[4]
    print('Top C2')
    print(top_k_c2)

    '''
        Load POC data
    '''
    filename = temp_path+'Find_POC.obj'
    data = dh.load_Data(filename)

    if pt == 0:
        print('POC Type = Adjusted')
        poc_df = data[3]
    else:
        print('POC Type = Normal')
        poc_df = data[1]

    print(poc_df)

    '''
        Generate packages
    '''
    packages = list(product(top_k_c1, top_k_c2))
    print('We formed %d packages' % len(packages))
    print(packages)

    '''
        Generate a DF with package pref for CAT 1

        Extract cat preferences from POC for CAT 1
    '''
    poc_c1 = poc_df['c1']
    prob_and_poc_c1 = prob_u_i_c1.apply(lambda x: np.asarray(x) * np.asarray(poc_c1))

    '''
        Total pref for Cat 1  eq.14
    '''
    print('\nPref(u,P) for Cat1')
    pref_u_P_c1 = prob_and_poc_c1.multiply(importance_u_i_c1, axis=1)

    '''
        Generate a DF with package pref for CAT 2

        Extract cat preferences from POC for CAT 2
    '''
    poc_c2 = poc_df['c2']
    prob_and_poc_c2 = prob_u_i_c2.apply(lambda x: np.asarray(x) * np.asarray(poc_c2))
    '''
        Total pref for Cat 2 eq.14
    '''
    print('Pref(u,P) for Cat2')
    pref_u_P_c2 = prob_and_poc_c2.multiply(importance_u_i_c2, axis=1)

    '''
        Users in G
    '''
    G = poc_c1
    print('Total users in G=', len(G))
    balanced_pref = 1 / len(G)

    print('Pref(u,P) for G')
    recommended_packages = []
    mae_percentage_data = []

    for p in packages:
        item_c1, item_c2 = p
        p1 = pref_u_P_c1.iloc[:,item_c1-1]
        p2 = pref_u_P_c2.iloc[:,item_c2-1]
        pref_u_P = p1 * p2
        pref_G_P_agg = agg_function()
        data = (item_c1, item_c2, pref_G_P_agg)
        recommended_packages.append(data)

    if aggregation == 5:
        recommended_packages = sorted(recommended_packages, key=lambda tup: (tup[2]), reverse=False)
    else:
        recommended_packages = sorted(recommended_packages, key=lambda tup: (tup[2]), reverse=True)

    recommended_packages_df = pd.DataFrame(recommended_packages, columns=['item_c1', 'item_c2', 'score'])
    recommended_packages_df['agg_function'] = aggregation
    print('Top %d packages' % num_packages)
    print(recommended_packages_df.loc[0:num_packages-1,:])

    '''
        Export the list of the Top-k packages
    '''
    top_packages = recommended_packages_df.loc[0:num_packages-1, :]
    top_packages['package'] = top_packages[['item_c1', 'item_c2']].apply(tuple, axis=1)
    top_packages = list(top_packages['package'])
    print( "Top {} Packages:".format( num_packages ) )
    print( top_packages )
    dh.save_top_packages_list( packages_path + "Model1_top_packages.txt", top_packages )

    data = top_packages
    dh.save_data(data, packages_path+'Model1_top_Packages.obj')

    print(mae_percentage_data)
    data = [recommended_packages, recommended_packages_df, mae_percentage_data, pref_u_P_c1, prob_and_poc_c1,
            pref_u_P_c2, prob_and_poc_c2]
    filename = dh.save_data(data, temp_path+'Test_Pref_u_P.obj')

    score = 0
    if aggregation != 5:
        t_10 = recommended_packages_df.loc[0:num_packages-1,:]
        t_10 = t_10.drop(['score','agg_function'], axis=1)
        score = t_10.apply(find_package_probs, axis=1)
        score = find_score()
    else:
        t_10_error_sum = recommended_packages_df.loc[0:num_packages-1, :]
        score = t_10_error_sum['score'].sum()

    print('Sum of errors=' + str(score))
    print()