# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 17:19
@author: mengph
reach
"""
import sys
sys.path.append("..")
import unittest
import VIM.glance.create_image
import set_flavor
import boot_vm

fuel_ip = "10.121.137.11"
controller_node = "node-5"
br_ex_address = "fd00:dead:beef:57::5"
keystone_url = "http://[%s]:5000/v2.0/tokens" % br_ex_address


def test_cpu_policy_dedicated():
    spec = ["hw:cpu_policy=dedicated"]
    vm_name="cpu_policy_dedicated"
    flavor=set_flavor.create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec,flavor_name="cpu_policy_dedicated")
    print flavor
    image=VIM.glance.create_image.create_image_from_local(fuel_ip=fuel_ip, controller_node=controller_node,keystone_url=keystone_url)
    print image
    server=boot_vm.create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,name=vm_name,custom_script="/root/custom_script",flavor="cpu_policy_dedicated",key="my_key")
    print server
    return image

def tearDown(self):
    print("- End - DeleteResourse")
    boot_vm.tearDown(fuel_ip=fuel_ip, controller_node=controller_node, vm_name="cpu_policy_dedicated")
    set_flavor.tearDown(fuel_ip=fuel_ip, controller_node=controller_node, flavor_name="cpu_policy_dedicated")



if __name__ == '__main__':
    unittest.main()
    # image = test_cpu_policy_dedicated(fuel_ip=fuel_ip, controller_node=controller_node, keystone_url=keystone_url_12_v6)
    # try:
    #     image=test_cpu_policy_dedicated(fuel_ip=fuel_ip,controller_node=controller_node,keystone_url=keystone_url_12_v6)
    # except Exception,error:
    #     print error
    # finally:
    #     set_flavor.tearDown(fuel_ip=fuel_ip,controller_node=controller_node,flavor_name="cpu_policy_dedicated")
    #     glance.create_image.tearDown(fuel_ip=fuel_ip,controller_node=controller_node,image_uuid=image[0]["id"])
    #     boot_vm.tearDown(fuel_ip=fuel_ip,controller_node=controller_node,vm_name="cpu_policy_dedicated")