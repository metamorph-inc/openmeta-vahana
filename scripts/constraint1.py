'''
# Name: constraint1.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 7/11/2017
# Edit Date: 7/11/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Constraint on available energy (E is in kW-hr)

# Inputs:
#   mBattery    - battery mass [kg]
#   EReserve    - energy required to complete reserve mission [kW-hr]

# Outputs:
#   c1          - c1 = (mBattery*230.0*0.95/1000.0) - EReserve
'''

from __future__ import print_function

from openmdao.api import Component
import math

class constraint1(Component):
    def __init__(self):
        super(constraint1, self).__init__()
        self.add_param('mBattery', val=0.0)
        self.add_param('EReserve', val=0.0)
        
        self.add_output('c1', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        # Assumed values
        batteryEnergyDensity = 230.0  # Expected pack energy density in 3-5 years [Wh/kg]
        dischargeDepthReserve = 0.95  # Can only use 95% of battery energy in reserve mission
        
        # Constraint on available energy (E is in kW-hr)
        unknowns['c1'] = (params['mBattery'] * batteryEnergyDensity * dischargeDepthReserve / 1000.0) - params['EReserve']