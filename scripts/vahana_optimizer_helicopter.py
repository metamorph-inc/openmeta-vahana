'''
# Name: vahana_optimizer_helicopter.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/15/2017
# Edit Date: 7/20/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Implementation of optimizer nested within a parameter study using 
# the OpenMDAO framework and Python conversions of the vahanaTradeStudy

# Inputs:
#   Input               - input description [units]

# Outputs:
#   Outputs             - output description [units]
'''

from __future__ import print_function  # allows for backwards compatibility with Python 2.X - OpenMDAO (and OpenMeta) uses Python 2.7
import sys
import math
import csv  # for data export

# OpenMDAO imports
from openmdao.api import Problem, Group, Component, IndepVarComp, ExecComp, \
                         ScipyOptimizer, SubProblem, FullFactorialDriver, \
                         SqliteRecorder  
 
# Recorder import
import sqlitedict  
from pprint import pprint

# Component imports
from mass_2_weight import mass_2_weight
from cruise_power import CruisePower
from hover_power import HoverPower
from loiter_power import loiter_power
from mission import mission
from wire_mass_helicopter import wire_mass
from prop_mass import prop_mass
from fuselage_mass import fuselage_mass
from config_weight import config_weight
from tooling_cost import tooling_cost
from operating_cost import operating_cost

# Group imports

# Component definitions

# Group definitions

