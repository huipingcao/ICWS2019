import subprocess
import itertools
import random
import argparse
from builtins import print

import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

from parameters import common_parameters as p
from model import DataHelper as dh


MAX_G = p.MAX_G
LOGS_PATH = p.LOGS_PATH
alphas = p.alphas
xs = p.xs
ys = p.ys
categories = p.categories
k_vals = p.k_vals
u_vals = p.u_vals
top_k_items = p.top_k_items
pt = p.pt
g = p.g
cluster = p.cluster
agg = p.agg_function

def pause():
    programPause = input("Press the <ENTER> key to continue...")


def select_random_groups(k=3):
    random.seed(42 + k)
    all_groups = []
    for i in range(k):
        all_users = list(range(1,250))
        random.shuffle(all_users)
        G = all_users[:MAX_G]
        all_groups.append(G)

    return all_groups


if __name__ == '__main__':

    dh.manage_folders(p.folders)

    parser = argparse.ArgumentParser(description='Package Recommednations.')
    args = parser.parse_args()
    total_groups = p.total_groups
    base = p.base

    all_groups = select_random_groups(total_groups)
    print(len(all_groups))
    print(all_groups)

    for i, G in enumerate(all_groups):
        print('Group', i+1, G)

        biclusters = itertools.product(xs, ys)
        for b in biclusters:
            x = b[0]
            y = b[1]
            for alpha in alphas:
                for k in k_vals:
                    for u in u_vals:
                        G_members = G[:u]
                        G_seq = ','.join(map(str, G_members))
                        print("G_seq",G_seq)

                        for t in top_k_items:
                            for c in categories:
                                print('Category=',c)

                                '''
                                    Scripts
                                '''
                                s1 = base + 'Extract_Biclusters.py -o '+ str(c) + ' -x '+ str(x) + ' -y '+ str(y)
                                s2 = base + 'CC_Utils.py -o ' + str(c)
                                s3 = base + 'Get_Items_Based_UF.py -o ' + str(c) + ' -kitems ' + str(k)
                                s4 = base + 'Get_SIM_i_f.py -o ' + str(c)
                                s5 = base + 'Find_UI_items.py -o ' + str(c)
                                s6 = base + 'Get_CC_U-I_Belong.py -o ' + str(c)
                                s7 = base + 'I-I-CF.py -o '+ str(c) + ' -G ' + G_seq
                                s8 = base + 'U-U-CF.py -o '+ str(c) + ' -G ' + G_seq
                                s9 = base + 'Predict_Ratings.py -o ' + str(c) + ' -alpha ' + str(alpha)
                                s10 = base + 'Build_Dense_Matrix.py -o ' + str(c) + ' -kitems ' + str(t) + ' -G ' + G_seq

                                '''
                                    Calling scripts
                                '''
                                result_s1 = subprocess.check_output(s1, shell=True)
                                print(result_s1)
                                result_s2 = subprocess.check_output(s2, shell=True)
                                print(result_s2)
                                result_s3 = subprocess.check_output(s3, shell=True)
                                print(result_s3)
                                result_s4 = subprocess.check_output(s4, shell=True)
                                print(result_s4)
                                result_s5 = subprocess.check_output(s5, shell=True)
                                print(result_s5)
                                result_s6 = subprocess.check_output(s6, shell=True)
                                print(result_s6)
                                result_s7 = subprocess.check_output(s7, shell=True)
                                print(result_s7)
                                result_s8 = subprocess.check_output(s8, shell=True)
                                print(result_s8)
                                result_s9 = subprocess.check_output(s9, shell=True)
                                print(result_s9)
                                result_s10 = subprocess.check_output(s10, shell=True)
                                print(result_s10)

                                print( '\n' * 3 )

                            '''
                                POC
                            '''
                            s11 = base + 'Get_POC.py -o all -G ' + G_seq
                            result_s11 = subprocess.check_output(s11, shell=True)
                            print(result_s11)

                            '''
                                Extract user preferences
                            '''
                            s12 = base + 'Extract_User_Preferences.py -o all -agg ' + str(agg) + ' --pt ' + str(pt)
                            result_s12 = subprocess.check_output( s12, shell=True )
                            print( result_s12 )
                            '''
                                Run models
                            '''
                            s13 = base + 'Model1.py -o all -agg ' + str(agg) + ' --pt ' + str(pt)
                            result_s13 = subprocess.check_output(s13, shell=True)
                            print(result_s13)

                            s14 = base + 'Model2.py -o all -agg ' + str(agg) + ' --pt ' + str(pt)
                            result_s14 = subprocess.check_output(s14, shell=True)
                            print(result_s14)

                            '''
                                Run Baselines
                            '''
                            s15 = base + 'Fairness_baseline.py -o all --kitems ' + str(t)
                            result_s15 = subprocess.check_output(s15, shell=True)
                            print(result_s15)

                            s16 = base + 'Average_baseline.py -o all --kitems ' + str( t )
                            result_s16 = subprocess.check_output( s16, shell=True )
                            print( result_s16 )

                            s17 = base + 'GRmodel_baseline.py -o all --kitems ' + str( t )
                            result_s17 = subprocess.check_output( s17, shell=True )
                            print( result_s17 )


                #print("\033[H\033[J")

    print(' ' * 200)
    dh.manage_folders( ['temp'] )
    print("Packages in folder {}".format(p.PACKAGES_PATH))
    print('DONE!')