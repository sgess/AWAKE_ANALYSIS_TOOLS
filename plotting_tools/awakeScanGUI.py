from __future__ import unicode_literals

"""
Spencer tries to make a thing
Karl copied it, because Karls QVBoxLayout doesnt like him, but spencers behaves well.. good boy
"""

''' Get all the things '''
import sys
import time
import os
import matplotlib as mpl
# Make sure that we are using QT5
mpl.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

import numpy as np
import pyjapc
import awakeIMClass
import scipy.special as special

from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QComboBox, QCheckBox, QMessageBox, QGroupBox, QFormLayout,
    QTextEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication, QPushButton, QSizePolicy, QStatusBar)
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import (QIcon, QDoubleValidator, QRegExpValidator)
from PyQt5 import QtCore, QtWidgets

''' This is where my code starts '''
class awakeScanGui(QWidget):


    ''' Init Self '''
    def __init__(self,*args):
        super().__init__()
        self.initScans(*args)
        self.initUI()

    ''' Initialize GUI '''
    def initUI(self):

        #self.connect(self,QtCore.Signal('triggered()'),self.closeEvent)
        #self.file_menu = QtWidgets.QMenu('&File', self)
        #self.file_menu.addAction('&Quit', self.closeEvent,QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        #self.menuBar().addMenu(self.file_menu)
        
        # Create a combobox for selecting camera
        self.selectScan = QLabel('Select Scan:')
        self.scanList = QComboBox(self)
        self.scanList.addItems(list(self.scanFunDict.keys()))
        self.scanList.currentIndexChanged.connect(self.selectScanFun)

        self.btnStart = QPushButton('Start', self)
        self.btnStart.setStyleSheet("background-color:#63f29a")
        self.btnStart.clicked[bool].connect(self.doStart)
        self.btnStop = QPushButton('Stop', self)
        self.btnStop.setStyleSheet("background-color:#63f29a")
        self.btnStop.clicked[bool].connect(self.doStop)

        # Create a group box for camera properties
        prop_box = QGroupBox('Camera Properties')
        self.inpNShot = QLineEdit(self)
        self.inpNShot.setValidator(QDoubleValidator(-100000,100000,4))
        self.inpAnfang = QLineEdit(self)
        self.inpAnfang.setValidator(QDoubleValidator(-100000,100000,4))
        self.inpEnde = QLineEdit(self)
        self.inpEnde.setValidator(QDoubleValidator(-100000,100000,4))
        self.inpStep = QLineEdit(self)
        self.inpStep.setValidator(QDoubleValidator(-100000,100000,4))
        self.inpSavestr = QLineEdit(self)
        self.regExp=QtCore.QRegExp('^.*$')# accept everything
        self.inpSavestr.setValidator(QRegExpValidator(self.regExp))
        #self.inpSavestr.setValidator(QRegExpValidator('^ .*$'))
        prop_form = QFormLayout()
        prop_form.addRow('Number of Shots (empty=5):',self.inpNShot)
        prop_form.addRow('Start Value:',self.inpAnfang)
        prop_form.addRow('End Value:',self.inpEnde)
        prop_form.addRow('Step Value:',self.inpStep)
        prop_form.addRow('Savestring (empty = no save):',self.inpSavestr)
        prop_box.setLayout(prop_form)
        
        # Create a plotting window
        self.main_widget = QWidget(self)
        def lpass(x,*args):
            pass
        self.screen=awakeIMClass.awakeScreen(lpass,parent=self.main_widget)
        # Create Status Bar 
        self.statusBar = QStatusBar(self)
        self.statusBar.setSizeGripEnabled(False)

        # Create Layout
        self.vbox = QVBoxLayout()
        
        self.vbox.addWidget(self.selectScan)
        self.vbox.addWidget(self.scanList)
        self.vbox.addWidget(self.btnStart)
        self.vbox.addWidget(self.btnStop)
        self.vbox.addWidget(prop_box)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.statusBar)
                    
        self.hbox = QHBoxLayout()
        self.hbox.addLayout(self.vbox)
        self.hbox.addStretch()
        self.hbox.addWidget(self.screen, QtCore.Qt.AlignRight)
        self.setLayout(self.hbox)
            
        
        self.setGeometry(1600, 300, 900, 500)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))

        self.setWindowTitle('Streak scan selector')
        self.show()
        self.statusBar.showMessage('Here speaks God, give Gandalf your Ring!')

        print('Init screen')
        self.hbox.removeWidget(self.screen)
        self.screen=self.activeScan.finfun
        self.screen.setParent(self.main_widget)
        self.hbox.addWidget(self.screen, QtCore.Qt.AlignRight)

        
    def closeEvent(self, event):
        self.doStop()
        #QCoreApplication.quit()
        
        #QWidget.closeEvent(self, event)
        
        
    def doStart(self):
        self.doStop()
        buffMax=self.inpNShot.text()
        savestr=self.inpSavestr.text()
        if buffMax !='':
            try:
                self.activeScan.MaxCall=np.float(buffMax)
            except:
                self.statusBar.showMessage('Error: Number of shots could not be converted to float')
                raise ValueError('No float constructable for N shot!')
        try:
            start=np.float(self.inpAnfang.text())
            end=np.float(self.inpEnde.text())
            step=np.float(self.inpStep.text())
        except:
            self.statusBar.showMessage('Error: one or more of start,end,stop could be converted to float!')
            raise ValueError('One or more of start,end,stop could be converted to float!')
        self.activeScan.ScanList=np.arange(start,end,step)
        print(self.activeScan.ScanList)
        if savestr != '':
            self.activeScan.file_string=savestr
            self.activeScan.savePickle=True
        else:
            self.activeScan.savePickle=False
        self.statusBar.showMessage('Acquiring!')
        self.activeScan.start()
        return
        
    def doStop(self):
        self.activeScan.stop()
        self.statusBar.showMessage('Stopped the acquisition!',5)
        return

    def about(self):
        QtWidgets.QMessageBox.about(self, "About","""A single Awake window, able to show something nice""")
        
    def initScans(self,*args):
        self.activeScan=None
        self.scanFunDict={}

        zeroname=''
        i=0
        for k in args:
            if isinstance(k,list):
                for l in k:
                    if not isinstance(l,awakeLoop):
                        raise IOError('please provide awakeLoop instance')
                    #self.scanFunDict[l.name]=l
                    if i==0:
                       i+=1
                       zeroname=l.name
                    # speichere nicht die awakeloop sondern nur die argumente fÃ¼r sie
                    subList=[]
                    for m in l.subs.subNum.keys():
                        subList+=[l.subs.subNum[m]]
                    self.scanFunDict[l.name]={'subs':subList,'finfun':l.finfun,'scanList':l.ScanList,'wkQue':l.callFKT,'checkBeam':l.checkBeam,'selector':l.subs.selector,'savestr':l.file_string,'name':l.name}
                if i==1:
                    i+=1
                    self.activeScan=awakeIMClass.awakeLoop(**self.scanFunDict[zeroname])
            else:
                #speichere nur die argumente fuer awakeloop
                #self.scanFunDict[k.name]=k
                subList=[]
                for m in k.subs.subNum.keys():
                    subList+=[k.subs.subNum[m]]
                self.scanFunDict[k.name]={'subs':subList,'finfun':k.finfun,'scanList':k.ScanList,'wkQue':k.callFKT,'checkBeam':k.checkBeam,'selector':k.subs.selector,'savestr':k.file_string,'name':k.name}
                if i==0:
                   i+=1
                   print(k.name)
                   self.activeScan=awakeIMClass.awakeLoop(**self.scanFunDict[k.name])
        if not isinstance(args[0],list):
            # not working atm!
            print('Passing atm')#self.activeScan=args[0]
        else:
            # not working atm!
            print('Passing list atm')
            #self.activeScan=args[0][0]

    def selectScanFun(self,l):
        #self.activeScan=self.scanFunDict[self.scanList.currentText()]
        #del(self.activeScan)
        self.activeScan=None
        print(self.scanFunDict[self.scanList.currentText()])
        kwargs=self.scanFunDict[self.scanList.currentText()]
        self.activeScan=awakeIMClass.awakeLoop(**kwargs)
        print('Now self.activeScan')
        self.activeScan.print()
        if self.activeScan.finfun is not None and isinstance(self.activeScan.finfun,awakeIMClass.awakeScreen):
            self.hbox.removeWidget(self.screen)
            self.screen=self.activeScan.finfun
            self.screen.setParent(self.main_widget)
            self.hbox.addWidget(self.screen, QtCore.Qt.AlignRight)
            

                

