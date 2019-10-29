'''
    Module to find to which Co-cluster a user/item belongs

'''

import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

from collections import defaultdict
import sys
from model import Arguments
from parameters import common_parameters as p
from model import DataHelper as dh
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

outputfile = ""
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH


def find_where_users_belongs(cc, dictionary):
    for i, cc in enumerate(cc):
        elements = cc.index
        for e in elements:
            dictionary[e+1].append(i)

def find_where_items_belongs(cc, dictionary):
    for i, cc in enumerate(cc):
        elements = cc.columns
        for e in elements:
            dictionary[e+1].append(i)


###############################################################

if __name__ == "__main__":
    print("Get_CC_U-I_Belong")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another

    '''
    Load data
    '''
    filename = temp_path + 'Find_SIM_i_f.'+outputfile+'.obj'
    SIM_i_f_data = dh.load_Data(filename)

    filename = temp_path + 'Find_UI_items.'+outputfile+'.obj'
    UI_items_data = dh.load_Data(filename)

    CC_u_i_biclusters = UI_items_data[0]
    print('DFs in CC_u_i = ',len(CC_u_i_biclusters))

    SIM_i_f_biclusters = SIM_i_f_data[0]
    print('DFs in SIM_u_i =',len(SIM_i_f_biclusters))

    users_in_CC_u_i = defaultdict(list)
    users_in_SIM_i_f = defaultdict(list)
    items_in_CC_u_i = defaultdict(list)
    items_in_SIM_i_f = defaultdict(list)

    find_where_users_belongs(CC_u_i_biclusters, users_in_CC_u_i)
    find_where_users_belongs(SIM_i_f_biclusters, users_in_SIM_i_f)
    find_where_items_belongs(CC_u_i_biclusters, items_in_CC_u_i)
    find_where_items_belongs(SIM_i_f_biclusters, items_in_SIM_i_f)

    # Export data from this module
    data = [users_in_CC_u_i, users_in_SIM_i_f, items_in_CC_u_i, items_in_SIM_i_f]
    dh.save_data(data, temp_path + 'Find_U-I_belong_DF.'+outputfile+'.obj')
