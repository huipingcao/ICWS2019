'''
    m-envy metric

'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))
from builtins import print
from statistics import mean
import time
import pandas as pd
from collections import defaultdict
from model import DataHelper as dh
from parameters import common_parameters as p
from model import Arguments
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

kitems = p.top_k_items
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
packages_path = p.PACKAGES_PATH
LOGS_PATH = p.LOGS_PATH
num_packages = p.num_packages
at_least_m = p.at_least_m

def create_metric_output_file(G, data, metric):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    header = 'm1,m2,fairness,average,GRmodel\n'
    total_users = len(G)
    filename =  timestr + '_' + metric + '_' + str(total_users) +  '.log'
    print(LOGS_PATH + filename)
    with open(LOGS_PATH + filename, 'w') as f:
        f.write(header)

        group_metric_c0 = data[0]
        group_metric_c1 = data[1]
        group_metric_c2 = data[2]
        mean = data[3]
        GRmodel = data[4]

        row = str(group_metric_c0) + ',' + \
              str(group_metric_c1) + ',' + \
              str(group_metric_c2) + ',' + \
              str(mean) + ',' + \
              str(GRmodel) + ',' + \
              '\n'
        f.write(row)


def extract_percentage(col):
    val_list = col.tolist()
    val_list_sorted = sorted(val_list, reverse=True)
    top_items = int(round(len(val_list) * percentage))
    if top_items < 1:
        top_items = 1

    top_items = val_list_sorted[:top_items]
    top_items_list.append(top_items)


def find_envy(row):
    cats = row.tolist()
    number_of_true = 0
    for i in range(len(cats)):
        if cats[i] in top_items_list[i]:
            number_of_true = number_of_true + 1

    if number_of_true >= m_items:
        return True
    else:
        return False


def fairness_m_envy():
    df.columns = ['a', 'b', 'm_envy']
    g_p = df['m_envy'].sum()
    g_size = df.shape[0]

    return g_p / float(g_size)


###############################################################
if __name__ == "__main__":
    print("Fairness m_prop")
    percentage = p.percentage

#############################################

    '''
        Load top-10 packages for Method2
    '''
    method1_packages = dh.load_Data(packages_path+'Model1_top_Packages.obj')

    '''
        Load top-10 packages for Method2
    '''
    method2_packages = dh.load_Data(packages_path+'Model2_top_Packages.obj')

    '''
        Load top-10 packages for Fairness
    '''
    fairness_packages = dh.load_Data(packages_path+'Fairness_top_Packages.obj')

    '''
        Load top-10 packages for Avergage
    '''
    average_packages = dh.load_Data(packages_path+'Average_top_Packages.obj')

    '''
        Load top-10 packages for GRmodel
    '''
    GRmodel_packages = dh.load_Data(packages_path+'GRmodel_top_Packages.obj')


    filename = temp_path+'Extract_User_Preferences.obj'
    data = dh.load_Data(filename)
    ratings_c1 = data[0]
    ratings_c2 = data[1]

    '''
        Extract users
    '''
    G = list(ratings_c1.index)
    print('Users', G)
    g_size = len(G)

    packages = [method1_packages, method2_packages, fairness_packages, average_packages, GRmodel_packages]
    print('Packages')
    print(packages)

    dict_for_df = defaultdict(list)
    dict_for_df['id'].append(G)
    print(dict_for_df)
    data_packages_m_envy = []

    for package in packages:
        data_m_envy = []
        print('#' * 50)
        for element in package:
            c1_item = [element[0]]
            c2_item = [element[1]]
            c1_ratings = ratings_c1.loc[G, c1_item]
            c2_ratings = ratings_c2.loc[G, c2_item]
            df = pd.concat([c1_ratings, c2_ratings], axis=1)
            m_items = int(df.shape[1] / 2)
            top_items_list = []
            df.apply(extract_percentage, axis=0)
            df['m_envy'] = df.apply(find_envy, axis=1)
            package_m_envy = fairness_m_envy()
            data_m_envy.append(package_m_envy)

        mean_m_envy = mean(data_m_envy[:num_packages])

        data_packages_m_envy.append(mean_m_envy)

    print('^' * 40)
    print(data_packages_m_envy)

    create_metric_output_file(G, data_packages_m_envy, 'M_ENVY_PREFERENCES')
