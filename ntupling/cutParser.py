# -*- coding: utf-8 -*-
"""
Created on Wed Feb  23 23:10:11 2017

@author: Karl
"""

"""
Fileparser, has to be python 2.7 compatible

problem: time conversion in _awakeTypeconversion() is timezone UTC the correct one?
"""


'''
Imports
'''
import h5py
import numpy as np
import copy
import cutParserDefines
"""
Comparison class
"""

class comparator:
    def __init__(self,string,cmptype,tocomp=None):
        self.compare=None
        self.cmptype=cmptype
        self.tocompare=tocomp
        self.string=string
        self.setcompare()

    def setcompare(self):
        if self.string=='<=' or self.string =='=<':
            self.compare=lambda x: self.cmptype.__le__(x,self.tocompare)
            return
        if self.string=='>=' or self.string =='=>':
            self.compare=lambda x: self.cmptype.__ge__(x,self.tocompare)
            return
        if self.string=='>': 
            self.compare=lambda x: self.cmptype.__gt__(x,self.tocompare)
            return
        if self.string=='<': 
            self.compare=lambda x: self.cmptype.__lt__(x,self.tocompare)
            return
        if self.string=='==' or self.string== '=': 
            self.compare=lambda x: self.cmptype.__eq__(x,self.tocompare)
            return    
        
    def __call__(self,other,casttype=None):
        if other == None:
            return np.array([False])
        if self.compare is not None and self.tocompare is not None:
            try:
                return self.compare(np.nan_to_num(other.astype(self.tocompare.dtype)))
            except:
                return np.array([False])
                
def _awakeTypeconversion(x):
#
# type conversion is simple:
# a) float
# b) if not a) time/date
# c) if not b) try bool
# d) if not c) then use as string
#    
    import copy
    import re
    import calendar
    import time
    import datetime
    import pytz
    
    local = pytz.timezone('Europe/Zurich')
    regExpr=re.compile('\s*[tTfF][rRaA][uUlL][sSeE]([eE])?\s*')
    reg=re.compile('\[([0-9]+\s?,?)+|(nan\s?,?)*|(inf\s?,?)*\]')
    buff=copy.deepcopy(x)
    try:
        x=np.array(buff.strip('[').strip(']').split(','),dtype=np.dtype('f'))
        return x, type(x)
    except:
        try:
            # in seconds, becomes ns and then datatype is numpy.int64
            # beware: datatype conversion is done in compare
            # is timezone correct? -> check with spencer
            # -3600 is a workaround
            #x=np.array(((calendar.timegm(time.strptime(x.replace('/',':').replace('-',':').strip(),"%d:%m:%Y %H:%M:%S"))-3600)*1e9),dtype='f')
            x=x.replace('/',':').replace('-',':').strip()
            dtUTC = datetime.datetime.strptime(x,'%d:%m:%Y %H:%M:%S')
            dtLOC = local.localize(dtUTC, is_dst=None)
            x = 1e9*dtLOC.timestamp()
            return x, type(x)
        except:
            m=regExpr.match(buff)
            if m:
               x=np.array(bool(buff),dtype='b')
               return x,type(x)
            else:
                m=reg.match(buff)
                if m.group()!='':
                    x=np.nan_to_num(np.fromstring(buff.strip('[').strip(']'),dtype=np.dtype('f'),sep=','))#,dtype=np.dtype('f')
                    return x,type(x)
                else:
                    x=np.array([buff])
                    return x,type(x)
        
"""
Things that need to be converted: time -> timestamp
Allow following operators:
    <, <=, >, >=, ==
"""            
class inputObject:

    import numpy as np
    class cmpObjects:
        cmpList=['<=','=<','<','==','>=','=>','>','='] #lazy solution to put '=' at the end
        def __init__(self):
            pass
        def __iter__(self):
            return iter(self.cmpList)
    cmplist=cmpObjects()

    def __init__(self,line):
        def assignBound(string,val):
            self.isinterval=True
            if string=='<=' or string =='<' or string=='=<':
                self.upper_bound=comparator(string,type(val),val)
            if string=='=>' or string =='>' or string=='>=':
                self.lower_bound=comparator(string,type(val),val)
            elif string=='=' or string=='==':
                self.eqval=comparator(string,type(val),val)
                self.lower_bound=self.eqval
                self.upper_bound=self.eqval
                self.isinterval=False
                
        def lineattr(line,string,attr='name',string2=None):
            if type(line) is not type(str()):
                return None
            if len(line.split(string))>1:
                val,mtype=_awakeTypeconversion(line.split(string)[1].strip())
                setattr(self,attr,line.split(string)[0].strip())
                assignBound(string,val)
                return val
            #wenn kein string zum trennen erkannt wird ist es anscheinend ein device was gewollt wird
            # autoset ist True
            buff=[k for k in self.cmplist]
            buffBool=False
            for k in buff:
                if line.find(k)!=-1:
                    buffBool=True
            if buffBool==False:
                setattr(self,attr,'DEVICE:'+line.strip())
                assignBound('==',True)
                self.isdevice=True
                self.value='DEVICE:'+line.strip()
                return None
            return None
        
        self.name=None
        self.eqval=None
        self.lower_bound=None
        self.upper_bound=None
        self.isinterval=True
        self.value=None
        self.isdevice=False
        
        for k in self.cmplist:
            buff=lineattr(line,k,'name')
            if buff is not None: #if we remove the break statement order doesnt matter in cmplist
                self.value=buff
                break
            
    def __call__(self,other):
        buff=np.zeros(int(other.size),dtype=other.dtype)
        if type(other) == type(np.array([])):
            buff=other
        else:
            other.read_direct(buff)
        if self.isinterval is False:
            return self.eqval(buff,other.dtype).all()
        if self.lower_bound is None:
            return self.upper_bound(buff,other.dtype)
        if self.upper_bound is None:    
            return self.lower_bound(buff,other.dtype).all()
        return (self.lower_bound(buff,other.dtype).all() and self.upper_bound(buff,other.dtype)).all()
        
    def __str__(self):
        try:
            return str(self.name+' ' +self.val)
        except:
            return str(self.name)
        

    def append(self,other,name=None):
        if other.eqval is not None:# ??? unsciher
            self.eqval=other.eqval
        if other.lower_bound is not None:
            self.lower_bound=other.lower_bound
            self.isinterval=True
        if other.upper_bound is not None:
            self.upper_bound=other.upper_bound        
            self.isinterval=True
        if name is not None:
            self.name=other.name
            self.value=other.value
        return self
   
