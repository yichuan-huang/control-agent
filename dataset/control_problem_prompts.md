# CFDC Dataset: Six-Field Inputs for Two Hundred Classic Control Problems

> Each entry matches the global identifier in control_problems.md. Safety limits and dominant time scales are conservative normalized scheduling defaults for software simulation, not textbook hardware ratings or measured textbook parameters. For analysis-only examples with no controller, the Actuators field records the prescribed excitation or test input.

Every problem description is one formula-free natural-language test narrative with eight sentences in the exact Stage 0 evidence order. Diagnostic labels are not shown; the observable evidence is embedded in problem-specific prose so the engine can proceed without a clarification turn.

---

## 1. Household thermostat with hysteresis

### Control Problem Description

Use binary heater command as the available control or test action and continuously record room temperature, heater state; when the bounded input returns to its baseline, no autonomous mode grows and room temperature settles or remains bounded. After a small reversible change in binary heater command, observe room temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from binary heater command to room temperature, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From binary heater command to room temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording room temperature, heater state while applying binary heater command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of binary heater command are applied while recording room temperature, heater state, the thermostat changes heater state through a fixed hysteresis band rather than a smooth dynamic law, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering binary heater command together with the recorded quantities room temperature, heater state, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from binary heater command to room temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

room temperature, heater state

### Actuators

binary heater command

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=80.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

10.0

---

## 2. Automobile cruise control, open versus closed loop

### Control Problem Description

Use throttle angle as the available control or test action and continuously record vehicle speed; when the bounded input returns to its baseline, no autonomous mode grows and vehicle speed settles or remains bounded. After a small reversible change in throttle angle, observe vehicle speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from throttle angle to vehicle speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From throttle angle to vehicle speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording vehicle speed while applying throttle angle makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of throttle angle are applied while recording vehicle speed, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering throttle angle together with the recorded quantities vehicle speed, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from throttle angle to vehicle speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

vehicle speed

### Actuators

throttle angle

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=100.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

10.0

---

## 3. Manual automobile steering

### Control Problem Description

Use steering wheel angle as the available control or test action and continuously record heading angle, lane error; when the bounded input returns to its baseline, no autonomous mode grows and heading angle settles or remains bounded. After a small reversible change in steering wheel angle, observe heading angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from steering wheel angle to heading angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From steering wheel angle to heading angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording heading angle, lane error while applying steering wheel angle makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of steering wheel angle are applied while recording heading angle, lane error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering steering wheel angle together with the recorded quantities heading angle, lane error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from steering wheel angle to heading angle is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

heading angle, lane error

### Actuators

steering wheel angle

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 4. Drebbel incubator temperature regulator

### Control Problem Description

Use air or fuel valve position as the available control or test action and continuously record incubator temperature; when the bounded input returns to its baseline, no autonomous mode grows and incubator temperature settles or remains bounded. After a small reversible change in air or fuel valve position, observe incubator temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from air or fuel valve position to incubator temperature, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From air or fuel valve position to incubator temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording incubator temperature while applying air or fuel valve position makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of air or fuel valve position are applied while recording incubator temperature, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering air or fuel valve position together with the recorded quantities incubator temperature, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from air or fuel valve position to incubator temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

incubator temperature

### Actuators

air or fuel valve position

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

20.0

---

## 5. Float-valve water-level regulator

### Control Problem Description

Use inlet valve opening as the available control or test action and continuously record tank liquid level; when the bounded input returns to its baseline, no autonomous mode grows and tank liquid level settles or remains bounded. After a small reversible change in inlet valve opening, observe tank liquid level; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from inlet valve opening to tank liquid level, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From inlet valve opening to tank liquid level, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording tank liquid level while applying inlet valve opening makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of inlet valve opening are applied while recording tank liquid level, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering inlet valve opening together with the recorded quantities tank liquid level, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from inlet valve opening to tank liquid level is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

tank liquid level

### Actuators

inlet valve opening

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 6. Watt fly-ball steam-engine governor

### Control Problem Description

Use steam valve opening as the available control or test action and continuously record engine shaft speed, governor displacement; when the bounded input returns to its baseline, no autonomous mode grows and engine shaft speed settles or remains bounded. After a small reversible change in steam valve opening, observe engine shaft speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from steam valve opening to engine shaft speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From steam valve opening to engine shaft speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording engine shaft speed, governor displacement while applying steam valve opening makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of steam valve opening are applied while recording engine shaft speed, governor displacement, governor displacement follows a fixed nonlinear speed map around the chosen operating point, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering steam valve opening together with the recorded quantities engine shaft speed, governor displacement, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from steam valve opening to engine shaft speed is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

engine shaft speed, governor displacement

### Actuators

steam valve opening

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=80.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

10.0

---

## 7. Paper-machine stock-consistency control

### Control Problem Description

Use dilution water valve as the available control or test action and continuously record stock consistency; when the bounded input returns to its baseline, no autonomous mode grows and stock consistency settles or remains bounded. After a small reversible change in dilution water valve, observe stock consistency; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from dilution water valve to stock consistency, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From dilution water valve to stock consistency, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording stock consistency while applying dilution water valve makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of dilution water valve are applied while recording stock consistency, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering dilution water valve together with the recorded quantities stock consistency, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from dilution water valve to stock consistency is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

stock consistency

### Actuators

dilution water valve

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 8. Paper-machine moisture control

### Control Problem Description

Use dryer steam command as the available control or test action and continuously record paper moisture; when the bounded input returns to its baseline, no autonomous mode grows and paper moisture settles or remains bounded. After a small reversible change in dryer steam command, observe paper moisture; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from dryer steam command to paper moisture, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From dryer steam command to paper moisture, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording paper moisture while applying dryer steam command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of dryer steam command are applied while recording paper moisture, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering dryer steam command together with the recorded quantities paper moisture, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from dryer steam command to paper moisture is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

paper moisture

### Actuators

dryer steam command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 9. Human blood-pressure regulation

### Control Problem Description

Use neural cardiac and vascular commands as the available control or test action and continuously record arterial pressure, heart rate; when the bounded input returns to its baseline, no autonomous mode grows and arterial pressure settles or remains bounded. After a small reversible change in neural cardiac and vascular commands, observe arterial pressure; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from neural cardiac and vascular commands to arterial pressure, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From neural cardiac and vascular commands to arterial pressure, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording arterial pressure, heart rate while applying neural cardiac and vascular commands makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of neural cardiac and vascular commands are applied while recording arterial pressure, heart rate, vascular resistance, cardiac output, and baroreflex activity all change with the physiological state, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering neural cardiac and vascular commands together with the recorded quantities arterial pressure, heart rate, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from neural cardiac and vascular commands to arterial pressure is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

arterial pressure, heart rate

### Actuators

neural cardiac and vascular commands

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

5.0

---

## 10. Human blood-glucose regulation

### Control Problem Description

Use endogenous insulin and counterregulation as the available control or test action and continuously record blood glucose, insulin level; when the bounded input returns to its baseline, no autonomous mode grows and blood glucose settles or remains bounded. After a small reversible change in endogenous insulin and counterregulation, observe blood glucose; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from endogenous insulin and counterregulation to blood glucose, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From endogenous insulin and counterregulation to blood glucose, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording blood glucose, insulin level while applying endogenous insulin and counterregulation makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of endogenous insulin and counterregulation are applied while recording blood glucose, insulin level, insulin release, glucose uptake, and meal disturbances change with blood-glucose level and time, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering endogenous insulin and counterregulation together with the recorded quantities blood glucose, insulin level, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from endogenous insulin and counterregulation to blood glucose is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

blood glucose, insulin level

### Actuators

endogenous insulin and counterregulation

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

5.0

---

## 11. Human heart-rate regulation

### Control Problem Description

Use sympathetic and parasympathetic drive as the available control or test action and continuously record heart rate; when the bounded input returns to its baseline, no autonomous mode grows and heart rate settles or remains bounded. After a small reversible change in sympathetic and parasympathetic drive, observe heart rate; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sympathetic and parasympathetic drive to heart rate, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From sympathetic and parasympathetic drive to heart rate, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording heart rate while applying sympathetic and parasympathetic drive makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sympathetic and parasympathetic drive are applied while recording heart rate, autonomic drive and cardiac response rates change with exertion and the current heart state, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering sympathetic and parasympathetic drive together with the recorded quantities heart rate, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from sympathetic and parasympathetic drive to heart rate is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

heart rate

### Actuators

sympathetic and parasympathetic drive

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

5.0

---

## 12. Eye-pointing-angle control

### Control Problem Description

Use ocular muscle torque as the available control or test action and continuously record eye angle, retinal error; when the bounded input returns to its baseline, no autonomous mode grows and eye angle settles or remains bounded. After a small reversible change in ocular muscle torque, observe eye angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from ocular muscle torque to eye angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From ocular muscle torque to eye angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording eye angle, retinal error while applying ocular muscle torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of ocular muscle torque are applied while recording eye angle, retinal error, ocular-muscle torque and visual-error feedback vary with gaze angle and muscle state, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering ocular muscle torque together with the recorded quantities eye angle, retinal error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from ocular muscle torque to eye angle is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

eye angle, retinal error

### Actuators

ocular muscle torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

5.0

---

## 13. Pupil-diameter light regulation

### Control Problem Description

Use iris muscle activation as the available control or test action and continuously record pupil diameter, retinal illumination; when the bounded input returns to its baseline, no autonomous mode grows and pupil diameter settles or remains bounded. After a small reversible change in iris muscle activation, observe pupil diameter; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from iris muscle activation to pupil diameter, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From iris muscle activation to pupil diameter, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pupil diameter, retinal illumination while applying iris muscle activation makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of iris muscle activation are applied while recording pupil diameter, retinal illumination, iris-muscle action and retinal illumination change together with pupil diameter, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering iris muscle activation together with the recorded quantities pupil diameter, retinal illumination, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from iris muscle activation to pupil diameter is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

pupil diameter, retinal illumination

### Actuators

iris muscle activation

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

5.0

---

## 14. Elevator position control with coarse/fine sensing and cable stretch

### Control Problem Description

Use hoist motor torque and brake as the available control or test action and continuously record car position, landing error, cable stretch; when the bounded input returns to its baseline, no autonomous mode grows and car position settles or remains bounded. After a small reversible change in hoist motor torque and brake, observe car position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from hoist motor torque and brake to car position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From hoist motor torque and brake to car position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording car position, landing error, cable stretch while applying hoist motor torque and brake makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of hoist motor torque and brake are applied while recording car position, landing error, cable stretch, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering hoist motor torque and brake together with the recorded quantities car position, landing error, cable stretch, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from hoist motor torque and brake to car position is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

car position, landing error, cable stretch

### Actuators

hoist motor torque and brake

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 15. Electrical temperature sensing and actuation

### Control Problem Description

Use electrical heater voltage as the available control or test action and continuously record temperature, sensor voltage; when the bounded input returns to its baseline, no autonomous mode grows and temperature settles or remains bounded. After a small reversible change in electrical heater voltage, observe temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from electrical heater voltage to temperature, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From electrical heater voltage to temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording temperature, sensor voltage while applying electrical heater voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of electrical heater voltage are applied while recording temperature, sensor voltage, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering electrical heater voltage together with the recorded quantities temperature, sensor voltage, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from electrical heater voltage to temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

temperature, sensor voltage

### Actuators

electrical heater voltage

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

20.0

---

## 16. Electrical pressure sensing and actuation

### Control Problem Description

Use valve command as the available control or test action and continuously record pressure, sensor voltage; when the bounded input returns to its baseline, no autonomous mode grows and pressure settles or remains bounded. After a small reversible change in valve command, observe pressure; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from valve command to pressure, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From valve command to pressure, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pressure, sensor voltage while applying valve command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of valve command are applied while recording pressure, sensor voltage, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering valve command together with the recorded quantities pressure, sensor voltage, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from valve command to pressure is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

pressure, sensor voltage

### Actuators

valve command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 17. Electrical liquid-level sensing and actuation

### Control Problem Description

Use pump speed or valve position as the available control or test action and continuously record liquid level, transmitter signal; when the bounded input returns to its baseline, no autonomous mode grows and liquid level settles or remains bounded. After a small reversible change in pump speed or valve position, observe liquid level; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from pump speed or valve position to liquid level, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From pump speed or valve position to liquid level, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording liquid level, transmitter signal while applying pump speed or valve position makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of pump speed or valve position are applied while recording liquid level, transmitter signal, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering pump speed or valve position together with the recorded quantities liquid level, transmitter signal, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from pump speed or valve position to liquid level is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

liquid level, transmitter signal

### Actuators

pump speed or valve position

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 18. Electrical pipe-flow sensing and actuation

### Control Problem Description

Use control valve position as the available control or test action and continuously record pipe flow rate; when the bounded input returns to its baseline, no autonomous mode grows and pipe flow rate settles or remains bounded. After a small reversible change in control valve position, observe pipe flow rate; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from control valve position to pipe flow rate, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From control valve position to pipe flow rate, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pipe flow rate while applying control valve position makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of control valve position are applied while recording pipe flow rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering control valve position together with the recorded quantities pipe flow rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from control valve position to pipe flow rate is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

pipe flow rate

### Actuators

control valve position

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

10.0

---

## 19. HPA-axis stress-hormone negative feedback

### Control Problem Description

Use endogenous secretion rates as the available control or test action and continuously record hormone concentrations; when the bounded input returns to its baseline, no autonomous mode grows and hormone concentrations settles or remains bounded. After a small reversible change in endogenous secretion rates, observe hormone concentrations; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from endogenous secretion rates to hormone concentrations, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From endogenous secretion rates to hormone concentrations, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording hormone concentrations while applying endogenous secretion rates makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of endogenous secretion rates are applied while recording hormone concentrations, hormone secretion rates and feedback sensitivity vary with the endocrine state, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering endogenous secretion rates together with the recorded quantities hormone concentrations, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from endogenous secretion rates to hormone concentrations is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

hormone concentrations

### Actuators

endogenous secretion rates

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

5.0

---

## 20. Oxytocin-mediated childbirth positive feedback

### Control Problem Description

Use endogenous oxytocin release as the available control or test action and continuously record oxytocin level, contraction intensity; when the bounded input returns to its baseline, the reinforcing oxytocin-contraction loop amplifies a departure instead of restoring the labor state, so the deviation continues to grow rather than return. After a small reversible change in endogenous oxytocin release, observe oxytocin level; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from endogenous oxytocin release to oxytocin level, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From endogenous oxytocin release to oxytocin level, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording oxytocin level, contraction intensity while applying endogenous oxytocin release makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of endogenous oxytocin release are applied while recording oxytocin level, contraction intensity, oxytocin release and contraction intensity reinforce one another as labor progresses, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering endogenous oxytocin release together with the recorded quantities oxytocin level, contraction intensity, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from endogenous oxytocin release to oxytocin level is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

oxytocin level, contraction intensity

### Actuators

endogenous oxytocin release

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=60.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

10.0

---

## 21. First-order automobile cruise dynamics

### Control Problem Description

Use longitudinal drive force as the available control or test action and continuously record vehicle speed; when the bounded input returns to its baseline, no autonomous mode grows and vehicle speed settles or remains bounded. After a small reversible change in longitudinal drive force, observe vehicle speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from longitudinal drive force to vehicle speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From longitudinal drive force to vehicle speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording vehicle speed while applying longitudinal drive force makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of longitudinal drive force are applied while recording vehicle speed, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering longitudinal drive force together with the recorded quantities vehicle speed, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from longitudinal drive force to vehicle speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

vehicle speed

### Actuators

longitudinal drive force

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 22. Quarter-car road-input two-mass suspension

### Control Problem Description

Use prescribed road-displacement test input as the available control or test action and continuously record body displacement, wheel displacement, and suspension travel; when the bounded input returns to its baseline, no autonomous mode grows and body displacement settles or remains bounded. After a small reversible change in prescribed road-displacement test input, observe body displacement; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed road-displacement test input to body displacement, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From prescribed road-displacement test input to body displacement, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording body displacement, wheel displacement, and suspension travel while applying prescribed road-displacement test input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed road-displacement test input are applied while recording body displacement, wheel displacement, and suspension travel, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed road-displacement test input together with the recorded quantities body displacement, wheel displacement, and suspension travel, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from prescribed road-displacement test input to body displacement is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

body displacement, wheel displacement, and suspension travel

### Actuators

prescribed road-displacement test input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 23. Rigid-satellite single-axis attitude

### Control Problem Description

Use thruster force or body torque as the available control or test action and continuously record attitude angle, angular rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets attitude angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in thruster force or body torque, observe attitude angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from thruster force or body torque to attitude angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From thruster force or body torque to attitude angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording attitude angle, angular rate while applying thruster force or body torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of thruster force or body torque are applied while recording attitude angle, angular rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering thruster force or body torque together with the recorded quantities attitude angle, angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from thruster force or body torque to attitude angle is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

attitude angle, angular rate

### Actuators

thruster force or body torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 24. Flexible-satellite collocated/noncollocated model

### Control Problem Description

Use body torque on the main inertia as the available control or test action and continuously record both body angles and rates; when the bounded input returns to its baseline, an integrating or non-restoring mode lets both body angles retain an offset or drift after the prescribed drive is removed. After a small reversible change in body torque on the main inertia, observe both body angles; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from body torque on the main inertia to both body angles, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From body torque on the main inertia to both body angles, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording both body angles and rates while applying body torque on the main inertia makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of body torque on the main inertia are applied while recording both body angles and rates, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering body torque on the main inertia together with the recorded quantities both body angles and rates, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from body torque on the main inertia to both body angles is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

both body angles and rates

### Actuators

body torque on the main inertia

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 25. Quadrotor roll/pitch/yaw allocation

### Control Problem Description

Use four rotor thrust perturbations as the available control or test action and continuously record roll, pitch, and yaw response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets roll retain an offset or drift after the prescribed drive is removed. After a small reversible change in four rotor thrust perturbations, observe roll; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from four rotor thrust perturbations to roll, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From four rotor thrust perturbations to roll, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording roll, pitch, and yaw response while applying four rotor thrust perturbations makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of four rotor thrust perturbations are applied while recording roll, pitch, and yaw response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering four rotor thrust perturbations together with the recorded quantities roll, pitch, and yaw response, changing any one of several actuators visibly moves several recordings, so actuator directions must be allocated or paired together. When the bounded test from four rotor thrust perturbations to roll is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

roll, pitch, and yaw response

### Actuators

four rotor thrust perturbations

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
change several actuator channels simultaneously during the first identification test

### Dominant Time Scale (Seconds)

2.0

---

## 26. Pendulum nonlinear model, small-angle linearization, and nonlinear simulation

### Control Problem Description

