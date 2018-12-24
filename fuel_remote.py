# -*- coding: utf-8 -*-
"""
Created on 2018/11/15 16:09
@author: mengph
reach
"""
import paramiko
import os

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


def scp(host,src_path,dst_path,fun="download"):
    print src_path,dst_path
    try:
        t=paramiko.Transport(host,22)
        t.connect(username="root",password="passw0rd")
        sftp=paramiko.SFTPClient.from_transport(t)
        if fun=="download":
            sftp.get(src_path,dst_path)
        elif fun=="upload":
            sftp.put(src_path,dst_path)
        t.close()
        return True
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
    return stdout.readlines()

if __name__ == '__main__':
    ssh("10.121.137.12","python /root/fuel_config.py download")
    if scp("10.121.137.12","/home/mengph","/home/mengph/env_12/"):
        print os.popen("ls "+"/home/mengph/env_12/").readlines()

