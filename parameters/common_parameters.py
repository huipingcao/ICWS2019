'''
	Different parameters used in the models
	The parameters presented in the paper are in this file.
'''

## Paths
LOGS_PATH = '../logs/'
TEMP_PATH = '../temp/'
DATA_PATH = '../datasets/'
PACKAGES_PATH = '../packages/'
folders = ['temp', 'packages']

## Groups' parameters
# Random seed
seed = 0
# Maximum number of members
MAX_G = 8
total_groups = 1
# Number of users picked for the group
u_vals = [4]
# Group is randomly picked
g = 'random'

## System base
base = "python "

## Parameters from the Paper
# alpha
alphas = [0.6]
# Co-clusrer Rows
xs = {10}
# Co-cluster Columns
ys = {4}
# KNN
k_vals = [20]
# Z items
top_k_items = [20]
categories = [1, 2]
# aPOC=0, POC=1
pt = 0
# Type of aggregation function
agg_function = 5
# Top packages
num_packages = 10

## Co-cluster parameters
cluster = 0
cc_rows = 50
cc_columns = 100






