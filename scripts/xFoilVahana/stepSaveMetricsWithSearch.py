import json

if __name__ == '__main__':
    print "Running " + str(__file__) + "..."

    #Populate the testbench_manifest with the results ------------------------------------------------------------------
    #Open 'polar.txt'
    print "Opening 'polar.txt'..."
    NCrit = None
    with open('polar.txt', 'r') as f_in:
        polar_lines = list()
        for line in f_in:
            polar_lines.append(line)
            print line
        
    #Convert to Matrix
    for x in range(len(polar_lines)):
        polar_lines[x]=polar_lines[x].split()

    #Find NCrit
    print "Finding NCrit..."
    for x in range(len(polar_lines)):
        for y in range(len(polar_lines[x])):
            if str(polar_lines[x][y]) == "Ncrit":
                if len(polar_lines[x])>=y+2 and polar_lines[x][y+1]=='=':
                    NCrit = polar_lines[x][y+2]

    #Find Table
    print "Finding CL/CD/CM Table..."
    for x in range(len(polar_lines)):
        if len(polar_lines[x])!=0 and len(polar_lines[x][0])!=None and polar_lines[x][0][0]=='-':
            break
    x+=1

    print x
    print polar_lines[x]
    maximum_glide_ratio = float(polar_lines[x][1])/float(polar_lines[x][2])
    optimal_alpha_cl_cd = polar_lines[x][:3]
    Alpha = polar_lines[x][0]
    CL = polar_lines[x][1]
    CD = polar_lines[x][2]
    CM = polar_lines[x][4]

    #Prepare Table
    print "Converting CL/CD/CM Table to float and finding Maximum Glide Ratio..."
    cl_cd_cm_table = list()
    while x < len(polar_lines):
        row = list()
        for y in range(len(polar_lines[x])):
            row.append(float(polar_lines[x][y]))
        cl_cd_cm_table.append(row)
        #Remember location of optimal Alpha/CL/CD
        if row[1]/row[2] > maximum_glide_ratio:
            maximum_glide_ratio = row[1]/row[2]
            optimal_alpha_cl_cd = row[:3]
            Alpha = row[0]
            CL = row[1]
            CD = row[2]
            CM = row[4]
        x=x+1

    #Open 'testbench_manifest.json'
    with open('testbench_manifest.json', 'r') as f_in:
        testbench_manifest = json.load(f_in)

    #Add metrics
    print "Saving Metrics to testbench_manifest.json..."
    for metric in testbench_manifest["Metrics"]:
        if str(metric["Name"])=="Ncrit":
            metric["Value"]=NCrit
        elif str(metric["Name"])=="CL":
            metric["Value"]=CL
        elif str(metric["Name"])=="CM":
            metric["Value"]=CM
        elif str(metric["Name"])=="CD":
            metric["Value"]=CD
        elif str(metric["Name"])=="Alpha2":
            metric["Value"]=Alpha
        elif str(metric["Name"])=="CL_CD_CM_Table":
            metric["Value"]=cl_cd_cm_table
        elif str(metric["Name"])=="Glide_Ratio":
            metric["Value"]=maximum_glide_ratio

    testbench_manifest["Status"]="OK"

    #Save the modified testbench_manifest
    with open('testbench_manifest.json', 'w') as f_out:
        json.dump(testbench_manifest, f_out, indent=2)

    print "Done."
