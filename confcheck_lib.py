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
    fo.write("VERIFY: " + check['desc'])
    #extract xpath
    items=conf.xpath(check['path'])
    fo.write("Found patterns: " + str(len(items)))

    #if nothing found check is over
    if len(items)==0:
        return

    if 'eq' in check:
        fo.write("Check if all the nodes have value " + str(check['eq']))
        for item in items:
            if item.text is not None:
                flag=(str(item.text)==str(check['eq']))
                if not flag:
                    break
        if flag:
            fo.write("\t PASS")
        else:
            fo.write("\t FAIL")
