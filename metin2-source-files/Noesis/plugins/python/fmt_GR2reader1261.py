# Granny .GR2 Reader script by Jayn23 at XeNTaX fourm
# Credit to norbyte from DOS fourm - his source code for gr2 to collada was my main reference
# can be found at https://github.com/Norbyte/lslib

# Version 1.2.6.1
# Last updated 13.02.2020


#1.2.6.1
#Added missing degree to convert function (old animation to new animation)

#1.2.6
#Added Oprion to load all Mesh/Skeleton in a folder
#Change preview to always show Bauldrs Gate 3 meshes facing forward
#When format isnt supported shouldnt crash anymore

from math import *
from inc_noesis import *
import struct
import ctypes
import io
import sys
import math 
import bisect


#================================================================
#Plugin Options
#================================================================

MULTIFILE = 0 # when set to 1, all files in chosen folder are loaded and mesh/skeleten are merged to one scene, 2 - loads all meshes in folder, 3 - loads all skeleton, Should be used with all other options on 0.
SKELETON_LOAD = 0    #for loading paired skeleton file change value to 1
ANIMATION_MODE = 1   #switch between Animation modes, 1 - load paired animation file, 2 - load animation from main file, 0 - disable animation loading
MERGE_SCENE = 0    #if set  = 1 means merge is active, 0 merge is disabled, should be used only with animation mode 2, will merge all models + skeleton + animation in chosen file to 1 model/Scene 
ANIMATION_TRACK = 0  #for files with multiple animations - choose animation to load, 1 - will load first animation, 2 second animation etc... , in case you choose a animation number that dosent exist it will default to first animation
  
def registerNoesisTypes():
    handle = noesis.register("GR2 Reader", ".gr2;.fgx")    
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    #opens debug consle
    #noesis.logPopup()
    return 1


def noepyCheckType(data):
    '''Verify that the format is supported by this plugin. Default yes'''
    #I preform my check while reading mesh data
    return 1
    

#===========================================================
#Supporting Animation Classes
#===========================================================

class dakeyframes32f: # type = 0

    def __init__(self):

         self.Format = 0
         self.Degree = 0
         self.Dimension = 0
         self.Controls = []

    def NumKnots(self):
         return len(self.Controls)//self.Dimension


    def Knots(self):
        knots = []
        for i in range(self.NumKnots()):
            knots.append(float(i))
        return knots

    def GetTranslation(self):
        NumKnots = self.NumKnots()
        Translation = []
        for i in range(NumKnots):
            vector = [None]*3
            vector[0] = self.Controls[i * 3 + 0]
            vector[1] = self.Controls[i * 3 + 1]
            vector[2] = self.Controls[i * 3 + 2]
            Translation.append(vector)

        return Translation, self.Knots()

    def GetMartix(self):
        NumKnots = self.NumKnots()
        matrix = []
        for i in range(NumKnots):
            mat = [None]*9
            mat[0] = self.Controls[i * 9 + 0]
            mat[1] = self.Controls[i * 9 + 1]
            mat[2] = self.Controls[i * 9 + 2]
            mat[3] = self.Controls[i * 9 + 3]
            mat[4] = self.Controls[i * 9 + 4]
            mat[5] = self.Controls[i * 9 + 5]
            mat[6] = self.Controls[i * 9 + 6]
            mat[7] = self.Controls[i * 9 + 7]
            mat[8] = self.Controls[i * 9 + 8]
            matrix.append(mat)

        return matrix, self.Knots()

    def GetQuterions(self):
        NumKnots = self.NumKnots()
        quats = []
        for i in range(NumKnots):
            quat = [None]*4
            quat[0] = self.Controls[i * 4 + 0]
            quat[1] = self.Controls[i * 4 + 1]
            quat[2] = self.Controls[i * 4 + 2]
            quat[3] = self.Controls[i * 4 + 3]
            quats.append(quat)

        return quats, self.Knots()


class dak32fc32f: #type = 1

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.Padding = 0
         self.Knots = []
         self.Controls = []


    def NumKnots(self):
         return len(self.Knots)


    def GetTranslation(self): 
        NumKnots = self.NumKnots()
        Translation = []
        for i in range(NumKnots):
            vector = [None]*3
            vector[0] = self.Controls[i * 3 + 0]
            vector[1] = self.Controls[i * 3 + 1]
            vector[2] = self.Controls[i * 3 + 2]
            Translation.append(vector)

        return Translation, self.Knots

    def GetMartix(self):
        NumKnots = self.NumKnots()
        matrix = []
        for i in range(NumKnots):
            mat = [None]*9
            mat[0] = self.Controls[i * 9 + 0]
            mat[1] = self.Controls[i * 9 + 1]
            mat[2] = self.Controls[i * 9 + 2]
            mat[3] = self.Controls[i * 9 + 3]
            mat[4] = self.Controls[i * 9 + 4]
            mat[5] = self.Controls[i * 9 + 5]
            mat[6] = self.Controls[i * 9 + 6]
            mat[7] = self.Controls[i * 9 + 7]
            mat[8] = self.Controls[i * 9 + 8]
            matrix.append(mat)

        return matrix, self.Knots

    def GetQuterions(self):
        NumKnots = self.NumKnots()
        quats = []
        for i in range(NumKnots):
            quat = [None]*4
            quat[0] = self.Controls[i * 4 + 0]
            quat[1] = self.Controls[i * 4 + 1]
            quat[2] = self.Controls[i * 4 + 2]
            quat[3] = self.Controls[i * 4 + 3]
            quats.append(quat)

        return quats, self.Knots


# it isnt correct to return identity values for animation!! , i fix it before applying flat transform list
class daidentity: #type 2

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.Dimension = 0

    def NumKnots(self):
        return 1

    def knots(self):
        a = [0] 
        return a

    def GetTranslation(self):
        IdentityPos = [[0.0,0.0,0.0]]
        return IdentityPos, self.knots()
    
    def GetQuterions(self):
        IdentityQuat = [[0.0,0.0,0.0,1.0]]
        return IdentityQuat ,self.knots()
        
    def GetMartix(self):
        IdentityMatrix = [[1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]]
        return IdentityMatrix, self.knots()


#holds a single constant value. 
class daconstant32f: # type = 3

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.Padding = 0
         self.Controls = []

    def NumKnots(self):
        return 1

    def knots(self):
        return [0]

    def GetQuterions(self):
        q = [None]*4
        q[0] = self.Controls[0]
        q[1] = self.Controls[1]
        q[2] = self.Controls[2]
        q[3] = self.Controls[3]

        return [q], self.knots()


    def GetTranslation(self): 
        l = [None]*3
        l[0] = self.Controls[0]
        l[1] = self.Controls[1]
        l[2] = self.Controls[2]

        return [l], self.knots()
        
        
    def GetMartix(self):
        mat = [None]*9
        mat[0] = self.Controls[0]
        mat[1] = self.Controls[1]
        mat[2] = self.Controls[2]
        mat[3] = self.Controls[3]
        mat[4] = self.Controls[4]
        mat[5] = self.Controls[5]
        mat[6] = self.Controls[6]
        mat[7] = self.Controls[7]
        mat[8] = self.Controls[8]

        return [mat], self.knots()


#only stores 3-dimensional data
class d3constant32f: # type = 4

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.Padding = 0
         self.Controls = []

    def NumKnots(self):
        return 1

    def knots(self):
        return 0

    def GetTranslation(self):
        v = [None]*3
        v[0] = self.Controls[0]
        v[1] = self.Controls[1]
        v[2] = self.Controls[2]

        Knots = []
        for i in range(self.NumKnots()):
            Knots.append(self.knots())

        return [v], Knots


#only stores 4-dimensional data
class d4constant32f: # type = 5

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.Padding = 0
         self.Controls = []

    def NumKnots(self):
        return 1

    def knots(self):
        return [0]

    def GetQuterions(self):
        q = [None]*4
        q[0] = self.Controls[0]
        q[1] = self.Controls[1]
        q[2] = self.Controls[2]
        q[3] = self.Controls[3]
        return [q], self.knots()


class dak16uc16u: # type = 6

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScaleOffsetCount = 0
         self.ControlScaleOffsets = []
         self.KnotsControls = []


    def Components(self):
        return len(self.ControlScaleOffsets)//2

    def NumKnots(self):
        return len(self.KnotsControls)//(self.Components() + 1)

    def Knots(self):
        scale = self.ConvertOneOverKnotScaleTrunc()
        numKnots = self.NumKnots()
        knots = []
        for i in range(numKnots): 
            knots.append(self.KnotsControls[i]/scale)
        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetMartix(self):
        numKnots = self.NumKnots()
        matrix = []
        for i in range(numKnots):
            mat = [None]*9
            mat[0] = self.KnotsControls[numKnots + i * 9 + 0] * self.ControlScaleOffsets[0] + self.ControlScaleOffsets[9 + 0]
            mat[1] = self.KnotsControls[numKnots + i * 9 + 1] * self.ControlScaleOffsets[1] + self.ControlScaleOffsets[9 + 1]
            mat[2] = self.KnotsControls[numKnots + i * 9 + 2] * self.ControlScaleOffsets[2] + self.ControlScaleOffsets[9 + 2]
            mat[3] = self.KnotsControls[numKnots + i * 9 + 3] * self.ControlScaleOffsets[3] + self.ControlScaleOffsets[9 + 3]
            mat[4] = self.KnotsControls[numKnots + i * 9 + 4] * self.ControlScaleOffsets[4] + self.ControlScaleOffsets[9 + 4]
            mat[5] = self.KnotsControls[numKnots + i * 9 + 5] * self.ControlScaleOffsets[5] + self.ControlScaleOffsets[9 + 5]
            mat[6] = self.KnotsControls[numKnots + i * 9 + 6] * self.ControlScaleOffsets[6] + self.ControlScaleOffsets[9 + 6]
            mat[7] = self.KnotsControls[numKnots + i * 9 + 7] * self.ControlScaleOffsets[7] + self.ControlScaleOffsets[9 + 7]
            mat[8] = self.KnotsControls[numKnots + i * 9 + 8] * self.ControlScaleOffsets[8] + self.ControlScaleOffsets[9 + 8]
            matrix.append(mat)

        return matrix, self.Knots()

    def GetQuterions(self):
        numKnots = self.NumKnots()
        quats = []
        for i in range(numKnots):
            quat = [None]*4
            quat[0] = self.KnotsControls[numKnots + i * 4 + 0] * self.ControlScaleOffsets[0] + self.ControlScaleOffsets[4 + 0]
            quat[1] = self.KnotsControls[numKnots + i * 4 + 1] * self.ControlScaleOffsets[1] + self.ControlScaleOffsets[4 + 1]
            quat[2] = self.KnotsControls[numKnots + i * 4 + 2] * self.ControlScaleOffsets[2] + self.ControlScaleOffsets[4 + 2]
            quat[3] = self.KnotsControls[numKnots + i * 4 + 3] * self.ControlScaleOffsets[3] + self.ControlScaleOffsets[4 + 3]
            quats.append(quat)

        return quats, self.Knots()
        
        


class dak8uc8u: # type 7

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScaleOffsetCount = 0
         self.ControlScaleOffsets = []
         self.KnotsControls = []

    def Components(self):
        return len(self.ControlScaleOffsets)//2

    def NumKnots(self):
        return len(self.KnotsControls)//(self.Components() + 1)

    def Knots(self):
        scale = self.ConvertOneOverKnotScaleTrunc()
        numKnots = self.NumKnots()
        knots = []
        for i in range(numKnots): 
            knots.append(self.KnotsControls[i]/scale)
        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetMartix(self):
        numKnots = self.NumKnots()
        matrix = []
        for i in range(numKnots):
            mat = [None]*9
            mat[0] = self.KnotsControls[numKnots + i * 9 + 0] * self.ControlScaleOffsets[0] + self.ControlScaleOffsets[9 + 0]
            mat[1] = self.KnotsControls[numKnots + i * 9 + 1] * self.ControlScaleOffsets[1] + self.ControlScaleOffsets[9 + 1]
            mat[2] = self.KnotsControls[numKnots + i * 9 + 2] * self.ControlScaleOffsets[2] + self.ControlScaleOffsets[9 + 2]
            mat[3] = self.KnotsControls[numKnots + i * 9 + 3] * self.ControlScaleOffsets[3] + self.ControlScaleOffsets[9 + 3]
            mat[4] = self.KnotsControls[numKnots + i * 9 + 4] * self.ControlScaleOffsets[4] + self.ControlScaleOffsets[9 + 4]
            mat[5] = self.KnotsControls[numKnots + i * 9 + 5] * self.ControlScaleOffsets[5] + self.ControlScaleOffsets[9 + 5]
            mat[6] = self.KnotsControls[numKnots + i * 9 + 6] * self.ControlScaleOffsets[6] + self.ControlScaleOffsets[9 + 6]
            mat[7] = self.KnotsControls[numKnots + i * 9 + 7] * self.ControlScaleOffsets[7] + self.ControlScaleOffsets[9 + 7]
            mat[8] = self.KnotsControls[numKnots + i * 9 + 8] * self.ControlScaleOffsets[8] + self.ControlScaleOffsets[9 + 8]
            matrix.append(mat)

        return matrix, self.Knots()

    def GetQuterions(self):
        numKnots = NumKnots()
        quats = []
        for i in range(numKnots):
            quat = [None]*4
            quat[0] = self.KnotsControls[numKnots + i * 4 + 0] * self.ControlScaleOffsets[0] + self.ControlScaleOffsets[4 + 0]
            quat[1] = self.KnotsControls[numKnots + i * 4 + 1] * self.ControlScaleOffsets[1] + self.ControlScaleOffsets[4 + 1]
            quat[2] = self.KnotsControls[numKnots + i * 4 + 2] * self.ControlScaleOffsets[2] + self.ControlScaleOffsets[4 + 2]
            quat[3] = self.KnotsControls[numKnots + i * 4 + 3] * self.ControlScaleOffsets[3] + self.ControlScaleOffsets[4 + 3]
            quats.append(quat)

        return quats, self.Knots()



