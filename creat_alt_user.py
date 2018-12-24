# -*- coding: utf-8 -*-
"""
Created on 2018/7/10 17:33
@author: mengph
reach
"""
from keystoneauth1 import loading,session
from keystoneclient import client
from keystoneclient import base
from keystoneclient import exceptions
keystone_url_200="http://172.16.90.2:5000/v2.0"
keystone_url_180_2="http://172.15.60.2:5000/v2.0"
keystone_url_180_3="http://172.15.50.2:5000/v2.0"
keystone_url_108="http://172.16.80.3:5000/v2.0"
loader=loading.get_plugin_loader('password')
auth=loader.load_from_options(auth_url=keystone_url_108,username="admin",password="admin",project_name="admin")
sess=session.Session(auth=auth)
keystone=client.Client(version="2.0",session=sess)
try:
    tenant_mengph=keystone.tenants.create(tenant_name="mengph", description=None, enabled=True)
except:
    print "tenant has already exist"
else:
    print "tenant mengph created successful"
try:
    keystone.users.create(name="mengph", password="mengph", email="mengph@chinaunicom.cn",
               tenant_id=base.getid(tenant_mengph), enabled=True)
except:
    print "user has already exist"
else:
    print "user mengph created successful"
try:
    keystone.users.create(name="zhangy", password="zhangy", email="zhangy@chinaunicom.cn",
               tenant_id=base.getid(tenant_mengph), enabled=True)
except:
    print "user has already exist"
else:
    print "user mengph created successful"
