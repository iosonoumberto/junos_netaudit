import os
import json
import yaml
import operator

from jnpr.junos.factory.factory_loader import FactoryLoader

### VALIDATE FUNCTIONS

def validate_devicesjson(scan):
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    valid=1
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            print("ERROR: could not load device json output " + result)
            print("ERROR: skipping device.")
            valid=0
            continue
        if type(res_dict) is not dict:
            return 0
        if 'model' not in res_dict['facts']['info']:
            print("VALIDATION ERROR: file " + result + " missing model information")
            valid=0
        if 'role' not in res_dict['facts']['info']:
            print("VALIDATION ERROR: file " + result + " missing role information")
            valid=0
        if 'hostname' not in res_dict['facts']['info']:
            print("VALIDATION ERROR: file " + result + " missing hostname information")
            valid=0
    return valid

def validate_checks(checks):
    valid=1
    facts=['release','model','hostname','role']
    fs=open('configuration/commands.yml','r')
    commands = yaml.load(fs, Loader=yaml.FullLoader)
    fs.close()

    fs=open('configuration/nonstd_commands.yml','r')
    nonstd_commands = yaml.load(fs, Loader=yaml.FullLoader)
    fs.close()

    cmd_list=[]
    for cmd in commands:
        cmd_list.append(cmd['name'])
    nonstd_cmd_list=[]
    for cmd in nonstd_commands:
        nonstd_cmd_list.append(cmd['cmd'])

    for check in checks:
        if check['cmd']=='facts' and check['tfield'] not in facts:
            print("VALIDATION ERROR: check " + check['desc'] + " : test field " + check['tfield'] + " not a valid fact")
            valid=0
            continue
        if check['cmd']=='facts' and check['tfield'] in facts:
            continue
        if check['cmd'] in nonstd_cmd_list:
            print("VALIDATION ERROR: check " + check['desc'] + " : cmd " + check['cmd'] + " is a non stadnard command. Full validation skipped.")
            continue
        if check['cmd'] not in cmd_list:
            print("VALIDATION ERROR: check " + check['desc'] + " : cmd " + check['cmd'] + " not found in commands yaml file")
            valid=0
            continue
        if check['test'] in ["string_equal","device_distribution","global_distribution","basic_stats","total_filtered", "all_equal_device", "good_values"]:
            ftv=open('tableviews/'+check['cmd']+'.yaml', 'r')
            d=yaml.load(ftv, Loader=yaml.FullLoader)
            if check['tfield'] not in d[d[check['cmd']]['view']]['fields'].keys():
                print("VALIDATION ERROR: check " + check['desc'] + " : test field " + check['tfield'] + " not found in RPC view")
                valid=0
            continue
        if check['test'] in ["threshold"]:
            fs=open('configuration/devrole_thresholds.yml','r')
            drthresholds = yaml.load(fs, Loader=yaml.FullLoader)
            fs.close()

            fs=open('configuration/global_thresholds.yml','r')
            gthresholds = yaml.load(fs, Loader=yaml.FullLoader)
            fs.close()

            if check['fail'] not in ['higher','lower']:
                print("VALIDATION ERROR: check " + check['desc'] + " : threshold type " + check['fail'] + " not a valid failure criteria")
                valid=0
            if check['tfield'] not in gthresholds and check['tfield'] not in drthresholds:
                print("VALIDATION ERROR: check " + check['desc'] + " : test field " + check['tfield'] + " not defined in any threshold file")
                valid=0
            ftv=open('tableviews/'+check['cmd']+'.yaml', 'r')
            d=yaml.load(ftv, Loader=yaml.FullLoader)
            if check['tfield'] not in d[d[check['cmd']]['view']]['fields'].keys():
                print("VALIDATION ERROR: check " + check['desc'] + " : test field " + check['tfield'] + " not found in RPC view")
                valid=0
            continue
        if check['test'] in ["total","empty"]:
            continue
        print("VALIDATION ERROR: check " + check['desc'] + " : test type " + check['test'] + " not a valid test type")
        valid=0

    return valid

### CHECK FUNCTIONS

