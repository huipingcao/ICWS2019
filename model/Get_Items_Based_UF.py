'''
    Module to get the closest items based on the features
'''

import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

from model import DataHelper as dh
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import sys
from model import Arguments
from parameters import common_parameters as p
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

outputfile = ""
kitems = p.k_vals
data_path = p.DATA_PATH
temp_path = p.TEMP_PATH

def load_Matrix(matrix_filename):
    M_u_i = dh.read_file_to_df(matrix_filename)
    print(M_u_i.shape)

    return M_u_i


'''
 Generate df based on the co-cluster rows and cols
'''
def find_df_cc():
    df_cc_values = []
    for e in CC_u_f:
        cc = CC_u_f[e]
        M_rows = cc[0]
        M_cols = cc[1]
        M_rows = [int(r)-1 for r in M_rows]
        M_cols = [int(c) - 1 for c in M_cols]

        df_cc = pd.DataFrame(index=M_rows, columns=M_cols)
        for r in M_rows:
            for c in M_cols:
                value = M_u_f.loc[r, c]
                df_cc.at[r,c] = value
        df_cc_values.append(df_cc)
    return df_cc_values


def find_col_means():
    uf_col_means = []
    uf_col_names = []
    for df in df_cc_values:
        means = []
        cols = list(df)
        for c in cols:
            means.append(df.loc[:,c].mean())
        uf_col_means.append(means)
        uf_col_names.append(cols)

    return (uf_col_means, uf_col_names)

def train_knn(X, n=10):
    knn = NearestNeighbors(n_neighbors=n, algorithm='kd_tree')
    knn.fit(X)

    return knn

def find_neighbors(y, knn):
    _v, idx = knn.kneighbors(y, return_distance=True)

    return idx[0]


def cc_knn(n=20):
    neighbors = []

    for i, c_name in enumerate(uf_col_names):
        X = M_i_f.loc[:,c_name]
        knn = train_knn(X, n)
        y = [uf_col_means[i]]
        idx_items = find_neighbors(y, knn)
        neighbors.append(sorted(idx_items))

    return neighbors


#########################################################

if __name__ == "__main__":
    print("Get Items Based UF")

    Arguments.create_parser(sys.argv,globals())

    obj_filename = temp_path + 'CC_Utils_data.'+outputfile+'.obj'
    data= dh.load_Data(obj_filename)
    biclusters = data[0]
    CC_u_f = biclusters[1]

    obj_filename = temp_path + 'M_u_f.'+outputfile+'.obj'
    M_u_f = dh.load_Data(obj_filename)
    print(M_u_f.shape)

    df_cc_values = find_df_cc()
    uf_col_means, uf_col_names = find_col_means()
    print(uf_col_names)
    print(uf_col_means)

    # Load M_i_f
    matrix_filename = data_path + "M_i_f_dataset."+outputfile+".txt"
    M_i_f = load_Matrix(matrix_filename)
    dh.save_data(data, temp_path + 'M_i_f.'+outputfile+'.obj')
    print(M_i_f.shape)

    closest_items = cc_knn(int(kitems))

    #Export data from this module
    data = [df_cc_values, uf_col_names, uf_col_means, closest_items]
    dh.save_data(data, temp_path + 'Find_UF_Items.'+outputfile+'.obj')
