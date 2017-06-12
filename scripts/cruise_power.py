# Company: MetaMorph, Inc.
# Author(s): Austin Tabulog, Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/5/2017
# Edit Date: 6/9/2017

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
import platform
from subprocess import Popen, PIPE, STDOUT
import os
import math

class CruisePower(Component):

    def __init__(self):
        super(CruisePower, self).__init__()
        
        self.add_param('Vehicle', val=u'abcdef', description='Vehicle type', pass_by_obj=True)  # 'tiltwing' or 'helicopter'
        self.add_param('rProp', val=0.0, description='prop/rotor radius [m]')
        self.add_param('V', val=0.0, description='Cruise speed [m/s]')
        self.add_param('W', val=0.0, description='Weight of vehicle [N]')
        
        self.add_output('etaProp', val=0.0, description='efficiency of Prop')
        self.add_output('etaMotor', val=0.0, description='efficiency of motor')
        self.add_output('CLmax', val=0.0, description='maximum CL for aircraft, section cl is much higher')
        self.add_output('bRef', val=0.0, description='reference wingspan assuming 2 props per wing with outboard props are at wingtips, 1 meter wide fuselage plus clearance between props and fuselage')
        self.add_output('SRef', val=0.0, description='reference surface area of both wings')
        self.add_output('cRef', val=0.0, description='Chord calculation of each wing')
        self.add_output('AR', val=0.0, description='Aspect Ratio of wings')
        self.add_output('D', val=0.0, description='Force of Drag on vehicle at cruise')
        self.add_output('PCruise',val=0.0, description='Power required during cruise')
        self.add_output('PBattery', val=0.0, description='battery power required for cruise')
        self.add_output('Cd0', val=0.0, description='Overall profile drag coefficent')
        self.add_output('CL', val=0.0, description='CL during cruise')
        self.add_output('LoverD', val=0.0, description='total lift over drag')
        self.add_output('omega', val=0.0, description='angular velocity of blade tips')
        self.add_output('alpha', val=0.0, description='inflow angle')
        self.add_output('mu', val=0.0, description='advance ratio')
        self.add_output('Ct', val=0.0, description='Thrust coefficient (including tip loss factor for effective disk area)')
        self.add_output('lambda', val=0.0, description='induced velocity /w Newton method')
        self.add_output('v', val=0.0, description='TBD')
        self.add_output('SCdFuse', val=0.0, description='Drage area of fuselage and gears combined [m]')
        self.add_output('Cd0Wing', val=0.0, description='wing profile drag coefficient')
        self.add_output('e', val=0.0, description='span efficiency')
        self.add_output('B', val=0.0, description='Tip loss factor')
        self.add_output('sigma', val=0.0, description='Blade solidity')
        
        
    def solve_nonlinear(self, params, unknowns, resids):
        # Altitude, compute atmospheric properties
        rho = 1.225
        
        # Fuselage / landing gear area
        unknowns['SCdFuse'] = 0.35

        if(params['Vehicle'].lower().replace('-', '') == "tiltwing"):
            # Specify stall conditions
            VStall = 35  # m/s
            unknowns['CLmax'] = 1.1  # Whole aircraft CL, section Clmax much higher

            # Compute Wingspan assuming 2 props per wing with outboard props are at
            # wingtips, 1 meter wide fuselage plus clearance between props and fuselage
            unknowns['bRef'] = 6 * params['rProp'] + 1.2  # Rough distance between hubs of outermost props

            # Compute reference area (counting both wings)
            unknowns['SRef'] = params['W'] / (0.5 * rho * VStall**2 * unknowns['CLmax'])

            # Compute reference chord (chord of each wing)
            unknowns['cRef'] = 0.5 * unknowns['SRef'] / unknowns['bRef'] 
                
            # Equivalent aspect ratio
            unknowns['AR'] = unknowns['bRef']**2 / unknowns['SRef']

            # Motor efficiency
            unknowns['etaMotor'] = 0.85

            # Wing profile drag coefficent
            unknowns['Cd0Wing'] = 0.012

            # Overall profile drag
            unknowns['Cd0'] = unknowns['Cd0Wing'] + unknowns['SCdFuse'] / unknowns['SRef']

            # Span efficiency
            unknowns['e'] = 1.3

            # Solve for CL at cruise
            unknowns['CL'] = params['W'] / (0.5 * rho * params['V']**2 * unknowns['SRef'])

            # Prop efficiency
            unknowns['etaProp'] = 0.8

            # Estimate drag at cruise using quadratic drag polar
            unknowns['D'] = 0.5 * rho * params['V']**2 * (unknowns['SRef'] * (unknowns['Cd0'] + \
                unknowns['CL']**2 / (math.pi * unknowns['AR'] * unknowns['e'])) + unknowns['SCdFuse'])

            # Compute cruise power estimate
            unknowns['PCruise'] = unknowns['D'] * params['V']

            # Battery power
            unknowns['PBattery'] = unknowns['PCruise'] / unknowns['etaProp'] / unknowns['etaMotor']

            # Cruise L/D
            unknowns['LoverD'] = params['W'] / unknowns['D']

        elif (params['Vehicle'].lower().replace('-', '') == "helicopter"):
            # Motor efficiency
            unknowns['etaMotor'] = 0.85 * 0.98 # Assumed motor and gearbox efficiencies (85%, and 98% respectively)

            # Tip Mach number constraint
            MTip = 0.65

            # Tip loss factor 
            unknowns['B'] = 0.97

            # Blade solidity
            unknowns['sigma'] = 0.1

            # Blade profile drag coefficient
            unknowns['Cd0'] = 0.012

            # Compute rotation rate at cruise to be at tip mach limit
            unknowns['omega'] = (340.2940 * MTip - params['V']) / params['rProp']

            # Fuselage drag
            unknowns['D'] = 0.5 * rho * params['V']**2 * unknowns['SCdFuse']

            # Inflow angle 
            unknowns['alpha'] = math.atan2(unknowns['D'], params['W'])

            # Compute advance ratio
            unknowns['mu'] = params['V'] * math.cos(unknowns['alpha']) / (unknowns['omega'] * params['rProp'])
                
            # Thrust coefficient (including tip loss factor for effective disk area)
            unknowns['Ct'] = params['W'] / (rho * math.pi * params['rProp']**2 * unknowns['B']**2 * unknowns['omega']**2 * params['rProp']**2)

            # Solve for induced velocity /w Newton method (see "Helicopter Theory" section 4.1.1)
            unknowns['lambda'] = unknowns['mu'] * math.tan(unknowns['alpha']) + unknowns['Ct'] / \
                (2.0 * math.sqrt(unknowns['mu']**2 + unknowns['Ct']/2.0))
            for i in range(5):
                unknowns['lambda']  = (unknowns['mu'] * math.tan(unknowns['alpha']) + \
                    unknowns['Ct'] / 2.0 * (unknowns['mu']**2 + 2.0*unknowns['lambda']**2) / \
                    (unknowns['mu']**2 + unknowns['lambda']**2)**1.5) / \
                    (1 + unknowns['Ct']/2 * unknowns['lambda'] / (unknowns['mu']**2 + unknowns['lambda']**2)**1.5)
            unknowns['v'] = unknowns['lambda'] * unknowns['omega'] * params['rProp'] - params['V'] * math.sin(unknowns['alpha'])

            # Power in forward flight (see "Helicopter Theory" section 5-12)
            unknowns['PCruise'] = params['W'] * (params['V'] * math.sin(unknowns['alpha']) + 1.3 * math.cosh(8 * unknowns['mu']**2) * unknowns['v'] + \
                unknowns['Cd0'] * unknowns['omega'] * params['rProp'] * \
                (1 + 4.5 * unknowns['mu']**2 + 1.61 * unknowns['mu']**3.7) * \
                (1 - (0.03 + 0.1 * unknowns['mu'] + 0.05 * math.sin(4.304 * unknowns['mu'] - 0.20)) * \
                (1-math.cos(unknowns['alpha'])**2)) / 8 / (unknowns['Ct'] / unknowns['sigma']))

            # 10% power added for helicopter tail rotor
            unknowns['PCruise'] = 1.1 * unknowns['PCruise']

            # Equivalent L/D, assuming power = D * V and L = W
            unknowns['LoverD'] = params['W'] / (unknowns['PCruise'] / params['V'])

            # Battery power
            unknowns['PBattery'] = unknowns['PCruise'] / unknowns['etaMotor']

        else:
            pass
            
if __name__ == "__main__":
    top = Problem()
    root = top.root = Group()

    # Sample Inputs
    indep_vars_constants = [('Vehicle', u'tiltwing', {'pass_by_obj':True}),
                            ('rProp', 1.4),
                            ('V', 50.0),
                            ('W', 2000.0)]

    root.add('Inputs', IndepVarComp(indep_vars_constants))

    root.add('Example', CruisePower())

    root.connect('Inputs.Vehicle', 'Example.Vehicle')
    root.connect('Inputs.rProp', 'Example.rProp')
    root.connect('Inputs.V', 'Example.V')
    root.connect('Inputs.W', 'Example.W')

    top.setup()
    top.run()
    
    print("Tiltwing..     PBattery:", top['Example.PBattery'])
    
    top['Inputs.Vehicle'] = u'helicopter'
    top['Inputs.rProp'] = 4.0
    
    top.run()
    
    print("Helicopter..   PBattery:", top['Example.PBattery'])