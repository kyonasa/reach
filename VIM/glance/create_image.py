# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 15:45
@author: mengph
reach
"""
import time
import json
import sys
sys.path.append("..")
import glance_hello
from VIM.common.remote_cli import remote_cmd
from VIM.common.fuck_trans_stdout_to_correct import fuck_trans_stdout_to_correct

def create_image_from_url(fuel_ip,controller_node,image_url="http://10.121.136.222/centos6.8_gb.qcow2",keystone_url="",image_name="mengph"):
    '''ensure the image we need was active in glance. when the image was not ready, create an image instead of '''
    image=[]
    try:
        image=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
    except Exception, error:
        print error
    if not image:
        try:
            _set_api_version(fuel_ip=fuel_ip,controller_node=controller_node,api_v="1")
            _create_image(fuel_ip=fuel_ip, controller_node=controller_node, image_name=image_name, image_url=image_url)
            time.sleep(5)
            image=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
            _set_api_version(fuel_ip=fuel_ip,controller_node=controller_node,api_v="2")
        except Exception, error:
            print error
            return False
    times=0
    while image and image[0]['status']!="active" and times<=30:
        time.sleep(5)
        try:
            image=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
        except Exception, error:
            print error
        times+=1
    return image

def create_image_from_local(fuel_ip,controller_node,keystone_url,image_url="http://10.121.136.222/centos6.8_gb.qcow2",image_name="mengph"):
    if not _copy_image_from_url(fuel_ip=fuel_ip, controller_node=controller_node,image_url=image_url):
        return False
    res=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
    print res
    if res:
        return res
    try:
        _set_api_version(fuel_ip=fuel_ip, controller_node=controller_node,api_v="2")
        cmd_create_logic="source /root/openrc && glance image-create --file /root/%s --disk-format raw --container-format bare --name %s" %(image_url.split("/")[-1],image_name)
        print cmd_create_logic
        print remote_cmd(fuel_ip=fuel_ip, node=controller_node,cmd=cmd_create_logic)
    except Exception,error:
        print error,"loaction: create image_from_local"
    finally:
        _set_api_version(fuel_ip=fuel_ip, controller_node=controller_node, api_v="2")
        res= _check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
        return res

def _create_image(fuel_ip,controller_node,image_name,image_url):
    '''create an image from url'''
    cmd_create_image = "source /root/openrc && glance image-create --name %s --copy-from %s --disk-format qcow2 --container-format bare  --progress" %(image_name,image_url)
    print cmd_create_image
    print remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_create_image)



def _check_image(fuel_ip,controller_node,image_name="cyborg_image",keystone_url=""):
    '''check the status of image '''
    try:
        glance_client=glance_hello.setup(keystone_url)
        image=glance_hello.image_get(glance_client,name=image_name)
        image["id"]
        if image:
            return image
        else:
            return []
    except Exception,error:
        print error,"location: check_image"
        cmd_check_image="source /root/openrc && openstack image show %s -f json" %image_name
        image=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_image)
        if not image:
            return []
        try:
            json.loads(image)["id"]
            return [json.loads(image)]
        except:
            return [fuck_trans_stdout_to_correct(image)]

def _set_api_version(fuel_ip,controller_node,api_v="2"):
    cmd_set_api_to_x="sed -i '$d' openrc && sed -i '$a export OS_IMAGE_API_VERSION='%s'' openrc" %api_v
    remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_set_api_to_x)


def _copy_image_from_url(fuel_ip,controller_node,image_url):
    cmd_wget="wget %s" %image_url
    cmd_check_firmaware="ls | grep %s" %image_url.split("/")[-1]
    i=0
    '''if not firmware in controller node, download from url, try 3 times, if after download still no firmware, return false'''
    while not remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_firmaware) and i<3:
        remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_wget)
        i+=1
    return i<3

def tearDown(fuel_ip,controller_node,image_uuid):
    '''after test,clean image'''
    cmd_delete_image="source /root/openrc && glance image-delete %s"%image_uuid
    print cmd_delete_image
    try:
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_image)
        print "env_cleaned",time.ctime()
    except Exception, error:
        print error,"location: clean up"


if __name__ == '__main__':
    fuel_ip = "10.121.137.12"
    controller_node = "node-1"
    br_ex_address = "fd00:dead:beef:57::5"
    keystone_url_12_v6 = "http://[%s]:5000/v2.0/tokens" % br_ex_address
    try:
        # image=create_image_from_url(fuel_ip=fuel_ip, controller_node=controller_node, keystone_url=keystone_url_12_v6)
        image=create_image_from_local(fuel_ip=fuel_ip, controller_node=controller_node,keystone_url=keystone_url_12_v6)
        print image
    except Exception,error:
        print error
    finally:
        tearDown(fuel_ip=fuel_ip,controller_node=controller_node,image_uuid=image[0]["id"])