#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 10:34:02 2017

@author: sgess
"""
import h5py

def createFileMap(file, path, depth, info, timeCheck, map_file):
    
    # Path is the current path in the h5 file
    if not path:
        #Print Header
        line = 'Path,Field,DataType,Size,Dim1,Dim2,AttrDepth,TimeInfo,Comment\n'
        map_file.write(line)
        
        # Loop over top level groups (directories)
        for name, item in file.items():
            if isinstance(item,h5py.Group):
                path = '/' + name
                # Reset info dictionary
                info['depth'] = depth
                info['dtype'] = None
                info['comment'] = None
                info['time_info'] = None
                info['size'] = None
                info['dim1'] = None
                info['dim2'] = None
                # Pass the current path and repeat
                createFileMap(file, path, depth, info, timeCheck, map_file)
            else:
                return
    else:
        # Set the current path
        top = path
        # Keep track of how 'deep' we are in the file
        depth += 1
        # Loop over next level groups (directories)
        for name, item in file[top].items():
            # If the item is a group, check for attributes
            if isinstance(item,h5py.Group):
                path = top + '/' + name
                # Reset info dictionary
                info['depth'] = depth
                info['dtype'] = None
                info['comment'] = None
                info['time_info'] = None
                info['size'] = None
                info['dim1'] = None
                info['dim2'] = None
                if item.attrs.__contains__('exception'):
                    info['depth'] = depth
                if item.attrs.__contains__('comment'):
                    info['comment'] = item.attrs['comment']
                if item.attrs.__contains__('acqStamp'):
                    info['time_info'] = 'acqStamp'
                # Pass the current path and repeat
                createFileMap(file, path, depth, info, timeCheck, map_file)
            # If the item is a dataset, check for attributes
            elif isinstance(item,h5py.Dataset):
                # Reset info dictionary
                info['dtype'] = None
                info['size'] = None
                info['dim1'] = None
                info['dim2'] = None
                if item.attrs.__contains__('exception'):
                    info['depth'] = 0
                if item.attrs.__contains__('comment'):
                    info['comment'] = item.attrs['comment']
                if path in timeCheck.timing_dictionary:
                    if path+'/'+timeCheck.timing_dictionary[path] in file:
                        info['time_info'] = timeCheck.timing_dictionary[path]
                elif item.attrs.__contains__('acqStamp'):
                    info['time_info'] = 'acqStamp'
                # check that the dataset has a known type (fails for arrays of bools)
                try:
                    info['dtype'] = item.dtype
                except:
                    print(name + ' has bad type')
                # Check that the dataset has a reasonable size and shape
                info['size'] = int(item.size)
                if item.size and item.shape:
                    shape = item.shape
                    info['dim1'] = shape[0]
                    if len(shape) == 2:
                        info['dim2'] = shape[1]
                    else:
                        info['dim2'] = 0
                # Write all of the information gathered to the map file
                line = path+','
                line = line+name+','
                line = line+str(info['dtype'])+','
                line = line+str(info['size'])+','
                line = line+str(info['dim1'])+','
                line = line+str(info['dim2'])+','
                line = line+str(info['depth'])+','
                line = line+str(info['time_info'])+','
                if info['comment']:
                    line = line+str(info['comment'].decode())+'\n'
                else:
                    line = line+str(info['comment'])+'\n'
                map_file.write(line)