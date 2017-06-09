'''
# Name: tooling_cost.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 6/8/2017
# Edit Date: 6/8/2017

# Conversion of Airbus A^3's vahanaTradeStudy>reserveMission.mat code
# (located here: https://github.com/VahanaOpenSource/vahanaTradeStudy )
# to Python 2.7 for use in the MetaMorph, Inc. OpenMETA environment
# http://www.metamorphsoftware.com/openmeta/

# Estimate tooling cost of a vehicle by summing tooling costs for all major
# components

# Inputs:
#   Vehicle             - Vehicle type (0 = 'tilt-wing' and 1 = 'helicopter')
#   rProp               - prop radius
#   cruiseOutput_bRef   - mass of motors [kg]
#   cruiseOutput_cRef   - maximum take-off mass [kg]
#   partsPerTool        - # of parts produced by tool

# Outputs:
#   toolCostPerVehicle  - Estimate of tool cost per vehicle [$]
'''

from __future__ import print_function

from openmdao.api import Component
import math

class tooling_cost(Component):
    def __init__(self):
        super(tooling_cost, self).__init__()
        self.add_param('Vehicle', val=u'abcdef')
        self.add_param('rProp', val=0.0)
        self.add_param('cruiseOutput_bRef', val=0.0)
        self.add_param('cruiseOutput_cRef', val=0.0)
        self.add_param('partsPerTool', val=0.0)
        
        self.add_output('toolCostPerVehicle', val=0.0)
    
    def solve_nonlinear(self, params, unknowns, resids):
        # Assumed values
        fuselageWidth = 1.0
        fuselageLength = 5.0
        toc = 0.15  # Wing / canard thickness
        propRadius = params['rProp']
        propChord = 0.15*propRadius  # Max chord
        xhinge = 0.8
        winglet = 0.2
        
        totalToolCost = 0.0
        
        def toolingCost(length, width, depth):
            # Material
            toolSideOffset = 0.09  # Offset on each side of tool
            toolDepthOffset = 0.03  # Offset at bottom of tool
            toolCost = 10000.0  # Cost be m^3 of tooling material [$/m^3]

            toolVolume = (length+2*toolSideOffset)*(width+2*toolSideOffset)*(depth+toolDepthOffset)
            materialCost = toolCost*toolVolume  # Tooling material costs

            # Machining (Rough Pass)
            roughSFM = 200.0  # Roughing surface feet per minute
            roughFPT = 0.003  # Roughing feed per tooth [in]
            roughCostRate = 150.0/3600.0  # Cost to rough [$/s]
            roughBitDiam = 0.05  # Rougher diameter [m]

            roughBitDepth = roughBitDiam/4  # Rougher cut depth [m]
            roughRPM = 3.82*roughSFM/(39.37*roughBitDiam)  # Roughing RPM
            roughFeed = roughFPT*roughRPM*2*0.00042  # Roughing Feed [m/s]
            roughBitStep = 0.8*roughBitDiam  # Rougher step size

            cutVolume = length*math.pi*depth*width/4  # Amount of material to rough out
            roughTime = cutVolume / (roughFeed*roughBitStep*roughBitDepth)  # Time for roughing
            roughCost = roughTime*roughCostRate  # Roughing cost

            # Machining (Finish Pass)
            finishSFM = 400  # Roughing surface feet per minute
            finishFPT = 0.004  # Roughing feed per tooth [in]
            finishCostRate = 175.0/3600.0  # Cost to finish [$/s]
            finishBitDiam = 0.006  # Finish diameter [m]
            finishPasses = 5.0  # Number of surface passes

            finishRPM = 3.82*finishSFM/(39.37*finishBitDiam)  # Roughing RPM
            finishFeed = finishFPT*finishRPM*2.0*0.00042  # Roughing Feed [m/s]

            finishBitStep = 0.8*finishBitDiam  # Rougher step size
            a = width/2.0
            b = depth
            h = (a-b)**2 / (a+b)**2
            p = math.pi*(a+b)*(1.0+3.0*h/(10.0+math.sqrt(4.0-3.0*h)))  # Approximate solution to ellipse perimeter
            cutArea = length*p/2.0  # Amount of material to rough out
            finishTime = cutArea / (finishFeed*finishBitStep) * finishPasses  # Time for roughing
            finishCost = finishTime*finishCostRate  # Roughing cost

            # Total Cost
            cost = materialCost + roughCost + finishCost 
            return cost  # [$]
            
        if (params["Vehicle"].lower().replace('-', '') == "tiltwing"):  # tilt-wing
            fuselageHeight = 1.3  # Guess
            span = params['cruiseOutput_bRef']
            chord = params['cruiseOutput_cRef']
            
            # Wing Tooling
            wingToolCost = list([])
            wingToolCost.append(toolingCost((span-fuselageWidth)/2.0,toc*chord,chord*.2))  # Leading edge
            wingToolCost.append(toolingCost((span-fuselageWidth)/2.0,toc*chord*0.7,chord*.2))  # Aft spar
            wingToolCost.append(toolingCost((span-fuselageWidth)/2.0,chord*0.75,0.02)*2.0)  # Upper/Lower skin
            wingToolCost.append(toolingCost(span,toc*chord,chord*.20))  # Forward spar
            wingToolCost = 2.0*(2.0*sum(wingToolCost[0:3])+wingToolCost[3])  # Total wing tooling cost (matched tooling)
            
            # Winglet Tooling
            wingletToolCost = list([])
            wingletToolCost.append(toolingCost(winglet*span/2.0,toc*chord,chord*.2))  # Leading edge
            wingletToolCost.append(toolingCost(winglet*span/2.0,toc*chord*0.7,chord*.2))  # Aft spar
            wingletToolCost.append(toolingCost(winglet*span/2.0,chord*0.75,0.02)*2.0)  # Upper/Lower skin
            wingletToolCost.append(toolingCost(winglet*span/2.0,toc*chord,chord*.20))  # Forward spar
            wingletToolCost = 4.0*sum(wingletToolCost)  # Total winglet tooling cost (matched tooling)
            
            # Canard Tooling
            canardToolCost = wingToolCost  # Total canard tooling cost
            
            # Fuselage Tooling
            fuselageToolCost = list([])
            fuselageToolCost.append(toolingCost(fuselageLength*.8,fuselageHeight,fuselageWidth/2.0)*2.0)  # Right/Left skin
            fuselageToolCost.append(toolingCost(fuselageLength*.8,fuselageWidth/2.0,fuselageHeight/4.0))  # Keel
            fuselageToolCost.append(toolingCost(fuselageWidth,fuselageHeight,0.02)*2.0)  # Fwd/Aft Bulkhead
            fuselageToolCost.append(toolingCost(fuselageLength*.1,fuselageWidth,fuselageHeight/3.0))  # Nose/Tail cone
            fuselageToolCost = 2.0*sum(fuselageToolCost)  # Total fuselage tooling cost (matched tooling)
            
            # Prop Tooling
            propToolCost = list([])
            propToolCost.append(toolingCost(propRadius,propChord,propChord*toc/2.0)*2.0)  # Skin
            propToolCost.append(toolingCost(propRadius,propChord*toc,propChord/4.0)*2.0)  # Spar tool
            propToolCost = 4.0*sum(propToolCost)  # Total propeller tooling cost (left/right hand) (matched tooling)
            
            # Control Surface (2 tools)
            controlToolCost = list([])
            controlToolCost.append(toolingCost((span-fuselageWidth)/2.0,(1.0-xhinge)*chord,chord*toc/4.0))  # Skin
            controlToolCost.append(toolingCost((span-fuselageWidth)/2.0,(1.0-xhinge)*chord,chord*toc/4.0))  # Skin
            controlToolCost = 8.0*sum(controlToolCost)  # Total wing tooling (matched tooling)
            
            # Total tool cost
            totalToolCost = wingToolCost+canardToolCost+fuselageToolCost+propToolCost+controlToolCost+wingletToolCost
        
        elif (params["Vehicle"].lower().replace('-', '') == "helicopter"):  # helicopter
            fuselageHeight = 1.6  # Guess

            # Fuselage Tooling
            fuselageToolCost = list([])
            fuselageToolCost.append(toolingCost(fuselageLength*.8,fuselageHeight,fuselageWidth/2.0)*2.0)  # Right/Left skin
            fuselageToolCost.append(toolingCost(fuselageLength*.8,fuselageWidth/2.0,fuselageHeight/4.0))  # Keel
            fuselageToolCost.append(toolingCost(fuselageWidth,fuselageHeight,0.02)*2.0)  # Fwd/Aft Bulkhead
            fuselageToolCost.append(toolingCost(fuselageLength*.1,fuselageWidth,fuselageHeight/3.0))  # Nose/Tail cone
            fuselageToolCost = 2.0*sum(fuselageToolCost)  # Total fuselage tooling cost (matched tooling)
            
            # Rotor Tooling
            rotorToolCost = list([])
            rotorToolCost.append(toolingCost(propRadius,propChord,propChord*toc/2.0)*2.0)  # Skin
            rotorToolCost.append(toolingCost(propRadius,propChord*toc,propChord/4.0)*2.0)  # Spar tool
            rotorToolCost = 2.0*sum(rotorToolCost)  # Total rotor tooling cost (matched tooling)
            
            # Tail Rotor Tooling
            tailRotorToolCost = list([])
            tailRotorToolCost.append(toolingCost(propRadius/4.0,propChord/4.0,propChord/4.0*toc/2.0)*2.0)  # Skin
            tailRotorToolCost.append(toolingCost(propRadius/4.0,propChord/4.0*toc,propChord/4.0/4.0)*2.0)  # Spar tool
            tailRotorToolCost = 2.0*sum(tailRotorToolCost)  # Total rotor tooling cost (matched tooling)
            
            # Total tool cost
            totalToolCost = fuselageToolCost+rotorToolCost+tailRotorToolCost
        else:
            pass
            
        unknowns['toolCostPerVehicle'] = totalToolCost / params['partsPerTool']
            