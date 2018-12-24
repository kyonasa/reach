# -*- coding: utf-8 -*-
"""
Created on 2018/6/25 10:31
@author: mengph
reach
"""
import yaml
from heatclient import client as htclient
from heatclient.common import template_utils
from keystoneauth1 import loading,session
yaml_name="nic_qos.yaml"
keystone_url_200="http://172.16.90.2:5000/v2.0"
keystone_url_180_11="http://10.121.137.50:5000/v2.0"
keystone_url_180_12="http://10.121.137.80:5000/v2.0"
keystone_url_136_132="http://10.121.136.132:5000/v2.0"
loader=loading.get_plugin_loader('password')
auth=loader.load_from_options(auth_url=keystone_url_180_11,username="admin",password="admin",project_name="admin")
sess=session.Session(auth=auth,verify=False)
heat=htclient.Client(version="1",session=sess)
files,template=template_utils.process_template_path(yaml_name)
heat_parameters = open(yaml_name)
# temp_params = yaml.load(heat_parameters)
# heat_parameters.close()ls

# print files,template
# print temp_params["parameters"]
# heat.stacks.create(stack_name="cmcc", template=template, parameters=temp_params["parameters"], files=files)
heat.stacks.create(stack_name=yaml_name, template=template, files=files)
print heat.stacks.list()