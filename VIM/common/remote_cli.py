# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 14:22
@author: mengph
reach
"""
from sshtunnel import SSHTunnelForwarder
import paramiko
import os


def remote_cmd(fuel_ip,node,cmd,port=10022,std=""):
    '''this function was designed for type a cli command in remote host.
    and using an ssh tunnel for the case when remote host can,t login directly, must using an middle machine.
    input was middle machine(fuel_ip), remote host(node), port of middle machine and the cmd you want
    you can chosie std arg to switch the cmd output from stdout ,stderr .if null, means return stdout or stderr when stdout was null'''
    def ssh_tunnel(jump_host,remote_host,bind_port):
        def outter_warpper(func):
            def wrapper(*args,**kwargs):
                with SSHTunnelForwarder(
                        (jump_host, 22),
                        ssh_username="root",
                        ssh_password="passw0rd",
                        remote_bind_address=(remote_host, 22),
                        local_bind_address=("0.0.0.0", bind_port)
                ) as tunnel:
                    return func(*args,**kwargs)
            return  wrapper
        return outter_warpper

    @ssh_tunnel(jump_host=fuel_ip,remote_host=node,bind_port=port)
    def ssh(ip_addr="127.0.0.1",cmd="",loacl_port=10022,std=""):
        key_path ="/home/mengph/rearch/id_rsa"
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            ssh.connect(hostname=ip_addr, port=loacl_port, username="root", pkey=pkey)
        except:
            key_path = get_ssh_key(fuel_ip)
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            ssh.connect(hostname=ip_addr, port=loacl_port, username="root", pkey=pkey)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        if std=="stdout":
            return stdout.read()
        elif std=="stderr":
            return [stdout.read(),stderr.read()]
        elif not std :
            out=stdout.read()
            err=stderr.read()
            if err:
                print err
            return out


    res=ssh(cmd=cmd,loacl_port=port,std=std)
    # print res
    return res

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