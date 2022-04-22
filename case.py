#!/usr/bin/env python
#-*-coding:utf8-*-
#!/bin/bash

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Notice
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This code is a part of NextLib module

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <1> Header
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Common
import os, sys
path_NextLib_PyFoamDict_case_py = os.path.dirname(os.path.abspath(__file__))

path_NextLib = os.path.abspath(path_NextLib_PyFoamDict_case_py + "/../..")
sys.path.append(path_NextLib)

# NextLibrary
from NextLib.cmn import *
from NextLib.PyFoamDict.foam import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <2> Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class FOAM_CASE_CLASS:
    def __init__(self, appPath=path_NextLib_PyFoamDict_case_py):
        # Common
        self.appPath    = appPath
        self.casePath   = ""

        # Data Name
        self.name       = OrderedDict([])
        return

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Main
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # [1] New/End
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def New(self, casePath=""):
        # Init
        self.casePath = casePath
        self.Load_CaseInfo()
        return

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # [2] Run
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # [3] Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def Load_CaseInfo(self):
        # Init
        fileData = Read_File("%s/Setting/Info/caseInfo" % self.appPath)
        #
        readData = Remove_Comment(fileData, 0)
        readData = Remove_Empty(readData)
        splitData = readData.split("\n")
        for dd in splitData:
            if dd:
                dd = dd.split(" ")
                self.name[dd[0]] = FOAM_DATA_CLASS()
                fileName = "%s/%s" % (self.casePath, dd[1])
                self.name[dd[0]].New(fileName)
        return

    # Check_Data
    def Check_Data(self, searchName=""):
        if not searchName or self.name.get(searchName) is None:
            return False
        if not self.name[searchName].foamData:
            return False
        return True

    # Update all
    def Update(self, searchName=""):
        # Check_Data
        if searchName and not self.Check_Data(searchName):
            return

        # Load
        if searchName:
            self.name[searchName].Load()
        else:
            for dd in self.name:
                self.name[dd].Load()
        return

    # --------------------------------------------------------------------------
    # Load/Save
    # --------------------------------------------------------------------------
    def Load(self, searchName=""):
        # Check_Data
        if searchName and not self.Check_Data(searchName):
            return

        # Load
        if searchName:
            self.name[searchName].Load()
        else:
            for dd in self.name:
                self.name[dd].Load()
        return

    def Save(self, searchName=""):
        # Check_Data
        if searchName and not self.Check_Data(searchName):
            return
        # Save
        if searchName == "":
            for dd in self.name.values():
                if os.path.isfile(dd.fileName):
                    dd.Save()
        else:
            dd = self.name[searchName]
            dd.Save()
            if os.path.isfile(dd.fileName):
                dd.Save()

        # Update
        self.Load(searchName)
        return

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <3> Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# <4> Run
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    # Example
    path ="/home/test/Desktop/ExampleCase"

    foamCase = FOAM_CASE_CLASS()
    foamCase.New(path)

    getData = foamCase.name["control"].Get(["startTime"])
    print(getData)

    foamCase.name["control"].Set(["startTime"], 100)
    foamCase.name["control"].Save()

    foamCase.name["control"].Del(["startTime"])
    foamCase.name["control"].Save()
    
    
    
    
