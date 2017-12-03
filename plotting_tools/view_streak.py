#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 15:45:04 2017

@author: sgess
"""
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

def view_streak(data_dict,cam,scale,cax,fft_sum=[]):
    
    if len(scale) == 1:
        scale_1 = scale
        scale_2 = scale
    elif len(scale) == 2:
        scale_1 = scale[0]
        scale_2 = scale[1]
    else:
        print('ERROR: Bad scale')
        return

    # get axis
    x_ax = data_dict['x_ax']
    y_ax = data_dict['y_ax']
    f_ax = data_dict['streak_data']['f_ax']
    
    # get image, band, and lineout
    img = data_dict['img']
    band = data_dict['streak_data']['band']
    line = data_dict['streak_data']['line']
    
    # get ffts
    fftb = data_dict['streak_data']['fftb']
    fftl = data_dict['streak_data']['fftl']
    
    # scale and offset profiles so it fits in frame
    noOffD_b = band - min(band)
    noOffD_l = line - min(line)
    noOff_bMaxD = max(noOffD_b)
    noOff_lMaxD = max(noOffD_l)
    x_min = min(x_ax)
    x_max = max(x_ax)
    y_min = min(y_ax)
    y_max = max(y_ax)
    Dscale_b = scale_1*(x_min/noOff_bMaxD)*noOffD_b
    Dscale_l = -scale_2*(x_min/noOff_lMaxD)*noOffD_l
    plot_b = Dscale_b + x_min
    plot_l = -Dscale_l + x_max

    # get band and center indices
    xc = data_dict['streak_data']['xc']
    xl = data_dict['streak_data']['xl']
    xh = data_dict['streak_data']['xh']
    
    # Now make some pretty plots
    fig = plt.figure(1)
    ax = fig.add_subplot(121)
    #plt.pcolormesh(x_ax,y_ax,img,cmap=cm.plasma,clim=cax)
    ax.imshow(img,extent=[x_min,x_max,y_min,y_max],cmap=cm.inferno,clim=cax,aspect='auto')
    fig.colorbar
    ax.plot([xl, xl],[y_min, y_max],'r--',[xh, xh],[y_min, y_max],'r--',[xc, xc],[y_min, y_max],'w--',linewidth=3)
    ax.plot(np.flipud(plot_b),y_ax,'r',plot_l,y_ax,'w',linewidth=3)
    ax.set_ylabel('Time [ps]')
    ax.set_xlabel('X [mm]')
    ax.set_title(cam)

    ax = fig.add_subplot(222)
    ax.semilogy(f_ax,fftb,'r',linewidth=2,label='FFT of Band')
    ax.set_xlim([0,500])
    #ax.set_xlabel('Spectrum [GHz]')
    ax.legend()
    ax.set_title('FFTs')

    ax = fig.add_subplot(224)
    if len(fft_sum) > 1:
        ax.semilogy(f_ax,fft_sum,'k',linewidth=2,label='Running FFT Avg.')
        ax.set_xlim([0,500])
        ax.set_xlabel('Spectrum [GHz]')
        ax.legend()
    else:
        ax.semilogy(f_ax,fftl,'k',linewidth=2,label='FFT of Lineout')
        ax.set_xlim([0,500])
        ax.set_xlabel('Spectrum [GHz]')
        ax.legend()
    #ax.set_title('FFT of Lineout')
    
    #plt.show()
    return fig
