'''
# Name: vahana_optimizer.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/15/2017
# Edit Date: 6/15/2017

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
from test_component import TestSystem
#from cruise_power import CruisePower
#from hover_power import HoverPower
#from loiter_power import loiter_power

#TODO: Add Component imports
# E.g: from test_component import TestSystem
#      and(or)
#      Add Component definitions


#TODO: Add Group imports
#      and(or)
#      Add Group definitions


class TopLevelSystem(Group):
    def __init__(self):
        super(TopLevelSystem, self).__init__()
        
        # add independent variables - IS THIS EVEN NEEDED?
        self.add('indep1', IndepVarComp('range', 50.0))
        self.add('indep2', IndepVarComp('rProp', 1.0))
        self.add('indep3', IndepVarComp('cruiseSpeed', 50.0))
        self.add('indep4', IndepVarComp('batteryMass', 117.0))
        self.add('indep5', IndepVarComp('motorMass', 30.0))
        self.add('indep6', IndepVarComp('mtom', 650.0))
        
        # add components
        self.add('comp', TestSystem())
        
        # add constraint equations
        self.add('con', ExecComp('c = motorMass + batteryMass - mtom'))
        
        # connect components and variables
        self.connect('indep1.range', 'comp.range') 
        self.connect('indep2.rProp', 'comp.rProp') 
        self.connect('indep3.cruiseSpeed', 'comp.cruiseSpeed') 
        self.connect('indep4.batteryMass', 'comp.batteryMass')
        self.connect('indep5.motorMass', 'comp.motorMass')
        self.connect('indep6.mtom', 'comp.mtom')
        self.connect('comp.motorMass', 'con.motorMass')
        self.connect('comp.batteryMass', 'con.batteryMass')
        self.connect('comp.mtom', 'con.mtom')
        
        
if __name__ == '__main__':
    # SubProblem: define a Problem to optimize the system
    sub = Problem(root=TopLevelSystem())
    
    # SubProblem: set up the optimizer
    sub.driver = ScipyOptimizer()
    sub.driver.options['optimizer'] = 'COBYLA'  # The 'COBYLA' optimizer is supported by OpenMETA. 
                                                # Unlike the 'SLSQP' optimizer, the 'COBYLA' optimizer doesn't require a Jacobian matrix.
    sub.driver.options['disp'] = True  # enable optimizer output
    
    # SubProblem: set design variables for sub.driver
    sub.driver.add_desvar('indep2.rProp', lower=0.3, upper=2.0)
    sub.driver.add_desvar('indep3.cruiseSpeed', lower=39.0, upper=80.0)
    sub.driver.add_desvar('indep4.batteryMass', lower=10.0, upper=999.0)
    sub.driver.add_desvar('indep5.motorMass', lower=1.0, upper=999.0)
    sub.driver.add_desvar('indep6.mtom', lower=100.0, upper=9999.0)
    
    # SubProblem: set design objectives
    sub.driver.add_objective('comp.costPerFlight')
    
    # SubProblem: set constraints
    sub.driver.add_constraint("con.c", lower=0.0)
    
    # TopProblem: define a Problem to set up different optimization cases
    top = Problem(root=Group())
    
    # TopProblem: add independent variables
    #top.root.add('vehicle', IndepVarComp('vehicle'))  # 1st get this working with just the tiltwing
    top.root.add('indep1', IndepVarComp('range', 50.0))
    top.root.add('indep2', IndepVarComp('rProp', 1.0))
    top.root.add('indep3', IndepVarComp('cruiseSpeed', 50.0))
    top.root.add('indep4', IndepVarComp('batteryMass', 117.0))
    top.root.add('indep5', IndepVarComp('motorMass', 30.0))
    top.root.add('indep6', IndepVarComp('mtom', 650.0))
    
    # TopProblem: add the SubProblem
    top.root.add('subprob', SubProblem(sub, params=['indep1.range', 'indep2.rProp', \
                                                    'indep3.cruiseSpeed', 'indep4.batteryMass', \
                                                    'indep5.motorMass', 'indep6.mtom'],
                                            unknowns=['comp.costPerFlight']))
    
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
    top.driver = FullFactorialDriver(num_levels=21)
    
    # TopProblem: add top.driver's design variables
    top.driver.add_desvar('indep1.range', lower=10.0, upper=20.0)  #TODO: Change lower bounds to '10000.0' and upper bound to '200000.0'
    
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
    
    
    