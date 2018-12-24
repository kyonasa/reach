# -*- coding: utf-8 -*-
"""
Created on 2018/12/4 11:01
@author: mengph
reach
"""
from sshtunnel import SSHTunnelForwarder
import paramiko
import fuel_remote
import json
from check_vm import check_vm
import glance_hello
import xmltodict
import time
nodes = {}
fuel_ip="10.121.137.11"
'''fuel_ip means witch env you want to test'''

devices={}
'''devices is a dict to record acc_device in all env,the key was uuid and the value was device obj'''

devices_type_dict={"Co-processor":"hw:accelerator_device=Co-processor:",
                    "FPGA":"hw:accelerator_device=FPGA:"
                   }
''' this dict was shown the relationship of acc_device's type in cyborg and the value in flavor extra spec'''

device_type_in_host={
    "Co-processor": "Co-processor",
    "FPGA":"Memory controller"
}
'''this dict was shown the relationship of acc_device's type in cyborg and the type in host or a vm,mainly in the case we use "lspci" to check the device'''

result={}
'''result record a summary of this test script result'''

firmware_url="http://10.121.136.222/Lenovo_thinkcloud_shell_role_20181213_015432.shr"
firmware_uuid=""


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
            key_path = fuel_remote.get_ssh_key(fuel_ip)
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


def get_controller_node():
    '''this function check nodes list to choise an compute host'''
    for node in nodes.values():
        if " controller" in node.roles :
            return node.name

def get_nodes():
    '''thie function login the fuel host to get all host information of env, and return a dict.
    the key was the host name and the value was a node obj'''
    cmd = "fuel nodes"
    res = fuel_remote.ssh(fuel_ip, cmd=cmd)
    for i in range(2, len(res)):
        nodes["node-" + res[i].split("|")[0].strip()] = Nodes(name="node-" + res[i].split("|")[0].strip(),roles=res[i].split("|")[6].rstrip().split(","))


class Nodes(object):
    '''record node information as below'''
    def __init__(self,name,roles):
        self.name=name
        self.roles=roles
        self.networks={}
        self.linked={}
        self.nova_service=None
        self.neutron_service = None
        self.rabbitmq_service=None
        self.devices={}

    def show_node(self):
        print "-------------"
        print "name:",self.name
        print "roles: ",self.roles
        print "networks: ",self.networks
        print "linked: ",self.linked
        print "nova_service: ",self.nova_service
        print "neutron_service: ", self.neutron_service
        print "rabbitmq_service: ", self.rabbitmq_service
        print "devices: ",self.devices
        print "-------------"

class Device(object):
    '''record device information as below'''
    def __init__(self,uuid,pci_address,type,host):
        self.uuid=uuid
        self.pci_address=pci_address
        self.type=type
        self.host=host
        self.state=True
        self.ex=None

    def show_device(self):
        print "-------------"
        print "uuid:",self.uuid
        print "pci_address: ",self.pci_address
        print "type: ",self.type
        print "host: ",self.host
        print "state: ",self.state
        print "ex: ",self.ex
        print "-------------"

def tearDown(fuel_ip,controller_node,firmware_uuid):
    '''after test,clean all vm ,flavor ,keypair that used in case, not include image'''
    flavor="cyborg"
    name="cyborg-copro"
    keypair="cyborg_key"
    cmd_delete_flavor="source /root/openrc && nova flavor-delete %s" %flavor
    cmd_delete_vm="source /root/openrc && nova delete %s" %name
    cmd_delete_keypair="source /root/openrc && openstack keypair delete %s"%keypair
    cmd_delete_keypath="rm -rf /root/cyborg_key.priv"
    cmd_delete_firmware="source /root/openrc && glance image-delete %s"%firmware_uuid
    print cmd_delete_firmware
    try:
        remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_delete_flavor)
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_vm)
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_keypair)
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_keypath)
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_delete_firmware)
        print "env_cleaned",time.ctime()
    except Exception, error:
        print error,"location: clean up"

