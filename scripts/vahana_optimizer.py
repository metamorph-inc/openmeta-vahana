'''
# Name: vahana_optimizer.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/15/2017
# Edit Date: 6/16/2017

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
from wing_mass import wing_mass
from wire_mass import wire_mass
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
        
        # add design variables - Q. is this even needed?
        self.add('indep1', IndepVarComp('range', 50.0))
        self.add('indep2', IndepVarComp('rProp', 1.0))
        self.add('indep3', IndepVarComp('cruiseSpeed', 50.0))
        self.add('indep4', IndepVarComp('batteryMass', 117.0))
        self.add('indep5', IndepVarComp('motorMass', 30.0))
        self.add('indep6', IndepVarComp('mtom', 650.0))
        self.add('indep7', IndepVarComp('vehicle', u'tiltwing'))  # TypeError: In subproblem 'subprob': Type <type 'str'> of source 'indep7.vehicle' must be the same as type <type 'unicode'> of target 'ConfigWeight.Vehicle'.
        
        # add components
        self.add('MassToWeight', mass_2_weight())
        self.add('CruisePower', CruisePower())
        self.add('HoverPower', HoverPower())
        self.add('LoiterPower', loiter_power())
        self.add('SimpleMission', mission())
        self.add('ReserveMission', mission())
        self.add('WingMass', wing_mass())  # TEMPORARY
        self.add('CanardMass', wing_mass())  # TEMPORARY
        self.add('WireMass', wire_mass())
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
        self.add('wireMassConst1', IndepVarComp('fuselageLength', 5.0))
        self.add('wireMassConst2', IndepVarComp('fuselageHeight', 1.65))
        self.add('configWeightConst1', IndepVarComp('payload_mass', 114.0))
        self.add('configWeightConst2', IndepVarComp('fuselage_mass', 55.0))
        self.add('configWeightConst3', IndepVarComp('prop_mass', 14.0))
        #self.add('configWeightConst4', IndepVarComp('wing_mass', 40.0))  # TEMPORARY: This constant is a workaround until I add wing_mass.py back
        #self.add('configWeightConst5', IndepVarComp('canard_mass', 38.0))  # TEMPORARY: This constant is a workaround until I add wing_mass.py back
        self.add('costBuildupConst1', IndepVarComp('partsPerTool', 1000.0))
        
        # add constraint equations
        self.add('con1', ExecComp('c = EReserve - (mBattery*230.0*0.95/1000.0)'))
        self.add('con2', ExecComp('c = hoverPower_PMax / 1000.0 - mMotors*5.0'))
        self.add('con3', ExecComp('c = mass_W - mtow*9.8'))
        #self.add('con4', ExecComp('c = 0.5*mass_m*hoverPower_VAutoRotation**2.0 - 0.5*1.0/3.0*mass_rotor*hoverPower_Vtip**2.0'))  # Helicopter only - doesn't work for this version
        
        # connect components
        self.connect('indep6.mtom', 'MassToWeight.mass')  # MassToWeight inputs
        
        self.connect('indep2.rProp', 'CruisePower.rProp')  # CruisePower inputs
        self.connect('indep3.cruiseSpeed', 'CruisePower.V')
        self.connect('indep7.vehicle', 'CruisePower.Vehicle')
        self.connect('MassToWeight.weight', 'CruisePower.W')
        
        self.connect('CruisePower.omega', 'HoverPower.cruisePower_omega')  # HoverPower inputs
        self.connect('indep2.rProp', 'HoverPower.rProp')
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
        self.connect('indep2.rProp', 'LoiterPower.rProp')
        self.connect('indep3.cruiseSpeed', 'LoiterPower.V')
        self.connect('indep7.vehicle', 'LoiterPower.Vehicle')
        self.connect('MassToWeight.weight', 'LoiterPower.W')
          
        self.connect('CruisePower.PBattery', 'SimpleMission.cruiseOutput_PBattery')  # SimpleMission inputs
        self.connect('simpleMissionConst1.hops', 'SimpleMission.hops')
        self.connect('HoverPower.hoverPower_PBattery', 'SimpleMission.hoverOutput_PBattery')
        self.connect('simpleMissionConst2.loiterTime', 'SimpleMission.loiterTime')
        self.connect('indep1.range', 'SimpleMission.range')
        self.connect('indep2.rProp', 'SimpleMission.rProp')
        self.connect('indep3.cruiseSpeed', 'SimpleMission.V')
        self.connect('indep7.vehicle', 'SimpleMission.Vehicle')
        
        self.connect('CruisePower.PBattery', 'ReserveMission.cruiseOutput_PBattery')  # ReserveMission inputs
        self.connect('reserveMissionConst1.hops', 'ReserveMission.hops')
        self.connect('HoverPower.hoverPower_PBattery', 'ReserveMission.hoverOutput_PBattery')
        self.connect('LoiterPower.PBattery', 'ReserveMission.loiterOutput_PBattery')
        self.connect('reserveMissionConst2.loiterTime', 'ReserveMission.loiterTime')
        self.connect('indep1.range', 'ReserveMission.range')
        self.connect('indep2.rProp', 'ReserveMission.rProp')
        self.connect('indep3.cruiseSpeed', 'ReserveMission.V')
        self.connect('indep7.vehicle', 'ReserveMission.Vehicle')
        
        self.connect('CruisePower.cRef', 'WingMass.chord')  # WingMass inputs # TEMPORARY 
        self.connect('wingMassConst2.fc', 'WingMass.fc')
        self.connect('indep2.rProp', 'WingMass.rProp')
        self.connect('CruisePower.bRef', 'WingMass.span')
        self.connect('HoverPower.TMax', 'WingMass.thrust')
        self.connect('MassToWeight.weight', 'WingMass.W')
        self.connect('wingMassConst1.winglet', 'WingMass.winglet')

        self.connect('CruisePower.cRef', 'CanardMass.chord')  # CanardMass inputs # TEMPORARY 
        self.connect('canardMassConst2.fc', 'CanardMass.fc')
        self.connect('indep2.rProp', 'CanardMass.rProp')
        self.connect('CruisePower.bRef', 'CanardMass.span') 
        self.connect('HoverPower.TMax', 'CanardMass.thrust')
        self.connect('MassToWeight.weight', 'CanardMass.W')
        self.connect('canardMassConst1.winglet', 'CanardMass.winglet')
        
        self.connect('wireMassConst2.fuselageHeight', 'WireMass.fuselageHeight')  # WireMass inputs
        self.connect('wireMassConst1.fuselageLength', 'WireMass.fuselageLength')
        self.connect('HoverPower.hoverPower_PMax', 'WireMass.power')
        self.connect('indep2.rProp', 'WireMass.rProp')
        self.connect('CruisePower.bRef', 'WireMass.span')
        
        self.connect('CanardMass.mass', 'ConfigWeight.canard_mass')  # ConfigWeight inputs # TEMPORARY 
        self.connect('configWeightConst2.fuselage_mass', 'ConfigWeight.fuselage_mass')
        self.connect('HoverPower.hoverPower_PMax', 'ConfigWeight.hoverOutput_PMax')
        self.connect('indep4.batteryMass', 'ConfigWeight.mBattery')
        self.connect('indep5.motorMass', 'ConfigWeight.mMotors')
        self.connect('indep6.mtom', 'ConfigWeight.mtow')
        self.connect('configWeightConst1.payload_mass', 'ConfigWeight.payload')
        self.connect('configWeightConst3.prop_mass', 'ConfigWeight.prop_mass')
        self.connect('indep2.rProp', 'ConfigWeight.rProp')
        self.connect('indep7.vehicle', 'ConfigWeight.Vehicle')
        self.connect('WingMass.mass', 'ConfigWeight.wing_mass')  # TEMPORARY
        self.connect('WireMass.mass', 'ConfigWeight.wire_mass')
        
        self.connect('CruisePower.bRef', 'ToolingCost.cruiseOutput_bRef')  # ToolingCost inputs
        self.connect('CruisePower.cRef', 'ToolingCost.cruiseOutput_cRef')
        self.connect('costBuildupConst1.partsPerTool', 'ToolingCost.partsPerTool')
        self.connect('indep2.rProp', 'ToolingCost.rProp')
        self.connect('indep7.vehicle', 'ToolingCost.Vehicle')
        
        self.connect('SimpleMission.E', 'OperatingCost.E')  # OperatingCost inputs
        self.connect('SimpleMission.t', 'OperatingCost.flightTime')
        self.connect('indep4.batteryMass', 'OperatingCost.mass_battery')
        self.connect('indep5.motorMass', 'OperatingCost.mass_motors')
        self.connect('ConfigWeight.mass_structural', 'OperatingCost.mass_structural')
        self.connect('indep2.rProp', 'OperatingCost.rProp')
        self.connect('ToolingCost.toolCostPerVehicle', 'OperatingCost.toolingCost')
        self.connect('indep7.vehicle', 'OperatingCost.Vehicle')
  
        self.connect('ReserveMission.E', 'con1.EReserve')  # Constraint inputs
        self.connect('indep4.batteryMass', 'con1.mBattery')
        self.connect('HoverPower.hoverPower_PMax', 'con2.hoverPower_PMax')
        self.connect('indep5.motorMass', 'con2.mMotors')
        self.connect('ConfigWeight.mass_W', 'con3.mass_W')
        self.connect('indep6.mtom', 'con3.mtow')
        
        
if __name__ == '__main__':
    # SubProblem: define a Problem to optimize the system
    sub = Problem(root=TopLevelSystem())
    
    # SubProblem: set up the optimizer
    sub.driver = ScipyOptimizer()
    sub.driver.options['optimizer'] = 'COBYLA'  # The 'COBYLA' optimizer is supported by OpenMETA. 
                                                # Unlike the 'SLSQP' optimizer, the 'COBYLA' optimizer doesn't require a Jacobian matrix.
    sub.driver.options['disp'] = True  # enable optimizer output
    sub.driver.maxfun = 10000  # COBYLA-specific setting: maximum number of iterations
    sub.driver.rhobeg = 1000.0  # don't know what this is - yet - but I'm just going to play with some values
    sub.driver.rhoend = 10.0  #  convergence tolerance
    # ^ Working here
    
    # SubProblem: set design variables for sub.driver
    sub.driver.add_desvar('indep2.rProp', lower=0.3, upper=2.0)
    sub.driver.add_desvar('indep3.cruiseSpeed', lower=39.0, upper=80.0)
    sub.driver.add_desvar('indep4.batteryMass', lower=10.0, upper=999.0)
    sub.driver.add_desvar('indep5.motorMass', lower=1.0, upper=999.0)
    sub.driver.add_desvar('indep6.mtom', lower=100.0, upper=9999.0)
    
    # SubProblem: set design objectives
    sub.driver.add_objective('OperatingCost.C_costPerFlight')
    
    # SubProblem: set design variable constraints - Jonathan says that some of the optimizers
    # (in particular COBYLA) seem to totally ignore the design variable lower and upper bounds
    # Jonathan's work-around is to set additional constraints
    # Interesting article: http://openmdao.org/forum/questions/342/slsqpdriver-not-respecting-paramaters-low-and-high-contraints
    sub.driver.add_constraint('indep2.rProp', lower=0.3, upper=2.0)
    sub.driver.add_constraint('indep3.cruiseSpeed', lower=39.0, upper=80.0)
    sub.driver.add_constraint('indep4.batteryMass', lower=10.0, upper=999.0)
    sub.driver.add_constraint('indep5.motorMass', lower=1.0, upper=999.0)
    sub.driver.add_constraint('indep6.mtom', lower=100.0, upper=9999.0)
    
    # SubProblem: set design constraints
    sub.driver.add_constraint('con1.c', upper=0.0)
    sub.driver.add_constraint('con2.c', upper=0.0)
    sub.driver.add_constraint('con3.c', upper=0.0)
    
    # TopProblem: define a Problem to set up different optimization cases
    top = Problem(root=Group())
    
    # TopProblem: add independent variables
    top.root.add('indep1', IndepVarComp('range', 50.0))
    top.root.add('indep2', IndepVarComp('rProp', 1.0))
    top.root.add('indep3', IndepVarComp('cruiseSpeed', 50.0))
    top.root.add('indep4', IndepVarComp('batteryMass', 117.0))
    top.root.add('indep5', IndepVarComp('motorMass', 30.0))
    top.root.add('indep6', IndepVarComp('mtom', 650.0))
    #top.root.add('indep7', IndepVarComp('vehicle', 'tiltwing'))  # 1st get this working with just the tiltwing
    
    # TopProblem: add the SubProblem
    top.root.add('subprob', SubProblem(sub, params=['indep1.range', 'indep2.rProp', \
                                                    'indep3.cruiseSpeed', 'indep4.batteryMass', \
                                                    'indep5.motorMass', 'indep6.mtom'],
                                            unknowns=['OperatingCost.C_costPerFlight']))
    
    # TopProblem: connect top's independent variables to sub's params
    top.root.connect('indep1.range', 'subprob.indep1.range')
    top.root.connect('indep2.rProp', 'subprob.indep2.rProp')
    top.root.connect('indep3.cruiseSpeed', 'subprob.indep3.cruiseSpeed')
    top.root.connect('indep4.batteryMass', 'subprob.indep4.batteryMass')
    top.root.connect('indep5.motorMass', 'subprob.indep5.motorMass')
    top.root.connect('indep6.mtom', 'subprob.indep6.mtom')
    
    # TopProblem: set up the parameter study
    # for a parameter study, the following drivers can be used:
    # UniformDriver, FullFactorialDriver, LatinHypercubeDriver, OptimizedLatinHypercubeDriver
    # in this case, we will use FullFactorialDriver
    top.driver = FullFactorialDriver(num_levels=20)
    
    # TopProblem: add top.driver's design variables
    top.driver.add_desvar('indep1.range', lower=10000.0, upper=200000.0)
    
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
    db = sqlitedict.SqliteDict( 'subprob', 'iterations' )
    db_keys = list( db.keys() ) # list() needed for compatibility with Python 3. Not needed for Python 2
    for i in db_keys:
        data = db[i]
        print('\n')
        print(data['Unknowns'])
        print(data['Parameters'])
    
    
    