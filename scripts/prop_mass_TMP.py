'''
# Name: prop_mass.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/22/2017
# Edit Date: 6/22/2017

# Adaption of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Estimate optimal prop mass using an equation extracted from data in the Vahana Trade Study's tradeStudyResults.mat file.
# In the interests of time, I'm using this TMP solution for now. Later, if it is needed, I can convert the propMass.m file
# to a PythonWrapper Component but based off the wingMass.m conversion, that isn't worth the time (for now).

# Inputs:
#   range   - range [km]

# Outputs:
#   mass    - estimated prop mass [kg]
'''

from __future__ import print_function

from openmdao.api import Component
import numpy as np
import math

class prop_mass_TMP(Component):
    def __init__(self):
        super(prop_mass_TMP, self).__init__()
        self.add_param('range', val=0.0)
        
        self.add_output('mass', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['mass'] = 12.386*math.exp(0.015*(params['range']/1000.0))