def TimeBeamScanXMPP(japc,scanListElem,subs):
    import time
    time.sleep(0.5)
    BeamInten=subs.get()[1]
    posREAD=japc.getParam('VTUAwake3FT1/Mode#pdcOutDelay')
    japc.setParam('VTUAwake3FT1/Mode#pdcOutDelay',scanListElem)
    time=japc.getParam('XMPP-STREAK/StreakImage#streakImageTime')
    return {'posRead':posREAD,'posSet':scanListElem,'StreakImageTime':time,'BeamIntensity':BeamInten}
def finfunT ( ax,japc,result,*args):
    ax.plot([1,2,3,4,5])
    return True
TimeScanFinalXMPP=awakeIMClass.awakeScreen(finfunT)
TimeScanXMPP_L=awakeIMClass.awakeLoop("TT41.BCTF.412340/Acquisition#totalIntensityPreferred",TimeBeamScanXMPP,None,finfun=TimeScanFinalXMPP)

def SlitScanXMPP(japc,scanListElem,subs):
    import time
    import scipy as sp
    time.sleep(0.5)
    print('SlitScanXMPP called!')
    BeamInten=subs.get()[1]
    posREAD=japc.getParam("MPP-TSG41-MIRROR1-V/Position#position")
    japc.setParam("MPP-TSG41-MIRROR1-V/MoveTo#position",scanListElem)
    #posREAD=scanListElem
    posSET=scanListElem
    print(scanListElem)
    imData=japc.getParam("XMPP-STREAK/StreakImage#streakImageData").reshape(512,672)
    imData=imData-np.mean(imData[0:25,:])
    startGuess=np.array([4e3,16,345,260,50])
    def gaussFIT(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - ((x[0]-prm[2])**2 + (x[1]-prm[3])**2)/(2*prm[1]**2)) + prm[4]) -y).ravel()
    x,y=np.meshgrid(np.arange(250,450),np.arange(245,267))
    INTEN=(imData[240:275,280:420]).sum()#(imData[240:275,280:420]-np.mean(imData[240:275,0:140])).sum()
    time=japc.getParam('XMPP-STREAK/StreakImage#streakImageTime')
    optimres=sp.optimize.least_squares(gaussFIT,startGuess,args=([x,y],imData[245:267,250:450]))
    return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'fitParam':optimres,'measBeamIntensity':INTEN,'ImageData':imData}
