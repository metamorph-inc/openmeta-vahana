'''
# Name: stepRunVSPAERO.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com (https://www.metamorphsoftware.com/)
# Create Date: 8/31/2017
# Edit Date: 8/31/2017

# Generates the *.vspaero setup file from the *_DegenGeom.csv file.
# TODO: Edit the *.vspaero file.
# Runs vspaero.exe with the *.vspaero and *_DegenGeom files.

# Based on Adam Nagel's blademda xfoil scripts.
# Written for OpenVSP Version-3.13.2-win32.
'''

import json
import os.path
import posixpath
import platform
import sys

def read_testbench_manifest_parameters(testbench_manifest):
    parameters_dict = dict()
    print "Reading parameters from testbench_manifest.json..."
    print
    for parameter in testbench_manifest['Parameters']:
        parameters_dict[parameter['Name']] = parameter['Value']
        print parameter['Name'] + ": " + str(parameter['Value'])
    print
    return parameters_dict

if __name__ == '__main__':
    print "Running " + str(__file__) + "..."

    # Obtain testbench configuration
    with open('testbench_manifest.json', 'r') as f_in:
        testbench_manifest = json.load(f_in)
        
    replacement_dict = read_testbench_manifest_parameters(testbench_manifest)
    vspFilename = replacement_dict.get('VSP_Filename')
    if vspFilename is None:
        raise ValueError("OpenVSP filename must be provided - e.g. 'vspmodel.vsp3'")
    vspName = vspFilename[2:-6]  # Trim off "u' and .vsp3" from ends of filename

    # Run vspaero.exe
    print "Running vspaero.exe"
    
    fileDir = os.path.dirname(os.path.realpath(__file__))
    exeName = ''
    if platform.system() == 'Windows':
        exeName = 'vspaero.exe'
    elif platform.system() == 'Darwin':
        exeName = 'vspaero'
    path = os.path.join(fileDir, exeName)
    print "Path: " + path
    
    
    
    
    
    
    
    
    