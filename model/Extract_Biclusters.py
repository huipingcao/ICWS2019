'''
    Module for Bicluster extraction
    It uses the Find_Biclusters module to create the model
'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

from builtins import print
from model import Arguments
from model import Find_Biclusters as bic
from parameters import common_parameters as p
import sys
import _pickle as pickle

outputfile = ""
filename = ""
seed = p.seed
users = p.cc_rows
items = p.cc_columns
features = p.ys
x= p.xs
y = p.ys
data_path = p.DATA_PATH
temp_path = p.TEMP_PATH

def extract_biclusters():
    biclusters_dfs = []

    matrix_filename = data_path + "M_u_i_dataset." + outputfile +".txt"
    M_u_i = bic.read_file_to_df(matrix_filename)

    with open(temp_path + 'M_u_i.'+ outputfile + '.obj', 'wb') as matrix_data:
        pickle.dump(M_u_i, matrix_data)
    r, c = M_u_i.shape
    print('Users=',r,"Items=",c)

    biclusters = bic.create_model(M_u_i, [x, y], 'log', rnd)
    bic.save_bicluster_info_to_file('SpectralBicluster', temp_path + 'M_u_i_cc.'+ outputfile +'.txt', biclusters)

    matrices = bic.get_bicluster_matrices(biclusters, M_u_i)
    biclusters_dfs.append(matrices)

    matrix_filename = data_path+ "M_u_f_dataset." + outputfile + ".txt"
    M_u_f = bic.read_file_to_df(matrix_filename)

    with open(temp_path + 'M_u_f.'+ outputfile +'.obj', 'wb') as matrix_data:
        pickle.dump(M_u_f, matrix_data)

    r, c = M_u_f.shape
    print('Users=', r, "Features=", c)

    biclusters = bic.create_model(M_u_f, [x, y], 'log', rnd)
    bic.save_bicluster_info_to_file('SpectralBicluster', temp_path + 'M_u_f_cc.' + outputfile+ '.txt', biclusters)

    matrices = bic.get_bicluster_matrices(biclusters,M_u_f)
    biclusters_dfs.append(matrices)

    with open(temp_path + 'biclusters_dataframes.'+ outputfile +'.obj', 'wb') as matrix_data:
        pickle.dump(biclusters_dfs, matrix_data)


##################################################################################
if __name__ == "__main__":
    print("Extract Biclusters")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another
    if seed == 0:   #off default
        rnd = 128
    else:           #on
        rnd = 44

    extract_biclusters()
