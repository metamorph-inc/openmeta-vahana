'''
# Name: stepGenerateOpenVSPVscpscrFile.py
# Company: MetaMorph, Inc. (https://www.metamorphsoftware.com/)
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/30/2017
# Edit Date: 8/30/2017

# Generates the *.vspscript file

# Based on Adam Nagel's blademda xfoil scripts.
# Written for OpenVSP Version-3.13.2-win32.
'''

import os
import sys
import json
from string import Template

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
    vspFilename = vspFilename[2:-1]  # Trim off "u' and " from ends of filename
    
    new_replacement_dict = {'VSP_Filename': vspFilename[:-5]}
    
    # Load template vspscript
    templateDir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(templateDir, 'template.vspscript'), 'r') as f_in:
        vspscript_template = Template(f_in.read())
        
    # Substitute the OpenVSP model's filename into the template vspscript
    vspscript = vspscript_template.substitute(new_replacement_dict)

    print "Saving vspscript to '" + vspFilename[:-5] + ".vspscript'..."
    vspscriptFilename = vspFilename[:-5] + '.vspscript'
    with open(os.path.join(templateDir, vspscriptFilename), 'w') as f_out:
        f_out.write(vspscript)
   
    # Record the new artifact
    print "Recording artifacts..."
    if os.path.exists(vspscriptFilename):
        testbench_manifest["Artifacts"].append({"Tag": "vspscript", "Location": vspscriptFilename})
  
    # Save the testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

    print "Done."
