#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:35:21 2017

@author: rieger & pena
"""
import sys
sys.path.append('/user/rieger/')
from awakeIMClass import *
import numpy as np
import scipy as sp
import matplotlib as mpl
import pickle
import time
import os

slth = 3
filt = 'yes'       #'yes' or 'no'
fstrength = 10
slc = int(512/slth)

def gaus(x,a,x0,sigma,c):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))+c

def bunchAnalysis(vec, slth, x,timeVal):
    from scipy import ndimage

    #time = get_SCtimelabel()                         #get correct timevector
    slc = int(512/slth)                               #compute how many stripes will be analyzed, SLice Count
    time = np.arange(0,timeVal[-1],timeVal[-1]/slc)   #generate a vector for correct plotting dependent on slc
    if filt is 'yes':
        vec = ndimage.median_filter(vec,fstrength)
        print('Image is filtered')

    allgvalues = getGvalues(vec,x,slth)               #compute all parameters for each stripe

    amplitudes = allgvalues[:,0]                      #in counts/intensity
    centroids = allgvalues[:,1]                       #in millimeters
    sigmas = allgvalues[:,2]                          #in millimeters, *1000 for micrometers
    integrals = allgvalues[:,0]*sigmas*np.sqrt(2*np.pi)
    print('End of one Bunch analysis...................................................')
    return amplitudes, centroids, sigmas, integrals, time

def get_SCtimelabel():
    import h5py

    file1 = h5py.File('/user/awakeop/event_data/2017/06/02/1496354911335000000_40_25.h5','r')
    timelabel = list(file1['AwakeEventData']['XMPP-STREAK']['StreakImage']['streakImageTimeValues'])
    timelabel[0] = -8.296966560000001                        #correct the first value
    timelabel[:] = [i+8.296966560000001 for i in timelabel]  #shift all values s.t. we start at time t=0
	
    return timelabel            #time vector for the plots

def getDate(stamp):
    from datetime import datetime
    dt = datetime.fromtimestamp(stamp//1000000000)
    date = dt.strftime('%d-%m-%d %H:%M:%S')
    return date


def getGvalues(streakimage,x,slth):
    from scipy.optimize import curve_fit
    slth = slth                             #SLice THickness
    slc = int(512/slth)                     #SLice Count
    sections = np.arange(0,512,slth)        #sections determined by slth
    allgvalues = np.zeros((slc,4))          #Gauss values for each stripe will be saved here
    c = 0
    #print('x[0] is '+str(x[0])+' and x[-1] is '+str(x[-1]))
    for i in sections:                              #compute the following for all stripes
        if i+slth <=512:                            #check if we run out of image to compute stuff on
            buffero = streakimage[i:i+slth,:]       #selecting the values of the stripe with thickness slth
            line = np.sum(buffero,0)                #summing all values into a line
            #print(line)
            maximum = np.mean(line)*3               #computing guessing values for the gaus fit
            x0 = x[345]
            sigma = 1/4*np.abs(x[0]-x[-1])          #was at *1/10
            c0 = np.mean(line)*0.99
            #print(maximum,x0,sigma,c0)
            try:
                gvalues,error = curve_fit(gaus,x, line, p0=[maximum,x0,sigma,c0])
            except:                                 #fitting was not possible
                gvalues = [0,0,0,0]                 #setting some value
                print('No fitting possible, fit number '+str(c))
            gvalues[2] = np.abs(gvalues[2])
            allgvalues[c] = gvalues
            #print(gvalues)
            c = c+1
        else:
            break
    return allgvalues    #allgvalues has all the parameters of the fitted gaussians per stripe

def ImagePlot(plotax,fig,fixedaxes,japc,vec,something,SliceThickness, YesNoFilter, Filterstrength):
    #TT41.BTV.412350.STREAK,XMPP-STREAK
    print('ImagePlot executed............................................................................')
    import time
    time.sleep(1)
    timestamp=japc.getParam('BOVWA.01TT41.CAM1/ExtractionImage#imageTimeStamp')
    timerange=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeRange')
    timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData').reshape(512,672)

    global slth
    global filt
    global strength
    global slc

    slth = int(SliceThickness)
    filt = YesNoFilter
    fstrength = int(Filterstrength)
    slc = int(512/slth)

    print('slth = '+str(slth))

    if filt is 'yes':
        filtertext = 'ndimage.median_filter('+str(fstrength)+') used'
    else:
        filtertext = ' '


    '''
    im prinzip hast du jetzt:
        bild: vec (512-> timeachse, 672->space achse)
        zeitachse: timeVal (beachte 0. wert ist usually schachsinn)
        x-achse: fixedaxes
        plotaxes (pyplot achse in die man ganz normal plotten kann)
        kannst beliebige berechnungen machen (wie in diesen beispielen gemacht)
    '''
    #print(np.shape(vec))
    if something is None:
        something = 1.1*np.max(vec[:,300:400].sum()/100/512)
    plotax.clear()
    xmin = 250 #250
    xmax = 422 #422 from 672
    vec = vec[:,xmin:xmax]
    plotax.imshow(np.fliplr(vec.T),extent=[timeVal[1],timeVal[-1],fixedaxes[0][xmin],fixedaxes[0][xmax]],vmin=400,vmax=np.mean(vec)*1.9,aspect='auto',cmap='jet')

    amplitudes, centroids, sigmas, integrals, time = bunchAnalysis(vec, slth, fixedaxes[0],timeVal)
    '''
    ax2.plot(time,np.abs(sigmas),'k.')
    
    ax2.set_ylabel('Sigma',color='r')
    ax2.set_xlim(timeVal[-1],timeVal[1])
    '''
    #BOVWA.01TT41.CAM1/ExtractionImage/imageTimeStamp
    date = 'On '+getDate(timestamp)+', '
    text = ', timescale: '+timerange+', '+filtertext
    plotax.set_title(date+str(japc.getParam('XMPP-STREAK/StreakImage#streakImageTime'))+text)
    return


def SigmaAndAmplitude(plotax,fig,fixedaxes,japc,vec,something3):
    plotax.clear()
    timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
    time = np.linspace(timeVal[0],timeVal[-1],timeVal[-1]/slc)
    vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData').reshape(512,672)
    
    import h5py
    from scipy.optimize import curve_fit
    import scipy

    amplitudes, centroids, sigmas, integrals, time = bunchAnalysis(vec, slth, fixedaxes[0],timeVal)

    
    plobj1=plotax.plot(time,sigmas*1000,'b.-',label='Sigma along the bunch')

    plotax.set_ylim(200,900)
    plotax.set_xlim(time[0],time[-1])
    plotax.set_ylabel('Sigma [micrometers]', color='b')
    plotax.yaxis.tick_left()
    #plotax.set_title('Sigma along the bunch')
    plotax.yaxis.set_label_position("left")
    plotax.legend()

    return


def amplitude(plotax,fig,fixedaxes,japc,vec,something,something2):
    plotax.clear()
    timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData').reshape(512,672)

    import h5py
    from scipy.optimize import curve_fit
    import scipy

    amplitudes, centroids, sigmas, integrals, time = bunchAnalysis(vec, slth, fixedaxes[0],timeVal)
    
    #print(amplitudes)

    plobj1=plotax.plot(time,amplitudes,'b.-', label='Amplitude')
    plotax.set_xlim(time[0],time[-1])
    plotax.set_ylabel('Amplitude',color='b')
    #plotax.set_title('Amplitude along the bunch')
    plotax.legend()
    return
	
def centroid(plotax,fig,fixedaxes,japc,vec,something,something2):
    plotax.clear()
    timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData').reshape(512,672)

    import h5py
    from scipy.optimize import curve_fit
    import scipy

    amplitudes, centroids, sigmas, integrals, time = bunchAnalysis(vec, slth, fixedaxes[0],timeVal)
    
    #print(centroids)

    plobj1=plotax.plot(time,centroids,'b.-', label='Centroid')
    plotax.set_xlim(time[0],time[-1])
    plotax.set_ylim(-0.5,0.5)
    plotax.set_ylabel('centroid [mm]',color='b')
    #plotax.set_title('Location of the centroid')
    plotax.legend()
    return
	
def integrals(plotax,fig,fixedaxes,japc,vec,something,something2):
    plotax.clear()
    e=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeRange')

    unit = e[-2]+e[-1]
    timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData').reshape(512,672)

    import h5py
    from scipy.optimize import curve_fit
    import scipy

    amplitudes, centroids, sigmas, integrals, time = bunchAnalysis(vec, slth, fixedaxes[0],timeVal)
    
    plobj1=plotax.plot(time,integrals,'b.-',label='counts/slice')
    plotax.set_xlim(time[0],time[-1])
    plotax.set_xlabel('time ['+unit+']')
    plotax.set_ylabel('counts/slice',color='b')
    #plotax.set_title('Sum of counts per slice')
    plotax.yaxis.set_label_position("left")
    plotax.yaxis.tick_left()
    plotax.legend()

    print('Last function got called...............................................................')
    return

if __name__=='__main__':
    app = QApplication(sys.argv)
    aw = AwakeWindow(["TT41.BCTF.412340/Acquisition#totalIntensityPreferred"],ImagePlot,SigmaAndAmplitude,amplitude,centroid,integrals,fixedaxes=(np.linspace(-8.7,8.7,672),),selector="SPS.USER.AWAKE1",name='Felipe Image',ImagePlot={'something':None,'SliceThickness':slth,'YesNoFilter':'yes','Filterstrength':10},SigmaAndAmplitude={'something3':2},amplitude={'something':None,'something2':2},centroid={'something':None,'something2':2},integrals={'something':None,'something2':2},reverse=True)
    progname='felipePlots'
    aw.setWindowTitle("%s" % progname)
    aw.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))
    aw.show()
    app.exec_()
