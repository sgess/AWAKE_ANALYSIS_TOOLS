#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 15:36:57 2017

@author: sgess
"""

def returnFileData(file_list):
    
    file_path = []
    file_name = []
    file_time = []
    file_runN = []
    file_evtN = []
    for f in file_list:
        [path,name] = str.rsplit(f,'/',1)
        [temp,ext] = str.split(name,'.')
        [time,runN,evtN] = str.rsplit(temp,'_')
        file_path.append(path)
        file_name.append(name)
        file_time.append(int(time))
        file_runN.append(int(runN))
        file_evtN.append(int(evtN))
        

    dictFileData = {'FilePath': file_path,
                    'FileName': file_name,
                    'FileTime': file_time,
                    'FileRunN': file_runN,
                    'FileEvtN': file_evtN}
    
    return dictFileData