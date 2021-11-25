#RE Engine [PC] - ".mesh" plugin
#v2.4
#By alphaZomega and Gh0stblade 
#Special thanks: Chrrox

#Options: These are options that change or enable/disable certain features! They are global and affect ALL platforms!
#		Var										Effect
#Export Extensions
fExportExtension = ".1902042334"		#You can set the default MESH extension here (.1902042334 for RE3, .1808312334 for RE2, .1808282334 for DMC5)
bRE2texExport = True					#Enable or disable export of tex.10 from the export list			
bRE3texExport = True					#Enable or disable export of tex.190820018 from the export list
bDMCtexExport = True					#Enable or disable export of tex.11 from the export list
bRE7texExport = True					#Enable or disable export of tex.8 from the export list

#Mesh Global
fDefaultMeshScale = 100.0 				#Override mesh scale (default is 1.0)
bMaterialsEnabled = 1					#Materials (1 = on, 0 = off)
bRenderAsPoints = 0						#Render mesh as points without triangles drawn (1 = on, 0 = off)

#Vertex Components (Import)
bNORMsEnabled = 1						#Normals (1 = on, 0 = off)
bTANGsEnabled = 1						#Tangents (1 = on, 0 = off)
bUVsEnabled = 1							#UVs (1 = on, 0 = off))
bSkinningEnabled = 1					#Enable skin weights (1 = on, 0 = off)
bDebugNormals = 0						#Debug normals as RGBA
bDebugTangents = 0						#Debug tangents as RGBA

#Import Options
bDebugMDF = 0							#Prints debug info for MDF files (1 = on, 0 = off)
bDebugMESH = 0							#Prints debug info for MESH files (1 = on, 0 = off)
bPopupDebug = 1							#Pops up debug window on opening MESH with MDF (1 = on, 0 = off)
bPrintFileList = 1						#Prints a list of files used by the MDF
bColorize = 0							#Colors the materials of the model and lists which material is which color
bAddBoneNumbers = 0						#Adds bone numbers like the MaxScript
bUseOldNamingScheme = 0					#Names submeshes by their material ID (like in the MaxScript) rather than by their order in the file 

#Export Options
bNormalizeWeights = 1					#Makes sure that the weights of every vertex add up to 1.0, giving the remainder to the bone with the least influence

from inc_noesis import *
import math
import os
import re
import copy

def registerNoesisTypes():
	handle = noesis.register("RE Engine MESH [PC]", ".1902042334;.1808312334;.1808282334;.NewMesh")
	noesis.setHandlerTypeCheck(handle, meshCheckType)
	noesis.setHandlerLoadModel(handle, meshLoadModel)
	
	handle = noesis.register("RE Engine Texture [PC]", ".10;.190820018;.11;.8")
	noesis.setHandlerTypeCheck(handle, texCheckType)
	noesis.setHandlerLoadRGBA(handle, texLoadDDS)

	if bRE2texExport:
		handle = noesis.register("RE2 Remake Texture [PC]", ".10")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
	if bRE3texExport:
		handle = noesis.register("RE3 Remake Texture [PC]", ".190820018")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
	if bDMCtexExport:
		handle = noesis.register("Devil May Cry 5 Texture [PC]", ".11")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
	if bRE7texExport:
		handle = noesis.register("Resident Evil 7 Texture [PC]", ".8")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)

	handle = noesis.register("RE3 MESH", (".mesh.1902042334"))
	noesis.setHandlerTypeCheck(handle, meshCheckType)
	noesis.setHandlerWriteModel(handle, meshWriteModel)
	
	handle = noesis.register("RE2 MESH", (".mesh.1808312334"))
	noesis.setHandlerTypeCheck(handle, meshCheckType)
	noesis.setHandlerWriteModel(handle, meshWriteModel)
	
	handle = noesis.register("DMC5 MESH", (".mesh.1808282334"))
	noesis.setHandlerTypeCheck(handle, meshCheckType)
	noesis.setHandlerWriteModel(handle, meshWriteModel)
	
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
	
def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c
	
def dot(v1, v2):
	return sum(x*y for x,y in zip(v1,v2))
	
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
	
	mipData = []
	mipDataAll = []
	for i in range(numImages):
		for j in range(mipCount):
			mipData.append([bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
		mipDataAll.append(mipData[i])
		
	bs.seek(mipDataAll[0][0], NOESEEK_ABS)
	texData = bs.readBytes(mipDataAll[0][3])
	
	texFormat = None
	#if bDebugMDF:
	print(format)
	if format == 28:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_ATI1)
	elif format == 29:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC1)
	elif format == 71: #ATOS
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
		#ddsData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
		#texData = rapi.imageEncodeRaw(ddsData, width, height, "r8r8r8r8")
		#texData = rapi.imageDecodeRaw(texData, width, height, "b8g8r8a8")
	elif format == 72:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
	elif format == 80: #BC4 wetmasks
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4)
	elif format == 83: #BC5
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC5)
	elif format == 95:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC6H)
	elif format == 98:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
	elif format == 99:
		texFormat = noesis.NOESISTEX_RGBA32
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
	else:
		print("Fatal Error: Unsupported texture type: " + str(format))
		return 0
		

		
		
	if texFormat != None:
		texList.append(NoeTexture(rapi.getInputName(), int(width), int(height), texData, texFormat))
	return 1
	
