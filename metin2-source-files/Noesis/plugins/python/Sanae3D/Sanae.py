from .StructReader import StructReader
from inc_noesis import *
import noesis
import rapi

class SanaeObject(object):
    '''A generic class that provides some common methods'''
    
    def __init__(self, data):
        
        self.inFile = StructReader(data)
        self.meshList = []
        self.uvList = []
        self.vertList = ""
        self.idxList = ""
        self.animList = ""
        self.texList = []
        self.matList = []
        
    def create_mesh(self, meshName):
      
        mesh = NoeMesh(self.idxList, self.vertList, meshName, self.animList)
        mesh.uvs.extend(self.uvList)
        self.meshList.append(mesh)