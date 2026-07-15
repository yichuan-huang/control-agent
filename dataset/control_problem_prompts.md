# CFDC Dataset: Six-Field Inputs for Two Hundred Classic Control Problems

> Each entry matches the global identifier in control_problems.md. Safety limits and dominant time scales are conservative normalized scheduling defaults for software simulation, not textbook hardware ratings or measured textbook parameters. For analysis-only examples with no controller, the Actuators field records the prescribed excitation or test input.

Every description contains exactly eight formula-free diagnostic sentences in the order stability, sign, delay, dynamic order, sensing and actuation, nonlinearity, coupling, and uncertainty.

---

## 1. Household thermostat with hysteresis

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are room temperature, heater state, and the available actuation is binary heater command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

room temperature, heater state

### Actuators

binary heater command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 2. Automobile cruise control, open versus closed loop

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are vehicle speed, road grade, and the available actuation is throttle angle. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

vehicle speed, road grade

### Actuators

throttle angle

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 3. Manual automobile steering

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are heading angle, lane error, and the available actuation is steering wheel angle. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

heading angle, lane error

### Actuators

steering wheel angle

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 4. Drebbel incubator temperature regulator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are incubator temperature, and the available actuation is air or fuel valve position. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

incubator temperature

### Actuators

air or fuel valve position

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 5. Float-valve water-level regulator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are tank liquid level, and the available actuation is inlet valve opening. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

tank liquid level

### Actuators

inlet valve opening

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 6. Watt fly-ball steam-engine governor

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are engine shaft speed, governor displacement, and the available actuation is steam valve opening. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

engine shaft speed, governor displacement

### Actuators

steam valve opening

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 7. Paper-machine stock-consistency control

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are stock consistency, and the available actuation is dilution water valve. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

stock consistency

### Actuators

dilution water valve

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 8. Paper-machine moisture control

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are paper moisture, and the available actuation is dryer steam command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

paper moisture

### Actuators

dryer steam command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 9. Human blood-pressure regulation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are arterial pressure, heart rate, and the available actuation is neural cardiac and vascular commands. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

arterial pressure, heart rate

### Actuators

neural cardiac and vascular commands

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 10. Human blood-glucose regulation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are blood glucose, insulin level, and the available actuation is endogenous insulin and counterregulation. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

blood glucose, insulin level

### Actuators

endogenous insulin and counterregulation

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 11. Human heart-rate regulation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are heart rate, and the available actuation is sympathetic and parasympathetic drive. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

heart rate

### Actuators

sympathetic and parasympathetic drive

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 12. Eye-pointing-angle control

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are eye angle, retinal error, and the available actuation is ocular muscle torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

eye angle, retinal error

### Actuators

ocular muscle torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 13. Pupil-diameter light regulation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pupil diameter, retinal illumination, and the available actuation is iris muscle activation. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pupil diameter, retinal illumination

### Actuators

iris muscle activation

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 14. Elevator position control with coarse/fine sensing and cable stretch

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are car position, landing error, cable stretch, and the available actuation is hoist motor torque and brake. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

car position, landing error, cable stretch

### Actuators

hoist motor torque and brake

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 15. Electrical temperature sensing and actuation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are temperature, sensor voltage, and the available actuation is electrical heater voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

temperature, sensor voltage

### Actuators

electrical heater voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 16. Electrical pressure sensing and actuation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pressure, sensor voltage, and the available actuation is valve command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pressure, sensor voltage

### Actuators

valve command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 17. Electrical liquid-level sensing and actuation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are liquid level, transmitter signal, and the available actuation is pump speed or valve position. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

liquid level, transmitter signal

### Actuators

pump speed or valve position

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 18. Electrical pipe-flow sensing and actuation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pipe flow rate, and the available actuation is control valve position. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pipe flow rate

### Actuators

control valve position

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 19. HPA-axis stress-hormone negative feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are hormone concentrations, and the available actuation is endogenous secretion rates. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

hormone concentrations

### Actuators

endogenous secretion rates

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 20. Oxytocin-mediated childbirth positive feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are oxytocin level, contraction intensity, and the available actuation is endogenous oxytocin release. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

oxytocin level, contraction intensity

### Actuators

endogenous oxytocin release

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

10.0

---

## 21. First-order automobile cruise dynamics

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are vehicle speed, and the available actuation is longitudinal drive force. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

vehicle speed

### Actuators

longitudinal drive force

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 22. Quarter-car road-input two-mass suspension

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are body and wheel displacement, suspension travel, and the available actuation is prescribed road displacement as an analysis input; no control actuator. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

body and wheel displacement, suspension travel

### Actuators

prescribed road displacement as an analysis input; no control actuator

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 23. Rigid-satellite single-axis attitude

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are attitude angle, angular rate, and the available actuation is thruster force or body torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

attitude angle, angular rate

### Actuators

thruster force or body torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 24. Flexible-satellite collocated/noncollocated model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are both body angles and rates, and the available actuation is body torque on the main inertia. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

both body angles and rates

### Actuators

body torque on the main inertia

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 25. Quadrotor roll/pitch/yaw allocation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are roll, pitch, yaw, and the available actuation is four rotor torque perturbations. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

roll, pitch, yaw

### Actuators

four rotor torque perturbations

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 26. Pendulum nonlinear model, small-angle linearization, and nonlinear simulation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pendulum angle and angular rate, and the available actuation is pivot torque. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pendulum angle and angular rate

