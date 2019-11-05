'''
    Calculate Consensus metric

'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))
from itertools import combinations
from statistics import mean
import time
from model import DataHelper as dh
from parameters import common_parameters as p
import math
from model import Arguments
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

outputfile = ""
kitems = p.top_k_items
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
packages_path = p.PACKAGES_PATH
LOGS_PATH = p.LOGS_PATH
num_packages = p.num_packages


def calculate_pdcg(G, base=2):
    pDCG = []

    for i in range(len(G)):
        res_pDCG = (2 ** G[i] - 1) / math.log((i + 1) + 1, base)
        pDCG.append(res_pDCG)

    return sum(pDCG)


def create_metric_output_file(G, data, metric):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    header = 'g_mean_c1,g_mean_c2,mean\n'
    total_users = len(G)
    filename =  timestr + '_' + metric + '_' + str(total_users) +  '.log'
    print(LOGS_PATH + filename)
    with open(LOGS_PATH + filename, 'w') as f:
        f.write(header)

        for method in data:
            group_metric_c1 = method[0]
            group_metric_c2 = method[1]
            mean = method[2]

            row = str(group_metric_c1) + ',' + \
                  str(group_metric_c2) + ',' + \
                  str(mean) + ',' + \
                  '\n'
            f.write(row)


def group_consensus(ratings):
    comb = combinations(ratings, 2)
    sumation = []
    for c in comb:
        sub = abs(c[0] - c[1])
        sumation.append(sub)

    numerator = sum(sumation)
    denominator = g_size * ((g_size - 1) / 2.)
    consensus = 1 - (numerator / denominator)
    all_consensus.append(consensus)

def average_consensus(all_consensus):
    return mean(all_consensus)


###############################################################
if __name__ == "__main__":
    print("Consensus metric")

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

    data_consensus = []
    for package in packages:
        print('#' * 50)
        print(package)
        all_consensus = []
        package_items_c1 = set()
        package_items_c2 = set()
        for item in package:
            package_items_c1.add(item[0])
            package_items_c2.add(item[1])

        print('Package Items C1',package_items_c1)
        print('Package Items C2', package_items_c2)

        ################ For Category 1 #####################
        ratings = ratings_c1.loc[G,list(package_items_c1)]
        print(ratings)
        ratings.apply(lambda col: group_consensus(col), axis=0)

        average_consensus_c1 = average_consensus(all_consensus)
        print()

        ################ For Category 2 #####################
        ratings = ratings_c2.loc[G, list(package_items_c2)]
        print(ratings)
        ratings.apply(lambda col: group_consensus(col), axis=0)

        average_consensus_c2 = average_consensus(all_consensus)
        avg_all_consensus = (average_consensus_c1 + average_consensus_c2) / 2
        data_consensus.append([average_consensus_c1, average_consensus_c2, avg_all_consensus])

    print()
    print('^' * 40)
    print(data_consensus)

    create_metric_output_file(G, data_consensus, 'CONSENSUS_PREFERENCES')