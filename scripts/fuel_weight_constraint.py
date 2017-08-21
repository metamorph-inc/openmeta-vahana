'''
# Name: fuel_weight_constraint.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/17/2017
# Edit Date: 8/17/2017

# Constraint on battery mass with respect to maximum takeoff mass

# Inputs:
#   mBattery    - battery mass [kg]
#   mtom        - maximum takeoff mass [kg]

# Outputs:
#   c          - c = mBattery - mtom
'''

from __future__ import print_function

from openmdao.api import Component
import math

class fuel_weight_constraint(Component):
    def __init__(self):
        super(fuel_weight_constraint, self).__init__()
        self.add_param('mBattery', val=0.0)
        self.add_param('mtom', val=0.0)
        
        self.add_output('c', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        # Constraint on battery mass with respect to maximum takeoff mass
        unknowns['c'] = (1.0/3.0)*params['mtom'] - params['mBattery']