Use pivot torque as the available control or test action and continuously record pendulum angle and angular rate; when the bounded input returns to its baseline, no autonomous mode grows and pendulum angle settles or remains bounded. After a small reversible change in pivot torque, observe pendulum angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from pivot torque to pendulum angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From pivot torque to pendulum angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pendulum angle and angular rate while applying pivot torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of pivot torque are applied while recording pendulum angle and angular rate, gravity torque changes with pendulum angle and departs materially from its local small-angle approximation, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering pivot torque together with the recorded quantities pendulum angle and angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from pivot torque to pendulum angle is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

pendulum angle and angular rate

### Actuators

pivot torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 27. Hanging-crane and inverted-pendulum coupled model

### Control Problem Description

Use cart force as the available control or test action and continuously record cart position, pendulum angle; when the bounded input returns to its baseline, the upright pendulum mode drives the cart-pendulum state away from equilibrium when cart feedback is absent, so the deviation continues to grow rather than return. After a small reversible change in cart force, observe cart position; the first useful output change moves in an unfavorable or opposite direction before turning toward its eventual value. For the same small change from cart force to cart position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From cart force to cart position, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording cart position, pendulum angle while applying cart force makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of cart force are applied while recording cart position, pendulum angle, cart motion, cable geometry, and pendulum gravity couple through the evolving swing state, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering cart force together with the recorded quantities cart position, pendulum angle, there are fewer independent actuators than regulated coordinates, so natural motion and state interaction must supply the missing direction. When the bounded test from cart force to cart position is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

cart position, pendulum angle

### Actuators

cart force

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
command an unactuated coordinate as though it had a direct actuator

### Dominant Time Scale (Seconds)

2.0

---

## 28. Bridged-tee RC circuit

### Control Problem Description

Use input voltage as the available control or test action and continuously record output and capacitor voltages; when the bounded input returns to its baseline, no autonomous mode grows and output settles or remains bounded. After a small reversible change in input voltage, observe output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from input voltage to output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From input voltage to output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording output and capacitor voltages while applying input voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of input voltage are applied while recording output and capacitor voltages, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering input voltage together with the recorded quantities output and capacitor voltages, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from input voltage to output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

output and capacitor voltages

### Actuators

input voltage

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 29. Current-driven RLC circuit

### Control Problem Description

Use source current as the available control or test action and continuously record two capacitor voltages and inductor current; when the bounded input returns to its baseline, no autonomous mode grows and two capacitor voltages settles or remains bounded. After a small reversible change in source current, observe two capacitor voltages; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from source current to two capacitor voltages, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From source current to two capacitor voltages, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording two capacitor voltages and inductor current while applying source current makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of source current are applied while recording two capacitor voltages and inductor current, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering source current together with the recorded quantities two capacitor voltages and inductor current, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from source current to two capacitor voltages is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

two capacitor voltages and inductor current

### Actuators

source current

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 30. Ideal op-amp weighted summer

### Control Problem Description

Use input voltages as the available control or test action and continuously record summed output voltage; when the bounded input returns to its baseline, no autonomous mode grows and summed output voltage settles or remains bounded. After a small reversible change in input voltages, observe summed output voltage; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from input voltages to summed output voltage, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From input voltages to summed output voltage, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording summed output voltage while applying input voltages makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of input voltages are applied while recording summed output voltage, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering input voltages together with the recorded quantities summed output voltage, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from input voltages to summed output voltage is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

summed output voltage

### Actuators

input voltages

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 31. Ideal op-amp integrator

### Control Problem Description

Use input voltage as the available control or test action and continuously record integrator output voltage; when the bounded input returns to its baseline, an integrating or non-restoring mode lets integrator output voltage retain an offset or drift after the prescribed drive is removed. After a small reversible change in input voltage, observe integrator output voltage; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from input voltage to integrator output voltage, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From input voltage to integrator output voltage, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording integrator output voltage while applying input voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of input voltage are applied while recording integrator output voltage, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering input voltage together with the recorded quantities integrator output voltage, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from input voltage to integrator output voltage is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

integrator output voltage

### Actuators

input voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 32. Loudspeaker electromechanical model with drive circuit

### Control Problem Description

Use amplifier voltage as the available control or test action and continuously record cone displacement, coil current; when the bounded input returns to its baseline, an integrating or non-restoring mode lets cone displacement retain an offset or drift after the prescribed drive is removed. After a small reversible change in amplifier voltage, observe cone displacement; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from amplifier voltage to cone displacement, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From amplifier voltage to cone displacement, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording cone displacement, coil current while applying amplifier voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of amplifier voltage are applied while recording cone displacement, coil current, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering amplifier voltage together with the recorded quantities cone displacement, coil current, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from amplifier voltage to cone displacement is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

cone displacement, coil current

### Actuators

amplifier voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 33. DC-motor position and speed models

### Control Problem Description

Use armature voltage as the available control or test action and continuously record motor position, speed, armature current; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in armature voltage, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from armature voltage to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From armature voltage to motor position, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording motor position, speed, armature current while applying armature voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of armature voltage are applied while recording motor position, speed, armature current, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering armature voltage together with the recorded quantities motor position, speed, armature current, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from armature voltage to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

motor position, speed, armature current

### Actuators

armature voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 34. Gear-train torque multiplication and reflected inertia

### Control Problem Description

Use motor torque as the available control or test action and continuously record motor and load angle, shaft torque; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor retain an offset or drift after the prescribed drive is removed. After a small reversible change in motor torque, observe motor; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from motor torque to motor, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From motor torque to motor, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor and load angle, shaft torque while applying motor torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of motor torque are applied while recording motor and load angle, shaft torque, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering motor torque together with the recorded quantities motor and load angle, shaft torque, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from motor torque to motor is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

motor and load angle, shaft torque

### Actuators

motor torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 35. Room heat-loss model

### Control Problem Description

Use heating rate in the labeled control extension as the available control or test action and continuously record room temperature; when the bounded input returns to its baseline, no autonomous mode grows and room temperature settles or remains bounded. After a small reversible change in heating rate in the labeled control extension, observe room temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from heating rate in the labeled control extension to room temperature, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From heating rate in the labeled control extension to room temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording room temperature while applying heating rate in the labeled control extension makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of heating rate in the labeled control extension are applied while recording room temperature, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering heating rate in the labeled control extension together with the recorded quantities room temperature, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from heating rate in the labeled control extension to room temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

room temperature

### Actuators

heating rate in the labeled control extension

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

20.0

---

## 36. Two-thermal-mass controlled process

### Control Problem Description

Use heater power as the available control or test action and continuously record two body temperatures; when the bounded input returns to its baseline, no autonomous mode grows and two body temperatures settles or remains bounded. After a small reversible change in heater power, observe two body temperatures; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from heater power to two body temperatures, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From heater power to two body temperatures, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording two body temperatures while applying heater power makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of heater power are applied while recording two body temperatures, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering heater power together with the recorded quantities two body temperatures, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from heater power to two body temperatures is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

two body temperatures

### Actuators

heater power

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

20.0

---

## 37. Heat exchanger with nonlinear valve and measurement delay

### Control Problem Description

Use steam inlet valve area as the available control or test action and continuously record measured outlet water temperature; when the bounded input returns to its baseline, no autonomous mode grows and measured outlet water temperature settles or remains bounded. After a small reversible change in steam inlet valve area, observe measured outlet water temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from steam inlet valve area to measured outlet water temperature, heat transport and temperature measurement hold back the outlet response, and a visible pause separates the command from the first recorded response. From steam inlet valve area to measured outlet water temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording measured outlet water temperature while applying steam inlet valve area makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of steam inlet valve area are applied while recording measured outlet water temperature, steam-valve geometry gives a static flow map before the delayed thermal dynamics, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering steam inlet valve area together with the recorded quantities measured outlet water temperature, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from steam inlet valve area to measured outlet water temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

measured outlet water temperature

### Actuators

steam inlet valve area

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

20.0

---

## 38. Water-tank continuity, square-root outflow, and operating-point linearization

### Control Problem Description

Start from a fixed liquid-level operating point and use inlet mass flow as the available control or test action and continuously record tank level and outlet flow; when the bounded input returns to its baseline, no autonomous mode grows and tank level settles or remains bounded. After a small reversible change in inlet mass flow, observe tank level; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from inlet mass flow to tank level, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From inlet mass flow to tank level, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording tank level and outlet flow while applying inlet mass flow makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of inlet mass flow are applied while recording tank level and outlet flow, tank outflow follows a static square-root level law around the selected operating point, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering inlet mass flow together with the recorded quantities tank level and outlet flow, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from inlet mass flow to tank level is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

tank level and outlet flow

### Actuators

inlet mass flow

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 39. Pressure-driven hydraulic piston

### Control Problem Description

Use chamber pressure difference as the available control or test action and continuously record piston position and velocity; when the bounded input returns to its baseline, an integrating or non-restoring mode lets piston position retain an offset or drift after the prescribed drive is removed. After a small reversible change in chamber pressure difference, observe piston position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from chamber pressure difference to piston position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From chamber pressure difference to piston position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording piston position and velocity while applying chamber pressure difference makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of chamber pressure difference are applied while recording piston position and velocity, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering chamber pressure difference together with the recorded quantities piston position and velocity, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from chamber pressure difference to piston position is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

piston position and velocity

### Actuators

chamber pressure difference

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 40. Hydraulic control-surface actuator and load-dependent integrator model

### Control Problem Description

Use servo valve displacement as the available control or test action and continuously record surface angle and load force; when the bounded input returns to its baseline, an integrating or non-restoring mode lets surface angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in servo valve displacement, observe surface angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from servo valve displacement to surface angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From servo valve displacement to surface angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording surface angle and load force while applying servo valve displacement makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of servo valve displacement are applied while recording surface angle and load force, hydraulic flow gain and surface motion change with load force and valve operating point, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering servo valve displacement together with the recorded quantities surface angle and load force, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from servo valve displacement to surface angle is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

surface angle and load force

### Actuators

servo valve displacement

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 41. Test linearity and time invariance by superposition and shift

### Control Problem Description

Use prescribed test signal as the available control or test action and continuously record system output response; when the bounded input returns to its baseline, no autonomous mode grows and system output response settles or remains bounded. After a small reversible change in prescribed test signal, observe system output response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed test signal to system output response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From prescribed test signal to system output response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording system output response while applying prescribed test signal makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed test signal are applied while recording system output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed test signal together with the recorded quantities system output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from prescribed test signal to system output response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

system output response

### Actuators

prescribed test signal

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 42. Derive a first-order impulse response and arbitrary-input convolution

### Control Problem Description

Use input signal as the available control or test action and continuously record output response; when the bounded input returns to its baseline, no autonomous mode grows and output response settles or remains bounded. After a small reversible change in input signal, observe output response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from input signal to output response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From input signal to output response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording output response while applying input signal makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of input signal are applied while recording output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering input signal together with the recorded quantities output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from input signal to output response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

output response

### Actuators

input signal

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 43. Convert an ODE to a transfer function under zero initial conditions

### Control Problem Description

Use prescribed forcing signal as the available control or test action and continuously record system output response; when the bounded input returns to its baseline, no autonomous mode grows and system output response settles or remains bounded. After a small reversible change in prescribed forcing signal, observe system output response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed forcing signal to system output response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From prescribed forcing signal to system output response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording system output response while applying prescribed forcing signal makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed forcing signal are applied while recording system output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed forcing signal together with the recorded quantities system output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from prescribed forcing signal to system output response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

system output response

### Actuators

prescribed forcing signal

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 44. Derive the RC low-pass transfer function and impulse response

### Control Problem Description

Use input voltage as the available control or test action and continuously record capacitor voltage; when the bounded input returns to its baseline, no autonomous mode grows and capacitor voltage settles or remains bounded. After a small reversible change in input voltage, observe capacitor voltage; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from input voltage to capacitor voltage, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From input voltage to capacitor voltage, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording capacitor voltage while applying input voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of input voltage are applied while recording capacitor voltage, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering input voltage together with the recorded quantities capacitor voltage, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from input voltage to capacitor voltage is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

capacitor voltage

### Actuators

input voltage

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 45. Compute magnitude and phase of first-order sinusoidal response

### Control Problem Description

Use sinusoidal input as the available control or test action and continuously record sinusoidal output amplitude and phase; when the bounded input returns to its baseline, no autonomous mode grows and sinusoidal output amplitude settles or remains bounded. After a small reversible change in sinusoidal input, observe sinusoidal output amplitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sinusoidal input to sinusoidal output amplitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From sinusoidal input to sinusoidal output amplitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sinusoidal output amplitude and phase while applying sinusoidal input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sinusoidal input are applied while recording sinusoidal output amplitude and phase, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sinusoidal input together with the recorded quantities sinusoidal output amplitude and phase, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sinusoidal input to sinusoidal output amplitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sinusoidal output amplitude and phase

### Actuators

sinusoidal input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 46. Transform canonical step, ramp, impulse, and sinusoidal inputs

### Control Problem Description

Use canonical test signal as the available control or test action and continuously record transformed system response; when the bounded input returns to its baseline, no autonomous mode grows and transformed system response settles or remains bounded. After a small reversible change in canonical test signal, observe transformed system response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from canonical test signal to transformed system response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From canonical test signal to transformed system response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording transformed system response while applying canonical test signal makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of canonical test signal are applied while recording transformed system response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering canonical test signal together with the recorded quantities transformed system response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from canonical test signal to transformed system response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

transformed system response

### Actuators

canonical test signal

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 47. Recover a time response by partial-fraction expansion

### Control Problem Description

Use prescribed transformed input as the available control or test action and continuously record time-domain output response; when the bounded input returns to its baseline, no autonomous mode grows and time-domain output response settles or remains bounded. After a small reversible change in prescribed transformed input, observe time-domain output response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed transformed input to time-domain output response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From prescribed transformed input to time-domain output response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording time-domain output response while applying prescribed transformed input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed transformed input are applied while recording time-domain output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed transformed input together with the recorded quantities time-domain output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from prescribed transformed input to time-domain output response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

time-domain output response

### Actuators

prescribed transformed input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 48. Apply the Final Value Theorem and reject invalid unstable use

### Control Problem Description

Use test input as the available control or test action and continuously record steady-state output; when the bounded input returns to its baseline, no autonomous mode grows and steady-state output settles or remains bounded. After a small reversible change in test input, observe steady-state output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from test input to steady-state output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From test input to steady-state output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording steady-state output while applying test input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of test input are applied while recording steady-state output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering test input together with the recorded quantities steady-state output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from test input to steady-state output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

steady-state output

### Actuators

test input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 49. Compute stable-system DC gain from the transfer function

### Control Problem Description

Use unit-step input as the available control or test action and continuously record steady output; when the bounded input returns to its baseline, no autonomous mode grows and steady output settles or remains bounded. After a small reversible change in unit-step input, observe steady output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from unit-step input to steady output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From unit-step input to steady output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording steady output while applying unit-step input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of unit-step input are applied while recording steady output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering unit-step input together with the recorded quantities steady output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from unit-step input to steady output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

steady output

### Actuators

unit-step input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 50. Solve homogeneous and forced ODEs with initial conditions

### Control Problem Description

Use forcing input and prescribed initial-state release as the available control or test action and continuously record state and output response; when the bounded input returns to its baseline, no autonomous mode grows and state settles or remains bounded. After a small reversible change in forcing input and prescribed initial-state release, observe state; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from forcing input and prescribed initial-state release to state, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From forcing input and prescribed initial-state release to state, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording state and output response while applying forcing input and prescribed initial-state release makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of forcing input and prescribed initial-state release are applied while recording state and output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering forcing input and prescribed initial-state release together with the recorded quantities state and output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from forcing input and prescribed initial-state release to state is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

state and output response

### Actuators

forcing input and prescribed initial-state release

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 51. Analyze automobile position dynamics from the cruise model

### Control Problem Description

Use drive force as the available control or test action and continuously record vehicle position and speed; when the bounded input returns to its baseline, an integrating or non-restoring mode lets vehicle position retain an offset or drift after the prescribed drive is removed. After a small reversible change in drive force, observe vehicle position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from drive force to vehicle position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From drive force to vehicle position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording vehicle position and speed while applying drive force makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of drive force are applied while recording vehicle position and speed, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering drive force together with the recorded quantities vehicle position and speed, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from drive force to vehicle position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

vehicle position and speed

### Actuators

drive force

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 52. Analyze DC-motor position and speed poles with numerical parameters

### Control Problem Description

Use armature voltage as the available control or test action and continuously record motor speed and position; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor speed retain an offset or drift after the prescribed drive is removed. After a small reversible change in armature voltage, observe motor speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from armature voltage to motor speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From armature voltage to motor speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor speed and position while applying armature voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of armature voltage are applied while recording motor speed and position, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering armature voltage together with the recorded quantities motor speed and position, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from armature voltage to motor speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor speed and position

### Actuators

armature voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 53. Predict rigid-satellite response to a finite thrust pulse

### Control Problem Description

Use finite thruster-force pulse as the available control or test action and continuously record attitude angle and rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets attitude angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in finite thruster-force pulse, observe attitude angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from finite thruster-force pulse to attitude angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From finite thruster-force pulse to attitude angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording attitude angle and rate while applying finite thruster-force pulse makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of finite thruster-force pulse are applied while recording attitude angle and rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering finite thruster-force pulse together with the recorded quantities attitude angle and rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from finite thruster-force pulse to attitude angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

attitude angle and rate

### Actuators

finite thruster-force pulse

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 54. Reduce nested control block diagrams to one transfer function

### Control Problem Description

Use reference input as the available control or test action and continuously record closed-loop output; when the bounded input returns to its baseline, no autonomous mode grows and closed-loop output settles or remains bounded. After a small reversible change in reference input, observe closed-loop output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from reference input to closed-loop output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From reference input to closed-loop output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording closed-loop output while applying reference input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of reference input are applied while recording closed-loop output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering reference input together with the recorded quantities closed-loop output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from reference input to closed-loop output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output

### Actuators

reference input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 55. Derive a closed-loop transfer function with Mason's signal-flow rule

### Control Problem Description

Use prescribed source-node signal as the available control or test action and continuously record signal-flow output response; when the bounded input returns to its baseline, no autonomous mode grows and signal-flow output response settles or remains bounded. After a small reversible change in prescribed source-node signal, observe signal-flow output response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed source-node signal to signal-flow output response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From prescribed source-node signal to signal-flow output response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording signal-flow output response while applying prescribed source-node signal makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed source-node signal are applied while recording signal-flow output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed source-node signal together with the recorded quantities signal-flow output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from prescribed source-node signal to signal-flow output response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

signal-flow output response

### Actuators

prescribed source-node signal

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 56. Infer transient form and decay rate from pole locations

### Control Problem Description

