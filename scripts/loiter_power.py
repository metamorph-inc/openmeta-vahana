"""
Translating MatLab to Python 2.7

built from A^3's LoiterPower.m code
"""

from __future__ import print_function

from openmdao.api import IndepVarComp, Component, Problem, Group, FileRef
import numpy as np
import platform
from subprocess import Popen, PIPE, STDOUT
import os
import math
import scipy.optimize

class LoiterPower(Component):

    def __init__(self):
        super(LoiterPower, self).__init__()
        
        self.add_param('Vehicle', val=1.0, description='Vehicle type')
        self.add_param('rProp', val=1.0, description='prop/rotor radius [m]')
        self.add_param('W', val=1.0, description='Weight [N]')
        self.add_param('cruiseOutput', val=1.0, description='Output of Cruise analysis')
        self.add_param('hoverOutput', val=1.0, description='Output of Hover analysis')
        
        self.add_output('CL', val=1.0, description='Vehicle total cofficient of lift')
        self.add_output('VLoiter', val=1.0, description='loiter velocity [m/s]')
        self.add_output('S', val=1.0, description='reference surface area of both wings')
        self.add_output('Cd0', val=1.0, description='Overall profile drag coefficent')
        self.add_output('AR', val=1.0, description='Aspect Ratio of wings')
        self.add_output('e', val=1.0, description='span efficiency')
        self.add_output('SCdFuse', val=1.0, description='Drage area of fuselage and gears combined [m]')
        self.add_output('D', val=1.0, description='Force of Drag on vehicle at cruise')
        self.add_output('PBattery', val=1.0, description='battery power required for cruise')
        self.add_output('PCruise',val=1.0, description='Power required during cruise')
        self.add_output('etaProp', val=1.0, description='prop efficiency')
        self.add_output('etaMotor', val=1.0, description='efficiency of motor')
        self.add_output('LoverD', val=1.0, description='total lift over drag')
        self.add_output('omega', val=1.0, description='angular velocity of blade tips')
        self.add_output('B', val=1.0, description='Tip loss factor')
        self.add_output('V', val=1.0, description='minimum power Velocity')
        self.add_output('Ct', val=1.0, description='Thrust coefficient (including tip loss factor for effective disk area)')
        self.add_output('PLoiter',val=1.0, description='Power required during loiter')
        self.add_output('alpha', val=1.0, description='inflow angle')
        self.add_output('mu', val=1.0, description='advance ratio')
        self.add_output('lambda', val=1.0, description='induced velocity /w Newton method')
        self.add_output('sigma', val=1.0, description='Blade solidity')
        
    def solve_nonlinear(self, params, unknowns, resids)
    
        rho=1.225
        unknowns['PBattery'] = unknowns['PBattery']

if strcmpi(vehicle,'tiltwing')
    
    # Note typical loiter at CL^1.5/CD for quadratic drag model likely is
    # beyond CLMax for the airplane
    # Lift coefficent at loiter a little below vehicle CLmax of ~1.1
    unknowns['CL'] = 1.0
    
    # Compute velocity
    unknowns['VLoiter'] = math.sqrt(2 * params['W'] / (rho * unknowns['S'] * unknowns['CL']))
    
    # Compute drag
    unknowns['D'] = 0.5 * rho * unknowns['VLoiter']^2 * (['S'] * (['Cd0'] + ...
        ['CL']^2 / (math.pi * unknowns['AR'] * unknowns['e'])) + unknowns['SCdFuse'])
    
    # Compute cruise power estimate
    unknowns['PCruise'] = unknowns['D'] * unknowns['VLoiter']
    
    # Battery power
    unknowns['PBattery'] = unknowns['PCruise'] / unknowns['etaProp'] / unknowns['etaMotor']
    
    # Cruise L/D
    unknowns['LoverD'] = params['W'] / unknowns['D']
    
elif strcmpi(vehicle,'helicopter')
    
    # Thrust coefficient (including tip loss factor for effective disk area
    unknowns['Ct'] = params['W'] / (rho * math.pi * params['rProp']^2 * unknowns['B']^2 * unknowns['omega']^2 * params['rProp']^2)
    
    # Find velocity for min power
    unknowns['V'] = scipy.optimize.brentq(VLoiter, 0, params['V'])

    # Get loiter power
    unknowns['PLoiter'] = loiterPower(params['V'])
    
    # Battery Power
    unknowns['PBattery'] = unknowns['PLoiter'] / unknowns['etaMotor']
    
else
    error('Unrecognized vehicle!')
end


    # Compute helicopter power in at a given speed
    def LoiterPower(self, params, unknowns, resids):
        
        # Fuselage drag
        unknowns['D'] = 0.5 * rho * unknowns['VLoiter']^2 * unknowns['SCdFuse']
        
        # Inflow angle
        unknowns['alpha'] = math.atan2(unknowns['D'],params['W'])
        
        # Compute advance ratio
        unknowns['mu'] = unknowns['VLoiter'] * math.cos(unknowns['alpha']) / (unknowns['omega'] * params['rProp'])
        
        # Solve for induced velocity /w Newton method (see "Helicopter Theory" section 4.1.1)
        unknowns['lambda'] = unknowns['mu'] * math.tan(unknowns['alpha']) + unknowns['Ct'] / ...
            (2 * math.sqrt(unknowns['mu']^2 + unknowns['Ct']/2))
        for i = 1:5
            unknowns['lambda']  = (unknowns['mu'] * math.tan(unknowns['alpha']) + ...
                unknowns['Ct'] / 2 * (unknowns['mu']^2 + 2*unknowns['lambda']^2) / ...
                (unknowns['mu']^2 + unknowns['lambda']^2)^1.5) / ...
                (1 + unknowns['Ct']/2 * unknowns['lambda'] / (unknowns['mu']^2 + unknowns['lambda']^2)^1.5)
        end
        unknowns['v'] = unknowns['lambda'] * unknowns['omega'] * params['rProp'] - unknowns['VLoiter'] * math.sin(unknowns['alpha'])
        
        # Power in forward flight (see "Helicopter Theory" section 5-12)
        unknowns['PLoiter'] = params['W'] * (unknowns['VLoiter'] * math.sin(unknowns['alpha']) + 1.3 * math.cosh(8 * unknowns['mu']^2) * unknowns['v'] + ...
            unknowns['Cd0'] * unknowns['omega'] * params['rProp'] * ...
            (1 + 4.5 * unknowns['mu']^2 + 1.61 * unknowns['mu']^3.7) * ...
            (1 - (0.03 + 0.1 * unknowns['mu'] + 0.05 * math.sin(4.304 * unknowns['mu'] - 0.20)) * ...
            (1-math.cos(unknowns['alpha'])^2)) / 8 / (unknowns['Ct'] / unknowns['sigma']))
    end

end
