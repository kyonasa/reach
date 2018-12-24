# -*- coding: utf-8 -*-
"""
Created on 2018/6/13 18:49
@author: mengph
reach
"""
from neutronclient import client as  nuclient
from novaclient import client as  nvclient
from novaclient import base
from keystoneauth1 import loading,session
keystone_url_200="http://172.16.90.2:5000/v2.0"
keystone_url_10_1="https://10.121.137.50:5000/v2.0"
keystone_url_10_2="https://10.121.137.80:5000/v2.0"
keystone_url_180_3="http://172.15.50.2:5000/v2.0"
keystone_url_tmp="http://10.121.136.132:5000/v2.0"
def setup(keystone_url=keystone_url_10_2,admin="admin",password="admin",project="admin"):
    loader=loading.get_plugin_loader('password')
    auth=loader.load_from_options(auth_url=keystone_url,username=admin,password=password,project_name=project)
    sess=session.Session(auth=auth,verify=False)
    nova=nvclient.Client(version="2.1",session=sess)
    neutron=nuclient.HTTPClient(session=sess)
    return nova
# print neutron.list_networks()['networks']
# nova=Client(version="2.1",username="admin@exaple.org",password="admin",project_id="f3bf3b87226c431f9b28a369d47b7730",auth_url="http://172.16.80.2:8774/v2.1")
# print nova.servers.list()[0].status

def nova_service(nova_client):
    nova_service=nova_client.services.list()
    return nova_service

def server_list(nova_client):
    servers=nova_client.servers.list()
    return servers


if __name__ == '__main__':
    nova=setup(keystone_url=keystone_url_10_1)
    print server_list(nova)
    uuid=base.getid()
    print uuid
    instance=nova.servers.get(uuid)
    print getattr(instance,"OS-EXT-SRV-ATTR:hypervisor_hostname",None)
    # print nova.servers.get_vnc_console("68782865-405b-4feb-8d32-d766a9474885","novnc")

