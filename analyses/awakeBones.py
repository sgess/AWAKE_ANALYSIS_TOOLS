# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 06:18:03 2017

@author: Karl
"""

"""
scBase file, this file defines most of the important places
"""


"""
Definition where nonEventbuilder data lies (i.e. Rb Valves and laser power)
"""
BaseFolder=r'/home/KarlRieger/AWAKE'.replace('\\','/')
RBUPFiles=BaseFolder+'/UP_Valve_closed.txt'
RBDOWNFiles=BaseFolder+'/DOWN_Valve_closed.txt'
LASERPOWER=BaseFolder+'/LaserEnergy.txt'

nonEventData=(RBUPFiles,RBDOWNFiles,LASERPOWER)


"""
Definition where dataFiles are
"""


baseFolderData=r'D:/AWAKE'

fullDataFolders=[baseFolderData+r'/2016/12/09',baseFolderData+r'/2016/12/10',baseFolderData+r'/2016/12/11',baseFolderData+r'/2016/12/12']