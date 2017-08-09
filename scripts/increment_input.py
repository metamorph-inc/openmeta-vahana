'''
# Name: increment_input.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/8/2017
# Edit Date: 8/8/2017

# Inputs:
in  - int input

# Outputs:
out - int output
'''

from __future__ import print_function

from openmdao.api import Component

class increment_input(Component):
    def __init__(self):
        super(increment_input, self).__init__()
        self.add_param('input', val=0.0)
        
        self.add_output('output', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['output'] = params['input'] + 1.0