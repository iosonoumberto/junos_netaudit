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
    fo.write("Found patterns: " + str(len(items)) + "\n")

    if len(check)==2 and len(items)>0:
        fo.write("\t PASS\n")
    if len(check)==2 and len(items)==0:
        fo.write("\t FAIL\n")

    #if nothing found check is over
    if len(items)==0:
        fo.write("\t FAIL\n")
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

    fo.write("\n")
