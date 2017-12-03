#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 01:46:40 2017

@author: sgess
"""

import datetime
import pytz
import numpy as np
    
''' Class for Checking Time offsets '''
class TimingCheck(object):
    def __init__(self):
        
        self.timing_dictionary = self.get_timingDict()
        self.GVA = pytz.timezone('Europe/Zurich')
        self.UTC = pytz.timezone('UTC')
        
    def checkTime(self,h5File,group,field=''):
        
        if group in self.timing_dictionary:
            time_bool, time_delta = getattr(self,self.timing_dictionary[group])(h5File,group)
            return time_bool, time_delta
        elif h5File[group+field].attrs.__contains__('acqStamp'):
            time_bool, time_delta = self.acqStamp(h5File,group+field)
            return time_bool, time_delta
        else:
            print('No timing information for group ' + group)
            return False, np.nan
        
    ''' List of devices and their timestamp fields '''
    def get_timingDict(self):

        timing_dictionary = {}

        timing_dictionary['/AwakeEventData/BOVWA.01TT41.CAM1/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.02TT41.CAM2/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.03TT41.CAM3/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.04TT41.CAM4/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.05TT41.CAM5/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.01TCC4.CAM9/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.02TCC4.CAM10/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.03TCC4.CAM11/ExtractionImage'] = 'imageTimeStamp'
        timing_dictionary['/AwakeEventData/BOVWA.04TCC4.CAM12/ExtractionImage'] = 'imageTimeStamp'
        
        timing_dictionary['/AwakeEventData/SR.SCOPE27.CH01/Acquisition'] = 'triggerStamp'
        timing_dictionary['/AwakeEventData/SR.SCOPE27.CH02/Acquisition'] = 'triggerStamp'
        timing_dictionary['/AwakeEventData/SR.SCOPE28.CH01/Acquisition'] = 'triggerStamp'
        timing_dictionary['/AwakeEventData/SR.SCOPE29.CH01/Acquisition'] = 'triggerStamp'
        timing_dictionary['/AwakeEventData/SR.SCOPE30.CH01/Acquisition'] = 'triggerStamp'
        timing_dictionary['/AwakeEventData/SR.SCOPE30.CH02/Acquisition'] = 'triggerStamp'
        
        timing_dictionary['/AwakeEventData/TCC4.AWAKE-SCOPE-CTR.CH1/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TCC4.AWAKE-SCOPE-CTR.CH2/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TCC4.AWAKE-SCOPE-CTR.CH3/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TCC4.AWAKE-SCOPE-CTR.CH4/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TSG40.AWAKE-LASER-CORRELATOR/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TSG41.AWAKE-CTRHET-VDI/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TSG41.AWAKE-CTRHET-WR8/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TT41.AWAKE-PLASMA-SPECTRO-DOWN/FileRead'] = 'fileTime'
        timing_dictionary['/AwakeEventData/TT41.AWAKE-PLASMA-SPECTRO-UP/FileRead'] = 'fileTime'
        
        timing_dictionary['/AwakeEventData/TT41.BCTF.412340/Acquisition'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412350/Acquisition'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412350/Image'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412353/Acquisition'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412353/Image'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412426/Acquisition'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412426/Image'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412442/Acquisition'] = 'acqTime'
        timing_dictionary['/AwakeEventData/TT41.BTV.412442/Image'] = 'acqTime'
        
        timing_dictionary['/AwakeEventData/TT41.BTV.412350.STREAK/StreakImage'] = 'streakImageTime'
        timing_dictionary['/AwakeEventData/XMPP-STREAK/StreakImage'] = 'streakImageTime'
        
        return timing_dictionary
    
    ''' Timestamp check for PXI cameras '''
    def imageTimeStamp(self,h5file,group):
        
        try:
            cycle_time = h5file['/AwakeEventInfo/timestamp'].value
        except:
            print('Could not extract cycle time from file')
            return False, np.nan
        try:
            image_time = h5file[group+'/'+'imageTimeStamp'][0]
        except:
            print('Could not extract image time from file')
            return False,  np.nan
        
        time_delta = (image_time - cycle_time)/1e9
        if time_delta > 0 and time_delta < 10:
            return True, time_delta
        else:
            return False, time_delta
        
    ''' Timestamp check for OASIS scopes '''
    def triggerStamp(self,h5file,group):
        
        try:
            cycle_time = h5file['/AwakeEventInfo/timestamp'].value
        except:
            print('Could not extract cycle time from file')
            return False, np.nan
        try:
            trigger_time = h5file[group+'/'+'triggerStamp'][0]
        except:
            print('Could not extract trigger time from file')
            return False, np.nan
        
        time_delta = (trigger_time - cycle_time)/1e9
        if time_delta > 5 and time_delta < 10:
            return True, time_delta
        else:
            return False, time_delta
            
    ''' Timestamp check for FileReader '''
    def fileTime(self,h5file,group):
        
        try:
            cycle_time = h5file['/AwakeEventInfo/timestamp'].value
        except:
            print('Could not extract cycle time from file')
            return False, np.nan
        try:
            file_time = h5file[group+'/'+'fileTime'][0]
        except:
            print('Could not extract file time from file')
            return False, np.nan
        
        time_delta = (file_time - cycle_time)/1e9
        if time_delta > -10 and time_delta < 11:
            return True, time_delta
        else:
            return False, time_delta
        
    ''' Timestamp check for BI devices '''
    def acqTime(self,h5file,group):
        
        try:
            cycle_time = h5file['/AwakeEventInfo/timestamp'].value
        except:
            print('Could not extract cycle time from file')
            return False, np.nan
        try:
            acq_t = h5file[group+'/'+'acqTime'][0].decode()
            dtLOC = datetime.datetime.strptime(acq_t,'%Y/%m/%d %H:%M:%S.%f')
            dtUTC = self.UTC.localize(dtLOC, is_dst=None)
            acq_time = 1e9*dtUTC.timestamp()
        except:
            print('Could not extract acquisition time from file')
            return False, np.nan
        
        time_delta = (acq_time - cycle_time)/1e9
        if time_delta > 5 and time_delta < 10:
            return True, time_delta
        else:
            return False, time_delta
        
    ''' Timestamp check for Streak Cameras '''
    def streakImageTime(self,h5file,group):
        
        try:
            cycle_time = h5file['/AwakeEventInfo/timestamp'].value
            cyUTC = datetime.datetime.fromtimestamp(cycle_time/1e9, pytz.timezone('UTC'))
            cyLOC = cyUTC.astimezone(self.GVA)
            date_str = str(cyLOC.year)+'/'+'{0:02d}'.format(cyLOC.month)+'/'+'{0:02d}'.format(cyLOC.day)
        except:
            print('Could not extract cycle time from file')
            return False, np.nan
        
        
        if group == '/AwakeEventData/XMPP-STREAK/StreakImage':
            try:
                img_t = h5file[group+'/'+'streakImageTime'][0].decode()
                HMS,PMF = img_t.split()
                H,M,S = HMS.split(':')
                PM,F = PMF.split('.')
                if PM == 'pm':
                    h = int(H)
                    h += 12
                    H = str(h)
                if PM == 'am' and H == '12':
                    H = '00'
                    
                t_str = date_str+' '+H+':'+M+':'+S+'.'+F
                dtLOC = datetime.datetime.strptime(t_str,'%Y/%m/%d %H:%M:%S.%f')
                dtGVA = self.GVA.localize(dtLOC, is_dst=None)
                image_time = 1e9*dtGVA.timestamp()
                
            except:
                print('Could not extract image time from file')
                return False, np.nan
                    
        elif group == '/AwakeEventData/TT41.BTV.412350.STREAK/StreakImage':
            try:
                img_t = h5file[group+'/'+'streakImageTime'][0].decode()
                t_str = date_str+' '+img_t
                dtLOC = datetime.datetime.strptime(t_str,'%Y/%m/%d %H:%M:%S.%f')
                dtGVA = self.GVA.localize(dtLOC, is_dst=None)
                image_time = 1e9*dtGVA.timestamp()
                
            except:
                print('Could not extract image time from file')
                return False, np.nan   
                        
        time_delta = (image_time - cycle_time)/1e9
        if time_delta > 0 and time_delta < 10:
            return True, time_delta
        else:
            return False, time_delta
        
    ''' Timestamp check for all other devices '''
    def acqStamp(self,h5file,group):
        
        try:
            cycle_time = h5file['/AwakeEventInfo/timestamp'].value
        except:
            print('Could not extract cycle time from file')
            return False, np.nan
        try:
            stamp_time = h5file[group].attrs['acqStamp']
        except:
            print('Could not extract image time from file')
            return False, np.nan
        
        time_delta = (stamp_time - cycle_time)/1e9
        if time_delta > 0 and time_delta < 11:
            return True, time_delta
        else:
            return False, time_delta    