def string_equal(scan, check):
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=''
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            dev_skipped.append(result)
            warn=1
            continue
        flag=1
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        for tested in res_dict[check['cmd']]:
            if check['tfield'] not in res_dict[check['cmd']][tested]:
                warn_text+="WARNING: string_equal - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " tfield not found " + str(check['tfield']) + ".\n"
                continue
            if isinstance(res_dict[check['cmd']][tested][check['tfield']], list):
                if len(res_dict[check['cmd']][tested][check['tfield']])==0:
                    nodata.append(res_dict['facts']['info']['hostname'])
                    continue
                try:
                    for listelem in res_dict[check['cmd']][tested][check['tfield']]:
                        if 'ignore' in check:
                            if listelem in check['ignore']:
                                continue
                        if listelem!=check['val']:
                            if flag:
                                failed.append(res_dict['facts']['info']['hostname'])
                                failed_detail[res_dict['facts']['info']['hostname']]=[]
                                flag=0
                            failed_detail[res_dict['facts']['info']['hostname']].append(res_dict[check['cmd']][tested])
                            break
                except Exception as e:
                    warn_text+="WARNING: string_equal - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed.\n"
                    warn_text+="\t" + str(e) + "\n"
                    warn=1
                continue
            try:
                if 'ignore' in check:
                    if res_dict[check['cmd']][tested][check['tfield']] in check['ignore']:
                        continue
                if res_dict[check['cmd']][tested][check['tfield']]!=check['val']:
                    if flag:
                        failed.append(res_dict['facts']['info']['hostname'])
                        failed_detail[res_dict['facts']['info']['hostname']]=[]
                        flag=0
                    failed_detail[res_dict['facts']['info']['hostname']].append(res_dict[check['cmd']][tested])
            except Exception as e:
                warn_text+="WARNING: string_equal - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed.\n"
                warn_text+="\t" + str(e) + "\n"
                warn=1
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped, warn_text)
    return text

def threshold(scan, check):
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=""
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    try:
        fs=open('configuration/devrole_thresholds.yml','r')
        drthresholds = yaml.load(fs, Loader=yaml.FullLoader)
        fs.close()

        fs=open('configuration/global_thresholds.yml','r')
        gthresholds = yaml.load(fs, Loader=yaml.FullLoader)
        fs.close()
    except:
        warn_text+="ERROR: could not open one of thresholds files when running a threshold type test.\n"
        warn_text+="ERROR: check " + check['desc'] + " will be aborted and we will move to next check.\n"
        return
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if str(check['tfield']) in drthresholds:
            if res_dict['facts']['info']['model'] + "_" + res_dict['facts']['info']['role'] in drthresholds[check['tfield']]:
                threshold=float(drthresholds[check['tfield']][res_dict['facts']['info']['model'] + "_" + res_dict['facts']['info']['role']])
        else:
            threshold=float(gthresholds[check['tfield']])
        flag=1
        for tested in res_dict[check['cmd']]:
            if check['tfield'] not in res_dict[check['cmd']][tested]:
                warn_text+="WARNING: threshold - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " tfield not found " + str(check['tfield']) + ".\n"
                continue
            if 'interest' in check:
                if tested not in check['interest']:
                    continue
            try:
                test_float=float(res_dict[check['cmd']][tested][check['tfield']])
            except Exception as e:
                warn_text+="WARNING: threshold - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed.\n"
                warn_text+="\t" + str(e) + "\n"
                warn=1
                continue
            if check['fail']=="lower":
                good = float(res_dict[check['cmd']][tested][check['tfield']])>=threshold
            else:
                good = float(res_dict[check['cmd']][tested][check['tfield']])<=threshold
            if not good:
                if flag:
                    failed.append(res_dict['facts']['info']['hostname'])
                    failed_detail[res_dict['facts']['info']['hostname'] + ' thr: ' + str(threshold)]=[]
                    flag=0
                failed_detail[res_dict['facts']['info']['hostname'] + ' thr: ' + str(threshold)].append(res_dict[check['cmd']][tested])
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped, warn_text)
    return text

