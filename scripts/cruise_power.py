"""
Attempt at translating Matlab to Python.

built from A^3's CruisePower.m code
"""

from __future__ import print_function

from openmdao.api import IndepVarComp, Component, Problem, Group, FileRef
import numpy as np
import platform
from subprocess import Popen, PIPE, STDOUT
import os

class CruisePower(Component):

    def __init__(self):
        super(CruisePower, self).__init__()

        self.add_param('Vehicle', val=1.0, description='Vehicle type')	#arb.add_param('vehicle', val=Vehicle, description='would this be how you would get the values from vehicle from an file called arb?')
        self.add_param('rProp', val=1.0, description='prop/rotor radius [m]')
        self.add_param('V', val=1.0, description='Cruise speed [m/s]')
        self.add_param('W', val=1.0, description='Weight of vehicle [N]')

        self.add_output('etaProp', val=1.0, description='efficiency of Prop')
        self.add_output('etaMotor', val=1.0, description='efficiency of motor')
        self.add_output('VStall', val=35, description='Stall speed [m/s]')
        self.add_output('CLmax', val=1.0, description='maximum CL for aircraft, section cl is much higher')
        self.add_output('rho', val=1.0, description='density of air at cruise altitude. should be solved for using a database of altitude information')

        self.add_output('bRef', val=1.0, description='reference wingspan assuming 2 props per wing with outboard props are at wingtips, 1 meter wide fuselage plus clearance between props and fuselage')
        self.add_output('sRef', val=1.0, description='reference surface area of boht wings')
        self.add_output('cRef', val=1.0, description='Chord calculation of each wing')
        self.add_output('AR', val=1.0, description='')
        self.add_output('D', val=1.0, description='Force of Drag on vehicle at cruise')
        self.add_output('PCruise',val=1.0, description='Power required during cruise')
        self.add_output('PBattery', val=1.0, description='battery power required for cruise')
        self.add_output('PBattery', val=1.0, description='battery power required for cruise')
		
		
    def solve_nonlinear(self, params, unknowns, resids):
        
        if(params['vehicle'] == 0):
            VStall = 35 # m/s
            CLmax = 1.1 # Whole aircraft CL, section Clmax much higher

            # Compute Wingspan assuming 2 props per wing with outboard props are at
            # wingtips, 1 meter wide fuselage plus clearance between props and fuselage
            unknowns['bRef'] = 6 * rProp + 1.2; # Rough distance between hubs of outermost props

            # Compute reference area (counting both wings)
            SRef = W / (0.5 * rho * VStall^2 * CLmax);

            # Compute reference chord (chord of each wing)
            cRef = 0.5 * SRef / bRef; 
                
            # Equivalent aspect ratio
            AR = bRef^2 / SRef;

            # Motor efficiency
            etaMotor = 0.85;

            # Wing profile drag coefficent
            Cd0Wing = 0.012;

            # Overall profile drag
            Cd0 = Cd0Wing + SCdFuse / SRef;

            # Span efficiency
            e = 1.3;

            # Solve for CL at cruise
            CL = W / (0.5 * rho * V^2 * SRef);

            # Prop efficiency
            etaProp = 0.8;

            # Estimate drag at cruise using quadratic drag polar
            D = 0.5 * rho * V^2 * (SRef * (Cd0 + ...
                CL^2 / (pi * AR * e)) + SCdFuse);

            # Compute cruise power estimate
            PCruise = D * V;

            # Battery power
            PBattery = PCruise / etaProp / etaMotor;

            # Cruise L/D
            LoverD = W / D;

        elif (params['vehicle'] == 1):

            # Motor efficiency
            unknowns['etaMotor'] = 0.85 * 0.98; # Assumed motor and gearbox efficiencies (85%, and 98% respectively)

            # Tip Mach number constraint
            MTip = 0.65;

            # Tip loss factor 
            B = 0.97;

            # Blade solidity
            sigma = 0.1;

            # Blade profile drag coefficient
            Cd0 = 0.012;

            # Compute rotation rate at cruise to be at tip mach limit
            omega = (340.2940 * MTip - V) / rProp;

            # Fuselage drag
            D = 0.5 * rho * V^2 * SCdFuse;

            # Inflow angle 
            alpha = atan(D/W);

            # Compute advance ratio
            mu = V * cos(alpha) / (omega * rProp);
                
            # Thrust coefficient (including tip loss factor for effective disk area)
            Ct = W / (rho * pi * rProp^2 * B^2 * omega^2 * rProp^2);

            # Solve for induced velocity /w Newton method (see "Helicopter Theory" section 4.1.1)
            lambda = mu * tan(alpha) + Ct / ...
                (2 * sqrt(mu^2 + Ct/2));
            for i = 1:5
                lambda  = (mu * tan(alpha) + ...
                    Ct / 2 * (mu^2 + 2*lambda^2) / ...
                    (mu^2 + lambda^2)^1.5) / ...
                    (1 + Ct/2 * lambda / (mu^2 + lambda^2)^1.5);
            end
            v = lambda * omega * rProp - V * sin(alpha);

            # Power in forward flight (see "Helicopter Theory" section 5-12)
            PCruise = W * (V * sin(alpha) + 1.3 * cosh(8 * mu^2) * v + ...
                Cd0 * omega * rProp * ...
                (1 + 4.5 * mu^2 + 1.61 * mu^3.7) * ...
                (1 - (0.03 + 0.1 * mu + 0.05 * sin(4.304 * mu - 0.20)) * ...
                (1-cos(alpha)^2)) / 8 / (Ct / sigma));

            # 10% power added for helicopter tail rotor
            PCruise = 1.1 * PCruise;

            # Equivalent L/D, assuming power = D * V and L = W
            LoverD = W / (PCruise / V);

            # Battery power
            PBattery = PCruise / etaMotor;

            else

            error('Unrecognized vehicle!')

            end