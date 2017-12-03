#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 19:20:05 2017

@author: sgess, karl
"""

import glob
import datetime as dt
from pytz import timezone
import numpy as np
import time
import os

#
# special time function, gives
#

#header = '/user/awakeop/event_data/'

def fileListfromTime(header,kwords,*args):
    # hopefully specified epoch timestamp
    header=kwords['searchDir'].value[0]
    #header=header[0]
    if header[-1] !='/':
        header+='/'
    try:
        t_low=kwords['/AwakeEventInfo/timestamp'].lower_bound.tocompare/1e9
        #print('{0:09f}'.format(t_low))
    except:
        t_low=0
    try:
        t_high=kwords['/AwakeEventInfo/timestamp'].upper_bound.tocompare/1e9
        #print('{0:09f}'.format(t_high))
    except:
        t_high=1e10 #hardcoded bad solution
    
    #print(t_low,t_high)
    # next, create epoch timestamp 
    start = t_low
    end = t_high
    dt_low=dt.date.timetuple(dt.date.fromtimestamp(t_low))
    dt_high=dt.date.timetuple(dt.date.fromtimestamp(t_high))
    # next, create the list of dates to search
    
    years  = np.arange(dt_low[0],dt_high[0]+1)
    months = np.arange(dt_low[1],dt_high[1]+1)
    if months.size==1:
       days=[np.arange(dt_low[2],dt_high[2]+1)]
    else:
       days=[]
       for k in range(months.size):
           if k==months.size-1:
              days+=[np.arange(1,dt_high[2]+1)]
           if k==0:
              days+=[np.arange(dt_low[2],31+1)]
           if k<months.size-1 and k>0:
              days+=[np.arange(1,31+1)]

    file_list = []
    for y in range(years.size):
        for m in range(months.size):
            for d in days[m]:
                date_path = header + str(years[y]) + '/' + '{0:02d}'.format(months[m]) + '/' + '{0:02d}'.format(d) + '/'
                #print(y)
                #print(date_path)
                files = glob.glob(date_path + '*.h5')
                files.sort(key=os.path.getmtime)
                for f in files:
                    h5_file = os.path.basename(f)#.rsplit('/',1)[1]
                    ns_timeStamp = float(h5_file.split('_',1)[0])/1e9
                    if ns_timeStamp > start and ns_timeStamp < end:
                        file_list.append(f)

    return file_list


#
# List of Standard Keywords that are alway allowed
# please only edit when you are sure what you are doing
#

standardKeywords={'searchDir':fileListfromTime,'/AwakeEventInfo/timestamp': (lambda x=None,*args,**kwargs:np.array([True]))}#:None#: fileListfromTime, 'laser_on': laserFKT, 'RbValveDown': rbDownFKT....
standardFlags=['targetDir','ntupling','nTupling']
