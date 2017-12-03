#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 12:30:47 2017

@author: sgess
"""

import os
import numpy as np

def returnPlasmaDensity(eventTimeStamps):
   
   
    map_path = os.environ['AAT']+'ntupling/map_files/'
    den_file = 'rb_data.csv'
    den_info = open(map_path+den_file,'r')
    
    timeStamp = []
    USDensity = []
    DSDensity = []
    DensGrads = []
    US_Valves = []
    DS_Valves = []
    USBoolean = []
    DSBoolean = []
    USWarning = []
    DSWarning = []    
    for idx,line in enumerate(den_info):
        if idx == 0:
            continue
        
        lineSplit = line.split(',')
        ts = int(lineSplit[0].lstrip())
        up = float(lineSplit[1].lstrip())
        dn = float(lineSplit[2].lstrip())
        gr = float(lineSplit[3].lstrip())
        uv = int(lineSplit[4].lstrip())
        dv = int(lineSplit[5].lstrip())
        ub = lineSplit[6].lstrip()
        db = lineSplit[7].lstrip()
        uw = lineSplit[8].lstrip()
        dw = lineSplit[9].lstrip()
        
        timeStamp.append(ts)
        USDensity.append(up)
        DSDensity.append(dn)
        DensGrads.append(gr)
        US_Valves.append(uv)
        DS_Valves.append(dv)
        if ub == 'True':
            USBoolean.append(True)
        elif ub == 'False':
            USBoolean.append(False)
        if db == 'True':
            DSBoolean.append(True)
        elif db == 'False':
            DSBoolean.append(False)
        USWarning.append(uw)
        DSWarning.append(dw[0:-1])
        
    den_info.close()
    
    US_densities = []
    DS_densities = []
    Gradients = []
    US_valve = []
    DS_valve = []
    US_dataBool = []
    DS_dataBool = []
    US_warning = []
    DS_warning = []

    for eTS in eventTimeStamps:
        try:
            ind = timeStamp.index(eTS)
            US_densities.append(USDensity[ind])
            DS_densities.append(DSDensity[ind])
            Gradients.append(DensGrads[ind])
            US_valve.append(US_Valves[ind])
            DS_valve.append(DS_Valves[ind])
            US_dataBool.append(USBoolean[ind])
            DS_dataBool.append(DSBoolean[ind])
            US_warning.append(USWarning[ind])
            DS_warning.append(DSWarning[ind])
            
        except:
            print('Warning: Time Stamp Out of Range')
            US_densities.append(np.nan)
            DS_densities.append(np.nan)
            Gradients.append(np.nan)
            US_valve.append(np.nan)
            DS_valve.append(np.nan)
            US_dataBool.append(False)
            DS_dataBool.append(False)
            US_warning.append('')
            DS_warning.append('')
            
              
    return (US_densities, DS_densities, Gradients, US_valve, DS_valve,
            US_dataBool, DS_dataBool, US_warning, DS_warning)
