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
import re

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
        print("\t" + str(e))
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

def nonstd_table(dev, res_dict, command, args=', dev_timeout=180'):
    if 'args' in command:
        args=command['args'] + ', dev_timeout=55'
    rpc=command['rpc']
    cmd=command['cmd']
    res_dict[cmd]={}

    try:
        xml=eval('dev.rpc.' + rpc.replace('-','_') + '(' + args + ')')
    except Exception as e:
        print("\tRPC error")
        print("\t" + str(e))
        res_dict[cmd]={}
        return 1

    keys=xml.xpath(command['item'] + '/' + command['key'] + '/text()')

    tmp_dict={}
    for field in command['map']:
        tmp_dict[field] = xml.xpath(command['item'] + '/' + command['map'][field] + '/text()')

    for k in keys:
        res_dict[cmd][k]={}
        for f in tmp_dict:
            res_dict[cmd][k][f] = tmp_dict[f][0]
            tmp_dict[f].pop(0)
    return 1

def sys_snap_1re(dev, res_dict, command, args=''):
    if 'args' in command:
        args=command['args']
    rpc=command['rpc']
    cmd=command['cmd']
    res_dict[cmd]={}
    res_dict[cmd]['re0']={}

    try:
        xml=eval('dev.rpc.' + rpc.replace('-','_') + '(' + args + ')')
    except Exception as e:
        print("\tRPC error")
        print("\t" + str(e))
        res_dict[cmd]={}
        return 1
    res=xml.text
    res_dict[cmd]['re0']['versions']=re.findall('Junos version: (.*)\n',res)
    try:
        res_dict[cmd]['re0']['nonrectot']=re.search('Total non-recovery snapshots: (\d+)\n',res).group(1)
    except:
        res_dict[cmd]['re0']['nonrectot']=0
    try:
        res_dict[cmd]['re0']['rectot']=re.search('Total recovery snapshots: (\d+)\n',res).group(1)
    except:
        res_dict[cmd]['re0']['rectot']=0
    return 1

def nonstd_nested_table(dev, res_dict, command, args=''):
    if 'args' in command:
        args=command['args']
    rpc=command['rpc']
    cmd=command['cmd']
    res_dict[cmd]={}

    try:
        xml=eval('dev.rpc.' + rpc.replace('-','_') + '(' + args + ')')
    except Exception as e:
        print("\tRPC error")
        print("\t" + str(e))
        res_dict[cmd]={}
        return 1

    items=xml.xpath(command['item'])

    for i in items:
        k=i.findtext(command['key'])
        res_dict[cmd][k]={}
        for f in command['fields']:
            res_dict[cmd][k][f]=i.findtext(command['fields'][f])
        sub_items=i.xpath(command['nested']['item'])
        for si in sub_items:
            sk=si.findtext(command['nested']['key'])
            for sf in command['nested']['fields']:
                res_dict[cmd][k][sk.lower() + "_" + sf]=si.findtext(command['nested']['fields'][sf])
    return 1
