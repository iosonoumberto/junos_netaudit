import os
import json

def print_results(desc, failed, failed_details):
    text="TEST REPORT RESULT FOR " + desc + "\n\n"
    if len(failed)==0:
        text+="Nothing failed\n"
    else:
        text+="The following items failed :\n"
        for e in failed:
            text+="\t" + e + "\n"
        text+="\n"
        text+="Details:\n"
        for e in failed_detail:
            for k in failed_detail[e]:
                text+="\t" + k + " - " + failed_deatil[e][k] + "\n"
            text+="----\n"
    text+="\n"
    return text

def string_equal(scan, check):
    failed=[]
    failed_detail={}
    results = os.listdir(scan)
    print(results)
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