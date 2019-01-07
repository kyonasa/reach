# -*- coding: utf-8 -*-
"""
Created on 2018/12/28 14:37
@author: mengph
reach
"""



def fuck_trans_stdout_to_correct(fuck_output):
    '''for the fucking bug!!!!!'''
    d={}
    item=fuck_output[2:-3].split("}, {")
    for line in item:
        field=line[line.find("Field")+9:line.find("Value")-4]
        value=line[line.find("Value")+8:]
        if value[0]=="\"":
            tmp=value[:]
            value=tmp[1:-1]
        d[field]=value
    return d