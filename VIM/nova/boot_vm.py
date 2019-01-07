# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 15:43
@author: mengph
reach
"""
import sys
sys.path.append("..")
from VIM.common.remote_cli import remote_cmd
from VIM.common.fuck_trans_stdout_to_correct import fuck_trans_stdout_to_correct
import time
import json

def create_vm_cli(fuel_ip,controller_node,image="centos6.8",flavor="cyborg",network="share_net",SG="default",AZ="nova",name="cyborg-copro",key="cyborg_key",custom_script=""):
    '''create a vm with cli ,return the vm's information as a dict '''
    if custom_script:
        cmd_create_vm="source /root/openrc && nova boot --image %s --flavor %s --nic net-name=%s --config-drive True --user-data %s --key-name %s  --security-groups %s --availability-zone %s %s" \
                  %(image,flavor,network,custom_script,key,SG,AZ,name)
    else:
        cmd_create_vm = "source /root/openrc && nova boot --image %s --flavor %s --nic net-name=%s --config-drive True --key-name %s  --security-groups %s --availability-zone %s %s" \
                        % (image, flavor, network, key, SG, AZ, name)
    cmd_check_vm="source /root/openrc && openstack server show %s -f json" %name
    try:
        print cmd_create_vm
        print remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_vm)
    except Exception, error:
        print error
    finally:
        tmp_res=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_vm)
        try:
            json.loads(tmp_res)["id"]
            return json.loads(tmp_res)
        except:
            return fuck_trans_stdout_to_correct(tmp_res)

def tearDown(fuel_ip,controller_node,vm_name):
    '''after test,clean all vm ,flavor ,keypair that used in case, not include image'''
    name=vm_name
    cmd_delete_vm="source /root/openrc && nova delete %s" %name
    try:
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_vm)
        print "env_cleaned",time.ctime()
    except Exception, error:
        print error,"location: clean up"

if __name__ == '__main__':
    fuel_ip = "10.121.137.12"
    controller_node = "node-1"
    br_ex_address = "fd00:dead:beef:57::5"
    keystone_url_12_v6 = "http://[%s]:5000/v2.0/tokens" % br_ex_address
    vm_name="mengph"
    try:
        server=create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,name=vm_name,custom_script="/root/custom_script",flavor="4-4096-20",key="my_key")
        print server
    except Exception,error:
        print error
    finally:
        tearDown(fuel_ip=fuel_ip,controller_node=controller_node,vm_name=vm_name)