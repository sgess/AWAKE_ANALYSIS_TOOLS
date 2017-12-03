# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 05:56:00 2017

@author: Karl
"""

import numpy as np
import scipy as sp
from copy import deepcopy
import pathlib
import re
import os
import sys
import datetime as dt
import copy
import scipy.constants as spc
import h5py as h5
import matplotlib.pyplot as plt
import matplotlib.colors as plcol
import datetime

import awakeBones

def meanlist(x):
    r=deepcopy(x[0])
    for y in x[1:]:
        r +=y
    return r/len(x)

def Gauss2D(x, prm): #*1e4 ist da um die start guesses auf ein level zu bringen
    return prm[3]*1e4/(2*np.pi*prm[0]**2) * np.exp(- ((x[0] - prm[1])**2 + (x[1] - prm[2])**2)/(2*prm[0]**2)) + prm[4] #/(2*np.pi*prm[0]**2)

def gaussModel(x,coord,y):
    return (Gauss2D(coord,x) -y).ravel()

def Gauss1D(x,mu=0,sigma=1,Area=1):
    return Area/(np.sqrt(2*np.pi)*sigma)*np.exp(- (x-mu)**2/(2*sigma**2))
    
def GaussModel1D(x,coord,y):
    return x[1]*np.exp(- (coord)**2/(2*x[0]**2))-y #/(np.sqrt(2*np.pi)*x[0])

def Gauss1D(x,coord,y):
    if(len(x)<4):
        x4=0
    else:
        x4=x[3]
    return x[1]*np.exp(- (coord-x[2])**2/(2*x[0]**2))+x4-y #/(np.sqrt(2*np.pi)*x[0])    

def Gauss1D_n(x,coord,y,n=1):
    if(len(x)<4):
        x4=0
    else:
        x4=x[3]
    z=0
    for k in range(0,n):
       z=z+Gauss1D(x[k*3+0:k*3+3:1],coord,0) 
    
    return z-y+x[-1]    

def heavyside(x,a):
    return 0.5 * (np.sign(x-a) + 1)

"""
Berechne fuer jede datei die 2D FFT und schaetze fuer jeden datenpunkt innerhalb 
eines bestimmten bereichs (<500GHz und )
durch: 
http://ac.els-cdn.com/S109078070600019X/1-s2.0-S109078070600019X-main.pdf?_tid=6864cfc0-f44d-11e6-8538-00000aacb361&acdnat=1487252578_962b188f2fcb7d8af0850ce8a43f843e
"""

# np.pi/8 =0.39269908169872414
def zeta(x):
    return 2 + x**2 - 0.39269908169872414 * np.exp(-x**2/2) *( (2+x**2)*sp.special.iv(0,1/4*x**2) + x**2*sp.special.iv(1,1/4*x**2) )**2

def fpoint(x,mean,var):
    buff= zeta(x)*(1+mean**2/var) -2
    if buff <0:
        return x
    else:
        return x - np.sqrt(buff)

# 0.42920367320510344*estVar ist varianz der rici distribution, verwende das um zu cutten wenn estimated signal =0

def estimateCut(mean,var,nmin=1,nmax=100):
    skipZero=0
    if nmin==0:
        skipZero=1
    estSig=np.zeros(mean[nmin:nmax].shape)
    estNoise=np.zeros(mean[nmin:nmax].shape)

    for k in range(0,estSig.shape[0]):
        """if skipZero==1 and k==0:
                continue
        """
        try:
            buff=sp.optimize.brentq(fpoint,0,20,args=(mean[k+nmin],var[k+nmin]))
            estNoise[k]=var[k+nmin]/zeta(buff)
            estSig[k]=np.maximum(0,mean[k+nmin]**2 + (1-2/zeta(buff))*var[k+nmin])
        except:
                estNoise[k]=var[k+nmin]*2 # noise fuer signal=0 from wiki
                estSig[k]=0
    rice_mean=np.sqrt(estNoise)*np.sqrt(np.pi/2)*sp.special.assoc_laguerre(-estSig/estNoise/2,0.5,0)
    return estSig,estNoise,rice_mean, 0.42920367320510344*estNoise

def estimateCut2d(mean,var,nmin=1,nmax=100,ymin=0,ymax=50):
    skipZero=0
    if nmin==0:
        skipZero=1
    estSig=np.zeros(mean[nmin:nmax,ymin:ymax].shape)
    estNoise=np.zeros(mean[nmin:nmax,ymin:ymax].shape)
    
    for k in range(0,estSig.shape[0]):
        for l in range(0,estSig.shape[1]):
            if skipZero==1 and k==0:
                continue
            try:
                buff=sp.optimize.brentq(fpoint,0,20,args=(mean[k+nmin,l+ymin],var[k+nmin,l+ymin]))
                estNoise[k,l]=var[k+nmin,l+ymin]/zeta(buff)
                estSig[k,l]=np.maximum(0,mean[k+nmin,l+ymin]**2 + (1-2/zeta(buff))*var[k+nmin,l+ymin])
            except:
                estNoise[k,l]=1
                estSig[k,l]=0
    rice_mean=np.sqrt(estNoise)*np.sqrt(np.pi/2)*sp.special.assoc_laguerre(-estSig/estNoise/2,0.5,0)
    return estSig,estNoise,np.nan_to_num(rice_mean), 0.42920367320510344*np.nan_to_num(estNoise)
                                
    
"""
Useful functions needed
liest aus .txt datei enstprechend die werte aus (RB valve on/off laser power)
"""
def ldir(sFolder,fpattern=None):
    buff=searchdir(sFolder)
    return buff(filepattern=fpattern)
    
def getValandDate(x):
    x=pathlib.Path(x)
    timevals=[]
    objvals=[]
    with open(str(x)) as f:
        i=0
        for line in f:
            if i<2: # ueberspringe ersten 2 zeilen hardgecodet
                i +=1
                continue
            objvals.append(float( (line.split('\t')[-1]).split()[0].replace(',','.')  ))
            timevals.append( float(dt.datetime.strptime(line.split('\t')[0].split(',')[0],'%Y-%m-%d %H:%M:%S').timestamp())+3600) # +3600 weil UTC timestamp 1h spÃ¤ter ist als zÃ¼rich
    return np.array(timevals),np.array(objvals)
    

"""
Laser und Rubidium metadatenklasse
"""
# is sorted!
class NOSCDATA:
    def __init__(self,RbUp,RbDown,LaserPower):
        self.tRbUp,self.RbUp=getValandDate(RbUp)
        self.tRbDown,self.RbDown=getValandDate(RbDown)
        self.tLaser,self.LaserPow=getValandDate(LaserPower)

# nimmt ein objekt: NOSCDATA
def findMatchandvalue(time,y):
    LaserOn=False
    LaserPower=0
    try:
        buff= np.where( np.abs(time-y.tLaser) < 19)[0]
    except:
        buff=np.array([])
    if buff.any(): # non empty
        LaserOn=True
        LaserPower=y.LaserPow[buff] # gibt array aus -> korrigiere im return
    RbvalveUp=False
    # gibt alle zeiten aus die vor der aktuellen zeit sind
    # waehle den letzten value aus
    try:
        buff= np.where( (time-y.tRbUp) > 0)[0] [-1]
    except:
        buff=None
    if buff:
        RbvalveUp=not y.RbUp[buff]    
    
    RbvalveDown=False
    # gibt alle zeiten aus die vor der aktuellen zeit sind
    # waehle den letzten value aus
    try:
        buff= np.where( (time-y.tRbDown) > 0)[0] [-1]
    except:
        buff=None
    if buff:
        RbvalveDown=not y.RbDown[buff]
    return LaserOn,LaserPower,RbvalveDown,RbvalveUp
     
def getMetadata(x): #x has to be eventFile or path/str
    if x==None: #empty image
            return None,None,None,None
    if type(x)==type(str()) or type(x)==type(pathlib.Path()):
        x=eventFile(x)
    f=h5.File(str(x.path),'r')
    try:
        charComment=list(f['AwakeEventData']['XMPP-STREAK']['StreakImage']['streakImageInfo'])[0].decode()
    except:
        return None,None,None,None
    #shutter
    buff=charComment.find('shutter')
    shutter=charComment[buff:buff+20].split('"')[1]
    #slit
    buff=charComment.find('slit width')
    slit=float(charComment[buff:buff+19].split('"')[1])
    #MCP
    mcp=np.array(f['AwakeEventData']['XMPP-STREAK']['StreakImage']['streakImageMcpGain'])[0]
    #Timerange
    trange=list(f['AwakeEventData']['XMPP-STREAK']['StreakImage']['streakImageTimeRange'])[0].decode()
    if trange.split()[1]=='ps':
        trange=float(trange.split()[0])/1e3
    else:
        trange=float(trange.split()[0])
    f.close()
    return mcp,shutter,slit,trange
 
def _getBeamInten(x):
    if x==None:
        return 0
    f=h5.File(str(x),'r')
    rval=list(f['AwakeEventData']['TT41.BCTF.412340']['Acquisition']['totalIntensityPreferred'])[0]
    f.close()
    return rval    

def imagemean(x,x_axis,xmin=None,xmax=None):
    x_axis=x_axis.reshape(1,x_axis.shape[0])
    #bekommt einenen numpy array und berechnet daraus fuer alle y werte den x mw und varianz
    if xmin is not None:
        xmin=np.where(x_axis>xmin)[-1][0]
    else:
        xmin=0
    if xmax is not None:
        xmax=np.where(x_axis<xmax)[-1][-1]
    else:
        xmax=x_axis.size-1
    xax=x_axis[0,xmin:xmax]#.reshape(1,xmax-xmin)
    x=x[:,xmin:xmax]/x[:,xmin:xmax].sum(1).reshape(x.shape[0],1)
    mw=(x*xax).sum(1)
    var=np.zeros((x.shape[0],))
    for k in range(0,x.shape[0]):
        buff=np.nonzero(x[k,:])
        var[k]=(((xax[buff]-mw[k])**2)*x[k,buff]).sum(1)
    return mw,var            
    
def selectIMG(x,meanImg=0,y=['.'],externalFiles=awakeBones.nonEventData,imStats=False,*args,**kwargs):
    noMODInput=x
    fParserNI=cutParser.inputParser(noMODInput,setStandardKeyword={})
    fListTotal=filelist()
    for k in y:
        fListTotal+=ldir(k)
    NI_bkg=[]
    for k in fListTotal:
        if fParserNI(k):
            NI_bkg.append(k)
    RBUPFiles,RBDOWNFILES,LASERPOWER=externalFiles
    nonSCMData=NOSCDATA(RBUPFiles,RBDOWNFILES,LASERPOWER)
    NI_bkg=[scMetadata(k) for k in NI_bkg]
    NI_Metadata=metadatalist([envMetadata(x,nonSCMData) for x in NI_bkg])
    if len(kwargs)>0:
        NI_Final=NI_Metadata.search(**kwargs)
    else:
        NI_Final=NI_Metadata.search(LaserOn=False,RbValveDown=True,RbValveUp=True,shutter='open')
    NI_Imagelist=imagelist(NI_Final)
    NI_Imagelist.subtractBKG(meanImg)
    if imStats:
        meanImg,var=eventImageListBKG.mean()
    else:
        meanImg=None
        var=None
    return NI_Imagelist,meanImg,var

"""
EventData to a streak camera image class
These classes create metadata infomration for sc images
"""
    
    
class eventFile:
    def __init__(self,x=None):
        if x is not None:
            self.path=pathlib.Path(x)
            self.time=int(np.floor(float(self.path.name.split('_')[0])/1e9))
            self.timeUTC=datetime.datetime.utcfromtimestamp(self.time)
            self.timeSTR=datetime.datetime.strftime(self.timeUTC,'%Y/%m/%d %H-%M-%S')
            self.Number=int(np.floor(float(self.path.name.split('_')[2].split('.')[0])))
        else:
            self.path=None
            self.time=None
            self.Number=None
        self.BeamIntensity=_getBeamInten(self.path)
        
    def __eq__(self,other):
        if isinstance(other,eventFile):
            return self.time==other.time
        return False
    
class scMetadata(eventFile):
    def __init__(self,x=None):
        super().__init__(x)
        # missing: mode
        self.mcp,self.shutter,self.slit,self.trange=getMetadata(x)
        

#
# metadatenklasse die alles enthÃ¤lt
# enthaelt auch die laser/rb werte
#    
    # gives horrible error when not used properly!
class envMetadata(scMetadata):
    def __init__(self,x,y=None):
        if type(x)==type(str()) or type(x)==type(pathlib.Path()):
            super().__init__(x)
            if y is not None:
                self.LaserOn,self.LaserPower,self.RbValveDown,self.RbValveUp=findMatchandvalue(self.time,y)
        else:
            
            #copy scMetadata
            self.mcp=x.mcp
            self.shutter=x.shutter
            self.slit=x.slit
            self.trange=x.trange
            
            self.path=x.path
            self.time=x.time
            self.timeUTC=x.timeUTC
            self.timeSTR=x.timeSTR
            self.Number=x.Number
            self.BeamIntensity=x.BeamIntensity
            if y is not None:
                self.LaserOn,self.LaserPower,self.RbValveDown,self.RbValveUp=findMatchandvalue(self.time,y)
            else:
                self.LaserOn=x.LaserOn
                self.LaserPower=x.LaserPower
                self.RbValveDown=x.RbValveDown
                self.RbValveUp=x.RbValveUp

#
# scImage class includes either all metadata orr only scmetadata, has additionally image properties
#
class scImage(envMetadata,scMetadata):
    def __init__(self,x=None):
        if isinstance(x,scImage):
            self.copy_constructor(x)
            return
        if type(x)==type(str()) or type(x) == type(pathlib.Path()):
            envMetadata.__init__(self,x)
        if isinstance(x,scMetadata) and isinstance(x,envMetadata):
            #print('blub')
            super().__init__(x)
        elif isinstance(x,scMetadata): #wird: elif isinstance(x,envMetadata)  ?
            #print('bla')
            super().__init__(x.path)
        #print('blaub')
        # missing: imheihgt/width
        if type(x)==type(None):
            self.image=None
            self.t=None
            self.x=None
        else:
            f=h5.File(str(self.path),'r')
            try:
                self.image=np.array(f['AwakeEventData']['XMPP-STREAK']['StreakImage']['streakImageData']).reshape(512,672)
                self.t=np.array(f['AwakeEventData']['XMPP-STREAK']['StreakImage']['streakImageTimeValues'])
                # safly needed workaround
                self.t[0]=self.t[1]-(np.abs(self.t[1]-self.t[2]))
            except:
                self.image=None
                self.t=None
            self.x=(np.linspace(0,4.04,672)-2.02)*4.35  #hardcoded atm
            f.close()
    def copy_constructor(self,other):
        self.super(scImage,self).__init__(other) # funzt weil super der reihe nach probiert aufzurufen
        self.image=other.image
        self.t=other.t
        self.x=other.x         


"""
Special function for reading non eventbuilder files (i.e. .img vendor files)
and returns a eventbuilder streak class
"""
        
def scread(filename,mode="ieee-le") :
        
        # select mode
        if mode=="ieee-le":
                mode="<"
        else :
                mode=">"
        
        # oeffne die datei
        try :
                f=open(filename,'rb')
        except OSError as err :
                print("OS error:".format(err))
        else :
                data_type=np.dtype(np.uint16)
                data_type.newbyteorder(mode)
                img_type=np.dtype(np.uint32)
                img_type.newbyteorder(mode)
                
                char_im=np.frombuffer(f.read(2),data_type)
                comm_length=np.frombuffer(f.read(2),data_type)
                im_width=np.int(np.frombuffer(f.read(2),data_type)[0])
                im_height=np.int(np.frombuffer(f.read(2),data_type)[0])
                x_offs=np.frombuffer(f.read(2),data_type)
                y_offs=np.frombuffer(f.read(2),data_type)
                bit_depth=np.frombuffer(f.read(2),data_type)
                if bit_depth==0 :
                        bit_depth=1
                else :
                        bit_depth=int((2**(bit_depth+2))/8)
                        
                f.seek(25*2,1) #die naechsten 50 byte sind useless dewegen werden sie uebersprungen, whence=1 weil relative position
                comment=np.frombuffer(f.read(comm_length[0]),np.dtype(np.uint8)).view('c') # uint8=char -> view('c')
                img_type=np.dtype('uint'+str(int(8*bit_depth)))
                imgsize=im_width*im_height
                # data stored zuerst im_width (656 typischerweise), das ganze im_heigth mal (typ. 508)
                y=np.frombuffer(f.read(imgsize*bit_depth),img_type)
                mat_data=np.asmatrix(np.ones([im_height,im_width],np.dtype(np.int)))
                for k in range(im_height): 
                        mat_data[k,:]=np.asmatrix( y[(k*im_width):((k+1)*im_width)] )
                
                        

        f.close()
        comment=str(comment.tostring())
        # create important data
        # slit:
        buff=comment.find('Slit Width')
        slitWidth=float(comment[buff:buff+19].split('"')[1])
        # data matrix
        mat_data=np.array(mat_data)
        # mcp
        buff=comment.find('MCP Gain')
        MCP=float(comment[buff:buff+18].split(',')[0].split('"')[1])
        #timescale immer in ns
        buff=comment.find('Time Range')
        
        # implement hier den modus weil einfacher
        mode=comment[buff:-1].find('Mode')
        mode=comment[buff+mode:buff+mode+20].split('"')[1]
        
        # weiter mit timescale
        buff=comment[buff+8:buff+19].split('"')[1]
        timescale=float(buff.split(' ')[0])
        if buff.split(' ')[1]=='ps':
            timescale=timescale/1e3
        #shutter
        buff=comment.find('Shutter')
        shutter=False
        if comment[buff+5:buff+13].split('"')[1]=='Open':
            shutter=True  
        
        # mache hier eine eventbuilder klasse daraus
        buff=scImage()
        #members=[attr for attr in dir(scImage()) if not callable(attr) and not attr.startswith("__") ]
        buff.path=pathlib.Path(filename)
        buff.image=mat_data
        buff.mcp=MCP
        buff.Number=None
        buff.trange=timescale
        buff.slit=slitWidth
        buff.shutter=shutter
        
        return buff
        

"""
Finding files and getting fileslists, regexpression base, together with subclasses for streak images
"""

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = (pathlib.Path(newPath)).expanduser()
        #self.newPath = newPath

    def __enter__(self): #damit man die klasse mit with benutzen kann
        self.savedPath = pathlib.Path.cwd()
        os.chdir(str(self.newPath))

    def __exit__(self, etype, value, traceback):
        os.chdir(str(self.savedPath))

class filelist:
    def __init__(self,x=[]):
        #print(x)
        if isinstance(x,filelist):
            self.flist=x.flist
        elif hasattr(x,'__getitem__'):#type(x).__name__=='list':
            self.flist=x
        else:
            self.flist=[x]
            
    def __eq__(self,other):
        if isinstance(other,filelist):
            return self.flist==other.flist
        return False
    def __getitem__(self,num):
        return self.flist[num]
    def match(self,regExpr=None):
        rlist=list()
        if regExpr is not None:
            for i in self.flist:
                if(re.search(re.compile(regExpr),str(i))):
                    rlist.append(i)
        return filelist(rlist)
    def __repr__(self):
        return str(self.flist)
    def __len__(self):
        return len(self.flist)
    def __iter__(self):
        return iter(self.flist)
    def __add__(self,other):
        if type(other) != type(self):
            return self
        return filelist(self.flist + other.flist)
        
class searchdir:
        def __init__(self, readDir='.', filepattern='.*'):
            self.fileExt=filepattern
            self.rDir=readDir
            
        def __call__(self,readDir=None,filepattern=None):
            if readDir!=None and not isinstance(readDir,filelist):
                self.rDir=readDir
            filesImage=filelist([])
            if filepattern is not None:
                self.fileExt=filepattern
            if isinstance(readDir,filelist):
                for fiter in readDir.flist:
                    if(re.search(self.fileExt,fiter)):
                        filesImage.flist.append(os.path.join(str(self.rDir),fiter))
                return filesImage
            #self.rDir=self.pathlib.Path(self.rDir)
            with cd(self.rDir):
                files=os.listdir()
                # suche die dateien
                for fiter in files:
                    if(re.search(self.fileExt,fiter)):
                        filesImage.flist.append(os.path.join(str(self.rDir),fiter))
                return filesImage

class metadatalist(filelist):
    def __init__(self,x=[]):
        super().__init__(x)
    def append(self,x):
        self.flist.append(x)
    def search(self,**kwargs):
        # check hier for **kwarg (z.b. mcp=30) und dann gib nur dinge zurÃ¼ck die das attribut haben 
        buff=[]
        for k in self.flist:
            isvalid=[getattr(k,str(name))==val for name,val in kwargs.items()]
            if all(isvalid):                 
                buff.append(k)
        return metadatalist(buff)
        
class imagelist(metadatalist):
    def __init__(self,x=[]):
        super().__init__(x)
        if isinstance(x,metadatalist) and not isinstance(x,imagelist):
            self.flist=[scImage(k) for k in x]
        """
        if isinstance(x,imagelist):
            self.flist=x.flist
        if isinstance(x,list):
            self.flist=x
        """
        if isinstance(x,scImage):
            self.flist=[x]
            
    def subtractBKG(self,x):
        if isinstance(x,np.ndarray):
            for l,k in enumerate(self.flist):
                self.flist[l].image=k.image-x
        elif type(x).__name__=='scImage':
            for l,k in enumerate(self.flist):
                try:
                    self.flist[l].image=k.image-x.image
                except:
                    pass
        return self
    def mean(self): # erschafft den mittelwert, eigentlich nur useful fuer
    # background aber man kanns ja mal behalten
        try:
            buff=np.zeros(self.flist[0].image.shape)
            buffvar=np.zeros(self.flist[0].image.shape)
            rVal=self.flist[0]
            for k in self.flist:
                buff += k.image
            rVal.image=buff/len(self.flist)
            for k in self.flist:
                buffvar += (k.image-rVal.image)**2
            buffvar=buffvar/(len(self.flist)-1)
            return rVal,buffvar # returns scImage und varianzMatrix
        except:
            return scImage()

class roi: #agiert auf numpy arrays mindestens 2d
    def __init__(self,x=None,*args):
        if x is None:
            self.xs=0
            self.xe=None
            self.ys=0
            self.ye=None
            return
        # atm: alles per args angegbene
        self.xs=x
        buff=[]
        for k in args:
            buff.append(k)
        self.xe=buff[0]
        self.ys=buff[1]
        self.ye=buff[2]
        #if type(x)== type(list()):
        #    for k,l in zip(x,)
    def shape(self):
        if self.xe==None or self.ye==None:
            return (0,0)
        return (self.xe-self.xs,self.ye-self.ys)
        
        
    def __call__(self,x):
        buff=x[self.ys:self.ye,self.xs:self.xe]
        return buff,buff.shape

class scManipulation(imagelist):
    def __init__(self,x,fftroi=None,varianz=None):
        super().__init__(x)
        self.cut=False
        if type(fftroi) == type(roi()):
            self.roi=fftroi
        else:
            self.roi=roi(fftroi)
        self.var=varianz
        
    def cutNoise(self,Nsigma=2,var=None,enforce=False):
        if self.cut==True and enforce==False:
            return self
        if var is not None:
            self.var=var
        if self.var is None:
            return self
        for k in self.flist:
            buff=np.where(k.image-Nsigma*np.sqrt(self.var) <0)
            #k.image=np.maximum(0,k.image-Nsigma*np.sqrt(self.var)) #scImage
            k.image[buff]=0
        return self
    
    def lin_interp(self,x=None,roi=None):
        if roi is not None:
            self.roi=roi
        buff=[]
        if x is None:
            for k in self.flist:
                self.roi(k.image)
            return
        # nehme an ich habe also schon einen lineout bekommen
        prm=np.polyfit(np.linspace(0,np.max(x.shape)-1,np.max(x.shape)),x,1)
        #return x-(x[-1]-x[0])/(np.max(x.shape)-1)*np.linspace(0,np.max(x.shape)-1,np.max(x.shape)) - x[0]
        return x-prm[0]*np.linspace(0,np.max(x.shape)-1,np.max(x.shape))-prm[1]
    
    def profile(self,dim=1,roi=None,mean=True,window=None):
        if roi is not None:
            self.roi=roi
        buff=[]
        win=np.ones(self.flist[0].image.shape[0])
        if window is not None:
            win=win*window(win.shape[0])
        for k in self.flist:
            im,sh=self.roi(k.image)
            if mean:
                buff.append(im.sum(dim)/sh[1])
            else:
                buff.append(im.sum(dim))
            if window is not None:
                buff[-1]=buff[-1]*win
        return buff
    
    def roiMean(self,roi=None):
        if roi is not None:
            self.roi=roi
        ebuff=0
        # nehm an dass jedes bild gleich viele pixel hat
        if self.roi.xe is None:
            ebuff=(self.flist[0].image.shape[1]-1).T
            xax=np.linspace(self.roi.xs,ebuff)
        else:
            xax=np.arange(self.roi.xs,self.roi.xe).T
        m=[]
        v=[]
        for k in self.flist:
            m1,v1=imagemean(k.image,k.x,k.x[self.roi.xs],k.x[:self.roi.xe][-1])
            m.append(m1)
            v.append(v1)
        return m,v
        

class scFFT(scManipulation):
    def __init__(self,x,fftroi=None):
        super().__init__(x,fftroi)
        """
        if type(fftroi) == type(roi()):
            self.roi=fftroi
        else:
            self.roi=roi(fftroi)
        """
    def __call__(self):
        pass
    
    def fft1d(self,norm=False,linInterp=False,windowFKT=None):
        retVal=[]
        retValFFT=[]
        bbool=False
        for k in self.flist:
            try:
                buffroi,shaperoi=self.roi(k.image)
            except:
                buffroi,shaperoi=self.roi(k)
            
            buffroi=buffroi.sum(1)/shaperoi[1]
            nrg=buffroi.sum()
            if windowFKT is not None:
                buffroi=windowFKT(buffroi.shape[0])*buffroi
            if linInterp:
                buffroi=self.lin_interp(buffroi)
            if norm:
                retVal.append(np.abs(np.fft.fft(buffroi))/buffroi.size/nrg) #
            else:
                retVal.append(np.abs(np.fft.fft(buffroi))/buffroi.size) #
            if bbool==False:
                try:
                    df=1/(k.t[:self.roi.ye][-1]-k.t[self.roi.ys])*1e3 #tim
                    retValFFT=np.linspace(0,(shaperoi[0]-1)*df,shaperoi[0])
                except:
                    df=1/(k.shape[0]) #tim
                    retValFFT=np.linspace(0,(k.shape[0]-1)*df,k.shape[0])
                bbool=True
        return retVal,retValFFT
    
    def fftline(self,norm=False):
        retVal=[]
        retValFFT=[]
        bbool=False
        for k in self.flist:
            try:
                buffroi,shaperoi=self.roi(k.image)
            except:
                buffroi,shaperoi=self.roi(k)
            buff=np.zeros(shaperoi)
            normsum=(np.abs(np.fft.fft(buffroi.sum(1)))/shaperoi[0]/shaperoi[1])
            for l in range(0,shaperoi[1]):    
                if norm:
                    buff[:,l]=np.abs(np.fft.fft(buffroi[:,l]))/shaperoi[0]/normsum[l]#/buffroi.sum() #
                else:
                    buff[:,l]=np.abs(np.fft.fft(buffroi[:,l]))/shaperoi[0]/normsum[l] #
            retVal.append(buff)
            if bbool==False:
                df=1/(k.t[:self.roi.ye][-1]-k.t[self.roi.ys])*1e3 #tim
                retValFFT=np.linspace(0,(shaperoi[0]-1)*df,shaperoi[0])
                bbool=True
        return retVal,retValFFT        
    
    def fft2d(self,norm=False,windowX=None,windowY=None):
        retVal=[]
        retValFFTY=[]
        retValFFTX=[]
        buffroi,shaperoi=self.roi(self.flist[0].image)
        window=np.ones(shaperoi)
        if windowX is not None:
            buffX=windowX(shaperoi[1]).reshape(1,shaperoi[1])
            window=window*buffX
        if windowY is not None:
            buffY=windowY(shaperoi[0]).reshape(shaperoi[0],1)
            window=window*buffY
            
        
        bbool=False
        for k in self.flist:
            buffroi,shaperoi=self.roi(k.image)
            nrg=buffroi.sum()
            if norm:
                retVal.append(np.abs(np.fft.fft2(buffroi*window))/buffroi.size/nrg)
            else:
                retVal.append(np.abs(np.fft.fft2(buffroi*window))/buffroi.size)
            if bbool==False:
                df=1/(k.t[:self.roi.ye][-1]-k.t[self.roi.ys])*1e3 #time in 1/ps <- annahme daraus folgt *1e3
                retValFFTY=np.linspace(0,(shaperoi[0]-1)*df,shaperoi[0])
                dx=1/(k.x[:self.roi.ye][-1]-k.x[self.roi.ys])*spc.c*1e3/2/np.pi/1e9 #space
                retValFFTX=np.linspace(0,(shaperoi[1]-1)*dx,shaperoi[1])
                bbool=True
            
        return retVal,retValFFTX,retValFFTY
    
    def projectFFT(self,x,anyroi=None):
        if anyroi==None:
            anyroi=roi()
            #buff=np.zeros((x[0].shape[0],))
            #buff=np.zeros(anyroi.shape())
        buff=[]
        for k in x:
            mybuff,roisize=anyroi(k)
            buff += [mybuff.sum(1)/roisize[1]]
        #rbuff=np.zeros(buff[0].shape)
        #for k in buff:
        #    rbuff +=k
        return buff
    
    def zpadInterp1d(self,nZPad=5,norm=False,subtractMean=False,windowFKT=None):
        # 1d interpolation via zeropadding, subtract mean to get rid
        retVal=[]
        retValFFT=[]
        bbool=False
        for k in self.flist:
            try:
                buffroi,shaperoi=self.roi(k.image)
            except:
                buffroi,shaperoi=self.roi(k)
            
            buffroi=buffroi.sum(1)/shaperoi[1]
            nrg=buffroi.sum()
            if windowFKT is not None:
                buffroi=windowFKT(buffroi.shape[0])*buffroi
            lenbuff=buffroi.shape[0]
            buffmean=np.mean(buffroi)
            if subtractMean:
                buffroi=buffroi-buffmean # subtract mean to get rid of ringing effects
            buffroi=np.pad(buffroi,(0, (nZPad-1)*lenbuff ),'constant',constant_values=0)
            if norm:
                retVal.append(np.abs(np.fft.fft(buffroi))/lenbuff/nrg) #
            else:
                retVal.append(np.abs(np.fft.fft(buffroi))/buffroi.size) #
            if bbool==False:
                try:
                    df=1/(k.t[:self.roi.ye][-1]-k.t[self.roi.ys])*1e3 #tim
                    retValFFT=np.append(np.linspace(0,(shaperoi[0]-1)*df,buffroi.size-nZPad+1,endpoint=True),np.linspace((shaperoi[0]-1)*df+df/nZPad,(shaperoi[0]-1)*df+df*(nZPad-1)/nZPad,nZPad-1,endpoint=False))
                except:
                    df=1/(k.shape[0]) #tim
                    retValFFT=np.append(np.linspace(0,(k.shape[0]-1)*df,buffroi.size-nZPad+1,endpoint=True),np.linspace((k.shape[0]-1)*df+df/nZPad,(k.shape[0]-1)*df+df*(nZPad-1)/nZPad,nZPad-1,endpoint=False))
                bbool=True
        return retVal,retValFFT
 
    def zpadInterp2d(self,nZPad=3,norm=True,subtractMean=False,windowX=None,windowY=None):
            # 2d interpolation via zeropadding, subtract mean to get rid
            retVal=[]
            retValFFTY=[]
            retValFFTX=[]
            bbool=False
            buffroi,shaperoi=self.roi(self.flist[0].image)
            lenbuffY=buffroi.shape[0]
            lenbuffX=buffroi.shape[1]
            window=np.ones(shaperoi)
            if windowX is not None:
                buffX=windowX(shaperoi[1]).reshape(1,shaperoi[1])
                window=window*buffX
            if windowY is not None:
                buffY=windowY(shaperoi[0]).reshape(shaperoi[0],1)
                window=window*buffY
            for k in self.flist:
                try:
                    buffroi,shaperoi=self.roi(k.image)
                except:
                    buffroi,shaperoi=self.roi(k)
                nrg=buffroi.sum()
                if (windowX is not None) or (windowY is not None):
                    buffroi=window*buffroi
                if subtractMean:
                    buffmean=np.mean(buffroi)
                    buffroi=buffroi-buffmean # subtract mean to get rid of ringing effects
                
                buffroi=np.pad(buffroi,[(0, (nZPad-1)*lenbuffY),(0,(nZPad-1)*lenbuffX)] ,'constant',constant_values=0)
                if norm:
                    retVal.append(np.abs(np.fft.fft2(buffroi))/buffroi.size/nrg) #
                    """if k.Number==3002:
                        plt.figure()
                        plt.imshow(np.abs(np.fft.fft(buffroi)),vmin=0,vmax=1e-7)
                    """
                else:
                    retVal.append(np.abs(np.fft.fft2(buffroi))/buffroi.size) #
                if bbool==False:
                    try:
                        df=1/(k.t[:self.roi.ye][-1]-k.t[self.roi.ys])*1e3 #tim
                        retValFFTY=np.append(np.linspace(0,(shaperoi[0]-1)*df,buffroi.shape[0]-nZPad+1,endpoint=True),np.linspace((shaperoi[0]-1)*df+df/nZPad,(shaperoi[0]-1)*df+df*(nZPad-1)/nZPad,nZPad-1,endpoint=False))
                        dx=1/(k.x[:self.roi.ye][-1]-k.x[self.roi.ys])*spc.c*1e3/2/np.pi/1e9 #space
                        retValFFTX=np.append(np.linspace(0,(shaperoi[1]-1)*df,buffroi.shape[1]-nZPad+1,endpoint=True),np.linspace((shaperoi[1]-1)*dx+dx/nZPad,(shaperoi[1]-1)*dx+dx*(nZPad-1)/nZPad,nZPad-1,endpoint=False))
                    except:
                        df=1/(k.shape[0]) #tim
                        retValFFTY=np.append(np.linspace(0,(k.shape[0]-1)*df,buffroi.shape[0]-nZPad+1,endpoint=True),np.linspace((k.shape[0]-1)*df+df/nZPad,(k.shape[0]-1)*df+df*(nZPad-1)/nZPad,nZPad-1,endpoint=False))
                        dx=1/(k.x[:self.roi.ye][-1]-k.x[self.roi.ys])*spc.c*1e3/2/np.pi/1e9 #space
                        retValFFTXnp.append(np.linspace(0,(k.shape[1]-1)*dx,buffroi.shape[1]-nZPad+1,endpoint=True),np.linspace((k.shape[1]-1)*dx+dx/nZPad,(k.shape[1]-1)*dx+dx*(nZPad-1)/nZPad,nZPad-1,endpoint=False))
                    bbool=True
            return retVal,retValFFTY, retValFFTX
    

"""
Plotting class for streak class
takes as inpout an scImage object and then can do different plots for it

