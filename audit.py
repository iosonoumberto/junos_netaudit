from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.factory.factory_loader import FactoryLoader

import audit_lib

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

fs=open('configuration/commands.yml','r')
commands = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('configuration/nonstd_commands.yml','r')
nonstd_commands = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('configuration/models.yml','r')
models = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('configuration/historic.yml','r')
historic = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

#to manage historic file inizialization
if historic is None:
    historic={}

#create output folder
foldername= args.role + "_" + time.ctime().replace(' ','_').replace(':','_')
os.mkdir(foldername)

#loop over devices
for router in devices:

    #init results dictionary
    res_dict={}

    #set sleep time between commands
    zzz_cand=max(int(models[router['model']]['zzz']), int(roles[router['role']]['zzz']))
    if 'zzz' in router:
        router['zzz']=max(int(zzz_cand), int(router['zzz']))
    else:
        router['zzz']=zzz_cand

    #check if device must be considered
    if  router['role']==args.role or args.role=="all":
        print("DEVICE: " + router['name'])

        #connect to device
        dev = Device(host=router['ip'], user=settings['username'], password=settings['password'])
        dev.open()

        #save release, model and hostname
        res_dict['facts']={}
        res_dict['facts']['info']={}
        res_dict['facts']['info']['release']=dev.facts['junos_info']['re0']['text']
        res_dict['facts']['info']['hostname']=dev.facts['hostname']
        res_dict['facts']['info']['model']=router['model']
        res_dict['facts']['info']['role']=router['role']

        #find out whther device is single or dual re
        router['2re']=dev.facts['2RE']

        #loop over commands
        for command in commands:
            #check if command has to be executed
            if router['role'] in command['supp_plat'] and (command['2re']=='all' or router['2re']==command['2re']):
                print("\trunning -> "+command['display_name'])
                audit_lib.exec_command(command['name'], dev, res_dict)
            time.sleep(router['zzz'])

        #loop over non standard commands
        for command in nonstd_commands:
            #check if command has to be executed
            if router['role'] in command['supp_plat'] and (command['2re']=='all' or router['2re']==command['2re']):
                print("\trunning -> "+command['display_name'])
                eval('audit_lib.' + command['function'] + '(dev, res_dict, command)')
            time.sleep(router['zzz'])
        #close connection to device
        dev.close()

        #print collected data in json format
        json_out = json.dumps(res_dict, indent = 4)
        fout_name=router['name']+"_"+time.ctime().replace(' ','_').replace(':','_')+".json"
        fo=open(foldername+"/"+fout_name,'w')
        fo.write(json_out)
        fo.close()

        #update historic data
        if router['name'] not in historic:
            historic[router['name']]=[]
            historic[router['name']].append(foldername+"/"+fout_name)
        else:
            historic[router['name']].append(foldername+"/"+fout_name)

#print historic file
hf=open('configuration/historic.yml','w')
yaml.dump(historic, hf)
