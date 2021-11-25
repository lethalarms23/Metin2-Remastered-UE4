#Resident Evil 3 Remake [PC] - ".mesh" Loader
#By Gh0stblade
#v1.7a unofficial
#Special thanks: Chrrox
#Edited for auto-detection of MDF by alphaZomega
#Options: These are bools that enable/disable certain features! They are global and affect ALL platforms!
#Var							Effect
#Misc
#Mesh Global
fDefaultMeshScale = 1.0 				#Override mesh scale (default is 1.0)
bOptimizeMesh = 0						#Enable optimization (remove duplicate vertices, optimize lists for drawing) (1 = on, 0 = off)
bMaterialsEnabled = 1					#Materials (1 = on, 0 = off)
bRenderAsPoints = 0						#Render mesh as points without triangles drawn (1 = on, 0 = off)
#Vertex Components
bNORMsEnabled = 1						#Normals (1 = on, 0 = off)
bTANGsEnabled = 1						#Tangents (1 = on, 0 = off)
bUVsEnabled = 1							#UVs (1 = on, 0 = off))
bSkinningEnabled = 1					#Enable skin weights (1 = on, 0 = off)
bDebugNormals = 0						#Debug normals as RGBA
bDebugTangents = 0						#Debug tangents as RGBA

#Options
bDebugMDF = 1							#Prints debug info for MDF files (1 = on, 0 = off)
bDebugMESH = 0 							#Prints debug info for MESH files (1 = on, 0 = off)
bPopupDebug = 1							#Pops up debug window on opening MESH with MDF (1 = on, 0 = off)
bPrintFileList = 1						#Prints a list of files used by the MDF
bColorize = 0							#Colors the materials of the model and lists which material is which color


from inc_noesis import *
import math
import os
import re

def registerNoesisTypes():
	handle = noesis.register("Resident Evil 3 Remake [PC]", ".1902042334")
	noesis.setHandlerTypeCheck(handle, meshCheckType)
	noesis.setHandlerLoadModel(handle, meshLoadModel)
	
	handle = noesis.register("Resident Evil 3 Remake Texture [PC]", ".190820018")
	noesis.setHandlerTypeCheck(handle, texCheckType)
	noesis.setHandlerLoadRGBA(handle, texLoadDDS)
	
	noesis.logPopup()
	return 1

def meshCheckType(data):
	bs = NoeBitStream(data)
	magic = bs.readUInt()
	if magic == 0x4853454D:
		return 1
	else: 
		print("Fatal Error: Unknown file magic: " + str(hex(magic) + " expected 'MESH'!"))
		return 0

def texCheckType(data):
	bs = NoeBitStream(data)
	magic = bs.readUInt()
	if magic == 0x00584554:
		return 1
	else: 
		print("Fatal Error: Unknown file magic: " + str(hex(magic) + " expected TEX!"))
		return 0
		
def texLoadDDS(data, texList):
	bs = NoeBitStream(data)
	
	magic = bs.readUInt()
	version = bs.readUInt()
	width = bs.readUShort()
	height = bs.readUShort()
	unk00 = bs.readUShort()
	mipCount = bs.readUByte()
	numImages = bs.readUByte()
	
	format = bs.readUInt()
	unk02 = bs.readUInt()
	unk03 = bs.readUInt()
	unk04 = bs.readUInt()
	
	#mipData = []
	#mipDataAll = []
	#for i in range(int(numImages)):
	#	for j in range(int(mipCount)):
	#		mipData.append([bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
	#	print (i)
	#	print (str(mipData[i]))
		
	
	#bs.seek(mipData[0][0], NOESEEK_ABS)
	#texData = bs.readBytes(mipData[0][3])
	
	mipData = []
	mipDataAll = []
	for i in range(numImages):
		for j in range(mipCount):
			mipData.append([bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
		mipDataAll.append(mipData[i])
		
	#print (len(mipData))
	#print (str(mipData[0]))
	#print (len(mipDataAll))
	#print (str(mipDataAll[0]))	
	bs.seek(mipDataAll[0][0], NOESEEK_ABS)
	texData = bs.readBytes(mipDataAll[0][3])
		
	texFormat = None
	if bDebugMDF:
		print(format)
	#if format == 0x2: #Actually float rgba
	#	count = int(len(texData)/4)
	#	intTexData = list(struct.unpack('I'*count, texData))
	#	for i in range(len(intTexData)):
	#		intTexData[i] += 1
	#			
	#	texData = struct.pack("<%uI" % len(intTexData), *intTexData)
	#	print(texData)
	#	texFormat = noesis.NOESISTEX_RGBA32
	#	texData = rapi.imageDecodeRaw(texData, width, height, "r32g32b32a32", 0)
	if format == 0x1C:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_ATI1)
	elif format == 0x1D:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC1)
	elif format == 0x47:#FIXME
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
	elif format == 0x48:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
	elif format == 0x50:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4)
	elif format == 0x5F:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC6H)
	elif format == 0x62:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
	elif format == 0x63:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
	else:
		print("Fatal Error: Unsupported texture type: " + str(format))
		return 0
		
	if texFormat != None:
		texList.append(NoeTexture(rapi.getInputName(), int(width), int(height), texData, texFormat))
	return 1
	