Use bounded impulse test as the available control or test action and continuously record transient output response; when the bounded input returns to its baseline, no autonomous mode grows and transient output response settles or remains bounded. After a small reversible change in bounded impulse test, observe transient output response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded impulse test to transient output response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded impulse test to transient output response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording transient output response while applying bounded impulse test makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded impulse test are applied while recording transient output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded impulse test together with the recorded quantities transient output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded impulse test to transient output response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

transient output response

### Actuators

bounded impulse test

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 57. Map second-order rise time, overshoot, settling time, and peak time to pole regions

### Control Problem Description

Use bounded command step as the available control or test action and continuously record step response and its transient features; when the bounded input returns to its baseline, no autonomous mode grows and step response settles or remains bounded. After a small reversible change in bounded command step, observe step response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded command step to step response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded command step to step response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording step response and its transient features while applying bounded command step makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded command step are applied while recording step response and its transient features, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded command step together with the recorded quantities step response and its transient features, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded command step to step response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

step response and its transient features

### Actuators

bounded command step

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 58. Explain and quantify Boeing 747 nonminimum-phase altitude response

### Control Problem Description

Use impulsive elevator deflection as the available control or test action and continuously record aircraft altitude; when the bounded input returns to its baseline, an integrating or non-restoring mode lets aircraft altitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in impulsive elevator deflection, observe aircraft altitude; the first useful output change moves in an unfavorable or opposite direction before turning toward its eventual value. For the same small change from impulsive elevator deflection to aircraft altitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From impulsive elevator deflection to aircraft altitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording aircraft altitude while applying impulsive elevator deflection makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of impulsive elevator deflection are applied while recording aircraft altitude, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering impulsive elevator deflection together with the recorded quantities aircraft altitude, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from impulsive elevator deflection to aircraft altitude is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

aircraft altitude

### Actuators

impulsive elevator deflection

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 59. Test BIBO stability of a current-driven capacitor

### Control Problem Description

Use bounded source current as the available control or test action and continuously record capacitor voltage; when the bounded input returns to its baseline, an integrating or non-restoring mode lets capacitor voltage retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded source current, observe capacitor voltage; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded source current to capacitor voltage, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded source current to capacitor voltage, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording capacitor voltage while applying bounded source current makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded source current are applied while recording capacitor voltage, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded source current together with the recorded quantities capacitor voltage, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded source current to capacitor voltage is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

capacitor voltage

### Actuators

bounded source current

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 60. Determine proportional and PI gain stability regions with the Routh criterion

### Control Problem Description

Use bounded controller command during proportional and integral setting sweeps as the available control or test action and continuously record regulated output response across the tested settings; when the bounded input returns to its baseline, the first Routh-design case retains a growing mode until a stabilizing controller setting is introduced, so the deviation continues to grow rather than return. After a small reversible change in bounded controller command during proportional and integral setting sweeps, observe regulated output response across the tested settings; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded controller command during proportional and integral setting sweeps to regulated output response across the tested settings, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded controller command during proportional and integral setting sweeps to regulated output response across the tested settings, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording regulated output response across the tested settings while applying bounded controller command during proportional and integral setting sweeps makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded controller command during proportional and integral setting sweeps are applied while recording regulated output response across the tested settings, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded controller command during proportional and integral setting sweeps together with the recorded quantities regulated output response across the tested settings, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded controller command during proportional and integral setting sweeps to regulated output response across the tested settings is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

regulated output response across the tested settings

### Actuators

bounded controller command during proportional and integral setting sweeps

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 61. Derive closed-loop reference, disturbance, sensor-noise, control, and error maps using sensitivity and complementary sensitivity

### Control Problem Description

Use reference command with prescribed plant disturbance and sensor noise as the available control or test action and continuously record regulated output, tracking error, and control effort; when the bounded input returns to its baseline, no autonomous mode grows and regulated output settles or remains bounded. After a small reversible change in reference command with prescribed plant disturbance and sensor noise, observe regulated output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from reference command with prescribed plant disturbance and sensor noise to regulated output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From reference command with prescribed plant disturbance and sensor noise to regulated output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording regulated output, tracking error, and control effort while applying reference command with prescribed plant disturbance and sensor noise makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of reference command with prescribed plant disturbance and sensor noise are applied while recording regulated output, tracking error, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering reference command with prescribed plant disturbance and sensor noise together with the recorded quantities regulated output, tracking error, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from reference command with prescribed plant disturbance and sensor noise to regulated output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

regulated output, tracking error, and control effort

### Actuators

reference command with prescribed plant disturbance and sensor noise

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 62. Stabilize an unstable inverted-pendulum model by feedback characteristic-equation design

### Control Problem Description

Use bounded dynamic-compensator command as the available control or test action and continuously record pendulum angle and compensator output; when the bounded input returns to its baseline, the inverted-pendulum angle moves farther from upright after a small displacement unless the dynamic compensator closes the loop, so the deviation continues to grow rather than return. After a small reversible change in bounded dynamic-compensator command, observe pendulum angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded dynamic-compensator command to pendulum angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded dynamic-compensator command to pendulum angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pendulum angle and compensator output while applying bounded dynamic-compensator command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded dynamic-compensator command are applied while recording pendulum angle and compensator output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded dynamic-compensator command together with the recorded quantities pendulum angle and compensator output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded dynamic-compensator command to pendulum angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

pendulum angle and compensator output

### Actuators

bounded dynamic-compensator command

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 63. Quantify feedback reduction of plant-gain sensitivity

### Control Problem Description

Use bounded controller command as the available control or test action and continuously record regulated output and tracking error; when the bounded input returns to its baseline, no autonomous mode grows and regulated output settles or remains bounded. After a small reversible change in bounded controller command, observe regulated output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded controller command to regulated output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded controller command to regulated output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording regulated output and tracking error while applying bounded controller command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded controller command are applied while recording regulated output and tracking error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded controller command together with the recorded quantities regulated output and tracking error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded controller command to regulated output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

regulated output and tracking error

### Actuators

bounded controller command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 64. Resolve low-frequency plant-disturbance rejection versus high-frequency sensor-noise attenuation

### Control Problem Description

Use plant disturbance and sensor-noise test inputs as the available control or test action and continuously record regulated output, error, and sensor-noise response; when the bounded input returns to its baseline, no autonomous mode grows and regulated output settles or remains bounded. After a small reversible change in plant disturbance and sensor-noise test inputs, observe regulated output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from plant disturbance and sensor-noise test inputs to regulated output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From plant disturbance and sensor-noise test inputs to regulated output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording regulated output, error, and sensor-noise response while applying plant disturbance and sensor-noise test inputs makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of plant disturbance and sensor-noise test inputs are applied while recording regulated output, error, and sensor-noise response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering plant disturbance and sensor-noise test inputs together with the recorded quantities regulated output, error, and sensor-noise response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from plant disturbance and sensor-noise test inputs to regulated output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

regulated output, error, and sensor-noise response

### Actuators

plant disturbance and sensor-noise test inputs

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 65. Compute Type 0 speed-control error with proportional feedback

### Control Problem Description

Use proportional control command as the available control or test action and continuously record speed and tracking error; when the bounded input returns to its baseline, no autonomous mode grows and speed settles or remains bounded. After a small reversible change in proportional control command, observe speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from proportional control command to speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From proportional control command to speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording speed and tracking error while applying proportional control command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of proportional control command are applied while recording speed and tracking error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering proportional control command together with the recorded quantities speed and tracking error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from proportional control command to speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

speed and tracking error

### Actuators

proportional control command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 66. Raise speed control to Type 1 with integral action

### Control Problem Description

Use PI control command as the available control or test action and continuously record speed and tracking error; when the bounded input returns to its baseline, no autonomous mode grows and speed settles or remains bounded. After a small reversible change in PI control command, observe speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from PI control command to speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From PI control command to speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording speed and tracking error while applying PI control command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of PI control command are applied while recording speed and tracking error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering PI control command together with the recorded quantities speed and tracking error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from PI control command to speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

speed and tracking error

### Actuators

PI control command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 67. Evaluate system type and velocity constant with tachometer feedback

### Control Problem Description

Use armature voltage under tachometer feedback as the available control or test action and continuously record motor position, speed, and tracking error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in armature voltage under tachometer feedback, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from armature voltage under tachometer feedback to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From armature voltage under tachometer feedback to motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor position, speed, and tracking error while applying armature voltage under tachometer feedback makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of armature voltage under tachometer feedback are applied while recording motor position, speed, and tracking error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering armature voltage under tachometer feedback together with the recorded quantities motor position, speed, and tracking error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from armature voltage under tachometer feedback to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor position, speed, and tracking error

### Actuators

armature voltage under tachometer feedback

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 68. Compare P and PI rejection of DC-motor torque disturbances

### Control Problem Description

Use armature voltage with prescribed load-torque disturbance as the available control or test action and continuously record motor position, speed, and disturbance response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in armature voltage with prescribed load-torque disturbance, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from armature voltage with prescribed load-torque disturbance to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From armature voltage with prescribed load-torque disturbance to motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor position, speed, and disturbance response while applying armature voltage with prescribed load-torque disturbance makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of armature voltage with prescribed load-torque disturbance are applied while recording motor position, speed, and disturbance response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering armature voltage with prescribed load-torque disturbance together with the recorded quantities motor position, speed, and disturbance response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from armature voltage with prescribed load-torque disturbance to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor position, speed, and disturbance response

### Actuators

armature voltage with prescribed load-torque disturbance

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 69. Tune proportional control while exposing speed/offset/damping tradeoffs

### Control Problem Description

Use proportional actuator command as the available control or test action and continuously record regulated output, tracking error, and control effort; when the bounded input returns to its baseline, no autonomous mode grows and regulated output settles or remains bounded. After a small reversible change in proportional actuator command, observe regulated output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from proportional actuator command to regulated output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From proportional actuator command to regulated output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording regulated output, tracking error, and control effort while applying proportional actuator command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of proportional actuator command are applied while recording regulated output, tracking error, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering proportional actuator command together with the recorded quantities regulated output, tracking error, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from proportional actuator command to regulated output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

regulated output, tracking error, and control effort

### Actuators

proportional actuator command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 70. Use integral control for robust zero step error and constant-disturbance rejection

### Control Problem Description

Use integral control command and test disturbance as the available control or test action and continuously record tracking error, plant output, and control effort; when the bounded input returns to its baseline, no autonomous mode grows and tracking error settles or remains bounded. After a small reversible change in integral control command and test disturbance, observe tracking error; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from integral control command and test disturbance to tracking error, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From integral control command and test disturbance to tracking error, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording tracking error, plant output, and control effort while applying integral control command and test disturbance makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of integral control command and test disturbance are applied while recording tracking error, plant output, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering integral control command and test disturbance together with the recorded quantities tracking error, plant output, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from integral control command and test disturbance to tracking error is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

tracking error, plant output, and control effort

### Actuators

integral control command and test disturbance

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 71. Use derivative/rate feedback to add damping without derivative kick

### Control Problem Description

Use proportional and rate command as the available control or test action and continuously record output and output rate; when the bounded input returns to its baseline, no autonomous mode grows and output settles or remains bounded. After a small reversible change in proportional and rate command, observe output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from proportional and rate command to output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From proportional and rate command to output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording output and output rate while applying proportional and rate command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of proportional and rate command are applied while recording output and output rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering proportional and rate command together with the recorded quantities output and output rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from proportional and rate command to output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

output and output rate

### Actuators

proportional and rate command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 72. Design PI control for a two-thermal-mass process

### Control Problem Description

Use heater command as the available control or test action and continuously record controlled temperature and control effort; when the bounded input returns to its baseline, no autonomous mode grows and controlled temperature settles or remains bounded. After a small reversible change in heater command, observe controlled temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from heater command to controlled temperature, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From heater command to controlled temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording controlled temperature and control effort while applying heater command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of heater command are applied while recording controlled temperature and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering heater command together with the recorded quantities controlled temperature and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from heater command to controlled temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

controlled temperature and control effort

### Actuators

heater command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

20.0

---

## 73. Compare P, PI, and PID on DC-motor speed

### Control Problem Description

Use armature voltage with prescribed load-torque disturbance as the available control or test action and continuously record motor speed, tracking error, and disturbance response; when the bounded input returns to its baseline, no autonomous mode grows and motor speed settles or remains bounded. After a small reversible change in armature voltage with prescribed load-torque disturbance, observe motor speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from armature voltage with prescribed load-torque disturbance to motor speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From armature voltage with prescribed load-torque disturbance to motor speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor speed, tracking error, and disturbance response while applying armature voltage with prescribed load-torque disturbance makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of armature voltage with prescribed load-torque disturbance are applied while recording motor speed, tracking error, and disturbance response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering armature voltage with prescribed load-torque disturbance together with the recorded quantities motor speed, tracking error, and disturbance response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from armature voltage with prescribed load-torque disturbance to motor speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor speed, tracking error, and disturbance response

### Actuators

armature voltage with prescribed load-torque disturbance

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 74. Analyze P/PI DC-motor position disturbance types with non-unity sensing

### Control Problem Description

Use motor voltage with prescribed disturbance torque as the available control or test action and continuously record motor position, speed, and sensed error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in motor voltage with prescribed disturbance torque, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from motor voltage with prescribed disturbance torque to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From motor voltage with prescribed disturbance torque to motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor position, speed, and sensed error while applying motor voltage with prescribed disturbance torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of motor voltage with prescribed disturbance torque are applied while recording motor position, speed, and sensed error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering motor voltage with prescribed disturbance torque together with the recorded quantities motor position, speed, and sensed error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from motor voltage with prescribed disturbance torque to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor position, speed, and sensed error

### Actuators

motor voltage with prescribed disturbance torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 75. Compare satellite PD and PID system type for reference and disturbance inputs

### Control Problem Description

Use body-torque command with prescribed disturbance torque as the available control or test action and continuously record attitude angle, angular rate, and tracking error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets attitude angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in body-torque command with prescribed disturbance torque, observe attitude angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from body-torque command with prescribed disturbance torque to attitude angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From body-torque command with prescribed disturbance torque to attitude angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording attitude angle, angular rate, and tracking error while applying body-torque command with prescribed disturbance torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of body-torque command with prescribed disturbance torque are applied while recording attitude angle, angular rate, and tracking error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering body-torque command with prescribed disturbance torque together with the recorded quantities attitude angle, angular rate, and tracking error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from body-torque command with prescribed disturbance torque to attitude angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

attitude angle, angular rate, and tracking error

### Actuators

body-torque command with prescribed disturbance torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 76. Tune a PID from a process reaction curve for quarter-decay behavior

### Control Problem Description

Use P, PI, or PID process command as the available control or test action and continuously record process output and quarter-decay response; when the bounded input returns to its baseline, no autonomous mode grows and process output settles or remains bounded. After a small reversible change in P, PI, or PID process command, observe process output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from P, PI, or PID process command to process output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From P, PI, or PID process command to process output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording process output and quarter-decay response while applying P, PI, or PID process command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of P, PI, or PID process command are applied while recording process output and quarter-decay response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering P, PI, or PID process command together with the recorded quantities process output and quarter-decay response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from P, PI, or PID process command to process output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

process output and quarter-decay response

### Actuators

P, PI, or PID process command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 77. Tune P/PI/PID from ultimate gain and ultimate period

### Control Problem Description

Use proportional or PID process command as the available control or test action and continuously record marginal oscillation and tuned response; when the bounded input returns to its baseline, no autonomous mode grows and marginal oscillation settles or remains bounded. After a small reversible change in proportional or PID process command, observe marginal oscillation; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from proportional or PID process command to marginal oscillation, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From proportional or PID process command to marginal oscillation, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording marginal oscillation and tuned response while applying proportional or PID process command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of proportional or PID process command are applied while recording marginal oscillation and tuned response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering proportional or PID process command together with the recorded quantities marginal oscillation and tuned response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from proportional or PID process command to marginal oscillation is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

marginal oscillation and tuned response

### Actuators

proportional or PID process command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 78. Apply reaction-curve Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

Use steam-valve P or PI command as the available control or test action and continuously record heat-exchanger temperature and step response; when the bounded input returns to its baseline, no autonomous mode grows and heat-exchanger temperature settles or remains bounded. After a small reversible change in steam-valve P or PI command, observe heat-exchanger temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from steam-valve P or PI command to heat-exchanger temperature, heat transport and temperature measurement hold back the outlet response, and a visible pause separates the command from the first recorded response. From steam-valve P or PI command to heat-exchanger temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording heat-exchanger temperature and step response while applying steam-valve P or PI command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of steam-valve P or PI command are applied while recording heat-exchanger temperature and step response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering steam-valve P or PI command together with the recorded quantities heat-exchanger temperature and step response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from steam-valve P or PI command to heat-exchanger temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

heat-exchanger temperature and step response

### Actuators

steam-valve P or PI command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

20.0

---

## 79. Apply ultimate-sensitivity Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

Use steam-valve P or PI command as the available control or test action and continuously record heat-exchanger temperature and oscillation; when the bounded input returns to its baseline, no autonomous mode grows and heat-exchanger temperature settles or remains bounded. After a small reversible change in steam-valve P or PI command, observe heat-exchanger temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from steam-valve P or PI command to heat-exchanger temperature, heat transport and temperature measurement hold back the outlet response, and a visible pause separates the command from the first recorded response. From steam-valve P or PI command to heat-exchanger temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording heat-exchanger temperature and oscillation while applying steam-valve P or PI command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of steam-valve P or PI command are applied while recording heat-exchanger temperature and oscillation, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering steam-valve P or PI command together with the recorded quantities heat-exchanger temperature and oscillation, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from steam-valve P or PI command to heat-exchanger temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

heat-exchanger temperature and oscillation

### Actuators

steam-valve P or PI command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

20.0

---

## 80. Add inverse-DC-gain feedforward to DC-motor tracking and measured-disturbance rejection

### Control Problem Description

Use armature voltage combining feedback and feedforward as the available control or test action and continuously record motor speed, tracking error, and disturbance response; when the bounded input returns to its baseline, no autonomous mode grows and motor speed settles or remains bounded. After a small reversible change in armature voltage combining feedback and feedforward, observe motor speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from armature voltage combining feedback and feedforward to motor speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From armature voltage combining feedback and feedforward to motor speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor speed, tracking error, and disturbance response while applying armature voltage combining feedback and feedforward makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of armature voltage combining feedback and feedforward are applied while recording motor speed, tracking error, and disturbance response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering armature voltage combining feedback and feedforward together with the recorded quantities motor speed, tracking error, and disturbance response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from armature voltage combining feedback and feedforward to motor speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor speed, tracking error, and disturbance response

### Actuators

armature voltage combining feedback and feedforward

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 81. Draw and parameterize the DC-motor position-control root locus

### Control Problem Description