class d4nk16uc15u: #type 8

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.ScaleOffsetTableEntries = 0
         self.OneOverKnotScale = 0
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//4

    def Knots(self):
        knots = []
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/self.OneOverKnotScale)   
        return knots


    def CreateQuat(self,a,b,c,scales,offsets):

        swizzle1 = ((b & 0x8000) >> 14) | (c >> 15)
        swizzle2 = (swizzle1 + 1) & 3
        swizzle3 = (swizzle2 + 1) & 3
        swizzle4 = (swizzle3 + 1) & 3

        dataA = (a & 0x7fff) * scales[swizzle2] + offsets[swizzle2]
        dataB = (b & 0x7fff) * scales[swizzle3] + offsets[swizzle3]
        dataC = (c & 0x7fff) * scales[swizzle4] + offsets[swizzle4]

        dataD = math.sqrt((1 - (dataA * dataA + dataB * dataB + dataC * dataC)))
    
        if (a & 0x8000) != 0:
            dataD = -dataD

        quat = [None]*4       
        quat[swizzle2] = dataA
        quat[swizzle3] = dataB
        quat[swizzle4] = dataC
        quat[swizzle1] = dataD

        return quat


    def GetQuterions(self):

        ScaleTable = [
                        1.4142135, 0.70710677, 0.35355338, 0.35355338,
                        0.35355338, 0.17677669, 0.17677669, 0.17677669,
                        -1.4142135, -0.70710677, -0.35355338, -0.35355338,
                        -0.35355338, -0.17677669, -0.17677669, -0.17677669]


        OffsetTable = [
                        -0.70710677, -0.35355338, -0.53033006, -0.17677669,
                        0.17677669, -0.17677669, -0.088388346, 0.0,
                        0.70710677, 0.35355338, 0.53033006, 0.17677669,
                        -0.17677669, 0.17677669, 0.088388346, -0.0]

        knots = self.Knots()

        #now we create quats
        scaleTable = [None]*4
        offsetTable = [None]*4
        selector = self.ScaleOffsetTableEntries

        scaleTable[0] = ScaleTable[(selector >> 0) & 0x0F] * 0.000030518509 
        scaleTable[1] = ScaleTable[(selector >> 4) & 0x0F] * 0.000030518509 
        scaleTable[2] = ScaleTable[(selector >> 8) & 0x0F] * 0.000030518509 
        scaleTable[3] = ScaleTable[(selector >> 12) & 0x0F] * 0.000030518509 

        offsetTable[0] =  OffsetTable[(selector >> 0) & 0x0F]
        offsetTable[1] =  OffsetTable[(selector >> 4) & 0x0F]
        offsetTable[2] =  OffsetTable[(selector >> 8) & 0x0F]
        offsetTable[3] =  OffsetTable[(selector >> 12) & 0x0F]

        numKnots = self.NumKnots()
        quaterions = []
        for i in range(numKnots):          
            quat = self.CreateQuat(self.KnotsControls[numKnots + i * 3 + 0],self.KnotsControls[numKnots + i * 3 + 1],self.KnotsControls[numKnots + i * 3 + 2],scaleTable,offsetTable)
            quaterions.append(quat) #x,y,z,w

        return quaterions,knots 


class d4nk8uc7u: #type 9


    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.ScaleOffsetTableEntries = 0
         self.OneOverKnotScale = 0
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//4

    def Knots(self):
        knots = []
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/self.OneOverKnotScale)

        return knots


    def CreateQuat(self,a,b,c,scales,offsets):

        swizzle1 = ((b & 0x80) >> 6) | ((c & 0x80) >> 7) 
        swizzle2 = (swizzle1 + 1) & 3
        swizzle3 = (swizzle2 + 1) & 3
        swizzle4 = (swizzle3 + 1) & 3

        dataA = (a & 0x7f) * scales[swizzle2] + offsets[swizzle2] 
        dataB = (b & 0x7f) * scales[swizzle3] + offsets[swizzle3] 
        dataC = (c & 0x7f) * scales[swizzle4] + offsets[swizzle4] 

        dataD = math.sqrt((1 - (dataA * dataA + dataB * dataB + dataC * dataC))) 
    
        if (a & 0x80) != 0:
            dataD = -dataD

        quat = [None]*4
        quat[swizzle2] = dataA
        quat[swizzle3] = dataB
        quat[swizzle4] = dataC
        quat[swizzle1] = dataD

        return quat


    def GetQuterions(self):

        ScaleTable = [
                        1.4142135, 0.70710677, 0.35355338, 0.35355338,
                        0.35355338, 0.17677669, 0.17677669, 0.17677669,
                        -1.4142135, -0.70710677, -0.35355338, -0.35355338,
                        -0.35355338, -0.17677669, -0.17677669, -0.17677669]


        OffsetTable = [
                        -0.70710677, -0.35355338, -0.53033006, -0.17677669,
                        0.17677669, -0.17677669, -0.088388346, 0.0,
                        0.70710677, 0.35355338, 0.53033006, 0.17677669,
                        -0.17677669, 0.17677669, 0.088388346, -0.0]

        knots = self.Knots()

        #now we create quats
        scaleTable = [None]*4
        offsetTable = [None]*4
        selector = self.ScaleOffsetTableEntries

        scaleTable[0] = ScaleTable[(selector >> 0) & 0x0F] * 0.0078740157 
        scaleTable[1] = ScaleTable[(selector >> 4) & 0x0F] * 0.0078740157 
        scaleTable[2] = ScaleTable[(selector >> 8) & 0x0F] * 0.0078740157 
        scaleTable[3] = ScaleTable[(selector >> 12) & 0x0F] * 0.0078740157 

        offsetTable[0] =  OffsetTable[(selector >> 0) & 0x0F] 
        offsetTable[1] =  OffsetTable[(selector >> 4) & 0x0F] 
        offsetTable[2] =  OffsetTable[(selector >> 8) & 0x0F] 
        offsetTable[3] =  OffsetTable[(selector >> 12) & 0x0F] 

        numKnots = self.NumKnots()
        quaterions = []
        for i in range(numKnots):          
            quat = self.CreateQuat(self.KnotsControls[numKnots + i * 3 + 0],self.KnotsControls[numKnots + i * 3 + 1],self.KnotsControls[numKnots + i * 3 + 2],scaleTable,offsetTable)
            quaterions.append(quat) #w,x,y,z

        return quaterions,knots # knots is the time


class d3k16uc16u: # type 10

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScales = []
         self.ControlOffsets = []
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//4
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetTranslation(self):
        numKnots = self.NumKnots()
        vectors = []
        for i in range(numKnots):
             v = [None]*3
             v[0] = self.KnotsControls[numKnots + i * 3 + 0] * self.ControlScales[0] + self.ControlOffsets[0]
             v[1] = self.KnotsControls[numKnots + i * 3 + 1] * self.ControlScales[1] + self.ControlOffsets[1]
             v[2] = self.KnotsControls[numKnots + i * 3 + 2] * self.ControlScales[2] + self.ControlOffsets[2]
             vectors.append(v)
         

        return vectors, self.Knots()


class d3k8uc8u: # type 11

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScales = []
         self.ControlOffsets = []
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//4
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetTranslation(self):
        numKnots = self.NumKnots()
        vectors = []
        for i in range(numKnots):
             v = [None]*3
             v[0] = self.KnotsControls[numKnots + i * 3 + 0] * self.ControlScales[0] + self.ControlOffsets[0]
             v[1] = self.KnotsControls[numKnots + i * 3 + 1] * self.ControlScales[1] + self.ControlOffsets[1]
             v[2] = self.KnotsControls[numKnots + i * 3 + 2] * self.ControlScales[2] + self.ControlOffsets[2]
             vectors.append(v)
        
        return vectors, self.Knots()


class d9i1k16uc16u: # type 12

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScale = []
         self.ControlOffset = []
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//2
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetMartix(self):
        numKnots = self.NumKnots()
        matrix = []
        for i in range(numKnots):
            mat = [None]*9
            mat[0] = self.KnotsControls[numKnots + i] * self.ControlScale + self.ControlOffset
            mat[1] = 0
            mat[2] = 0
            mat[3] = 0
            mat[4] = self.KnotsControls[numKnots + i] * self.ControlScale + self.ControlOffset
            mat[5] = 0
            mat[6] = 0
            mat[7] = 0
            mat[8] = self.KnotsControls[numKnots + i] * self.ControlScale + self.ControlOffset
            matrix.append(mat)

        return matrix, self.Knots()


class d9i3k16uc16u: # type = 13
    
    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScales = []
         self.ControlOffsets = []
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//4
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a


    def GetMartix(self): 
        numKnots = self.NumKnots()
        matrix = []
        for i in range(numKnots):
            mat = [None]*9
            mat[0] = self.KnotsControls[numKnots + i * 3 + 0] * self.ControlScales[0] + self.ControlOffsets[0]
            mat[1] = 0
            mat[2] = 0
            mat[3] = 0
            mat[4] = self.KnotsControls[numKnots + i * 3 + 1] * self.ControlScales[1] + self.ControlOffsets[1]
            mat[5] = 0
            mat[6] = 0
            mat[7] = 0
            mat[8] = self.KnotsControls[numKnots + i * 3 + 2] * self.ControlScales[2] + self.ControlOffsets[2]
            matrix.append(mat)

        return matrix, self.Knots()



class d9i1k8uc8u: # type = 14

    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScale = []
         self.ControlOffset = []
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//2
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetMartix(self): 
        numKnots = self.NumKnots()
        matrix = []
        for i in range(numKnots):
            mat = [None]*9
            mat[0] = self.KnotsControls[numKnots + i] * self.ControlScale + self.ControlOffset
            mat[1] = 0
            mat[2] = 0
            mat[3] = 0
            mat[4] = self.KnotsControls[numKnots + i] * self.ControlScale + self.ControlOffset
            mat[5] = 0
            mat[6] = 0
            mat[7] = 0
            mat[8] = self.KnotsControls[numKnots + i] * self.ControlScale + self.ControlOffset
            matrix.append(mat)

        return matrix, self.Knots()



class d9i3k8uc8u: # type = 15
    
    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScales = []
         self.ControlOffsets = []
         self.KnotsControls = []


    def NumKnots(self):
         return len(self.KnotsControls)//4
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a


    def GetMartix(self):
        numKnots = self.NumKnots()
        matrix = []
        for i in range(numKnots):
            mat = [None]*9
            mat[0] = self.KnotsControls[numKnots + i * 3 + 0] * self.ControlScales[0] + self.ControlOffsets[0]
            mat[1] = 0
            mat[2] = 0
            mat[3] = 0
            mat[4] = self.KnotsControls[numKnots + i * 3 + 1] * self.ControlScales[1] + self.ControlOffsets[1]
            mat[5] = 0
            mat[6] = 0
            mat[7] = 0
            mat[8] = self.KnotsControls[numKnots + i * 3 + 2] * self.ControlScales[2] + self.ControlOffsets[2]
            matrix.append(mat)

        return matrix, self.Knots()



class d3i1k32fc32f: # type = 16
    
    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.Padding = 0
         self.ControlScales = []
         self.ControlOffsets = []
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//2
    
    def Knots(self):
        knots = []
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i])

        return knots

    def GetTranslation(self):
        numKnots = self.NumKnots()
        vectors = []
        for i in range(numKnots):
             v = [None]*3
             v[0] = self.KnotsControls[numKnots + i ] * self.ControlScales[0] + self.ControlOffsets[0]
             v[1] = self.KnotsControls[numKnots + i ] * self.ControlScales[1] + self.ControlOffsets[1]
             v[2] = self.KnotsControls[numKnots + i ] * self.ControlScales[2] + self.ControlOffsets[2]
             vectors.append(v)
        

        return vectors, self.Knots()


class d3i1k16uc16u: # type = 17
    
    def __init__(self):
         self.Format = 0
         self.Degree = 0
         self.OneOverKnotScaleTrunc = 0
         self.ControlScales = []
         self.ControlOffsets = []
         self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//2
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetTranslation(self):
        numKnots = self.NumKnots()
        vectors = []
        for i in range(numKnots):
             v = [None]*3
             v[0] = self.KnotsControls[numKnots + i ] * self.ControlScales[0] + self.ControlOffsets[0]
             v[1] = self.KnotsControls[numKnots + i ] * self.ControlScales[1] + self.ControlOffsets[1]
             v[2] = self.KnotsControls[numKnots + i ] * self.ControlScales[2] + self.ControlOffsets[2]
             vectors.append(v)
       

        return vectors, self.Knots()



class d3i1k8uc8u: #type = 18

    def __init__(self):
        self.Format = 0
        self.Degree = 0
        self.OneOverKnotScaleTrunc = 0
        self.ControlScales = []
        self.ControlOffsets = []
        self.KnotsControls = []

    def NumKnots(self):
         return len(self.KnotsControls)//2
    
    def Knots(self):
        knots = []
        scale = self.ConvertOneOverKnotScaleTrunc() 
        for i in range(self.NumKnots()):
            knots.append(self.KnotsControls[i]/scale)

        return knots

    def ConvertOneOverKnotScaleTrunc(self):
        a = self.OneOverKnotScaleTrunc << 16
        a = a.to_bytes(4,byteorder='little')
        a = struct.unpack("<f",a)[0]
        return a

    def GetTranslation(self):
        numKnots = self.NumKnots()
        vector = []
        for i in range(numKnots):
             v = [None]*3
             v[0] = self.KnotsControls[numKnots + i ] * self.ControlScales[0] + self.ControlOffsets[0]
             v[1] = self.KnotsControls[numKnots + i ] * self.ControlScales[1] + self.ControlOffsets[1]
             v[2] = self.KnotsControls[numKnots + i ] * self.ControlScales[2] + self.ControlOffsets[2]
             vector.append(v)

        return vector, self.Knots()



