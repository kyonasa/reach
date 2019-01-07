# -*- coding: utf-8 -*-
"""
Created on 2018/11/28 14:48
@author: mengph
reach
check nova,cinder ervcie and neutron agents state
check all node linked state
check ceph health state
check crm:mysql state
check rabbitmq cluster state
IPv6 and Https for keystone public URL are not unsupported
"""
from sshtunnel import SSHTunnelForwarder
import paramiko
import fuel_remote
import json
import threading
import time
import random
import nova_hello
import cinder_hellow
import neutron_hello

fuel_ip="10.121.137.11"
keystone_url_10_1="http://10.121.137.50:5000/v2.0"
keystone_url_10_2="http://10.121.137.80:5000/v2.0"
keystone_url_10_3="http://10.121.137.54:5000/v2.0"
keystone_url_tmp="http://10.121.136.132:5000/v2.0"

result={}
nodes={}
net_linked={}
detail={}
class Nodes(object):
    def __init__(self,name,roles):
        self.name=name
        self.roles=roles
        self.networks={}
        self.linked={}
        self.nova_service=None
        self.neutron_service = None
        self.rabbitmq_service=None

    def show_node(self):
        print "-------------"
        print "name:",self.name
        print "roles: ",self.roles
        print "networks: ",self.networks
        print "linked: ",self.linked
        print "nova_service: ",self.nova_service
        print "neutron_service: ", self.neutron_service
        print "rabbitmq_service: ", self.rabbitmq_service
        print "-------------"

def get_controller_node():
    for node in nodes.values():
        if " controller" in node.roles and node.linked["br-mgmt"]:
            return node.name

def get_nodes():
    cmd = "fuel nodes"
    res = fuel_remote.ssh(fuel_ip, cmd=cmd)
    for i in range(2, len(res)):
        nodes["node-" + res[i].split("|")[0].strip()] = Nodes(name="node-" + res[i].split("|")[0].strip(),roles=res[i].split("|")[6].rstrip().split(","))


def get_keystone_url(fuel_ip,controller_node):
    cmd_get_keystone_url="source /root/openrc && openstack endpoint show keystone -f json"
    tmp=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_get_keystone_url)
    try:
        return json.loads(tmp)["publicurl"]
    except:
        return fuck_trans_stdout_to_correct(tmp)["publicurl"]

def remote_cmd(fuel_ip,node,cmd,port=10022,std="stdout"):

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
    def ssh(ip_addr="127.0.0.1",cmd="",loacl_port=10022,std="stdout"):
        key_path ="/home/mengph/rearch/id_rsa"
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # pkey = paramiko.RSAKey.from_private_key_file(key_path)
        # ssh.connect(hostname=ip_addr, port=loacl_port, username="root", pkey=pkey)
        try:
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            ssh.connect(hostname=ip_addr, port=loacl_port, username="root", pkey=pkey)
        except:
            key_path = fuel_remote.get_ssh_key(fuel_ip)
            pkey = paramiko.RSAKey.from_private_key_file(key_path)
            ssh.connect(hostname=ip_addr, port=loacl_port, username="root", pkey=pkey)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        if std=="stdout":
            return stdout.read()
        elif std=="stderr":
            return [stdout.read(),stderr.read()]


    res=ssh(cmd=cmd,loacl_port=port,std=std)
    # print res
    return res


def get_networks():
    try:
        port=10022
        networks={"br-ex":["10.121.137.254"]}
        cmd_ifconfig="ifconfig"
        for node in nodes.keys():
            try:
                tmp=remote_cmd(fuel_ip=fuel_ip,node=node,cmd=cmd_ifconfig,port=port).split("\n")
            except:
                tmp=""
            br = ""
            ipv4_address = ""
            ipv6_address = ""
            for e in tmp:
                if e.rfind(": ") != -1 and e.rfind("br-") != -1:
                    br = e.split(": ")[0]
                elif e.rfind("inet6") != -1 and e.rfind("global") != -1:
                    ipv6_address = e.split(" ")[9]
                elif e.rfind("inet ") != -1:
                    ipv4_address = e.split(" ")[9]
                elif not e and br:
                    nodes[node].networks[br] = [ipv4_address, ipv6_address]
                    if br in networks:
                        if ipv4_address:
                            networks[br].append(ipv4_address)
                        elif ipv6_address:
                            networks[br].append(ipv6_address)
                        else:
                            networks[br] .append("")
                    else:
                        if ipv4_address:
                            networks[br]=[ipv4_address]
                        elif ipv6_address:
                            networks[br]=[ipv6_address]
                        else:
                            networks[br] =[""]
                    br = ""
                    ipv4_address = ""
                    ipv6_address = ""
        return  networks
    except Exception,error:
        print error
        return {}

