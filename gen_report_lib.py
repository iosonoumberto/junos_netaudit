import os
import json
import yaml
import operator

def print_failures(desc, warn, failed, failed_detail, nodata, dev_skipped):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    if warn:
        text+=" ! warning: it was not possible to process all the data !\n\n"
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
                    text+="\t" + str(k) + " - " + str(l[k]) + "\n"
                text+="\t----\n"
    text+="\n"
    if len(nodata) > 0:
        text+="\n"
        text+="The following devices had no data: " + str(nodata) + "\n"
    if len(dev_skipped) > 0:
        text+="\n"
        text+="The following devices were skipped: " + str(nodata) + "\n"
    return text

def print_distribution(desc, warn, dfield, distr, nodata, dev_skipped):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    if warn:
        text+=" ! warning: it was not possible to process all the data !\n\n"
    text+="distribution based on field : " + dfield + "\n"
    for dev in distr:
        tot=0
        text+="  " + dev + "\n"
        for x in distr[dev]:
            tot+=distr[dev][x]
        for e in distr[dev]:
            text+="  " + e + " : " + str(distr[dev][e]) + " , " + str(float(distr[dev][e]/tot*100)) + "%\n"
        text+="\t----\n"
    if len(nodata) > 0:
        text+="\n"
        text+="The following devices had no data: " + str(nodata) + "\n"
    if len(dev_skipped) > 0:
        text+="\n"
        text+="The following devices were skipped: " + str(nodata) + "\n"
    return text

def print_dict(desc, warn, dict, nodata, dev_skipped):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    if warn:
        text+=" ! warning: it was not possible to process all the data !\n\n"
    for x in dict:
        text+="  - " + x + " : " + str(dict[x]) + "\n"
        text+="\t----\n"
    if len(nodata) > 0:
        text+="\n"
        text+="The following devices had no data: " + str(nodata) + "\n"
    if len(dev_skipped) > 0:
        text+="\n"
        text+="The following devices were skipped: " + str(nodata) + "\n"
    return text

def print_basic_stats(desc, warn, unit, stats, nodata, dev_skipped):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    if warn:
        text+=" ! warning: it was not possible to process all the data !\n\n"
    text+="MAX value -> device " + stats['maxv']['host'] + " : " + str(stats['maxv']['val']) + unit + "\n"
    text+="MIN value -> device " + stats['minv']['host'] + " : " + str(stats['minv']['val']) + unit + "\n"
    text+="AVG value -> " + str(stats['avg']) + unit + "\n"
    if len(nodata) > 0:
        text+="\n"
        text+="The following devices had no data: " + str(nodata) + "\n"
    if len(dev_skipped) > 0:
        text+="\n"
        text+="The following devices were skipped: " + str(nodata) + "\n"
    return text

def string_equal(scan, check):
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    results = os.listdir(scan)
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            print("ERROR: could not load device json output " + result + "\n")
            print("ERROR: skipping device.\n")
            dev_skipped.append(result)
            warn=1
            continue
        flag=1
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['hostname'])
            continue
        for tested in res_dict[check['cmd']]:
            try:
                if res_dict[check['cmd']][tested][check['tfield']]!=check['val']:
                    if flag:
                        failed.append(res_dict['hostname'])
                        failed_detail[res_dict['hostname']]=[]
                        flag=0
                        failed_detail[res_dict['hostname']].append(res_dict[check['cmd']][tested])
            except Exception as e:
                print("WARNING: string_equal - " + check['desc'] + " - " + res_dict['hostname'] + " - " + tested + " logic failed.")
                print("\t" + str(e))
                warn=1
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped)
    return text