#general animation class
class Animations:

    def __init__(self):
        self.Duration = -1
        self.Name = ''
        self.Oversampling = -1
        self.TimeStep = -1
        self.Tracks = []



#used to upgarde old curve to new curves
class old_curev:
    def __init__(self):
        self.Name = ''
        self.PositionCurve = self.CurveData()
        self.OrientationCurve = self.CurveData()
        self.ScaleShearCurve = self.CurveData()

    class CurveData:
        def __init__(self):
            self.CurveData = []



#each track is an animation of a different model
class Transform_Tracks:
    def __init__(self):
        self.Name = ''
        self.PositionCurve = self.Curve()
        self.OrientationCurve = self.Curve()
        self.ScaleShearCurve = self.Curve()

    class Curve:
        def __init__(self): 
            self.Format = -1
            self.Degree = -1
            self.Knots = []
            self.Controls = [] 


class Tracks:

    def __init__(self): 
        self.InitialPlacement = []
        self.Name = []
        self.TransformTracks = [] 



class KeyFrame:
      def __init__(self):
          #should have 1 Translation, 1 rotation and 1 scale/shear per bone
          self.Name = ''
          self.time = 0.0
          self.Translation = -1
          self.Rotation = -1
          self.ScaleShaer = -1
          self.Matrix = -1

      def __lt__(self, other):
        return self.time < other


#############################################################################
#Functions
#############################################################################

def CreateStructCurve(Format):
    if Format == 0:
         dummy = dakeyframes32f()
    if Format == 1:
         dummy = dak32fc32f()
    if Format == 2:
         dummy = daidentity()
    if Format == 3:
         dummy = daconstant32f()
    if Format == 4:
         dummy = d3constant32f()
    if Format == 5:
         dummy = d4constant32f()
    if Format == 6:
         dummy = dak16uc16u()
    if Format == 7:
         dummy = dak8uc8u()
    if Format == 8:
         dummy = d4nk16uc15u()
    if Format == 9:
         dummy =  d4nk8uc7u()
    if Format == 10:
         dummy = d3k16uc16u()
    if Format == 11:
         dummy =  d3k8uc8u()
    if Format == 12:
         dummy =  d9i1k16uc16u()
    if Format == 13:
         dummy =  d9i3k16uc16u()
    if Format == 14:
         dummy =  d9i1k8uc8u()
    if Format == 15:
         dummy =  d9i3k8uc8u()
    if Format == 16:
         dummy =  d3i1k32fc32f()
    if Format == 17:
         dummy =  d3i1k16uc16u()
    if Format == 18:
         dummy =  d3i1k8uc8u()
    
    return dummy


def get_CurveData_Format(Type):
    for obj in vars(Type.CurveData):
            if obj[:15] == 'CurveDataHeader':                       
                temp = getattr(Type.CurveData, obj)
                return temp.Degree, temp.Format

            if obj == 'Format':
                return Type.CurveData.Degree, Type.CurveData.Format


def Struct_To_List(Primary,secondery):
    temp  =[]
    if type(Primary) != list:
        if secondery:
            temp.append(getattr(Primary,secondery))
        else:
            temp.append(Primary)
            
    else:
        for p in Primary:
            if secondery:
                temp.append(getattr(p,secondery))
            else:
                temp.append(p)
    return temp



def GetCurveData(Format,Curve,input):

    #dakeyframes32f
    if Format == 0:
         Curve.Dimension = input.Dimension
         Curve.Controls = Struct_To_List(input.Controls,'Real32')

    #need to revisit - dak32fc32f
    if Format == 1:
        if input.Controls and hasattr(input.Controls[0], 'Real32'):         
             Curve.Padding = input.Padding
             Curve.Knots = Struct_To_List(input.Knots,'Real32')             
             Curve.Controls = Struct_To_List(input.Controls,'Real32')
        else:
             Curve.Padding = input.Padding
             Curve.Knots = input.Knots
             Curve.Controls = input.Controls
    #daidentity
    if Format == 2:
         Curve.Dimension = input.Dimension
    
    #daconstant32f
    if Format == 3:        
         Curve.Controls = Struct_To_List(input.Controls,'Real32')
         Curve.Padding = input.Padding 

    #d3constant32f
    if Format == 4:
        Curve.Controls = Struct_To_List(input.Controls, None)
        Curve.Padding = input.Padding

    #d4constant32f
    if Format == 5:
        Curve.Controls = Struct_To_List(input.Controls, None)
        Curve.Padding = input.Padding
        
    #dak16uc16u
    if Format == 6: 
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScaleOffsets =  Struct_To_List(input.ControlScaleOffsets, 'Real32')
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt16')

    #dak8uc8u
    if Format == 7: 
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScaleOffsets = Struct_To_List(input.ControlScaleOffsets, 'Real32')
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt8')

    #d4nk16uc15u
    if Format == 8:
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt16')
        Curve.OneOverKnotScale = input.OneOverKnotScale
        Curve.ScaleOffsetTableEntries = input.ScaleOffsetTableEntries

    #d4nk8uc7u
    if Format == 9:
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt8')
        Curve.OneOverKnotScale = input.OneOverKnotScale 
        Curve.ScaleOffsetTableEntries = input.ScaleOffsetTableEntries

    #d3k16uc16u
    if Format == 10:
        Curve.ControlOffsets = input.ControlOffsets
        Curve.ControlScales = input.ControlScales
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt16')        
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc

    #d3k8uc8u
    if Format == 11:
        Curve.ControlOffsets = input.ControlOffsets
        Curve.ControlScales = input.ControlScales
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt8')
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        
    #d9i1k16uc16u
    if Format == 12: 
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScale = input.ControlScale
        Curve.ControlOffset = input.ControlOffset
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt16')
        
    #d9i3k16uc16u
    if Format == 13: 
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScales = input.ControlScales
        Curve.ControlOffsets = input.ControlOffsets
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt16')
        
    #d9i1k8uc8u
    if Format == 14: 
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScale = input.ControlScale
        Curve.ControlOffset = input.ControlOffset
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt8')
        
    #d9i3k8uc8u
    if Format == 15: 
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScales = input.ControlScales
        Curve.ControlOffsets = input.ControlOffsets
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt8')
        
    #d3i1k32fc32f
    if Format == 16: 
        Curve.Padding = input.Padding
        Curve.ControlScales = input.ControlScales
        Curve.ControlOffsets = input.ControlOffsets
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'Real32')

    #d3i1k16uc16u
    if Format == 17: 
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScales = input.ControlScales
        Curve.ControlOffsets = input.ControlOffsets
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt16')

    #d3i1k8uc8u
    if Format == 18:
        Curve.OneOverKnotScaleTrunc = input.OneOverKnotScaleTrunc
        Curve.ControlScales = input.ControlScales
        Curve.ControlOffsets = input.ControlOffsets
        Curve.KnotsControls = Struct_To_List(input.KnotsControls, 'UInt8')

    return Curve


def Convert(Degree,input):
    
    #Degree 0 - means there is no interpolation , so we would have only "static" animation
    if Degree == 0:
        dummy = daidentity()
        dummy.Degree = 0
        dummy.Format = 2
    #degree = 1 is linear interpolation , degree = 2 is quadratic interpolation, degree = 3 is cubic interpolation
    if Degree == 1 or Degree == 2 or Degree == 3:
        dummy = dak32fc32f()
        dummy.Degree = Degree
        dummy.Format = 1
        dummy.Controls = input.Controls
        dummy.Knots = input.Knots

    return dummy


def UpgradeAnimation(TransformTrack):
        Dummy = old_curev()                         
        Dummy.OrientationCurve.CurveData = Convert(TransformTrack.OrientationCurve.Degree,TransformTrack.OrientationCurve)
        Dummy.PositionCurve.CurveData = Convert(TransformTrack.PositionCurve.Degree,TransformTrack.PositionCurve)        
        Dummy.ScaleShearCurve.CurveData = Convert(TransformTrack.ScaleShearCurve.Degree,TransformTrack.ScaleShearCurve)

        return Dummy


def GetRotation(OrientationCurve):
    Format = OrientationCurve.Format

    if Format == 0:
        if OrientationCurve.Dimension == 4:
            return OrientationCurve.GetQuterions() 
        if OrientationCurve.Dimension == 9:
            return OrientationCurve.GetMartix()

    if Format == 1:
         return OrientationCurve.GetQuterions() 


    if Format == 2:
         return OrientationCurve.GetQuterions()

    if Format == 3:
         length = len(OrientationCurve.Controls)
         if length == 4:
              return OrientationCurve.GetQuterions()
         if length == 9:
              return OrientationCurve.GetMartix()

    if Format == 4:
        print("bad rotation")
        # can only be vecor

    if Format == 5:
         return OrientationCurve.GetQuterions()

    if Format == 6:
        Dimension = len(OrientationCurve.ControlScaleOffsets)
        if Dimension == 9:
            return OrientationCurve.GetMartix()
        if Dimension == 4:
            return OrientationCurve.GetQuterions()

    if Format == 7:
         Dimension = len(OrientationCurve.ControlScaleOffsets)
         if Dimension == 9:
              return OrientationCurve.GetMartix()
         if Dimension == 4:
             return OrientationCurve.GetQuterions()

    if Format == 8:
         return OrientationCurve.GetQuterions()

    if Format == 9:
         return OrientationCurve.GetQuterions()

    if Format == 10:
        print("bad rotation")
        # can only be vecor

    if Format == 11:
        print("bad rotation")
        # can only be vecor

    if Format == 12:
        return OrientationCurve.GetMartix()

    if Format == 13:
        return OrientationCurve.GetMartix()

    if Format == 14:
        return OrientationCurve.GetMartix()

    if Format == 15:
         return OrientationCurve.GetMartix()

    if Format == 16:
        print("bad rotation")
        # can only be vecor

    if Format == 17:
        print("bad rotation")
        # can only be vecor

    if Format == 18:
        print("bad rotation")
        # can only be vecor


def GetTranslation(PositionCurve):
    Format = PositionCurve.Format

    if Format == 0:
        #Dimension should be 3
        return PositionCurve.GetTranslation()

    if Format == 1:
        #Dimension should be 3
        return PositionCurve.GetTranslation()

    if Format == 2:
        return PositionCurve.GetTranslation()

    if Format == 3:
        length = len(PositionCurve.Controls)
        if length == 3:
            return PositionCurve.GetTranslation()
        else:
            print("bad translation")

    if Format == 4:
        return PositionCurve.GetTranslation()

    if Format == 5:
        print("bad translation")
        # can only be quaterion

    if Format == 6:
        print("bad translation")
        # can only be quaterion or matrix

    if Format == 7:
        print("bad translation")
        # can only be quaterion or matrix

    if Format == 8:
        print("bad translation")
        # can only be quaterion

    if Format == 9:
        print("bad translation")
        # can only be quaterion

    if Format == 10:
        return PositionCurve.GetTranslation()

    if Format == 11:
        return PositionCurve.GetTranslation()

    if Format == 12:
        print("bad translation")
        # can only be matrix

    if Format == 13:
        print("bad translation")
        # can only be matrix

    if Format == 14:
        print("bad translation")
        # can only be matrix

    if Format == 15:
        print("bad translation")
        # can only be matrix

    if Format == 16:
        return PositionCurve.GetTranslation()

    if Format == 17:
        return PositionCurve.GetTranslation()

    if Format == 18:
        return PositionCurve.GetTranslation()


#get a given frame from data and fill in all the blanks using interpolation
def FrameInterpolate(Data):
    next = -1
    for i in range(len(Data) - 1):
        previous = Data[i]
        current = Data[i+1]
        
        if previous.Translation != -1 and current.Translation == -1:
            #now we find the next element that has a translation
            for j in range(i+1,len(Data)):
                if Data[j].Translation != -1:
                    next = Data[j]
                    break
            if next != -1 and next.Translation!= -1:                
                factor = (current.time - previous.time)/(next.time - previous.time)
                a = NoeVec3([previous.Translation[0], previous.Translation[1], previous.Translation[2]])
                b = NoeVec3([next.Translation[0], next.Translation[1], next.Translation[2]])
                c =  a.lerp(b,factor) 
                current.Translation = [c[0],c[1],c[2]]
            else:
                current.Translation = previous.Translation
       
        next = -1
        if previous.Rotation != -1 and current.Rotation == -1:
            #now we find the next element that has a Rotation
            for j in range(i+1,len(Data)):
                if Data[j].Rotation != -1:
                    next = Data[j]
                    break
            if next != -1 and next.Rotation!= -1:
                factor = (current.time - previous.time)/(next.time - previous.time)
                a = NoeQuat([previous.Rotation[0], previous.Rotation[1], previous.Rotation[2],previous.Rotation[3]])
                b = NoeQuat([next.Rotation[0], next.Rotation[1], next.Rotation[2],next.Rotation[3]]) 
                c = a.slerp(b,factor)
                current.Rotation = [c[0],c[1],c[2],c[3]]
            else:
                current.Rotation = previous.Rotation

        next = -1
        if previous.ScaleShaer != -1 and current.ScaleShaer == -1:
            for j in range(i+1,len(Data)):
                if Data[j].ScaleShaer != -1:
                    next = Data[j]
                    break
            if next!= -1:
               current.ScaleShaer = [None] * 9
               factor = (current.time - previous.time)/(next.time - previous.time)
               current.ScaleShaer[0] = previous.ScaleShaer[0] * (1 - factor) + next.ScaleShaer[0] * factor
               current.ScaleShaer[1] = previous.ScaleShaer[1] * (1 - factor) + next.ScaleShaer[1] * factor
               current.ScaleShaer[2] = previous.ScaleShaer[2] * (1 - factor) + next.ScaleShaer[2] * factor
               current.ScaleShaer[3] = previous.ScaleShaer[3] * (1 - factor) + next.ScaleShaer[3] * factor
               current.ScaleShaer[4] = previous.ScaleShaer[4] * (1 - factor) + next.ScaleShaer[4] * factor
               current.ScaleShaer[5] = previous.ScaleShaer[5] * (1 - factor) + next.ScaleShaer[5] * factor
               current.ScaleShaer[6] = previous.ScaleShaer[6] * (1 - factor) + next.ScaleShaer[6] * factor
               current.ScaleShaer[7] = previous.ScaleShaer[7] * (1 - factor) + next.ScaleShaer[7] * factor
               current.ScaleShaer[8] = previous.ScaleShaer[8] * (1 - factor) + next.ScaleShaer[8] * factor
            else:
                current.ScaleShaer = previous.ScaleShaer
                
    return Data


