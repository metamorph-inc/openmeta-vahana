'''
# Name: prop_mass.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 7/20/2017
# Edit Date: 7/20/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate propeller blade mass

# Inputs:
#   R - rotor radius [m]
#   T - maximum thrust [N]

# Outputs:
#   mass - Mass of the blades for one propeller [kg]
'''

from __future__ import print_function

from openmdao.api import Component
from openmdao.api import Problem, IndepVarComp, Group  # for unit testing
import math
import numpy as np
from scipy import interpolate

class prop_mass(Component):

    def __init__(self):
        super(prop_mass, self).__init__()
        self.add_param('rProp', val=1.0)
        self.add_param('thrust', val=1.0)
        
        self.add_output('mass', val=1.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
        
        rProp = params['rProp']
        thrust = params['thrust']
        
        # Setup
        chord = 0.1 * rProp  # Assumed prop chord 
        nBlades = 3.0  # Number of blades
        N = 5  # Number of radial points
        sf = 1.5  # Safety factor
        toc = 0.12  # Average blade t/c
        fwdWeb = np.array([0.25, 0.35])  # Forward web location x/c
        xShear = 0.25  # Approximate shear center
        rootLength = rProp / 10.0  # Root fitting length [m]
        fudge = 1.2  # Fudge factor to account for misc items
        sound = 340.2940  # Speed of sound [m/s]
        tipMach = 0.65  # Tip mach number
        cmocl = 0.02 / 1.0  # Ratio of cm/cl for sizing torsion (magnitude)
        
        # List of Material properties
        # rho is density [kg/m^3]
        # stress is design ultimate tensile stress [Pa]
        # shear is design ultimate shear stress [Pa]
        # minThk is minimum gauge thickness [m]
        # width is rib width
        # bearing is bearing allowable [Pa]

        # Unidirectional carbon fiber
        uni_rho = 1660.0
        uni_stress = 450.0e6

        # Bi-directional carbon fiber
        bid_rho = 1660.0
        bid_stress = 275.0e6
        bid_shear = 47.0e6
        bid_minThk = 0.00042
        bid_bearing = 400.0e6

        # Honeycomb core
        core_rho = 52.0
        core_minThk = 0.0064

        # Epoxy
        glue_thk = 2.54e-4
        glue_rho = 1800.0

        # Aluminum ribs
        rib_thk = 0.0015
        rib_width = 0.0254

        # Paint or vinyl
        paint_thk = 0.00015
        paint_rho = 1800.0

        # Aluminum
        alum_stress = 350.0e6
        alum_rho = 2800.0

        # Acrylic
        canopy_thk = 0.003175
        canopy_rho = 1180.0

        # Steel
        steel_shear = 500.0e6
        
        # Airfoil
        naca = 5.0 * toc * np.array([0.2969, -0.1260, -0.3516, 0.2843, -0.1015]).reshape(-1,1)  # Thickness distribution for NACA 4-series airfoil
        coord = np.concatenate((fwdWeb, np.linspace(0, 1, N)))
        coord = np.unique(coord).reshape(-1, 1)  # for a 1-D array, reshape(-1,1) serves the same role as Matlab's ' operator
        tmpCol = coord[:, 0].reshape(-1, 1)
        tmpArr = np.dot(np.concatenate((tmpCol ** 0.5, tmpCol, tmpCol ** 2.0, tmpCol ** 3.0, tmpCol ** 4.0), 1), naca)
        coord = np.concatenate((coord, tmpArr), 1)
        topHalf = np.flipud(coord[1:, :])
        botHalf = np.dot(coord, np.array([[1, 0], [0, -1]]))
        coord = np.concatenate((topHalf, botHalf))
        coord[:, 0] = coord[:, 0] - xShear
        
        # Beam Geometry
        x = np.linspace(0, rProp, N)
        dx = x[1] - x[0]  # Don't forget: Python is 0-based whereas Matlab is 1-based
        fwdWeb = fwdWeb - xShear
        
        # Loads
        omega = sound*tipMach/rProp  # Rotational speed (for CF calc)
        F = sf*3.0*thrust/(rProp**3.0)*(x**2.0)/nBlades  # Force distribution
        Q = F*chord*cmocl  # Torque distribution

        # Initial mass estimates
        box = coord*chord  # OML coordinates
        L = sum(np.sqrt(np.sum(np.diff(box, axis=0)**2, 1)))  # Skin length
        y0 = (max(box[:, 1])-min(box[:, 1]))/2.0
        M0 = sf*thrust/nBlades*0.75*rProp  # Bending moment
        m = uni_rho*dx*M0/(2*uni_stress*y0)+L*bid_minThk*dx*bid_rho  # Assumed mass distribution
        m = m*np.ones(N)
        error = 1  # Initialize error
        tolerance = 1e-8  # Mass tolerance
        massOld = sum(m)

        # General structural properties
        # Torsion Properties

        def polyarea(x1, y1):  # https://en.wikipedia.org/wiki/Shoelace_formula - https://stackoverflow.com/a/30408825
           return 0.5*np.abs(np.dot(x1, np.roll(y1, 1))-np.dot(y1, np.roll(x1, 1)))       

        Ae = polyarea(box[:, 0] ,box[:, 1])  # Enclosed wing area
        skinLength = sum(np.sqrt(np.sum(np.diff(box, axis=0)**2, 1)))

        # Flap Properties
        box = np.copy(coord)  # Get airfoil coordinates
        box[box[:, 0] > fwdWeb[1], :] = 0
        box[box[:, 0] < fwdWeb[0], :] = 0
        box = box[~np.all(box == 0, axis=1)]  # Remove rows of all zeros
        seg = list([])
        if bool(np.any(box)):
            seg.append(box[box[:, 1] > np.mean(box[:, 1]), :]*chord)  # Upper fwd segment
            seg.append(box[box[:, 1] < np.mean(box[:, 1]), :]*chord)  # Lower fwd segment
        else:
            seg.append(np.array([[0, 0], [0, 0], [0, 0]]))
            seg.append(np.array([[0, 0], [0, 0], [0, 0]]))
        
        # Flap/drag inertia
        capInertia = 0
        capLength = 0
        for i in range(2):
            l = np.sqrt(np.sum(np.diff(seg[i], axis=0)**2.0, 1)).reshape(-1, 1)  # Segment lengths
            c = (np.add(seg[i][1:, :], seg[i][0:-1, :]))/2.0  # Segment centroids

            capInertia = capInertia + abs(np.sum(l*c[:, 1].reshape(-1, 1)**2))  # Bending Inertia per unit thickness
            capLength = capLength + np.sum(l)

        # Shear Properties
        box = np.copy(coord)  # Get airfoil coordinates
        box[box[:, 0] > fwdWeb[1], :] = 0  # Trim coordinates
        box = box[~np.all(box == 0, axis=1)]  # Remove rows of all zeros
        z = box[box[:, 0] == fwdWeb[0], 1]*chord;
        shearHeight = abs(z[0]-z[1]);
        
        # Core Properties
        box = np.copy(coord)  # get airfoil coordinates
        box[box[:, 0] < fwdWeb[0], :] = 0
        box = box*chord
        coreArea = polyarea(box[:, 0], box[:, 1])
        
        # Shear/Moment Calcs
        Vz = np.concatenate(((np.cumsum(F[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Shear due to lift
        Mx = np.concatenate(((np.cumsum(Vz[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Flap moment
        My = np.concatenate(((np.cumsum(Q[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Torsion moment

        while error > tolerance:
            CF = sf*(omega**2)*np.concatenate(((np.cumsum(m[-2::-1] * -np.diff(x[-1::-1]) * x[-2::-1]))[::-1], np.array([0])))  # Centripetal force
        
            # Structural Calcs
            # Torsion Analysis: all torsion taken in skinLength
            tTorsion = My/(2.0*bid_shear*Ae)  # Torsion skin thickness
            tTorsion = np.maximum(tTorsion, bid_minThk*np.ones(N))  # Min gauge constraint
            mTorsion = tTorsion*skinLength*bid_rho  # Mass for torsion
            
            # Flap Bending Analysis: all bending taken in fwd caps
            tFlap = CF/(capLength*uni_stress) + Mx*np.max(abs(box[:, 1]))/(capInertia*uni_stress)  # Thickness for flap bending
            mFlap = tFlap*capLength*uni_rho  # Mass for flap bending
            mGlue = glue_thk*glue_rho*capLength*np.ones(N)
            
            # Shear Web Analysis: all shear taken in shear web
            tShear = 1.5*Vz/(bid_shear*shearHeight)
            tShear = np.maximum(tShear, bid_minThk*np.ones(N))  # min gauge constraint
            mShear = tShear*shearHeight*bid_rho
            
            # Paint weight
            mPaint = skinLength*paint_thk*paint_rho*np.ones(N)
            
            # Core Mass
            mCore = coreArea*core_rho*np.ones(N)
            mGlue = mGlue+glue_thk*glue_rho*skinLength*np.ones(N)
        
            # Section mass
            m = mTorsion+mCore+mFlap+mShear+mGlue+mPaint
            
            # Rib weight
            mRib = (Ae+skinLength*rib_width)*rib_thk*alum_rho

            # Root fitting
            box = coord*chord
            rRoot = np.max(box[:, 1]) - np.min(box[:, 1])/2.0  # Fitting diam is thickness
            t = np.max(CF)/(2.0*math.pi*rRoot*alum_stress) + np.max(Mx)/(3.0*math.pi*(rRoot**2)*alum_stress)
            mRoot = 2.0*math.pi*rRoot*t*rootLength*alum_rho

            # Total weight
            mass = nBlades*(np.sum(m[0:-1] * np.diff(x))+2.0*mRib+mRoot)
            error = abs(mass-massOld)
            massOld = mass
            
        mass = fudge*mass  # Fudge factor
        
        unknowns['mass'] = mass

            
if __name__ == "__main__":  # DEBUG
    top = Problem()
    root = top.root = Group()

    # Sample Inputs
    indep_vars_constants = [('rProp', 1.4),
                            ('thrust', 10000.0)]

    root.add('Inputs', IndepVarComp(indep_vars_constants))

    root.add('Example', prop_mass())

    root.connect('Inputs.rProp', 'Example.rProp')
    root.connect('Inputs.thrust', 'Example.thrust')

    top.setup()
    top.run()
        