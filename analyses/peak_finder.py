#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 14:21:19 2017

@author: sgess
"""

import numpy as np
from scipy import signal

def findPeaks(fft):
    
    mx=np.array(signal.argrelmax(fft)).squeeze()
    mn=np.array(signal.argrelmin(fft)).squeeze()
    
    if len(mx) < len(mn):
        maxs = fft[mx]
        mins = fft[mn]

        lps = maxs - mins[0:-1]
        rps = maxs - mins[1:]

        return maxs, mins, lps, rps, mx, mn

    if len(mx) == len(mn):
        if mx[0] > mn[0]:
            mn = np.append(mn,len(fft)-1)
        else:
            mn = np.insert(mn,0,0)
        
        maxs = fft[mx]
        mins = fft[mn]

        lps = maxs - mins[0:-1]
        rps = maxs - mins[1:]

        return maxs, mins, lps, rps, mx, mn
        
    if len(mx) > len(mn):
        mn = np.append(mn,len(fft)-1)
        mn = np.insert(mn,0,0)
        
        maxs = fft[mx]
        mins = fft[mn]

        lps = maxs - mins[0:-1]
        rps = maxs - mins[1:]

        return maxs, mins, lps, rps, mx, mn
        
    print('You fucked up')
        
        


            
            