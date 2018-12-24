# -*- coding: utf-8 -*-
"""
Created on 2018/10/9 13:22
@author: mengph
reach
"""
from freezerclient.v1 import client
from keystoneauth1 import loading,session
from novaclient import client as  nvclient
import paramiko
import json
import time
import MySQLdb
keystone_url_180_11="http://10.121.137.50:5000/v2.0"
keystone_url_180_12="http://10.121.137.80:5000/v2.0"
keystone_url_136_132="https://10.121.136.132:5000/v2.0"
loader=loading.get_plugin_loader('password')
auth=loader.load_from_options(auth_url=keystone_url_180_12,username="admin",password="admin",project_name="admin")
sess=session.Session(auth=auth)
# print sess.auth
freezer=client.Client(version="2.0",session=sess,endpoint_type="public")
# print freezer.endpoint
# print self.check_job("bf805cdd08f3449997e37a12bfcfc6af")
# search={'match': [{u'description': u'ft-config-backup-222'},{ u'job_id': u'3c5092a6520e4fbd9cebc3fec04e978f'}]}
# print freezer.jobs.list(search=search,client_id="node-8")
# print freezer.jobs.get(job_id="3c5092a6520e4fbd9cebc3fec04e978f")[u'job_schedule'][u'result']
def create_job():
    f=open("/home/mengph/rearch/test.json")
    file=json.load(f)
    # print file
    return freezer.jobs.create(doc=file)

def start_job(job_id):
    freezer.jobs.start_job(job_id)

def check_job(job_id):
    while freezer.jobs.get(job_id=job_id)[u'job_schedule']['status']!="completed":
        time.sleep(1)
        # print freezer.jobs.get(job_id=job_id)[u'job_schedule']['status']
    return freezer.jobs.get(job_id=job_id)[u'job_schedule'][u'result']

def ssh(ip_addr):
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip_addr,port=22,username="root",password="passw0rd")
    cmd="ip a"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read()
job_id=create_job()
print check_job(job_id)
# print check_job("a6c883fea435488bac2405ae5cab7569")
# print ssh("10.121.137.10")

# db = MySQLdb.connect("10.121.", "testuser", "test123", "TESTDB", charset='utf8' )