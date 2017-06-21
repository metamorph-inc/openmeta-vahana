'''
# Name: divideHundred
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/21/2017
# Edit Date: 6/21/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Divide the input by one hundred and output the result

# Inputs:
#   number

# Outputs:
#   hundredth
'''

from __future__ import print_function

from openmdao.api import Component

class hundredth(Component):
    def __init__(self):
        super(hundredth, self).__init__()
        self.add_param('num', val=0.0)
        
        self.add_output('hundredth', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['hundredth'] = params['num']*0.01