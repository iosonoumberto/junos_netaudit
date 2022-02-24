from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.factory.factory_loader import FactoryLoader

import audit_lib

import time
import argparse
import sys
import yaml
import json

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--role", action="store", type=str, default='all',help="device role")

args = parser.parse_args()

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

fs=open('configuration/models.yml','r')
models = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

for router in devices:
    res_dict={}
    zzz_cand=max(int(models[router['model']]['zzz']), int(roles[router['role']]['zzz']))
    if 'zzz' in router:
        router['zzz']=max(int(zzz_cand), int(router['zzz']))
    else:
        router['zzz']=zzz_cand
    if  router['role']==args.role or args.role=="all":
        print("DEVICE: " + router['name'])
        dev = Device(host=router['ip'], user=settings['username'], password=settings['password'])
        dev.open()
        router['2re']=dev.facts['2RE']
        for command in commands:
            if router['role'] in command['supp_plat'] and (command['2re']=='all' or router['2re']==command['2re']):
                print("\trunning -> "+command['display_name'])
                audit_lib.exec_command(command['name'], dev, res_dict)
            time.sleep(router['zzz'])
        dev.close()
        json_out = json.dumps(res_dict, indent = 4)
        fout_name=router['name']+"_"+time.ctime().replace(' ','_')+".json"
        fo=open(fout_name,'w')
        fo.write(json_out)
        fo.close()