### Actuators

pivot torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 27. Hanging-crane and inverted-pendulum coupled model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are cart position, pendulum angle, and the available actuation is cart force. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

cart position, pendulum angle

### Actuators

cart force

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 28. Bridged-tee RC circuit

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are output and capacitor voltages, and the available actuation is input voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

output and capacitor voltages

### Actuators

input voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 29. Current-driven RLC circuit

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are two capacitor voltages and inductor current, and the available actuation is source current. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

two capacitor voltages and inductor current

### Actuators

source current

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 30. Ideal op-amp weighted summer

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are summed output voltage, and the available actuation is input voltages. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

summed output voltage

### Actuators

input voltages

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 31. Ideal op-amp integrator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are integrator output voltage, and the available actuation is input voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

integrator output voltage

### Actuators

input voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 32. Loudspeaker electromechanical model with drive circuit

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are cone displacement, coil current, and the available actuation is amplifier voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

cone displacement, coil current

### Actuators

amplifier voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 33. DC-motor position and speed models

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor position, speed, armature current, and the available actuation is armature voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor position, speed, armature current

### Actuators

armature voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 34. Gear-train torque multiplication and reflected inertia

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor and load angle, shaft torque, and the available actuation is motor torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor and load angle, shaft torque

### Actuators

motor torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 35. Room heat-loss model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are room temperature, and the available actuation is heating rate in the labeled control extension. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

room temperature

### Actuators

heating rate in the labeled control extension

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 36. Two-thermal-mass controlled process

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are two body temperatures, and the available actuation is heater power. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

two body temperatures

### Actuators

heater power

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 37. Heat exchanger with nonlinear valve and measurement delay

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are measured outlet water temperature, and the available actuation is steam inlet valve area. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

measured outlet water temperature

### Actuators

steam inlet valve area

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 38. Water-tank continuity, square-root outflow, and operating-point linearization

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are tank level and outlet flow, and the available actuation is inlet mass flow. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

tank level and outlet flow

### Actuators

inlet mass flow

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 39. Pressure-driven hydraulic piston

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are piston position, acceleration, chamber pressure, and the available actuation is chamber pressure input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

piston position, acceleration, chamber pressure

### Actuators

chamber pressure input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 40. Hydraulic control-surface actuator and load-dependent integrator model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are surface angle and load force, and the available actuation is servo valve displacement. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

surface angle and load force

### Actuators

servo valve displacement

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 41. Test linearity and time invariance by superposition and shift

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are system response, and the available actuation is test input signal. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

system response

### Actuators

test input signal

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 42. Derive a first-order impulse response and arbitrary-input convolution

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are output response, and the available actuation is input signal. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

output response

### Actuators

input signal

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 43. Convert an ODE to a transfer function under zero initial conditions

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are system output, and the available actuation is forcing input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

system output

### Actuators

forcing input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 44. Derive the RC low-pass transfer function and impulse response

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are capacitor voltage, and the available actuation is input voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

capacitor voltage

### Actuators

input voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 45. Compute magnitude and phase of first-order sinusoidal response

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are sinusoidal output amplitude and phase, and the available actuation is sinusoidal input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

sinusoidal output amplitude and phase

### Actuators

sinusoidal input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 46. Transform canonical step, ramp, impulse, and sinusoidal inputs

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are transformed input and output, and the available actuation is canonical test input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

transformed input and output

### Actuators

canonical test input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 47. Recover a time response by partial-fraction expansion

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are time response, and the available actuation is Laplace-domain signal. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

time response

### Actuators

Laplace-domain signal

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 48. Apply the Final Value Theorem and reject invalid unstable use

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are steady-state output, and the available actuation is test input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

steady-state output

### Actuators

test input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 49. Compute stable-system DC gain from the transfer function

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are steady output, and the available actuation is unit-step input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

steady output

### Actuators

unit-step input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 50. Solve homogeneous and forced ODEs with initial conditions

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are state and output response, and the available actuation is forcing input and initial condition. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

state and output response

### Actuators

forcing input and initial condition

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 51. Analyze automobile position dynamics from the cruise model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are vehicle position and speed, and the available actuation is drive force. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

vehicle position and speed

### Actuators

drive force

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 52. Analyze DC-motor position and speed poles with numerical parameters

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor speed and position, and the available actuation is armature voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor speed and position

### Actuators

armature voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 53. Predict rigid-satellite response to a finite thrust pulse

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are attitude angle and rate, and the available actuation is finite thruster-force pulse. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

attitude angle and rate

### Actuators

finite thruster-force pulse

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 54. Reduce nested control block diagrams to one transfer function

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are closed-loop output, and the available actuation is reference input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

closed-loop output

### Actuators

reference input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 55. Derive a closed-loop transfer function with Mason's signal-flow rule

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are signal-flow output, and the available actuation is source node input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

signal-flow output

### Actuators

source node input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 56. Infer transient form and decay rate from pole locations

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are transient output, and the available actuation is impulse input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

transient output

### Actuators

impulse input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 57. Map second-order rise time, overshoot, settling time, and peak time to pole regions

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are step response metrics, and the available actuation is command input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

step response metrics

### Actuators

command input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 58. Explain and quantify Boeing 747 nonminimum-phase altitude response

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are aircraft altitude, and the available actuation is impulsive elevator deflection. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

aircraft altitude

### Actuators

