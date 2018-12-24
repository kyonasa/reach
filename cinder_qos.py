# -*- coding: utf-8 -*-
"""
Created on 2018/6/15 16:34
@author: mengph
reach
"""
from freezerclient.v1.client import Client
from cinderclient import base
from cinderclient import client
from keystoneauth1 import loading,session
keystone_url_180_11="http://10.121.137.50:5000/v2.0"
keystone_url_180_12="http://10.121.137.80:5000/v2.0"
keystone_url_136_132="https://10.121.136.132:5000/v2.0"
loader=loading.get_plugin_loader('password')
auth=loader.load_from_options(auth_url=keystone_url_180_12,username="admin",password="admin",project_name="admin")
sess=session.Session(auth=auth)
cinder=client.Client(version="2.0",session=sess)
spec1={
    "total_iops_sec":"2000"
}
spec2={
    "total_bytes_sec":"2048000"
}
consumer1="front-end"
consumer2="back-end"
qos1=cinder.qos_specs.create(name="high_read_low_write",specs=spec1,consumer=consumer1)
qos2=cinder.qos_specs.create(name="read_write",specs=spec2,consumer=consumer1)
type1=cinder.volume_types.create(name="cmcc3",description="iops")
type2=cinder.volume_types.create(name="cmcc4",description="bw")
tspec1={
    "volume_backend_name":"DEFAULT"
}
tspec2={
    "volume_backend_name":"DEFAULT"
}
type1.set_keys(tspec1)
type2.set_keys(tspec2)
q_a_t1=cinder.qos_specs.associate(qos1,base.getid(type1))
q_a_t2=cinder.qos_specs.associate(qos2,base.getid(type2))

volume1=cinder.volumes.create(name="cmcc3",size=10,volume_type=base.getid(type1),availability_zone="nova")
volume2=cinder.volumes.create(name="cmcc4",size=10,volume_type=base.getid(type2),availability_zone="nova")

# def set_qos(cinder,""):