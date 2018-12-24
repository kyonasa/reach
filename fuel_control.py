# -*- coding: utf-8 -*-
"""
Created on 2018/11/15 16:11
@author: mengph
reach
"""
from fuel_remote import ssh,scp
from fuel_sync_setting import sync_node,sync_network
import os

env=8
ROLE_CONF="/home/mengph/env_12/roles.conf"
fuel_path="/home/mengph"
robot_path="/home/mengph/env_12"
fuel_ip="10.121.137.12"
nodes={}
cmd_debug="fuel nodes"
def setup():
    # ssh("10.121.137.12",
    #           "fuel env -c --name mengph --rel 1 --mode ha --network-mode neutron --net-segment-type vlan --storage ceph")
    res=ssh(fuel_ip,cmd=cmd_debug)
    while len(nodes.keys())<5:
        for i in range(2,len(res)):
            nodes[res[i].split("|")[5].strip()]=res[i].split("|")[0].rstrip()
    # print nodes
    env= ssh("10.121.137.12",
              "fuel env -c --name mengph --rel 1 --mode ha --network-mode neutron --net-segment-type vlan --storage ceph")
    if env:
        left = env[0].find("id")
        right = env[0].find(",")

    return env[0][left+3:right]

def set_role(fuel_ip):
    fr=open(ROLE_CONF)
    for node in fr.readlines():
        node_mac=":".join(node.split(":")[0:6])[1:-1]
        node_roles=node.split(":")[-1][1:-2]
        if node_mac in nodes:
            cmd="fuel --env %s node set --node %s --role %s" %(env,node_mac,node_roles)
            print cmd
            print ssh(fuel_ip,cmd=cmd)


def copy_new_conf_to_loacl(fuel_ip,nodes,mode):
    if mode=="nodes":
        for node_mac in nodes.keys():
            scp(fuel_ip,src_path=fuel_path+"/"+node_mac+"/node_"+nodes[node_mac]+"/interfaces.yaml",dst_path=robot_path+"/"+node_mac+"/interfaces.yaml",fun="download")
    elif mode=="settings":
        scp(fuel_ip, src_path=fuel_path + "/network_"+str(env)+".yaml",
            dst_path=robot_path +"/N_network.yaml", fun="download")

def conf_nodes():
    for node_mac in nodes.keys():
        old_dir=os.popen("ls "+"/home/mengph/env_12/home/mengph/"+node_mac+" | grep node").readlines()
        O_CONF = "/home/mengph/env_12/home/mengph/"+node_mac+"/"+old_dir[0].splitlines()[0]+"/interfaces.yaml"
        N_CONF = "/home/mengph/env_12/"+node_mac+"/interfaces.yaml"
        OUT_PUT="/home/mengph/env_12/"+node_mac+"/interfaces_new.yaml"
        # print O_CONF,N_CONF,OUT_PUT
        os.popen("cp "+"/home/mengph/env_12/home/mengph/"+node_mac+"/"+old_dir[0].splitlines()[0]+"/disks.yaml"+" /home/mengph/env_12/"+node_mac+"/disks.yaml")
        sync_node(O_CONF,N_CONF,OUT_PUT=OUT_PUT)

def copy_refresh_conf_to_fuel(fuel_ip,mode):
    if mode=="nodes":
        for node_mac in nodes.keys():
            scp(fuel_ip,dst_path=fuel_path+"/"+node_mac+"/node_"+nodes[node_mac]+"/interfaces.yaml",src_path=robot_path+"/"+node_mac+"/interfaces_new.yaml",fun="upload")
            scp(fuel_ip, dst_path=fuel_path + "/" + node_mac + "/node_" + nodes[node_mac] + "/disks.yaml",
                src_path=robot_path + "/" + node_mac + "/disks.yaml", fun="upload")
    elif mode=="settings":
        scp(fuel_ip,dst_path=fuel_path + "/network_"+str(env)+".yaml",src_path=robot_path+"/network_R.yaml",fun="upload")
        scp(fuel_ip, dst_path=fuel_path + "/settings_" + str(env) + ".yaml", src_path=robot_path + "/settings_R.yaml",fun="upload")


def conf_env():
    O_CONF="/home/mengph/env_12/home/mengph/network_2.yaml"
    N_CONF="/home/mengph/env_12/N_network.yaml"
    OUT_PUT = "/home/mengph/env_12/" + "/network_R.yaml"
    sync_network(O_CONF,N_CONF,OUT_PUT)
    os.popen("cp /home/mengph/env_12/home/mengph/settings_2.yaml /home/mengph/env_12/settings_R.yaml")



if __name__ == '__main__':
    env=setup()
    scp(fuel_ip,dst_path="/root/",src_path="home/mengph/rearch/fuel_config.py",fun="upload")
    ssh(fuel_ip,"python /root/fuel_config.py download_settings "+str(env))
    copy_new_conf_to_loacl(fuel_ip,nodes,mode="settings")
    conf_env()
    copy_refresh_conf_to_fuel(fuel_ip,mode="settings")
    ssh(fuel_ip,"python /root/fuel_config.py upload_settings "+str(env))
    set_role(fuel_ip)
    ssh(fuel_ip,"python /root/fuel_config.py download_nodes "+str(env))
    copy_new_conf_to_loacl(fuel_ip,nodes,mode="nodes")
    conf_nodes()
    copy_refresh_conf_to_fuel(fuel_ip,mode="nodes")
    ssh(fuel_ip,"python /root/fuel_config.py upload_nodes "+str(env))
