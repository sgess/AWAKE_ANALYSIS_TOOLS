#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:37:47 2017

@author: sgess
"""
import numpy as np
from scipy.optimize import curve_fit

''' Define Gaussian Shape '''
def gaussian(x, amp, cen, wid, off):

    return amp * np.exp(-(x-cen)**2 /(2*wid**2)) + off

''' Fit Gaussian. Not called by default '''
def gaussFit(axis,prof,guess):
    
    try:
        result,pcov = curve_fit(gaussian,axis,prof,guess)
        result[2] = abs(result[2])
        fit = gaussian(axis, *result)
    except:
        print('Failed to fit in '+axis+'-direction')
        result = [0,0,0,0]
        fit = np.zeros(np.shape(axis))
        
    return result, fit