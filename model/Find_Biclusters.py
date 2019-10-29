'''
    Module to create the SpectralBiclusters algorithm
'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))


import pandas as pd
from collections import defaultdict
from sklearn.cluster.bicluster import SpectralBiclustering
from  model.DataHelper import save_df_to_file, read_file_to_df
from parameters import common_parameters as p

temp_path = p.TEMP_PATH
data_path = p.DATA_PATH

def create_model(data, n_clusters, method, random):
    model = SpectralBiclustering(n_clusters=n_clusters, method=method, random_state=random)
    model.fit(data)

    return model

def get_total_biclusters(model):
    return len(model.biclusters_[0])

def get_rows_and_columns(model):
    biclusters_indices = defaultdict(list)
    for i in range(get_total_biclusters(model)):
        row_indices, column_indices = model.get_indices(i)
        row_indices = [i+1 for i in row_indices]
        column_indices = [j + 1 for j in column_indices]
        biclusters_indices[i].append(list(row_indices))
        biclusters_indices[i].append(list(column_indices))

    return biclusters_indices

def show_biclusters_shape(model):
    for i in range(get_total_biclusters(model)):
        print('Bicluster', i + 1, model.get_shape(i))


def get_bicluster_matrices(model,data):
    r_c_indices = get_rows_and_columns(model)
    biclusters = get_total_biclusters(model)
    biclusters_data = []

    for i in range(biclusters):
        index = r_c_indices[i][0]
        columns = r_c_indices[i][1]

        bc_matrix = model.get_submatrix(i,data)
        bc_matrix_df = pd.DataFrame(bc_matrix, index=index, columns=columns)
        biclusters_data.append(bc_matrix_df)

    return biclusters_data

def save_bicluster_info_to_file(type, filename, model):
    print('Saving info to %s' % filename)

    file = open(filename, 'w')

    file.write(type + '\n')

    biclusters = get_total_biclusters(model)
    r_c_indices = get_rows_and_columns(model)

    for i in range(biclusters):
        model.get_shape(i)
        index = r_c_indices[i][0]
        columns = r_c_indices[i][1]
        file.write(' '.join([str(x) for x in model.get_shape(i)]) + '\n')
        file.write(' '.join(['R'+str(x) for x in index]) + '\n')
        file.write(' '.join(['C'+str(x) for x in columns]) + '\n')

    file.close()

###############################################################
if __name__ == "__main__":
    print("Find_Biclusters")

    matrix_filename = data_path + "M_u_i_dataset.txt"
    M_u_i = read_file_to_df(matrix_filename)
    r,c = M_u_i.shape
    biclusters = create_model(M_u_i, [int(r*.10),int(c*.10)], 'bistochastic', 128)
    total_biclusters = get_total_biclusters(biclusters)

    show_biclusters_shape(biclusters)

    save_bicluster_info_to_file('SpectralBicluster',temp_path+'M_u_i_cc.txt', biclusters)

    matrix_filename = "M_u_f_dataset.txt"
    M_u_f = read_file_to_df(matrix_filename)
    print(M_u_f.shape)
    r, c = M_u_f.shape

    biclusters = create_model(M_u_f, [int(r * .10), 2], 'bistochastic', 128)
    total_biclusters = get_total_biclusters(biclusters)
    show_biclusters_shape(biclusters)
    save_bicluster_info_to_file('SpectralBicluster', temp_path+'M_u_f_cc.txt', biclusters)
