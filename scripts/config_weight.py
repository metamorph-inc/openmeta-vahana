# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/6/2017
# Edit Date: 6/6/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Mass & weight models for both the tilt-wing and helicopter configurations
# Inputs:
#   vehicle                 - vehicle type
#   rProp                   - prop/rotor radius [m]
#   mBattery                - battery mass [kg]
#   mMotors                 - total motor mass [kg]
#   mtow                    - maximum takeoff mass [kg]
#   payload                 - Payload mass [kg]
#   cruiseOutput.bRef       - TODO
#   cruiseOutput.cRef       - TODO
#   hoverOutput.TMax        - TODO
#   hoverOutput.PMaxBattery - TODO
#   hoverOutput.QMax        - TODO
#   hoverOutput.PMax        - TODO
#   prop.mass               - propeller blade mass [kg]
#   fuselage.mass           - fuselage mass [kg]
#   wire.mass               - wire mass [kg]
#   wing.mass               - wing mass [kg]
#   canard.mass             - canard mass [kg]

# Outputs:
#   mass.payload        - total payload mass [kg]
#   mass.seat           - seat mass [kg]
#   mass.avionics       - avionics mass [kg]
#   mass.motors         - motor mass [kg]
#   mass.battery        - battery mass [kg]
#   mass.servos         - servo mass [kg]
#   mass.tilt           - tilt mechanism mass [kg]
#   mass.brs            - ballistic recovery system mass [kg]
#   mass.wing           - wing mass [kg]
#   mass.canard         - canard mass [kg]
#   mass.props          - propeller blade mass [kg]
#   mass.hub            - hub mass [kg]
#   mass.fuselage       - fuselage mass [kg]
#   mass.lg             - landing gear mass [kg]
#   mass.wire           - electrical wire mass [kg]
#   mass.structural     - total structural mass [kg]
#   mass.m              - total mass + 10% fudge factor [kg]
#   mass.rotor          - rotor mass [kg]
#   mass.tailRotor      - tail rotor mass [kg]
#   mass.transmission   - transmission mass [kg]
#   mass.W              - total weight + 10% fudge factor [N]


from __future__ import print_function

from openmdao.api import Component
import math