def _create_priv_key(fuel_ip,controller_node):
    '''fucntion for create an openstack keypair for test vm'''
    key="cyborg_key"
    key_path = "/root/cyborg_key.priv"
    cmd_create_priv_key="source /root/openrc && openstack keypair create %s > %s" %(key,key_path)
    cmd_chmod=" chmod 600 %s" %key_path
    try:
        remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_priv_key)
        remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_chmod)
        return [key,key_path]
    except Exception, error:
        print error
        return False


def get_keystone_url(fuel_ip,controller_node):
    '''get the keystone endpoint from controller node, so need get controller node first ,return the env's keystone publicurl'''
    cmd_get_keystone_url="source /root/openrc && openstack endpoint show keystone -f json"
    tmp=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_get_keystone_url)
    try:
        return json.loads(tmp)["publicurl"]
    except:
        return fuck_trans_stdout_to_correct(tmp)["publicurl"]

def create_image(fuel_ip,controller_node,image_url="http://10.121.136.222/centos6.8_gb.qcow2",keystone_url=""):
    '''ensure the image we need was active in glance. when the image was not ready, create an image instead of '''
    image_name="centos6.8"
    image=[]
    try:
        image=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
        print image
    except Exception, error:
        print error
    if not image:
        try:
            _create_image(fuel_ip=fuel_ip, controller_node=controller_node, image_name=image_name, image_url=image_url)
            time.sleep(5)
            image=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
            print image
        except Exception, error:
            print error
            return False
    times=0
    while image and image[0]['status']!="active" and times<=30:
        time.sleep(5)
        try:
            image=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name=image_name,keystone_url=keystone_url)
            print image
        except Exception, error:
            print error
        times+=1
    if image[0]['status']!="active":
        return False
    else:
        return True



def _create_image(fuel_ip,controller_node,image_name,image_url):
    '''create an image from url'''
    cmd_create_image = "source /root/openrc && glance image-create --name %s --copy-from %s --disk-format qcow2 --container-format bare  --progress" %(image_name,image_url)
    print cmd_create_image
    print remote_cmd(fuel_ip=fuel_ip, node=controller_node, cmd=cmd_create_image)



def _check_image(fuel_ip,controller_node,image_name="cyborg_image",keystone_url=""):
    '''check the status of image '''
    try:
        glance_client=glance_hello.setup(keystone_url)
        image=glance_hello.image_get(glance_client,name=image_name)
        image["id"]
        print "fuckoff"
        if image:
            return image
        else:
            return []
    except Exception,error:
        print error,"location: check_image"
        cmd_check_image="source /root/openrc && openstack image show %s -f json" %image_name
        image=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_image)
        if not image:
            return []
        try:
            json.loads(image)["id"]
            return [json.loads(image)]
        except:
            return [fuck_trans_stdout_to_correct(image)]

def _create_vm_cli(fuel_ip,controller_node,image="centos6.8",flavor="cyborg",network="share_net",SG="default",AZ="nova",name="cyborg-copro",key="cyborg_key"):
    '''create a vm with cli ,return the vm's information as a dict '''
    cmd_create_vm="source /root/openrc && nova boot --image %s --flavor %s --nic net-name=%s --config-drive True --key-name %s  --security-groups %s --availability-zone %s %s" \
                  %(image,flavor,network,key,SG,AZ,name)
    cmd_check_vm="source /root/openrc && openstack server show %s -f json" %name
    try:
        print cmd_create_vm
        print remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_vm)
    except Exception, error:
        print error
    finally:
        tmp_res=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_vm)
        try:
            json.loads(tmp_res)["id"]
            return json.loads(tmp_res)
        except:
            return fuck_trans_stdout_to_correct(tmp_res)

def _create_flavor_cli(fuel_ip,controller_node,spec=["hw:accelerator_device=Co-processor:1"]):
    '''create a flavor you want ,even can set the extra spec, return the flavor infor as a dict'''
    flavor="cyborg"
    cmd_create_flavor="source /root/openrc && nova flavor-create %s auto 4096 20 4" %flavor
    cmd_check_flavor="source /root/openrc && openstack flavor show %s -f json" %flavor
    try:
        if remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_create_flavor):
            for item in spec:
                cmd_set_flavor_spec = "source /root/openrc && openstack flavor set %s --property %s" % (flavor, item)
                print cmd_set_flavor_spec
                remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_set_flavor_spec)
    except Exception, error:
        print error
    finally:
        tmp_res=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_flavor)
        try:
            json.loads(tmp_res)["id"]
            return json.loads(tmp_res)
        except:
            return fuck_trans_stdout_to_correct(tmp_res)

