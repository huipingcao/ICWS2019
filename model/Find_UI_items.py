import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

from model import DataHelper as dh
import sys
from model import Arguments
from parameters import common_parameters as p
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

outputfile = ""
data_path = p.DATA_PATH
temp_path = p.TEMP_PATH

'''
 Generate df based on the co-cluster rows and cols
'''
def find_df_cc():
    df_cc_values = []
    for e in CC_u_i:
        cc = CC_u_i[e]
        M_rows = cc[0]
        M_rows = [int(i)-1 for i in M_rows]
        M_cols = cc[1]
        M_cols = [int(i)-1 for i in M_cols]
        df_cc = M_u_i.ix[M_rows, M_cols]
        df_cc_values.append(df_cc)

    return df_cc_values


#########################################################

if __name__ == "__main__":
    print("Find UI Items")

    Arguments.create_parser(sys.argv,globals())

    '''
    Load M_u_i
    '''
    filename = temp_path + 'M_u_i.'+outputfile+'.obj'
    M_u_i = dh.load_Data(filename)
    r,c = M_u_i.shape
    print('M_u_i | Users=', r, 'Items=',c)

    filename = temp_path + 'CC_Utils_data.'+outputfile+'.obj'
    CC_Utils_data = dh.load_Data(filename)

    CC_u_i = CC_Utils_data[0][0]
    print('CC_u_i = ', len(CC_u_i))
    df_CC_u_i = find_df_cc()

    data = [df_CC_u_i]
    dh.save_data(data, temp_path + 'Find_UI_items.'+outputfile+'.obj')