def SlitScanFinXMPP( ax,japc,result,*args):
    import scipy.optimize as sp_o
    def modelFit(x,prm1,prm2,prm3,prm4):
        return prm1*prm2*(special.erf((prm3-x)/prm2)-special.erf((prm4-x)/prm2) )

    listR=[]
    for k in result:
        listR+=k
    posread=np.array([l['posRead'] for l in listR])
    beamInten=np.array([l['measBeamIntensity']/l['BeamIntensity'] for l in listR])
    beamInten=beamInten/np.max(beamInten)
    yFitVal=np.array([l['fitParam'].x[3]-257 for l in listR])

    #
    # Fit the double error function model
    #
    
    argSorted=np.argsort(posread)
    scatterX_inten=posread[argSorted]
    beamInten=beamInten[argSorted]
    xvals_inten=np.array([scatterX_inten[k] for k in range(0,len(scatterX_inten)-1) if ((scatterX_inten[k-1]<scatterX_inten[k] or k==0) and scatterX_inten[k+1]==scatterX_inten[k])])
    shiftvals_inten=[0]
    shiftvals_inten+=[k+1 for k in range(0,len(scatterX_inten)-1) if (scatterX_inten[k]<scatterX_inten[k+1] or k==len(scatterX_inten)-1)]
    shiftvals_inten+=[len(scatterX_inten)]
    
    yvals_inten=[np.array(beamInten[shiftvals_inten[k]:shiftvals_inten[k+1]]) for k in range(0,len(shiftvals_inten)-1)]
    inten_mean=np.array([np.mean(k) for k in yvals_inten if k.size>1])
    scale=np.max(inten_mean)
    inten_std=np.array([np.sqrt(np.var(k)) for k in yvals_inten if k.size>1])
    
    print(xvals_inten,inten_mean,scale,inten_std)
    print(beamInten)

    popt,pcov=sp_o.curve_fit(modelFit,xvals_inten,inten_mean,[1,50,7275,7150],sigma=inten_std)
    xfit=np.linspace(xvals_inten[0],xvals_inten[-1],200)
    print(popt)
    print(pcov)
    #
    # plot
    #
    ax.clear()
    ax.scatter(posread,beamInten,c='r',label='Data')
    ax.errorbar(xvals_inten,inten_mean,inten_std,label='Mean + standard error',c='b',linestyle='None',marker='x')
    #ax.plot(xfit,modelFit(xfit,*popt),c='k',label='PRM: {0:1.2e},{1:1.2e},{2:1.3e},{3:1.3e}\nCOV: {4:1.2e},{5:1.2e},{6:1.3e},{7:1.3e}'.format(popt[0],popt[1],popt[2],popt[3],np.sqrt(pcov[0,0],np.sqrt(pcov[1,1]),np.sqrt(pcov[2,2]),np.sqrt(pcov[3,3]))))
    ax.plot(xfit,modelFit(xfit,popt[0],popt[1],popt[2],popt[3]),c='k',label='Fit, optimum parameter={0:1.3e}'.format(np.abs(popt[2]+popt[3])/2))

    ax.legend()
    #ax.scatter(posread,yFitVal,c='b')
    ax.set_ylim(0.9*np.min(inten_mean),1.1*np.max(inten_mean))
    return True
