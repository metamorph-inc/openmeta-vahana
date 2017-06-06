# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/5/2017
# Edit Date: 6/5/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate time and energy use for a simple VTOL mission
# Inputs:
#   vehicle                 - vehicle type
#   rProp                   - prop/rotor radius
#   V                       - cruise speed
#   W                       - weight
#   range                   - range
#   hoverOutputPBattery     - #TODO
#   cruiseOutputPBattery    - #TODO
#   loiterOutputPBattery    - #TODO

# Outputs:
#   E            - Total energy use in reserve mission
#   t            - Flight time for reserve mission

from __future__ import print_function

from openmdao.api import Component
import math

class simple_mission(Component):

    def __init__(self):
        super(simple_mission, self).__init__()
        self.add_param('vehicle', val=0.0, desciption='vehicle type - tilt-wing or helicopter')
        self.add_param('rProp', val=0.0, description='propellor/rotor radius')
        self.add_param('V', val=0.0, description='cruise speed')
        self.add_param('W', val=0.0, description='weight')
        self.add_param('range', val=0.0, description='range')
        self.add_param('hoverOutputPBattery', val=0.0, description='TODO')
        self.add_param('cruiseOutputPBattery', val=0.0, description='TODO')
        self.add_param('loiterOutputPBattery', val=0.0, description='TODO')

        self.add_output('E', val=0.0, description='total energy use in reserve mission')
        self.add_output('t', val=0.0, description='flight time for reserve mission')


    def solve_nonlinear(self, params, unknowns, resids): #QUESTION: does this always need to be named solve_nonlinear
        if (params['vehicle'] == 0 or params['vehicle'] == 1):
            # Basic mission
            hoverTime = 180 * 1 # sec to account for VTOL takeoff and climb, transition, transition, VTOL descent and landing

            # Compute cruise time
            cruiseTime = params['range'] / params['V'] # sec

            # Loiter time
            loiterTime = 0 # no reserve        
            
            # Compute total energy use (kW-hr)
            E = (params['hoverOutputPBattery'] * hoverTime + params['cruiseOutputPBattery'] * cruiseTime + params['loiterOutputPBattery'] * loiterTime) * 2.77778e-7 # kW-hr

            # Compute total flight time
            t = hoverTime + cruiseTime + loiterTime;

        else:
            print('Unrecognized vehicle!')
            pass