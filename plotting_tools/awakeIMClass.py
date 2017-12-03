#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 29 18:59:19 2017

@author: rieger
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May 27 08:51:34 2017

@author: Spencer&Karl
"""

import sys
import os.path as osp
import functools
import matplotlib as mpl
# Make sure that we are using QT5
mpl.use('Qt5Agg')
#mpl.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import pyjapc
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QComboBox, QCheckBox,
    QTextEdit, QGridLayout, QApplication, QPushButton, QSizePolicy, QMessageBox, QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout, QStatusBar)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import (QIcon, QDoubleValidator, QRegExpValidator)
import PyQt5.QtGui as QtGui

from PyQt5 import QtCore, QtWidgets
import queue as qe
import pickle
            
long=int

class AWAKException(Exception):
    pass

"""
Spencers Canvas class renamed
"""
class awakeCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100,reverse=False,*args):
        #self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.fig=Figure(figsize=(width, height), dpi=dpi,tight_layout=True)

        self.nSubPlots=len([k for k in args if type(k) is type(lambda x:1)])
        if reverse:
            self.gs=mpl.gridspec.GridSpec(self.nSubPlots,1)
        else:
            self.gs=mpl.gridspec.GridSpec(1,self.nSubPlots)
            
        #self.axes = [self.fig.add_subplot(int("1"+str(l+1)+"1")) for l in range(0,nSubPlots)] #maybe change later, dont like the subplot call
        self.axes = {l:self.fig.add_subplot(self.gs[l]) for l in range(0,self.nSubPlots)} #maybe change later, dont like the subplot call
        #for k in self.axes:
        #    k.hold(False)# We want the axes cleared every time plot() is called
        #print(self.axes)
        """

        Figure Canvas initialisation
        """
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        

class awakeScreen(awakeCanvas):
    def __init__(self,*args, parent=None, width=5, height=4, dpi=100,**kwargs):
        if 'reverse' in kwargs.keys():
            reverse=kwargs['reverse']
            print('Using reverse Image conf!:',reverse)
        else:
            reverse=False
        super(awakeScreen,self).__init__(parent,width,height,dpi,reverse,*args)
        self.f=[k for k in args if type(k) is type(lambda x:1)]
        self.fnames=[k.__name__ for k in self.f]
        self.fargs={}
        for k in kwargs.keys():
            if k in self.fnames:
                self.fargs[k]=kwargs[k]

    def __iter__(self):
        return self.f.__iter__()
        
    def __call__(self,*args):
        #self._cleanAxes()
        callDraw=[]
        for k,name,ax in zip(self.f,self.fnames,self.axes.keys()):
            if name in self.fargs.keys():
                try:
                    callDraw.append(k(self.axes[ax],*args,**self.fargs[name]))
                except:
                    pass
            else:
                try:
                    callDraw.append(k(self.axes[ax],*args))
                except:
                    pass
        if np.any(callDraw):
            self.draw()
                
    def _cleanAxes(self):
        print(self.fig.axes)
        print(self.axes)
        for k in self.fig.axes:
            if k not in self.axes:
                self.fig.delaxes(k)
        print(self.fig.axes)
        print(self.axes)
        
    def updateFunction(self,fun,replace=False,**kwargs):
        if not replace:    
            if fun.__name__ in self.fnames:
                i=0
                while fun.__name__ != self.f[i].__name__:
                    i+=1
                    if i>10:
                        print('awakeJAPC|updateFunction: You sure that the functions exists?')
                        break
                self.f[i]=fun
            for k in kwargs.keys:
                self.fargs[fun.__name__][k]=kwargs[k]
                #self.fargs[fun.__name__]=kwargs
            return True
        if replace:
            if not isinstance(fun):
                fun=[fun]
            if len(fun)>self.axes:
                print('Did not update as there are too many functions!')
                return False
            self.f=fun
            self.fnames=[k.__name__ for k in self.f]
            self.fargs={}
            for k in kwargs.keys():
                if k in self.fnames:
                    self.fargs[k]=kwargs[k]
        return True
            
    def draw(self,*args,**kwargs):
        super(awakeCanvas,self).draw()

class awakeJAPC(awakeScreen):
    
    def __init__(self,subscriptions,*args,axes=None,selector="SPS.USER.AWAKE1",name='MyAwakeImage',autostart=False,**kwargs):
        super(awakeJAPC,self).__init__(*args,**kwargs)#self.screen=awakeScreen(*args,**kwargs)
        
        self.selector=selector
        self.subs=awakeSubscriptions(subscriptions,selector,self._workQueue)
        self.name=str(name)
        self.fixedaxes=axes
        self.inSubs=False# lazy solution
        if autostart:
            self.start()

    def start(self,verbose=True):
        self.subs.start()
    
    def stop(self,verbose=True):
        self.subs.stop()
        
    def _workQueue(self,*args,**kwargs):
        tpl=[self.fig,self.fixedaxes,self.subs.japc]
        for k in range(len(self.subs)):
            tpl.append(None)
        while not self.subs.empty():
            name,val=self.subs.get()
            tpl[self.subs[name]+3]=val
        tpl=tuple(tpl)
        #print('Subscriptions recieved! Calling the functions!')
        if self.inSubs:
            super(awakeJAPC,self).__call__(*tpl)
            super(awakeJAPC,self).draw()
        while not self.subs.all_tasks_done:# k in range(0,len(tpl)-3):
            self.subs.task_done()
        # lazy solution
        if self.inSubs is False:
            self.inSubs=not self.inSubs
        
    def __del__(self):
        self.stop()
        
class awakeSubscriptions(qe.Queue):
    waitAll=True
    _fullNames={}
    def __init__(self,x,selector="SPS.USER.AWAKE1",wkQueue=None):
        self.selector=selector
        self.japc = pyjapc.PyJapc(selector)
        if wkQueue is not None:
            self._workQueue=wkQueue
        #self.japc.setSelector(selector)
        self._setSubs(x)
        
    def _setSubs(self,x):
        if isinstance(x,str):
            super(awakeSubscriptions,self).__init__(1)
            self.subs={x:0}
            self.subNum={0:x}
            return
        try:
            super(awakeSubscriptions,self).__init__(len(x))
            self.subs={str(x[k]):k for k in range(0,len(x))}
            self.subNum={k:str(x[k]) for k in range(0,len(x))}
        except:
            raise AWAKException('For Subscriptions please provide string construtables iterable or single string!')
  
    def _fillQueue(self,name,val):
        if not self.waitAll:
            self.put((name,val))
        else:
            if not (name in self._fullNames.keys()):
                self.put((name,val))
                self._fullNames[name]=True
        if self.full():
            self._workQueue()
            self._fullNames={}
        if not self.empty(): #jem,and hat vergessen queue zu leeren
            while not self.empty():
                self.get()
                self.task_done()
        while not self.all_tasks_done: #some1 forgot to place a task done...
            self.task_done()


    def start(self,verbose=True):
        self.japc.stopSubscriptions()
        self.japc.clearSubscriptions()
        
        for k in list(self.subs.keys()):
            print(k)
            self.japc.subscribeParam(k,self._fillQueue)
        self.japc.startSubscriptions()
        if verbose:
            print('STARTED ALL SUBSCRIPTIONS!')
    
    def stop(self,verbose=True):
        self.japc.stopSubscriptions()
        if verbose:
            print('STOPPED ALL SUBSCRIPTIONS!')
                      
    def __getitem__(self,k):
        if k in self.subs.keys():
            return self.subs[k]
        if k in self.subNum.keys():
            return self.subNum[k]
        raise AWAKException('Requested object not in Subscritpions')

    def setSubscriptions(self,x,selector=None):
        self.stop(False)
        if selector is not None:
            self.japc.setSelector(selector)
        self._setSubs(x)
        self.start(False)    
        
    def __repr__(self):
        print(self.subs)
        
    def __iter__(self):
        return self.subs.__iter__()
        
    def __len__(self):
        return len(self.subNum)
    
    def _workQueue(self,*args,**kwargs):
        pass
    
    def __del__(self):
        self.stop()
        self.japc.clearSubscriptions()
        
class awakeLoop:
    SubCalls=0
    MaxCall=5
    ListCallNumber=0
    savePickle=True
    firstCall=True
    
    def __init__(self,subs,wkQue,scanList=None,checkBeam=lambda x: x.japc.getParam("TT41.BCTF.412340/Acquisition#totalIntensityPreferred")<0.1,selector="SPS.USER.AWAKE1",savestr='awakeLoop.pickle',finfun=None,name=None):
        print('init called')
        self.subs=awakeSubscriptions(subs,selector,self.__call__)
        self.callFKT=wkQue
        self.ScanList=scanList
        if scanList is not None:
            self.result=[[] for k in range(0,len(scanList))]
        self.file_string=savestr
        self.checkBeam=checkBeam
        self.finfun=finfun
        if name is None:
            self.name=self.callFKT.__name__
        else:
            self.name=name

    def reset(self):
        self.SubCalls=0
        self.MaxCall=5
        self.ListCallNumber=0
        self.firstCall=True
        self.savePickle=True


    def __call__(self,*args,**kwargs):
        print('awakeLoop called!\nListCallNumber:{0:2.0f}'.format(self.ListCallNumber)) 
        # daten sind in self.subs als queue, sind ungeordnet aber immer als parmeter (name,val)
        if self.firstCall:
            self.firstCall= not self.firstCall
            self.result=[[] for k in range(0,len(self.ScanList))]
            return
        if self.checkBeam(self.subs):
           print('NO BEAM!')
           return 
           #pass
        # call order: name, val
        try:
            self.result[self.ListCallNumber].append(self.callFKT(self.subs.japc,self.ScanList[self.ListCallNumber],self.subs))
        except:
            print('EXCEPTION IN LOOPCALL!')
            self.result[self.ListCallNumber].append({'result':None})
        self.SubCalls+=1
        if self.SubCalls%self.MaxCall ==0:
            self.SubCalls=0
            self.ListCallNumber+=1
        if self.ListCallNumber==len(self.ScanList):
            self.subs.stop()
            print("Finished with scan!")
            self.reset()
            if self.savePickle:
                try:
                    print("Saving scan results!")
                    pickle.dump(self.result,open(self.file_string,'wb+'))
                except:
                    print("Saving failed! (disk quota?)")
            if self.finfun is not None:
                print('Calling Finfun!')
                self.finfun(self.subs.japc,self.result)
        
    def print(self):
        print('printing self!')
        print(self.SubCalls,self.MaxCall,self.ListCallNumber,self.savePickle,self.firstCall)
        #print(self.subs)
        print(self.callFKT)
        print(self.ScanList)

    def stop(self):
        self.subs.stop()
        
    def start(self):
        self.result=[[] for k in range(0,len(self.ScanList))]
        self.subs.start()
        
class awakeLaserBox:
    def __init__(self,ns1,ns05,ns02,ns01,element='MPPAWAKE:FASTTRIG-1:STREAKTUBE-FINEDELAY',name='XMPP'):
        #pixel definitions of laserposition
        self.tRange={'1 ns':ns1,'500 ps':ns05,'200 ps':ns02,'100 ps':ns01}
        self.elem=element
        self.name=name
        import pytimber
        import time
        self.ldb=pytimber.LoggingDB()
        self.timeVal=self.ldb.get(self.elem,time.strftime('%Y-%m-%d %H:%M:%S'))
        
    def __call__(self,x=None):
        import time
        try:
            self.timeVal=self.ldb.get(self.elem,time.strftime('%Y-%m-%d %H:%M:%S'))        
        except: #hardgecoded
            if x is not None:
                self.timeVal=self.tRange[x][0]
                return self.timeVal
            else:
                return None
                #raise AWAKException('__call__ in awakeLaserBox: Please secify tranges via constructor!')
                
        return self.timeVal[self.elem][1][0]
        
    def __getitem__(self,k):
        try :
            rVal=self.tRange[k]
        except:
            return None,None
        return rVal

class windowClass(QtWidgets.QMainWindow):
    def __init__(self,ev=None,parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.main_widget = QtWidgets.QWidget(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setCentralWidget(self.main_widget)
        if ev is not None:
           self.endF=ev
        else:
           self.endF=None

    def fileQuit():
        pass

    def closeEvent(self,ce):
        if self.endF is not None:
           self.endF(self)
    
class AwakeWindow(QtWidgets.QMainWindow):
    def __init__(self,subscriptions,*args,fixedaxes=None,selector="SPS.USER.AWAKE1",name='MyAwakeImage',autostart=True,**kwargs):
        
        self.childWindows={}

        QtWidgets.QMainWindow.__init__(self)
        self.main_widget = QtWidgets.QWidget(self)
        self.awakeJAPC_instance=awakeJAPC(subscriptions,*args,axes=fixedaxes,selector=selector,name=name,autostart=autostart,parent=self.main_widget,**kwargs)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("%s"%self.awakeJAPC_instance.name)
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&About', self.about)
        
        """
        start& stop
        """
        self.start_menu = QtWidgets.QMenu('&Subscriptions Control', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.start_menu)
        self.start_menu.addAction('&Start Subscriptions', self.start)
        self.start_menu.addAction('&Stop Subscriptions', self.stop)

        '''
        Add Menu for parameters of plotfunctions and add the points
        '''
        self.option_menu = QtWidgets.QMenu('&Parameter Control', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.option_menu)

        self.wrapperFKT={}
        self.wrapperSETFKT={}
        self.prmNAMES={}
        for k in kwargs.keys():
            if type(kwargs[k]) is not type({}):
                continue
            else:
                for l in kwargs[k]:
                    buff=str(k)+'/'+str(l)
                    #print(buff)
                    self.prmNAMES[buff]=buff
                    #self.wrapperFKT[buff]=lambda :self.wrapperChildWindow(self.prmNAMES[buff])
                    self.wrapperFKT[buff]=lambda :self.spawnChildWindow(self.prmNAMES[buff])#'StdPlotMPPT/maxVal'])
                    #self.wrapperSETFKT[buff]=lambda :self.wrapperSetPrmToFunction(self.prmNAMES[buff])
                    self.wrapperSETFKT[buff]=lambda :self.SetPrmToFunction(self.prmNAMES[buff])
                    #self.option_menu.addAction('&Set parameter: '+buff,self.wrapperFKT[buff])
                    #action = self.option_menu.addAction(buff)
                    #action.triggered.connect(self.wrapperFKT[buff])
                    
        self.prm_menus=[]
        for k in self.prmNAMES.keys():
            #print(k)
            prmIdx='&Set parameter: '+self.prmNAMES[k]
            #self.prm_menus.append(QtWidgets.QMenu(prmIdx, self))
            #self.menuBar().addSeparator()
            #self.menuBar().addMenu(self.prm_menus[-1])
            
            #action = self.prm_menus[-1].addAction(prmIdx)
            #print(self.wrapperFKT[str(k)])
            #action.triggered.connect(self.wrapperFKT['StdPlotMPPT/maxVal'])
            self.option_menu.addAction(prmIdx,functools.partial(self.spawnChildWindow,self.prmNAMES[k]))
        #self.option_menu.addAction('bla1',self.wrapperFKT['StdPlotMPPT/maxVal'])
        

        """
        Update functions
        
        self.start_menu = QtWidgets.QMenu('&Subscriptions Control', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.start_menu)
        """ 
        BoxLayout = QtWidgets.QVBoxLayout(self.main_widget)
        BoxLayout.addWidget(self.awakeJAPC_instance)
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.statusBar().showMessage("Here speaks God, give Gandalf your ring!!", -1)
        
    def start(self):
        self.awakeJAPC_instance.start()

    def wrapperChildWindow(self,x):
        self.spawnChildWindow(x)

    def wrapperSetPrmToFunction(self,x):
        '''
        Hier gehÃƒÂ¶rt der ganze conversion kram hin!
        '''
        text=self.childWindows[x].inpVal.text()
        print(text)
        text=text.strip()
        if text[0] == '[' or text[0]=='(':
            if text[-1]==']' or text[-1]==')':
               text=np.array(text)
            else:
               print('NOT ACCEPTED INPUT!')
               return
            if text.size==1:
               text=float(text)
        else:
            text=float(text)
    
        arg=text#float(self.childWindows[x].inpVal.text())
        self.SetPrmToFunction(x,arg)

    def SetPrmToFunction(self,x):
        '''
        Hier gehÃƒÂ¶rt der ganze conversion kram hin!
        '''
        text=self.childWindows[x].inpVal.text()
        print('--------------')
        print(text)
        text=text.strip()
        print(text) 
        if text[0] == '[' or text[0]=='(':
            if text[-1]==']' or text[-1]==')':
               text=text.strip('[').strip('(').strip(']').strip(']')
               text=np.fromstring(text,sep=',')
               print(text)
            else:
               text=text
               print('text input!')
            if text.size==1:
               text=float(text[0])
        else:
            try:
                text=float(text)
            except:
                text=text
                print('text input!')

        arg=text#float(self.childWindows[x].inpVal.text())

        #arg=float(self.childWindows[x].inpVal.text())
        fname=x.split('/')[0]
        farg=x.split('/')[1]
        print(self.awakeJAPC_instance.fargs[fname][farg])
        print(arg)
        self.awakeJAPC_instance.fargs[fname][farg]=arg

    def spawnChildWindow(self,name):
        # Create a group box for camera properties
        '''
        self.childWindows[name]=windowClass(self.killChild)
        '''
        self.childWindows[name]=awakeScreen(parent=None)
        child=self.childWindows[name]
        child.name=name

        child.btnStart = QPushButton('Send', child)
        child.btnStart.setStyleSheet("background-color:#63f29a")
        child.btnStart.clicked[bool].connect(functools.partial(self.SetPrmToFunction,name))

        prop_box = QGroupBox('Properties')
        #child.inpVal = QLineEdit(child)
        #child.inpVal.setValidator(QDoubleValidator(-100000,100000,4))
        child.inpVal = QLineEdit(self)
        child.regExp=QtCore.QRegExp('^.*$')# accept everything
        child.inpVal.setValidator(QRegExpValidator(child.regExp))
        prop_form = QFormLayout()
        prop_form.addRow('New Value:',child.inpVal)
        prop_box.setLayout(prop_form)

        # Create a plotting window
        #child.main_widget = QWidget(self)

        # Create Layout
        child.vbox=QVBoxLayout()
        child.hbox = QHBoxLayout()

        child.vbox.addWidget(prop_box)
        child.vbox.addWidget(child.btnStart)
        #child.hbox.addStretch(1)
        
        child.hbox.addLayout(child.vbox)
        child.setLayout(child.hbox)
        child.show()

    def killChild(self,node):
        for k in self.childWindows.keys():
            if node.name==str(k):
               delcand=self.childWindows[k]
        del(delcand)
        
    def stop(self):
        self.awakeJAPC_instance.stop()
        
    def fileQuit(self):
        self.awakeJAPC_instance.stop()
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About","""A single Awake window, able to show something nice""")

#laserboxMPP=awakeLaserBox((4.3,[270,290]),(9.2,[310,330]),(4.3,[415,440]),(8.35,[225,335]))
laserboxMPP=awakeLaserBox((4.3,[280,300]),(9.2,[300,320]),(4.3,[415,440]),(8.35,[205,325]))
laserboxBI=awakeLaserBox((5.3,[210,260]),None,None,None,name='BI.TT41.STREAK')

