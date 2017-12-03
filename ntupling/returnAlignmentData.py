#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 01:59:19 2017

@author: sgess
"""

import os
import numpy as np

def returnAlignmentData(eventTimeStamps):
   
    map_path = os.environ['AAT']+'ntupling/map_files/'
    align_file = 'LaserAlignmentData.csv'
    align_info = open(map_path+align_file,'r')
    
    EvtsTimeStamp = []
    Cam3TimeStamp = []
    Cam3XPos = []
    Cam3YPos = []
    Cam3RPos = []
    Cam5TimeStamp = []
    Cam5XPos = []
    Cam5YPos = []
    Cam5RPos = []
    Cam3TimeBool = []
    Cam5TimeBool = []
    for idx,line in enumerate(align_info):
        if idx == 0:
            continue
        
        lineSplit = line.split(',')
        evtts_str = lineSplit[0].lstrip()
        cam3ts_str = lineSplit[1].lstrip()
        cam3x = float(lineSplit[2].lstrip())
        cam3y = float(lineSplit[3].lstrip())
        cam3r = float(lineSplit[4].lstrip())
        cam5ts_str = lineSplit[5].lstrip()
        cam5x = float(lineSplit[6].lstrip())
        cam5y = float(lineSplit[7].lstrip())
        cam5r = float(lineSplit[8].lstrip())
        cam3b_str = lineSplit[9].lstrip()
        cam5b_str = lineSplit[10].lstrip()
        
        if evtts_str == 'nan':
            EvtsTimeStamp.append(np.nan)
        else:
            EvtsTimeStamp.append(int(evtts_str))
            
        if cam3ts_str == 'nan':
            Cam3TimeStamp.append(np.nan)
        else:
            Cam3TimeStamp.append(int(cam3ts_str))
        Cam3XPos.append(cam3x)
        Cam3YPos.append(cam3y)
        Cam3RPos.append(cam3r)
        
        if cam5ts_str == 'nan':
            Cam5TimeStamp.append(np.nan)
        else:
            Cam5TimeStamp.append(int(cam3ts_str))
        Cam5XPos.append(cam5x)
        Cam5YPos.append(cam5y)
        Cam5RPos.append(cam5r)
        
        if cam3b_str == 'True':
            Cam3TimeBool.append(True)
        elif cam3b_str == 'False':
            Cam3TimeBool.append(False)
        if cam5b_str == 'True':
            Cam5TimeBool.append(True)
        elif cam5b_str == 'False':
            Cam5TimeBool.append(False)
        
    align_info.close()
    
    Cam3TimeStamps = []
    Cam3XPositions = []
    Cam3YPositions = []
    Cam3RPositions = []
    Cam3DataStatus = []
    Cam5TimeStamps = []
    Cam5XPositions = []
    Cam5YPositions = []
    Cam5RPositions = []
    Cam5DataStatus = []
    

    for eTS in eventTimeStamps:
        try:
            ind = EvtsTimeStamp.index(eTS)
            
            Cam3TimeStamps.append(Cam3TimeStamp[ind])
            Cam3XPositions.append(Cam3XPos[ind])
            Cam3YPositions.append(Cam3YPos[ind])
            Cam3RPositions.append(Cam3RPos[ind])
            if (np.isnan(Cam3XPos[ind]) or np.isnan(Cam3YPos[ind]) or 
                np.isnan(Cam3RPos[ind]) or not Cam3TimeBool[ind]):
                Cam3DataStatus.append(False)
            else:
                Cam3DataStatus.append(True)
                
            Cam5TimeStamps.append(Cam5TimeStamp[ind])
            Cam5XPositions.append(Cam5XPos[ind])
            Cam5YPositions.append(Cam5YPos[ind])
            Cam5RPositions.append(Cam5RPos[ind])
            if (np.isnan(Cam5XPos[ind]) or np.isnan(Cam5YPos[ind]) or 
                np.isnan(Cam5RPos[ind]) or not Cam5TimeBool[ind]):
                Cam5DataStatus.append(False)
            else:
                Cam5DataStatus.append(True)
            
        except:
            print('Warning: Timestamp not in list of events')
            Cam3TimeStamps.append(np.nan)
            Cam3XPositions.append(np.nan)
            Cam3YPositions.append(np.nan)
            Cam3RPositions.append(np.nan)
            Cam3DataStatus.append(False)
            Cam5TimeStamps.append(np.nan)
            Cam5XPositions.append(np.nan)
            Cam5YPositions.append(np.nan)
            Cam5RPositions.append(np.nan)
            Cam5DataStatus.append(False)
            
              
    return (Cam3XPositions, Cam3YPositions, Cam3RPositions, Cam3TimeStamps, Cam3DataStatus,
            Cam5XPositions, Cam5YPositions, Cam5RPositions, Cam5TimeStamps, Cam5DataStatus)