impulsive elevator deflection

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 59. Test BIBO stability of a current-driven capacitor

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are capacitor voltage, and the available actuation is bounded source current. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

capacitor voltage

### Actuators

bounded source current

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 60. Determine proportional and PI gain stability regions with the Routh criterion

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are closed-loop poles and stability region, and the available actuation is proportional or PI controller gains. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

closed-loop poles and stability region

### Actuators

proportional or PI controller gains

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 61. Derive closed-loop reference, disturbance, sensor-noise, control, and error maps using sensitivity and complementary sensitivity

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are output, error, control, sensitivity, complementary sensitivity, and the available actuation is reference, plant-input disturbance, and sensor-noise test inputs. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

output, error, control, sensitivity, complementary sensitivity

### Actuators

reference, plant-input disturbance, and sensor-noise test inputs

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 62. Stabilize an unstable inverted-pendulum model by feedback characteristic-equation design

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pendulum output and closed-loop poles, and the available actuation is dynamic compensator command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pendulum output and closed-loop poles

### Actuators

dynamic compensator command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 63. Quantify feedback reduction of plant-gain sensitivity

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are closed-loop gain, and the available actuation is controller input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

closed-loop gain

### Actuators

controller input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 64. Resolve low-frequency plant-disturbance rejection versus high-frequency sensor-noise attenuation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are regulated output, error, and sensor-noise response, and the available actuation is plant disturbance and sensor-noise test inputs. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

regulated output, error, and sensor-noise response

### Actuators

plant disturbance and sensor-noise test inputs

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 65. Compute Type 0 speed-control error with proportional feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are speed and tracking error, and the available actuation is proportional control command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

speed and tracking error

### Actuators

proportional control command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 66. Raise speed control to Type 1 with integral action

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are speed and tracking error, and the available actuation is PI control command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

speed and tracking error

### Actuators

PI control command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 67. Evaluate system type and velocity constant with tachometer feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are position, speed, and tracking error, and the available actuation is motor control and tachometer feedback signals. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

position, speed, and tracking error

### Actuators

motor control and tachometer feedback signals

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 68. Compare P and PI rejection of DC-motor torque disturbances

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor position error and disturbance response, and the available actuation is disturbance torque and controller command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor position error and disturbance response

### Actuators

disturbance torque and controller command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 69. Tune proportional control while exposing speed/offset/damping tradeoffs

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are regulated output, tracking error, and control effort, and the available actuation is proportional actuator command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

regulated output, tracking error, and control effort

### Actuators

proportional actuator command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 70. Use integral control for robust zero step error and constant-disturbance rejection

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are tracking error, plant output, and control effort, and the available actuation is integral control command and test disturbance. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

tracking error, plant output, and control effort

### Actuators

integral control command and test disturbance

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 71. Use derivative/rate feedback to add damping without derivative kick

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are output and output rate, and the available actuation is proportional and rate command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

output and output rate

### Actuators

proportional and rate command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 72. Design PI control for a two-thermal-mass process

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are controlled temperature and control effort, and the available actuation is heater command. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

controlled temperature and control effort

### Actuators

heater command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 73. Compare P, PI, and PID on DC-motor speed

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor speed, tracking error, and disturbance response, and the available actuation is armature voltage and disturbance torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor speed, tracking error, and disturbance response

### Actuators

armature voltage and disturbance torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 74. Analyze P/PI DC-motor position disturbance types with non-unity sensing

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor position, sensed error, and disturbance response, and the available actuation is controller command and disturbance torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor position, sensed error, and disturbance response

### Actuators

controller command and disturbance torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 75. Compare satellite PD and PID system type for reference and disturbance inputs

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are attitude angle, error, and disturbance response, and the available actuation is body torque and controller command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

attitude angle, error, and disturbance response

### Actuators

body torque and controller command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 76. Tune a PID from a process reaction curve for quarter-decay behavior

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are process output and quarter-decay response, and the available actuation is P, PI, or PID process command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

process output and quarter-decay response

### Actuators

P, PI, or PID process command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 77. Tune P/PI/PID from ultimate gain and ultimate period

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are marginal oscillation and tuned response, and the available actuation is proportional or PID process command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

marginal oscillation and tuned response

### Actuators

proportional or PID process command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 78. Apply reaction-curve Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are heat-exchanger temperature and step response, and the available actuation is steam-valve P or PI command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

heat-exchanger temperature and step response

### Actuators

steam-valve P or PI command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 79. Apply ultimate-sensitivity Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are heat-exchanger temperature and oscillation, and the available actuation is steam-valve P or PI command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

heat-exchanger temperature and oscillation

### Actuators

steam-valve P or PI command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 80. Add inverse-DC-gain feedforward to DC-motor tracking and measured-disturbance rejection

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor speed, tracking error, and disturbance response, and the available actuation is feedback plus reference or measured-disturbance feedforward. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor speed, tracking error, and disturbance response

### Actuators

feedback plus reference or measured-disturbance feedforward

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 81. Draw and parameterize the DC-motor position-control root locus

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor position and closed-loop poles, and the available actuation is position-loop gain. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor position and closed-loop poles

### Actuators

position-loop gain

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 82. Draw a root locus with respect to a physical damping/pole parameter

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are modal poles and damping, and the available actuation is physical pole and damping coefficient. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

modal poles and damping

### Actuators

physical pole and damping coefficient

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 83. Construct a higher-order locus from Evans phase, real-axis, asymptote, departure, and gain rules

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are closed-loop poles, damping, and velocity constant, and the available actuation is loop gain. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

