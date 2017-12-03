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
from matplotlib.figure import Figure
import matplotlib.colors as colors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
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
        
        fig = Figure(figsize=(width, height), dpi=dpi, frameon=True, tight_layout=True)
        fig.patch.set_facecolor('aliceblue')
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class SpaceView(Canvas):

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self)
        

    def compute_initial_figure(self):
        t_ax = [1,2,3,4,5]
        data = [1,2,3,4,5]
        
        self.axes.plot(t_ax,data)
        
    def update_figure(self,x1,y1,x2,y2):
        self.axes.cla()
        
        self.axes.plot(x1,y1,'bo')
        earth= plt.Circle((x1,y1), self.rL, color = 'skyblue')
        self.axes.add_patch(earth) 
        self.axes.plot(x2,y2,'ro')
        moon= plt.Circle((x2,y2), self.rP, color = 'lightsalmon')
        self.axes.add_patch(moon) 
        self.axes.set_title(self.title, fontsize = 16)
        self.axes.set_xlabel('x, mm')
        self.axes.set_ylabel('y, mm')
        self.axes.legend(self.legend,bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0.)
        #self.axes.legend(bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0.)
        self.axes.set_xlim([-self.axlim,self.axlim])
        self.axes.set_ylim([-self.axlim,self.axlim])
        self.axes.grid('on')
#        axarr[0,0].yaxis.label.set_color(textcolor)
#        axarr[0,0].tick_params(axis = 'y', colors = textcolor)
#        axarr[0,0].xaxis.label.set_color(textcolor)
#        axarr[0,0].tick_params(axis = 'x', colors = textcolor)
#        axarr[0,0].set_axis_bgcolor(bgfigcolor)
        self.axes.set_aspect('equal', adjustable='box')
        
        self.draw()

class TimeView(Canvas):

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self)
        

    def compute_initial_figure(self):
        t_ax = [datetime.datetime.now()]
        data = [0]
        
        self.axes.plot(t_ax,data,'bo')
        
    def update_figure(self,timeBuffer,dataBuffer1,dataBuffer2):
        self.axes.cla()
        
        self.axes.plot(np.array(timeBuffer),np.array(dataBuffer1),'bo', markersize = 4)
        self.axes.plot(timeBuffer,dataBuffer2,'ro', markersize =4)
        self.axes.set_xlabel('time')
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.axes.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        self.axes.set_ylabel(self.yLabel)
        self.axes.set_ylim([-self.axlim,self.axlim])
        
#        self.axes.set_xticklabels(rotation = 45)
        #self.axes.legend(self.legend)
        self.axes.grid('on')
#    axarr[1,0].set_axis_bgcolor(bgfigcolor)
#    axarr[1,0].yaxis.label.set_color(textcolor)
#    axarr[1,0].tick_params(axis = 'y', colors = textcolor)
#    axarr[1,0].xaxis.label.set_color(textcolor)
#    axarr[1,0].tick_params(axis = 'x', colors = textcolor)
        
        self.draw()

    

