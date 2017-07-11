'''
# Name: constraint3.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 7/11/2017
# Edit Date: 7/11/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Constraint on max take-off weight

# Inputs:
#   mtom    - maximum takeoff mass [kg]
#   mass_W  - total vehicle weight [N]

# Outputs:
#   c3      - c3 = mtow*9.8 - mass_W
'''

from __future__ import print_function

from openmdao.api import Component
import math

class constraint3(Component):
    def __init__(self):
        super(constraint3, self).__init__()
        self.add_param('mtom', val=0.0)
        self.add_param('mass_W', val=0.0)
        
        self.add_output('c3', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        # Assumed values
        
        # Constraint on max take-off weight
        unknowns['c3'] = (params['mtom'] * 9.8) - params['mass_W']
        