'''
# Name: stepGenerateOpenVSPDegenGeomFile.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com (https://www.metamorphsoftware.com/)
# Create Date: 8/30/2017
# Edit Date: 8/30/2017

# Runs OpenVSP, updates the model using the Design Variable file,
# and generates the *_DegenGeom.csv file

# Based on Adam Nagel's blademda xfoil scripts.
# Written for OpenVSP Version-3.13.2-win32.
'''

import json
import os.path
import posixpath
import platform
import sys

from subprocess import Popen, PIPE, STDOUT

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
    
    # Run OpenVSP in script model
    print "Running OpenVSP in script mode"
    
    fileDir = os.path.dirname(os.path.realpath(__file__))
    exeName = ''
    if platform.system() == 'Windows':
        exeName = 'vspscript.exe'
    elif platform.system() == 'Darwin':
        exeName = 'vspscript'
    path = os.path.join(fileDir, exeName)
    print "Path: " + path
    arg = '-script'
    vspscript = vspName + '.vspscript'
    
    args = [path, arg, vspscript]
    p = Popen(args, cwd=fileDir)
    p.wait()

    # Record the new artifact
    print "Recording artifacts..."
    if os.path.exists(vspName + '_DegenGeom.csv'):
        testbench_manifest["Artifacts"].append({"Tag": "DegenGeom", "Location": vspName + '_DegenGeom.csv'})
  
    # Save the testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)
    
    print "Done."
