# CFDC Dataset: Six-Field Gradio Inputs for Twenty Classic Control Problems

> This document is adapted from `control_problems.md` in the same directory. Each problem follows the six input fields of the Gradio natural-language interface and can be copied field by field.
>
> All safety bounds are conservative dataset defaults for software simulation and safe small-perturbation experiments. They are neither hardware ratings from the book nor safety-certified limits for physical equipment.

## How to Use

Each control problem provides the following six fields in order:

1. Control Problem Description: eight natural-language sentences that provide evidence for the eight-part structural diagnosis;
2. Observable Outputs: copy into the Observable Outputs input;
3. Actuators: copy into the Actuators input;
4. Safety Bounds: preserve the `name=value` format on each line;
5. Forbidden Actions: enter one action per line so commas inside a sentence remain intact;
6. Dominant Time Scale: enter a positive value in seconds.

Do not copy field headings into the inputs. Control problem descriptions contain no formulas or mathematical relations.

---

## 1. Household Thermostat: On-Off Temperature Control with Hysteresis

### Control Problem Description

With a fixed heater command, the room temperature is self-regulating and settles to a finite equilibrium instead of diverging. A small increase in heater command makes the measured temperature begin moving upward, with no inverse response. The first temperature change begins immediately in the software model, although the thermal response itself is slow. Heater power changes the rate of temperature motion through one dominant thermal storage effect. Room temperature is recorded and the only actuator is the binary furnace or heater command. The thermal plant is approximately linear in the declared range, while the thermostat contributes a static hysteresis and on-off nonlinearity. This is a single-input single-output loop with no cross-channel coupling. Thermal resistance, thermal capacity, outside temperature, and heater effectiveness vary moderately across weather and occupancy conditions.

### Observable Outputs

room temperature

### Actuators

binary furnace command

### Safety Bounds

temperature_min_f=50.0
temperature_max_f=70.0
max_heater_command=1.0
max_setpoint_step_f=10.0
min_switch_interval_s=60.0

### Forbidden Actions

deploy commands to physical heating hardware
command heating above the configured temperature maximum
switch faster than the configured minimum interval

### Dominant Time Scale (Seconds)

1800.0

---

## 2. Automobile Cruise Control: Open- and Closed-Loop Steady-State Comparison

### Control Problem Description

Because aerodynamic and rolling drag oppose motion, vehicle speed is self-regulating and settles after a small fixed throttle change. A positive throttle-angle change initially increases speed, while a positive uphill grade decreases it, so the commanded channel has no inverse response. The speed measurement begins responding immediately after the command changes in the software model. Throttle angle affects speed through one dominant vehicle lag. Vehicle speed and road grade are recorded, and throttle angle is the single actuator. The local steady-state map is approximately linear near the nominal cruising condition, although real drag becomes nonlinear farther from that operating point. This is a single-input single-output speed loop with road grade entering as an additive disturbance. Plant gain and drag vary moderately with vehicle mass, wind, and grade.

### Observable Outputs

vehicle speed, road grade

### Actuators

throttle angle

### Safety Bounds

speed_min_mph=50.0
speed_max_mph=70.0
max_throttle_angle_deg=10.0
max_grade_percent=2.0
max_abs_speed_error_mph=10.0

### Forbidden Actions

deploy commands to a physical vehicle
exceed the configured throttle-angle bound
continue a trial after the speed-error bound is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 3. Automobile Cruise Control: First-Order Dynamics

### Control Problem Description

The viscous-drag vehicle model is open-loop stable and its speed settles after a constant drive force is applied. A small positive longitudinal force makes speed increase immediately in the expected direction. The speed begins changing immediately after force is applied in the software model. Drive force changes acceleration and reaches speed through one dominant lag opposed by drag. Vehicle speed is measured and longitudinal drive force is the only actuator. The declared model is linear, while unmodeled aerodynamic drag remains weak inside the bounded test range. This is a single-input single-output speed process. Vehicle mass and effective drag are known only approximately and create moderate gain and time-scale uncertainty.

