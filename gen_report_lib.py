import os
import json

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
            if res_dict[check['cmd']][tested][check['kfield']]!=check['val']:
                if flag:
                    failed.append(res_dict['hostname'])
                    failed_detail[res_dict['hostname']]=[]
                    flag=0
                failed_detail[res_dict['hostname']].append(res_dict[check['cmd']][tested])
    text="TEST REPORT RESULT FOR " + check['desc'] + "\n\n"
    if len(failed)==0:
        text+="Nothing failed\n"
    else:
        text+="The following items failed :\n"
        for e in failed:
            text+="\t" + e + "\n"
        text+="\n"
        text+="Details:\n"
        print(failed_detail)
