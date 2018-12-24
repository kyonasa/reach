# -*- coding: utf-8 -*-
"""
Created on 2018/11/7 15:10
@author: mengph
reach
"""

from keystoneauth1 import loading,session
import ConfigParser
import sys
import paramiko
import json
import time
import os
import subprocess
import commands
from glanceclient import client as Gclient
from neutronclient import client as Nclient
from glanceclient.common import utils
keystone_url_180_11="http://10.121.137.50:5000/v2.0"
keystone_url_180_12="http://10.121.137.80:5000/v2.0"
keystone_url_136_132="https://10.121.136.132:5000/v2.0"
keystone_url_137_13="http://10.121.137.54:5000/v2.0"
OPENRC="/root/openrc"
TEMPEST_CONF="/var/lib/jenkins/workspace/tempest/nfvi_4.3/etc/tempest.conf"
def setup(url):
    loader=loading.get_plugin_loader('password')
    auth=loader.load_from_options(auth_url=url,username="admin",password="admin",project_name="admin")
    sess=session.Session(auth=auth)
    glance=Gclient.Client(version="2",session=sess)
    return glance

def image_get(images_client,name="centos"):
    res=[]
    images = images_client.images.list()
    try:
        for image in images:
            image_name=getattr(image,"name",None)
            image_status=getattr(image,"status",None)
            if name.lower() in image_name.lower() and image_status.lower()=="active":
                res.append(image)
    finally:
        return res

def image_create(images_client):
    # fields={'name': u'centos',
    #         'container_format': u'bare',
    #         'disk_format': u'qcow2',
    #         'location': 'http://10.121.136.222/centos7.3_tx.qcow2',
    #         'is_public': "true"
    #         }
    fields = {'name': u'centos',
              'container_format': u'bare',
              'disk_format': u'qcow2',
              'file': 'centos7.3_tx.qcow2',
              'is_public': "true"
              }
    image = images_client.images.create(**fields)
    return image

def check_openrc(url):
    with open(OPENRC,"r") as rc_file:
        rc=rc_file.readlines()
        for i,line in enumerate(rc):
            if "OS_AUTH_URL" in line:
                tmp=line.split("=")
                tmp[1]="'"+url+"'\n"
                rc[i]="=".join(tmp)
    with open("./openrc","w") as new_rc_file:
        new_rc_file.writelines(rc)


def net_get(name="share_net"):
    cmd="source %s && openstack network list -f json"% OPENRC
    res=[]
    try:
        networks=json.loads(subprocess.check_output(cmd, shell=True))
        for net in networks:
            if net["Name"].lower()==name.lower():
                res.append(net)
    finally:
        return res

def tempest_conf(image,net=None,url=None):
    cp = ConfigParser.SafeConfigParser()
    cp.read(TEMPEST_CONF)
    sections=cp.sections()
    if image:
        if cp.has_option('compute', 'image_ref'):
            cp.set('compute', 'image_ref',image[0]["id"])
        if cp.has_option('compute', 'image_ref_alt'):
            cp.set('compute', 'image_ref_alt',image[0]["id"])
    if net:
        if cp.has_option('network', 'public_network_id'):
            cp.set('network', 'public_network_id', net[0]["ID"])
    if url:
        if cp.has_option('identity', 'uri'):
            cp.set('identity', 'uri', url)
        if cp.has_option('identity', 'uri_v3'):
            v3_uri = url.replace('v2.0', 'v3')
            cp.set('identity', 'uri_v3', v3_uri)

    cp.write(open(TEMPEST_CONF, 'w'))


if __name__ == '__main__':
    AUTH_URI=sys.argv[1]
    check_openrc(AUTH_URI)
    glance=setup(AUTH_URI)
    # centos=image_create(glance)
    image=image_get(glance,"testvm")
    net=net_get()
    tempest_conf(image,net,AUTH_URI)



