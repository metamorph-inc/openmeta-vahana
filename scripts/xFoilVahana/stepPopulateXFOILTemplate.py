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

def build_script_failed(testbench_manifest, err_message):
    #Mark as "FAILED" and clean up testbench_manifest
    testbench_manifest["Status"] = "FAILED"
    testbench_manifest["Artifacts"] = []
    testbench_manifest["Metrics"] = []

    #Pass error message to Manifest
    testbench_manifest["ErrorMessage"] = err_message

    #Save the testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

if __name__ == '__main__':
    print "Running " + str(__file__) + "..."

    #Populate the XFOIL script template --------------------------------------------------------------------------------

    #Obtain testbench configuration
    with open('testbench_manifest.json', 'r') as f_in:
        testbench_manifest = json.load(f_in)

    replacement_dict = read_testbench_manifest_parameters(testbench_manifest)
    replacement_dict['Naca_Code'] = int(replacement_dict.get('Naca_Code', 0))
    #replacement_dict['Alpha'] = float(replacement_dict.get('Alpha', 0))
    if replacement_dict.get('Reynolds_Number') is None:
        raise ValueError('Reynolds_Number must be provided')

    #Load template XFOIL script
    templateDir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(templateDir, 'template.xfoil'), 'r') as f_in:
        xfoil_template = Template(f_in.read())

    #Substitute parameters into XFOIL Script
    print "Substituting parameters into template script..."
    try:
        xfoil_script = xfoil_template.substitute(replacement_dict)
    except KeyError, Argument:
        build_script_failed(testbench_manifest, "Error: Run Aborted: {} does not exist in testbench_config.".format(Argument))
        print "Error: {} does not exist in testbench_config.".format(Argument)
        print "Execution Aborted."
        sys.exit(1)

    print "Saving script to 'script.xfoil'..."
    with open('script.xfoil', 'w') as f_out:
        f_out.write(xfoil_script)

    #Record the new artifact
    print "Recording artifacts..."
    if os.path.exists('script.xfoil'):
        testbench_manifest["Artifacts"].append({"Tag": "XFOIL Script", "Location": "script.xfoil"})

    #Save the testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

    print "Done."
