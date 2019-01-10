# -*- coding: utf-8 -*-
"""
Created on 2019/1/9 11:06
@author: mengph
reach
"""
from VIM.common.remote_cli import remote_cmd
from VIM.common.fuck_trans_stdout_to_correct import fuck_trans_stdout_to_correct
import json
import time

class Interface(object):
    '''record interface information as below'''
    def __init__(self,network_id=None):
        self.name=""
        self.admin_state_up=None
        self.allowed_address_pairs=[]
        self.binding_host_id=""
        self.binding_profile={}
        self.binding_vif_details={}
        self.binding_vif_type  = ""
        self.binding_vnic_type=""
        self.created_at=""
        self.description=""
        self.device_id=""
        self.device_owner=""
        self.extra_dhcp_opts={}
        self.fixed_ips={}
        self.id=""
        self.mac_address=""
        self.network_id=network_id
        self.qos_policy_id=""
        self.security_groups=""
        self.status=None
        self.tenant_id=""
        self.updated_at=""

    def show_interface(self):
        print "-------------"
        for item in self.__dict__.items():
            print item[0],":",item[1]
        print "-------------"

    def create_port(self,fuel_ip,controller_node,network=None):
        cmd_create_port_cli="source /root/openrc && neutron port-create"
        args=[]
        for item in self.__dict__.items():
            if item[1]:
                if item[0]=="network_id" and not network:
                    network=item[1]
                elif item[0]=="id":
                    print "port exist"
                    return
                else:
                    args.append(item)
        if args:
            for arg in args:
                cmd_create_port_cli+=(" --"+arg[0].replace("_","-")+" "+arg[1])
        cmd_create_port_cli+=" %s" %network
        print cmd_create_port_cli
        try:
            remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_port_cli)
        except Exception,error:
            raise error

    def check_port(self,fuel_ip,controller_node,uuid=None):
        if not uuid:
            uuid=self.id
        cmd_check_port_cli = "source /root/openrc && neutron port-show %s -f json" %uuid
        try:
            port=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_port_cli)
        except Exception,error:
            raise error
        for k,v in fuck_trans_stdout_to_correct(port).iteritems():
            setattr(self,k,v)

if __name__ == '__main__':
    fuel_ip = "10.121.138.100"
    controller_node = "node-3"
    br_ex_address = "fd00:dead:beef:57::5"
    keystone_url_12_v6 = "http://[%s]:5000/v2.0/tokens" % br_ex_address

    # port1=Interface(network_id="d99fb12e-a724-4fcc-800e-a22105e92824")
    # setattr(port1,"name","test-mengph-2")
    # port1.create_port(fuel_ip=fuel_ip,controller_node=controller_node)
    # port1.show_interface()

    port1=Interface()
    port1.check_port(fuel_ip=fuel_ip,controller_node=controller_node,uuid="b6497c2f-b752-42d0-b8ce-2cadeedd699b")
    port1.show_interface()