SlitScanFinalXMPP_L=awakeIMClass.awakeScreen(SlitScanFinXMPP)
SlitScanXMPP_L=awakeIMClass.awakeLoop("TT41.BCTF.412340/Acquisition#totalIntensityPreferred",SlitScanXMPP,None,finfun=SlitScanFinalXMPP_L)

def FocusScanXMPP(japc,scanListElem,subs):
    import time
    import scipy as sp
    print('Called FocusScanXMPP!')
    time.sleep(0.5)
    '''
    old translator!, new one is MPP-TSG41-TRANSL1-BI!
    '''
    #posREAD=japc.getParam("MPP-TSG41-TRANSL1/Position#position")
    posREAD=japc.getParam("MPP-TSG41-TRANSL1-BI/Position#position")
    #posREAD=scanListElem
    imData=japc.getParam("XMPP-STREAK/StreakImage#streakImageData").reshape(512,672)
    time=japc.getParam('XMPP-STREAK/StreakImage#streakImageTime')

    #japc.setParam("MPP-TSG41-TRANSL1/MoveTo#position",scanListElem)
    japc.setParam("MPP-TSG41-TRANSL1-BI/MoveTo#position",scanListElem)
    posSET=scanListElem
    BeamInten=subs.get()[1]
    
    startGuess=np.array([4e3,16,345,255,50])
    def gaussFIT(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - ((x[0]-prm[2])**2 + (x[1]-prm[3])**2)/(2*prm[1]**2)) + prm[4]) -y).ravel()
    def gaussFIT1D(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - ((x-prm[2])**2)/(2*prm[1]**2)) + prm[3]) -y).ravel()

    print('Before inten')
    INTEN=np.sum(imData[:,200:450]-np.mean(imData[:,:200]))
    x,y=np.meshgrid(np.arange(100,500),np.arange(245,270))
    optimres=sp.optimize.least_squares(gaussFIT,startGuess,args=([x,y],imData[245:270,100:500]))
    print('fits')
    optimres_1d=sp.optimize.least_squares(gaussFIT1D,[INTEN,15,330,10],args=(np.arange(100,500),imData[245:270,100:500].sum(0)/25))
    
    ''' Automatic steering '''
     
    delMR=10
    posMR=japc.getParam("MPP-TSG41-MIRROR1-V/Position#position")
    if optimres.x[3] <= 240:
        japc.setParam("MPP-TSG41-MIRROR1-V/MoveTo#position",posMR+delMR)
        chMR=posMR
    if optimres.x[3] >= 272:
        japc.setParam("MPP-TSG41-MIRROR1-V/MoveTo#position",posMR-delMR)
    
    
    return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'fitParam':optimres,'measBeamIntensity':INTEN,'MirrorSteering:':posMR,'ImageData':imData,'optimres_1d':optimres_1d}
    #return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'fitParam':optimres,'measBeamIntensity':INTEN,'MirrorSteering:':1,'ImageData':imData}
