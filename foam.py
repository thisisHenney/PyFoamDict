#!/usr/bin/env python
# -*-coding:utf8-*-
# !/bin/bash

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Notice
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 용어 정리
# - Dict    : 모든 앞부분 이름을 가리킴
# - Name    : 하위 딕셔너리가 포함된 Dict를 가리킴
# - Keyword : 하위 딕셔너리가 없는 Dict 를 가리킴
# - Entry   : 하위 딕셔너리가 없는 Dict 의 value를 지칭

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <1> Header
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Common
import os, sys
path_NextLib_PyFoamDict_foam_py = os.path.dirname(os.path.abspath(__file__))

path_NextLib = os.path.abspath(path_NextLib_PyFoamDict_foam_py + "/../..")
sys.path.append(path_NextLib)

# NextLib Module
from NextLib.cmn import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <2> Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class FOAM_DATA_CLASS:
    def __init__(self):
        # Common
        # self.dataName       = ""  # 안쓰므로 삭제
        self.fileName       = ""

        # File Data
        self.readData       = []    # 원본 파일 데이터
        self.pureData       = []    # 주석 제거한 파일 데이터 # Dict Name 찾을 때 필요함, 항상 readData 와 동기화 되어야함
        self.tokenData      = []    # token 데이터 (최소단위로 구분한 데이터)
        self.foamData       = []    # 추출된 모든 데이터
        return

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Main
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # [1] New/End
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def New(self, fileName=""):
        self.fileName = fileName

        # Set
        self.Load()
        return

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # [2] Run
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # [@] Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Check
    def Check(self):
        if not self.fileName or not self.foamData:
            return False
        return True
    # --------------------------------------------------------------------------
    # File
    # --------------------------------------------------------------------------
    # Create (v2.0)
    def Create(self, path="", version="5.x", location="system", object="controlDict"):
        self.fileName = path
        self.readData = Create_FoamHeader(version, location, object)
        self.Save()
        return

    # Load (v2.2)
    def Load(self, bHeader=True):
        # readData
        self.readData = Read_File("%s" % self.fileName)
        self.tokenData = Extract_Data(self.readData)
        self.foamData = Get_FoamData(self.tokenData)
        #
        if not bHeader and len(self.foamData) > 0:
            if len(self.foamData[0]) and self.foamData[0][0] == "FoamFile":
                del self.foamData[0]

        # pureData
        self.pureData = Remove_Comment(self.readData, bStay=True)
        return

    # Save (v2.2)
    def Save(self):
        # Init (줄맞추기 위함)
        self.readData = Replace_String(self.readData, "\n\n\n", "\n\n")
        self.readData = Replace_String(self.readData, "\n\n\n", "\n")

        # Run
        Write_File(self.fileName, self.readData)

        # Update
        self.Load()
        return

    # --------------------------------------------------------------------------
    # Check
    # --------------------------------------------------------------------------
    # IsDict (v2.0)
    def IsDict(self, route=[]):
        # Init
        totalPos = len(route)

        # Check
        if totalPos == 0:
            return False

        for dd in self.foamData:
            if dd[0] == route[0]:
                if totalPos == 1:
                    return True
                else:
                    return self.IsDict_Sub(route, dd)
        return False

    # IsDict_Sub (v2.0)
    def IsDict_Sub(self, route=[], foamData=[]):
        # Check
        if len(route) == 0 or len(foamData) == 0:
            return

        # Init
        subRoute = route[1:]
        subFoamData = foamData[1:]
        totalSubPos = len(subRoute)

        for dd in subFoamData:
            if len(dd) == 0:    # 빈칸이면 내용이 없으므로 False
                return False
            elif dd[0] == subRoute[0]:
                if totalSubPos == 1:
                    return True
                else:
                    return self.IsDict_Sub(subRoute, dd)
        return False

    # --------------------------------------------------------------------------
    # IsName (v2.1)
    def IsName(self, route=[]):
        # Check
        if not self.IsDict(route):
            return

        # Init
        pureData = self.pureData
        bResult = True

        # Find Dict
        endPos = self.Get_Dict_Title_Pos(route)[1]
        if endPos == -1:
            return False

        # Find Brace
        bracePos = Find_BracesSet(pureData, endPos)
        if bracePos == (-1, -1):
            return False

        return bResult

    # --------------------------------------------------------------------------
    # IsKeyword (v2.2)
    def IsKeyword(self, route=[]):
        # Check
        if not self.IsDict(route):
            return

        # Init
        pureData = self.pureData

        # Find Dict
        endPos = self.Get_Dict_Title_Pos(route)[1]
        if endPos == -1:
            return False

        # Check FunctionObject
        if route[-1].find("#") == 0:
            return True

        # Find Brace
        bracePos = Find_BracesSet(pureData, endPos)
        if bracePos == (-1, -1):
            return True

        return False

    # --------------------------------------------------------------------------
    # Common
    # --------------------------------------------------------------------------
    # Adjust_Indent_byPos (v2.0)
    def Adjust_Indent_byPos(self, startPos=-1, endPos=-1, endString="\n"):
        # Init
        pureData = self.pureData
        changed_startPos = startPos
        changed_endPos  = endPos

        # Find previous "\n"
        removeStartPos = Find_Nearby_String(pureData, "\n", 0, changed_startPos, True)
        if removeStartPos is not False:
            changed_startPos = startPos + removeStartPos

        # Find End Position
        removeEndPos = Find_Nearby_String(pureData, endString, changed_endPos)
        if removeEndPos is not False:
            changed_endPos = changed_endPos + removeEndPos
            if endString == ";":
                changed_endPos += 1

        return changed_startPos, changed_endPos

    # Change_String_byPos (v2.0)
    def Change_String_byPos(self, startPos, endPos, value="", bStay=False):
        # Init
        value = str(value)

        self.readData = Replace_String_byPos(self.readData, startPos, endPos, value, bStay)
        self.pureData = Replace_String_byPos(self.pureData, startPos, endPos, value, bStay)

        self.tokenData = Extract_Data(self.readData)
        self.foamData = Get_FoamData(self.tokenData)
        return

    # Insert_String_byPos (v2.0)
    def Insert_String_byPos(self, startPos, value=""):
        # Init
        value = str(value)

        self.readData = Insert_String_byPos(self.readData, startPos, value)
        self.pureData = Insert_String_byPos(self.pureData, startPos, value)

        self.tokenData = Extract_Data(self.readData)
        self.foamData = Get_FoamData(self.tokenData)
        return

    # Get_ReadData (v2.0)
    def Get_ReadData(self):
        return self.readData, self.pureData

    # --------------------------------------------------------------------------
    # Dict
    # --------------------------------------------------------------------------
    # Get_Dict_List (v2.2)
    def Get_Dict_List(self, route=[], bHeader=False):
        # Init
        resultData = []
        subPos = len(route)

        # Search
        for dd in self.foamData:
            if subPos == 0:
                resultData.append(dd[0])
            else:
                if route[0] == "" or dd[0] == route[0]:
                    resultData = self.Get_Dict_List_Sub(dd, route)

        # bHeader: FoamFile 헤더는 제외 여부
        if not bHeader:
            if len(resultData) > 0 and isinstance(resultData, list):
                if resultData[0] == "FoamFile":
                    del resultData[0]
                elif resultData[0][0] == "FoamFile":
                    del resultData[0][0]
        return resultData

    # Get_Dict_List_Sub (v2.1)
    def Get_Dict_List_Sub(self, data, route=[]):
        # Init
        resultData = []

        # Set
        subRoute = route[1:]
        subPos = len(subRoute)
        subData = data[1:]

        # Check
        if len(subData) > 0 and not isinstance(subData[0], list):
            return resultData

        # Search
        for dd in subData:
            if subPos == 0:
                resultData.append(dd[0])
            else:
                if subRoute[0] == "" or dd[0] == subRoute[0]:
                    resultData = self.Get_Dict_List_Sub(dd, subRoute)
        #
        return resultData

    # Get (v2.4)
    def Get(self, route=[], pos=0, bDuple=False):   # pos : 몇 번째 값을 출력할 것인지 -1: 전체, 0: 1번째 값
        # Check
        if not self.IsDict(route):
            return []

        # Check FunctionObject
        if bDuple:
            return self.Get_Dict_Entry(route, bDuple=bDuple)

        if self.IsKeyword(route):
            return self.Get_Dict_Entry(route, pos)

        # Init
        totalPos = len(route)

        # Find
        for dd in self.foamData:
            if len(dd) > 0:
                if dd[0] == route[0]:
                    if (totalPos-1) == 0:
                        if pos >= 0:
                            return dd[pos + 1]  # 0번째는 keyword 이름
                        else:
                            return dd[1:]
                    else:
                        return self.Get_Sub(dd, route[1:], pos)
        return []

    # Get_Sub (v2.3)
    def Get_Sub(self, subFoamData=[], route=[], pos=0):
        # Init
        totalPos = len(route)

        # Find
        for ee in subFoamData:
            if ee[0] == route[0]:
                if (totalPos - 1) == 0:
                    if pos >= 0:
                        return ee[pos + 1]  # 0번째는 keyword 이름
                    else:
                        return ee[1:]
                else:
                    return self.Get_Sub(ee, route[1:], pos)
        return []

    # Get_Dict_Title_Pos (v2.0)
    def Get_Dict_Title_Pos(self, route=[]):
        # Read
        pureData = self.pureData

        # Init
        pos_Start, pos_Next, pos_End = -1, -1, -1

        pos = 0
        for dd in self.foamData:
            header = dd[0]
            subData = dd[1:]
            pos = Find_String(pureData, header, pos, endChar=[" ", "\t", ";", ")", "\n", "{"])
            lenWord = len(header)
            if header == route[0]:
                pos_Start = pos
                pos_End = pos_Start + lenWord
                pos = pos_End
                if len(route) > 1:
                    pos_Start, pos_End = self.Get_Dict_Title_Pos_Sub(pureData, subData, pos, route[1:])
                    break
            else:
                pos_Next = self.Jump_Dict_Title_Pos_Sub(pureData, subData, pos)
                pos = pos_Next
        # End
        return pos_Start, pos_End

    # Get_Dict_Title_Pos_Sub (v2.0)
    def Get_Dict_Title_Pos_Sub(self, pureData, subData=[], pos_Next=0, route=[]):
        pos = pos_Next
        pos_Start = -1
        pos_End = -1
        for dd in subData:
            header = dd[0]
            subData = dd[1:]
            pos = Find_String(pureData, header, pos, endChar=[" ", "\t", ";", ")", "\n", "{"])
            if header == route[0]:
                if len(route) > 1:
                    pos_Start, pos_End = self.Get_Dict_Title_Pos_Sub(pureData, subData, pos, route[1:])
                    break
                else:
                    pos_Start = pos
                    pos_End = pos_Start + len(header)
            else:
                pos = self.Jump_Dict_Title_Pos_Sub(pureData, subData, pos)
        #
        return pos_Start, pos_End

    # Jump_Dict_Title_Pos_Sub (v2.0)
    def Jump_Dict_Title_Pos_Sub(self, pureData, subData=[], pos_Next=0):
        pos = pos_Next
        for dd in subData:
            if isinstance(dd, list):
                header = dd[0]
                subData = dd[1:]
                pos = Find_String(pureData, header, pos, endChar=[" ", "\t", ";", ")", "\n", "{"])
                pos = self.Jump_Dict_Title_Pos_Sub(pureData, subData, pos)
            else:
                pos = Find_String(pureData, dd, pos, endChar=[" ", "\t", ";", ")", "\n", "{"])
                pos += len(dd)
        return pos

    # --------------------------------------------------------------------------
    # Get_Brace_Pos (v2.0)
    def Get_Brace_Pos(self, route=[]):
        # Init
        startPos = -1
        endPos = -1
        pureData = self.pureData

        # Find Dict
        startPos, endPos = self.Get_Dict_Title_Pos(route)
        if startPos < 0:
            return startPos, endPos

        # Find Brace
        dictPos = Find_BracesSet(pureData, endPos)

        # End
        return dictPos

    # --------------------------------------------------------------------------
    # Get_Dict_Pos (v2.2)
    def Get_Dict_Pos(self, route=[]):
        # Init
        startPos = -1
        endPos = -1
        pureData = self.pureData

        # Find Dict
        startPos, endPos = self.Get_Dict_Title_Pos(route)
        if startPos < 0:
            return startPos, endPos

        # Find Brace
        dictPos = Find_BracesSet(pureData, startPos)

        if dictPos[0] == -1 or dictPos[1] == -1:     # Keyword 형식일 경우
            endPos = Find_String(pureData, ";", endPos) + 1
        else:                       # Name 형식일 경우
            endPos = dictPos[1]

        # End
        return startPos, endPos

    # --------------------------------------------------------------------------
    # Change_Dict_Title (v2.2)
    def Change_Dict_Title(self, route=[], title=""):
        # Check
        if not self.IsDict(route):
            return

        # Init
        lenTitle = len(title)

        if lenTitle == 0:
            return

        # Find
        startPos, endPos = self.Get_Dict_Title_Pos(route)

        if self.IsName(route):
            lastPos = endPos
        elif self.IsKeyword(route):
            lastPos = self.Get_Dict_Entry_Pos(route)[0]
        else:
            return

        # Replace
        gap = lastPos - (startPos + lenTitle + 1)
        if gap > 0:
            self.Change_String_byPos(startPos, lastPos, title, True)
        else:
            title += " "
            self.Change_String_byPos(startPos, lastPos, title, False)
        return

    # --------------------------------------------------------------------------
    # Del (v2.1)     << Remove (v2.1)
    def Del(self, route=[]):
        # Check
        if self.IsName(route):
            self.Delete_Dict_Name(route)
        elif self.IsKeyword(route):
            self.Delete_Dict_Keyword(route)
        return

    # Clear (v2.0)     # 헤더 제외 한 모든 Dictionary 삭제
    def Clear(self):
        arrDict = self.Get_Dict_List([])
        for dd in arrDict:
            self.Del([dd])

        # just for aesthetics
        startPos = 0
        endPos = len(self.readData)
        while startPos < endPos:
            findPos = Find_String(self.readData, "\n\n", startPos)
            if findPos == -1:
                startPos = endPos
            else:
                self.readData = Replace_String_byPos(self.readData, findPos, findPos + 2, "\n")
                self.pureData = Replace_String_byPos(self.pureData, findPos, findPos + 2, "\n")
                startPos = findPos - 1

        self.tokenData = Extract_Data(self.readData)
        self.foamData = Get_FoamData(self.tokenData)
        return

    # --------------------------------------------------------------------------
    # Insert (v2.5)
    def Insert(self, route=[], entry="", prevWord="-1", bKeyword=True):     # prevWord: 0 is Top, -1 is Bottom
        # Check
        if len(route) >= 2 and self.IsKeyword([route[0]]):
            return
        if len(route) >= 2 and not self.IsName([route[0]]):   # 입력하려는 route 에서 Root Dict는 반드시 있어야함
            self.Insert_Dict_Name([route[0]])

        # Check2
        if self.IsDict(route):
            if entry:
                self.Set_Dict_Entry(route, entry)
            return

        # Check previous Route
        numRoute = len(route[:-1])
        if numRoute > 0 :
            for ii in range(1, numRoute): # prev:numRoute+1
                self.Insert(route[:ii])
                # return    # 20211116 changed  >> ???

        # Insert
        if entry == "" and not bKeyword:
            self.Insert_Dict_Name(route, prevWord)
        else:
            self.Insert_Dict_Keyword(route, entry, prevWord)
        return

    # Reset (v2.2)  # Set은 값이 있으면 그대로 두지만 Reset은 값이 있으면 하위 내용을 모두 지운 후 기존 자리에 새로 작성
    def Reset(self, route=[], value="", prevWord="-1", bKeyword=False):
        # Read Data
        readData, pureData = self.Get_ReadData()

        # Delete
        if self.IsName(route):
            posBrace = self.Get_Brace_Pos(route)

            insertData = "{\n"
            insertIndent = Find_Indent(pureData, posBrace[0])
            for ee in range(insertIndent):
                insertData += " "
            insertData += "}"

            self.Change_String_byPos(posBrace[0], posBrace[1], insertData, False)
        #
        if not bKeyword:
            self.Set2(route=route, value=value, prevWord=prevWord)
        else:
            self.Set(route=route, value=value, prevWord=prevWord, bKeyword=bKeyword)
        return

    # Set (v2.1)
    def Set(self, route=[], value="", prevWord="-1", bKeyword=True):   # bKeyword: keyword값이 비었을 경우 Name 형식으로 만들지 않게 하기 위함
        # Check
        if isinstance(value, list) and len(value) > 0:
            tmpData = "%s" %value[0]
            for ii in range(1, len(value)):
                tmpData+=" %s" % value[ii]
            value = tmpData

        # Init
        value = str(value)

        # Check
        if not self.IsDict(route):
            self.Insert(route, value, prevWord=prevWord, bKeyword=bKeyword)
            return

        # Change
        if self.IsName(route):
            self.Change_Dict_Title(route, value)
        elif self.IsKeyword(route):
            self.Set_Dict_Entry(route, value)
        return

    # Set2 (v2.0)
    def Set2(self, route=[], value="", prevWord="-1"):
        self.Set(route=route, value=value, prevWord=prevWord, bKeyword=False)
        return

    # --------------------------------------------------------------------------
    # Name
    # --------------------------------------------------------------------------
    # Delete_Dict_Name (v2.2)
    def Delete_Dict_Name(self, route=[]):
        # Check
        if not self.IsName(route):
            return

        # Find
        startPos, endPos = self.Get_Dict_Pos(route)
        if startPos == -1 or endPos == -1:
            return

        # Adjust
        startPos, endPos = self.Adjust_Indent_byPos(startPos, endPos, "\n")

        # Delete
        self.Change_String_byPos(startPos, endPos)
        return

    # Insert_Dict_Name (v2.4)
    def Insert_Dict_Name(self, route=[], prevName=""):
        # Init
        bLine = False

        # Read Data
        readData, pureData = self.Get_ReadData()

        # Check
        if self.IsName(route) or self.IsKeyword(route):
            return
        else:
            # Init
            insertRoute = route[:-1]
            lenInsertRoute = len(insertRoute)

            # Check
            if lenInsertRoute == 0:
                insertRoute = []
                bLine = True
            elif not self.IsDict(insertRoute):
                self.Insert_Dict_Name(insertRoute)

                # Reload Data
                readData, pureData = self.Get_ReadData()
                # return

            # Find
            subDicts = self.Get_Dict_List(insertRoute, bHeader=True)
            if len(subDicts) == 0:  # 하위 Dict가 없는 빈 Dict 일 경우
                # Find Pos
                startDictPos, endDictPos = self.Get_Dict_Title_Pos(insertRoute)
                startBracePos, endBracePos = Find_BracesSet(pureData, endDictPos)
                if (startBracePos, endBracePos) == (-1, -1):    # Insert
                    # Insert
                    insertData = ""
                    if bLine: insertData = "\n"
                    
                    insertData += "%s\n{\n}\n" % route[-1]
                    self.Insert_String_byPos(0, insertData)
                else:
                    # Init
                    insertIndent = Find_Indent(pureData, startBracePos)

                    # Insert
                    insertData = ""
                    if bLine: insertData = "\n"
                    
                    insertData += "\n"
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "    %-15s\n" % route[-1]
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "    {\n"
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "    }"

                    if Find_Nearby_String(pureData[startBracePos:endBracePos], "\n") == -1:
                        insertData += "\n"
                    self.Insert_String_byPos(startBracePos+1, insertData)
            else:
                if prevName == "0":
                    insertRoute.append(subDicts[0])

                    # Find Pos
                    preStartPos, preEndPos = self.Get_Dict_Pos(insertRoute)
                    insertIndent = Find_Indent(pureData, preStartPos)

                    # Insert
                    insertData = ""
                    if bLine: insertData = "\n"
                    
                    insertData += "%-15s\n" % route[-1]
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "{\n"
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "}\n"
                    for ee in range(insertIndent):
                        insertData += " "

                    self.Insert_String_byPos(preStartPos, insertData)

                else:
                    if prevName == "-1" or prevName == "":
                        insertRoute.append(subDicts[-1])
                    else:
                        bCheck = False
                        for dd in subDicts:
                            if dd == prevName:
                                bCheck = True
                                insertRoute.append(dd)
                                break
                        if not bCheck:
                            return

                    # Find Pos
                    preStartPos, preEndPos = self.Get_Dict_Pos(insertRoute)
                    insertIndent = Find_Indent(pureData, preStartPos)

                    preSplitStartPos = Find_String(readData, Create_FoamSplit(), 0)
                    preSplitEndPos = Find_Nearby_String(readData, "//", preSplitStartPos + 1) + preSplitStartPos + 2

                    # Insert
                    insertData = ""
                    if bLine: insertData = "\n"

                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "%-15s\n" % route[-1]
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "{\n"
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "}\n"
                    #
                    if preEndPos+1 < preSplitEndPos:
                        preEndPos = preSplitEndPos
                        insertData = "\n" + insertData  # before "\n\n"

                    self.Insert_String_byPos(preEndPos+1, insertData)   # +1 은 개행문자
        return

    # --------------------------------------------------------------------------
    # Keyword
    # --------------------------------------------------------------------------
    # Delete_Dict_Keyword (v2.0)
    def Delete_Dict_Keyword(self, route=[]):
        # Check
        if not self.IsKeyword(route):
            return

        startPos, endPos = self.Get_Dict_Title_Pos(route)
        if startPos == -1 or endPos == -1:
            return

        # Adjust
        startPos, endPos = self.Adjust_Indent_byPos(startPos, endPos, ";")

        # Delete
        self.Change_String_byPos(startPos, endPos)
        return

    # Insert_Dict_Keyword (v2.2)
    def Insert_Dict_Keyword(self, route=[], entry="", prevWord="-1"):   # prevWord: 0 is Top, -1 is Bottom
        # Init
        bLine = False

        # Read Data
        readData, pureData = self.Get_ReadData()

        # Check
        if self.IsDict(route):
            self.Set_Dict_Entry(route, entry)
        else:
            # Init
            insertRoute = route[:-1]
            lenInsertRoute = len(insertRoute)

            # Check
            if lenInsertRoute == 0:
                insertRoute = []
                bLine = True
            else:
                if not self.IsName(insertRoute):
                    return

            # Find
            subDicts = self.Get_Dict_List(insertRoute)
            if len(subDicts) == 0:  # 하위 Dict가 없는 빈 Dict 일 경우
                # Find Pos
                startDictPos, endDictPos = self.Get_Dict_Title_Pos(insertRoute)
                startBracePos, endBracePos = Find_BracesSet(pureData, endDictPos)
                if (startBracePos, endBracePos) == (-1, -1):
                    
                    # Insert
                    insertData = ""
                    if bLine: insertData = "\n"

                    # Insert
                    insertData += "%-15s %s;\n" % (route[-1], entry)                    
                    self.Insert_String_byPos(0, insertData)
                else:
                    # Init
                    insertIndent = Find_Indent(pureData, startBracePos)
                                       
                    # Insert
                    insertData = ""
                    if bLine: insertData = "\n"
                    
                    insertData += "\n"
                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "    %-15s %s;" % (route[-1], entry)
                    if Find_Nearby_String(pureData[startBracePos:endBracePos], "\n") == -1:
                        insertData += "\n"
                    self.Insert_String_byPos(startBracePos+1, insertData)

            else:
                if prevWord == "0":
                    insertRoute.append(subDicts[0])

                    # Find Pos
                    preStartPos, preEndPos = self.Get_Dict_Pos(insertRoute)
                    insertIndent = Find_Indent(pureData, preStartPos)

                    # Insert
                    insertData = ""
                    if bLine: insertData = "\n"

                    insertData += "%-15s %s;\n" % (route[-1], entry)
                    for ee in range(insertIndent):
                        insertData += " "
                    self.Insert_String_byPos(preStartPos, insertData)

                else:
                    if prevWord == "-1" or prevWord == "":
                        insertRoute.append(subDicts[-1])
                    else:
                        bCheck = False
                        for dd in subDicts:
                            if dd == prevWord:
                                bCheck = True
                                insertRoute.append(dd)
                                break
                        if not bCheck:
                            return

                    # Find Pos
                    preStartPos, preEndPos = self.Get_Dict_Pos(insertRoute)
                    insertIndent = Find_Indent(pureData, preStartPos)

                    preSplitStartPos = Find_String(readData, Create_FoamSplit(), 0)
                    preSplitEndPos = Find_Nearby_String(readData, "//", preSplitStartPos + 1) + preSplitStartPos + 2

                    # Insert
                    insertData = ""
                    if bLine:
                        insertData = "\n"

                    for ee in range(insertIndent):
                        insertData += " "
                    insertData += "%-15s %s;\n" % (route[-1], entry)

                    if preEndPos+1 < preSplitEndPos:
                        preEndPos = preSplitEndPos
                        insertData = "\n\n" + insertData                    
                    self.Insert_String_byPos(preEndPos+1, insertData)   # +1 은 개행문자
        return

    # --------------------------------------------------------------------------
    # Entry
    # --------------------------------------------------------------------------
    # Get_Dict_Entry_Pos (v2.1)
    def Get_Dict_Entry_Pos(self, route=[]):
        # Init
        startPos, endPos = -1, -1
        pureData = self.pureData

        # Check
        if not self.IsKeyword(route):
            return []

        # Find
        findStartPos = self.Get_Dict_Title_Pos(route)[1]
        findLastPos = self.Get_Dict_Pos(route)[1]
        result = self.Get_Dict_Entry(route)

        if len(result) == 0:
            startPos = findStartPos + Find_Nearby_String(pureData, ";", findStartPos, findLastPos)
            endPos = startPos
        else:
            # "(", ")"
            BracesPos = Find_BracesSet(pureData, findStartPos, ["(", ")"])
            if BracesPos[0] != BracesPos[1]:
                startPos = BracesPos[0]
                endPos = BracesPos[1] + Find_Nearby_String(pureData, ";", BracesPos[1])

            else:
                # "[", "]"
                BracesPos = Find_BracesSet(pureData, findStartPos, ["[", "]"])
                if BracesPos[0] != BracesPos[1]:
                    startPos = BracesPos[0]
                    endPos = BracesPos[1] + Find_Nearby_String(pureData, ";", BracesPos[1])
                else:
                    strEntry = self.Get_Dict_Entry(route)[0]
                    startPos = findStartPos + Find_Nearby_String(pureData, strEntry, findStartPos, findLastPos)
                    endPos = startPos + Find_Nearby_String(pureData, ";", startPos)

        return startPos, endPos

    # Get_Dict_Entry (v2.0)
    def Get_Dict_Entry(self, route=[], pos=-1, bDuple=False): # pos : 몇 번째 값을 출력할 것인지 -1: 전체, 0: 1번째 값
        # Check
        if not self.IsKeyword(route):
            return []

        # Init
        totalPos = len(route)
        allData = []

        # Find
        for dd in self.foamData:
            if dd[0] == route[0]:
                if (totalPos - 1) == 0:
                    if pos >=0 :
                        if not bDuple:
                            return dd[pos+1]    # 0번째는 keyword 이름
                        else:
                            allData.append(dd[pos+1])
                    else:
                        if not bDuple:
                            return dd[1:]
                        else:
                            allData.append(dd[pos + 1])
                else:
                    if not bDuple:
                        return self.Get_Dict_Entry_Sub(dd, route[1:], pos)
                    else:
                        allData.append(dd[pos + 1])
        return []

    # Get_Dict_Entry_Sub (v2.0)
    def Get_Dict_Entry_Sub(self, subFoamData=[], route=[], pos=-1):
        # Init
        totalPos = len(route)

        # Find
        for ee in subFoamData:
            if ee[0] == route[0]:
                if (totalPos - 1) == 0:
                    if pos >=0 :
                        if len(ee) > pos + 1:
                            return ee[pos + 1]  # 0번째는 keyword 이름, 없을 경우도 있으므로
                        else:
                            return []
                    else:
                        return ee[1:]
                else:
                    return self.Get_Dict_Entry_Sub(ee, route[1:], pos)
        return []   # Default:   return

    # Set_Dict_Entry (v2.0)
    def Set_Dict_Entry(self, route=[], value=""):
        # Init
        value = str(value)
        # Check
        if not self.IsKeyword(route):
            return

        # Find
        startPos, endPos = self.Get_Dict_Entry_Pos(route)
        self.Change_String_byPos(startPos, endPos, value)
        return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <3> Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ------------------------------------------------------------------------------
