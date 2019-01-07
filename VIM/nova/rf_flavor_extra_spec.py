# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 17:53
@author: mengph
reach
"""
import sys
sys.path.append("..")
import VIM.glance.create_image
import set_flavor
import boot_vm
import priv_key
import time
import xmltodict
from  VIM.common.check_vm import check_vm
from VIM.common.get_controller_node import get_nodes,get_controller_node,get_keystone_url


def setup(fuel_ip,controller_node,keystone_url):
    priv_key.create_priv_key(fuel_ip=fuel_ip, controller_node=controller_node, key=key, key_path=key_path)
    image=VIM.glance.create_image.create_image_from_local(fuel_ip=fuel_ip, controller_node=controller_node,keystone_url=keystone_url,image_name="centos6.8",image_url="http://10.121.136.222/centos6.8_gb.qcow2")
    print image

def _teardown_vm(fuel_ip,controller_node,vm_name,flavor_name):
    set_flavor.tearDown(fuel_ip=fuel_ip, controller_node=controller_node, flavor_name=flavor_name)
    boot_vm.tearDown(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name)

def env_teardown(fuel_ip,controller_node,key,key_path):
    priv_key.tearDown(fuel_ip=fuel_ip, controller_node=controller_node, keypair=key, key_path=key_path)

def cpu_policy_dedicated(fuel_ip,controller_node):
    spec = ["hw:cpu_policy=dedicated"]
    vm_name="cpu_policy_dedicated"
    flavor=set_flavor.create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec,flavor_name=vm_name)
    print flavor
    server=boot_vm.create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,name=vm_name,flavor=vm_name,key=key)
    print server
    cmd_check_device_in_vm=["sudo uname -a"]
    time.sleep(20)
    for i in range(7):
        try:
            time.sleep(5)
            r = check_vm(fuel_ip=fuel_ip, vm_name=server["name"], ex_cmd=[key_path, cmd_check_device_in_vm],
                         controller_node=controller_node)
            '''check vm status include network and using cmd inner the vm to check the pci device was attched weather or not '''
            print r
            print "check_time: %d" % i
            if r["ex"]:
                tmp = xmltodict.parse(r["vm_xml"])["domain"]["cputune"]["vcpupin"]
                print tmp
                for vcpu in tmp:
                    if not vcpu["@cpuset"].isdigit():
                        _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name,
                                     flavor_name=vm_name)
                        return False
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return True
        except Exception,error:
            print error,"location: cpu_policy_dedicated"
            _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node,vm_name=vm_name,flavor_name=vm_name)
            return False
    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
    return False

def vm_socket_policy(fuel_ip,controller_node):
    result=None
    spec = ["hw:cpu_sockets=2"]
    vm_name="cpu_sockets_2"
    flavor=set_flavor.create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec,flavor_name=vm_name)
    print flavor
    server=boot_vm.create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,name=vm_name,flavor=vm_name,key=key)
    print server
    cmd_check_device_in_vm=["sudo lscpu"]
    time.sleep(20)
    for i in range(7):
        try:
            time.sleep(5)
            r = check_vm(fuel_ip=fuel_ip, vm_name=server["name"], ex_cmd=[key_path, cmd_check_device_in_vm],
                         controller_node=controller_node)
            '''check vm status include network and using cmd inner the vm to check the pci device was attched weather or not '''
            print r
            print "check_time: %d" % i
            if r["ex"]:
                tmp = xmltodict.parse(r["vm_xml"])["domain"]["cpu"]["topology"]
                print tmp
                if tmp["@sockets"]=="2":
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return True
                else:
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return False
        except Exception,error:
            print error,"location: cpu_policy_dedicated"
            _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
            return False
    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
    return False

def vm_numa_pinning(fuel_ip,controller_node):
    result=None
    spec = ["hw:numa_node.0=0"]
    vm_name="numa_node0_0"
    flavor=set_flavor.create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec,flavor_name=vm_name)
    print flavor
    server=boot_vm.create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,name=vm_name,flavor=vm_name,key=key)
    print server
    cmd_check_device_in_vm=["sudo lscpu"]
    time.sleep(20)
    for i in range(7):
        try:
            time.sleep(5)
            r = check_vm(fuel_ip=fuel_ip, vm_name=server["name"], ex_cmd=[key_path, cmd_check_device_in_vm],
                         controller_node=controller_node)
            '''check vm status include network and using cmd inner the vm to check the pci device was attched weather or not '''
            print r
            print "check_time: %d" % i
            if r["ex"]:
                tmp = xmltodict.parse(r["vm_xml"])["domain"]["numatune"]
                print tmp
                if tmp["memnode"]["@nodeset"]=="0":
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return True
                else:
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return False
        except Exception,error:
            print error,"location: cpu_policy_dedicated"
            _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
            return False
    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
    return False


def vm_numa_policy(fuel_ip,controller_node):
    result=None
    spec = ["hw:numa_nodes=2"]
    vm_name="vm_numa_policy"
    flavor=set_flavor.create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec,flavor_name=vm_name)
    print flavor
    server=boot_vm.create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,name=vm_name,flavor=vm_name,key=key)
    print server
    cmd_check_device_in_vm=["sudo lscpu"]
    time.sleep(20)
    for i in range(7):
        try:
            time.sleep(5)
            r = check_vm(fuel_ip=fuel_ip, vm_name=server["name"], ex_cmd=[key_path, cmd_check_device_in_vm],
                         controller_node=controller_node)
            '''check vm status include network and using cmd inner the vm to check the pci device was attched weather or not '''
            print r
            print "check_time: %d" % i
            if r["ex"]:
                tmp = xmltodict.parse(r["vm_xml"])["domain"]["numatune"]
                print tmp
                if tmp["memory"]["@nodeset"]=="0-1":
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return True
                else:
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return False
        except Exception,error:
            print error,"location: cpu_policy_dedicated"
            _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
            return False
    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
    return False

def pci_numa_affinity_strict(fuel_ip,controller_node):
    spec = ["hw:pci_numa_affinity=strict"]
    vm_name="pci_numa_affinity_strict"
    flavor=set_flavor.create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec,flavor_name=vm_name)
    print flavor
    server=boot_vm.create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,name=vm_name,flavor=vm_name,key=key)
    print server
    cmd_check_device_in_vm=["sudo uname -a"]
    time.sleep(20)
    for i in range(7):
        try:
            time.sleep(5)
            r = check_vm(fuel_ip=fuel_ip, vm_name=server["name"], ex_cmd=[key_path, cmd_check_device_in_vm],
                         controller_node=controller_node)
            '''check vm status include network and using cmd inner the vm to check the pci device was attched weather or not '''
            print r
            print "check_time: %d" % i
            if r["ex"]:
                tmp = xmltodict.parse(r["vm_xml"])["domain"]["numatune"]
                print tmp
                if tmp["memory"]["@nodeset"]=="0-1":
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return True
                else:
                    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
                    return False
        except Exception,error:
            print error,"location: cpu_policy_dedicated"
            _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
            return False
    _teardown_vm(fuel_ip=fuel_ip, controller_node=controller_node, vm_name=vm_name, flavor_name=vm_name)
    return False

if __name__ == '__main__':
    print time.ctime()
    fuel_ip = "10.121.138.100"
    nodes=get_nodes(fuel_ip=fuel_ip)
    controller_node=get_controller_node(nodes)
    keystone_url_12_v6 = get_keystone_url(fuel_ip=fuel_ip, controller_node=controller_node)
    # controller_node = "node-5"
    # br_ex_address = "fd00:dead:beef:57::5"
    # keystone_url_12_v6 = "http://[%s]:5000/v2.0/tokens" % br_ex_address
    key="cyborg_key"
    key_path = "/root/cyborg_key.priv"
    setup(fuel_ip=fuel_ip,controller_node=controller_node,keystone_url=keystone_url_12_v6)
    try:
        xml=cpu_policy_dedicated(fuel_ip=fuel_ip,controller_node=controller_node)
        print xml
        xml=vm_numa_policy(fuel_ip=fuel_ip,controller_node=controller_node)
        print xml
        xml=vm_socket_policy(fuel_ip=fuel_ip,controller_node=controller_node)
        print xml
        xml=vm_numa_pinning(fuel_ip=fuel_ip,controller_node=controller_node)
        print xml
        xml=pci_numa_affinity_strict(fuel_ip=fuel_ip,controller_node=controller_node)
        print xml
    except Exception,error:
        print error
    finally:
        env_teardown(fuel_ip=fuel_ip,controller_node=controller_node,key=key,key_path=key_path)
        print time.ctime()