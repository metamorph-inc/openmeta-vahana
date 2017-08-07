import json
import os.path
import posixpath
import platform
import sys
import time

from subprocess import Popen, PIPE, STDOUT
from threading import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

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

    
    #Obtain alpha
    with open('testbench_manifest.json', 'r') as f_in:
        testbench_manifest = json.load(f_in)

    alpha = float(read_testbench_manifest_parameters(testbench_manifest)["Alpha"])
    
    #Run the XFoil simulation ------------------------------------------------------------------------------------------
    print "Opening 'script.xfoil'..."
    with open('script.xfoil', 'r') as f_in:
        xfoil_script = f_in.readlines()

    files = ["plot.ps", "polar.txt"]
    for f in files:
        if os.path.exists(f):
            os.remove(f)

    print "Running XFOIL simulation..."
    converged = False
    
    if platform.system() == 'Windows':
        p = Popen(['C:/OpenMETA/xfoil-and-nrel-codes/bin/xfoil.exe'], stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=ON_POSIX)
    elif platform.system() == 'Darwin':
        p = Popen(['/Applications/Xfoil.app/Contents/Resources/xfoil'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        
    '''
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True # thread dies with the program
    t.start()
    
    #Setup
    for i in range(len(xfoil_script)):
        print ">>> {}".format(xfoil_script[i][:-1])
        p.stdin.write(xfoil_script[i])
    
    
    # read line without blocking
    try:
        line = q.get_nowait() # or q.get(timeout=.1)
    except Empty:
        print('no output yet')
    else: # got line
        print line
    '''    
    
    #Setup
    for i in range(9):
        print ">>> {}".format(xfoil_script[i][:-1])
        p.stdin.write(xfoil_script[i])
    
    start_alpha = 5.0
    if start_alpha > alpha:
        offset = -0.5
    else:
        offset = 0.5
    
    while start_alpha != alpha:
        print ">>> {}".format("alfa {}".format(start_alpha))
        print ">>> !"
        print ">>> !"
        p.stdin.write("alfa {}\n".format(start_alpha))
        p.stdin.write("!\n")
        p.stdin.write("!\n")
        start_alpha += offset
    
    
    print ">>> {}".format("alfa {}".format(start_alpha))
    print ">>> !"
    print ">>> !"
    p.stdin.write("alfa {}\n".format(start_alpha))
    p.stdin.write("!\n")
    p.stdin.write("!\n")
    
    for i in range(12, 17):
        print ">>> {}".format(xfoil_script[i][:-1])
        p.stdin.write(xfoil_script[i])
    
    p.stdin.close()  # Needed or else the script hangs. 
    p.stdout.close() # See: https://stackoverflow.com/questions/21141712/subprocess-popen-communicate-vs-stdin-write-and-stdout-read
    p.stderr.close() # and: https://stackoverflow.com/questions/27451182/proper-way-to-close-all-files-after-subprocess-popen-and-communicate?rq=1
    
    
    converged = True 
    # result = p.communicate(input=xfoil_script)
    result = ["",""]

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

    # if converged:
        # with open('polar.txt', 'r') as f_in:
            # polar_lines = f_in.readlines()
            
        # for line in polar_lines:
            # print line[:-1]
            
        # print len(polar_lines)
        # final_line=polar_lines[-1].split()
        
        # # Alpha = final_line[0]
        # CL = final_line[1]
        # CD = final_line[2]
        # CM = final_line[4]
        
        # print CL
        # print CD
        # print CM
    
    
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