def device_distribution(scan, check):
    distr={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=""
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        host=res_dict['facts']['info']['hostname']
        distr[host]={}
        distr_cmd=check['cmd']
        tfield=check['tfield']
        for tested in res_dict[distr_cmd]:
            if check['tfield'] not in res_dict[check['cmd']][tested]:
                warn_text+="WARNING: device_distribution - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " tfield not found " + str(check['tfield']) + ".\n"
                continue
            if 'ignore' in check:
                if res_dict[distr_cmd][tested][tfield] in check['ignore']:
                    continue
            try:
                if res_dict[distr_cmd][tested][tfield] not in distr[host]:
                    distr[host][res_dict[distr_cmd][tested][tfield]]=1
                else:
                    distr[host][res_dict[distr_cmd][tested][tfield]]+=1
            except Exception as e:
                warn_text+="WARNING: distribution - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed."
                warn_text+="\t" + str(e) + "\n"
                warn=1
                continue
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_distribution(check['desc'], warn, tfield, distr, nodata, dev_skipped, warn_text)
    return text

def total(scan, check):
    tot_dict={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=""
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except Exception as e:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            warn_text+="\t" + str(e) + "\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        host=res_dict['facts']['info']['hostname']
        tot=len(res_dict[check['cmd']])
        tot_dict[host]=tot
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_dict(check['desc'], warn, tot_dict, nodata, dev_skipped, warn_text)
    return text

def total_filtered(scan, check):
    tot_dict={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=""
    cmd=check['cmd']
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except Exception as e:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            warn_text+="\t" + str(e) + "\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[cmd]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        host=res_dict['facts']['info']['hostname']
        tot=0
        for tested in res_dict[cmd]:
            if check['tfield'] not in res_dict[check['cmd']][tested]:
                warn_text+="WARNING: total_filtered - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " tfield not found " + str(check['tfield']) + ".\n"
                continue
            if str(res_dict[cmd][tested][check['tfield']])==str(check['val']):
                tot+=1
        tot_dict[host]=tot
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_dict(check['desc'], warn, tot_dict, nodata, dev_skipped, warn_text)
    return text

def basic_stats(scan, check):
    vals={}
    stats={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=""
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    totdev=0
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except Exception as e:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            warn_text+="\t" + str(e) + "\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if check['tfield'] not in res_dict[check['cmd']][list(res_dict[check['cmd']].keys())[0]]:
                warn_text+="WARNING: basic_stats - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " -  tfield not found " + str(check['tfield']) + ".\n"
                nodata.append(res_dict['facts']['info']['hostname'])
                continue
        try:
            vals[res_dict['facts']['info']['hostname']]=float(res_dict[check['cmd']][list(res_dict[check['cmd']].keys())[0]][check['tfield']].strip("%"))
            totdev+=1
        except Exception as e:
            warn_text+="WARNING: basic stats - " + check['desc'] + " - could not extract stats value : " + str(res_dict[check['cmd']][list(res_dict[check['cmd']].keys())[0]][check['tfield']].strip("%")) + " , device : " + res_dict['facts']['info']['hostname'] + "\n"
            warn_text+="\t" + str(e) + "\n"
            warn=1
    if len(vals)==0:
        warn_text+="WARNING: basic stats - " + check['desc'] + " - no values to compute stats\n"
        if bool(len(warn_text)):
            print(warn_text[:-1])
        text=">>> CHECK RESULT FOR " + check['desc'] + "\n\n"
        text+= "No values to compute stats\n"
        return text
    stats["maxv"]={}
    stats["minv"]={}
    try:
        sorted_reverse_stats = sorted(vals.items(), key=operator.itemgetter(1), reverse=True)
        stats["maxv"]["val"]=sorted_reverse_stats[0][1]
        stats["maxv"]["host"]=sorted_reverse_stats[0][0]
    except Exception as e:
        warn_text+="WARNING: basic stats - " + check['desc'] + "could not compute max value\n"
        warn_text+="\t" + str(e) + "\n"
        stats["maxv"]["val"]="NA"
        stats["maxv"]["host"]="NA"
        warn=1
    try:
        sorted_stats = sorted(vals.items(), key=operator.itemgetter(1))
        stats["minv"]["val"]=sorted_stats[0][1]
        stats["minv"]["host"]=sorted_stats[0][0]
    except Exception as e:
        warn_text+="WARNING: basic stats - " + check['desc'] + "could not compute max value\n"
        warn_text+="\t" + str(e) + "\n"
        stats["minv"]["val"]="NA"
        stats["minv"]["host"]="NA"
        warn=1
    tot=0.0
    try:
        for x in vals:
            tot+=float(vals[x])
        stats["avg"]=tot/totdev
        stats["tot"]=totdev
    except Exception as e:
        warn_text+="WARNING: basic stats - " + check['desc'] + "could not compute avg value\n"
        warn_text+="\t" + str(e) + "\n"
        stats["avg"]="NA"
        stats["tot"]="NA"
        warn=1
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_basic_stats(check['desc'], warn, check['unit'], stats, nodata, dev_skipped, warn_text)
    return text

def empty(scan, check):
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=""
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if len(res_dict[check['cmd']])!=0:
            failed.append(res_dict['facts']['info']['hostname'])
            failed_detail[res_dict['facts']['info']['hostname']]=[]
            failed_detail[res_dict['facts']['info']['hostname']].append(res_dict[check['cmd']])
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped, warn_text)
    return text

def global_distribution(scan, check):
    distr={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=""
    distr={}
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        distr_cmd=check['cmd']
        tfield=check['tfield']
        for tested in res_dict[distr_cmd]:
            if check['tfield'] not in res_dict[check['cmd']][tested]:
                warn_text+="WARNING: global_distribution - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " tfield not found " + str(check['tfield']) + ".\n"
                continue
            if 'ignore' in check:
                if res_dict[distr_cmd][tested][tfield] in check['ignore']:
                    continue
            try:
                if res_dict[distr_cmd][tested][tfield] not in distr:
                    distr[res_dict[distr_cmd][tested][tfield]]=1
                else:
                    distr[res_dict[distr_cmd][tested][tfield]]+=1
            except Exception as e:
                warn_text+="WARNING: distribution - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed."
                warn_text+="\t" + str(e) + "\n"
                warn=1
                continue
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_dict(check['desc'], warn, distr, nodata, dev_skipped, warn_text)
    return text

def all_equal_device(scan, check):
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=''
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            dev_skipped.append(result)
            warn=1
            continue
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        testlist=[]
        for tested in res_dict[check['cmd']]:
            if check['tfield'] not in res_dict[check['cmd']][tested]:
                warn_text+="WARNING: all_equal_device - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " tfield not found " + str(check['tfield']) + ".\n"
                continue
            if isinstance(res_dict[check['cmd']][tested][check['tfield']], list):
                if len(res_dict[check['cmd']][tested][check['tfield']])==0:
                    continue
                try:
                    for listelem in res_dict[check['cmd']][tested][check['tfield']]:
                        testlist.append(str(testelem))
                except Exception as e:
                    warn_text+="WARNING: all_equal_equal - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed.\n"
                    warn_text+="\t" + str(e) + "\n"
                    warn=1
                continue
            try:
                testlist.append(str(res_dict[check['cmd']][tested][check['tfield']]))
            except Exception as e:
                warn_text+="WARNING: string_equal - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed.\n"
                warn_text+="\t" + str(e) + "\n"
                warn=1
        if len(testlist)==0:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        alleq = all(elem == testlist[0] for elem in testlist)
        if not alleq:
            failed.append(res_dict['facts']['info']['hostname'])
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped, warn_text)
    return text

def good_values(scan, check):
    failed=[]
    failed_detail={}
    nodata=[]
    dev_skipped=[]
    warn=0
    warn_text=''
    results = os.listdir(scan)
    results.pop(results.index('report.txt'))
    for result in results:
        try:
            fr=open(scan+"/"+result,'r')
            res_dict=json.load(fr)
            fr.close()
        except:
            warn_text+="ERROR: could not load device json output " + result + "\n"
            warn_text+="ERROR: skipping device.\n"
            dev_skipped.append(result)
            warn=1
            continue
        flag=1
        if check['cmd'] not in res_dict:
            print(check['cmd'] + " not found for this file " + result)
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        if not res_dict[check['cmd']]:
            nodata.append(res_dict['facts']['info']['hostname'])
            continue
        for tested in res_dict[check['cmd']]:
            if check['tfield'] not in res_dict[check['cmd']][tested]:
                warn_text+="WARNING: good_values - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " tfield not found " + str(check['tfield']) + ".\n"
                continue
            if isinstance(res_dict[check['cmd']][tested][check['tfield']], list):
                if len(res_dict[check['cmd']][tested][check['tfield']])==0:
                    nodata.append(res_dict['facts']['info']['hostname'])
                    continue
                try:
                    for listelem in res_dict[check['cmd']][tested][check['tfield']]:
                        if listelem not in check['val']:
                            if flag:
                                failed.append(res_dict['facts']['info']['hostname'])
                                failed_detail[res_dict['facts']['info']['hostname']]=[]
                                flag=0
                            failed_detail[res_dict['facts']['info']['hostname']].append(res_dict[check['cmd']][tested])
                            break
                except Exception as e:
                    warn_text+="WARNING: string_equal - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed.\n"
                    warn_text+="\t" + str(e) + "\n"
                    warn=1
                continue
            try:
                if res_dict[check['cmd']][tested][check['tfield']] not in check['val']:
                    if flag:
                        failed.append(res_dict['facts']['info']['hostname'])
                        failed_detail[res_dict['facts']['info']['hostname']]=[]
                        flag=0
                    failed_detail[res_dict['facts']['info']['hostname']].append(res_dict[check['cmd']][tested])
            except Exception as e:
                warn_text+="WARNING: string_equal - " + check['desc'] + " - " + res_dict['facts']['info']['hostname'] + " - " + tested + " logic failed.\n"
                warn_text+="\t" + str(e) + "\n"
                warn=1
    if bool(len(warn_text)):
        print(warn_text[:-1])
    text=print_failures(check['desc'], warn, failed, failed_detail, nodata, dev_skipped, warn_text)
    return text

### PRINT FUNCTIONS

def print_failures(desc, warn, failed, failed_detail, nodata, dev_skipped, warn_text):
    text=">>> CHECK RESULT FOR " + desc + "\n\n"
    if warn:
        text+="!!! warning: it was not possible to process all the data !!!\n\n"
        text+=warn_text + "\n"
    if len(failed)==0:
        text+="Nothing failed\n"
    else:
        text+="The following items failed : " + str(failed) + "\n"
        text+="\n"
        if len(failed_detail)>0:
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

def print_distribution(desc, warn, tfield, distr, nodata, dev_skipped, warn_text):
    text=">>> CHECK RESULT FOR " + desc + "\n\n"
    if warn:
        text+="!!! warning: it was not possible to process all the data !!!\n\n"
        text+=warn_text + "\n"
    text+="distribution based on field : " + tfield + "\n"
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

def print_dict(desc, warn, dict, nodata, dev_skipped, warn_text):
    text=">>> CHECK RESULT FOR " + desc + "\n\n"
    if warn:
        text+="!!! warning: it was not possible to process all the data !!!\n\n"
        text+=warn_text + "\n"
    for x in dict:
        text+="  - " + x + " : " + str(dict[x]) + "\n"
    if len(nodata) > 0:
        text+="\n"
        text+="The following devices had no data: " + str(nodata) + "\n"
    if len(dev_skipped) > 0:
        text+="\n"
        text+="The following devices were skipped: " + str(nodata) + "\n"
    return text

def print_basic_stats(desc, warn, unit, stats, nodata, dev_skipped, warn_text):
    text=">>> CHECK RESULT FOR " + desc + "\n\n"
    if warn:
        text+="!!! warning: it was not possible to process all the data !!!\n\n"
        text+=warn_text + "\n"
    text+="MAX value -> device " + stats['maxv']['host'] + " : " + str(stats['maxv']['val']) + unit + "\n"
    text+="MIN value -> device " + stats['minv']['host'] + " : " + str(stats['minv']['val']) + unit + "\n"
    text+="AVG value -> " + str(stats['avg']) + unit + "\n"
    text+="\t computed over " + str(stats["tot"]) + " devices\n"
    if len(nodata) > 0:
        text+="\n"
        text+="The following devices had no data: " + str(nodata) + "\n"
    if len(dev_skipped) > 0:
        text+="\n"
        text+="The following devices were skipped: " + str(nodata) + "\n"
    return text