def check_nerworks(networks):
    port=10022
    threads=[]
    res=True
    for node in nodes.values():
        net_linked[node]={}
        for network in node.networks.keys():
            net_linked[node][network]={}
            for address in networks[network]:
                if  address:
                    if node.networks[network][0]:
                        cmd_ping="ping %s -c 4" %address
                    else:
                        cmd_ping = "ping -6 %s -c 4" % address
                    # print cmd_ping
                    # _check_linked(fuel_ip, node, cmd_ping, port, network, address)
                    threads.append(threading.Thread(target=_check_linked,args=(fuel_ip,node,cmd_ping,port,network,address)))
                    port+=1
    comp=10
    # for i in range(0,len(threads),comp):
    #     tmp=threads[i:i+comp]
    #     for t in tmp:
    #         t.setDaemon(True)
    #         t.start()
    #     for t in tmp:
    #         # print threading.activeCount()
    #         t.join()
    i=0
    while i < len(threads):
        count = 0
        for t in threads:
            if t.isAlive():
                count+=1
        if count < comp:
            threads[i].setDaemon(True)
            threads[i].start()
            i+=1
    for t in threads:
        t.join()

    for node in nodes.values():
        for network in net_linked[node]:
            tmp=net_linked[node][network].values()
            node.linked[network]=\
                tmp.count(True)==len(net_linked[node][network].keys()) or tmp.count(True)>1
            if node.linked[network]==False:
                res=False
    return res,net_linked

def _check_linked(fuel_ip,node,cmd,port,network,address):
    # print fuel_ip,node,cmd,port,network,address
    for i in range(3):
        try:
            tmp= remote_cmd(fuel_ip=fuel_ip, node=node.name, cmd=cmd, port=port)
            if int(tmp.split("\n")[-3].split(",")[1].strip()[0]) > 0:
                net_linked[node][network][address]=True
            else:
                net_linked[node][network][address] =False
            # print node.name,network,address," linked ",net_linked[node][network][address]
            break
        except:
            t=random.randint(1,4)
            time.sleep(t)
            print node.name,network,address,"connected failed, retry time ",i," retry after ",t," s"
        net_linked[node][network][address] = False


def _check_service_status(servcies,service_name,host,status,state):
    servcie_detail={}
    for service in servcies:
        if getattr(service,host) in servcie_detail:
            servcie_detail[getattr(service,host)][getattr(service,service_name)]=[getattr(service,status),getattr(service,state)]
        else:
            servcie_detail[getattr(service, host)]={getattr(service,service_name):[getattr(service,status),getattr(service,state)]}
    # print servcie_detail
    return servcie_detail


def check_nova_service(keystone_url,admin,password,project):
    try:
        res=True
        nova_client=nova_hello.setup(keystone_url=keystone_url,admin=admin,password=password,project=project)
        nova_services=nova_hello.nova_service(nova_client)
        res_detail=_check_service_status(nova_services,service_name="binary",host="host",status="status",state="state")
        for node in nodes.values():
            if node.name+".domain.tld" in res_detail:
                tmp=res_detail[node.name+".domain.tld"]
                for state in tmp.values():
                    if state[1]!="up":
                        node.nova_service=False
                        res=False
                        break
                    node.nova_service=True
        return res,res_detail
    except Exception,error:
        return False,error

def check_cinder_service(keystone_url,admin,password,project):
    try:
        res=True
        cinder_client=cinder_hellow.setup(keystone_url=keystone_url,admin=admin,password=password,project=project)
        cinder_services=cinder_hellow.cinder_services(cinder_client)
        res_detail=_check_service_status(cinder_services,service_name="binary",host="host",status="status",state="state")
        for tmp in res_detail.values():
            for state in tmp.values():
                if state[1]!="up":
                    res=False
                    break
        return res,res_detail
    except Exception,error:
        return False,error

