'''
# Name: heli_prop_mass_tail_inputs.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/7/2017
# Edit Date: 8/7/2017

# Inputs:
#   rProp               - rotor radius [m]
#   hoverOutput_QMax    - #TODO

# Outputs:
#   R   - til rotor radius
#   T   - tail rotor thrust
'''

from __future__ import print_function

from openmdao.api import Component
import math

class heli_prop_mass_tail_inputs(Component):
    def __init__(self):
        super(heli_prop_mass_tail_inputs, self).__init__()
        self.add_param('rProp', val=0.0)
        self.add_param('hoverOutput_QMax', val=0.0)
        
        self.add_output('R', val=0.0)
        self.add_output('T', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['R'] = params['rProp']/5.0
        unknowns['T'] = 1.5*params['hoverOutput_QMax']/(1.25*params['rProp'])