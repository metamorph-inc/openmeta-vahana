'''
# Name: heli_wire_mass_input.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/7/2017
# Edit Date: 8/7/2017

# Inputs:
#   rProp   - rotor radius [m]

# Outputs:
#   length  - [m]
'''

from __future__ import print_function

from openmdao.api import Component
import math

class heli_wire_mass_input(Component):
    def __init__(self):
        super(heli_wire_mass_input, self).__init__()
        self.add_param('rProp', val=0.0)
        
        self.add_output('length', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['length'] = 1.5 + 1.25*params['rProp']