Use motor armature voltage as the available control or test action and continuously record motor position and tracking response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in motor armature voltage, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from motor armature voltage to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From motor armature voltage to motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor position and tracking response while applying motor armature voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of motor armature voltage are applied while recording motor position and tracking response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering motor armature voltage together with the recorded quantities motor position and tracking response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from motor armature voltage to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor position and tracking response

### Actuators

motor armature voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 82. Draw a root locus with respect to a physical damping/pole parameter

### Control Problem Description

Use bounded modal test input while damping is varied as the available control or test action and continuously record modal response and decay envelope; when the bounded input returns to its baseline, an integrating or non-restoring mode lets modal response retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded modal test input while damping is varied, observe modal response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded modal test input while damping is varied to modal response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded modal test input while damping is varied to modal response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording modal response and decay envelope while applying bounded modal test input while damping is varied makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded modal test input while damping is varied are applied while recording modal response and decay envelope, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded modal test input while damping is varied together with the recorded quantities modal response and decay envelope, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded modal test input while damping is varied to modal response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

modal response and decay envelope

### Actuators

bounded modal test input while damping is varied

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 83. Construct a higher-order locus from Evans phase, real-axis, asymptote, departure, and gain rules

### Control Problem Description

Use bounded command during a loop-strength sweep as the available control or test action and continuously record controlled output and transient response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets controlled output retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded command during a loop-strength sweep, observe controlled output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded command during a loop-strength sweep to controlled output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded command during a loop-strength sweep to controlled output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording controlled output and transient response while applying bounded command during a loop-strength sweep makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded command during a loop-strength sweep are applied while recording controlled output and transient response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded command during a loop-strength sweep together with the recorded quantities controlled output and transient response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded command during a loop-strength sweep to controlled output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

controlled output and transient response

### Actuators

bounded command during a loop-strength sweep

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 84. Stabilize a satellite double integrator with PD control

### Control Problem Description

Use PD body-torque command as the available control or test action and continuously record satellite attitude and angular rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets satellite attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in PD body-torque command, observe satellite attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from PD body-torque command to satellite attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From PD body-torque command to satellite attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording satellite attitude and angular rate while applying PD body-torque command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of PD body-torque command are applied while recording satellite attitude and angular rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering PD body-torque command together with the recorded quantities satellite attitude and angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from PD body-torque command to satellite attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

satellite attitude and angular rate

### Actuators

PD body-torque command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 85. Quantify how a finite lead pole changes the satellite PD locus, including the 9:1 transition

### Control Problem Description

Use lead-compensated body torque as the available control or test action and continuously record satellite attitude and angular rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets satellite attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in lead-compensated body torque, observe satellite attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from lead-compensated body torque to satellite attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From lead-compensated body torque to satellite attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording satellite attitude and angular rate while applying lead-compensated body torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of lead-compensated body torque are applied while recording satellite attitude and angular rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering lead-compensated body torque together with the recorded quantities satellite attitude and angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from lead-compensated body torque to satellite attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

satellite attitude and angular rate

### Actuators

lead-compensated body torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 86. Analyze collocated satellite flexibility and flexible-mode damping

### Control Problem Description

Use collocated body torque as the available control or test action and continuously record collocated attitude and flexible deflection; when the bounded input returns to its baseline, an integrating or non-restoring mode lets collocated attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in collocated body torque, observe collocated attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from collocated body torque to collocated attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From collocated body torque to collocated attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording collocated attitude and flexible deflection while applying collocated body torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of collocated body torque are applied while recording collocated attitude and flexible deflection, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering collocated body torque together with the recorded quantities collocated attitude and flexible deflection, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from collocated body torque to collocated attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

collocated attitude and flexible deflection

### Actuators

collocated body torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 87. Analyze noncollocated satellite flexibility and spillover instability

### Control Problem Description

Use main-body torque as the available control or test action and continuously record remote attitude and flexible deflection; when the bounded input returns to its baseline, an integrating or non-restoring mode lets remote attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in main-body torque, observe remote attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from main-body torque to remote attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From main-body torque to remote attitude, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording remote attitude and flexible deflection while applying main-body torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of main-body torque are applied while recording remote attitude and flexible deflection, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering main-body torque together with the recorded quantities remote attitude and flexible deflection, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from main-body torque to remote attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

remote attitude and flexible deflection

### Actuators

main-body torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 88. Handle complex multiple roots on a fourth-order locus

### Control Problem Description

Use bounded command during a loop-strength sweep as the available control or test action and continuously record closed-loop output near the repeated-root condition; when the bounded input returns to its baseline, an integrating or non-restoring mode lets closed-loop output near the repeated-root condition retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded command during a loop-strength sweep, observe closed-loop output near the repeated-root condition; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded command during a loop-strength sweep to closed-loop output near the repeated-root condition, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded command during a loop-strength sweep to closed-loop output near the repeated-root condition, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording closed-loop output near the repeated-root condition while applying bounded command during a loop-strength sweep makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded command during a loop-strength sweep are applied while recording closed-loop output near the repeated-root condition, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded command during a loop-strength sweep together with the recorded quantities closed-loop output near the repeated-root condition, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded command during a loop-strength sweep to closed-loop output near the repeated-root condition is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output near the repeated-root condition

### Actuators

bounded command during a loop-strength sweep

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 89. Design lead compensation to meet rise-time and overshoot limits

### Control Problem Description

Use lead-compensated servo command as the available control or test action and continuously record servo position, tracking error, and control effort; when the bounded input returns to its baseline, an integrating or non-restoring mode lets servo position retain an offset or drift after the prescribed drive is removed. After a small reversible change in lead-compensated servo command, observe servo position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from lead-compensated servo command to servo position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From lead-compensated servo command to servo position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording servo position, tracking error, and control effort while applying lead-compensated servo command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of lead-compensated servo command are applied while recording servo position, tracking error, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering lead-compensated servo command together with the recorded quantities servo position, tracking error, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from lead-compensated servo command to servo position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

servo position, tracking error, and control effort

### Actuators

lead-compensated servo command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 90. Add lag compensation to improve velocity-error constant without moving dominant roots

### Control Problem Description

Use lead-lag servo command as the available control or test action and continuously record servo position, tracking error, and control effort; when the bounded input returns to its baseline, an integrating or non-restoring mode lets servo position retain an offset or drift after the prescribed drive is removed. After a small reversible change in lead-lag servo command, observe servo position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from lead-lag servo command to servo position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From lead-lag servo command to servo position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording servo position, tracking error, and control effort while applying lead-lag servo command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of lead-lag servo command are applied while recording servo position, tracking error, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering lead-lag servo command together with the recorded quantities servo position, tracking error, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from lead-lag servo command to servo position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

servo position, tracking error, and control effort

### Actuators

lead-lag servo command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 91. Add notch compensation for an unmodeled flexible resonance

### Control Problem Description

Use notch-filtered actuator command as the available control or test action and continuously record nominal output and flexible displacement; when the bounded input returns to its baseline, an integrating or non-restoring mode lets nominal output retain an offset or drift after the prescribed drive is removed. After a small reversible change in notch-filtered actuator command, observe nominal output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from notch-filtered actuator command to nominal output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From notch-filtered actuator command to nominal output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording nominal output and flexible displacement while applying notch-filtered actuator command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of notch-filtered actuator command are applied while recording nominal output and flexible displacement, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering notch-filtered actuator command together with the recorded quantities nominal output and flexible displacement, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from notch-filtered actuator command to nominal output is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

nominal output and flexible displacement

### Actuators

notch-filtered actuator command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 92. Realize a lead compensator with an operational-amplifier circuit

### Control Problem Description

Use input error voltage as the available control or test action and continuously record lead-network output voltage; when the bounded input returns to its baseline, no autonomous mode grows and lead-network output voltage settles or remains bounded. After a small reversible change in input error voltage, observe lead-network output voltage; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from input error voltage to lead-network output voltage, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From input error voltage to lead-network output voltage, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording lead-network output voltage while applying input error voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of input error voltage are applied while recording lead-network output voltage, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering input error voltage together with the recorded quantities lead-network output voltage, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from input error voltage to lead-network output voltage is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

lead-network output voltage

### Actuators

input error voltage

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 93. Design quadrotor pitch-axis lead compensation

### Control Problem Description

Use pitch rotor-torque command as the available control or test action and continuously record quadrotor pitch angle and angular rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets quadrotor pitch angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in pitch rotor-torque command, observe quadrotor pitch angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from pitch rotor-torque command to quadrotor pitch angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From pitch rotor-torque command to quadrotor pitch angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording quadrotor pitch angle and angular rate while applying pitch rotor-torque command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of pitch rotor-torque command are applied while recording quadrotor pitch angle and angular rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering pitch rotor-torque command together with the recorded quantities quadrotor pitch angle and angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from pitch rotor-torque command to quadrotor pitch angle is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

quadrotor pitch angle and angular rate

### Actuators

pitch rotor-torque command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 94. Design a small-airplane pitch autopilot and integral trim loop

### Control Problem Description

Use elevator and trim-tab commands as the available control or test action and continuously record pitch attitude, elevator, and trim-tab deflections; when the bounded input returns to its baseline, no autonomous mode grows and pitch attitude settles or remains bounded. After a small reversible change in elevator and trim-tab commands, observe pitch attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from elevator and trim-tab commands to pitch attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From elevator and trim-tab commands to pitch attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pitch attitude, elevator, and trim-tab deflections while applying elevator and trim-tab commands makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of elevator and trim-tab commands are applied while recording pitch attitude, elevator, and trim-tab deflections, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering elevator and trim-tab commands together with the recorded quantities pitch attitude, elevator, and trim-tab deflections, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from elevator and trim-tab commands to pitch attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

pitch attitude, elevator, and trim-tab deflections

### Actuators

elevator and trim-tab commands

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 95. Use a negative root locus for nonminimum-phase airplane altitude dynamics

### Control Problem Description

Use elevator command as the available control or test action and continuously record aircraft altitude response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets aircraft altitude response retain an offset or drift after the prescribed drive is removed. After a small reversible change in elevator command, observe aircraft altitude response; the first useful output change moves in an unfavorable or opposite direction before turning toward its eventual value. For the same small change from elevator command to aircraft altitude response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From elevator command to aircraft altitude response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording aircraft altitude response while applying elevator command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of elevator command are applied while recording aircraft altitude response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering elevator command together with the recorded quantities aircraft altitude response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from elevator command to aircraft altitude response is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

aircraft altitude response

### Actuators

elevator command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 96. Select tachometer and amplifier gains by successive loop closure

### Control Problem Description

Use servo amplifier voltage under tachometer feedback as the available control or test action and continuously record servomechanism position and speed response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets servomechanism position retain an offset or drift after the prescribed drive is removed. After a small reversible change in servo amplifier voltage under tachometer feedback, observe servomechanism position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from servo amplifier voltage under tachometer feedback to servomechanism position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From servo amplifier voltage under tachometer feedback to servomechanism position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording servomechanism position and speed response while applying servo amplifier voltage under tachometer feedback makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of servo amplifier voltage under tachometer feedback are applied while recording servomechanism position and speed response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering servo amplifier voltage under tachometer feedback together with the recorded quantities servomechanism position and speed response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from servo amplifier voltage under tachometer feedback to servomechanism position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

servomechanism position and speed response

### Actuators

servo amplifier voltage under tachometer feedback

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 97. Design inner-attitude/outer-position quadrotor cascade control

### Control Problem Description

Use outer position command and inner rotor-torque command as the available control or test action and continuously record horizontal position, pitch attitude, and angular rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets horizontal position retain an offset or drift after the prescribed drive is removed. After a small reversible change in outer position command and inner rotor-torque command, observe horizontal position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from outer position command and inner rotor-torque command to horizontal position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From outer position command and inner rotor-torque command to horizontal position, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording horizontal position, pitch attitude, and angular rate while applying outer position command and inner rotor-torque command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of outer position command and inner rotor-torque command are applied while recording horizontal position, pitch attitude, and angular rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering outer position command and inner rotor-torque command together with the recorded quantities horizontal position, pitch attitude, and angular rate, the outer response appears only through a separately stabilized inner attitude, rate, or biochemical path. When the bounded test from outer position command and inner rotor-torque command to horizontal position is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

horizontal position, pitch attitude, and angular rate

### Actuators

outer position command and inner rotor-torque command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
disable the inner stabilizing channel while testing the outer command

### Dominant Time Scale (Seconds)

5.0

---

## 98. Design a lead compensator for a numerically controlled machine-tool servo

### Control Problem Description

Use lead-compensated servo command as the available control or test action and continuously record machine-tool position, tracking error, and control effort; when the bounded input returns to its baseline, an integrating or non-restoring mode lets machine-tool position retain an offset or drift after the prescribed drive is removed. After a small reversible change in lead-compensated servo command, observe machine-tool position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from lead-compensated servo command to machine-tool position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From lead-compensated servo command to machine-tool position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording machine-tool position, tracking error, and control effort while applying lead-compensated servo command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of lead-compensated servo command are applied while recording machine-tool position, tracking error, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering lead-compensated servo command together with the recorded quantities machine-tool position, tracking error, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from lead-compensated servo command to machine-tool position is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

machine-tool position, tracking error, and control effort

### Actuators

lead-compensated servo command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 99. Linearize and stabilize an elementary magnetic suspension

### Control Problem Description

Use electromagnet current command as the available control or test action and continuously record ball position, sensor voltage, and coil current; when the bounded input returns to its baseline, magnetic force weakens in the direction that lets a displaced ball move farther from its levitation point, so the deviation continues to grow rather than return. After a small reversible change in electromagnet current command, observe ball position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from electromagnet current command to ball position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From electromagnet current command to ball position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording ball position, sensor voltage, and coil current while applying electromagnet current command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of electromagnet current command are applied while recording ball position, sensor voltage, and coil current, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering electromagnet current command together with the recorded quantities ball position, sensor voltage, and coil current, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from electromagnet current command to ball position is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

ball position, sensor voltage, and coil current

### Actuators

electromagnet current command

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 100. Design yaw-rate-aided heading control for the USCG cutter Tampa under wind disturbance

### Control Problem Description

Use rudder command and prescribed wind-gust input as the available control or test action and continuously record ship heading, yaw rate, rudder angle, and wind response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets ship heading retain an offset or drift after the prescribed drive is removed. After a small reversible change in rudder command and prescribed wind-gust input, observe ship heading; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from rudder command and prescribed wind-gust input to ship heading, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From rudder command and prescribed wind-gust input to ship heading, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording ship heading, yaw rate, rudder angle, and wind response while applying rudder command and prescribed wind-gust input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of rudder command and prescribed wind-gust input are applied while recording ship heading, yaw rate, rudder angle, and wind response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering rudder command and prescribed wind-gust input together with the recorded quantities ship heading, yaw rate, rudder angle, and wind response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from rudder command and prescribed wind-gust input to ship heading is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

ship heading, yaw rate, rudder angle, and wind response

### Actuators

rudder command and prescribed wind-gust input

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 101. Compute the current response of a voltage-driven capacitor

### Control Problem Description

Use sinusoidal voltage as the available control or test action and continuously record capacitor current magnitude and phase; when the bounded input returns to its baseline, no autonomous mode grows and capacitor current magnitude settles or remains bounded. After a small reversible change in sinusoidal voltage, observe capacitor current magnitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sinusoidal voltage to capacitor current magnitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From sinusoidal voltage to capacitor current magnitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording capacitor current magnitude and phase while applying sinusoidal voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sinusoidal voltage are applied while recording capacitor current magnitude and phase, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sinusoidal voltage together with the recorded quantities capacitor current magnitude and phase, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sinusoidal voltage to capacitor current magnitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

capacitor current magnitude and phase

### Actuators

sinusoidal voltage

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 102. Derive the magnitude and phase of a first-order lead element

### Control Problem Description

Use sinusoidal error signal as the available control or test action and continuously record lead-compensator magnitude and phase; when the bounded input returns to its baseline, no autonomous mode grows and lead-compensator magnitude settles or remains bounded. After a small reversible change in sinusoidal error signal, observe lead-compensator magnitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sinusoidal error signal to lead-compensator magnitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From sinusoidal error signal to lead-compensator magnitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording lead-compensator magnitude and phase while applying sinusoidal error signal makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sinusoidal error signal are applied while recording lead-compensator magnitude and phase, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sinusoidal error signal together with the recorded quantities lead-compensator magnitude and phase, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sinusoidal error signal to lead-compensator magnitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

lead-compensator magnitude and phase

### Actuators

sinusoidal error signal

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 103. Build an asymptotic Bode plot from real poles and zeros

### Control Problem Description

Use sinusoidal plant input as the available control or test action and continuously record open-loop magnitude and phase; when the bounded input returns to its baseline, an integrating or non-restoring mode lets open-loop magnitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in sinusoidal plant input, observe open-loop magnitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sinusoidal plant input to open-loop magnitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From sinusoidal plant input to open-loop magnitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording open-loop magnitude and phase while applying sinusoidal plant input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sinusoidal plant input are applied while recording open-loop magnitude and phase, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sinusoidal plant input together with the recorded quantities open-loop magnitude and phase, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sinusoidal plant input to open-loop magnitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

open-loop magnitude and phase

### Actuators

sinusoidal plant input

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 104. Include complex pole/zero factors in ordinary and flexible-system Bode plots

### Control Problem Description

Use sinusoidal applied force as the available control or test action and continuously record plant displacement magnitude and phase; when the bounded input returns to its baseline, an integrating or non-restoring mode lets plant displacement magnitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in sinusoidal applied force, observe plant displacement magnitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sinusoidal applied force to plant displacement magnitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From sinusoidal applied force to plant displacement magnitude, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording plant displacement magnitude and phase while applying sinusoidal applied force makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sinusoidal applied force are applied while recording plant displacement magnitude and phase, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sinusoidal applied force together with the recorded quantities plant displacement magnitude and phase, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sinusoidal applied force to plant displacement magnitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

plant displacement magnitude and phase

### Actuators

sinusoidal applied force

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 105. Infer low-frequency error constants and system type from a Bode plot

### Control Problem Description

Use unit-ramp reference as the available control or test action and continuously record tracking error and regulated output; when the bounded input returns to its baseline, an integrating or non-restoring mode lets tracking error retain an offset or drift after the prescribed drive is removed. After a small reversible change in unit-ramp reference, observe tracking error; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from unit-ramp reference to tracking error, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From unit-ramp reference to tracking error, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording tracking error and regulated output while applying unit-ramp reference makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of unit-ramp reference are applied while recording tracking error and regulated output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering unit-ramp reference together with the recorded quantities tracking error and regulated output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from unit-ramp reference to tracking error is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

tracking error and regulated output

### Actuators

unit-ramp reference

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 106. Apply the Nyquist criterion to a second-order loop stable for every positive gain

