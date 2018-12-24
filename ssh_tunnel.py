# -*- coding: utf-8 -*-
"""
Created on 2018/11/27 10:03
@author: mengph
reach
"""
import paramiko
import psycopg2
from sshtunnel import SSHTunnelForwarder
import fuel_remote
import glance_hello
import time
import  json
import xmltodict
import threading

def remote_cmd(fuel_ip,node,cmd,bind_port=10022):

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

    @ssh_tunnel(jump_host=fuel_ip,remote_host=node,bind_port=bind_port)
    def ssh(ip_addr="127.0.0.1",cmd="",local_port=10022):
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_path = "/home/mengph/rearch/id_rsa"
        key_path = fuel_remote.get_ssh_key(fuel_ip)
        # print key_path
        pkey = paramiko.RSAKey.from_private_key_file(key_path)
        ssh.connect(hostname=ip_addr, port=local_port, username="root", pkey=pkey)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # print stdout.read()
        return stdout.read()

    res=ssh(cmd=cmd,local_port=bind_port)
    return res

def remote_sql(fuel_ip,node,db,cmd):
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

    @ssh_tunnel(jump_host=fuel_ip, remote_host=node, bind_port=10022)
    def sql(ip_addr="127.0.0.1",db="",cmd=""):
        conn=psycopg2.connect(database=db,
                              user="root",
                              password="",
                              host=ip_addr,
                              port=10022
                              )
        print conn
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchone()
        print(rows)
        conn.close()
    sql(db=db,cmd=cmd)

def ssh_tunnel(jump_host,remote_host,bind_port):
    def outter_warpper(func):
        def wrapper(*args,**kwargs):
            with SSHTunnelForwarder(
                    (jump_host, 22),
                    ssh_username="root",
                    ssh_password="passw0rd",
                    remote_bind_address=(remote_host, 5000),
                    local_bind_address=("fd00:dead:beef:10::2", bind_port)
            ) as tunnel:
                return func(*args,**kwargs)
        return  wrapper
    return outter_warpper



@ssh_tunnel(jump_host="10.121.137.11",remote_host="node-8",bind_port=5000)
def glance_setup_v6(url):
    glance=glance_hello.setup(url=url)
    return glance

@ssh_tunnel(jump_host="10.121.137.11",remote_host="node-8",bind_port=5000)
def glance_get_image_v6(images_client,name="centos"):
    image=glance_hello.image_get(images_client=images_client,name=name)
    return image

url="http://127.0.0.1:5000/v2.0"

glance_client=glance_setup_v6(url)
print glance_client
print glance_get_image_v6(images_client=glance_client,name="TestVM")











# remote_sql(fuel_ip="10.121.137.12",node="node-57",db="vimops",cmd="show tables;")
#
# count=[]
# def fuck_off(fuel_ip,node,cmd_ping,port):
#     tmp= remote_cmd(fuel_ip=fuel_ip, node=node, cmd=cmd_ping, bind_port=port)
#     # print tmp
#     # time.sleep(1)
#     if int(tmp.split("\n")[-3].split(",")[1].strip()[0]) > 0:
#         count.append(True)
#     else:
#         count.append( False)
#
# nodes={"node-3":"","node-4":"","node-5":"","node-1":"","node-2":""}
# nodes={"node-10":"","node-11":"","node-12":""}
# cmd_sql=" << eeooff mysql use vimops;  eeooff"
# tmp=[]
# fuel_ip="10.121.137.11"
# port=10022
#
# cmd_show_vm="source /root/openrc && openstack server show IOE-1 -f json"


