from openmdao.api import Component
from pprint import pprint

''' First, let's create the component defining our system. We'll call it 'Paraboloid'. '''
class Paraboloid(Component):
    ''' Evaluates the equation f(x,y) = (x-3)^2 +xy +(y+4)^2 - 3 '''
    
    def __init__(self):
        super(Paraboloid, self).__init__()
        
        ''' Inputs to the PythonWrapper Component are added here as params '''
        self.add_param('x', val=0.0)
        self.add_param('y', val=0.0)
        
        ''' Outputs from the PythonWrapper Component are added here as unknowns '''
        self.add_output('f_xy', shape=1)
        
    def solve_nonlinear(self, params, unknowns, resids):
        ''' This is where we describe the system that we want to add to OpenMETA '''
        ''' f(x,y) = (x-3)^2 + xy + (y+4)^2 - 3 '''
        
        x = params['x']
        y = params['y']
        
        f_xy = (x-3.0)**2 + x*y + (y+4.0)**2 - 3.0
        
        unknowns['f_xy'] = f_xy
        
        ''' This is an equivalent expression to the one above
        unknowns['f_xy'] = (params['x']-3.0)**2 + params['x']*params['y'] + (params['y']+4.0)**2 - 3.0
        '''