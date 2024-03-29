'''

    Module to calculate the Item-Item Collaborative Filtering

'''

import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
import sys
from model import DataHelper as dh
from model import Arguments
from parameters import common_parameters as p
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

outputfile = ""
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
G=[]

def max_items_rated(total_rated, active_user):
    if active_user in total_item_rated:
        if total_rated > total_item_rated[active_user]:
            total_item_rated[active_user] = total_rated
    else:
        total_item_rated[active_user] = total_rated


###############################################################
if __name__ == "__main__":
    print("I-I-CF")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another

    if not G:
        print("G is empty")
        sys.exit(0)

    print('Group members: ', G)

    columns_predictions = ['user_id','item_id','rating','u-i','bics','cc']
    predictions_i_i_df = pd.DataFrame(columns= columns_predictions)
    total_item_rated = {}

    '''
    Load data
    '''
    filename = temp_path + 'CC_Utils_data.'+outputfile+'.obj'
    CC_Utils_data = dh.load_Data(filename)
    sim_u_v_in_CC = CC_Utils_data[5]

    filename = temp_path + 'Find_SIM_i_f.'+outputfile+'.obj'
    Find_SIM_i_f_data = dh.load_Data(filename)
    sim_i_j_in_CC = Find_SIM_i_f_data[4]
    items_col_index = sim_i_j_in_CC.keys()

    '''
        Load M_u_i_dataset to calculate user and item means
    '''

    filename = data_path + "M_u_i_dataset." + outputfile + ".txt"
    M_u_i = dh.read_file_to_df( filename )
    idx = M_u_i.index
    cols = M_u_i.columns

    print('M_u_i | Users= ', len(idx), 'Items=', len(cols))
    M_u_i = M_u_i.replace(0, np.NaN)
    user_means = M_u_i.mean(axis=1)
    item_means = M_u_i.mean(axis=0)
    user_means = user_means.fillna(0)
    item_means = item_means.fillna(0)

    filename = temp_path + 'Find_U-I_belong_DF.' + outputfile + '.obj'
    users_belong_to = dh.load_Data(filename)
    total_missing_ratings_for_G = 0

    CCs = [temp_path + 'Find_UI_items.'+outputfile+'.obj', temp_path + 'Find_SIM_i_f.'+outputfile+'.obj']
    for e, cc in enumerate(CCs):
        print('v' * 80)
        print(e,cc)
        filename = cc
        data = dh.load_Data(filename)
        biclusters = data[0]

        for active_user in G:
            print('^' * 80)
            bic_for_user = set(users_belong_to[e][active_user])

            for element in bic_for_user:
                rating = biclusters[element]
                rating_index = [ix+1 for ix in rating.index]
                rating_columns = [ix + 1 for ix in rating.columns]
                rating = rating.set_index([rating_index])
                rating.columns= rating_columns
                rating = rating.replace(0, np.NaN)
                item_users_df = rating.T
                sub_user_means = user_means[list(rating.index)]
                sub_item_means = item_means[list(item_users_df.index)]

                user_items_normalized_df = rating.subtract(sub_user_means,axis=0)
                user_items_normalized_df.fillna(0, inplace=True)
                item_users_normalized_df = item_users_df.subtract(sub_item_means, axis=0)
                item_similarity = 1 - pairwise_distances(user_items_normalized_df.T, metric='cosine')
                item_similarity_df = pd.DataFrame(item_similarity, index=user_items_normalized_df.columns, columns=user_items_normalized_df.columns)
                sim_i_j_in_CC_df = pd.DataFrame(sim_i_j_in_CC)
                sim_i_j_in_CC_df = sim_i_j_in_CC_df.loc[user_items_normalized_df.columns,user_items_normalized_df.columns]
                sim_i_j_in_CC_df.fillna(1, inplace=True)

                item_item_sim_adj_df = sim_i_j_in_CC_df.multiply(item_similarity_df, axis=0)

                '''
                    Predictions
                '''
                active_user_ratings = rating.loc[active_user]
                active_user_missing_ratings = active_user_ratings[active_user_ratings.isnull()].index
                total_missing_ratings = len(active_user_missing_ratings)
                m_item_normalized = item_users_normalized_df[active_user]
                sim_m_item_j = item_item_sim_adj_df[active_user_missing_ratings]

                for i in sim_m_item_j.columns:
                    sim_m_item_j.at[i,i] = np.nan

                numerator_df = sim_m_item_j.multiply(m_item_normalized,axis=0)
                denominator_df = numerator_df
                denominator_df = denominator_df.abs()
                denominator_df[(denominator_df > 0)] = 1
                denominator_df = denominator_df.multiply(sim_m_item_j, axis=0)
                numerator_sum_df = numerator_df.sum()
                denominator_sum_df = denominator_df.abs().sum()
                right = numerator_sum_df/denominator_sum_df
                right = right.replace(np.nan,0)

                prediction_u_I = sub_item_means[active_user_missing_ratings] + right
                print('Total missing ratings PREDICTED for active user', active_user,'in CC', element,'=', len(prediction_u_I))
                prediction_u_I_df = pd.DataFrame(prediction_u_I, columns=['rating'])
                prediction_u_I_df.index.rename('item_id', inplace=True)
                prediction_u_I_df.reset_index(level=0, inplace=True)
                prediction_u_I_df['user_id'] = active_user
                prediction_u_I_df['u-i'] = 0
                prediction_u_I_df['bics'] = e
                prediction_u_I_df['cc'] = element
                prediction_u_I_df = prediction_u_I_df[columns_predictions]
                predictions_i_i_df = pd.concat([predictions_i_i_df, prediction_u_I_df])
                total_missing_ratings_for_G = total_missing_ratings_for_G + len(prediction_u_I_df)


    predictions_i_i_df.reset_index(drop=True, inplace=True)
    dh.save_df_to_file(predictions_i_i_df, temp_path + 'predictions-I-I-CF.'+outputfile+'.txt')
    print()
    predictions_i_i_df_gb = predictions_i_i_df.drop(columns=['u-i','bics', 'cc'])
    predictions_i_i_avg_df = predictions_i_i_df_gb.groupby(['user_id','item_id']).mean()
    agg_predicted_ratings_df = predictions_i_i_avg_df.reset_index()
    dh.save_df_to_file(agg_predicted_ratings_df, temp_path + 'agg_predictions-I-I-CF.'+outputfile+'.txt')

    data = [predictions_i_i_df, agg_predicted_ratings_df]             #the missing ratings predictions for each of the users in G in every CC
    dh.save_data(data, temp_path + 'I-I-CF.'+outputfile+'.obj')