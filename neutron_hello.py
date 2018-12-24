# -*- coding: utf-8 -*-
"""
Created on 2018/11/30 15:43
@author: mengph
reach
"""
from neutronclient.v2_0 import client
from keystoneauth1 import loading,session
keystone_url_200="http://172.16.90.2:5000/v2.0"
keystone_url_10_2="http://10.121.137.80:5000/v2.0"
keystone_url_180_3="http://172.15.50.2:5000/v2.0"
keystone_url_tmp="http://10.121.136.132:5000/v2.0"
def setup(keystone_url=keystone_url_10_2,admin="admin",password="admin",project="admin"):
    loader=loading.get_plugin_loader('password')
    auth=loader.load_from_options(auth_url=keystone_url,username=admin,password=password,project_name=project)
    sess=session.Session(auth=auth,verify=False)
    neutron=client.Client(session=sess)
    return neutron

def neutron_agents(neutron_client):
    return  neutron_client.list_agents()["agents"]