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
        fo.write("\t PASS\n")

    #if nothing found check is over
    if len(items)==0:
        fo.write("\t FAIL\n\n")
        return

    if 'eq' in check:
        fo.write("Check if all the nodes have value " + str(check['eq']) + "\n")
        flag=items[0].text is not None
        if not flag:
            fo.write("\t FAIL [specified node path has no text]\n")

        for item in items:
            if item.text is not None:
                flag=(str(item.text)==str(check['eq']))
                if not flag:
                    fo.write("\t FAIL\n")
                    break

        if flag:
            fo.write("\t PASS\n")

    if 'tot' in check:
        if len(items)==int(check['tot']):
            fo.write("\t PASS\n")
        else:
            fo.write("\t FAIL [expected matches: " + str(check['tot']) + " ]\n")

    if 'inspect' in check:
        wrng=False
        if 'failid' not in check:
            fo.write("WRNG: failure identifier not found. Please define it.\n")
            wrng=True
        for i in check['inspect']:
            if 'node' in i and 'value' not in i:
                for item in items:
                    xpathstr=".//" + i['node']
                    if not item.xpath(xpathstr):
                        if wrng:
                            fo.write("One item failed. Please check device.\n")
                        if not wrng:
                            fail_l=[]
                            for key in check['failid']:
                                fail_l.append(item.findtext(key))
                            fail_str=' - '.join(fail_l)
                            fo.write(fail_str + " failed.\n")
            if 'node' in i and 'value' in i:
                for item in items:
                    xpathstr=".//" + i['node'] + "/text()='" + i['value'] + "'"
                    if not item.xpath(xpathstr):
                        if wrng:
                            fo.write("One item failed. Please check device.\n")
                        if not wrng:
                            fail_l=[]
                            for key in check['failid']:
                                fail_l.append(item.findtext(key))
                            fail_str=' - '.join(fail_l)
                            fo.write(fail_str + " failed.\n")

    fo.write("\n")