closed-loop poles, damping, and velocity constant

### Actuators

loop gain

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 84. Stabilize a satellite double integrator with PD control

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are satellite attitude and angular rate, and the available actuation is PD body-torque command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

satellite attitude and angular rate

### Actuators

PD body-torque command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 85. Quantify how a finite lead pole changes the satellite PD locus, including the 9:1 transition

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are satellite attitude and lead-pole effects, and the available actuation is lead-compensated torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

satellite attitude and lead-pole effects

### Actuators

lead-compensated torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 86. Analyze collocated satellite flexibility and flexible-mode damping

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are collocated attitude and flexible-mode poles, and the available actuation is collocated body torque. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

collocated attitude and flexible-mode poles

### Actuators

collocated body torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 87. Analyze noncollocated satellite flexibility and spillover instability

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are remote attitude and flexible-mode poles, and the available actuation is main-body torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

remote attitude and flexible-mode poles

### Actuators

main-body torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 88. Handle complex multiple roots on a fourth-order locus

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are closed-loop pole multiplicity, and the available actuation is loop gain. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

closed-loop pole multiplicity

### Actuators

loop gain

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 89. Design lead compensation to meet rise-time and overshoot limits

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are servo position and step-response metrics, and the available actuation is lead-compensated command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

servo position and step-response metrics

### Actuators

lead-compensated command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 90. Add lag compensation to improve velocity-error constant without moving dominant roots

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are tracking error, position, and slow pole, and the available actuation is lead-lag command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

tracking error, position, and slow pole

### Actuators

lead-lag command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 91. Add notch compensation for an unmodeled flexible resonance

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are flexible-mode response and nominal output, and the available actuation is notch-filtered actuator command. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

flexible-mode response and nominal output

### Actuators

notch-filtered actuator command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 92. Realize a lead compensator with an operational-amplifier circuit

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are lead-network output voltage, and the available actuation is input error voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

lead-network output voltage

### Actuators

input error voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 93. Design quadrotor pitch-axis lead compensation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are quadrotor pitch angle, rate, and closed-loop poles, and the available actuation is pitch rotor-torque command. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

quadrotor pitch angle, rate, and closed-loop poles

### Actuators

pitch rotor-torque command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 94. Design a small-airplane pitch autopilot and integral trim loop

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pitch attitude, elevator, and trim-tab deflections, and the available actuation is elevator and trim-tab commands. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pitch attitude, elevator, and trim-tab deflections

### Actuators

elevator and trim-tab commands

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 95. Use a negative root locus for nonminimum-phase airplane altitude dynamics

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are aircraft altitude and closed-loop poles, and the available actuation is elevator-loop gain. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

aircraft altitude and closed-loop poles

### Actuators

elevator-loop gain

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 96. Select tachometer and amplifier gains by successive loop closure

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are servomechanism position, speed, and poles, and the available actuation is tachometer and amplifier gains. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

servomechanism position, speed, and poles

### Actuators

tachometer and amplifier gains

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 97. Design inner-attitude/outer-position quadrotor cascade control

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are horizontal position, pitch attitude, and all closed-loop poles, and the available actuation is outer position command and inner rotor-torque command. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

horizontal position, pitch attitude, and all closed-loop poles

### Actuators

outer position command and inner rotor-torque command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 98. Design a lead compensator for a numerically controlled machine-tool servo

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are machine-tool position and closed-loop poles, and the available actuation is lead-compensated servo command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

machine-tool position and closed-loop poles

### Actuators

lead-compensated servo command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 99. Linearize and stabilize an elementary magnetic suspension

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are ball position, sensor voltage, and coil current, and the available actuation is electromagnet current command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

ball position, sensor voltage, and coil current

### Actuators

electromagnet current command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 100. Design yaw-rate-aided heading control for the USCG cutter Tampa under wind disturbance

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are ship heading, yaw rate, rudder angle, and wind response, and the available actuation is rudder command and prescribed wind-gust input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

ship heading, yaw rate, rudder angle, and wind response

### Actuators

rudder command and prescribed wind-gust input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 101. Compute the current response of a voltage-driven capacitor

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are capacitor current magnitude and phase, and the available actuation is sinusoidal voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

capacitor current magnitude and phase

### Actuators

sinusoidal voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 102. Derive the magnitude and phase of a first-order lead element

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are lead-compensator magnitude and phase, and the available actuation is sinusoidal error signal. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

lead-compensator magnitude and phase

### Actuators

sinusoidal error signal

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 103. Build an asymptotic Bode plot from real poles and zeros

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are open-loop magnitude and phase, and the available actuation is sinusoidal plant input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

open-loop magnitude and phase

### Actuators

sinusoidal plant input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 104. Include complex pole/zero factors in ordinary and flexible-system Bode plots

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are plant displacement magnitude and phase, and the available actuation is sinusoidal applied force. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

plant displacement magnitude and phase

### Actuators

sinusoidal applied force

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 105. Infer low-frequency error constants and system type from a Bode plot

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are tracking error and low-frequency loop gain, and the available actuation is unit-ramp reference. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

tracking error and low-frequency loop gain

### Actuators

unit-ramp reference

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 106. Apply the Nyquist criterion to a second-order loop stable for every positive gain

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are Nyquist locus and closed-loop poles, and the available actuation is loop gain K. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

Nyquist locus and closed-loop poles

