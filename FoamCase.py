#!/usr/bin/env python3
# -*-coding:utf8-*-
# !/bin/bash

import os

from NextLibs.OpenFOAM.PyFoamDict.Tools.StringTool import (
    remove_comment, remove_empty
)
from NextLibs.OpenFOAM.PyFoamDict.FoamData import FoamData


FileInfo = {
    'regionProp': 'constant/regionProperties',
    'MRFProp': 'constant/MRFProperties',
    'transportProp': 'constant/transportProperties',
    'turbulenceProp': 'constant/turbulenceProperties',
    'boundary': 'constant/polyMesh/boundary',
    'controlDict': 'system/controlDict',
    'createBaffles': 'system/createBafflesDict',
    'decomposePar': 'system/decomposeParDict',
    'fvOptions': 'system/fvOptions',
    'fvSchemes': 'system/fvSchemes',
    'fvSolution': 'system/fvSolution'
}


class FoamCase:
    def __init__(self):
        self.case_path = ''
        self.foam_file = {}

    def end(self):
        ...

    def set_case_path(self, path=''):
        self.case_path = path
        self.get_case_info()

    def get_case_info(self, info_path='/Settings/files'):
        # Basic
        for key, value in FileInfo.items():
            tmp_foam_data = FoamData()
            tmp_foam_data.set_file('%s/%s' % (self.case_path, value))
            self.foam_file[key] = tmp_foam_data

        # Additional
        this_file_path = os.path.dirname(os.path.abspath(__file__))
        file_data = self.read_file(this_file_path + info_path)

        read_data = remove_comment(file_data, 0)
        read_data = remove_empty(read_data)
        split_data = read_data.split('\n')
        for d in split_data:
            if d:
                d = d.split(' ')
                tmp_foam_data = FoamData()
                tmp_foam_data.set_file('%s/%s' % (self.case_path, d[1]))
                if not d[0] in self.foam_file:
                    self.foam_file[d[0]] = tmp_foam_data

    def read_file(self, path):
        data = ''
        if os.path.isfile(path):
            with open(path, 'r') as f:
                data = f.read()
        return data

    def check_name(self, name=''):
        if not name or self.foam_file.get(name) is None:
            return False
        if not self.foam_file[name].foam_data:
            return False
        return True

    def update(self, load_header=True):
        for d in self.foam_file:
            self.foam_file[d].load(load_header)

    def load(self, name=''):
        if not name or not self.check_name(name):
            return False

        self.foam_file[name].load()
        return True

    def save(self, name=''):
        if name == '':
            for d in self.foam_file.values():
                d.save()
        else:
            d = self.foam_file[name]
            d.save()

        return True

    def is_foam_folder(self):
        self.update(False)

        required_files = ['boundary', 'controlDict', 'fvSchemes', 'fvSolution']
        for d in required_files:
            if not self.foam_file[d].is_foam_file():
                return False
            if not os.path.isfile(self.foam_file[d].file_name):
                return False
        return True


if __name__ == '__main__':
    # Example
    case_path = '/home/test/Desktop/TestCase'

    foam = FoamCase()
    foam.set_case_path(case_path)
    foam.update()

    # Read
    fvSolution = foam.foam_file['fvSolution']
    result = fvSolution.get_dict_list(['solvers'])
    print(result)

    result = fvSolution.get(['solvers', 'cellDisplacement', 'relTol'])
    print(result)

    # Write
    fvSolution.set(['solvers', 'cellDisplacement', 'relTol'], '2')
    fvSolution.save()
