import matplotlib.pyplot as plt
import yaml

def simple_line(jplot, historic, foldername):
    dev_list=[]
    if devices in jplot:
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
        fig, ax = plt.subplots()
        ax.plot(x,y)
        ax.grid()
        fig.savefig(foldername + "/" + device + "_" + jplot['img_name'] + ".png")