### Actuators

loop gain K

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 107. Apply Nyquist indentation to a third-order loop with a pole at the origin

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are Nyquist locus and stability region, and the available actuation is loop gain K. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

Nyquist locus and stability region

### Actuators

loop gain K

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 108. Compare special Nyquist cases with an RHP pole and imaginary-axis zeros

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are Nyquist loci and closed-loop stability, and the available actuation is the two loop gains. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

Nyquist loci and closed-loop stability

### Actuators

the two loop gains

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 109. Diagnose conditional stability and misleading gain margin

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are stability region and margins, and the available actuation is loop gain K. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

stability region and margins

### Actuators

loop gain K

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 110. Interpret multiple unity-gain crossings and stability margins

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are multiple crossover margins, and the available actuation is loop excitation. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

multiple crossover margins

### Actuators

loop excitation

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 111. Use Bode's gain-phase slope rule to design spacecraft PD control

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are attitude, sensitivity, and bandwidth, and the available actuation is body-torque command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

attitude, sensitivity, and bandwidth

### Actuators

body-torque command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 112. Relate crossover frequency, phase margin, resonant peak, and closed-loop bandwidth

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are closed-loop magnitude and bandwidth, and the available actuation is open-loop frequency sweep. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

closed-loop magnitude and bandwidth

### Actuators

open-loop frequency sweep

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 113. Design lead compensation for DC-motor position control

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor position, error, and step response, and the available actuation is lead-compensated motor command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor position, error, and step response

### Actuators

lead-compensated motor command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 114. Design single- and double-lead compensation for a thermal plant and servomechanism

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are temperature or servo output, and the available actuation is single- or double-lead command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

temperature or servo output

### Actuators

single- or double-lead command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 115. Design lag compensation for a thermal plant and DC motor, and compare it with lead

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are thermal or motor response and slow tail, and the available actuation is lag-compensated command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

thermal or motor response and slow tail

### Actuators

lag-compensated command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 116. Design spacecraft PID control with a sensor lag and constant torque disturbance

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are attitude, sensitivity, and disturbance response, and the available actuation is controller and disturbance torques. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

attitude, sensitivity, and disturbance response

### Actuators

controller and disturbance torques

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 117. Convert a sinusoidal tracking-error requirement into a loop-gain performance bound

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are tracking error and sensitivity bound, and the available actuation is prescribed sinusoidal references. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

tracking error and sensitivity bound

### Actuators

prescribed sinusoidal references

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 118. Enforce robust-stability and sensitivity bounds under plant uncertainty

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are robustness bounds and sensitivity, and the available actuation is loop-shaped feedback command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

robustness bounds and sensitivity

### Actuators

loop-shaped feedback command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 119. Quantify the phase-margin loss caused by sampling-equivalent time delay

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are phase margin and sampled step response, and the available actuation is digitally sampled control command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

phase margin and sampled step response

### Actuators

digitally sampled control command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 120. Read closed-loop bandwidth, resonant peak, and stability margins from a Nichols chart

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are Nichols locus and closed-loop response, and the available actuation is frequency-swept loop excitation. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

Nichols locus and closed-loop response

### Actuators

frequency-swept loop excitation

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 121. Put rigid-satellite attitude dynamics into state-variable form

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are attitude angle and angular rate, and the available actuation is thruster force. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

attitude angle and angular rate

### Actuators

thruster force

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 122. Derive a DC-motor state model from coupled mechanical and electrical equations

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor position, speed, current, and the available actuation is armature voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor position, speed, current

### Actuators

armature voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 123. Realize a quarter-car transfer function in real modal canonical form

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are quarter-car output and modal states, and the available actuation is realization input. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

quarter-car output and modal states

### Actuators

realization input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 124. Transform a thermal system from control canonical form to modal form

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are thermal modal states and output, and the available actuation is heat input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

thermal modal states and output

### Actuators

heat input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 125. Recover poles, zeros, and transfer function from the Piper Dakota state model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pitch attitude and modal states, and the available actuation is elevator input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pitch attitude and modal states

### Actuators

elevator input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 126. Test controllability and observability and interpret pole-zero cancellation physically

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are state modes and rank tests, and the available actuation is test excitation. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

state modes and rank tests

### Actuators

test excitation

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 127. Place repeated closed-loop poles for an undamped pendulum by full-state feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pendulum angle and rate, and the available actuation is pivot torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pendulum angle and rate

### Actuators

pivot torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 128. Apply Ackermann pole placement and diagnose gain growth near a weakly controllable zero

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are closed-loop poles, gains, and control effort, and the available actuation is state-feedback command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

closed-loop poles, gains, and control effort

### Actuators

state-feedback command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 129. Introduce a step reference robustly into a Type 1 DC-motor loop

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor position and speed, and the available actuation is state feedback voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor position and speed

### Actuators

state feedback voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 130. Select dominant second-order poles for a third-order drone model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are drone attitude response, and the available actuation is control moment. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

drone attitude response

### Actuators

control moment

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 131. Balance tracking error and effort with LQR for the drone

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are drone state and control effort, and the available actuation is optimal control moment. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

drone state and control effort

### Actuators

optimal control moment

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 132. Design and validate a full-order pendulum state estimator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are measured angle and estimated state, and the available actuation is known pivot torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

measured angle and estimated state

### Actuators

known pivot torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 133. Design a reduced-order pendulum estimator without differentiating the measurement

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are measured angle and estimated rate, and the available actuation is known pivot torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

