# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 23:56:21 2024

@author: Rdrac
"""

import requests




DATAVALIDEVENTNAME = 'Local\\IRSDKDataValidEvent'
MEMMAPFILE = 'Local\\IRSDKMemMapFileName'
MEMMAPFILESIZE = 1164 * 1024
BROADCASTMSGNAME = 'IRSDK_BROADCASTMSG'
SIM_STATUS_URL = 'http://127.0.0.1:32034/get_sim_status?object=simStatus'

def sim_is_on():
    r = requests.get(SIM_STATUS_URL)
    if 'running:1' in r.text:
        return True
    if 'running:0' in r.text:
        return False
    return False