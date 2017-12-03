#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 13:07:52 2017

@author: sgess
"""
import os

def returnFileMap(runNumber):
   
   
   map_path = os.environ['AAT']+'ntupling/map_files/'
   map_file = 'map_run'+str(runNumber)+'.csv'
   file_info = open(map_path+map_file,'r')

   nTuple_map = []
   for line in file_info:
      nTuple_map.append(line[0:-1])
   file_info.close()
   
   nBranch = len(nTuple_map)
   branches = range(nBranch)
   
   dPath = []
   dType = []
   dSize = []
   dDim1 = []
   dDim2 = []
   field = []
   map_branch = []
   
   for info,branch in zip(nTuple_map,branches):
      split_info = str.split(info,',')
      dPath.append(split_info[0])
      field.append(split_info[1])
      if split_info[2][0] == '|':
          dType.append('str')
      else:
          dType.append(split_info[2])
      
      dSize.append(int(split_info[3]))
      dDim1.append(int(split_info[4]))
      dDim2.append(int(split_info[5]))
      map_branch.append(split_info[0]+'/'+split_info[1])
      
   dictFileMap = {'DataPath':  dPath,
                  'DataField': field,
                  'DataType':  dType,
                  'DataSize':  dSize,
                  'DataDim1':  dDim1,
                  'DataDim2':  dDim2,
                  'MapBranch': map_branch}
   
   return dictFileMap
    