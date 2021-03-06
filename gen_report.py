import os
import yaml
import json
import sys
import argparse

import gen_report_lib

#command line interfaces argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scan", action="store", type=str, default='all',help="specify a scan to work on")
parser.add_argument('-v', "--validate", action='store_true', help="only validate files")

args = parser.parse_args()

#load configuration files
try:
    fs=open('configuration/checks.yml','r')
    checks = yaml.load(fs, Loader=yaml.FullLoader)
    fs.close()
except:
    print("ERROR: cannot open checks file. Exiting.")
    sys.exit()

print("VALIDATE: checks file...")
valid=gen_report_lib.validate_checks(checks)
if not valid:
    print("VALIDATION ERROR: exiting")
    sys.exit()
print("VALIDATE: check file looks ok")

if args.validate:
    sys.exit()

fo=open(args.scan + '/report.txt','w')
fo.write("### REPORT FILE FOR SCAN " + args.scan + " ###\n\n")

print("VALIDATE: devices json files...")
valid=gen_report_lib.validate_devicesjson(args.scan)
if not valid:
    print("VALIDATION ERROR: exiting")
    sys.exit()
print("VALIDATE: devices json files look ok")

print("PROCESSING: start")
for check in checks:
    print("PROCESSING: check " + check['desc'])
    text = eval('gen_report_lib.'+check['test']+'(args.scan, check)')
    #print(text)
    fo.write(text)
    fo.write("\n")

fo.close()
print("PROCESSING: end")