### Control Problem Description

Use bounded loop command during a gain sweep as the available control or test action and continuously record closed-loop output and frequency response; when the bounded input returns to its baseline, no autonomous mode grows and closed-loop output settles or remains bounded. After a small reversible change in bounded loop command during a gain sweep, observe closed-loop output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded loop command during a gain sweep to closed-loop output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded loop command during a gain sweep to closed-loop output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording closed-loop output and frequency response while applying bounded loop command during a gain sweep makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded loop command during a gain sweep are applied while recording closed-loop output and frequency response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded loop command during a gain sweep together with the recorded quantities closed-loop output and frequency response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded loop command during a gain sweep to closed-loop output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output and frequency response

### Actuators

bounded loop command during a gain sweep

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 107. Apply Nyquist indentation to a third-order loop with a pole at the origin

### Control Problem Description

Use bounded loop command during a gain sweep as the available control or test action and continuously record closed-loop output and frequency response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets closed-loop output retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded loop command during a gain sweep, observe closed-loop output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded loop command during a gain sweep to closed-loop output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded loop command during a gain sweep to closed-loop output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording closed-loop output and frequency response while applying bounded loop command during a gain sweep makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded loop command during a gain sweep are applied while recording closed-loop output and frequency response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded loop command during a gain sweep together with the recorded quantities closed-loop output and frequency response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded loop command during a gain sweep to closed-loop output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output and frequency response

### Actuators

bounded loop command during a gain sweep

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 108. Compare special Nyquist cases with an RHP pole and imaginary-axis zeros

### Control Problem Description

Use bounded commands used in the two loop tests as the available control or test action and continuously record closed-loop outputs and frequency responses of both cases; when the bounded input returns to its baseline, the first Nyquist case contains a growing open-loop mode that must be counted before any encirclement conclusion, so the deviation continues to grow rather than return. After a small reversible change in bounded commands used in the two loop tests, observe closed-loop outputs; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded commands used in the two loop tests to closed-loop outputs, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded commands used in the two loop tests to closed-loop outputs, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording closed-loop outputs and frequency responses of both cases while applying bounded commands used in the two loop tests makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded commands used in the two loop tests are applied while recording closed-loop outputs and frequency responses of both cases, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded commands used in the two loop tests together with the recorded quantities closed-loop outputs and frequency responses of both cases, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded commands used in the two loop tests to closed-loop outputs is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop outputs and frequency responses of both cases

### Actuators

bounded commands used in the two loop tests

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 109. Diagnose conditional stability and misleading gain margin

### Control Problem Description

Use bounded loop command during a gain sweep as the available control or test action and continuously record closed-loop output and frequency response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets closed-loop output retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded loop command during a gain sweep, observe closed-loop output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded loop command during a gain sweep to closed-loop output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded loop command during a gain sweep to closed-loop output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording closed-loop output and frequency response while applying bounded loop command during a gain sweep makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded loop command during a gain sweep are applied while recording closed-loop output and frequency response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded loop command during a gain sweep together with the recorded quantities closed-loop output and frequency response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded loop command during a gain sweep to closed-loop output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output and frequency response

### Actuators

bounded loop command during a gain sweep

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 110. Interpret multiple unity-gain crossings and stability margins

### Control Problem Description

Use bounded sinusoidal loop excitation as the available control or test action and continuously record closed-loop output and open-loop frequency response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets closed-loop output retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded sinusoidal loop excitation, observe closed-loop output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded sinusoidal loop excitation to closed-loop output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded sinusoidal loop excitation to closed-loop output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording closed-loop output and open-loop frequency response while applying bounded sinusoidal loop excitation makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded sinusoidal loop excitation are applied while recording closed-loop output and open-loop frequency response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded sinusoidal loop excitation together with the recorded quantities closed-loop output and open-loop frequency response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded sinusoidal loop excitation to closed-loop output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output and open-loop frequency response

### Actuators

bounded sinusoidal loop excitation

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 111. Use Bode's gain-phase slope rule to design spacecraft PD control

### Control Problem Description

Use body-torque command as the available control or test action and continuously record attitude, angular rate, and control effort; when the bounded input returns to its baseline, an integrating or non-restoring mode lets attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in body-torque command, observe attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from body-torque command to attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From body-torque command to attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording attitude, angular rate, and control effort while applying body-torque command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of body-torque command are applied while recording attitude, angular rate, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering body-torque command together with the recorded quantities attitude, angular rate, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from body-torque command to attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

attitude, angular rate, and control effort

### Actuators

body-torque command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 112. Relate crossover frequency, phase margin, resonant peak, and closed-loop bandwidth

### Control Problem Description

Use bounded sinusoidal command sweep as the available control or test action and continuously record closed-loop output and bandwidth response; when the bounded input returns to its baseline, no autonomous mode grows and closed-loop output settles or remains bounded. After a small reversible change in bounded sinusoidal command sweep, observe closed-loop output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded sinusoidal command sweep to closed-loop output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded sinusoidal command sweep to closed-loop output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording closed-loop output and bandwidth response while applying bounded sinusoidal command sweep makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded sinusoidal command sweep are applied while recording closed-loop output and bandwidth response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded sinusoidal command sweep together with the recorded quantities closed-loop output and bandwidth response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded sinusoidal command sweep to closed-loop output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output and bandwidth response

### Actuators

bounded sinusoidal command sweep

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 113. Design lead compensation for DC-motor position control

### Control Problem Description

Use lead-compensated motor command as the available control or test action and continuously record motor position, error, and step response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in lead-compensated motor command, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from lead-compensated motor command to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From lead-compensated motor command to motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor position, error, and step response while applying lead-compensated motor command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of lead-compensated motor command are applied while recording motor position, error, and step response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering lead-compensated motor command together with the recorded quantities motor position, error, and step response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from lead-compensated motor command to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor position, error, and step response

### Actuators

lead-compensated motor command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 114. Design single- and double-lead compensation for a thermal plant and servomechanism

### Control Problem Description

Use single- or double-lead command as the available control or test action and continuously record temperature or servo output; when the bounded input returns to its baseline, an integrating or non-restoring mode lets temperature or servo output retain an offset or drift after the prescribed drive is removed. After a small reversible change in single- or double-lead command, observe temperature or servo output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from single- or double-lead command to temperature or servo output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From single- or double-lead command to temperature or servo output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording temperature or servo output while applying single- or double-lead command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of single- or double-lead command are applied while recording temperature or servo output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering single- or double-lead command together with the recorded quantities temperature or servo output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from single- or double-lead command to temperature or servo output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

temperature or servo output

### Actuators

single- or double-lead command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

20.0

---

## 115. Design lag compensation for a thermal plant and DC motor, and compare it with lead

### Control Problem Description

Use lag-compensated command as the available control or test action and continuously record thermal or motor response and slow tail; when the bounded input returns to its baseline, an integrating or non-restoring mode lets thermal or motor response retain an offset or drift after the prescribed drive is removed. After a small reversible change in lag-compensated command, observe thermal or motor response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from lag-compensated command to thermal or motor response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From lag-compensated command to thermal or motor response, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording thermal or motor response and slow tail while applying lag-compensated command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of lag-compensated command are applied while recording thermal or motor response and slow tail, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering lag-compensated command together with the recorded quantities thermal or motor response and slow tail, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from lag-compensated command to thermal or motor response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

thermal or motor response and slow tail

### Actuators

lag-compensated command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

20.0

---

## 116. Design spacecraft PID control with a sensor lag and constant torque disturbance

### Control Problem Description

Use body-torque command with prescribed disturbance torque as the available control or test action and continuously record attitude, angular rate, and disturbance response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in body-torque command with prescribed disturbance torque, observe attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from body-torque command with prescribed disturbance torque to attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From body-torque command with prescribed disturbance torque to attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording attitude, angular rate, and disturbance response while applying body-torque command with prescribed disturbance torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of body-torque command with prescribed disturbance torque are applied while recording attitude, angular rate, and disturbance response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering body-torque command with prescribed disturbance torque together with the recorded quantities attitude, angular rate, and disturbance response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from body-torque command with prescribed disturbance torque to attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

attitude, angular rate, and disturbance response

### Actuators

body-torque command with prescribed disturbance torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 117. Convert a sinusoidal tracking-error requirement into a loop-gain performance bound

### Control Problem Description

Use prescribed sinusoidal reference command as the available control or test action and continuously record tracking error and regulated output; when the bounded input returns to its baseline, an integrating or non-restoring mode lets tracking error retain an offset or drift after the prescribed drive is removed. After a small reversible change in prescribed sinusoidal reference command, observe tracking error; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed sinusoidal reference command to tracking error, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From prescribed sinusoidal reference command to tracking error, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording tracking error and regulated output while applying prescribed sinusoidal reference command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed sinusoidal reference command are applied while recording tracking error and regulated output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed sinusoidal reference command together with the recorded quantities tracking error and regulated output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from prescribed sinusoidal reference command to tracking error is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

tracking error and regulated output

### Actuators

prescribed sinusoidal reference command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 118. Enforce robust-stability and sensitivity bounds under plant uncertainty

### Control Problem Description

Use loop-shaped feedback command under prescribed plant variation as the available control or test action and continuously record regulated output, tracking error, and control effort; when the bounded input returns to its baseline, no autonomous mode grows and regulated output settles or remains bounded. After a small reversible change in loop-shaped feedback command under prescribed plant variation, observe regulated output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from loop-shaped feedback command under prescribed plant variation to regulated output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From loop-shaped feedback command under prescribed plant variation to regulated output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording regulated output, tracking error, and control effort while applying loop-shaped feedback command under prescribed plant variation makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of loop-shaped feedback command under prescribed plant variation are applied while recording regulated output, tracking error, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering loop-shaped feedback command under prescribed plant variation together with the recorded quantities regulated output, tracking error, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from loop-shaped feedback command under prescribed plant variation to regulated output is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

regulated output, tracking error, and control effort

### Actuators

loop-shaped feedback command under prescribed plant variation

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=24.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

2.0

---

## 119. Quantify the phase-margin loss caused by sampling-equivalent time delay

### Control Problem Description

Use digitally sampled control command as the available control or test action and continuously record sampled plant output, tracking error, and control effort; when the bounded input returns to its baseline, no autonomous mode grows and sampled plant output settles or remains bounded. After a small reversible change in digitally sampled control command, observe sampled plant output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digitally sampled control command to sampled plant output, sampling and causal computation hold back the effect of each updated command, and a visible pause separates the command from the first recorded response. From digitally sampled control command to sampled plant output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sampled plant output, tracking error, and control effort while applying digitally sampled control command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digitally sampled control command are applied while recording sampled plant output, tracking error, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digitally sampled control command together with the recorded quantities sampled plant output, tracking error, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digitally sampled control command to sampled plant output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sampled plant output, tracking error, and control effort

### Actuators

digitally sampled control command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=24.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

2.0

---

## 120. Read closed-loop bandwidth, resonant peak, and stability margins from a Nichols chart

### Control Problem Description

Use bounded frequency-swept input as the available control or test action and continuously record closed-loop output and frequency response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets closed-loop output retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded frequency-swept input, observe closed-loop output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded frequency-swept input to closed-loop output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded frequency-swept input to closed-loop output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording closed-loop output and frequency response while applying bounded frequency-swept input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded frequency-swept input are applied while recording closed-loop output and frequency response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded frequency-swept input together with the recorded quantities closed-loop output and frequency response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded frequency-swept input to closed-loop output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

closed-loop output and frequency response

### Actuators

bounded frequency-swept input

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 121. Put rigid-satellite attitude dynamics into state-variable form

### Control Problem Description

Use thruster force as the available control or test action and continuously record attitude angle and angular rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets attitude angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in thruster force, observe attitude angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from thruster force to attitude angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From thruster force to attitude angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording attitude angle and angular rate while applying thruster force makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of thruster force are applied while recording attitude angle and angular rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering thruster force together with the recorded quantities attitude angle and angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from thruster force to attitude angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

attitude angle and angular rate

### Actuators

thruster force

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 122. Derive a DC-motor state model from coupled mechanical and electrical equations

### Control Problem Description

Use armature voltage as the available control or test action and continuously record motor position, speed, current; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in armature voltage, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from armature voltage to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From armature voltage to motor position, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording motor position, speed, current while applying armature voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of armature voltage are applied while recording motor position, speed, current, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering armature voltage together with the recorded quantities motor position, speed, current, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from armature voltage to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor position, speed, current

### Actuators

armature voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 123. Realize a quarter-car transfer function in real modal canonical form

### Control Problem Description

Use realization input as the available control or test action and continuously record quarter-car output and modal states; when the bounded input returns to its baseline, an integrating or non-restoring mode lets quarter-car output retain an offset or drift after the prescribed drive is removed. After a small reversible change in realization input, observe quarter-car output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from realization input to quarter-car output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From realization input to quarter-car output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording quarter-car output and modal states while applying realization input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of realization input are applied while recording quarter-car output and modal states, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering realization input together with the recorded quantities quarter-car output and modal states, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from realization input to quarter-car output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

quarter-car output and modal states

### Actuators

realization input

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 124. Transform a thermal system from control canonical form to modal form

### Control Problem Description

Use heat input as the available control or test action and continuously record thermal modal states and output; when the bounded input returns to its baseline, no autonomous mode grows and thermal modal states settles or remains bounded. After a small reversible change in heat input, observe thermal modal states; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from heat input to thermal modal states, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From heat input to thermal modal states, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording thermal modal states and output while applying heat input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of heat input are applied while recording thermal modal states and output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering heat input together with the recorded quantities thermal modal states and output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from heat input to thermal modal states is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

thermal modal states and output

### Actuators

heat input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

20.0

---

## 125. Recover poles, zeros, and transfer function from the Piper Dakota state model

### Control Problem Description

Use elevator input as the available control or test action and continuously record pitch attitude and modal states; when the bounded input returns to its baseline, no autonomous mode grows and pitch attitude settles or remains bounded. After a small reversible change in elevator input, observe pitch attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from elevator input to pitch attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From elevator input to pitch attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pitch attitude and modal states while applying elevator input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of elevator input are applied while recording pitch attitude and modal states, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering elevator input together with the recorded quantities pitch attitude and modal states, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from elevator input to pitch attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

pitch attitude and modal states

### Actuators

elevator input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 126. Test controllability and observability and interpret pole-zero cancellation physically

### Control Problem Description

Use bounded state-space test excitation as the available control or test action and continuously record state trajectories and declared output response; when the bounded input returns to its baseline, no autonomous mode grows and state trajectories settles or remains bounded. After a small reversible change in bounded state-space test excitation, observe state trajectories; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded state-space test excitation to state trajectories, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded state-space test excitation to state trajectories, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording state trajectories and declared output response while applying bounded state-space test excitation leaves one pole-zero-canceled mode absent from the recordings and unreachable from the prescribed excitation. When permitted changes in the direction or amplitude of bounded state-space test excitation are applied while recording state trajectories and declared output response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded state-space test excitation together with the recorded quantities state trajectories and declared output response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded state-space test excitation to state trajectories is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

state trajectories and declared output response

### Actuators

bounded state-space test excitation

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 127. Place repeated closed-loop poles for an undamped pendulum by full-state feedback

### Control Problem Description

Use pivot torque as the available control or test action and continuously record pendulum angle and rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets pendulum angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in pivot torque, observe pendulum angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from pivot torque to pendulum angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From pivot torque to pendulum angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pendulum angle and rate while applying pivot torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of pivot torque are applied while recording pendulum angle and rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering pivot torque together with the recorded quantities pendulum angle and rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from pivot torque to pendulum angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

pendulum angle and rate

### Actuators

pivot torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 128. Apply Ackermann pole placement and diagnose gain growth near a weakly controllable zero

### Control Problem Description

Use bounded state-feedback command as the available control or test action and continuously record closed-loop state response and control effort; when the bounded input returns to its baseline, no autonomous mode grows and closed-loop state response settles or remains bounded. After a small reversible change in bounded state-feedback command, observe closed-loop state response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded state-feedback command to closed-loop state response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded state-feedback command to closed-loop state response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording closed-loop state response and control effort while applying bounded state-feedback command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded state-feedback command are applied while recording closed-loop state response and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering bounded state-feedback command together with the recorded quantities closed-loop state response and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded state-feedback command to closed-loop state response is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

closed-loop state response and control effort

### Actuators

bounded state-feedback command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=24.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

2.0

---

## 129. Introduce a step reference robustly into a Type 1 DC-motor loop

### Control Problem Description

Use state feedback voltage as the available control or test action and continuously record motor position and speed; when the bounded input returns to its baseline, an integrating or non-restoring mode lets motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in state feedback voltage, observe motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from state feedback voltage to motor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From state feedback voltage to motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor position and speed while applying state feedback voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of state feedback voltage are applied while recording motor position and speed, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering state feedback voltage together with the recorded quantities motor position and speed, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from state feedback voltage to motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor position and speed

### Actuators

state feedback voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 130. Select dominant second-order poles for a third-order drone model

### Control Problem Description

Use control moment as the available control or test action and continuously record drone attitude response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets drone attitude response retain an offset or drift after the prescribed drive is removed. After a small reversible change in control moment, observe drone attitude response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from control moment to drone attitude response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From control moment to drone attitude response, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording drone attitude response while applying control moment makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of control moment are applied while recording drone attitude response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering control moment together with the recorded quantities drone attitude response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from control moment to drone attitude response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

drone attitude response

### Actuators

control moment

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 131. Balance tracking error and effort with LQR for the drone

### Control Problem Description

Use optimal control moment as the available control or test action and continuously record drone state and control effort; when the bounded input returns to its baseline, an integrating or non-restoring mode lets drone state retain an offset or drift after the prescribed drive is removed. After a small reversible change in optimal control moment, observe drone state; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from optimal control moment to drone state, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From optimal control moment to drone state, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording drone state and control effort while applying optimal control moment makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of optimal control moment are applied while recording drone state and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering optimal control moment together with the recorded quantities drone state and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from optimal control moment to drone state is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

drone state and control effort

### Actuators

optimal control moment

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 132. Design and validate a full-order pendulum state estimator

### Control Problem Description

Use known pivot torque as the available control or test action and continuously record measured angle and estimated state; when the bounded input returns to its baseline, an integrating or non-restoring mode lets measured angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in known pivot torque, observe measured angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from known pivot torque to measured angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From known pivot torque to measured angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording measured angle and estimated state while applying known pivot torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of known pivot torque are applied while recording measured angle and estimated state, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering known pivot torque together with the recorded quantities measured angle and estimated state, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from known pivot torque to measured angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

measured angle and estimated state

### Actuators

known pivot torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 133. Design a reduced-order pendulum estimator without differentiating the measurement

