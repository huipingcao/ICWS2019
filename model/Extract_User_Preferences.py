import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))
import pandas as pd
import numpy as np
from model import DataHelper as dh
from model import Arguments
from parameters import common_parameters as p

import warnings
warnings.filterwarnings('ignore')

outputfile = ""
aggregation = p.agg_function
pt = p.pt
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
packages_path = p.PACKAGES_PATH

df_agg = pd.DataFrame()

###############################################################
if __name__ == "__main__":
    print("Extract_User_Preferences")

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

    poc_df.drop(['totals'], axis=1, inplace=True)
    poc_df.set_index('user_id', inplace=True)
    print(poc_df)

    '''
        Extract cat preferences from POC for CAT 1
    '''
    print('CAT 1')
    poc_c1 = poc_df['c1']
    prob_and_poc_c1 = prob_u_i_c1.apply(lambda x: np.asarray(x) + np.asarray(poc_c1))

    '''
        Calculate for each member the Sum of the other members' probabilities
    '''
    sum_prob_u_i_for_G_c1 = prob_u_i_c1.sum(axis=0)
    influence_c1 = sum_prob_u_i_for_G_c1 - prob_u_i_c1
    pref_u_P_c1 = prob_and_poc_c1.multiply(influence_c1, axis=1)

    '''
        Extract cat preferences from POC for CAT 2
    '''
    print('CAT 2')
    poc_c2 = poc_df['c2']
    prob_and_poc_c2 = prob_u_i_c2.apply(lambda x: np.asarray(x) + np.asarray(poc_c2))

    '''
        Calculate for each member the Sum of the other members' probabilities
    '''
    sum_prob_u_i_for_G_c2 = prob_u_i_c2.sum(axis=0)
    influence_c2 = sum_prob_u_i_for_G_c2 - prob_u_i_c2
    pref_u_P_c2 = prob_and_poc_c2.multiply(influence_c2, axis=1)

    '''
        Export the preferences
        These will be used instead of the raw ratings
    '''
    data = [pref_u_P_c1, pref_u_P_c2]
    dh.save_data(data, temp_path+'Extract_User_Preferences.obj')
