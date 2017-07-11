'''
# Name: constraint2.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 7/11/2017
# Edit Date: 7/11/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Constraint on available motor power (kW)

# Inputs:
#   mMotors         - motor mass [kg]
#   hoverPower_PMax - energy required to complete reserve mission [kW-hr]

# Outputs:
#   c2              - c2 = mMotors*5.0 - hoverPower_PMax / 1000.0
'''

from __future__ import print_function

from openmdao.api import Component
import math

class constraint2(Component):
    def __init__(self):
        super(constraint2, self).__init__()
        self.add_param('mMotors', val=0.0)
        self.add_param('hoverPower_PMax', val=0.0)
        
        self.add_output('c2', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        # Assumed values
        motorPowerDensity = 5.0  # kW/kg, including controller and other accessories in 3-5 years
        
        # Constraint on available motor power (kW)
        unknowns['c2'] = (params['mMotors'] * motorPowerDensity) - (params['hoverPower_PMax'] / 1000.0) 
        