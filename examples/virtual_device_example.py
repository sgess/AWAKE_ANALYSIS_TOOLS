#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 16:57:43 2017

Example script for subscribing to a JAPC parameter and publishing a calculation
to an AWAKE Virtual Variable device.

In this example, we get our data from the BCTF and republish in the 
AWAKE-GUI-SUPPORT device

@author: sgess
"""
#%% Import PyJapc and declare devices
import pyjapc
import numpy as np

my_data_source = 'TT41.BCTF.412340/Acquisition#totalIntensityPreferred'
my_virtual_device = 'TSG41.AWAKE-GUI-SUPPORT'

#%% Initialize PyJapc
japc=pyjapc.PyJapc('SPS.USER.AWAKE1')

#%% Set variable names (you only have to do this once)
nameList = ['']*100
nameList[0] = 'Timestamp'
nameList[1] = 'BCTF Data'
japc.setParam(my_virtual_device+'/NameSettings#nameValue',nameList)

#%% Declare call back function
def myCallbackFunction(paramName,paramValue,header):
    
    timeStamp = header['acqStamp']
    
    print(paramName+' = '+ '{:0.2f}'.format(paramValue))
    print('Timestamp = '+str(timeStamp))
    
    values_to_publish = np.zeros(100)
    values_to_publish[0] = timeStamp
    values_to_publish[1] = paramValue
    japc.setParam(my_virtual_device+'/ValueSettings#floatValue',values_to_publish)
    
#%% Start subscription
japc.subscribeParam(my_data_source,myCallbackFunction,getHeader=True,unixtime=True)
japc.startSubscriptions()

#%% Stop subscription
japc.stopSubscriptions()

#%% Clear subscription, do this if you want to start a subscription with a new parameter
japc.clearSubscriptions()
