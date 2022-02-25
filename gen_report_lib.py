import os
import json
import yaml

def print_failures(desc, failed, failed_detail):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    if len(failed)==0:
        text+="Nothing failed\n"
    else:
        text+="The following items failed : " + str(failed) + "\n"
        text+="\n"
        text+="Details:\n"
        for e in failed_detail:
            text+="  " + e + "\n"
            for l in failed_detail[e]:
                for k in l:
                    text+="\t" + k + " - " + l[k] + "\n"
                text+="\t----\n"
    text+="\n"
    return text

def print_distribution(desc, dfield, distr):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    text+="distribution based on field : " + dfield + "\n"
    for dev in distr:
        tot=0
        text+="  " + e + "\n"
        for x in distr[dev]:
            tot+=distr[dev][x]
        for e in distr[dev]:
            text+="  " + e + " : " + distr[dev][e] + " , " + str(float(distr[dev][e]/tot)) + "%\n"
        text+="\t----\n"
    return text

def string_equal(scan, check):
    failed=[]
    failed_detail={}
    results = os.listdir(scan)
    for result in results:
        fr=open(scan+"/"+result,'r')
        res_dict=json.load(fr)
        flag=1
        for tested in res_dict[check['cmd']]:
            if res_dict[check['cmd']][tested][check['tfield']]!=check['val']:
                if flag:
                    failed.append(res_dict['hostname'])
                    failed_detail[res_dict['hostname']]=[]
                    flag=0
                failed_detail[res_dict['hostname']].append(res_dict[check['cmd']][tested])
    text=print_failures(check['desc'], failed, failed_detail)
    return text

def threshold(scan, check):
    fs=open('configuration/models.yml','r')
    models = yaml.load(fs, Loader=yaml.FullLoader)
    fs.close()

    fs=open('configuration/global_thresholds.yml','r')
    gthresholds = yaml.load(fs, Loader=yaml.FullLoader)
    fs.close()

    failed=[]
    failed_detail={}
    results = os.listdir(scan)
    for result in results:
        fr=open(scan+"/"+result,'r')
        res_dict=json.load(fr)
        if str(check['tfield']+'_thr') in models[res_dict['model']]:
            threshold=models[res_dict['model']][check['tfield']+'_thr']
        else:
            threshold=gthresholds[check['tfield']]
        flag=1
        for tested in res_dict[check['cmd']]:
            if check['fail']=="lower":
                good = int(res_dict[check['cmd']][tested][check['tfield']])>=threshold
            else:
                good = int(res_dict[check['cmd']][tested][check['tfield']])<=threshold
            if not good:
                if flag:
                    failed.append(res_dict['hostname'])
                    failed_detail[res_dict['hostname'] + ' thr: ' + str(threshold)]=[]
                    flag=0
                failed_detail[res_dict['hostname'] + ' thr: ' + str(threshold)].append(res_dict[check['cmd']][tested])
    text=print_failures(check['desc'], failed, failed_detail)
    return text

def distribution(scan, check):
    results = os.listdir(scan)
    distr={}
    for result in results:
        fr=open(scan+"/"+result,'r')
        res_dict=json.load(fr)
        host=result['hostname']
        distr[host]={}
        distr_cmd=check['cmd']
        dfield=check['dfield']
        for e in res_dict[distr_cmd]:
            if e[dfield] not in distr:
                distr[host][e[dfield]]=1
            else:
                distr[host][e[dfield]]+=1
    text=print_distribution(check['desc'], , dfield, distr)
    return text
