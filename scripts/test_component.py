'''
# Name: test_component.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/15/2017
# Edit Date: 6/15/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Implementation of optimizer nested within a parameter study using 
# the OpenMDAO framework and Python conversions of the vahanaTradeStudy

# Inputs:
#   Input               - input description [units]

# Outputs:
#   Outputs             - output description [units]
'''

from __future__ import print_function  # allows for backwards compatibility with Python 2.X - OpenMDAO (and OpenMeta) uses Python 2.7
import sys
import math

from openmdao.api import Problem, Group, Component

class TestSystem(Component):
    ''' costPerFlight = range*rProp - cruiseSpeed*batteryMass - (motorMass*mtom)^3
        - (range*cruiseSpeed)^2 + rProp*motorMass - cruiseSpeed*mtom '''
    def __init__(self):
        super(TestSystem, self).__init__()
        
        self.add_param('range', val=50.0)
        self.add_param('rProp', val=1.0)
        self.add_param('cruiseSpeed', val=50.0)
        self.add_param('batteryMass', val=117.0)
        self.add_param('motorMass', val=30.0)
        self.add_param('mtom', val=650.0)
        
        self.add_output('costPerFlight', shape=1)
        
    def solve_nonlinear(self, params, unknowns, resids):
        ''' costPerFlight = range*rProp - cruiseSpeed*batteryMass - (motorMass*mtom)^3
            - (range*cruiseSpeed)^2 + rProp*motorMass - cruiseSpeed*mtom '''
        
        range = params['range']
        rProp = params['rProp']
        cruiseSpeed = params['cruiseSpeed']
        batteryMass = params['batteryMass']
        motorMass = params['motorMass']
        mtom = params['mtom']
        
        unknowns['costPerFlight'] = range*rProp - cruiseSpeed*batteryMass - (motorMass*mtom)**3 \
                                    - (range*cruiseSpeed)**2 + rProp*motorMass - cruiseSpeed*mtom