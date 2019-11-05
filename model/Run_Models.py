import subprocess
import itertools
import time
import random
import argparse
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

from builtins import print
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

    parser = argparse.ArgumentParser(description='This is a demo script.')
    args = parser.parse_args()
    total_groups = p.total_groups
    base = p.base

    all_groups = select_random_groups(total_groups)
    print(len(all_groups))
    print(all_groups)

    timestr = time.strftime("%Y%m%d-%H%M%S")
    separator_file = timestr + '_' + '-'*15 + '#'*5 + 'SEPARATOR ' + g.upper() + ' ' + str(total_groups) + ' GROUPS' + '#'*5 + '-'*15 + '.log'

    print(separator_file)
    path = LOGS_PATH
    file = open(path + separator_file, 'w')
    file.close()

    for i, G in enumerate(all_groups):
        print('Group', i+1, G)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        header = 'x,y,alpha,knn,top_k_items,users,category,pt,e_method1,e_method2,e_fairness,e_average,e_GRmodel\n'

        biclusters = itertools.product(xs, ys)
        for b in biclusters:
            x = b[0]
            y = b[1]
            for alpha in alphas:
                filename = timestr + '_' + g + str(x) + 'x' + str(y) + '_' + str(alpha) + '_Group_' + str(i+1) + '.log'
                print(LOGS_PATH + filename)
                with open(LOGS_PATH + filename, 'w') as f:
                    f.write(header)
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
                                    #print(result_s1)
                                    result_s2 = subprocess.check_output(s2, shell=True)
                                    #print(result_s2)
                                    result_s3 = subprocess.check_output(s3, shell=True)
                                    #print(result_s3)
                                    result_s4 = subprocess.check_output(s4, shell=True)
                                    #print(result_s4)
                                    result_s5 = subprocess.check_output(s5, shell=True)
                                    #print(result_s5)
                                    result_s6 = subprocess.check_output(s6, shell=True)
                                    #print(result_s6)
                                    result_s7 = subprocess.check_output(s7, shell=True)
                                    #print(result_s7)
                                    result_s8 = subprocess.check_output(s8, shell=True)
                                    #print(result_s8)
                                    result_s9 = subprocess.check_output(s9, shell=True)
                                    #print(result_s9)
                                    result_s10 = subprocess.check_output(s10, shell=True)
                                    #print(result_s10)

                                    print( '\n' * 3 )

                                '''
                                    POC
                                '''
                                s11 = base + 'Get_POC.py -o all -G ' + G_seq
                                result_s11 = subprocess.check_output(s11, shell=True)
                                #print(result_s11)

                                '''
                                    Extract the PREFERENCES to be used as Ratings
                                '''
                                s21 = base + 'Extract_User_Preferences.py -o all -agg ' + str( agg ) + ' --pt ' + str(pt)
                                result_s21 = subprocess.check_output( s21, shell=True )

                                '''
                                    Models
                                '''
                                s12 = base + 'Model1.py -o all -agg ' + str(agg) + ' --pt ' + str(pt)
                                result_s12 = subprocess.check_output(s12, shell=True)
                                print(result_s12)

                                s13 = base + 'Model2.py -o all -agg ' + str(agg) + ' --pt ' + str(pt)
                                result_s13 = subprocess.check_output(s13, shell=True)
                                print(result_s13)

                                '''
                                    Locating information of interest
                                '''
                                q = "Sum of errors="

                                if q in result_s12.decode():
                                    v = result_s12.decode().split(q)
                                    method1 = v[1].strip('\n')


                                if q in result_s13.decode():
                                    v = result_s13.decode().split(q)
                                    method2 = v[1].strip('\n')

                                '''
                                    Fairness strategy
                                '''
                                print('Fairness')
                                s15 = base + 'Fairness_baseline.py -o all --kitems ' + str(t)
                                result_s15 = subprocess.check_output(s15, shell=True)
                                print(result_s15)
                                '''
                                    Locating information of interest
                                '''
                                q = "Sum of errors="

                                if q in result_s15.decode():
                                    v = result_s15.decode().split(q)
                                    fairness = v[1].strip('\n')

                                '''
                                    Average strategy
                                '''
                                print('Average')
                                s16 = base + 'Average_baseline.py -o all --kitems ' + str(t)
                                result_s16 = subprocess.check_output(s16, shell=True)
                                print(result_s16)
                                '''
                                    Locating information of interest
                                '''
                                q = "Sum of errors="

                                if q in result_s16.decode():
                                    v = result_s16.decode().split(q)
                                    average = v[1].strip('\n')

                                '''
                                    GRmodel strategy
                                '''
                                print('GRmodel')
                                s22 = base + 'GRmodel_baseline.py -o all --kitems ' + str(t)
                                result_s22 = subprocess.check_output(s22, shell=True)
                                print(result_s22)
                                '''
                                    Locating information of interest
                                '''
                                q = "Sum of errors="

                                if q in result_s22.decode():
                                    v = result_s22.decode().split(q)
                                    GRmodel = v[1].strip('\n')

                                '''
                                    Printing row
                                '''
                                print( 'Metdhod1\tMethod2\tFaieness\tAverage\GRmodel' )
                                print(method1+'\t'+method2+'\t'+fairness+'\t'+average+'\t'+GRmodel)

                                '''
                                    Save the data
                                '''
                                print(header)
                                row = str(x) + ',' +\
                                      str(y) + ',' +\
                                      str(alpha) + ',' +\
                                      str(k) + ',' +\
                                      str(t) + ',' +\
                                      str(u) + ',' +\
                                      str(c) + ',' +\
                                      str(pt) + ',' +\
                                      method1 + ',' +\
                                      method2 + ',' +\
                                      fairness + ',' +\
                                      average + ',' +\
                                      GRmodel+\
                                      '\n'
                                f.write(row)

                            s18 = base + 'Consensus_metric.py'
                            result_s18 = subprocess.check_output(s18, shell=True)

                            s20 = base + 'm_envy_metric.py'
                            result_s20 = subprocess.check_output(s20, shell=True)

    print(' ' * 200)
    dh.manage_folders( [ 'temp' ] )
    print( "Packages in folder {}".format( p.PACKAGES_PATH ) )
    print( "Metric results in folder {}".format( p.LOGS_PATH ) )
    print('DONE!')