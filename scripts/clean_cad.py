import json
        
if __name__ == '__main__':

    #Open 'testbench_manifest.json'
    with open('testbench_manifest.json', 'r') as f_in:
        testbench_manifest = json.load(f_in)

    #Add metrics
    print "Saving Metrics to testbench_manifest.json..."
    for metric in testbench_manifest["Metrics"]:
        if str(metric["Name"])=="CenterOfMass":
            metric["Value"]=float(metric["Value"].split(';')[2])
        elif str(metric["Name"])=="CanardPt":
            metric["Value"]=float(metric["Value"].split(';')[2])
        elif str(metric["Name"])=="WingPt":
            metric["Value"]=float(metric["Value"].split(';')[2])

    testbench_manifest["Status"]="OK"

    #Save the modified testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

    print "Done."