class TopLevelSystem(Group):
    def __init__(self):
        super(TopLevelSystem, self).__init__()
        
        print('running...')
        
        # add design variables
        self.add('indep1', IndepVarComp('range', 50.0))
        self.add('indep2', IndepVarComp('rProp', 30.0))
        self.add('indep3', IndepVarComp('cruiseSpeed', 50.0))
        self.add('indep4', IndepVarComp('batteryMass', 11.70))
        self.add('indep5', IndepVarComp('motorMass', 3.00))
        self.add('indep6', IndepVarComp('mtom', 6.500))
        self.add('indep7', IndepVarComp('vehicle', u'helicopter'))  # TypeError: In subproblem 'subprob': Type <type 'str'> of source 'indep7.vehicle' must be the same as type <type 'unicode'> of target 'ConfigWeight.Vehicle'.
        
        # design variable scaling - this is CRITICAL or else the COBYLA optimizer WILL NOT WORK
        self.add('scale2', ExecComp('scaled = orig*0.1'))
        self.add('scale3', ExecComp('scaled = orig*1.0'))
        self.add('scale4', ExecComp('scaled = orig*10.0'))
        self.add('scale5', ExecComp('scaled = orig*10.0'))
        self.add('scale6', ExecComp('scaled = orig*100.0'))
        
        self.connect('indep2.rProp', 'scale2.orig')
        self.connect('indep3.cruiseSpeed', 'scale3.orig')
        self.connect('indep4.batteryMass', 'scale4.orig')
        self.connect('indep5.motorMass', 'scale5.orig')
        self.connect('indep6.mtom', 'scale6.orig')
        
        # add components
        self.add('MassToWeight', mass_2_weight())
        self.add('CruisePower', CruisePower())
        self.add('HoverPower', HoverPower())
        self.add('LoiterPower', loiter_power())
        self.add('SimpleMission', mission())
        self.add('ReserveMission', mission())
        self.add('WireMass', wire_mass())
        self.add('PropMass', prop_mass())
        self.add('PropMass_Tail', prop_mass())
        self.add('FuselageMass', fuselage_mass())
        self.add('ConfigWeight', config_weight())
        self.add('ToolingCost', tooling_cost())
        self.add('OperatingCost', operating_cost())
        
        # add component constants - Q. is there a better way to do this?
        self.add('simpleMissionConst1', IndepVarComp('hops', 1.0))
        self.add('simpleMissionConst2', IndepVarComp('loiterTime', 0.0))
        self.add('reserveMissionConst1', IndepVarComp('hops', 2.0))
        self.add('reserveMissionConst2', IndepVarComp('loiterTime', 1020.0))
        self.add('wingMassConst1', IndepVarComp('winglet', 0.2))
        self.add('wingMassConst2', IndepVarComp('fc', 0.4))
        self.add('canardMassConst1', IndepVarComp('winglet', 0.0))
        self.add('canardMassConst2', IndepVarComp('fc', 0.6))
        #self.add('wireMassConst1', IndepVarComp('fuselageLength', 5.0))
        self.add('wireMassConst2', IndepVarComp('fuselageHeight', 2.0))
        self.add('wireMassConst3', IndepVarComp('span', 0.0))
        self.add('wireMassConst4', IndepVarComp('xmotor', 0.0))
        #self.add('fuselageMassConst1', IndepVarComp('length', 5.0))  # Not needed for Helicopter configuration
        self.add('fuselageMassConst2', IndepVarComp('width', 1.0))
        self.add('fuselageMassConst3', IndepVarComp('height', 2.0))
        self.add('fuselageMassConst4', IndepVarComp('span', 1.0))
        self.add('configWeightConst1', IndepVarComp('payload_mass', 113.398))
        self.add('costBuildupConst1', IndepVarComp('partsPerTool', 1000.0))
        
        # add constraint equations
        self.add('con1', ExecComp('c1 = (mBattery*230.0*0.95/1000.0) - EReserve'))
        self.add('con2', ExecComp('c2 = mMotors*5.0 - hoverPower_PMax / 1000.0'))
        self.add('con3', ExecComp('c3 = mtow*9.8 - mass_W'))
        self.add('con4', ExecComp('c4 = (0.5*1.0/3.0*mass_rotor*(hoverPower_Vtip**2.0)) - (0.5*mass_m*(hoverPower_VAutoRotation**2.0))'))
        
        # connect components - as Jonathan pointed out, the alternative is to use a consistent naming convetion and promote variables. This is a pain without a wrapper *cough* OpenMETA *cough*.
        self.connect('scale6.scaled', 'MassToWeight.mass')  # MassToWeight inputs
        
        self.connect('scale2.scaled', 'CruisePower.rProp')  # CruisePower inputs
        self.connect('scale3.scaled', 'CruisePower.V')
        self.connect('indep7.vehicle', 'CruisePower.Vehicle')
        self.connect('MassToWeight.weight', 'CruisePower.W')
        
        self.connect('CruisePower.omega', 'HoverPower.cruisePower_omega')  # HoverPower inputs
        self.connect('scale2.scaled', 'HoverPower.rProp')
        self.connect('indep7.vehicle', 'HoverPower.Vehicle')
        self.connect('MassToWeight.weight', 'HoverPower.W')
        
        self.connect('CruisePower.B', 'LoiterPower.B')  # LoiterPower inputs
        self.connect('CruisePower.AR', 'LoiterPower.cruiseOutputAR')
        self.connect('CruisePower.Cd0', 'LoiterPower.cruiseOutputCd0')
        self.connect('CruisePower.e', 'LoiterPower.cruiseOutputE')
        self.connect('CruisePower.etaMotor', 'LoiterPower.cruiseOutputEtaMotor')
        self.connect('CruisePower.etaProp', 'LoiterPower.cruiseOutputEtaProp')
        self.connect('CruisePower.omega', 'LoiterPower.cruiseOutputOmega')
        self.connect('CruisePower.PCruise', 'LoiterPower.cruiseOutputP')
        self.connect('CruisePower.PBattery', 'LoiterPower.cruiseOutputPBattery')
        self.connect('CruisePower.SCdFuse', 'LoiterPower.cruiseOutputSCdFuse')
        self.connect('CruisePower.sigma', 'LoiterPower.cruiseOutputSigma')
        self.connect('CruisePower.SRef', 'LoiterPower.cruiseOutputSRef')
        self.connect('scale2.scaled', 'LoiterPower.rProp')
        self.connect('scale3.scaled', 'LoiterPower.V')
        self.connect('indep7.vehicle', 'LoiterPower.Vehicle')
        self.connect('MassToWeight.weight', 'LoiterPower.W')
          
        self.connect('CruisePower.PBattery', 'SimpleMission.cruiseOutput_PBattery')  # SimpleMission inputs
        self.connect('simpleMissionConst1.hops', 'SimpleMission.hops')
        self.connect('HoverPower.hoverPower_PBattery', 'SimpleMission.hoverOutput_PBattery')
        self.connect('simpleMissionConst2.loiterTime', 'SimpleMission.loiterTime')
        self.connect('indep1.range', 'SimpleMission.range')
        self.connect('scale2.scaled', 'SimpleMission.rProp')
        self.connect('scale3.scaled', 'SimpleMission.V')
        self.connect('indep7.vehicle', 'SimpleMission.Vehicle')
        
        self.connect('CruisePower.PBattery', 'ReserveMission.cruiseOutput_PBattery')  # ReserveMission inputs
        self.connect('reserveMissionConst1.hops', 'ReserveMission.hops')
        self.connect('HoverPower.hoverPower_PBattery', 'ReserveMission.hoverOutput_PBattery')
        self.connect('LoiterPower.PBattery', 'ReserveMission.loiterOutput_PBattery')
        self.connect('reserveMissionConst2.loiterTime', 'ReserveMission.loiterTime')
        self.connect('indep1.range', 'ReserveMission.range')
        self.connect('scale2.scaled', 'ReserveMission.rProp')
        self.connect('scale3.scaled', 'ReserveMission.V')
        self.connect('indep7.vehicle', 'ReserveMission.Vehicle')
        
        self.add('WireMassInput1', ExecComp('length = 1.5+1.25*rProp'))
        self.connect('scale2.scaled', 'WireMassInput1.rProp')
        
        self.connect('wireMassConst2.fuselageHeight', 'WireMass.fuselageHeight')  # WireMass inputs
        self.connect('WireMassInput1.length', 'WireMass.fuselageLength')
        self.connect('HoverPower.hoverPower_PMaxBattery', 'WireMass.power')
        self.connect('wireMassConst4.xmotor', 'WireMass.xmotor')
        self.connect('wireMassConst3.span', 'WireMass.span')
        
        self.connect('scale2.scaled', 'PropMass.rProp')  # PropMass inputs
        self.connect('HoverPower.TMax', 'PropMass.thrust')
        
        self.add('PropMassInput1', ExecComp('R = rProp/5.0'))
        self.add('PropMassInput2', ExecComp('T = 1.5*hoverOutput_QMax/(1.25*rProp)'))
        self.connect('scale2.scaled', 'PropMassInput1.rProp')
        self.connect('HoverPower.QMax', 'PropMassInput2.hoverOutput_QMax')
        self.connect('scale2.scaled', 'PropMassInput2.rProp')

        self.connect('PropMassInput1.R', 'PropMass_Tail.rProp')  # PropMass_Tail inputs
        self.connect('PropMassInput2.T', 'PropMass_Tail.thrust')
        
        self.add('FuselageMassInput1', ExecComp('length = 1.5+1.25*rProp'))
        self.connect('scale2.scaled', 'FuselageMassInput1.rProp')
        
        self.connect('FuselageMassInput1.length', 'FuselageMass.length')  # FuselageMass inputs
        self.connect('fuselageMassConst2.width', 'FuselageMass.width')
        self.connect('fuselageMassConst3.height', 'FuselageMass.height')
        self.connect('fuselageMassConst4.span', 'FuselageMass.span')
        self.connect('MassToWeight.weight', 'FuselageMass.weight')
        
        self.connect('FuselageMass.mass', 'ConfigWeight.fuselage_mass') # ConfigWeight inputs
        self.connect('HoverPower.hoverPower_PMax', 'ConfigWeight.hoverOutput_PMax')
        self.connect('scale4.scaled', 'ConfigWeight.mBattery')
        self.connect('scale5.scaled', 'ConfigWeight.mMotors')
        self.connect('scale6.scaled', 'ConfigWeight.mtow')
        self.connect('configWeightConst1.payload_mass', 'ConfigWeight.payload')
        self.connect('PropMass.mass', 'ConfigWeight.prop_mass')
        self.connect('PropMass_Tail.mass', 'ConfigWeight.prop_mass_tail')
        self.connect('scale2.scaled', 'ConfigWeight.rProp')
        self.connect('indep7.vehicle', 'ConfigWeight.Vehicle')
        self.connect('WireMass.mass', 'ConfigWeight.wire_mass')
        
        self.connect('CruisePower.bRef', 'ToolingCost.cruiseOutput_bRef')  # ToolingCost inputs
        self.connect('CruisePower.cRef', 'ToolingCost.cruiseOutput_cRef')
        self.connect('costBuildupConst1.partsPerTool', 'ToolingCost.partsPerTool')
        self.connect('scale2.scaled', 'ToolingCost.rProp')
        self.connect('indep7.vehicle', 'ToolingCost.Vehicle')
        
        self.connect('SimpleMission.E', 'OperatingCost.E')  # OperatingCost inputs
        self.connect('SimpleMission.t', 'OperatingCost.flightTime')
        self.connect('scale4.scaled', 'OperatingCost.mass_battery')
        self.connect('scale5.scaled', 'OperatingCost.mass_motors')
        self.connect('ConfigWeight.mass_structural', 'OperatingCost.mass_structural')
        self.connect('scale2.scaled', 'OperatingCost.rProp')
        self.connect('ToolingCost.toolCostPerVehicle', 'OperatingCost.toolingCost')
        self.connect('indep7.vehicle', 'OperatingCost.Vehicle')
  
        self.connect('ReserveMission.E', 'con1.EReserve')  # Constraint inputs
        self.connect('scale4.scaled', 'con1.mBattery')
        self.connect('HoverPower.hoverPower_PMax', 'con2.hoverPower_PMax')
        self.connect('scale5.scaled', 'con2.mMotors')
        self.connect('ConfigWeight.mass_W', 'con3.mass_W')
        self.connect('scale6.scaled', 'con3.mtow')
        self.connect('ConfigWeight.mass_rotor', 'con4.mass_rotor')
        self.connect('HoverPower.hoverPower_Vtip', 'con4.hoverPower_Vtip')
        self.connect('HoverPower.hoverPower_VAutoRotation', 'con4.hoverPower_VAutoRotation')
        
        
