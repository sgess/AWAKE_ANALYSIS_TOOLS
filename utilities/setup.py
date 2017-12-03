#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 00:49:35 2017

@author: sgess
"""
# Import modules and set path
import os
import sys
import time
import h5py
import numpy as np
import matplotlib.pyplot as plt

os.environ['AAT'] = os.environ['HOME']+'/AWAKE_ANALYSIS_TOOLS/'
sys.path.append(os.environ['AAT']+'ntupling/')
sys.path.append(os.environ['AAT']+'utilities/')
sys.path.append(os.environ['AAT']+'analyses/')
sys.path.append(os.environ['AAT']+'plotting_tools/')

import cutParser as cp
import createNtuple as cn
from view_streak import view_streak
from analyze_frame import analyze_frame
