# -*- coding: utf-8 -*-
"""
Created on 2019/1/2 18:29
@author: mengph
reach
"""
from VIM.common.remote_cli import remote_cmd
from VIM.common.fuck_trans_stdout_to_correct import fuck_trans_stdout_to_correct
import json
import time

def create_subnet_cli(fuel_ip,controller_node,net_name="test-mengph-0",CIDR="2001::0/64",ra_mode="dhcpv6-stateful",
                      address_mode="dhcpv6-stateful",nameserver="2001::114",subnet_name="test-mengph-0",ip_version=6,host_route=["2002::0/64","2001::29"]):
    cmd_create_net="source /root/openrc && neutron subnet-create %s %s --ipv6-ra-mode %s --ipv6-address-mode %s " \
                   "--dns-nameserver %s --name=%s --ip-version %d " \
                   "--host-route destination=%s,nexthop=%s" % (net_name,CIDR,ra_mode,address_mode,nameserver,subnet_name,ip_version,host_route[0],host_route[1])
    print cmd_create_net
    print remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_net)

def check_subnet_cli(fuel_ip,controller_node,net_name):
    cmd_check_net="source /root/openrc && neutron subnet-show %s -f json" %net_name
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

def create_subnet(fuel_ip,controller_node,net_name="test-mengph-0",CIDR="2001::0/64",ra_mode="dhcpv6-stateful",
                      address_mode="dhcpv6-stateful",nameserver="2001::114",subnet_name="test-mengph-0",ip_version=6,host_route=["2002::0/64","2001::29"]):
    res=check_subnet_cli(fuel_ip=fuel_ip,controller_node=controller_node,net_name=net_name)
    if res:
        return res
    try:
        create_subnet_cli(fuel_ip,controller_node,net_name=net_name,CIDR=CIDR,ra_mode=ra_mode,
                      address_mode=address_mode,nameserver=nameserver,subnet_name=subnet_name,ip_version=ip_version,host_route=host_route)
    except Exception,error:
        print error, "loacton:create net"
        raise error
    return check_subnet_cli(fuel_ip=fuel_ip,controller_node=controller_node,net_name=net_name)

def tearDown(fuel_ip,controller_node,subnet_name):
    '''after test,clean network'''
    cmd_delete_net="source /root/openrc && neutron subnet-delete %s"%subnet_name
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
    subnet_name="test-mengph-0"
    try:
        net=create_subnet(fuel_ip=fuel_ip,controller_node=controller_node,subnet_name=subnet_name)
        print net

    except Exception,error:
        print error
    finally:
        tearDown(fuel_ip=fuel_ip,controller_node=controller_node,subnet_name=subnet_name)