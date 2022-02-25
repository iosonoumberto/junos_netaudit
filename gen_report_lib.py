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
        text+="  " + dev + "\n"
        for x in distr[dev]:
            tot+=distr[dev][x]
        for e in distr[dev]:
            text+="  " + e + " : " + str(distr[dev][e]) + " , " + str(float(distr[dev][e]/tot*100)) + "%\n"
        text+="\t----\n"
    return text

def print_dict(desc, dict):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    for x in dict:
        text+="  - " + x + " : " + str(dict[x]) + "\n"
        text+="\t----\n"
    return text

def print_basic_stats(desc,unit, stats):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    text+="MAX value -> device " + stats['maxv']['host'] + " : " + float(stats['maxv']['val']) + unit + "\n"
    text+="MIN value -> device " + stats['minv']['host'] + " : " + float(stats['minv']['val']) + unit + "\n"
    text+="AVG value -> " + float(stats['avg']) + unit + "\n"
    return text

def string_equal(scan, check):
    failed=[]
    failed_detail={}
    results = os.listdir(scan)
    for result in results:
        fr=open(scan+"/"+result,'r')
        res_dict=json.load(fr)
        fr.close()
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
        fr.close()
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
        fr.close()
        host=res_dict['hostname']
        distr[host]={}
        distr_cmd=check['cmd']
        dfield=check['dfield']
        for e in res_dict[distr_cmd]:
            if res_dict[distr_cmd][e][dfield] not in distr[host]:
                distr[host][res_dict[distr_cmd][e][dfield]]=1
            else:
                distr[host][res_dict[distr_cmd][e][dfield]]+=1
    text=print_distribution(check['desc'], dfield, distr)
    return text

def total(scan, check):
    results = os.listdir(scan)
    tot_dict={}
    for result in results:
        fr=open(scan+"/"+result,'r')
        res_dict=json.load(fr)
        fr.close()
        host=res_dict['hostname']
        tot=len(res_dict[check['cmd']])
        tot_dict[host]=tot
    text=print_dict(check['desc'], tot_dict)
    return text

def basic_stats(scan, check):
    results = os.listdir(scan)
    vals={}
    stats={}
    totdev=float(len(results))
    for result in results:
        fr=open(scan+"/"+result,'r')
        res_dict=json.load(fr)
        fr.close()
        vals[res_dict['hostname']]=float(res_dict[check['cmd']][list(res_dict['cmd'].keys())[0]][check['sfield']].strip("%"))
    sorted_stats = sorted(vals.items(), key=operator.itemgetter(1))
    sorted_reverse_stats = sorted(vals.items(), key=operator.itemgetter(1), reverse=True)
    stats["maxv"]["val"]=sorted_reverse_stats[list(sorted_reverse_stats.keys())[0]]
    stats["maxv"]["host"]=list(sorted_reverse_stats.keys())[0]
    stats["minv"]["val"]=sorted_stats[list(sorted_stats.keys())[0]]
    stats["minv"]["host"]=list(sorted_stats.keys())[0]
    tot=0.0
    for x in vals:
        tot+=float(vals[x])
    stats["avgv"]=tot/totdev
    text=print_basic_stats(check['desc'],check['unit'], stats)
    return text
