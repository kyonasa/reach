# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 16:36
@author: mengph
reach
"""
import sys
sys.path.append("..")
from VIM.common.remote_cli import remote_cmd
import time

def create_priv_key(fuel_ip,controller_node,key,key_path):
    '''fucntion for create an openstack keypair for test vm'''
    cmd_create_priv_key="source /root/openrc && openstack keypair create %s > %s" %(key,key_path)
    cmd_chmod=" chmod 600 %s" %key_path
    try:
        print cmd_create_priv_key
        keypair=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_priv_key)
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_chmod)
        return True
    except Exception, error:
        print error
        return False

def tearDown(fuel_ip,controller_node,keypair,key_path):
    '''after test,clean all vm ,flavor ,keypair that used in case, not include image'''
    cmd_delete_keypair = "source /root/openrc && openstack keypair delete %s" % keypair
    cmd_delete_keypath="rm -rf %s" %key_path
    try:
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_keypair)
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_keypath)
        print "env_cleaned",time.ctime()
    except Exception, error:
        print error,"location: clean up"

if __name__ == '__main__':
    fuel_ip = "10.121.137.12"
    controller_node = "node-1"
    key="cyborg_key"
    key_path = "/root/cyborg_key.priv"
    try:
        keypair=create_priv_key(fuel_ip=fuel_ip,controller_node=controller_node,key=key,key_path=key_path)
        print keypair
    except Exception,error:
        print error
    finally:
        tearDown(fuel_ip=fuel_ip,controller_node=controller_node,keypair=key,key_path=key_path)