### Control Problem Description

Use known pivot torque as the available control or test action and continuously record measured angle and estimated rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets measured angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in known pivot torque, observe measured angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from known pivot torque to measured angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From known pivot torque to measured angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording measured angle and estimated rate while applying known pivot torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of known pivot torque are applied while recording measured angle and estimated rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering known pivot torque together with the recorded quantities measured angle and estimated rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from known pivot torque to measured angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

measured angle and estimated rate

### Actuators

known pivot torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 134. Select estimator poles from a symmetric root locus under process/sensor noise tradeoffs

### Control Problem Description

Use known plant input as the available control or test action and continuously record state estimate and innovation; when the bounded input returns to its baseline, an integrating or non-restoring mode lets state estimate retain an offset or drift after the prescribed drive is removed. After a small reversible change in known plant input, observe state estimate; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from known plant input to state estimate, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From known plant input to state estimate, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording state estimate and innovation while applying known plant input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of known plant input are applied while recording state estimate and innovation, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering known plant input together with the recorded quantities state estimate and innovation, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from known plant input to state estimate is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

state estimate and innovation

### Actuators

known plant input

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 135. Combine controller and estimator by the separation principle and form a DC-servo compensator

### Control Problem Description

Use dynamic compensator voltage as the available control or test action and continuously record servo output, estimated state, and control effort; when the bounded input returns to its baseline, an integrating or non-restoring mode lets servo output retain an offset or drift after the prescribed drive is removed. After a small reversible change in dynamic compensator voltage, observe servo output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from dynamic compensator voltage to servo output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From dynamic compensator voltage to servo output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording servo output, estimated state, and control effort while applying dynamic compensator voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of dynamic compensator voltage are applied while recording servo output, estimated state, and control effort, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering dynamic compensator voltage together with the recorded quantities servo output, estimated state, and control effort, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from dynamic compensator voltage to servo output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

servo output, estimated state, and control effort

### Actuators

dynamic compensator voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 136. Assign controller feedforward zeros to increase a servomechanism velocity constant

### Control Problem Description

Use two-input or equivalent lag-lead command as the available control or test action and continuously record servo position, tracking error, and slow tail; when the bounded input returns to its baseline, an integrating or non-restoring mode lets servo position retain an offset or drift after the prescribed drive is removed. After a small reversible change in two-input or equivalent lag-lead command, observe servo position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from two-input or equivalent lag-lead command to servo position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From two-input or equivalent lag-lead command to servo position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording servo position, tracking error, and slow tail while applying two-input or equivalent lag-lead command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of two-input or equivalent lag-lead command are applied while recording servo position, tracking error, and slow tail, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering two-input or equivalent lag-lead command together with the recorded quantities servo position, tracking error, and slow tail, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from two-input or equivalent lag-lead command to servo position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

servo position, tracking error, and slow tail

### Actuators

two-input or equivalent lag-lead command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 137. Add integral state feedback for robust motor-speed tracking and constant-disturbance rejection

### Control Problem Description

Use motor voltage as the available control or test action and continuously record motor speed and integral error; when the bounded input returns to its baseline, no autonomous mode grows and motor speed settles or remains bounded. After a small reversible change in motor voltage, observe motor speed; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from motor voltage to motor speed, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From motor voltage to motor speed, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording motor speed and integral error while applying motor voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of motor voltage are applied while recording motor speed and integral error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering motor voltage together with the recorded quantities motor speed and integral error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from motor voltage to motor speed is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

motor speed and integral error

### Actuators

motor voltage

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 138. Embed a sinusoidal internal model for disk-drive tracking and rejection

### Control Problem Description

Use voice-coil force as the available control or test action and continuously record disk-head position and sinusoidal error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets disk-head position retain an offset or drift after the prescribed drive is removed. After a small reversible change in voice-coil force, observe disk-head position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from voice-coil force to disk-head position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From voice-coil force to disk-head position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording disk-head position and sinusoidal error while applying voice-coil force makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of voice-coil force are applied while recording disk-head position and sinusoidal error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering voice-coil force together with the recorded quantities disk-head position and sinusoidal error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from voice-coil force to disk-head position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

disk-head position and sinusoidal error

### Actuators

voice-coil force

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 139. Recover LQR loop shape with an LTR estimator while quantifying sensor-noise actuator activity

### Control Problem Description

Use body torque under prescribed sensor noise as the available control or test action and continuously record attitude response and body-torque activity; when the bounded input returns to its baseline, an integrating or non-restoring mode lets attitude response retain an offset or drift after the prescribed drive is removed. After a small reversible change in body torque under prescribed sensor noise, observe attitude response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from body torque under prescribed sensor noise to attitude response, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From body torque under prescribed sensor noise to attitude response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording attitude response and body-torque activity while applying body torque under prescribed sensor noise makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of body torque under prescribed sensor noise are applied while recording attitude response and body-torque activity, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering body torque under prescribed sensor noise together with the recorded quantities attitude response and body-torque activity, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from body torque under prescribed sensor noise to attitude response is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

attitude response and body-torque activity

### Actuators

body torque under prescribed sensor noise

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 140. Control a delayed heat exchanger with a Smith predictor and state-space pole placement

### Control Problem Description

Use steam command through Smith predictor as the available control or test action and continuously record delayed heat-exchanger temperature; when the bounded input returns to its baseline, no autonomous mode grows and delayed heat-exchanger temperature settles or remains bounded. After a small reversible change in steam command through Smith predictor, observe delayed heat-exchanger temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from steam command through Smith predictor to delayed heat-exchanger temperature, heat transport and temperature measurement hold back the outlet response, and a visible pause separates the command from the first recorded response. From steam command through Smith predictor to delayed heat-exchanger temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording delayed heat-exchanger temperature while applying steam command through Smith predictor makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of steam command through Smith predictor are applied while recording delayed heat-exchanger temperature, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering steam command through Smith predictor together with the recorded quantities delayed heat-exchanger temperature, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from steam command through Smith predictor to delayed heat-exchanger temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

delayed heat-exchanger temperature

### Actuators

steam command through Smith predictor

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

20.0

---

## 141. Digitize a DC-motor lead controller with Tustin's bilinear approximation

### Control Problem Description

Use digital motor voltage as the available control or test action and continuously record sampled motor position and error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets sampled motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in digital motor voltage, observe sampled motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital motor voltage to sampled motor position, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital motor voltage to sampled motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sampled motor position and error while applying digital motor voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital motor voltage are applied while recording sampled motor position and error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital motor voltage together with the recorded quantities sampled motor position and error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital motor voltage to sampled motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sampled motor position and error

### Actuators

digital motor voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 142. Digitize the same lead controller with the zero-order-hold approximation

### Control Problem Description

Use held motor voltage as the available control or test action and continuously record sampled motor position and error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets sampled motor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in held motor voltage, observe sampled motor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from held motor voltage to sampled motor position, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From held motor voltage to sampled motor position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sampled motor position and error while applying held motor voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of held motor voltage are applied while recording sampled motor position and error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering held motor voltage together with the recorded quantities sampled motor position and error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from held motor voltage to sampled motor position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sampled motor position and error

### Actuators

held motor voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 143. Design a space-station attitude controller with matched pole-zero emulation

### Control Problem Description

With a sampled controller obtained by mapping a verified continuous attitude design, use digital body torque as the available control or test action and continuously record space station attitude; when the bounded input returns to its baseline, an integrating or non-restoring mode lets space station attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in digital body torque, observe space station attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital body torque to space station attitude, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital body torque to space station attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording space station attitude while applying digital body torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital body torque are applied while recording space station attitude, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital body torque together with the recorded quantities space station attitude, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital body torque to space station attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

space station attitude

### Actuators

digital body torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 144. Compare continuous and sampled root loci for a first-order plant

### Control Problem Description

Use held proportional command as the available control or test action and continuously record sampled first-order output; when the bounded input returns to its baseline, no autonomous mode grows and sampled first-order output settles or remains bounded. After a small reversible change in held proportional command, observe sampled first-order output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from held proportional command to sampled first-order output, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From held proportional command to sampled first-order output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sampled first-order output while applying held proportional command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of held proportional command are applied while recording sampled first-order output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering held proportional command together with the recorded quantities sampled first-order output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from held proportional command to sampled first-order output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sampled first-order output

### Actuators

held proportional command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 145. Design the space-station controller directly in the z-plane

### Control Problem Description

With a sampled controller whose compensator is designed directly from the discrete response, use digital body torque as the available control or test action and continuously record space station attitude; when the bounded input returns to its baseline, an integrating or non-restoring mode lets space station attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in digital body torque, observe space station attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital body torque to space station attitude, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital body torque to space station attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording space station attitude while applying digital body torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital body torque are applied while recording space station attitude, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital body torque together with the recorded quantities space station attitude, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital body torque to space station attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

space station attitude

### Actuators

digital body torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 146. Compare continuous, emulated, and direct-discrete damping and step response

### Control Problem Description

Use continuous or digital command as the available control or test action and continuously record continuous and sampled step responses; when the bounded input returns to its baseline, an integrating or non-restoring mode lets continuous retain an offset or drift after the prescribed drive is removed. After a small reversible change in continuous or digital command, observe continuous; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from continuous or digital command to continuous, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From continuous or digital command to continuous, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording continuous and sampled step responses while applying continuous or digital command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of continuous or digital command are applied while recording continuous and sampled step responses, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering continuous or digital command together with the recorded quantities continuous and sampled step responses, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from continuous or digital command to continuous is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

continuous and sampled step responses

### Actuators

continuous or digital command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 147. Recover a filter difference equation, pole damping, and stability from its z transfer function

### Control Problem Description

Use discrete filter input as the available control or test action and continuously record filter output; when the bounded input returns to its baseline, no autonomous mode grows and filter output settles or remains bounded. After a small reversible change in discrete filter input, observe filter output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from discrete filter input to filter output, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From discrete filter input to filter output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording filter output while applying discrete filter input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of discrete filter input are applied while recording filter output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering discrete filter input together with the recorded quantities filter output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from discrete filter input to filter output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

filter output

### Actuators

discrete filter input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 148. Solve a forced second-order difference equation by the z-transform

### Control Problem Description

Use ramp sequence input as the available control or test action and continuously record discrete sequence output; when the bounded input returns to its baseline, no autonomous mode grows and discrete sequence output settles or remains bounded. After a small reversible change in ramp sequence input, observe discrete sequence output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from ramp sequence input to discrete sequence output, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From ramp sequence input to discrete sequence output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording discrete sequence output while applying ramp sequence input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of ramp sequence input are applied while recording discrete sequence output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering ramp sequence input together with the recorded quantities discrete sequence output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from ramp sequence input to discrete sequence output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

discrete sequence output

### Actuators

ramp sequence input

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 149. Prove and use the mapping properties between the s-plane and z-plane

### Control Problem Description

Use prescribed modal mapping test as the available control or test action and continuously record continuous and sampled free-response modes; when the bounded input returns to its baseline, no autonomous mode grows and continuous settles or remains bounded. After a small reversible change in prescribed modal mapping test, observe continuous; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed modal mapping test to continuous, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From prescribed modal mapping test to continuous, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording continuous and sampled free-response modes while applying prescribed modal mapping test makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed modal mapping test are applied while recording continuous and sampled free-response modes, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed modal mapping test together with the recorded quantities continuous and sampled free-response modes, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from prescribed modal mapping test to continuous is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

continuous and sampled free-response modes

### Actuators

prescribed modal mapping test

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 150. Map a continuous lag compensator to a 20 Hz digital implementation

### Control Problem Description

Use digital lag command as the available control or test action and continuously record regulated output and digital error; when the bounded input returns to its baseline, no autonomous mode grows and regulated output settles or remains bounded. After a small reversible change in digital lag command, observe regulated output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital lag command to regulated output, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital lag command to regulated output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording regulated output and digital error while applying digital lag command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital lag command are applied while recording regulated output and digital error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital lag command together with the recorded quantities regulated output and digital error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital lag command to regulated output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

regulated output and digital error

### Actuators

digital lag command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 151. Compare Tustin and matched pole-zero digitizations of a lead network

### Control Problem Description

Use sampled error as the available control or test action and continuously record lead network magnitude and phase; when the bounded input returns to its baseline, no autonomous mode grows and lead network magnitude settles or remains bounded. After a small reversible change in sampled error, observe lead network magnitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sampled error to lead network magnitude, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From sampled error to lead network magnitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording lead network magnitude and phase while applying sampled error makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sampled error are applied while recording lead network magnitude and phase, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sampled error together with the recorded quantities lead network magnitude and phase, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sampled error to lead network magnitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

lead network magnitude and phase

### Actuators

sampled error

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 152. Compare Tustin and matched pole-zero digitizations of a lag network

### Control Problem Description

Use sampled error as the available control or test action and continuously record lag network magnitude and phase; when the bounded input returns to its baseline, no autonomous mode grows and lag network magnitude settles or remains bounded. After a small reversible change in sampled error, observe lag network magnitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sampled error to lag network magnitude, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From sampled error to lag network magnitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording lag network magnitude and phase while applying sampled error makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sampled error are applied while recording lag network magnitude and phase, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sampled error together with the recorded quantities lag network magnitude and phase, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sampled error to lag network magnitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

lag network magnitude and phase

### Actuators

sampled error

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 153. Digitize a PID at three sample periods and assess transient degradation

### Control Problem Description

Use digital PID command as the available control or test action and continuously record sampled step response; when the bounded input returns to its baseline, an integrating or non-restoring mode lets sampled step response retain an offset or drift after the prescribed drive is removed. After a small reversible change in digital PID command, observe sampled step response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital PID command to sampled step response, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital PID command to sampled step response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sampled step response while applying digital PID command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital PID command are applied while recording sampled step response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital PID command together with the recorded quantities sampled step response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital PID command to sampled step response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sampled step response

### Actuators

digital PID command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 154. Determine the sampled-data stability-gain range of a plant with an unstable mode

### Control Problem Description

Use held proportional command as the available control or test action and continuously record sampled plant output; when the bounded input returns to its baseline, sampling does not remove the plant's growing mode, so a bounded stabilizing gain range is still required, so the deviation continues to grow rather than return. After a small reversible change in held proportional command, observe sampled plant output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from held proportional command to sampled plant output, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From held proportional command to sampled plant output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sampled plant output while applying held proportional command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of held proportional command are applied while recording sampled plant output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering held proportional command together with the recorded quantities sampled plant output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from held proportional command to sampled plant output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sampled plant output

### Actuators

held proportional command

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=3.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 155. Design discrete proportional-plus-velocity satellite attitude feedback

### Control Problem Description

Use digital torque as the available control or test action and continuously record satellite attitude and sampled rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets satellite attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in digital torque, observe satellite attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital torque to satellite attitude, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital torque to satellite attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording satellite attitude and sampled rate while applying digital torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital torque are applied while recording satellite attitude and sampled rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital torque together with the recorded quantities satellite attitude and sampled rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital torque to satellite attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

satellite attitude and sampled rate

### Actuators

digital torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 156. Linearize and digitally stabilize a magnetic-levitation ball subject to sensor/current limits

### Control Problem Description

Use electromagnet current as the available control or test action and continuously record ball displacement and current; when the bounded input returns to its baseline, the levitated ball moves farther from its operating gap after a small open-loop displacement, so the deviation continues to grow rather than return. After a small reversible change in electromagnet current, observe ball displacement; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from electromagnet current to ball displacement, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From electromagnet current to ball displacement, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording ball displacement and current while applying electromagnet current makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of electromagnet current are applied while recording ball displacement and current, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering electromagnet current together with the recorded quantities ball displacement and current, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from electromagnet current to ball displacement is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

ball displacement and current

### Actuators

electromagnet current

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=3.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 157. Redesign a lead-lag servomechanism directly in the z-plane

### Control Problem Description

Use digital servo voltage as the available control or test action and continuously record servo position and ramp error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets servo position retain an offset or drift after the prescribed drive is removed. After a small reversible change in digital servo voltage, observe servo position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital servo voltage to servo position, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital servo voltage to servo position, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording servo position and ramp error while applying digital servo voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital servo voltage are applied while recording servo position and ramp error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital servo voltage together with the recorded quantities servo position and ramp error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital servo voltage to servo position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

servo position and ramp error

### Actuators

digital servo voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 158. Design an antenna-servo controller by emulation and direct z-plane root locus

### Control Problem Description

Use digital motor torque as the available control or test action and continuously record antenna angle; when the bounded input returns to its baseline, an integrating or non-restoring mode lets antenna angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in digital motor torque, observe antenna angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital motor torque to antenna angle, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital motor torque to antenna angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording antenna angle while applying digital motor torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital motor torque are applied while recording antenna angle, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital motor torque together with the recorded quantities antenna angle, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital motor torque to antenna angle is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

antenna angle

### Actuators

digital motor torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

0.5

---

## 159. Design discrete compensation for a two-real-pole plant under rise-time and overshoot limits

### Control Problem Description

Use digital compensated command as the available control or test action and continuously record sampled plant output; when the bounded input returns to its baseline, no autonomous mode grows and sampled plant output settles or remains bounded. After a small reversible change in digital compensated command, observe sampled plant output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digital compensated command to sampled plant output, the stated sample-and-hold action is modeled directly and no additional transport or computation pause dominates the loop, so the first recorded change begins promptly without a separate silent interval. From digital compensated command to sampled plant output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording sampled plant output while applying digital compensated command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digital compensated command are applied while recording sampled plant output, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering digital compensated command together with the recorded quantities sampled plant output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from digital compensated command to sampled plant output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

sampled plant output

### Actuators

digital compensated command

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

0.5

---

## 160. Explain the unavoidable one-sample delay in a causal discrete derivative

### Control Problem Description

Use sampled error sequence as the available control or test action and continuously record estimated error-rate response; when the bounded input returns to its baseline, no autonomous mode grows and estimated error-rate response settles or remains bounded. After a small reversible change in sampled error sequence, observe estimated error-rate response; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sampled error sequence to estimated error-rate response, sampling and causal computation hold back the effect of each updated command, and a visible pause separates the command from the first recorded response. From sampled error sequence to estimated error-rate response, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording estimated error-rate response while applying sampled error sequence makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sampled error sequence are applied while recording estimated error-rate response, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering sampled error sequence together with the recorded quantities estimated error-rate response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sampled error sequence to estimated error-rate response is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

estimated error-rate response

### Actuators

sampled error sequence

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=6.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

0.5

---

## 161. Find pendulum equilibria and classify their small-signal stability

### Control Problem Description