measured angle and estimated rate

### Actuators

known pivot torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 134. Select estimator poles from a symmetric root locus under process/sensor noise tradeoffs

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are state estimate and innovation, and the available actuation is known plant input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

state estimate and innovation

### Actuators

known plant input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 135. Combine controller and estimator by the separation principle and form a DC-servo compensator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are servo output, estimated state, and poles, and the available actuation is dynamic compensator voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

servo output, estimated state, and poles

### Actuators

dynamic compensator voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 136. Assign controller feedforward zeros to increase a servomechanism velocity constant

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are servo position, tracking error, and slow tail, and the available actuation is two-input or equivalent lag-lead command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

servo position, tracking error, and slow tail

### Actuators

two-input or equivalent lag-lead command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 137. Add integral state feedback for robust motor-speed tracking and constant-disturbance rejection

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are motor speed and integral error, and the available actuation is motor voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

motor speed and integral error

### Actuators

motor voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 138. Embed a sinusoidal internal model for disk-drive tracking and rejection

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are disk-head position and sinusoidal error, and the available actuation is voice-coil force. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

disk-head position and sinusoidal error

### Actuators

voice-coil force

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 139. Recover LQR loop shape with an LTR estimator while quantifying sensor-noise actuator activity

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are attitude, loop gain, margins, and control RMS, and the available actuation is body torque under sensor noise. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

attitude, loop gain, margins, and control RMS

### Actuators

body torque under sensor noise

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 140. Control a delayed heat exchanger with a Smith predictor and state-space pole placement

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are delayed heat-exchanger temperature, and the available actuation is steam command through Smith predictor. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

delayed heat-exchanger temperature

### Actuators

steam command through Smith predictor

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 141. Digitize a DC-motor lead controller with Tustin's bilinear approximation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are sampled motor position and error, and the available actuation is digital motor voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

sampled motor position and error

### Actuators

digital motor voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 142. Digitize the same lead controller with the zero-order-hold approximation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are sampled motor position and error, and the available actuation is held motor voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

sampled motor position and error

### Actuators

held motor voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 143. Design a space-station attitude controller with matched pole-zero emulation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are space station attitude, and the available actuation is digital body torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

space station attitude

### Actuators

digital body torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 144. Compare continuous and sampled root loci for a first-order plant

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are sampled first-order output, and the available actuation is held proportional command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

sampled first-order output

### Actuators

held proportional command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 145. Design the space-station controller directly in the z-plane

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are space station attitude, and the available actuation is digital body torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

space station attitude

### Actuators

digital body torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 146. Compare continuous, emulated, and direct-discrete damping and step response

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are continuous and sampled step responses, and the available actuation is continuous or digital command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

continuous and sampled step responses

### Actuators

continuous or digital command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 147. Recover a filter difference equation, pole damping, and stability from its z transfer function

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are filter output, and the available actuation is discrete filter input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

filter output

### Actuators

discrete filter input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 148. Solve a forced second-order difference equation by the z-transform

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are discrete sequence output, and the available actuation is ramp sequence input. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

discrete sequence output

### Actuators

ramp sequence input

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 149. Prove and use the mapping properties between the s-plane and z-plane

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are mapped pole locations, and the available actuation is continuous pole location. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

mapped pole locations

### Actuators

continuous pole location

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 150. Map a continuous lag compensator to a 20 Hz digital implementation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are regulated output and digital error, and the available actuation is digital lag command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

regulated output and digital error

### Actuators

digital lag command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 151. Compare Tustin and matched pole-zero digitizations of a lead network

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are lead network magnitude and phase, and the available actuation is sampled error. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

lead network magnitude and phase

### Actuators

sampled error

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 152. Compare Tustin and matched pole-zero digitizations of a lag network

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are lag network magnitude and phase, and the available actuation is sampled error. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

lag network magnitude and phase

### Actuators

sampled error

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 153. Digitize a PID at three sample periods and assess transient degradation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are sampled step response, and the available actuation is digital PID command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

sampled step response

### Actuators

digital PID command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 154. Determine the sampled-data stability-gain range of a plant with an unstable mode

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are sampled plant output, and the available actuation is held proportional command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

sampled plant output

### Actuators

held proportional command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 155. Design discrete proportional-plus-velocity satellite attitude feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are satellite attitude and sampled rate, and the available actuation is digital torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

satellite attitude and sampled rate

### Actuators

digital torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 156. Linearize and digitally stabilize a magnetic-levitation ball subject to sensor/current limits

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are ball displacement and current, and the available actuation is electromagnet current. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

ball displacement and current

### Actuators

electromagnet current

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 157. Redesign a lead-lag servomechanism directly in the z-plane

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are servo position and ramp error, and the available actuation is digital servo voltage. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

servo position and ramp error

### Actuators

digital servo voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 158. Design an antenna-servo controller by emulation and direct z-plane root locus

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are antenna angle, and the available actuation is digital motor torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

antenna angle

### Actuators

digital motor torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 159. Design discrete compensation for a two-real-pole plant under rise-time and overshoot limits

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are sampled plant output, and the available actuation is digital compensated command. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

sampled plant output

### Actuators

digital compensated command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 160. Explain the unavoidable one-sample delay in a causal discrete derivative

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are estimated error derivative, and the available actuation is digital derivative command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

estimated error derivative

### Actuators

digital derivative command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