### Observable Outputs

vehicle speed

### Actuators

longitudinal drive force

### Safety Bounds

max_abs_force_n=500.0
max_speed_mps=12.0
max_test_duration_s=100.0

### Forbidden Actions

deploy commands to a physical vehicle
apply a force larger than the configured limit
continue after the speed or duration boundary is reached

### Dominant Time Scale (Seconds)

20.0

---

## 4. Active Quarter-Car Suspension

### Control Problem Description

The passive two-mass suspension is open-loop stable and a small release produces an oscillation that decays because of the damper. A positive active-suspension force moves the body initially in the commanded direction, with the wheel reacting in the opposite direction and no intended inverse response at the body output. Body and wheel motion begins immediately after force is applied in the software model. Force reaches body displacement through acceleration and two coupled storage modes. Body displacement, wheel displacement, and both velocities are recorded, and an active force between body and wheel is available as the actuator. The spring-damper model is approximately linear only while suspension travel remains small and tire contact is maintained. One actuator moves two linked coordinates, creating an underactuated internal coupling even when the controlled body output is treated as one loop. Body mass, tire stiffness, suspension stiffness, damping, and road profile have moderate uncertainty.

### Observable Outputs

car-body displacement, wheel displacement, car-body velocity, wheel velocity

### Actuators

active suspension force

### Safety Bounds

max_road_displacement_m=0.05
max_body_displacement_m=0.1
max_suspension_travel_m=0.12
max_abs_actuator_force_n=500.0

### Forbidden Actions

deploy commands to a physical suspension
allow loss of simulated tire contact
exceed suspension travel or actuator-force limits

### Dominant Time Scale (Seconds)

0.5

---

## 5. Single-Axis Attitude of a Rigid Satellite

### Control Problem Description

Without feedback, the rigid satellite attitude is marginal because a torque pulse leaves a nonzero angular rate and the angle keeps drifting. A small positive control torque initially increases angular rate and attitude angle in the expected direction. Angular motion begins immediately after torque is applied in the software model. Torque changes angular acceleration and reaches attitude through two successive accumulations. Attitude angle and angular rate are recorded, and a single reaction-jet or equivalent body torque is available. The one-axis rigid-body model is linear for small motion and fixed inertia. This is a single-input single-output attitude loop with disturbance torque entering additively. Inertia, jet effectiveness, and external disturbance torque create moderate uncertainty.

### Observable Outputs

attitude angle, angular rate

### Actuators

body control torque

### Safety Bounds

max_abs_angle_rad=0.1
max_abs_rate_rad_s=0.05
max_abs_torque_nm=0.01
max_test_duration_s=20.0

### Forbidden Actions

deploy commands to physical spacecraft hardware
apply unbounded constant torque
continue after angle, rate, torque, or duration limits are reached

### Dominant Time Scale (Seconds)

5.0

---

## 6. Flexible Satellite: Collocated and Noncollocated Sensors

### Control Problem Description

Without feedback, the flexible satellite contains a marginal rigid-body drift and a lightly damped resonant mode between the main body and instrument package. A small positive body torque initially moves both measured angles in the expected direction, although the remote instrument angle can ring strongly. Main-body motion begins immediately after torque is applied in the software model. The non-collocated path passes through body acceleration and a flexible mode before the remote angle responds. Main-body angle, instrument-package angle, their angular rates, and relative twist are recorded, while body torque is the single actuator. The two-inertia spring-damper behavior is linear in the declared small-angle range, but unmodeled flexible modes become important outside the selected bandwidth. The actuator and remote sensor form a cascaded flexible coupling rather than an independent rigid-body loop. Flexible stiffness, damping, modal frequency, and sensor placement create large uncertainty near resonance.

### Observable Outputs

main-body angle, instrument-package angle, main-body angular rate, instrument-package angular rate, relative twist