# Foam Define
# ------------------------------------------------------------------------------
# Create_FoamHeader (v2.0)
def Create_FoamHeader(version="5.x", location="system", object="controlDict"):
    strHeader = ""
    strHeader += "/*--------------------------------*- C++ -*----------------------------------*\\\n"
    strHeader += "| =========                 |                                                 |\n"
    strHeader += "| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n"
    strHeader += "|  \\\\    /   O peration     | Version:  %s                                   |\n" % version
    strHeader += "|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |\n"
    strHeader += "|    \\\\/     M anipulation  |                                                 |\n"
    strHeader += "\\*---------------------------------------------------------------------------*/\n"
    strHeader += "FoamFile\n"
    strHeader += "{\n"
    strHeader += "    version     2.0;\n"
    strHeader += "    format      ascii;\n"
    strHeader += "    class       dictionary;\n"
    strHeader += "    location    \"%s\";\n" % location
    strHeader += "    object      %s;\n" % object
    strHeader += "}\n"
    strHeader += Create_FoamSplit() + "\n\n"
    return strHeader

# Create_FoamSplit (v2.0)
def Create_FoamSplit():
    strSplit = "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //"
    return strSplit

# Create_FoamBottom (v2.0)
def Create_FoamBottom():
    strBottom = "// ************************************************************************* //"
    return strBottom

