# -*- coding: utf-8 -*-
"""
Created on 2018/7/9 11:57
@author: mengph
reach
"""
from heatclient import client as htclient
from heatclient.common import template_utils
from keystoneauth1 import loading,session
import json
yaml_name="nic_qos.yaml"
keystone_url_200="http://172.16.90.2:5000/v2.0"
keystone_url_180_11="http://10.121.137.51:5000/v2.0"
keystone_url_180_12="http://172.15.50.2:5000/v2.0"
loader=loading.get_plugin_loader('password')
auth=loader.load_from_options(auth_url=keystone_url_180_11,username="admin",password="admin",project_name="admin")
sess=session.Session(auth=auth)
heat=htclient.Client(version="1",session=sess)
events=heat.events.list(stack_id=yaml_name)
event_s={}
events_s={}
for event in events:

     event_s['event_time']=event.to_dict()['event_time']
     event_s['resource_status'] = event.to_dict()['resource_status']
     event_s['resource_status_reason'] = event.to_dict()['resource_status_reason']
     events_s[event.to_dict()["resource_name"]]=event_s
print events_s
print heat.stacks.get(stack_id=yaml_name, resolve_outputs=True).to_dict()["stack_status"]
