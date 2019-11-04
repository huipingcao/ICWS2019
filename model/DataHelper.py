'''
    Various Utitity functions for all modules
'''
import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))

import pandas as pd
import pickle
import os
import sys

def manage_folders(folders):
    for folder in folders:
        try:
            folder_path = "../"+folder
            if os.path.isdir(folder_path):
                files = os.listdir(folder_path)
                for f in files:
                    os.remove(folder_path+"/"+f)
            else:
                # Create the directory
                os.mkdir("../"+folder)
                print("Directory", "../"+folder, "created!")

        except:
            print("Something went wrong!")
            sys.exit(1)


def save_df_to_file(df, filename):
    print("Saving data to file", filename)

    try:
        df.to_csv(filename, index=False, header=False,)
        print("Data was saved!")
    except:
        print("Ups! something went wrong saving the data")


def read_file_to_df(filename):
    print("Reading %s" % filename)

    try:
        df = pd.read_csv(filename, header=None, na_filter=True)
        print("Data from %s is loaded!" % filename)
        return df
    except:
        print("Ups! something went wrong loading the data")


def save_data(data, filename):
    print('Saving data', filename)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_Data(filename):
    with open(filename, 'rb') as _data:
        data = pickle.load(_data)

    return data

def save_top_packages_list(filename, top_packages):
    with open(filename, "w") as f:
        for p in top_packages:
            f.write(str(p)+'\n')

def print_agg_method(aggregation):
    if aggregation == 0:
        print('Aggregation Method = MEAN')
    elif aggregation == 1:
        print('Aggregation Method = MAX')
    elif aggregation == 2:
        print('Aggregation Method = MIN')
    elif aggregation == 3:
        print('Aggregation Method = GEOMETRIC MEAN')
    elif aggregation == 4:
        print('Aggregation Method = SUM')
    elif aggregation == 5:
        print('Aggregation Method = MAE')

if __name__ == "__main__":
    pass