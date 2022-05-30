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

def exec_confcheck(check, conf, fo):
    fo.write("VERIFY: " + check['desc'] + "\n")
    #extract xpath
    items=conf.xpath(check['path'])
    fo.write("Matches: " + str(len(items)) + "\n")

    if len(check)==2 and len(items)>0:
        fo.write("\tPASS\n")

    #if nothing found check is over
    if len(items)==0:
        fo.write("\tFAIL\n\n")
        return

    if 'eq' in check:
        fo.write("Check if all the nodes have value " + str(check['eq']) + "\n")
        flag=items[0].text is not None
        if not flag:
            fo.write("\tFAIL [specified node path has no text]\n")

        for item in items:
            if item.text is not None:
                flag=(str(item.text)==str(check['eq']))
                if not flag:
                    fo.write("\tFAIL\n")
                    break

        if flag:
            fo.write("\tPASS\n")

    if 'tot' in check:
        fo.write("Check if the number of occurences is the expected one: " + str(check['tot']) + "\n")
        if len(items)==int(check['tot']):
            fo.write("\tPASS\n")
        else:
            fo.write("\tFAIL\n")

    if 'inspect' in check:
        fo.write("Inspecting element\n")
        wrng=False
        if 'failid' not in check:
            fo.write("WRNG: failure identifier not found. Please define it.\n")
            wrng=True
        for i in check['inspect']:
            if 'node' in i and 'value' not in i:
                fo.write("\tNode: " + i['node'] + "\n")
                for item in items:
                    xpathstr=".//" + i['node']
                    if not item.xpath(xpathstr):
                        if wrng:
                            fo.write("\t\tOne item failed. Please check device.\n")
                        if not wrng:
                            fail_l=[]
                            for key in check['failid']:
                                fail_l.append(item.findtext(key))
                            fail_str=' - '.join(fail_l)
                            fo.write("\t\t" + fail_str + " failed.\n")
            if 'node' in i and 'value' in i:
                fo.write("\tNode: " + i['node'] + " , value: " + i['value'] + "\n")
                for item in items:
                    xpathstr=".//" + i['node'] + "/text()='" + i['value'] + "'"
                    if not item.xpath(xpathstr):
                        if wrng:
                            fo.write("\t\tOne item failed. Please check device.\n")
                        if not wrng:
                            fail_l=[]
                            for key in check['failid']:
                                fail_l.append(item.findtext(key))
                            fail_str=' - '.join(fail_l)
                            fo.write("\t\t" + fail_str + " failed.\n")

    fo.write("\n")