class config_weight(Component):

    def __init__(self):
        super(config_weight, self).__init__()
        self.add_param('vehicle', val=0.0)
        self.add_param('rProp', val=0.0)
        self.add_param('mBattery', val=0.0)
        self.add_param('mMotors', val=0.0)
        self.add_param('mtow', val=0.0)
        self.add_param('payload', val=0.0)
        self.add_param('cruiseOutput.bRef', val=0.0)
        self.add_param('cruiseOutput.cRef', val=0.0)
        self.add_param('hoverOutput.TMax', val=0.0)
        self.add_param('hoverOutput.PMaxBattery', val=0.0)
        self.add_param('hoverOutput.QMax', val=0.0)
        self.add_param('hoverOutput.PMax', val=0.0)
        self.add_param('prop.mass', val=0.0)
        self.add_param('fuselage.mass', val=0.0)
        self.add_param('wire.mass', val=0.0)
        self.add_param('wing.mass', val=0.0)
        self.add_param('canard.mass', val=0.0)
        self.add_param('vehicle', val=0.0)
        self.add_param('rProp', val=0.0)
        self.add_param('mBattery', val=0.0)
        self.add_param('mMotors', val=0.0)
        self.add_param('mtow', val=0.0)
        self.add_param('payload', val=0.0)

        self.add_output('mass.payload', val=0.0)
        self.add_output('mass.seat', val=0.0)
        self.add_output('mass.avionics', val=0.0)
        self.add_output('mass.motors', val=0.0)
        self.add_output('mass.battery', val=0.0)
        self.add_output('mass.servos', val=0.0)
        self.add_output('mass.tilt', val=0.0)
        self.add_output('mass.brs', val=0.0)
        self.add_output('mass.wing', val=0.0)
        self.add_output('mass.canard', val=0.0)
        self.add_output('mass.props', val=0.0)
        self.add_output('mass.hub', val=0.0)
        self.add_output('mass.fuselage', val=0.0)
        self.add_output('mass.lg', val=0.0)
        self.add_output('mass.wire', val=0.0)
        self.add_output('mass.structural', val=0.0)
        self.add_output('mass.m', val=0.0)
        self.add_output('mass.rotor', val=0.0)
        self.add_output('mass.tailRotor', val=0.0)
        self.add_output('mass.transmission', val=0.0)
        self.add_output('mass.W', val=0.0)

    def solve_nonlinear(self, params, unknowns, resids): #QUESTION: does this always need to be named solve_nonlinear
        # Total payload mass
        unknowns['mass.payload'] = params['payload']
        
        # Fixed weight components between configs
        unknowns['mass.seat'] = 15 # kg
        unknowns['mass.avionics'] = 15 # kg, Flight computer, sensors, BMS, backup power battery
        
        # Motor and battery weight (design variables)
        unknowns['mass.motors'] = params['mMotors']
        unknowns['mass.battery'] = params['mBattery']
        
        mPerServo = 0.65 # per servo in class needed
        mPerTilt = 4 # per wing tilt actuator (prelim design)
            
        if (params['vehicle'] == 0 ):
            # Servo weight
            unknowns['mass.servos'] = mPerServo * 12 # 4 ctrl surfaces + variable pitch actuators
            
            # Tilt mechanism weight
            unknowns['mass.tilt'] = 2 * mPerTilt # 2 wing tilt mechanisms
        
            # Ballistic Recovery System 
            # For 1600 lbf experimental aircraft, should actually scale with size
            unknowns['mass.brs'] = 16
        
            # Wing weight estimate (taking 40% of load w/ 20% semi-span winglets)
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass.wing'] = params['wing.mass']
            
            # Canard weight estimate (taking 60% of load)
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass.canard'] = params['canard.mass']
            
            # Propeller blade mass plus 2 kg per VP hub
            unknowns['mass.props'] = 8 * params['prop.mass']
            unknowns['mass.hub'] = 8 * 2
            
            # Fuselage mass assuming 5 m long fuselage, 1 m wide fuselage, and 1.65
            # m tall fuselage
            unknowns['mass.fuselage'] = params['fuselage.mass']
            
            # Landing gear mass is assumed to be 2% of MTOW for helicopters
            unknowns['mass.lg'] = 0.02 * params['mtow']
            
            # Wire mass estimates
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass.wire'] = params['wire.mass']
        
            # Total structural mass (material cost)
            unknowns['mass.structural'] = unknowns['mass.wing'] + unknowns['mass.canard'] + unknowns['mass.props'] + unknowns['mass.hub'] + unknowns['mass.fuselage'] + unknowns['mass.lg']
            
            # Total mass + 10% Fudge factor
            unknowns['mass.m'] = 1.1 * (mass.params['payload'] + unknowns['mass.seat'] + unknowns['mass.avionics'] + unknowns['mass.servos'] + \
                unknowns['mass.tilt'] + unknowns['mass.structural'] +  \
                unknowns['mass.battery'] + unknowns['mass.motors'] + unknowns['mass.wire'] + unknowns['mass.brs'])            
        
        elif (params['vehicle'] == 1 ):
            # Servo weight
            unknowns['mass.servos'] = mPerServo * 8 # 8 for redundant collective, cyclic (2x), tail rotor
           
            # No BRS for helicopter
            unknowns['mass.brs'] = 0
        
            # Rotor mass plus assumed 4% of params['mtow'] for hub and linkages
            unknowns['mass.rotor'] = params['prop.mass']
            unknowns['mass.hub'] = 0.04 * params['mtow']
            
            # Tail rotor mass (20% main rotor radius), assuming moment arm of 1.25x
            # rotor radius, need to be capable of providing 1.5x thrust required to
            # fight max rotor torque
            unknowns['mass.tailRotor'] = params['prop.mass']
            
            # Transmission mass
            # Estimate from OH-58 gearbox study that has a lower bound of 0.26 lb/Hp
            # https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19880020744.pdf    
            transmissionPowerDensity = 6.3 # kW/kg
            unknowns['mass.transmission'] = params['hoverOutput.PMax'] / 1000 / transmissionPowerDensity
            
            # Fuselage mass assuming fuselage length of 1.5 m nose plus 1.25x rotor
            # radius for tailboom length, 1 meter wide and 2 meter tall fuselage.
            unknowns['mass.fuselage'] = params['mass.fuselage']
            
            # Landing gear mass is assumed to be 2% of MTOW for helicopters
            unknowns['mass.lg'] = 0.02 * params['mtow']
            
            # Wire mass assuming motors located close to battery
            unknowns['mass.wire'] = unknowns['mass.wire']
            
            # Total structural mass (material cost)
            unknowns['mass.structural'] = unknowns['mass.rotor'] + unknowns['mass.hub'] + unknowns['mass.tailRotor'] + unknowns['mass.fuselage'] + unknowns['mass.lg']
            
            # Total mass + 10% Fudge factor
            unknowns['mass.m'] = 1.1 * (mass.params['payload'] + unknowns['mass.seat'] + unknowns['mass.avionics'] + unknowns['mass.servos'] + \
                unknowns['mass.transmission'] + unknowns['mass.structural'] + \
                unknowns['mass.battery'] + unknowns['mass.motors'] + unknowns['mass.wire'] + unknowns['mass.brs'])

        else:
            print('Unrecognized vehicle!')
            pass
            
        unknowns['mass.W'] = unknowns['mass.m'] * 9.8
    