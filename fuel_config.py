# -*- coding: utf-8 -*-
"""
Created on 2018/9/3 15:15
@author: mengph
reach
"""
import os
import sys
env=sys.argv[2]
dir="/home/mengph"
cmd_mkdir="mkdir %s" % dir
cmd_download_settings="fuel settings --env %s --download --dir %s" %(env,dir)
cmd_download_network="fuel network --env %s --download --dir %s" %(env,dir)

cmd_upload_settings="fuel settings --env %s --upload --dir %s" %(env,dir)
cmd_upload_network="fuel network --env %s --upload --dir %s" %(env,dir)

# pre
cmd_debug="fuel nodes"
res=os.popen(cmd_debug).readlines()
d={}
for i in range(2,len(res)):
	d[res[i].split("|")[5].strip()]=res[i].split("|")[0]



if sys.argv[1]=="download_settings":
    os.popen(cmd_mkdir)
    os.popen(cmd_download_settings)
    os.popen(cmd_download_network)
elif sys.argv[1] == "download_nodes":
    for mac in d.keys():
        node_dir=dir+"/"+str(mac)
        cmd_mkdir="mkdir %s" % node_dir
        cmd_download_node_network="fuel node --node %s --network --download --dir %s" %(mac,node_dir)
        cmd_download_node_disk="fuel node --node %s --disk --download --dir %s" %(mac,node_dir)
        os.popen(cmd_mkdir)
        os.popen(cmd_download_node_network)
        os.popen(cmd_download_node_disk)
    cmd_tar="tar czvf fuel_settings_all.tar %s" % dir
    os.popen(cmd_tar)
elif sys.argv[1]=="upload_settings":
        os.popen(cmd_upload_settings)
        os.popen(cmd_upload_network)

elif sys.argv[1]=="upload_nodes":
    for mac in d.keys():
        cmd_set_node_id = "ls %s" % (dir + "/" + str(mac))
        cmd_upload_node_network = "fuel node --node %s --network --upload --dir %s" % (mac, dir)
        cmd_upload_node_disk = "fuel node --node %s --disk --upload --dir %s" % (mac, dir)
        file = os.popen(cmd_set_node_id).readlines()[0].splitlines()
        cmd_copy_file_to_new_node = "cp -r %s %s" % (dir + "/" + str(mac) + "/" + file[0], dir + "/node_" + d[mac])
        os.popen(cmd_copy_file_to_new_node)
        os.popen(cmd_upload_node_network)
        os.popen(cmd_upload_node_disk)

elif sys.argv[1]=="debug":
    for mac in d.keys():
        cmd_set_node_id = "ls %s" % (dir + "/" + str(mac))
        cmd_upload_node_network = "fuel node --node %s --network --upload --dir %s" % (mac, dir)
        cmd_upload_node_disk = "fuel node --node %s --disk --upload --dir %s" % (mac, dir)
        file = os.popen(cmd_set_node_id).readlines()[0].splitlines()
        cmd_copy_file_to_new_node = "cp -r %s %s" % (dir + "/" + str(mac) + "/" + file[0], dir + "/node_" + d[mac])
        os.popen(cmd_copy_file_to_new_node)
        os.popen(cmd_upload_node_network)
        os.popen(cmd_upload_node_disk)

#	cmd_debug="fuel nodes"
#	res=os.popen(cmd_debug).readlines()
#	d={}
#	for i in range(2,len(res)):
#		d[res[i].split("|")[5]]=res[i].split("|")[0]
#	print d
