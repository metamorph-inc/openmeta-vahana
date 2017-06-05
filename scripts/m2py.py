# author: tthomas@metamorphsoftware.com
# date:   2017-06-05
# description: automations script for converting '.m' files to python wrappers

import re

if __name__ == '__main__':
    component_name = ""
    params_orig = list()
    params_new = list()
    unknowns_orig = list()
    unknowns_new = list()
    arrays = list()
    with open('hoverPower.m', 'r') as fin:
        text = fin.readlines()
        # Pass 1
        for line in text:
            m = re.match(r'function \[([\w,]+)\] = (\w+)\(([\w,]+)\)', line)
            if m is not None:
                unknowns_orig = list(m.group(1).split(','))
                component_name = m.group(2)
                params_orig = list(m.group(3).split(','))
            else:
                for unknown in unknowns_orig:
                    if unknown in line:
                        captures = re.findall('({}\\.\\w+)'.format(unknown), line)
                        if len(captures) > 0:
                            if unknown not in arrays:
                                arrays.append(unknown)
                            for c in captures:
                                if c not in unknowns_new:
                                    unknowns_new.append(c)
                for param in params_orig:
                    if param in line:
                        captures = re.findall('({}\\.\\w+)'.format(param), line)
                        if len(captures) > 0:
                            if param not in arrays:
                                arrays.append(param)
                            for c in captures:
                                if c not in params_new:
                                    params_new.append(c)
                            
        for name in arrays:
            if name in params_orig:
                params_orig.remove(name)
            if name in unknowns_orig:
                unknowns_orig.remove(name)
        
        # print component_name
        # print params_orig
        # print unknowns_orig
        # print params_new + params_orig
        # print unknowns_new + unknowns_orig
        
        params = params_new + params_orig
        unknowns = unknowns_new + unknowns_orig
        
        header = """
from __future__ import print_function

from openmdao.api import IndepVarComp, Component, Problem, Group, FileRef
import numpy as np

class {name}(Component):

    def __init__(self):
        super({name}, self).__init__()
        
""".format(name=component_name)
            
        solve_nonlinear = """
    def solve_nonlinear(self, params, unknowns, resids):
        
"""
            
        with open('{}.py'.format(component_name), 'w') as fout:
            in_body = False
            # Pass 2
            for line in text:
                m = re.match(r'function \[([\w,]+)\] = (\w+)\(([\w,]+)\)', line)
                if m is not None:
                    fout.write(header)
                    for param in params:
                        fout.write("        self.add_param('{}', val=1.0)\n".format(param))
                    fout.write("\n")
                    for unknown in unknowns:
                        fout.write("        self.add_output('{}', val=1.0)\n".format(unknown))
                    fout.write(solve_nonlinear)
                    in_body = True
                else:
                    line = re.sub(r'^([ \t]*)%', r'\1#', line)
                    line = re.sub(r'; %', r' #', line)
                    line = re.sub(r';', r'', line)
                    line = re.sub(r'^\w*end\w*$', r'', line)
                    line = line.replace('^', '**')
                    line = line.replace(' pi ', ' math.pi ')
                    line = line.replace('sqrt(', 'math.sqrt(')
                    line = line.replace('^', '**')
                    line = line.replace('...', '\\')
                    line = line.replace('./', '/')
                    line = line.replace('.*', '*')
                    if in_body:
                        for unknown in unknowns:
                            line = line.replace(unknown, "unknowns['{}']".format(unknown))
                        for param in params:
                            line = line.replace(param, "params['{}']".format(param))
                        fout.write("        "+line)
                    else:
                        fout.write(line)