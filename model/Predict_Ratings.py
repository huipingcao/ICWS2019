'''
    Module for rating prediction
'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

import pandas as pd
import numpy as np
import sys
from model import DataHelper as dh
from parameters import common_parameters as p
from model import Arguments
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')


outputfile = ""
alpha = 0.6
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH

###############################################################
if __name__ == "__main__":
    print("Predict_Ratings")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another

    '''
        Load M_u_i_dataset to calculate user and item means
    '''
    filename = temp_path+'M_u_i.' + outputfile + '.obj'
    M_u_i = dh.load_Data(filename)
    idx = [x + 1 for x in M_u_i.index]
    cols = [x + 1 for x in M_u_i.columns]
    idx = pd.Index(idx)
    M_u_i.columns = cols
    M_u_i = M_u_i.set_index(idx)
    M_u_i = M_u_i.replace(0, np.NaN)
    r, c = M_u_i.shape
    print('M_u_i | Users=', r, 'Columns=',c)
    user_means = M_u_i.mean(axis=1)
    item_means = M_u_i.mean(axis=0)

    '''
        Load data
    '''
    filename = temp_path+'U-U-CF.'+outputfile+'.obj'
    U_U_CF_data = dh.load_Data(filename)
    U_U_CF_data_df = U_U_CF_data[1]
    filename = temp_path+'I-I-CF.'+outputfile+'.obj'
    I_I_CF_data = dh.load_Data(filename)
    I_I_CF_data_df = I_I_CF_data[1]

    unique_u_idx = U_U_CF_data_df['user_id'].unique()
    unique_i_idx = U_U_CF_data_df['item_id'].unique()
    print("U_U_CF | Users in G = ", len(unique_u_idx),'Items=',len(unique_i_idx))

    unique_u_idx = I_I_CF_data_df['user_id'].unique()
    unique_i_idx = I_I_CF_data_df['item_id'].unique()
    print("I_I_CF | Users in G = ", len(unique_u_idx), 'Items=', len(unique_i_idx))

    I_I_CF_data_df['rating'].fillna(0, inplace=True)
    U_U_CF_data_df['times_alpha'] = U_U_CF_data_df['rating'] * alpha
    I_I_CF_data_df['times_alpha'] = I_I_CF_data_df['rating'] * (1-alpha)
    ratings_df = pd.merge(U_U_CF_data_df, I_I_CF_data_df, on=['user_id','item_id'], how='inner')
    ratings_df['balanced_rating'] = ratings_df['times_alpha_x'] + ratings_df['times_alpha_y']
    ratings_df = ratings_df[['user_id', 'item_id', 'balanced_rating']]

    dh.save_df_to_file(ratings_df, temp_path+'rating_predictions.'+outputfile+'.txt')

    data = [ratings_df, alpha]
    dh.save_data(data, temp_path+'Predict_Ratings.'+outputfile+'.obj')



