import matplotlib.pyplot as plt
import yaml
from datetime import datetime
import matplotlib.dates as mdates

def simple_line_specific(jplot, historic, foldername):
    dev_list=[]
    if 'devices' in jplot:
        dev_list = jplot['devices'].copy()
    else:
        dev_list = historic.keys().copy()

    for device in dev_list:
        x=[]
        y=[]
        for scan in historic[device]:
            try:
                fi=open(scan,'r')
                dev_data = yaml.load(fi, Loader=yaml.FullLoader)
            except Exception as e:
                print(str(device) + " SCAN: " + str(scan) + ", LOAD SCAN FILE ERROR: " + str(e))
                return
            try:
                l1=jplot['data'].split("->")[0]
                l2=jplot['data'].split("->")[1]
                l3=jplot['data'].split("->")[2]
                float_verify=float(dev_data[str(l1)][str(l2)][str(l3)])
            except Exception as e:
                print(str(device) + " SCAN: " + str(scan) + ", DATA EXTRACT ERROR: " + str(e))
                return
            x.append(scan.split("/")[1].split("_audit_")[1].replace("_"," ")[:-5])
            y.append(float(dev_data[str(l1)][str(l2)][str(l3)]))
        if len(x)<1:
            print(str(device) + ", NO DATA TO PLOT ERROR: " + str(e))
            return
        plt.plot(x,y, linestyle='-', marker='o')
        plt.grid()
        plt.title(jplot['desc'])
        plt.ylabel(jplot['ylabel'])
        plt.xlabel("scans")
        plt.xticks(rotation=80)
        plt.tight_layout()
        plt.savefig(foldername + "/" + device + "_" + jplot['img_name'] + ".png", bbox_inches = "tight")
        plt.clf()

def simple_line_multi(jplot, historic, foldername):
    dev_list=[]
    if 'devices' in jplot:
        dev_list = jplot['devices'].copy()
    else:
        dev_list = historic.keys().copy()

    for device in dev_list:
        plots_data={}
        for scan in historic[device]:
            try:
                fi=open(scan,'r')
                dev_data = yaml.load(fi, Loader=yaml.FullLoader)
            except Exception as e:
                print(str(device) + " SCAN: " + str(scan) + ", LOAD SCAN FILE ERROR: " + str(e))
                return
            l1=jplot['data'].split("->")[0]
            l3=jplot['data'].split("->")[1]
            for l2 in dev_data[str(l1)]:
                try:
                    float_verify=float(dev_data[str(l1)][l2][str(l3)])
                except Exception as e:
                    print(str(device) + " SCAN: " + str(scan) + ", DATA EXTRACT ERROR: " + str(e))
                    return
                if l2 not in plots_data:
                    plots_data[l2]={}
                    plots_data[l2]['y']=[]
                    plots_data[l2]['y'].append(float(dev_data[str(l1)][l2][str(l3)]))
                    plots_data[l2]['x']=[]
                    plots_data[l2]['x'].append(scan.split("/")[1].split("_audit_")[1].replace("_"," ")[:-5])
                else:
                    plots_data[l2]['y'].append(float(dev_data[str(l1)][l2][str(l3)]))
                    plots_data[l2]['x'].append(scan.split("/")[1].split("_audit_")[1].replace("_"," ")[:-5])
        for draw in plots_data:
            if len(plots_data[draw]['x'])<1:
                print(str(device) + ", " + l2 + " NO DATA TO PLOT ERROR: " + str(e))
                continue
            plt.plot(plots_data[draw]['x'], plots_data[draw]['y'], label=draw, linestyle='-', marker='o')
        plt.grid()
        plt.title(jplot['desc'])
        plt.ylabel(jplot['ylabel'])
        plt.xlabel("scans")
        plt.xticks(rotation=80)
        plt.legend()
        plt.tight_layout()
        plt.savefig(foldername + "/" + device + "_" + jplot['img_name'] + ".png", bbox_inches = "tight")
        plt.clf()

def compare_devices_specific(jplot, historic, foldername):
    dev_list=[]
    if 'devices' in jplot:
        dev_list = jplot['devices'].copy()
    else:
        dev_list = list(historic.keys()).copy()

    timeline=[]
    create_timeline(timeline,historic)
    print(timeline)

    for device in dev_list:
        tmp_tl=timeline.copy()
        x=[]
        y=[]
        for scan in historic[device]:
            try:
                fi=open(scan,'r')
                dev_data = yaml.load(fi, Loader=yaml.FullLoader)
            except Exception as e:
                print(str(device) + " SCAN: " + str(scan) + ", LOAD SCAN FILE ERROR: " + str(e))
                return
            scandate = " ".join(scan.split("/")[0].split("_")[1:])
            while scandate != tmp_tl[0]:
                x.append(tmp_tl[0])
                y.append(None)
                tmp_tl.pop(0)
            try:
                l1=jplot['data'].split("->")[0]
                l2=jplot['data'].split("->")[1]
                l3=jplot['data'].split("->")[2]
                float_verify=float(dev_data[str(l1)][str(l2)][str(l3)])
            except Exception as e:
                print(str(device) + " SCAN: " + str(scan) + ", DATA EXTRACT ERROR: " + str(e))
                x.append(scan.split('/')[0][scan.split('/')[0].index('_')+1:].replace('_',' ' ))
                y.append(None)
                tmp_tl.pop(0)
                continue
            x.append(scan.split('/')[0][scan.split('/')[0].index('_')+1:].replace('_',' ' ))
            y.append(float(dev_data[str(l1)][str(l2)][str(l3)]))
            tmp_tl.pop(0)
        if len(x)<1:
            print(str(device) + ", NO DATA TO PLOT ERROR FOR DEVICE: " + device)
            continue
        print("X")
        print(x)
        print("Y")
        print(y)
        plt.plot(x,y, linestyle='-', marker='o', label=device)
    plt.grid()
    plt.title(jplot['desc'])
    plt.ylabel(jplot['ylabel'])
    plt.xlabel("scans")
    plt.xticks(rotation=80)
    plt.legend()
    plt.tight_layout()
    plt.savefig(foldername + "/" + jplot['img_name'] + ".png", bbox_inches = "tight")
    plt.clf()

def create_timeline(timeline,historic):
    tmptl=[]
    for device in historic:
        for scan in historic[device]:
            strdate = " ".join(scan.split("/")[0].split("_")[1:])
            ts = datetime.strptime(strdate, '%a %b %d %H %M %S %Y').timestamp()
            if ts not in tmptl:
                tmptl.append(ts)
    tmptl.sort()
    for elem in tmptl:
        timeline.append(datetime.fromtimestamp(elem).strftime('%a %b %d %H %M %S %Y'))