def check_neutron_agent(keystone_url,admin,password,project):
    try:
        res=True
        agent_detail={}
        neutron_client=neutron_hello.setup(keystone_url=keystone_url,admin=admin,password=password,project=project)
        neutron_agents=neutron_hello.neutron_agents(neutron_client)
        for agent in neutron_agents:
            if agent["host"] in agent_detail:
                agent_detail[agent["host"]][agent["binary"]]=[agent["admin_state_up"],agent["alive"]]
            else:
                agent_detail[agent["host"]]={agent["binary"]:[agent["admin_state_up"],agent["alive"]]}
        for node in nodes.values():
            if node.name+".domain.tld" in agent_detail:
                tmp=agent_detail[node.name+".domain.tld"]
                for state in tmp.values():
                    if not state[1]:
                        node.neutron_service=False
                        res=False
                        break
                    node.neutron_service=True
        return res,agent_detail
    except Exception,error:
        return False,error


def check_ceph(fuel_ip,controller_node):
    try:
        cmd_ceph = "ceph health"
        tmp=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_ceph)[:-1].split(" ")
        if tmp[0]=="HEALTH_OK":
            return True, " ".join(tmp)
        else:
            return False, " ".join(tmp)
    except Exception,error:
        return False,error

def check_crm_status(fuel_ip,controller_node,resource):
    try:
        cmd_crm = "crm resource show %s " %resource
        tmp = remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_crm,std="stderr")
        # print tmp.split("\n")
        if tmp[1]:
            return False,tmp
        else:
            return True,tmp
    except Exception,error:
        return False,error

def check_rabbitmq_status(fuel_ip,controller_node):
    try:
        q=[]
        rabbit_node={}
        cmd_rabbit="rabbitmqctl -q cluster_status"
        tmp=remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_rabbit).replace("<<","[").replace(">>","]")
        # tmp = remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_rabbit)[1:-1].split("\n")
        res=""
        for i,e in enumerate(tmp):
            ree=e
            if e=="[" or e=="{":
                q.append(e)
            elif e=="," and q[-1]=="{":
                ree=":"
            elif e=="]" or e=="}":
                q.pop()
            elif e==" ":
                ree=""
            res+=ree
        for line in res.split("\n"):
            if "running_nodes" in line:
                for node in line[1:-2].split(":")[1][1:-1].split(","):
                   rabbit_node[node[1:-1]]=[True]
            elif "alarms" in line:
                alarms = line[1:-3].split(",")
                for alarm in alarms:
                    for node in rabbit_node:
                        if node in alarm:
                            rabbit_node[node].append(alarm.split(":")[-1][1:-2])
        for node in rabbit_node.keys():
            nodes[node.split("@")[1]].rabbitmq_service=rabbit_node[node]
        for alarm in rabbit_node.values():
            if alarm[1]:
                return False,rabbit_node
        return True,rabbit_node
    except Exception, error:
        return False, error

def fuck_trans_stdout_to_correct(fuck_output):
    d={}
    item=fuck_output[2:-3].split("}, {")
    for line in item:
        tmp= line.split(", ")
        d[tmp[0].split(": ")[1][1:-1]]=tmp[1].split(": ")[1][1:-1]
    return d



def check_env(fuel_ip):
    print time.ctime()
    get_nodes()
    networks = get_networks()
    result["networks"],detail["net_linked"]=check_nerworks(networks)
    detail["networks"]=networks
    controller_node = get_controller_node()
    print controller_node
    # controller_node="node-8"
    keystone_url=get_keystone_url(fuel_ip=fuel_ip,controller_node=controller_node)
    result["rabbitmq_service"], detail["rabbitmq_service"] = check_rabbitmq_status(fuel_ip=fuel_ip,controller_node=controller_node)
    result["mysql_service"], detail["mysql_service"]=check_crm_status(fuel_ip=fuel_ip,controller_node=controller_node,resource="clone_p_mysql")
    result["ceph_health"], detail["ceph_health"] = check_ceph(fuel_ip=fuel_ip, controller_node=controller_node)
    result["nova_service"],detail["nova_service"] = check_nova_service(keystone_url=keystone_url,admin="admin",password="admin",project="admin")
    result["cinder_service"] ,detail["cinder_service"] = check_cinder_service(keystone_url=keystone_url, admin="admin", password="admin", project="admin")
    result["neutron_service"] ,detail["neutron_service"] = check_neutron_agent(keystone_url=keystone_url, admin="admin", password="admin", project="admin")
    for node in nodes.values():
        node.show_node()
    print result
    print detail
    print time.ctime()
    if set(result.values())==set([True]):
        return True
    else:
        return False

if __name__ == '__main__':
    check_env(fuel_ip=fuel_ip)