def threshold(scan, check):
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    results = os.listdir(scan)
    try:
        fs=open('configuration/models.yml','r')
        models = yaml.load(fs, Loader=yaml.FullLoader)
        fs.close()

        fs=open('configuration/global_thresholds.yml','r')
        gthresholds = yaml.load(fs, Loader=yaml.FullLoader)
        fs.close()
    except:
        print("ERROR: could not open one of thresholds files when running a threshold type test.\n")
        print("ERROR: check " + check['desc'] + " will be aborted and we will move to next check.\n")
        return
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            print("ERROR: could not load device json output " + result + "\n")
            print("ERROR: skipping device.\n")
            dev_skipped.append(result)
            warn=1
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['hostname'])
            continue
        if str(check['tfield']+'_thr') in models[res_dict['model']]:
            threshold=float(models[res_dict['model']][check['tfield']+'_thr'])
        else:
            threshold=float(gthresholds[check['tfield']])
        flag=1
        for tested in res_dict[check['cmd']]:
            if 'interest' in check:
                if tested not in check['interest']:
                    continue
            try:
                test_float=float(res_dict[check['cmd']][tested][check['tfield']])
            except Exception as e:
                print("WARNING: threshold - " + check['desc'] + " - " + res_dict['hostname'] + " - " + tested + " logic failed.")
                print("\t" + str(e))
                warn=1
                continue
            if check['fail']=="lower":
                good = float(res_dict[check['cmd']][tested][check['tfield']])>=threshold
            else:
                good = float(res_dict[check['cmd']][tested][check['tfield']])<=threshold
            if not good:
                if flag:
                    failed.append(res_dict['hostname'])
                    failed_detail[res_dict['hostname'] + ' thr: ' + str(threshold)]=[]
                    flag=0
                failed_detail[res_dict['hostname'] + ' thr: ' + str(threshold)].append(res_dict[check['cmd']][tested])
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped)
    return text

def distribution(scan, check):
    distr={}
    nodata=[]
    dev_skipped=[]
    warn=0
    results = os.listdir(scan)
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            print("ERROR: could not load device json output " + result + "\n")
            print("ERROR: skipping device.\n")
            dev_skipped.append(result)
            warn=1
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['hostname'])
            continue
        host=res_dict['hostname']
        distr[host]={}
        distr_cmd=check['cmd']
        dfield=check['dfield']
        for tested in res_dict[distr_cmd]:
            try:
                if res_dict[distr_cmd][tested][dfield] not in distr[host]:
                    distr[host][res_dict[distr_cmd][tested][dfield]]=1
                else:
                    distr[host][res_dict[distr_cmd][tested][dfield]]+=1
            except Exception as e:
                print("WARNING: distribution - " + check['desc'] + " - " + res_dict['hostname'] + " - " + tested + " logic failed.")
                print("\t" + str(e))
                warn=1
                continue
    text=print_distribution(check['desc'], warn, dfield, distr, nodata, dev_skipped)
    return text

def total(scan, check):
    results = os.listdir(scan)
    tot_dict={}
    nodata=[]
    dev_skipped=[]
    warn=0
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            print("ERROR: could not load device json output " + result + "\n")
            print("ERROR: skipping device.\n")
            dev_skipped.append(result)
            warn=1
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['hostname'])
            continue
        host=res_dict['hostname']
        tot=len(res_dict[check['cmd']])
        tot_dict[host]=tot
    text=print_dict(check['desc'], warn, tot_dict, nodata, dev_skipped)
    return text

def basic_stats(scan, check):
    results = os.listdir(scan)
    vals={}
    stats={}
    totdev=float(len(results))
    nodata=[]
    dev_skipped=[]
    warn=0
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            print("ERROR: could not load device json output " + result + "\n")
            print("ERROR: skipping device.\n")
            dev_skipped.append(result)
            warn=1
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['hostname'])
            continue
        vals[res_dict['hostname']]=float(res_dict[check['cmd']][list(res_dict[check['cmd']].keys())[0]][check['sfield']].strip("%"))
    sorted_stats = sorted(vals.items(), key=operator.itemgetter(1))
    sorted_reverse_stats = sorted(vals.items(), key=operator.itemgetter(1), reverse=True)
    stats["maxv"]={}
    stats["minv"]={}
    stats["maxv"]["val"]=sorted_reverse_stats[0][1]
    stats["maxv"]["host"]=sorted_reverse_stats[0][0]
    stats["minv"]["val"]=sorted_stats[0][1]
    stats["minv"]["host"]=sorted_stats[0][0]
    tot=0.0
    for x in vals:
        tot+=float(vals[x])
    stats["avg"]=tot/totdev
    text=print_basic_stats(check['desc'], warn, check['unit'], stats, nodata, dev_skipped)
    return text

def empty(scan, check):
    results = os.listdir(scan)
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            print("ERROR: could not load device json output " + result + "\n")
            print("ERROR: skipping device.\n")
            dev_skipped.append(result)
            warn=1
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['hostname'])
            continue
        if len(res_dict[check['cmd']])!=0:
            failed.append(res_dict['hostname'])
            failed_detail[res_dict['hostname']]=[]
            failed_detail[res_dict['hostname']].append(res_dict[check['cmd']])
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped)
    return text
