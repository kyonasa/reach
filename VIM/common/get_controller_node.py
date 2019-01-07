# -*- coding: utf-8 -*-
"""
Created on 2019/1/2 15:07
@author: mengph
reach
"""
import sys
sys.path.append("..")
from remote_cli import remote_cmd
from fuck_trans_stdout_to_correct import fuck_trans_stdout_to_correct
import fuel_remote as fuel_remote
import json



class Nodes(object):
    def __init__(self,name,roles):
        self.name=name
        self.roles=roles
        self.networks={}
        self.linked={}
        self.nova_service=None
        self.neutron_service = None
        self.rabbitmq_service=None

    def show_node(self):
        print "-------------"
        print "name:",self.name
        print "roles: ",self.roles
        print "networks: ",self.networks
        print "linked: ",self.linked
        print "nova_service: ",self.nova_service
        print "neutron_service: ", self.neutron_service
        print "rabbitmq_service: ", self.rabbitmq_service
        print "-------------"

def get_controller_node(nodes):
    for node in nodes.values():
        if " controller" in node.roles:
            return node.name
    return "no avalibale controller node"

def get_nodes(fuel_ip):
    nodes = {}
    cmd = "fuel nodes"
    res = fuel_remote.ssh(fuel_ip, cmd=cmd)
    for i in range(2, len(res)):
        nodes["node-" + res[i].split("|")[0].strip()] = Nodes(name="node-" + res[i].split("|")[0].strip(),roles=res[i].split("|")[6].rstrip().split(","))
    return nodes


def get_keystone_url(fuel_ip,controller_node):
    cmd_get_keystone_url="source /root/openrc && openstack endpoint show keystone -f json"
    tmp=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_get_keystone_url)
    try:
        return json.loads(tmp)["publicurl"]
    except:
        return fuck_trans_stdout_to_correct(tmp)["publicurl"]

if __name__ == '__main__':
    fuel_ip = "10.121.137.12"
    nodes=get_nodes(fuel_ip=fuel_ip)
    controller_node=get_controller_node(nodes=nodes)
    print controller_node
    keystone_url=get_keystone_url(fuel_ip=fuel_ip,controller_node=controller_node)
    print keystone_url