def check_cli_deployables_attach_vm(fuel_ip,controller_node,devices_type=[["Co-processor",2]]):
    '''this function get many sub_function together to check cyborg can create a vm with acc_device correctly'''
    device_in_host_res=True
    spec=[]
    for type in devices_type:
        spec.append(devices_type_dict[type[0]]+str(type[1]))
    print spec
    '''when multi device need to attach to vm'''
    try:
        '''try to create a vm with the key-pair and the flavor we create'''
        key=_create_priv_key(fuel_ip=fuel_ip,controller_node=controller_node)
        if key:
            flavor=_create_flavor_cli(fuel_ip=fuel_ip,controller_node=controller_node,spec=spec)
            print flavor
        vm=_create_vm_cli(fuel_ip=fuel_ip,controller_node=controller_node,flavor=flavor["name"],key=key[0],image="centos6.8")
        print vm
        print time.ctime()
    except Exception, error:
        vm={"name":""}
        print error,"loaction:create vm"
    cmd_check_device_in_vm=[]
    '''cmd using inner a vm'''
    type_num=[]
    for type in devices_type:
        cmd_check_device_in_vm.append("sudo lspci | grep \"%s\"" %device_type_in_host[type[0]])
        type_num.append(type[1])
    time.sleep(20)
    for i in range(7):
        try :
            time.sleep(5)
            r=check_vm(fuel_ip=fuel_ip,vm_name=vm["name"],ex_cmd=[key[1],cmd_check_device_in_vm])
            '''check vm status include network and using cmd inner the vm to check the pci device was attched weather or not '''
            print r
            print "check_time: %d" %i
            if  r["ex"]:
                '''r["ex] was the result of inner cmd, it mainly record the pci_device information inner the vm'''
                device_in_host=[]
                '''check the every type of acc_deice'numbers'''
                for i,type in enumerate(r["ex"]):
                    device_in_host.append(type.strip().split("\n"))
                    if len(device_in_host[-1])!=type_num[i]:
                        device_in_host_res=False
                '''check the virsh xml infor for the vm ,check the pci_address information'''
                tmp=xmltodict.parse( r["vm_xml"])["domain"]["devices"]["hostdev"]
                res=[]
                try:
                    pci_address = tmp["source"]["address"]
                    res.append([r["host"], pci_address["@bus"] + pci_address["@slot"] + pci_address["@function"]])
                except:
                    for t in tmp:
                        pci_address=t["source"]["address"]
                        res.append([r["host"],pci_address["@bus"]+pci_address["@slot"]+pci_address["@function"]])
                return device_in_host_res ,[device_in_host,res]
        except Exception, error:
            print error,"location: check_vm"
    return False,[]