0.5

---

## 161. Find pendulum equilibria and classify their small-signal stability

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pendulum angle and angular rate, and the available actuation is pivot torque. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pendulum angle and angular rate

### Actuators

pivot torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 162. Linearize a magnetic ball levitator from experimentally measured force curves

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are ball displacement, velocity, coil current, and the available actuation is electromagnet current perturbation. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

ball displacement, velocity, coil current

### Actuators

electromagnet current perturbation

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 163. Linearize nonlinear square-root water-tank outflow around an operating point

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are tank level and outlet flow, and the available actuation is inlet mass flow. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

tank level and outlet flow

### Actuators

inlet mass flow

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 164. Cancel pendulum gravity by computed-torque nonlinear feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are pendulum angle and angular rate, and the available actuation is computed pivot torque. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

pendulum angle and angular rate

### Actuators

computed pivot torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 165. Cancel a rapid-thermal-processing lamp square law with an inverse nonlinearity

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are lamp voltage and delivered power, and the available actuation is commanded lamp voltage. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

lamp voltage and delivered power

### Actuators

commanded lamp voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 166. Predict amplitude-dependent overshoot caused by actuator saturation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are output, error, saturated control, and the available actuation is amplitude-limited command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

output, error, saturated control

### Actuators

amplitude-limited command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 167. Expose large-signal instability in a conditionally stable saturated loop

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are output, loop error, effective gain, and the available actuation is saturated proportional command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

output, loop error, effective gain

### Actuators

saturated proportional command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 168. Predict a saturation-induced flexible-mode limit cycle and eliminate it with a notch

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are flexible displacement and saturated command, and the available actuation is notch-shaped limited command. The declared nonlinearity is preserved and tested over a bounded operating region. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

flexible displacement and saturated command

### Actuators

notch-shaped limited command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 169. Add back-calculation antiwindup to a saturated PI-controlled integrator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are integrator output, plant output, actuator command, and the available actuation is saturated PI command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

integrator output, plant output, actuator command

### Actuators

saturated PI command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 170. Derive the describing function of a saturation nonlinearity

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are nonlinear input and fundamental output, and the available actuation is sinusoidal test amplitude. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

nonlinear input and fundamental output

### Actuators

sinusoidal test amplitude

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 171. Derive the describing function of an ideal relay

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are relay input and fundamental output, and the available actuation is binary relay output. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

relay input and fundamental output

### Actuators

binary relay output

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 172. Derive the complex describing function of a relay with hysteresis

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are hysteresis input and fundamental output, and the available actuation is hysteretic relay output. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

hysteresis input and fundamental output

### Actuators

hysteretic relay output

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 173. Predict a saturation limit cycle from a Nyquist/describing-function intersection

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are oscillation amplitude and frequency, and the available actuation is saturated loop command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

oscillation amplitude and frequency

### Actuators

saturated loop command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 174. Predict a hysteresis-induced limit cycle from the same construction

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are hysteretic oscillation amplitude and frequency, and the available actuation is hysteretic relay command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

hysteretic oscillation amplitude and frequency

### Actuators

hysteretic relay command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 175. Derive bang-bang minimum-time switching and a chatter-reducing PTOS law for a double integrator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are position, velocity, switching function, and the available actuation is bounded acceleration command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

position, velocity, switching function

### Actuators

bounded acceleration command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 176. Prove parameter-dependent stability of a second-order linear system with a Lyapunov equation

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are state vector and Lyapunov energy, and the available actuation is initial state perturbation. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

state vector and Lyapunov energy

### Actuators

initial state perturbation

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 177. Construct a direct Lyapunov function for nonlinear position feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are position error, velocity, Lyapunov function, and the available actuation is nonlinear restoring feedback. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

position error, velocity, Lyapunov function

### Actuators

nonlinear restoring feedback

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 178. Bound a signum nonlinearity by a sector

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are nonlinearity input and output, and the available actuation is signum feedback output. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

nonlinearity input and output

### Actuators

signum feedback output

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 179. Bound actuator saturation by a sector

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are saturation input and output, and the available actuation is amplitude-limited actuator. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

saturation input and output

### Actuators

amplitude-limited actuator

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 180. Certify absolute stability of a saturated loop with the circle criterion

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are loop signals and Nyquist locus, and the available actuation is sector-bounded actuator command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

loop signals and Nyquist locus

### Actuators

sector-bounded actuator command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

2.0

---

## 181. Model a flexible two-body satellite and translate pointing specifications into robust design targets

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are two satellite angles, rates, pointing error, and the available actuation is body control torque. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

two satellite angles, rates, pointing error

### Actuators

body control torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 182. Compare gain stabilization and notch-based phase stabilization of the flexible satellite

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are satellite pointing and flexible deflection, and the available actuation is gain-shaped or notch-shaped torque. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

satellite pointing and flexible deflection

### Actuators

gain-shaped or notch-shaped torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 183. Design satellite state feedback and an estimator from symmetric-root-locus pole choices

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are measured attitude and estimated flexible states, and the available actuation is estimated-state feedback torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

measured attitude and estimated flexible states

### Actuators

estimated-state feedback torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 184. Redesign the satellite by collocating the attitude sensor with the torque actuator

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are collocated attitude and remote flexible angle, and the available actuation is collocated body torque. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

collocated attitude and remote flexible angle

### Actuators