def texWriteRGBA(data, width, height, bs):
	bTexAsSource = False
	print ("\n			----RE Engine TEX Export----\n")
	def getExportName(fileName):		
		if fileName == None:
			newTexName = rapi.getInputName()
		else:
			newTexName = fileName
		newTexName =  newTexName.lower().replace(".texout","").replace(".tex","").replace(".dds","").replace(".out","").replace(".10","").replace(".190820018","").replace(".11","").replace(".8","") \
		.replace(".jpg","").replace(".png","").replace(".tga","").replace(".gif","").replace(".8","")
		ext = ".tex.10"
		if rapi.checkFileExists(newTexName + ".tex.190820018"):
			ext = ".tex.190820018"
		elif rapi.checkFileExists(newTexName + ".tex.11"):
			ext = ".tex.11"
		elif rapi.checkFileExists(newTexName + ".tex.8"):
			ext = ".tex.8"
		newTexName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Export over tex", "Choose a tex file to export over", newTexName + ext, None)
		if newTexName == None:
			print("Aborting...")
			return
		return newTexName
		
	fileName = None
	newTexName = getExportName(fileName)
	if newTexName == None:
		return 0
	while not (rapi.checkFileExists(newTexName)):
		print ("File not found")
		newTexName = getExportName(fileName)	
		fileName = newTexName
		if newTexName == None:
			return 0	
			
	newTEX = rapi.loadIntoByteArray(newTexName)
	oldDDS = rapi.loadIntoByteArray(rapi.getInputName())
	f = NoeBitStream(newTEX)
	og = NoeBitStream(oldDDS)

	magic = f.readUInt()
	ddsMagic = og.readUInt()
	bDoEncode = False
	if magic != 5784916:
		print ("Selected file is not a TEX file!\nAborting...")
		return 0
		
	f.seek(16, NOESEEK_ABS)
	imgType = f.readUInt()
	print ("TEX type:", imgType)
	
	ddsFmt = 0
	bQuitIfEncode = False
	try:
		if imgType == 28 or imgType == 29 or imgType == 71 or imgType == 72: ddsFmt = noesis.NOE_ENCODEDXT_BC1
		elif imgType == 80: ddsFmt = noesis.NOE_ENCODEDXT_BC4
		elif imgType == 83: ddsFmt = noesis.NOE_ENCODEDXT_BC5
		elif imgType == 95: ddsFmt = noesis.NOE_ENCODEDXT_BC6H
		elif imgType == 98 or imgType == 99: ddsFmt = noesis.NOE_ENCODEDXT_BC7
		else: 
			print ("Unknown TEX type:", imgType)
			return 0
	except: 
		bQuitIfEncode = True

	print ("Exporting over \"" + rapi.getLocalFileName(newTexName)+ "\"")
	
	texFmt = ddsFmt
	#headerSize = 0
	if ddsMagic == 542327876: #DDS
		headerSize = og.readUInt() + 4
		og.seek(84, NOESEEK_ABS)
		if og.readUInt() == 808540228: #DX10
			headerSize += 20
			if ddsFmt == noesis.NOE_ENCODEDXT_BC1:
				print ("Source DDS encoding (BC7) does not match TEX file (BC1)!\nEncoding image...")
				bDoEncode = True
		elif ddsFmt == noesis.NOE_ENCODEDXT_BC7:
			print ("Source DDS encoding (BC1) does not match TEX file (BC7)!\nEncoding image")
			bDoEncode = True
	elif ddsMagic == 5784916: #TEX
		bTexAsSource = True
		og.seek(14, NOESEEK_ABS)
		headerSize = og.readUByte() * 16 + 32
		og.seek(16, NOESEEK_ABS)
		srcType = og.readUInt()
		if srcType == 28 or srcType == 29 or srcType == 71 or srcType == 72: texFmt = noesis.NOE_ENCODEDXT_BC1
		elif srcType == 80: texFmt = noesis.NOE_ENCODEDXT_BC4
		elif srcType == 83: ddsFmt = noesis.NOE_ENCODEDXT_BC5
		elif srcType == 95: texFmt = noesis.NOE_ENCODEDXT_BC6H
		elif srcType == 98 or srcType == 99: texFmt = noesis.NOE_ENCODEDXT_BC7
		else: 
			print ("Unknown TEX type:", srcType)
			return 0
		if texFmt != ddsFmt: 
			print ("Input TEX file uses a different compression from Source TEX file!\nEncoding image...")
			bDoEncode = True
	else: 
		print ("Input file is not a DDS or TEX file\nEncoding image...")
		bDoEncode = True
	
	mipSize = width * height
	if texFmt == noesis.NOE_ENCODEDXT_BC1: mipSize = int(mipSize / 2)
	if not bDoEncode and mipSize < int((os.path.getsize(rapi.getInputName())) / 4):
		print ("Unexpected source image size\nEncoding...")
		bDoEncode = True
	
	if not bDoEncode: 
		print ("Copying image data from \"" + rapi.getLocalFileName(rapi.getInputName()) + "\"")
	elif bQuitIfEncode:
		print ("Fatal Error: BC7 Encoding not supported!\nUpdate to Noesis v4434 (Oct 14, 2020) or later to encode BC7 images\nAborting...\n")
		return 0
		
	#copy header
	f.seek(0, NOESEEK_ABS)
	bs.writeBytes(f.readBytes(32))
	
	numMips = 0
	dataSize = 0
	sizeArray = []
	fileData = []
	mipWidth = width
	mipHeight = height
	
	#write mipmap headers & encode image
	while mipWidth > 4 or mipHeight > 4:
		numMips += 1
		
		mipData = rapi.imageResample(data, width, height, mipWidth, mipHeight)
		if bDoEncode:
			dxtData = rapi.imageEncodeDXT(mipData, 4, mipWidth, mipHeight, ddsFmt)
			fileData.append(dxtData)
			mipSize = len(dxtData)
		else:
			mipSize = mipWidth * mipHeight
			if texFmt == noesis.NOE_ENCODEDXT_BC1:
				mipSize = int(mipSize / 2)
			
		sizeArray.append(dataSize)
		dataSize += mipSize
		bs.writeUInt64(0)
		pitch = 4 * mipWidth
		if ddsFmt == noesis.NOE_ENCODEDXT_BC1:
			pitch = int(pitch / 2)
		bs.writeUInt(pitch)
		bs.writeUInt(mipSize)
		#if bDoEncode: print ("Mip", numMips, ": ", mipWidth, "x", mipHeight, "\n            ", pitch, "\n            ", mipSize)
		if mipWidth > 4: mipWidth = int(mipWidth / 2)
		if mipHeight > 4: mipHeight = int(mipHeight / 2)
	
	if bDoEncode: 
		for d in range(len(fileData)): #write image data
			bs.writeBytes(fileData[d])
	else:
		og.seek(headerSize, NOESEEK_ABS) #copy image data
		bs.writeBytes(og.readBytes(os.path.getsize(rapi.getInputName()) - headerSize))

	#adjust header
	bs.seek(8, NOESEEK_ABS)
	bs.writeUShort(width)
	bs.writeUShort(height)
	bs.seek(14, NOESEEK_ABS)
	bs.writeUByte(numMips)
	bsHeaderSize = numMips * 16 + 32
	bs.seek(32, NOESEEK_ABS)
	for mip in range(numMips):
		bs.writeUInt64(sizeArray[mip] + bsHeaderSize)
		bs.seek(8, NOESEEK_REL)	

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
		if lastFolderName == "stm" or lastFolderName == "x64":
			break
		else:
			path = os.path.normpath(os.path.join(path, ".."))
	return path	+ "\\"
	
def LoadExtractedDir():
	nativesPath = ""
	try: 
		with open(noesis.getPluginsPath() + '\python\\' + fGameName + 'NativesPath.txt') as fin:
			nativesPath = fin.read()
			fin.close()
	except IOError:
		return ""
	return nativesPath
		
