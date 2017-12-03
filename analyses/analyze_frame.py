#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 21:27:20 2017

@author: sgess
"""

import numpy as np
import scipy.signal as sig
from scipy.optimize import curve_fit
from numpy.fft import fft

# Centroid and weighted RMS
def profile_moments(prof_data,prof_axis):
    
    cent = prof_data.dot(prof_axis)/prof_data.sum()
    rms = np.sqrt(prof_data.dot((prof_axis-cent)**2)/prof_data.sum())
    
    return cent, rms

# Define Gaussian
def gaussian(x, amp, cen, wid, off):
    
    return amp * np.exp(-(x-cen)**2 /(2*wid**2)) + off

# Fit Gaussian
def gaussFit(ax,data,guess):
    
    try:
        result,pcov = curve_fit(gaussian,ax,data,guess)
        result[2] = abs(result[2])
        fit = gaussian(ax, *result)
    except:
        result = [0,0,0,0]
        fit = np.zeros(np.shape(ax))
    
    return fit, result

# Streak analysis
def streak_ana(data_dict,width):
    
    # Extract axes centroid and image
    x_ax = data_dict['x_ax']
    t_ax = data_dict['y_ax']
    xc = data_dict['mean_x']
    img = data_dict['img']
    
    # Create lineout and bands for FFT
    xl = xc - width*data_dict['sig_x']
    xh = xc + width*data_dict['sig_x']
    x_ind = (x_ax > xl) & (x_ax < xh)
    c_ind = np.argmin(min(abs(x_ax-xc)))    
    band = img[:,x_ind].mean(1)
    line = img[:,c_ind]
    outb = img[:,~x_ind].mean(1)

    # Create FFT axis
    nsamp = len(t_ax)
    s_max = round(nsamp/2)
    dt = t_ax[1]-t_ax[0]
    f_max = 1/dt
    t_max = t_ax[-1]-t_ax[0]
    f_min = 1/t_max
    full_ax = np.linspace(0,f_max,nsamp)
    f_ax = 1000*full_ax[0:s_max]

    # FFT the data
    fb = fft(band)
    fl = fft(line)
    fo = fft(outb)

    # Get the phase for each bin
    pb = np.imag(fb)
    pl = np.imag(fl)
    po = np.imag(fo)

    # Get the absolute value of the FFT
    fftb = abs(fb[0:s_max])
    fftl = abs(fl[0:s_max]) 
    ffto = abs(fo[0:s_max])

    # Get the normalized FFT
    nfftb = abs(fb[0:s_max])/sum(abs(fb[0:s_max]))
    nfftl = abs(fl[0:s_max])/sum(abs(fl[0:s_max])) 
    nffto = abs(fo[0:s_max])/sum(abs(fo[0:s_max]))

    # Store the data
    streak_dict = {}
    streak_dict['band'] = band
    streak_dict['line'] = line
    streak_dict['outB'] = outb
    streak_dict['f_ax'] = f_ax
    streak_dict['fftb'] = fftb
    streak_dict['fftl'] = fftl
    streak_dict['ffto'] = ffto
    streak_dict['nfftb'] = nfftb
    streak_dict['nfftl'] = nfftl
    streak_dict['nffto'] = nffto
    streak_dict['pb'] = pb
    streak_dict['pl'] = pl
    streak_dict['po'] = po
    streak_dict['xc'] = xc
    streak_dict['xl'] = xl
    streak_dict['xh'] = xh
               
    return streak_dict

# Filter and analyze image    
def analyze_frame(frame,x_ax,y_ax,roi={},bg_frame=[],do={}):
    
    # Find pixel sum of image before applying manipulations
    sum_no_filt = frame.sum()
    
    # Set ROI to full image if none specified
    if not roi:
        roi['x_min'] = x_ax[0]
        roi['x_max'] = x_ax[-1]
        roi['y_min'] = y_ax[0]
        roi['y_max'] = y_ax[-1]
        
    # Subtract background image     
    if bg_frame:
        frame = frame - bg_frame
    
    # Cast image as float and apply median filter
    im_float = frame.astype(float)
    im_filt = sig.medfilt2d(im_float)

    # Extract ROI and relevant portions of axes
    x_ind = (x_ax >= roi['x_min']) & (x_ax <= roi['x_max'])
    y_ind = (y_ax >= roi['y_min']) & (y_ax <= roi['y_max'])
    im_roi = im_filt[np.ix_(y_ind,x_ind)]
    x_roi = x_ax[x_ind]
    y_roi = y_ax[y_ind]

    # Find pixel sum and projections of ROI'd image
    pix_sum = im_roi.sum()
    proj_roi_x = im_roi.mean(0)
    proj_roi_y = im_roi.mean(1)

    # Find centroid and RMS
    xBar,xRMS = profile_moments(proj_roi_x,x_roi)
    yBar,yRMS = profile_moments(proj_roi_y,y_roi)
    xMax = max(proj_roi_x)
    xMin = min(proj_roi_x)
    yMax = max(proj_roi_y)
    yMin = min(proj_roi_y)
    
    # Perform Gaussian fits
    guessX = [xMax-xMin,xBar,xRMS,xMin]
    guessY = [yMax-yMin,yBar,yRMS,yMin]
    fitX,resX = gaussFit(x_roi,proj_roi_x,guessX)
    fitY,resY = gaussFit(y_roi,proj_roi_y,guessY)

    # store data
    data_dict = {}
    data_dict['img']    = im_roi
    data_dict['sum']    = pix_sum
    data_dict['x_ax']   = x_roi
    data_dict['y_ax']   = y_roi
    data_dict['proj_x'] = proj_roi_x
    data_dict['proj_y'] = proj_roi_y
    data_dict['amp_x']  = resX[0]
    data_dict['amp_y']  = resY[0]
    data_dict['mean_x'] = resX[1]
    data_dict['mean_y'] = resY[1]
    data_dict['sig_x']  = resX[2]
    data_dict['sig_y']  = resY[2]
    data_dict['off_x']  = resX[3]
    data_dict['off_y']  = resY[3]
    data_dict['fit_x']  = fitX
    data_dict['fit_y']  = fitY
    data_dict['sum_no_filt'] = sum_no_filt

    # device specific analyses
    if do:
        
        # Streak image analysis
        if 'streak' in do.keys():
            streak_data = streak_ana(data_dict,do['streak'])
            data_dict['streak_data'] = streak_data
                     
    return data_dict