def FocusScanFinXMPP( ax,japc,result,*args):
    print('1')
    listR=[]
    for k in result:
        listR+=k
    #print(listR)
    posread=np.array([l['posRead'] for l in listR])
    print('2')
    beamSize=np.array([np.abs(l['fitParam'].x[1]) for l in listR])# [k for k in listR]])
    print('3')
    beamSize_1d=np.array([np.abs(l['optimres_1d'].x[1]) for l in listR])#[k for k in listR]])

    print(beamSize,beamSize_1d)
    #
    # cut
    #
    #argsBig=np.where(beamSize<40)
    #posread=posread[argsBig]
    #posread=posread[np.where(beamSize[argsBig]>10)]
    #beamSize=beamSize[argsBig]
    #beamSize=beamSize[np.where(beamSize[argsBig]>10)]
    beamInten=beamSize

    print(beamInten)

    argSorted=np.argsort(posread)
    scatterX_inten=posread[argSorted]
    beamInten=beamInten[argSorted]
    beamInten_1d=beamSize_1d[argSorted]
    xvals_inten=np.array([scatterX_inten[k] for k in range(0,len(scatterX_inten)-1) if ((scatterX_inten[k-1]<scatterX_inten[k] or k==0) and scatterX_inten[k+1]==scatterX_inten[k])])
    shiftvals_inten=[0]
    shiftvals_inten+=[k+1 for k in range(0,len(scatterX_inten)-1) if (scatterX_inten[k]<scatterX_inten[k+1] or k==len(scatterX_inten)-1)]
    shiftvals_inten+=[len(scatterX_inten)]

    print('4')
    yvals_inten=[np.array(beamInten[shiftvals_inten[k]:shiftvals_inten[k+1]]) for k in range(0,len(shiftvals_inten)-1)]
    inten_mean=np.array([np.mean(k) for k in yvals_inten if k.size>1])
    inten_std=np.array([np.sqrt(np.var(k)) for k in yvals_inten if k.size>1])

    yvals_inten1d=[np.array(beamInten_1d[shiftvals_inten[k]:shiftvals_inten[k+1]]) for k in range(0,len(shiftvals_inten)-1)]
    inten_mean1d=np.array([np.mean(k) for k in yvals_inten1d if k.size>1])
    inten_std1d=np.array([np.sqrt(np.var(k)) for k in yvals_inten1d if k.size>1])


    print(inten_mean,inten_mean1d)
    
    poly=np.polyfit(xvals_inten,inten_mean,2,w=1/inten_std)
    poly1d=np.polyfit(xvals_inten,inten_mean1d,2,w=1/inten_std1d)
    polyX=np.linspace(xvals_inten[0],xvals_inten[-1],200)
    polyY=lambda x,prm: prm[0]*x**2+ prm[1]*x**1+ prm[2]
    #
    # plot
    #
    #print(poly,xvals_inten,inten_mean,inten_std)
    #print(posread,beamSize)
    ax.clear()
    ax.plot(np.linspace(xvals_inten[0],xvals_inten[-1],200),polyY(polyX,poly),label='Full beam, Quadratic fit:{0:1.3e}*x^2+{1:1.3e}*x+{2:1.3e}'.format(poly[0],poly[1],poly[2]))
    ax.plot(np.linspace(xvals_inten[0],xvals_inten[-1],200),polyY(polyX,poly1d),label='Projected beam, Quadratic fit:{0:1.3e}*x^2+{1:1.3e}*x+{2:1.3e}'.format(poly1d[0],poly1d[1],poly1d[2]))

    ax.errorbar(xvals_inten,inten_mean,inten_std,linestyle='None',label='Mean data')
    ax.errorbar(xvals_inten,inten_mean1d,inten_std1d,linestyle='None',label='Mean data, projection',c='r')

    #ax.plot(xvals_inten,inten_mean,linestyle='None',label='Mean data')
    ax.scatter(posread,beamSize,label='Raw data')
    ax.scatter(posread,beamSize_1d,label='Raw data, projection')
    
    ax.set_ylim(0,75)
    ax.legend()
    return True
FocusScanFinal=awakeIMClass.awakeScreen(FocusScanFinXMPP)
FocusScanXMPP_L=awakeIMClass.awakeLoop("TT41.BCTF.412340/Acquisition#totalIntensityPreferred",FocusScanXMPP,None,finfun=FocusScanFinal)

def FocusPartScanXMPP(japc,scanListElem,subs):
    import time
    import scipy as sp
    print('Called FocusScanXMPP!')
    time.sleep(0.5)
    '''
    old translator!, new one is MPP-TSG41-TRANSL1-BI!
    '''
    #posREAD=japc.getParam("MPP-TSG41-TRANSL1/Position#position")
    posREAD=japc.getParam("MPP-TSG41-TRANSL1-BI/Position#position")
    #posREAD=scanListElem
    imData=japc.getParam("XMPP-STREAK/StreakImage#streakImageData").reshape(512,672)
    time=japc.getParam('XMPP-STREAK/StreakImage#streakImageTime')

    #japc.setParam("MPP-TSG41-TRANSL1/MoveTo#position",scanListElem)
    japc.setParam("MPP-TSG41-TRANSL1-BI/MoveTo#position",scanListElem)
    posSET=scanListElem
    BeamInten=subs.get()[1]

    def gaussFIT(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - ((x-prm[2])**2)/(2*prm[1]**2)) + prm[3]) -y).ravel()
    INTEN=np.sum(imData[250:260,200:450]-np.mean(imData[:,:250]))
    startGuess=np.array([Inten,15,330,380])
    x=np.arange(200,450)
    optimres=sp.optimize.least_squares(gaussFIT,startGuess,args=(x,imData[245:270,200:450].sum(0)/25))

    ''' Automatic steering '''

    return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'fitParam':optimres,'measBeamIntensity':INTEN,'ImageData':imData}
    #return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'fitParam':optimres,'measBeamIntensity':INTEN,'MirrorSteering:':1,'ImageData':imData}
