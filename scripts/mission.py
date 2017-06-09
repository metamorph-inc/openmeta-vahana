'''
# Name: mission.py
# Company: MetaMorph, Inc.
# Author(s): Austin Tabulog, Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/5/2017
# Edit Date: 6/6/2017

# Compilation of Airbus A^3's vahanaTradeStudy>reserveMission.mat and vahanaTradeStudy>simpleMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate time and energy use for VTOL missions of varying vehicle types, ranges, loiter time, and trip legs
# Inputs:
#   Vehicle                 - vehicle type
#   rProp                   - prop/rotor radius [m]
#   V                       - cruise speed [m/s]
#   range                   - range [m]
#   loiterTime              - time spent loitering [s]
#   hops                    - number of legs or "hops" in the mission
#   hoverOutput_PBattery    - #TODO
#   cruiseOutput_PBattery   - #TODO
#   loiterOutput_PBattery   - #TODO

# Outputs:
#   E            - Total energy use [kW-hr]
#   t            - Flight time for reserve mission [s]
'''

from __future__ import print_function

from openmdao.api import Component
import math

class mission(Component):

    def __init__(self):
        super(mission, self).__init__()
        self.add_param('Vehicle', val=u'abcdef', desciption='vehicle type - tilt-wing or helicopter')
        self.add_param('rProp', val=0.0, description='propellor/rotor radius')
        self.add_param('V', val=0.0, description='cruise speed')
        self.add_param('range', val=0.0, description='range')
        self.add_param('loiterTime', val=0.0, description='20 minute total reserve time - 3 min for hoverTime')
        self.add_param('hops', val=1.0, desciption='number of stops')
        self.add_param('hoverOutput_PBattery', val=0.0, description='TODO')
        self.add_param('cruiseOutput_PBattery', val=0.0, description='TODO')
        self.add_param('loiterOutput_PBattery', val=0.0, description='TODO')
        
        self.add_output('E', val=0.0, description='total energy use in reserve mission')
        self.add_output('t', val=0.0, description='flight time for reserve mission')
        
    def solve_nonlinear(self, params, unknowns, resids):
        if (params["Vehicle"].lower().replace('-', '') == "tiltwing" or params["Vehicle"].lower().replace('-', '') == "helicopter"):
            # Mission
            hoverTime = 180.0 * params['hops']  # time to account for VTOL takeoff and climb, transition, transition, VTOL descent and landing
            
            # Compute cruise time [s]
            cruiseTime = params['range'] / params['V']
            
            # Compute total energy use [KW-hr]
            unknowns['E'] = (params['hoverOutput_PBattery'] * hoverTime + params['cruiseOutput_PBattery'] * cruiseTime + params['loiterOutput_PBattery'] * params['loiterTime']) * 2.77778e-7  # kW-hr
            
            # Compute total flight time [s]
            unknowns['t'] = params['loiterTime'] + hoverTime + cruiseTime
            
        else:
            print('unrecognized vehicle!')
            pass
            