def CreateKeyFrame(Data):

    FrameList = []

    for i,time in enumerate(Data.OrientationCurve.Knots):
        Dummy = KeyFrame()
        Dummy.time = time
        Dummy.Name = Data.Name
        Dummy.Rotation = Data.OrientationCurve.Controls[i]       
        FrameList.append(Dummy)

    for i,time in enumerate(Data.PositionCurve.Knots):

        index = bisect.bisect_left(FrameList, time)
        #if it alraedt exits
        if index < len(FrameList) and FrameList[index].time == time:
            FrameList[index].Translation = Data.PositionCurve.Controls[i]
        #if it dosent exist create new frame
        else:
            Dummy = KeyFrame()        
            Dummy.time = time
            Dummy.Name = Data.Name
            Dummy.Translation = Data.PositionCurve.Controls[i]
            FrameList.insert(index,Dummy)

    for i,time in enumerate(Data.ScaleShearCurve.Knots):

        index = bisect.bisect_left(FrameList, time)
        #if it alraedy exits
        if index < len(FrameList) and FrameList[index].time == time:
            FrameList[index].ScaleShaer = Data.ScaleShearCurve.Controls[i]
        #if it dosent exist create new frame
        else:
            Dummy = KeyFrame()        
            Dummy.time = time
            Dummy.Name = Data.Name
            Dummy.ScaleShaer = Data.ScaleShearCurve.Controls[i]
            FrameList.insert(index,Dummy)
            
    
    # sometimes 2 different frames are at time 0, so i delete the first and leave the second
    if len(FrameList) > 1 and FrameList[0].time == 0 and FrameList[1].time == 0:

        if FrameList[1].Translation == -1 and FrameList[0].Translation != -1:
            FrameList[1].Translation = FrameList[0].Translation
        if FrameList[1].Rotation == -1 and FrameList[0].Rotation != -1:
            FrameList[1].Rotation = FrameList[0].Rotation
        if FrameList[1].ScaleShaer == -1 and FrameList[0].ScaleShaer != -1:
            FrameList[1].ScaleShaer = FrameList[0].ScaleShaer

        del(FrameList[0])

    return FrameList


#function to equlize number of frames for all bones in order to allow flat list of bone_transform * frame
def EqualizeFrames(BoneFramelist,Duration,TimeStep):

    Max = -1
    
    for a in BoneFramelist:
          for b in a:
              if b.time > Max:
                  Max = b.time
    print("Duration", Duration)        
    print("TimeStep", TimeStep)     
    print("Max", Max)
    TimeList = []
    time = 0.0
    
    # all time steps are estimest need to add a calcualtion based on time step and duration - need more work here!!!
    if Max <= Duration + 0.5:
        while time < Max:
            TimeList.append(time)
            time += 1/30
    else:
        while time < Max:
            TimeList.append(time)
            time += 0.96
            
    if Max == 0:
        TimeList.append(time)
        
    BoneFrames = []
    frames = []
       
    # a represents all the frames of a specific bone
    Dummy = TimeList[:]
    for a in BoneFramelist:       
        Newlist = []
        for i,time in enumerate(Dummy):
            Index = bisect.bisect_left(a, time)
            #i would put it before index or insert in index
            if len(a) == 1:
                Newlist.append(a[0])
                continue
            if Index == 0 and time == 0.0:
                Newlist.append(a[Index])
            else:
                if Index <= len(a)-1:
                    factor = (time - a[Index-1].time)/(a[Index].time - a[Index-1].time)
                    Temp = FrameInterpolateSingle( a[Index-1],  a[Index], factor)
                    Temp.time = time
                    Newlist.append(Temp)
                else:
                    Temp = KeyFrame()
                    Temp.Name = Newlist[len(Newlist)-1].Name
                    Temp.Rotation = Newlist[len(Newlist)-1].Rotation                    
                    Temp.Translation = Newlist[len(Newlist)-1].Translation
                    Temp.ScaleShaer = Newlist[len(Newlist)-1].ScaleShaer
                    Temp.time = time
                    Newlist.append(Temp)                    
        
        ApplyShear(Newlist)
        frames.append(Newlist)

    
    return frames


def FrameInterpolateSingle(start, end, factor):
        new = KeyFrame()
        a = NoeQuat([start.Rotation[0], start.Rotation[1], start.Rotation[2],start.Rotation[3]])
        b = NoeQuat([end.Rotation[0], end.Rotation[1], end.Rotation[2],end.Rotation[3]]) 
        c = a.slerp(b,factor)
        new.Rotation = [c[0],c[1],c[2],c[3]]
        
        a = NoeVec3([start.Translation[0], start.Translation[1], start.Translation[2]])
        b = NoeVec3([end.Translation[0], end.Translation[1], end.Translation[2]])
        c =  a.lerp(b,factor) 
        new.Translation = [c[0],c[1],c[2]]
        
        new.ScaleShaer = [0.0] * 9
        new.ScaleShaer[0] = start.ScaleShaer[0] * (1 - factor) + end.ScaleShaer[0] * factor
        new.ScaleShaer[1] = start.ScaleShaer[1] * (1 - factor) + end.ScaleShaer[1] * factor
        new.ScaleShaer[2] = start.ScaleShaer[2] * (1 - factor) + end.ScaleShaer[2] * factor
        new.ScaleShaer[3] = start.ScaleShaer[3] * (1 - factor) + end.ScaleShaer[3] * factor
        new.ScaleShaer[4] = start.ScaleShaer[4] * (1 - factor) + end.ScaleShaer[4] * factor
        new.ScaleShaer[5] = start.ScaleShaer[5] * (1 - factor) + end.ScaleShaer[5] * factor
        new.ScaleShaer[6] = start.ScaleShaer[6] * (1 - factor) + end.ScaleShaer[6] * factor
        new.ScaleShaer[7] = start.ScaleShaer[7] * (1 - factor) + end.ScaleShaer[7] * factor
        new.ScaleShaer[8] = start.ScaleShaer[8] * (1 - factor) + end.ScaleShaer[8] * factor

        new.Name = start.Name

        return new


         
# apply scale/ shear matrix - to transform 
def ApplyShear(Frame):
    
    for i,m in enumerate(Frame):
        temp = Transform()
        temp.Quaterion = m.Rotation
        temp.Translation = m.Translation 
        temp.ScaleShear = m.ScaleShaer
        
        if temp.ScaleShear == -1:
            temp.ScaleShear = [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]
        m.Matrix = ComposeLocalMatrix(temp)

    return Frame     

#still not working at intended
def fixOrinationInfo(Main_Model,model):
    Zearo = NoeVec3((0.0,0.0,0.0))   
    Wanted_Orination = NoeMat43([NoeVec3(Main_Model.OrinationInfo[0]),NoeVec3(Main_Model.OrinationInfo[1]),NoeVec3(Main_Model.OrinationInfo[2]),Zearo])
    Current_Orination = NoeMat43([NoeVec3(model.OrinationInfo[0]),NoeVec3(model.OrinationInfo[1]),NoeVec3(model.OrinationInfo[2]),Zearo])
    CorrectionMatrix = Wanted_Orination * Current_Orination.inverse()

    return CorrectionMatrix
    

class Transform:
    
    def __init__(self):
        self.flag = -1
        self.Translation = []
        self.Quaterion =  []
        self.ScaleShear = []

        
class Model:
    def __init__(self):
        self.Name = ''
        self.Bones = []
        self.Meshes = []
        self.AnimationInfo = []
        self.Trackgroups = []
        self.InitialPlacement = []
        self.OrinationInfo = []

class Mesh:
    def __init__(self):        
        self.info = self.Info()
        self.mesh = self.Data()

    class Info:
        def __init__(self): 
            self.Mesh_Name = []
            self.Vertex_Count = []
            self.Face_Count = [] 
            self.Polygroups = []                

    class Data:
        def __init__(self):
            self.Positions = []
            self.Normals = []
            self.TextureCoordinates = []
            self.TextureCoordinates2 = []
            self.Binormal = []
            self.Tangents = []
            self.Indices = []
            self.BoneWeights = []
            self.BoneIndices = []
            self.BoneBindings = []


class Skeleton:
    def __init__(self): 
        self.Name = ''
        self.BoneNames = []
        self.ParentIndex = []
        self.Transform = []
        self.InverseWorldTransform = []
        self.Bone_Count = 0 
 
