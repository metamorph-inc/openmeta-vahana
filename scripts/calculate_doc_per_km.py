'''
# Name: calculate_doc_per_km.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 8/6/2017
# Edit Date: 8/6/2017

# Inputs:
costPerFlight   - cost per a flight [$]
range           - range [m]

# Outputs:
'''

from __future__ import print_function

from openmdao.api import Component

class calculate_doc_per_km(Component):
    def __init__(self):
        super(calculate_doc_per_km, self).__init__()
        self.add_param('costPerFlight', val=0.0)
        self.add_param('range', val=0.0)
        
        self.add_output('costPerFlightPerKm', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['costPerFlightPerKm'] = params['costPerFlight']/(params['range']/1000)