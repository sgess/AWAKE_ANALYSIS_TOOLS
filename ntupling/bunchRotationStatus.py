#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 17:52:33 2017

@author: sgess
"""

import os
import numpy as np

def bunchRotationStatus(eventTimeStamps):
   
   
    map_path = os.environ['AAT']+'ntupling/map_files/'
    rot_file = 'bunch_rotation_history_160601_170619.csv'
    rot_info = open(map_path+rot_file,'r')
    
    timeStamps = []
    statuses = []
    for line in rot_info:
        lineSplit = line.split(',')
        ts = int(lineSplit[0])
        timeStamps.append(ts)
        status = lineSplit[1]
        if status[0:-1] == 'Enable':
            statuses.append(True)
        elif status[0:-1] == 'Disable':
            statuses.append(False)
            
    bunchRotOn = np.zeros(len(eventTimeStamps),dtype=bool)
    for ids,eTS in enumerate(eventTimeStamps):
        for idx,ts in enumerate(timeStamps):
            if eTS > ts:
                bunchRotOn[ids] = statuses[idx]
            elif eTS < ts:
                break
              
    return bunchRotOn