''' This is where my code starts '''
class Example(QWidget):


    ''' Init Self '''
    def __init__(self):
        super().__init__()

        self.GUI = 'TSG41.AWAKE-LASER-DATA/ValueAcquisition#floatValue'
        self.timeBuffer = []
        self.xVLC3Buffer = []
        self.yVLC3Buffer = []
        self.xVLC5Buffer = []
        self.yVLC5Buffer = []
        self.x352Buffer = []
        self.y352Buffer = []
        self.x425Buffer = []
        self.y425Buffer = []
        self.axlim = 3
        self.rlEx = 0.7 #fwhm laser at the waist
        self.rlEn = 1 #fwhm laser at the waist
        self.rp = 0.47 #fwhm p+ if sigma is 200um
        self.bufferLength = 40
        self.legend = ['Laser','p+']
        self.initJAPC()
        self.initUI()

    ''' JAPC initialization '''
    def initJAPC(self):

        self.japc = pyjapc.PyJapc("SPS.USER.AWAKE1")

    ''' Initialize GUI '''
    def initUI(self):

        self.main_widget = QWidget(self)
        
        # Create a plotting window
        self.Entrance = SpaceView(self.main_widget, width=5, height=4, dpi=100)
        self.Entrance.title = 'Entrance'
        self.Entrance.axlim = self.axlim
        self.Entrance.rL = self.rlEn
        self.Entrance.rP = self.rp
        self.Entrance.legend = self.legend
        
        # Create a plotting window
        self.Exit = SpaceView(self.main_widget, width=5, height=4, dpi=100)
        self.Exit.title = 'Exit'
        self.Exit.axlim = self.axlim
        self.Exit.rL = self.rlEx
        self.Exit.rP = self.rp
        self.Exit.legend = self.legend
        
        # Create a plotting window
        self.UpX = TimeView(self.main_widget, width=5, height=4, dpi=100)
        self.UpX.title = 'UpXTime'
        self.UpX.yLabel = 'x, mm'
        self.UpX.axlim = self.axlim
        self.UpX.legend = self.legend
        
        # Create a plotting window
        self.UpY = TimeView(self.main_widget, width=5, height=4, dpi=100)
        self.UpY.title = 'UpYTime'
        self.UpY.yLabel = 'y, mm'
        self.UpY.axlim = self.axlim
        self.UpY.legend = self.legend
        
        # Create a plotting window
        self.DwX = TimeView(self.main_widget, width=5, height=4, dpi=100)
        self.DwX.title = 'DwXTime'
        self.DwX.yLabel = 'x, mm'
        self.DwX.axlim = self.axlim
        self.DwX.legend = self.legend
        
        # Create a plotting window
        self.DwY = TimeView(self.main_widget, width=5, height=4, dpi=100)
        self.DwY.title = 'DwYTime'
        self.DwY.yLabel = 'y, mm'
        self.DwY.axlim = self.axlim
        self.DwY.legend = self.legend
        
        # Create Layout
        grid = QGridLayout()
        grid.addWidget(self.Entrance, 0, 0)
        grid.addWidget(self.Exit, 0, 1)
        grid.addWidget(self.UpX, 1, 0)
        grid.addWidget(self.DwX, 1, 1)
        grid.addWidget(self.UpY, 2, 0)
        grid.addWidget(self.DwY, 2, 1)
        
    
        self.setLayout(grid)
        self.setGeometry(1600, 300, 900, 1000)

        # Make a window
        self.setWindowTitle('Laser Plots')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__),'awakeicon1_FkV_icon.ico')))

        # Start the show
        self.show()
        self.start_subs()

   
    ''' Start Subs '''
    def start_subs(self):

        
        self.japc.subscribeParam(self.GUI,self.proc_gui_data)
        self.japc.startSubscriptions()

    ''' What to do when you have the data '''
    def proc_gui_data(self, name, paramValue):
        
        timeStamp = paramValue[0]/1e9
        self.timeBuffer.append(datetime.datetime.fromtimestamp(timeStamp))
        
        self.xVLC3Buffer.append(paramValue[7])
        self.yVLC3Buffer.append(paramValue[8])
        self.xVLC5Buffer.append(paramValue[9])
        self.yVLC5Buffer.append(paramValue[10])
        self.x352Buffer.append(paramValue[11])
        self.y352Buffer.append(paramValue[12])
        self.x425Buffer.append(paramValue[13])
        self.y425Buffer.append(paramValue[14])
        
        if len(self.timeBuffer)>self.bufferLength:
            del(self.timeBuffer[0])
            del(self.xVLC3Buffer[0])
            del(self.yVLC3Buffer[0])
            del(self.xVLC5Buffer[0])
            del(self.yVLC5Buffer[0])
            del(self.x352Buffer[0])
            del(self.y352Buffer[0])
            del(self.x425Buffer[0])
            del(self.y425Buffer[0])
            
        self.Entrance.update_figure(paramValue[7],paramValue[8],paramValue[11],paramValue[12])
        self.Exit.update_figure(paramValue[9],paramValue[10],paramValue[13],paramValue[14])
        self.UpX.update_figure(self.timeBuffer,self.xVLC3Buffer,self.x352Buffer)
        self.UpY.update_figure(self.timeBuffer,self.yVLC3Buffer,self.y352Buffer)
        self.DwX.update_figure(self.timeBuffer,self.xVLC5Buffer,self.x425Buffer)
        self.DwY.update_figure(self.timeBuffer,self.yVLC5Buffer,self.y425Buffer)
        
        
        
        
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
