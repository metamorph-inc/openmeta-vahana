# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe, Austin Tabulog
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/5/2017
# Edit Date: 6/5/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate time and energy use for a reserve VTOL mission
# Inputs:
#    #TODO

# Outputs:
#    #TODO

from __future__ import print_function

from openmdao.api import IndepVarComp, Component, Problem, Group, FileRef
import numpy as np
from scipy import optimize, special
import platform
from subprocess import Popen, PIPE, STDOUT
import os
import math

class LoiterPower(Component):

    def __init__(self):
        super(LoiterPower, self).__init__()
        
        self.add_param('Vehicle', val=1.0, description='Vehicle type')
        self.add_param('rProp', val=1.0, description='prop/rotor radius [m]')
        self.add_param('W', val=1.0, description='Weight [N]')
        self.add_param('V', val=1.0, description='Speed [m/s]')
        self.add_param('cruiseOutputP', val=1.0, description='Output of Cruise analysis')
        self.add_param('cruiseOutputSRef', val=1.0, description='reference surface area of both wings')
        self.add_param('cruiseOutputCd0', val=1.0, description='Overall profile drag coefficent')
        self.add_param('cruiseOutputAR', val=1.0, description='Aspect Ratio of wings')
        self.add_param('cruiseOutputE', val=1.0, description='span efficiency')
        self.add_param('cruiseOutputSCdFuse', val=1.0, description='#TODO')
        self.add_param('cruiseOutputEtaProp', val=1.0, description='prop efficiency')
        self.add_param('cruiseOutputEtaMotor', val=1.0, description='efficiency of motor')
        self.add_param('cruiseOutputOmega', val=1.0, description='angular velocity of blade tips')
        self.add_param('cruiseOutputSigma', val=1.0, description='#TODO')
        
        self.add_output('CL', val=1.0, description='Vehicle total cofficient of lift')
        self.add_output('VLoiter', val=1.0, description='loiter velocity [m/s]')
        self.add_output('D', val=1.0, description='Force of Drag on vehicle at cruise')
        self.add_output('PBattery', val=1.0, description='battery power required for cruise')
        self.add_output('PCruise',val=1.0, description='Power required during cruise')
        self.add_output('LoverD', val=1.0, description='total lift over drag')
        self.add_output('B', val=1.0, description='Tip loss factor')
        self.add_output('loiterV', val=1.0, description='minimum power Velocity')
        self.add_output('Ct', val=1.0, description='Thrust coefficient (including tip loss factor for effective disk area)')
        self.add_output('PLoiter',val=1.0, description='Power required during loiter')
        
    def solve_nonlinear(self, params, unknowns, resids):
    
        rho=1.225
        unknowns['PBattery'] = unknowns['PBattery']

        if (params['Vehicle'] == 0):
            # Note typical loiter at CL^1.5/CD for quadratic drag model likely is
            # beyond CLMax for the airplane
            # Lift coefficent at loiter a little below vehicle CLmax of ~1.1
            unknowns['CL'] = 1.0
            
            # Compute velocity
            unknowns['VLoiter'] = math.sqrt(2 * params['W'] / (rho * params['cruiseOutputSRef'] * unknowns['CL']))
            
            # Compute drag
            unknowns['D'] = 0.5 * rho * unknowns['VLoiter']**2 * (params['cruiseOutputSRef'] * (params['cruiseOutputCd0'] + \
                unknowns['CL']**2 / (math.pi * params['cruiseOutputAR'] * params['cruiseOutputE'])) + params['cruiseOutputSCdFuse'])
            
            # Compute cruise power estimate
            unknowns['PCruise'] = unknowns['D'] * unknowns['VLoiter']
            
            # Battery power
            unknowns['PBattery'] = unknowns['PCruise'] / params['cruiseOutputEtaProp'] / params['cruiseOutputEtaMotor']
            
            # Cruise L/D
            unknowns['LoverD'] = params['W'] / unknowns['D']
            
        elif (params['Vehicle'] == 1):
        
            def loiterPower(Vloiter):
                # Fuselage drag
                D = 0.5 * rho * unknowns['VLoiter']**2 * params['cruiseOutputSCdFuse']
                
                # Inflow angle
                alpha = math.atan2(D, params['W'])
                
                # Compute advance ratio
                mu = unknowns['VLoiter'] * math.cos(alpha) / (params['cruiseOutputOmega'] * params['rProp'])
                
                # Solve for induced velocity /w Newton method (see "Helicopter Theory" section 4.1.1)
                lambda_ = mu * math.tan(alpha) + unknowns['Ct'] / \
                    (2 * math.sqrt(mu**2 + unknowns['Ct']/2))
                for i in range(5):
                    lambda_  = (mu * math.tan(alpha) + \
                        unknowns['Ct'] / 2 * (mu**2 + 2*lambda_**2) / \
                        (mu**2 + lambda_**2)**1.5) / \
                        (1 + unknowns['Ct']/2 * lambda_ / (mu**2 + lambda_**2)**1.5)
                v = lambda_ * params['cruiseOutputOmega'] * params['rProp'] - unknowns['VLoiter'] * math.sin(alpha)
                
                # Power in forward flight (see "Helicopter Theory" section 5-12)
                PLoiter = params['W'] * (unknowns['VLoiter'] * math.sin(alpha) + 1.3 * math.cosh(8 * mu**2) * v + \
                    params['cruiseOutputCd0'] * params['cruiseOutputOmega'] * params['rProp'] * \
                    (1 + 4.5 * mu**2 + 1.61 * mu**3.7) * \
                    (1 - (0.03 + 0.1 * mu + 0.05 * math.sin(4.304 * mu - 0.20)) * \
                    (1-math.cos(alpha)**2)) / 8 / (unknowns['Ct'] / params['cruiseOutputSigma']))
                
                return PLoiter
        
        
            # Thrust coefficient (including tip loss factor for effective disk area
            unknowns['Ct'] = params['W'] / (rho * math.pi * params['rProp']**2 * unknowns['B']**2 * params['cruiseOutputOmega']**2 * params['rProp']**2)
            
            # Find velocity for min power
            unknowns['loiterV'] = optimize.fminbound(loiterPower, 0, params['V']) #https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fminbound.html#scipy.optimize.fminbound
            
            # instead of
            # unknowns['loiterV'] = optimize.brentq(loiterPower, 0, params['V']) #https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.optimize.brentq.html
            # brentq requires that f[a] and f[b] have different signs if a and b are the lower and upper bounds respectively
            
            # Get loiter power
            unknowns['PLoiter'] = loiterPower(unknowns['loiterV'])
            
            # Battery Power
            unknowns['PBattery'] = unknowns['PLoiter'] / params['cruiseOutputEtaMotor']
    
        else:
            pass
            # error