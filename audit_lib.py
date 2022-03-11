from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.factory.factory_loader import FactoryLoader

import audit_lib

import time
import argparse
import sys
import yaml
import json
import lxml

#function to execute an arbitrary command
#tableview definition file must be named consistently with commands configuration file
#inside tableview definition file, object must have the same name as the filename
def exec_command (cmd, dev, res_dict):
    ftv = open('tableviews/'+cmd+'.yaml', 'r')
    yml = ftv.read()
    ftv.close()
    globals().update(FactoryLoader().load(yaml.load(yml, Loader=yaml.FullLoader)))
    try:
        tmp_dict = eval(cmd+'(dev).get()')
        res_dict[cmd]=json.loads(tmp_dict.to_json()).copy()
    except Exception as e:
        print("\tRPC error")
        res_dict[cmd]={}
    return 1

def nonstd_single_node(dev, res_dict, command, args=''):
    if 'args' in command:
        args=command['args']
    rpc=command['rpc']
    cmd=command['cmd']
    res_dict[cmd]={}
    res_dict[cmd]['data']={}
    for field in command['map']:
        res_dict[cmd]['data'][field]=eval('dev.rpc.' + rpc.replace('-','_') + '(' + args + ')').find(command['map'][field]).text
    return 1

def nonstd_table(dev, res_dict, command, args=''):
    if 'args' in command:
        args=command['args']
    rpc=command['rpc']
    cmd=command['cmd']
    res_dict[cmd]={}

    xml=eval('dev.rpc.' + rpc.replace('-','_') + '(' + args + ')')

    keys=xml.findall(command['item'] + '/' + command['key'])

    tmp_dict={}
    for field in command['map']:
        tmp_dict[field] = xml.xpath(command['item'] + '/' + command['map'][field] + '/text()')

    for k in keys:
        res_dict[cmd][k]={}
        for f in tmp_dict:
            res_dict[cmd][k][f] = tmp_dict[f][0]
            tmp_dict[f].pop(0)
    return 1
