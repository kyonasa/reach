# -*- coding: utf-8 -*-
"""
Created on 2018/6/12 17:28
@author: mengph
reach
"""

from subprocess import Popen, PIPE
import os,sys
import paramiko
import MySQLdb
def getIfconfig():
    u'''
    返回服务器ip信息
    :return:
    '''
    p = Popen(['ifconfig'], stdout = PIPE)
    data = p.stdout.read()
    return data

def getCpu():
    u'''
    返回服务器cpu信息
    :return:
    '''
    num = 0
    with open('/proc/cpuinfo') as fd:
        for line in fd:
            if line.startswith('processor'):
                num += 1
            if line.startswith('model name'):
                cpu_model = line.split(':')[1].strip().split()
                cpu_model = cpu_model[0] + ' ' + cpu_model[2]  + ' ' + cpu_model[-1]
    return {'cpu_num':num, 'cpu_model':cpu_model}


def get_ssh_key(host):
    try:
        local_path="/home/mengph/rearch/id_rsa"
        t=paramiko.Transport(host,22)
        t.connect(username="root",password="passw0rd")
        sftp=paramiko.SFTPClient.from_transport(t)
        sftp.get("/root/.ssh/id_rsa",local_path)
        t.close()
        os.popen("chmod 600 "+local_path)
        return local_path
    except Exception,e:
        print e

def ssh(ip_addr,cmd):
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip_addr,port=22,username="root",password="passw0rd")
    except paramiko.ssh_exception.BadAuthenticationType:
        key_path=get_ssh_key("10.121.137.12")
        print key_path
        pkey=paramiko.RSAKey.from_private_key_file(key_path)
        ssh.connect(hostname=ip_addr, port=22, username="root", pkey=pkey)


    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read()
#
# print get_ssh_key("10.121.137.12")
print ssh("10.121.137.81",cmd="source /root/openrc && nova list")
# db = MySQLdb.connect("10.121.", "testuser", "test123", "TESTDB", charset='utf8' )