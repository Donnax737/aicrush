#coding=utf-8
import pickle
#with open('data.json', 'wb') as fp:
#    pickle.dump(dict_temp, fp)
#for k,d in dict_temp.items():
#    print(k)

def load_prompts():
    with open('data.json', 'rb') as fp:
        dict_temp = pickle.load(fp)
    #  可以打印出来瞅瞅
    dcode0 = dict_temp['daction']['d0']
    dcode1 = dict_temp['daction']['d1']
    dcodesp = dict_temp['daction']['dsp']
    lcode0 =[]
    lcode1 = []
    lcodesp = []
    for i in dcode0.keys():
        lcode0.append(i)
    for i in dcode1.keys():
        lcode1.append(i)
    for i in dcodesp.keys():
        lcodesp.append(i)
    return dict_temp,dcode0,dcode1,dcodesp,lcode0,lcode1,lcodesp

def load_aips():
    with open('daip.json', 'rb') as fp:
        daip = pickle.load(fp)
    return daip

