# -*- coding: utf-8 -*-
"""
Created on 2018/11/15 11:31
@author: mengph
reach
"""

import yaml
env=4


O_CONF = "/home/mengph/env_12/home/mengph/network_2.yaml"
N_CONF = "/home/mengph/env_12/N_network.yaml"
OUT_PUT = "/home/mengph/env_12/" + "/network_" + str(env) + ".yaml"




def sync_to_new(conf_0,conf_1):
    # print conf_0
    # print conf_1
    if type(conf_0)==type(conf_1)==dict:
        for key in conf_0.keys():
            if sync_to_new(conf_0[key],conf_1[key]):
                print key,conf_0[key],conf_1[key]
                if key.find("id")==-1 or key=="cidr":
                    conf_1[key]=conf_0[key]
    elif type(conf_0)==type(conf_1)==list:
        for i in range(len(conf_0)):
            if type(conf_0[i])==dict:
                for j in range(len(conf_1)):
                    if conf_0[i]["name"]==conf_1[j]["name"]:
                        break
            else:
                j=i
            if sync_to_new(conf_0[i],conf_1[j]):
                return True
    else:
        if conf_0!=conf_1:
            return True
        else:
            return False

def sync_network(O_CONF,N_CONF,OUT_PUT):
    fr_0=open(O_CONF)
    fr_1=open(N_CONF)
    conf_0=yaml.load(fr_0)
    conf_1=yaml.load(fr_1)
    sync_to_new(conf_0,conf_1)
    print "=----------------------------="
    sync_to_new(conf_0,conf_1)
    f=open(OUT_PUT,"w")
    yaml.dump(conf_1,f)
    fr_1.close()
    fr_0.close()



def refresh_old(conf_0,conf_1):
    ports = {}
    networks = {}
    tmp = []
    for p in conf_1:
         ports[p["mac"]]=p["id"]
         tmp+=p["assigned_networks"]

    for network in tmp:
        networks[network["name"]]=network["id"]

    # print "-----------------------------------------"
    # for p in conf_0:
    #     print p
    # print "-----------------------------------------"
    # for p in conf_1:
    #     print p
    #
    # print "-----------------------------------------"
    # print ports
    # print networks

    for p in conf_0:
        if p["mac"]:
            p["id"]=ports[p["mac"]]
        if p['assigned_networks']:
            for network in p['assigned_networks']:
                network["id"]=networks[network["name"]]

    print "-----------------------------------------"
    for p in conf_0:
        print p
    print "-----------------------------------------"
    for p in conf_1:
        print p


def sync_node(O_CONF,N_CONF,OUT_PUT):
    fr_0=open(O_CONF)
    fr_1=open(N_CONF)
    conf_0=yaml.load(fr_0)
    conf_1=yaml.load(fr_1)
    refresh_old(conf_0, conf_1)
    f=open(OUT_PUT,"w")
    yaml.dump(conf_0,f)
    fr_1.close()
    fr_0.close()







if __name__ == '__main__':
    sync_network(O_CONF,N_CONF,OUT_PUT)
