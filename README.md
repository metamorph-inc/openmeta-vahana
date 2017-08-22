# OpenMETA-Vahana

[Summary](#summary)


## Summary
_An OpenMETA model for the conceptual design of an autonomous transport aircraft_

Inspired by the Vahana Project from A³ by Airbus, we built OpenMETA models of the Vahana Tilt-Wing Multirotor aircraft using A³'s publicly released source code as a template. 

A parametric CAD model of the Vahana was also built within OpenMETA with the goal of using CAD analysis to improve the accuracy of future studies. The most recent draft of this CAD model is shown below with its rotors angled to transition between the hover and cruise modes.

**Vahana CAD model:**
  
![Image of 45 deg rotation](images/Vahana_V2_2.PNG "Image of Vahana transitioning from hover to cruise")

The OpenMETA models were used to perform similar DOC analyses to those in the Vahana Configuration Trade Study as well as improve on the original study. 

**OpenMETA 'Optimizer' Results and Vahana Trade Study Results for Tilt-Wing Configuration at Range of 100 km:**

|                        | DOC ($) | DOC (km/$) | rProp (m) | cruiseSpeed (m/s) | batteryMass (kg) | motorMass (kg) | mtom (kg) |
|:----------------------:|:-------:|:----------:|:---------:|:-----------------:|:----------------:|:--------------:|:---------:|
| OpenMETA |   116.3  |    1.16    |    1.10   |        45.5       |        413       |      66.7      |    968    |
|   Vahana Study   |  116.3  |    1.16    |    1.10   |        45.5       |        413       |      66.7      |    968    |

**OpenMETA PET model results:**

DOC vs. Range for Tilt Wing and Helicopter Configurations
![tilt wing and helicopter doc vs. range comparison](images/openmeta-vahana-doc-vs-range.png)

DOC vs. Range for Tilt Wing Configuration with and without Fuel Weight Constraint
![tilt wing fuel_constraint doc vs. range comparison](images/openmeta-vahana-tilt-wing-fuel-weight-constraint.png)

## Airbus Vahana Configuration Trade Study
Project Vahana is an Airbus A³ campaign to create a low-cost, single-passenger, electric VTOL aircraft. As part of their design process, Airbus conducted the Vahana Configuration Trade Study to better examine 2 different configurations (an electric helicopter and an electric eight fan tilt-wing) using multidisciplinary design optimization (MDO). 

The A³ team set up a MDO sizing problem in which they compared an electric helicopter model and an electric eight fan tilt-wing model over a range of operating distances (10 km to 200 km in 10 km steps). At each distance, both vehicle models were optimized seperately for Direct Operating Cost (DOC) by varying 5 design variables: Cruise Speed, Rotor Radius, Battery Mass, and Takeoff Mass. The A³ team also provided the optimizer with 3 constraint equations (4 if the vehicle was a helicopter) that defined certain design requirements - E.g. The vehicle's effective energy capacity (Battery Mass * Battery Energy Density * Battery Discharge Depth) had to be greater than the amount of energy required to execute a reserve ("worst case") mission. 

As a result of their Sizing Trade Study, the Vahana team concluded that an eight-fan, tilt-wing configuration would best meet their broad design requirements for a low-cost, single-passenger, electric VTOL aircraft.

## OpenMETA Vahana Configuration Trade Study 
Here at MetaMorph, we set out to first replicate the Vahana Configuration Trade Study's results using the OpenMETA toolset. Since OpenMETA is designed for Multidisciplinary Design Analysis and Optimization, we thought that it would be interesting to see if we could reproduce the A³ team's results using the OpenMETA toolset.

To read about the OpenMETA Vahana Configuration Trade Study, check out our blog post.

##

## Improvements to Vahana Configuration Trade Study / Future Plans
Since we were able to produce similar trends to those in the Vahana Configuration Trade Study using OpenMETA, we wanted to explore ways in which to improve on the Trade Study's results. Outside of exercising the OpenMETA toolset, there was little reason to recreate the Vahana Configuration Trade Study - it had already served its purpose and Aribus had already progressed to the next stage in the design process. Therefore, our next goal was to see how we could improve the Trade Study's model and provide more detailed anaylsis for design purposes.

### Meta-Link CAD Model
A CAD model can provide a more accurate representation of a vehicle's geometry, mass, and mass distribution. In creating a CREO model of the Tilt-Wing Configuration, we hoped to provide a more model that could eventually be used to calculate mass, center of gravity, and production costs.

The model (shown below) is based on the sketches of the Tilt-Wing configuration that A³ released in the Vahana Trade Study Report. This model is composed within GME and contains parametric features that align with the design requirements outlined within the Vahana Trade Study's MATLAB code. The rotational orientation of the wings and canards can be varied between the cruise and hover positions (or 0-90 degrees).

**Vahana in hover mode:**
![Image of 90 deg rotation](images/Vahana_V2_90Deg.PNG "Image of Vahana in hover configuration")


**Vahana transitioning from hover mode to cruise mode:**
![Image of 45 deg rotation](images/Vahana_V2_2.PNG "Image of Vahana transitioning from hover to cruise")


**Vahana in cruise mode:**
![Image of 0 deg rotation](images/Vahana_V2_0Deg.PNG "Image of Vahana in cruise configuration")

The model assembly is located at `RootFolder/ComponentAssemblies/Vahana2` within openmeta-vahana.xme. By changing the values of the `Canard_Rotation` and `Wing_Rotation` parameters, a user can be change the orientation for a specific analysis. The `rProp` parameter allows the user to change vary the length of the propeller blades. Changing the propeller blade radius also changes the span of both flight surfaces as well as the positions of the rotors in order to maintain an appropriate spacing between the neighboring rotors.

### xFOIL Integration
Work in progress...

### Iterative Mass Calculations
When running the PET 'Parameter Study' we noticed that the low success rate of less than 0.04% was primarily caused by designs failing the first two design constraints:

* The vehicle battery must contain more energy than the energy required to complete its mission 
* The vehicle motors must the capacity to provide at least 1.7 times the maximum power required for hover mode

The Vahana Trade Study set battery mass and motor mass as design variables while using assumed values for battery specific energy and motor specific power. Since 95% of all 'Parameter Study' PET runs failed as a result of the first two constraints, we looked into making battery mass and motor mass dependent variables which could be solved using an iterative method and the other design variables.

Using Euler's linear method of numerical integration (method shown [here](https://docs.google.com/spreadsheets/d/170VYNoF4OTg8ZG605DoPC1EO5k4rxNIF8a00Ac6IGiI/edit?usp=sharing)) the required battery mass and motor mass can be solved for within 0.01% of the theoretical value in 10 interation for ranges up to ten times larger than the assumed payload of 150 kg. A future model may implement these mass calculations in order to more intelligently explore the design space

<!-- Image isn't in images/ ...
<p align="center">Image of Mass Convergence at 1500 kg</p>

![Image of mass convergence](images/mass_convergence.PNG)
-->

## References
[A³ Vahana Configuration Trade Study Part - 1](https://vahana.aero/vahana-configuration-trade-study-part-i-47729eed1cdf)  
[A³ Vahana Configuration Trade Study Part - 2](https://vahana.aero/vahana-configuration-trade-study-part-ii-1edcdac8ad93)  
[A³ MATLAB Code](https://github.com/VahanaOpenSource/vahanaTradeStudy)