# ------------------------------------------------------------------------------
# FoamData
# ------------------------------------------------------------------------------
# Extract_Data (v2.2)
def Extract_Data(readData):
    # Check
    if not readData:
        return []

    # Init
    allData = readData

    # 모든 주석 제거
    allData = Remove_Comment(allData)

    # 여러개의 빈 칸 / 개행문자(\n) / 탭(\t)을 하나의 빈칸으로 변경
    allData = Remove_Empty(allData, "\n")

    # 모든 세미콜론/대괄호/중괄호의 공백 추가 (항목 분리 위함)
    allData = Replace_String(allData, ";", " ; ")
    allData = Replace_String(allData, "{", " { ")
    allData = Replace_String(allData, "}", " } ")

    # 빈 칸을 기준으로 구분시키기
    split1Data = allData.split(" ")

    # 소괄호 분리 (키워드 제외)
    split2Data = []
    bDictName = True  # first is always keyword

    for dd in split1Data:
        if not dd:
            continue
        elif dd == ";" or dd == "{" or dd == "}" or \
                dd == "(" or dd == ")" or dd == "[" or dd == "]":
            split2Data.append(dd)
            bDictName = True  # next Token is keyword
        else:
            if not bDictName:  # replace 함수는 문자열 내 모둔 문자 변경
                dd = Replace_String(dd, "(", " ( ")
                dd = Replace_String(dd, ")", " ) ")
                # dd = Replace_String(dd, "[", " [ ")
                # dd = Replace_String(dd, "]", " ] ")

                subSplitData = dd.split(" ")
                for ee in subSplitData:
                    if ee:
                        split2Data.append(ee)
            else:  # 예외 처리
                # 소/중 괄호 분리
                if (dd.find("(") == -1 and dd.find(")")) or (dd.find(")") == -1 and dd.find("(")):
                    dd = dd.replace(")", " ) ")
                    subSplitData = dd.split(" ")
                    for ee in subSplitData:
                        if ee:
                            split2Data.append(ee)
                elif (dd.find("[") == -1 and dd.find("]")) or (dd.find("]") == -1 and dd.find("[")):
                    dd = dd.replace("]", " ] ")
                    subSplitData = dd.split(" ")
                    for ee in subSplitData:
                        if ee:
                            split2Data.append(ee)
                else:
                    split2Data.append(dd)
            bDictName = False

    # #include / #remove 분리
    pos = -1
    split3Data = []
    for ii, dd in enumerate(split2Data):
        if not dd:
            continue
        if ii == pos:  # 아래 문장과 순서 바꾸지 말 것
            split3Data.append(";")
        if dd.find("#include") == 0 or dd.find("#remove") == 0:
            pos = ii + 2
        #
        split3Data.append(dd)

    # Last
    tokenData = split3Data

    # End
    return tokenData