def SaveExtractedDir(dirIn):
	try: 
		print (noesis.getPluginsPath() + 'python\\' + fGameName + 'NativesPath.txt')
		with open(noesis.getPluginsPath() + 'python\\' + fGameName + 'NativesPath.txt') as fout:
			print ("Writing string: " + dirIn + " to " + str(fout))
			fout.flush()
			fout.write(str(dirIn))
			fout.close()
	except IOError:
		print ("Failed to save natives path: IO Error")
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
		global bColorize, bDebugMDF, fGameName, fExportExtension
		noMDFFound = 0
		skipPrompt = 0
		
		nDir = "x64"
		mdfExt = ".mdf2.10"
		fGameName = "RE2"
		modelExt= ".1808312334" 
		texExt = ".10"
		mmtrExt = ".1808160001"
		
		if rapi.getInputName().find(".1808282334") != -1:
			fGameName = "DMC5"
			modelExt = ".1808282334"
			texExt = ".11"
			mmtrExt = ".1808168797"
		elif rapi.getInputName().find(".1902042334") != -1:
			fGameName = "RE3"
			modelExt = ".1902042334"
			texExt = ".190820018"
			mmtrExt = ".1905100741"
			nDir = "stm"
			mdfExt = ".mdf2.13"		
		print (fGameName)
		fExportExtension = modelExt
		
		extractedNativesPath = LoadExtractedDir()
		
		#Try to find & save extracted game dir for later if extracted game dir is unknown
		if (extractedNativesPath == ""):
			dirName = GetRootGameDir()
			if (dirName.endswith("chunk_000\\natives\\" + nDir + "\\")):
				print ("Saving natives path...")
				SaveExtractedDir(dirName)
				extractedNativesPath = dirName
		
		pathPrefix = ((rapi.getInputName()).replace(".mesh" + modelExt,""))
		materialFileName = (pathPrefix + mdfExt)
		if not (rapi.checkFileExists(materialFileName)):
			materialFileName = (pathPrefix + "_mat" + mdfExt)
		if not (rapi.checkFileExists(materialFileName)):
			materialFileName = (pathPrefix + "_00" + mdfExt)
		if not (rapi.checkFileExists(materialFileName)):
			if fGameName == "RE3":
				pathPrefix = extractedNativesPath + re.sub(r'.*stm\\', '', rapi.getInputName().replace(".mesh" + modelExt,''))
			else:
				pathPrefix = extractedNativesPath + re.sub(r'.*x64\\', '', rapi.getInputName().replace(".mesh" + modelExt,''))
			materialFileName = (pathPrefix + mdfExt)
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = (pathPrefix + "_mat" + mdfExt)
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = (pathPrefix + "_00" + mdfExt)
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "MDF File Not Found", "Manually enter the name of the MDF file or cancel.", (rapi.getInputName()).replace(".mesh" + modelExt,"") + mdfExt, None)
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
			
			if ((rapi.checkFileExists(msgName)) and (msgName.endswith(mdfExt))):
				materialFileName = msgName
			else:
				noMDFFound = 1
		
		if (bPopupDebug == 1):
			noesis.logPopup()
		
		#Save a manually entered natives directory path name for later
		if ((msgName.endswith("\\natives\\" + nDir + "\\")) and (os.path.isdir(msgName))):
			print ("Attempting to write: ")
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
			bs.seek(0x10 + (i * 0x40), NOESEEK_ABS)
			materialInfo.append([bs.readUInt64(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64()])			
			bs.seek(materialInfo[i][0], NOESEEK_ABS)
			materialName = ReadUnicodeString(bs)
			bs.seek(materialInfo[i][10], NOESEEK_ABS)
			mmtrName = ReadUnicodeString(bs)
			if bPrintFileList:
				self.texNames.append(("natives/" + nDir + "/" + mmtrName + mmtrExt).lower())
			
			if bDebugMDF or 1:
				print("Material Name: [" + str(i) + "]-" + materialName)
			self.matNames.append(materialName)
			materialFlags = 0
			materialFlags2 = 0
			material = NoeMaterial(materialName, "")
			material.setDefaultBlend(0)
			#material.setBlendMode("GL_ONE", "GL_ONE")
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
			
			for j in range(materialInfo[i][3]): # floats
				bs.seek(materialInfo[i][7] + (j * 0x18), NOESEEK_ABS)
				#dscrptnOffs[0], type[1], strctOffs[2], numFloats[3] 
				paramInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt(), bs.readUInt()])
				bs.seek(paramInfo[j][0], NOESEEK_ABS)
				paramType = ReadUnicodeString(bs)
				
				colours = []
				if fGameName == "RE3":
					bs.seek(materialInfo[i][9] + paramInfo[j][2], NOESEEK_ABS)
					if paramInfo[j][3] == 4:
						colours.append(NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())))
					elif paramInfo[j][3] == 1:
						colours.append(bs.readFloat())
				else:
					bs.seek(materialInfo[i][9] + paramInfo[j][3], NOESEEK_ABS)
					if paramInfo[j][2] == 4:
						colours.append(NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())))
					elif paramInfo[j][2] == 1:
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
				
			for j in range(materialInfo[i][4]): # texture headers
				#TextureTypeOffset[0], uknBytes[1], TexturePathOffset[2], padding[3]
				if fGameName == "RE3":
					bs.seek(materialInfo[i][8] + (j * 0x20), NOESEEK_ABS)
					textureInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64()])
				else:
					bs.seek(materialInfo[i][8] + (j * 0x18), NOESEEK_ABS)
					textureInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt64()])
				bs.seek(textureInfo[j][0], NOESEEK_ABS)
				textureType = ReadUnicodeString(bs)
				bs.seek(textureInfo[j][2], NOESEEK_ABS)
				textureName = ReadUnicodeString(bs)
				
				#if bDebugMDF:
				#	print("Texture Type: " + textureType + " Name: " + textureName)
				
				textureFilePath = ""
				textureFilePath2 = ""
				if (rapi.checkFileExists(self.rootDir + "streaming/" + textureName + texExt)):
					textureFilePath = self.rootDir + "streaming/" + textureName + texExt						
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + "streaming/" + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList and not (rapi.checkFileExists(self.rootDir + textureName + texExt)):
						self.texNames.append(("DOES NOT EXIST: " + ('natives/' + (re.sub(r'.*natives\\', '', textureFilePath)).lower()).replace("\\","/")).replace(extractedNativesPath,''))
							
				elif (rapi.checkFileExists(self.rootDir + textureName + texExt)):
					textureFilePath = self.rootDir + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + textureName).rsplit('.', 1)[0] + ".dds"
				elif (rapi.checkFileExists(extractedNativesPath + "streaming/" + textureName + texExt)):
					textureFilePath = extractedNativesPath + "streaming/" + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(extractedNativesPath + "streaming/" + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList and not (rapi.checkFileExists(extractedNativesPath + textureName + texExt)):
						self.texNames.append(("DOES NOT EXIST: " + ('natives/' + (re.sub(r'.*natives\\', '', textureFilePath)).lower()).replace("\\","/")).replace(extractedNativesPath,''))
							
				elif (rapi.checkFileExists(extractedNativesPath + textureName + texExt)):
					textureFilePath = extractedNativesPath + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(extractedNativesPath + textureName).rsplit('.', 1)[0] + ".dds"
				else:
					textureFilePath = self.rootDir + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList and not (textureFilePath.endswith("rtex" + texExt)):
						self.texNames.append("DOES NOT EXIST: " + ('natives/' + (re.sub(r'.*natives\\', '', textureFilePath)).lower()).replace("\\","/"))
				
				bAlreadyLoadedTexture = False
				
				for k in range(len(self.texList)):
					if self.texList[k].name == textureFilePath2:
						bAlreadyLoadedTexture = True
				
				if bPrintFileList:
					if (textureName.endswith("rtex")):
						self.texNames.append((((('natives/' + (re.sub(r'.*natives\\', '', textureFilePath))).replace("\\","/")).replace(texExt,".4")).replace(extractedNativesPath,'')).lower())
					else:
						newTexPath = ((('natives/' + (re.sub(r'.*natives\\', '', textureFilePath))).replace("\\","/")).replace(extractedNativesPath,'')).lower()
						self.texNames.append(newTexPath)
						if newTexPath.find('streaming') != -1:
							testPath = newTexPath.replace('natives/' + nDir + '/streaming/', '')
							if rapi.checkFileExists(self.rootDir + testPath) or rapi.checkFileExists(extractedNativesPath + testPath):
								self.texNames.append(newTexPath.replace('streaming/',''))
								
				if bColorize:
					colors = [(0.0, 0.0, 0.0, 1.0), 	(1.0, 1.0, 1.0, 1.0), 	  (1.0, 0.0, 0.0, 1.0),	  	(0.0, 1.0, 0.0, 1.0), 		(0.0, 0.0, 1.0, 1.0), 	 (1.0, 1.0, 0.0, 1.0), 		(0.0, 1.0, 1.0, 1.0),\
							  (1.0, 0.0, 1.0, 1.0), 	(0.75, 0.75, 0.75, 1.0),  (0.5, 0.5, 0.5, 1.0),	  	(0.5, 0.0, 0.0, 1.0), 		(0.5, 0.5, 0.0, 1.0), 	 (0.0, 0.5, 0.0, 1.0), 		(0.5, 0.0, 0.5, 1.0),\
							  (0.0, 0.5, 0.5, 1.0), 	(0.0, 0.0, 0.5, 1.0), 	  (0.82, 0.7, 0.53, 1.0), 	(0.294, 0.0, 0.51, 1.0), 	(0.53, 0.8, 0.92, 1.0),  (0.25, 0.88, 0.815, 1.0),  (0.18, 0.545, 0.34, 1.0),\
							  (0.68, 1.0, 0.18, 1.0), 	(0.98, 0.5, 0.45, 1.0),   (1.0, 0.41, 0.7, 1.0),  	(0.0, 0.0, 0.0, 1.0), 		(1.0, 1.0, 1.0, 1.0), 	 (1.0, 0.0, 0.0, 1.0), 		(0.0, 1.0, 0.0, 1.0),\
							  (0.0, 0.0, 1.0, 1.0), 	(1.0, 1.0, 0.0, 1.0), 	  (0.0, 1.0, 1.0, 1.0),	  	(1.0, 0.0, 1.0, 1.0), 	 	(0.75, 0.75, 0.75, 1.0), (0.5, 0.5, 0.5, 1.0), 	 	(0.5, 0.0, 0.0, 1.0),\
							  (0.5, 0.5, 0.0, 1.0), 	(0.0, 0.5, 0.0, 1.0),	  (0.5, 0.0, 0.5, 1.0),	  	(0.0, 0.5, 0.5, 1.0), 		(0.0, 0.0, 0.5, 1.0), 	 (0.82, 0.7, 0.53, 1.0), 	(0.294, 0.0, 0.51, 1.0),\
							  (0.53, 0.8, 0.92, 1.0), 	(0.25, 0.88, 0.815, 1.0), (0.18, 0.545, 0.34, 1.0), (0.68, 1.0, 0.18, 1.0), 	(0.98, 0.5, 0.45, 1.0),  (1.0, 0.41, 0.7, 1.0)]
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
							print(str(textureFilePath).replace(texExt,".4") + " cannot be read!")
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
						#material.setNextPass(textureFilePath2)
						material.setOcclTexture(textureFilePath2) 
						#matArray.append(textureFilePath2)
						materialFlags2 |= noesis.NMATFLAG2_OPACITY_UV1 | noesis.NMATFLAG2_OCCL_UV1 | noesis.NMATFLAG2_OCCL_BLUE
						#material.setAlphaTest(0.5)
						
					elif textureType == "Heat_Mask" and not bFoundHM:
						bFoundHM = True
					elif textureType == "BloodTexture" and not bFoundBT:
						bFoundBT = True
					
					if bFoundSpecColour:
						material.setSpecularColor(texSpecColour[i][0])
					if bFoundAmbiColour:
						material.setAmbientColor(texAmbiColour[i][0])
					if bFoundMetallicColour:
						material.setMetal(texMetallicColour[i][0], 0.25)
					if bFoundRoughColour:
						material.setRoughness(texRoughColour[i][0], 0.25)
					if bFoundFresnelColour:
						material.setEnvColor(NoeVec4((1.0, 1.0, 1.0, texFresnelColour[i][0])))
						
					if bDebugMDF:
						print(textureType + " -- " + textureName)
			material.setFlags(materialFlags)
			material.setFlags2(materialFlags2)
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
		
		magic = bs.readUInt()
		unk00 = bs.readUShort()
		unk01 = bs.readUShort()
		fileSize = bs.readUInt()
		unk02 = bs.readUInt()
		
		unk03 = bs.readUShort()
		numModels = bs.readUShort()
		unk04 = bs.readUInt()
		
		self.rootDir = GetRootGameDir()
		if not (rapi.noesisIsExporting()):
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
			
			trans = NoeVec3((100.0, 100.0, 100.0))
			bs.seek(boneInfo[5], NOESEEK_ABS)
			for i in range(boneInfo[0]):
				mat = NoeMat44.fromBytes(bs.readBytes(0x40)).toMat43()
				mat[3] *= trans
				boneName = names[countArray[1] + i]
				if bAddBoneNumbers:
					for j in range(len(boneRemapTable)):
						if boneParentInfo[i][0] == boneRemapTable[j]:
							if j<9:
								boneName = "b00" + str(j+1) + ":" + boneName
							elif j>8 and j<99:
								boneName = "b0" + str(j+1) + ":" + boneName
							elif j>98 and j<999:
								boneName = "b" + str(j+1) + ":" + boneName	
							break
				self.boneList.append(NoeBone(boneParentInfo[i][0], boneName, mat, None, boneParentInfo[i][1]))
			self.boneList = rapi.multiplyBones(self.boneList)
		
		meshInfo = []
		bs.seek(headerOffsets[7], NOESEEK_ABS)
		meshInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt(), bs.readUInt(), bs.readUShort(), bs.readUShort(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
		
		if bDebugMESH:
			print("Mesh Info:")
			print(meshInfo)
		
		vertElemHeaders = []
		positionIndex = -1
		normalIndex = -1
		uvIndex = -1
		uv2Index = -1
		weightIndex = -1

		for i in range (meshInfo[0][6]):
			vertElemHeaders.append([bs.readUShort(), bs.readUShort(), bs.readUInt()])
			
			if vertElemHeaders[i][0] == 0 and positionIndex == -1:
				positionIndex = i
			elif vertElemHeaders[i][0] == 1 and normalIndex == -1:
				normalIndex = i
			elif vertElemHeaders[i][0] == 2 and uvIndex == -1:
				uvIndex = i
			elif vertElemHeaders[i][0] == 3 and uv2Index == -1:
				uv2Index = i
			elif vertElemHeaders[i][0] == 4 and weightIndex == -1:
				weightIndex = i
		vertexStartIndex = bs.tell()
			
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
			
			for j in range(numOffsets):
				bs.seek(offsetInfo2[j], NOESEEK_ABS)
				meshVertexInfo.append([bs.readUByte(), bs.readUByte(), bs.readUShort(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
					
				submeshData = []
				for k in range(meshVertexInfo[j][1]):
					submeshData.append([bs.readUByte(), bs.readUByte(), bs.readUByte(), bs.readUByte(), bs.readUInt(), bs.readUInt(), bs.readUInt()])#Index, faceCount, indexBufferStartIndex, vertexStartIndex
				
				for k in range(meshVertexInfo[j][1]):
					rapi.rpgSetMaterial("")
					
					#Search for material
					if i == 0:
						for l in range(len(self.matNames)):
							if self.matNames[l] == names[nameRemapTable[submeshData[k][0]]]:
								rapi.rpgSetMaterial(self.matNames[l])
								#rapi.rpgSetLightmap(matArray[k].replace(".dds".lower(), ""))
								break
							
					if bUseOldNamingScheme:
						rapi.rpgSetName("LODGroup_" + str(i+1) + "_MainMesh_" + str(j+1) + "_SubMesh_" + str(submeshData[k][0]+1))
					else:
						rapi.rpgSetName("LODGroup_" + str(i+1) + "_MainMesh_" + str(j+1) + "_SubMesh_" + str(k+1))
					rapi.rpgSetPosScaleBias((fDefaultMeshScale, fDefaultMeshScale, fDefaultMeshScale), (0, 0, 0))
					
					if positionIndex != -1:
						rapi.rpgBindPositionBufferOfs(vertexBuffer, noesis.RPGEODATA_FLOAT, vertElemHeaders[positionIndex][1], (vertElemHeaders[positionIndex][1] * submeshData[k][6]))
					
					if normalIndex != -1 and bNORMsEnabled:
						if bDebugNormals:
							rapi.rpgBindColorBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, vertElemHeaders[normalIndex][1], vertElemHeaders[normalIndex][2] + (vertElemHeaders[normalIndex][1] * submeshData[k][6]), 4)
						else:
							rapi.rpgBindNormalBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, vertElemHeaders[normalIndex][1], vertElemHeaders[normalIndex][2] + (vertElemHeaders[normalIndex][1] * submeshData[k][6]))
							if bTANGsEnabled:
								rapi.rpgBindTangentBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, vertElemHeaders[normalIndex][1], 4 + vertElemHeaders[normalIndex][2] + (vertElemHeaders[normalIndex][1] * submeshData[k][6]))
					
					if uvIndex != -1 and bUVsEnabled:
						rapi.rpgBindUV1BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, vertElemHeaders[uvIndex][1], vertElemHeaders[uvIndex][2] + (vertElemHeaders[uvIndex][1] * submeshData[k][6]))
					if uv2Index != -1 and bUVsEnabled:
						rapi.rpgBindUV2BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, vertElemHeaders[uv2Index][1], vertElemHeaders[uv2Index][2] + (vertElemHeaders[uv2Index][1] * submeshData[k][6]))
						
					if weightIndex != -1 and bSkinningEnabled:
						rapi.rpgSetBoneMap(boneRemapTable)
						rapi.rpgBindBoneIndexBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, vertElemHeaders[weightIndex][1], vertElemHeaders[weightIndex][2] + (vertElemHeaders[weightIndex][1] * submeshData[k][6]), 8)
						rapi.rpgBindBoneWeightBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, vertElemHeaders[weightIndex][1], vertElemHeaders[weightIndex][2] + (vertElemHeaders[weightIndex][1] * submeshData[k][6]) + 8, 8)
						
					if submeshData[k][4] > 0:
						bs.seek(meshInfo[0][2] + (submeshData[k][5] * 2), NOESEEK_ABS)
						indexBuffer = bs.readBytes(submeshData[k][4] * 2)
						if bRenderAsPoints:
							rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, (meshVertexInfo[j][4] - (submeshData[k][6])), noesis.RPGEO_POINTS, 0x1)
						else:
							rapi.rpgSetStripEnder(0x10000)
							rapi.rpgCommitTriangles(indexBuffer, noesis.RPGEODATA_USHORT, submeshData[k][4], noesis.RPGEO_TRIANGLE, 0x1)
							rapi.rpgClearBufferBinds()
							
			try:
				mdl = rapi.rpgConstructModel()
			except:
				mdl = NoeModel()
			mdl.setBones(self.boneList)
			mdl.setModelMaterials(NoeModelMaterials(self.texList, self.matList))
			
			mdlList.append(mdl)
		return mdlList
				