def check_cli_cyborg_deployables_list(fuel_ip,controller_node,devices_type_list=devices_type_dict.keys()):
    '''check the cyborg acc_device list information was correct or not
    compared the cyborg cmd output and every host lspci output'''
    res=True
    cmd_cyborg_deployables_list = "source /root/openrc && cyborg deployables-list"
    tmp = remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_cyborg_deployables_list).split("\n")[3:-2]
    print tmp
    '''put cyborg output information to devices dict and node dict'''
    for device in tmp:
        tmp_device=device.split("|")
        devices[tmp_device[1].strip()]=Device(tmp_device[1].strip(),tmp_device[4].strip(),tmp_device[3].strip(),tmp_device[5].strip().split(".")[0])
        if tmp_device[3].strip() in nodes[tmp_device[5].strip().split(".")[0]].devices:
            nodes[tmp_device[5].strip().split(".")[0]].devices[tmp_device[3].strip()][(":".join(tmp_device[4].strip().split(":")[1:-1])+"."+tmp_device[4].strip().split(":")[-1])]=tmp_device[1].strip()
        else:
            nodes[tmp_device[5].strip().split(".")[0]].devices[tmp_device[3].strip()]={(":".join(tmp_device[4].strip().split(":")[1:-1])+"."+tmp_device[4].strip().split(":")[-1]):tmp_device[1].strip()}
    err = 0
    '''check every node's acc_device information with lspci cmd , and create an dict named validted_devices to record the information'''
    for node in nodes.values():
        cmd_lspci="lspci"
        validated_devices={}
        tmp=remote_cmd(fuel_ip=fuel_ip,node=node.name,cmd=cmd_lspci).split("\n")
        for line in tmp:
            if  line:
                tmp_ex=line.split(": ")[1]
                tmp_line=line.split(": ")[0].split(" ")
                if " ".join(tmp_line[1:]) in validated_devices:
                    validated_devices[" ".join(tmp_line[1:])][tmp_line[0]]=tmp_ex
                else:
                    validated_devices[" ".join(tmp_line[1:])]={tmp_line[0]:tmp_ex}
        '''compare the information in node and validated_devices'''
        for type in devices_type_list:
            try:
                validated_device_addresses= set(validated_devices[device_type_in_host[type]].keys())
            except:
                validated_device_addresses = set()
            try:
                node_device_addresses= set(node.devices[type].keys())
            except:
                node_device_addresses=set()
            for address in node_device_addresses:
                try :
                    validated_device_addresses.remove(address)
                except:
                    err_device=devices[node.devices[type][address]]
                    err_device.state = False
                    err_device.ex = "Device not in host"
                    res=False
            for address in validated_device_addresses:
                err_device_name=validated_devices[device_type_in_host[type]][address]+"-"+str(err)
                if "Xi" in err_device_name or ("QAT" in err_device_name and "Virtual Function" in err_device_name):
                    devices[err_device_name]=(Device(err_device_name,address,type,node.name))
                    err_device=devices[err_device_name]
                    err_device.state=False
                    err_device.ex="Device not in database"
                    res=False
                    err+=1
    return res

def check_acc_status(fuel_ip,controller_node,result):
    '''check the cyborg deployment-show cmd compare the output with attachment information from vm xml '''
    acc_address=[]
    acc_uuid=[]
    pci_address= result["attach_to_vm_detail"][1]
    res=True
    for adress in pci_address:
        tmp=adress[1].split("0x")
        acc_address.append([adress[0],"0000:"+":".join(tmp[1:])])
        for device in devices.values():
            if device.pci_address==acc_address[-1][1] and device.host==acc_address[-1][0]:
                acc_address[-1].append(device.uuid)
        devices[acc_address[-1][2]].ex=_check_device(fuel_ip=fuel_ip,controller_node=controller_node,device_uuid=acc_address[-1][2])
        if devices[acc_address[-1][2]].ex["availability"]!="in-use":
            res=False
    return res

def _check_device(fuel_ip,controller_node,device_uuid):
    '''get the cyborg output'''
    cmd_device_show="source /root/openrc && cyborg deployables-show %s" %device_uuid
    ex={}
    try:
        tmp=remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_device_show)
    except Exception, error:
        print error, "location: check_deivce"
    for line in tmp.split("\n")[3:-2]:
        ex[line.split("|")[1].strip()]=line.split("|")[2].strip()
    return ex

def fuck_trans_stdout_to_correct(fuck_output):
    '''for the fucking bug!!!!!'''
    d={}
    item=fuck_output[2:-3].split("}, {")
    for line in item:
        tmp= line.split(", ")
        d[tmp[0].split(": ")[1][1:-1]]=tmp[1].split(": ")[1][1:-1]
    return d

def check_program(fuel_ip,controller_node,firmware):
    devices_uuid=[]
    for device in devices.values():
        if device.type=="FPGA":
            devices_uuid.append(device.uuid)
    for uuid in devices_uuid:
        status_before=_check_device(fuel_ip=fuel_ip,controller_node=controller_node,device_uuid=uuid)
        cmd_program="source /root/openrc && cyborg deployables-program %s %s"%(uuid,firmware["id"])
        remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_program)
        status_after=_check_device(fuel_ip=fuel_ip,controller_node=controller_node,device_uuid=uuid)
        print status_before,status_after