# Get_FoamData (v2.1)
def Get_FoamData(tokenData=[]):
    # Init
    pos = 0
    iState = 0
    totalNum = len(tokenData)
    foamData = []
    bContinue = False  # Get_SubFoamData 에서만 필요함

    # Parse
    while pos < totalNum:
        token = tokenData[pos]
        if iState == 0:
            iState = 0
            if token == "{" or token == "(":
                foamData.append("@")
            elif token == "}" or token == ")" or token == ";":
                pass
            else:
                foamData.append([token])
                iState += 1

        elif iState == 1:
            pos, subData, bContinue = Get_SubFoamData(pos, tokenData)
            for ee in subData:
                foamData[-1].append(ee)
            if not subData:
                foamData[-1].append("")
            #
            iState -= 1

        # Next
        pos += 1

    # End
    return foamData

# Get_SubFoamData (v2.1)
def Get_SubFoamData(idx, rootData):
    # Init
    pos = idx
    iState = 1
    totalNum = len(rootData)
    subFoamData = []
    bContinue = False
    pre_token = ""

    #
    while iState > 0 and pos < totalNum:
        token = rootData[pos]

        if iState == 1:
            if token == ";" or token == "}" or token == ")":
                iState -= 1
            elif token == "]":
                bContinue = True  # 대괄호 이후 데이터 있을 가능성 있음
                iState -= 1
            elif token == "{" or token == "(" or token == "[":
                iState += 1
            else:
                subFoamData.append(token)

        elif iState == 2:
            if token == ";" or token == "}":
                iState -= 2

            elif token == "]":
                iState -= 1

            elif token == ")":
                if pre_token == "(":  # pre_token == "{" (X)
                    subFoamData.append("")
                #
                iState -= 1

            elif token == "(":
                # iState = 2  # 연속 소괄호는 현재 위치 유지하면서 연속으로 읽기
                pass
            elif token == "(":  # or token == "{" or token == "[":
                print("[Error] Cannot read file, %s" % pos)  # 이 부분이 나오면 파일 에러임
                return 0, [], bContinue
            else:
                if bContinue:
                    subFoamData.append(token)
                    iState = 2  # 그대로 유지
                else:
                    subFoamData.append([token])
                    iState += 1

        elif iState == 3:
            pos, subSubData, bContinue = Get_SubFoamData(pos, rootData)
            for ee in subSubData:
                subFoamData[-1].append(ee)
            if not subFoamData:
                subFoamData[-1].append("")
            #
            iState -= 1

        # Next
        pos += 1
        pre_token = token

    # End
    pos -= 1
    return pos, subFoamData, bContinue
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Convert
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 아직 활용도가 없는 함수
# Get_TF_Type (v1.0)
def Get_Type(self, bState=True, opt=0, userTF=None):
    # Init
    if userTF is None:
        userTF = ["1", "-1"]
    #
    if bState:  # true, 1, on 모두 같은 값임
        if opt == "truefalse" or opt == 0:
            value = "true"
        elif opt == "onoff" or opt == 1:
            value = "on"
        elif opt == "yesno" or opt == 2:
            value = "yes"
        elif opt == "1" or opt == 3:
            value = "1"
        elif opt == "user" or opt == 4:
            value = userTF[0]
        else:
            value = 1
    else:
        if opt == "truefalse" or opt == 0:
            value = "false"
        elif opt == "onoff" or opt == 1:
            value = "off"
        elif opt == "yesno" or opt == 2:
            value = "no"
        elif opt == 0 or opt == 3:
            value = "0"
        elif opt == "user" or opt == 4:
            value = userTF[1]
        else:
            value = 0
    return value

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <4> Run
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    # Init
    # testFile = "/home/test/Desktop/ExampleCase/system/controlDict"
    # if not os.path.isfile(testFile):
    #     print("Cannot find file")
    #     exit(1)

    # New
    # foam = FOAM_DATA_CLASS()
    # foam.New(testFile)

    # Check
    # print(foam.IsDict(["application"]))
    # print(foam.IsName(["application"]))
    # print(foam.IsKeyword(["application"]))
    
    # Get
    # print(foam.Get_Dict_List([]))
    
    # Set (Insert/Change)
    # foam.Set(["application"] ,"simpleFoam")


    # Delete
    # foam.Del(["application"])
    # foam.Save()

    # Test
    testFile = "/home/test/Desktop/ExampleCase/system/settings/regionConditions"
    foam = FOAM_DATA_CLASS()
    foam.New(testFile)

    # print(foam.foamData)
    foam.Set(["gravity"], "(0 0 0)")
    foam.Save()