class specialInputObject(inputObject):
    def __init__(self,x,fkt=None):
        inputObject.__init__(self,x)
        self.f=fkt
    def __call__(self,*args,**kwargs):
        if len(args)>0:
            if isinstance(args[0],h5py.File):
                return inputObject.__call__(self,self.f(args[0],kwargs))
        #except:
        if self.f is not None:
            return self.f(self.value,*args,**kwargs)
                

"""
/bla/blub <= sets upper bound
/bla/blub >= sets lower bound
/bla/blub == sets equality
last operator set is used for __call__ method
"""

#
# setFileList defines keyword that creates a filelist
#
     
class inputParser:
    
    def __init__(self,x,*args,setFileList='searchDir',setStandardKeyword=cutParserDefines.standardKeywords,setStandardFlags=cutParserDefines.standardFlags,**kwargs):
        
        self.specialKeywords={}
        self.flist=None        
        self.Flags={}
    
        specialNames={}
        for l,k in setStandardKeyword.items():
                specialNames[l]=k
        for l,k in enumerate(args):
            if type(k)==type(tuple()):
                specialNames[k[0]]=k[1]
        for l,k in kwargs.items():
            specialNames[l]=k

        self.path=str(x) #python 2.7 kompabilität
        argDict={}
        content=[]
        self.argDevices=[]
        with open(self.path,'r') as f:
            content=f.read().splitlines()
        for buff in content:
            buff=buff.split('#')[0].strip() # kill comments
            if buff=='': #kills empty lines and only comment lines
                continue
            # split now for <=,==,=>,<,>
            # mybuff=specialInputObject(buff)
            mybuff=inputObject(buff)
            if mybuff.name in specialNames.keys():    
                if mybuff.name in self.specialKeywords.keys():
                    self.specialKeywords[mybuff.name]=self.specialKeywords[mybuff.name].append(mybuff,mybuff.name)
                else:
                    #print(mybuff.name)
                    self.specialKeywords[mybuff.name]=specialInputObject(buff)
                    (self.specialKeywords[mybuff.name]).f=specialNames[mybuff.name]
                #continue
            elif mybuff.name in setStandardFlags:
                self.Flags[mybuff.name]=mybuff.value
                #continue
            else:
                if mybuff.name in argDict.keys() and mybuff.isdevice is not True:
                    argDict[mybuff.name]=argDict[mybuff.name].append(mybuff)
                elif mybuff.isdevice is not True:
                    argDict[mybuff.name]=mybuff
                elif mybuff.isdevice is True:
                    self.argDevices+=[mybuff.name]
        self.args=argDict
        if setFileList is not None and setFileList in self.specialKeywords.keys():
            self.flist=self.specialKeywords[setFileList](self.specialKeywords)
            del self.specialKeywords[setFileList] #delte setFileList

    def __call__(self,h5file=None,*args,**kwargs):
        if h5file is None and self.flist is not None:
            return self.__call__(self.flist)
        if type(h5file)==type(list()):
            buff=[]
            for k in range(0,len(h5file)):
                buff+=[self.__call__(h5file[k])]
            h5file=(buff,h5file)
            buff=np.array(h5file[1])[np.where(buff)].tolist()
            return buff,h5file
        try:
            f=h5file
            if type(h5file) is type(str()):
                f=h5py.File(h5file,'r')
            for k in self.args.keys():
                if k not in f:
                    f.close()
                    return False
                if not self.args[k](f[k]):
                    f.close()
                    return False
            for l,k in self.specialKeywords.items():
                if not k(*((f,),args),**kwargs):
                    f.close()
                    return False
            f.close()
            return True
        except OSError:
            #raise IOError('Input file not found, please provide a string or a filehandle')
            return False
            
    def __repr__(self):
        return repr(self.args)
