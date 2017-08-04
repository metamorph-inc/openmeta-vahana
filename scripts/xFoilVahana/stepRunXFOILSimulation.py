import json
import os.path
import posixpath
import platform
import sys

from subprocess import Popen, PIPE, STDOUT

if __name__ == '__main__':
    print "Running " + str(__file__) + "..."

    #Run the XFoil simulation ------------------------------------------------------------------------------------------
    print "Opening 'script.xfoil'..."
    with open('script.xfoil', 'r') as f_in:
        xfoil_script = f_in.read()

    files = ["plot.ps", "polar.txt"]
    for f in files:
        if os.path.exists(f):
            os.remove(f)

    print "Running XFOIL simulation..."
    if platform.system() == 'Windows':
        p = Popen(['C:/OpenMETA/xfoil-and-nrel-codes/bin/xfoil.exe'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        result = p.communicate(input=xfoil_script)
    elif platform.system() == 'Darwin':
        p = Popen(['/Applications/Xfoil.app/Contents/Resources/xfoil'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        result = p.communicate(input=xfoil_script)

    #Save log files
    print "Saving log files..."
    with open(os.path.join('log', 'xfoil-stdout.log'), 'w') as f_out:
        f_out.write(result[0])

    with open(os.path.join('log', 'xfoil-stderr.log'), 'w') as f_out:
        if result[1]:
            f_out.write(result[1])
        else:
            # empty file
            pass

    #Add artifacts to "artifacts" in testbench_manifest.json
    print "Recording artifacts..."
    with open('testbench_manifest.json', 'r') as f_in:
        testbench_manifest = json.load(f_in)

    expected_files = {"plot": "plot.ps",
                      "polar table": "polar.txt",
                      "XFOIL stdout log": posixpath.join("log", "xfoil-stdout.log"),
                      "XFOIL stderr log": posixpath.join("log", "xfoil-stderr.log")}

    artifacts = testbench_manifest["Artifacts"]
    for k, v in expected_files.iteritems():
        if os.path.exists(v):
            artifacts.append({"Tag": k, "Location": v})

    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

    print "Done."

    #Let the testbench executor know how the job went
    sys.exit(p.returncode)