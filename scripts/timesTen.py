'''
# Name: timesTen
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/21/2017
# Edit Date: 6/21/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Multiply the input by ten and output the result

# Inputs:
#   number

# Outputs:
#   ten
'''

from __future__ import print_function

from openmdao.api import Component

class timesTen(Component):
    def __init__(self):
        super(timesTen, self).__init__()
        self.add_param('num', val=0.0)
        
        self.add_output('timesTen', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['timesTen'] = params['num']*10.0