collocated body torque

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 185. Linearize Boeing 747 longitudinal/lateral dynamics and identify Dutch-roll, spiral, roll, phugoid, and short-period modes

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are aircraft rates, attitude, speed, altitude, and the available actuation is rudder, elevator, aileron, thrust. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

aircraft rates, attitude, speed, altitude

### Actuators

rudder, elevator, aileron, thrust

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 186. Design a yaw damper with rudder actuation, yaw-rate sensing, actuator dynamics, and washout

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are yaw rate, sideslip, rudder position, and the available actuation is rudder command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

yaw rate, sideslip, rudder position

### Actuators

rudder command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 187. Compare the practical yaw damper with a higher-order SRL controller-estimator design

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are yaw rate and estimated lateral states, and the available actuation is rudder command from low or high order control. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

yaw rate and estimated lateral states

### Actuators

rudder command from low or high order control

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 188. Design an altitude-hold autopilot with pitch-rate/pitch inner loops and altitude outer-loop feedback

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are altitude, pitch angle, pitch rate, and the available actuation is elevator command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

altitude, pitch angle, pitch rate

### Actuators

elevator command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 189. Model and tune PI feedback for a delayed automotive fuel-air process

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are fuel air ratio and oxygen sensor signal, and the available actuation is fuel injection command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

fuel air ratio and oxygen sensor signal

### Actuators

fuel injection command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 190. Predict the nonlinear oxygen-sensor limit cycle by effective gain and describing function

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are air fuel error and oxygen sensor oscillation, and the available actuation is fuel injection command. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

air fuel error and oxygen sensor oscillation

### Actuators

fuel injection command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 191. Replace sensor-slope dependence by relay feedback to obtain robust average stoichiometry

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are average fuel-air ratio and switching signal, and the available actuation is fuel injection command through relay-conditioned sensing. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

average fuel-air ratio and switching signal

### Actuators

fuel injection command through relay-conditioned sensing

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 192. Build decoupled longitudinal, lateral, yaw, and altitude state models for a quadrotor and map four rotor commands

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are position, attitude, angular rates, altitude, and the available actuation is four rotor thrust commands. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

position, attitude, angular rates, altitude

### Actuators

four rotor thrust commands

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 193. Design cascaded inner-attitude and outer-position PD loops for quadrotor trajectory following

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are quadrotor position, attitude, path error, and the available actuation is mixed rotor thrusts. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

quadrotor position, attitude, path error

### Actuators

mixed rotor thrusts

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 194. Design LQR/estimator controllers for quadrotor longitudinal, lateral, and yaw axes

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are measured and estimated quadrotor axis states, and the available actuation is LQR mixed rotor commands. The working model is locally linear, while saturation and operating range are still checked during simulation. Multiple states or channels exchange energy and must be evaluated as a coupled system. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

measured and estimated quadrotor axis states

### Actuators

LQR mixed rotor commands

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 195. Identify nonlinear radiation/conduction dynamics and a three-state small-signal model for an RTP chamber

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are plate center and support temperatures, and the available actuation is common command to three lamps. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

plate center and support temperatures

### Actuators

common command to three lamps

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 196. Apply PI temperature-trajectory control while respecting the absence of active cooling

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are temperature trajectory and tracking error, and the available actuation is nonnegative lamp power. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

temperature trajectory and tracking error

### Actuators

nonnegative lamp power

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 197. Design an error-space LQG regulator that balances tracking, actuation, and wafer-temperature uniformity

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are center temperature, estimated three-node temperatures, and uniformity, and the available actuation is common lamp command. The working model is locally linear, while saturation and operating range are still checked during simulation. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

center temperature, estimated three-node temperatures, and uniformity

### Actuators

common lamp command

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 198. Verify RTP control with lamp inversion, saturation, antiwindup, and a digital prototype

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. Sampling, computation, sensing, or transport delay is retained as a material part of the loop. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are wafer temperatures, lamp voltage, integrator state, and the available actuation is digitally commanded lamp voltage. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

wafer temperatures, lamp voltage, integrator state

### Actuators

digitally commanded lamp voltage

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

20.0

---

## 199. Model exact adaptation in E. coli chemotaxis as integral feedback of receptor activity

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are receptor activity and methylation state, and the available actuation is ligand concentration and endogenous methylation feedback. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

receptor activity and methylation state

### Actuators

ligand concentration and endogenous methylation feedback

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---

## 200. Map CheY activity into the one-dimensional mean chemotaxis motion model

### Control Problem Description

The relevant unforced behavior is assessed explicitly, and unstable or marginal modes are treated before performance tuning. A positive actuator perturbation follows the sign convention declared in the model, and any inverse response is checked explicitly. No separate pure delay is assumed beyond the dynamic lags stated in the model. The path from actuation to the regulated output contains the storage and integration stages stated in the technical model. The recorded quantities are mean cell position, receptor activity, and methylation, and the available actuation is ligand perturbation through the endogenous pathway. The declared nonlinearity is preserved and tested over a bounded operating region. The main input and output form one control channel, with listed disturbances entering separately. Plant coefficients, sensing, loading, and actuator effectiveness are treated as uncertain during verification.

### Observable Outputs

mean cell position, receptor activity, and methylation

### Actuators

ligand perturbation through the endogenous pathway

### Safety Bounds

max_abs_reference_normalized=1.0
max_abs_output_normalized=2.0
max_abs_actuator_normalized=2.0
max_test_duration_s=50.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed

### Dominant Time Scale (Seconds)

5.0

---