Class is inefficient, but thats ok
"""          
class plotSC:
    
    def __init__(self,x,tickfsize=20,setmax=275,prf_roi=roi(225,425,0,None)):
        if type(x).__name__ != 'scImage':
            x=scImage(x) #normalerweise funzt das nur noch mit pass
        self.image=x
        self.tickfsize=tickfsize
        
        self.roi=prf_roi
            
        self.linewidth=1.5
        self.max=setmax
        self.min=np.min(self.image.image)
        
        
    #def definePlot(self,)
    def streakOverview(self,fig=1,profile=True,prf_roi=None,statistics=False,stat_mean=True,ax=None,cmap='Blues',lsize=20,**kwargs):
        if prf_roi is not None:
            self.roi=prf_roi
        if ax is not None:
            a=ax
        else:
            plt.figure(fig).clf()
            a=plt.figure(fig).gca()
            fig=plt.gcf()
            fig.set_size_inches(18.5, 10.5)
        buff=a.imshow(self.image.image,vmin=self.min,vmax=self.max,extent=[self.image.x[0],self.image.x[-1],self.image.t[-1],self.image.t[0]],aspect='auto',cmap=plt.get_cmap(cmap))
        if ax is None:
            plt.colorbar(buff)
        a.set_xlabel('Beam transverse dimension (mm)',fontsize=lsize+2)
        a.set_ylabel('Time (ps)',fontsize=lsize+2)
        a_extra=None
        if ax is None:
            plt.gcf().suptitle(str(self.image.Number)+'/'+datetime.datetime.utcfromtimestamp(self.image.time).strftime('%h %d: %H-%M-%S')+'/Laser power: '+str(self.image.LaserPower)+'\nRb valve open up/downstream: ' +str(self.image.RbValveUp)+'/'+str(self.image.RbValveDown),fontsize=24)
        mean,varianz=imagemean(self.image.image,self.image.x,self.image.x[self.roi.xs],self.image.x[:self.roi.xe][-1])
        if stat_mean:
            a.plot(mean,self.image.t,c='r',linewidth=self.linewidth,linestyle='dotted')
        if statistics:
            a.plot(np.sqrt(varianz)+mean,self.image.t,c='m',linewidth=self.linewidth,linestyle='dotted')
            a.plot(-np.sqrt(varianz)+mean,self.image.t,c='m',linewidth=self.linewidth,linestyle='dotted')     
            
        if profile:
            t=self.image.t
            myprof=self.image.image[:,self.roi.xs:self.roi.xe].sum(1)/(self.roi.xe-self.roi.xs)
            a.plot((self.image.x[self.roi.xs],self.image.x[self.roi.xs]),(t[self.roi.ys],t[:self.roi.ye][-1]),linewidth=self.linewidth,linestyle='--',color='k')
            a.plot((self.image.x[self.roi.xe],self.image.x[self.roi.xe]),(t[self.roi.ys],t[:self.roi.ye][-1]),linewidth=self.linewidth,linestyle='--',color='k')
            a.plot((self.image.x[self.roi.xs],self.image.x[self.roi.xe]),(t[self.roi.ys],t[self.roi.ys]),linewidth=self.linewidth,linestyle='--',color='k')
            a.plot((self.image.x[self.roi.xs],self.image.x[self.roi.xe]),(t[:self.roi.ye][-1],t[:self.roi.ye][-1]),linewidth=self.linewidth,linestyle='--',color='k')
            
            # plotte jetzt ein lineout, hat keine labels
            a_extra=plt.gcf().add_axes(a.get_position(),frameon=False)
            a_extra.xaxis.tick_top()
            #ax0_extra.xaxis.set_ticklabels([])
            a_extra.plot(myprof,np.flipud(t),c='g',linewidth=self.linewidth*1.5,linestyle='dotted')
            a_extra.yaxis.set_ticklabels([])
            a_extra.set_yticks(ticks=[])
            
            a_extra.set_ylim(t[0],t[-1])
            a_extra.set_xlim(np.min(myprof),4*np.max(myprof))
        
        a.tick_params(axis='both',labelsize=lsize)
        a.set_xlim(self.image.x[0],self.image.x[-1])
        a.set_ylim(self.image.t[-1],self.image.t[0])
        return a,a_extra
    
    def streakStatistic(self,fig=2,ax=None,fsize=20):
        if ax is not None:
            a=ax
        else:
            plt.figure(fig).clf()
            a=plt.figure(fig).gca()
            fig=plt.gcf()
            fig.set_size_inches(18.5, 10.5)
        mean,varianz=imagemean(self.image.image,self.image.x,self.image.x[self.roi.xs],self.image.x[:self.roi.xe][-1])
        a.plot(self.image.t,mean,c='r',label='Mean value',linewidth=self.linewidth*1.0)
        if ax is None:
            plt.gcf().suptitle(str(self.image.Number)+'/'+datetime.datetime.utcfromtimestamp(self.image.time).strftime('%h %d: %H-%M-%S')+'/Laser power: '+str(self.image.LaserPower)+'\nRb valve open up/downstream: ' +str(self.image.RbValveUp)+'/'+str(self.image.RbValveDown),fontsize=22)
        a.set_ylabel('Mean (mm)',fontsize=fsize)
        plt.legend(loc='upper left',fontsize=fsize-2)
        a_extra=a.twinx()
        a_extra.plot(self.image.t,np.sqrt(varianz),c='m',linewidth=self.linewidth*1.0,label='std deviation')
        a_extra.set_ylabel('std deviation (mm)',fontsize=fsize)
        #a_extra.yaxis.set_ticklabels([])
        plt.legend(loc='upper right',fontsize=fsize-2)
        
        a.tick_params(axis='both',labelsize=fsize)
        a_extra.tick_params(axis='both',labelsize=fsize)
        a.set_xlabel('Time (ps)',fontsize=fsize)
        a.set_ylim(-.8,-.2)
        a_extra.set_ylim(0.4,0.9)
        return self
    
    def streakProfile(self,fig=3,a=None,fsize=20,n_roi=None,startGuess=np.array([0.7,100,-0.4,0]),dim=0,ax=None,**kwargs):
        if ax is not None:
            a=ax
        else:
            plt.figure(fig).clf()
            a=plt.figure(fig).gca()
            fig=plt.gcf()
            fig.set_size_inches(16.5, 9.5)
        roiL=n_roi
        buff=scManipulation(self.image)
        if n_roi is None:
            roiL=[self.roi]
        optimres=[]
        lObj=[]
        if ax is None:
            plt.gcf().suptitle(str(self.image.Number)+'/'+datetime.datetime.utcfromtimestamp(self.image.time).strftime('%h %d: %H-%M-%S')+'/Laser power: '+str(self.image.LaserPower)+'\nRb valve open up/downstream: ' +str(self.image.RbValveUp)+'/'+str(self.image.RbValveDown),fontsize=fsize+2)
        for k in roiL:
            x=self.image.x[k.xs:k.xe]
            buff2=buff.profile(dim,roi=k)
            optimres.append(sp.optimize.least_squares(scDefines.Gauss1D,startGuess,args=(x,buff2[0]),verbose=0))
            lObj+=a.plot(x,scDefines.Gauss1D(optimres[-1].x,x,0),linewidth=self.linewidth)
            lObj+=a.plot(x,buff2[0],linewidth=self.linewidth)
            #a.legend(lObj,['roi:'+str(l+1),'roi'+str(l+1)+' fit: '+'{0:0.2f}'.format(optimres[-1].x[0])+'and {0:0.2f}'.format(optimres[-1].x[2])])
            #l=l+1
        b=[]
        for k in range(0,len(optimres)):
            b+=['roi:'+str(k+1),'roi'+str(k+1)+' fit: '+'{0:0.2f}'.format(optimres[k].x[0])+' and {0:0.2f}'.format(optimres[k].x[2])]
        #a.legend(lObj,[['roi:'+str(k+1),'roi'+str(k+1)+' fit: '+'{0:0.2f}'.format(optimres[k].x[0])+'and {0:0.2f}'.format(optimres[k].x[2])] for k in range(0,len(optimres))])
        a.legend(lObj,b)
        """
        for k,l in zip(optimres,range(0,len(optimres))):
            a.plot(x,Gauss1D(k.x,x,0),x,,label='roi:'+str(l+1),linewidth=self.linewidth)
        """
        #plt.legend(loc='upper right',fontsize=fsize-2)
        a.tick_params(axis='both',labelsize=fsize)
        if dim==0:
            a.set_xlabel('Space (mm)',fontsize=fsize)
        else:
            a.set_xlabel('Time (ps)',fontsize=fsize)
        return self,optimres,a,lObj,b
        
    def __call__(self,figN,**kwargs): #standard plot image, lineout, FFT
        fig=plt.figure(figN)
        fig.set_size_inches(18.5,10)
        fig.clf()
        fig.suptitle(datetime.datetime.utcfromtimestamp(self.image.time).strftime('%h %d: %H-%M-%S')+' / Number:' + str(self.image.Number) + ' Laser Power:' +str(self.image.LaserPower) + ' Rb Valve Up/Down:' + str(self.image.RbValveDown) + '/' + str(self.image.RbValveUp),fontsize=18)
        self.ax=[fig.add_subplot(2,2,n+1) for n in range(0,4)]
        ax=self.ax
        
        self.streakOverview(ax=ax[0],profile=True,lsize=12,prf_roi=self.roi,statistics=True,**kwargs)
        self.streakStatistic(ax=ax[1],fsize=14)
        self.streakProfile(ax=ax[2],fsize=14,**kwargs)

        return self
