#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 00:49:35 2017

@author: sgess
"""

import numpy as np
import h5py
from returnFileData import returnFileData
from returnFileMap import returnFileMap
from returnBranchData import returnBranchData
from returnCamProps import returnCamProps

def createNtuples (file_list,InputParsed):

    if not len(file_list):
        print('Error:Empty file list')
        return

    
    # Get information on the files to be ntupled
    dictFileData = returnFileData(file_list)
    runNums = np.unique(dictFileData['FileRunN'])
    file_maps = {}
    cam_props = {}
    for i in runNums:
        file_map = returnFileMap(i)
        file_maps[str(i)] = file_map
        cam_prop = returnCamProps(i)
        cam_props[str(i)] = cam_prop
        
    # Get information on the branches to be ntupled
    devices = InputParsed.argDevices
    branches = [d[7:] for d in devices]
    # Add cut branches
    for k in InputParsed.args.keys():
        if k not in branches:
            branches.append(k)
        
    dictBranchData = returnBranchData(file_maps,branches,InputParsed)
    
    # How many files are there?
    nFiles = len(file_list)
    fNum = range(nFiles)
    nBranch = len(branches)
    
    # Now we a ready to ntuple
    ntupleDir = InputParsed.Flags['ntupleDir'][0]
    ntupleFile = InputParsed.Flags['ntupleFile'][0]
    nTup = h5py.File(ntupleDir+ntupleFile, "w")
    info_qual = [True] * nFiles
    # Add file data to ntuple
    Dataset = nTup.create_dataset('/file_info/FileName', data=str(dictFileData['FileName']))
    Dataset = nTup.create_dataset('/file_info/FileName.quality', data=info_qual)
    Dataset = nTup.create_dataset('/file_info/FileTime', data=dictFileData['FileTime'])
    Dataset = nTup.create_dataset('/file_info/FileTime.quality', data=info_qual)
    Dataset = nTup.create_dataset('/file_info/RunNumber', data=dictFileData['FileRunN'])
    Dataset = nTup.create_dataset('/file_info/RunNumber.quality', data=info_qual)
    Dataset = nTup.create_dataset('/file_info/EvtNumber', data=dictFileData['FileEvtN'])
    Dataset = nTup.create_dataset('/file_info/EvtNumber.quality', data=info_qual)
    
    # Add branch data to ntuple
    BranchData = dictBranchData['master']
    count = 0
    dec = 0
    for branch in branches:
            
        #print(branch)
        # Get branch info from 'master'
        indB = BranchData['Branches'].index(branch)
        dType = BranchData['DataType'][indB]
        dDim1 = BranchData['DataDim1'][indB]
        dDim2 = BranchData['DataDim2'][indB]
  
        # Allocate data arrays based on branch info
        # from 'master' branch info
        if dType == 'str' and dDim1 == 1:
            my_data = []
        elif dType == 'str' and dDim1 != 1:
            my_data = []
        else:
            if dDim2 == 0:
                my_data = np.zeros((dDim1,nFiles),dType)
            else:
                my_data = np.zeros((dDim1,dDim2,nFiles),dType)
                
        # Set data quality to false for this branch
        my_qual = [False] * nFiles
        
        # Now loop over files and fill in data
        for f,i in zip(file_list,fNum):
            
            count+=1
            if np.floor(100*count/(nBranch*nFiles)) > dec:
                
                print(str(dec)+'%')
                dec+=10
            
            #print(f)
            # Load AEB file
            h5_file = h5py.File(f,'r')
            runNum = dictFileData['FileRunN'][i]
            
            # Data size may change between runs . . .
            nBranchData = dictBranchData[str(runNum)]
            indnB = nBranchData['Branches'].index(branch)
            dnType = BranchData['DataType'][indnB]
            dnDim1 = BranchData['DataDim1'][indnB]
            dnDim2 = BranchData['DataDim2'][indnB]
            if dnType != dType:
                IOError('Data type cannot change between runs. Branch excluded from nTuple')
                continue
                
            if dnType == 'str' and dnDim1 == 1:
                try:
                    my_str = h5_file[branch][0].decode()
                    my_data.append(my_str)
                    my_qual[i] = True
                except:
                    my_data.append('')
                    my_qual[i] = False
            elif dnType == 'str' and dnDim1 != 1:
                try:
                    sub_data = []
                    for n_str in h5_file[branch][0]:
                        my_str = n_str.decode()
                        sub_data.append(my_str)
                    my_data.append(sub_data)
                    my_qual[i] = True
                except:
                    my_data.append(['']*dnDim1)
                    my_qual[i] = False
            elif dnType != 'str':
                if dnDim2 == 0:
                    try:
                        my_data[:,i] = h5_file[branch].value
                        my_qual[i] = True
                    except:
                        my_qual[i] = False
                else:
                    try:
                        
                        tmp_dat = h5_file[branch][:]
                        if branch in cam_props[str(runNum)]['cameraList']:
                            #print(branch)
                            indC = cam_props[str(runNum)]['cameraList'].index(branch)
                            height = cam_props[str(runNum)]['cameraHeight'][indC]
                            width = cam_props[str(runNum)]['cameraWidth'][indC]
                            #print('Height = ' + str(height) + ', Width = ' + str(width))
                            dat = tmp_dat.reshape((height,width))
                            #print(dat.shape)
                            my_data[:,:,i] = dat
                        else:
                            my_data[:,:,i] = tmp_dat
                        my_qual[i] = True
                    except:
                        my_qual[i] = False
        
        if dType == 'str':
            Dataset = nTup.create_dataset(branch, data=str(my_data))
            Dataset = nTup.create_dataset(branch+'.quality', data=my_qual)
        else:
            Dataset = nTup.create_dataset(branch, data=my_data)
            Dataset = nTup.create_dataset(branch+'.quality', data=my_qual)

    nTup.close()
