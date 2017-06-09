'''
# Name: constraints_checker.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/8/2017
# Edit Date: 6/8/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Checks to see whether or not predetermined constraint conditions are satisfied
# Outputs:
#   '1' if all predetermined constraint conditions have been satisfied
#   '0' if at least one pretdetermided constraint condition has not been satisfied

# Inputs:
#   Vehicle                     - Vehicle type ('tiltwing' or 'helicopter')
#   mBattery                    - battery mass [kg]
#   mMotors                     - mass of motors [kg]
#   mtow                        - maximum take-off mass
#   EReserve                    - energy required to complete reserve mission [kW-hr]
#   hoverPower_PMax             - #TODO
#   hoverPower_VAutoRotation    - #TODO
#   hoverPower_Vtip             - #TODO
#   mass_W                      - total weight [N]
#   mass_m                      - total mass [kg]
#   mass_rotor                  - rotor mass [kg]
#   rProp                       - rProp [m]

# Outputs:
#   allPass                     - '1' = all constraints satisfied; '0' = at least one constraint unsatisfied
'''

from __future__ import print_function

from openmdao.api import Component
import math

class constraints_checker(Component):
    def __init__(self):
        super(constraints_checker, self).__init__()
        self.add_param('Vehicle', val=u'abcdef')
        self.add_param('mBattery', val=0.0)
        self.add_param('mMotors', val=0.0)
        self.add_param('mtow', val=0.0)
        self.add_param('EReserve', val=0.0)
        self.add_param('hoverPower_PMax', val=0.0)
        self.add_param('hoverPower_VAutoRotation', val=0.0)
        self.add_param('hoverPower_Vtip', val=0.0)
        self.add_param('mass_W', val=0.0)    
        self.add_param('mass_m', val=0.0)
        self.add_param('mass_rotor', val=0.0)
        self.add_param('rProp', val=0.0)
        self.add_param('cruiseSpeed', val=0.0)
        
        
        self.add_output('allPass', val='fail')
    
    def solve_nonlinear(self, params, unknowns, resids):
        # Assumed values
        batteryEnergyDensity = 230  # Expected pack energy density in 3-5 years [Wh/kg]
        motorPowerDensity = 5  # kW/kg, including controller and other accessories in 3-5 years
        dischargeDepthReserve = 0.95  # Can only use 95% of battery energy in reserve mission
        
        # Constraint on available energy (E is in kW-hr)
        c1 = (0 > (params['EReserve'] - params['mBattery'] * batteryEnergyDensity * dischargeDepthReserve / 1000.0))
        
        # Constraint on available motor power (kW)
        c2 = (0 > (params['hoverPower_PMax'] / 1000.0 - params['mMotors'] * motorPowerDensity))
        
        # Constraint on max take-off weight
        c3 = (0 > (params['mass_W'] - params['mtow'] * 9.8))
        
        c4 = False
        if (params["Vehicle"].lower().replace('-', '') == "helicopter"):  # helicopter
            # Auto-rotation energy constraint => kinetic energy in blades has to be
            # twice that of vehicle in autorotation descent to be able to arrest
            # the descent.
            # See "Helicopter Theory" section 7-5, assume rotor CLmax is twice
            # hover CL. Rotor inertia is approximated as a solid rod. 
            c4 = (0 > (0.5 * params['mass_m'] * params['hoverPower_VAutoRotation']**2.0 - 0.5 * 1.0 / 3.0 * params['mass_rotor'] * params['hoverPower_Vtip']**2.0))
        else:  # tilt-wing
            c4 = True
        
        c5 = False
        if (params["Vehicle"].lower().replace('-', '') == "helicopter"):  # helicopter
            if ((params['rProp'] > 1.0) and (params['rProp'] < 10.0)):
                c5 = True
        else:  #tilt-wing
             if ((params['rProp'] > 0.3) and (params['rProp'] < 2.0)):
                c5 = True           
        
        c6 = False
        if (params["Vehicle"].lower().replace('-', '') == "helicopter"):  # helicopter
            if ((params['cruiseSpeed'] > 30.0) and (params['cruiseSpeed'] < 80.0)):
                c6 = True
        else:  #tilt-wing
             if ((params['cruiseSpeed'] > (1.3 * 35)) and (params['cruiseSpeed'] < 80.0)):
                c6 = True           
        
        test = c1 and c2 and c3 and c4 and c5 and c6
        
        if test:
            unknowns['allPass'] = "pass"
        else:
            unknowns['allPass'] = "fail"