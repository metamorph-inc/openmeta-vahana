'''
# Name: wing_mass.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/6/2017
# Edit Date: 6/6/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate lifting surface structural areas

# Inputs:
#   W       - vehicle weight (to calculate lift) [N]
#   span    - wing span [m]
#   chord   - wing chord [m]
#   winglet - winglet length normalized by semi-span
#   fc      - fraction of vehicle lift supported by wing
#   xmotor  - vector of motor locations normalized by semi-span
#   thrust  - maximum thrust produced by motor

# Outputs:
#   mass    - mass of the lifting surface
'''


from __future__ import print_function

from openmdao.api import Component
import math
import numpy as np

class wing_mass(Component):

    def __init__(self):
    
        super(wing_mass, self).__init__()
        self.add_param('W', val=0.0)
        self.add_param('span', val=0.0)
        self.add_param('chord', val=0.0)
        self.add_param('winglet', val=0.0)
        self.add_param('fc', val=0.0)
        self.add_param('xmotor', val=0.0)
        self.add_param('thrust', val=0.0)
        
        ## Material Properties
        # rho is density [kg/m^3]
        # stress is design ultimate tensile stress [Pa]
        # shear is design ultimate shear stress [Pa]
        # minThk is minimum guage thickness [m]
        # width is rib width [m]
        # bearing is bearing allowable [Pa]
        
        # Unidirectional carbon fiber
        self.add_param('uni_rho', val=1660.0)
        self.add_param('uni_stress', val=450e6)
        
        # Bi-directional carbon fiber
        self.add_param('bid_rho', val=1660.0)
        self.add_param('bid_stress', val=275e6)
        self.add_param('bid_shear', val=47e6)
        self.add_param('bid_minThk', val=0.00042)
        self.add_param('bid_bearing', val=400e6)
        
        # Honeycomb core
        self.add_param('core_rho', val=52)
        self.add_param('core_minThk', val=0.0064)
        
        # Epoxy
        self.add_param('glue_thk', val=2.54e-4)
        self.add_param('glue_rho', val=1800.0)
        
        # Aluminum ribs
        self.add_param('rib_thk', val=0.0015)
        self.add_param('rib_width', val=0.0254)
        
        # Paint or vinyl
        self.add_param('paint_thk', val=0.00015)
        self.add_param('paint_rho', val=1800.0)
        
        # Aluminum
        self.add_param('alum_stress', val=350e6)
        self.add_param('alum_rho', val=2800.0)
        
        # Acrylic
        self.add_param('canopy_thk', val=0.003175)
        self.add_param('canopy_rho', val=1180.0)
        
        # Steel
        self.add_param('steel_shear', val=500e6)
        
        self.add_output('mass', val=0.0)
        
    def solve_nonlinear(self, params, unknowns, resids): #QUESTION: does this always need to be named solve_nonlinear
        ## Setup
        N = 10 # Number of spanwise points
        sf = 1.5 # Safety factor
        n = 3.8 # Maximum g's
        toc = 0.15 # Airfoil thickness
        cmocl = 0.02/1 # Ratio of cm/cl for sizing torsion (magnitude)
        LoD = 7 # For drag loads
        fwdWeb = [0.25, 0.35] # Forward web location x/c
        aftWeb = [0.65, 0.75] # Aft web location x/c
        xShear = 0.25 # Approximate shear center
        fudge = 1.2 # Scale up mass by this to account for misc components

        nRibs = len(xmotor)+2 #CHECK THIS: I'm assuming a simple Python list as the input
        xmotor = xmotor*span/2
        
        ## Airfoil
        naca = 5*toc*np.array([0.2969, -0.1260, -0.3516, 0.2843, -0.1015]).reshape(-1,1) # Thickness distribution for NACA 4-series airfoil
        coord = np.concatenate((fwdWeb, aftWeb, np.linspace(0,1,N)))
        coord = np.unique(coord).reshape(-1,1) # for a 1-D array, reshape(-1,1) serves the same role as Matlab's ' operator
        tmp = np.dot(np.concatenate((coord[:,0].reshape(-1,1)**0.5, coord[:,0].reshape(-1,1), coord[:,0].reshape(-1,1)**2, coord[:,0].reshape(-1,1)**3, coord[:,0].reshape(-1,1)**4), 1), naca)
        coord = np.concatenate((coord, tmp),1)
        topHalf = np.flipud(coord[1:,:])
        botHalf = np.dot(coord,np.array([[1, 0],[0, -1]]))
        coord = np.concatenate((topHalf,botHalf))