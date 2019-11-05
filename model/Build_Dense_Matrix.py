'''
    Module to build a dense matrix using the predicted ratings.
'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

import pandas as pd
from scipy.stats.mstats import gmean
import sys
from model import DataHelper as dh
from model import Arguments
from parameters import common_parameters as p

outputfile = ""
kitems = p.top_k_items
G = []
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH

def geom_mean(items):
    return gmean(items)

def insert_rating(row):
    u_id = row['user_id']
    i_id = row['item_id']
    r = row['balanced_rating']
    ratings_G.at[u_id,i_id] = r

###############################################################
if __name__ == "__main__":
    print("Build_Dense_Matrix")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another

    if not G:
        print("G is empty")
        sys.exit(0)

    '''
        Load M_u_i
    '''
    matrix_filename = data_path+"M_u_i_dataset."+outputfile+".txt"
    M_u_i = dh.read_file_to_df(matrix_filename)

    ratings = pd.DataFrame(M_u_i)
    index = [x+1 for x in ratings.index]
    columns = [x+1 for x in ratings.columns]
    ratings = ratings.set_index([index])
    ratings.columns = [columns]

    print('M_u_i | Users=', len(ratings.index), 'Items=',len(ratings.columns))

    '''
        Load predictions
    '''
    filename = temp_path+'Predict_Ratings.'+outputfile+'.obj'
    data = dh.load_Data(filename)
    predictions = data[0]

    '''
        Extract submatrix for G
    '''
    ratings_G = ratings.loc[G]

    '''
       Send each prediction row to be inserted into ratings_G 
    '''
    predictions.apply(insert_rating, axis=1)

    '''
        For each member of G find his/her top-k items
        and place them in a set
    '''
    top_k_items_for_G = set()

    if kitems < 1:
        top_k = int(len(ratings.columns) * kitems)
    else:
        top_k = int(kitems)

    for u in G:
        u_sorted_items = ratings_G.loc[u]
        u_sorted_items.sort_values(ascending=False, inplace=True)
        top = u_sorted_items[0:top_k]
        top = top.keys().codes
        top = set(x+1 for x in top[0])
        top_k_items_for_G = top_k_items_for_G.union(top)

    top_k_items_for_G = list(top_k_items_for_G)
    print('top_k items for G')
    print(top_k_items_for_G)
    print("Total items for G:",len(top_k_items_for_G))

    '''
        Calculate the item's rating average for G        
    '''
    items_mean_for_G = ratings_G
    items_mean_for_G = geom_mean(items_mean_for_G)
    idx = [x+1 for x in range(len(items_mean_for_G))]
    items_mean_for_G = pd.Series(items_mean_for_G, index=idx)

    '''
        Pick k-top items based on their rating mean
    '''
    items_mean_for_G_sort = items_mean_for_G.sort_values(ascending=False)
    k_items_mean_for_G_sort = items_mean_for_G_sort[0:top_k]
    top_k_items_mean = k_items_mean_for_G_sort.index.values
    top_k_items_mean = [x for x in top_k_items_mean]  #as a list
    print()

    '''
        Calculate the rating total for each user in G
    '''
    ratings_G_sum = ratings_G.sum(axis=1)
    '''
        Calculate the probability that each user picks an item based on his/her ratings
    '''
    prob_u_i = ratings_G.divide(ratings_G_sum, axis=0)

    '''
        Pick k-top items based on the user's probability mean
    '''
    print('#'*50)
    '''
        Calculate the relative importance of item i for user u compared with the other group members
    '''
    sum_prob_item_for_G = prob_u_i.sum(axis=0)
    importance_u_i_for_G = prob_u_i.divide(sum_prob_item_for_G, axis=1)

    # Export data from this module
    data = [ratings_G, top_k_items_mean, top_k_items_for_G, prob_u_i, importance_u_i_for_G ]  # the missing ratings predictions for each of the users in G in every CC
    dh.save_data(data, temp_path+'Build_Dense_Matrix.'+outputfile+'.obj')

    dh.save_df_to_file(ratings_G, temp_path+'dense_matrix.'+outputfile+'.txt')


