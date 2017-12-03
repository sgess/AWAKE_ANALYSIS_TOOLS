#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
Spencer tries to make a thing
"""

''' Get all the things '''
import sys
import time
import os
import matplotlib as mpl
mpl.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
#import matplotlib.colors as colors
import matplotlib.dates as mdates
#import matplotlib.pyplot as plt
#from matplotlib import cm

import numpy as np
import pyjapc
import datetime


from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QComboBox, QCheckBox, QMessageBox, QGroupBox, QFormLayout, QTabWidget,
    QTextEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication, QPushButton, QSizePolicy, QStatusBar, QRadioButton)
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import (QIcon, QDoubleValidator, QIntValidator)

class Canvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        
        fig = Figure(figsize=(width, height), dpi=dpi, frameon=False, tight_layout=True)
        
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class Plotter(Canvas):

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self)
        

    def compute_initial_figure(self):
        t_ax = [1,2,3,4,5]
        data = [1,2,3,4,5]
        
        self.axes.plot(t_ax,data)
        
    def update_figure(self):
        self.axes.cla()
        #print(self.xData)
        #print(self.yData)
        self.axes.plot(self.xData,self.yData,'o',color=self.color)
        self.axes.set_xlabel(self.xLabel)
        self.axes.set_ylabel(self.yLabel)
        if self.time:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            #self.axes.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        
        self.draw()


    

''' This is where my code starts '''
class Example(QWidget):


    ''' Init Self '''
    def __init__(self):
        super().__init__()
        self.BCTF_dev = 'TT41.BCTF.412340/Acquisition#totalIntensityPreferred'
        self.BCTF_name = 'Bunch Intensity'
        self.BCTF_ns = True
        
        self.LASER_dev = 'TSG41.AWAKE-LASER-DATA'
        self.LASER_inds = range(15,19)
        self.LASER_ns = True
        
        self.TwoScreen_dev = 'TSG41.AWAKE-TWO-SCREEN-MEAS'
        self.TwoScreen_inds = range(5,9)
        self.TwoScreen_ns = False
        
        self.CTR_dev = 'TSG41.AWAKE-CTR-WR4-WR8-MIXERS'
        self.CTR_inds = range(1,8)
        self.CTR_ns = True
        
        self.StreakFFT_dev = 'TSG41.AWAKE-XMPP-FFTFREQ'
        self.StreakFFT_inds = range(1,5)
        self.StreakFFT_ns = False
        
        self.LaserEng_dev = 'EMETER04/Acq#value'
        self.LaserEng_name = 'Laser Energy'
        self.LaserEng_ns = True
        
        self.SPSdelay_dev = 'Sps2AwakeSynchro/ProtonDelayNs#delay'
        self.SPSdelay_name = 'Laser-SPS Delay'
        self.SPSdelay_ns = True
        self.sps0time = 1111688.5
        
        self.Density_dev = 'TSG41.AWAKE-DENSITY-DATA'
        self.Density_inds = range(1,4)
        self.Density_ns = True
        
        self.getVal= '/ValueAcquisition#floatValue'
        self.getName= '/NameAcquisition#nameValue'
        
        self.bufferLength = 100
        self.index = 0
        
        
        self.initJAPC()
        self.initUI()

    ''' JAPC initialization '''
    def initJAPC(self):

        self.japc = pyjapc.PyJapc("SPS.USER.AWAKE1")

    ''' Initialize GUI '''
    def initUI(self):

        plot_list = self.get_list_of_plots()
        
        self.time_array = []
        self.data_array = np.zeros((self.bufferLength,len(plot_list)-1))
        
        self.main_widget = QWidget(self)
        self.Plots = []
        self.xCombos = []
        self.yCombos = []
        self.toolBars = []
        self.zoomButt = []
        self.homeButt = []
        
        # Create Layout
        grid = QGridLayout()
        colors = ['b','r','g','m','c','k']
        
        for i in range(6):
            self.Plots.append(Plotter(self.main_widget, width=5, height=4, dpi=100))
            self.Plots[i].color = colors[i]
            
            xcb = QComboBox(self)
            self.xCombos.append(xcb)
            self.xCombos[i].addItems(plot_list)
            self.xCombos[i].currentIndexChanged.connect(lambda index, caller=xcb: self.x_select(index,caller))
            self.xCombos[i].setFixedWidth(100)
            
            ycb = QComboBox(self)
            self.yCombos.append(ycb)
            self.yCombos[i].addItems(plot_list)
            self.yCombos[i].setCurrentIndex(i+1)
            self.yCombos[i].currentIndexChanged.connect(lambda index, caller=ycb: self.y_select(index,caller))
            self.yCombos[i].setFixedWidth(100)
            
            zpb = QPushButton('Zoom')
            hpb = QPushButton('Home')
            self.toolBars.append(NavigationToolbar(self.Plots[i], self))
            self.toolBars[i].hide()
            self.zoomButt.append(zpb)
            self.zoomButt[i].setStyleSheet("background-color:#00f2ff")
            self.zoomButt[i].clicked.connect(lambda state, caller=zpb: self.zoom(state, caller))
            self.homeButt.append(hpb)
            self.homeButt[i].setStyleSheet("background-color:#00f2ff")
            self.homeButt[i].clicked.connect(lambda state, caller=hpb: self.home(state, caller))
            
            x_label = QLabel('X-Axis:')
            y_label = QLabel('Y-Axis:')
            
            v_box = QVBoxLayout()
            v_box.addWidget(x_label)
            v_box.addWidget(self.xCombos[i])
            v_box.addWidget(y_label)
            v_box.addWidget(self.yCombos[i])
            v_box.addWidget(self.zoomButt[i])
            v_box.addWidget(self.homeButt[i])
            v_box.addStretch()
            
            h_box = QHBoxLayout()
            h_box.addLayout(v_box)
            h_box.addWidget(self.Plots[i])
            h_box.addStretch()
            grid.addLayout(h_box,np.floor_divide(i,2),np.mod(i,2))
        
    
        self.setLayout(grid)
        self.setGeometry(1600, 300, 1000, 1000)

        # Make a window
        self.setWindowTitle('Plots')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))

        # Start the show
        self.show()
        self.start_subs()

    ''' Create list of things we plot '''
    def get_list_of_plots(self):
        
        temp = self.japc.getParam(self.StreakFFT_dev+self.getName)
        streak_fft_names = temp[self.StreakFFT_inds]
        temp = self.japc.getParam(self.TwoScreen_dev+self.getName)
        two_screen_names = temp[self.TwoScreen_inds]
        temp = self.japc.getParam(self.CTR_dev+self.getName)
        ctr_dev_names = temp[self.CTR_inds]
        temp = self.japc.getParam(self.LASER_dev+self.getName)
        laser_dev_names = temp[self.LASER_inds]
        temp = self.japc.getParam(self.Density_dev+self.getName)
        dens_dev_names = temp[self.Density_inds]
        
        plot_list = []
        plot_list.append('Time')
        plot_list.append(self.BCTF_name)
        plot_list.append(self.LaserEng_name)
        plot_list.extend(streak_fft_names)
        plot_list.extend(two_screen_names)
        plot_list.extend(ctr_dev_names)
        plot_list.extend(laser_dev_names)
        plot_list.extend(dens_dev_names)
        plot_list.append(self.SPSdelay_name)
        
        
        return plot_list
        
    ''' Zoom and Home '''
    def zoom(self, state, caller):
        
        pInd = self.zoomButt.index(caller)
        self.toolBars[pInd].zoom()
        
    def home(self, state, caller):
        
        pInd = self.homeButt.index(caller)
        self.toolBars[pInd].home()
    
    ''' Update plot selection '''
    def x_select(self,index,caller):
        
        pInd = self.xCombos.index(caller)
        self.Update(pInd)
        
    ''' Update plot selection '''
    def y_select(self,index,caller):
        
        pInd = self.yCombos.index(caller)
        self.Update(pInd)
        
    ''' Start Subs '''
    def start_subs(self):

        self.japc.subscribeParam(self.BCTF_dev,self.proc_plot_data,getHeader=True,unixtime=True)
        self.japc.startSubscriptions()

    ''' What to do when you have the data '''
    def proc_plot_data(self, name, paramValue, header):
        
        time.sleep(7)
        
        laserEng = self.japc.getParam(self.LaserEng_dev)
        spsDelay = self.japc.getParam(self.SPSdelay_dev) - self.sps0time
        laserAlign = self.japc.getParam(self.LASER_dev+self.getVal)[self.LASER_inds]
        twoScreen = self.japc.getParam(self.TwoScreen_dev+self.getVal)[self.TwoScreen_inds]
        CTR = self.japc.getParam(self.CTR_dev+self.getVal)[self.CTR_inds]
        StreakFFT = self.japc.getParam(self.StreakFFT_dev+self.getVal)[self.StreakFFT_inds]
        Density = self.japc.getParam(self.Density_dev+self.getVal)[self.Density_inds]
        
        if self.index == (self.bufferLength-1):
            
            self.data_array = np.roll(self.data_array,-1,axis=0)
            del(self.time_array[0])
            
            self.time_array.append(datetime.datetime.fromtimestamp(header['acqStamp']))
        
            self.data_array[self.index,0] = paramValue
            self.data_array[self.index,1] = laserEng
            self.data_array[self.index,2:6] = StreakFFT
            self.data_array[self.index,6:10] = twoScreen
            self.data_array[self.index,10:17] = CTR
            self.data_array[self.index,17:21] = laserAlign
            self.data_array[self.index,21:24] = Density
            self.data_array[self.index,24] = spsDelay
            
        else:
            
            self.time_array.append(datetime.datetime.fromtimestamp(header['acqStamp']))
            
            self.data_array[self.index,0] = paramValue
            self.data_array[self.index,1] = laserEng
            self.data_array[self.index,2:6] = StreakFFT
            self.data_array[self.index,6:10] = twoScreen
            self.data_array[self.index,10:17] = CTR
            self.data_array[self.index,17:21] = laserAlign
            self.data_array[self.index,21:24] = Density
            self.data_array[self.index,24] = spsDelay 
                           
#            print('BCTF = '+str(self.data_array[self.index,0]))
#            print('LasEng = '+str(self.data_array[self.index,1]))
#            print('StkFFT = '+str(self.data_array[self.index,2:6]))
#            print('2Screen = '+str(self.data_array[self.index,6:10]))
#            print('CTR = '+str(self.data_array[self.index,10:17]))
#            print('Laser = '+str(self.data_array[self.index,17:21]))
            
            self.index += 1
            
        self.Update(0)
        self.Update(1)
        self.Update(2)
        self.Update(3)
        self.Update(4)
        self.Update(5)
        
    ''' Get Plot Stuff '''
    def Update(self,ind):
        
        if self.index > 1:
        
            xInd = self.xCombos[ind].currentIndex()
            yInd = self.yCombos[ind].currentIndex()
            
            if xInd == 0:
                self.Plots[ind].xData = self.time_array
                self.Plots[ind].yData = self.data_array[0:self.index,yInd-1]
                self.Plots[ind].time = True
            else:
                self.Plots[ind].xData = self.data_array[0:self.index,xInd-1]
                self.Plots[ind].yData = self.data_array[0:self.index,yInd-1]
                self.Plots[ind].time = False
            
            self.Plots[ind].xLabel = self.xCombos[ind].currentText() 
            self.Plots[ind].yLabel = self.yCombos[ind].currentText()
            self.Plots[ind].update_figure()
        
    ''' Stop Subs '''
    def stop_subs(self):
        
        self.japc.stopSubscriptions()
        self.japc.clearSubscriptions()

    ''' Clear Subs '''
    def clear_subs(self):
        
        self.japc.stopSubscriptions()
        self.japc.clearSubscriptions()
        
    ''' GTFO '''
    def closeEvent(self, event):
        self.clear_subs()
        QWidget.closeEvent(self, event)

''' Start the GUI '''
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