### Actuators

main-body control torque

### Safety Bounds

max_abs_body_angle_rad=0.08
max_abs_payload_angle_rad=0.08
max_relative_twist_rad=0.02
max_abs_torque_nm=0.01
max_test_duration_s=20.0

### Forbidden Actions

deploy commands to physical spacecraft hardware
excite the flexible mode with an unbounded pulse
continue after the relative-twist boundary is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 7. Quadrotor Attitude Control Allocation

### Control Problem Description

Near hover, open-loop roll, pitch, and yaw angles are non-restoring and small torque errors can produce continuing angular drift, so the equilibrium is safety-critical. A positive virtual roll, pitch, or yaw torque initially accelerates the corresponding angle in the expected direction when the motor allocation signs are correct. Angular acceleration begins immediately after virtual torque is applied in the software model. Each virtual torque changes angular acceleration before attitude changes, while motor allocation adds an upstream mixing stage. Roll, pitch, yaw, and their rates are recorded, and the available actuators are virtual roll torque, pitch torque, and yaw torque generated from four motor perturbations. The small-angle behavior is weakly nonlinear inside the tilt boundary, but large attitude motion introduces strong trigonometric and inertial coupling. The three virtual channels are weakly coupled near hover but form a cascaded multivariable system when mapped back to individual motors. Inertia, payload, motor gain, aerodynamic damping, and allocation mismatch create large uncertainty.

### Observable Outputs

roll angle, pitch angle, yaw angle, roll rate, pitch rate, yaw rate

### Actuators

virtual roll torque, virtual pitch torque, virtual yaw torque

### Safety Bounds

max_tilt_rad=0.26
max_abs_yaw_rad=0.35
max_abs_angular_rate_rad_s=1.0
max_abs_axis_torque_nm=1.0
max_normalized_motor_perturbation=0.25

### Forbidden Actions

deploy commands to a physical quadrotor
disable motor saturation or tilt limits
continue after allocation produces unexpected cross-axis motion

### Dominant Time Scale (Seconds)

0.5

---

## 8. Downward Pendulum: Small-Angle Oscillation

### Control Problem Description

With no damping, the downward rotational oscillator is marginal because it keeps oscillating after a small release instead of settling or diverging. A small positive pivot torque initially accelerates the measured angle in the positive direction. Angular acceleration begins immediately after pivot torque is applied in the software model. Pivot torque changes angular acceleration before the angle changes, while gravity provides the restoring motion. Angle and angular rate are recorded, and pivot torque is the only actuator. The restoring force is approximately linear inside the small-angle boundary but becomes strongly amplitude dependent for larger excursions. This is a single-input single-output rotational loop. Mass, length, friction, and torque calibration create moderate uncertainty even though nominal gravity is known.

### Observable Outputs

pendulum angle, pendulum angular rate

### Actuators

pivot torque

### Safety Bounds

max_abs_angle_rad=0.2
max_abs_angular_rate_rad_s=1.0
max_abs_torque_nm=1.0
max_test_duration_s=10.0

### Forbidden Actions

deploy commands to a physical pendulum
command a large-angle swing-up
continue after the small-angle boundary is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 9. Cart-Pole: Underactuated Upright Stabilization

### Control Problem Description

A rod on a cart falls away from the upright equilibrium without feedback, so the target is open-loop unstable and safety-critical. A small horizontal cart force may initially move cart position before correcting rod angle, creating unfavorable initial-motion risk. Cart motion begins immediately after horizontal force is applied in the software model. One force must move the cart and then the unactuated rod through coupled acceleration. Cart position, rod angle, and both rates are recorded, while horizontal cart force is the only actuator. Large-angle swing-up and upright capture require strong dynamic nonlinearity, even though behavior near upright can be locally approximated. The system is underactuated because one actuator must control two linked coordinates through natural dynamics and energy exchange. Cart mass, rod mass, inertia, friction, and force gain are not assumed exact, so uncertainty is large.

