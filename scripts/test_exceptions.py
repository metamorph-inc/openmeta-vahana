'''
# Name: test_exceptions.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/12/2017
# Edit Date: 6/12/2017

# Testing: exception openmdao.core.system.AnalysisError
# Link: http://openmdao.readthedocs.io/en/1.7.3/srcdocs/packages/core/system.html?highlight=analysiserror#openmdao.core.system.AnalysisError

# Inputs:
# X

# Outputs:
#  Y
'''


from __future__ import print_function
from openmdao.core.system import AnalysisError

from openmdao.api import Component
import math

class test_exceptions(Component):

    def __init__(self):
        super(test_exceptions, self).__init__()
        self.add_param('X', val=0.0)
        
        self.add_output('Y', val=0.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['Y'] = 0.0
        if (params['X'] < 0.5):
        
            unknowns['Y'] = 0.25
            try:
                raise AnalysisError
                unknowns['Y'] = 0.125
            except:
                unknowns['Y'] = 0.5
            
        unknowns['Y'] = 1.0
            
        