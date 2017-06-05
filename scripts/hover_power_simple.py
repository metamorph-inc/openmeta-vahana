# Author:         Tim Thomas
# Date:           2017-06-05
#
# Description:
#  Conversion of VahanaTradeStudy 'hoverPower.m' script
#
# Estimate hover performance
#
# Inputs:
#  vehicle      - Vehicle type ('tiltwing' or 'helicopter')
#  rProp        - Prop/rotor radius
#  W            - Weight
#  cruiseOutput - Cruise data
#
# Outputs:
#  hoverOutput - Structure with hover performance values
#

from __future__ import print_function

from openmdao.api import Component
import math

class hover_power(Component):

    def __init__(self):
        super(hover_power, self).__init__()
        
        self.add_param('vehicle', val=0.0, description='0=tiltwing, 1=helicopter')
        self.add_param('rProp', val=1.0, description='radius of prop/rotor')
        self.add_param('W', val=1.0, description='Weight')
        self.add_param('cruiseOutputOmega', val=2.0, description='Cruise data omega')
		
        self.add_output('PBattery', val=1.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
        # Altitude, compute atmospheric properties
        rho = 1.225

        # Blade parameters
        Cd0 = 0.012 # Blade airfoil profile drag coefficient
        sigma = 0.1 # Solidity (could estimate from Ct assuming some average blade CL)

        
        # Different assumptions per vehicle
        if (params['vehicle'] == 0):
            
            nProp = 8 # Number of props / motors
            ToverW = 1.7 # Max required T/W to handle rotor out w/ manuever margin
            k = 1.15 # Effective disk area factor (see "Helicopter Theory" Section 2-6.2)
            etaMotor = 0.85 # Assumed electric motor efficiency
            
            # Tip Mach number constraint for noise reasons at max thrust condition
            MTip = 0.65
            
            # Tip speed limit
            Vtip = 340.2940 * MTip / math.sqrt(ToverW) # Limit tip speed at max thrust, not hover
            omega = Vtip / params['rProp']
            
            # Thrust per prop / rotor at hover
            THover = W / nProp
            
            # Compute thrust coefficient
            Ct = THover / (rho * math.pi * params['rProp']**2 * Vtip**2)
            
            # Average blade CL (see "Helicopter Theory" section 2-6.3)
            AvgCL = 6 * Ct / sigma
            
            # Hover Power
            PHover = nProp * THover * \
                (k * math.sqrt(THover / (2 * rho * math.pi * params['rProp']**2)) + \
                sigma * Cd0 / 8 * (Vtip)**3 / (THover / (rho * math.pi * params['rProp']**2)))
            FOM = nProp * THover * math.sqrt(THover / (2 * rho * math.pi * params['rProp']**2)) / PHover
            
            # Battery power
            unknowns['PBattery'] = PHover / etaMotor
            
            # Maximum thrust per motor
            TMax = THover * ToverW
            
            # Maximum shaft power required (for motor sizing)
            # Note: Tilt-wing multirotor increases thrust by increasing RPM at constant collective
            PMax = nProp * TMax * \
                (k * math.sqrt(TMax / (2 * rho * math.pi * params['rProp']**2)) + \
                sigma * Cd0 / 8 * (Vtip * math.sqrt(ToverW))**3 / (TMax / (rho * math.pi * params['rProp']**2)))
            
            # Max battery power
            PMaxBattery = PMax / etaMotor
            
            # Maximum torque per motor
            QMax = PMax / (omega * math.sqrt(ToverW))

        elif (params['vehicle'] == 1):
            
            nProp = 1 # Number of rotors
            ToverW = 1.1 # Max required T/W for climb and operating at higher altitudes
            k = 1.15 # Effective disk area factor (see "Helicopter Theory" Section 2-6.2)
            etaMotor = 0.85 * 0.98 # Assumed motor and gearbox efficiencies (85% and 98% respectively)
            
            omega = params['cruiseOutputOmega']
            Vtip = omega * params['rProp']
            
            # Thrust per prop / rotor at hover
            THover = W / nProp
            
            # Compute thrust coefficient
            Ct = THover / (rho * math.pi * params['rProp']**2 * Vtip**2)
            
            # Average blade CL (see "Helicopter Theory" Section 2-6.4)
            AvgCL = 6 * Ct / sigma
            
            # Auto-rotation descent rate (see "Helicopter Theory" Section 3-2)
            VAutoRotation = 1.16 * math.sqrt(THover / (math.pi * params['rProp']**2))
            
            # Hover Power
            PHover = nProp * THover * \
                (k * math.sqrt(THover / (2 * rho * math.pi * params['rProp']**2)) + \
                sigma * Cd0 / 8 * (Vtip)**3 / (THover / (rho * math.pi * params['rProp']**2)))
            FOM = nProp * THover * math.sqrt(THover / (2 * rho * math.pi * params['rProp']**2)) / PHover
            
            # Battery power
            # ~10% power to tail rotor (see "Princples of Helicopter Aerodynamics" by Leishman)
            PTailRotor = 0.1 * PHover
            unknowns['PBattery'] = (PHover + PTailRotor) / etaMotor
            
            # Maximum thrust per motor
            TMax = THover * ToverW
            
            # Maximum shaft power required (for motor sizing)
            # Note: Helicopter increases thrust by increasing collective with constant RPM
            PMax = nProp * TMax * \
                (k * math.sqrt(TMax / (2 * rho * math.pi * params['rProp']**2)) + \
                sigma * Cd0 / 8 * (Vtip)**3 / (TMax / (rho * math.pi * params['rProp']**2)))
                
            # ~15% power to tail rotor for sizing (see "Princples of Helicopter Aerodynamics" by Leishman)
            PMax = 1.15 * PMax
            
            # Max battery power
            PMaxBattery = PMax / etaMotor
            
            # Maximum torque per motor
            QMax = PMax / omega
            
        else:
            pass
            #TODO: raise OpenMDAO exception

