#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 15:58:36 2017

@author: sgess

"""

def returnData(h5file,dsetName):

    shape = h5file[dsetName].shape
    if shape[0]==1:
        dataArray = h5file[dsetName][0]
    else:
        dataArray = h5file[dsetName].value

    dataQual = h5file[dsetName+'.quality'].value    

    return dataArray, dataQual
