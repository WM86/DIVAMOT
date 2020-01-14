#By Minmode
#Based on the noesis script by Chrrox
#Anim research help from Skyth

from inc_noesis import *
import noesis
import rapi
import math

#0 = Normal
#1 = Send vertex tangent data to UV
Import_Option = 0

#0 = Dreamy Theater
#1 = Future Tone
#2 = F
#3 = F2nd
#4 = X
motImportOption = 4
motName = "pv932"
motID = "_hih_p1_00"

def registerNoesisTypes():
      handle = noesis.register("SEGA Model", ".bin")
      noesis.setHandlerTypeCheck(handle, objBinCheckType)
      noesis.setHandlerLoadModel(handle, objBinLoadModel)
      return 1

def objBinCheckType(data):
      bs = NoeBitStream(data)
      header = bs.readUInt()
      if len(data) < 4:
            return 0
      if header != 0x05062500:
            return 0
      return 1

def texBinCheckType(data):
      bs = NoeBitStream(data)
      header = bs.readUInt()
      if len(data) < 4:
            return 0
      if header != 0x03505854:
            return 0
      return 1

class binModel:
      def __init__(self, bs):
            self.texList = []
            self.texNames = []
            self.matList = []
            self.matDict = {}
            self.animList = []
            self.boneList = []
            self.boneNList = []
            self.boneMap = []
            self.boneDict = {}
            self.bonePDict = {}
            self.skelDict = {}
            self.tex_db = {}
            self.obj_file_db = [[], [], [], [], []]
            self.obj_mesh_db = {}
            self.mot_db = [{}, []]
            self.bone_data = []
            self.texID = []
            self.objectID = []
            self.loadAll(bs)
		
      def loadAll(self, bs):
            self.readBin(bs)
		
      def readBin(self, bs):
            baseName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
            baseName = baseName[:-4]
            try:
                  binTexDB = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName()) + "tex_db.bin")
            except:
                  binTexDB = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName()) + "mdata_tex_db.bin")
            self.readBinTexDB(binTexDB)
            magic, objectCount, boneCount, objectTableOff, boneTableOff, meshNameOff, objectIDOff, texIDOff, texIDCount = bs.read("9I")
            self.readTexID(bs, [texIDOff, texIDCount])
            self.readObjectID(bs, [objectIDOff, objectCount])
            binTex = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName()) + baseName + "_tex.bin")
            self.readBinTex(binTex)
            if objectCount != 0:
                  bs.seek(boneTableOff, NOESEEK_ABS)
                  boneTable = bs.read(objectCount * "I")
                  boneData = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "bone_data.bin")
                  self.readBoneData(boneData, baseName[:3].upper())
                  self.readBones(bs, boneTable)
                  bs.seek(objectTableOff, NOESEEK_ABS)
                  objectTable = bs.read(objectCount * "I")
                  self.readObject(bs, objectTable)
            if motImportOption < 3:
                  if(rapi.checkFileExists(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "rob" + os.sep + "mot_" + motName + ".bin")):
                        binMotDB = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "rob" + os.sep + "mot_db.bin")
                        self.readBinMotDB(binMotDB)
                        binAnim = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "rob" + os.sep + "mot_" + motName + ".bin")
                        self.readAnim(binAnim)
            elif motImportOption >= 3:
                  if(rapi.checkFileExists(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "mot" + os.sep + motName + motID + ".mot")):
                        motAnim = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "mot" + os.sep + motName + motID + ".mot")
                        self.readMotAnim(motAnim)

      def readTexID(self, bs, texInfo):
            bs.seek(texInfo[0], NOESEEK_ABS)
            self.texID = bs.read(texInfo[1] * "I")

      def readObjectID(self, bs, objectInfo):
            bs.seek(objectInfo[0], NOESEEK_ABS)
            self.objectID = bs.read(objectInfo[1] * "I")

      def readBones(self, bs, boneTable):
            lastSkel = -1
            for i in range(len(boneTable)-1, -1, -1):
                  if boneTable[i] != 0:
                        lastSkel = i
                        break
            OSG = [[], []]
            EXP = [[], []]
            for i in range(0, len(boneTable)):
                  tmpBName = []
                  if boneTable[i] != 0:
                        bs.seek(boneTable[i], NOESEEK_ABS)
                        boneInfo = bs.read("6I")
                        bs.seek(boneInfo[0], NOESEEK_ABS)
                        boneIdList = []
                        bonePDict = {}
                        for a in range(0, boneInfo[4]):
                              boneIdList.append(bs.readUInt())
                              if self.bonePDict.__contains__(str(boneIdList[a])):
                                    pass
                              else:
                                    self.bonePDict[str(boneIdList[a])] = len(self.bonePDict)
                        boneMatrixList = []
                        for a in range(0, boneInfo[4]):
                              bs.seek(boneInfo[1] + (0x40 * a), NOESEEK_ABS)
                              m01, m02, m03, m04 = bs.read("4f")
                              m11, m12, m13, m14 = bs.read("4f")
                              m21, m22, m23, m24 = bs.read("4f")
                              m31, m32, m33, m34 = bs.read("4f")
                              boneMtx = NoeMat43( [NoeVec3((m01, m02, m03)), NoeVec3((m11, m12, m13)), NoeVec3((m21, m22, m23)), NoeVec3((m04, m14, m24))] ).inverse()
                              boneMatrixList.append(boneMtx)
                        bs.seek(boneInfo[2], NOESEEK_ABS)
                        boneNameOff = bs.read(boneInfo[4] * "I")
                        boneName = []
                        for a in range(0, boneInfo[4]):
                              bs.seek(boneNameOff[a], NOESEEK_ABS)
                              boneName.append(bs.readString())
                              tmpBName.append(boneName[a])
                        bs.seek(boneInfo[3], NOESEEK_ABS)
                        boneUnk = bs.read(10 * "I")
                        try:
                              if i == 0 and len(self.bone_data[0]) != 0:
                                    boneMtx = NoeMat43()
                                    newBone = NoeBone(0, "gblctr", boneMtx, None, -1)
                                    self.boneDict["gblctr"] = len(self.boneList)
                                    self.boneList.append(newBone)
                                    self.boneNList.append("gblctr")
                                    newBone = NoeBone(1, "kg_ya_ex", boneMtx, None, len(self.boneList) - 1)
                                    self.boneDict["kg_ya_ex"] = len(self.boneList)
                                    self.boneList.append(newBone)
                                    self.boneNList.append("kg_ya_ex")
                                    for a in range(0, len(self.bone_data[0])):
                                          if self.bone_data[0][a] in boneName:
                                                boneMtx = boneMatrixList[boneName.index(self.bone_data[0][a])]
                                          elif self.bone_data[0][a] == "n_hara_cp" and "kl_kosi_etc_wj" in boneName:
                                                boneMtx = NoeMat43()
                                                boneMtx[3] = boneMatrixList[boneName.index("kl_kosi_etc_wj")][3]
                                          elif self.bone_data[0][a] == "n_hara_cp":
                                                boneMtx = NoeMat43()
                                          elif self.bone_data[0][a] == "n_hara":
                                                boneMtx = self.boneList[self.boneNList.index(self.bone_data[0][self.skelDict[self.bone_data[0][a]]])]._matrix
                                          elif (self.bone_data[0][a] == "cl_mune" or self.bone_data[0][a] == "j_mune_wj") and "kl_kosi_etc_wj" in boneName:
                                                boneMtx = NoeMat43()
                                                boneMtx[3] = boneMatrixList[boneName.index("kl_kosi_etc_wj")][3]
                                          elif self.bone_data[0][a] == "kl_kubi" and "n_kubi_wj_ex" in boneName:
                                                boneMtx = NoeMat43()
                                                boneMtx[3] = boneMatrixList[boneName.index("n_kubi_wj_ex")][3]
                                          elif (self.bone_data[0][a] == "n_kao" or self.bone_data[0][a] == "cl_kao") and "j_kao_wj" in boneName:
                                                boneMtx = NoeMat43()
                                                boneMtx[3] = boneMatrixList[boneName.index("j_kao_wj")][3]
                                          elif self.bone_data[0][a] == "face_root":
                                                boneMtx = self.bone_data[1][a] * self.boneList[self.boneNList.index(self.bone_data[0][self.skelDict[self.bone_data[0][a]]])]._matrix
                                                rot = NoeAngles((0, 0, 0))
                                                mat = rot.toMat43_XYZ()
                                                boneMtx[0] = mat[0]
                                                boneMtx[1] = mat[1]
                                                boneMtx[2] = mat[2]
                                          elif self.bone_data[0][a] == "c_kata_l" and "n_skata_l_wj_cd_ex" in boneName:
                                                boneMtx = NoeMat43()
                                                boneMtx[3] = boneMatrixList[boneName.index("n_skata_l_wj_cd_ex")][3]
                                          elif self.bone_data[0][a] == "c_kata_r" and "n_skata_r_wj_cd_ex" in boneName:
                                                boneMtx = NoeMat43()
                                                boneMtx[3] = boneMatrixList[boneName.index("n_skata_r_wj_cd_ex")][3]
                                          elif self.bone_data[0][a] == "cl_momo_l":
                                                boneMtx = self.bone_data[1][a] * self.boneList[self.boneNList.index(self.bone_data[0][self.skelDict[self.bone_data[0][a]]])]._matrix
                                                rot = NoeAngles((0, 0, 0))
                                                mat = rot.toMat43_XYZ()
                                                boneMtx[0] = mat[0]
                                                boneMtx[1] = mat[1]
                                                boneMtx[2] = mat[2]
                                          elif self.bone_data[0][a] == "cl_momo_r":
                                                boneMtx = self.bone_data[1][a] * self.boneList[self.boneNList.index(self.bone_data[0][self.skelDict[self.bone_data[0][a]]])]._matrix
                                                rot = NoeAngles((0, 0, 0))
                                                mat = rot.toMat43_XYZ()
                                                boneMtx[0] = mat[0]
                                                boneMtx[1] = mat[1]
                                                boneMtx[2] = mat[2]
                                          elif self.bone_data[0][a] == "j_momo_l_wj":
                                                fix = self.bone_data[1][a]
                                                fix[3] = NoeVec3((fix[3][1], fix[3][0] * -1, fix[3][2]))
                                                boneMtx =  fix * self.boneList[self.boneNList.index(self.bone_data[0][self.skelDict[self.bone_data[0][a]]])]._matrix
                                          elif self.bone_data[0][a] == "j_momo_r_wj":
                                                fix = self.bone_data[1][a]
                                                fix[3] = NoeVec3((fix[3][1], fix[3][0] * -1, fix[3][2]))
                                                boneMtx =  fix * self.boneList[self.boneNList.index(self.bone_data[0][self.skelDict[self.bone_data[0][a]]])]._matrix
                                          else:
                                                boneMtx = self.bone_data[1][a] * self.boneList[self.boneNList.index(self.bone_data[0][self.skelDict[self.bone_data[0][a]]])]._matrix
                                          if self.bone_data[0][self.skelDict[self.bone_data[0][a]]].endswith("_cp"):
                                                newBone = NoeBone(a + 2, self.bone_data[0][a], boneMtx, None, self.skelDict[self.bone_data[0][self.skelDict[self.bone_data[0][a]]]] + 2)
                                          else:
                                                newBone = NoeBone(a + 2, self.bone_data[0][a], boneMtx, None, self.skelDict[self.bone_data[0][a]] + 2)
                                          self.boneDict[self.bone_data[0][a]] = len(self.boneList)
                                          self.boneList.append(newBone)
                                          self.boneNList.append(self.bone_data[0][a])
                                    self.boneList[self.boneNList.index("n_hara_cp")].parentIndex =  self.boneDict["kg_ya_ex"]
                                    for a in range(0, len(self.boneList)):
                                          if self.boneList[a].name in self.skelDict:
                                                if self.boneList[a].name == "n_momo_l_cd_ex" or self.boneList[a].name == "n_momo_a_l_wj_cd_ex":
                                                      self.boneList[a].parentIndex = self.boneNList.index("cl_momo_l")
                                                elif self.boneList[a].name == "n_momo_r_cd_ex" or self.boneList[a].name == "n_momo_a_r_wj_cd_ex":
                                                      self.boneList[a].parentIndex = self.boneNList.index("cl_momo_r")
                                    ik = ["e_mune_cp", "e_kao_cp", "e_ude_l_cp", "e_ude_r_cp", "e_sune_l_cp", "e_sune_r_cp"]
                                    for a in range(0, len(self.boneList)):
                                          if self.boneList[a].name in ik:
                                                if self.boneList[a].name == "e_mune_cp":
                                                      boneMtx = NoeMat43()
                                                      if "kl_kosi_etc_wj" in self.boneNList:
                                                            boneMtx[3] = self.boneList[self.boneNList.index("kl_kosi_etc_wj")]._matrix[3]
                                                      self.boneList[a]._matrix = boneMtx
                                                      self.boneList[a].parentIndex = self.boneDict["kg_ya_ex"]
                                                elif self.boneList[a].name == "e_kao_cp":
                                                      boneMtx = NoeMat43()
                                                      if "j_kao_wj" in self.boneNList:
                                                            boneMtx[3] = self.boneList[self.boneNList.index("j_kao_wj")]._matrix[3]
                                                      self.boneList[a]._matrix = boneMtx
                                                      self.boneList[a].parentIndex = self.boneDict["kg_ya_ex"]
                                                elif self.boneList[a].name == "e_ude_l_cp":
                                                      boneMtx = NoeMat43()
                                                      if "n_ste_l_wj_ex" in self.boneNList:
                                                            boneMtx[3] = self.boneList[self.boneNList.index("n_ste_l_wj_ex")]._matrix[3]
                                                      self.boneList[a]._matrix = boneMtx
                                                      self.boneList[a].parentIndex = self.boneDict["kg_ya_ex"]
                                                elif self.boneList[a].name == "e_ude_r_cp":
                                                      boneMtx = NoeMat43()
                                                      if "n_ste_r_wj_ex" in self.boneNList:
                                                            boneMtx[3] = self.boneList[self.boneNList.index("n_ste_r_wj_ex")]._matrix[3]
                                                      self.boneList[a]._matrix = boneMtx
                                                      self.boneList[a].parentIndex = self.boneDict["kg_ya_ex"]
                                                elif self.boneList[a].name == "e_sune_l_cp":
                                                      boneMtx = NoeMat43()
                                                      if "kl_asi_l_wj_co" in self.boneNList:
                                                            boneMtx[3] = self.boneList[self.boneNList.index("kl_asi_l_wj_co")]._matrix[3]
                                                      self.boneList[a]._matrix = boneMtx
                                                      self.boneList[a].parentIndex = self.boneDict["kg_ya_ex"]
                                                elif self.boneList[a].name == "e_sune_r_cp":
                                                      boneMtx = NoeMat43()
                                                      if "kl_asi_r_wj_co" in self.boneNList:
                                                            boneMtx[3] = self.boneList[self.boneNList.index("kl_asi_r_wj_co")]._matrix[3]
                                                      self.boneList[a]._matrix = boneMtx
                                                      self.boneList[a].parentIndex = self.boneDict["kg_ya_ex"]
                        except:
                              pass
                        skelLength = len(self.boneList)
                        notInSkel = []
                        for a in range(0, boneInfo[4]):
                              if boneName[a] not in self.boneNList:
                                    notInSkel.append(boneName[a])
                        for a in range(0, boneInfo[4]):
                              bs.seek(boneInfo[5] + (0x4 * a), NOESEEK_ABS)
                              bpar = bs.readInt()
                              if boneName[a] in self.boneNList:
                                    pass
                              else:
                                    if str(bpar) in self.bonePDict:
                                          parent = self.bonePDict[str(bpar)]
                                    else:
                                          parent = -1
                                    if parent == -1:
                                          newBone = NoeBone(len(self.boneList), boneName[a], boneMatrixList[a], None, parent)
                                    elif boneName[parent] in notInSkel:
                                          newBone = NoeBone(len(self.boneList), boneName[a], boneMatrixList[a], None, skelLength + notInSkel.index(boneName[parent]))
                                    else:
                                          newBone = NoeBone(len(self.boneList), boneName[a], boneMatrixList[a], None, self.boneDict[boneName[parent]])
                                    self.boneDict[boneName[a]] = len(self.boneList)
                                    self.boneList.append(newBone)
                                    self.boneNList.append(boneName[a])
                        if boneInfo[3] != 0:
                              parentInfo = []
                              parentNameInfo = []
                              bs.seek(boneUnk[5], NOESEEK_ABS)
                              pT = bs.readUInt()
                              pI = bs.readUInt()
                              parentInfo.append([pT, pI])
                              while pT != 0 and pT != 0:
                                    pT = bs.readUInt()
                                    pI = bs.readUInt()
                                    parentInfo.append([pT, pI])
                              bs.seek(boneUnk[7], NOESEEK_ABS)
                              current = bs.tell()
                              for a in range(0, boneUnk[6]):
                                    bs.seek(current, NOESEEK_ABS)
                                    pNO = bs.readUInt()
                                    current = bs.tell()
                                    bs.seek(pNO, NOESEEK_ABS)
                                    parentNameInfo.append(bs.readString())
                              for a in range(0, len(parentInfo)):
                                    bs.seek(parentInfo[a][0], NOESEEK_ABS)
                                    parentType = bs.readString()
                                    if parentType == "OSG":
                                          bs.seek(parentInfo[a][1], NOESEEK_ABS)
                                          parentNameOff = bs.readUInt()
                                          bs.seek(0x28, NOESEEK_REL)
                                          childCount = bs.readUInt()
                                          pNInfoRef1 = bs.readUInt()
                                          pNInfoRef2 = bs.readUInt()
                                          bs.seek(parentNameOff, NOESEEK_ABS)
                                          parentName = bs.readString()
                                          for b in range(0, childCount):
                                                if b == 0:
                                                      OSG[0].append(parentName)
                                                      OSG[1].append(parentNameInfo[(pNInfoRef1-0x8000+1)])
                                                else:
                                                      OSG[0].append(parentNameInfo[(pNInfoRef1-0x8000+b)])
                                                      OSG[1].append(parentNameInfo[(pNInfoRef1-0x8000+1+b)])
                                    elif parentType == "EXP":
                                          bs.seek(parentInfo[a][1], NOESEEK_ABS)
                                          parentNameOff = bs.readUInt()
                                          bs.seek(0x24, NOESEEK_REL)
                                          childNameOff = bs.readUInt()
                                          bs.seek(parentNameOff, NOESEEK_ABS)
                                          parentName = bs.readString()
                                          bs.seek(childNameOff, NOESEEK_ABS)
                                          childName = bs.readString()
                                          EXP[0].append(parentName)
                                          EXP[1].append(childName)
                        if i == lastSkel:
                              for a in range(0, len(OSG[0])):
                                    if OSG[1][a] in self.boneNList:
                                          if OSG[0][a] in self.boneNList:
                                                self.boneList[self.boneNList.index(OSG[1][a])].parentIndex = self.boneNList.index(OSG[0][a])
                                          elif OSG[0][a] in EXP[1] and EXP[0][EXP[1].index(OSG[0][a])] in self.boneNList:
                                                self.boneList[self.boneNList.index(OSG[1][a])].parentIndex = self.boneNList.index(EXP[0][EXP[1].index(OSG[0][a])])
                              for a in range(0, len(EXP[0])):
                                    if EXP[1][a] in self.boneNList:
                                          if EXP[0][a] in self.boneNList:
                                                self.boneList[self.boneNList.index(EXP[1][a])].parentIndex = self.boneNList.index(EXP[0][a])
                                          elif EXP[0][a] in EXP[1] and EXP[0][EXP[1].index(EXP[0][a])] in self.boneNList:
                                                self.boneList[self.boneNList.index(EXP[1][a])].parentIndex = self.boneNList.index(EXP[0][EXP[1].index(EXP[0][a])])
                  self.boneMap.append(tmpBName)

      def readObject(self, bs, objectTable):
            matDupCheck = []
            for i in range(0, len(objectTable)):
                  bs.seek(objectTable[i] + 0x18, NOESEEK_ABS)
                  meshCount, meshTableOff, matCount, matOff = bs.read("4I")
                  uvScale = []
                  matBase = len(self.matList)
                  for a in range(0, matCount):
                        bs.seek(objectTable[i] + matOff + (0x4B0 * a), NOESEEK_ABS)
                        bs.seek(0x8, NOESEEK_REL)
                        matType = bs.readBytes(8).decode("ASCII").rstrip("\0")
                        matInfo = []
                        for b in range(0, 8):
                              unk = bs.read("2I")
                              tex_dbID = bs.readUInt()
                              texType = bs.readUInt()
                              if b == 0:
                                    bs.seek(0xC, NOESEEK_REL)
                                    uvX = bs.readFloat()
                                    bs.seek(0x10, NOESEEK_REL)
                                    uvY = bs.readFloat()
                                    bs.seek(0x10, NOESEEK_REL)
                                    uvZ = bs.readFloat()
                                    uvScale.append([uvX, uvY, uvZ])
                                    bs.seek(0x30, NOESEEK_REL)
                              else:
                                    bs.seek(0x68, NOESEEK_REL)
                              matInfo.append([texType, tex_dbID])
                        unk = bs.readUInt()
                        alphaBlend = bs.readUInt()
                        diffColour = bs.read("4f")
                        ambiColour = bs.read("4f")
                        specColour = bs.read("4f")
                        emiColour = bs.read("4f")
                        specPower = bs.readFloat()
                        bs.seek(0x14, NOESEEK_REL)
                        matName = bs.readBytes(64).decode("ASCII").rstrip("\0")
                        if matName in matDupCheck:
                              matName = matName + "_" + str(i)
                        matDupCheck.append(matName)
                        material = NoeMaterial(matType + "_" + matName, "")
                        for b in range(0, 8):
                              if matInfo[b][0] == 0xF1 and b == 0:
                                    material.setTexture(self.tex_db[matInfo[b][1]])
                              elif matInfo[b][0] == 0xF2:
                                    material.setNormalTexture(self.tex_db[matInfo[b][1]])
                              elif matInfo[b][0] == 0xF3:
                                    material.setSpecularTexture(self.tex_db[matInfo[b][1]])
                              elif matInfo[b][0] == 0x3F9:
                                    material.setEnvTexture(self.tex_db[matInfo[b][1]])
                        material.setDefaultBlend(alphaBlend & 0x1)
                        material.setDiffuseColor(diffColour)
                        material.setSpecularColor([specColour[0], specColour[1], specColour[2], specPower])
                        if emiColour != (0.0, 0.0, 0.0, 1.0):
                              print(matType + "_" + matName)
                              print(emiColour)
                        self.matList.append(material)
                  for a in range(0, meshCount):
                        bs.seek(objectTable[i] + meshTableOff + (0xD8 * a), NOESEEK_ABS)
                        bs.seek(0x14, NOESEEK_REL)
                        meshInfo = bs.read(33 * "I")
                        meshName = bs.readBytes(64).decode("ASCII").rstrip("\0")
                        baseName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
                        if baseName.startswith("stg"):
                              try:
                                    srch = self.obj_file_db[2].index(baseName + ".bin")
                                    fileID = self.obj_file_db[0][srch]
                                    #meshName = obj_mesh_DB[fileID][meshNameId_Array[i]]
                              except:
                                    pass
                        if meshInfo[2] & 0x1:
                              bs.seek(objectTable[i] + meshInfo[5], NOESEEK_ABS)
                              vertBuff = bs.readBytes(meshInfo[4] * 0xC)
                              rapi.rpgBindPositionBufferOfs(vertBuff, noesis.RPGEODATA_FLOAT, 12, 0)
                        if meshInfo[2] & 0x2:
                              bs.seek(objectTable[i] + meshInfo[6], NOESEEK_ABS)
                              normalBuff = bs.readBytes(meshInfo[4] * 0xC)
                              rapi.rpgBindNormalBufferOfs(normalBuff, noesis.RPGEODATA_FLOAT, 12, 0)
                        if meshInfo[2] & 0x4:
                              bs.seek(objectTable[i] + meshInfo[7], NOESEEK_ABS)
                              tangentBuff = bs.readBytes(meshInfo[4] * 0x10)
                              if Import_Option == 1:
                                    rapi.rpgBindUV1BufferOfs(tangentBuff, noesis.RPGEODATA_FLOAT, 16, 0)
                                    rapi.rpgBindUV2BufferOfs(tangentBuff, noesis.RPGEODATA_FLOAT, 16, 8)
                              else:
                                    rapi.rpgBindTangentBuffer(tangentBuff, noesis.RPGEODATA_FLOAT, 16, 0)
                        if meshInfo[2] & 0x10:
                              bs.seek(objectTable[i] + meshInfo[9], NOESEEK_ABS)
                              uvBuff = bs.readBytes(meshInfo[4] * 0x8)
                              if Import_Option != 1:
                                    rapi.rpgBindUV1BufferOfs(uvBuff, noesis.RPGEODATA_FLOAT, 8, 0)
                        if meshInfo[2] & 0x20:
                              bs.seek(objectTable[i] + meshInfo[10], NOESEEK_ABS)
                              #uv2Buff = bs.readBytes(meshInfo[4] * 0x8)
                              for b in range(0, meshInfo[4]):
                                    u, v = bs.read("2f")
                                    if b == 0:
                                          uv2Buff = struct.pack("f", u)
                                          uv2Buff += struct.pack("f", v * -1)
                                    else:
                                          uv2Buff += struct.pack("f", u)
                                          uv2Buff += struct.pack("f", v * -1)
                              if Import_Option != 1:
                                    rapi.rpgBindUV2BufferOfs(uv2Buff, noesis.RPGEODATA_FLOAT, 8, 0)
                        if meshInfo[2] & 0x100:
                              bs.seek(objectTable[i] + meshInfo[13], NOESEEK_ABS)
                              colourBuff = bs.readBytes(meshInfo[4] * 0x10)

                              rapi.rpgBindColorBufferOfs(colourBuff, noesis.RPGEODATA_FLOAT, 16, 0, 4)
                        if meshInfo[2] & 0x400:
                              bs.seek(objectTable[i] + meshInfo[15], NOESEEK_ABS)
                              weightBuff = bs.readBytes(meshInfo[4] * 0x10)
                              rapi.rpgBindBoneWeightBuffer(weightBuff, noesis.RPGEODATA_FLOAT, 16, 4)
                        if meshInfo[2] & 0x800:
                              bs.seek(objectTable[i] + meshInfo[1], NOESEEK_ABS)
                              bs.seek(0x14, NOESEEK_REL)
                              faceInfo = bs.read(10 * "I")
                              bs.seek(objectTable[i] + meshInfo[16], NOESEEK_ABS)
                              boneTmp = []
                              for b in range(0, meshInfo[4]):
                                    for c in range(0, 4):
                                          bId = bs.readFloat()
                                          if faceInfo[3] < 85:
                                                if bId == 255:
                                                      bId = 0
                                          boneTmp.append(int(bId // 3))
                              indexBuff = struct.pack('h'*len(boneTmp), *boneTmp)
                              rapi.rpgBindBoneIndexBuffer(indexBuff, noesis.RPGEODATA_SHORT, 8, 4)
                        rapi.rpgSetName(meshName)
                        for b in range(0, meshInfo[0]):
                              bs.seek(objectTable[i] + meshInfo[1] + (0x5C * b), NOESEEK_ABS)
                              bs.seek(0x14, NOESEEK_REL)
                              faceInfo = bs.read(10 * "I")
                              bs.seek(objectTable[i] + faceInfo[4], NOESEEK_ABS)
                              boneMapTemp = bs.read(faceInfo[3] * "H")
                              boneMap = []
                              for c in range(0, faceInfo[3]):
                                    boneMap.append(self.boneDict[self.boneMap[i][boneMapTemp[c]]])
                              if len(boneMap) != 0:
                                    rapi.rpgSetBoneMap(boneMap)
                              rapi.rpgSetUVScaleBias(NoeVec3 ((uvScale[faceInfo[0]][0], uvScale[faceInfo[0]][1]*-1, uvScale[faceInfo[0]][2])), None)
                              rapi.rpgSetMaterial(self.matList[faceInfo[0] + matBase].name)
                              bs.seek(objectTable[i] + faceInfo[9], NOESEEK_ABS)
                              faceBuff = bs.readBytes(faceInfo[8] * 0x2)
                              if faceInfo[6] == 5:
                                    rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, faceInfo[8], noesis.RPGEO_TRIANGLE_STRIP, 1)
                              else:
                                    rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, faceInfo[8], noesis.RPGEO_TRIANGLE, 1)
                        rapi.rpgClearBufferBinds()

      def readBinTexDB(self, binTexDB):
            bs = NoeBitStream(binTexDB)
            texCount = bs.readUInt()
            texIDTableOff = bs.readUInt()
            bs.seek(texIDTableOff, NOESEEK_ABS)
            currentOff = bs.tell()
            for i in range(0, texCount):
                  bs.seek(currentOff, NOESEEK_ABS)
                  texID = bs.readUInt()
                  texNameOff = bs.readUInt()
                  currentOff = bs.tell()
                  bs.seek(texNameOff, NOESEEK_ABS)
                  texName = bs.readString()
                  self.tex_db[texID] = texName

      def readBinMotDB(self, binMotDB):
            bs = NoeBitStream(binMotDB)
            version = bs.readUInt()
            motTableOff = bs.readUInt()
            motTableIDsOff = bs.readUInt()
            motTableCount = bs.readUInt()
            boneTableOff = bs.readUInt()
            boneTableCount = bs.readUInt()
            bs.seek(motTableOff, NOESEEK_ABS)
            for i in range(0, motTableCount):
                  nameOff = bs.readUInt()
                  motNamesOff = bs.readUInt()
                  motCount = bs.readUInt()
                  motIDOff = bs.readUInt()
                  cur = bs.tell()
                  bs.seek(nameOff, NOESEEK_ABS)
                  name = bs.readString()
                  motNames = []
                  bs.seek(motNamesOff, NOESEEK_ABS)
                  for a in range(0, motCount):
                        stringOff = bs.readUInt()
                        cur2 = bs.tell()
                        bs.seek(stringOff, NOESEEK_ABS)
                        motNames.append(bs.readString())
                        bs.seek(cur2, NOESEEK_ABS)
                  motIDs = []
                  bs.seek(motIDOff, NOESEEK_ABS)
                  for a in range(0, motCount):
                        IDOff = bs.readUInt()
                        cur2 = bs.tell()
                        bs.seek(IDOff, NOESEEK_ABS)
                        motNames.append(bs.readUInt())
                        bs.seek(cur2, NOESEEK_ABS)
                  self.mot_db[0][name] = [motCount, motNames, motIDs]
                  bs.seek(cur, NOESEEK_ABS)
            bs.seek(boneTableOff, NOESEEK_ABS)
            for i in range(0, boneTableCount):
                  stringOff = bs.readUInt()
                  cur = bs.tell()
                  bs.seek(stringOff, NOESEEK_ABS)
                  self.mot_db[1].append(bs.readString())
                  bs.seek(cur, NOESEEK_ABS)

      def readBoneData(self, boneData, vocaloid):
            bs = NoeBitStream(boneData)
            boneMagic, skelCount, skelOff1, skelOff2 = bs.read("4I")
            bs.seek(skelOff1, NOESEEK_ABS)
            skelInfo1 = bs.read(skelCount * "I")
            bs.seek(skelOff2, NOESEEK_ABS)
            skelInfo2 = bs.read(skelCount * "I")
            for i in range(0, skelCount):
                  bs.seek(skelInfo2[i], NOESEEK_ABS)
                  skelName = bs.readString()
                  if skelName == vocaloid:
                        bs.seek(skelInfo1[i], NOESEEK_ABS)
                        skelInfo3 = bs.read("9I")
                        boneTable = {}
                        boneMtxs = []
                        boneNames1 = []
                        boneNames2 = []
                        boneParents = []
                        bones = []
                        bs.seek(skelInfo3[0], NOESEEK_ABS)
                        while True:
                              Flags = bs.readUByte()
                              hasParent = bs.readBool()
                              parentIndex = bs.readByte()
                              unk1 = bs.readUByte()
                              pairIndex = bs.readByte()
                              unk2 = bs.readUByte()
                              bs.seek(0x02, NOESEEK_REL)
                              nameOff = bs.readUInt()
                              cur = bs.tell()
                              bs.seek(nameOff, NOESEEK_ABS)
                              name = bs.readString()
                              if name != "End":
                                    boneTable[name] = [Flags, hasParent, parentIndex, unk1, pairIndex, unk2]
                                    bs.seek(cur, NOESEEK_ABS)
                              else:
                                    break
                        bs.seek(skelInfo3[2], NOESEEK_ABS)
                        for a in range(0, skelInfo3[1]):
                              boneMtxs.append(bs.read("3f"))
                        bs.seek(skelInfo3[5], NOESEEK_ABS)
                        skelNameOff1 = bs.read(skelInfo3[4] * "I")
                        for a in range(0, skelInfo3[4]):
                              bs.seek(skelNameOff1[a], NOESEEK_ABS)
                              boneNames1.append(bs.readString())
                        bs.seek(skelInfo3[7], NOESEEK_ABS)
                        skelNameOff2 = bs.read(skelInfo3[6] * "I")
                        for a in range(0, skelInfo3[6]):
                              bs.seek(skelNameOff2[a], NOESEEK_ABS)
                              boneNames2.append(bs.readString())
                        bs.seek(skelInfo3[8], NOESEEK_ABS)
                        boneParents = bs.read(skelInfo3[6] * "h")
                        for a in range(0, skelInfo3[6]):
                              if boneNames2[a] in boneNames1:
                                    index = boneNames1.index(boneNames2[a])
                                    pos = NoeVec3(boneMtxs[index + 2])
                              else:
                                    pos = NoeVec3((0, 0, 0))
                              boneMtx = NoeMat43()
                              boneMtx[3] = pos
                              bones.append(boneMtx)
                              self.skelDict[boneNames2[a]] = boneParents[a]
                        self.bone_data.append(boneNames2)
                        self.bone_data.append(bones)
                        self.bone_data.append(boneTable)

      def readAnim(self, binAnim):
            bs = NoeBitStream(binAnim)
            animCount = self.mot_db[0][motName][0]
            animOffsets = []
            for i in range(0, animCount):
                  animOffsets.append(bs.read("4I"))
            for i in range(0, animCount):
                  animMap = []
                  kfBones = []
                  bs.seek(animOffsets[i][0], NOESEEK_ABS)
                  mapByteSize = bs.readUShort() & 0x3FFF
                  mapSize = math.ceil(mapByteSize / 4)
                  gblFrameCount = bs.readUShort()
                  bs.seek(animOffsets[i][1], NOESEEK_ABS)
                  for a in range(0, int(math.ceil(mapSize / 2))):
                        mapSet = bin(bs.readUShort())[2:].zfill(16)
                        animMap.append(mapSet[14:])
                        animMap.append(mapSet[12:14])
                        animMap.append(mapSet[10:12])
                        animMap.append(mapSet[8:10])
                        animMap.append(mapSet[6:8])
                        animMap.append(mapSet[4:6])
                        animMap.append(mapSet[2:4])
                        animMap.append(mapSet[:2])
                  animMap = animMap[:mapByteSize - 1]
                  #00 = None 01 = Pose 10 = Linear 11 = Interp
                  keyFrames = []
                  bs.seek(animOffsets[i][2], NOESEEK_ABS)
                  for a in range(0, len(animMap)):
                        if animMap[a] == "00":
                              keyFrames.append(None)
                        elif animMap[a] == "01":
                              keyFrames.append([bs.readFloat()] * gblFrameCount)
                        elif animMap[a] == "10":
                              frameCount = bs.readUShort()
                              keyFrameIndex = bs.read(frameCount * "H")
                              self.padding4(bs)
                              ikf = []
                              for b in range(0, frameCount):
                                    if b != 0:
                                          if keyFrameIndex[b] == keyFrameIndex[b-1]:
                                                del ikf[-1]
                                                ikf.append(bs.readFloat())
                                          elif keyFrameIndex[b] != keyFrameIndex[b-1] + 1:
                                                kf = bs.readFloat()
                                                n = (keyFrameIndex[b] - keyFrameIndex[b-1])
                                                pkf = ikf[-1]
                                                for c in range(1, n):
                                                      f = c / n
                                                      rf = keyFrameIndex[b-1] + c
                                                      nkf = ((((f * 2.0) - 3.0) * (f * f)) * (pkf - kf)) + pkf
                                                      ikf.append(nkf)
                                                ikf.append(kf)
                                          else:
                                                ikf.append(bs.readFloat())
                                    elif b == 0 and keyFrameIndex[b] != 0:
                                          kf = bs.readFloat()
                                          for c in range(0, keyFrameIndex[b]):
                                                ikf.append(kf)
                                          ikf.append(kf)
                                    else:
                                          ikf.append(bs.readFloat())
                              for b in range(keyFrameIndex[-1] + 1, gblFrameCount):
                                    ikf.append(ikf[-1])
                              keyFrames.append(ikf)
                        elif animMap[a] == "11":
                              frameCount = bs.readUShort()
                              keyFrameIndex = bs.read(frameCount * "H")
                              self.padding4(bs)
                              ikf = []
                              iv = []
                              for b in range(0, frameCount):
                                    if b != 0:
                                          if keyFrameIndex[b] == keyFrameIndex[b-1]:
                                                del ikf[-1]
                                                del iv[-1]
                                                ikf.append(bs.readFloat())
                                                iv.append(bs.readFloat())
                                          elif keyFrameIndex[b] != keyFrameIndex[b-1] + 1:
                                                kf = bs.readFloat()
                                                ik = bs.readFloat()
                                                n = (keyFrameIndex[b] - keyFrameIndex[b-1])
                                                pkf = ikf[-1]
                                                pik = iv[-1]
                                                for c in range(1, n):
                                                      f = c / n
                                                      rf = keyFrameIndex[b-1] + c
                                                      nkf = ((((((f - 1) * 2) - 1) * (f * f)) * (pkf - kf)) + (((((f - 1) * pik) + (f * ik)) * (f - 1)) * (rf - keyFrameIndex[b-1]))) + pkf
                                                      ikf.append(nkf)
                                                      iv.append(ik)
                                                ikf.append(kf)
                                                iv.append(ik)
                                          else:
                                                ikf.append(bs.readFloat())
                                                iv.append(bs.readFloat())
                                    elif b == 0 and keyFrameIndex[b] != 0:
                                          kf = bs.readFloat()
                                          ik = bs.readFloat()
                                          for c in range(0, keyFrameIndex[b]):
                                                ikf.append(kf)
                                                iv.append(ik)
                                          ikf.append(kf)
                                          iv.append(ik)
                                    else:
                                          ikf.append(bs.readFloat())
                                          iv.append(bs.readFloat())
                              for b in range(keyFrameIndex[-1] + 1, gblFrameCount):
                                    ikf.append(ikf[-1])
                              keyFrames.append(ikf)
                  boneNames = []
                  bs.seek(animOffsets[i][3], NOESEEK_ABS)
                  for a in range(0, int(len(animMap) / 3) - 1):
                        boneIndex = bs.readUShort()
                        boneNames.append(self.mot_db[1][boneIndex])
                  ptr = 0
                  if motImportOption == 0:
                        usedBones = ["n_hara_cp", "kg_hara_y", "kl_hara_xz", "kl_hara_etc", "e_mune_cp", "cl_mune", "kl_mune_b_wj", "kl_kubi", "e_kao_cp", "cl_kao", "kl_ago_wj", "tl_tooth_under_wj",
                                    "kl_eye_l_wj", "kl_eye_r_wj", "tl_eyelid_l_a_wj", "tl_eyelid_l_b_wj", "tl_eyelid_r_a_wj", "tl_eyelid_r_b_wj", "tl_kuti_d_wj",
                                    "tl_kuti_d_l_wj", "tl_kuti_d_r_wj", "tl_kuti_ds_l_wj", "tl_kuti_ds_r_wj", "tl_kuti_l_wj", "tl_kuti_m_l_wj", "tl_kuti_m_r_wj", "tl_kuti_r_wj", "tl_kuti_u_wj",
                                    "tl_kuti_u_l_wj", "tl_kuti_u_r_wj", "tl_mabu_l_d_a_wj", "tl_mabu_l_d_b_wj", "tl_mabu_l_d_c_wj", "tl_mabu_l_u_a_wj", "tl_mabu_l_u_b_wj", "tl_eyelashes_l_wj",
                                    "tl_mabu_l_u_c_wj", "tl_mabu_r_d_a_wj", "tl_mabu_r_d_b_wj", "tl_mabu_r_d_c_wj", "tl_mabu_r_u_a_wj", "tl_mabu_r_u_b_wj", "tl_eyelashes_r_wj", "tl_mabu_r_u_c_wj",
                                    "tl_mayu_l_wj", "tl_mayu_l_b_wj", "tl_mayu_l_c_wj", "tl_mayu_r_wj", "tl_mayu_r_b_wj", "tl_mayu_r_c_wj", "tl_tooth_upper_wj", "kl_waki_l_wj", "e_ude_l_cp",
                                    "kl_te_l_wj", "nl_hito_l_wj", "nl_hito_b_l_wj", "nl_hito_c_l_wj", "nl_ko_l_wj", "nl_ko_b_l_wj", "nl_ko_c_l_wj", "nl_kusu_l_wj", "nl_kusu_b_l_wj", "nl_kusu_c_l_wj",
                                    "nl_naka_l_wj", "nl_naka_b_l_wj", "nl_naka_c_l_wj", "nl_oya_l_wj", "nl_oya_b_l_wj", "nl_oya_c_l_wj", "kl_waki_r_wj", "e_ude_r_cp", "kl_te_r_wj", "nl_hito_r_wj",
                                    "nl_hito_b_r_wj", "nl_hito_c_r_wj", "nl_ko_r_wj", "nl_ko_b_r_wj", "nl_ko_c_r_wj", "nl_kusu_r_wj", "nl_kusu_b_r_wj", "nl_kusu_c_r_wj", "nl_naka_r_wj", "nl_naka_b_r_wj",
                                    "nl_naka_c_r_wj", "nl_oya_r_wj", "nl_oya_b_r_wj", "nl_oya_c_r_wj", "tl_up_kata_l", "tl_up_kata_r", "kl_kosi_y", "kl_kosi_xz", "kl_kosi_etc_wj", "e_sune_l_cp", "cl_momo_l",
                                    "kl_asi_l_wj_co", "kl_toe_l_wj", "e_sune_r_cp", "cl_momo_r", "kl_asi_r_wj_co", "kl_toe_r_wj", "gblctr", "kg_ya_ex"]
                  else:
                        usedBones = ["n_hara_cp", "kg_hara_y", "kl_hara_xz", "kl_hara_etc", "e_mune_cp", "cl_mune", "kl_mune_b_wj", "kl_kubi", "e_kao_cp", "cl_kao", "kl_ago_wj", "tl_tooth_under_wj",
                                    "kl_eye_l", "kl_highlight_l_wj", "kl_eye_r", "kl_highlight_r_wj", "tl_eyelid_l_a_wj", "tl_eyelid_l_b_wj", "tl_eyelid_r_a_wj", "tl_eyelid_r_b_wj", "tl_kuti_d_wj",
                                    "tl_kuti_d_l_wj", "tl_kuti_d_r_wj", "tl_kuti_ds_l_wj", "tl_kuti_ds_r_wj", "tl_kuti_l_wj", "tl_kuti_m_l_wj", "tl_kuti_m_r_wj", "tl_kuti_r_wj", "tl_kuti_u_wj",
                                    "tl_kuti_u_l_wj", "tl_kuti_u_r_wj", "tl_mabu_l_d_a_wj", "tl_mabu_l_d_b_wj", "tl_mabu_l_d_c_wj", "tl_mabu_l_u_a_wj", "tl_mabu_l_u_b_wj", "tl_eyelashes_l_wj",
                                    "tl_mabu_l_u_c_wj", "tl_mabu_r_d_a_wj", "tl_mabu_r_d_b_wj", "tl_mabu_r_d_c_wj", "tl_mabu_r_u_a_wj", "tl_mabu_r_u_b_wj", "tl_eyelashes_r_wj", "tl_mabu_r_u_c_wj",
                                    "tl_mayu_l_wj", "tl_mayu_l_b_wj", "tl_mayu_l_c_wj", "tl_mayu_r_wj", "tl_mayu_r_b_wj", "tl_mayu_r_c_wj", "tl_tooth_upper_wj", "kl_waki_l_wj", "e_ude_l_cp",
                                    "kl_te_l_wj", "nl_hito_l_wj", "nl_hito_b_l_wj", "nl_hito_c_l_wj", "nl_ko_l_wj", "nl_ko_b_l_wj", "nl_ko_c_l_wj", "nl_kusu_l_wj", "nl_kusu_b_l_wj", "nl_kusu_c_l_wj",
                                    "nl_naka_l_wj", "nl_naka_b_l_wj", "nl_naka_c_l_wj", "nl_oya_l_wj", "nl_oya_b_l_wj", "nl_oya_c_l_wj", "kl_waki_r_wj", "e_ude_r_cp", "kl_te_r_wj", "nl_hito_r_wj",
                                    "nl_hito_b_r_wj", "nl_hito_c_r_wj", "nl_ko_r_wj", "nl_ko_b_r_wj", "nl_ko_c_r_wj", "nl_kusu_r_wj", "nl_kusu_b_r_wj", "nl_kusu_c_r_wj", "nl_naka_r_wj", "nl_naka_b_r_wj",
                                    "nl_naka_c_r_wj", "nl_oya_r_wj", "nl_oya_b_r_wj", "nl_oya_c_r_wj", "tl_up_kata_l", "tl_up_kata_r", "kl_kosi_y", "kl_kosi_xz", "kl_kosi_etc_wj", "e_sune_l_cp", "cl_momo_l",
                                    "kl_asi_l_wj_co", "kl_toe_l_wj", "e_sune_r_cp", "cl_momo_r", "kl_asi_r_wj_co", "kl_toe_r_wj", "gblctr", "kg_ya_ex"]
                  for a in range(0, len(boneNames)):
                        if keyFrames[ptr] != None or keyFrames[ptr + 1] != None or keyFrames[ptr + 2] != None:
                              if boneNames[a] in self.boneNList and boneNames[a] in usedBones:
                                    boneKey = NoeKeyFramedBone(self.boneNList.index(boneNames[a]))
                                    try:
                                          if self.bone_data[2][boneNames[a]][0] & 0x02:
                                                if self.bone_data[2][boneNames[a]][0] & 0x04:
                                                      rotKeys = []
                                                      if keyFrames[ptr] != None:
                                                            x = keyFrames[ptr]
                                                      else:
                                                            x = [0] * gblFrameCount
                                                      if keyFrames[ptr + 1] != None:
                                                            y = keyFrames[ptr + 1]
                                                      else:
                                                            y = [0] * gblFrameCount
                                                      if keyFrames[ptr + 2] != None:
                                                            z = keyFrames[ptr + 2]
                                                      else:
                                                            z = [0] * gblFrameCount
                                                      for b in range(0, gblFrameCount):
                                                            fix = (self.boneList[self.boneNList.index(boneNames[a])]._matrix * self.boneList[self.boneList[self.boneNList.index(boneNames[a])].parentIndex]._matrix.inverse()).toAngles()
                                                            rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                      #buffer frame
                                                      rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                      boneKey.setRotation(rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                                                else:
                                                      posKeys = []
                                                      if keyFrames[ptr] != None:
                                                            x = keyFrames[ptr]
                                                      else:
                                                            x = [0] * gblFrameCount
                                                      if keyFrames[ptr + 1] != None:
                                                            y = keyFrames[ptr + 1]
                                                      else:
                                                            y = [0] * gblFrameCount
                                                      if keyFrames[ptr + 2] != None:
                                                            z = keyFrames[ptr + 2]
                                                      else:
                                                            z = [0] * gblFrameCount
                                                      for b in range(0, gblFrameCount):
                                                            posKeys.append(NoeKeyFramedValue(b, (x[b], y[b], z[b])))
                                                      #buffer frame
                                                      posKeys.append(NoeKeyFramedValue(gblFrameCount, (x[-1], y[-1], z[-1])))
                                                      boneKey.setTranslation(posKeys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
                                                if self.bone_data[2][boneNames[a]][0] & 0x01:
                                                      ptr += 3
                                                kfBones.append(boneKey)
                                          else:
                                                rotKeys = []
                                                if keyFrames[ptr] != None:
                                                      x = keyFrames[ptr]
                                                else:
                                                      x = [0] * gblFrameCount
                                                if keyFrames[ptr + 1] != None:
                                                      y = keyFrames[ptr + 1]
                                                else:
                                                      y = [0] * gblFrameCount
                                                if keyFrames[ptr + 2] != None:
                                                      z = keyFrames[ptr + 2]
                                                else:
                                                      z = [0] * gblFrameCount
                                                for b in range(0, gblFrameCount):
                                                      fix = (self.boneList[self.boneNList.index(boneNames[a])]._matrix * self.boneList[self.boneList[self.boneNList.index(boneNames[a])].parentIndex]._matrix.inverse()).toAngles()
                                                      if boneNames[a] == "cl_kao":
                                                            rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                      else:
                                                            rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                #buffer frame
                                                if boneNames[a] == "cl_kao":
                                                      rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                else:
                                                      rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                boneKey.setRotation(rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                                                kfBones.append(boneKey)
                                    except:
                                          if boneNames[a].endswith("_cp") or boneNames[a] == "gblctr":
                                                posKeys = []
                                                if keyFrames[ptr] != None:
                                                      x = keyFrames[ptr]
                                                else:
                                                      x = [0] * gblFrameCount
                                                if keyFrames[ptr + 1] != None:
                                                      y = keyFrames[ptr + 1]
                                                else:
                                                      y = [0] * gblFrameCount
                                                if keyFrames[ptr + 2] != None:
                                                      z = keyFrames[ptr + 2]
                                                else:
                                                      z = [0] * gblFrameCount
                                                for b in range(0, gblFrameCount):
                                                      posKeys.append(NoeKeyFramedValue(b, (x[b], y[b], z[b])))
                                                #buffer frame
                                                posKeys.append(NoeKeyFramedValue(gblFrameCount, (x[-1], y[-1], z[-1])))
                                                boneKey.setTranslation(posKeys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
                                          else:
                                                rotKeys = []
                                                if keyFrames[ptr] != None:
                                                      x = keyFrames[ptr]
                                                else:
                                                      x = [0] * gblFrameCount
                                                if keyFrames[ptr + 1] != None:
                                                      y = keyFrames[ptr + 1]
                                                else:
                                                      y = [0] * gblFrameCount
                                                if keyFrames[ptr + 2] != None:
                                                      z = keyFrames[ptr + 2]
                                                else:
                                                      z = [0] * gblFrameCount
                                                for b in range(0, gblFrameCount):
                                                      fix = (self.boneList[self.boneNList.index(boneNames[a])]._matrix * self.boneList[self.boneList[self.boneNList.index(boneNames[a])].parentIndex]._matrix.inverse()).toAngles()
                                                      rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                #buffer frame
                                                rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                boneKey.setRotation(rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                                          kfBones.append(boneKey)
                        ptr += 3
                  self.animList.append(NoeKeyFramedAnim(self.mot_db[0][motName][1][i], self.boneList, kfBones, 1.0))
      
      def readMotAnim(self, motAnim):
            if motImportOption == 3:
                  kfBones = []
                  bs = NoeBitStream(motAnim, 1)
                  bs.seek(0x8, NOESEEK_REL)
                  offset = bs.read("I")
                  bs.seek(offset[0], NOESEEK_ABS)
                  ID = bs.readUInt64()
                  animOffsets = bs.read(">7I")
                  divFrameCount = bs.readUShort()
                  divFileCount = bs.readUByte()
                  bs.seek(animOffsets[0], NOESEEK_ABS)
                  animName = bs.readString()
                  animMap = []
                  bs.seek(animOffsets[1], NOESEEK_ABS)
                  mapByteSize = bs.readUShort() & 0x3FFF
                  mapSize = math.ceil(mapByteSize / 4)
                  gblFrameCount = bs.readUShort()
                  bs.seek(animOffsets[2], NOESEEK_ABS)
                  for i in range(0, int(math.ceil(mapSize / 2))):
                        mapSet = bin(bs.readUShort())[2:].zfill(16)
                        animMap.append(mapSet[14:])
                        animMap.append(mapSet[12:14])
                        animMap.append(mapSet[10:12])
                        animMap.append(mapSet[8:10])
                        animMap.append(mapSet[6:8])
                        animMap.append(mapSet[4:6])
                        animMap.append(mapSet[2:4])
                        animMap.append(mapSet[:2])
                  animMap = animMap[:mapByteSize - 1]
                  boneNames = []
                  bs.seek(animOffsets[4], NOESEEK_ABS)
                  for i in range(0, animOffsets[6]):
                        nameOff = bs.readUInt()
                        cur = bs.tell()
                        bs.seek(nameOff, NOESEEK_ABS)
                        boneNames.append(bs.readString())
                        bs.seek(cur, NOESEEK_ABS)
                  keyFrames = []
                  location = {}
                  for i in range(0, len(animMap)):
                        keyFrameIndex = []
                        interpFrames = []
                        frames = []
                        for a in range(0, divFileCount):
                              divInterpFrames = []
                              divKeyFrames = []
                              if a == 0:
                                    divFrameIndex = []
                              divFrameIndex2 = []
                              if a == 0:
                                    div = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "mot" + os.sep + motName + motID + ".mot")
                              else:
                                    div = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "mot" + os.sep + motName + motID + "_div_" + str(a) + ".mot")
                              bs = NoeBitStream(div, 1)
                              if i == 0:
                                    bs.seek(animOffsets[3], NOESEEK_ABS)
                              else:
                                    bs.seek(location[a], NOESEEK_ABS)
                              if animMap[i] == "00":
                                    if a == 0:
                                          keyFrames.append(None)
                              elif animMap[i] == "01":
                                    if a == 0:
                                          keyFrames.append([bs.readFloat()] * gblFrameCount)
                                    else:
                                          bs.seek(0x4, NOESEEK_REL)
                              elif animMap[i] == "10":
                                    frameCount = bs.readUShort()
                                    animType = bs.readUShort()
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          if animType == 0:
                                                divKeyFrames.append(bs.readFloat())
                                          elif animType == 1:
                                                divKeyFrames.append(bs.readHalfFloat())
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          fi = bs.readUShort()
                                          if a == 0:
                                                divFrameIndex.append(fi)
                                                keyFrameIndex.append(fi)
                                                frames.append(divKeyFrames[b])
                                          else:
                                                divFrameIndex2.append(fi)
                                                if fi not in divFrameIndex:
                                                      keyFrameIndex.append(fi)
                                                      frames.append(divKeyFrames[b])
                                    self.padding4(bs)
                                    if a != 0:
                                          divFrameIndex = divFrameIndex2
                              elif animMap[i] == "11":
                                    frameCount = bs.readUShort()
                                    animType = bs.readUShort()
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          divInterpFrames.append(bs.readFloat())
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          if animType == 0:
                                                divKeyFrames.append(bs.readFloat())
                                          elif animType == 1:
                                                divKeyFrames.append(bs.readHalfFloat())
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          fi = bs.readUShort()
                                          if a == 0:
                                                divFrameIndex.append(fi)
                                                keyFrameIndex.append(fi)
                                                interpFrames.append(divInterpFrames[b])
                                                frames.append(divKeyFrames[b])
                                          else:
                                                divFrameIndex2.append(fi)
                                                if fi not in divFrameIndex:
                                                      keyFrameIndex.append(fi)
                                                      interpFrames.append(divInterpFrames[b])
                                                      frames.append(divKeyFrames[b])
                                    self.padding4(bs)
                                    if a != 0:
                                          divFrameIndex = divFrameIndex2
                              location[a] = bs.tell()
                        if animMap[i] == "10":
                              ikf = []
                              for b in range(0, len(keyFrameIndex)):
                                    if b != 0:
                                          if keyFrameIndex[b] == keyFrameIndex[b-1]:
                                                del ikf[-1]
                                                ikf.append(frames[b])
                                          elif keyFrameIndex[b] != keyFrameIndex[b-1] + 1:
                                                kf = frames[b]
                                                n = (keyFrameIndex[b] - keyFrameIndex[b-1])
                                                pkf = ikf[-1]
                                                for c in range(1, n):
                                                      f = c / n
                                                      rf = keyFrameIndex[b-1] + c
                                                      nkf = ((((f * 2.0) - 3.0) * (f * f)) * (pkf - kf)) + pkf
                                                      ikf.append(nkf)
                                                ikf.append(kf)
                                          else:
                                                ikf.append(frames[b])
                                    elif b == 0 and keyFrameIndex[b] != 0:
                                          kf = frames[b]
                                          for c in range(0, keyFrameIndex[b]):
                                                ikf.append(kf)
                                          ikf.append(kf)
                                    else:
                                          ikf.append(frames[b])
                              for b in range(keyFrameIndex[-1] + 1, gblFrameCount):
                                    ikf.append(ikf[-1])
                              keyFrames.append(ikf)
                        elif animMap[i] == "11":
                              ikf = []
                              iv = []
                              for b in range(0, len(keyFrameIndex)):
                                    if b != 0:
                                          if keyFrameIndex[b] == keyFrameIndex[b-1]:
                                                del ikf[-1]
                                                del iv[-1]
                                                ikf.append(frames[b])
                                                iv.append(interpFrames[b])
                                          elif keyFrameIndex[b] != keyFrameIndex[b-1] + 1:
                                                kf = frames[b]
                                                ik = interpFrames[b]
                                                n = (keyFrameIndex[b] - keyFrameIndex[b-1])
                                                pkf = ikf[-1]
                                                pik = iv[-1]
                                                for c in range(1, n):
                                                      f = c / n
                                                      rf = keyFrameIndex[b-1] + c
                                                      nkf = ((((((f - 1) * 2) - 1) * (f * f)) * (pkf - kf)) + (((((f - 1) * pik) + (f * ik)) * (f - 1)) * (rf - keyFrameIndex[b-1]))) + pkf
                                                      ikf.append(nkf)
                                                      iv.append(ik)
                                                ikf.append(kf)
                                                iv.append(ik)
                                          else:
                                                ikf.append(frames[b])
                                                iv.append(interpFrames[b])
                                    elif b == 0 and keyFrameIndex[b] != 0:
                                          kf = frames[b]
                                          ik = interpFrames[b]
                                          for c in range(0, keyFrameIndex[b]):
                                                ikf.append(kf)
                                                iv.append(ik)
                                          ikf.append(kf)
                                          iv.append(ik)
                                    else:
                                          ikf.append(frames[b])
                                          iv.append(interpFrames[b])
                              for b in range(keyFrameIndex[-1] + 1, gblFrameCount):
                                    ikf.append(ikf[-1])
                              keyFrames.append(ikf)
            else:
                  kfBones = []
                  bs = NoeBitStream(motAnim)
                  bs.seek(0x8, NOESEEK_REL)
                  offset = bs.readUInt()
                  bs.seek(offset, NOESEEK_ABS)
                  ID = bs.readUInt64()
                  animOffsets = bs.read("6QI")
                  divFrameCount = bs.readUShort()
                  divFileCount = bs.readUByte()
                  bs.seek(animOffsets[0] + offset, NOESEEK_ABS)
                  animName = bs.readString()
                  animMap = []
                  bs.seek(animOffsets[1] + offset, NOESEEK_ABS)
                  mapByteSize = bs.readUShort() & 0x3FFF
                  mapSize = math.ceil(mapByteSize / 4)
                  gblFrameCount = bs.readUShort()
                  bs.seek(animOffsets[2] + offset, NOESEEK_ABS)
                  for i in range(0, int(math.ceil(mapSize / 2))):
                        mapSet = bin(bs.readUShort())[2:].zfill(16)
                        animMap.append(mapSet[14:])
                        animMap.append(mapSet[12:14])
                        animMap.append(mapSet[10:12])
                        animMap.append(mapSet[8:10])
                        animMap.append(mapSet[6:8])
                        animMap.append(mapSet[4:6])
                        animMap.append(mapSet[2:4])
                        animMap.append(mapSet[:2])
                  animMap = animMap[:mapByteSize - 1]
                  boneNames = []
                  bs.seek(animOffsets[4] + offset, NOESEEK_ABS)
                  for i in range(0, animOffsets[6]):
                        nameOff = bs.readUInt64()
                        cur = bs.tell()
                        bs.seek(nameOff + offset, NOESEEK_ABS)
                        boneNames.append(bs.readString())
                        bs.seek(cur, NOESEEK_ABS)
                  keyFrames = []
                  location = {}
                  for i in range(0, len(animMap)):
                        keyFrameIndex = []
                        interpFrames = []
                        frames = []
                        for a in range(0, divFileCount):
                              divInterpFrames = []
                              divKeyFrames = []
                              if a == 0:
                                    divFrameIndex = []
                              divFrameIndex2 = []
                              if a == 0:
                                    div = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "mot" + os.sep + motName + motID + ".mot")
                              else:
                                    div = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getLastCheckedName())[:-7] + "mot" + os.sep + motName + motID + "_div_" + str(a) + ".mot")
                              bs = NoeBitStream(div)
                              if i == 0:
                                    bs.seek(animOffsets[3] + offset, NOESEEK_ABS)
                              else:
                                    bs.seek(location[a], NOESEEK_ABS)
                              if animMap[i] == "00":
                                    if a == 0:
                                          keyFrames.append(None)
                              elif animMap[i] == "01":
                                    if a == 0:
                                          keyFrames.append([bs.readFloat()] * gblFrameCount)
                                    else:
                                          bs.seek(0x4, NOESEEK_REL)
                              elif animMap[i] == "10":
                                    frameCount = bs.readUShort()
                                    animType = bs.readUShort()
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          if animType == 0:
                                                divKeyFrames.append(bs.readFloat())
                                          elif animType == 1:
                                                divKeyFrames.append(bs.readHalfFloat())
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          fi = bs.readUShort()
                                          if a == 0:
                                                divFrameIndex.append(fi)
                                                keyFrameIndex.append(fi)
                                                frames.append(divKeyFrames[b])
                                          else:
                                                divFrameIndex2.append(fi)
                                                if fi not in divFrameIndex:
                                                      keyFrameIndex.append(fi)
                                                      frames.append(divKeyFrames[b])
                                    self.padding4(bs)
                                    if a != 0:
                                          divFrameIndex = divFrameIndex2
                              elif animMap[i] == "11":
                                    frameCount = bs.readUShort()
                                    animType = bs.readUShort()
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          divInterpFrames.append(bs.readFloat())
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          if animType == 0:
                                                divKeyFrames.append(bs.readFloat())
                                          elif animType == 1:
                                                divKeyFrames.append(bs.readHalfFloat())
                                    self.padding4(bs)
                                    for b in range(0, frameCount):
                                          fi = bs.readUShort()
                                          if a == 0:
                                                divFrameIndex.append(fi)
                                                keyFrameIndex.append(fi)
                                                interpFrames.append(divInterpFrames[b])
                                                frames.append(divKeyFrames[b])
                                          else:
                                                divFrameIndex2.append(fi)
                                                if fi not in divFrameIndex:
                                                      keyFrameIndex.append(fi)
                                                      interpFrames.append(divInterpFrames[b])
                                                      frames.append(divKeyFrames[b])
                                    self.padding4(bs)
                                    if a != 0:
                                          divFrameIndex = divFrameIndex2
                              location[a] = bs.tell()
                        if animMap[i] == "10":
                              ikf = []
                              for b in range(0, len(keyFrameIndex)):
                                    if b != 0:
                                          if keyFrameIndex[b] == keyFrameIndex[b-1]:
                                                del ikf[-1]
                                                ikf.append(frames[b])
                                          elif keyFrameIndex[b] != keyFrameIndex[b-1] + 1:
                                                kf = frames[b]
                                                n = (keyFrameIndex[b] - keyFrameIndex[b-1])
                                                pkf = ikf[-1]
                                                for c in range(1, n):
                                                      f = c / n
                                                      rf = keyFrameIndex[b-1] + c
                                                      nkf = ((((f * 2.0) - 3.0) * (f * f)) * (pkf - kf)) + pkf
                                                      ikf.append(nkf)
                                                ikf.append(kf)
                                          else:
                                                ikf.append(frames[b])
                                    elif b == 0 and keyFrameIndex[b] != 0:
                                          kf = frames[b]
                                          for c in range(0, keyFrameIndex[b]):
                                                ikf.append(kf)
                                          ikf.append(kf)
                                    else:
                                          ikf.append(frames[b])
                              for b in range(keyFrameIndex[-1] + 1, gblFrameCount):
                                    ikf.append(ikf[-1])
                              keyFrames.append(ikf)
                        elif animMap[i] == "11":
                              ikf = []
                              iv = []
                              for b in range(0, len(keyFrameIndex)):
                                    if b != 0:
                                          if keyFrameIndex[b] == keyFrameIndex[b-1]:
                                                del ikf[-1]
                                                del iv[-1]
                                                ikf.append(frames[b])
                                                iv.append(interpFrames[b])
                                          elif keyFrameIndex[b] != keyFrameIndex[b-1] + 1:
                                                kf = frames[b]
                                                ik = interpFrames[b]
                                                n = (keyFrameIndex[b] - keyFrameIndex[b-1])
                                                pkf = ikf[-1]
                                                pik = iv[-1]
                                                for c in range(1, n):
                                                      f = c / n
                                                      rf = keyFrameIndex[b-1] + c
                                                      nkf = ((((((f - 1) * 2) - 1) * (f * f)) * (pkf - kf)) + (((((f - 1) * pik) + (f * ik)) * (f - 1)) * (rf - keyFrameIndex[b-1]))) + pkf
                                                      ikf.append(nkf)
                                                      iv.append(ik)
                                                ikf.append(kf)
                                                iv.append(ik)
                                          else:
                                                ikf.append(frames[b])
                                                iv.append(interpFrames[b])
                                    elif b == 0 and keyFrameIndex[b] != 0:
                                          kf = frames[b]
                                          ik = interpFrames[b]
                                          for c in range(0, keyFrameIndex[b]):
                                                ikf.append(kf)
                                                iv.append(ik)
                                          ikf.append(kf)
                                          iv.append(ik)
                                    else:
                                          ikf.append(frames[b])
                                          iv.append(interpFrames[b])
                              for b in range(keyFrameIndex[-1] + 1, gblFrameCount):
                                    ikf.append(ikf[-1])
                              keyFrames.append(ikf)
            ptr = 0
            usedBones = ["n_hara_cp", "kg_hara_y", "kl_hara_xz", "kl_hara_etc", "e_mune_cp", "cl_mune", "kl_mune_b_wj", "kl_kubi", "e_kao_cp", "cl_kao", "kl_ago_wj", "tl_tooth_under_wj",
                              "kl_eye_l", "kl_highlight_l_wj", "kl_eye_r", "kl_highlight_r_wj", "tl_eyelid_l_a_wj", "tl_eyelid_l_b_wj", "tl_eyelid_r_a_wj", "tl_eyelid_r_b_wj", "tl_kuti_d_wj",
                              "tl_kuti_d_l_wj", "tl_kuti_d_r_wj", "tl_kuti_ds_l_wj", "tl_kuti_ds_r_wj", "tl_kuti_l_wj", "tl_kuti_m_l_wj", "tl_kuti_m_r_wj", "tl_kuti_r_wj", "tl_kuti_u_wj",
                              "tl_kuti_u_l_wj", "tl_kuti_u_r_wj", "tl_mabu_l_d_a_wj", "tl_mabu_l_d_b_wj", "tl_mabu_l_d_c_wj", "tl_mabu_l_u_a_wj", "tl_mabu_l_u_b_wj", "tl_eyelashes_l_wj",
                              "tl_mabu_l_u_c_wj", "tl_mabu_r_d_a_wj", "tl_mabu_r_d_b_wj", "tl_mabu_r_d_c_wj", "tl_mabu_r_u_a_wj", "tl_mabu_r_u_b_wj", "tl_eyelashes_r_wj", "tl_mabu_r_u_c_wj",
                              "tl_mayu_l_wj", "tl_mayu_l_b_wj", "tl_mayu_l_c_wj", "tl_mayu_r_wj", "tl_mayu_r_b_wj", "tl_mayu_r_c_wj", "tl_tooth_upper_wj", "kl_waki_l_wj", "e_ude_l_cp",
                              "kl_te_l_wj", "nl_hito_l_wj", "nl_hito_b_l_wj", "nl_hito_c_l_wj", "nl_ko_l_wj", "nl_ko_b_l_wj", "nl_ko_c_l_wj", "nl_kusu_l_wj", "nl_kusu_b_l_wj", "nl_kusu_c_l_wj",
                              "nl_naka_l_wj", "nl_naka_b_l_wj", "nl_naka_c_l_wj", "nl_oya_l_wj", "nl_oya_b_l_wj", "nl_oya_c_l_wj", "kl_waki_r_wj", "e_ude_r_cp", "kl_te_r_wj", "nl_hito_r_wj",
                              "nl_hito_b_r_wj", "nl_hito_c_r_wj", "nl_ko_r_wj", "nl_ko_b_r_wj", "nl_ko_c_r_wj", "nl_kusu_r_wj", "nl_kusu_b_r_wj", "nl_kusu_c_r_wj", "nl_naka_r_wj", "nl_naka_b_r_wj",
                              "nl_naka_c_r_wj", "nl_oya_r_wj", "nl_oya_b_r_wj", "nl_oya_c_r_wj", "tl_up_kata_l", "tl_up_kata_r", "kl_kosi_y", "kl_kosi_xz", "kl_kosi_etc_wj", "e_sune_l_cp", "cl_momo_l",
                              "kl_asi_l_wj_co", "kl_toe_l_wj", "e_sune_r_cp", "cl_momo_r", "kl_asi_r_wj_co", "kl_toe_r_wj", "gblctr", "kg_ya_ex"]
            for a in range(0, len(boneNames)):
                  if keyFrames[ptr] != None or keyFrames[ptr + 1] != None or keyFrames[ptr + 2] != None:
                        if boneNames[a] in self.boneNList and boneNames[a] in usedBones:
                              boneKey = NoeKeyFramedBone(self.boneNList.index(boneNames[a]))
                              try:
                                    if self.bone_data[2][boneNames[a]][0] & 0x02:
                                          if self.bone_data[2][boneNames[a]][0] & 0x04:
                                                rotKeys = []
                                                if keyFrames[ptr] != None:
                                                      x = keyFrames[ptr]
                                                else:
                                                      x = [0] * gblFrameCount
                                                if keyFrames[ptr + 1] != None:
                                                      y = keyFrames[ptr + 1]
                                                else:
                                                      y = [0] * gblFrameCount
                                                if keyFrames[ptr + 2] != None:
                                                      z = keyFrames[ptr + 2]
                                                else:
                                                      z = [0] * gblFrameCount
                                                for b in range(0, gblFrameCount):
                                                      fix = (self.boneList[self.boneNList.index(boneNames[a])]._matrix * self.boneList[self.boneList[self.boneNList.index(boneNames[a])].parentIndex]._matrix.inverse()).toAngles()
                                                      rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                #buffer frame
                                                rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                boneKey.setRotation(rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                                          else:
                                                posKeys = []
                                                if keyFrames[ptr] != None:
                                                      x = keyFrames[ptr]
                                                else:
                                                      x = [0] * gblFrameCount
                                                if keyFrames[ptr + 1] != None:
                                                      y = keyFrames[ptr + 1]
                                                else:
                                                      y = [0] * gblFrameCount
                                                if keyFrames[ptr + 2] != None:
                                                      z = keyFrames[ptr + 2]
                                                else:
                                                      z = [0] * gblFrameCount
                                                for b in range(0, gblFrameCount):
                                                      posKeys.append(NoeKeyFramedValue(b, (x[b], y[b], z[b])))
                                                #buffer frame
                                                posKeys.append(NoeKeyFramedValue(gblFrameCount, (x[-1], y[-1], z[-1])))
                                                boneKey.setTranslation(posKeys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
                                          if self.bone_data[2][boneNames[a]][0] & 0x01:
                                                ptr += 3
                                          kfBones.append(boneKey)
                                    else:
                                          rotKeys = []
                                          if keyFrames[ptr] != None:
                                                x = keyFrames[ptr]
                                          else:
                                                x = [0] * gblFrameCount
                                          if keyFrames[ptr + 1] != None:
                                                y = keyFrames[ptr + 1]
                                          else:
                                                y = [0] * gblFrameCount
                                          if keyFrames[ptr + 2] != None:
                                                z = keyFrames[ptr + 2]
                                          else:
                                                z = [0] * gblFrameCount
                                          for b in range(0, gblFrameCount):
                                                fix = (self.boneList[self.boneNList.index(boneNames[a])]._matrix * self.boneList[self.boneList[self.boneNList.index(boneNames[a])].parentIndex]._matrix.inverse()).toAngles()
                                                if boneNames[a] == "cl_kao":
                                                      rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                                else:
                                                      rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                          #buffer frame
                                          if boneNames[a] == "cl_kao":
                                                rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                          else:
                                                rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                          boneKey.setRotation(rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                                          kfBones.append(boneKey)
                              except:
                                    if boneNames[a].endswith("_cp") or boneNames[a] == "gblctr":
                                          posKeys = []
                                          if keyFrames[ptr] != None:
                                                x = keyFrames[ptr]
                                          else:
                                                x = [0] * gblFrameCount
                                          if keyFrames[ptr + 1] != None:
                                                y = keyFrames[ptr + 1]
                                          else:
                                                y = [0] * gblFrameCount
                                          if keyFrames[ptr + 2] != None:
                                                z = keyFrames[ptr + 2]
                                          else:
                                                z = [0] * gblFrameCount
                                          for b in range(0, gblFrameCount):
                                                posKeys.append(NoeKeyFramedValue(b, (x[b], y[b], z[b])))
                                          #buffer frame
                                          posKeys.append(NoeKeyFramedValue(gblFrameCount, (x[-1], y[-1], z[-1])))
                                          boneKey.setTranslation(posKeys, noesis.NOEKF_TRANSLATION_VECTOR_3, noesis.NOEKF_INTERPOLATE_LINEAR)
                                    else:
                                          rotKeys = []
                                          if keyFrames[ptr] != None:
                                                x = keyFrames[ptr]
                                          else:
                                                x = [0] * gblFrameCount
                                          if keyFrames[ptr + 1] != None:
                                                y = keyFrames[ptr + 1]
                                          else:
                                                y = [0] * gblFrameCount
                                          if keyFrames[ptr + 2] != None:
                                                z = keyFrames[ptr + 2]
                                          else:
                                                z = [0] * gblFrameCount
                                          for b in range(0, gblFrameCount):
                                                fix = (self.boneList[self.boneNList.index(boneNames[a])]._matrix * self.boneList[self.boneList[self.boneNList.index(boneNames[a])].parentIndex]._matrix.inverse()).toAngles()
                                                rotKeys.append(NoeKeyFramedValue(b, (NoeAngles((x[b]*noesis.g_flRadToDeg, y[b]*noesis.g_flRadToDeg, z[b]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                          #buffer frame
                                          rotKeys.append(NoeKeyFramedValue(gblFrameCount, (NoeAngles((x[-1]*noesis.g_flRadToDeg, y[-1]*noesis.g_flRadToDeg, z[-1]*noesis.g_flRadToDeg)).toMat43_XYZ() * fix.toMat43()).toQuat()))
                                          boneKey.setRotation(rotKeys, noesis.NOEKF_ROTATION_QUATERNION_4, noesis.NOEKF_INTERPOLATE_LINEAR)
                                    kfBones.append(boneKey)
                  ptr += 3
            self.animList.append(NoeKeyFramedAnim(animName, self.boneList, kfBones, 1.0))

      def readBinTex(self, binTex):
            bs = NoeBitStream(binTex)
            txpMagic, txpCount, unk1 = bs.read("3I")
            txpOffs = bs.read(txpCount * "I")
            for i in range(0, txpCount):
                  bs.seek(txpOffs[i], NOESEEK_ABS)
                  txpMagic01, mipCount, unk2, texOff = bs.read("4I")
                  bs.seek(txpOffs[i] + texOff, NOESEEK_ABS)
                  texHeader = bs.read("6I")
                  texData = bs.readBytes(texHeader[5])
                  texFmt = 0
                  name = self.tex_db[self.texID[i]]
                  if texHeader[3] == 1:
                        texFmt = noesis.NOESISTEX_RGB24
                        tex1 = NoeTexture(str(i), texHeader[1], texHeader[2], texData, texFmt)
                        texData = rapi.imageGetTexRGBA(tex1)
                        if "ENVMAP" not in name:
                              texData = rapi.imageFlipRGBA32(texData, texHeader[1], texHeader[2], 0, 1)
                        texFmt = noesis.NOESISTEX_RGBA32
                  elif texHeader[3] == 2:
                        texFmt = noesis.NOESISTEX_RGBA32
                        if "ENVMAP" not in name:
                              texData = rapi.imageFlipRGBA32(texData, texHeader[1], texHeader[2], 0, 1)
                  elif texHeader[3] == 6:
                        texFmt = noesis.NOESISTEX_DXT1
                        texData = rapi.imageDecodeDXT(texData, texHeader[1], texHeader[2], noesis.FOURCC_DXT1)
                        if "ENVMAP" not in name:
                              texData = rapi.imageFlipRGBA32(texData, texHeader[1], texHeader[2], 0, 1)
                        texData = rapi.imageEncodeDXT(texData, 4, texHeader[1], texHeader[2], noesis.NOE_ENCODEDXT_BC1)
                  elif texHeader[3] == 7:
                        texFmt = noesis.NOESISTEX_DXT3
                        texData = rapi.imageDecodeDXT(texData, texHeader[1], texHeader[2], noesis.FOURCC_DXT3)
                        if "ENVMAP" not in name:
                              texData = rapi.imageFlipRGBA32(texData, texHeader[1], texHeader[2], 0, 1)
                        texData = rapi.imageEncodeDXT(texData, 4, texHeader[1], texHeader[2], noesis.NOE_ENCODEDXT_BC3)
                  elif texHeader[3] == 9:
                        texFmt = noesis.NOESISTEX_DXT5
                        texData = rapi.imageDecodeDXT(texData, texHeader[1], texHeader[2], noesis.FOURCC_DXT5)
                        if "ENVMAP" not in name:
                              texData = rapi.imageFlipRGBA32(texData, texHeader[1], texHeader[2], 0, 1)
                        texData = rapi.imageEncodeDXT(texData, 4, texHeader[1], texHeader[2], noesis.NOE_ENCODEDXT_BC3)
                  elif texHeader[3] == 10:
                        texData = rapi.imageDecodeDXT(texData, texHeader[1], texHeader[2], noesis.FOURCC_BC4)
                        if "ENVMAP" not in name:
                              texData = rapi.imageFlipRGBA32(texData, texHeader[1], texHeader[2], 0, 1)
                        texFmt = noesis.NOESISTEX_RGBA32
                  elif texHeader[3] == 11:
                        texData = rapi.imageDecodeDXT(texData, texHeader[1], texHeader[2], noesis.FOURCC_BC5)
                        if "ENVMAP" not in name:
                              texData = rapi.imageFlipRGBA32(texData, texHeader[1], texHeader[2], 0, 1)
                        texFmt = noesis.NOESISTEX_RGBA32
                  tex1 = NoeTexture(name, texHeader[1], texHeader[2], texData, texFmt)
                  self.texList.append(tex1)
            return 1

      def padding4(self, bs):
            offFix = bs.tell()
            while offFix%4 != 0:
                  bs.seek(0x01, NOESEEK_REL)
                  offFix = bs.tell()
            return 1

def objBinLoadModel(data, mdlList):
      ctx = rapi.rpgCreateContext()
      bin = binModel(NoeBitStream(data))
      try:
            mdl = rapi.rpgConstructModel()
      except:
            mdl = NoeModel()
      mdl.setModelMaterials(NoeModelMaterials(bin.texList, bin.matList))
      if bin.animList != []:
            mdl.setAnims(bin.animList)
            rapi.setPreviewOption("setAnimSpeed", "60")
      #bin.boneList = rapi.multiplyBones(bin.boneList)
      mdlList.append(mdl); mdl.setBones(bin.boneList)
      return 1
