'''
# Name: calculate_reynolds_number.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/2/2017
# Edit Date: 8/2/2017

# Calculates a Reynold's Number using density, velocity,
# viscosity, and length

# Inputs:
#   rho     - fluid density [kg / m^3]
#   V       - fluid velocity [m / s]
#   L       - chord length [m]
#   mu      - fluid viscosity [kg / m / s]

# Outputs:
#   Re      - Reynold's Number
'''


from __future__ import print_function

from openmdao.api import Component
import math

class calculate_reynolds_number(Component):

    def __init__(self):
        super(calculate_reynolds_number, self).__init__()
        self.add_param('rho', val=1.0)
        self.add_param('V', val=1.0)
        self.add_param('L', val=1.0)
        self.add_param('mu', val=1.0)
        
        self.add_output('Re', val=1.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
       
       unknowns['Re'] = (params['rho']*params['V']*params['L'])/params['mu']
       