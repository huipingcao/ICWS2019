import sys
import os.path as o
sys.path.append(o.abspath(o.join(o.dirname(sys.modules[__name__].__file__), "..")))
from model import DataHelper as dh
from model import Arguments
from parameters import common_parameters as p

outputfile = ""
kitems = p.top_k_items
temp_path = p.TEMP_PATH
data_path = p.DATA_PATH
packages_path = p.PACKAGES_PATH
num_packages = p.num_packages

def select_top_packages():
    pairs = []

    pairs.append((top_ranked_c1[0], top_ranked_c2[0]))
    print(top_ranked_c1[0], top_ranked_c2[0])

    i = 1
    try:
        while len(pairs) < num_packages:
            print(top_ranked_c1[i], top_ranked_c2[i - 1])
            print(top_ranked_c1[i - 1],top_ranked_c2[i])
            print(top_ranked_c1[i], top_ranked_c2[i])

            pairs.append((top_ranked_c1[i], top_ranked_c2[i - 1]))
            pairs.append((top_ranked_c1[i - 1], top_ranked_c2[i]))
            pairs.append((top_ranked_c1[i], top_ranked_c2[i]))

            i = i + 1
    except:
        pass

    # print pairs
    return pairs[:int(num_packages)]


###############################################################
if __name__ == "__main__":
    print("Average")

    Arguments.create_parser(sys.argv,globals())   #globals(): pass the global vars from one module to another


    '''
        Load the dense matrix
    '''
    filename = temp_path+'Build_Dense_Matrix.' + str(1) + '.obj'
    data = dh.load_Data(filename)
    ratings_G = data[0]

    items_avg = ratings_G.mean()

    items_avg_soted = items_avg.sort_values(ascending=False)

    top_k_items = items_avg_soted[0:int(kitems)]
    print(top_k_items)

    index_1 = list(top_k_items.index)
    top_ranked_c1 = [i[0] for i in index_1]
    top_ranked_c1 = sorted(set(top_ranked_c1), key=top_ranked_c1.index)
    print('Items=', top_ranked_c1)


    '''
        Load the dense matrix
    '''
    filename = temp_path+'Build_Dense_Matrix.' + str(2) + '.obj'
    data = dh.load_Data(filename)
    ratings_G = data[0]

    items_avg = ratings_G.mean()

    items_avg_soted = items_avg.sort_values(ascending=False)

    top_k_items = items_avg_soted[0:int(kitems)]
    print(top_k_items)

    index_2 = list(top_k_items.index)
    top_ranked_c2 = [i[0] for i in index_2]
    top_ranked_c2 = sorted(set(top_ranked_c2), key=top_ranked_c2.index)
    print('Items=', top_ranked_c2)

    '''
            Create the packages
        '''
    top_packages = select_top_packages()
    top_packages = list( top_packages )
    print( "Top {} Packages:".format( num_packages ) )
    print( top_packages )

    '''
		Export the list of the Top-k packages
	'''
    # Export data from this module
    dh.save_top_packages_list( packages_path + "Average_top_packages.txt", top_packages )

