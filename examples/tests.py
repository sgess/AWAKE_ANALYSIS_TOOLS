#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' These commands set up the work environemt '''
import os
import sys

''' Replace this line with your local AAT directory '''
os.environ['AAT'] = '/afs/cern.ch/user/s/sgess/AWAKE_ANALYSIS_TOOLS/'
sys.path.append(os.environ['AAT']+'ntupling/')
sys.path.append(os.environ['AAT']+'utilities/')

import cutParser
from bunchRotationStatus import bunchRotationStatus
from returnGoodData import returnGoodData
from returnPlasmaDensity import returnPlasmaDensity

#%%
''' Replace this line to point to your input file '''
input_file = '/afs/cern.ch/user/s/sgess/AWAKE_ANALYSIS_TOOLS/scratch/input.txt'
InputParsed=cutParser.inputParser(input_file)
good_list, bool_set = InputParsed()

#%%
''' Extract timestamps '''
eventTimeStamps = []
for file in good_list:
    file_split = file.split('/')
    name_split = file_split[-1].split('_')
    eventTimeStamps.append(int(name_split[0]))

#%%
''' Get plasma densities '''
(US_densities, DS_densities, Gradients, US_valve, DS_valve,
 US_dataBool, DS_dataBool, US_warning, DS_warning) = returnPlasmaDensity(eventTimeStamps)

#%%
''' Get bunch rotation status '''
bunchRotStatus = bunchRotationStatus(eventTimeStamps)

#%%
''' Get plasma cell temp '''
temp_path = '/AwakeEventData/awake.XAWAVS_BEAML_TT_AVG/PosSt/value'
temp_data, temp_bool, temp_warn, temp_time = returnGoodData(temp_path,good_list)

#%%
''' Get bunch charge '''
bctf_path = '/AwakeEventData/TT41.BCTF.412340/Acquisition/totalIntensityPreferred'
bctf_data, bctf_bool, bctf_warn, bctf_time = returnGoodData(bctf_path,good_list)

#%%
''' Get Streak image '''
xmpp_path = '/AwakeEventData/XMPP-STREAK/StreakImage/streakImageData'
xmpp_data, xmpp_bool, xmpp_warn, xmpp_time = returnGoodData(xmpp_path,good_list)