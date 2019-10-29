'''
    Get items that satisfy user's features prefernes, and co-cluster-based similarities
'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

from collections import defaultdict
import sys
from model import Arguments
from itertools import combinations,permutations
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from parameters import common_parameters as p
from model import DataHelper as dh

outputfile = ""
data_path = p.DATA_PATH
temp_path = p.TEMP_PATH

def create_bic_with_items():
    new_SIM_i_f = []
    SIM_i_f_users = []
    SIM_i_f_items = []
    for x, cc in enumerate(u_f_cc_users):
        indices = cc.index
        new_columns = cc_items_satisfy[x]
        df = M_u_i.ix[indices, new_columns]
        new_SIM_i_f.append(df)
        SIM_i_f_users.append(indices)
        SIM_i_f_items.append(new_columns)

    return (new_SIM_i_f, SIM_i_f_users, SIM_i_f_items)


def _in_Sim_i_f_columns_2(items, pairs):
    for p in pairs:
        a,b = p
        if a in items and b in items:
            a = a+1
            b = b+1
            if a in C_in_CC.keys():
                if b in C_in_CC[a].keys():
                    value = C_in_CC[a][b]
                    C_in_CC[a][b] = value + 1
                else:
                    C_in_CC[a][b] = 1
            else:
                C_in_CC[a][b] = 1

            if b in C_in_CC.keys():
                if a in C_in_CC[b].keys():
                    value = C_in_CC[b][a]
                    C_in_CC[b][a] = value + 1
                else:
                    C_in_CC[b][a] = 1
            else:
                C_in_CC[b][a] = 1
        else:
            a = a + 1
            b = b + 1
            if a not in C_in_CC.keys():
                C_in_CC[a][b] = 0
            else:
                if b not in C_in_CC[a].keys():
                    C_in_CC[a][b] = 0

            if b not in C_in_CC.keys():
                C_in_CC[b][a] = 0
            else:
                if a not in C_in_CC[b].keys():
                    C_in_CC[b][a] = 0


def _in_Sim_u_i_columns_2(items, pairs):
    for p in pairs:
        a,b = p
        if a in items and b in items:
            if a in C_in_CC.keys():
                if b in C_in_CC[a].keys():
                    value = C_in_CC[a][b]
                    C_in_CC[a][b] = value + 1
                else:
                    C_in_CC[a][b] = 1
            else:
                C_in_CC[a][b] = 1

            if b in C_in_CC.keys():
                if a in C_in_CC[b].keys():
                    value = C_in_CC[b][a]
                    C_in_CC[b][a] = value + 1
                else:
                    C_in_CC[b][a] = 1
            else:
                C_in_CC[b][a] = 1
        else:
            if a not in C_in_CC.keys():
                C_in_CC[a][b] = 0
            else:
                if b not in C_in_CC[a].keys():
                    C_in_CC[a][b] = 0

            if b not in C_in_CC.keys():
                C_in_CC[b][a] = 0
            else:
                if a not in C_in_CC[b].keys():
                    C_in_CC[b][a] = 0


def similarity_cc_2(list, pairs):
    for p in pairs:
        a,b = p
        s = C_in_CC[a][b] / CC
        sim_i_j_in_CC[a][b] = s
        sim_i_j_in_CC[b][a] = s



###############################################################

if __name__ == "__main__":
    print("Get_SIM_i_f")

    Arguments.create_parser(sys.argv,globals())

    R_in_CC = defaultdict(dict)
    C_in_CC = defaultdict(dict)
    sim_i_j_in_CC = defaultdict(dict)
    sim_C_in_CC = defaultdict(dict)
    i_j_in_CC = []

    #load information from UF_Items
    obj_filename = temp_path+'Find_UF_Items.'+outputfile+'.obj'
    data = dh.load_Data(obj_filename)
    u_f_cc_users = data[0]

    print('UF co-clusters =',len(u_f_cc_users))

    cc_items_satisfy = data[3]
    print('Satisfying items co-clusters =',len(cc_items_satisfy))

    obj_filename = temp_path + 'M_u_i.' + outputfile + '.obj'
    M_u_i = dh.load_Data(obj_filename)
    rows, cols = M_u_i.shape
    print('M_u_i | Users=', rows, 'Items=', cols)

    unique_items_satisfy_sim_i_f = set([x for cc in cc_items_satisfy for x in cc ])
    unique_items_from_u_i = list(range(cols))

    print('Finding |CC_ij| for SIM_if')
    for list in cc_items_satisfy:
        pairs = combinations(unique_items_from_u_i, 2)
        _in_Sim_i_f_columns_2(set(list),pairs)

    SIM_i_f_cc, SIM_i_f_cc_users, SIM_i_f_cc_items = create_bic_with_items()
    print('Derived U-F cc = ',len(SIM_i_f_cc))

    obj_filename = temp_path + 'CC_Utils_data.'+outputfile+'.obj'
    cc_data = dh.load_Data(obj_filename)
    biclusters = cc_data[0]
    bic_u_i = biclusters[0]
    CC = cc_data[1]

    print('CC_u_i biclusters = ',len(bic_u_i))
    print('Total biclusters = ', CC)

    unique_items_from_u_i = set([x+1 for x in unique_items_from_u_i])

    for i in bic_u_i:
        list = [int(x) for x in bic_u_i[i][1]]
        list = set(list)
        pairs = combinations(unique_items_from_u_i, 2)
        _in_Sim_u_i_columns_2(set(list),pairs)

    C_in_CC_elements = set(C_in_CC.keys())

    print('Finding |CC_ij|/|CC|')
    pairs = combinations(C_in_CC_elements, 2)
    similarity_cc_2(C_in_CC_elements,pairs)

    data = [SIM_i_f_cc, unique_items_from_u_i, C_in_CC_elements, C_in_CC, sim_i_j_in_CC]
    dh.save_data(data, temp_path + 'Find_SIM_i_f.'+outputfile+'.obj')

