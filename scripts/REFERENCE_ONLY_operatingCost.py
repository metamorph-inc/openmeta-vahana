# Estimate direct operating costs per flight including: acquisition cost,
# insurance cost, operating facility cost, energy cost, andn maintenance. 
#
# Inputs:
#  vehicle      - Vehicle type ('tiltwing' or 'helicopter')
#  rProp        - Propeller or rotor radius [m]
#  flightTime   - Flight time for nominal flight [sec]
#  E            - Energy use for flight [kW-hr]
#  mass         - Maximum takeoff mass [kg]
#  cruiseOutput - Structure containing cruise performance outputs
#
# Outputs:
#  C - Operating cost per flight [$]



    from __future__ import print_function

    from openmdao.api import IndepVarComp, Component, Problem, Group, FileRef
    import numpy as np

    class operatingCost(Component):

        def __init__(self):
            super(operatingCost, self).__init__()
            
            self.add_param('mass_structural', val=1.0)
        self.add_param('mass_battery', val=1.0)
        self.add_param('mass_motors', val=1.0)
        self.add_param('vehicle', val=1.0)
        self.add_param('rProp', val=1.0)
        self.add_param('flightTime', val=1.0)
        self.add_param('E', val=1.0)
        self.add_param('cruiseOutput', val=1.0)

        self.add_output('C_flightHoursPerYear', val=1.0)
        self.add_output('C_flightsPerYear', val=1.0)
        self.add_output('C_flightHoursPerYear', val=1.0)
        self.add_output('C_vehicleLifeYears', val=1.0)
        self.add_output('C_nVehiclesPerFacility', val=1.0)
        self.add_output('C_toolCostPerVehicle', val=1.0)
        self.add_output('C_materialCostPerKg', val=1.0)
        self.add_output('C_materialCost', val=1.0)
        self.add_output('C_materialCostPerKg', val=1.0)
        self.add_output('C_batteryCostPerKg', val=1.0)
        self.add_output('C_batteryCost', val=1.0)
        self.add_output('C_batteryCostPerKg', val=1.0)
        self.add_output('C_motorCostPerKg', val=1.0)
        self.add_output('C_motorCost', val=1.0)
        self.add_output('C_motorCostPerKg', val=1.0)
        self.add_output('C_servoCost', val=1.0)
        self.add_output('C_avionicsCost', val=1.0)
        self.add_output('C_BRSCost', val=1.0)
        self.add_output('C_BRSCost', val=1.0)
        self.add_output('C_acquisitionCost', val=1.0)
        self.add_output('C_batteryCost', val=1.0)
        self.add_output('C_motorCost', val=1.0)
        self.add_output('C_servoCost', val=1.0)
        self.add_output('C_avionicsCost', val=1.0)
        self.add_output('C_BRSCost', val=1.0)
        self.add_output('C_materialCost', val=1.0)
        self.add_output('C_toolCostPerVehicle', val=1.0)
        self.add_output('C_acquisitionCostPerFlight', val=1.0)
        self.add_output('C_acquisitionCost', val=1.0)
        self.add_output('C_flightsPerYear', val=1.0)
        self.add_output('C_vehicleLifeYears', val=1.0)
        self.add_output('C_insuranceCostPerYear', val=1.0)
        self.add_output('C_acquisitionCost', val=1.0)
        self.add_output('C_insuranceCostPerFlight', val=1.0)
        self.add_output('C_insuranceCostPerYear', val=1.0)
        self.add_output('C_flightsPerYear', val=1.0)
        self.add_output('C_vehicleFootprint', val=1.0)
        self.add_output('C_vehicleFootprint', val=1.0)
        self.add_output('C_areaCost', val=1.0)
        self.add_output('C_facilityCostPerYear', val=1.0)
        self.add_output('C_vehicleFootprint', val=1.0)
        self.add_output('C_vehicleFootprint', val=1.0)
        self.add_output('C_nVehiclesPerFacility', val=1.0)
        self.add_output('C_areaCost', val=1.0)
        self.add_output('C_facilityCostPerFlightHour', val=1.0)
        self.add_output('C_facilityCostPerYear', val=1.0)
        self.add_output('C_flightHoursPerYear', val=1.0)
        self.add_output('C_facilityCostPerFlight', val=1.0)
        self.add_output('C_facilityCostPerFlightHour', val=1.0)
        self.add_output('C_energyCostPerFlight', val=1.0)
        self.add_output('C_battLifeCycles', val=1.0)
        self.add_output('C_batteryReplCostPerFlight', val=1.0)
        self.add_output('C_batteryCost', val=1.0)
        self.add_output('C_battLifeCycles', val=1.0)
        self.add_output('C_motorLifeHrs', val=1.0)
        self.add_output('C_motorReplCostPerFlight', val=1.0)
        self.add_output('C_motorLifeHrs', val=1.0)
        self.add_output('C_motorCost', val=1.0)
        self.add_output('C_servoLifeHrs', val=1.0)
        self.add_output('C_servoReplCostPerFlight', val=1.0)
        self.add_output('C_servoLifeHrs', val=1.0)
        self.add_output('C_servoCost', val=1.0)
        self.add_output('C_humanCostPerHour', val=1.0)
        self.add_output('C_manHrPerFlightHour', val=1.0)
        self.add_output('C_manHrPerFlight', val=1.0)
        self.add_output('C_manHrPerFlightHour', val=1.0)
        self.add_output('C_manHrPerFlight', val=1.0)
        self.add_output('C_laborCostPerFlight', val=1.0)
        self.add_output('C_manHrPerFlightHour', val=1.0)
        self.add_output('C_manHrPerFlight', val=1.0)
        self.add_output('C_humanCostPerHour', val=1.0)
        self.add_output('C_costPerFlight', val=1.0)
        self.add_output('C_acquisitionCostPerFlight', val=1.0)
        self.add_output('C_insuranceCostPerFlight', val=1.0)
        self.add_output('C_facilityCostPerFlight', val=1.0)
        self.add_output('C_energyCostPerFlight', val=1.0)
        self.add_output('C_batteryReplCostPerFlight', val=1.0)
        self.add_output('C_motorReplCostPerFlight', val=1.0)
        self.add_output('C_servoReplCostPerFlight', val=1.0)
        self.add_output('C_laborCostPerFlight', val=1.0)

        def solve_nonlinear(self, params, unknowns, resids):
            
            
        # Assumptions
        C.flightHoursPerYear = 600
        C.flightsPerYear = C.flightHoursPerYear / (params['flightTime']/3600)
        C.params['vehicle']LifeYears = 10
        C.nVehiclesPerFacility = 200 # Size of storage depot
        
        # Tooling cost
        C.toolCostPerVehicle = costBuildup(params['vehicle'],params['rProp'],params['cruiseOutput'])
        
        # Material cost
        C.materialCostPerKg = 220 # Material plus assmebly cost
        C.materialCost = C.materialCostPerKg * mass.structural
        
        # battery cost per kg
        C.batteryCostPerKg = 161 # Roughly $700/kW-hr * 230 W-hr/kg
        C.batteryCost = C.batteryCostPerKg * mass.battery
        
        # motor cost per kg
        C.motorCostPerKg = 150 # Approx $1500 for 10 kg motor? + controller
        C.motorCost = C.motorCostPerKg * mass.motors
        
        # servo cost 
        if strcmpi(params['vehicle'],'tiltwing')
            nServo = 14 # 8 props, 4 surfaces, 2 tilt
        elseif strcmpi(params['vehicle'],'helicopter')
            nServo = 8 # For cyclic (2x) / collective, tail rotor w/ redundancy
        
        C.servoCost = nServo * 800 # params['E']stimate $800 per servo in large quantities
        
        # Avionics cost
        C.avionicsCost = 30000 # guess for all sensors and computers in large quantities
        
        # BRS Cost
        if strcmpi(params['vehicle'],'tiltwing')
            C.BRSCost = 5200
        elseif strcmpi(params['vehicle'],'helicopter')
            C.BRSCost = 0
        
        
        # Total aquisition cost
        C.acquisitionCost = C.batteryCost + C.motorCost + C.servoCost + C.avionicsCost + C.BRSCost + C.materialCost + C.toolCostPerVehicle 
        C.acquisitionCostPerFlight = C.acquisitionCost / (C.flightsPerYear * C.params['vehicle']LifeYears)
        
        # Insurance cost
        # Follow R22 for estimate of 6.5% of acquisition cost
        C.insuranceCostPerYear = C.acquisitionCost * 0.065
        C.insuranceCostPerFlight = C.insuranceCostPerYear / C.flightsPerYear
        
        # Facility rental cost
        if strcmpi(params['vehicle'],'tiltwing')
            C.params['vehicle']Footprint = 1.2 * (8 * params['rProp'] + 1) * (4 * params['rProp'] + 3) # m**2, 20% for movement around aircraft for maintenance, etc.
        elseif strcmpi(params['vehicle'],'helicopter')
            C.params['vehicle']Footprint = 1.2 * (2 * params['rProp'])**2 # m**2, 20% for movement around aircraft for maintenance, etc.
        
        C.areaCost = 10.7639 * 2 * 12 # $/m**2, $2/ft**2 per month assumed
        
        # Facility cost = Vehicle footprint + 10x footprint for operations,
        # averaged over # of params['vehicle']s at each facility
        C.facilityCostPerYear = (C.params['vehicle']Footprint + 10 * C.params['vehicle']Footprint / C.nVehiclesPerFacility) * C.areaCost 
        C.facilityCostPerFlightHour = C.facilityCostPerYear / C.flightHoursPerYear
        C.facilityCostPerFlight = C.facilityCostPerFlightHour * params['flightTime'] / 3600
        
        # params['E']lectricity cost
        # params['E'] * $/kWhr including 90% charging efficiency
        # Average US electricity cost is $0.12 per kW-hr, up to $0.20 per kW-hr in CA
        C.energyCostPerFlight = 0.12 * params['E'] / 0.9
        
        # Battery replacement cost
        C.battLifeCycles = 2000
        C.batteryReplCostPerFlight = C.batteryCost / C.battLifeCycles # 1 cycle per flight
        
        # Motor replacement cost
        C.motorLifeHrs = 6000
        C.motorReplCostPerFlight = params['flightTime'] / 3600 / C.motorLifeHrs * C.motorCost
        
        # Servo replacement cost
        C.servoLifeHrs = 6000
        C.servoReplCostPerFlight = params['flightTime'] / 3600 / C.servoLifeHrs * C.servoCost
        
        # Maintenance cost
        C.humanCostPerHour = 60
        if strcmpi(params['vehicle'],'tiltwing')
            C.manHrPerFlightHour = 0.10 # periodic maintenance estimate
            C.manHrPerFlight = 0.2 # Inspection, battery swap estimate
        elseif strcmpi(params['vehicle'],'helicopter')
            C.manHrPerFlightHour = 0.05 # periodic maintenance estimate
            C.manHrPerFlight = 0.2 # Inspection, battery swap estimate
        else
            error('Vehicle not recognized!')
        
        C.laborCostPerFlight = (C.manHrPerFlightHour * params['flightTime'] / 3600 + C.manHrPerFlight) * C.humanCostPerHour
        
        # Cost per flight
        C.costPerFlight = C.acquisitionCostPerFlight + C.insuranceCostPerFlight + C.facilityCostPerFlight + \
            C.energyCostPerFlight + C.batteryReplCostPerFlight + C.motorReplCostPerFlight + \
            C.servoReplCostPerFlight + C.laborCostPerFlight
        
