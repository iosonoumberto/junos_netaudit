from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.factory.factory_loader import FactoryLoader

import confcheck_lib

import time
import argparse
import sys
import yaml
import json
import os

#command line interfaces argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--role", action="store", type=str, default='all',help="device role")

args = parser.parse_args()

#load configuration files
fs=open('configuration/settings.yml','r')
settings = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('devices.yml','r')
devices = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('configuration/roles.yml','r')
roles = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('configuration/confchecks.yml','r')
confchecks = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

#create output folder
foldername= "sanity_conf_check_" + args.role + "_" + time.ctime().replace(' ','_').replace(':','_')
os.mkdir(foldername)

#loop over devices
for router in devices:
    #check if device must be considered
    if  router['role']==args.role or args.role=="all":
        print("* DEVICE: " + router['name'])

        #connect to device
        dev = Device(host=router['ip'], user=settings['username'], password=settings['password'])
        dev.open()
        conf=dev.rpc.get_config()
        dev.close()

        #open output file
        fout_name=router['name']+"_"+time.ctime().replace(' ','_').replace(':','_')+".txt"
        fo=open(foldername+"/"+fout_name,'w')

        #loop over commands
        for check in confchecks:
            confcheck_lib.exec_confcheck(check, conf, fo)
