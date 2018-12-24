# -*- coding: utf-8 -*-
"""
Created on 2018/7/11 19:14
@author: mengph
reach
"""
import IxNetwork
host="10.100.217.66"
ixNet=IxNetwork.IxNet()
apiKey = ixNet.getApiKey(host, 'admin', 'admin', './api.key')
ixNet.connect(host, '-version', '8.20', '-apiKey', apiKey)
print ixNet.getSessions(host, '-apiKey', apiKey)
print ixNet.getSessionInfo()

