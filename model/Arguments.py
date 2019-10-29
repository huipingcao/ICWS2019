'''
    Parser functions
'''

import argparse
import sys
from builtins import print


def create_parser(arguments, glob):
    parser = argparse.ArgumentParser(description='This is a demo script.')
    parser.add_argument('-i', '--input', help='Input file name', required=False)
    parser.add_argument('-o', '--output', help='Output file name', required=True)
    parser.add_argument('-d', '--dataset', help='Dataset file name', required=False)
    parser.add_argument('-n', '--number', help='Threshold', required=False, type=int)

    parser.add_argument('-G', '--Group', help='Group list separated by ","', required=False, type=str)

    parser.add_argument('-users', '--users', help='Number of users', required=False, type=int)
    parser.add_argument('-items', '--items', help='Number of items', required=False, type=int)
    parser.add_argument('-features', '--features', help='Number of features', required=False, type=int)

    parser.add_argument('-alpha', '--alpha', help='Parameter alpha', required=False, type=float)

    parser.add_argument('-kitems', '--kitems', help='Percentage for top-k items', required=False, type=float)

    parser.add_argument('-agg', '--aggregation', help='Aggregation function (0=mean, 1=max, 2=min)', required=False, type=int)

    parser.add_argument('-pt', '--pt', help='POC Type (0=normal, 1=adjusted)', required=False, type=int)

    parser.add_argument('-t', '--test', help='Percentage of test users', required=False, type=int)

    parser.add_argument('--verbose', help='Show verbosity', required=False, action="store_true")
    parser.add_argument('--seed', help='Set seed for random', required=False,action="store_true")

    parser.add_argument('-c', '--categories', help='Number of Categories', required=False, type=int)

    parser.add_argument('-x', '--x', help='Number of Cocluster rows', required=False, type=int)
    parser.add_argument('-y', '--y', help='Number of Cocluster columns', required=False, type=int)

    args = parser.parse_args()

    ## show values ##
    if args.input:
        print("Input file: %s" % args.input)
        glob["inputfile"] = args.input

    if args.output:
        print("Append to output filename: %s" % args.output)
        glob["outputfile"] = args.output

    if args.dataset:
        print("Dataset filename: %s" % args.dataset)
        glob["filename"] = args.dataset

    if args.number:
        print("New threshold must be changed to {}".format(args.number))
        glob["threshold"] = args.number

    if args.Group:
        print("The group of users G is {}".format(args.Group))
        glob["G"] = [int(item) for item in args.Group.split(',')]

    if args.users:
        print("Users: {}".format(args.users))
        glob["users"] = args.users

    if args.items:
        print("Items: {}".format(args.items))
        glob["items"] = args.items

    if args.features:
        print("features: {}".format(args.features))
        glob["features"] = args.features

    if args.alpha:
        print("Alpha parameter: {}".format(args.alpha))
        glob["alpha"] = args.alpha

    if args.kitems:
        print("% of Top-k items: {}".format(args.kitems))
        glob["kitems"] = args.kitems

    if args.aggregation:
        if args.aggregation == 0:
            method = 'mean'
        elif args.aggregation == 1:
            method = 'max'
        elif args.aggregation == 2:
            method = 'min'
        elif args.aggregation == 3:
            method = 'geometric'
        elif args.aggregation == 4:
            method = 'sum'
        elif args.aggregation == 5:
            method = 'mae'
        else:
            print('Value not defined for the aggragation function')
            sys.exit(0)

        print("Aggregation method: {}".format(method))
        glob["aggregation"] = args.aggregation

    if args.pt:
        if args.pt == 0:
            print('POC Type = Adjusted [default]')

        elif args.pt == 1:
            print('POC Type = Normal')

        else:
            print('Value not defined for POC Type')
            exit(0)

        glob["pt"] = args.pt

    if args.test:
        print('% Test user = ' , args.test/100.)
        glob["test"] = args.test

    if args.verbose:
        print("Verbosity is On")

    if args.seed:
        print("Seed is On")
        glob["seed"] = 1


    if args.categories:
        print("Number of Categories {}".format(args.categories))
        glob["categories"] = args.categories

    if args.x:
        print("Number of Cocluster rows {}".format(args.x))
        glob["x"] = args.x

    if args.y:
        print("Number of Cocluster columns {}".format(args.y))
        glob["y"] = args.y