# -*- coding: utf-8 -*-
"""
Created on 2019/1/2 17:37
@author: mengph
reach
"""
from VIM.common.remote_cli import remote_cmd
from VIM.common.fuck_trans_stdout_to_correct import fuck_trans_stdout_to_correct
import json
import time

def create_net_cli(fuel_ip,controller_node,net_name="test-mengph-0",ra_type="ra-advertisement",type="vlan",physical_network="physnet2",segmentation_id="1010",vlan_transparent=True,mtu=9000):
    cmd_create_net="source /root/openrc && neutron net-create %s --ra-type %s --provider:network_type %s " \
                   "--provider:physical_network %s --provider:segmentation_id %s --vlan-transparent %s " \
                   "--mtu %d" % (net_name,ra_type,type,physical_network,segmentation_id,vlan_transparent,mtu)
    print cmd_create_net
    print remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_net)

def check_net_cli(fuel_ip,controller_node,net_name):
    cmd_check_net="source /root/openrc && neutron net-show %s -f json" %net_name
    try:
        network=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_net)
        if not network:
            return None
        try:
            json.loads(network)["id"]
            return json.loads(network)
        except:
            return fuck_trans_stdout_to_correct(network)
    except Exception,error:
        print error,"loacton:check net"
        raise error

def update_net_cli(fuel_ip,controller_node,net_name,element):
    cmd_update_net="source /root/openrc && neutron net-show %s -f json"

def create_net(fuel_ip,controller_node,net_name="test-mengph-0",ra_type="ra-advertisement",type="vlan",physical_network="physnet2",segmentation_id="1010",vlan_transparent=True,mtu=9000):
    res=check_net_cli(fuel_ip=fuel_ip,controller_node=controller_node,net_name=net_name)
    if res:
        return res
    try:
        create_net_cli(fuel_ip,controller_node,net_name=net_name,ra_type=ra_type,type=type,physical_network=physical_network,segmentation_id=segmentation_id,vlan_transparent=vlan_transparent,mtu=mtu)
    except Exception,error:
        print error, "loacton:create net"
        raise error
    return check_net_cli(fuel_ip=fuel_ip,controller_node=controller_node,net_name=net_name)

def tearDown(fuel_ip,controller_node,net_name):
    '''after test,clean network'''
    cmd_delete_net="source /root/openrc && neutron net-delete %s"%net_name
    print cmd_delete_net
    try:
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_net)
        print "env_cleaned",time.ctime()
    except Exception, error:
        print error,"location: clean up"


if __name__ == '__main__':
    fuel_ip = "10.121.138.100"
    controller_node = "node-3"
    br_ex_address = "fd00:dead:beef:57::5"
    keystone_url_12_v6 = "http://[%s]:5000/v2.0/tokens" % br_ex_address
    net_name="test-mengph-1"
    try:
        net=create_net(fuel_ip=fuel_ip,controller_node=controller_node,net_name=net_name)
        print net

    except Exception,error:
        print error
    finally:
        tearDown(fuel_ip=fuel_ip,controller_node=controller_node,net_name=net_name)