#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:54:33 2017

@author: sgess
"""
from returnCamProps import returnCamProps

def returnBranchData(file_maps,branches,InputParsed):
    
    # Check to see if the images should be formatted into a 2D array
    formatImages = False
    if 'formatImages' in InputParsed.Flags:
        formatImVal = InputParsed.Flags['formatImages']
        if formatImVal:
            formatImages = True        
    
    # Loop over k = runNumber
    dictBranchData = {}
    for k in file_maps.keys():
        file_map = file_maps[k]
        allBranches = file_map['MapBranch']
        
        # Get camera properties for runNumber k
        if formatImages:
            cam_props = returnCamProps(int(k))
        
        Branches = []
        DataType = []
        DataSize = []
        DataDim1 = []
        DataDim2 = []
        
        # Loop over branches
        for b in branches:
            
            try: # check if branch exists for given run number
                indB = allBranches.index(b)
                dType = file_map['DataType'][indB]
                dSize = file_map['DataSize'][indB]
                dDim1 = file_map['DataDim1'][indB]
                dDim2 = file_map['DataDim2'][indB]
            
                # Change data dimensions for images
                if formatImages:
                    if b in cam_props['cameraList']:
                        indC = cam_props['cameraList'].index(b)
                        dDim1 = cam_props['cameraHeight'][indC]
                        dDim2 = cam_props['cameraWidth'][indC]
                        if dDim1*dDim1 != dSize:
                            IOError('Camera size does not match array size')
                
                # Add data for each branch
                Branches.append(b)
                DataType.append(dType)
                DataSize.append(dSize)
                DataDim1.append(dDim1)
                DataDim2.append(dDim2)
            except:
                print('Branch '+b+' does not exist for run number '+k)
        #print('Here')            
        # Add dictionary for each run number
        dictRunNMap = {'Branches': Branches,
                       'DataType': DataType,
                       'DataSize': DataSize,
                       'DataDim1': DataDim1,
                       'DataDim2': DataDim2}
        dictBranchData[k] = dictRunNMap
    
    if len(file_maps.keys()) > 1:
        # One file loop to get "master map" for ntuple
        Branches = []
        DataType = []
        DataSize = []
        DataDim1 = []
        DataDim2 = []
        for b in branches:
            for k in dictBranchData:
                dictRunNMap = dictBranchData[k]
    else:
        dictBranchData['master'] = dictRunNMap
    
    return dictBranchData