def _copy_firmware_from_url(fuel_ip,controller_node,firmware_url):
    cmd_wget="wget %s" %firmware_url
    cmd_check_firmaware="ls | grep %s" %firmware_url.split("/")[-1]
    i=0
    '''if not firmware in controller node, download from url, try 3 times, if after download still no firmware, return false'''
    while not remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_check_firmaware) and i<3:
        remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_wget)
        i+=1
    return i<3

def _set_api_version(fuel_ip,controller_node,api_v="2"):
    cmd_set_api_to_x="sed -i '$d' openrc && sed -i '$a export OS_IMAGE_API_VERSION='%s'' openrc" %api_v
    remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_set_api_to_x)

def update_firmware(fuel_ip,controller_node,firmware_uuid,keystone_url):
    cmd_update_firmware="source /root/openrc && glance image-update %s --name cyborg-modify" %firmware_uuid
    print cmd_update_firmware
    try:
        _set_api_version(fuel_ip=fuel_ip, controller_node=controller_node, api_v="2")
        remote_cmd(fuel_ip=fuel_ip,node=controller_node,cmd=cmd_update_firmware,std="stderr")
        res = _check_image(fuel_ip=fuel_ip, controller_node=controller_node, image_name="cyborg-modify",
                           keystone_url=keystone_url)
    except Exception,error:
        res=[]
        print error,"location: update_firmware"
    finally:
        _set_api_version(fuel_ip=fuel_ip, controller_node=controller_node, api_v="1")
        print res
        return res[0]["name"]=="cyborg-modify"

def create_firmware(fuel_ip,controller_node,firmware_url,keystone_url):
    if not _copy_firmware_from_url(fuel_ip=fuel_ip, controller_node=controller_node,firmware_url=firmware_url):
        return False
    res=_check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name="cyborg-logic",keystone_url=keystone_url)
    print res
    if res:
        return res
    try:
        _set_api_version(fuel_ip=fuel_ip, controller_node=controller_node,api_v="2")
        cmd_create_logic="source /root/openrc && glance image-create --file /root/%s --disk-format raw --container-format bare --name cyborg-logic --tags firmware" %firmware_url.split("/")[-1]
        print remote_cmd(fuel_ip=fuel_ip, node=controller_node,cmd=cmd_create_logic)
    except Exception,error:
        print error,"loaction: create firmware"
    finally:
        _set_api_version(fuel_ip=fuel_ip, controller_node=controller_node, api_v="1")
        res= _check_image(fuel_ip=fuel_ip, controller_node=controller_node,image_name="cyborg-logic",keystone_url=keystone_url)
        return res

def cyborg_test(fuel_ip):
    try:
        print time.ctime()
        get_nodes()
        controller_node=get_controller_node()
        # controller_node="node-7"
        print controller_node
        keystone_url = get_keystone_url(fuel_ip=fuel_ip, controller_node=controller_node)
        print keystone_url
        firmware_1=create_firmware(fuel_ip=fuel_ip,controller_node=controller_node,keystone_url=keystone_url,firmware_url=firmware_url)
        firmware_uuid = firmware_1[0]["id"]
        result["firmware_modify"] =update_firmware(fuel_ip=fuel_ip,controller_node=controller_node,keystone_url=keystone_url,firmware_uuid=firmware_uuid)
        create_image(fuel_ip=fuel_ip,controller_node=controller_node,keystone_url=keystone_url)
        result["list"]=check_cli_cyborg_deployables_list(fuel_ip=fuel_ip,controller_node=controller_node)
        result["attach_to_vm"],result["attach_to_vm_detail"]=check_cli_deployables_attach_vm(fuel_ip=fuel_ip,controller_node=controller_node,devices_type=[["Co-processor",2]])
        result["acc_status"]=check_acc_status(fuel_ip=fuel_ip,controller_node=controller_node,result=result)
    except Exception, error:
        print error,"localtion:main"
    finally:
        tearDown(fuel_ip=fuel_ip,controller_node=controller_node,firmware_uuid=firmware_uuid)

    print result
    print result["list"]
    for device in devices.values():
        if device.state==False or device.ex:
            device.show_device()

if __name__ == '__main__':
    cyborg_test(fuel_ip=fuel_ip)