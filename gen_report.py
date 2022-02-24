import os
import yaml
import json
import sys
import argparse

#command line interfaces argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scan", action="store", type=str, default='all',help="specify a scan to work on")

args = parser.parse_args()

if not os.path.isdir(args.scan):
    print("Given scan does not exist. Exiting.")
    sys.exit()

results = os.listdir(args.scan)

print(results)
