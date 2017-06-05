# This is a cool script

from __future__ import print_function

from openmdao.api import Component

class Add(Component):

    def __init__(self):
        super(Add, self).__init__()
        
        self.add_param('x', val=1.0, description='thing one to add')
        self.add_param('y', val=2.0, description='thing two to add')
		
        self.add_output('a', val=3.0, description='results of adding thing one and thing two')
        
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['a'] = params['x'] + params['y']