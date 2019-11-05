'''
    Module to extract the top-K packages based on Fairness Baseline

'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))
import pandas as pd
from model import DataHelper as dh
from parameters import common_parameters as p
from model import Arguments
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

outputfile = ""
kitems = p.top_k_items
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
packages_path = p.PACKAGES_PATH
num_packages = p.num_packages


def mae_aggregation():
    print('Balanced preference for G=',balanced_preference)
    temp_pref_u_P = pref_u_P
    sum_pref = pref_u_P.sum()
    temp_pref_u_P['percentage'] = temp_pref_u_P.divide(sum_pref, axis=0)
    percentage_data = temp_pref_u_P['percentage']
    percentage_data = percentage_data.to_dict()
    temp_pref_u_P['difference'] = abs(temp_pref_u_P['percentage'] - balanced_preference)
    mae_score = temp_pref_u_P['difference'].mean()

    return mae_score


def select_top_packages():
    pairs = []

    pairs.append((top_ranked_c1[0], top_ranked_c2[0]))
    print(top_ranked_c1[0], top_ranked_c2[0])

    i = 1
    try:
        while len(pairs) < num_packages:
            print(top_ranked_c1[i], top_ranked_c2[i - 1])
            print(top_ranked_c1[i - 1],top_ranked_c2[i])
            print(top_ranked_c1[i], top_ranked_c2[i])

            pairs.append((top_ranked_c1[i], top_ranked_c2[i - 1]))
            pairs.append((top_ranked_c1[i - 1], top_ranked_c2[i]))
            pairs.append((top_ranked_c1[i], top_ranked_c2[i]))

            i = i + 1
    except:
        pass

    # print pairs
    return pairs[:int(num_packages)]


###############################################################
if __name__ == "__main__":
    print("Fairness")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another

    '''
        Load the dense matrix
    '''
    filename =  temp_path+'Build_Dense_Matrix.' + str(1) + '.obj'
    data = dh.load_Data(filename)
    ratings_G = data[0]

    df_1 = pd.DataFrame()
    users_1 = list(ratings_G.index)
    print('Users=',users_1)
    for u in users_1:
        u_ratings_1 = ratings_G.loc[u,:].sort_values(ascending=False)
        max = u_ratings_1[0:int(kitems)]
        df_1 = pd.concat([df_1, max])

    df_1 = df_1[0].sort_values(ascending=False)
    index_1 = list(df_1.index)
    top_ranked_c1 = [i[0] for i in index_1]
    top_ranked_c1 = sorted(set(top_ranked_c1), key=top_ranked_c1.index)
    print('Items=',top_ranked_c1)

    '''
        Load importance information
    '''
    importance_c1 = data[3]
    filename =  temp_path+'Build_Dense_Matrix.' + str(2) + '.obj'
    data = dh.load_Data(filename)
    ratings_G = data[0]

    df_2 = pd.DataFrame()
    users_2 = list(ratings_G.index)
    print('Users=',users_2)
    for u in users_2:
        u_ratings_2 = ratings_G.loc[u, :].sort_values(ascending=False)
        max = u_ratings_2[0:int(kitems)]
        df_2 = pd.concat([df_2, max])

    df_2 = df_2[0].sort_values(ascending=False)
    index_2 = list(df_2.index)

    top_ranked_c2 = [i[0] for i in index_2]
    top_ranked_c2 = sorted(set(top_ranked_c2), key=top_ranked_c2.index)
    print('Items=',top_ranked_c2)

    '''
        Load importance information
    '''
    importance_c2 = data[3]
    top_packages = select_top_packages()

    '''
        Export the list of the Top-k packages
    '''
    data = top_packages
    dh.save_data(data,  packages_path+'Fairness_top_Packages.obj')

    print( "Top {} Packages:".format( num_packages ) )
    print( top_packages )
    dh.save_top_packages_list( packages_path + "Fairness_top_packages.txt", top_packages )

    balanced_preference = 1 /ratings_G.shape[0]
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
        print('error_G_P=',error_G_P)
        top_k_total_error = top_k_total_error + error_G_P

    print('Total error for the top %d recommended packages %f' % (int(num_packages), top_k_total_error))
    print('Sum of errors=' + str(top_k_total_error))
