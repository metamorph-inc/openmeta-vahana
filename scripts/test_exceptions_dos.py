'''
# Name: test_exceptions_dos.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/12/2017
# Edit Date: 6/12/2017

# Testing: exception openmdao.core.system.AnalysisError
# Link: http://openmdao.readthedocs.io/en/1.7.3/srcdocs/packages/core/system.html?highlight=analysiserror#openmdao.core.system.AnalysisError

# Inputs:
# X2

# Outputs:
#  Y2
'''


from __future__ import print_function
from openmdao.api import Component
import math

class testexceptionsdos(Component):

    def __init__(self):
        super(testexceptionsdos, self).__init__()
        self.add_param('X2', val=2.0)
        
        self.add_output('Y2', val=3.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['Y2'] = params['X2']
            
        