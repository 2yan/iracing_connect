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

def get_blank():
    global blank
    parts = blank.split(',')
    if parts[2] == '0':
        parts[2] = '1'
    else:
        parts[2] = '0'
    blank = ','.join(parts)
    return blank
    

blank = """$IRTEL,TIME,0,0,0.032359,1,0.000000,0.000000,0.000000,0.002766,0.000000,0.000000,0.109816,300.000000,-0.001262,0.002462,-0.000002,0.290551,-0.065876,9.795001,-0.001526,0.000147,0.008782,0.004638,0.005359,1.992813"""
