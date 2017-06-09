'''
# Name: mass_2_weight
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/9/2017
# Edit Date: 6/9/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Convert mass [kg] to weight [N]

# Inputs:
#   mass    - [kg]

# Outputs:
#   weight  - [N}
'''

from __future__ import print_function

from openmdao.api import Component

class mass_2_weight(Component):
    def __init__(self):
        super(mass_2_weight, self).__init__()
        self.add_param('mass', val=0.0)
        
        self.add_output('weight', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['weight'] = params['mass']