def FocusPartScanFinXMPP( ax,japc,result,*args):
    listR=[]
    for k in result:
        listR+=k
    posread=np.array([l['posRead'] for l in [k for k in listR]])
    beamSize=np.array([l['fitParam'].x[1] for l in [k for k in listR]])

    print(beamSize)
    #
    # cut
    #
    #argsBig=np.where(beamSize<40)
    #posread=posread[argsBig]
    #posread=posread[np.where(beamSize[argsBig]>10)]
    #beamSize=beamSize[argsBig]
    #beamSize=beamSize[np.where(beamSize[argsBig]>10)]
    beamInten=beamSize

    print(beamInten)

    argSorted=np.argsort(posread)
    scatterX_inten=posread[argSorted]
    beamInten=beamInten[argSorted]
    xvals_inten=np.array([scatterX_inten[k] for k in range(0,len(scatterX_inten)-1) if ((scatterX_inten[k-1]<scatterX_inten[k] or k==0) and scatterX_inten[k+1]==scatterX_inten[k])])
    shiftvals_inten=[0]
    shiftvals_inten+=[k+1 for k in range(0,len(scatterX_inten)-1) if (scatterX_inten[k]<scatterX_inten[k+1] or k==len(scatterX_inten)-1)]
    shiftvals_inten+=[len(scatterX_inten)]

    yvals_inten=[np.array(beamInten[shiftvals_inten[k]:shiftvals_inten[k+1]]) for k in range(0,len(shiftvals_inten)-1)]
    inten_mean=np.array([np.mean(k) for k in yvals_inten if k.size>1])
    inten_std=np.array([np.sqrt(np.var(k)) for k in yvals_inten if k.size>1])

    print(inten_mean)

    poly=np.polyfit(xvals_inten,inten_mean,2,w=1/inten_std)
    polyX=np.linspace(xvals_inten[0],xvals_inten[-1],200)
    polyY=lambda x,prm: prm[0]*x**2+ prm[1]*x**1+ prm[2]
    #
    # plot
    #
    #print(poly,xvals_inten,inten_mean,inten_std)
    #print(posread,beamSize)
    ax.clear()
    ax.plot(np.linspace(xvals_inten[0],xvals_inten[-1],200),polyY(polyX,poly),label='Quadratic fit:{0:1.3e}*x^2+{1:1.3e}*x+{2:1.3e}'.format(poly[0],poly[1],poly[2]))
    ax.errorbar(xvals_inten,inten_mean,inten_std,linestyle='None',label='Mean data')
    #ax.plot(xvals_inten,inten_mean,linestyle='None',label='Mean data')
    ax.scatter(posread,beamSize,label='Raw data')
    ax.set_ylim(0,75)
    ax.legend()
    return True
FocusPartScanFinal=awakeIMClass.awakeScreen(FocusPartScanFinXMPP)
FocusPartScanXMPP_L=awakeIMClass.awakeLoop("TT41.BCTF.412340/Acquisition#totalIntensityPreferred",FocusPartScanXMPP,None,finfun=FocusPartScanFinal)

def FocusScanBI(japc,scanListElem,subs):
    import time
    import scipy as sp
    time.sleep(0.5)
    print('FocusScanBI called!')
    BeamInten=subs.get()[1]
    posREAD=japc.getParam("BTV.TT41.412350_FOCUS/Position#position")
    japc.setParam("BTV.TT41.412350_FOCUS/MoveTo#position",scanListElem)
    #posREAD=scanListElem
    posSET=scanListElem
    print(scanListElem)
    imData=japc.getParam("TT41.BTV.412350.STREAK/StreakImage#streakImageData").reshape(512,672)
    imData=imData-np.mean(imData[:,50:100])
    def gaussFIT(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - ((x-prm[2])**2)/(2*prm[1]**2)) + prm[3]) -y).ravel()
    x=np.arange(250,450)
    INTEN=(imData[:,280:420]).sum()#(imData[240:275,280:420]-np.mean(imData[240:275,0:140])).sum()
    startGuess=np.array([INTEN,16,345,10])
    time=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTime')
    optimres=sp.optimize.least_squares(gaussFIT,startGuess,args=(x,imData[:,250:450].sum(0)))
    return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'fitParam':optimres,'measBeamIntensity':INTEN,'ImageData':imData}
