#!/usr/bin/env python3
# -*-coding:utf8-*-
# !/bin/bash

# Name Definition
# Dict    : All formats such as 'Name' and 'Keyword' except entry
# Name    : dict with sub dict
# Keyword : dict without sub dict
# Entry   : value of 'Keyword'

# Hierarchy of foam file
# Name
# {
#     keyword     entry;
#     Name
#     {
#         keyword     entry;
#     }
# }

def write_file(self, path, data):
    with open(path, 'w') as f:
        f.write(data)
    return True


def create_dict_file(path, version, location, object_name):
    foam_data = create_foamfile_header(version, location, object_name)
    write_file(path, foam_data)


def create_foamfile_header(version='5.x', location='system', object_value='controlDict'):
    header_data = ''
    header_data += '/*--------------------------------*- C++ -*----------------------------------*\\n'
    header_data += '| =========                 |                                                 |\n'
    header_data += '| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n'
    header_data += '|  \\    /   O peration     | Version:  %s                                   |\n' % version
    header_data += '|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |\n'
    header_data += '|    \\/     M anipulation  |                                                 |\n'
    header_data += '\\*---------------------------------------------------------------------------*/\n'
    header_data += 'FoamFile\n'
    header_data += '{\n'
    header_data += '    version     2.0;\n'
    header_data += '    format      ascii;\n'
    header_data += '    class       dictionary;\n'
    header_data += '    location    \'%s\';\n' % location
    header_data += '    object      %s;\n' % object_value
    header_data += '}\n'
    header_data += create_foamfile_split() + '\n\n'
    return header_data


def create_foamfile_split():
    split_data = '// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //'
    return split_data


def create_foamfile_bottom():
    bottom_data = '// ************************************************************************* //'
    return bottom_data
