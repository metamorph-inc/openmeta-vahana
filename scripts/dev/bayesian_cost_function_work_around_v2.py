'''
# Name: bayesian_cost_function_work_around_v2.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/18/2017
# Edit Date: 8/19/2017

# Inputs:
costPerFlight       - cost per flight [$]
constraint1         - constraint function 1 value    
constriant2         - constraint function 2 value    
constraint3         - constraint function 3 value    

# Outputs:
bayesianObjFunc     - output [$]
'''

from __future__ import print_function

from openmdao.api import Component

class buffer(Component):
    def __init__(self):
        super(buffer, self).__init__()
        self.add_param('costPerFlight', val=0.0)
        self.add_param('constraint1', val=0.0)
        self.add_param('constraint2', val=0.0)
        self.add_param('constraint3', val=0.0)
        
        self.add_output('bayesianObjFunc', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        costPerFlight = params['costPerFlight']
        constraint1 = params['constraint1']
        constraint2 = params['constraint2']
        constraint3 = params['constraint3']
        
        penaltyOverhead = 10.0
        penaltyMultiplier = 50.0
        constraintTolerance = 0.1        

        # Initialize penalty at 0.0
        constraintViolationPenalty = 0.0
        
        if (constraint1 < -constraintTolerance):
            constraintViolationPenalty += (-1.0)*constraint1*penaltyMultiplier     
            constraintViolationPenalty += penaltyOverhead     
        if (constraint2 < -constraintTolerance):
            constraintViolationPenalty += (-1.0)*constraint2*penaltyMultiplier     
            constraintViolationPenalty += penaltyOverhead     
        if (constraint3 < -constraintTolerance):
            constraintViolationPenalty += (-1.0)*constraint3*penaltyMultiplier     
            constraintViolationPenalty += penaltyOverhead     
        
        unknowns['bayesianObjFunc'] = params['costPerFlight'] + constraintViolationPenalty