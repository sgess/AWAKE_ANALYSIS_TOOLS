#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 16:45:33 2017

@author: sgess
"""

import os

def getFileMap(runNumber):
   
   
    map_path = os.environ['AAT']+'ntupling/map_files/'
    map_file = 'map_run'+str(runNumber)+'.csv'
    file_info = open(map_path+map_file,'r')
   
    dictFileMap = {}
    for idx,line in enumerate(file_info):
        if idx == 0:
            continue
        no_ret = line[0:-1]
        info = no_ret.split(',')
        key = info[0]+'/'+info[1]
        dictFileMap[key] = info
              
    file_info.close()
    return dictFileMap