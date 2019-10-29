'''
    Utitity functions for Co-clusters
'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

import pandas as pd
from collections import defaultdict
from model import Arguments
import sys
from itertools import combinations,permutations
import numpy as np
from parameters import common_parameters as p
from model import DataHelper as dh

outputfile = ""
data_path = p.DATA_PATH
temp_path = p.TEMP_PATH

def pause():
    programPause = input("Press the <ENTER> key to continue...")

def read_CC_File(cc_filename):
    with open(cc_filename,'r') as f:
        lines = f.readlines()

        # declarations
        biclusters = defaultdict(list)
        bic = 0

        for i in range(1, len(lines), 3):
            r = lines[i + 1].replace('\n','').replace('R','')   # Rows in line 1
            biclusters[bic].append(r.split())
            c = lines[i + 2].replace('\n','').replace('C','')   # Columns in line 2
            biclusters[bic].append(c.split())
            bic = bic + 1
    return biclusters


def Items_in_Biclusters(biclusters, roc='row'):
    if roc == "row":
        parameter = 0
    else:
        parameter = 1

    elements = set()

    for i in biclusters:
        bic_elements = biclusters[i][parameter]
        elements.update(bic_elements)

    return elements

#########################################################

if __name__ == "__main__":
    print("CC_Utils")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another

    CC = 0
    biclusters = []

    cc_files = [temp_path + 'M_u_i_cc.'+outputfile+'.txt', temp_path + 'M_u_f_cc.'+outputfile+'.txt']
    for i in range(len(cc_files)):
        bic = read_CC_File(cc_files[i])
        biclusters.append(bic)
        CC = CC + len(bic)

    print("|CC_{ui}|= %d" % len(biclusters[0]))
    print("|CC_{uf}|= %d" % len(biclusters[1]))
    print('|CC| = %d ' % CC)

    R_in_CC = defaultdict(dict)
    C_in_CC = defaultdict(dict)
    sim_u_v_in_CC = defaultdict(dict)
    sim_C_in_CC = defaultdict(dict)
    unique_rows = set()
    unique_columns = set()
    u_v_in_CC = []
    i_j_in_CC = []

    '''
        obtain the number of rows and columns
    '''
    # Obtain the unique elements in the biclusters
    for i in range(len(biclusters)):
        unique_rows = unique_rows.union(set(Items_in_Biclusters(biclusters[i], "row")))
        unique_columns = unique_columns.union(set(Items_in_Biclusters(biclusters[i], "col")))

    print(len(unique_rows))
    print()
    all_user_ids = range(1, len(unique_rows) + 1)

    '''
        Create a nxn Array with all zeros, and the diagonal with NaN
    '''
    u_v_in_CC = np.zeros(shape=(len(unique_rows), len(unique_rows)))
    np.fill_diagonal(u_v_in_CC, np.nan)
    print(u_v_in_CC.shape)

    count = 1
    for c in range(len(biclusters)):
        for r in biclusters[c]:
            list = map(int, biclusters[c][r][0])
            list = set(list)
            pairs = combinations(list, 2)

            for p in pairs:
                a, b = p
                a = a - 1
                b = b -1
                value_in_cell = u_v_in_CC[a][b]
                u_v_in_CC[a][b] = value_in_cell + 1
                u_v_in_CC[b][a] = value_in_cell + 1
            #print()
            count = count + 1

    print('Finding |CC_uv|/|CC|')
    sim_u_v_in_CC = np.divide(u_v_in_CC,CC)

    print('Convert to DF')
    u_v_in_CC_df = pd.DataFrame(u_v_in_CC, index=all_user_ids, columns=all_user_ids)
    sim_u_v_in_CC_df = pd.DataFrame(sim_u_v_in_CC, index=all_user_ids, columns=all_user_ids)
    u_v_in_CC_dict = {col: u_v_in_CC_df[col].dropna().to_dict() for col in u_v_in_CC_df}
    sim_u_v_in_CC_df_dict = {col: sim_u_v_in_CC_df[col].dropna().to_dict() for col in sim_u_v_in_CC_df}

    data = [biclusters, CC, unique_rows, unique_columns, u_v_in_CC_dict, sim_u_v_in_CC_df_dict]
    dh.save_data(data, temp_path + 'CC_Utils_data.'+outputfile+'.obj')
