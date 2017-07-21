'''
# Name: fuselage_mass.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/12/2017
# Edit Date: 6/12/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy ) 
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment.

# Estimate fuselage structural mass assuming a structural keel to take
# bending and torsional loads.

# Inputs:
# length - fuselage length [m]
# width  - fuselage width [m]
# height - fuselage height [m]
# span   - wingspan [m]
# weight - vehicle weight [N]

# Outputs:
#   mass    - mass of the fuselage [kg]
'''


from __future__ import print_function

from openmdao.api import Component
import math

class fuselage_mass(Component):

    def __init__(self):
        super(fuselage_mass, self).__init__()
        self.add_param('length', val=0.0)
        self.add_param('width', val=0.0)
        self.add_param('height', val=0.0)
        self.add_param('span', val=0.0)
        self.add_param('weight', val=0.0)
        
        self.add_output('mass', val=0.0)
        
    def solve_nonlinear(self, params, unknowns, resids):
        ng = 3.8  # Max g lift
        nl = 3.5  # Landing load factor
        sf = 1.5  # Safety factor

        # Load material properties:
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
        alum_stress = 350e6
        alum_rho = 2800.0

        # Acrylic
        canopy_thk = 0.003175
        canopy_rho = 1180.0

        # Steel
        steel_shear = 500.0e6

        # Skin areal weight
        arealWeight = bid_minThk * bid_rho + core_minThk * core_rho + paint_thk * paint_rho

        # Skin Mass - approximate area of ellipsoid given length, width, height,
        # (see https://en.wikipedia.org/wiki/Ellipsoid#Surface_area)
        Swet = 4.0 * math.pi * (((params['length'] * params['width'] / 4.0) ** 1.6 + (params['length'] * params['height'] / 4.0) ** 1.6 + \
            (params['width'] * params['height'] / 4.0) ** 1.6) / 3.0) ** (1.0 / 1.6)
        skinMass = Swet * arealWeight

        # Bulkhead Mass
        bulkheadMass = 3 * math.pi * params['height'] * params['width'] / 4 * arealWeight

        # Canopy Mass
        canopyMass = Swet / 8 * canopy_thk * canopy_rho

        # Keel Mass due to lift
        L = ng * params['weight'] * sf  # Lift
        M = L * params['length'] / 2  # Peak moment
        beamWidth = params['width'] / 3  # Keel width
        beamHeight = params['height'] / 10  # Keel height

        A = M * beamHeight / (4 * uni_stress * (beamHeight / 2) ** 2)
        massKeel = A * params['length'] * uni_rho

        # Keel Mass due to torsion
        M = 0.25 * L * params['span'] / 2  # Wing torsion
        A = beamHeight * beamWidth
        t = 0.5 * M / (bid_shear * A)
        massKeel = massKeel + 2 * (beamHeight + beamWidth) * t * bid_rho

        # Keel Mass due to landing
        F = sf * params['weight'] * nl * math.sqrt(1 ** 2 + 0.8 ** 2) / 2  # Landing force, side landing
        A = F / steel_shear  # Required bolt area
        d = 2 * math.sqrt(A / math.pi)  # Bolt diameter
        t = F / (d * bid_bearing)  # Laminate thickness
        V = math.pi * (20 * t) ** 2 * t / 3  # Pad up volume
        massKeel = massKeel + 4 * V * bid_rho  # Mass of all 4 pad ups

        # Total mass
        unknowns['mass'] = skinMass + bulkheadMass + canopyMass + massKeel