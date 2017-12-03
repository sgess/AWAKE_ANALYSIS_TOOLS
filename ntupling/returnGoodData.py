#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 12:38:17 2017

@author: sgess
"""

import numpy as np
from getFileMap import getFileMap
import h5py
from TimingCheck import TimingCheck

def returnGoodData(dataPath,file_list):
    
    ''' Clean up dataPath '''
    if dataPath[-1] == '/':
        dataPath = dataPath[:-1]

    ''' Extract File Info '''
    eventTimeStamps = []
    eventRunNumbers = []
    eventEvtNumbers = []
    for file in file_list:
        dir_split = file.split('/')
        ext_split = dir_split[-1].split('.')
        ts, rn, en = ext_split[0].split('_')
        eventTimeStamps.append(int(ts))
        eventRunNumbers.append(int(rn))
        eventEvtNumbers.append(int(en))
        
    ''' Collect Field Info '''
    field_info = {}
    for run in np.unique(eventRunNumbers):
        file_map = getFileMap(run)
        if dataPath in file_map:
            field_info[str(run)] = file_map[dataPath]
        else:
            print('Warning: Data Path ' + dataPath + ' not found in Run Number ' + str(run))
    
    ''' Setup data arrays '''
    nFiles = len(file_list)
    propPath = field_info[str(eventRunNumbers[0])][0]
    field = field_info[str(eventRunNumbers[0])][1]
    dtype = field_info[str(eventRunNumbers[0])][2]
    dim1 = int(field_info[str(eventRunNumbers[0])][4])
    dim2 = int(field_info[str(eventRunNumbers[0])][5])
    if dim2 < 2:
        data_array = np.zeros((nFiles,dim1),dtype=dtype)
    elif dim2 > 1:
        data_array = np.zeros((nFiles,dim1,dim2),dtype=dtype)
    bool_array = np.zeros(nFiles,dtype=bool)
    warn_array = nFiles*['']
    time_array = np.empty(nFiles)
    time_array.fill(np.nan)
        
    ''' Check that data dimensions do not change between runs (that's a big no-no) '''
    if len(np.unique(eventRunNumbers)) > 1:
        for run in np.unique(eventRunNumbers):
            d1 = field_info[str(run)][4]
            d2 = field_info[str(run)][5]
            
            if d1 != dim1 or d2 != dim2:
                print('Warning: Field ' + dataPath + ' has inconsistent dimensions')
                return data_array, bool_array, warn_array, time_array
        
    ''' Loop over files and extract data '''
    timeChecker = TimingCheck()
    for idx,f in enumerate(file_list):
        evbFile = h5py.File(f)
        runNum = eventRunNumbers[idx]
        attr = int(field_info[str(runNum)][6])
        time = field_info[str(runNum)][7]
        
        
        ''' First, check if data is present '''
        if attr == 0:
            acqBool = evbFile[dataPath].attrs['exception']
            if acqBool:
                warn_array[idx] = 'No data present for event'
                continue
        elif attr > 0:
            acqBool = evbFile[propPath].attrs['exception']
            if acqBool:
                warn_array[idx] = 'No data present for event'
                continue
        
        ''' Next, retrieve data '''
        try:
            #print(dim2)
            if dim2 < 2:
                #data_array[idx,:] = evbFile[dataPath][0]
                data_array[idx,:] = evbFile[dataPath].value
                bool_array[idx] = True
            elif dim2 > 1:
                data_array[idx,:,:] = evbFile[dataPath].value
                bool_array[idx] = True
        except:
            warn_array[idx] = 'Could not retrieve data'
        
        ''' Finally, check timing '''
        if time == 'None':
            warn_array[idx] = 'No timing information present'
        else:
            if attr == 0:
                timeBool, timeDelta = timeChecker.checkTime(evbFile,propPath,'/'+field)
                time_array[idx] = timeDelta
                if not timeBool and timeDelta==np.nan:
                    warn_array[idx] = 'No timing information present'
                    bool_array[idx] = False
                elif not timeBool:
                    warn_array[idx] = 'Out-of-time data'
                    bool_array[idx] = False
            elif attr > 0:
                timeBool, timeDelta = timeChecker.checkTime(evbFile,propPath)
                time_array[idx] = timeDelta
                if not timeBool and timeDelta==np.nan:
                    warn_array[idx] = 'No timing information present'
                    bool_array[idx] = False
                elif not timeBool:
                    warn_array[idx] = 'Out-of-time data'
                    bool_array[idx] = False     
        
    return data_array, bool_array, warn_array, time_array