### Observable Outputs

cart position, rod angle, cart velocity, rod angular rate

### Actuators

cart motor force

### Safety Bounds

force_limit_n=10.0
rail_limit_m=2.4
max_upright_angle_error_rad=0.35
max_abs_rod_rate_rad_s=2.5
max_test_duration_s=5.0

### Forbidden Actions

deploy commands to a physical cart-pole
disable rail, force, or angle limits
release a controller without an upright capture and rollback condition

### Dominant Time Scale (Seconds)

0.5

---

## 10. Bridged-T RC Network

### Control Problem Description

With positive resistances and capacitances, the passive bridge network is open-loop stable and its output settles after a bounded voltage change. A small positive input voltage moves the output initially in the expected direction for the declared positive component values. The electrical response begins immediately after input voltage changes in the software model. The input-output behavior has a direct response together with two capacitor storage effects. Input voltage, output voltage, and both capacitor-related node voltages are recorded, while the input voltage source is the actuator. The ideal resistor-capacitor behavior is linear until component voltage or current limits are approached. This is a single-input single-output network with one internal bridge path. Component tolerances and parasitic loading are small to moderate sources of uncertainty.

### Observable Outputs

input voltage, output voltage, internal node voltage, bridge capacitor voltage

### Actuators

input voltage source

### Safety Bounds

max_abs_input_voltage_v=5.0
max_abs_output_voltage_v=5.0
max_abs_capacitor_voltage_v=5.0
max_abs_branch_current_a=0.05
max_test_duration_s=1.0

### Forbidden Actions

connect the prompt to a physical circuit without rated components
exceed capacitor-voltage or branch-current limits
apply an unbounded ideal voltage step

### Dominant Time Scale (Seconds)

0.1

---

## 11. Current-Driven RLC Network

### Control Problem Description

Positive resistance dissipates stored electrical energy, so the inductor-capacitor mode oscillates and decays while the second capacitor voltage settles. A small positive source-current change initially moves the measured capacitor voltages in the expected direction. The electrical response begins immediately after source current changes in the software model. Source current reaches the recorded states through one or more electrical storage elements, with a dominant oscillatory mode. Inductor current and both capacitor voltages are recorded, and the source current is the only actuator. The ideal resistor-inductor-capacitor behavior is linear inside voltage and current bounds. This is treated as one input with several diagnostic state measurements rather than independently actuated multivariable control. Resistance, inductance, capacitance, and sensor loading have moderate uncertainty.

### Observable Outputs

inductor current, first capacitor voltage, second capacitor voltage

### Actuators

source current

### Safety Bounds

max_abs_source_current_a=1.0
max_abs_inductor_current_a=1.0
max_abs_node_voltage_v=10.0
max_test_duration_s=2.0

### Forbidden Actions

connect the prompt to a physical circuit without rated components
exceed current or node-voltage limits
start with unbounded stored energy

### Dominant Time Scale (Seconds)

0.2

---

## 12. Operational-Amplifier Summing Circuit

### Control Problem Description

Inside the unsaturated ideal operating range, the op-amp summer is statically stable and its output settles immediately to a finite weighted sum. A positive change on either inverting input moves the output immediately in the known negative direction, so the sign is known rather than ambiguous. The algebraic output responds immediately after either input changes in the software model. Both input voltages affect output without a dynamic storage stage. Output voltage is recorded, and the two input voltage channels are independently commanded actuators. The ideal weighted sum is linear, while rail saturation and slew limits are static or rate nonlinearities outside the declared region. Two inputs share one output through known resistor weights, producing weak multivariable interaction rather than hidden cross-coupling. Resistor tolerances, offset voltage, finite gain, and rail limits create moderate uncertainty.

### Observable Outputs

op-amp output voltage

### Actuators

first input voltage, second input voltage

### Safety Bounds

