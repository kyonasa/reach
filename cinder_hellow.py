# -*- coding: utf-8 -*-
"""
Created on 2018/6/14 18:37
@author: mengph
reach
"""

from cinderclient import base
from cinderclient import client
from keystoneauth1 import loading,session
def setup(keystone_url="",admin="admin",password="admin",project="admin"):
    loader=loading.get_plugin_loader('password')
    auth=loader.load_from_options(auth_url=keystone_url,username="admin",password="admin",project_name="admin")
    sess=session.Session(auth=auth,verify=False)
    cinder=client.Client(version="2.0",session=sess)
    return cinder
# q_a_t1=cinder.qos_specs.associate()
def cinder_services(cinder_client):
    return cinder_client.services.list()

if __name__ == '__main__':
    cinder=setup()
    print cinder.services.list()
    print cinder.volume_types.list()
    print cinder.volumes.list()
