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
    tmp_dict = eval(cmd+'(dev).get()')
    res_dict[cmd]=json.loads(tmp_dict.to_json()).copy()
    return 1

def nonstd_single_node(dev, res_dict, command, args=''):
    if 'args' in command:
        args=command['args']
    rpc=command['cmd']
    field=command['field']
    xml=eval('dev.rpc.' + rpc.replace('-','_') + '(' + args + ')')
    data=xml.find(field).text
    res_dict[rpc]={}
    res_dict[rpc]['data']={}
    res_dict[rpc]['data'][field]=data
    return 1
