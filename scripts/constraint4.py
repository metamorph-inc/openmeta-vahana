'''
# Name: constraint4.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/7/2017
# Edit Date: 8/7/2017

# Constraint on autorotation

# Inputs:
#   mass_rotor                  - tail rotor mass [kg]
#   mass_m                      - vehicle mass [kg]
#   hoverPower_Vtip             - velocity of main prop tip
#   hoverPower_VAutoRotation    - velocity of main prop tip in autorotation

# Outputs:
#   c4          - c4 = (0.5*1.0/3.0*mass_rotor*(hoverPower_Vtip**2.0)) - (0.5*mass_m*(hoverPower_VAutoRotation**2.0))
'''

from __future__ import print_function

from openmdao.api import Component
import math

class constraint4(Component):
    def __init__(self):
        super(constraint4, self).__init__()
        self.add_param('mass_rotor', val=0.0)
        self.add_param('mass_m', val=0.0)
        self.add_param('hoverPower_Vtip', val=0.0)
        self.add_param('hoverPower_VAutoRotation', val=0.0)
        
        self.add_output('c4', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        # Constraint on autorotation
        unknowns['c4'] = (0.5*1.0/3.0*params['mass_rotor']*(params['hoverPower_Vtip']**2.0)) - (0.5*params['mass_m']*(params['hoverPower_VAutoRotation']**2.0))