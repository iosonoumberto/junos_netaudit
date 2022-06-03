from jnpr.junos import Device
from jnpr.junos.exception import *
from jnpr.junos.factory.factory_loader import FactoryLoader

import jplot_lib

import time
import argparse
import sys
import yaml
import json
import os

#load configuration files
fs=open('configuration/settings.yml','r')
settings = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('configuration/jplots.yml','r')
jplots = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

fs=open('configuration/historic.yml','r')
historic = yaml.load(fs, Loader=yaml.FullLoader)
fs.close()

#create output folder
foldername= "JPLOT_" + time.ctime().replace(' ','_').replace(':','_')
os.mkdir(foldername)

#loop over devices
for jplot in jplots:
    print("\plotting -> "+jplot['desc'])
    eval('jplot_lib.'+jplot['test']+'(jplot, historic, foldername)')
