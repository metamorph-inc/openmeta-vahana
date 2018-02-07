# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/5/2017
# Edit Date: 6/5/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate time and energy use for a reserve VTOL mission
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

class reserve_mission(Component):

    def __init__(self):
        super(reserve_mission, self).__init__()
        self.add_param('Vehicle', val=u'abcdef', description='Vehicle type')  # 'tiltwing' or 'helicopter'
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
        if params['Vehicle'].lower() in ('tiltwing', 'helicopter'):
            # Reserve mission
            hoverTime = 180.0 * 2 # sec to account for VTOL takeoff and climb, transition, transition, VTOL descent and landing and repeated for diversion

            # Compute cruise time
            cruiseTime = params['range'] / params['V'] # sec

            # Loiter time
            loiterTime = 17 * 60 # 20 minute total reserve

            # Compute total energy use (kW-hr)
            unknowns['E'] = (params['hoverOutputPBattery'] * hoverTime + params['cruiseOutputPBattery'] * cruiseTime + params['loiterOutputPBattery'] * loiterTime) * 2.77778e-7 # kW-hr

            # Compute total flight time
            unknowns['t'] = hoverTime + cruiseTime + loiterTime;

        else:
            print('Unrecognized vehicle!')
            pass