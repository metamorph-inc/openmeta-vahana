# OpenMETA-Vahana
An OpenMETA model for the conceptual design of an autonomous transport aircraft, inspired by the Vahana Project from A^3 by Airbus.

## Background
Project Vahana is an Airbus A^3 project to create a low-cost, single-passenger, electric VTOL aircraft. As part of their design process, A^3 conducted the Vahana Configuration Trade Study to examine two different configurations (an electric helicopter and an electric eight fan tilt-wing) using multidisciplinary design optimization (MDO). 

## Objective
Airbus released the [MATLAB source code](https://github.com/VahanaOpenSource/vahanaTradeStudy) used in their [Vahana Configuration Trade Study](https://vahana.aero/vahana-configuration-trade-study-part-ii-1edcdac8ad93) on GitHub.

Here at MetaMorph, we wanted to see if we could set up the same MDO problem and solve it in OpenMETA.  Our objective was twofold; we setout to replicate the Trade Study in OpenMETA and to improve the accuracy of the study with the addition of a CAD model. 

# Improvements

## CAD Model
The use of a CAD model allows for more accurate calculations of mass values with the given design variables. The model created for this purpose is based on the sketches of the tilt-wing variant that A^3 released in their Trade Study Report. This model is composed within GME and contains a few parametric features. The canards and wings rotation position is an exposed parameter that ranges from cruise position to hover position (0-90 degrees). The design variable rProp is also a parameter that varies the length of the propeller blades. This blade radius changes the length of both flight surfaces as well as the position of the rotors so that there is a small specified distance between each blade tip as specified in the MatLAB code used in the the Trade Study. The use of this model provides a more refined mass calculation based on real geometry, in turn providing more realistic values for mass used to calculate the main design objective, Direct Operating Cost (DOC). 


![Image of Creo model](Vahana_V2.PNG "Image of Creo model")

Figure 1 - Image of Creo Model [CENTER]

## Iterative mass Calculations
In replicating the analysis done, we noticed that there was a very low success rate caused by the vehicles not meeting two of the design constraints:

* The vehicle must contain more energy in the battery than the energy that was required to complete its mission 
* The Vehicle motors must have availale power that is least 1.7 times the maximum power required for hover

While the specific energy of the battery and specific power of the motors to be used were known, the masses of these components were made design varibales. With a known specific energy and specific power, the necessary masses of the battery and rotors resectively 
can be solved for to always satisfy these design constraints. This requires an iterative solving method as the component mass is dependent on the total vehicle mass. Using Euler's method of linear numerical integration, the required mass of the battery and motors can be solved within 0.01% of the theoretical value in 10 iterations for ranges up to ten times larger than the assumed payload of 150 kg. Implementing this iterative mass calculation ensures all vehicles satisfy these constraints, which drastically reduces overhead as    
First, we converted Airbus's MATLAB Code into composable PythonWrapper Components which could then be used as 'building blocks' in the OpenMETA environment.


![cruisePower.m, hoverPower.m, loiterPower.m, simpleMission.m, and reserveMission.m were all turned into seperate PythonWrapper Components](Vahana_PET_Power.PNG)

Figure 2 - PythonWrapper Components for Power and Mission Calculations

Note: In Figure 2, CruisePower has many exposed outputs. One the other hand, HoverPower has only five exposed outputs. When building/modifying a PythonWrapper Component, the user can decide which input/output variables to be exposed.


![PythonWrapper Components for Mass Calculations](Vahana_PET_MassCalcs.PNG)

Figure 3 - PythonWrapper Components for Mass Calculations

Note: Constants Components allow the user to quickly provide constant values to a system. In Figure 3, Constants Components provide WingMass, WireMass, and CanardMass with unique design parameters

![PythonWrapper Components for Cost and Constraint Calculations](Vahana_PET_CostAndConstraints.PNG)

Figure 4 - PythonWrapper Components for Cost and Constraint Calculations

## Parameter Study
After converting the major MATLAB scripts in PythonWrapper Components, we added a Parameter Study Component to explore the available design space. Figure 5 shows the Parameter Study has 7 Design Variables on its left side and 8 Objectives on its right side.


![Parameter Study](Vahana_PET_ParameterStudy.PNG)

Figure 5 - Parameter Study Component




Now we can set the ranges of the design variables in the Parameter Study Component and run the Master Interpreter to generate some data. Let's set the Parameter Study to 1 million samples and run the PET.

Here's a filtered subset of our data in the OpenMETA Visualizer - 397 points to be exact:

![Filtered PET Result in Visualizer](1MilFilteredVisualizerResults.PNG) <- Get a higher res image if possible

Figure 5 - Filtered PET Result in Visualizer


## References
[Vahana Configuration Trade Study Part - 1](https://vahana.aero/vahana-configuration-trade-study-part-i-47729eed1cdf)

[Vahana Configuration Trade Study Part - 2](https://vahana.aero/vahana-configuration-trade-study-part-ii-1edcdac8ad93)

[MATLAB Code](https://github.com/VahanaOpenSource/vahanaTradeStudy)
