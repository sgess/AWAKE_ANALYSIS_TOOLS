#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 18:09:25 2017

@author: sgess
Map from Mike Litos
"""

from matplotlib.colors import LinearSegmentedColormap

def custom_cmap():
    colors = [(1, 1, 1),(0, 0, 1),(0, 1, 1),(1, 1, 0),(1, 0, 0),(0.5, 0, 0)]
    cm = LinearSegmentedColormap.from_list('litos',colors,N=256)
    return cm
