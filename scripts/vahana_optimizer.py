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

from openmdao.api import Problem, Group, Component, IndepVarComp, ExecComp, \  # OpenMDAO imports
                         ScipyOptimizer, SubProblem, FullFactorialDriver, \
                         SqliteRecorder

import sqlitedict
from pprint import pprint

#TODO: Add Component imports
#      and(or)
#      Add Component definitions

#TODO: Add Group imports
#      and(or)
#      Add Group definitions


class TopLevelSystem(Group):
    def __init__(self):
        super(TopLevelSystem, self).__init__()
        
        # add independent variables - IS THIS EVEN NEEDED?
        # E.g: self.add('indep1', IndepVarComp('x', 0.0))
        #TODO
        
        # add components
        # E.g: self.add('comp', System())
        #TODO
        
        # add constraint equations
        # E.g: self.add('con, ExecComp('c = x-y))
        #TODO
        
        # connect components and variables
        # E.g: self.connect('indep1.x', 'comp.x') 
        #TODO        
        
        
if __name__ == '__main__':
    # SubProblem: define a Problem to optimize the system
    sub = Problem(root=TopLevelSystem())
    
    # SubProblem: set up the optimizer
    sub.driver = ScipyOptimizer()
    sub.driver.options['optimizer'] = 'COBYLA'
    sub.driver.options['disp'] = True  # disable optimizer output
    
    # SubProblem: set design variables for sub.driver
    # E.g: sub.driver.add_desvar("indep1.x", lower=3.1, upper=50)
    #TODO    
    
    # SubProblem: set design objectives
    # sub.driver.add_objective("comp.f_xyz")
    #TODO
    
    # SubProblem: set constraints
    # E.g: sub.driver.add_constraint("con.c", lower=15.0)
    #TODO
    
    # TopProblem: define a Problem to set up different optimization cases
    top = Problem(root=Group())
    
    # TopProblem: add independent variables
    # E.g: prob.root.add("top_indep1", IndepVarComp('x', 3.1))
    #TODO
    
    # TopProblem: add the SubProblem
    # E.g: prob.root.add("subprob", SubProblem(sub, params=['indep1.x', 'indep2.y', 'indep3.z'],
    #      unknowns=['comp.f_xyz']))
    #TODO
    
    # TopProblem: connect top's independent variables to sub's params
    # E.g: prob.root.connect("top_indep1.x", "subprob.indep1.x")
    #TODO
    
    # TopProblem: set up the parameter study
    # for a parameter study, the following drivers can be used:
    # UniformDriver, FullFactorialDriver, LatinHypercubeDriver, OptimizedLatinHypercubeDriver
    # in this case, we will use FullFactorialDriver
    prob.driver = FullFactorialDriver(num_levels=20)
    
    # TopProblem: add top.driver's design variables
    # E.g: prob.driver.add_desvar('top_indep3.z', lower=0.0, upper=20.0)
    #TODO
    
    # Data collection
    recorder = SqliteRecorder('subprob')
    recorder.options['record_params'] = True
    recorder.options['record_metadata'] = True
    prob.driver.add_recorder(recorder)
    
    # Setup
    prob.setup(check=False)
    
    # Run 
    prob.run()
    
    # Cleanup
    prob.cleanup()
    
    # Data retrieval & display
    db = sqlitedict.SqliteDict( 'subprob', 'iterations' )
    db_keys = list( db.keys() ) # list() needed for compatibility with Python 3. Not needed for Python 2
    for i in db_keys:
        data = db[i]
        print('\n')
        print(data['Unknowns'])
        print(data['Parameters'])
    
    
    