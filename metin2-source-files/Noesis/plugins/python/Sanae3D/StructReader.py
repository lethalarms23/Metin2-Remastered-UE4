#a struct reader

from inc_noesis import *
import noesis
import rapi

class StructReader(object):
    
    def __init__(self, data):
        
        self.inFile = NoeBitStream(data)
        
    def filesize(self, offset=0):
        
        self.inFile.seek(0, 2)
        size = self.inFile.tell()
        self.inFile.seek(offset)
        return size
    
    def read(self, n=0):
        
        self.inFile.readBytes(n)
        
    def seek(self, n=0, mode=0):
        
        self.inFile.seek(n, mode)
        
    def readBytes(self, n):
        
        return self.inFile.readBytes(n)
    
    #def read_char(self, n=1):
        
        #data = noeStrFromBytes(self.inFile.readBytes(n))
        #if n == 1:
            #return data[0]
        #return data
        
    def read_string(self, n=1):
        
        string = noeStrFromBytes(self.inFile.readBytes(n))
        return string
    
    def read_byte(self, n=1):
        
        data = self.inFile.read('B'*n)
        if n == 1:
            return data[0]
        return data
        
    def read_long(self, n=1):
        
        data = self.inFile.read('l'*n)
        if n == 1:
            return data[0]
        return data
    
    def read_short(self, n=1):
        
        data = self.inFile.read('h'*n)
        if n == 1:
            return data[0]
        return data
    
    def read_float(self, n=1):
        
        data = self.inFile.read('f'*n)
        if n == 1:
            return data[0]
        return data