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
from scipy import interpolate

class wing_mass(Component):

    def __init__(self):
        super(wing_mass, self).__init__()
        self.add_param('W', val=0.0)
        self.add_param('span', val=0.0)
        self.add_param('chord', val=0.0)
        self.add_param('winglet', val=0.0)
        self.add_param('fc', val=0.0)
        #self.add_param('xmotor', val=0.0)
        self.add_param('rProp', val=0.0)
        self.add_param('cruiseOutput_bRef', val=0.0)
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
        self.add_param('uni_stress', val=450000000.0)
        
        # Bi-directional carbon fiber
        self.add_param('bid_rho', val=1660.0)
        self.add_param('bid_stress', val=275000000.0)
        self.add_param('bid_shear', val=47000000.0)
        self.add_param('bid_minThk', val=0.00042)
        self.add_param('bid_bearing', val=400000000.0)
        
        # Honeycomb core
        self.add_param('core_rho', val=52.0)
        self.add_param('core_minThk', val=0.0064)
        
        # Epoxy
        self.add_param('glue_thk', val=.000254)
        self.add_param('glue_rho', val=1800.0)
        
        # Aluminum ribs
        self.add_param('rib_thk', val=0.0015)
        self.add_param('rib_width', val=0.0254)
        
        # Paint or vinyl
        self.add_param('paint_thk', val=0.00015)
        self.add_param('paint_rho', val=1800.0)
        
        # Aluminum
        self.add_param('alum_stress', val=350000000.0)
        self.add_param('alum_rho', val=2800.0)
        
        # Acrylic
        self.add_param('canopy_thk', val=0.003175)
        self.add_param('canopy_rho', val=1180.0)
        
        # Steel
        self.add_param('steel_shear', val=500000000.0)
        
        self.add_output('mass', val=0.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
        # Setup
        N = 10  # Number of spanwise points
        sf = 1.5  # Safety factor
        n = 3.8  # Maximum g's
        toc = 0.15  # Airfoil thickness
        cmocl = 0.02 / 1  # Ratio of cm/cl for sizing torsion (magnitude)
        LoD = 7  # For drag loads
        fwdWeb = np.array([0.25, 0.35])  # Forward web location x/c
        aftWeb = np.array([0.65, 0.75])  # Aft web location x/c
        xShear = 0.25  # Approximate shear center
        fudge = 1.2  # Scale up mass by this to account for misc components
        
        xmotor = np.array([2*(0.5 + params['rProp'])/params['cruiseOutput_bRef'], 2*(0.5 + 3*params['rProp'] + 0.05)/params['cruiseOutput_bRef']])
        
        nRibs = len(xmotor) + 2.0 
        xmotor = xmotor * params['span'] / 2.0

        # Airfoil
        naca = 5 * toc * np.array([0.2969, -0.1260, -0.3516, 0.2843, -0.1015]).reshape(-1,1)  # Thickness distribution for NACA 4-series airfoil
        coord = np.concatenate((fwdWeb, aftWeb, np.linspace(0, 1, N)))
        coord = np.unique(coord).reshape(-1, 1)  # for a 1-D array, reshape(-1,1) serves the same role as Matlab's ' operator
        tmpCol = coord[:, 0].reshape(-1, 1)
        tmpArr = np.dot(np.concatenate((tmpCol ** 0.5, tmpCol, tmpCol ** 2, tmpCol ** 3, tmpCol ** 4), 1), naca)
        coord = np.concatenate((coord, tmpArr), 1)
        topHalf = np.flipud(coord[1:, :])
        botHalf = np.dot(coord, np.array([[1, 0], [0, -1]]))
        coord = np.concatenate((topHalf, botHalf))
        coord[:, 0] = coord[:, 0] - xShear

        # Beam Geometry
        x = np.concatenate((np.linspace(0, 1, N), np.linspace(1, 1 + params['winglet'], N))) * params['span'] / 2.0
        x = np.sort(np.concatenate((x, xmotor)))
        dx = x[1] - x[0]  # Don't forget: Python is 0-based whereas Matlab is 1-based
        N = len(x)
        fwdWeb = fwdWeb - xShear
        aftWeb = aftWeb - xShear

        # Loads
        L = (1 - (x / np.amax(x)) ** 2.0) ** (1.0 / 2.0)  # Elliptic lift distribution profile
        L0 = 0.5 * n * params['W'] * params['fc'] * sf  # Total design lift force on surface
        L = L0 / np.sum(L[0:N - 1] * np.diff(x[0:N])) * L  # Lift distribution

        T = L * params['chord'] * cmocl  # Torque distribution
        D = L / LoD  # Drag distribution

        Vx = np.concatenate(((np.cumsum(D[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Shear due to drag
        Vz = np.concatenate(((np.cumsum(L[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Shear due to lift
        Vt = 0 * Vz  # Initialize shear due to thrust
        for i in xmotor:
            Vt[x <= i] = Vt[x <= i] + params['thrust']  # Shear due to thrust

        Mx = np.concatenate(((np.cumsum(Vz[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Bending moment
        My = np.concatenate(((np.cumsum(T[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Torsion moment
        Mz = np.concatenate(((np.cumsum(Vx[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Drag moment
        Mt = np.concatenate(((np.cumsum(Vt[-2::-1] * -np.diff(x[-1::-1])))[::-1], np.array([0])))  # Thrust moment
        Mz = np.maximum(Mz, Mt)  # Worst case Mz

        # General structural properties
        # Torsion Cell
        box = np.copy(coord)
        box[box[:, 0] > aftWeb[1], :] = 0
        box[box[:, 0] < fwdWeb[0], :] = 0
        box = box*params['chord']
        box = box[~np.all(box == 0, axis=1)]  # Remove rows of all zeros


        def polyarea(x1, y1):  # https://en.wikipedia.org/wiki/Shoelace_formula - https://stackoverflow.com/a/30408825
            return 0.5*np.abs(np.dot(x1, np.roll(y1, 1))-np.dot(y1, np.roll(x1, 1)))

        torsionArea = polyarea(box[:, 0], box[:, 1])  # Enclosed wing area
        torsionLength = np.sum(np.sqrt(np.sum(np.diff(box, axis=0)**2, 1)))

        # Bending
        box = np.copy(coord)  # Get airfoil coordinates
        box[box[:, 0] > fwdWeb[1], :] = 0
        box[box[:, 0] < fwdWeb[0], :] = 0
        box = box[~np.all(box == 0, axis=1)]  # Remove rows of all zeros
        seg = list([])
        if bool(np.any(box)):
            seg.append(box[box[:, 1] > np.mean(box[:, 1]), :]*params['chord'])  # Upper fwd segment
            seg.append(box[box[:, 1] < np.mean(box[:, 1]), :]*params['chord'])  # Lower fwd segment
        else:
            seg.append(np.array([[0, 0], [0, 0], [0, 0]]))
            seg.append(np.array([[0, 0], [0, 0], [0, 0]]))

        # Drag
        box = np.copy(coord)  # Get airfoil coordinates
        box[box[:, 0] > aftWeb[1], :] = 0
        box[box[:, 0] < aftWeb[0], :] = 0
        box = box[~np.all(box == 0, axis=1)]  # Remove rows of all zeros
        if bool(np.any(box)):
            seg.append(box[box[:, 1] > np.mean(box[:, 1]), :]*params['chord'])  # Upper aft segment
            seg.append(box[box[:, 1] < np.mean(box[:, 1]), :]*params['chord'])  # Lower aft segment
        else:
            seg.append(np.array([[0, 0], [0, 0], [0, 0]]))
            seg.append(np.array([[0, 0], [0, 0], [0, 0]]))

        # Bending/drag inertia
        flapInertia = 0
        flapLength = 0
        dragInertia = 0
        dragLength = 0
        for i in range(4):
            l = np.sqrt(np.sum(np.diff(seg[i], axis=0)**2.0, 1)).reshape(-1, 1)  # Segment lengths
            c = (np.add(seg[i][1:, :], seg[i][0:-1, :]))/2.0  # Segment centroids

            if i < 2:
                flapInertia = flapInertia + abs(np.sum(l*c[:, 1].reshape(-1, 1)**2))  # Bending Inertia per unit thickness
                flapLength = flapLength + np.sum(l)
            else:
                dragInertia = dragInertia + abs(np.sum(l*c[:, 0].reshape(-1, 1)**2))  # Drag Inertia per unit thickness
                dragLength = dragLength + np.sum(l)

        # Shear
        box = coord.copy()
        box[box[:, 0] > fwdWeb[1], :] = 0
        box = box[~np.all(box == 0, axis=1)]  # Remove rows of all zeros
        z = list([])
        x1 = box[box[:, 1] > 0, 0]
        y1 = box[box[:, 1] > 0, 1]
        f1 = interpolate.interp1d(x1, y1)  # numpy.interp gives wonky answers if the x-values don't increase steadily
        z.append(f1(fwdWeb[0])*params['chord'])
        x2 = box[box[:, 1] < 0, 0]
        y2 = box[box[:, 1] < 0, 1]
        f2 = interpolate.interp1d(x2, y2)
        z.append(f2(fwdWeb[0])*params['chord'])
        h = z[0] - z[1]

        # Skin
        box = coord.copy()*params['chord']
        skinLength = sum(np.sqrt(np.sum(np.diff(box, axis=0)**2, 1)))
        A = polyarea(box[:, 0], box[:, 1])

        # Structural Calcs

        # Torsion Analysis: all torsion taken in skin
        tTorsion = My*dx/(2*params['bid_shear']*torsionArea)  # Torsion skin thickness
        tTorsion = np.maximum(tTorsion, params['bid_minThk']*np.ones(N))  # Min gauge constraint
        mTorsion = tTorsion*torsionLength*params['bid_rho']  # Mass for torsion
        mCore = params['core_minThk']*torsionLength*params['core_rho']*np.ones(N)  # Core mass
        mGlue = params['glue_thk']*params['glue_rho']*torsionLength*np.ones(N)

        # Flap Bending Analysis
        tFlap = Mx*np.max(seg[0][:, 1])/(flapInertia*params['uni_stress'])  # Thickness for flap bending  # note: Python appears to have less precision than Matlab
        mFlap = tFlap*flapLength*params['uni_rho']  # Mass for flap bending
        mGlue = mGlue+params['glue_thk']*params['glue_rho']*flapLength*np.ones(N)

        # Drag Bending Analysis
        tDrag = Mz*max(seg[2][:, 0])/(dragInertia*params['uni_stress'])  # Thickness for flap bending
        mDrag = tDrag*dragLength*params['uni_rho']  # Mass for flap bending
        mGlue = mGlue+params['glue_thk']*params['glue_rho']*dragLength*np.ones(N)

        # Shear Web Analysis: all shear taken in shear web
        tShear = 1.5*Vz/(params['bid_shear']*h)
        tShear = np.maximum(tShear, params['bid_minThk']*np.ones(N))  # Min gauge constraint
        mShear = tShear*h*params['bid_rho']

        # Paint weight
        mPaint = skinLength*params['paint_thk']*params['paint_rho']*np.ones(N)

        # Section mass
        m = mTorsion+mCore+mFlap+mDrag+mShear+mGlue+mPaint

        # Rib weight
        mRib = (A+skinLength*params['rib_width'])*params['rib_thk']*params['alum_rho']

        # Total weight
        unknowns['mass'] = 2*(np.sum(m[0:-1]*np.diff(x))+nRibs*mRib)*fudge


