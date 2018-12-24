# -*- coding: utf-8 -*-
"""
Created on 2018/7/12 16:31
@author: mengph
reach
"""
from keystoneauth1 import loading,session
from keystoneclient import client
from keystoneclient import base
from keystoneclient import exceptions
keystone_url_200="http://172.16.90.2:5000/v2.0"
keystone_url_10_2="http://10.121.137.50:5000/v2.0"
keystone_url_180_3="http://172.15.50.2:5000/v2.0"
keystone_url_108="http://172.16.80.3:5000/v2.0"
keystone_url_tmp="http://10.121.136.132:5000/v2.0"
loader=loading.get_plugin_loader('password')
auth=loader.load_from_options(auth_url=keystone_url_10_2,username="admin",password="admin",project_name="admin")
sess=session.Session(auth=auth)
keystone=client.Client(version="2.0",session=sess)
print keystone.tokens.authenticate(username="admin", tenant_name="admin", password="admin").to_dict()["token"]["id"]