max_abs_input_voltage_v=5.0
max_abs_output_voltage_v=10.0
max_abs_output_current_a=0.02

### Forbidden Actions

connect the prompt to a physical op-amp without rated supply rails
command output beyond the configured voltage rails
treat saturation data as linear-response evidence

### Dominant Time Scale (Seconds)

0.01

---

## 13. Operational-Amplifier Integrator

### Control Problem Description

The ideal op-amp integrator is marginal because a nonzero constant input makes output voltage drift until a rail is reached. A small positive input causes output to ramp in the known negative direction because the circuit is inverting. The output ramp begins immediately after input voltage changes in the software model. Input voltage reaches output through one accumulation of the input history. Output voltage and capacitor voltage are recorded, and input voltage is the only actuator. The integration behavior is linear inside the rails, while output saturation and windup are static nonlinear constraints. This is a single-input single-output circuit. Resistance, capacitance, bias, leakage, and rail limits create moderate uncertainty in integration gain and drift.

### Observable Outputs

integrator output voltage, feedback capacitor voltage

### Actuators

integrator input voltage

### Safety Bounds

max_abs_input_voltage_v=1.0
max_abs_output_voltage_v=5.0
max_abs_capacitor_voltage_v=5.0
max_integration_duration_s=5.0

### Forbidden Actions

connect the prompt to a physical op-amp without rated supply rails
hold a nonzero input after the output reaches its bound
use saturated data to estimate the linear integration gain

### Dominant Time Scale (Seconds)

1.0

---

## 14. Electromechanical Loudspeaker Coupling

### Control Problem Description

In the simplified behavior without suspension stiffness, a voltage pulse excites damped electrical and mechanical modes but a sustained force can leave cone displacement drifting, so the displacement channel is marginal. A small positive coil voltage produces current, force, and cone motion in the expected polarity. Coil current begins changing immediately after voltage is applied in the software model. Voltage passes through coil dynamics, current-to-force conversion, mass acceleration, and displacement accumulation before the measured position changes. Cone displacement, cone velocity, coil current, and applied voltage are recorded, and coil voltage is the actuator. The electromagnetic behavior is approximately linear inside current and travel limits, while suspension, saturation, and acoustic loading add nonlinear effects outside them. Electrical and mechanical subsystems form a cascaded coupling through force and back electromotive voltage. Effective mass, damping, inductance, resistance, magnetic field, and acoustic load create moderate uncertainty.

### Observable Outputs

cone displacement, cone velocity, voice-coil current, applied coil voltage

### Actuators

voice-coil voltage

### Safety Bounds

max_abs_voltage_v=5.0
max_abs_current_a=1.0
max_abs_displacement_m=0.005
max_abs_velocity_m_s=0.2
max_test_duration_s=1.0

### Forbidden Actions

drive a physical loudspeaker from this dataset prompt
exceed current or cone-travel limits
inject sustained direct current after displacement drift is detected

### Dominant Time Scale (Seconds)

0.05

---

## 15. DC Motor Position and Speed

### Control Problem Description

Motor speed is self-regulating because of friction and back electromotive voltage, but shaft position is marginal and keeps moving after a command leaves nonzero speed. A small positive armature voltage initially produces positive current, torque, speed, and angle. Armature current begins changing immediately after voltage is applied in the software model. Voltage reaches speed through electrical and mechanical lags and reaches position through one additional accumulation. Shaft position, shaft speed, and armature current are recorded, and armature voltage is the only actuator. The behavior is approximately linear before current saturation, voltage saturation, friction deadzone, or mechanical end stops become active. This is a single-input single-output drive with internal electrical-to-mechanical cascading. Inertia, friction, resistance, inductance, torque constant, load torque, and supply voltage create moderate uncertainty.

### Observable Outputs

shaft position, shaft speed, armature current

### Actuators

armature voltage

### Safety Bounds