Use pivot torque as the available control or test action and continuously record pendulum angle and angular rate; when the bounded input returns to its baseline, the upright pendulum equilibrium sends a small angular displacement away even though the hanging equilibrium is neutral, so the deviation continues to grow rather than return. After a small reversible change in pivot torque, observe pendulum angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from pivot torque to pendulum angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From pivot torque to pendulum angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pendulum angle and angular rate while applying pivot torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of pivot torque are applied while recording pendulum angle and angular rate, gravity torque changes with pendulum angle and produces distinct hanging and upright equilibria, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering pivot torque together with the recorded quantities pendulum angle and angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from pivot torque to pendulum angle is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

pendulum angle and angular rate

### Actuators

pivot torque

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 162. Linearize a magnetic ball levitator from experimentally measured force curves

### Control Problem Description

Use electromagnet current perturbation as the available control or test action and continuously record ball displacement, velocity, coil current; when the bounded input returns to its baseline, the measured magnetic-force slope makes a small ball displacement grow away from the levitation point, so the deviation continues to grow rather than return. After a small reversible change in electromagnet current perturbation, observe ball displacement; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from electromagnet current perturbation to ball displacement, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From electromagnet current perturbation to ball displacement, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording ball displacement, velocity, coil current while applying electromagnet current perturbation makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of electromagnet current perturbation are applied while recording ball displacement, velocity, coil current, magnetic force changes jointly with air gap and coil current along the measured force curves, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering electromagnet current perturbation together with the recorded quantities ball displacement, velocity, coil current, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from electromagnet current perturbation to ball displacement is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

ball displacement, velocity, coil current

### Actuators

electromagnet current perturbation

### Safety Bounds

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 163. Linearize nonlinear square-root water-tank outflow around an operating point

### Control Problem Description

Repeat the bounded test at several nearby steady liquid levels and use inlet mass flow as the available control or test action and continuously record tank level and outlet flow; when the bounded input returns to its baseline, no autonomous mode grows and tank level settles or remains bounded. After a small reversible change in inlet mass flow, observe tank level; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from inlet mass flow to tank level, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From inlet mass flow to tank level, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording tank level and outlet flow while applying inlet mass flow makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of inlet mass flow are applied while recording tank level and outlet flow, tank outflow follows a static square-root level law around the selected operating point, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering inlet mass flow together with the recorded quantities tank level and outlet flow, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from inlet mass flow to tank level is repeated after varying relevant physical parameters and operating conditions within safe limits, reasonable component, load, sensing, and actuator changes shift the response rate and final level modestly while preserving motion direction and channel structure.

### Observable Outputs

tank level and outlet flow

### Actuators

inlet mass flow

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 164. Cancel pendulum gravity by computed-torque nonlinear feedback

### Control Problem Description

Use computed pivot torque as the available control or test action and continuously record pendulum angle and angular rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets pendulum angle retain an offset or drift after the prescribed drive is removed. After a small reversible change in computed pivot torque, observe pendulum angle; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from computed pivot torque to pendulum angle, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From computed pivot torque to pendulum angle, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording pendulum angle and angular rate while applying computed pivot torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of computed pivot torque are applied while recording pendulum angle and angular rate, the computed-torque law must cancel the full angle-dependent gravity torque along the motion, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering computed pivot torque together with the recorded quantities pendulum angle and angular rate, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from computed pivot torque to pendulum angle is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

pendulum angle and angular rate

### Actuators

computed pivot torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 165. Cancel a rapid-thermal-processing lamp square law with an inverse nonlinearity

### Control Problem Description

Use commanded lamp voltage as the available control or test action and continuously record lamp voltage and delivered power; when the bounded input returns to its baseline, no autonomous mode grows and lamp voltage settles or remains bounded. After a small reversible change in commanded lamp voltage, observe lamp voltage; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from commanded lamp voltage to lamp voltage, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From commanded lamp voltage to lamp voltage, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording lamp voltage and delivered power while applying commanded lamp voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of commanded lamp voltage are applied while recording lamp voltage and delivered power, delivered lamp power follows a static square law that can be inverted over the positive command range, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering commanded lamp voltage together with the recorded quantities lamp voltage and delivered power, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from commanded lamp voltage to lamp voltage is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

lamp voltage and delivered power

### Actuators

commanded lamp voltage

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

20.0

---

## 166. Predict amplitude-dependent overshoot caused by actuator saturation

### Control Problem Description

Use amplitude-limited command as the available control or test action and continuously record output, error, saturated control; when the bounded input returns to its baseline, an integrating or non-restoring mode lets output retain an offset or drift after the prescribed drive is removed. After a small reversible change in amplitude-limited command, observe output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from amplitude-limited command to output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From amplitude-limited command to output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording output, error, saturated control while applying amplitude-limited command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of amplitude-limited command are applied while recording output, error, saturated control, the actuator clips the proportional command at a fixed amplitude and changes the effective loop gain, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering amplitude-limited command together with the recorded quantities output, error, saturated control, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from amplitude-limited command to output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

output, error, saturated control

### Actuators

amplitude-limited command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 167. Expose large-signal instability in a conditionally stable saturated loop

### Control Problem Description

Use saturated proportional command as the available control or test action and continuously record regulated output, loop error, and saturated control signal; when the bounded input returns to its baseline, an integrating or non-restoring mode lets regulated output retain an offset or drift after the prescribed drive is removed. After a small reversible change in saturated proportional command, observe regulated output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from saturated proportional command to regulated output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From saturated proportional command to regulated output, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording regulated output, loop error, and saturated control signal while applying saturated proportional command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of saturated proportional command are applied while recording regulated output, loop error, and saturated control signal, command saturation lowers the effective gain until the conditionally stable loop can cross its stability boundary, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering saturated proportional command together with the recorded quantities regulated output, loop error, and saturated control signal, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from saturated proportional command to regulated output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

regulated output, loop error, and saturated control signal

### Actuators

saturated proportional command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 168. Predict a saturation-induced flexible-mode limit cycle and eliminate it with a notch

### Control Problem Description

Use notch-shaped limited command as the available control or test action and continuously record flexible displacement and saturated command; when the bounded input returns to its baseline, an integrating or non-restoring mode lets flexible displacement retain an offset or drift after the prescribed drive is removed. After a small reversible change in notch-shaped limited command, observe flexible displacement; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from notch-shaped limited command to flexible displacement, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From notch-shaped limited command to flexible displacement, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording flexible displacement and saturated command while applying notch-shaped limited command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of notch-shaped limited command are applied while recording flexible displacement and saturated command, the limited actuator changes its effective gain with oscillation amplitude and can sustain the flexible mode, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering notch-shaped limited command together with the recorded quantities flexible displacement and saturated command, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from notch-shaped limited command to flexible displacement is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

flexible displacement and saturated command

### Actuators

notch-shaped limited command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 169. Add back-calculation antiwindup to a saturated PI-controlled integrator

### Control Problem Description

Use saturated PI command as the available control or test action and continuously record integrator output, plant output, actuator command; when the bounded input returns to its baseline, an integrating or non-restoring mode lets integrator output retain an offset or drift after the prescribed drive is removed. After a small reversible change in saturated PI command, observe integrator output; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from saturated PI command to integrator output, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From saturated PI command to integrator output, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording integrator output, plant output, actuator command while applying saturated PI command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of saturated PI command are applied while recording integrator output, plant output, actuator command, the actuator limit is static, while back-calculation prevents the separate integral state from winding up, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering saturated PI command together with the recorded quantities integrator output, plant output, actuator command, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from saturated PI command to integrator output is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

integrator output, plant output, actuator command

### Actuators

saturated PI command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 170. Derive the describing function of a saturation nonlinearity

### Control Problem Description

Use bounded sinusoidal nonlinearity test as the available control or test action and continuously record nonlinear input and fundamental output; when the bounded input returns to its baseline, no autonomous mode grows and nonlinear input settles or remains bounded. After a small reversible change in bounded sinusoidal nonlinearity test, observe nonlinear input; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded sinusoidal nonlinearity test to nonlinear input, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded sinusoidal nonlinearity test to nonlinear input, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording nonlinear input and fundamental output while applying bounded sinusoidal nonlinearity test makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded sinusoidal nonlinearity test are applied while recording nonlinear input and fundamental output, the saturation element is a memoryless amplitude map evaluated by its fundamental response, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering bounded sinusoidal nonlinearity test together with the recorded quantities nonlinear input and fundamental output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded sinusoidal nonlinearity test to nonlinear input is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

nonlinear input and fundamental output

### Actuators

bounded sinusoidal nonlinearity test

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 171. Derive the describing function of an ideal relay

### Control Problem Description

Use binary relay command as the available control or test action and continuously record relay input and fundamental output; when the bounded input returns to its baseline, no autonomous mode grows and relay input settles or remains bounded. After a small reversible change in binary relay command, observe relay input; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from binary relay command to relay input, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From binary relay command to relay input, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording relay input and fundamental output while applying binary relay command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of binary relay command are applied while recording relay input and fundamental output, the ideal relay switches between two fixed output levels according to the input sign, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering binary relay command together with the recorded quantities relay input and fundamental output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from binary relay command to relay input is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

relay input and fundamental output

### Actuators

binary relay command

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 172. Derive the complex describing function of a relay with hysteresis

### Control Problem Description

Use hysteretic relay command as the available control or test action and continuously record hysteresis input and fundamental output; when the bounded input returns to its baseline, no autonomous mode grows and hysteresis input settles or remains bounded. After a small reversible change in hysteretic relay command, observe hysteresis input; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from hysteretic relay command to hysteresis input, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From hysteretic relay command to hysteresis input, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording hysteresis input and fundamental output while applying hysteretic relay command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of hysteretic relay command are applied while recording hysteresis input and fundamental output, the relay retains a fixed switching memory band that appears as hysteresis in its input-output map, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering hysteretic relay command together with the recorded quantities hysteresis input and fundamental output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from hysteretic relay command to hysteresis input is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

hysteresis input and fundamental output

### Actuators

hysteretic relay command

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 173. Predict a saturation limit cycle from a Nyquist/describing-function intersection

### Control Problem Description

Use saturated loop command as the available control or test action and continuously record oscillation amplitude and frequency; when the bounded input returns to its baseline, an integrating or non-restoring mode lets oscillation amplitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in saturated loop command, observe oscillation amplitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from saturated loop command to oscillation amplitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From saturated loop command to oscillation amplitude, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording oscillation amplitude and frequency while applying saturated loop command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of saturated loop command are applied while recording oscillation amplitude and frequency, the saturation map changes effective loop gain with candidate oscillation amplitude, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering saturated loop command together with the recorded quantities oscillation amplitude and frequency, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from saturated loop command to oscillation amplitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

oscillation amplitude and frequency

### Actuators

saturated loop command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 174. Predict a hysteresis-induced limit cycle from the same construction

### Control Problem Description

Use hysteretic relay command as the available control or test action and continuously record hysteretic oscillation amplitude and frequency; when the bounded input returns to its baseline, an integrating or non-restoring mode lets hysteretic oscillation amplitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in hysteretic relay command, observe hysteretic oscillation amplitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from hysteretic relay command to hysteretic oscillation amplitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From hysteretic relay command to hysteretic oscillation amplitude, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording hysteretic oscillation amplitude and frequency while applying hysteretic relay command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of hysteretic relay command are applied while recording hysteretic oscillation amplitude and frequency, the hysteretic relay contributes an amplitude-dependent magnitude and phase shift, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering hysteretic relay command together with the recorded quantities hysteretic oscillation amplitude and frequency, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from hysteretic relay command to hysteretic oscillation amplitude is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

hysteretic oscillation amplitude and frequency

### Actuators

hysteretic relay command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 175. Derive bang-bang minimum-time switching and a chatter-reducing PTOS law for a double integrator

### Control Problem Description

Use bounded acceleration command as the available control or test action and continuously record position and velocity; when the bounded input returns to its baseline, an integrating or non-restoring mode lets position retain an offset or drift after the prescribed drive is removed. After a small reversible change in bounded acceleration command, observe position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded acceleration command to position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded acceleration command to position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording position and velocity while applying bounded acceleration command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded acceleration command are applied while recording position and velocity, the time-optimal command switches between bounded acceleration levels according to position and velocity, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering bounded acceleration command together with the recorded quantities position and velocity, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded acceleration command to position is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

position and velocity

### Actuators

bounded acceleration command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

2.0

---

## 176. Prove parameter-dependent stability of a second-order linear system with a Lyapunov equation

### Control Problem Description

Use prescribed initial-state release as the available control or test action and continuously record state trajectory and decay behavior; when the bounded input returns to its baseline, no autonomous mode grows and state trajectory settles or remains bounded. After a small reversible change in prescribed initial-state release, observe state trajectory; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from prescribed initial-state release to state trajectory, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From prescribed initial-state release to state trajectory, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording state trajectory and decay behavior while applying prescribed initial-state release makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of prescribed initial-state release are applied while recording state trajectory and decay behavior, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering prescribed initial-state release together with the recorded quantities state trajectory and decay behavior, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from prescribed initial-state release to state trajectory is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

state trajectory and decay behavior

### Actuators

prescribed initial-state release

### Safety Bounds

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the normalized excitation beyond the declared local operating range

### Dominant Time Scale (Seconds)

2.0

---

## 177. Construct a direct Lyapunov function for nonlinear position feedback

### Control Problem Description

Use nonlinear restoring feedback as the available control or test action and continuously record position error, velocity, and state trajectory; when the bounded input returns to its baseline, no autonomous mode grows and position error settles or remains bounded. After a small reversible change in nonlinear restoring feedback, observe position error; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from nonlinear restoring feedback to position error, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From nonlinear restoring feedback to position error, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording position error, velocity, and state trajectory while applying nonlinear restoring feedback makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of nonlinear restoring feedback are applied while recording position error, velocity, and state trajectory, the restoring feedback changes with position error and shapes the state energy throughout the trajectory, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering nonlinear restoring feedback together with the recorded quantities position error, velocity, and state trajectory, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from nonlinear restoring feedback to position error is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

position error, velocity, and state trajectory

### Actuators

nonlinear restoring feedback

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 178. Bound a signum nonlinearity by a sector

### Control Problem Description

Use bounded signum test signal as the available control or test action and continuously record nonlinearity input and output; when the bounded input returns to its baseline, no autonomous mode grows and nonlinearity input settles or remains bounded. After a small reversible change in bounded signum test signal, observe nonlinearity input; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from bounded signum test signal to nonlinearity input, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From bounded signum test signal to nonlinearity input, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording nonlinearity input and output while applying bounded signum test signal makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of bounded signum test signal are applied while recording nonlinearity input and output, the sign map is a memoryless sector-bounded relation outside its switching point, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering bounded signum test signal together with the recorded quantities nonlinearity input and output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from bounded signum test signal to nonlinearity input is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

nonlinearity input and output

### Actuators

bounded signum test signal

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 179. Bound actuator saturation by a sector

### Control Problem Description

Use amplitude-limited actuator command as the available control or test action and continuously record saturation input and output; when the bounded input returns to its baseline, no autonomous mode grows and saturation input settles or remains bounded. After a small reversible change in amplitude-limited actuator command, observe saturation input; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from amplitude-limited actuator command to saturation input, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From amplitude-limited actuator command to saturation input, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording saturation input and output while applying amplitude-limited actuator command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of amplitude-limited actuator command are applied while recording saturation input and output, the actuator clips its input through a memoryless sector-bounded saturation map, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering amplitude-limited actuator command together with the recorded quantities saturation input and output, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from amplitude-limited actuator command to saturation input is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

saturation input and output

### Actuators

amplitude-limited actuator command

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 180. Certify absolute stability of a saturated loop with the circle criterion

### Control Problem Description

Use sector-bounded actuator command as the available control or test action and continuously record loop input, output, and closed-loop response; when the bounded input returns to its baseline, no autonomous mode grows and loop input settles or remains bounded. After a small reversible change in sector-bounded actuator command, observe loop input; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from sector-bounded actuator command to loop input, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From sector-bounded actuator command to loop input, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording loop input, output, and closed-loop response while applying sector-bounded actuator command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of sector-bounded actuator command are applied while recording loop input, output, and closed-loop response, the actuator belongs to a declared static sector used by the circle-criterion test, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering sector-bounded actuator command together with the recorded quantities loop input, output, and closed-loop response, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from sector-bounded actuator command to loop input is repeated after varying relevant physical parameters and operating conditions within safe limits, the motion direction, response timing, and final level remain almost unchanged, leaving only numerical or sampling variation.

### Observable Outputs

loop input, output, and closed-loop response

### Actuators

sector-bounded actuator command

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

2.0

---

## 181. Model a flexible two-body satellite and translate pointing specifications into robust design targets

### Control Problem Description

Use body control torque as the available control or test action and continuously record two satellite angles, rates, pointing error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets two satellite angles retain an offset or drift after the prescribed drive is removed. After a small reversible change in body control torque, observe two satellite angles; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from body control torque to two satellite angles, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From body control torque to two satellite angles, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording two satellite angles, rates, pointing error while applying body control torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of body control torque are applied while recording two satellite angles, rates, pointing error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering body control torque together with the recorded quantities two satellite angles, rates, pointing error, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from body control torque to two satellite angles is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

two satellite angles, rates, pointing error

### Actuators

body control torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 182. Compare gain stabilization and notch-based phase stabilization of the flexible satellite

### Control Problem Description

Use gain-shaped or notch-shaped torque as the available control or test action and continuously record satellite pointing and flexible deflection; when the bounded input returns to its baseline, an integrating or non-restoring mode lets satellite pointing retain an offset or drift after the prescribed drive is removed. After a small reversible change in gain-shaped or notch-shaped torque, observe satellite pointing; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from gain-shaped or notch-shaped torque to satellite pointing, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From gain-shaped or notch-shaped torque to satellite pointing, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording satellite pointing and flexible deflection while applying gain-shaped or notch-shaped torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of gain-shaped or notch-shaped torque are applied while recording satellite pointing and flexible deflection, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering gain-shaped or notch-shaped torque together with the recorded quantities satellite pointing and flexible deflection, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from gain-shaped or notch-shaped torque to satellite pointing is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

satellite pointing and flexible deflection

### Actuators

gain-shaped or notch-shaped torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 183. Design satellite state feedback and an estimator from symmetric-root-locus pole choices

### Control Problem Description

Use estimated-state feedback torque as the available control or test action and continuously record measured attitude and estimated flexible states; when the bounded input returns to its baseline, an integrating or non-restoring mode lets measured attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in estimated-state feedback torque, observe measured attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from estimated-state feedback torque to measured attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From estimated-state feedback torque to measured attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording measured attitude and estimated flexible states while applying estimated-state feedback torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of estimated-state feedback torque are applied while recording measured attitude and estimated flexible states, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering estimated-state feedback torque together with the recorded quantities measured attitude and estimated flexible states, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from estimated-state feedback torque to measured attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

measured attitude and estimated flexible states

### Actuators

estimated-state feedback torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 184. Redesign the satellite by collocating the attitude sensor with the torque actuator

