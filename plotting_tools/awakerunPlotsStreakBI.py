#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:35:21 2017

@author: rieger
"""
import sys
#sys.path.append('/user/awakeop/AWAKE_ANALYSIS_TOOLS/plotting_tools/')
from awakeIMClass import *
import numpy as np
import scipy as sp
import matplotlib as mpl
import pickle
import time
import os

'''
Defining the plots for the GUI
'''

def XMPP_beamImage(plotax,fig,fixedaxes,japc,vec,awkLBox,maxVal,PixelLengthProfileFit):
    # fixedaxes beinhaltet x axis calibration value
    time.sleep(1)#TT41.BTV.412350.STREAK,TT41.BTV.412350.STREAK
    timeVal=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageData')
    vec=vec.reshape(512,672)
    if maxVal <=0:
        # maxVal = 1.1*np.max(vec[:,300:400].sum()/100/512)
        maxVal=1.5*np.mean(vec[:,315:365])+0.1*np.max(vec[:,315:365])
    plotax.clear()
    plotax.imshow(np.fliplr(vec.T),extent=[timeVal[-1],timeVal[1],fixedaxes[0][150],fixedaxes[0][-150]],vmin=175,vmax=maxVal,aspect='auto',cmap='Blues') 
    
    plotax.set_ylabel('Space (mm)')
    plotax.set_xlabel('Time (ps)')

    PixelLengthProfileFit=int(PixelLengthProfileFit)
    currentFineDelay=awkLBox() #get finedelay setting
    fineDelay,pxTpl=awkLBox[japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTimeRange')]#acess timerange values
    if fineDelay is not None:
        psShift=(fineDelay-currentFineDelay)*1000
        lowerlim=(512-pxTpl[0])/512*(timeVal[-1]-timeVal[1]) + psShift
        upperlim=(512-pxTpl[1])/512*(timeVal[-1]-timeVal[1]) + psShift
        plotax.plot((upperlim,upperlim),(fixedaxes[0][150],fixedaxes[0][-150]),c='y',linestyle='dotted',linewidth=4)
        plotax.plot((lowerlim,lowerlim),(fixedaxes[0][150],fixedaxes[0][-150]),c='y',linestyle='dotted',linewidth=4,label='LASER BOX')
    
    '''
    thickness plot
    '''
    def gaussFIT1D(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - (x-prm[2])**2 /(2*prm[1]**2)) + prm[3]) -y).ravel()
    try:
        startVals= np.arange(10,490,PixelLengthProfileFit)
        endVals= np.arange(10+PixelLengthProfileFit,500,PixelLengthProfileFit)
        startGuess=[3,1/4*np.abs(fixedaxes[0][0]-fixedaxes[0][-1]),fixedaxes[0][345],400]
        import scipy as sp
        slices=[(vec.T[:,l:k].sum(1)/(np.abs(l-k)))/((vec.T[:,l:k].sum()/(np.abs(l-k)))) for l,k in zip(startVals,endVals)]
        fits=[sp.optimize.least_squares(gaussFIT1D,startGuess,args=(fixedaxes[0],k)) for k in slices]

        parentFig=plotax.get_figure()
        if len(parentFig.axes)>3:
            ax2=parentFig.axes[3]
            ax2.clear()

        else:
            ax2=plotax.twinx()

        ax2.scatter(timeVal[endVals-5],[np.abs(k.x[1]) for k in fits],label='Spatial fits (mm)',s=30,marker='d',c='r')
        ax2.set_ylim(0,np.minimum(np.max([np.abs(k.x[1]) for k in fits])*1.1,5))
    except:
        print('no spatial fit!')
    plotax.set_xlim(timeVal[-1],timeVal[1])
    plotax.set_title(str(japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTime')))
        
def XMPP_PlotFFT(plotax,fig,fixedaxes,japc,vec,historyList):
    time.sleep(0.5)
    plotax.clear()
    timeVal=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTimeValues')
    vec,header=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageData',getHeader=True,unixtime=True)
    vec=vec.reshape(512,672)
    FFT_PRF=np.abs(np.fft.fft(np.hanning(512)*vec[:,300:340].sum(1)))
    F=1/(timeVal[-1]-timeVal[1])*1e3
    FFT_TIME=np.arange(0,512*F,F)
    
    
    
    plobj1=plotax.plot(FFT_TIME,FFT_PRF,linewidth=2.5,label='current FFT')
    axmax=np.minimum(320,np.maximum(320,40*F))
    xticks=np.arange(0,axmax,20)
    plotax.xaxis.set_ticks(xticks)
    plotax.set_xlim(0,axmax)
    plotax.set_ylim(0,np.max(FFT_PRF[3:40])*1.25)
    plotax.set_xlabel('Frequency (GHz)')
    try:
        parentFig=plotax.get_figure()
        if len(parentFig.axes)>4:
            ax2=parentFig.axes[4]
            ax2.clear()
        else:
            ax2=plotax.twinx()
        historyList.append(FFT_PRF)
        if len(historyList)>20:
            del(historyList[0])
        data=np.array(historyList).sum(0)/len(historyList)
        plobj2=ax2.plot(FFT_TIME,data,label='FFT History (20 shots)',c='r',linestyle='dotted')
        ax2.set_xlim(0,axmax)
        ax2.set_ylim(0,np.max(data[3:40])*1.25)
        ax2.xaxis.set_ticks(xticks)
        legendAll=[l.get_label() for l in plobj1+plobj2]
        plotax.legend(plobj1+plobj2,legendAll)
        
    except:
        print('no fft history')
        
    my_gui_vals = japc.getParam('TSG41.AWAKE-XMPP-FFTFREQ/ValueAcquisition#floatValue')
    FFT_MAX_IND = np.argmax(FFT_PRF[3:40]) + 3
    FFT_MAX_VAL = np.max(FFT_PRF[3:40])
    FFT_MAX_FRQ = FFT_TIME[FFT_MAX_IND]
    
    if 'data' in locals():
        AVG_MAX_IND = np.argmax(data[3:40]) + 3
        AVG_MAX_VAL = np.max(data[3:40])
        AVG_MAX_FRQ = FFT_TIME[AVG_MAX_IND]
    else:
        AVG_MAX_VAL = my_gui_vals[9]
        AVG_MAX_FRQ = my_gui_vals[8]
    
    
    my_gui_vals[5] = header['acqStamp']
    my_gui_vals[6] = FFT_MAX_FRQ
    my_gui_vals[7] = FFT_MAX_VAL
    my_gui_vals[8] = AVG_MAX_FRQ
    my_gui_vals[9] = AVG_MAX_VAL
    japc.setParam('TSG41.AWAKE-XMPP-FFTFREQ/ValueSettings#floatValue',my_gui_vals)
    
def XMPP_ProfilePlot(plotax,fig,fixedaxes,japc,vec,prf=[300,400]):
    time.sleep(0.5)
    plotax.clear()
    timeVal=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageData')-175
    def gaussFIT1D(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - (x-prm[2])**2 /(2*prm[1]**2)) + prm[3]) -y).ravel()
    
    vecP=vec.reshape(512,672)[:,prf[0]:prf[1]].sum(1)/(prf[1]-prf[0])
    vecP=vecP/np.max(vecP)
    timeVal=np.append(timeVal[1],timeVal[1:])
    plobj1=plotax.plot(np.flipud(timeVal),np.flipud(vecP),c='r',linewidth=2,label='temporal Profile')
    try:
        parentFig=plotax.get_figure()
        if len(parentFig.axes)>5:
            ax2=parentFig.axes[5]
            ax2.clear()
        else:
            ax2=plotax.twiny()
        vecP2=vec.reshape(512,672).sum(0)/(512)
        plobj2=ax2.plot(fixedaxes[0],vecP2/np.max(vecP2),label='Spatial Profile')
    except:
        print('no standard')
        
    try:
        import scipy as sp
        startGuess=[(np.max(vecP)-np.min(vecP))/2,2/3*(timeVal[-1]-timeVal[0]),timeVal[255],175]
        optimres=sp.optimize.least_squares(gaussFIT1D,startGuess,args=(np.flipud(timeVal),np.flipud(vecP)))
        plobj3=plotax.plot(np.flipud(timeVal),np.flipud(gaussFIT1D(optimres.x,timeVal,0)),c='g',linestyle='dotted',linewidth=1.5,label='Gauss fit: sigma={0:1.2f}'.format(np.abs(optimres.x[1])))
        legendAll=[l.get_label() for l in plobj1+plobj2+plobj3]
        plotax.legend(plobj1+plobj2+plobj3,legendAll)
    except:
        print('no fitplot')
    #plotax.set_ylim(np.min(vec),1.05*np.max(vec))
    plotax.set_ylim(0,1.05)

'''
Starting the GUI application
'''
    
app = QApplication(sys.argv)
aw = AwakeWindow(["TT41.BCTF.412340/Acquisition#totalIntensityPreferred"],XMPP_beamImage,XMPP_PlotFFT,XMPP_ProfilePlot,fixedaxes=(np.linspace(-8.7,8.7,672),),selector="SPS.USER.AWAKE1",name='AwakeLaserBox Image',XMPP_beamImage={'awkLBox':laserboxMPP,'maxVal':-1,'PixelLengthProfileFit':10},XMPP_PlotFFT={'historyList':[]},reverse=True)
progname='AwakeSTREAK'
aw.setWindowTitle("%s" % progname)
aw.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))
aw.show()
app.exec_()
