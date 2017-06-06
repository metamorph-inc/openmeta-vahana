# Company: MetaMorph, Inc.
# Author(s): Austin Tabulog, Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/5/2017
# Edit Date: 6/6/2017

# Compilation of Airbus A^3's vahanaTradeStudy>reserveMission.mat and vahanaTradeStudy>simpleMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate time and energy use for either a simple or reserve VTOL mission
# Inputs:
#   vehicle                 - vehicle type
#   rProp                   - prop/rotor radius [m]
#   V                       - cruise speed [m/s]
#   W                       - weight [N]
#   range                   - range [m]
#   hoverOutput_PBattery     - #TODO
#   cruiseOutput_PBattery    - #TODO
#   loiterOutput_PBattery    - #TODO

# Outputs:
#   E            - Total energy use in reserve mission
#   t            - Flight time for reserve mission

from __future__ import print_function

from openmdao.api import Component
import math

class mission(component):

    def__init__(self):
        super(mission, self).__init__()
        self.add_param('vehicle', val=0.0, desciption='vehicle type - tilt-wing or helicopter')
        self.add_param('rProp', val=0.0, description='propellor/rotor radius')
        self.add_param('V', val=0.0, description='cruise speed')
        self.add_param('W', val=0.0, description='weight')
        self.add_param('range', val=0.0, description='range')
        self.add_param('loiterTime', val=0.0, description='20 minute total reserve time - 3 min for hoverTime')
        self.add_param('hops', val=1.0, desciption='number of stops')
        self.add_param('hoverOutput_PBattery', val=0.0, description='TODO')
        self.add_param('cruiseOutput_PBattery', val=0.0, description='TODO')
        self.add_param('loiterOutput_PBattery', val=0.0, description='TODO')
        
        
        self.add_output('E', val=0.0, description='total energy use in reserve mission')
        self.add_output('t', val=0.0, description='flight time for reserve mission')
        
    def solve_nonlinear(self, params, unknowns, resids):
        if (params['vehicle'] == 0 or params['vehicle'] == 1):
            # Mission
            hoverTime = 180 * params['hops'] #time to account for VTOL takeoff and climb, transition, transition, VTOL descent and landing
            
            # Compute cruise time [s]
            cruiseTime = params['range'] / params['V']
            cruiseTime = params['range'] / params['V']
            
            # Compute total energy use [KW-hr]
            unknowns['E'] = (params['hoverOutputPBattery'] * hoverTime + params['cruiseOutputPBattery'] * cruiseTime + params['loiterOutputPBattery'] * params['loiterTime']) * 2.77778e-7
            
            # Compute total flight time [s]
            unknowns['t'] = params['loiterTime'] + hoverTime + cruiseTime
            
        else:
            print('unrecognized vehicle!')
            pass