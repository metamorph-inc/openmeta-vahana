# Weight models for both configurations
#
# Inputs:
#  vehicle      - vehicle type ('tiltwing' or 'helicopter')
#  rProp        - prop/rotor radius [m]
#  mBattery     - battery mass [kg]
#  mMotors      - total motor mass [kg]
#  mtow         - maximum takeoff mass [kg]
#  hoverOutput  - Structure with computed hover performance
#  cruiseOutput - Structure with computed cruise performance
#  payload      - Payload mass [kg]
#
# Outputs:
#  mass - structure with component masses [kg] and maximum takeoff weight [N]



    from __future__ import print_function

    from openmdao.api import IndepVarComp, Component, Problem, Group, FileRef
    import numpy as np

    class configWeight(Component):

        def __init__(self):
            super(configWeight, self).__init__()
            
            self.add_param('cruiseOutput.bRef', val=1.0)
        self.add_param('cruiseOutput.cRef', val=1.0)
        self.add_param('hoverOutput.TMax', val=1.0)
        self.add_param('hoverOutput.PMaxBattery', val=1.0)
        self.add_param('hoverOutput.QMax', val=1.0)
        self.add_param('hoverOutput.PMax', val=1.0)
        self.add_param('vehicle', val=1.0)
        self.add_param('rProp', val=1.0)
        self.add_param('mBattery', val=1.0)
        self.add_param('mMotors', val=1.0)
        self.add_param('mtow', val=1.0)
        self.add_param('payload', val=1.0)

        self.add_output('mass.payload', val=1.0)
        self.add_output('mass.seat', val=1.0)
        self.add_output('mass.avionics', val=1.0)
        self.add_output('mass.motors', val=1.0)
        self.add_output('mass.battery', val=1.0)
        self.add_output('mass.servos', val=1.0)
        self.add_output('mass.tilt', val=1.0)
        self.add_output('mass.brs', val=1.0)
        self.add_output('mass.wing', val=1.0)
        self.add_output('mass.canard', val=1.0)
        self.add_output('mass.props', val=1.0)
        self.add_output('mass.hub', val=1.0)
        self.add_output('mass.fuselage', val=1.0)
        self.add_output('mass.lg', val=1.0)
        self.add_output('mass.wire', val=1.0)
        self.add_output('mass.structural', val=1.0)
        self.add_output('mass.m', val=1.0)
        self.add_output('mass.rotor', val=1.0)
        self.add_output('mass.tailRotor', val=1.0)
        self.add_output('mass.transmission', val=1.0)
        self.add_output('mass.W', val=1.0)

        def solve_nonlinear(self, params, unknowns, resids):
            
            
        # Total params['payload'] mass
        unknowns['mass.params['payload']'] = params['payload']
        
        # Fixed weight components between configs
        unknowns['mass.seat'] = 15 # kg
        unknowns['mass.avionics'] = 15 # kg, Flight computer, sensors, BMS, backup power battery
        
        # Motor and battery weight (design variables)
        unknowns['unknowns['mass.m']otors'] = params['mMotors']
        unknowns['mass.battery'] = params['mBattery']
        
        mPerServo = 0.65 # per servo in class needed
        mPerTilt = 4 # per wing tilt actuator (prelim design)
        
        if strcmpi(params['vehicle'],'tiltwing')
            
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
            unknowns['mass.wing'] = wingMass(params['mtow']*9.8,params['cruiseOutput.bRef'],params['cruiseOutput.cRef'],0.2,0.4,\
                [2*(0.5 + params['rProp']) / params['cruiseOutput.bRef'],2*(0.5 + 3*params['rProp'] + 0.05)/params['cruiseOutput.bRef']], params['hoverOutput.TMax'])
            
            # Canard weight estimate (taking 60% of load)
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass.canard'] = wingMass(params['mtow']*9.8,params['cruiseOutput.bRef'],params['cruiseOutput.cRef'],0,0.6,\
                [2*(0.5 + params['rProp']) / params['cruiseOutput.bRef'],2*(0.5 + 3*params['rProp'] + 0.05)/params['cruiseOutput.bRef']], params['hoverOutput.TMax'])
            
            # Propeller blade mass plus 2 kg per VP hub
            unknowns['mass.props'] = 8 * propMass(params['rProp'],params['hoverOutput.TMax'])
            unknowns['mass.hub'] = 8 * 2
            
            # Fuselage mass assuming 5 m long fuselage, 1 m wide fuselage, and 1.65
            # m tall fuselage
            unknowns['mass.fuselage'] = fuselageMass(5,1,1.65,params['cruiseOutput.bRef'],params['mtow']*9.8)
            
            # Landing gear mass is assumed to be 2% of MTOW for helicopters
            unknowns['mass.lg'] = 0.02 * params['mtow']
            
            # Wire mass estimates
            # Inboard motor tips located 0.5 m from centerline, with 0.05 m gap to
            # outer motors
            unknowns['mass.wire'] = wireMass(params['cruiseOutput.bRef'],5,1.65,params['params['hoverOutput.PMax']Battery'],[2*(0.5 + params['rProp']) / params['cruiseOutput.bRef'] * ones(1,4),2*(0.5 + 3*params['rProp'] + 0.05)/params['cruiseOutput.bRef'] * ones(1,4)])
        
            # Total structural mass (material cost)
            unknowns['mass.structural'] = unknowns['mass.wing'] + unknowns['mass.canard'] + unknowns['mass.props'] + unknowns['mass.hub'] + unknowns['mass.fuselage'] + unknowns['mass.lg']
            
            # Total mass + 10% Fudge factor
            unknowns['mass.m'] = 1.1 * (unknowns['mass.params['payload']'] + unknowns['mass.seat'] + unknowns['mass.avionics'] + unknowns['mass.servos'] + \
                unknowns['mass.tilt'] + unknowns['mass.structural'] +  \
                unknowns['mass.battery'] + unknowns['unknowns['mass.m']otors'] + unknowns['mass.wire'] + unknowns['mass.brs'])
                
        elseif strcmpi(params['vehicle'],'helicopter')
            
            # Servo weight
            unknowns['mass.servos'] = mPerServo * 8 # 8 for redundant collective, cyclic (2x), tail rotor
           
            # No BRS for helicopter
            unknowns['mass.brs'] = 0
        
            # Rotor mass plus assumed 4% of params['mtow'] for hub and linkages
            unknowns['mass.rotor'] = propMass(params['rProp'],params['hoverOutput.TMax'])
            unknowns['mass.hub'] = 0.04 * params['mtow']
            
            # Tail rotor mass (20% main rotor radius), assuming moment arm of 1.25x
            # rotor radius, need to be capable of providing 1.5x thrust required to
            # fight max rotor torque
            unknowns['mass.tailRotor'] = propMass(params['rProp']/5,1.5*params['hoverOutput.QMax']/(1.25 * params['rProp'])) 
            
            # Transmission mass
            # Estimate from OH-58 gearbox study that has a lower bound of 0.26 lb/Hp
            # https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19880020744.pdf    
            transmissionPowerDensity = 6.3 # kW/kg
            unknowns['mass.transmission'] = params['hoverOutput.PMax'] / 1000 / transmissionPowerDensity
            
            # Fuselage mass assuming fuselage length of 1.5 m nose plus 1.25x rotor
            # radius for tailboom length, 1 meter wide and 2 meter tall fuselage.
            unknowns['mass.fuselage'] = fuselageMass(1.5+1.25*params['rProp'],1,2,1,params['mtow']*9.8)
            
            # Landing gear mass is assumed to be 2% of MTOW for helicopters
            unknowns['mass.lg'] = 0.02 * params['mtow']
            
            # Wire mass assuming motors located close to battery
            unknowns['mass.wire'] = wireMass(0,1.5+1.25*params['rProp'],2,params['params['hoverOutput.PMax']Battery'],0)
            
            # Total structural mass (material cost)
            unknowns['mass.structural'] = unknowns['mass.rotor'] + unknowns['mass.hub'] + unknowns['mass.tailRotor'] + unknowns['mass.fuselage'] + unknowns['mass.lg']
            
            # Total mass + 10% Fudge factor
            unknowns['mass.m'] = 1.1 * (unknowns['mass.params['payload']'] + unknowns['mass.seat'] + unknowns['mass.avionics'] + unknowns['mass.servos'] + \
                unknowns['mass.transmission'] + unknowns['mass.structural'] + \
                unknowns['mass.battery'] + unknowns['unknowns['mass.m']otors'] + unknowns['mass.wire'] + unknowns['mass.brs'])
            
        else
            error('Unrecognized params['vehicle']!') 
        
        
        unknowns['mass.W'] = unknowns['mass.m'] * 9.8
        
