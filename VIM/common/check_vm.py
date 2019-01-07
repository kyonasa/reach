# -*- coding: utf-8 -*-
"""
Created on 2018/11/26 16:21
@author: mengph
reach
"""

import  json
from fuel_remote import ssh
fuel_ip="10.121.138.100"
nodes = {}
vm_name="fxg"
import paramiko
import psycopg2
import yaml
import logging
from sshtunnel import SSHTunnelForwarder
import fuel_remote
import xmltodict
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt = '%Y-%m-%d  %H:%M:%S %a',
                    filename=r"/var/log/mengph_check_vm.log"
                    )
result = {}

def remote_cmd(fuel_ip,node,cmd):

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

    @ssh_tunnel(jump_host=fuel_ip,remote_host=node,bind_port=10022)
    def ssh(ip_addr="127.0.0.1",cmd=""):
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_path = fuel_remote.get_ssh_key(fuel_ip)
        pkey = paramiko.RSAKey.from_private_key_file(key_path)
        ssh.connect(hostname=ip_addr, port=10022, username="root", pkey=pkey)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read()
        err = stderr.read()
        if err:
            print err
        return out

    res=ssh(cmd=cmd)
    # print res
    return res


def get_nodes():
    cmd = "fuel nodes"
    res = ssh(fuel_ip, cmd=cmd)
    for i in range(2, len(res)):
        nodes["node-" + res[i].split("|")[0].strip()] = res[i].split("|")[6].rstrip().split(",")

def get_controller_node():
    for node in nodes.keys():
        if " controller" in nodes[node]:
            return node

class NetWork(object):
    def __init__(self,name,address):
        self.name=name
        self.address=address
        self.uuid=None
        self.netns=None
        self.linked=None
    def check_result(self):
        print "-----------"
        print self.name
        print self.address
        print self.uuid
        print self.netns
        print self.linked
        print "-----------"

def check_network(fuel_ip,networks,controller_node,ex_cmd=[]):
    network_info={}
    ex=[]
    try:
        for network in networks:
            network_info[network.split("=")[0].strip()]=NetWork(network.split("=")[0].strip(),network.split("=")[1].strip().split(",")[0])
    except Exception,error:
        print error,"location: check_network"
        return error,"location: check_network"
    for network in network_info.keys():
        cmd_show_network="source /root/openrc && openstack network show %s -f json" %network
        # print fuel_ip,controller_node
        tmp_res=remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_show_network)
        try:
            json.loads(tmp_res)["id"]
            network_infos=json.loads(tmp_res)
        except:
            network_infos=fuck_trans_stdout_to_correct(tmp_res)
        network_info[network].uuid=network_infos["id"]
        network_info[network].netns = "qdhcp-"+network_infos["id"]
        if ":" in  network_info[network].address and "." not in network_info[network].address:
            cmd_ping_vm = "ip netns exec %s ping -6 %s -c 4" % (network_info[network].netns, network_info[network].address)
        elif "." in  network_info[network].address and ":" not in network_info[network].address:
            cmd_ping_vm="ip netns exec %s ping %s -c 4" %(network_info[network].netns,network_info[network].address)
        print cmd_ping_vm
        tmp=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_ping_vm)
        print tmp
        logging.info(tmp)
        network_info[network].linked= int(tmp.split("\n")[-3].split(",")[1].strip()[0])>0
        if network_info[network].linked and ex_cmd:
            for cmd in ex_cmd[1]:
                cmd_ex="ip netns exec %s ssh -i %s centos@%s "%(network_info[network].netns,ex_cmd[0],network_info[network].address)+cmd
                print cmd_ex,controller_node
                logging.info(cmd_ex)
                for i in range(3):
                    ex_res=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_ex)
                    print ex_res
                    if ex_res:
                        ex.append(ex_res)
                        break

    res=True
    for network in network_info.keys():
        res=res and network_info[network].linked
        network_info[network].check_result()
    return res,ex


def check_in_host(fuel_ip,compute_node,instance_name):
    cmd_virsh_check="virsh list | grep %s" %instance_name
    cmd_virsh_dumpxml="virsh dumpxml %s" %instance_name
    try:
        res=remote_cmd(fuel_ip=fuel_ip,node=compute_node,cmd=cmd_virsh_check).split(" ")
        vm_xml=remote_cmd(fuel_ip=fuel_ip,node=compute_node,cmd=cmd_virsh_dumpxml)
    except Exception, error:
        print error,"location:vm_check in host"
        logging.error(error)
        return "error","error"
    tmp=[]
    for e in res:
        if e!="":
            tmp.append(e)
    return tmp[2][:-1],vm_xml


def set_reult(server):
    result["status"] = server["OS-EXT-STS:vm_state"]
    result["instance_name"] = server["OS-EXT-SRV-ATTR:instance_name"]
    try:
        result["host"] = server["OS-EXT-SRV-ATTR:hypervisor_hostname"].split(".")[0]
    except AttributeError:
        result["host"]=None

def fuck_trans_stdout_to_correct(fuck_output):
    d={}
    item=fuck_output[2:-3].split("}, {")
    for line in item:
        tmp= line.split(", ")
        d[tmp[0].split(": ")[1][1:-1]]=tmp[1].split(": ")[1][1:-1]
    return d



def check_vm(fuel_ip,vm_name,ex_cmd=[],controller_node=""):
    cmd_show_vm="source /root/openrc && openstack server show %s -f json" %vm_name
    if not controller_node:
        get_nodes()
        controller_node=get_controller_node()
    # controller_node="node-3"
    try:
        tmp_res=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_show_vm)
        try:
            json.loads(tmp_res)["status"]
            server=json.loads(tmp_res)
        except:
            server=fuck_trans_stdout_to_correct(tmp_res)
    except ValueError:
        result["status"]=None
        result["instance_name"]=None
        result["host"]=None
        result["all_network_linked"]=None
        result["virsh_status"]=None
        result["ex"]="vm not in env"
        result["vm_xml"]=None
        return result
    set_reult(server=server)
    network=server["addresses"].split(";")
    # print network
    print "check network"
    result["all_network_linked"],result["ex"]=check_network(fuel_ip=fuel_ip,networks=network,controller_node=controller_node,ex_cmd=ex_cmd)
    print "check host"
    result["virsh_status"],result["vm_xml"]=check_in_host(fuel_ip=fuel_ip,compute_node=result["host"],instance_name=result["instance_name"])
    return result


if __name__ == '__main__':
    r=check_vm(fuel_ip=fuel_ip,vm_name=vm_name,ex_cmd=["/root/cyborg_key.priv",["uname -a"]],controller_node="node-3")
    print r
    logging.info(r)
    tmp=xmltodict.parse( r["vm_xml"])
    # print tmp["domain"]["devices"]["hostdev"]["source"]["address"]
    print tmp["domain"]["devices"]["disk"][1]["alias"]["@name"]