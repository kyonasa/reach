# -*- coding: utf-8 -*-
"""
Created on 2018/6/19 10:41
@author: mengph
reach
"""

from cinderclient import base
from cinderclient import client
from keystoneauth1 import loading,session
loader=loading.get_plugin_loader('password')
auth=loader.load_from_options(auth_url="http://172.15.60.3:5000/v2.0",username="admin",password="admin",project_id="fbd24f11b4664aa4884e6079be1195f1")
sess=session.Session(auth=auth)
cinder=client.Client(version="2.0",session=sess)



try:
    type1=cinder.volume_types.list()[0]
    cinder.volume_types.delete(type1)
    # cinder.volume_types.delete(volume_type="cmcc2")
except IndexError,e:
    print e.message

try:
    qos1=cinder.qos_specs.list()[0]
    cinder.qos_specs.delete(qos1)
    # cinder.volume_types.delete(volume_type="cmcc2")
except IndexError,e:
    print e.message