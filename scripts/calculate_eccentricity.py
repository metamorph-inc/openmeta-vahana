'''
# Name: calculate_eccentricity.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe, Austin Tabulog, Timothy Thomas
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/4/2017
# Edit Date: 8/4/2017

# Calculate eccentricity based on CAD's center of mass, xFoil's airfoil CL,
# and CruisePower's wing/canard surface area

# Inputs:
#   Cl              - airfoil lift coefficient
#   Cd              - airfoil drag coefficient
#   Cm              - airfoil moment coefficient
#   Chord           - airfoil chord [m]
#   V               - velocity [m/s]
#   P               - density [kg/m^3]
#   S               - total surface area of lifting surface [m^2]
#   CanardPt        - CanardAxis coordinates - string in form: x; y; z [mm]
#   WingPt          - WingAxis coordinates - string in form: x; y; z [mm]
#   CenterOfMass    - Center of Mass coordinates - string in form: x; y; z [mm]

# Outputs:
#   eccentricity    - z-axis difference between estimated center-of-lift and center-of-mass [m]
'''


from __future__ import print_function

from openmdao.api import Component
import math

class calculate_eccentricity(Component):

    def __init__(self):
        super(calculate_eccentricity, self).__init__()
        self.add_param('Cl', val=1.0)
        self.add_param('Cd', val=1.0)
        self.add_param('Cm', val=1.0)
        self.add_param('Chord', val=1.0)
        self.add_param('V', val=1.0)
        self.add_param('P', val=1.0)
        self.add_param('S', val=1.0)
        self.add_param('CanardPt', val=0.0)
        self.add_param('WingPt', val=0.0)
        self.add_param('CenterOfMass', val=0.0)    
        
        self.add_output('eccentricity', val=1.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
        cl = float(params['Cl'])
        cd = float(params['Cd'])
        cm = float(params['Cm'])
        chord = params['Chord']
        v = params['V']
        p = params['P']
        s = params['S']
        canardZCoord = params['CanardPt']
        wingZCoord = params['WingPt']
        comZCoord = params['CenterOfMass']

        q = 0.5*p*v**2.0
        wingArea = 0.6*s
        canardArea = 0.4*s
        
        # Lift
        liftWing = cl*q*wingArea        # using Cl as a very rough approximation of CL - 
        liftCanard = cl*q*canardArea    # in reality, wing CL is generally lower than airfoil Cl
        
        # Drag
        # eventually add/use drag calculations
        
        # Moment
        momentWing = cm*q*wingArea*chord
        momentCanard = cm*q*canardArea*chord
        
        wingZDisp = abs(wingZCoord-comZCoord)
        canardZDisp = abs(canardZCoord-comZCoord)
        
        e = momentWing + momentCanard - wingZDisp*liftWing*0.001 + canardZDisp*liftCanard*0.001  # eventually add drag values too!
        
        unknowns['eccentricity'] = e
        