from inc_noesis import *
import noesis
import rapi
from Sanae3D.Sanae import SanaeObject

def registerNoesisTypes():
   handle = noesis.register("Crucis Fatal Fake", ".lmd")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel) #see also noepyLoadModelRPG
   noesis.logPopup()
   
   return 1

#check if it's this type based on the data
def noepyCheckType(data):
   #if len(data) < 4:
      #return 0
   #bs = NoeBitStream(data)
   #if bs.readBytes(4).decode("ASCII") != "xbin":
      #return 0
   return 1

#load the model
def noepyLoadModel(data, mdlList):
   ctx = rapi.rpgCreateContext()
   parser = CrucisFatalFake_LMD(data)
   parser.parse_file()
   mdl = NoeModel(parser.meshList, None, None)
   mdlList.append(mdl)
   mdl.setModelMaterials(NoeModelMaterials(parser.texList, parser.matList))
   return 1

class CrucisFatalFake_LMD(SanaeObject):
    
   def __init__(self, data):
       
      super(CrucisFatalFake_LMD, self).__init__(data)
      self.meshes = []
      self.materials = []

   def read_name(self):
     
      name = self.inFile.read_string(self.inFile.read_short())
      return name
      
   def parse_vertices(self, meshName, numVerts):
        
      self.vertList = []
      self.uvList = []
      for i in range(numVerts):
         vx, vy, vz = self.inFile.read_float(3)
         self.inFile.read_float()
         self.inFile.read_long(3)
         self.inFile.read_float(3)
         tu, tv = self.inFile.read_float(2)
         
         vx *= -1
         
         self.vertList.append(NoeVec3((vx, vy, vz)))
         self.uvList.append((NoeVec3((tu, tv, 1))))
    
   def parse_faces(self, meshName, numIdx):
        
      self.idxList = []
      for i in range(numIdx):
         self.idxList.append(self.inFile.read_short())
         
   def parse_submesh(self):
        
      unk = self.inFile.read_long()
      self.inFile.read_long(unk)
      unkbyte = self.inFile.read_byte()
      self.inFile.read_long()
      if unkbyte:
         count = self.inFile.read_long()
         for i in range(count):
            self.inFile.read_float(4)
            self.inFile.read_long()
            self.inFile.read_byte(2)
            unk1, unk2 = self.inFile.read_long(2)
            for j in range(unk2):
               self.inFile.read_long()
          
         count2 = self.inFile.read_long()
         for i in range(count2):
            self.inFile.read_long(2)
            self.inFile.read_float(5)
            self.inFile.read_long()
         self.inFile.seek(56, 1)
       
   def parse_mesh(self, numMesh):
        
      for i in range(numMesh):
            
         self.inFile.read_long()
         meshName = self.read_name()
         self.inFile.read_float(16)
         self.inFile.read_long()
         numVerts = self.inFile.read_long()
         self.inFile.read_byte()
         self.parse_vertices(meshName, numVerts)
         unk2, unk3, numIndex = self.inFile.read_long(3)
         self.parse_faces(meshName, numIndex)
         matIndex = self.inFile.read_long()
         matName = self.read_name()
         self.parse_submesh()
         self.create_mesh(meshName)
         self.meshes.append([meshName, matIndex])
  
   def parse_materials(self, numMat):
        
      offset = len(self.matList)
      for i in range(numMat):
         index = offset + i
         self.inFile.read_float(17)
         matName = self.read_name()
         self.inFile.read_long(5)
         numTex = self.inFile.read_long()
         for j in range(numTex):
            texName = self.read_name()
         self.materials.append(texName)
         
   def assign_materials(self):
      
      for i in range(len(self.meshes)):
         meshName = self.meshes[i][0]
         matIndex = self.meshes[i][1]
         texName = self.materials[matIndex]
         self.meshList[i].setMaterial(texName)
         
   def parse_textures(self, numTex):
      '''Parse textures'''
      
      for i in range(numTex):
         texName = self.read_name()
         size = self.inFile.read_long()
         texture = self.inFile.read(size)         

   def parse_file(self):

      self.inFile.read_long()
      self.read_name()
      unk1, numMesh = self.inFile.read_long(2)
      self.parse_mesh(numMesh)
      
      self.inFile.read_long(2)
      self.read_name()
      numMat = self.inFile.read_long()
      self.parse_materials(numMat)
      
      self.inFile.read_long()
      self.read_name()
      numMat2 = self.inFile.read_long()
      self.parse_materials(numMat2)
      self.assign_materials()
      
      numTex = self.inFile.read_long()
      self.parse_textures(numTex)
      