def meshLoadModel(data, mdlList):
	mesh = meshFile(data)
	mdlList = mesh.loadMeshFile(mdlList)
	return 1
	
def meshWriteModel(mdl, bs):
	global fExportExtension, w1, w2, bWriteBones, bRigToCoreBones #, doLOD	
	def getExportName(fileName):
		global fExportExtension, w1, w2, bWriteBones, bRigToCoreBones #, doLOD
		bRigToCoreBones = False
		w1 = -128
		w2 = 127
		#doLOD = 0
		if fileName == None:
			newMeshName = rapi.getInputName().lower().replace(".meshout","").replace(".fbx","").replace("out.",".").replace(".mesh","").replace(".1808312334","").replace(".1902042334","").replace(".1808282334","")
			ext = ".mesh" + fExportExtension
			if rapi.checkFileExists(newMeshName + ".mesh.1808312334"):
				ext = ".mesh.1808312334"
			elif rapi.checkFileExists(newMeshName + ".mesh.1902042334"):
				ext = ".mesh.1902042334"
			elif rapi.checkFileExists(newMeshName + ".mesh.1808282334"):
				ext = ".mesh.1808282334"
			newMeshName += ext
		else:
			newMeshName = fileName
		newMeshName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Export over MESH", "Choose a MESH file to export over", newMeshName, None)
			
		if newMeshName == None:
			print("Aborting...")
			return
		if newMeshName.find(" -flip".lower()) != -1:
			newMeshName = newMeshName.replace(" -flip".lower(), "")
			print ("Exporting with reversed handedness")
			w1 = 127
			w2 = -128
		bWriteBones = 0
		if newMeshName.find(" -bones".lower()) != -1:
			newMeshName = newMeshName.replace(" -bones".lower(), "")
			print ("Exporting with new bone positions")
			bWriteBones = 1
			
		if newMeshName.find(" -match".lower()) != -1:
			newMeshName = newMeshName.replace(" -match".lower(), "")
			print ("Unmatched bones will be rigged to the hips and spine")
			bRigToCoreBones = True
		'''if newMeshName.find(" -lod") != -1:
			newMeshName = newMeshName.replace(" -lod", "")
			print ("Exporting with LOD...")
			doLOD = 1	'''
		return newMeshName
		
	print ("			----RE Engine MESH Export----\nOpen fmt_RE_MESH.py in your Noesis plugins folder to change global exporter options.\n\
	Export Parameters:\n -flip  =  flip handedness (fixes seams and inverted lighting)\n -bones = save bone positions & hierarchy from \
	Noesis to the MESH file\n -match = assign non-matching bones to the hips and spine\n") #\n -lod = export with additional LODGroups")
	
	fileName = None
	newMeshName = getExportName(fileName)
	if newMeshName == None:
		return 0
	while not (rapi.checkFileExists(newMeshName)):
		print ("File not found!")
		newMeshName = getExportName(fileName)	
		fileName = newMeshName
		if newMeshName == None:
			return 0
			
	newMesh = rapi.loadIntoByteArray(newMeshName)
	f = NoeBitStream(newMesh)
	magic = f.readUInt()
	if magic != 1213416781:
		noesis.messagePrompt("Not a MESH file.\nAborting...")
		return 0		
	
	f.seek(18, NOESEEK_ABS)
	numModels = f.readUShort()
	
	f.seek(24, NOESEEK_ABS)
	# 0 LODOffs, # 1 uknOffs, # 3 bonesOffs, # 6 offs1, # 7 vert_BuffOffs, # 9 offs2, # 10 boneIndicesOffs, # 12 namesOffs
	headerOffsets = [f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64(),f.readUInt64()]
	
	
	f.seek(headerOffsets[0], NOESEEK_ABS)
	countArray = f.read("16B")
	
	numLODs = 1
	#if doLOD:
	#	numLODs = countArray[0]
	
	f.seek(headerOffsets[7], NOESEEK_ABS)
	#0 VertElemHdrOffs #1 vertBuffOffs #2 faceBuffOffs #3 vertBuffSize #4 faceBuffSize #5 vertElemCount[0] #6 vertElemCount[1] #9 vertBuffOffsNegative
	vertexBufferInfo = ([f.readUInt64(), f.readUInt64(), f.readUInt64(), f.readUInt(), f.readUInt(), f.readUShort(), f.readUShort(), f.readUInt(), f.readUInt(), f.readUInt()])
	vertexPosStart = vertexBufferInfo[1]
	
	vertElemHeaders = []
	for i in range(vertexBufferInfo[6]):
		vertElemHeaders.append([f.readUShort(), f.readUShort(), f.readUInt()])
	
	doUV1 = 0
	bDoSkin = 0
	for i in range(len(vertElemHeaders)):
		if vertElemHeaders[i][0] == 3:
			doUV1 = 1
		if vertElemHeaders[i][0] == 4:
			bDoSkin = 1
	
	nameOffsets = []	
	f.seek(headerOffsets[12], NOESEEK_ABS)
	for i in range(numModels):
		nameOffsets.append(f.readUInt64())
	
	names = []
	for i in range(numModels):
		f.seek(nameOffsets[i], NOESEEK_ABS)
		names.append(f.readString())
	bonesList = []
	boneNameAddressList = []
	
	#Remove Blender numbers from all names
	for mesh in mdl.meshes:
		if mesh.name.find('.') != -1:
			print ("Renaming Mesh " + str(mesh.name) + " to " + str(mesh.name.split('.')[0]))
			mesh.name = mesh.name.split('.')[0]
			
	
	if bDoSkin:		
		bBoneMismatch = False
		boneRemapTable = []
		boneInds = []
		reverseSkinBoneMap = []
		#0 numBones #1 boneMapCount #4 heirarchyOffs #5 localOffs #6 globalOffs #7 inverseGlobalOffs
		f.seek(headerOffsets[3], NOESEEK_ABS)
		boneInfo = [f.readUInt(), f.readUInt(), f.readUInt(), f.readUInt(), f.readUInt64(), f.readUInt64(), f.readUInt64(), f.readUInt64()]
		if len(mdl.bones) != boneInfo[0]:
			print ("WARNING: Model Bones do not match the bones in the MESH file!")
			print ("Model Bones: " + str(len(mdl.bones)) + "\nMESH Bones: " + str(boneInfo[0]))
			bBoneMismatch = True
		
		for b in range(boneInfo[1]):
			boneRemapTable.append(f.readUShort())
		
		f.seek(headerOffsets[10], NOESEEK_ABS)
		for i in range(boneInfo[0]):
			boneInds.append(f.readUShort())
			boneMapIndex = -1
			for b in range(len(boneRemapTable)):
				if boneRemapTable[b] == i:
					boneMapIndex = b
			reverseSkinBoneMap.append(boneMapIndex)
		
		f.seek(headerOffsets[12] + countArray[1]*8, NOESEEK_ABS)
		for i in range(boneInfo[0]):
			boneNameAddressList.append(f.readUInt64())
		
		for bone in mdl.bones:
			if bone.name.find('.') != -1:
				print ("Renaming Bone " + str(bone.name) + " to " + str(bone.name.split('.')[0]))
				bone.name = bone.name.split('.')[0] #remove blender numbers
			bName = bone.name.split(':') #remove bone numbers
			if len(bName) == 2:
				bonesList.append(bName[1])
			else:
				bonesList.append(bone.name)

	#clone beginning of file
	f.seek(0, NOESEEK_ABS) 
	bs.seek(0, NOESEEK_ABS)
	bs.writeBytes(f.readBytes(vertexPosStart))
	
	bs.seek(200, NOESEEK_ABS)
	offsetUnk00 = bs.readUInt64()
	bs.seek(offsetUnk00)
	offsetInfo = []
	meshVertexInfo = []
	for i in range(numLODs): #LODGroup Offsets
		offsetInfo.append(bs.readUInt64())
	
	#Validate meshes are named correctly
	objToExport = []
	for i, mesh in enumerate(mdl.meshes):
		ss = mesh.name.split('_')
		if len(ss) == 6:
			if ss[0] == 'LODGroup' and ss[1].isnumeric() and ss[2] == 'MainMesh' and ss[3].isnumeric() and ss[4] == 'SubMesh' and ss[5].isnumeric():
				objToExport.append(i)
				
	submeshes = []
	for ldc in range(numLODs):
		bs.seek(offsetInfo[ldc], NOESEEK_ABS)
		mainmeshCount = bs.readUInt()
		hash = bs.readUInt()
		offsetSubOffsets = bs.readUInt64()
		bs.seek(offsetSubOffsets, NOESEEK_ABS)
		meshOffsets = []
		for i in range(mainmeshCount):
			meshOffsets.append(bs.readUInt64())
		for mmc in range(mainmeshCount):
			bs.seek(meshOffsets[mmc], NOESEEK_ABS)
			meshVertexInfo.append([bs.readUByte(), bs.readUByte(), bs.readUShort(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
			for smc in range(meshVertexInfo[mmc][1]):
				matID = bs.readUInt() + 1
				bFind = 0
				for s in range(len(objToExport)):
					sName = mdl.meshes[objToExport[s]].name.split('_')
					if int(sName[1]) == (ldc+1) and int(sName[3]) == (mmc+1) and ((not bUseOldNamingScheme and int(sName[5]) == (smc+1)) or (bUseOldNamingScheme and int(sName[5]) == (matID))):
						submeshes.append(copy.copy(mdl.meshes[objToExport[s]]))
						bFind = 1
						break
				if bFind == 0:
					submeshes.append(None)
				bs.seek(12, NOESEEK_REL)
		
	vertexStrideStart = 0
	submeshVertexCount = []
	submeshVertexStride = []
	submeshFaceCount = []
	submeshFaceStride = []
	submeshFaceSize = []
	
	#Write vertex data
	bs.seek(vertexPosStart)
	for mesh in submeshes:
		submeshVertexStride.append(vertexStrideStart)
		if mesh == None:
			for i in range(9):
				bs.writeFloat(0)
			submeshVertexCount.append(3)
			vertexStrideStart += 3
		else:
			for vcmp in mesh.positions:
				bs.writeBytes((vcmp * 0.01).toBytes())
			submeshVertexCount.append(len(mesh.positions))
			vertexStrideStart += len(mesh.positions)
			
	normalTangentStart = bs.tell()	
	for mesh in submeshes:
		if mesh == None:
			for i in range(6):
				bs.writeFloat(0)
		else:
			for vcmp in mesh.tangents:
				bs.writeByte(int(vcmp[0][0] * 127 + 0.5)) #normal
				bs.writeByte(int(vcmp[0][1] * 127 + 0.5))
				bs.writeByte(int(vcmp[0][2] * 127 + 0.5))
				bs.writeByte(0)
				bs.writeByte(int(vcmp[2][0] * 127 + 0.5)) #bitangent
				bs.writeByte(int(vcmp[2][1] * 127 + 0.5))
				bs.writeByte(int(vcmp[2][2] * 127 + 0.5))
				TNW = dot(cross(vcmp[0], vcmp[1]), vcmp[2])
				if (TNW < 0.0):
					bs.writeByte(w1)
				else:
					bs.writeByte(w2)
					
	UV0start = bs.tell()
	for mesh in submeshes:
		if mesh == None:
			for i in range(3):
				bs.writeFloat(0)
		else:
			for vcmp in mesh.uvs:
				bs.writeHalfFloat(vcmp[0])
				bs.writeHalfFloat(vcmp[1])
				
	UV1start = bs.tell()
	if doUV1:
		for mesh in submeshes:
			if mesh == None:
				for i in range(3):
					bs.writeFloat(0)
			else:
				for vcmp in mesh.lmUVs:
					bs.writeHalfFloat(vcmp[0])
					bs.writeHalfFloat(vcmp[1])
	
	bnWeightStart = bs.tell()
	if bDoSkin:
		for m, mesh in enumerate(submeshes):
			if mesh == None:
				for i in range(12):
					bs.writeFloat(0)
			else:
				pos = bs.tell()
				for vcmp in mesh.weights: #write 0's
					for i in range(4):
						bs.writeFloat(0)
				bs.seek(pos, NOESEEK_ABS)
				
				for i, vcmp in enumerate(mesh.weights): #write bone indices & weights over 0's
					total = 0
					tupleList = []
					weightList = []
					for idx in range(len(vcmp.weights)):
						weightList.append(round(vcmp.weights[idx] * 255.0))
						total += weightList[idx]
					if bNormalizeWeights and total != 255:
						weightList[0] += 255 - total
						print ("Normalizing vertex weight", mesh.name, "vertex", i,",", total)
							
					for idx in range(len(vcmp.weights)):
						if idx > 8:
							print ("Warning: ", mesh.name, "vertex", i,"exceeds the vertex weight limit of 8!", )
							break
						elif vcmp.weights[idx] != 0:				
							byteWeight = weightList[idx]
							tupleList.append((byteWeight, vcmp.indices[idx]))
							
					tupleList = sorted(tupleList, reverse=True) #sort in ascending order
					
					pos = bs.tell()
					lastBone = 0
					for idx in range(len(tupleList)):	
						#if True:
						bFind = False
						for b in range(len(boneRemapTable)):
							if names[boneInds[boneRemapTable[b]]] == bonesList[tupleList[idx][1]]:
								bs.writeUByte(b)
								lastBone = b
								bFind = True
								break	
						if bFind == False: #assign unmatched bones
							if not bRigToCoreBones:
								i
								bs.writeUByte(lastBone)
							else:
								for b in range(lastBone, 0, -1):
									if names[boneInds[boneRemapTable[b]]].find("spine") != -1 or names[boneInds[boneRemapTable[b]]].find("hips") != -1:
										bs.writeUByte(b)
										break
					for x in range(8-len(tupleList)):
						bs.writeUByte(lastBone)
					
					bs.seek(pos+8, NOESEEK_ABS)
					for wval in range(len(tupleList)):
						bs.writeUByte(tupleList[wval][0])
					bs.seek(pos+16, NOESEEK_ABS)
	vertexDataEnd = bs.tell()
	
	for mesh in submeshes:
		faceStart = bs.tell()
		submeshFaceStride.append(faceStart - vertexDataEnd)
		if mesh == None:
			bs.writeUShort(0)
			bs.writeUShort(1)
			bs.writeUShort(2)
			submeshFaceCount.append(3)
			submeshFaceSize.append(3)
		else:
			submeshFaceCount.append(len(mesh.indices))
			submeshFaceSize.append(len(mesh.indices))
			for idx in mesh.indices:
				bs.writeUShort(idx)
		if ((bs.tell() - faceStart) / 6) % 2 != 0: #padding
			bs.writeUShort(0)
	faceDataEnd = bs.tell()
		
	#update mainmesh and submesh headers
	loopSubmeshCount = 0
	for ldc in range(numLODs):
		for mmc in range(mainmeshCount):
			mainmeshVertexCount = 0
			mainmeshFaceCount = 0
			bs.seek(meshOffsets[mmc] + 16, NOESEEK_ABS)
			for smc in range(meshVertexInfo[mmc][1]):
				bs.seek(4, NOESEEK_REL)
				bs.writeUInt(submeshFaceCount[loopSubmeshCount])
				bs.writeUInt(int(submeshFaceStride[loopSubmeshCount] / 2))
				bs.writeUInt(submeshVertexStride[loopSubmeshCount])
				mainmeshVertexCount += submeshVertexCount[loopSubmeshCount]
				mainmeshFaceCount += submeshFaceSize[loopSubmeshCount]
				loopSubmeshCount += 1
			bs.seek(meshOffsets[mmc]+8, NOESEEK_ABS)
			bs.writeUInt(mainmeshVertexCount)
			bs.writeUInt(mainmeshFaceCount)
	
	bs.seek(headerOffsets[7] + 16, NOESEEK_ABS)
	bs.writeInt64(vertexDataEnd)
	bs.writeUInt(vertexDataEnd - vertexPosStart)
	bs.writeUInt(faceDataEnd - vertexDataEnd)
	
	bs.seek(vertexBufferInfo[0], NOESEEK_ABS)
	for i in range (vertexBufferInfo[6]):
		elementType = bs.readUShort()
		elementSize = bs.readUShort()
		if elementType == 0:
			bs.writeUInt(vertexPosStart - vertexPosStart)
		elif elementType == 1:
			bs.writeUInt(normalTangentStart - vertexPosStart)
		elif elementType == 2:
			bs.writeUInt(UV0start - vertexPosStart)
		elif elementType == 3:
			bs.writeUInt(UV1start - vertexPosStart)
		elif elementType == 4:
			bs.writeUInt(bnWeightStart - vertexPosStart)
	
	#Save bone positions
	if bDoSkin and bWriteBones:
		for bone in mdl.bones:
			subBoneName = bone.name
			bHasParent = False
			parentBoneName = ""
			if (bone.parentName != ""):
				bHasParent = True
				parentBoneName = bone.parentName
				ps = parentBoneName.split(':')
				if len(ps) == 2:
					parentBoneName = ps[1]
			cs = subBoneName.split(':')
			if len(cs) == 2:
				subBoneName = cs[1]

			TWMat = NoeMat44(([1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]))
			if bHasParent:
				pMat = mdl.bones[bone.parentIndex].getMatrix().toMat44()
				boneLocalMat = (bone.getMatrix().toMat44() * pMat.inverse()) * TWMat
				boneLocalMat[3] = boneLocalMat[3] * 0.01
				boneLocalMat[3][3] = 1.0
			boneGlobalMat = bone.getMatrix().toMat44() * TWMat
			boneGlobalMat[3] = boneGlobalMat[3] * 0.01
			boneGlobalMat[3][3] = 1.0
			inverseGlobalMat = boneGlobalMat.inverse()
			
			subBoneID= -1
			parentBoneID = -1
			for i in range(boneInfo[0]):
				bs.seek(boneNameAddressList[i], NOESEEK_ABS)
				fileBoneName = bs.readString();
				if fileBoneName == subBoneName:
					subBoneID = i
				if fileBoneName == parentBoneName:
					parentBoneID = i
			bs.seek(boneNameAddressList[parentBoneID])
			#myVar = bs.readString();
			#print (bone.name, subBoneID, myVar)
			if subBoneID != -1:
				if parentBoneID != -1:
					bs.seek(boneInfo[4] + subBoneID*16 + 2, NOESEEK_ABS)
					bs.writeUShort(parentBoneID)
				
				if bHasParent: #Local Transform Bones
					bs.seek(boneInfo[5] + 64*subBoneID, NOESEEK_ABS)
					bs.writeBytes(boneLocalMat.toBytes())
				
				#Global Transform Bones
				bs.seek(boneInfo[6] + 64*subBoneID, NOESEEK_ABS)
				bs.writeBytes(boneGlobalMat.toBytes())
				
				#Inverse Global Transform Bones
				bs.seek(boneInfo[7] + 64*subBoneID, NOESEEK_ABS)
				bs.writeBytes(inverseGlobalMat.toBytes())
		
	#if not doLOD:
	bs.seek(headerOffsets[0], NOESEEK_ABS)
	bs.writeByte(1)
	
	#crash fix
	bs.seek(32, NOESEEK_ABS)
	bs.writeUShort(0)
	
	if bDoSkin:
		#shadow fix
		bs.seek(16, NOESEEK_ABS)
		bs.writeByte(3)
		
		#uroboros fix
		bs.seek(56, NOESEEK_ABS)
		bs.writeUInt(0)
	
	#fileSize
	bs.seek(8, NOESEEK_ABS)
	bs.writeUInt64(faceDataEnd) 
	return 1