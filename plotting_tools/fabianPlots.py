#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:35:21 2017

@author: rieger
"""
import sys
#sys.path.append('/user/rieger/')
from awakeIMClass import *
import numpy as np
import scipy as sp
import matplotlib as mpl
import pickle
import time
import os

'''
Laser zeroDict, pixelvalue and finedelay!
(timeVal and finedelay)
'''
LaserZeroValDict={'1 ns':(480,1.68),'500 ps':(341,6.75),'200 ps':(10,1.85),'100 ps':(10,5.90)}#LaserZeroValDict[japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeRange')]#acess timerange values

'''
Defining the plots for the GUI
'''

def XMPP_beamImage(plotax,fig,fixedaxes,japc,vec,awkLBox,maxVal,PixelLengthProfileFit):
    import time
    # fixedaxes beinhaltet x axis calibration value
    time.sleep(1)#TT41.BTV.412350.STREAK,XMPP-STREAK
    timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData')
    vec=vec.reshape(512,672)
    if maxVal <=0:
        # maxVal = 1.1*np.max(vec[:,300:400].sum()/100/512)
        maxVal=1.5*np.mean(vec[:,315:365])+0.1*np.max(vec[:,315:365])
    plotax.clear()
    plotax.imshow(np.fliplr(vec.T),extent=[timeVal[-1],timeVal[1],fixedaxes[0][0],fixedaxes[0][-1]],vmin=400,vmax=maxVal,aspect='auto',cmap='Blues') 
    
    plotax.set_ylabel('Space (mm)')
    plotax.set_xlabel('Time (ps)')

    PixelLengthProfileFit=int(PixelLengthProfileFit)
    currentFineDelay=awkLBox() #get finedelay setting
    fineDelay,pxTpl=awkLBox[japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeRange')]#acess timerange values
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
    plotax.set_title(str(japc.getParam('XMPP-STREAK/StreakImage#streakImageTime')))
        
def XMPP_ProfilePlot(plotax,fig,fixedaxes,japc,vec,prfLaser,MarkerLaserStageSetValmm,textPos,StagePositionZeroValmm):
    laserSetVal=MarkerLaserStageSetValmm
    import scipy.constants as spc
    import time
    time.sleep(1)
    plotax.clear()
    timeVal=japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeValues')
    vec=japc.getParam('XMPP-STREAK/StreakImage#streakImageData')-400
    currentPos=japc.getParam('AIRTR01/Acq#numericPosition')
    
    '''
    Unverschobener laserwert!
    '''
    delayZeroPos=StagePositionZeroValmm #mm
    delayZeroPs=delayZeroPos*1e-3/spc.c/1e-12 #ps
    ZeroPxVal,ZeroFineDelay=LaserZeroValDict[japc.getParam('XMPP-STREAK/StreakImage#streakImageTimeRange')]
    '''Calc difference'''
    psShiftDelay=2*(currentPos-delayZeroPos)*1e-3/spc.c/1e-12 # in ps, 2* weil zweifacher weg
    print(psShiftDelay)
    # laserSetVal in ps, aber translator ist in mm
    setMMpos=laserSetVal#spc.c/1e12/1e3*laserSetVal+delayZeroPos
    
    if laserSetVal != -1 and laserSetVal != currentPos:
        # setze auf zerovalue!
        japc.setParam('AIRTR01/Setting#positionIn',setMMpos)
    if laserSetVal ==-1:
        japc.setParam('AIRTR01/Setting#positionIn',delayZeroPos)
    
    def gaussFIT1D(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - (x-prm[2])**2 /(2*prm[1]**2)) + prm[3]) -y).ravel()
    
    vecP=vec.reshape(512,672)[:,prfLaser[0]:prfLaser[1]].sum(1)/(prfLaser[1]-prfLaser[0])
    vecP=vecP/np.max(vecP)
    timeVal=np.append(timeVal[1],timeVal[1:])
    plobj1=plotax.plot(np.flipud(timeVal),np.flipud(vecP),c='r',linewidth=2,label='temporal Profile')
    try:
        parentFig=plotax.get_figure()
        if len(parentFig.axes)>3:
            ax2=parentFig.axes[3]
            ax2.clear()
        else:
            ax2=plotax.twiny()
        vecP2=vec.reshape(512,672).sum(0)/(512)
        plobj2=ax2.plot(fixedaxes[0],vecP2/np.max(vecP2),label='Spatial Profile')
    except:
        print('no standard')
        
    try:
        import scipy as sp
        startGuess=[(np.max(vecP)-np.min(vecP))/2,1/100*(timeVal[-1]-timeVal[0]),timeVal[255],10]
        optimres=sp.optimize.least_squares(gaussFIT1D,startGuess,args=(np.flipud(timeVal),np.flipud(vecP)))
  
        print('Finished fit')
        '''Calc TimeWindow Shift'''
        import pytimber
        ldb=pytimber.LoggingDB()
        FineDelayStreak=ldb.get('MPPAWAKE:FASTTRIG-1:STREAKTUBE-FINEDELAY',time.strftime('%Y-%m-%d %H:%M:%S'))['MPPAWAKE:FASTTRIG-1:STREAKTUBE-FINEDELAY'][1][0]
         
        print('Finished getting ldb finedelay value:{0:1.2f}'.format(FineDelayStreak))
        FineDelay=FineDelayStreak-ZeroFineDelay # set shift
        relShift=optimres.x[2]-ZeroPxVal #relative shift measured by laser
        totalShift=FineDelay-(FineDelay+relShift)+psShiftDelay

        print('trying to plot')
        plotax.text(textPos[0],textPos[1],'StageCurrentPosition is {4:3.2f}mm\nStageZeroPosition is {3:3.2f}mm\nMeasured delay shift is:{0:3.0f}ps, set is {1:1.2f}ps\nmarker laser stage shift is:{2:3.0f}ps'.format(totalShift,FineDelay,psShiftDelay,StagePositionZeroValmm,currentPos),bbox=dict(facecolor='red', alpha=0.5))
        
        '''PLot'''
        plobj3=plotax.plot(np.flipud(timeVal),np.flipud(gaussFIT1D(optimres.x,timeVal,0)),c='g',linestyle='dotted',linewidth=1.5,label='Gauss fit: sigma={0:1.2f}ps,   pos in image is {1:3.0f}ps'.format(np.abs(optimres.x[1]),optimres.x[2]))
        legendAll=[l.get_label() for l in plobj1+plobj2+plobj3]
        plotax.legend(plobj1+plobj2+plobj3,legendAll)
    except:
        print('no fitplot')
    #plotax.set_ylim(np.min(vec),1.05*np.max(vec))
    plotax.set_ylim(0,1.05)
    #plotax.set_title('StageZeroPosition is:{0:3.2f}'.format(StagePositionZeroValmm))

'''
Starting the GUI application
'''
    
app = QApplication(sys.argv)
aw = AwakeWindow(["TT41.BCTF.412340/Acquisition#totalIntensityPreferred"],XMPP_beamImage,XMPP_ProfilePlot,fixedaxes=(np.linspace(-8.7,8.7,672),),selector="SPS.USER.AWAKE1",name='AwakeLaserBox Image',XMPP_beamImage={'awkLBox':laserboxMPP,'maxVal':-1,'PixelLengthProfileFit':10},XMPP_ProfilePlot={'MarkerLaserStageSetValmm':-1,'prfLaser':[0,100],'textPos':[0.1,0.2],'StagePositionZeroValmm':72.6},reverse=True)
progname='AwakeSTREAK'
aw.setWindowTitle("%s" % progname)
aw.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))
aw.show()
app.exec_()