def FocusScanFinBI( ax,japc,result,*args):    
    listR=[]
    for k in result:
        listR+=k
    posread=np.array([l['posRead'] for l in [k for k in listR]])
    beamSize=np.array([l['fitParam'].x[1] for l in [k for k in listR]])

    print(beamSize)
    #
    # cut
    #
    #argsBig=np.where(beamSize<40)
    #posread=posread[argsBig]
    #posread=posread[np.where(beamSize[argsBig]>10)]
    #beamSize=beamSize[argsBig]
    #beamSize=beamSize[np.where(beamSize[argsBig]>10)]
    beamInten=beamSize

    print(beamInten)

    argSorted=np.argsort(posread)
    scatterX_inten=posread[argSorted]
    beamInten=beamInten[argSorted]
    xvals_inten=np.array([scatterX_inten[k] for k in range(0,len(scatterX_inten)-1) if ((scatterX_inten[k-1]<scatterX_inten[k] or k==0) and scatterX_inten[k+1]==scatterX_inten[k])])
    shiftvals_inten=[0]
    shiftvals_inten+=[k+1 for k in range(0,len(scatterX_inten)-1) if (scatterX_inten[k]<scatterX_inten[k+1] or k==len(scatterX_inten)-1)]
    shiftvals_inten+=[len(scatterX_inten)]

    yvals_inten=[np.array(beamInten[shiftvals_inten[k]:shiftvals_inten[k+1]]) for k in range(0,len(shiftvals_inten)-1)]
    inten_mean=np.array([np.mean(k) for k in yvals_inten if k.size>1])
    inten_std=np.array([np.sqrt(np.var(k)) for k in yvals_inten if k.size>1])

    print(inten_mean)

    poly=np.polyfit(xvals_inten,inten_mean,2,w=1/inten_std)
    polyX=np.linspace(xvals_inten[0],xvals_inten[-1],200)
    polyY=lambda x,prm: prm[0]*x**2+ prm[1]*x**1+ prm[2]
    #
    # plot
    #
    #print(poly,xvals_inten,inten_mean,inten_std)
    #print(posread,beamSize)
    ax.clear()
    ax.plot(np.linspace(xvals_inten[0],xvals_inten[-1],200),polyY(polyX,poly),label='Quadratic fit:{0:1.3e}*x^2+{1:1.3e}*x+{2:1.3e}'.format(poly[0],poly[1],poly[2]))
    ax.errorbar(xvals_inten,inten_mean,inten_std,linestyle='None',label='Mean data')
    #ax.plot(xvals_inten,inten_mean,linestyle='None',label='Mean data')
    ax.scatter(posread,beamSize,label='Raw data')
    ax.set_ylim(0,75)
    ax.legend()
    return True
FocusScanFinalBI=awakeIMClass.awakeScreen(FocusScanFinBI)
FocusScanBI_L=awakeIMClass.awakeLoop("TT41.BCTF.412340/Acquisition#totalIntensityPreferred",FocusScanBI,None,finfun=FocusScanFinalBI)

def StreakScanBI(japc,scanListElem,subs):
    import time
    import scipy as sp
    time.sleep(0.5)
    print('SlitScanBI called!')
    BeamInten=subs.get()[1]
    posREAD=japc.getParam("BTV.TT41.412350_STREAK_V/Position#position")
    japc.setParam("BTV.TT41.412350_STREAK_V/MoveTo#position",scanListElem)
    #posREAD=scanListElem
    posSET=scanListElem
    print(scanListElem)
    imData=japc.getParam("TT41.BTV.412350.STREAK/StreakImage#streakImageData").reshape(512,672)
    imData=imData-np.mean(imData[:,20:100])
    def gaussFIT(prm,x,y):
        return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - ((x-prm[2])**2)/(2*prm[1]**2)) + prm[3]) -y).ravel()
    x=np.arange(250,450)
    INTEN=(imData[:,280:420]).sum()#(imData[240:275,280:420]-np.mean(imData[240:275,0:140])).sum()
    startGuess=np.array([INTEN,16,345,10])
    time=japc.getParam('TT41.BTV.412350.STREAK/StreakImage#streakImageTime')
    optimres=sp.optimize.least_squares(gaussFIT,startGuess,args=(x,imData[240:270,250:450].sum(0)))
    return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'fitParam':optimres,'measBeamIntensity':INTEN,'ImageData':imData}

