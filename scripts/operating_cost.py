'''
# Name: operating_cost.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/8/2017
# Edit Date: 6/8/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Estimate direct operating costs per flight including: acquisition cost,
# insurance cost, operating facility cost, energy cost, and maintenance. 

# Inputs:
#   vehicle          - Vehicle type ('tiltwing' or 'helicopter')
#   rProp            - Propeller or rotor radius [m]
#   flightTime       - Flight time for nominal flight [sec]
#   E                - Energy use for flight [kW-hr]
#   mass_structural  - structural mass [kg]
#   mass_battery     - battery mass [kg]
#   mass_motors      - motor mass[kg]

# Outputs:
#   C               - #TODO
'''

from __future__ import print_function

from openmdao.api import Component
import math

class operating_cost(Component):

    def __init__(self):
        super(operating_cost, self).__init__()
        self.add_param('vehicle', val=0.0)
        self.add_param('rProp', val=0.0)
        self.add_param('flightTime', val=0.0)
        self.add_param('E', val=0.0)
        self.add_param('mass_structural', val=0.0)
        self.add_param('mass_battery', val=0.0)
        self.add_param('mass_motors', val=0.0)
        self.add_param('costBuildup_toolCostPerVehicle', val=0.0)
        
        self.add_output('C_flightHoursPerYear', val=0.0)
        self.add_output('C_flightsPerYear', val=0.0)
        self.add_output('C_vehicleLifeYears', val=0.0)
        self.add_output('C_nVehiclesPerFacility', val=0.0)
        self.add_output('C_toolCostPerVehicle', val=0.0)
        self.add_output('C_materialCostPerKg', val=0.0)
        self.add_output('C_materialCost', val=0.0)
        self.add_output('C_batteryCostPerKg', val=0.0)
        self.add_output('C_batteryCost', val=0.0)
        self.add_output('C_motorCostPerKg', val=0.0)
        self.add_output('C_motorCost', val=0.0)
        self.add_output('C_servoCost', val=0.0)
        self.add_output('C_avionicsCost', val=0.0)
        self.add_output('C_BRSCost', val=0.0)
        self.add_output('C_acquisitionCost', val=0.0)
        self.add_output('C_acquisitionCostPerFlight', val=0.0)
        self.add_output('C_insuranceCostPerYear', val=0.0)
        self.add_output('C_insuranceCostPerFlight', val=0.0)
        self.add_output('C_vehicleFootprint', val=0.0)
        self.add_output('C_areaCost', val=0.0)
        self.add_output('C_facilityCostPerYear', val=0.0)
        self.add_output('C_facilityCostPerFlightHour', val=0.0)
        self.add_output('C_facilityCostPerFlight', val=0.0)
        self.add_output('C_energyCostPerFlight', val=0.0)
        self.add_output('C_battLifeCycles', val=0.0)
        self.add_output('C_batteryReplCostPerFlight', val=0.0)
        self.add_output('C_motorLifeHrs', val=0.0)
        self.add_output('C_motorReplCostPerFlight', val=0.0)
        self.add_output('C_servoLifeHrs', val=0.0)
        self.add_output('C_servoReplCostPerFlight', val=0.0)
        self.add_output('C_humanCostPerHour', val=0.0)
        self.add_output('C_manHrPerFlightHour', val=0.0)
        self.add_output('C_manHrPerFlight', val=0.0)
        self.add_output('C_laborCostPerFlight', val=0.0)
        self.add_output('C_costPerFlight', val=0.0)

    def solve_nonlinear(self, params, unknowns, resids):
        # Assumptions
        unknowns['C_flightHoursPerYear'] = 600
        unknowns['C_flightsPerYear'] = unknowns['C_flightHoursPerYear'] / (params['flightTime']/3600)
        unknowns['C_vehicleLifeYears'] = 10
        unknowns['C_nVehiclesPerFacility'] = 200 # Size of storage depot
        
        # Tooling cost
        unknowns['C_toolCostPerVehicle'] = params['costBuildup_toolCostPerVehicle']
        
        # Material cost
        unknowns['C_materialCostPerKg'] = 220 # Material plus assmebly cost
        unknowns['C_materialCost'] = unknowns['C_materialCostPerKg'] * params['mass_structural']
        
        # battery cost per kg
        unknowns['C_batteryCostPerKg'] = 161 # Roughly $700/kW-hr * 230 W-hr/kg
        unknowns['C_batteryCost'] = unknowns['C_batteryCostPerKg'] * params['mass_battery']
        
        # motor cost per kg
        unknowns['C_motorCostPerKg'] = 150 # Approx $1500 for 10 kg motor? + controller
        unknowns['C_motorCost'] = unknowns['C_motorCostPerKg'] * params['mass_motors']
        
        # servo cost 
        if (params['vehicle'] == 0):
            nServo = 14 # 8 props, 4 surfaces, 2 tilt
        elif (params['vehicle'] == 1):
            nServo = 8 # For cyclic (2x) / collective, tail rotor w/ redundancy
        
        unknowns['C_servoCost'] = nServo * 800 # Estimate $800 per servo in large quantities
        
        # Avionics cost
        unknowns['C_avionicsCost'] = 30000 # guess for all sensors and computers in large quantities
        
        # BRS Cost
        if (params['vehicle'] == 0):
            unknowns['C_BRSCost'] = 5200
        elif (params['vehicle'] == 1):
            unknowns['C_BRSCost'] = 0
        
        # Total aquisition cost
        unknowns['C_acquisitionCost'] = unknowns['C_batteryCost'] + unknowns['C_motorCost'] + unknowns['C_servoCost'] + \
            unknowns['C_avionicsCost'] + unknowns['C_BRSCost'] + unknowns['C_materialCost'] + unknowns['C_toolCostPerVehicle']
        unknowns['C_acquisitionCostPerFlight'] = unknowns['C_acquisitionCost'] / (unknowns['C_flightsPerYear'] * unknowns['C_vehicleLifeYears'])
        
        # Insurance cost
        # Follow R22 for estimate of 6.5% of acquisition cost
        unknowns['C_insuranceCostPerYear'] = unknowns['C_acquisitionCost'] * 0.065
        unknowns['C_insuranceCostPerFlight'] = unknowns['C_insuranceCostPerYear'] / unknowns['C_flightsPerYear']
        
        # Facility rental cost
        if (params['vehicle'] == 0):
            unknowns['C_vehicleFootprint'] = 1.2 * (8 * params['rProp'] + 1) * (4 * params['rProp'] + 3) # m^2, 20% for movement around aircraft for maintenance, etc.
        elif (params['vehicle'] == 1):
            unknowns['C_vehicleFootprint'] = 1.2 * (2 * params['rProp'])**2 # m^2, 20% for movement around aircraft for maintenance, etc.
        
        unknowns['C_areaCost'] = 10.7639 * 2 * 12 # $/m^2, $2/ft^2 per month assumed
        
        # Facility cost = Vehicle footprint + 10x footprint for operations,
        # averaged over # of vehicles at each facility
        unknowns['C_facilityCostPerYear'] = (unknowns['C_vehicleFootprint'] + 10 * unknowns['C_vehicleFootprint'] / unknowns['C_nVehiclesPerFacility']) * unknowns['C_areaCost']
        unknowns['C_facilityCostPerFlightHour'] = unknowns['C_facilityCostPerYear'] / unknowns['C_flightHoursPerYear']
        unknowns['C_facilityCostPerFlight'] = unknowns['C_facilityCostPerFlightHour'] * params['flightTime'] / 3600
        
        # Electricity cost
        # E * $/kWhr including 90% charging efficiency
        # Average US electricity cost is $0.12 per kW-hr, up to $0.20 per kW-hr in CA
        unknowns['C_energyCostPerFlight'] = 0.12 * params['E'] / 0.9
        
        # Battery replacement cost
        unknowns['C_battLifeCycles'] = 2000
        unknowns['C_batteryReplCostPerFlight'] = unknowns['C_batteryCost'] / unknowns['C_battLifeCycles'] # 1 cycle per flight
        
        # Motor replacement cost
        unknowns['C_motorLifeHrs'] = 6000
        unknowns['C_motorReplCostPerFlight'] = params['flightTime'] / 3600 / unknowns['C_motorLifeHrs'] * unknowns['C_motorCost']
        
        # Servo replacement cost
        unknowns['C_servoLifeHrs'] = 6000
        unknowns['C_servoReplCostPerFlight'] = params['flightTime'] / 3600 / unknowns['C_servoLifeHrs'] * unknowns['C_servoCost']
        
        # Maintenance cost
        unknowns['C_humanCostPerHour'] = 60
        if (params['vehicle'] == 0):
            unknowns['C_manHrPerFlightHour'] = 0.10 # periodic maintenance estimate
            unknowns['C_manHrPerFlight'] = 0.2 # Inspection, battery swap estimate
        elif (params['vehicle'] == 1):
            unknowns['C_manHrPerFlightHour'] = 0.05 # periodic maintenance estimate
            unknowns['C_manHrPerFlight'] = 0.2 # Inspection, battery swap estimate
        else:
            pass
            error('Vehicle not recognized!')
        
        unknowns['C_laborCostPerFlight'] = (unknowns['C_manHrPerFlightHour'] * params['flightTime'] / 3600 + unknowns['C_manHrPerFlight']) * unknowns['C_humanCostPerHour']
        
        # Cost per flight
        unknowns['C_costPerFlight'] = unknowns['C_acquisitionCostPerFlight'] + unknowns['C_insuranceCostPerFlight'] + unknowns['C_facilityCostPerFlight'] + \
            unknowns['C_energyCostPerFlight'] + unknowns['C_batteryReplCostPerFlight'] + unknowns['C_motorReplCostPerFlight'] + \
            unknowns['C_servoReplCostPerFlight'] + unknowns['C_laborCostPerFlight']
        