### Control Problem Description

Use collocated body torque as the available control or test action and continuously record collocated attitude and remote flexible angle; when the bounded input returns to its baseline, an integrating or non-restoring mode lets collocated attitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in collocated body torque, observe collocated attitude; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from collocated body torque to collocated attitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From collocated body torque to collocated attitude, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording collocated attitude and remote flexible angle while applying collocated body torque makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of collocated body torque are applied while recording collocated attitude and remote flexible angle, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering collocated body torque together with the recorded quantities collocated attitude and remote flexible angle, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from collocated body torque to collocated attitude is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

collocated attitude and remote flexible angle

### Actuators

collocated body torque

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
apply an unbounded open-loop command to a marginal or unstable mode

### Dominant Time Scale (Seconds)

5.0

---

## 185. Linearize Boeing 747 longitudinal/lateral dynamics and identify Dutch-roll, spiral, roll, phugoid, and short-period modes

### Control Problem Description

Use rudder, elevator, aileron, thrust as the available control or test action and continuously record aircraft rates, attitude, speed, altitude; when the bounded input returns to its baseline, no autonomous mode grows and aircraft rates settles or remains bounded. After a small reversible change in rudder, elevator, aileron, thrust, observe aircraft rates; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from rudder, elevator, aileron, thrust to aircraft rates, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From rudder, elevator, aileron, thrust to aircraft rates, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording aircraft rates, attitude, speed, altitude while applying rudder, elevator, aileron, thrust makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of rudder, elevator, aileron, thrust are applied while recording aircraft rates, attitude, speed, altitude, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering rudder, elevator, aileron, thrust together with the recorded quantities aircraft rates, attitude, speed, altitude, changing any one of several actuators visibly moves several recordings, so actuator directions must be allocated or paired together. When the bounded test from rudder, elevator, aileron, thrust to aircraft rates is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

aircraft rates, attitude, speed, altitude

### Actuators

rudder, elevator, aileron, thrust

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
change several actuator channels simultaneously during the first identification test

### Dominant Time Scale (Seconds)

5.0

---

## 186. Design a yaw damper with rudder actuation, yaw-rate sensing, actuator dynamics, and washout

### Control Problem Description

Use rudder command as the available control or test action and continuously record yaw rate, sideslip, rudder position; when the bounded input returns to its baseline, no autonomous mode grows and yaw rate settles or remains bounded. After a small reversible change in rudder command, observe yaw rate; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from rudder command to yaw rate, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From rudder command to yaw rate, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording yaw rate, sideslip, rudder position while applying rudder command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of rudder command are applied while recording yaw rate, sideslip, rudder position, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering rudder command together with the recorded quantities yaw rate, sideslip, rudder position, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from rudder command to yaw rate is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

yaw rate, sideslip, rudder position

### Actuators

rudder command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

5.0

---

## 187. Compare the practical yaw damper with a higher-order SRL controller-estimator design

### Control Problem Description

Use rudder command from low or high order control as the available control or test action and continuously record yaw rate and estimated lateral states; when the bounded input returns to its baseline, no autonomous mode grows and yaw rate settles or remains bounded. After a small reversible change in rudder command from low or high order control, observe yaw rate; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from rudder command from low or high order control to yaw rate, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From rudder command from low or high order control to yaw rate, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording yaw rate and estimated lateral states while applying rudder command from low or high order control makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of rudder command from low or high order control are applied while recording yaw rate and estimated lateral states, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering rudder command from low or high order control together with the recorded quantities yaw rate and estimated lateral states, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from rudder command from low or high order control to yaw rate is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

yaw rate and estimated lateral states

### Actuators

rudder command from low or high order control

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

5.0

---

## 188. Design an altitude-hold autopilot with pitch-rate/pitch inner loops and altitude outer-loop feedback

### Control Problem Description

Use elevator command as the available control or test action and continuously record altitude, pitch angle, pitch rate; when the bounded input returns to its baseline, an integrating or non-restoring mode lets altitude retain an offset or drift after the prescribed drive is removed. After a small reversible change in elevator command, observe altitude; the first useful output change moves in an unfavorable or opposite direction before turning toward its eventual value. For the same small change from elevator command to altitude, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From elevator command to altitude, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording altitude, pitch angle, pitch rate while applying elevator command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of elevator command are applied while recording altitude, pitch angle, pitch rate, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering elevator command together with the recorded quantities altitude, pitch angle, pitch rate, the outer response appears only through a separately stabilized inner attitude, rate, or biochemical path. When the bounded test from elevator command to altitude is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

altitude, pitch angle, pitch rate

### Actuators

elevator command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
disable the inner stabilizing channel while testing the outer command

### Dominant Time Scale (Seconds)

5.0

---

## 189. Model and tune PI feedback for a delayed automotive fuel-air process

### Control Problem Description

Use fuel injection command as the available control or test action and continuously record fuel air ratio and oxygen sensor signal; when the bounded input returns to its baseline, no autonomous mode grows and fuel air ratio settles or remains bounded. After a small reversible change in fuel injection command, observe fuel air ratio; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from fuel injection command to fuel air ratio, mixture transport, combustion, and oxygen sensing hold back the measured response to a fuel command, and a visible pause separates the command from the first recorded response. From fuel injection command to fuel air ratio, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording fuel air ratio and oxygen sensor signal while applying fuel injection command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of fuel injection command are applied while recording fuel air ratio and oxygen sensor signal, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering fuel injection command together with the recorded quantities fuel air ratio and oxygen sensor signal, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from fuel injection command to fuel air ratio is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

fuel air ratio and oxygen sensor signal

### Actuators

fuel injection command

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

5.0

---

## 190. Predict the nonlinear oxygen-sensor limit cycle by effective gain and describing function

### Control Problem Description

Use fuel injection command as the available control or test action and continuously record air fuel error and oxygen sensor oscillation; when the bounded input returns to its baseline, no autonomous mode grows and air fuel error settles or remains bounded. After a small reversible change in fuel injection command, observe air fuel error; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from fuel injection command to air fuel error, mixture transport, combustion, and oxygen sensing hold back the measured response to a fuel command, and a visible pause separates the command from the first recorded response. From fuel injection command to air fuel error, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording air fuel error and oxygen sensor oscillation while applying fuel injection command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of fuel injection command are applied while recording air fuel error and oxygen sensor oscillation, the oxygen sensor applies a steep static map to air-fuel error and can sustain a switching oscillation, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering fuel injection command together with the recorded quantities air fuel error and oxygen sensor oscillation, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from fuel injection command to air fuel error is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

air fuel error and oxygen sensor oscillation

### Actuators

fuel injection command

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

5.0

---

## 191. Replace sensor-slope dependence by relay feedback to obtain robust average stoichiometry

### Control Problem Description

Use fuel injection command through relay-conditioned sensing as the available control or test action and continuously record average fuel-air ratio and switching signal; when the bounded input returns to its baseline, no autonomous mode grows and average fuel-air ratio settles or remains bounded. After a small reversible change in fuel injection command through relay-conditioned sensing, observe average fuel-air ratio; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from fuel injection command through relay-conditioned sensing to average fuel-air ratio, mixture transport, combustion, and oxygen sensing hold back the measured response to a fuel command, and a visible pause separates the command from the first recorded response. From fuel injection command through relay-conditioned sensing to average fuel-air ratio, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording average fuel-air ratio and switching signal while applying fuel injection command through relay-conditioned sensing makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of fuel injection command through relay-conditioned sensing are applied while recording average fuel-air ratio and switching signal, relay conditioning replaces the uncertain sensor slope by fixed output levels before fuel control, and the departure from proportional behavior stays in this fixed input-output rule without adding another dynamic state. Considering fuel injection command through relay-conditioned sensing together with the recorded quantities average fuel-air ratio and switching signal, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from fuel injection command through relay-conditioned sensing to average fuel-air ratio is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

average fuel-air ratio and switching signal

### Actuators

fuel injection command through relay-conditioned sensing

### Safety Bounds

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
increase the command again before the delayed response becomes visible

### Dominant Time Scale (Seconds)

5.0

---

## 192. Build decoupled longitudinal, lateral, yaw, and altitude state models for a quadrotor and map four rotor commands

### Control Problem Description

Use four rotor thrust commands as the available control or test action and continuously record position, attitude, angular rates, altitude; when the bounded input returns to its baseline, an integrating or non-restoring mode lets position retain an offset or drift after the prescribed drive is removed. After a small reversible change in four rotor thrust commands, observe position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from four rotor thrust commands to position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From four rotor thrust commands to position, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording position, attitude, angular rates, altitude while applying four rotor thrust commands makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of four rotor thrust commands are applied while recording position, attitude, angular rates, altitude, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering four rotor thrust commands together with the recorded quantities position, attitude, angular rates, altitude, changing any one of several actuators visibly moves several recordings, so actuator directions must be allocated or paired together. When the bounded test from four rotor thrust commands to position is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

position, attitude, angular rates, altitude

### Actuators

four rotor thrust commands

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
change several actuator channels simultaneously during the first identification test

### Dominant Time Scale (Seconds)

5.0

---

## 193. Design cascaded inner-attitude and outer-position PD loops for quadrotor trajectory following

### Control Problem Description

Use mixed rotor thrusts as the available control or test action and continuously record quadrotor position, attitude, path error; when the bounded input returns to its baseline, an integrating or non-restoring mode lets quadrotor position retain an offset or drift after the prescribed drive is removed. After a small reversible change in mixed rotor thrusts, observe quadrotor position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from mixed rotor thrusts to quadrotor position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From mixed rotor thrusts to quadrotor position, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording quadrotor position, attitude, path error while applying mixed rotor thrusts makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of mixed rotor thrusts are applied while recording quadrotor position, attitude, path error, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering mixed rotor thrusts together with the recorded quantities quadrotor position, attitude, path error, the outer response appears only through a separately stabilized inner attitude, rate, or biochemical path. When the bounded test from mixed rotor thrusts to quadrotor position is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

quadrotor position, attitude, path error

### Actuators

mixed rotor thrusts

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
disable the inner stabilizing channel while testing the outer command

### Dominant Time Scale (Seconds)

5.0

---

## 194. Design LQR/estimator controllers for quadrotor longitudinal, lateral, and yaw axes

### Control Problem Description

Use LQR mixed rotor commands as the available control or test action and continuously record measured and estimated quadrotor axis states; when the bounded input returns to its baseline, an integrating or non-restoring mode lets measured retain an offset or drift after the prescribed drive is removed. After a small reversible change in LQR mixed rotor commands, observe measured; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from LQR mixed rotor commands to measured, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From LQR mixed rotor commands to measured, the actuator effect reaches the main output only after three or more successive storage or integration stages, or after a separately closed inner path. Recording measured and estimated quadrotor axis states while applying LQR mixed rotor commands makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of LQR mixed rotor commands are applied while recording measured and estimated quadrotor axis states, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering LQR mixed rotor commands together with the recorded quantities measured and estimated quadrotor axis states, changing any one of several actuators visibly moves several recordings, so actuator directions must be allocated or paired together. When the bounded test from LQR mixed rotor commands to measured is repeated after varying relevant physical parameters and operating conditions within safe limits, changes in inertia, flexible or aerodynamic motion, loading, sensing, or actuator effectiveness can materially alter both the response rate and channel interaction.

### Observable Outputs

measured and estimated quadrotor axis states

### Actuators

LQR mixed rotor commands

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
change several actuator channels simultaneously during the first identification test

### Dominant Time Scale (Seconds)

5.0

---

## 195. Identify nonlinear radiation/conduction dynamics and a three-state small-signal model for an RTP chamber

### Control Problem Description

Use common command to three lamps as the available control or test action and continuously record plate center and support temperatures; when the bounded input returns to its baseline, no autonomous mode grows and plate center settles or remains bounded. After a small reversible change in common command to three lamps, observe plate center; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from common command to three lamps to plate center, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From common command to three lamps to plate center, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording plate center and support temperatures while applying common command to three lamps makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of common command to three lamps are applied while recording plate center and support temperatures, radiation, lamp effectiveness, saturation, and the lack of active cooling change the thermal dynamics across the trajectory, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering common command to three lamps together with the recorded quantities plate center and support temperatures, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from common command to three lamps to plate center is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

plate center and support temperatures

### Actuators

common command to three lamps

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

20.0

---

## 196. Apply PI temperature-trajectory control while respecting the absence of active cooling

### Control Problem Description

Use nonnegative lamp power as the available control or test action and continuously record temperature trajectory and tracking error; when the bounded input returns to its baseline, no autonomous mode grows and temperature trajectory settles or remains bounded. After a small reversible change in nonnegative lamp power, observe temperature trajectory; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from nonnegative lamp power to temperature trajectory, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From nonnegative lamp power to temperature trajectory, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording temperature trajectory and tracking error while applying nonnegative lamp power makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of nonnegative lamp power are applied while recording temperature trajectory and tracking error, radiation, lamp effectiveness, saturation, and the lack of active cooling change the thermal dynamics across the trajectory, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering nonnegative lamp power together with the recorded quantities temperature trajectory and tracking error, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from nonnegative lamp power to temperature trajectory is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

temperature trajectory and tracking error

### Actuators

nonnegative lamp power

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

20.0

---

## 197. Design an error-space LQG regulator that balances tracking, actuation, and wafer-temperature uniformity

### Control Problem Description

Use common lamp command as the available control or test action and continuously record center temperature, estimated three-node temperatures, and uniformity; when the bounded input returns to its baseline, no autonomous mode grows and center temperature settles or remains bounded. After a small reversible change in common lamp command, observe center temperature; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from common lamp command to center temperature, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From common lamp command to center temperature, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording center temperature, estimated three-node temperatures, and uniformity while applying common lamp command makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of common lamp command are applied while recording center temperature, estimated three-node temperatures, and uniformity, radiation, lamp effectiveness, saturation, and the lack of active cooling change the thermal dynamics across the trajectory, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering common lamp command together with the recorded quantities center temperature, estimated three-node temperatures, and uniformity, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from common lamp command to center temperature is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

center temperature, estimated three-node temperatures, and uniformity

### Actuators

common lamp command

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

20.0

---

## 198. Verify RTP control with lamp inversion, saturation, antiwindup, and a digital prototype

### Control Problem Description

Use digitally commanded lamp voltage as the available control or test action and continuously record wafer temperatures, lamp voltage, integrator state; when the bounded input returns to its baseline, no autonomous mode grows and wafer temperatures settles or remains bounded. After a small reversible change in digitally commanded lamp voltage, observe wafer temperatures; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from digitally commanded lamp voltage to wafer temperatures, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From digitally commanded lamp voltage to wafer temperatures, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording wafer temperatures, lamp voltage, integrator state while applying digitally commanded lamp voltage makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of digitally commanded lamp voltage are applied while recording wafer temperatures, lamp voltage, integrator state, radiation, lamp effectiveness, saturation, and the lack of active cooling change the thermal dynamics across the trajectory, so the response law changes with the evolving state and one fixed local gain cannot represent the full motion. Considering digitally commanded lamp voltage together with the recorded quantities wafer temperatures, lamp voltage, integrator state, several recordings share internal motion, yet each declared channel can be exercised without a large cross-channel correction. When the bounded test from digitally commanded lamp voltage to wafer temperatures is repeated after varying relevant physical parameters and operating conditions within safe limits, operating point, load, unmodeled motion, sensing, or actuator effectiveness can materially change the response rate, final level, or safe excursion.

### Observable Outputs

wafer temperatures, lamp voltage, integrator state

### Actuators

digitally commanded lamp voltage

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
replace the declared nonlinearity by an unrestricted linear element during safety verification

### Dominant Time Scale (Seconds)

20.0

---

## 199. Model exact adaptation in E. coli chemotaxis as integral feedback of receptor activity

### Control Problem Description

Use ligand concentration as the prescribed pathway input as the available control or test action and continuously record receptor activity and methylation state; when the bounded input returns to its baseline, no autonomous mode grows and receptor activity settles or remains bounded. After a small reversible change in ligand concentration as the prescribed pathway input, observe receptor activity; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from ligand concentration as the prescribed pathway input to receptor activity, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From ligand concentration as the prescribed pathway input to receptor activity, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording receptor activity and methylation state while applying ligand concentration as the prescribed pathway input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of ligand concentration as the prescribed pathway input are applied while recording receptor activity and methylation state, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering ligand concentration as the prescribed pathway input together with the recorded quantities receptor activity and methylation state, one principal action-to-recording path carries the experiment and any listed disturbance enters separately. When the bounded test from ligand concentration as the prescribed pathway input to receptor activity is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

receptor activity and methylation state

### Actuators

ligand concentration as the prescribed pathway input

### Safety Bounds

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
reuse nominal gains outside the declared operating region without bounded validation

### Dominant Time Scale (Seconds)

5.0

---

## 200. Map CheY activity into the one-dimensional mean chemotaxis motion model

### Control Problem Description

Use ligand perturbation as the prescribed pathway input as the available control or test action and continuously record mean cell position, receptor activity, and methylation; when the bounded input returns to its baseline, an integrating or non-restoring mode lets mean cell position retain an offset or drift after the prescribed drive is removed. After a small reversible change in ligand perturbation as the prescribed pathway input, observe mean cell position; the first useful output change follows its eventual direction and does not move the opposite way first. For the same small change from ligand perturbation as the prescribed pathway input to mean cell position, dynamic lag is present but no separate transport, sensing, or computation pause precedes useful output motion, so the first recorded change begins promptly without a separate silent interval. From ligand perturbation as the prescribed pathway input to mean cell position, the actuator effect reaches the measured output through no more than two dominant storage or integration stages, while any additional modes shape the later waveform rather than postponing the first response. Recording mean cell position, receptor activity, and methylation while applying ligand perturbation as the prescribed pathway input makes every relevant motion mode appear in at least one recording and change under an available input. When permitted changes in the direction or amplitude of ligand perturbation as the prescribed pathway input are applied while recording mean cell position, receptor activity, and methylation, small positive and negative trials remain smooth, reversible, and nearly proportional, with no observed dead zone, hysteresis, or amplitude clipping. Considering ligand perturbation as the prescribed pathway input together with the recorded quantities mean cell position, receptor activity, and methylation, the outer response appears only through a separately stabilized inner attitude, rate, or biochemical path. When the bounded test from ligand perturbation as the prescribed pathway input to mean cell position is repeated after varying relevant physical parameters and operating conditions within safe limits, subject variation, physiological condition, sensing, and endogenous actuation can materially change the response rate and final recorded level.

### Observable Outputs

mean cell position, receptor activity, and methylation

### Actuators

ligand perturbation as the prescribed pathway input

### Safety Bounds

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### Forbidden Actions

issue commands to physical hardware
disable simulated saturation or automatic stopping checks
continue after an output or actuator limit is crossed
disable the inner stabilizing channel while testing the outer command

### Dominant Time Scale (Seconds)

5.0

---