max_abs_voltage_v=12.0
max_abs_current_a=2.0
max_abs_speed_rad_s=100.0
max_abs_position_rad=3.14
max_test_duration_s=5.0

### Forbidden Actions

deploy commands to a physical motor
disable voltage or current saturation
continue after speed or mechanical-position boundaries are reached

### Dominant Time Scale (Seconds)

0.5

---

## 16. Gear Train and Reflected Inertia

### Control Problem Description

With viscous damping the output speed decays after torque removal, but output position behaves like an integrator and continues moving if residual speed remains. A small positive motor torque moves the output gear angle in the expected sign after accounting for the gear-direction convention. Gear acceleration begins immediately after motor torque is applied in the software model. Motor torque changes equivalent-inertia acceleration before output angle changes. Output angle, output speed, and motor-side speed are recorded, and motor torque is the single actuator. The ideal rigid-gear behavior is linear inside torque and speed limits, with backlash and tooth compliance explicitly excluded from the first dataset model. This is a single-input single-output drive with deterministic kinematic scaling rather than independent multivariable coupling. Gear ratio is known, while reflected inertia, damping, efficiency, and unmodeled backlash create moderate uncertainty.

### Observable Outputs

output gear angle, output gear speed, motor-side speed

### Actuators

motor torque

### Safety Bounds

max_abs_motor_torque_nm=2.0
max_abs_output_angle_rad=1.57
max_abs_output_speed_rad_s=10.0
max_test_duration_s=5.0

### Forbidden Actions

deploy commands to a physical gear train
reverse torque at a rate that would require an unmodeled backlash impact
continue after torque, speed, or angle limits are reached

### Dominant Time Scale (Seconds)

0.5

---

## 17. Two-Thermal-Mass Temperature Process

### Control Problem Description

The two-mass thermal process is open-loop stable and both temperature deviations settle after a bounded heat-input change. A positive heat input first raises the driven mass and then raises the second mass in the expected direction. The driven mass begins warming immediately after heat input changes in the software model. Heat must pass through two thermal storage stages before the second temperature responds. Both mass temperatures are recorded, and heat flow into the first mass is the single actuator. The heat-balance behavior is linear around a fixed environment while radiation and property changes are neglected. The measured second mass is coupled to the actuator through the first thermal mass, forming a cascaded single-actuator process. Thermal capacities, contact conductance, environmental losses, and sensor calibration create moderate uncertainty.

### Observable Outputs

thermal mass one temperature, thermal mass two temperature

### Actuators

heat flow into thermal mass one

### Safety Bounds

temperature_min_c=0.0
temperature_max_c=100.0
max_abs_heat_input_w=500.0
max_inter_mass_temperature_difference_c=20.0
max_test_duration_s=600.0

### Forbidden Actions

deploy commands to physical thermal hardware
exceed either temperature or inter-mass temperature-difference bound
apply an unbounded heat step

### Dominant Time Scale (Seconds)

100.0

---

## 18. Heat Exchanger with Measurement Delay

### Control Problem Description

At a declared safe operating point, the steam-water heat exchanger is self-regulating and its temperatures settle after a small valve change. A small increase in steam-valve opening raises steam and water outlet temperatures in the expected direction. The downstream water-temperature sensor has a known significant transport delay before measured temperature begins moving. Valve area affects steam energy and then water energy through two storage stages plus the delay. Steam temperature, water outlet temperature, delayed measured temperature, and valve opening are recorded, and steam-valve area is the actuator. The interaction between valve flow and steam temperature makes gain and time scale depend strongly on operating point, so only local approximation is valid. Steam and water thermal states form a cascaded coupling even though there is one manipulated valve. Heat-transfer resistance, flow rates, inlet temperatures, sensor delay, and operating point create large uncertainty.

### Observable Outputs

steam temperature, water outlet temperature, delayed measured water temperature, steam valve opening

### Actuators

steam inlet valve area

### Safety Bounds

