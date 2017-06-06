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
#   hoverOutput_PMax        - TODO
#   prop_mass               - propeller blade mass [kg]
#   fuselage_mass           - fuselage mass [kg]
#   wire_mass               - wire mass [kg]
#   wing_mass               - wing mass [kg]
#   canard_mass             - canard mass [kg]

# Outputs:
#   mass_payload        - total payload mass [kg]
#   mass_seat           - seat mass [kg]
#   mass_avionics       - avionics mass [kg]
#   mass_motors         - motor mass [kg]
#   mass_battery        - battery mass [kg]
#   mass_servos         - servo mass [kg]
#   mass_tilt           - tilt mechanism mass [kg]
#   mass_brs            - ballistic recovery system mass [kg]
#   mass_wing           - wing mass [kg]
#   mass_canard         - canard mass [kg]
#   mass_props          - propeller blade mass [kg]
#   mass_hub            - hub mass [kg]
#   mass_fuselage       - fuselage mass [kg]
#   mass_lg             - landing gear mass [kg]
#   mass_wire           - electrical wire mass [kg]
#   mass_structural     - total structural mass [kg]
#   mass_m              - total mass + 10% fudge factor [kg]
#   mass_rotor          - rotor mass [kg]
#   mass_tailRotor      - tail rotor mass [kg]
#   mass_transmission   - transmission mass [kg]
#   mass_W              - total weight + 10% fudge factor [N]


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
        self.add_param('hoverOutput_PMax', val=0.0)
        self.add_param('prop_mass', val=0.0)
        self.add_param('fuselage_mass', val=0.0)
        self.add_param('wire_mass', val=0.0)
        self.add_param('wing_mass', val=0.0)
        self.add_param('canard_mass', val=0.0)

        self.add_output('mass_payload', val=0.0)
        self.add_output('mass_seat', val=0.0)
        self.add_output('mass_avionics', val=0.0)
        self.add_output('mass_motors', val=0.0)
        self.add_output('mass_battery', val=0.0)
        self.add_output('mass_servos', val=0.0)
        self.add_output('mass_tilt', val=0.0)
        self.add_output('mass_brs', val=0.0)
        self.add_output('mass_wing', val=0.0)
        self.add_output('mass_canard', val=0.0)
        self.add_output('mass_props', val=0.0)
        self.add_output('mass_hub', val=0.0)
        self.add_output('mass_fuselage', val=0.0)
        self.add_output('mass_lg', val=0.0)
        self.add_output('mass_wire', val=0.0)
        self.add_output('mass_structural', val=0.0)
        self.add_output('mass_m', val=0.0)
        self.add_output('mass_rotor', val=0.0)
        self.add_output('mass_tailRotor', val=0.0)
        self.add_output('mass_transmission', val=0.0)
        self.add_output('mass_W', val=0.0)

    def solve_nonlinear(self, params, unknowns, resids): #QUESTION: does this always need to be named solve_nonlinear
        # Total payload mass
        unknowns['mass_payload'] = params['payload']
        
        # Fixed weight components between configs
        unknowns['mass_seat'] = 15 # kg
        unknowns['mass_avionics'] = 15 # kg, Flight computer, sensors, BMS, backup power battery
        
        # Motor and battery weight (design variables)
        unknowns['mass_motors'] = params['mMotors']
        unknowns['mass_battery'] = params['mBattery']
        
        mPerServo = 0.65 # per servo in class needed
        mPerTilt = 4 # per wing tilt actuator (prelim design)
            
        if (params['vehicle'] == 0 ):
            # Servo weight
            unknowns['mass_servos'] = mPerServo * 12 # 4 ctrl surfaces + variable pitch actuators
            
            # Tilt mechanism weight
            unknowns['mass_tilt'] = 2 * mPerTilt # 2 wing tilt mechanisms
        
            # Ballistic Recovery System 
            # For 1600 lbf experimental aircraft, should actually scale with size
            unknowns['mass_brs'] = 16
        
            # Wing weight estimate (taking 40% of load w/ 20% semi-span winglets)
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass_wing'] = params['wing_mass']
            
            # Canard weight estimate (taking 60% of load)
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass_canard'] = params['canard_mass']
            
            # Propeller blade mass plus 2 kg per VP hub
            unknowns['mass_props'] = 8 * params['prop_mass']
            unknowns['mass_hub'] = 8 * 2
            
            # Fuselage mass assuming 5 m long fuselage, 1 m wide fuselage, and 1.65
            # m tall fuselage
            unknowns['mass_fuselage'] = params['fuselage_mass']
            
            # Landing gear mass is assumed to be 2% of MTOW for helicopters
            unknowns['mass_lg'] = 0.02 * params['mtow']
            
            # Wire mass estimates
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass_wire'] = params['wire_mass']
        
            # Total structural mass (material cost)
            unknowns['mass_structural'] = unknowns['mass_wing'] + unknowns['mass_canard'] + unknowns['mass_props'] + unknowns['mass_hub'] + unknowns['mass_fuselage'] + unknowns['mass_lg']
            
            # Total mass + 10% Fudge factor
            unknowns['mass_m'] = 1.1 * (mass.params['payload'] + unknowns['mass_seat'] + unknowns['mass_avionics'] + unknowns['mass_servos'] + \
                unknowns['mass_tilt'] + unknowns['mass_structural'] +  \
                unknowns['mass_battery'] + unknowns['mass_motors'] + unknowns['mass_wire'] + unknowns['mass_brs'])            
        
        elif (params['vehicle'] == 1 ):
            # Servo weight
            unknowns['mass_servos'] = mPerServo * 8 # 8 for redundant collective, cyclic (2x), tail rotor
           
            # No BRS for helicopter
            unknowns['mass_brs'] = 0
        
            # Rotor mass plus assumed 4% of params['mtow'] for hub and linkages
            unknowns['mass_rotor'] = params['prop_mass']
            unknowns['mass_hub'] = 0.04 * params['mtow']
            
            # Tail rotor mass (20% main rotor radius), assuming moment arm of 1.25x
            # rotor radius, need to be capable of providing 1.5x thrust required to
            # fight max rotor torque
            unknowns['mass_tailRotor'] = params['prop_mass']
            
            # Transmission mass
            # Estimate from OH-58 gearbox study that has a lower bound of 0.26 lb/Hp
            # https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19880020744.pdf    
            transmissionPowerDensity = 6.3 # kW/kg
            unknowns['mass_transmission'] = params['hoverOutput_PMax'] / 1000 / transmissionPowerDensity
            
            # Fuselage mass assuming fuselage length of 1.5 m nose plus 1.25x rotor
            # radius for tailboom length, 1 meter wide and 2 meter tall fuselage.
            unknowns['mass_fuselage'] = params['mass_fuselage']
            
            # Landing gear mass is assumed to be 2% of MTOW for helicopters
            unknowns['mass_lg'] = 0.02 * params['mtow']
            
            # Wire mass assuming motors located close to battery
            unknowns['mass_wire'] = unknowns['mass_wire']
            
            # Total structural mass (material cost)
            unknowns['mass_structural'] = unknowns['mass_rotor'] + unknowns['mass_hub'] + unknowns['mass_tailRotor'] + unknowns['mass_fuselage'] + unknowns['mass_lg']
            
            # Total mass + 10% Fudge factor
            unknowns['mass_m'] = 1.1 * (mass.params['payload'] + unknowns['mass_seat'] + unknowns['mass_avionics'] + unknowns['mass_servos'] + \
                unknowns['mass_transmission'] + unknowns['mass_structural'] + \
                unknowns['mass_battery'] + unknowns['mass_motors'] + unknowns['mass_wire'] + unknowns['mass_brs'])

        else:
            print('Unrecognized vehicle!')
            pass
            
        unknowns['mass_W'] = unknowns['mass_m'] * 9.8
    