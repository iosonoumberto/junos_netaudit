import matplotlib.pyplot as plt
import yaml

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
        plt.plot(x,y)
        plt.grid()
        plt.title(jplot['desc'])
        plt.ylabel(jplot['ylabel'])
        plt.xlabel("scans")
        plt.xticks(rotation=80)
        plt.tight_layout()
        plt.savefig(foldername + "/" + device + "_" + jplot['img_name'] + ".png", bbox_inches = "tight")

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
            plt.plt(plots_data[draw]['x'], plots_data[draw]['y'], label=l2)
        plt.grid()
        plt.title(jplot['desc'])
        plt.ylabel(jplot['ylabel'])
        plt.xlabel("scans")
        plt.xticks(rotation=80)
        plt.legend()
        plt.tight_layout()
        plt.savefig(foldername + "/" + device + "_" + jplot['img_name'] + ".png", bbox_inches = "tight")
