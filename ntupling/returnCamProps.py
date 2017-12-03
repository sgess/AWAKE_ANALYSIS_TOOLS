#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 15:58:36 2017

@author: sgess

This file keeps track of camera properties in order to format
the images properly. Need a better solution. . .
"""

def returnCamProps(runNumber):
    
    if runNumber <= 23:
#        cameraList = ['/AwakeEventData/BOVWA.01TT41.CAM1/ExtractionImage/imageRawData',
#                      '/AwakeEventData/BOVWA.02TT41.CAM2/ExtractionImage/imageRawData',
#                      '/AwakeEventData/BOVWA.03TT41.CAM3/ExtractionImage/imageRawData',
#                      '/AwakeEventData/BOVWA.04TT41.CAM4/ExtractionImage/imageRawData',
#                      '/AwakeEventData/BOVWA.05TT41.CAM5/ExtractionImage/imageRawData',
#                      '/AwakeEventData/TT41.BTV.412350/Image/imageSet',
#                      '/AwakeEventData/TT41.BTV.412353/Image/imageSet',
#                      '/AwakeEventData/TT41.BTV.412426/Image/imageSet',
#                      '/AwakeEventData/TT41.BTV.412442/Image/imageSet',
#                      '/AwakeEventData/XMPP-STREAK/StreakImage/streakImageData']
#        cameraWidth = [1280,
#                       1282,
#                       1920,
#                       1280,
#                       1626,
#                       385,
#                       385,
#                       391,
#                       385,
#                       672]
#        cameraHeight = [1024,
#                        1026,
#                        1200,
#                        960,
#                        1236,
#                        285,
#                        285,
#                        280,
#                        385,
#                        512]
        
        cameraList = ['/AwakeEventData/TT41.BTV.412350/Image/imageSet',
                      '/AwakeEventData/TT41.BTV.412353/Image/imageSet',
                      '/AwakeEventData/TT41.BTV.412426/Image/imageSet',
                      '/AwakeEventData/TT41.BTV.412442/Image/imageSet',
                      '/AwakeEventData/XMPP-STREAK/StreakImage/streakImageData']
        cameraWidth = [385,
                       385,
                       391,
                       385,
                       672]
        cameraHeight = [285,
                        285,
                        280,
                        285,
                        512]
        
        dictCamProps = {'cameraList': cameraList,
                        'cameraWidth': cameraWidth,
                        'cameraHeight': cameraHeight}
    return dictCamProps
                        