def StreakScanFinBI( ax,japc,result,*args):
    import scipy.optimize as sp_o
    def modelFit(x,prm1,prm2,prm3,prm4):
        return prm1*prm2*(special.erf((prm3-x)/prm2)-special.erf((prm4-x)/prm2) )

    listR=[]
    for k in result:
        listR+=k
    posread=np.array([l['posRead'] for l in listR])
    beamInten=np.array([l['measBeamIntensity']/l['BeamIntensity'] for l in listR])
    beamInten=beamInten/np.max(beamInten)
    yFitVal=np.array([l['fitParam'].x[0] for l in listR])

    #
    # Fit the double error function model
    #

    argSorted=np.argsort(posread)
    scatterX_inten=posread[argSorted]
    beamInten=beamInten[argSorted]
    xvals_inten=np.array([scatterX_inten[k] for k in range(0,len(scatterX_inten)-1) if ((scatterX_inten[k-1]<scatterX_inten[k] or k==0) and scatterX_inten[k+1]==scatterX_inten[k])])
    shiftvals_inten=[0]
    shiftvals_inten+=[k+1 for k in range(0,len(scatterX_inten)-1) if (scatterX_inten[k]<scatterX_inten[k+1] or k==len(scatterX_inten)-1)]
    shiftvals_inten+=[len(scatterX_inten)]

    yvals_inten=[np.array(beamInten[shiftvals_inten[k]:shiftvals_inten[k+1]]) for k in range(0,len(shiftvals_inten)-1)]
    inten_mean=np.array([np.mean(k) for k in yvals_inten if k.size>1])
    scale=np.max(inten_mean)
    inten_std=np.array([np.sqrt(np.var(k)) for k in yvals_inten if k.size>1])

    print(xvals_inten,inten_mean,scale,inten_std)
    print(beamInten)

    #opt,pcov=sp_o.curve_fit(modelFit,xvals_inten,inten_mean,[1,50,7275,7150],sigma=inten_std)
    #xfit=np.linspace(xvals_inten[0],xvals_inten[-1],200)
    print(popt)
    print(pcov)
    #
    # plot
    #
    ax.clear()
    ax.scatter(posread,beamInten,c='r',label='Data')
    ax.errorbar(xvals_inten,inten_mean,inten_std,label='Mean + standard error',c='b',linestyle='None',marker='x')
    #ax.plot(xfit,modelFit(xfit,*popt),c='k',label='PRM: {0:1.2e},{1:1.2e},{2:1.3e},{3:1.3e}\nCOV: {4:1.2e},{5:1.2e},{6:1.3e},{7:1.3e}'.format(popt[0],popt[1],popt[2],popt[3],np.sqrt(pcov[0,0],np.sqrt(pcov[1,1]),np.sqrt(pcov[2,2]),np.sqrt(pcov[3,3]))))
    #ax.plot(xfit,modelFit(xfit,popt[0],popt[1],popt[2],popt[3]),c='k',label='Fit, optimum parameter={0:1.3e}'.format(np.abs(popt[2]+popt[3])/2))

    ax.legend()
    #ax.scatter(posread,yFitVal,c='b')
    ax.set_ylim(0.9*np.min(inten_mean),1.1*np.max(inten_mean))
    return True
StreakIntenScanFinalBI=awakeIMClass.awakeScreen(StreakScanFinBI)
StreakIntenScanBI_L=awakeIMClass.awakeLoop("TT41.BCTF.412340/Acquisition#totalIntensityPreferred",StreakScanBI,None,finfun=StreakIntenScanFinalBI)


def StreakSlitScanXMPP(japc,scanListElem,subs):
    import time
    import scipy as sp
    time.sleep(0.5)
    BeamInten=subs.get()[1]
    posREAD=japc.getParam("MPP-TSG41-MIRROR1-V/Position#position")
    japc.setParam("MPP-TSG41-MIRROR1-V/MoveTo#position",scanListElem)
    time=japc.getParam('XMPP-STREAK/StreakImage#streakImageTime')
    posSET=scanListElem
    imData=japc.getParam("XMPP-STREAK/StreakImage#streakImageData").reshape(512,672)

    #prfB=imData[:,200:450].sum(0)/512
    #def gaussFIT1D(prm,x,y):
    #    return ((prm[0]/np.sqrt(2*prm[1]**2)*np.exp( - (x-prm[2])**2 /(2*prm[1]**2)) + prm[3]) -y).ravel()
    INTEN=np.sum(imData[:,200:450]-np.mean(imData[:,:150]))
    #startGuess=np.array([5e2,30,320,0])
    #x=np.arange(0,250)+200
    #optimresB=sp.optimize.least_squares(gaussFIT1D,startGuess,args=(x,prfB))
    return {'posRead':posREAD,'posSet':posSET,'StreakImageTime':time,'BeamIntensity':BeamInten,'measBeamIntensity':INTEN}
def StreakSlitScanFinXMPP( ax,japc,result,*args):
    listR=[]
    for k in result:
        listR+=k
    posread=np.array([l['posRead'] for l in listR])
    beamInten=np.array([l['measBeamIntensity']/l['BeamIntensity'] for l in listR])
    
    #
    # plot
    #
    ax.scatter(posread,beamInten/np.max(beamInten),c='r')
    #ax.scatter(posread,yFitVal,c='b')
    ax.set_ylim(-0.1,1.1)
    return True
StreakSlitScanFinalXMPP_L=awakeIMClass.awakeScreen(StreakSlitScanFinXMPP)
StreakSlitScanXMPP_L=awakeIMClass.awakeLoop("TT41.BCTF.412340/Acquisition#totalIntensityPreferred",StreakSlitScanXMPP,None,finfun=StreakSlitScanFinalXMPP_L)


''' Start the GUI '''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #ex = awakeScanGui(TimeScanXMPP_L,SlitScanXMPP_L,FocusScanXMPP_L,StreakSlitScanXMPP_L)
    ex = awakeScanGui(SlitScanXMPP_L,FocusScanXMPP_L,FocusScanBI_L,StreakIntenScanBI_L)
    sys.exit(app.exec_())
    #app.exec_()