#Main GR2 Reader Function        
def GR2Reader(data): 

    #=====================================================================
    #supporting Classes
    #=====================================================================
           
            
    class dummy_member:

        def __init__(self):
            self.randome = []


    class MemberDefinition:
        
        def __init__(self):
            self.name = ""
            self.Type = 0
            self.definitionOffset = 0
            self.StringOffset = 0
            self.arraySize = 0
            self. extra = []
            self.unk = 0
            self.Data = []


    class StructDefinition:
        def __init__(self):
            self.Members = []
            self.type = None


    class Marshalling:
        def __init__(self):
            self.count = 0
            self.offset = 0
            self.target_section = 0
            self.target_offset = 0


    class Relocation:
        def __init__(self):
            self.offset = 0
            self.target_section = 0
            self.target_offset = 0


    class Section_Header:
        # always 44 bytes
         def __init__(self):
            self.compression = 0 # 0: no compression, 1: Oodle0, 2: Oodle1
            self.data_offset = 0 # From the start of the file
            self.data_size = 0  # In bytes
            self.decompressed_size = 0 # In bytes
            self.alignment = 0     # Seems always 4
            self.first16bit  = 0    # Stop0 for Oodle1
            self.first8bit    = 0    # Stop1 for Oodle1
            self.relocations_offset = 0
            self.relocations_count = 0
            self.marshallings_offset = 0
            self.marshallings_count = 0


    class Header:
        # always 32 bytes
         def __init__(self):
            self.magic = [] #16 bytes
            self.size = 0 # Size of the header
            self.format = 0  # Seems always 0
            self.reserved =[] #Seems always 0, 8 bytes



    class HeaderInfo:
        def __init__(self):
            # from here can be considered info part
            self.version = 0 # Always seems 6 or 7 depending on game
            self.file_size = 0
            self.crc32 = 0
            self.sections_offset = 0 #From 'version'
            self.sections_count = 0
            self.type_section = 0 #rootType
            self.type_offset = 0 #rootType
            self.root_section = 0 #rootNode
            self.root_offset = 0 #rootNode
            self.tag = 0
            self.extra = [] # 16 bytes, Always seems 0
            self.stringTableCrc = 0
            self.reserved1 = 0
            self.reserved2 = 0
            self.reserved3 = 0      


    class Refrence:
        def __init__(self):
            self.section = 0
            self.offset = 0
            self.type = None

    class root:
        def __init__(self):
            self.offset = 0
            self.type = None


    #===========================================================
    #Supporting functions
    #===========================================================
                     
    def extractData(StructHeaders):
        All_Models = []
        
        #create this here incase file dosent have model data
        Models = Model()
        
        if StructHeaders.ArtToolInfo:
            #right, up, back, origin
            Orination = [[],[],[],[]]
            Orination[0] = StructHeaders.ArtToolInfo.RightVector
            Orination[1] = StructHeaders.ArtToolInfo.UpVector
            Orination[2] = StructHeaders.ArtToolInfo.BackVector
            Orination[3] = StructHeaders.ArtToolInfo.Origin
            Models.OrinationInfo = Orination
            
        for model in StructHeaders.Models:

            Models = Model()
            if StructHeaders.ArtToolInfo:
                Models.OrinationInfo = Orination
            Models.Name = model.Name
            if hasattr( model, "InitialPlacement"):
                Models.InitialPlacement =  model.InitialPlacement                
                
            #if we have mesh Data
            if hasattr(model, "MeshBindings") and model.MeshBindings and model.MeshBindings[0].Mesh.PrimaryVertexData:

                Num_Meshes = len(model.MeshBindings)
                mesh_array = []

                for i in range(Num_Meshes):
                    m = Mesh()           
                    Positions = []
                    Normals = []
                    TextureCoordinates = []
                    TextureCoordinates2 = []
                    BoneIndices = []
                    BoneWeights = []
                    Binormal = []
                    Tangent = []
                    Indices = []
                    BoneBindings = []
                    PolyGroups = []
                    
                    vertcies_Data = model.MeshBindings[i].Mesh.PrimaryVertexData.Vertices
                    tri_Data = model.MeshBindings[i].Mesh.PrimaryTopology
                    Num_Vertices = len(vertcies_Data)
                            
                    if  tri_Data.Indices16:
                        Num_Indices = len(model.MeshBindings[i].Mesh.PrimaryTopology.Indices16)
                    if  tri_Data.Indices:
                        Num_Indices = len(model.MeshBindings[i].Mesh.PrimaryTopology.Indices)                    

                    Bone_binds_data = model.MeshBindings[i].Mesh.BoneBindings
                    for j in range(len(Bone_binds_data)):            
                            BoneBindings.append(Bone_binds_data[j].BoneName)
                            
                    for j in range(Num_Vertices):
                
                        if hasattr(vertcies_Data[j], "Position"):
                            Positions.append(vertcies_Data[j].Position)
                        if hasattr(vertcies_Data[j], "Normal"):
                            Normals.append(vertcies_Data[j].Normal)
                        if hasattr(vertcies_Data[j], "TextureCoordinates0"):
                            TextureCoordinates.append(vertcies_Data[j].TextureCoordinates0)
                        if hasattr(vertcies_Data[j], "TextureCoordinates1"):
                            TextureCoordinates2.append(vertcies_Data[j].TextureCoordinates1)
                        if hasattr(vertcies_Data[j], "BoneIndices"):
                            BoneIndices.append(vertcies_Data[j].BoneIndices)
                        if hasattr(vertcies_Data[j], "BoneWeights"):
                            BoneWeights.append(vertcies_Data[j].BoneWeights)
                        if hasattr(vertcies_Data[j], "Binormal"):
                            Binormal.append(vertcies_Data[j].Binormal)
                        if hasattr(vertcies_Data[j], "Tangent"):
                            Tangent.append(vertcies_Data[j].Tangent)

                    for idx in range(Num_Indices):
                        if  tri_Data.Indices16:
                            Indices.append(tri_Data.Indices16[idx].Int16)
                        if  tri_Data.Indices:
                            Indices.append(tri_Data.Indices[idx].Int32)

                    for Polygroup in tri_Data.Groups:
                        PolyGroups.append(Polygroup.TriCount)
                
                    m.mesh.Positions = Positions
                    m.mesh.Normals = Normals
                    m.mesh.TextureCoordinates = TextureCoordinates
                    m.mesh.TextureCoordinates2 = TextureCoordinates2
                    m.mesh.BoneIndices = BoneIndices
                    m.mesh.BoneWeights = BoneWeights
                    m.mesh.Tangents = Tangent
                    m.mesh.Binormal = Binormal
                    m.mesh.Indices = Indices
                    m.mesh.BoneBindings = BoneBindings
                    m.info.Polygroups = PolyGroups
                    m.info.Mesh_Name = model.MeshBindings[i].Mesh.Name
                    mesh_array.append(m)

                Models.Meshes = mesh_array
                
            #if we have skeleton data
            if hasattr(model, "Skeleton") and model.Skeleton:

                for skel in model.Skeleton:
                    s = Skeleton()
                    Bone_names = []
                    InverseWorldTransform = []
                    LODError = []
                    ParentIndex = []
                    Loacl_Transform = []
                   
                    for Bone in skel.Bones:
                        if hasattr(Bone, "Name"):
                            Bone_names.append(Bone.Name)
                        if hasattr(Bone, "InverseWorldTransform"):
                            InverseWorldTransform.append( Bone.InverseWorldTransform)
                        if hasattr(Bone, "LODError"):
                            LODError.append(Bone.LODError)
                        if hasattr(Bone, "ParentIndex"):
                            ParentIndex.append(Bone.ParentIndex)
                        if hasattr(Bone, "Transform"):
                            Loacl_Transform.append(Bone.Transform)

                    s.InverseWorldTransform = InverseWorldTransform
                    s.Transform = Loacl_Transform
                    s.ParentIndex = ParentIndex
                    s.BoneNames = Bone_names
                    s.Bone_Count = len(s.ParentIndex)
                    s.Name = skel.Name
                    if len(model.Skeleton) == 1:
                        Models.Bones = s
            
            All_Models.append(Models)
            
            
        if StructHeaders.Animations:
            
            if  ANIMATION_TRACK > 0 and ANIMATION_TRACK <= len(StructHeaders.Animations):
                anim = StructHeaders.Animations[ANIMATION_TRACK - 1]
            else:
                anim = StructHeaders.Animations[0]
            
            a =  Animations()
            a.Duration = anim.Duration
            a.Name = anim.Name
            #old format didnt have oversampeling
            if hasattr(anim, "Oversampling"):
                a.Oversampling = anim.Oversampling
            else:
                a.Oversampling = 0
            a.TimeStep = anim.TimeStep
            a.Tracks = anim.TrackGroups

            TrackGroups = []

            for track in a.Tracks:

                Tr = Tracks()
                Tr.Name = track.Name
                TransformTracks = []
                
                if hasattr(track, "TransformTracks"):
                
                    for Transform_Track in track.TransformTracks:
                        t = Transform_Tracks()
                        t.Name = Transform_Track.Name
                        
                        #check if old curve format - need to upgrade
                        if not hasattr(Transform_Track.OrientationCurve, 'CurveData'):
                                Transform_Track = UpgradeAnimation(Transform_Track)                    
                        
                        DegreeO,FormatO = get_CurveData_Format(Transform_Track.OrientationCurve)
                        t.OrientationCurve = CreateStructCurve(FormatO)
                        t.OrientationCurve = GetCurveData(FormatO,t.OrientationCurve,Transform_Track.OrientationCurve.CurveData)
                        t.OrientationCurve.Degree = DegreeO
                        t.OrientationCurve.Format = FormatO

                        DegreeP,FormatP = get_CurveData_Format(Transform_Track.PositionCurve)
                        t.PositionCurve = CreateStructCurve(FormatP)
                        t.PositionCurve = GetCurveData(FormatP,t.PositionCurve,Transform_Track.PositionCurve.CurveData)
                        t.PositionCurve.Degree = DegreeP
                        t.PositionCurve.Format = FormatP

                        DegreeS,FormatS = get_CurveData_Format(Transform_Track.ScaleShearCurve)
                        t.ScaleShearCurve = CreateStructCurve(FormatS)
                        t.ScaleShearCurve = GetCurveData(FormatS,t.ScaleShearCurve,Transform_Track.ScaleShearCurve.CurveData)
                        t.ScaleShearCurve.Degree = DegreeS
                        t.ScaleShearCurve.Format = FormatS

                        TransformTracks.append(t)
                    
                    Tr.TransformTracks = TransformTracks
                    TrackGroups.append(Tr)

            a.Tracks = TrackGroups
            
            
            #for test only -- put track group inside its model class
            for model in All_Models:
                for track in a.Tracks:
                    if track.Name == model.Name:
                        model.Trackgroups = track
                        model.AnimationInfo = a
                        
                # if no track with coressponding name to model found insert last track to model
                if not model.Trackgroups:
                    model.Trackgroups = track
                    model.AnimationInfo = a
            
            #if we didnt have any model data, use empty struct taht was created and insert all animation data
            if not All_Models:
                Models.AnimationInfo = a
                transformTracks = []
                for j in range(len(TrackGroups)):
                    transformTracks += TrackGroups[j].TransformTracks
                TrackGroups[0].TransformTracks = transformTracks
                Models.Trackgroups = TrackGroups[0]
                All_Models.append(Models)
                        
        if StructHeaders.Models:
        
            if  MERGE_SCENE == 1:
                MergeModels = Model()
                tempMesh = []
                tempBones = []
                tempTracks = []
                
                if StructHeaders.Animations:
                    MergeModels.AnimationInfo = a
                    for track in a.Tracks:
                        tempTracks += track.TransformTracks
                    MergeModels.Trackgroups = Tracks()
                    MergeModels.Trackgroups.TransformTracks = tempTracks
                    
                for model in All_Models:
                    for i in range(len(model.Meshes)):           
                        tempMesh.append(model.Meshes[i])
                    if model.Bones:
                        model.Bones.InitialPlacement = model.InitialPlacement
                        tempBones.append(model.Bones)
                        MergeModels.Bones = tempBones
                        
                MergeModels.Meshes = tempMesh
                
                MergeModels.Name = 'merged_scene'
                models = []
                models.append(MergeModels)
                return models
            
        return All_Models


    def memberSize(type,member):
        if type == 1:
            size = 0
            originalPos = stream.tell()
            Members = readSubStructV2(stream,Format, member.definitionOffset)
            stream.seek(originalPos,0)
            for member in Members:
                size += memberSize(member.Type,member)
            return size

        if type == 11 or type == 12 or type == 13 or type == 14:
            return 1

        if type == 15 or type == 16 or type == 17 or type == 18 or type == 21: # i added type 21
            return 2

        if type == 2 or type == 8 or type == 19 or type == 20 or type == 10:
            return 4

        if type == 3 or type == 4 or type == 5:
            return 8
        
        if type == 7:
            return 12

        if type == 9:
            return 68



    def MarshallingSize(type):
        if type == 1 or type == 2 or type == 5 or type == 22: #inline,refrence,variantRefrence,empty refrence
            return 0

        if type == 11 or type == 12 or type == 13 or type == 14: #Int8,Bin8,Uint8,Norm8
            return 1

        if type == 15 or type == 16 or type == 17 or type == 18 or type == 21: # int16,Bin16,Uint16,Norm16,Real16
            return 2

        if type == 8 or type == 9 or type == 10 or type == 19 or type == 20 or type == 3 or type == 7 or type == 4:# transform,string.real32,Uint32,Int32,Refrencetoarray,arrayofreffrencees,refrence to varient array
            return 4


    def MixedMarshal(stream,count, Defenition_Offset):
        originalPos = stream.tell()
        Members = readSubStructV2(stream,Format, Defenition_Offset)
        stream.seek(originalPos,0)
        for j in range(count):
            for member in Members:
                size = memberSize(member.Type,member)
                marshalSize = MarshallingSize(member.Type)

                if member.Type == 1: 
                    if member.arraySize == 0:
                        count = 1
                    else:
                        count = member.arraySize

                    MixedMarshal(stream,count, member.definitionOffset)

                elif marshalSize > 1:
                    byte_array = bytearray(stream.readBytes(size))
                    #byte_array.reverse() - not good
                    for i in range(size//marshalSize):
                        for off in range(marshalSize//2):
                            temp = byte_array[i * marshalSize + off]
                            byte_array[i * marshalSize + off] = byte_array[i * marshalSize + marshalSize - 1 - off]
                            byte_array[i * marshalSize + marshalSize - 1 - off] = temp
                    stream.seek(-size,1)
                    stream.writeBytes(byte_array)
                    stream.seek(-size,1)

                stream.seek(size,1)


    def readformat(stream, Format):
        if Format == "LittleEndian32" or Format == "BigEndian32":
            Data_offset = stream.readUInt()
        else:
            Data_offset = stream.readUInt64()

        return Data_offset


    def createStruct(Headers):
        m = dummy_member()
        for header in Headers:
            setattr(m, header.name, [])

        return m
    
   
   
    #Sets start location for each memebr
    def seekContoller(Members,MemberClass):
        global  Name_List
        Name_List = ['MeshBindings','Models','Bones','Skeleton', 'Skeletons','TrackGroups','Animations','TransformTracks', 'BoneBindings', 'Groups']
        originalPos = stream.tell()
        for member in Members:
            array = []
            array.append(member)   
            if member.name == 'Models' or member.name == 'Animations' or member.name == 'ArtToolInfo':
                GetMemberData(stream,array,MemberClass)           
            if Format == "LittleEndian32" or Format == "BigEndian32":
                originalPos += 4
            else:
                originalPos += 8
            if member.Type == 3 or member.Type == 4:
                originalPos += 4
            stream.seek(originalPos)

        return MemberClass
    
    
    
    #get data for member
    def GetMemberData(stream,members,ParentMember):
         
        for member in members:            
            
            if member.arraySize > 0:
                temp = []
                for j in range(member.arraySize):
                    if member.Type == 19: 
                        temp.append(stream.readUInt())
                    if member.Type == 10:    
                        temp.append(stream.readFloat())
                    if member.Type == 11 or member.Type == 13: 
                        temp.append(stream.readByte())
                    if member.Type == 12 or member.Type == 14: 
                        temp.append(stream.readUByte())
                    if member.Type == 15 or member.Type == 17: 
                        temp.append(stream.readShort())
                    if member.Type == 16 or member.Type == 18: 
                        temp.append(stream.readUShort())
                    if member.Type == 20: 
                        temp.append(stream.readUInt())
                    if member.Type == 21: 
                        temp.append(stream.readHalfFloat())

                #member.Data.append(temp)
                setattr(ParentMember, member.name, temp)
                continue     

            #None
            if member.Type == 0: 
                member.Data = []
                continue

            # inline
            if member.Type == 1: 
                originalPos = stream.tell()
                AllSubHeaders = readSubStructV2(stream,Format, member.definitionOffset)
                StrucM = createStruct(AllSubHeaders)
                stream.seek(originalPos,0) 
                GetMemberData(stream, AllSubHeaders,StrucM)
                if member.Data != None:              
                    setattr(ParentMember, member.name, StrucM)
                continue          

            # refrence
            if member.Type == 2:
                Data_offset = readformat(stream, Format)
                if Data_offset == 0:
                    continue
                ContinueOffset = stream.tell()
                if member.definitionOffset:
                    AllSubHeaders = readSubStructV2(stream,Format, member.definitionOffset)
                    StrucM = createStruct(AllSubHeaders)
                   
                stream.seek(Data_offset,0)
                GetMemberData(stream, AllSubHeaders,StrucM)

                if member.name in Name_List:
                    array = []
                    array.append(StrucM)
                    setattr(ParentMember, member.name, array)               
                else:         
                    setattr(ParentMember, member.name, StrucM)
                    
                stream.seek(ContinueOffset,0)        
                continue

            #Type == 3 ReferenceToArray
            #Type == 7 ReferenceToVariantArray
            if member.Type == 3 or member.Type == 7:
                if  member.Type == 7:
                    member.definitionOffset = readformat(stream, Format) 
                size = stream.readUInt()
                offset = readformat(stream, Format)                     
                if size == 0 or offset == 0:              
                    continue
                ContinueOffset = stream.tell()           
                if member.definitionOffset:            
                    AllSubHeaders = readSubStructV2(stream,Format,  member.definitionOffset)
                    StrucM = createStruct(AllSubHeaders)

                stream.seek(offset,0)

                if size > 1 or member.name in Name_List:
                    array = []
                    for  tempP in range(size):
                        array.append(StrucM.__class__())
                    for j in range(size):               
                        GetMemberData(stream,AllSubHeaders,array[j])
                else:
                    for j in range(size):               
                        GetMemberData(stream,AllSubHeaders,StrucM)

                if size > 1 or member.name in Name_List:
                    setattr(ParentMember, member.name, array)               
                else:               
                    setattr(ParentMember, member.name, StrucM)
                  
                stream.seek(ContinueOffset,0)     
                continue

            #ArrayOfReferences
            if member.Type == 4:
                RefrenceOffset = []
                size = stream.readUInt()
                Data_offset = readformat(stream, Format)
                if size == 0 or Data_offset == 0:
                    continue
                ContinueOffset = stream.tell()         
                if member.definitionOffset: 
                    AllSubHeaders = readSubStructV2(stream,Format, member.definitionOffset)
                    StrucM = createStruct(AllSubHeaders)

                stream.seek(Data_offset,0)
                for j in range(size):               
                    RefrenceOffset.append(readformat(stream, Format)) 

                if size > 1 or member.name in Name_List:
                    array = []
                    for  tempP in range(size):
                        array.append(StrucM.__class__())
                    for j in range(size):
                        stream.seek(RefrenceOffset[j],0)
                        GetMemberData(stream, AllSubHeaders,array[j])
                else:
                    for j in range(size):
                        stream.seek(RefrenceOffset[j],0)
                        GetMemberData(stream, AllSubHeaders,StrucM)
            
                if size > 1 or member.name in Name_List:
                    setattr(ParentMember, member.name, array)              
                else:
                    setattr(ParentMember, member.name, StrucM)
                    
                stream.seek(ContinueOffset,0)       
                continue

            #extended data - currently i ignore it - "VariantReference"
            if member.Type == 5: 
                defnition_offset = readformat(stream, Format)
                Data_offset = readformat(stream, Format)
                if member.name == 'ExtendedData':
                    member.Data = []
                    continue
                if defnition_offset == 0:
                    continue
                ContinueOffset = stream.tell()          
                AllSubHeaders = readSubStructV2(stream,Format, defnition_offset)
                StrucM = createStruct(AllSubHeaders)
                stream.seek(Data_offset,0)
                GetMemberData(stream, AllSubHeaders,StrucM)
                setattr(ParentMember, member.name, StrucM)
                stream.seek(ContinueOffset,0)          
                continue

            #string
            if member.Type == 8:
                StringOffset = readformat(stream, Format)
                ContinueOffset = stream.tell()
                stream.seek(StringOffset,0)
                if ParentMember:
                    setattr(ParentMember, member.name, readString(stream))
                stream.seek(ContinueOffset,0)             
                continue

            # Transform Data
            if member.Type == 9:
                node = Transform()
                node.flag = stream.readUInt()

                # Translation
                for cord in range(3):
                    node.Translation.append(stream.readFloat())

                #Quaterion x,y,z,w
                for cord in range(4):
                    node.Quaterion.append(stream.readFloat()) 

                for cord in range(9):
                    node.ScaleShear.append(stream.readFloat())
                
                setattr(ParentMember, member.name, node)
                continue

            #float
            if member.Type == 10:    
                setattr(ParentMember, member.name, stream.readFloat())
                continue

            # 1 byte - char
            if member.Type == 11 or member.Type == 13: 
                setattr(ParentMember, member.name, stream.readByte())
                continue

            # 1 byte - unsigned char
            if member.Type == 12 or member.Type == 14: 
                setattr(ParentMember, member.name, stream.readUByte())
                continue

            #short/Int16
            if member.Type == 15 or member.Type == 17: 
                setattr(ParentMember, member.name, stream.readShort())
                continue

            #unsigned short
            if member.Type == 16 or member.Type == 18: 
                setattr(ParentMember, member.name, stream.readUShort())
                continue

            # int
            if member.Type == 19: 
                setattr(ParentMember, member.name, stream.readInt())
                continue

            # unsigned int
            if member.Type == 20: 
                setattr(ParentMember, member.name, stream.readUInt())
                continue

            # half float
            if member.Type == 21: 
                setattr(ParentMember, member.name, stream.readHalfFloat())
                continue

            #type == 22 ==> empty refrence
               

    def readString(stream):
        string = []
        while(1):
            bytes = stream.readBytes(1)
            if bytes == b'\x00':
                break
            string += bytes
        try:
            string = bytearray(string).decode(encoding='UTF-8')
        except:
            string = "Unk"

        return string


    #check format of file 64/32 bit
    def FormatType(String):
    
        #civ6 format - mixed format - 64 bit for header mix marshelling etc.., 32 bit for navigating ArtTool etc..
        LittleEndian32v4 = [0x5B, 0x6C, 0xD6, 0xD2, 0x3C, 0x46, 0x8B, 0xD6, 0x83, 0xC2, 0xAA, 0x99, 0x3F, 0xE1, 0x76, 0x52]
    
        #Magic value used for version 6 little-endian 32-bit Granny files
        LittleEndian32v3 = [0xB8, 0x67, 0xB0, 0xCA, 0xF8, 0x6D, 0xB1, 0x0F, 0x84, 0x72, 0x8C, 0x7E, 0x5E, 0x19, 0x00, 0x1E]
        
        #Magic value used for version 7 little-endian 32-bit Granny files
        LittleEndian32v1 = [0x29, 0xDE, 0x6C, 0xC0, 0xBA, 0xA4, 0x53, 0x2B, 0x25, 0xF5, 0xB7, 0xA5, 0xF6, 0x66, 0xE2, 0xEE]

        #Magic value used for version 7 little-endian 32-bit Granny files
        LittleEndian32v2 = [0x29, 0x75, 0x31, 0x82, 0xBA, 0x02, 0x11, 0x77, 0x25, 0x3A, 0x60, 0x2F, 0xF6, 0x6A, 0x8C, 0x2E]
        
        #Magic value used for version 7 big-endian 32-bit Granny files
        BigEndian32v1 = [0x0E, 0x11, 0x95, 0xB5, 0x6A, 0xA5, 0xB5, 0x4B, 0xEB, 0x28, 0x28, 0x50, 0x25, 0x78, 0xB3, 0x04]

        #Magic value used for version 7 big-endian 32-bit Granny files
        BigEndian32v2 = [0x0E, 0x74, 0xA2, 0x0A, 0x6A, 0xEB, 0xEB, 0x64, 0xEB, 0x4E, 0x1E, 0xAB, 0x25, 0x91, 0xDB, 0x8F]

        #Magic value used for version 7 little-endian 64-bit Granny files
        LittleEndian64v1 = [0xE5, 0x9B, 0x49, 0x5E, 0x6F, 0x63, 0x1F, 0x14, 0x1E, 0x13, 0xEB, 0xA9, 0x90, 0xBE, 0xED, 0xC4]

        #Magic value used for version 7 little-endian 64-bit Granny files
        LittleEndian64v2 = [0xE5, 0x2F, 0x4A, 0xE1, 0x6F, 0xC2, 0x8A, 0xEE, 0x1E, 0xD2, 0xB4, 0x4C, 0x90, 0xD7, 0x55, 0xAF]

        #Magic value used for version 7 big-endian 64-bit Granny files
        BigEndian64v1 = [0x31, 0x95, 0xD4, 0xE3, 0x20, 0xDC, 0x4F, 0x62, 0xCC, 0x36, 0xD0, 0x3A, 0xB1, 0x82, 0xFF, 0x89]

        #Magic value used for version 7 big-endian 64-bit Granny files
        BigEndian64v2 = [0x31, 0xC2, 0x4E, 0x7C, 0x20, 0x40, 0xA3, 0x25, 0xCC, 0xE1, 0xC2, 0x7A, 0xB1, 0x32, 0x49, 0xF3]

        #Magic value used for version 7 big-endian 64-bit Granny files - console 
        BigEndian32v3 = [0xB5, 0x95, 0x11, 0x0E, 0x4B, 0xB5, 0xA5, 0x6A, 0x50, 0x28, 0x28, 0xEB, 0x04, 0xB3, 0x78, 0x25]
        
        if String == bytearray(LittleEndian32v1) or String == bytearray(LittleEndian32v2) or String == bytearray(LittleEndian32v3) or String == bytearray(LittleEndian32v4):
            return "LittleEndian32" 

        elif String == bytearray(LittleEndian64v1) or String == bytearray(LittleEndian64v2):
            return "LittleEndian64" 
                    
        elif String == bytearray(BigEndian64v1) or String == bytearray(BigEndian64v2):
            return "BigEndian64" 
            
        elif String == bytearray(BigEndian32v1) or String == bytearray(BigEndian32v2) or String == bytearray(BigEndian32v3):
            return "BigEndian32"   
        
        else:        
            return None

    # 64 bit - member is 44 bytes
    # 32 bit - member is 32 bytes
    def readStruct(stream, offset, Format):
    
        stream.seek(offset,0)
        member = MemberDefinition()
        member.Type = stream.readUInt()
        if member.Type == 0:
            return member
        member.StringOffset = readformat(stream, Format)
        member.definitionOffset = readformat(stream, Format)
        member.arraySize = stream.readUInt()
        for i in range(3):
            member.extra.append(stream.readUInt())
        if Format == 'LittleEndian32' or Format == 'BigEndian32':
            stream.readBytes(4)
        else:
            stream.readBytes(8)
        Position = stream.tell()
        stream.seek(member.StringOffset,0)
        if  member.Type != 0:
            member.name =  readString(stream)
        stream.seek(Position,0)
        return member



    def readSubStructV2(stream, MagicType, definitionOffset): 
        AllSubHeaders = []
        while(True):
            SubHeader = readStruct(stream,definitionOffset, MagicType) 
            if SubHeader.Type != 0:
                AllSubHeaders.append(SubHeader)
                definitionOffset = stream.tell()
            else:
                return AllSubHeaders


    def InsertBytes(Data,offset,byte_array):
        for i in range(4):
            Data[offset+i] = byte_array[i]
            
    
    def read_relocations(index,file,AllDecompressedData,section_offsets):
        Relocations = []
                
        for i in range(section.relocations_count):
            dummy = Relocation()
            dummy.offset = file.readUInt()
            dummy.target_section = file.readUInt()
            dummy.target_offset = file.readUInt()
            Relocations.append(dummy)

        
        # apply relocations
        for relocation in Relocations:
            byte_array = bytearray()
            source_offset  = section_offsets[index] + relocation.offset;
            #print(source_offset)      
            target_offset = section_offsets[relocation.target_section] + relocation.target_offset;
            #print(target_offset)
            if Format == "BigEndian64" or Format == "BigEndian32":
                byte_array = target_offset.to_bytes(4,'big')
            else:
                byte_array = target_offset.to_bytes(4,'little')
            #print(byte_array)
            InsertBytes(AllDecompressedData,source_offset,byte_array)


    def ReadMarsheling(section,file,section_offsets,num_section):
        #print("marshallings_count",section.marshallings_count )
        for i in range(section.marshallings_count):
            count = file.readUInt()
            #print("count",count)
            OffsetInSection = file.readUInt()
            #print("OffsetInSection",OffsetInSection)
            Marshel_Section = file.readUInt()
            #print("Marshel_Section",Marshel_Section)
            Marshel_Offset = file.readUInt() # target offset
            #print("Marshel_Offset",Marshel_Offset)
            Defenition_Offset = section_offsets[info.type_section] + Marshel_Offset
            #print("Defenition_Offset",Defenition_Offset)
            stream.seek(section_offsets[num_section] + OffsetInSection,0) # 3 is a place holder
            #print("stream location",stream.tell())
            MixedMarshal(stream,count, Defenition_Offset)


    def GR2decompress(DecompressedData,ComperesedData,decompressed_size,compressed_size,section):
        
        reverseBytes  = 0
        
        if Format == "BigEndian64" or Format == "BigEndian32":
            reverseBytes  = 1
            
        lib = ctypes.WinDLL("granny2.dll")
        if section.compression == 1 or section.compression == 2:
            GrannyDecompressData = lib['_GrannyDecompressData@32']
            #Declare function argument types - as far as i know not necessary 
            GrannyDecompressData.argtypes = (ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_void_p,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_void_p)
            #declare result type
            GrannyDecompressData.restype = ctypes.c_int32
            #send all aguments to function and get result in DecompressedData
            value = GrannyDecompressData(section.compression,reverseBytes,compressed_size,ComperesedData,section.first16bit,section.first8bit,decompressed_size,DecompressedData)

        if section.compression == 3 or section.compression == 4:
            beginDecompressProc = lib['_GrannyBeginFileDecompression@24']
            decompressProc = lib['_GrannyDecompressIncremental@12']
            endDecompressProc = lib['_GrannyEndFileDecompression@4']
            WorkMemSize = 0x4000
            WorkMemBuffer = ctypes.cast(ctypes.create_string_buffer(WorkMemSize),ctypes.POINTER(ctypes.c_char))
            state = beginDecompressProc(section.compression,reverseBytes,decompressed_size,DecompressedData,WorkMemSize, WorkMemBuffer)
            Position = 0
            while(Position < compressed_size):
                chunkSize = min(compressed_size - Position, 0x2000)
                incrementOk = decompressProc(state, chunkSize, ComperesedData[Position:])
                if (incrementOk != 1):
                    print("Failed to decompress")
                Position += chunkSize        
            ok = endDecompressProc(state)
            if ok != 1:
                print("Failed to decompress")
            
        return DecompressedData

    #===================================================================
    #start
    #===================================================================

  
    f = NoeBitStream(data, NOE_LITTLEENDIAN)

    #====================================================================
    # header
    #====================================================================

    header = Header()
    info = HeaderInfo()
      
    Format = FormatType(f.readBytes(16))
   
    if Format == None:
        print("Format not supported")
        return 0
    
    if Format == "BigEndian64" or Format == "BigEndian32":
        f = NoeBitStream(data, NOE_BIGENDIAN)
    
    f.seek(0,0)
    for i in range(4):
        header.magic.append(f.readUInt())

    header.size = f.readUInt()
    header.format = f.readUInt()


    for i in range(2):
        header.reserved.append(f.readUInt())

    info.version = f.readUInt()
    info.file_size = f.readUInt()
    info.crc32 = f.readUInt()
    info.sections_offset = f.readUInt() #From 'version'
    info.sections_count = f.readUInt()
    info.type_section = f.readUInt()
    info.type_offset = f.readUInt()
    info.root_section = f.readUInt()
    info.root_offset = f.readUInt()
    info.tag = f.readUInt()

    for i in range(4):
        info.extra.append(f.readUInt())

    if info.version == 7:
        info.stringTableCrc = f.readUInt()
        info.reserved1 = f.readUInt()
        info.reserved2 = f.readUInt()
        info.reserved3 = f.readUInt() 

    #====================================================================
    # section header
    #====================================================================

    SectionHeaders = []

    for i in range(info.sections_count):
        dummy = Section_Header()
        dummy.compression = f.readUInt()    
        dummy.data_offset = f.readUInt() #offset In File
        dummy.data_size = f.readUInt() # compressed Size
        dummy.decompressed_size = f.readUInt()
        dummy.alignment = f.readUInt()
        dummy.first16bit = f.readUInt()
        dummy.first8bit  = f.readUInt()
        dummy.relocations_offset = f.readUInt()
        dummy.relocations_count = f.readUInt()
        dummy.marshallings_offset = f.readUInt() #mixedMarshallingDataOffset
        dummy.marshallings_count = f.readUInt()
        SectionHeaders.append(dummy)

    section_offsets = []
    size = 0

    section_offsets.append(0)
    for offset in SectionHeaders:
        section_offsets.append(offset.decompressed_size + size) 
        size += offset.decompressed_size

    section_offsets = section_offsets[:info.sections_count] # need to test make sure is always correct
    Section_totalSize = section_offsets[len(section_offsets) - 1]

    #====================================================================
    #Data Decompressing and manipulation
    #====================================================================


    AllDecompressedData = []
    # read sections and decompress using granny2.dll
    for section in SectionHeaders:
        if section.compression == 0:
            f.seek(section.data_offset,0)
            AllDecompressedData += f.readBytes(section.data_size)
            continue
        if section.data_size == 0:
            continue
        ComperesedData = []
        #create bytes object of wanted size 
        DecompressedData = bytes(section.decompressed_size)
        f.seek(section.data_offset,0)
        ComperesedData = f.readBytes(section.data_size)
        AllDecompressedData += GR2decompress(DecompressedData,ComperesedData,section.decompressed_size,section.data_size,section)
     
    
    #read and apply relocation
    index = 0
    for section in SectionHeaders:
        if section.relocations_count == 0:
            index += 1
            continue

        f.seek(section.relocations_offset,0)
                
        if section.compression == 3 or section.compression == 4:

            ComperesedData = []
            DecompressedData = []
            DecompressedSection = []

            DecompressedData = bytes(section.relocations_count * 12)
            CompressedSize = f.readUInt()
            ComperesedData = f.readBytes(CompressedSize)
            DecompressedSection = GR2decompress(DecompressedData,ComperesedData,section.relocations_count * 12,CompressedSize,section)
            
            SectionStream = NoeBitStream(bytes(DecompressedSection), NOE_LITTLEENDIAN)
            
            if Format == "BigEndian64" or Format == "BigEndian32":
                SectionStream = NoeBitStream(bytes(DecompressedSection), NOE_BIGENDIAN)

            SectionStream.seek(0,0)

            read_relocations(index,SectionStream,AllDecompressedData,section_offsets)

        else:
            read_relocations(index,f,AllDecompressedData,section_offsets)

        index += 1
    
    stream = NoeBitStream(bytearray(AllDecompressedData), NOE_LITTLEENDIAN)
    
    if Format == "BigEndian64" or Format == "BigEndian32":
        stream = NoeBitStream(bytearray(AllDecompressedData), NOE_BIGENDIAN)
        
    stream.seek(0,0)
    
    
    #need marsheling only if on none litle endian system????
    if Format != "LittleEndian32" and Format != "LittleEndian64":  
        num_section = 0   
        # marsheling
        for section in SectionHeaders: 
            if section.marshallings_count <= 0:
                num_section += 1
                continue
            f.seek(section.marshallings_offset,0)							
            #print("marsheling location",f.tell())
            if section.compression == 3 or section.compression == 4:

                ComperesedData = []
                DecompressedData = []
                DecompressedSection = []
                DecompressedData = bytes(section.marshallings_count * 16)
                CompressedSize = f.readUInt()
                ComperesedData = f.readBytes(CompressedSize)
                DecompressedSection = GR2decompress(DecompressedData,ComperesedData,section.marshallings_count * 16,CompressedSize,section)
                
                SectionStream = NoeBitStream(bytes(DecompressedSection), NOE_LITTLEENDIAN)
                
                if Format == "BigEndian64" or Format == "BigEndian32":
                    SectionStream = NoeBitStream(bytes(DecompressedSection), NOE_BIGENDIAN)
                    
                SectionStream.seek(0,0)

                ReadMarsheling(section,SectionStream,section_offsets,num_section)

            else:
                ReadMarsheling(section,f,section_offsets,num_section)
    
    #=================================================================================
    # reading all data - verts,faces,bones etc...
    #=================================================================================
       
    root_section = root()
    root_section.offset = section_offsets[info.type_section] + info.type_offset
    stream.seek(info.root_offset,0)
    
    stream = NoeBitStream(bytearray(AllDecompressedData), NOE_LITTLEENDIAN)
    
    if Format == "BigEndian64" or Format == "BigEndian32":
        stream = NoeBitStream(bytearray(AllDecompressedData), NOE_BIGENDIAN)
        
    Members = []

    Position = root_section.offset
    while(True):
        member  = readStruct(stream,Position ,Format)
        if member.Type == 0:
            break
        Members.append(member)
        Position = stream.tell()
   

    #after applying marsheling changes    
    stream.seek(0,0)   
    
    MemberClass = createStruct(Members)
    
    #civ6 game fix
    if hasattr(MemberClass, "FxsModels"):
       civ6m = dummy_member()
       for mn in vars(MemberClass):
           if mn[:3] == 'Fxs':
                setattr(civ6m, mn[3:], [])
       MemberClass = civ6m
         
    for member in Members:
        if member.name[:3] == 'Fxs':
            member.name = member.name[3:]
            
            
    #main gr2 TreeWalker function 
    StructHeaders = seekContoller(Members,MemberClass)
    
    Models = extractData(StructHeaders)

    return Models
 

def ComposeLocalMatrix(Transform):
        q = Transform.Quaterion
        t = Transform.Translation
        s = Transform.ScaleShear
        
        # matrix are column major in granny
        # first we sclae then translate then rotate
        # for row-major matrix we multiply matrix in the following order:  sclae * translation * rotation
        # for column-major in reverse order rotation * translation * scale
        # I made all my matrix row order
        RotationMat = NoeQuat((q[0],q[1],q[2],q[3])).toMat43().toMat44().transpose()
        ScaleMat = NoeMat44( [(s[0],s[1],s[2],0.0), (s[3],s[4],s[5],0.0), (s[6],s[7],s[8],0.0), (0.0,0.0,0.0,1.0)] ).transpose()
        TranslationMat = NoeMat44( [(1.0,0.0,0.0,t[0]), (0.0,1.0,0.0,t[1]), (0.0,0.0,1.0,t[2]), (0.0,0.0,0.0,1.0)] ).transpose()
        ComposeMat = ScaleMat * RotationMat * TranslationMat
        ComposeMat = ComposeMat.transpose()
        ComposeMat = NoeMat43([(ComposeMat[0][0], ComposeMat[0][1], ComposeMat[0][2]), (ComposeMat[1][0], ComposeMat[1][1], ComposeMat[1][2]), (ComposeMat[2][0], ComposeMat[2][1], ComposeMat[2][2]), (ComposeMat[0][3], ComposeMat[1][3], ComposeMat[2][3])])

        return ComposeMat
        
def MergeSkeletons(model):
    bones = []
    
    print(type(model))
    print(type(model.Bones))
    print(type(model.Bones[0]))
    #print(model.Bones[0].InitialPlacement)
    
    for i in range(len(model.Bones)):
        temp = Model()
        temp.Bones = model.Bones[i] 
        #not sure about this, seems like a mistake in the code "model.Bones[i].InitialPlacement" should be "model.InitialPlacement" but if it works no need to touch for now
        if MULTIFILE == 0:
            temp.InitialPlacement = model.Bones[i].InitialPlacement
        ModelBones = SkeletonLocale(temp)
        if i == 0:
            bones += ModelBones
            continue
        else:
           correction_num = len(bones)
           for bo in ModelBones:
                bo.index += correction_num
                if bo.parentIndex == -1:
                    continue
                else:
                    bo.parentIndex += correction_num
           bones += ModelBones

    return  bones
 
def UpdatePostMerge(model):
    tempNames = []
    tempTransforma = []
    for bones in model.Bones:
        tempNames += bones.BoneNames
        tempTransforma += bones.Transform
    #everything except for bone names is of no use anymore so i dont bother to upadte
    model.Bones = Skeleton()
    model.Bones.BoneNames = tempNames
    model.Bones.Bone_Count = len(tempNames)
    model.Bones.InverseWorldTransform = -1
    model.Bones.Name = 'Merged'
    model.Bones.Transform = tempTransforma
    model.Bones.InitialPlacement = -1
    
    return model.Bones

    
#load skeleton data - using local transform
def SkeletonLocale(model):
    
    bones = []        
    Name = model.Bones.Name
    BoneCount = model.Bones.Bone_Count
    BoneNameArray = model.Bones.BoneNames
    ParentIndex = model.Bones.ParentIndex
    tramsformaers = model.Bones.Transform
    if model.InitialPlacement:
        Initial_location = ComposeLocalMatrix(model.InitialPlacement)
        

    for i in range(BoneCount):
       boneMat = ComposeLocalMatrix(tramsformaers[i])
       
       #use world inverse matrix only for root bone to fix orintation for a few models, 95%+ load correctly when ,multiplying by Initial_location
       if i == 0:
            Matrix = model.Bones.InverseWorldTransform[0]
            boneMat = NoeMat44( [(Matrix[0],Matrix[1],Matrix[2],Matrix[3]), 
                     (Matrix[4],Matrix[5],Matrix[6],Matrix[7]), 
                     (Matrix[8],Matrix[9],Matrix[10],Matrix[11]), 
                     (Matrix[12],Matrix[13],Matrix[14],Matrix[15])]).toMat43().inverse()
       bones.append( NoeBone(i, BoneNameArray[i], boneMat, None, ParentIndex[i]) )
       
    # Converting local matrix to world space
    for i in range(0, BoneCount):
        j = bones[i].parentIndex
        if j != -1:        
            bones[i].setMatrix(bones[i].getMatrix().__mul__(bones[j].getMatrix()))
        #else:
        #    #add initial placment to root bone
        #    if model.InitialPlacement:
        #        bones[i].setMatrix(Initial_location * bones[i].getMatrix())


        
    return bones  
    
def CreateBytesData(Positions,Normals,UV,UV2,Tangents,BoneIndex,BoneWights,Faces):

    NewBytes = bytearray()
    
    for position in Positions:
        var = struct.pack('fff',position[0],position[1],position[2])
        NewBytes += var
     
    
    for Normal in Normals:
        var = struct.pack('fff',Normal[0],Normal[1],Normal[2])
        NewBytes += var
        
    for coord in UV:
        var = struct.pack('ff',coord[0],coord[1])
        NewBytes += var
      
    for coord in UV2:
        var = struct.pack('ff',coord[0],coord[1])
        NewBytes += var
        
    for Tangent in Tangents:
        var = struct.pack('fff',Tangent[0],Tangent[1],Tangent[2])
        NewBytes += var
      
    for index in BoneIndex:
        var = struct.pack('IIII',index[0],index[1],index[2], index[3]) 
        NewBytes += var
           
    for BoneWight in BoneWights:
        var = struct.pack('ffff',BoneWight[0],BoneWight[1],BoneWight[2], BoneWight[3])
        NewBytes += var
     
    #for negative face index assuming type is Int16 - short
    lowest = min(Faces)
    if lowest < 0:
        tempbytes = bytearray()
        for tri in Faces:       
            var = struct.pack('h',tri)
            tempbytes += var
            
        In = NoeBitStream(tempbytes, NOE_LITTLEENDIAN) 
        In.seek(0,0)
        
        for i in range(len(Faces)):
            var = In.readUShort()
            var = struct.pack('I',var)
            NewBytes += var
    else:
        for tri in Faces:       
            var = struct.pack('I',tri)
            NewBytes += var
        
    return NewBytes

    
#load mesh data
def LoadMeshData(model):
 
    matList = []
    texList = []
    MatCount = 0             
    
    for i in range(len(model.Meshes)):

        Normals = []
        UV1 = []
        UV2 = []
        Tangents = []
        BoneIndices = []
        BoneWeights = []
        Indices = []
        matListTemp = []
        texListTemp = []
        
        Vertex_Count = model.Meshes[i].info.Vertex_Count
        Face_Count = model.Meshes[i].info.Face_Count
        Mesh_Name = model.Meshes[i].info.Mesh_Name  
        Polygroups = model.Meshes[i].info.Polygroups       
        
        Positions =  model.Meshes[i].mesh.Positions       
        if model.Meshes[i].mesh.BoneWeights:
            BoneWeights = model.Meshes[i].mesh.BoneWeights
            
            #allows for any number of weights - if less than 4 weights will simply add 0 to complete extra weighs
            if len(BoneWeights[0]) != 4:
                num = 4 - len(BoneWeights[0])
                for weight in BoneWeights:
                    for bw in range(num):
                        weight.append(0)
                        
        if model.Meshes[i].mesh.Normals:
            Normals = model.Meshes[i].mesh.Normals
            if len(Normals[0]) != 3:
                Normals = []
                
        if model.Meshes[i].mesh.TextureCoordinates:
            UV1 = model.Meshes[i].mesh.TextureCoordinates
            if len(UV1[0]) != 2:
                UV1 = []
                
        if model.Meshes[i].mesh.TextureCoordinates2:
            UV2 = model.Meshes[i].mesh.TextureCoordinates2
            if len(UV2[0]) != 2:
                UV2 = []
        #tangents (matrix[0]=normal, matrix[1]=tangent, matrix[2]=bitangent)      
        if model.Meshes[i].mesh.Tangents:
            Tangents = model.Meshes[i].mesh.Tangents
            #for now i am deleting tangents data -----------------------need to address in the future
            Tangents = []
              
        #apply correction to bone index to global skeleton
        if model.Meshes[i].mesh.BoneIndices and model.Bones:
            NumIndexPerBone = len(model.Meshes[i].mesh.BoneIndices[0])
            BoneIndices = model.Meshes[i].mesh.BoneIndices
            Count = 0
            for index in BoneIndices:
                NewIndex = []
                IndexName = []
                for j in range(4):
                    if j >= NumIndexPerBone:
                        NewIndex.append(0)
                        continue
                    name = model.Meshes[i].mesh.BoneBindings[index[j]]                   
                    if name in (model.Bones.BoneNames):
                        IndexName.append(name)
                        NewIndex.append(model.Bones.BoneNames.index(IndexName[j]))
                if NewIndex:
                    model.Meshes[i].mesh.BoneIndices[Count] = NewIndex
                Count += 1             
        
        
        #if we have a bone bindings but no weights or Bone Indices - assume rigid mesh that should be skinned to this bone
        if model.Meshes[i].mesh.BoneBindings and not BoneWeights and model.Bones:            
                for boneName in model.Meshes[i].mesh.BoneBindings:
                    for num in range(len(Positions)):
                        index = []
                        weights = []
                        weights.append(255)
                        index.append(model.Bones.BoneNames.index(boneName))
                        for ij in range(3):
                            index.append(0)
                            weights.append(0.0)
                        BoneIndices.append(index)
                        BoneWeights.append(weights)
         
        
        Indices = model.Meshes[i].mesh.Indices
        NewBytes = CreateBytesData(Positions,Normals,UV1,UV2,Tangents,BoneIndices,BoneWeights,Indices)
                     
        ms = NoeBitStream(NewBytes, NOE_LITTLEENDIAN) 
        ms.seek(0,0)
                
        VertBuff = ms.readBytes(len(Positions) * 12) 
        rapi.rpgBindPositionBufferOfs(VertBuff, noesis.RPGEODATA_FLOAT, 12, 0) 
                
        if Normals:
            VertBuff = ms.readBytes(len(Normals) * 12)
            rapi.rpgBindNormalBufferOfs(VertBuff, noesis.RPGEODATA_FLOAT, 12, 0) 
        
        if UV1:
            VertBuff = ms.readBytes(len(UV1) * 8)
            rapi.rpgBindUV1BufferOfs(VertBuff, noesis.RPGEODATA_FLOAT, 8, 0)
        
        if UV2:
            VertBuff = ms.readBytes(len(UV2) * 8)
            rapi.rpgBindUV2BufferOfs(VertBuff, noesis.RPGEODATA_FLOAT, 8, 0)
            
        if BoneIndices:
            VertBuff = ms.readBytes(len(BoneIndices) * 16)
            rapi.rpgBindBoneIndexBufferOfs(VertBuff, noesis.RPGEODATA_UINT, 16, 0, 4)           
            
        if BoneWeights:
            VertBuff = ms.readBytes(len(BoneWeights) * 16)
            rapi.rpgBindBoneWeightBufferOfs(VertBuff, noesis.RPGEODATA_FLOAT, 16, 0, 4)
 
            
        if matListTemp:
                rapi.rpgSetMaterial(matList[MatCount].name)
                #print("added new marerial {}".format(i))
                MatCount += 1
        
        for j in range(len(Polygroups)):         
            FaceBuff = ms.readBytes(Polygroups[j] * 3 * 4)
            rapi.rpgSetName(Mesh_Name + "_" + str(j))
            rapi.rpgCommitTriangles(FaceBuff, noesis.RPGEODATA_UINT, Polygroups[j] * 3, noesis.RPGEO_TRIANGLE, 1)
        
        rapi.rpgClearBufferBinds()
        
    return texList, matList
 

def animation(model,bones, AnimMode, Main_Model,frameRate):
    
    if AnimMode == 1:
       Models = GR2Reader(model)
       #find track name the belongs to model name                     
       for i,mo in enumerate(Models):
            if mo.Name == Main_Model.Name:
                model = Models[i]
                break
            else:
                model = Models[0]
         

       #check orintation is the same for both files
       #for row in range(3):
       #     if Main_Model.OrinationInfo[row] != model.OrinationInfo[row]:
       #         CorrectionMatrix = fixOrinationInfo(Main_Model,model)
       #         break

    
       BoneNameArray = []
       BoneNameArray = Main_Model.Bones.BoneNames
       
       
    if AnimMode == 2:
       BoneNameArray = model.Bones.BoneNames
       
    frames = []
    anims = []  
      
       
    if model.Trackgroups:
        
        Duration = model.AnimationInfo.Duration 
        TimeStep = model.AnimationInfo.TimeStep 
        Oversampling = model.AnimationInfo.Oversampling
        
        #some models have trackgroups with no transform tracks
        if not hasattr(model.Trackgroups, "TransformTracks"):
            return [],1
            
        for Track in model.Trackgroups.TransformTracks:
                            
             #if animation contains a bone that is not part of skeleton i ignore that bone
             if Track.Name not in BoneNameArray:
                    continue
                    
             #get index of wanted bone
             Bindex = BoneNameArray.index(Track.Name)  
            
             #get locale transformes - will be used for bones that are static during animation
             if AnimMode == 1:
                 Quaterion = Main_Model.Bones.Transform[Bindex].Quaterion
                 Translation = Main_Model.Bones.Transform[Bindex].Translation
                 ScaleShear = Main_Model.Bones.Transform[Bindex].ScaleShear
                
             if AnimMode == 2:
                 Quaterion = model.Bones.Transform[Bindex].Quaterion
                 Translation = model.Bones.Transform[Bindex].Translation
                 ScaleShear = model.Bones.Transform[Bindex].ScaleShear
             
             Dummy = Transform_Tracks()
             Dummy.Name = Track.Name  

             if type(Track.OrientationCurve) == daidentity:
                Dummy.OrientationCurve.Controls = [list(Quaterion)]
                Dummy.OrientationCurve.Knots = [0.0]
             else:
                Dummy.OrientationCurve.Controls, Dummy.OrientationCurve.Knots = GetRotation(Track.OrientationCurve)
                if not Dummy.OrientationCurve.Controls:
                    Dummy.OrientationCurve.Controls = [list(Quaterion)]
                    Dummy.OrientationCurve.Knots = [0.0]
                        
             if type(Track.PositionCurve) == daidentity:
                Dummy.PositionCurve.Controls = [list(Translation)]
                Dummy.PositionCurve.Knots = [0.0]
             else:
                Dummy.PositionCurve.Controls , Dummy.PositionCurve.Knots = GetTranslation(Track.PositionCurve)
                if not Dummy.PositionCurve.Controls:
                    Dummy.PositionCurve.Controls = [list(Translation)]
                    Dummy.PositionCurve.Knots = [0.0]
                        
             if type(Track.ScaleShearCurve) == daidentity:
                Dummy.ScaleShearCurve.Controls = [list(ScaleShear)]
                Dummy.ScaleShearCurve.Knots = [0.0]
             else:
                Dummy.ScaleShearCurve.Controls , Dummy.ScaleShearCurve.Knots  = Track.ScaleShearCurve.GetMartix()
                if not Dummy.ScaleShearCurve.Controls:
                    Dummy.ScaleShearCurve.Controls = [list(ScaleShear)]
                    Dummy.ScaleShearCurve.Knots = [0.0]
             
             Frame = CreateKeyFrame(Dummy)
             Frame = FrameInterpolate(Frame)
             Frame = ApplyShear(Frame)
             frames.append(Frame)
        
                
        frames = EqualizeFrames(frames,Duration,TimeStep)

        if frames:
            animFrameMats = []
            Numframes = len(frames[0])             
            NumBones1 = len(BoneNameArray)            
            NumBones2 = len(frames)
            
            #create list of bones used in animation
            Names = []
            for k in range(NumBones2):
                Names.append(frames[k][0].Name)
               
            #create a list length of all bones in skeleton and put each "bone frames" in the correct order as in skeleton 
            BoneFramelist = [-1] * NumBones1     
            for k,name in enumerate(Names):
                Bindex = BoneNameArray.index(name)
                BoneFramelist[Bindex] = frames[k]
            
            for f in range(Numframes): 
                for i,Bone in enumerate(BoneFramelist):
                    #Bone is in bone list but not used in animation - i assign of loclae skeleton bone
                    if Bone == -1:
                        if AnimMode == 1:
                            boneMat = ComposeLocalMatrix(Main_Model.Bones.Transform[i]) 
                            
                        if AnimMode == 2:
                            boneMat = ComposeLocalMatrix(model.Bones.Transform[i])                   
                    else:   
                         boneMat = Bone[f].Matrix
                    animFrameMats.append(boneMat)   
            if Numframes/Duration >=  frameRate:
                frameRate = Numframes/Duration
            anim = NoeAnim("Anim", bones, Numframes, animFrameMats,frameRate )
            #used to set frame rate speed in noesis screen
            rapi.setPreviewOption("setAnimSpeed", str(int(frameRate)))
            anims.append(anim) 

        return anims,frameRate
    
    
def noepyLoadModel(data, mdlList):   
        
        All_Models = []
        Models = []
        anim_data = []
        anims = []
        bones = []
        frameRate = 1
        
        baseName = rapi.getLocalFileName(rapi.getInputName())
        #can be .gr2 or .fgx
        extension = baseName[-3:]
        
        if ANIMATION_MODE == 1:            
            anim_data = rapi.loadPairedFileOptional("Animation_Data", extension)
            
        if SKELETON_LOAD == 1:
           skel_data = rapi.loadPairedFileOptional("Skeleton_Data", extension)
        
        if MULTIFILE == 1 or MULTIFILE == 2 or MULTIFILE == 3:
        
        #load all .gr2 files in directory
          Combined = Model()
          MeshDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Open Folder", "Select the folder that containes wanted .GR2 files")
          for rootL, dirs, files in os.walk(MeshDir):
               for fileName in files:
                    lowerName = fileName.lower()
                    if lowerName.endswith(".gr2"):
                        MeshFilePath = os.path.join(rootL, fileName)
                        gr2Temp = open(MeshFilePath,"rb")
                        TempData = gr2Temp.read()
                        TModels = GR2Reader(TempData) 
                        All_Models += TModels
                    
          #copy all meshes and skeleton data to a single model
          for model in All_Models:
          
            if MULTIFILE == 1 or MULTIFILE == 2:
                Combined.Meshes += model.Meshes
                
            if MULTIFILE == 1 or MULTIFILE == 3:
                Combined.Bones.append(model.Bones)
                
            Combined.InitialPlacement = model.InitialPlacement
            
          Models.append(Combined)

          if MULTIFILE == 1 or MULTIFILE == 3:
              bones = MergeSkeletons(Combined)                       
              Combined.bones = UpdatePostMerge(Combined)

                   
        else:
            Models = GR2Reader(data)  
        
        if SKELETON_LOAD == 1 and skel_data:
            Skeleton = GR2Reader(skel_data)
            Models[0].Bones = Skeleton[0].Bones
        
        #condition when format is not supported and Models is equal to 0
        if Models == 0:
            return 0
            
        for model in Models:
                                 
            ctx = rapi.rpgCreateContext()
                        
            if model.Bones and MULTIFILE == 0:
                if MERGE_SCENE ==1:
                    bones = MergeSkeletons(model)
                    model.bones = UpdatePostMerge(model)
                    
                else:
                    bones = SkeletonLocale(model)               
                
            if model.Meshes:
                texList, matList = LoadMeshData(model)
                mdl = rapi.rpgConstructModel()
                if matList:
                    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
            else:
                mdl = NoeModel()
                       
                
            if anim_data and bones:                    
                    anims,frameRate = animation(anim_data,bones, ANIMATION_MODE, model,frameRate)
                    
            elif ANIMATION_MODE == 2 and bones and len(bones) > 1 and model.Trackgroups:
                    anims,frameRate = animation(model,bones, ANIMATION_MODE, None,frameRate)

              
            if bones:
                mdl.setBones(bones)
                
            if anims:
                mdl.setAnims(anims)
            
            #make sure i load only models that contain mesh and/or skeleton data
            if not bones and not model.Meshes:
                continue
                
            mdlList.append(mdl)
            
        #if model.OrinationInfo:
        rapi.setPreviewOption("setAngOfs", "0 90 90")
        #rapi.rpgClearBufferBinds()       
        
        return 1 