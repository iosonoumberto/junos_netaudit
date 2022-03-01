import os
import yaml
import json
import sys
import argparse

import gen_report_lib

#command line interfaces argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scan", action="store", type=str, default='all',help="specify a scan to work on")

args = parser.parse_args()

#load configuration files
try:
    fs=open('configuration/checks.yml','r')
    checks = yaml.load(fs, Loader=yaml.FullLoader)
    fs.close()
except:
    print("ERROR: cannot open checks file. Exiting.")
    sys.exit()
    
for check in checks:
    text = eval('gen_report_lib.'+check['test']+'(args.scan, check)')
    print(text)
