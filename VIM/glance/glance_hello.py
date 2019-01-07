# -*- coding: utf-8 -*-
"""
Created on 2018/12/7 13:21
@author: mengph
reach
"""
from keystoneauth1 import loading,session
from glanceclient import client as Gclient
keystone_url_180_11="http://10.121.137.50:5000/v2.0"
keystone_url_180_12="http://10.121.137.80:5000/v2.0"
keystone_url_136_132="https://10.121.136.132:5000/v2.0"
keystone_url_137_13="http://10.121.137.54:5000/v2.0"
keystone_url_12_v6="http://[fd00:dead:beef:10::2]:5000/v2.0"
OPENRC="/root/openrc"
TEMPEST_CONF="/var/lib/jenkins/workspace/tempest/nfvi_4.3/etc/tempest.conf"

def setup(url):
    loader=loading.get_plugin_loader('password')
    auth=loader.load_from_options(auth_url=url,username="admin",password="admin",project_name="admin")
    sess=session.Session(auth=auth,verify=False)
    glance=Gclient.Client(version="2",session=sess)
    return glance

def image_create(images_client):
    fields={'name': u'centos',
            'container_format': u'bare',
            'disk_format': u'qcow2',
            'copy_from': 'http://10.121.136.222/centos7.3_tx.qcow2',
            'is_public': "true"
            }
    # fields = {'name': u'centos',
    #           'container_format': u'bare',
    #           'disk_format': u'qcow2',
    #           'file': 'centos7.3_tx.qcow2',
    #           'is_public': "true"
    #           }
    image = images_client.images.create(**fields)
    return image

# def image_create2(images_client):

def image_get(images_client,name="centos"):
    res=[]
    images = images_client.images.list()
    try:
        for image in images:
            image_name=getattr(image,"name",None)
            image_status=getattr(image,"status",None)
            if name.lower() == image_name.lower():
                res.append(image)
    except Exception,error:
        print error
    finally:
        return res


if __name__ == '__main__':
    glance=setup(keystone_url_12_v6)
    # centos=image_create(glance)
    image=image_get(glance,"TestVM")
    print image