def ReadUnicodeString(bs):
	numZeroes = 0
	resultString = ""
	while(numZeroes < 2):
		c = bs.readUByte()
		if c == 0:
			numZeroes+=1
			continue
		else:
			numZeroes = 0
		resultString += chr(c)
	return resultString
		
def GetRootGameDir():
	path = rapi.getDirForFilePath(rapi.getInputName())
	while len(path) > 3:
		lastFolderName = os.path.basename(os.path.normpath(path))
		if lastFolderName == "stm":
			break
		else:
			path = os.path.normpath(os.path.join(path, ".."))
	return path	+ "\\"
	
def LoadExtractedDir():
	nativesPath = ""
	try: 
		with open(noesis.getPluginsPath() + '\\python\\RE3NativesPath.txt') as fin:
			nativesPath = fin.read()
			fin.close()
	except IOError:
		return ""
	return nativesPath
		
def SaveExtractedDir(dirIn):
	try: 
		with open(noesis.getPluginsPath() + '\\python\\RE3NativesPath.txt','w') as fout:
			print ("writing string: " + dirIn + " to " + str(fout))
			fout.flush()
			fout.write(str(dirIn))
			fout.close()
	except IOError:
		return
	return

class meshFile(object): 

	
	def __init__(self, data):
		self.inFile = NoeBitStream(data)
		self.boneList = []
		self.matNames = []
		self.matList = []
		self.texList = []
		self.texNames = []
		self.texColors = []
	
	def createMaterials(self):
		#Abort this section until errors are fixed for RE3
		#return
		global bColorize
		global bDebugMDF
		noMDFFound = 0
		skipPrompt = 0
		extractedNativesPath = LoadExtractedDir()
		
		#Try to find & save extracted game dir for later if extracted game dir is unknown
		if (extractedNativesPath == ""):
			dirName = GetRootGameDir()
			if (dirName.endswith("\\re_chunk_000\\natives\\stm\\")):
				SaveExtractedDir(dirName)
				extractedNativesPath = dirName
		
		pathPrefix = ((rapi.getInputName()).replace(".mesh.1902042334",""))
		materialFileName = (pathPrefix + ".mdf2.13")
		if not (rapi.checkFileExists(materialFileName)):
			materialFileName = (pathPrefix + "_mat.mdf2.13")
		if not (rapi.checkFileExists(materialFileName)):
			materialFileName = (pathPrefix + "_00.mdf2.13")
		if not (rapi.checkFileExists(materialFileName)):
			pathPrefix = extractedNativesPath + re.sub(r'.*stm\\', '', rapi.getInputName().replace('.mesh.1902042334',''))
			materialFileName = (pathPrefix + ".mdf2.13")
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = (pathPrefix + "_mat.mdf2.13")
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = (pathPrefix + "_00.mdf2.13")
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "MDF File Not Found", "Manually enter the name of the MDF file or cancel.", (rapi.getInputName()).replace(".mesh.1902042334","") + ".mdf2.13", None)
				if (materialFileName is None):
					print("No material file.")
					return
				elif not (rapi.checkFileExists(materialFileName)):
					noMDFFound = 1
				skipPrompt = 1
				msgName = materialFileName
					
		#Prompt for MDF load
		if not (skipPrompt):
			msgDefault = materialFileName
			msgName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "MDF File Detected", "Load materials? This may take some time.", msgDefault, None)
			if msgName is None:
				print("No material file.")
				return
			if msgName.endswith(" -c"):
				print (msgName)
				bColorize = 1
				bDebugMDF = 0												
				msgName = msgName.lower().replace(" -c", "")
			else:
				bColorize = 0
				bDebugMDF = 1													
			
			if ((rapi.checkFileExists(msgName)) and (msgName.endswith(".mdf2.13"))):
				materialFileName = msgName
			else:
				noMDFFound = 1
		
		if (bPopupDebug == 1):
			noesis.logPopup()
		
		#Save a manually entered natives directory path name for later
		if ((msgName.endswith("\\natives\\stm\\")) and (os.path.isdir(msgName))):
			print ("attempting to write: ")
			SaveExtractedDir(msgName)
			extractedNativesPath = msgName
				
		if (noMDFFound == 1) or not (rapi.checkFileExists(materialFileName)):
			print("Failed to open material file.")
			return
			

				
		texBaseColour = []
		texRoughColour = []
		texSpecColour = []
		texAmbiColour = []
		texMetallicColour = []
		texFresnelColour = []
			
		bs = rapi.loadIntoByteArray(materialFileName)
		bs = NoeBitStream(bs)
		#Magic, Unknown, MaterialCount, Unknown, Unknown
		matHeader = [bs.readUInt(), bs.readUShort(), bs.readUShort(), bs.readUInt(), bs.readUInt()]
		
		#Parse Materials
		materialInfo = []
		for i in range(matHeader[2]):
			#MaterialNamesOffset[0], uknBytes[1], sizeOfFloatStr[2], floatCount[3], texCount[4], Unknown[5], Unknown[6], floatHdrOffs[7], texHdrOffs[8] floatStartOffs[9], mmtr_PathOffs[10]
			if bDebugMDF:
				print("Start Offset: " + str(bs.getOffset()))
			bs.seek(0x10 + (i * 0x40), NOESEEK_ABS)
			materialInfo.append([bs.readUInt64(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64()])
			
			if bDebugMDF:
				print("End offset: " + str(bs.getOffset()))
			
			bs.seek(materialInfo[i][0], NOESEEK_ABS)
			materialName = ReadUnicodeString(bs)
			bs.seek(materialInfo[i][10], NOESEEK_ABS)
			mmtrName = ReadUnicodeString(bs)
			if bPrintFileList:
				self.texNames.append("natives/stm/" + mmtrName.lower() + ".1905100741")
			
			if bDebugMDF or 1:
				print("Material Name: [" + str(i) + "]-" + materialName)
			self.matNames.append(materialName)
			materialFlags = 0
			material = NoeMaterial(materialName, "")
			material.setDefaultBlend(0)
			#material.setBlendMode("GL_SRC_ALPHA", "GL_ONE")
			material.setAlphaTest(0)
			

		
			#Parse Textures
			textureInfo = []
			paramInfo = []
			
			bFoundBM = False
			bFoundNM = False
			bFoundHM = False
			bFoundBT = False
			bFoundSSSM = False
				
			bFoundBaseColour = False
			bFoundRoughColour = False
			bFoundSpecColour = False
			bFoundAmbiColour = False
			bFoundMetallicColour = False
			bFoundFresnelColour = False
			
			if bDebugMDF:
				print(materialInfo[i])
			
			for j in range(materialInfo[i][3]):
				bs.seek(materialInfo[i][7] + (j * 0x18), NOESEEK_ABS)
				#dscrptnOffs[0], type[1], strctOffs[2], numFloats[3] 
				paramInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt(), bs.readUInt()])
				bs.seek(paramInfo[j][0], NOESEEK_ABS)
				paramType = ReadUnicodeString(bs)
				
				bs.seek(materialInfo[i][9] + paramInfo[j][2], NOESEEK_ABS)
				colours = []
				if paramInfo[j][3] == 4:
					colours.append(NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())))
				elif paramInfo[j][3] == 1:
					colours.append(bs.readFloat())
					
				if bDebugMDF:
					print(paramType + ":")
					print(colours)
				
				if paramType == "BaseColor" and not bFoundBaseColour:
					bFoundBaseColour = True
					texBaseColour.append(colours)
				if paramType == "Roughness" and not bFoundRoughColour:
					bFoundRoughColour = True
					texRoughColour.append(colours)
				if paramType == "PrimalySpecularColor" and not bFoundSpecColour:
					bFoundSpecColour = True
					texSpecColour.append(colours)
				if paramType == "AmbientColor" and not bFoundAmbiColour:
					bFoundAmbiColour = True
					texAmbiColour.append(colours)
				if paramType == "Metallic" and not bFoundMetallicColour:
					bFoundMetallicColour = True
					texMetallicColour.append(colours)
				if paramType == "Fresnel_DiffuseIntensity" and not bFoundFresnelColour:
					bFoundFresnelColour = True
					texFresnelColour.append(colours)
			
			#Append defaults
			if not bFoundBaseColour:
				texBaseColour.append(NoeVec4((1.0, 1.0, 1.0, 1.0)))
			if not bFoundRoughColour:
				texRoughColour.append(1.0)
			if not bFoundSpecColour:
				texSpecColour.append(NoeVec4((1.0, 1.0, 1.0, 0.8)))
			if not bFoundAmbiColour:
				texAmbiColour.append(NoeVec4((1.0, 1.0, 1.0, 1.0)))
			if not bFoundMetallicColour:
				texMetallicColour.append(1.0)
			if not bFoundFresnelColour:
				texFresnelColour.append(0.8)
				
			for j in range(materialInfo[i][4]):
				bs.seek(materialInfo[i][8] + (j * 0x20), NOESEEK_ABS)
				#TextureTypeOffset[0], uknBytes[1], TexturePathOffset[2], padding[3]
				textureInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64()])
				bs.seek(textureInfo[j][0], NOESEEK_ABS)
				textureType = ReadUnicodeString(bs)
				bs.seek(textureInfo[j][2], NOESEEK_ABS)
				textureName = ReadUnicodeString(bs)
				
				if bDebugMDF:
					print("Texture Type: " + textureType + " Name: " + textureName)
				
				nativesDir = GetRootGameDir()
				textureFilePath = ""
				textureFilePath2 = ""
				if (rapi.checkFileExists(self.rootDir + "streaming/" + textureName + ".190820018")):
					textureFilePath = self.rootDir + "streaming/" + textureName + ".190820018"						
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + "streaming/" + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList:
						if (rapi.checkFileExists(self.rootDir + textureName + ".190820018")):
							self.texNames.append(("natives/stm/" + textureName + ".190820018").lower())
						else:
							self.texNames.append("DOES NOT EXIST: " + ("natives/stm/" + textureName + ".190820018").lower())
							
				elif (rapi.checkFileExists(self.rootDir + textureName + ".190820018")):
					textureFilePath = self.rootDir + textureName + ".190820018"
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + textureName).rsplit('.', 1)[0] + ".dds"
				elif (rapi.checkFileExists(extractedNativesPath + "streaming/" + textureName + ".190820018")):
					textureFilePath = extractedNativesPath + "streaming/" + textureName + ".190820018"
					textureFilePath2 = rapi.getLocalFileName(extractedNativesPath + "streaming/" + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList:
						if (rapi.checkFileExists(extractedNativesPath + textureName + ".190820018")):
							self.texNames.append(("natives/stm/" + textureName + ".190820018").lower())
						else:
							self.texNames.append("DOES NOT EXIST: " + ("natives/stm/" + textureName + ".190820018").lower())
							
				elif (rapi.checkFileExists(extractedNativesPath + textureName + ".190820018")):
					textureFilePath = extractedNativesPath + textureName + ".190820018"
					textureFilePath2 = rapi.getLocalFileName(extractedNativesPath + textureName).rsplit('.', 1)[0] + ".dds"
				else:
					textureFilePath = self.rootDir + textureName + ".190820018"
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList and not (textureFilePath.endswith("rtex.190820018")):
						self.texNames.append("DOES NOT EXIST: " + ("natives/stm/" + textureName + ".190820018").lower())
				
				bAlreadyLoadedTexture = False
				
				for k in range(len(self.texList)):
					if self.texList[k].name == textureFilePath2:
						bAlreadyLoadedTexture = True
				
				if bPrintFileList:
					if (textureName.endswith("rtex")):
						self.texNames.append(((textureFilePath.replace(str(self.rootDir),"natives/stm/")).lower()).replace(".190820018",".4"))
					else:
						self.texNames.append(((textureFilePath.replace(str(self.rootDir),"natives/stm/")).lower()))
				if bColorize:
					colors = [(0.0, 0.0, 0.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (1.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 1.0), (1.0, 0.0, 1.0, 1.0), (0.75, 0.75, 0.75, 1.0), (0.5, 0.5, 0.5, 1.0), (0.5, 0.0, 0.0, 1.0), (0.5, 0.5, 0.0, 1.0), (0.0, 0.5, 0.0, 1.0), (0.5, 0.0, 0.5, 1.0), (0.0, 0.5, 0.5, 1.0), (0.0, 0.0, 0.5, 1.0), (0.82, 0.7, 0.53, 1.0), (0.294, 0.0, 0.51, 1.0), (0.53, 0.8, 0.92, 1.0), (0.25, 0.88, 0.815, 1.0), (0.18, 0.545, 0.34, 1.0), (0.68, 1.0, 0.18, 1.0), (0.98, 0.5, 0.45, 1.0), (1.0, 0.41, 0.7, 1.0), (0.0, 0.0, 0.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (1.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 1.0), (1.0, 0.0, 1.0, 1.0), (0.75, 0.75, 0.75, 1.0), (0.5, 0.5, 0.5, 1.0), (0.5, 0.0, 0.0, 1.0), (0.5, 0.5, 0.0, 1.0), (0.0, 0.5, 0.0, 1.0), (0.5, 0.0, 0.5, 1.0), (0.0, 0.5, 0.5, 1.0), (0.0, 0.0, 0.5, 1.0), (0.82, 0.7, 0.53, 1.0), (0.294, 0.0, 0.51, 1.0), (0.53, 0.8, 0.92, 1.0), (0.25, 0.88, 0.815, 1.0), (0.18, 0.545, 0.34, 1.0), (0.68, 1.0, 0.18, 1.0), (0.98, 0.5, 0.45, 1.0), (1.0, 0.41, 0.7, 1.0)]
					colorNames = ['Black', 'White', 'Red', 'Lime', 'Blue', 'Yellow', 'Cyan', 'Magenta', 'Silver', 'Gray', 'Maroon', 'Olive', 'Green', 'Purple', 'Teal', 'Navy', 'Tan', 'Indigo', 'Sky Blue', 'Turquoise', 'Sea Green', 'Green Yellow', 'Salmon', 'Hot Pink', 'Black', 'White', 'Red', 'Lime', 'Blue', 'Yellow', 'Cyan', 'Magenta', 'Silver', 'Gray', 'Maroon', 'Olive', 'Green', 'Purple', 'Teal', 'Navy', 'Tan', 'Indigo', 'Sky Blue', 'Turquoise', 'Sea Green', 'Green Yellow', 'Salmon', 'Hot Pink']					
					
					material.setDiffuseColor(colors[i])
					if i < 10:
						myIndex = "0" + str(i)
					else:
						myIndex = str(i)
					self.texColors.append(myIndex + ": Material[" + str(i) + "] -- " + materialName + " is colored " + colorNames[i])
				else:
					if not bAlreadyLoadedTexture:
						if (textureName.endswith("rtex")):
							print("Error: Texture at path: " + str(textureFilePath).replace(".190820018",".4") + " cannot be read!")
						elif not (rapi.checkFileExists(textureFilePath)):
							print("Error: Texture at path: " + str(textureFilePath) + " does not exist!")
							self.texList.append(NoeTexture("dummy", 0, 0, 0, 0))
						else:
							textureData = rapi.loadIntoByteArray(textureFilePath)
							if texLoadDDS(textureData, self.texList) == 1:
								self.texList[len(self.texList)-1].name = textureFilePath2
							else:
								self.texList.append(NoeTexture("dummy", 0, 0, 0, 0))
					if textureType == "BaseMetalMap" or textureType == "BaseShiftMap" or "Base" in textureType and not bFoundBM:
						bFoundBM = True
						material.setTexture(textureFilePath2)
						material.setDiffuseColor(texBaseColour[i][0])
						material.setSpecularTexture(textureFilePath2)
						materialFlags |= noesis.NMATFLAG_PBR_SPEC #Not really :(
						material.setSpecularSwizzle( NoeMat44([[1, 1, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]) )
					elif textureType == "NormalRoughnessMap" and not bFoundNM:
						bFoundNM = True
						material.setNormalTexture(textureFilePath2)
						materialFlags |= noesis.NMATFLAG_PBR_ROUGHNESS_NRMALPHA
					elif textureType == "AlphaTranslucentOcclusionSSSMap" and not bFoundSSSM:
						bFoundSSSM = True
						material.setOpacityTexture(textureFilePath2)
						material.setOcclTexture(textureFilePath2)
					elif textureType == "Heat_Mask" and not bFoundHM:
						bFoundHM = True
					elif textureType == "BloodTexture" and not bFoundBT:
						bFoundBT = True
					
					if bFoundSpecColour:
						material.setSpecularColor(texSpecColour[i][0])
					if bFoundAmbiColour:
						material.setAmbientColor(texAmbiColour[i][0])
					if bFoundMetallicColour:
						material.setMetal(texMetallicColour[i][0], 0.0)
					if bFoundRoughColour:
						material.setRoughness(texRoughColour[i][0], 0.0)
					if bFoundFresnelColour:
						material.setEnvColor(NoeVec4((1.0, 1.0, 1.0, texFresnelColour[i][0])))
						
					if bDebugMDF:
						print("Type: " + textureType + " Name: " + textureName)
			material.setFlags(materialFlags)
			self.matList.append(material)
		if bPrintFileList:
			print ("\nReferenced Files:")
			textureList = sorted(list(set(self.texNames)))
			for x in range (len(textureList)):
				print (textureList[x])
			if bColorize:
				colorList = sorted(list(set(self.texColors)))
				print ("\nColor-coded Materials:")
				for g in range (len(colorList)):
					print (colorList[g])
			print ("\n")
			
	def loadMeshFile(self, mdlList):
		bs = self.inFile
		rapi.parseInstanceOptions("-fbxnewexport")
		
		magic = bs.readUInt()
		unk00 = bs.readUShort()
		unk01 = bs.readUShort()
		fileSize = bs.readUInt()
		unk02 = bs.readUInt()
		
		unk03 = bs.readUShort()
		numModels = bs.readUShort()
		unk04 = bs.readUInt()
		
		self.rootDir = GetRootGameDir()
		self.createMaterials();
		
		headerOffsets = [bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64(),bs.readUInt64()]
		
		if bDebugMESH:
			print("Header Offsets:")
			print(headerOffsets)
		
		bs.seek(headerOffsets[0], NOESEEK_ABS)
		countArray = bs.read("16B")
		
		if bDebugMESH:
			print("Count Array")
			print(countArray)
		
		#AABB Min/Max
		bs.seek(0x30, NOESEEK_REL)
		
		offsetUnk00 = bs.readUInt64()
		bs.seek(offsetUnk00)
		
		if numModels == 0:
			print("Unsupported model type")
			return
		
		offsetInfo = []
		for i in range(countArray[0]):
			offsetInfo.append(bs.readUInt64())
			
		if bDebugMESH:
			print("Vertex Info Offsets")
			print(offsetInfo)
		
		nameOffsets = []
		names = []
		nameRemapTable = []
		
		bs.seek(headerOffsets[9], NOESEEK_ABS)
		for i in range(numModels):
			nameRemapTable.append(bs.readUShort())
			
		bs.seek(headerOffsets[12], NOESEEK_ABS)
		for i in range(numModels):
			nameOffsets.append(bs.readUInt64())
			
		for i in range(numModels):
			bs.seek(nameOffsets[i], NOESEEK_ABS)
			names.append(bs.readString())
			
		if bDebugMESH:
			print("Names:")
			print(names)
			
		#Skeleton
		bs.seek(headerOffsets[3], NOESEEK_ABS)
		
		if headerOffsets[3] > 0:
			boneInfo = [bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64()]
			
			boneRemapTable = []
			for i in range(boneInfo[1]):
				boneRemapTable.append(bs.readShort())
				
			if bDebugMESH:
				print(boneRemapTable)

			boneParentInfo = []
			bs.seek(boneInfo[4], NOESEEK_ABS)
			for i in range(boneInfo[0]):
				boneParentInfo.append([bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort()])
			
			bs.seek(boneInfo[5], NOESEEK_ABS)
			for i in range(boneInfo[0]):
				mat = NoeMat44.fromBytes(bs.readBytes(0x40)).toMat43()
				self.boneList.append(NoeBone(boneParentInfo[i][0], names[countArray[1] + i], mat, None, boneParentInfo[i][1]))
			self.boneList = rapi.multiplyBones(self.boneList)
		
		meshInfo = []
		bs.seek(headerOffsets[7], NOESEEK_ABS)
		meshInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt(), bs.readUInt(), bs.readUShort(), bs.readUShort(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
		
		if bDebugMESH:
			print("Mesh Info:")
			print(meshInfo)
		
		meshVertDeclInfo = []
		positionIndex = -1
		normalIndex = -1
		uvIndex = -1
		uv2Index = -1
		weightIndex = -1

		for i in range (meshInfo[0][6]):
			meshVertDeclInfo.append([bs.readUShort(), bs.readUShort(), bs.readUInt()])
			
			if meshVertDeclInfo[i][0] == 0 and positionIndex == -1:
				positionIndex = i
			elif meshVertDeclInfo[i][0] == 1 and normalIndex == -1:
				normalIndex = i
			elif meshVertDeclInfo[i][0] == 2 and uvIndex == -1:
				uvIndex = i
			elif meshVertDeclInfo[i][0] == 3 and uv2Index == -1:
				uv2Index = i
			elif meshVertDeclInfo[i][0] == 4 and weightIndex == -1:
				weightIndex = i
		
		if bDebugMESH:
			print("Vert Decl info:")
			print(meshVertDeclInfo)
			
		bs.seek(meshInfo[0][1], NOESEEK_ABS)		
		vertexBuffer = bs.readBytes(meshInfo[0][3])
		
		for i in range(countArray[0]):
			meshVertexInfo = []
			ctx = rapi.rpgCreateContext()
			bs.seek(offsetInfo[i], NOESEEK_ABS)
			
			numOffsets = bs.readUInt()
			hash = bs.readUInt()
			offsetSubOffsets = bs.readUInt64()
			bs.seek(offsetSubOffsets, NOESEEK_ABS)
			
			offsetInfo2 = []
			for j in range(numOffsets):
				offsetInfo2.append(bs.readUInt64())
			
			if bDebugMESH:
				print("Offset info 2")
				print(offsetInfo2)
			
			for j in range(numOffsets):
				bs.seek(offsetInfo2[j], NOESEEK_ABS)
				meshVertexInfo.append([bs.readUByte(), bs.readUByte(), bs.readUShort(), bs.readUInt(), bs.readUInt(), bs.readUInt()])

				if bDebugMESH:
					print("Mesh vertex info:")
					print(meshVertexInfo)
				
				if bDebugMESH:
					print(meshVertexInfo[j])
					
				indexBufferSplitData = []
				for k in range(meshVertexInfo[j][1]):
					indexBufferSplitData.append([bs.readUByte(), bs.readUByte(), bs.readUByte(), bs.readUByte(), bs.readUInt(), bs.readUInt(), bs.readUInt()])#Index, faceCount, indexBufferStartIndex, vertexStartIndex
				
				for k in range(meshVertexInfo[j][1]):
					#Search for material
					for l in range(len(self.matNames)):
						if self.matNames[l] == names[nameRemapTable[indexBufferSplitData[k][0]]]:
							rapi.rpgSetMaterial(self.matNames[l])
							break
							
					rapi.rpgSetName("Model_" + str(i) + "_Mesh_" + str(j) + "_" + str(k))
					rapi.rpgSetPosScaleBias((fDefaultMeshScale, fDefaultMeshScale, fDefaultMeshScale), (0, 0, 0))

					if positionIndex != -1:
						rapi.rpgBindPositionBufferOfs(vertexBuffer, noesis.RPGEODATA_FLOAT, meshVertDeclInfo[positionIndex][1], (meshVertDeclInfo[positionIndex][1] * indexBufferSplitData[k][6]))
					
					if normalIndex != -1 and bNORMsEnabled:
						if bDebugNormals:
							rapi.rpgBindColorBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, meshVertDeclInfo[normalIndex][1], meshVertDeclInfo[normalIndex][2] + (meshVertDeclInfo[normalIndex][1] * indexBufferSplitData[k][6]), 4)
						else:
							rapi.rpgBindNormalBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, meshVertDeclInfo[normalIndex][1], meshVertDeclInfo[normalIndex][2] + (meshVertDeclInfo[normalIndex][1] * indexBufferSplitData[k][6]))
						
					if uvIndex != -1 and bUVsEnabled:
						rapi.rpgBindUV1BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, meshVertDeclInfo[uvIndex][1], meshVertDeclInfo[uvIndex][2] + (meshVertDeclInfo[uvIndex][1] * indexBufferSplitData[k][6]))
					if uv2Index != -1 and bUVsEnabled:
						rapi.rpgBindUV2BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, meshVertDeclInfo[uv2Index][1], meshVertDeclInfo[uv2Index][2] + (meshVertDeclInfo[uv2Index][1] * indexBufferSplitData[k][6]))
						
					if weightIndex != -1 and bSkinningEnabled:
						rapi.rpgSetBoneMap(boneRemapTable)
						rapi.rpgBindBoneIndexBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, meshVertDeclInfo[weightIndex][1], meshVertDeclInfo[weightIndex][2] + (meshVertDeclInfo[weightIndex][1] * indexBufferSplitData[k][6]), 8)
						rapi.rpgBindBoneWeightBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, meshVertDeclInfo[weightIndex][1], meshVertDeclInfo[weightIndex][2] + (meshVertDeclInfo[weightIndex][1] * indexBufferSplitData[k][6]) + 8, 8)
					
					if indexBufferSplitData[k][4] > 0:
						bs.seek(meshInfo[0][2] + (indexBufferSplitData[k][5] * 2), NOESEEK_ABS)
						if bDebugMESH:
							print("Index Buffer Start: " + str(bs.tell()))
						indexBuffer = bs.readBytes(indexBufferSplitData[k][4] * 2)
						if bDebugMESH:
							print("Index Buffer End: " + str(bs.tell()))
						
						if bRenderAsPoints:
							rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, (meshVertexInfo[j][4] - (indexBufferSplitData[k][6] - vertexStartIndex)), noesis.RPGEO_POINTS, 0x1)
						else:
							rapi.rpgSetStripEnder(0x10000)
							rapi.rpgCommitTriangles(indexBuffer, noesis.RPGEODATA_USHORT, indexBufferSplitData[k][4], noesis.RPGEO_TRIANGLE, 0x1)
							rapi.rpgClearBufferBinds()
			try:
				mdl = rapi.rpgConstructModelSlim()
			except:
				mdl = NoeModel()
			mdl.setBones(self.boneList)
			mdl.setModelMaterials(NoeModelMaterials(self.texList, self.matList))
			mdlList.append(mdl)
		return mdlList
				
def meshLoadModel(data, mdlList):
	mesh = meshFile(data)
	mdlList = mesh.loadMeshFile(mdlList)
	#mesh.buildSkeleton()
	return 1