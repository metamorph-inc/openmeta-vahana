'''
# Name: stepPopulateOpenVSPDesignVariableFile.py
# Company: MetaMorph, Inc. (https://www.metamorphsoftware.com/)
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/30/2017
# Edit Date: 8/30/2017

# Populates the OpenVSP Design Variable File with
# the testbench manifest parameters.

# Based on Adam Nagel's blademda xfoil scripts.
# Written for OpenVSP Version-3.13.2-win32.
'''

import os
import sys
import json

def read_testbench_manifest_parameters(testbench_manifest):
    parameters_dict = dict()
    print "Reading parameters from testbench_manifest.json..."
    print
    for parameter in testbench_manifest['Parameters']:
        parameters_dict[parameter['Name']] = parameter['Value']
        print parameter['Name'] + ": " + str(parameter['Value'])
    print
    return parameters_dict
    
def build_script_failed(testbench_manifest, err_message):
    # Mark as "FAILED" and clean up testbench_manifest
    testbench_manifest["Status"] = "FAILED"
    testbench_manifest["Artifacts"] = []
    testbench_manifest["Metrics"] = []

    # Pass error message to Manifest
    testbench_manifest["ErrorMessage"] = err_message

    # Save the testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

if __name__ == '__main__':
    print "Running " + str(__file__) + "..."
    
    # Obtain testbench configuration
    with open('testbench_manifest.json', 'r') as f_in:
        testbench_manifest = json.load(f_in)
        
    replacement_dict = read_testbench_manifest_parameters(testbench_manifest)
    desVarFilename = replacement_dict.get('Des_Var_Filename')
    if desVarFilename is None:
        raise ValueError("Design Variable filename must be provided - e.g. 'vspmodel.des'")
    desVarFilename = desVarFilename[2:-1] # Trim off "u' and " from ends of filename
    vspFilename = replacement_dict.get('VSP_Filename')
    if vspFilename is None:
        raise ValueError("OpenVSP filename must be provided - e.g. 'vspmodel.vsp3'")
    vspFilename = vspFilename[2:-1] # Trim off "u' and " from ends of filename
    
    # Check if design variable file name and VSP filename match
    try:
        desVarFilename[:-4] == vspFilename[:-5]
    except KeyError, Argument:
        build_script_failed(testbench_manifest, "Error: Run Aborted: \
            The design variable filename and VSP filename must match. \
            E.g. vspmodel.des and vspmodel.vsp3".format(Argument))
        print "Error: The design variable filename and VSP file do not match.".format(Argument)
        print "Execution Aborted."
        sys.exit(1)
    
    # Read the design variable .des file
    templateDir = os.path.dirname(os.path.realpath(__file__))
    f_data = []
    with open(os.path.join(templateDir, desVarFilename), 'r') as f_in:
        f_data = f_in.readlines()
    
    # Replace target design variable values with testbench manifest values
    firstLine = True
    expectedCnt = 0
    replacementCnt = 0
    new_data = []
    for line in f_data:
        if firstLine:
            expectedCnt = int(line)
            firstLine = False
        else:
            for parameter in replacement_dict:
                if parameter in line:
                    trimIndex = line.rfind(":")
                    line = line[:trimIndex+2] + str(replacement_dict[parameter]) + '\n'
                    replacements =+ 1
                    break
        new_data.append(line)

    # Check if all testbench design variable parameters were used
    try:
        expectedCnt == replacementCnt
    except KeyError, Argument:
        build_script_failed(testbench_manifest, "Error: Run Aborted: A design variable was missing \
        from the testbench manifest. Check for typos.".format(Argument))
        print "Error: A design variable does not exist in testbench_config.".format(Argument)
        print "Execution Aborted."
        sys.exit(1)
        
    with open(os.path.join(templateDir, desVarFilename), 'w') as f_out:
        f_out.writelines(new_data)

    #Record the new artifact
    print "Recording artifacts..."
    if os.path.exists(desVarFilename):
        testbench_manifest["Artifacts"].append({"Tag": "OpenVSP *.des file", "Location": desVarFilename})

    #Save the testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

    print "Done."
    