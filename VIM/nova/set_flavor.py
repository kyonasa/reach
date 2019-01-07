# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 14:20
@author: mengph
reach
"""
import sys
sys.path.append("..")
from VIM.common.remote_cli import remote_cmd
from VIM.common.fuck_trans_stdout_to_correct import fuck_trans_stdout_to_correct
import json
import time

def create_flavor_cli(fuel_ip,controller_node,spec=["hw:accelerator_device=Co-processor:1"],flavor_name="mengph",vcpu="4",ram="8192",disk="20"):
    '''create a flavor you want ,even can set the extra spec, return the flavor infor as a dict'''
    flavor=flavor_name
    cmd_create_flavor="source /root/openrc && nova flavor-create %s auto %s %s %s" %(flavor,ram,disk,vcpu)
    cmd_check_flavor="source /root/openrc && openstack flavor show %s -f json" %flavor
    try:
        print cmd_create_flavor
        if remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_flavor):
            specs={}
            for item in spec:
                key=item.split("=")[0]
                value=item.split("=")[1]
                if key in specs:
                    specs[key]+=(","+value)
                else:
                    specs[key]=value
            for key in specs.keys():
                cmd_set_flavor_spec = "source /root/openrc && openstack flavor set %s --property %s" % (flavor, key+"="+specs[key])
                print cmd_set_flavor_spec
                remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_set_flavor_spec)
    except Exception, error:
        print error
    finally:
        tmp_res=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_flavor)
        try:
            json.loads(tmp_res)["id"]
            return json.loads(tmp_res)
        except:
            return fuck_trans_stdout_to_correct(tmp_res)

def tearDown(fuel_ip,controller_node,flavor_name):
    '''after test,clean all vm ,flavor ,keypair that used in case, not include image'''
    flavor=flavor_name
    cmd_delete_flavor="source /root/openrc && nova flavor-delete %s" %flavor
    try:
        remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_delete_flavor)
        print "env_cleaned",time.ctime()
    except Exception, error:
        print error,"location: clean up"


if __name__ == '__main__':
    fuel_ip = "10.121.137.11"
    controller_node = "node-1"
    spec=["hw:accelerator_device=Co-processor:1","hw:pci_numapinning=2"]
    try:
        flavor=create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec)
        print flavor
    except Exception,error:
        print error
    finally:
        tearDown(fuel_ip=fuel_ip,controller_node=controller_node,flavor_name=flavor["name"])