max_steam_temperature_c=200.0
max_water_outlet_temperature_c=90.0
max_normalized_valve_opening=1.0
max_valve_step=0.1
max_test_duration_s=300.0

### Forbidden Actions

deploy commands to a physical heat exchanger
test outside the declared safe operating point
increase bandwidth or valve step while the transport delay is unmodeled

### Dominant Time Scale (Seconds)

30.0

---

## 19. Tank Level with Square-Root Outflow

### Control Problem Description

Around a positive equilibrium inflow, the tank level is self-regulating because outflow increases with level and the level settles after a small inlet-flow change. A positive inlet-flow perturbation initially raises level in the expected direction. The level begins changing immediately after inlet flow changes in the software model. Inlet flow changes the rate of level motion through one dominant storage effect. Tank level and inlet mass flow are recorded, and the inlet valve or pump flow command is the single actuator. Square-root outflow makes gain and time scale vary with operating point, so the behavior is only locally linear inside the declared level range. This is a single-input single-output level process. Tank area, fluid density, restriction coefficient, nominal level, and pump gain create large uncertainty across operating points.

### Observable Outputs

tank level, inlet mass flow

### Actuators

inlet flow command

### Safety Bounds

level_min_m=0.1
level_max_m=1.0
max_inlet_mass_flow_kg_s=1.0
max_inlet_flow_step_kg_s=0.1
max_test_duration_s=300.0

### Forbidden Actions

deploy commands to a physical tank
drain below the minimum level or exceed the overflow limit
reuse one local controller across undeclared operating points

### Dominant Time Scale (Seconds)

20.0

---

## 20. Hydraulic Control-Surface Actuator

### Control Problem Description

Under the constant-velocity local approximation, control-surface angle behaves like an integrator and keeps moving while valve displacement is held away from neutral. A small positive spool displacement produces pressure difference and angle motion in the expected direction while the pressure margin remains positive. Chamber pressure begins changing immediately after spool motion in the software model, although faster pressure effects may be unmodeled. Spool motion reaches angle through orifice flow, piston motion, linkage geometry, and accumulated motion. Surface angle, angular rate, chamber pressures, piston position, and spool displacement are recorded, and spool displacement is the single actuator. Square-root flow, linkage geometry, pressure saturation, and load-dependent gain create strong operating point dependent nonlinearity. The pressure, piston, linkage, and aerodynamic-load stages form a cascaded single-actuator process. Supply pressure, return pressure, fluid density, valve resistance, leakage, inertia, and aerodynamic load create large uncertainty.

### Observable Outputs

control-surface angle, control-surface angular rate, first chamber pressure, second chamber pressure, piston position, spool displacement

### Actuators

valve spool displacement

### Safety Bounds

max_abs_spool_displacement_m=0.002
max_abs_surface_angle_rad=0.2
max_abs_surface_rate_rad_s=0.5
max_pressure_difference_pa=5000000.0
max_abs_rod_load_n=1000.0
max_test_duration_s=2.0

### Forbidden Actions

deploy commands to a physical hydraulic actuator
command a state with nonpositive pressure margin
continue after pressure, spool, angle, rate, or load limits are reached

### Dominant Time Scale (Seconds)

0.2

---

## Usage Constraints

1. The six fields are intended only for Stage Zero structural diagnosis, software-simulation routing, and safe small-perturbation experiment planning.
2. Forbidden actions primarily constrain automatic experiment planning; they do not replace hardware interlocks, emergency stops, or independent safety controllers on physical equipment.
3. Before connecting real equipment, numeric safety bounds must be revalidated against ratings, sensor ranges, actuator saturation, mechanical limits, and a formal risk assessment.
4. Numerical controller values must not be synthesized directly from the description; diagnosis, feature extraction, simulation validation, and the controller release gate remain required.
5. If any safety bound or forbidden action is triggered, the experiment must stop and roll back, and out-of-bound data must not be treated as normal identification data.