if __name__ == '__main__':
    # SubProblem: define a Problem to optimize the system
    sub = Problem(root=TopLevelSystem())
    
    # SubProblem: set up the optimizer
    sub.driver = ScipyOptimizer()
    sub.driver.options['optimizer'] = 'COBYLA'  # The 'COBYLA' optimizer is supported by OpenMETA. 
                                                # Unlike the 'SLSQP' optimizer, the 'COBYLA' optimizer doesn't require a Jacobian matrix.
    sub.driver.options['disp'] = True  # enable optimizer output
    sub.driver.options['maxiter'] = 1000
    sub.driver.options['tol'] = 0.001
    #sub.driver.opt_settings['rhobeg'] = 100.0
    
    # SubProblem: set design variables for sub.driver
    sub.driver.add_desvar('indep2.rProp', lower=10.0, upper=100.0)
    sub.driver.add_desvar('indep3.cruiseSpeed', lower=30.0, upper=80.0)
    sub.driver.add_desvar('indep4.batteryMass', lower=1.0, upper=99.90)
    sub.driver.add_desvar('indep5.motorMass', lower=0.10, upper=99.90)
    sub.driver.add_desvar('indep6.mtom', lower=1.0, upper=99.990)
    
    # SubProblem: set design objectives
    sub.driver.add_objective('OperatingCost.C_costPerFlight')
    
    # SubProblem: set design variable constraints - Jonathan says that some of the optimizers
    # (in particular COBYLA) seem to totally ignore the design variable lower and upper bounds
    # Jonathan's work-around is to set additional constraints
    # Interesting article: http://openmdao.org/forum/questions/342/slsqpdriver-not-respecting-paramaters-low-and-high-contraints
    sub.driver.add_constraint('indep2.rProp', lower=10.0, upper=100.0)
    sub.driver.add_constraint('indep3.cruiseSpeed', lower=30.0, upper=80.0)
    sub.driver.add_constraint('indep4.batteryMass', lower=1.0, upper=99.90)
    sub.driver.add_constraint('indep5.motorMass', lower=0.10, upper=99.90)
    sub.driver.add_constraint('indep6.mtom', lower=1.0, upper=99.990)
    
    # SubProblem: set design constraints
    sub.driver.add_constraint('con1.c1', lower=0.0)
    sub.driver.add_constraint('con2.c2', lower=0.0)
    sub.driver.add_constraint('con3.c3', lower=0.0)
    sub.driver.add_constraint('con4.c4', lower=0.0)
    
    # TopProblem: define a Problem to set up different optimization cases
    top = Problem(root=Group())
    
    # TopProblem: add independent variables
    top.root.add('indep1', IndepVarComp('range', 50.0))
    top.root.add('indep2', IndepVarComp('rProp', 30.0))
    top.root.add('indep3', IndepVarComp('cruiseSpeed', 50.0))
    top.root.add('indep4', IndepVarComp('batteryMass', 11.70))
    top.root.add('indep5', IndepVarComp('motorMass', 3.00))
    top.root.add('indep6', IndepVarComp('mtom', 6.500))
    # top.root.add('indep7', IndepVarComp('vehicle', 'tiltwing'))  # 1st get this working with just the tiltwing
    
    # TopProblem: add the SubProblem
    top.root.add('subprob', SubProblem(sub, params=['indep1.range', 'indep2.rProp', \
                                                    'indep3.cruiseSpeed', 'indep4.batteryMass', \
                                                    'indep5.motorMass', 'indep6.mtom'],
                                            unknowns=['OperatingCost.C_costPerFlight']))
    
    # TopProblem: connect top's independent variables to sub's params
    top.root.connect('indep1.range', 'subprob.indep1.range')
    top.root.connect('indep2.rProp', 'subprob.indep2.rProp')  # Each of SubProblem's IndepVarComp components has to be connected (maybe promoted works too) to a 
    top.root.connect('indep3.cruiseSpeed', 'subprob.indep3.cruiseSpeed')  # IndepVarComp component in the top level. 
    top.root.connect('indep4.batteryMass', 'subprob.indep4.batteryMass')  # Alternatively it might make more sense to output the design variables states as metrics.
    top.root.connect('indep5.motorMass', 'subprob.indep5.motorMass')
    top.root.connect('indep6.mtom', 'subprob.indep6.mtom')
    
    # TopProblem: set up the parameter study
    # for a parameter study, the following drivers can be used:
    # UniformDriver, FullFactorialDriver, LatinHypercubeDriver, OptimizedLatinHypercubeDriver
    # in this case, we will use FullFactorialDriver
    top.driver = FullFactorialDriver(num_levels=11)
    
    # TopProblem: add top.driver's design variables
    top.driver.add_desvar('indep1.range', lower=10000.0, upper=110000.0)
    
    # Data collection
    recorder = SqliteRecorder('subprob')
    recorder.options['record_params'] = True
    recorder.options['record_metadata'] = True
    top.driver.add_recorder(recorder)
    
    # Setup
    top.setup(check=False)
    
    # Run 
    top.run()
    
    # Cleanup
    top.cleanup()
    
    # Data retrieval & display
    # Old way - good for debugging IndepVars
    #db = sqlitedict.SqliteDict( 'subprob', 'iterations' )
    #db_keys = list( db.keys() ) # list() needed for compatibility with Python 3. Not needed for Python 2
    #for i in db_keys:
    #    data = db[i]
    #    print('\n')
    #    print(data['Unknowns'])
    #    print(data['Parameters'])
    
    db = sqlitedict.SqliteDict( 'subprob', 'iterations' )
    db_keys = list( db.keys() ) # list() needed for compatibility with Python 3. Not needed for Python 2
    for i in db_keys:
        data = db[i]
        print('\n')
        print('Range (m): {}, DOC ($): {}, rProp (m): {}, cruiseSpeed (m/s): {}, batteryMass (kg): {}, motorMass (kg): {}, mtom (kg): {}' \
            .format(data['Parameters']['subprob.indep1.range'] / 1000.0, data['Unknowns']['subprob.OperatingCost.C_costPerFlight'], \
            data['Parameters']['subprob.indep2.rProp'] * 0.1, data['Parameters']['subprob.indep3.cruiseSpeed'], \
            data['Parameters']['subprob.indep4.batteryMass'] * 10.0, data['Parameters']['subprob.indep5.motorMass'] * 10.0, \
            data['Parameters']['subprob.indep6.mtom'] * 100.0))

    # Data export via .csv      
    with open('results.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Range [km]', 'DOC [$]', 'DOC [$/km]', 'RotorRadius [m]', 'CruiseSpeed [m/s]', 'BatteryMass [kg]', 'MotorMass [kg]', 'MaxTakeOffMass [kg]'])
        for i in db_keys:
            data = db[i]
            writer.writerow([data['Parameters']['subprob.indep1.range'] / 1000.0, data['Unknowns']['subprob.OperatingCost.C_costPerFlight'], \
            data['Unknowns']['subprob.OperatingCost.C_costPerFlight'] / data['Parameters']['subprob.indep1.range'] * 1000.0, \
            data['Parameters']['subprob.indep2.rProp'] * 0.1, data['Parameters']['subprob.indep3.cruiseSpeed'], \
            data['Parameters']['subprob.indep4.batteryMass'] * 10.0, data['Parameters']['subprob.indep5.motorMass'] * 10.0, \
            data['Parameters']['subprob.indep6.mtom'] * 100.0])
    