# CFDC Dataset: Guided Natural-Language Inputs for Two Hundred Classic Control Problems

<!-- GUIDED-UI-PROMPT-AUDIT: natural-language flow -->

> Each entry follows the current guided UI in two paste-ready stages: Control Problem Description and Profile Measurement Response. The eight-item checklist is grounded directly from the description rather than repeated as a measurement task. All records are synthetic software records for analysis and acceptance testing; they do not authorize commands to physical hardware.

Paste the control description first. Once its eight-item checklist is grounded, classification and Profile selection happen automatically; then paste only the requested Profile measurement response. No separate diagnostic-record repetition, observable-output, actuator, safety, forbidden-action, dominant-time-scale, or JSON field is required.

---

## 1. Household thermostat with hysteresis

### Control Problem Description

This is a residential heating system in which a thermostat watches room temperature and switches an electric heater on and off. The control input is binary heater command, and the measured outputs are room temperature, heater state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in room temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 60 s sample interval; after binary heater command changes, room temperature begins within one sample, with its first distinguishable change recorded 60 s after the input change and without a separate silent interval. The path from binary heater command actuation to the visible room temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the room temperature response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of binary heater command reveals fixed hysteresis and relay switching, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in binary heater command can drive a distinguishable change in the key output room temperature; binary heater command and the recorded readings room temperature, heater state share one clock, so all relevant motion can be reconstructed from these synchronized records. One binary heater command action affects the recorded readings room temperature, heater state; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use an outdoor temperature of 50 degF, a 65 degF setpoint, heat capacity 20000 Btu/degF, heat-loss coefficient 500 Btu/(h*degF), furnace rate 25000 Btu/h, and a 0.5 degF hysteresis half-width. Start at 64.5 degF with the furnace on and simulate for 6 h at 60 s sampling.

The existing record reports that changing binary heater command by 1 binary-command level produces a steady room temperature change of 50 degF with a recorded response time of 144000 s. For software simulation, binary heater command is limited from 0 binary-command level to 1 binary-command level. The simulation stops if room temperature leaves 64.5 degF to 65.5 degF.

The declared software model is a transfer function from binary heater command in binary-command units to room temperature in degF. Its numerator coefficients are 50; its denominator coefficients are 144000, 1; and its input delay is 0 s.

The accompanying existing software record uses a 60 s sample interval for 21600 s, starts the primary output at 64.5, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 2. Automobile cruise control, open versus closed loop

### Control Problem Description

This is a road vehicle whose longitudinal speed is set by engine traction acting against rolling and aerodynamic resistance. The control input is throttle angle, and the measured outputs are vehicle speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in vehicle speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after throttle angle changes, vehicle speed begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from throttle angle actuation to the visible vehicle speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the vehicle speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in throttle angle produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in throttle angle can drive a distinguishable change in the key output vehicle speed; throttle angle and the recorded readings vehicle speed share one clock, so all relevant motion can be reconstructed from these synchronized records. One throttle angle action affects the recorded readings vehicle speed; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for vehicle speed.


### Profile Measurement Response (Natural Language)

Around 65 mph, change throttle angle by 1 deg and use a 10 mph steady speed change per degree. Treat a 1% uphill grade as a -5 mph disturbance, use a 5 s response time for the dynamic simulation, and compare open loop with proportional feedback gain 10.

The existing record reports that changing throttle angle by 1 deg produces a steady vehicle speed change of 10 mph with a recorded response time of 5 s. For software simulation, throttle angle is limited from -3 deg to 3 deg. The simulation stops if vehicle speed leaves 45 mph to 80 mph.

The declared software model is a transfer function from throttle angle in deg to vehicle speed in mph. Its numerator coefficients are 10; its denominator coefficients are 5, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 60 s, starts the primary output at 65, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 3. Manual automobile steering

### Control Problem Description

This is a road vehicle whose driver corrects heading and lane position through the steering wheel. The control input is steering wheel angle, and the measured outputs are heading angle, lane error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heading angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.03 s sample interval; after steering wheel angle changes, heading angle begins within one sample, with its first distinguishable change recorded 0.03 s after the input change and without a separate silent interval. The path from steering wheel angle actuation to the visible heading angle response contains one or two dominant storage or integration processes. When the input returns to baseline, the heading angle response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steering wheel angle produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in steering wheel angle can drive a distinguishable change in the key output heading angle; steering wheel angle and the recorded readings heading angle, lane error share one clock, so all relevant motion can be reconstructed from these synchronized records. One steering wheel angle action affects the recorded readings heading angle, lane error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change steering wheel angle by 5 deg; expect a final heading angle, lane error change of 8 deg with a 63% response time of 1.5 s. Use an input range of -30 to 30 deg and an output range of -180 to 180 deg; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing steering wheel angle by 5 deg produces a steady heading angle change of 8 deg with a recorded response time of 1.5 s. For software simulation, steering wheel angle is limited from -30 deg to 30 deg. The simulation stops if heading angle leaves -180 deg to 180 deg.

The declared software model is a transfer function from steering wheel angle in deg to heading angle in deg. Its numerator coefficients are 1.6; its denominator coefficients are 1.5, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.03 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -5, -2.5, 2.5, 5, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 4. Drebbel incubator temperature regulator

### Control Problem Description

This is an incubator made from a heated water jacket, a furnace, and a mechanical temperature-regulating linkage. The control input is air or fuel valve position, and the measured outputs are incubator temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in incubator temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 2.4 s sample interval; after air or fuel valve position changes, incubator temperature begins within one sample, with its first distinguishable change recorded 2.4 s after the input change and without a separate silent interval. The path from air or fuel valve position actuation to the visible incubator temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the incubator temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in air or fuel valve position produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in air or fuel valve position can drive a distinguishable change in the key output incubator temperature; air or fuel valve position and the recorded readings incubator temperature share one clock, so all relevant motion can be reconstructed from these synchronized records. One air or fuel valve position action affects the recorded readings incubator temperature; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change air or fuel valve position by 10 %; expect a final incubator temperature change of 2 degC with a 63% response time of 120 s. Use an input range of 0 to 100 % and an output range of 30 to 42 degC; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing air or fuel valve position by 10 % produces a steady incubator temperature change of 2 degC with a recorded response time of 120 s. For software simulation, air or fuel valve position is limited from 0 % to 100 %. The simulation stops if incubator temperature leaves 30 degC to 42 degC.

The declared software model is a transfer function from air or fuel valve position in % to incubator temperature in degC. Its numerator coefficients are 0.2; its denominator coefficients are 120, 1; and its input delay is 0 s.

The accompanying existing software record uses a 2.4 s sample interval for 960 s, starts the primary output at 36, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 5. Float-valve water-level regulator

### Control Problem Description

This is a storage tank whose rising and falling float mechanically changes the inlet-valve opening. The control input is inlet valve opening, and the measured outputs are tank liquid level, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tank liquid level starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.4 s sample interval; after inlet valve opening changes, tank liquid level begins within one sample, with its first distinguishable change recorded 0.4 s after the input change and without a separate silent interval. The path from inlet valve opening actuation to the visible tank liquid level response contains one or two dominant storage or integration processes. When the input returns to baseline, the tank liquid level response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in inlet valve opening produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in inlet valve opening can drive a distinguishable change in the key output tank liquid level; inlet valve opening and the recorded readings tank liquid level share one clock, so all relevant motion can be reconstructed from these synchronized records. One inlet valve opening action affects the recorded readings tank liquid level; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change inlet valve opening by 10 %; expect a final tank liquid level change of 0.08 m with a 63% response time of 20 s. Use an input range of 0 to 100 % and an output range of 0.2 to 1.2 m; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing inlet valve opening by 10 % produces a steady tank liquid level change of 0.08 m with a recorded response time of 20 s. For software simulation, inlet valve opening is limited from 0 % to 100 %. The simulation stops if tank liquid level leaves 0.2 m to 1.2 m.

The declared software model is a transfer function from inlet valve opening in % to tank liquid level in m. Its numerator coefficients are 0.008; its denominator coefficients are 20, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.4 s sample interval for 160 s, starts the primary output at 0.7, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 6. Watt fly-ball steam-engine governor

### Control Problem Description

This is a mechanical engine governor in which fly-balls and linkage reposition a steam valve as shaft speed changes. The control input is steam valve opening, and the measured outputs are engine shaft speed, governor displacement, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in engine shaft speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.16 s sample interval; after steam valve opening changes, engine shaft speed begins within one sample, with its first distinguishable change recorded 0.16 s after the input change and without a separate silent interval. The path from steam valve opening actuation to the visible engine shaft speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the engine shaft speed response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of steam valve opening reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in steam valve opening can drive a distinguishable change in the key output engine shaft speed; steam valve opening and the recorded readings engine shaft speed, governor displacement share one clock, so all relevant motion can be reconstructed from these synchronized records. One steam valve opening action affects the recorded readings engine shaft speed, governor displacement; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change steam valve opening by 10 %; expect a final engine shaft speed, governor displacement change of 20 rpm with a 63% response time of 8 s. Use an input range of 0 to 100 % and an output range of 400 to 900 rpm; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing steam valve opening by 10 % produces a steady engine shaft speed change of 20 rpm with a recorded response time of 8 s. For software simulation, steam valve opening is limited from 0 % to 100 %. The simulation stops if engine shaft speed leaves 400 rpm to 900 rpm.

The declared software model is a transfer function from steam valve opening in % to engine shaft speed in rpm. Its numerator coefficients are 2; its denominator coefficients are 8, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.16 s sample interval for 64 s, starts the primary output at 650, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 7. Paper-machine stock-consistency control

### Control Problem Description

This is the wet-end section of a paper machine, where dilution water is used to hold pulp consistency steady. The control input is dilution water valve, and the measured outputs are stock consistency, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in stock consistency starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.6 s sample interval; after dilution water valve changes, stock consistency begins within one sample, with its first distinguishable change recorded 0.6 s after the input change and without a separate silent interval. The path from dilution water valve actuation to the visible stock consistency response contains one or two dominant storage or integration processes. When the input returns to baseline, the stock consistency response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in dilution water valve produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in dilution water valve can drive a distinguishable change in the key output stock consistency; dilution water valve and the recorded readings stock consistency share one clock, so all relevant motion can be reconstructed from these synchronized records. One dilution water valve action affects the recorded readings stock consistency; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change dilution water valve by 5 %; expect a final stock consistency change of -0.4 % with a 63% response time of 30 s. Use an input range of 0 to 100 % and an output range of 2 to 6 %; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing dilution water valve by 5 % produces a steady stock consistency change of -0.4 % with a recorded response time of 30 s. For software simulation, dilution water valve is limited from 0 % to 100 %. The simulation stops if stock consistency leaves 2 % to 6 %.

The declared software model is a transfer function from dilution water valve in % to stock consistency in %. Its numerator coefficients are -0.08; its denominator coefficients are 30, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.6 s sample interval for 240 s, starts the primary output at 4, contains input amplitudes -5, -2.5, 2.5, 5, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 8. Paper-machine moisture control

### Control Problem Description

This is the dryer section of a paper machine, where steam delivery determines the moisture left in the sheet. The control input is dryer steam command, and the measured outputs are paper moisture, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in paper moisture starts in its final direction rather than moving the opposite way first. The synchronized record has a 1.2 s sample interval; after dryer steam command changes, paper moisture begins within one sample, with its first distinguishable change recorded 1.2 s after the input change and without a separate silent interval. The path from dryer steam command actuation to the visible paper moisture response contains one or two dominant storage or integration processes. When the input returns to baseline, the paper moisture response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in dryer steam command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in dryer steam command can drive a distinguishable change in the key output paper moisture; dryer steam command and the recorded readings paper moisture share one clock, so all relevant motion can be reconstructed from these synchronized records. One dryer steam command action affects the recorded readings paper moisture; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change dryer steam command by 10 %; expect a final paper moisture change of -1.2 % with a 63% response time of 60 s and use 8 s pure delay. Use an input range of 0 to 100 % and an output range of 2 to 12 %; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing dryer steam command by 10 % produces a steady paper moisture change of -1.2 % with a recorded response time of 60 s. The recorded dead time is 8 s. For software simulation, dryer steam command is limited from 0 % to 100 %. The simulation stops if paper moisture leaves 2 % to 12 %.

The declared software model is a transfer function from dryer steam command in % to paper moisture in %. Its numerator coefficients are -0.12; its denominator coefficients are 60, 1; and its input delay is 8 s.

The accompanying existing software record uses a 1.2 s sample interval for 480 s, starts the primary output at 7, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 9. Human blood-pressure regulation

### Control Problem Description

This is a cardiovascular system in which the heart, blood vessels, and autonomic reflexes jointly regulate arterial pressure. The control input is neural cardiac and vascular commands, and the measured outputs are arterial pressure, heart rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in arterial pressure starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.12 s sample interval; after neural cardiac and vascular commands changes, arterial pressure begins within one sample, with its first distinguishable change recorded 0.12 s after the input change and without a separate silent interval. The path from neural cardiac and vascular commands actuation to the visible arterial pressure response contains one or two dominant storage or integration processes. When the input returns to baseline, the arterial pressure response settles or remains bounded instead of developing self-growing motion. As the size or operating point of neural cardiac and vascular commands changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in neural cardiac and vascular commands can drive a distinguishable change in the key output arterial pressure; neural cardiac and vascular commands and the recorded readings arterial pressure, heart rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One neural cardiac and vascular commands action affects the recorded readings arterial pressure, heart rate; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change neural cardiac and vascular commands by 0.1 neural_command; expect a final arterial pressure, heart rate change of 8 mmHg with a 63% response time of 6 s. Use an input range of -0.5 to 0.5 neural_command and an output range of 60 to 140 mmHg; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing neural cardiac and vascular commands by 0.1 neural_command produces a steady arterial pressure change of 8 mmHg with a recorded response time of 6 s. For software simulation, neural cardiac and vascular commands is limited from -0.5 neural_command to 0.5 neural_command. The simulation stops if arterial pressure leaves 60 mmHg to 140 mmHg.

The declared software model is a transfer function from neural cardiac and vascular commands in neural_command to arterial pressure in mmHg. Its numerator coefficients are 80; its denominator coefficients are 6, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.12 s sample interval for 48 s, starts the primary output at 100, contains input amplitudes -0.1, -0.05, 0.05, 0.1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 10. Human blood-glucose regulation

### Control Problem Description

This is a metabolic regulation system in which insulin and counter-regulatory hormones jointly maintain blood glucose. The control input is endogenous insulin and counterregulation, and the measured outputs are blood glucose, insulin level, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in blood glucose starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.4 s sample interval; after endogenous insulin and counterregulation changes, blood glucose begins within one sample, with its first distinguishable change recorded 0.4 s after the input change and without a separate silent interval. The path from endogenous insulin and counterregulation actuation to the visible blood glucose response contains one or two dominant storage or integration processes. When the input returns to baseline, the blood glucose response settles or remains bounded instead of developing self-growing motion. As the size or operating point of endogenous insulin and counterregulation changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in endogenous insulin and counterregulation can drive a distinguishable change in the key output blood glucose; endogenous insulin and counterregulation and the recorded readings blood glucose, insulin level share one clock, so all relevant motion can be reconstructed from these synchronized records. One endogenous insulin and counterregulation action affects the recorded readings blood glucose, insulin level; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change endogenous insulin and counterregulation by 0.1 insulin_command; expect a final blood glucose, insulin level change of -12 mg/dL with a 63% response time of 20 s. Use an input range of -0.5 to 0.5 insulin_command and an output range of 60 to 180 mg/dL; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing endogenous insulin and counterregulation by 0.1 insulin_command produces a steady blood glucose change of -12 mg/dL with a recorded response time of 20 s. For software simulation, endogenous insulin and counterregulation is limited from -0.5 insulin_command to 0.5 insulin_command. The simulation stops if blood glucose leaves 60 mg/dL to 180 mg/dL.

The declared software model is a transfer function from endogenous insulin and counterregulation in insulin_command to blood glucose in mg/dL. Its numerator coefficients are -120; its denominator coefficients are 20, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.4 s sample interval for 160 s, starts the primary output at 120, contains input amplitudes -0.1, -0.05, 0.05, 0.1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 11. Human heart-rate regulation

### Control Problem Description

This is a heart-rate regulation system in which sympathetic and parasympathetic nerves act on the cardiac pacemaker. The control input is sympathetic and parasympathetic drive, and the measured outputs are heart rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heart rate starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after sympathetic and parasympathetic drive changes, heart rate begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from sympathetic and parasympathetic drive actuation to the visible heart rate response contains one or two dominant storage or integration processes. When the input returns to baseline, the heart rate response settles or remains bounded instead of developing self-growing motion. As the size or operating point of sympathetic and parasympathetic drive changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in sympathetic and parasympathetic drive can drive a distinguishable change in the key output heart rate; sympathetic and parasympathetic drive and the recorded readings heart rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One sympathetic and parasympathetic drive action affects the recorded readings heart rate; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change sympathetic and parasympathetic drive by 0.1 autonomic_command; expect a final heart rate change of 8 bpm with a 63% response time of 5 s. Use an input range of -0.5 to 0.5 autonomic_command and an output range of 45 to 160 bpm; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing sympathetic and parasympathetic drive by 0.1 autonomic_command produces a steady heart rate change of 8 bpm with a recorded response time of 5 s. For software simulation, sympathetic and parasympathetic drive is limited from -0.5 autonomic_command to 0.5 autonomic_command. The simulation stops if heart rate leaves 45 bpm to 160 bpm.

The declared software model is a transfer function from sympathetic and parasympathetic drive in autonomic_command to heart rate in bpm. Its numerator coefficients are 80; its denominator coefficients are 5, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 40 s, starts the primary output at 102.5, contains input amplitudes -0.1, -0.05, 0.05, 0.1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 12. Eye-pointing-angle control

### Control Problem Description

This is an eye-pointing system in which the extraocular muscles rotate the eyeball to reduce retinal error. The control input is ocular muscle torque, and the measured outputs are eye angle, retinal error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in eye angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after ocular muscle torque changes, eye angle begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from ocular muscle torque actuation to the visible eye angle response contains one or two dominant storage or integration processes. When the input returns to baseline, the eye angle response settles or remains bounded instead of developing self-growing motion. As the size or operating point of ocular muscle torque changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in ocular muscle torque can drive a distinguishable change in the key output eye angle; ocular muscle torque and the recorded readings eye angle, retinal error share one clock, so all relevant motion can be reconstructed from these synchronized records. One ocular muscle torque action affects the recorded readings eye angle, retinal error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change ocular muscle torque by 0.002 Nm; expect a final eye angle, retinal error change of 0.12 rad with a 63% response time of 0.18 s. Use an input range of -0.01 to 0.01 Nm and an output range of -0.5 to 0.5 rad; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing ocular muscle torque by 0.002 Nm produces a steady eye angle change of 0.12 rad with a recorded response time of 0.18 s. For software simulation, ocular muscle torque is limited from -0.01 Nm to 0.01 Nm. The simulation stops if eye angle leaves -0.5 rad to 0.5 rad.

The declared software model is a transfer function from ocular muscle torque in Nm to eye angle in rad. Its numerator coefficients are 60; its denominator coefficients are 0.18, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 1.44 s, starts the primary output at 0, contains input amplitudes -0.002, -0.001, 0.001, 0.002, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 13. Pupil-diameter light regulation

### Control Problem Description

This is a pupillary light-reflex system in which iris muscles change aperture to regulate retinal illumination. The control input is iris muscle activation, and the measured outputs are pupil diameter, retinal illumination, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pupil diameter starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.016 s sample interval; after iris muscle activation changes, pupil diameter begins within one sample, with its first distinguishable change recorded 0.016 s after the input change and without a separate silent interval. The path from iris muscle activation actuation to the visible pupil diameter response contains one or two dominant storage or integration processes. When the input returns to baseline, the pupil diameter response settles or remains bounded instead of developing self-growing motion. As the size or operating point of iris muscle activation changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in iris muscle activation can drive a distinguishable change in the key output pupil diameter; iris muscle activation and the recorded readings pupil diameter, retinal illumination share one clock, so all relevant motion can be reconstructed from these synchronized records. One iris muscle activation action affects the recorded readings pupil diameter, retinal illumination; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change iris muscle activation by 0.1 iris_command; expect a final pupil diameter, retinal illumination change of -0.8 mm with a 63% response time of 0.8 s. Use an input range of -1 to 1 iris_command and an output range of 2 to 8 mm; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing iris muscle activation by 0.1 iris_command produces a steady pupil diameter change of -0.8 mm with a recorded response time of 0.8 s. For software simulation, iris muscle activation is limited from -1 iris_command to 1 iris_command. The simulation stops if pupil diameter leaves 2 mm to 8 mm.

The declared software model is a transfer function from iris muscle activation in iris_command to pupil diameter in mm. Its numerator coefficients are -8; its denominator coefficients are 0.8, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.016 s sample interval for 6.4 s, starts the primary output at 5, contains input amplitudes -0.1, -0.05, 0.05, 0.1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 14. Elevator position control with coarse/fine sensing and cable stretch

### Control Problem Description

This is an elevator positioning apparatus made from a hoist motor, brake, car, and elastic suspension cable. The control input is hoist motor torque and brake, and the measured outputs are car position, landing error, cable stretch, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in car position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after hoist motor torque and brake changes, car position begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from hoist motor torque and brake actuation to the visible car position response contains one or two dominant storage or integration processes. When the input returns to baseline, the car position response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in hoist motor torque and brake produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in hoist motor torque and brake can drive a distinguishable change in the key output car position; hoist motor torque and brake and the recorded readings car position, landing error, cable stretch share one clock, so all relevant motion can be reconstructed from these synchronized records. One hoist motor torque and brake action affects the recorded readings car position, landing error, cable stretch; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change hoist motor torque and brake by 100 Nm; expect a final car position, landing error, cable stretch change of 0.15 m with a 63% response time of 2.5 s. Use an input range of -1500 to 1500 Nm and an output range of 0 to 120 m; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing hoist motor torque and brake by 100 Nm produces a steady car position change of 0.15 m with a recorded response time of 2.5 s. For software simulation, hoist motor torque and brake is limited from -1500 Nm to 1500 Nm. The simulation stops if car position leaves 0 m to 120 m.

The declared software model is a transfer function from hoist motor torque and brake in Nm to car position in m. Its numerator coefficients are 0.0015; its denominator coefficients are 2.5, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 20 s, starts the primary output at 60, contains input amplitudes -100, -50, 50, 100, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 15. Electrical temperature sensing and actuation

### Control Problem Description

This is a temperature-control apparatus made from an electric heater, a thermal body, and an electrical temperature sensor. The control input is electrical heater voltage, and the measured outputs are temperature, sensor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 1.6 s sample interval; after electrical heater voltage changes, temperature begins within one sample, with its first distinguishable change recorded 1.6 s after the input change and without a separate silent interval. The path from electrical heater voltage actuation to the visible temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in electrical heater voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in electrical heater voltage can drive a distinguishable change in the key output temperature; electrical heater voltage and the recorded readings temperature, sensor voltage share one clock, so all relevant motion can be reconstructed from these synchronized records. One electrical heater voltage action affects the recorded readings temperature, sensor voltage; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change electrical heater voltage by 5 V; expect a final temperature, sensor voltage change of 8 degC with a 63% response time of 80 s. Use an input range of 0 to 48 V and an output range of 15 to 90 degC; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing electrical heater voltage by 5 V produces a steady temperature change of 8 degC with a recorded response time of 80 s. For software simulation, electrical heater voltage is limited from 0 V to 48 V. The simulation stops if temperature leaves 15 degC to 90 degC.

The declared software model is a transfer function from electrical heater voltage in V to temperature in degC. Its numerator coefficients are 1.6; its denominator coefficients are 80, 1; and its input delay is 0 s.

The accompanying existing software record uses a 1.6 s sample interval for 640 s, starts the primary output at 52.5, contains input amplitudes -5, -2.5, 2.5, 5, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 16. Electrical pressure sensing and actuation

### Control Problem Description

This is a pressure-control apparatus made from a regulating valve, a pressurized chamber, and a pressure transmitter. The control input is valve command, and the measured outputs are pressure, sensor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pressure starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.24 s sample interval; after valve command changes, pressure begins within one sample, with its first distinguishable change recorded 0.24 s after the input change and without a separate silent interval. The path from valve command actuation to the visible pressure response contains one or two dominant storage or integration processes. When the input returns to baseline, the pressure response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in valve command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in valve command can drive a distinguishable change in the key output pressure; valve command and the recorded readings pressure, sensor voltage share one clock, so all relevant motion can be reconstructed from these synchronized records. One valve command action affects the recorded readings pressure, sensor voltage; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change valve command by 10 %; expect a final pressure, sensor voltage change of 30 kPa with a 63% response time of 12 s. Use an input range of 0 to 100 % and an output range of 0 to 500 kPa; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing valve command by 10 % produces a steady pressure change of 30 kPa with a recorded response time of 12 s. For software simulation, valve command is limited from 0 % to 100 %. The simulation stops if pressure leaves 0 kPa to 500 kPa.

The declared software model is a transfer function from valve command in % to pressure in kPa. Its numerator coefficients are 3; its denominator coefficients are 12, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.24 s sample interval for 96 s, starts the primary output at 250, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 17. Electrical liquid-level sensing and actuation

### Control Problem Description

This is a liquid-level apparatus made from a storage vessel, pump or valve, and a level transmitter. The control input is pump speed or valve position, and the measured outputs are liquid level, transmitter signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in liquid level starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.5 s sample interval; after pump speed or valve position changes, liquid level begins within one sample, with its first distinguishable change recorded 0.5 s after the input change and without a separate silent interval. The path from pump speed or valve position actuation to the visible liquid level response contains one or two dominant storage or integration processes. When the input returns to baseline, the liquid level response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in pump speed or valve position produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in pump speed or valve position can drive a distinguishable change in the key output liquid level; pump speed or valve position and the recorded readings liquid level, transmitter signal share one clock, so all relevant motion can be reconstructed from these synchronized records. One pump speed or valve position action affects the recorded readings liquid level, transmitter signal; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change pump speed or valve position by 10 %; expect a final liquid level, transmitter signal change of 0.1 m with a 63% response time of 25 s. Use an input range of 0 to 100 % and an output range of 0.1 to 1.5 m; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing pump speed or valve position by 10 % produces a steady liquid level change of 0.1 m with a recorded response time of 25 s. For software simulation, pump speed or valve position is limited from 0 % to 100 %. The simulation stops if liquid level leaves 0.1 m to 1.5 m.

The declared software model is a transfer function from pump speed or valve position in % to liquid level in m. Its numerator coefficients are 0.01; its denominator coefficients are 25, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.5 s sample interval for 200 s, starts the primary output at 0.8, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 18. Electrical pipe-flow sensing and actuation

### Control Problem Description

This is a pipeline flow-control apparatus made from a pipe, regulating valve, and flow sensor. The control input is control valve position, and the measured outputs are pipe flow rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pipe flow rate starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.08 s sample interval; after control valve position changes, pipe flow rate begins within one sample, with its first distinguishable change recorded 0.08 s after the input change and without a separate silent interval. The path from control valve position actuation to the visible pipe flow rate response contains one or two dominant storage or integration processes. When the input returns to baseline, the pipe flow rate response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in control valve position produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in control valve position can drive a distinguishable change in the key output pipe flow rate; control valve position and the recorded readings pipe flow rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One control valve position action affects the recorded readings pipe flow rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change control valve position by 10 %; expect a final pipe flow rate change of 0.02 m^3/s with a 63% response time of 4 s. Use an input range of 0 to 100 % and an output range of 0 to 0.2 m^3/s; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing control valve position by 10 % produces a steady pipe flow rate change of 0.02 m^3/s with a recorded response time of 4 s. For software simulation, control valve position is limited from 0 % to 100 %. The simulation stops if pipe flow rate leaves 0 m^3/s to 0.2 m^3/s.

The declared software model is a transfer function from control valve position in % to pipe flow rate in m^3/s. Its numerator coefficients are 0.002; its denominator coefficients are 4, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.08 s sample interval for 32 s, starts the primary output at 0.1, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 19. HPA-axis stress-hormone negative feedback

### Control Problem Description

This is a hormonal stress-regulation system formed by feedback among the hypothalamus, pituitary, and adrenal glands. The control input is endogenous secretion rates, and the measured outputs are hormone concentrations, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in hormone concentrations starts in its final direction rather than moving the opposite way first. The synchronized record has a 12 s sample interval; after endogenous secretion rates changes, hormone concentrations begins within one sample, with its first distinguishable change recorded 12 s after the input change and without a separate silent interval. The path from endogenous secretion rates actuation to the visible hormone concentrations response contains one or two dominant storage or integration processes. When the input returns to baseline, the hormone concentrations response settles or remains bounded instead of developing self-growing motion. As the size or operating point of endogenous secretion rates changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in endogenous secretion rates can drive a distinguishable change in the key output hormone concentrations; endogenous secretion rates and the recorded readings hormone concentrations share one clock, so all relevant motion can be reconstructed from these synchronized records. One endogenous secretion rates action affects the recorded readings hormone concentrations; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

In a safe simulation, change endogenous secretion rates by 1 ng/(mL*min); expect a final hormone concentrations change of 0.8 ng/mL with a 63% response time of 600 s. Use an input range of 0 to 5 ng/(mL*min) and an output range of 0 to 20 ng/mL; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

The existing record reports that changing endogenous secretion rates by 1 ng/(mL*min) produces a steady hormone concentrations change of 0.8 ng/mL with a recorded response time of 600 s. For software simulation, endogenous secretion rates is limited from 0 ng/(mL*min) to 5 ng/(mL*min). The simulation stops if hormone concentrations leaves 0 ng/mL to 20 ng/mL.

The declared software model is a transfer function from endogenous secretion rates in ng/(mL*min) to hormone concentrations in ng/mL. Its numerator coefficients are 1; its denominator coefficients are 216000000, 1080000, 1800, 2; and its input delay is 0 s.

The accompanying existing software record uses a 12 s sample interval for 4800 s, starts the primary output at 10, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 20. Oxytocin-mediated childbirth positive feedback

### Control Problem Description

This is a childbirth feedback system in which contractions stimulate oxytocin release and oxytocin strengthens the contractions. The control input is endogenous oxytocin release, and the measured outputs are oxytocin level, contraction intensity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in oxytocin level starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.6 s sample interval; after endogenous oxytocin release changes, oxytocin level begins within one sample, with its first distinguishable change recorded 0.6 s after the input change and without a separate silent interval. The path from endogenous oxytocin release actuation to the visible oxytocin level response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in oxytocin level keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of endogenous oxytocin release changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in endogenous oxytocin release can drive a distinguishable change in the key output oxytocin level; endogenous oxytocin release and the recorded readings oxytocin level, contraction intensity share one clock, so all relevant motion can be reconstructed from these synchronized records. One endogenous oxytocin release action affects the recorded readings oxytocin level, contraction intensity; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use a two-state positive-feedback simulation with oxytocin time constant 30 s, contraction time constant 20 s, and loop product 1.2 before the birth-event switch; set the pressure-feedback gain to zero at 180 s.

The existing record reports that changing endogenous oxytocin release by 1 normalized release units/min produces a steady oxytocin level change of 1 normalized contraction units with a recorded response time of 30 s. For software simulation, endogenous oxytocin release is limited from 0 normalized release units/min to 5 normalized release units/min. The simulation stops if oxytocin level leaves 0 normalized contraction units to 10 normalized contraction units.

The declared software model is a transfer function from endogenous oxytocin release in normalized release units/min to oxytocin level in normalized contraction units. Its numerator coefficients are 30, 1; its denominator coefficients are 600, 50, -0.2; and its input delay is 0 s.

The accompanying existing software record uses a 0.6 s sample interval for 240 s, starts the primary output at 5, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 21. First-order automobile cruise dynamics

### Control Problem Description

This is a longitudinal vehicle model that combines vehicle mass, propulsion, and speed-dependent resistance. The control input is longitudinal drive force, and the measured outputs are vehicle speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in vehicle speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after longitudinal drive force changes, vehicle speed begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from longitudinal drive force actuation to the visible vehicle speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the vehicle speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in longitudinal drive force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in longitudinal drive force can drive a distinguishable change in the key output vehicle speed; longitudinal drive force and the recorded readings vehicle speed share one clock, so all relevant motion can be reconstructed from these synchronized records. One longitudinal drive force action affects the recorded readings vehicle speed; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for vehicle speed.


### Profile Measurement Response (Natural Language)

Use vehicle mass 1000 kg, viscous drag 50 N*s/m, and a 500 N force step. The force-to-speed DC gain is 0.02 (m/s)/N, the time constant is 20 s, and the predicted final speed change is 10 m/s.

The existing record reports that changing longitudinal drive force by 500 N produces a steady vehicle speed change of 10 m/s with a recorded response time of 20 s. For software simulation, longitudinal drive force is limited from -2000 N to 4000 N. The simulation stops if vehicle speed leaves 0 m/s to 50 m/s.

The declared software model is a transfer function from longitudinal drive force in N to vehicle speed in m/s. Its numerator coefficients are 0.001; its denominator coefficients are 1, 0.05; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 120 s, starts the primary output at 25, contains input amplitudes -500, -250, 250, 500, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 22. Quarter-car road-input two-mass suspension

### Control Problem Description

This is a quarter-car apparatus with body and wheel masses connected by suspension springs and dampers. The control input is prescribed road-displacement test input, and the measured outputs are body displacement, wheel displacement, and suspension travel, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in body displacement starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after prescribed road-displacement test input changes, body displacement begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from prescribed road-displacement test input actuation to the visible body displacement response contains one or two dominant storage or integration processes. When the input returns to baseline, the body displacement response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed road-displacement test input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed road-displacement test input can drive a distinguishable change in the key output body displacement; prescribed road-displacement test input and the recorded readings body displacement, wheel displacement, and suspension travel share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed road-displacement test input action affects the recorded readings body displacement, wheel displacement, and suspension travel; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for body displacement.


### Profile Measurement Response (Natural Language)

Use sprung mass 375 kg, wheel mass 20 kg, suspension stiffness 130000 N/m, tire stiffness 1000000 N/m, and damping 9800 N*s/m. Apply bounded 0.01, 0.025, and 0.05 m road steps and record body displacement, wheel displacement, and suspension travel at 1 ms.

The declared software model is a transfer function from prescribed road-displacement test input in m to body displacement in m. Its numerator coefficients are 1310000, 17423000; its denominator coefficients are 1, 516.1, 56850, 1307000, 17330000; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -0.05, -0.025, 0.025, 0.05, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 23. Rigid-satellite single-axis attitude

### Control Problem Description

This is a rigid spacecraft body equipped with a single-axis attitude actuator. The control input is thruster force or body torque, and the measured outputs are attitude angle, angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after thruster force or body torque changes, attitude angle begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from thruster force or body torque actuation to the visible attitude angle response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in thruster force or body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in thruster force or body torque can drive a distinguishable change in the key output attitude angle; thruster force or body torque and the recorded readings attitude angle, angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One thruster force or body torque action affects the recorded readings attitude angle, angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use a single-axis inertia of 1200 kg*m^2. A 12 Nm torque change gives 0.01 rad/s^2 angular acceleration; keep torque within +/-50 Nm and attitude within +/-0.2 rad.

The existing record reports that changing thruster force or body torque by 12 Nm produces an initial acceleration change of 0.01 rad/s^2 with a software motion time scale of 20 s. For software simulation, thruster force or body torque is limited from -50 Nm to 50 Nm. The simulation stops if attitude angle leaves -0.2 rad to 0.2 rad.

The declared software model is a transfer function from thruster force or body torque in Nm to attitude angle. Its numerator coefficients are 0.000833333333333; its denominator coefficients are 1, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 40 s, starts the primary output at 0, contains input amplitudes -12, -6, 6, 12, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 24. Flexible-satellite collocated/noncollocated model

### Control Problem Description

This is a satellite structure made from two rigid bodies joined by a flexible element, with torque and angle sensing available at different locations. The control input is body torque on the main inertia, and the measured outputs are both body angles and rates, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in both body angles starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after body torque on the main inertia changes, both body angles begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from body torque on the main inertia actuation to the visible both body angles response contains at least three successive storage or integration processes. When the input is removed, the both body angles response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body torque on the main inertia produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in body torque on the main inertia can drive a distinguishable change in the key output both body angles; body torque on the main inertia and the recorded readings both body angles and rates share one clock, so all relevant motion can be reconstructed from these synchronized records. One body torque on the main inertia action affects the recorded readings both body angles and rates; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use main-body inertia 800 kg*m^2, remote inertia 200 kg*m^2, torsional stiffness 80 Nm/rad, and torsional damping 2 Nm*s/rad. Apply +/-5 and +/-10 Nm torque pulses and log both angles and rates at 0.01 s.

The existing software record supplies a state-space model with state order body_angle, body_rate, instrument_angle, instrument_rate; matrix A has rows [0, 1, 0, 0]; [-0.1, -0.0025, 0.1, 0.0025]; [0, 0, 0, 1]; [0.4, 0.01, -0.4, -0.01]; matrix B has rows [0]; [0.00125]; [0]; [0]; matrix C has rows [1, 0, 0, 0]; [0, 0, 1, 0]; and matrix D has rows [0]; [0]. The input channels are body torque on the main inertia, the output channels are both body angles and rates channel 1, both body angles and rates channel 2, and the initial state is 0, 0, 0, 0.

The accompanying existing software record uses a 0.01 s sample interval for 60 s, starts the primary output at 0, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 25. Quadrotor roll/pitch/yaw allocation

### Control Problem Description

This is a quadrotor whose four thrust-producing rotors create roll, pitch, and yaw moments through differential thrust. The control inputs are four rotor thrust perturbations, and the measured outputs are roll, pitch, and yaw response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in roll starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after four rotor thrust perturbations changes, roll begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from four rotor thrust perturbations actuation to the visible roll response contains one or two dominant storage or integration processes. When the input is removed, the roll response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in four rotor thrust perturbations produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in four rotor thrust perturbations can drive a distinguishable change in the key output roll; four rotor thrust perturbations and the recorded readings roll, pitch, and yaw response share one clock, so all relevant motion can be reconstructed from these synchronized records. One four rotor thrust perturbations action affects the recorded readings roll, pitch, and yaw response; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use roll and pitch inertia 0.02 kg*m^2 and yaw inertia 0.05 kg*m^2. Use four signed rotor-torque deviations limited to +/-0.1 Nm; excite the roll, pitch, and yaw mixer columns separately.

The existing software record supplies a state-space model with state order roll, roll_rate, pitch, pitch_rate, yaw, yaw_rate; matrix A has rows [0, 1, 0, 0, 0, 0]; [0, 0, 0, 0, 0, 0]; [0, 0, 0, 1, 0, 0]; [0, 0, 0, 0, 0, 0]; [0, 0, 0, 0, 0, 1]; [0, 0, 0, 0, 0, 0]; matrix B has rows [0, 0, 0, 0]; [50, -50, -50, 50]; [0, 0, 0, 0]; [50, 50, -50, -50]; [0, 0, 0, 0]; [20, -20, 20, -20]; matrix C has rows [1, 0, 0, 0, 0, 0]; [0, 0, 1, 0, 0, 0]; [0, 0, 0, 0, 1, 0]; and matrix D has rows [0, 0, 0, 0]; [0, 0, 0, 0]; [0, 0, 0, 0]. The input channels are rotor 1 torque perturbation, rotor 2 torque perturbation, rotor 3 torque perturbation, rotor 4 torque perturbation, the output channels are roll, pitch, yaw response, and the initial state is 0, 0, 0, 0, 0, 0.

The accompanying existing software record uses a 0.002 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -0.02, -0.01, 0.01, 0.02, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 26. Pendulum nonlinear model, small-angle linearization, and nonlinear simulation

### Control Problem Description

This is a pendulum apparatus in which a concentrated mass is attached to a fixed pivot by a rigid link. The control input is pivot torque, and the measured outputs are pendulum angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after pivot torque changes, pendulum angle begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from pivot torque actuation to the visible pendulum angle response contains one or two dominant storage or integration processes. When the input returns to baseline, the pendulum angle response settles or remains bounded instead of developing self-growing motion. As the size or operating point of pivot torque changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in pivot torque can drive a distinguishable change in the key output pendulum angle; pivot torque and the recorded readings pendulum angle and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One pivot torque action affects the recorded readings pendulum angle and angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use mass 1 kg, length 1 m, gravity 9.81 m/s^2, and compare 1 Nm and 4 Nm torque steps for 10 s at 0.02 s sampling in both the sine model and its small-angle model.

The declared software model is a transfer function from pivot torque in Nm to pendulum angle and angular rate in rad. Its numerator coefficients are 1; its denominator coefficients are 1, 0, 9.81; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -4, -1, 1, 4, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 27. Hanging-crane and inverted-pendulum coupled model

### Control Problem Description

This is a rail-mounted cart coupled to either a hanging or an upright pendulum. The control input is cart force, and the measured outputs are cart position, pendulum angle, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in cart position first moves in an unfavorable or opposite direction before turning. The synchronized record has a 0.005 s sample interval; after cart force changes, cart position first begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from cart force actuation to the visible cart position first response contains at least three successive storage or integration processes. Even after the input returns to baseline, the deviation in cart position keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of cart force changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in cart force can drive a distinguishable change in the key output cart position first; cart force and the recorded readings cart position, pendulum angle share one clock, so all relevant motion can be reconstructed from these synchronized records. One cart force action affects the recorded readings cart position, pendulum angle; there are fewer independent actuators than controlled coordinates, so some coordinates move only through coupling. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use trolley mass 1 kg, pendulum mass 0.2 kg, center-of-mass length 0.5 m, inertia 0.006 kg*m^2, friction 0.1 N*s/m, force limit 20 N, travel limit 1.5 m, and an initial 0.05 rad angle.

The existing software record uses the registered nonlinear template underactuated_cartpole. Its declared parameters are cart mass kg 1, pole mass kg 0.2, com length m 0.5, pole inertia kg m2 0.006, cart friction n s m 0.1, gravity m s2 9.81, force limit n 20, cart position limit m 1.5; its initial state is position m 0, velocity m s 0, angle rad 0.05, angular rate rad s 0; its input channels are cart force; and its output channels are cart position, pendulum angle.

The accompanying existing software record uses a 0.005 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -5, -2.5, 2.5, 5, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 28. Bridged-tee RC circuit

### Control Problem Description

This is a passive bridged electrical network made from resistors and capacitors. The control input is input voltage, and the measured outputs are output and capacitor voltages, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0005 s sample interval; after input voltage changes, output begins within one sample, with its first distinguishable change recorded 0.0005 s after the input change and without a separate silent interval. The path from input voltage actuation to the visible output response contains one or two dominant storage or integration processes. When the input returns to baseline, the output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in input voltage can drive a distinguishable change in the key output output; input voltage and the recorded readings output and capacitor voltages share one clock, so all relevant motion can be reconstructed from these synchronized records. One input voltage action affects the recorded readings output and capacitor voltages; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output.


### Profile Measurement Response (Natural Language)

Set R1=R2=10 kohm and C1=C2=10 uF, giving G(s)=(0.01 s^2+0.2 s+1)/(0.01 s^2+0.3 s+1). Use +/-1 V tests to verify the unity low- and high-frequency gains and the bridged mid-band response.

The declared software model is a transfer function from input voltage in V to output and capacitor voltages in V. Its numerator coefficients are 0.01, 0.2, 1; its denominator coefficients are 0.01, 0.3, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.0005 s sample interval for 1 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 29. Current-driven RLC circuit

### Control Problem Description

This is a current-driven energy-storage circuit containing a resistor, an inductor, and two capacitors. The control input is source current, and the measured outputs are two capacitor voltages and inductor current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in two capacitor voltages starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0002 s sample interval; after source current changes, two capacitor voltages begins within one sample, with its first distinguishable change recorded 0.0002 s after the input change and without a separate silent interval. The path from source current actuation to the visible two capacitor voltages response contains one or two dominant storage or integration processes. When the input returns to baseline, the two capacitor voltages response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in source current produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in source current can drive a distinguishable change in the key output two capacitor voltages; source current and the recorded readings two capacitor voltages and inductor current share one clock, so all relevant motion can be reconstructed from these synchronized records. One source current action affects the recorded readings two capacitor voltages and inductor current; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for two capacitor voltages.


### Profile Measurement Response (Natural Language)

Use R1=R2=10 ohm, C1=C2=0.01 F, and L=0.1 H, with a 0.1 A bounded current step and all capacitor voltages plus inductor current logged.

The existing software record supplies a state-space model with state order capacitor_voltage_1, capacitor_voltage_2, inductor_current; matrix A has rows [-10, 0, -100]; [0, -10, 100]; [10, -10, 0]; matrix B has rows [100]; [0]; [0]; matrix C has rows [1, 0, 0]; [0, 1, 0]; [0, 0, 1]; and matrix D has rows [0]; [0]; [0]. The input channels are source current, the output channels are capacitor voltage 1, capacitor voltage 2, inductor current, and the initial state is 0, 0, 0.

The accompanying existing software record uses a 0.0002 s sample interval for 2 s, starts the primary output at 0, contains input amplitudes -0.1, -0.05, 0.05, 0.1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 30. Ideal op-amp weighted summer

### Control Problem Description

This is a weighted summing circuit made from an ideal operational amplifier and several input-resistor branches. The control input is input voltages, and the measured outputs are summed output voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in summed output voltage starts in its final direction rather than moving the opposite way first. The synchronized record has a 1e-05 s sample interval; after input voltages changes, summed output voltage begins within one sample, with its first distinguishable change recorded 1e-05 s after the input change and without a separate silent interval. The path from input voltages actuation to the visible summed output voltage response contains one or two dominant storage or integration processes. When the input returns to baseline, the summed output voltage response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input voltages produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in input voltages can drive a distinguishable change in the key output summed output voltage; input voltages and the recorded readings summed output voltage share one clock, so all relevant motion can be reconstructed from these synchronized records. One input voltages action affects the recorded readings summed output voltage; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for summed output voltage.


### Profile Measurement Response (Natural Language)

Choose Rf=20 kohm, R1=10 kohm, and R2=20 kohm, giving vout=-2 v1-v2; limit each input to +/-5 V and the output to +/-12 V.

The existing software record supplies a state-space model with state order amplifier_output_state; matrix A has rows [-1000]; matrix B has rows [2000, 1000]; matrix C has rows [-1]; and matrix D has rows [0, 0]. The input channels are input voltage 1, input voltage 2, the output channels are summed output voltage, and the initial state is 0.

The accompanying existing software record uses a 1e-05 s sample interval for 0.02 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 31. Ideal op-amp integrator

### Control Problem Description

This is an analog integrator made from an operational amplifier, an input resistor, and a feedback capacitor. The control input is input voltage, and the measured outputs are integrator output voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in integrator output voltage starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after input voltage changes, integrator output voltage begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from input voltage actuation to the visible integrator output voltage response contains one or two dominant storage or integration processes. When the input is removed, the integrator output voltage response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in input voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in input voltage can drive a distinguishable change in the key output integrator output voltage; input voltage and the recorded readings integrator output voltage share one clock, so all relevant motion can be reconstructed from these synchronized records. One input voltage action affects the recorded readings integrator output voltage; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for integrator output voltage.


### Profile Measurement Response (Natural Language)

Use Rin=100 kohm and C=10 uF so Rin*C=1 s. A +1 V input produces a -1 V/s output slope; stop before the output reaches +/-10 V.

The declared software model is a transfer function from input voltage in V to integrator output voltage in V. Its numerator coefficients are -1; its denominator coefficients are 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 5 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 32. Loudspeaker electromechanical model with drive circuit

### Control Problem Description

This is an electromechanical loudspeaker made from a voice coil, its drive circuit, and a compliant cone. The control input is amplifier voltage, and the measured outputs are cone displacement, coil current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in cone displacement starts in its final direction rather than moving the opposite way first. The synchronized record has a 5e-05 s sample interval; after amplifier voltage changes, cone displacement begins within one sample, with its first distinguishable change recorded 5e-05 s after the input change and without a separate silent interval. The path from amplifier voltage actuation to the visible cone displacement response contains at least three successive storage or integration processes. When the input is removed, the cone displacement response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in amplifier voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in amplifier voltage can drive a distinguishable change in the key output cone displacement; amplifier voltage and the recorded readings cone displacement, coil current share one clock, so all relevant motion can be reconstructed from these synchronized records. One amplifier voltage action affects the recorded readings cone displacement, coil current; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use magnetic flux 0.5 T, 20 turns at 2 cm diameter so Bl=0.63 N/A, together with M=0.02 kg, b=0.2 N*s/m, L=1 mH, and R=8 ohm.

The declared software model is a transfer function from amplifier voltage in V to cone displacement in m. Its numerator coefficients are 0.63; its denominator coefficients are 2e-05, 0.1602, 1.9969, 0; and its input delay is 0 s.

The accompanying existing software record uses a 5e-05 s sample interval for 2 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 33. DC-motor position and speed models

### Control Problem Description

This is a DC-motor drive made from an armature circuit, rotor inertia, and a viscous mechanical load. The control input is armature voltage, and the measured outputs are motor position, speed, armature current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0005 s sample interval; after armature voltage changes, motor position begins within one sample, with its first distinguishable change recorded 0.0005 s after the input change and without a separate silent interval. The path from armature voltage actuation to the visible motor position response contains at least three successive storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in armature voltage can drive a distinguishable change in the key output motor position; armature voltage and the recorded readings motor position, speed, armature current share one clock, so all relevant motion can be reconstructed from these synchronized records. One armature voltage action affects the recorded readings motor position, speed, armature current; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use J=0.01 kg*m^2, b=0.1 Nm*s/rad, Kt=Ke=0.01, R=1 ohm, and L=0.5 H; test +/-1 V and log current, speed, and position.

The declared software model is a transfer function from armature voltage in V to motor position in rad. Its numerator coefficients are 0.01; its denominator coefficients are 0.005, 0.06, 0.1001, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.0005 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 34. Gear-train torque multiplication and reflected inertia

### Control Problem Description

This is a rotary transmission made from a motor, gears, an elastic shaft, and a load inertia. The control input is motor torque, and the measured outputs are motor and load angle, shaft torque, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after motor torque changes, motor begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from motor torque actuation to the visible motor response contains one or two dominant storage or integration processes. When the input is removed, the motor response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in motor torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in motor torque can drive a distinguishable change in the key output motor; motor torque and the recorded readings motor and load angle, shaft torque share one clock, so all relevant motion can be reconstructed from these synchronized records. One motor torque action affects the recorded readings motor and load angle, shaft torque; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use gear ratio n=4, motor-side inertia J1=0.002 kg*m^2, load inertia J2=0.03 kg*m^2, b1=0.001 and b2=0.02 Nm*s/rad.

The declared software model is a transfer function from motor torque in Nm to motor and load angle in rad. Its numerator coefficients are 4; its denominator coefficients are 0.062, 0.036, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 35. Room heat-loss model

### Control Problem Description

This is a room thermal system whose indoor air stores heat while the enclosure loses heat to the outdoors. The control input is heating rate in the labeled control extension, and the measured outputs are room temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in room temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 60 s sample interval; after heating rate in the labeled control extension changes, room temperature begins within one sample, with its first distinguishable change recorded 60 s after the input change and without a separate silent interval. The path from heating rate in the labeled control extension actuation to the visible room temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the room temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heating rate in the labeled control extension produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in heating rate in the labeled control extension can drive a distinguishable change in the key output room temperature; heating rate in the labeled control extension and the recorded readings room temperature share one clock, so all relevant motion can be reconstructed from these synchronized records. One heating rate in the labeled control extension action affects the recorded readings room temperature; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use furnace rating 90000 Btu/h. At outdoor temperature 32 degF and indoor temperature 60 degF, heating raises temperature 2 degF in 0.1 h, while furnace-off cooling lowers it 2 degF in 40 min. These measurements give C=3913.04 Btu/degF and R=0.002385 degF/(Btu/h).

The existing record reports that changing heating rate in the labeled control extension by 1 binary-command level produces a steady room temperature change of 214.6597 degF with a recorded response time of 33600 s. For software simulation, heating rate in the labeled control extension is limited from 0 binary-command level to 1 binary-command level. The simulation stops if room temperature leaves 32 degF to 90 degF.

The declared software model is a transfer function from heating rate in the labeled control extension in binary-command units to room temperature in degF. Its numerator coefficients are 214.6597; its denominator coefficients are 33600, 1; and its input delay is 0 s.

The accompanying existing software record uses a 60 s sample interval for 120000 s, starts the primary output at 61, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 36. Two-thermal-mass controlled process

### Control Problem Description

This is a temperature process made from a heater and two thermal masses that exchange heat with one another. The control input is heater power, and the measured outputs are two body temperatures, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in two body temperatures starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.2 s sample interval; after heater power changes, two body temperatures begins within one sample, with its first distinguishable change recorded 0.2 s after the input change and without a separate silent interval. The path from heater power actuation to the visible two body temperatures response contains one or two dominant storage or integration processes. When the input returns to baseline, the two body temperatures response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heater power produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in heater power can drive a distinguishable change in the key output two body temperatures; heater power and the recorded readings two body temperatures share one clock, so all relevant motion can be reconstructed from these synchronized records. One heater power action affects the recorded readings two body temperatures; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use C1=10000 J/degC, C2=15000 J/degC, Hx=200 W/degC, H1=100 W/degC, and H2=150 W/degC; apply 250, 500, 750, and 1000 W heat steps.

The declared software model is a transfer function from heater power in W to two body temperatures in degC. Its numerator coefficients are 200; its denominator coefficients are 150000000, 8000000, 105000; and its input delay is 0 s.

The accompanying existing software record uses a 0.2 s sample interval for 1000 s, starts the primary output at 67.5, contains input amplitudes -1000, -500, 500, 1000, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 37. Heat exchanger with nonlinear valve and measurement delay

### Control Problem Description

This is a heat-exchanger process with a steam valve, two dominant thermal lags, and a temperature-measurement element. The control input is steam inlet valve area, and the measured outputs are measured outlet water temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured outlet water temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.2 s sample interval; after steam inlet valve area changes, a visible quiet interval separates the command from the first measured outlet water temperature change, which is first distinguishable 10 s after the input change. The path from steam inlet valve area actuation to the visible measured outlet water temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the measured outlet water temperature response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of steam inlet valve area reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in steam inlet valve area can drive a distinguishable change in the key output measured outlet water temperature; steam inlet valve area and the recorded readings measured outlet water temperature share one clock, so all relevant motion can be reconstructed from these synchronized records. One steam inlet valve area action affects the recorded readings measured outlet water temperature; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use a two-lag model with 30 s and 60 s thermal time constants, DC gain 0.5 degC/%, and 10 s downstream measurement delay. Test 2.5%, 5%, 7.5%, and 10% valve changes.

The declared software model is a transfer function from steam inlet valve area in % to measured outlet water temperature in degC. Its numerator coefficients are 0.5; its denominator coefficients are 1800, 90, 1; and its input delay is 10 s.

The accompanying existing software record uses a 0.2 s sample interval for 800 s, starts the primary output at 60, contains input amplitudes -10, -5, 5, 10, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 38. Water-tank continuity, square-root outflow, and operating-point linearization

### Control Problem Description

This is a storage tank that receives inlet flow and drains through an outlet whose flow follows the square root of liquid level. The control input is inlet mass flow, and the measured outputs are tank level and outlet flow, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tank level starts in its final direction rather than moving the opposite way first. The synchronized record has a 1 s sample interval; after inlet mass flow changes, tank level begins within one sample, with its first distinguishable change recorded 1 s after the input change and without a separate silent interval. The path from inlet mass flow actuation to the visible tank level response contains one or two dominant storage or integration processes. When the input returns to baseline, the tank level response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of inlet mass flow reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in inlet mass flow can drive a distinguishable change in the key output tank level; inlet mass flow and the recorded readings tank level and outlet flow share one clock, so all relevant motion can be reconstructed from these synchronized records. One inlet mass flow action affects the recorded readings tank level and outlet flow; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use water density 1000 kg/m^3, tank area 0.05 m^2, nominal height 0.15 m, and nominal outflow 200 g/min; linearize the square-root outlet law and test +/-25 and +/-50 g/min pump-flow changes.

The existing record reports that changing inlet mass flow by 50 g/min produces a steady tank level and outlet flow change of 0.1 m with a recorded response time of 120 s. For software simulation, inlet mass flow is limited from 0 g/min to 500 g/min. The simulation stops if tank level and outlet flow leaves 0 m to 0.5 m.

The declared software model is a transfer function from inlet mass flow in g/min to tank level and outlet flow in m. Its numerator coefficients are 0.002; its denominator coefficients are 120, 1; and its input delay is 0 s.

The accompanying existing software record uses a 1 s sample interval for 900 s, starts the primary output at 0.25, contains input amplitudes -50, -25, 25, 50, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 39. Pressure-driven hydraulic piston

### Control Problem Description

This is a hydraulic actuator in which chamber pressure drives a piston and its attached mechanical load. The control input is chamber pressure difference, and the measured outputs are piston position and velocity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in piston position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after chamber pressure difference changes, piston position begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from chamber pressure difference actuation to the visible piston position response contains one or two dominant storage or integration processes. When the input is removed, the piston position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in chamber pressure difference produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in chamber pressure difference can drive a distinguishable change in the key output piston position; chamber pressure difference and the recorded readings piston position and velocity share one clock, so all relevant motion can be reconstructed from these synchronized records. One chamber pressure difference action affects the recorded readings piston position and velocity; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use piston mass 50 kg and area 0.01 m^2. A 100 kPa chamber-pressure change gives 1000 N and 20 m/s^2 initial acceleration; limit displacement to +/-0.5 m.

The existing record reports that changing chamber pressure difference by 100 kPa produces an initial acceleration change of 20 m/s^2 with a software motion time scale of 2 s. For software simulation, chamber pressure difference is limited from 0 kPa to 500 kPa. The simulation stops if piston position and velocity leaves -0.5 m/s to 0.5 m/s.

The declared software model is a transfer function from chamber pressure difference in kPa to piston position and velocity. Its numerator coefficients are 0.2; its denominator coefficients are 1, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 3 s, starts the primary output at 0, contains input amplitudes -100, -50, 50, 100, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 40. Hydraulic control-surface actuator and load-dependent integrator model

### Control Problem Description

This is a hydraulic position actuator made from a servo valve, cylinder, and externally loaded control surface. The control input is servo valve displacement, and the measured outputs are surface angle and load force, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in surface angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after servo valve displacement changes, surface angle begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from servo valve displacement actuation to the visible surface angle response contains one or two dominant storage or integration processes. When the input is removed, the surface angle response retains an offset or keeps drifting rather than returning through its own restoring action. As the size or operating point of servo valve displacement changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in servo valve displacement can drive a distinguishable change in the key output surface angle; servo valve displacement and the recorded readings surface angle and load force share one clock, so all relevant motion can be reconstructed from these synchronized records. One servo valve displacement action affects the recorded readings surface angle and load force; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use a no-load local valve-to-angle-rate gain of 0.8 rad/(s*mm), valve travel +/-5 mm, and angle limit +/-0.5 rad. Repeat with load reducing the gain to 0.72 and 0.64 rad/(s*mm).

The declared software model is a transfer function from servo valve displacement in mm to surface angle and load force in rad. Its numerator coefficients are 0.8; its denominator coefficients are 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 3 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 41. Test linearity and time invariance by superposition and shift

### Control Problem Description

This is a repeatable input-output test bench built around one dynamic plant, with timing preserved so shifted and combined excitations can be compared. The control input is prescribed test signal, and the measured outputs are system output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in system output response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after prescribed test signal changes, system output response begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from prescribed test signal actuation to the visible system output response response contains one or two dominant storage or integration processes. When the input returns to baseline, the system output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed test signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed test signal can drive a distinguishable change in the key output system output response; prescribed test signal and the recorded readings system output response share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed test signal action affects the recorded readings system output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for system output response.


### Profile Measurement Response (Natural Language)

Set k=2 s^-1. Use u1(t)=1, u2(t)=sin(t), coefficients 1.5 and -0.5, and a 1 s shift; sample at 0.01 s for 8 s and compare superposed and shifted responses.

The declared software model is a transfer function from prescribed test signal in unit/s to system output response in unit. Its numerator coefficients are 1; its denominator coefficients are 1, 2; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 42. Derive a first-order impulse response and arbitrary-input convolution

### Control Problem Description

This is a stable first-order dynamic element connected to an input generator and a continuous output recorder. The control input is input signal, and the measured outputs are output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after input signal changes, output response begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from input signal actuation to the visible output response response contains one or two dominant storage or integration processes. When the input returns to baseline, the output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in input signal can drive a distinguishable change in the key output output response; input signal and the recorded readings output response share one clock, so all relevant motion can be reconstructed from these synchronized records. One input signal action affects the recorded readings output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output response.


### Profile Measurement Response (Natural Language)

Use k=0.5 s^-1. Simulate a unit impulse and a unit step at 0.01 s resolution for 16 s, then compare direct integration with convolution by exp(-0.5 t).

The declared software model is a transfer function from input signal in normalized impulse units to output response in unit. Its numerator coefficients are 1; its denominator coefficients are 1, 0.5; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 16 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 43. Convert an ODE to a transfer function under zero initial conditions

### Control Problem Description

This is a dynamic plant governed by a linear differential equation, with an external forcing port and a measured response channel. The control input is prescribed forcing signal, and the measured outputs are system output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in system output response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after prescribed forcing signal changes, system output response begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from prescribed forcing signal actuation to the visible system output response response contains one or two dominant storage or integration processes. When the input returns to baseline, the system output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed forcing signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed forcing signal can drive a distinguishable change in the key output system output response; prescribed forcing signal and the recorded readings system output response share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed forcing signal action affects the recorded readings system output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for system output response.


### Profile Measurement Response (Natural Language)

Use y_ddot+5 y_dot+4 y=2 u with zero initial conditions. Apply +/-0.5 and +/-1 N steps, sample at 0.01 s for 8 s, and verify G(s)=2/(s^2+5s+4).

The declared software model is a transfer function from prescribed forcing signal in N to system output response in m. Its numerator coefficients are 2; its denominator coefficients are 1, 5, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 44. Derive the RC low-pass transfer function and impulse response

### Control Problem Description

This is a resistor-capacitor low-pass circuit whose capacitor stores energy while the resistor dissipates it. The control input is input voltage, and the measured outputs are capacitor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in capacitor voltage starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after input voltage changes, capacitor voltage begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from input voltage actuation to the visible capacitor voltage response contains one or two dominant storage or integration processes. When the input returns to baseline, the capacitor voltage response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in input voltage can drive a distinguishable change in the key output capacitor voltage; input voltage and the recorded readings capacitor voltage share one clock, so all relevant motion can be reconstructed from these synchronized records. One input voltage action affects the recorded readings capacitor voltage; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for capacitor voltage.


### Profile Measurement Response (Natural Language)

Use R=10 kohm and C=100 uF, giving RC=1 s. Apply 0.25, 0.5, 0.75, and 1 V steps at 0.01 s sampling for 8 s.

The declared software model is a transfer function from input voltage in V to capacitor voltage in V. Its numerator coefficients are 1; its denominator coefficients are 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 45. Compute magnitude and phase of first-order sinusoidal response

### Control Problem Description

This is a stable first-order lag element driven by a sinusoidal source and observed after its transient has decayed. The control input is sinusoidal input, and the measured outputs are sinusoidal output amplitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sinusoidal output amplitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after sinusoidal input changes, sinusoidal output amplitude begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from sinusoidal input actuation to the visible sinusoidal output amplitude response contains one or two dominant storage or integration processes. When the input returns to baseline, the sinusoidal output amplitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sinusoidal input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sinusoidal input can drive a distinguishable change in the key output sinusoidal output amplitude; sinusoidal input and the recorded readings sinusoidal output amplitude and phase share one clock, so all relevant motion can be reconstructed from these synchronized records. One sinusoidal input action affects the recorded readings sinusoidal output amplitude and phase; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sinusoidal output amplitude.


### Profile Measurement Response (Natural Language)

Set k=1 s^-1, sinusoidal amplitude 1 V, and omega=10 rad/s. Sample at 0.002 s for 12 s and estimate steady amplitude and phase after the exponential transient.

The declared software model is a transfer function from sinusoidal input in V to sinusoidal output amplitude and phase in V. Its numerator coefficients are 1; its denominator coefficients are 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 46. Transform canonical step, ramp, impulse, and sinusoidal inputs

### Control Problem Description

This is a signal-analysis test bench that applies canonical step, ramp, impulse, and sinusoidal waveforms to a dynamic representation. The control input is canonical test signal, and the measured outputs are transformed system response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in transformed system response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after canonical test signal changes, transformed system response begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from canonical test signal actuation to the visible transformed system response response contains one or two dominant storage or integration processes. When the input returns to baseline, the transformed system response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in canonical test signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in canonical test signal can drive a distinguishable change in the key output transformed system response; canonical test signal and the recorded readings transformed system response share one clock, so all relevant motion can be reconstructed from these synchronized records. One canonical test signal action affects the recorded readings transformed system response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for transformed system response.


### Profile Measurement Response (Natural Language)

Use G(s)=1/(s+1), step amplitude 2, ramp slope 0.5, unit impulse area 1, and sinusoid omega=3 rad/s. Sample at 0.005 s for 12 s.

The declared software model is a transfer function from canonical test signal in canonical_input to transformed system response in unit. Its numerator coefficients are 1; its denominator coefficients are 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 47. Recover a time response by partial-fraction expansion

### Control Problem Description

This is a rational dynamic model whose internal modes are reconstructed from a transformed input and a recorded time response. The control input is prescribed transformed input, and the measured outputs are time-domain output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in time-domain output response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after prescribed transformed input changes, time-domain output response begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from prescribed transformed input actuation to the visible time-domain output response response contains one or two dominant storage or integration processes. When the input returns to baseline, the time-domain output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed transformed input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed transformed input can drive a distinguishable change in the key output time-domain output response; prescribed transformed input and the recorded readings time-domain output response share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed transformed input action affects the recorded readings time-domain output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for time-domain output response.


### Profile Measurement Response (Natural Language)

Use Y(s)=(s+2)(s+4)/[s(s+1)(s+3)]. Simulate a unit impulse at 0.005 s sampling for 12 s and compare residues 8/3, -3/2, and -1/6.

The declared software model is a transfer function from prescribed transformed input in normalized impulse units to time-domain output response in unit. Its numerator coefficients are 1, 6, 8; its denominator coefficients are 1, 4, 3, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 48. Apply the Final Value Theorem and reject invalid unstable use

### Control Problem Description

This is a dynamic plant whose long-time output is checked against the locations of every pole that can influence the response. The control input is test input, and the measured outputs are steady-state output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in steady-state output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after test input changes, steady-state output begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from test input actuation to the visible steady-state output response contains one or two dominant storage or integration processes. When the input returns to baseline, the steady-state output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in test input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in test input can drive a distinguishable change in the key output steady-state output; test input and the recorded readings steady-state output share one clock, so all relevant motion can be reconstructed from these synchronized records. One test input action affects the recorded readings steady-state output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for steady-state output.


### Profile Measurement Response (Natural Language)

Evaluate Y1=3(s+2)/[s(s^2+2s+10)] and Y2=3/[s(s-2)] side by side, using 0.002 s sampling for 8 s and a stop threshold of absolute output 100.

The declared software model is a transfer function from test input in normalized step units to steady-state output in unit. Its numerator coefficients are 3, 6; its denominator coefficients are 1, 2, 10, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 49. Compute stable-system DC gain from the transfer function

### Control Problem Description

This is a self-regulating stable plant with a finite static gain between a constant input and its settled output. The control input is unit-step input, and the measured outputs are steady output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in steady output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after unit-step input changes, steady output begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from unit-step input actuation to the visible steady output response contains one or two dominant storage or integration processes. When the input returns to baseline, the steady output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in unit-step input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in unit-step input can drive a distinguishable change in the key output steady output; unit-step input and the recorded readings steady output share one clock, so all relevant motion can be reconstructed from these synchronized records. One unit-step input action affects the recorded readings steady output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for steady output.


### Profile Measurement Response (Natural Language)

Use G(s)=3(s+2)/(s^2+2s+10). Apply step amplitudes 0.25, 0.5, 0.75, and 1, sample at 0.005 s for 12 s, and verify the 0.6 DC gain.

The declared software model is a transfer function from unit-step input in normalized step units to steady output in unit. Its numerator coefficients are 3, 6; its denominator coefficients are 1, 2, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 50. Solve homogeneous and forced ODEs with initial conditions

### Control Problem Description

This is a dynamic state model that can move from stored initial energy as well as from a separately applied external forcing signal. The control input is forcing input and prescribed initial-state release, and the measured outputs are state and output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after forcing input and prescribed initial-state release changes, state begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from forcing input and prescribed initial-state release actuation to the visible state response contains one or two dominant storage or integration processes. When the input returns to baseline, the state response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in forcing input and prescribed initial-state release produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in forcing input and prescribed initial-state release can drive a distinguishable change in the key output state; forcing input and prescribed initial-state release and the recorded readings state and output response share one clock, so all relevant motion can be reconstructed from these synchronized records. One forcing input and prescribed initial-state release action affects the recorded readings state and output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state.


### Profile Measurement Response (Natural Language)

Use y_ddot+5 y_dot+4 y=u. Run initial states (y0,ydot0)=(1,0) and (0,1), then the zero-initial input u=2 exp(-2t), at 0.005 s for 10 s.

The declared software model is a transfer function from forcing input and prescribed initial-state release in N to state and output response in m. Its numerator coefficients are 1; its denominator coefficients are 1, 5, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 51. Analyze automobile position dynamics from the cruise model

### Control Problem Description

This is a longitudinal vehicle system whose speed is determined by propulsion, vehicle mass, and road resistance. The control input is drive force, and the measured outputs are vehicle position and speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in vehicle position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after drive force changes, vehicle position begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from drive force actuation to the visible vehicle position response contains one or two dominant storage or integration processes. When the input is removed, the vehicle position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in drive force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in drive force can drive a distinguishable change in the key output vehicle position; drive force and the recorded readings vehicle position and speed share one clock, so all relevant motion can be reconstructed from these synchronized records. One drive force action affects the recorded readings vehicle position and speed; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for vehicle position.


### Profile Measurement Response (Natural Language)

Use m=1000 kg, b=50 N*s/m, and a 500 N force step. Sample speed and position at 0.05 s for 120 s; position uses Gx=0.001/[s(s+0.05)].

The declared software model is a transfer function from drive force in N to vehicle position and speed in m. Its numerator coefficients are 0.001; its denominator coefficients are 1, 0.05, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 120 s, starts the primary output at 0, contains input amplitudes -500, -250, 250, 500, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 52. Analyze DC-motor position and speed poles with numerical parameters

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage, and the measured outputs are motor speed and position, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after armature voltage changes, motor speed begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from armature voltage actuation to the visible motor speed response contains one or two dominant storage or integration processes. When the input is removed, the motor speed response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in armature voltage can drive a distinguishable change in the key output motor speed; armature voltage and the recorded readings motor speed and position share one clock, so all relevant motion can be reconstructed from these synchronized records. One armature voltage action affects the recorded readings motor speed and position; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.


### Profile Measurement Response (Natural Language)

Use J=0.01 kg*m^2, b=0.001 Nm*s/rad, Kt=Ke=1, Ra=10 ohm, and La=1 H. Test +/-1 V and record current, speed, and angle at 0.001 s for 5 s.

The declared software model is a transfer function from armature voltage in V to motor speed and position in rad. Its numerator coefficients are 100; its denominator coefficients are 1, 10.1, 101, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 5 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 53. Predict rigid-satellite response to a finite thrust pulse

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is finite thruster-force pulse, and the measured outputs are attitude angle and rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after finite thruster-force pulse changes, attitude angle begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from finite thruster-force pulse actuation to the visible attitude angle response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in finite thruster-force pulse produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in finite thruster-force pulse can drive a distinguishable change in the key output attitude angle; finite thruster-force pulse and the recorded readings attitude angle and rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One finite thruster-force pulse action affects the recorded readings attitude angle and rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude angle.


### Profile Measurement Response (Natural Language)

Use lever arm d=1 m and inertia I=5000 kg*m^2. Apply a 25 N pulse from 5.0 to 5.1 s and sample at 0.01 s through 10 s.

The existing record reports that changing finite thruster-force pulse by 25 N produces an initial acceleration change of 0.005 rad/s^2 with a software motion time scale of 10 s. For software simulation, finite thruster-force pulse is limited from -50 N to 50 N. The simulation stops if attitude angle and rate leaves -0.02 rad to 0.02 rad.

The declared software model is a transfer function from finite thruster-force pulse in N to attitude angle and rate in rad. Its numerator coefficients are 0.0002; its denominator coefficients are 1, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -25, -12.5, 12.5, 25, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 54. Reduce nested control block diagrams to one transfer function

### Control Problem Description

This is an interconnected feedback system containing reference, controller, plant, sensor, and nested inner-loop signal paths. The control input is reference input, and the measured outputs are closed-loop output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after reference input changes, closed-loop output begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from reference input actuation to the visible closed-loop output response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in reference input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in reference input can drive a distinguishable change in the key output closed-loop output; reference input and the recorded readings closed-loop output share one clock, so all relevant motion can be reconstructed from these synchronized records. One reference input action affects the recorded readings closed-loop output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.


### Profile Measurement Response (Natural Language)

Use parallel controller branches 2 and 4/s, plant 1/s, and unity negative feedback. Apply +/-0.5 and +/-1 reference steps at 0.005 s for 10 s.

The declared software model is a transfer function from reference input in normalized reference units to closed-loop output in normalized output units. Its numerator coefficients are 2, 4; its denominator coefficients are 1, 2, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 55. Derive a closed-loop transfer function with Mason's signal-flow rule

### Control Problem Description

This is a directed signal-flow network whose branches carry gains among source, internal, feedback, and output nodes. The control input is prescribed source-node signal, and the measured outputs are signal-flow output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in signal-flow output response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after prescribed source-node signal changes, signal-flow output response begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from prescribed source-node signal actuation to the visible signal-flow output response response contains one or two dominant storage or integration processes. When the input returns to baseline, the signal-flow output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed source-node signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed source-node signal can drive a distinguishable change in the key output signal-flow output response; prescribed source-node signal and the recorded readings signal-flow output response share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed source-node signal action affects the recorded readings signal-flow output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for signal-flow output response.


### Profile Measurement Response (Natural Language)

Use one forward path P=6 and one signed touching loop L=0.2, so the Mason gain is 6/(1-0.2)=7.5. Repeat after setting the loop to -0.2 and zero.

The declared software model is a transfer function from prescribed source-node signal in path_input to signal-flow output response in path_output. Its numerator coefficients are 6; its denominator coefficients are 1, -0.2; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 56. Infer transient form and decay rate from pole locations

### Control Problem Description

This is a modal dynamic plant whose free and pulse-driven motion is set by the location of its poles. The control input is bounded impulse test, and the measured outputs are transient output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in transient output response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after bounded impulse test changes, transient output response begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from bounded impulse test actuation to the visible transient output response response contains one or two dominant storage or integration processes. When the input returns to baseline, the transient output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded impulse test produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded impulse test can drive a distinguishable change in the key output transient output response; bounded impulse test and the recorded readings transient output response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded impulse test action affects the recorded readings transient output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for transient output response.


### Profile Measurement Response (Natural Language)

Use H(s)=(2s+1)/(s^2+3s+2). Apply unit signed impulses, sample at 0.005 s for 10 s, and fit the -1 and -2 modes with residues -1 and 3.

The declared software model is a transfer function from bounded impulse test in normalized impulse units to transient output response in unit. Its numerator coefficients are 2, 1; its denominator coefficients are 1, 3, 2; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 57. Map second-order rise time, overshoot, settling time, and peak time to pole regions

### Control Problem Description

This is a damped second-order plant whose dominant pole pair determines rise, peak, overshoot, and settling behavior. The control input is bounded command step, and the measured outputs are step response and its transient features, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in step response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.00666666 s sample interval; after bounded command step changes, step response begins within one sample, with its first distinguishable change recorded 0.00666666 s after the input change and without a separate silent interval. The path from bounded command step actuation to the visible step response response contains one or two dominant storage or integration processes. When the input returns to baseline, the step response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded command step produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded command step can drive a distinguishable change in the key output step response; bounded command step and the recorded readings step response and its transient features share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded command step action affects the recorded readings step response and its transient features; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for step response.


### Profile Measurement Response (Natural Language)

Use omega_n=3 rad/s and zeta=0.6, with a unit-DC-gain model 9/(s^2+3.6s+9). Sample at 0.002 s for 8 s and measure rise, peak, and 1% settling times.

The declared software model is a transfer function from bounded command step in normalized reference units to step response and its transient features in normalized output units. Its numerator coefficients are 9; its denominator coefficients are 1, 3.6, 9; and its input delay is 0 s.

The accompanying existing software record uses a 0.00666666 s sample interval for 2.666664 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 58. Explain and quantify Boeing 747 nonminimum-phase altitude response

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is impulsive elevator deflection, and the measured outputs are aircraft altitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in aircraft altitude first moves in an unfavorable or opposite direction before turning. The synchronized record has a 0.01 s sample interval; after impulsive elevator deflection changes, aircraft altitude first begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from impulsive elevator deflection actuation to the visible aircraft altitude first response contains one or two dominant storage or integration processes. When the input is removed, the aircraft altitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in impulsive elevator deflection produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in impulsive elevator deflection can drive a distinguishable change in the key output aircraft altitude first; impulsive elevator deflection and the recorded readings aircraft altitude share one clock, so all relevant motion can be reconstructed from these synchronized records. One impulsive elevator deflection action affects the recorded readings aircraft altitude; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use h/delta_e=30(s-6)/[s(s^2+4s+13)] with a -1 deg impulsive elevator input. Sample at 0.002 s for 12 s and retain the initial altitude dip and final offset.

The declared software model is a transfer function from impulsive elevator deflection in deg to aircraft altitude in ft. Its numerator coefficients are -30, 180; its denominator coefficients are 1, 4, 13, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 4 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 59. Test BIBO stability of a current-driven capacitor

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is bounded source current, and the measured outputs are capacitor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in capacitor voltage starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after bounded source current changes, capacitor voltage begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from bounded source current actuation to the visible capacitor voltage response contains one or two dominant storage or integration processes. When the input is removed, the capacitor voltage response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded source current produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded source current can drive a distinguishable change in the key output capacitor voltage; bounded source current and the recorded readings capacitor voltage share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded source current action affects the recorded readings capacitor voltage; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for capacitor voltage.


### Profile Measurement Response (Natural Language)

Use C=0.01 F. Apply constant currents +/-0.1 A with a 50 V stop bound; sample at 0.01 s and verify the voltage ramp and BIBO counterexample.

The declared software model is a transfer function from bounded source current in A to capacitor voltage in V. Its numerator coefficients are 100; its denominator coefficients are 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 60. Determine proportional and PI gain stability regions with the Routh criterion

### Control Problem Description

This is a dynamic feedback system in which controller settings are swept while closed-loop stability is observed. The control input is bounded controller command during proportional and integral setting sweeps, and the measured outputs are regulated output response across the tested settings, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output response across the tested settings starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after bounded controller command during proportional and integral setting sweeps changes, regulated output response across the tested settings begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from bounded controller command during proportional and integral setting sweeps actuation to the visible regulated output response across the tested settings response contains at least three successive storage or integration processes. Even after the input returns to baseline, the deviation in regulated output response across the tested settings keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in bounded controller command during proportional and integral setting sweeps produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded controller command during proportional and integral setting sweeps can drive a distinguishable change in the key output regulated output response across the tested settings; bounded controller command during proportional and integral setting sweeps and the recorded readings regulated output response across the tested settings share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded controller command during proportional and integral setting sweeps action affects the recorded readings regulated output response across the tested settings; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output response across the tested settings.


### Profile Measurement Response (Natural Language)

For the proportional case use K=13, then compare K=7.5 and 25. For the PI case use (K,Ki)=(2,6), compare the boundary Ki=6+3K, and sample at 0.005 s for 20 s.

The declared software model is a transfer function from bounded controller command during proportional and integral setting sweeps in normalized reference units to regulated output response across the tested settings in normalized output units. Its numerator coefficients are 13, 13; its denominator coefficients are 1, 5, 7, 13; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 61. Derive closed-loop reference, disturbance, sensor-noise, control, and error maps using sensitivity and complementary sensitivity

### Control Problem Description

This is a standard feedback loop with separate reference, plant-disturbance, sensor-noise, controller, and measured-output ports. The control input is reference command with prescribed plant disturbance and sensor noise, and the measured outputs are regulated output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after reference command with prescribed plant disturbance and sensor noise changes, regulated output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from reference command with prescribed plant disturbance and sensor noise actuation to the visible regulated output response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in reference command with prescribed plant disturbance and sensor noise produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in reference command with prescribed plant disturbance and sensor noise can drive a distinguishable change in the key output regulated output; reference command with prescribed plant disturbance and sensor noise and the recorded readings regulated output, tracking error, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One reference command with prescribed plant disturbance and sensor noise action affects the recorded readings regulated output, tracking error, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.


### Profile Measurement Response (Natural Language)

Use G=1/(s+1), D=9; excite reference, plant disturbance, and sensor noise separately at +/-0.5 and +/-1, sampled at 0.01 s for 8 s.

The declared software model is a transfer function from reference command with prescribed plant disturbance and sensor noise in normalized input units to regulated output in normalized output units. Its numerator coefficients are 9; its denominator coefficients are 1, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 62. Stabilize an unstable inverted-pendulum model by feedback characteristic-equation design

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is bounded dynamic-compensator command, and the measured outputs are pendulum angle and compensator output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after bounded dynamic-compensator command changes, pendulum angle begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from bounded dynamic-compensator command actuation to the visible pendulum angle response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in pendulum angle keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in bounded dynamic-compensator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded dynamic-compensator command can drive a distinguishable change in the key output pendulum angle; bounded dynamic-compensator command and the recorded readings pendulum angle and compensator output share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded dynamic-compensator command action affects the recorded readings pendulum angle and compensator output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pendulum angle.


### Profile Measurement Response (Natural Language)

For G=1/(s^2-1), use zeta=0.7, wn=2 rad/s, gamma=1, delta=3.8, K=7.8; sample +/-0.25 steps at 0.005 s for 8 s.

The declared software model is a transfer function from bounded dynamic-compensator command in normalized input units to pendulum angle and compensator output in normalized output units. Its numerator coefficients are 7.8, 7.8; its denominator coefficients are 1, 3.8, 6.8, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -0.25, -0.125, 0.125, 0.25, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 63. Quantify feedback reduction of plant-gain sensitivity

### Control Problem Description

This is a feedback-regulated plant whose physical gain can vary while the controller and sensor close the same loop. The control input is bounded controller command, and the measured outputs are regulated output and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded controller command changes, regulated output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded controller command actuation to the visible regulated output response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded controller command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded controller command can drive a distinguishable change in the key output regulated output; bounded controller command and the recorded readings regulated output and tracking error share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded controller command action affects the recorded readings regulated output and tracking error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.


### Profile Measurement Response (Natural Language)

Use P=1, C=99 at the test frequency and repeat with P times 0.9 and 1.1; use plant 1/(s+1) for the bounded time response.

The declared software model is a transfer function from bounded controller command in normalized input units to regulated output and tracking error in normalized output units. Its numerator coefficients are 99; its denominator coefficients are 1, 100; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 2 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 64. Resolve low-frequency plant-disturbance rejection versus high-frequency sensor-noise attenuation

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is plant disturbance and sensor-noise test inputs, and the measured outputs are regulated output, error, and sensor-noise response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0002 s sample interval; after plant disturbance and sensor-noise test inputs changes, regulated output begins within one sample, with its first distinguishable change recorded 0.0002 s after the input change and without a separate silent interval. The path from plant disturbance and sensor-noise test inputs actuation to the visible regulated output response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in plant disturbance and sensor-noise test inputs produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in plant disturbance and sensor-noise test inputs can drive a distinguishable change in the key output regulated output; plant disturbance and sensor-noise test inputs and the recorded readings regulated output, error, and sensor-noise response share one clock, so all relevant motion can be reconstructed from these synchronized records. One plant disturbance and sensor-noise test inputs action affects the recorded readings regulated output, error, and sensor-noise response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.


### Profile Measurement Response (Natural Language)

Use L=100/(s+1); test a low-frequency plant disturbance and sensor-noise sinusoids at 1, 10, 100, 1000 rad/s.

The declared software model is a transfer function from plant disturbance and sensor-noise test inputs in normalized input units to regulated output in normalized output units. Its numerator coefficients are 100; its denominator coefficients are 1, 101; and its input delay is 0 s.

The accompanying existing software record uses a 0.0002 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 65. Compute Type 0 speed-control error with proportional feedback

### Control Problem Description

This is a speed-control servo made from a self-regulating plant, proportional controller, and speed sensor. The control input is proportional control command, and the measured outputs are speed and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after proportional control command changes, speed begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from proportional control command actuation to the visible speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional control command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in proportional control command can drive a distinguishable change in the key output speed; proportional control command and the recorded readings speed and tracking error share one clock, so all relevant motion can be reconstructed from these synchronized records. One proportional control command action affects the recorded readings speed and tracking error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for speed.


### Profile Measurement Response (Natural Language)

Use A=2, tau=5 s, kP=4; apply +/-0.5 and +/-1 speed steps at 0.02 s for 20 s.

The declared software model is a transfer function from proportional control command in normalized input units to speed and tracking error in normalized output units. Its numerator coefficients are 8; its denominator coefficients are 5, 9; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 66. Raise speed control to Type 1 with integral action

### Control Problem Description

This is a speed-control servo whose proportional-integral controller adds an error-accumulating state to the plant loop. The control input is PI control command, and the measured outputs are speed and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after PI control command changes, speed begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from PI control command actuation to the visible speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in PI control command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in PI control command can drive a distinguishable change in the key output speed; PI control command and the recorded readings speed and tracking error share one clock, so all relevant motion can be reconstructed from these synchronized records. One PI control command action affects the recorded readings speed and tracking error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for speed.


### Profile Measurement Response (Natural Language)

Use A=2, tau=5 s, kP=2, kI=0.5; run unit step and ramp references at 0.02 s for 30 s.

The declared software model is a transfer function from PI control command in normalized input units to speed and tracking error in normalized output units. Its numerator coefficients are 4, 1; its denominator coefficients are 5, 5, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 67. Evaluate system type and velocity constant with tachometer feedback

### Control Problem Description

This is a DC-motor position drive equipped with armature actuation and tachometer speed feedback. The control input is armature voltage under tachometer feedback, and the measured outputs are motor position, speed, and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after armature voltage under tachometer feedback changes, motor position begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from armature voltage under tachometer feedback actuation to the visible motor position response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage under tachometer feedback produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in armature voltage under tachometer feedback can drive a distinguishable change in the key output motor position; armature voltage under tachometer feedback and the recorded readings motor position, speed, and tracking error share one clock, so all relevant motion can be reconstructed from these synchronized records. One armature voltage under tachometer feedback action affects the recorded readings motor position, speed, and tracking error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.


### Profile Measurement Response (Natural Language)

Use tau=1 s, kP=4, kt=0.25 s; apply step and ramp references at 0.01 s for 15 s.

The declared software model is a transfer function from armature voltage under tachometer feedback in normalized input units to motor position in normalized output units. Its numerator coefficients are 4; its denominator coefficients are 1, 2, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 68. Compare P and PI rejection of DC-motor torque disturbances

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage with prescribed load-torque disturbance, and the measured outputs are motor position, speed, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after armature voltage with prescribed load-torque disturbance changes, motor position begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from armature voltage with prescribed load-torque disturbance actuation to the visible motor position response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage with prescribed load-torque disturbance produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in armature voltage with prescribed load-torque disturbance can drive a distinguishable change in the key output motor position; armature voltage with prescribed load-torque disturbance and the recorded readings motor position, speed, and disturbance response share one clock, so all relevant motion can be reconstructed from these synchronized records. One armature voltage with prescribed load-torque disturbance action affects the recorded readings motor position, speed, and disturbance response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.


### Profile Measurement Response (Natural Language)

Use A=B=tau=1; compare P kP=4 with PI kP=4, kI=2 under a unit torque disturbance.

The declared software model is a transfer function from armature voltage with prescribed load-torque disturbance in normalized input units to motor position in normalized output units. Its numerator coefficients are 4; its denominator coefficients are 1, 1, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 69. Tune proportional control while exposing speed/offset/damping tradeoffs

### Control Problem Description

This is a self-regulating process operated by a proportional actuator command and observed through its output sensor. The control input is proportional actuator command, and the measured outputs are regulated output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after proportional actuator command changes, regulated output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from proportional actuator command actuation to the visible regulated output response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional actuator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in proportional actuator command can drive a distinguishable change in the key output regulated output; proportional actuator command and the recorded readings regulated output, tracking error, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One proportional actuator command action affects the recorded readings regulated output, tracking error, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.


### Profile Measurement Response (Natural Language)

Use A=1, a1=1.4, a2=1; compare kP=1.5 and 6 for a unit step at 0.01 s for 15 s.

The declared software model is a transfer function from proportional actuator command in normalized input units to regulated output in normalized output units. Its numerator coefficients are 1.5; its denominator coefficients are 1, 1.4, 2.5; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 70. Use integral control for robust zero step error and constant-disturbance rejection

### Control Problem Description

This is a process-control loop in which an integral controller accumulates tracking error while constant disturbances enter the plant. The control input is integral control command and test disturbance, and the measured outputs are tracking error, plant output, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tracking error starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after integral control command and test disturbance changes, tracking error begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from integral control command and test disturbance actuation to the visible tracking error response contains one or two dominant storage or integration processes. When the input returns to baseline, the tracking error response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in integral control command and test disturbance produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in integral control command and test disturbance can drive a distinguishable change in the key output tracking error; integral control command and test disturbance and the recorded readings tracking error, plant output, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One integral control command and test disturbance action affects the recorded readings tracking error, plant output, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for tracking error.


### Profile Measurement Response (Natural Language)

Use G=1/(s^2+1.4s+1), kI=0.5; apply reference and plant-disturbance steps separately with anti-windup.

The declared software model is a transfer function from integral control command and test disturbance in normalized input units to tracking error in normalized output units. Its numerator coefficients are 0.5; its denominator coefficients are 1, 1.4, 1, 0.5; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 71. Use derivative/rate feedback to add damping without derivative kick

### Control Problem Description

This is a motion-control plant equipped with both output sensing and rate feedback so damping can be changed independently of the reference step. The control input is proportional and rate command, and the measured outputs are output and output rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after proportional and rate command changes, output begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from proportional and rate command actuation to the visible output response contains one or two dominant storage or integration processes. When the input returns to baseline, the output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional and rate command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in proportional and rate command can drive a distinguishable change in the key output output; proportional and rate command and the recorded readings output and output rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One proportional and rate command action affects the recorded readings output and output rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output.


### Profile Measurement Response (Natural Language)

Use G=1/(s^2+1.4s+1), kP=6; compare kD=0 and output-rate kD=2 at 0.005 s for 12 s.

The declared software model is a transfer function from proportional and rate command in normalized input units to output and output rate in normalized output units. Its numerator coefficients are 6; its denominator coefficients are 1, 3.4, 7; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 12 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 72. Design PI control for a two-thermal-mass process

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is heater command, and the measured outputs are controlled temperature and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in controlled temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after heater command changes, controlled temperature begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from heater command actuation to the visible controlled temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the controlled temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heater command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in heater command can drive a distinguishable change in the key output controlled temperature; heater command and the recorded readings controlled temperature and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One heater command action affects the recorded readings controlled temperature and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use Ko=1000, tau1=1 s, tau2=10 s; compare P kP=0.03 and PI kP=0.03, kI=0.003 for a 30 degC/s ramp capped at 300 degC.

The declared software model is a transfer function from heater command in degC to controlled temperature and control effort in degC. Its numerator coefficients are 3; its denominator coefficients are 1, 1, 3; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 50 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 73. Compare P, PI, and PID on DC-motor speed

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage with prescribed load-torque disturbance, and the measured outputs are motor speed, tracking error, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after armature voltage with prescribed load-torque disturbance changes, motor speed begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from armature voltage with prescribed load-torque disturbance actuation to the visible motor speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the motor speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in armature voltage with prescribed load-torque disturbance produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in armature voltage with prescribed load-torque disturbance can drive a distinguishable change in the key output motor speed; armature voltage with prescribed load-torque disturbance and the recorded readings motor speed, tracking error, and disturbance response share one clock, so all relevant motion can be reconstructed from these synchronized records. One armature voltage with prescribed load-torque disturbance action affects the recorded readings motor speed, tracking error, and disturbance response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.


### Profile Measurement Response (Natural Language)

Use Jm=0.0113, b=0.028, La=0.1, Ra=1, Kt=Ke=0.067; compare P/PI/PID using kP=3, kI=15, kD=0.3.

The declared software model is a transfer function from armature voltage with prescribed load-torque disturbance in V to motor speed in rad/s. Its numerator coefficients are 0.0201, 0.201, 1.005; its denominator coefficients are 0.00113, 0.0342, 0.233489, 1.005; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 74. Analyze P/PI DC-motor position disturbance types with non-unity sensing

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is motor voltage with prescribed disturbance torque, and the measured outputs are motor position, speed, and sensed error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after motor voltage with prescribed disturbance torque changes, motor position begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from motor voltage with prescribed disturbance torque actuation to the visible motor position response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in motor voltage with prescribed disturbance torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in motor voltage with prescribed disturbance torque can drive a distinguishable change in the key output motor position; motor voltage with prescribed disturbance torque and the recorded readings motor position, speed, and sensed error share one clock, so all relevant motion can be reconstructed from these synchronized records. One motor voltage with prescribed disturbance torque action affects the recorded readings motor position, speed, and sensed error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.


### Profile Measurement Response (Natural Language)

Use A=B=tau=1, h=0.8; compare P kP=4 and PI kP=4, kI=2 for reference and torque disturbance.

The declared software model is a transfer function from motor voltage with prescribed disturbance torque in normalized input units to motor position in normalized output units. Its numerator coefficients are 4, 2; its denominator coefficients are 1, 1, 3.2, 1.6; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 25 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 75. Compare satellite PD and PID system type for reference and disturbance inputs

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body-torque command with prescribed disturbance torque, and the measured outputs are attitude angle, angular rate, and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after body-torque command with prescribed disturbance torque changes, attitude angle begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from body-torque command with prescribed disturbance torque actuation to the visible attitude angle response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body-torque command with prescribed disturbance torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in body-torque command with prescribed disturbance torque can drive a distinguishable change in the key output attitude angle; body-torque command with prescribed disturbance torque and the recorded readings attitude angle, angular rate, and tracking error share one clock, so all relevant motion can be reconstructed from these synchronized records. One body-torque command with prescribed disturbance torque action affects the recorded readings attitude angle, angular rate, and tracking error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude angle.


### Profile Measurement Response (Natural Language)

Use J=1, kP=4, kD=3; for PID add kI=1. Test reference and torque inputs one at a time.

The declared software model is a transfer function from body-torque command with prescribed disturbance torque in normalized input units to attitude angle in normalized output units. Its numerator coefficients are 3, 4; its denominator coefficients are 1, 3, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 25 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 76. Tune a PID from a process reaction curve for quarter-decay behavior

### Control Problem Description

This is an industrial process loop identified from a small actuator step and its recorded reaction curve before PID tuning. The control inputs are P, PI, or PID process command, and the measured outputs are process output and quarter-decay response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in process output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after P, PI, or PID process command changes, process output begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from P, PI, or PID process command actuation to the visible process output response contains one or two dominant storage or integration processes. When the input returns to baseline, the process output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in P, PI, or PID process command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in P, PI, or PID process command can drive a distinguishable change in the key output process output; P, PI, or PID process command and the recorded readings process output and quarter-decay response share one clock, so all relevant motion can be reconstructed from these synchronized records. One P, PI, or PID process command action affects the recorded readings process output and quarter-decay response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for process output.


### Profile Measurement Response (Natural Language)

Use G=2 exp(-3s)/(20s+1), R=0.1 s^-1, L=3 s; test reaction-curve P/PI/PID at 0.02 s for 100 s.

The declared software model is a transfer function from P in normalized input units to process output and quarter-decay response in normalized output units. Its numerator coefficients are 2; its denominator coefficients are 20, 1; and its input delay is 3 s.

The accompanying existing software record uses a 0.02 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 77. Tune P/PI/PID from ultimate gain and ultimate period

### Control Problem Description

This is a process feedback loop whose proportional gain can be raised until the measured output reaches sustained oscillation. The control input is proportional or PID process command, and the measured outputs are marginal oscillation and tuned response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in marginal oscillation starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after proportional or PID process command changes, marginal oscillation begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from proportional or PID process command actuation to the visible marginal oscillation response contains one or two dominant storage or integration processes. When the input returns to baseline, the marginal oscillation response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional or PID process command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in proportional or PID process command can drive a distinguishable change in the key output marginal oscillation; proportional or PID process command and the recorded readings marginal oscillation and tuned response share one clock, so all relevant motion can be reconstructed from these synchronized records. One proportional or PID process command action affects the recorded readings marginal oscillation and tuned response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for marginal oscillation.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s+1)(s+2)], whose Ku=6 and Pu=4.44288 s; measure marginal oscillation then apply P/PI/PID table settings.

The declared software model is a transfer function from proportional or PID process command in normalized input units to marginal oscillation and tuned response in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 3, 2, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 40 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 78. Apply reaction-curve Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is steam-valve P or PI command, and the measured outputs are heat-exchanger temperature and step response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heat-exchanger temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after steam-valve P or PI command changes, a visible quiet interval separates the command from the first heat-exchanger temperature change, which is first distinguishable 13 s after the input change. The path from steam-valve P or PI command actuation to the visible heat-exchanger temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the heat-exchanger temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steam-valve P or PI command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in steam-valve P or PI command can drive a distinguishable change in the key output heat-exchanger temperature; steam-valve P or PI command and the recorded readings heat-exchanger temperature and step response share one clock, so all relevant motion can be reconstructed from these synchronized records. One steam-valve P or PI command action affects the recorded readings heat-exchanger temperature and step response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use reaction-curve R=1/90 s^-1, L=13 s and model exp(-13s)/(90s+1); compare P 6.92 and PI 6.22, TI=43.3 s, then half gains.

The declared software model is a transfer function from steam-valve P or PI command in normalized input units to heat-exchanger temperature and step response in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 90, 1; and its input delay is 13 s.

The accompanying existing software record uses a 0.1 s sample interval for 500 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 79. Apply ultimate-sensitivity Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is steam-valve P or PI command, and the measured outputs are heat-exchanger temperature and oscillation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heat-exchanger temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after steam-valve P or PI command changes, a visible quiet interval separates the command from the first heat-exchanger temperature change, which is first distinguishable 13 s after the input change. The path from steam-valve P or PI command actuation to the visible heat-exchanger temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the heat-exchanger temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steam-valve P or PI command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in steam-valve P or PI command can drive a distinguishable change in the key output heat-exchanger temperature; steam-valve P or PI command and the recorded readings heat-exchanger temperature and oscillation share one clock, so all relevant motion can be reconstructed from these synchronized records. One steam-valve P or PI command action affects the recorded readings heat-exchanger temperature and oscillation; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use measured Ku=15.3, Pu=42 s; compare P kP=7.65 and PI kP=6.885, TI=35 s, then repeat with half gain.

The declared software model is a transfer function from steam-valve P or PI command in normalized input units to heat-exchanger temperature and oscillation in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 90, 1; and its input delay is 13 s.

The accompanying existing software record uses a 0.1 s sample interval for 500 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 80. Add inverse-DC-gain feedforward to DC-motor tracking and measured-disturbance rejection

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage combining feedback and feedforward, and the measured outputs are motor speed, tracking error, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after armature voltage combining feedback and feedforward changes, motor speed begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from armature voltage combining feedback and feedforward actuation to the visible motor speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the motor speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in armature voltage combining feedback and feedforward produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in armature voltage combining feedback and feedforward can drive a distinguishable change in the key output motor speed; armature voltage combining feedback and feedforward and the recorded readings motor speed, tracking error, and disturbance response share one clock, so all relevant motion can be reconstructed from these synchronized records. One armature voltage combining feedback and feedforward action affects the recorded readings motor speed, tracking error, and disturbance response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.


### Profile Measurement Response (Natural Language)

Use G=1/(s^2+1.4s+1), G(0)=1; compare kP=1.5 and 6 with kff=1 for reference and measured-disturbance feedforward.

The declared software model is a transfer function from armature voltage combining feedback and feedforward in normalized input units to motor speed in normalized output units. Its numerator coefficients are 2.5; its denominator coefficients are 1, 1.4, 2.5; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 81. Draw and parameterize the DC-motor position-control root locus

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is motor armature voltage, and the measured outputs are motor position and tracking response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after motor armature voltage changes, motor position begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from motor armature voltage actuation to the visible motor position response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in motor armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in motor armature voltage can drive a distinguishable change in the key output motor position; motor armature voltage and the recorded readings motor position and tracking response share one clock, so all relevant motion can be reconstructed from these synchronized records. One motor armature voltage action affects the recorded readings motor position and tracking response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s+1)] and sweep K over 0.1, 0.25, 1, 4; sample unit steps at 0.01 s for 20 s.

The declared software model is a transfer function from motor armature voltage in normalized input units to motor position and tracking response in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 82. Draw a root locus with respect to a physical damping/pole parameter

### Control Problem Description

This is a feedback system whose loop strength can be swept while closed-loop poles and motion are recorded. The control input is bounded modal test input while damping is varied, and the measured outputs are modal response and decay envelope, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in modal response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded modal test input while damping is varied changes, modal response begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded modal test input while damping is varied actuation to the visible modal response response contains one or two dominant storage or integration processes. When the input is removed, the modal response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded modal test input while damping is varied produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded modal test input while damping is varied can drive a distinguishable change in the key output modal response; bounded modal test input while damping is varied and the recorded readings modal response and decay envelope share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded modal test input while damping is varied action affects the recorded readings modal response and decay envelope; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for modal response.


### Profile Measurement Response (Natural Language)

Use characteristic s^2+c s+1 and sweep physical damping c=0,1,2,4; sample free and step responses.

The declared software model is a transfer function from bounded modal test input while damping is varied in normalized input units to modal response and decay envelope in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 2, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 83. Construct a higher-order locus from Evans phase, real-axis, asymptote, departure, and gain rules

### Control Problem Description

This is a feedback system whose loop strength can be swept while closed-loop poles and motion are recorded. The control input is bounded command during a loop-strength sweep, and the measured outputs are controlled output and transient response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in controlled output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded command during a loop-strength sweep changes, controlled output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded command during a loop-strength sweep actuation to the visible controlled output response contains at least three successive storage or integration processes. When the input is removed, the controlled output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded command during a loop-strength sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded command during a loop-strength sweep can drive a distinguishable change in the key output controlled output; bounded command during a loop-strength sweep and the recorded readings controlled output and transient response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded command during a loop-strength sweep action affects the recorded readings controlled output and transient response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for controlled output.


### Profile Measurement Response (Natural Language)

Use L=1/[s((s+4)^2+16)] and sweep K near 10, 32, 65, 100; sample at 0.01 s for 30 s.

The declared software model is a transfer function from bounded command during a loop-strength sweep in normalized input units to controlled output and transient response in normalized output units. Its numerator coefficients are 65; its denominator coefficients are 1, 8, 32, 65; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 84. Stabilize a satellite double integrator with PD control

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is PD body-torque command, and the measured outputs are satellite attitude and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after PD body-torque command changes, satellite attitude begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from PD body-torque command actuation to the visible satellite attitude response contains one or two dominant storage or integration processes. When the input is removed, the satellite attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in PD body-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in PD body-torque command can drive a distinguishable change in the key output satellite attitude; PD body-torque command and the recorded readings satellite attitude and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One PD body-torque command action affects the recorded readings satellite attitude and angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for satellite attitude.


### Profile Measurement Response (Natural Language)

Use satellite G=1/s^2 and PD D=K(s+1); sweep K=0.25,1,4,9 with filtered derivative.

The declared software model is a transfer function from PD body-torque command in normalized input units to satellite attitude and angular rate in normalized output units. Its numerator coefficients are 1, 1; its denominator coefficients are 1, 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 85. Quantify how a finite lead pole changes the satellite PD locus, including the 9:1 transition

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is lead-compensated body torque, and the measured outputs are satellite attitude and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after lead-compensated body torque changes, satellite attitude begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from lead-compensated body torque actuation to the visible satellite attitude response contains one or two dominant storage or integration processes. When the input is removed, the satellite attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in lead-compensated body torque can drive a distinguishable change in the key output satellite attitude; lead-compensated body torque and the recorded readings satellite attitude and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One lead-compensated body torque action affects the recorded readings satellite attitude and angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for satellite attitude.


### Profile Measurement Response (Natural Language)

Use L=(s+1)/[s^2(s+p)] and compare p=4,9,12 at K=1,5,20, with 0.005 s sampling.

The declared software model is a transfer function from lead-compensated body torque in normalized input units to satellite attitude and angular rate in normalized output units. Its numerator coefficients are 1, 1; its denominator coefficients are 1, 12, 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 86. Analyze collocated satellite flexibility and flexible-mode damping

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is collocated body torque, and the measured outputs are collocated attitude and flexible deflection, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in collocated attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after collocated body torque changes, collocated attitude begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from collocated body torque actuation to the visible collocated attitude response contains one or two dominant storage or integration processes. When the input is removed, the collocated attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in collocated body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in collocated body torque can drive a distinguishable change in the key output collocated attitude; collocated body torque and the recorded readings collocated attitude and flexible deflection share one clock, so all relevant motion can be reconstructed from these synchronized records. One collocated body torque action affects the recorded readings collocated attitude and flexible deflection; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use collocated flexible satellite G=[(s+0.1)^2+36]/{s^2[(s+0.1)^2+43.56]} and lead K(s+1)/(s+12); sweep K.

The declared software model is a transfer function from collocated body torque in normalized input units to collocated attitude and flexible deflection in normalized output units. Its numerator coefficients are 1, 1.2, 36.01; its denominator coefficients are 1, 12.2, 45.97, 522.84, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 87. Analyze noncollocated satellite flexibility and spillover instability

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is main-body torque, and the measured outputs are remote attitude and flexible deflection, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in remote attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after main-body torque changes, remote attitude begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from main-body torque actuation to the visible remote attitude response contains at least three successive storage or integration processes. When the input is removed, the remote attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in main-body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in main-body torque can drive a distinguishable change in the key output remote attitude; main-body torque and the recorded readings remote attitude and flexible deflection share one clock, so all relevant motion can be reconstructed from these synchronized records. One main-body torque action affects the recorded readings remote attitude and flexible deflection; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use noncollocated G=1/{s^2[(s+0.1)^2+43.56]} with lead K(s+1)/(s+12); start K at 1e-4 and stop on instability.

The declared software model is a transfer function from main-body torque in normalized input units to remote attitude and flexible deflection in normalized output units. Its numerator coefficients are 1, 1; its denominator coefficients are 1, 12.2, 45.97, 522.84, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -0.01, -0.005, 0.005, 0.01, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 88. Handle complex multiple roots on a fourth-order locus

### Control Problem Description

This is a feedback system whose loop strength can be swept while closed-loop poles and motion are recorded. The control input is bounded command during a loop-strength sweep, and the measured outputs are closed-loop output near the repeated-root condition, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output near the repeated-root condition starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after bounded command during a loop-strength sweep changes, closed-loop output near the repeated-root condition begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from bounded command during a loop-strength sweep actuation to the visible closed-loop output near the repeated-root condition response contains at least three successive storage or integration processes. When the input is removed, the closed-loop output near the repeated-root condition response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded command during a loop-strength sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded command during a loop-strength sweep can drive a distinguishable change in the key output closed-loop output near the repeated-root condition; bounded command during a loop-strength sweep and the recorded readings closed-loop output near the repeated-root condition share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded command during a loop-strength sweep action affects the recorded readings closed-loop output near the repeated-root condition; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output near the repeated-root condition.


### Profile Measurement Response (Natural Language)

Use L=1/[s(s+2)((s+1)^2+4)] and sweep K across 6.25; sample at 0.005 s for 20 s.

The declared software model is a transfer function from bounded command during a loop-strength sweep in normalized input units to closed-loop output near the repeated-root condition in normalized output units. Its numerator coefficients are 6.25; its denominator coefficients are 1, 4, 8, 8, 6.25; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 89. Design lead compensation to meet rise-time and overshoot limits

### Control Problem Description

This is a motor-driven position servo fitted with a lead compensator to reshape its dominant transient motion. The control input is lead-compensated servo command, and the measured outputs are servo position, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after lead-compensated servo command changes, servo position begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from lead-compensated servo command actuation to the visible servo position response contains one or two dominant storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated servo command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in lead-compensated servo command can drive a distinguishable change in the key output servo position; lead-compensated servo command and the recorded readings servo position, tracking error, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One lead-compensated servo command action affects the recorded readings servo position, tracking error, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s+1)] and lead D=91(s+2)/(s+13); test +/-1 steps at 0.002 s for 5 s.

The declared software model is a transfer function from lead-compensated servo command in normalized input units to servo position in normalized output units. Its numerator coefficients are 91, 182; its denominator coefficients are 1, 14, 104, 182; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 5 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 90. Add lag compensation to improve velocity-error constant without moving dominant roots

### Control Problem Description

This is a motor-driven position servo fitted with lead-lag compensation to improve tracking without displacing its dominant motion excessively. The control input is lead-lag servo command, and the measured outputs are servo position, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after lead-lag servo command changes, servo position begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from lead-lag servo command actuation to the visible servo position response contains one or two dominant storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-lag servo command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in lead-lag servo command can drive a distinguishable change in the key output servo position; lead-lag servo command and the recorded readings servo position, tracking error, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One lead-lag servo command action affects the recorded readings servo position, tracking error, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.


### Profile Measurement Response (Natural Language)

Add lag (s+0.05)/(s+0.01) to the K=91 lead design; run ramp and step tests for 300 s.

The declared software model is a transfer function from lead-lag servo command in normalized input units to servo position in normalized output units. Its numerator coefficients are 91, 186.55, 9.1; its denominator coefficients are 1, 14.01, 104.14, 186.68, 9.1; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 91. Add notch compensation for an unmodeled flexible resonance

### Control Problem Description

This is a flexible motion plant whose actuator excites a lightly damped structural mode and whose command path includes a notch filter. The control input is notch-filtered actuator command, and the measured outputs are nominal output and flexible displacement, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in nominal output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0005 s sample interval; after notch-filtered actuator command changes, nominal output begins within one sample, with its first distinguishable change recorded 0.0005 s after the input change and without a separate silent interval. The path from notch-filtered actuator command actuation to the visible nominal output response contains at least three successive storage or integration processes. When the input is removed, the nominal output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in notch-filtered actuator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in notch-filtered actuator command can drive a distinguishable change in the key output nominal output; notch-filtered actuator command and the recorded readings nominal output and flexible displacement share one clock, so all relevant motion can be reconstructed from these synchronized records. One notch-filtered actuator command action affects the recorded readings nominal output and flexible displacement; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use flexible plant 2500/[s(s+1)(s^2+s+2500)], the K=91 lead-lag, and notch (s^2+0.8s+3600)/(s+60)^2; sweep flexible frequency by +/-10%.

The declared software model is a transfer function from notch-filtered actuator command in normalized input units to nominal output and flexible displacement in normalized output units. Its numerator coefficients are 2500; its denominator coefficients are 1, 2, 2501, 2500, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.0005 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 92. Realize a lead compensator with an operational-amplifier circuit

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is input error voltage, and the measured outputs are lead-network output voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lead-network output voltage starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after input error voltage changes, lead-network output voltage begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from input error voltage actuation to the visible lead-network output voltage response contains one or two dominant storage or integration processes. When the input returns to baseline, the lead-network output voltage response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input error voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in input error voltage can drive a distinguishable change in the key output lead-network output voltage; input error voltage and the recorded readings lead-network output voltage share one clock, so all relevant motion can be reconstructed from these synchronized records. One input error voltage action affects the recorded readings lead-network output voltage; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lead-network output voltage.


### Profile Measurement Response (Natural Language)

Realize -5(s+2)/(s+10) with C=10 uF, R1=50 kohm, R2=200 kohm, Rf=250 kohm; sweep component tolerances +/-10%.

The declared software model is a transfer function from input error voltage in V to lead-network output voltage in V. Its numerator coefficients are -5, -10; its denominator coefficients are 1, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 5 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 93. Design quadrotor pitch-axis lead compensation

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is pitch rotor-torque command, and the measured outputs are quadrotor pitch angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in quadrotor pitch angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after pitch rotor-torque command changes, quadrotor pitch angle begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from pitch rotor-torque command actuation to the visible quadrotor pitch angle response contains one or two dominant storage or integration processes. When the input is removed, the quadrotor pitch angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in pitch rotor-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in pitch rotor-torque command can drive a distinguishable change in the key output quadrotor pitch angle; pitch rotor-torque command and the recorded readings quadrotor pitch angle and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One pitch rotor-torque command action affects the recorded readings quadrotor pitch angle and angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use quadrotor pitch plant 1/[s^2(s+2)] and lead 30(s+0.5)/(s+15); test +/-0.1 rad commands at 0.002 s for 15 s.

The declared software model is a transfer function from pitch rotor-torque command in rad to quadrotor pitch angle and angular rate in rad. Its numerator coefficients are 30, 15; its denominator coefficients are 1, 17, 30, 30, 15; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 94. Design a small-airplane pitch autopilot and integral trim loop

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is elevator and trim-tab commands, and the measured outputs are pitch attitude, elevator, and trim-tab deflections, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pitch attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after elevator and trim-tab commands changes, pitch attitude begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from elevator and trim-tab commands actuation to the visible pitch attitude response contains one or two dominant storage or integration processes. When the input returns to baseline, the pitch attitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in elevator and trim-tab commands produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in elevator and trim-tab commands can drive a distinguishable change in the key output pitch attitude; elevator and trim-tab commands and the recorded readings pitch attitude, elevator, and trim-tab deflections share one clock, so all relevant motion can be reconstructed from these synchronized records. One elevator and trim-tab commands action affects the recorded readings pitch attitude, elevator, and trim-tab deflections; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use airplane G=160(s+2.5)(s+0.7)/[(s^2+5s+40)(s^2+0.03s+0.06)], lead K=1.5,z=3,p=20, and trim integrator KI=0.15.

The declared software model is a transfer function from elevator and trim-tab commands in normalized input units to pitch attitude in normalized output units. Its numerator coefficients are 160, 512, 280; its denominator coefficients are 1, 5.03, 40.21, 1.5, 2.4; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 40 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 95. Use a negative root locus for nonminimum-phase airplane altitude dynamics

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is elevator command, and the measured outputs are aircraft altitude response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in aircraft altitude response first moves in an unfavorable or opposite direction before turning. The synchronized record has a 0.01 s sample interval; after elevator command changes, aircraft altitude response first begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from elevator command actuation to the visible aircraft altitude response first response contains one or two dominant storage or integration processes. When the input is removed, the aircraft altitude response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in elevator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in elevator command can drive a distinguishable change in the key output aircraft altitude response first; elevator command and the recorded readings aircraft altitude response share one clock, so all relevant motion can be reconstructed from these synchronized records. One elevator command action affects the recorded readings aircraft altitude response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use airplane altitude G=(6-s)/[s(s^2+4s+13)] and sweep positive physical gain using the corresponding negative root locus; apply +/-1 degree pulses.

The declared software model is a transfer function from elevator command in deg to aircraft altitude response in ft. Its numerator coefficients are -1, 6; its denominator coefficients are 1, 4, 13, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 96. Select tachometer and amplifier gains by successive loop closure

### Control Problem Description

This is a motor-driven servomechanism containing an amplifier, position loop, and tachometer speed-feedback loop. The control input is servo amplifier voltage under tachometer feedback, and the measured outputs are servomechanism position and speed response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servomechanism position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after servo amplifier voltage under tachometer feedback changes, servomechanism position begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from servo amplifier voltage under tachometer feedback actuation to the visible servomechanism position response contains one or two dominant storage or integration processes. When the input is removed, the servomechanism position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in servo amplifier voltage under tachometer feedback produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in servo amplifier voltage under tachometer feedback can drive a distinguishable change in the key output servomechanism position; servo amplifier voltage under tachometer feedback and the recorded readings servomechanism position and speed response share one clock, so all relevant motion can be reconstructed from these synchronized records. One servo amplifier voltage under tachometer feedback action affects the recorded readings servomechanism position and speed response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servomechanism position.


### Profile Measurement Response (Natural Language)

Use s^2+s+KA+KT s=0; choose KA=4 then KT=1 and repeat after +/-10% changes.

The declared software model is a transfer function from servo amplifier voltage under tachometer feedback in normalized input units to servomechanism position and speed response in normalized output units. Its numerator coefficients are 4; its denominator coefficients are 1, 2, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 97. Design inner-attitude/outer-position quadrotor cascade control

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is outer position command and inner rotor-torque command, and the measured outputs are horizontal position, pitch attitude, and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in horizontal position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after outer position command and inner rotor-torque command changes, horizontal position begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from outer position command and inner rotor-torque command actuation to the visible horizontal position response contains at least three successive storage or integration processes. When the input is removed, the horizontal position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in outer position command and inner rotor-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in outer position command and inner rotor-torque command can drive a distinguishable change in the key output horizontal position; outer position command and inner rotor-torque command and the recorded readings horizontal position, pitch attitude, and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One outer position command and inner rotor-torque command action affects the recorded readings horizontal position, pitch attitude, and angular rate; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use inner pitch plant 1/[s^2(s+2)] with 30(s+0.5)/(s+15), outer position plant -32.2/s^2, and outer lead 0.081(s+0.1)/(s+10).

The declared software model is a transfer function from outer position command and inner rotor-torque command in ft to horizontal position in ft. Its numerator coefficients are 2.6082, 0.26082; its denominator coefficients are 1, 10, 2.6082, 0.26082; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 40 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 98. Design a lead compensator for a numerically controlled machine-tool servo

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is lead-compensated servo command, and the measured outputs are machine-tool position, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in machine-tool position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after lead-compensated servo command changes, machine-tool position begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from lead-compensated servo command actuation to the visible machine-tool position response contains one or two dominant storage or integration processes. When the input is removed, the machine-tool position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated servo command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in lead-compensated servo command can drive a distinguishable change in the key output machine-tool position; lead-compensated servo command and the recorded readings machine-tool position, tracking error, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One lead-compensated servo command action affects the recorded readings machine-tool position, tracking error, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use machine-tool G=1/[s(s+1)] and lead 10(s+1)/(s+2); test +/-1 position steps and +/-10% pole variation.

The declared software model is a transfer function from lead-compensated servo command in normalized input units to machine-tool position in normalized output units. Its numerator coefficients are 10, 10; its denominator coefficients are 1, 3, 12, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 99. Linearize and stabilize an elementary magnetic suspension

### Control Problem Description

This is a magnetic-levitation apparatus in which an electromagnet supports a steel ball while a sensor measures the air gap. The control input is electromagnet current command, and the measured outputs are ball position, sensor voltage, and coil current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ball position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after electromagnet current command changes, ball position begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from electromagnet current command actuation to the visible ball position response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in ball position keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in electromagnet current command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in electromagnet current command can drive a distinguishable change in the key output ball position; electromagnet current command and the recorded readings ball position, sensor voltage, and coil current share one clock, so all relevant motion can be reconstructed from these synchronized records. One electromagnet current command action affects the recorded readings ball position, sensor voltage, and coil current; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use m=0.02 kg, g=9.8, e=100x, f=0.5i+20x, and lead (s+10)/(s+20) with K=1; sample at 0.001 s.

The declared software model is a transfer function from electromagnet current command in V to ball position in m. Its numerator coefficients are 50, 500; its denominator coefficients are 1, 20, 1500, 5000; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 100. Design yaw-rate-aided heading control for the USCG cutter Tampa under wind disturbance

### Control Problem Description

This is a surface-vessel steering system made from hull yaw motion, a rudder actuator, and heading sensors. The control input is rudder command and prescribed wind-gust input, and the measured outputs are ship heading, yaw rate, rudder angle, and wind response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ship heading starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after rudder command and prescribed wind-gust input changes, ship heading begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from rudder command and prescribed wind-gust input actuation to the visible ship heading response contains one or two dominant storage or integration processes. When the input is removed, the ship heading response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in rudder command and prescribed wind-gust input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in rudder command and prescribed wind-gust input can drive a distinguishable change in the key output ship heading; rudder command and prescribed wind-gust input and the recorded readings ship heading, yaw rate, rudder angle, and wind response share one clock, so all relevant motion can be reconstructed from these synchronized records. One rudder command and prescribed wind-gust input action affects the recorded readings ship heading, yaw rate, rudder angle, and wind response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use Tampa rudder plant -0.0184(s+0.0068)/[s(s+0.2647)(s+0.0063)]. With sign absorbed, use Kpsi=0.1, Kr=1, KI=0.0001 and enforce rudder limits.

The declared software model is a transfer function from rudder command and prescribed wind-gust input in rad to ship heading in rad. Its numerator coefficients are 0.00184, 1.4352e-05, 1.2512e-08; its denominator coefficients are 1, 0.2894, 0.00363273, 1.4352e-05, 1.2512e-08; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 2000 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 101. Compute the current response of a voltage-driven capacitor

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is sinusoidal voltage, and the measured outputs are capacitor current magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in capacitor current magnitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 5e-05 s sample interval; after sinusoidal voltage changes, capacitor current magnitude begins within one sample, with its first distinguishable change recorded 5e-05 s after the input change and without a separate silent interval. The path from sinusoidal voltage actuation to the visible capacitor current magnitude response contains one or two dominant storage or integration processes. When the input returns to baseline, the capacitor current magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sinusoidal voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sinusoidal voltage can drive a distinguishable change in the key output capacitor current magnitude; sinusoidal voltage and the recorded readings capacitor current magnitude and phase share one clock, so all relevant motion can be reconstructed from these synchronized records. One sinusoidal voltage action affects the recorded readings capacitor current magnitude and phase; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for capacitor current magnitude.


### Profile Measurement Response (Natural Language)

Use C=100 uF and voltage sinusoids of 1 V at 1, 10, 100, and 1000 rad/s; sample current with at least 50 points per cycle.

The declared software model is a transfer function from sinusoidal voltage in V to capacitor current magnitude and phase in A. Its numerator coefficients are 0.0001, 0; its denominator coefficients are 1; and its input delay is 0 s.

The accompanying existing software record uses a 5e-05 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 102. Derive the magnitude and phase of a first-order lead element

### Control Problem Description

This is a first-order lead network made from resistive and capacitive elements that advance output phase over a finite frequency band. The control input is sinusoidal error signal, and the measured outputs are lead-compensator magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lead-compensator magnitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after sinusoidal error signal changes, lead-compensator magnitude begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from sinusoidal error signal actuation to the visible lead-compensator magnitude response contains one or two dominant storage or integration processes. When the input returns to baseline, the lead-compensator magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sinusoidal error signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sinusoidal error signal can drive a distinguishable change in the key output lead-compensator magnitude; sinusoidal error signal and the recorded readings lead-compensator magnitude and phase share one clock, so all relevant motion can be reconstructed from these synchronized records. One sinusoidal error signal action affects the recorded readings lead-compensator magnitude and phase; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lead-compensator magnitude.


### Profile Measurement Response (Natural Language)

Use lead D=(s+1)/(0.1s+1), sweep 0.1 to 100 rad/s, and verify magnitude and phase at 1, sqrt(10), and 10 rad/s.

The declared software model is a transfer function from sinusoidal error signal in normalized input units to lead-compensator magnitude and phase in normalized output units. Its numerator coefficients are 1, 1; its denominator coefficients are 0.1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 103. Build an asymptotic Bode plot from real poles and zeros

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is sinusoidal plant input, and the measured outputs are open-loop magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in open-loop magnitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after sinusoidal plant input changes, open-loop magnitude begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from sinusoidal plant input actuation to the visible open-loop magnitude response contains one or two dominant storage or integration processes. When the input is removed, the open-loop magnitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in sinusoidal plant input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sinusoidal plant input can drive a distinguishable change in the key output open-loop magnitude; sinusoidal plant input and the recorded readings open-loop magnitude and phase share one clock, so all relevant motion can be reconstructed from these synchronized records. One sinusoidal plant input action affects the recorded readings open-loop magnitude and phase; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for open-loop magnitude.


### Profile Measurement Response (Natural Language)

Use L=2000(s+0.5)/[s(s+10)(s+50)] and evaluate 0.01 to 1000 rad/s on a logarithmic grid.

The declared software model is a transfer function from sinusoidal plant input in normalized input units to open-loop magnitude and phase in normalized output units. Its numerator coefficients are 2000, 1000; its denominator coefficients are 1, 60, 500, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 104. Include complex pole/zero factors in ordinary and flexible-system Bode plots

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is sinusoidal applied force, and the measured outputs are plant displacement magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in plant displacement magnitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after sinusoidal applied force changes, plant displacement magnitude begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from sinusoidal applied force actuation to the visible plant displacement magnitude response contains at least three successive storage or integration processes. When the input is removed, the plant displacement magnitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in sinusoidal applied force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sinusoidal applied force can drive a distinguishable change in the key output plant displacement magnitude; sinusoidal applied force and the recorded readings plant displacement magnitude and phase share one clock, so all relevant motion can be reconstructed from these synchronized records. One sinusoidal applied force action affects the recorded readings plant displacement magnitude and phase; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for plant displacement magnitude.


### Profile Measurement Response (Natural Language)

Compare L1=10/[s(s^2+0.4s+4)] with the flexible pole-zero doublet 0.01(s^2+0.01s+1)/{s^2(s^2/4+0.01s+1)}.

The declared software model is a transfer function from sinusoidal applied force in normalized input units to plant displacement magnitude and phase in normalized output units. Its numerator coefficients are 10; its denominator coefficients are 1, 0.4, 4, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 105. Infer low-frequency error constants and system type from a Bode plot

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is unit-ramp reference, and the measured outputs are tracking error and regulated output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tracking error starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after unit-ramp reference changes, tracking error begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from unit-ramp reference actuation to the visible tracking error response contains one or two dominant storage or integration processes. When the input is removed, the tracking error response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in unit-ramp reference produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in unit-ramp reference can drive a distinguishable change in the key output tracking error; unit-ramp reference and the recorded readings tracking error and regulated output share one clock, so all relevant motion can be reconstructed from these synchronized records. One unit-ramp reference action affects the recorded readings tracking error and regulated output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for tracking error.


### Profile Measurement Response (Natural Language)

Use L=10/[s(s+1)], run a unit ramp for 50 s at 0.01 s sampling, and fit the final error.

The declared software model is a transfer function from unit-ramp reference in normalized input units to tracking error and regulated output in normalized output units. Its numerator coefficients are 10; its denominator coefficients are 1, 1, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 50 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 106. Apply the Nyquist criterion to a second-order loop stable for every positive gain

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded loop command during a gain sweep, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded loop command during a gain sweep changes, closed-loop output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded loop command during a gain sweep actuation to the visible closed-loop output response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded loop command during a gain sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded loop command during a gain sweep can drive a distinguishable change in the key output closed-loop output; bounded loop command during a gain sweep and the recorded readings closed-loop output and frequency response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded loop command during a gain sweep action affects the recorded readings closed-loop output and frequency response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.


### Profile Measurement Response (Natural Language)

Use G=1/(s+1)^2 and sweep K=0.1,1,10,100; also test negative K=-0.5,-1,-2.

The declared software model is a transfer function from bounded loop command during a gain sweep in normalized input units to closed-loop output and frequency response in normalized output units. Its numerator coefficients are 4; its denominator coefficients are 1, 2, 5; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 107. Apply Nyquist indentation to a third-order loop with a pole at the origin

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded loop command during a gain sweep, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded loop command during a gain sweep changes, closed-loop output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded loop command during a gain sweep actuation to the visible closed-loop output response contains at least three successive storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded loop command during a gain sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded loop command during a gain sweep can drive a distinguishable change in the key output closed-loop output; bounded loop command during a gain sweep and the recorded readings closed-loop output and frequency response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded loop command during a gain sweep action affects the recorded readings closed-loop output and frequency response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s+1)^2] and sweep K=0.5,1,2,3; apply Nyquist indentation at the origin.

The declared software model is a transfer function from bounded loop command during a gain sweep in normalized input units to closed-loop output and frequency response in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 2, 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 108. Compare special Nyquist cases with an RHP pole and imaginary-axis zeros

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded commands used in the two loop tests, and the measured outputs are closed-loop outputs and frequency responses of both cases, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop outputs starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded commands used in the two loop tests changes, closed-loop outputs begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded commands used in the two loop tests actuation to the visible closed-loop outputs response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in closed-loop outputs keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in bounded commands used in the two loop tests produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded commands used in the two loop tests can drive a distinguishable change in the key output closed-loop outputs; bounded commands used in the two loop tests and the recorded readings closed-loop outputs and frequency responses of both cases share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded commands used in the two loop tests action affects the recorded readings closed-loop outputs and frequency responses of both cases; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop outputs.


### Profile Measurement Response (Natural Language)

For G1=(s+1)/[s(s/10-1)] use K=0.5,1,2; separately test G2=(s^2+3)/(s+1)^2 for positive gains.

The declared software model is a transfer function from bounded commands used in the two loop tests in normalized input units to closed-loop outputs and frequency responses of both cases in normalized output units. Its numerator coefficients are 20, 20; its denominator coefficients are 1, 10, 20; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 109. Diagnose conditional stability and misleading gain margin

### Control Problem Description

This is a feedback system whose closed-loop stability changes across distinct ranges of loop gain. The control input is bounded loop command during a gain sweep, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded loop command during a gain sweep changes, closed-loop output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded loop command during a gain sweep actuation to the visible closed-loop output response contains one or two dominant storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded loop command during a gain sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded loop command during a gain sweep can drive a distinguishable change in the key output closed-loop output; bounded loop command during a gain sweep and the recorded readings closed-loop output and frequency response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded loop command during a gain sweep action affects the recorded readings closed-loop output and frequency response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.


### Profile Measurement Response (Natural Language)

Use L=K(s+10)^2/s^3 and compare K=4.9,5,7,10; at K=7 measure both directions of gain margin.

The declared software model is a transfer function from bounded loop command during a gain sweep in normalized input units to closed-loop output and frequency response in normalized output units. Its numerator coefficients are 7, 140, 700; its denominator coefficients are 1, 7, 140, 700; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 110. Interpret multiple unity-gain crossings and stability margins

### Control Problem Description

This is a feedback loop whose open-loop frequency response crosses unit magnitude more than once before high-frequency rolloff. The control input is bounded sinusoidal loop excitation, and the measured outputs are closed-loop output and open-loop frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0005 s sample interval; after bounded sinusoidal loop excitation changes, closed-loop output begins within one sample, with its first distinguishable change recorded 0.0005 s after the input change and without a separate silent interval. The path from bounded sinusoidal loop excitation actuation to the visible closed-loop output response contains at least three successive storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded sinusoidal loop excitation produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded sinusoidal loop excitation can drive a distinguishable change in the key output closed-loop output; bounded sinusoidal loop excitation and the recorded readings closed-loop output and open-loop frequency response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded sinusoidal loop excitation action affects the recorded readings closed-loop output and open-loop frequency response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.


### Profile Measurement Response (Natural Language)

Use G=85(s+1)(s^2+2s+43.25)/{s^2(s^2+2s+82)(s^2+2s+101)} and resolve every unity crossing.

The declared software model is a transfer function from bounded sinusoidal loop excitation in normalized input units to closed-loop output and open-loop frequency response in normalized output units. Its numerator coefficients are 85, 255, 3846.25, 3676.25; its denominator coefficients are 1, 4, 187, 366, 8282, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.0005 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 111. Use Bode's gain-phase slope rule to design spacecraft PD control

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body-torque command, and the measured outputs are attitude, angular rate, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after body-torque command changes, attitude begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from body-torque command actuation to the visible attitude response contains one or two dominant storage or integration processes. When the input is removed, the attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in body-torque command can drive a distinguishable change in the key output attitude; body-torque command and the recorded readings attitude, angular rate, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One body-torque command action affects the recorded readings attitude, angular rate, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude.


### Profile Measurement Response (Natural Language)

Use spacecraft G=1/s^2 and KD=0.01(20s+1); apply +/-0.1 rad steps at 0.05 s for 200 s.

The declared software model is a transfer function from body-torque command in rad to attitude in rad. Its numerator coefficients are 0.2, 0.01; its denominator coefficients are 1, 0.2, 0.01; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 200 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 112. Relate crossover frequency, phase margin, resonant peak, and closed-loop bandwidth

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded sinusoidal command sweep, and the measured outputs are closed-loop output and bandwidth response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded sinusoidal command sweep changes, closed-loop output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded sinusoidal command sweep actuation to the visible closed-loop output response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded sinusoidal command sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded sinusoidal command sweep can drive a distinguishable change in the key output closed-loop output; bounded sinusoidal command sweep and the recorded readings closed-loop output and bandwidth response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded sinusoidal command sweep action affects the recorded readings closed-loop output and bandwidth response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.


### Profile Measurement Response (Natural Language)

Use representative L=1/[s(s+1)], calculate exact T=L/(1+L), and compare crossover, phase margin, resonance, and -3 dB bandwidth.

The declared software model is a transfer function from bounded sinusoidal command sweep in normalized input units to closed-loop output and bandwidth response in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 113. Design lead compensation for DC-motor position control

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is lead-compensated motor command, and the measured outputs are motor position, error, and step response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after lead-compensated motor command changes, motor position begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from lead-compensated motor command actuation to the visible motor position response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated motor command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in lead-compensated motor command can drive a distinguishable change in the key output motor position; lead-compensated motor command and the recorded readings motor position, error, and step response share one clock, so all relevant motion can be reconstructed from these synchronized records. One lead-compensated motor command action affects the recorded readings motor position, error, and step response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.


### Profile Measurement Response (Natural Language)

Use motor G=1/[s(s+1)] and lead D=10(s/2+1)/(s/10+1); test ramp and step commands.

The declared software model is a transfer function from lead-compensated motor command in normalized input units to motor position in normalized output units. Its numerator coefficients are 50, 100; its denominator coefficients are 1, 11, 60, 100; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 114. Design single- and double-lead compensation for a thermal plant and servomechanism

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is single- or double-lead command, and the measured outputs are temperature or servo output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in temperature or servo output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after single- or double-lead command changes, temperature or servo output begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from single- or double-lead command actuation to the visible temperature or servo output response contains at least three successive storage or integration processes. When the input is removed, the temperature or servo output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in single- or double-lead command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in single- or double-lead command can drive a distinguishable change in the key output temperature or servo output; single- or double-lead command and the recorded readings temperature or servo output share one clock, so all relevant motion can be reconstructed from these synchronized records. One single- or double-lead command action affects the recorded readings temperature or servo output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for temperature or servo output.


### Profile Measurement Response (Natural Language)

For the thermal plant use K=9 and lead (s/1.5+1)/(s/15+1); for the servo use the double lead (s/2+1)(s/4+1)/[(s/20+1)(s/40+1)].

The declared software model is a transfer function from single- or double-lead command in normalized input units to temperature or servo output in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 3.5, 3.5, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 115. Design lag compensation for a thermal plant and DC motor, and compare it with lead

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is lag-compensated command, and the measured outputs are thermal or motor response and slow tail, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in thermal or motor response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after lag-compensated command changes, thermal or motor response begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from lag-compensated command actuation to the visible thermal or motor response response contains at least three successive storage or integration processes. When the input is removed, the thermal or motor response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lag-compensated command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in lag-compensated command can drive a distinguishable change in the key output thermal or motor response; lag-compensated command and the recorded readings thermal or motor response and slow tail share one clock, so all relevant motion can be reconstructed from these synchronized records. One lag-compensated command action affects the recorded readings thermal or motor response and slow tail; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for thermal or motor response.


### Profile Measurement Response (Natural Language)

For the thermal plant use lag 3(5s+1)/(15s+1); for the motor use K=10 with lag zero 0.1 and pole 0.01 rad/s.

The declared software model is a transfer function from lag-compensated command in normalized input units to thermal or motor response and slow tail in normalized output units. Its numerator coefficients are 100, 10; its denominator coefficients are 100, 110, 10, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 116. Design spacecraft PID control with a sensor lag and constant torque disturbance

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body-torque command with prescribed disturbance torque, and the measured outputs are attitude, angular rate, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after body-torque command with prescribed disturbance torque changes, attitude begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from body-torque command with prescribed disturbance torque actuation to the visible attitude response contains one or two dominant storage or integration processes. When the input is removed, the attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body-torque command with prescribed disturbance torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in body-torque command with prescribed disturbance torque can drive a distinguishable change in the key output attitude; body-torque command with prescribed disturbance torque and the recorded readings attitude, angular rate, and disturbance response share one clock, so all relevant motion can be reconstructed from these synchronized records. One body-torque command with prescribed disturbance torque action affects the recorded readings attitude, angular rate, and disturbance response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude.


### Profile Measurement Response (Natural Language)

Use spacecraft G=0.9/s^2, sensor H=2/(s+2), and PID D=0.05(10s+1)(s+0.005)/s; test command and constant torque separately.

The declared software model is a transfer function from body-torque command with prescribed disturbance torque in normalized input units to attitude in normalized output units. Its numerator coefficients are 0.9, 0.0945, 0.00045; its denominator coefficients are 1, 2, 0, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 2000 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 117. Convert a sinusoidal tracking-error requirement into a loop-gain performance bound

### Control Problem Description

This is a tracking-control loop driven by a sinusoidal reference while error and regulated output are recorded together. The control input is prescribed sinusoidal reference command, and the measured outputs are tracking error and regulated output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tracking error starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0001 s sample interval; after prescribed sinusoidal reference command changes, tracking error begins within one sample, with its first distinguishable change recorded 0.0001 s after the input change and without a separate silent interval. The path from prescribed sinusoidal reference command actuation to the visible tracking error response contains one or two dominant storage or integration processes. When the input is removed, the tracking error response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in prescribed sinusoidal reference command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed sinusoidal reference command can drive a distinguishable change in the key output tracking error; prescribed sinusoidal reference command and the recorded readings tracking error and regulated output share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed sinusoidal reference command action affects the recorded readings tracking error and regulated output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for tracking error.


### Profile Measurement Response (Natural Language)

Require unit-amplitude sinusoidal tracking error <=0.005 from 0 to 100 Hz; use an exact sensitivity test with S=1/201 over the band.

The declared software model is a transfer function from prescribed sinusoidal reference command in normalized input units to tracking error and regulated output in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 201; and its input delay is 0 s.

The accompanying existing software record uses a 0.0001 s sample interval for 2 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 118. Enforce robust-stability and sensitivity bounds under plant uncertainty

### Control Problem Description

This is a feedback system built around an uncertain dynamic plant, with controller and sensor channels used to limit sensitivity. The control input is loop-shaped feedback command under prescribed plant variation, and the measured outputs are regulated output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after loop-shaped feedback command under prescribed plant variation changes, regulated output begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from loop-shaped feedback command under prescribed plant variation actuation to the visible regulated output response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in loop-shaped feedback command under prescribed plant variation produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in loop-shaped feedback command under prescribed plant variation can drive a distinguishable change in the key output regulated output; loop-shaped feedback command under prescribed plant variation and the recorded readings regulated output, tracking error, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One loop-shaped feedback command under prescribed plant variation action affects the recorded readings regulated output, tracking error, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use antenna G=1/[s(s+1)] and D=10(0.5s+1)/(0.1s+1); compute S and T, then apply the stated high-frequency uncertainty weight.

The declared software model is a transfer function from loop-shaped feedback command under prescribed plant variation in normalized input units to regulated output in normalized output units. Its numerator coefficients are 0.1, 1.1, 1, 0; its denominator coefficients are 0.1, 1.1, 6, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 50 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 119. Quantify the phase-margin loss caused by sampling-equivalent time delay

### Control Problem Description

This is a sampled-data feedback loop made from a sampler, digital command path, hold element, and continuous plant. The control input is digitally sampled control command, and the measured outputs are sampled plant output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled plant output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after digitally sampled control command changes, a visible quiet interval separates the command from the first sampled plant output change, which is first distinguishable 0.025 s after the input change. The path from digitally sampled control command actuation to the visible sampled plant output response contains one or two dominant storage or integration processes. When the input returns to baseline, the sampled plant output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in digitally sampled control command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digitally sampled control command can drive a distinguishable change in the key output sampled plant output; digitally sampled control command and the recorded readings sampled plant output, tracking error, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One digitally sampled control command action affects the recorded readings sampled plant output, tracking error, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled plant output.


### Profile Measurement Response (Natural Language)

Insert equivalent delay Td=0.025 s into the lead-compensated motor loop with crossover 5 rad/s; compare Ts=0.05 and 0.14 s.

The declared software model is a transfer function from digitally sampled control command in normalized input units to sampled plant output in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1; and its input delay is 0.025 s.

The accompanying existing software record uses a 0.001 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 120. Read closed-loop bandwidth, resonant peak, and stability margins from a Nichols chart

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded frequency-swept input, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded frequency-swept input changes, closed-loop output begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded frequency-swept input actuation to the visible closed-loop output response contains one or two dominant storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded frequency-swept input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded frequency-swept input can drive a distinguishable change in the key output closed-loop output; bounded frequency-swept input and the recorded readings closed-loop output and frequency response share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded frequency-swept input action affects the recorded readings closed-loop output and frequency response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.


### Profile Measurement Response (Natural Language)

Use the PID-loop frequency samples and read Nichols contours; verify bandwidth 0.8 rad/s, resonant peak 1.2, PM 37 degrees, and GM 1.26.

The declared software model is a transfer function from bounded frequency-swept input in normalized input units to closed-loop output and frequency response in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 0.9, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 121. Put rigid-satellite attitude dynamics into state-variable form

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is thruster force, and the measured outputs are attitude angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after thruster force changes, attitude angle begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from thruster force actuation to the visible attitude angle response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in thruster force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in thruster force can drive a distinguishable change in the key output attitude angle; thruster force and the recorded readings attitude angle and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One thruster force action affects the recorded readings attitude angle and angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude angle.


### Profile Measurement Response (Natural Language)

Use lever arm d=1 m, inertia I=5000 kg*m^2, state [angle, rate], and +/-25 N pulses; sample at 0.01 s for 20 s.

The existing software record supplies a state-space model with state order angle, rate; matrix A has rows [0, 1]; [0, 0]; matrix B has rows [0]; [0.0002]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are thruster force, the output channels are attitude angle and angular rate channel 1, attitude angle and angular rate channel 2, and the initial state is 0, 0.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -25, -12.5, 12.5, 25, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 122. Derive a DC-motor state model from coupled mechanical and electrical equations

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage, and the measured outputs are motor position, speed, current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after armature voltage changes, motor position begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from armature voltage actuation to the visible motor position response contains at least three successive storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in armature voltage can drive a distinguishable change in the key output motor position; armature voltage and the recorded readings motor position, speed, current share one clock, so all relevant motion can be reconstructed from these synchronized records. One armature voltage action affects the recorded readings motor position, speed, current; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.


### Profile Measurement Response (Natural Language)

Use J=0.0113, b=0.028, La=0.1, Ra=1, Kt=Ke=0.067; apply +/-1 V steps and log angle, speed, current at 0.001 s.

The existing software record supplies a state-space model with state order angle, speed, current; matrix A has rows [0, 1, 0]; [0, -2.477876, 5.929204]; [0, -0.67, -10]; matrix B has rows [0]; [0]; [10]; matrix C has rows [1, 0, 0]; [0, 1, 0]; [0, 0, 1]; and matrix D has rows [0]; [0]; [0]. The input channels are armature voltage, the output channels are motor position, speed, current, and the initial state is 0, 0, 0.

The accompanying existing software record uses a 0.001 s sample interval for 8 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 123. Realize a quarter-car transfer function in real modal canonical form

### Control Problem Description

This is a vehicle suspension apparatus made from body and wheel masses, springs, and dampers. The control input is realization input, and the measured outputs are quarter-car output and modal states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in quarter-car output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after realization input changes, quarter-car output begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from realization input actuation to the visible quarter-car output response contains at least three successive storage or integration processes. When the input is removed, the quarter-car output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in realization input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in realization input can drive a distinguishable change in the key output quarter-car output; realization input and the recorded readings quarter-car output and modal states share one clock, so all relevant motion can be reconstructed from these synchronized records. One realization input action affects the recorded readings quarter-car output and modal states; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for quarter-car output.


### Profile Measurement Response (Natural Language)

Use G=(2s+4)/[s^2(s^2+2s+4)] and realize the rigid-body and flexible modes separately; sample impulse response at 0.005 s.

The declared software model is a transfer function from realization input in normalized input units to quarter-car output and modal states in normalized output units. Its numerator coefficients are 2, 4; its denominator coefficients are 1, 2, 4, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 124. Transform a thermal system from control canonical form to modal form

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is heat input, and the measured outputs are thermal modal states and output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in thermal modal states starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after heat input changes, thermal modal states begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from heat input actuation to the visible thermal modal states response contains one or two dominant storage or integration processes. When the input returns to baseline, the thermal modal states response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heat input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in heat input can drive a distinguishable change in the key output thermal modal states; heat input and the recorded readings thermal modal states and output share one clock, so all relevant motion can be reconstructed from these synchronized records. One heat input action affects the recorded readings thermal modal states and output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for thermal modal states.


### Profile Measurement Response (Natural Language)

Use Ac=[[-7,-12],[1,0]], Bc=[1,0], Cc=[1,2] and T=[[4,-3],[-1,1]]; compare transformed trajectories.

The declared software model is a transfer function from heat input in normalized input units to thermal modal states and output in normalized output units. Its numerator coefficients are 1, 2; its denominator coefficients are 1, 7, 12; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 125. Recover poles, zeros, and transfer function from the Piper Dakota state model

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is elevator input, and the measured outputs are pitch attitude and modal states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pitch attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after elevator input changes, pitch attitude begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from elevator input actuation to the visible pitch attitude response contains one or two dominant storage or integration processes. When the input returns to baseline, the pitch attitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in elevator input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in elevator input can drive a distinguishable change in the key output pitch attitude; elevator input and the recorded readings pitch attitude and modal states share one clock, so all relevant motion can be reconstructed from these synchronized records. One elevator input action affects the recorded readings pitch attitude and modal states; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pitch attitude.


### Profile Measurement Response (Natural Language)

Use the supplied four-state Piper Dakota matrices; excite elevator by +/-1 degree pulses and compute poles, zeros, and pitch response.

The declared software model is a transfer function from elevator input in deg to pitch attitude and modal states in deg. Its numerator coefficients are 160, 512, 280; its denominator coefficients are 1, 5.03, 40.21, 1.5, 2.4; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 40 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 126. Test controllability and observability and interpret pole-zero cancellation physically

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is bounded state-space test excitation, and the measured outputs are state trajectories and declared output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state trajectories starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded state-space test excitation changes, state trajectories begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded state-space test excitation actuation to the visible state trajectories response contains one or two dominant storage or integration processes. When the input returns to baseline, the state trajectories response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded state-space test excitation produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Bounded state-space test excitation can drive the currently visible state trajectories and declared output response, but a pole-zero-cancelled mode is absent from the synchronized records and cannot be excited, so the records cannot reconstruct all relevant motion. One bounded state-space test excitation action affects the recorded readings state trajectories and declared output response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state trajectories.


### Profile Measurement Response (Natural Language)

Use A=diag(-3,-4), B=[1,1]^T, C=[0,1], D=0, so the -3 mode is controllable but unobservable; compare internal state and reduced transfer output.

The existing software record supplies a state-space model with state order hidden_mode, visible_mode; matrix A has rows [-3, 0]; [0, -4]; matrix B has rows [1]; [1]; matrix C has rows [0, 1]; and matrix D has rows [0]. The input channels are bounded state-space test excitation, the output channels are state trajectories and declared output response, and the initial state is 1, 0.

The accompanying existing software record uses a 0.01 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 127. Place repeated closed-loop poles for an undamped pendulum by full-state feedback

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is pivot torque, and the measured outputs are pendulum angle and rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after pivot torque changes, pendulum angle begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from pivot torque actuation to the visible pendulum angle response contains one or two dominant storage or integration processes. When the input is removed, the pendulum angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in pivot torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in pivot torque can drive a distinguishable change in the key output pendulum angle; pivot torque and the recorded readings pendulum angle and rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One pivot torque action affects the recorded readings pendulum angle and rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pendulum angle.


### Profile Measurement Response (Natural Language)

Use omega0=1 rad/s and feedback K=[3,4]; release from angle 0.1 rad and compare with open-loop pendulum.

The existing software record supplies a state-space model with state order angle, rate; matrix A has rows [0, 1]; [-4, -4]; matrix B has rows [0]; [1]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are pivot torque, the output channels are pendulum angle and rate channel 1, pendulum angle and rate channel 2, and the initial state is 0.1, 0.

The accompanying existing software record uses a 0.005 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 128. Apply Ackermann pole placement and diagnose gain growth near a weakly controllable zero

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is bounded state-feedback command, and the measured outputs are closed-loop state response and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop state response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded state-feedback command changes, closed-loop state response begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded state-feedback command actuation to the visible closed-loop state response response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop state response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded state-feedback command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in bounded state-feedback command can drive a distinguishable change in the key output closed-loop state response; bounded state-feedback command and the recorded readings closed-loop state response and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded state-feedback command action affects the recorded readings closed-loop state response and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use target s^2+2s+4. Compare z0=2 giving K=[-3.8,0.6] with z0=-2.99 giving K=[2052.5,-688.1].

The declared software model is a transfer function from bounded state-feedback command in normalized input units to closed-loop state response and control effort in normalized output units. Its numerator coefficients are 4; its denominator coefficients are 1, 2, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 129. Introduce a step reference robustly into a Type 1 DC-motor loop

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is state feedback voltage, and the measured outputs are motor position and speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after state feedback voltage changes, motor position begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from state feedback voltage actuation to the visible motor position response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in state feedback voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in state feedback voltage can drive a distinguishable change in the key output motor position; state feedback voltage and the recorded readings motor position and speed share one clock, so all relevant motion can be reconstructed from these synchronized records. One state feedback voltage action affects the recorded readings motor position and speed; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.


### Profile Measurement Response (Natural Language)

Use motor A=[[0,1],[0,-1]], B=[0,1], K=[8,3], and reference gain Nbar=8; apply +/-1 position steps.

The declared software model is a transfer function from state feedback voltage in normalized input units to motor position and speed in normalized output units. Its numerator coefficients are 8; its denominator coefficients are 1, 4, 8; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 130. Select dominant second-order poles for a third-order drone model

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is control moment, and the measured outputs are drone attitude response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in drone attitude response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after control moment changes, drone attitude response begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from control moment actuation to the visible drone attitude response response contains at least three successive storage or integration processes. When the input is removed, the drone attitude response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in control moment produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in control moment can drive a distinguishable change in the key output drone attitude response; control moment and the recorded readings drone attitude response share one clock, so all relevant motion can be reconstructed from these synchronized records. One control moment action affects the recorded readings drone attitude response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for drone attitude response.


### Profile Measurement Response (Natural Language)

Use the three-state drone model, K=[14,56,96], and Nbar=96; apply unit altitude steps at 0.005 s for 10 s.

The declared software model is a transfer function from control moment in normalized input units to drone attitude response in normalized output units. Its numerator coefficients are 96; its denominator coefficients are 1, 16, 56, 96; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 131. Balance tracking error and effort with LQR for the drone

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is optimal control moment, and the measured outputs are drone state and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in drone state starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after optimal control moment changes, drone state begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from optimal control moment actuation to the visible drone state response contains at least three successive storage or integration processes. When the input is removed, the drone state response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in optimal control moment produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in optimal control moment can drive a distinguishable change in the key output drone state; optimal control moment and the recorded readings drone state and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One optimal control moment action affects the recorded readings drone state and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for drone state.


### Profile Measurement Response (Natural Language)

Use the drone model with Q=100 C^T C, R=1 and LQR K=[2.8728,9.8720,10]; compare rho=10,100,1000.

The declared software model is a transfer function from optimal control moment in normalized input units to drone state and control effort in normalized output units. Its numerator coefficients are 10; its denominator coefficients are 1, 4.8728, 9.872, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 132. Design and validate a full-order pendulum state estimator

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is known pivot torque, and the measured outputs are measured angle and estimated state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after known pivot torque changes, measured angle begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from known pivot torque actuation to the visible measured angle response contains one or two dominant storage or integration processes. When the input is removed, the measured angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in known pivot torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in known pivot torque can drive a distinguishable change in the key output measured angle; known pivot torque and the recorded readings measured angle and estimated state share one clock, so all relevant motion can be reconstructed from these synchronized records. One known pivot torque action affects the recorded readings measured angle and estimated state; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for measured angle.


### Profile Measurement Response (Natural Language)

Use omega0=1 and full-order estimator L=[20,99]; initialize the estimate at [0.2,-0.1] while the plant starts at zero.

The existing software record supplies a state-space model with state order angle_error, rate_error; matrix A has rows [-20, 1]; [-100, 0]; matrix B has rows [0]; [0]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are known pivot torque, the output channels are measured angle and estimated state channel 1, measured angle and estimated state channel 2, and the initial state is 0.2, -0.1.

The accompanying existing software record uses a 0.001 s sample interval for 2 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 133. Design a reduced-order pendulum estimator without differentiating the measurement

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is known pivot torque, and the measured outputs are measured angle and estimated rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after known pivot torque changes, measured angle begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from known pivot torque actuation to the visible measured angle response contains one or two dominant storage or integration processes. When the input is removed, the measured angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in known pivot torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in known pivot torque can drive a distinguishable change in the key output measured angle; known pivot torque and the recorded readings measured angle and estimated rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One known pivot torque action affects the recorded readings measured angle and estimated rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for measured angle.


### Profile Measurement Response (Natural Language)

Use omega0=1 and reduced observer gain L=10; estimate rate from measured angle without numerical differentiation.

The declared software model is a transfer function from known pivot torque in normalized input units to measured angle and estimated rate in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 10; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 5 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 134. Select estimator poles from a symmetric root locus under process/sensor noise tradeoffs

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is known plant input, and the measured outputs are state estimate and innovation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state estimate starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after known plant input changes, state estimate begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from known plant input actuation to the visible state estimate response contains one or two dominant storage or integration processes. When the input is removed, the state estimate response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in known plant input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in known plant input can drive a distinguishable change in the key output state estimate; known plant input and the recorded readings state estimate and innovation share one clock, so all relevant motion can be reconstructed from these synchronized records. One known plant input action affects the recorded readings state estimate and innovation; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state estimate.


### Profile Measurement Response (Natural Language)

Use omega0=1, noise ratio q=365, and estimator poles -3+/-j3.18; compare q/10, q, 10q with identical noise seeds.

The declared software model is a transfer function from known plant input in normalized input units to state estimate and innovation in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 6, 19.1124; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 135. Combine controller and estimator by the separation principle and form a DC-servo compensator

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is dynamic compensator voltage, and the measured outputs are servo output, estimated state, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after dynamic compensator voltage changes, servo output begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from dynamic compensator voltage actuation to the visible servo output response contains at least three successive storage or integration processes. When the input is removed, the servo output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in dynamic compensator voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in dynamic compensator voltage can drive a distinguishable change in the key output servo output; dynamic compensator voltage and the recorded readings servo output, estimated state, and control effort share one clock, so all relevant motion can be reconstructed from these synchronized records. One dynamic compensator voltage action affects the recorded readings servo output, estimated state, and control effort; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo output.


### Profile Measurement Response (Natural Language)

Use servo G=10/[s(s+2)(s+8)], K=[-46.4,5.76,-0.65], L=[0.56,1.42,16]; sweep loop gain only within a stopped simulation.

The declared software model is a transfer function from dynamic compensator voltage in normalized input units to servo output in normalized output units. Its numerator coefficients are 10; its denominator coefficients are 1, 10, 16, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 136. Assign controller feedforward zeros to increase a servomechanism velocity constant

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is two-input or equivalent lag-lead command, and the measured outputs are servo position, tracking error, and slow tail, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after two-input or equivalent lag-lead command changes, servo position begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from two-input or equivalent lag-lead command actuation to the visible servo position response contains one or two dominant storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in two-input or equivalent lag-lead command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in two-input or equivalent lag-lead command can drive a distinguishable change in the key output servo position; two-input or equivalent lag-lead command and the recorded readings servo position, tracking error, and slow tail share one clock, so all relevant motion can be reconstructed from these synchronized records. One two-input or equivalent lag-lead command action affects the recorded readings servo position, tracking error, and slow tail; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s+1)], K=[8,3], estimator pole -0.1, controller zero -0.096, and verify Kv=10 with a unit ramp.

The declared software model is a transfer function from two-input or equivalent lag-lead command in normalized input units to servo position in normalized output units. Its numerator coefficients are 8.32, 8.32, 0.8; its denominator coefficients are 1, 4.0996, 0.08; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 200 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 137. Add integral state feedback for robust motor-speed tracking and constant-disturbance rejection

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is motor voltage, and the measured outputs are motor speed and integral error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after motor voltage changes, motor speed begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from motor voltage actuation to the visible motor speed response contains one or two dominant storage or integration processes. When the input returns to baseline, the motor speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in motor voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in motor voltage can drive a distinguishable change in the key output motor speed; motor voltage and the recorded readings motor speed and integral error share one clock, so all relevant motion can be reconstructed from these synchronized records. One motor voltage action affects the recorded readings motor speed and integral error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.


### Profile Measurement Response (Natural Language)

Use motor xdot=-3x+u+w, integral state xI_dot=y-r, gains [25,7], and observer L=7; test reference and constant load separately.

The declared software model is a transfer function from motor voltage in normalized input units to motor speed and integral error in normalized output units. Its numerator coefficients are 25; its denominator coefficients are 1, 10, 25; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 138. Embed a sinusoidal internal model for disk-drive tracking and rejection

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is voice-coil force, and the measured outputs are disk-head position and sinusoidal error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in disk-head position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after voice-coil force changes, disk-head position begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from voice-coil force actuation to the visible disk-head position response contains one or two dominant storage or integration processes. When the input is removed, the disk-head position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in voice-coil force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in voice-coil force can drive a distinguishable change in the key output disk-head position; voice-coil force and the recorded readings disk-head position and sinusoidal error share one clock, so all relevant motion can be reconstructed from these synchronized records. One voice-coil force action affects the recorded readings disk-head position and sinusoidal error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for disk-head position.


### Profile Measurement Response (Natural Language)

Use omega0=1 and controller gain vector [2.0718,16.3923,13.9282,4.4641]; track and reject sinusoids at 0.9,1.0,1.1 rad/s.

The declared software model is a transfer function from voice-coil force in normalized input units to disk-head position and sinusoidal error in normalized output units. Its numerator coefficients are 100; its denominator coefficients are 1, 8, 32, 80, 100; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 139. Recover LQR loop shape with an LTR estimator while quantifying sensor-noise actuator activity

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is body torque under prescribed sensor noise, and the measured outputs are attitude response and body-torque activity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after body torque under prescribed sensor noise changes, attitude response begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from body torque under prescribed sensor noise actuation to the visible attitude response response contains one or two dominant storage or integration processes. When the input is removed, the attitude response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body torque under prescribed sensor noise produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in body torque under prescribed sensor noise can drive a distinguishable change in the key output attitude response; body torque under prescribed sensor noise and the recorded readings attitude response and body-torque activity share one clock, so all relevant motion can be reconstructed from these synchronized records. One body torque under prescribed sensor noise action affects the recorded readings attitude response and body-torque activity; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use satellite LQR K=[1,1.414] and LTR estimators q=1,10,100; inject identical unit sensor noise and record control RMS.

The declared software model is a transfer function from body torque under prescribed sensor noise in normalized input units to attitude response and body-torque activity in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 1.414, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 140. Control a delayed heat exchanger with a Smith predictor and state-space pole placement

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is steam command through Smith predictor, and the measured outputs are delayed heat-exchanger temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in delayed heat-exchanger temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after steam command through Smith predictor changes, a visible quiet interval separates the command from the first delayed heat-exchanger temperature change, which is first distinguishable 5 s after the input change. The path from steam command through Smith predictor actuation to the visible delayed heat-exchanger temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the delayed heat-exchanger temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steam command through Smith predictor produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in steam command through Smith predictor can drive a distinguishable change in the key output delayed heat-exchanger temperature; steam command through Smith predictor and the recorded readings delayed heat-exchanger temperature share one clock, so all relevant motion can be reconstructed from these synchronized records. One steam command through Smith predictor action affects the recorded readings delayed heat-exchanger temperature; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use G0=1/[(10s+1)(60s+1)] with 5 s delay, K=[5.2,-0.17], L=[0.18,4.2], and Nbar=1.2055; perturb delay to 4.5 and 5.5 s.

The declared software model is a transfer function from steam command through Smith predictor in normalized input units to delayed heat-exchanger temperature in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 600, 70, 1; and its input delay is 5 s.

The accompanying existing software record uses a 0.05 s sample interval for 400 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 141. Digitize a DC-motor lead controller with Tustin's bilinear approximation

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is digital motor voltage, and the measured outputs are sampled motor position and error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.025 s sample interval; after digital motor voltage changes, sampled motor position begins within one sample, with its first distinguishable change recorded 0.025 s after the input change and without a separate silent interval. The path from digital motor voltage actuation to the visible sampled motor position response contains one or two dominant storage or integration processes. When the input is removed, the sampled motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital motor voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital motor voltage can drive a distinguishable change in the key output sampled motor position; digital motor voltage and the recorded readings sampled motor position and error share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital motor voltage action affects the recorded readings sampled motor position and error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled motor position.


### Profile Measurement Response (Natural Language)

Use continuous lead 10(0.5s+1)/(0.1s+1), T=0.025 s, and Tustin coefficients u[k]=0.7778u[k-1]+45.56e[k]-43.33e[k-1].

The declared software model is a transfer function from digital motor voltage in normalized error units to sampled motor position and error in normalized control units. Its numerator coefficients are 45.56, -43.33; its denominator coefficients are 1, -0.7778; and its input delay is 0 s.

The accompanying existing software record uses a 0.025 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 142. Digitize the same lead controller with the zero-order-hold approximation

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is held motor voltage, and the measured outputs are sampled motor position and error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled motor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.025 s sample interval; after held motor voltage changes, sampled motor position begins within one sample, with its first distinguishable change recorded 0.025 s after the input change and without a separate silent interval. The path from held motor voltage actuation to the visible sampled motor position response contains one or two dominant storage or integration processes. When the input is removed, the sampled motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in held motor voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in held motor voltage can drive a distinguishable change in the key output sampled motor position; held motor voltage and the recorded readings sampled motor position and error share one clock, so all relevant motion can be reconstructed from these synchronized records. One held motor voltage action affects the recorded readings sampled motor position and error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled motor position.


### Profile Measurement Response (Natural Language)

Use the same continuous lead and T=0.025 s with ZOH recursion u[k]=0.7788u[k-1]+50e[k]-47.79e[k-1].

The declared software model is a transfer function from held motor voltage in normalized error units to sampled motor position and error in normalized control units. Its numerator coefficients are 50, -47.79; its denominator coefficients are 1, -0.7788; and its input delay is 0 s.

The accompanying existing software record uses a 0.025 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 143. Design a space-station attitude controller with matched pole-zero emulation

### Control Problem Description

This is a rigid space-station attitude system whose digital controller preserves a continuous design through matched pole-zero emulation. The control input is digital body torque, and the measured outputs are space station attitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in space station attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 1 s sample interval; after digital body torque changes, space station attitude begins within one sample, with its first distinguishable change recorded 1 s after the input change and without a separate silent interval. The path from digital body torque actuation to the visible space station attitude response contains one or two dominant storage or integration processes. When the input is removed, the space station attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital body torque can drive a distinguishable change in the key output space station attitude; digital body torque and the recorded readings space station attitude share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital body torque action affects the recorded readings space station attitude; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for space station attitude.


### Profile Measurement Response (Natural Language)

Use space-station G=1/s^2, continuous lead 0.81(s+0.2)/(s+2), MPZ T=1 s controller 0.389(z-0.82)/(z-0.135), then repeat at T=0.5 s.

The declared software model is a transfer function from digital body torque in rad to space station attitude in normalized torque units. Its numerator coefficients are 0.389, -0.319; its denominator coefficients are 1, -0.135; and its input delay is 0 s.

The accompanying existing software record uses a 1 s sample interval for 80 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 144. Compare continuous and sampled root loci for a first-order plant

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is held proportional command, and the measured outputs are sampled first-order output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled first-order output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after held proportional command changes, sampled first-order output begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from held proportional command actuation to the visible sampled first-order output response contains one or two dominant storage or integration processes. When the input returns to baseline, the sampled first-order output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in held proportional command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in held proportional command can drive a distinguishable change in the key output sampled first-order output; held proportional command and the recorded readings sampled first-order output share one clock, so all relevant motion can be reconstructed from these synchronized records. One held proportional command action affects the recorded readings sampled first-order output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled first-order output.


### Profile Measurement Response (Natural Language)

Use a=1 s^-1, T=0.1 s, alpha=exp(-0.1), and sweep proportional K across the exact sampled stability limit.

The declared software model is a transfer function from held proportional command in normalized input units to sampled first-order output in normalized output units. Its numerator coefficients are 0, 0.0951626; its denominator coefficients are 1, -0.904837; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 145. Design the space-station controller directly in the z-plane

### Control Problem Description

This is a rigid space-station attitude system whose controller dynamics are designed directly in the discrete domain. The control input is digital body torque, and the measured outputs are space station attitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in space station attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 1 s sample interval; after digital body torque changes, space station attitude begins within one sample, with its first distinguishable change recorded 1 s after the input change and without a separate silent interval. The path from digital body torque actuation to the visible space station attitude response contains one or two dominant storage or integration processes. When the input is removed, the space station attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital body torque can drive a distinguishable change in the key output space station attitude; digital body torque and the recorded readings space station attitude share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital body torque action affects the recorded readings space station attitude; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for space station attitude.


### Profile Measurement Response (Natural Language)

Use exact ZOH Gd=0.5(z+1)/(z-1)^2 at T=1 s and direct controller 0.374(z-0.85)/z.

The declared software model is a transfer function from digital body torque in rad to space station attitude in normalized torque units. Its numerator coefficients are 0.374, -0.3179; its denominator coefficients are 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 1 s sample interval for 80 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 146. Compare continuous, emulated, and direct-discrete damping and step response

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is continuous or digital command, and the measured outputs are continuous and sampled step responses, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in continuous starts in its final direction rather than moving the opposite way first. The synchronized record has a 1 s sample interval; after continuous or digital command changes, continuous begins within one sample, with its first distinguishable change recorded 1 s after the input change and without a separate silent interval. The path from continuous or digital command actuation to the visible continuous response contains one or two dominant storage or integration processes. When the input is removed, the continuous response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in continuous or digital command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in continuous or digital command can drive a distinguishable change in the key output continuous; continuous or digital command and the recorded readings continuous and sampled step responses share one clock, so all relevant motion can be reconstructed from these synchronized records. One continuous or digital command action affects the recorded readings continuous and sampled step responses; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for continuous.


### Profile Measurement Response (Natural Language)

At T=1 s compare continuous lead, MPZ 0.389(z-0.82)/(z-0.135), and direct 0.374(z-0.85)/z on the same exact ZOH plant.

The declared software model is a transfer function from continuous or digital command in rad to continuous and sampled step responses in normalized torque units. Its numerator coefficients are 0.374, -0.3179; its denominator coefficients are 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 1 s sample interval for 80 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 147. Recover a filter difference equation, pole damping, and stability from its z transfer function

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is discrete filter input, and the measured outputs are filter output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in filter output starts in its final direction rather than moving the opposite way first. The synchronized record has a 1 s sample interval; after discrete filter input changes, filter output begins within one sample, with its first distinguishable change recorded 1 s after the input change and without a separate silent interval. The path from discrete filter input actuation to the visible filter output response contains one or two dominant storage or integration processes. When the input returns to baseline, the filter output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in discrete filter input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in discrete filter input can drive a distinguishable change in the key output filter output; discrete filter input and the recorded readings filter output share one clock, so all relevant motion can be reconstructed from these synchronized records. One discrete filter input action affects the recorded readings filter output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for filter output.


### Profile Measurement Response (Natural Language)

Use H(z)=(1+0.5z^-1)/[(1-0.5z^-1)(1+z^-1/3)] at 1 Hz and excite impulse, step, and alternating inputs.

The declared software model is a transfer function from discrete filter input in normalized input units to filter output in normalized output units. Its numerator coefficients are 1, 0.5; its denominator coefficients are 1, -0.1666667, -0.1666667; and its input delay is 0 s.

The accompanying existing software record uses a 1 s sample interval for 40 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 148. Solve a forced second-order difference equation by the z-transform

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is ramp sequence input, and the measured outputs are discrete sequence output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in discrete sequence output starts in its final direction rather than moving the opposite way first. The synchronized record has a 1 s sample interval; after ramp sequence input changes, discrete sequence output begins within one sample, with its first distinguishable change recorded 1 s after the input change and without a separate silent interval. The path from ramp sequence input actuation to the visible discrete sequence output response contains one or two dominant storage or integration processes. When the input returns to baseline, the discrete sequence output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in ramp sequence input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in ramp sequence input can drive a distinguishable change in the key output discrete sequence output; ramp sequence input and the recorded readings discrete sequence output share one clock, so all relevant motion can be reconstructed from these synchronized records. One ramp sequence input action affects the recorded readings discrete sequence output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for discrete sequence output.


### Profile Measurement Response (Natural Language)

Use y[k]-3y[k-1]+2y[k-2]=2u[k-1]-2u[k-2], u[k]=k, and zero prehistory for k=0..15.

The declared software model is a transfer function from ramp sequence input in normalized input units to discrete sequence output in normalized output units. Its numerator coefficients are 0, 2; its denominator coefficients are 1, -2; and its input delay is 0 s.

The accompanying existing software record uses a 1 s sample interval for 15 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 149. Prove and use the mapping properties between the s-plane and z-plane

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is prescribed modal mapping test, and the measured outputs are continuous and sampled free-response modes, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in continuous starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after prescribed modal mapping test changes, continuous begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from prescribed modal mapping test actuation to the visible continuous response contains one or two dominant storage or integration processes. When the input returns to baseline, the continuous response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed modal mapping test produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed modal mapping test can drive a distinguishable change in the key output continuous; prescribed modal mapping test and the recorded readings continuous and sampled free-response modes share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed modal mapping test action affects the recorded readings continuous and sampled free-response modes; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for continuous.


### Profile Measurement Response (Natural Language)

With T=0.1 s map s=-1+/-j2 and compare s=-1+/-j(2+2pi/T); verify identical z poles and aliasing.

The declared software model is a transfer function from prescribed modal mapping test in normalized input units to continuous and sampled free-response modes in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, -1.773602, 0.818731; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 150. Map a continuous lag compensator to a 20 Hz digital implementation

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is digital lag command, and the measured outputs are regulated output and digital error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after digital lag command changes, regulated output begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from digital lag command actuation to the visible regulated output response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in digital lag command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital lag command can drive a distinguishable change in the key output regulated output; digital lag command and the recorded readings regulated output and digital error share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital lag command action affects the recorded readings regulated output and digital error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.


### Profile Measurement Response (Natural Language)

Use lag (0.8s+1)/(50s+1), fs=20 Hz, and MPZ recursion with zero 0.93941, pole 0.99900, gain 0.01650.

The declared software model is a transfer function from digital lag command in normalized error units to regulated output and digital error in normalized control units. Its numerator coefficients are 0.0165, -0.0155; its denominator coefficients are 1, -0.999; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 151. Compare Tustin and matched pole-zero digitizations of a lead network

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is sampled error, and the measured outputs are lead network magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lead network magnitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.25 s sample interval; after sampled error changes, lead network magnitude begins within one sample, with its first distinguishable change recorded 0.25 s after the input change and without a separate silent interval. The path from sampled error actuation to the visible lead network magnitude response contains one or two dominant storage or integration processes. When the input returns to baseline, the lead network magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sampled error produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sampled error can drive a distinguishable change in the key output lead network magnitude; sampled error and the recorded readings lead network magnitude and phase share one clock, so all relevant motion can be reconstructed from these synchronized records. One sampled error action affects the recorded readings lead network magnitude and phase; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lead network magnitude.


### Profile Measurement Response (Natural Language)

Digitize H=(s+1)/(s+10.1) at T=0.25 s by Tustin and MPZ; compare phase at 3 rad/s.

The declared software model is a transfer function from sampled error in normalized input units to lead network magnitude and phase in normalized output units. Its numerator coefficients are 0.49724, -0.38675; its denominator coefficients are 1, 0.11602; and its input delay is 0 s.

The accompanying existing software record uses a 0.25 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 152. Compare Tustin and matched pole-zero digitizations of a lag network

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is sampled error, and the measured outputs are lag network magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lag network magnitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.25 s sample interval; after sampled error changes, lag network magnitude begins within one sample, with its first distinguishable change recorded 0.25 s after the input change and without a separate silent interval. The path from sampled error actuation to the visible lag network magnitude response contains one or two dominant storage or integration processes. When the input returns to baseline, the lag network magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sampled error produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sampled error can drive a distinguishable change in the key output lag network magnitude; sampled error and the recorded readings lag network magnitude and phase share one clock, so all relevant motion can be reconstructed from these synchronized records. One sampled error action affects the recorded readings lag network magnitude and phase; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lag network magnitude.


### Profile Measurement Response (Natural Language)

Digitize H=(10s+1)/(100s+1) at T=0.25 s by Tustin and MPZ; evaluate at 3 rad/s.

The declared software model is a transfer function from sampled error in normalized input units to lag network magnitude and phase in normalized output units. Its numerator coefficients are 0.101124, -0.098627; its denominator coefficients are 1, -0.997503; and its input delay is 0 s.

The accompanying existing software record uses a 0.25 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 153. Digitize a PID at three sample periods and assess transient degradation

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is digital PID command, and the measured outputs are sampled step response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled step response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after digital PID command changes, sampled step response begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from digital PID command actuation to the visible sampled step response response contains one or two dominant storage or integration processes. When the input is removed, the sampled step response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital PID command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital PID command can drive a distinguishable change in the key output sampled step response; digital PID command and the recorded readings sampled step response share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital PID command action affects the recorded readings sampled step response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled step response.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s+1)] and PID K=15.2,Td=0.3816 s,Ti=0.95 s; discretize at T=1,0.1,0.01 s and record output plus control.

The declared software model is a transfer function from digital PID command in normalized error units to sampled step response in normalized control units. Its numerator coefficients are 74.003, -130.406, 58.003; its denominator coefficients are 1, -1; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 154. Determine the sampled-data stability-gain range of a plant with an unstable mode

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is held proportional command, and the measured outputs are sampled plant output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled plant output starts in its final direction rather than moving the opposite way first. The synchronized record has a 1 s sample interval; after held proportional command changes, sampled plant output begins within one sample, with its first distinguishable change recorded 1 s after the input change and without a separate silent interval. The path from held proportional command actuation to the visible sampled plant output response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in sampled plant output keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in held proportional command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in held proportional command can drive a distinguishable change in the key output sampled plant output; held proportional command and the recorded readings sampled plant output share one clock, so all relevant motion can be reconstructed from these synchronized records. One held proportional command action affects the recorded readings sampled plant output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled plant output.


### Profile Measurement Response (Natural Language)

Use the exact T=1 s ZOH model Gd=(7.96703z^2+1.33509z-0.324537)/(z^3-3.57119z^2+1.000162z-0.0000454) and scan K>0.

The declared software model is a transfer function from held proportional command in normalized input units to sampled plant output in normalized output units. Its numerator coefficients are 7.96703, 1.33509, -0.324537; its denominator coefficients are 1, -3.57119, 1.000162, -4.54e-05; and its input delay is 0 s.

The accompanying existing software record uses a 1 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 155. Design discrete proportional-plus-velocity satellite attitude feedback

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is digital torque, and the measured outputs are satellite attitude and sampled rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after digital torque changes, satellite attitude begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from digital torque actuation to the visible satellite attitude response contains one or two dominant storage or integration processes. When the input is removed, the satellite attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital torque can drive a distinguishable change in the key output satellite attitude; digital torque and the recorded readings satellite attitude and sampled rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital torque action affects the recorded readings satellite attitude and sampled rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for satellite attitude.


### Profile Measurement Response (Natural Language)

Use T=0.1 s exact double-integrator model and state feedback Kp=1.8097,Kv=1.9032 targeting z=exp((-1+/-j1)T).

The existing software record supplies a state-space model with state order angle, rate; matrix A has rows [0.9909515, 0.0904841]; [-0.18097, 0.8096825]; matrix B has rows [0.0090485]; [0.18097]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are digital torque, the output channels are satellite attitude and sampled rate channel 1, satellite attitude and sampled rate channel 2, and the initial state is 0, 0.

The accompanying existing software record uses a 0.1 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 156. Linearize and digitally stabilize a magnetic-levitation ball subject to sensor/current limits

### Control Problem Description

This is a magnetic-levitation apparatus in which an electromagnet supports a steel ball while a sensor measures the air gap. The control input is electromagnet current, and the measured outputs are ball displacement and current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ball displacement starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after electromagnet current changes, ball displacement begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from electromagnet current actuation to the visible ball displacement response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in ball displacement keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in electromagnet current produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in electromagnet current can drive a distinguishable change in the key output ball displacement; electromagnet current and the recorded readings ball displacement and current share one clock, so all relevant motion can be reconstructed from these synchronized records. One electromagnet current action affects the recorded readings ball displacement and current; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use m=0.02 kg,k1=20 N/m,k2=0.4 N/A,T=0.02 s; test state feedback Kx=94 A/m,Kv=2.08 A*s/m from x0=+/-0.25 cm with 1 A current limit.

The existing software record supplies a state-space model with state order position, velocity; matrix A has rows [1.206756, 0.0213603]; [21.360255, 1.206756]; matrix B has rows [0.00413512]; [0.4272051]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are electromagnet current, the output channels are ball displacement and current channel 1, ball displacement and current channel 2, and the initial state is 0.0025, 0.

The accompanying existing software record uses a 0.02 s sample interval for 2 s, starts the primary output at 0, contains input amplitudes -0.25, -0.125, 0.125, 0.25, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 157. Redesign a lead-lag servomechanism directly in the z-plane

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is digital servo voltage, and the measured outputs are servo position and ramp error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0666667 s sample interval; after digital servo voltage changes, servo position begins within one sample, with its first distinguishable change recorded 0.0666667 s after the input change and without a separate silent interval. The path from digital servo voltage actuation to the visible servo position response contains at least three successive storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital servo voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital servo voltage can drive a distinguishable change in the key output servo position; digital servo voltage and the recorded readings servo position and ramp error share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital servo voltage action affects the recorded readings servo position and ramp error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.


### Profile Measurement Response (Natural Language)

Use G=10/[s(s+1)(s+10)], fs=15 Hz and its exact ZOH coefficients; design directly for Mp<=16%,tr<=0.4 s,Kv_d>1.333.

The declared software model is a transfer function from digital servo voltage in normalized input units to servo position and ramp error in normalized output units. Its numerator coefficients are 0, 0.00041424, 0.0013906, 0.00028724; its denominator coefficients are 1, -2.4489241, 1.92922941, -0.4803053; and its input delay is 0 s.

The accompanying existing software record uses a 0.0666667 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 158. Design an antenna-servo controller by emulation and direct z-plane root locus

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is digital motor torque, and the measured outputs are antenna angle, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in antenna angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 10 s sample interval; after digital motor torque changes, antenna angle begins within one sample, with its first distinguishable change recorded 10 s after the input change and without a separate silent interval. The path from digital motor torque actuation to the visible antenna angle response contains one or two dominant storage or integration processes. When the input is removed, the antenna angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital motor torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital motor torque can drive a distinguishable change in the key output antenna angle; digital motor torque and the recorded readings antenna angle share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital motor torque action affects the recorded readings antenna angle; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use antenna J=600000,B=20000 and T=10 s; compare emulation and direct z design on the same exact ZOH plant.

The declared software model is a transfer function from digital motor torque in Nm to antenna angle in rad. Its numerator coefficients are 0, 7.479697e-05, 6.693738e-05; its denominator coefficients are 1, -1.71653131, 0.71653131; and its input delay is 0 s.

The accompanying existing software record uses a 10 s sample interval for 1000 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 159. Design discrete compensation for a two-real-pole plant under rise-time and overshoot limits

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is digital compensated command, and the measured outputs are sampled plant output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled plant output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after digital compensated command changes, sampled plant output begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from digital compensated command actuation to the visible sampled plant output response contains one or two dominant storage or integration processes. When the input returns to baseline, the sampled plant output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in digital compensated command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in digital compensated command can drive a distinguishable change in the key output sampled plant output; digital compensated command and the recorded readings sampled plant output share one clock, so all relevant motion can be reconstructed from these synchronized records. One digital compensated command action affects the recorded readings sampled plant output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled plant output.


### Profile Measurement Response (Natural Language)

Use exact T=0.1 s Gd=(0.00451991z+0.00407643)/(z^2-1.73086805z+0.73344696) and D=6.1882(z-0.27594)/z.

The declared software model is a transfer function from digital compensated command in normalized error units to sampled plant output in normalized control units. Its numerator coefficients are 6.1882, -1.70762; its denominator coefficients are 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 160. Explain the unavoidable one-sample delay in a causal discrete derivative

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is sampled error sequence, and the measured outputs are estimated error-rate response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in estimated error-rate response starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after sampled error sequence changes, a visible quiet interval separates the command from the first estimated error-rate response change, which is first distinguishable 0.1 s after the input change. The path from sampled error sequence actuation to the visible estimated error-rate response response contains one or two dominant storage or integration processes. When the input returns to baseline, the estimated error-rate response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sampled error sequence produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in sampled error sequence can drive a distinguishable change in the key output estimated error-rate response; sampled error sequence and the recorded readings estimated error-rate response share one clock, so all relevant motion can be reconstructed from these synchronized records. One sampled error sequence action affects the recorded readings estimated error-rate response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for estimated error-rate response.


### Profile Measurement Response (Natural Language)

Use backward difference with T=0.1 s and KTd=1, so u[k]=10(e[k]-e[k-1]); compare with the noncausal forward difference offline only.

The declared software model is a transfer function from sampled error sequence in normalized error units to estimated error-rate response in normalized control units. Its numerator coefficients are 10, -10; its denominator coefficients are 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 161. Find pendulum equilibria and classify their small-signal stability

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is pivot torque, and the measured outputs are pendulum angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after pivot torque changes, pendulum angle begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from pivot torque actuation to the visible pendulum angle response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in pendulum angle keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of pivot torque changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in pivot torque can drive a distinguishable change in the key output pendulum angle; pivot torque and the recorded readings pendulum angle and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One pivot torque action affects the recorded readings pendulum angle and angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use g=9.81 m/s^2,l=1 m and test equilibria theta=0 and pi with +/-0.05 rad perturbations for 10 s.

The existing software record supplies a state-space model with state order angle, rate; matrix A has rows [0, 1]; [-9.81, 0]; matrix B has rows [0]; [1]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are pivot torque, the output channels are pendulum angle and angular rate channel 1, pendulum angle and angular rate channel 2, and the initial state is 0.05, 0.

The accompanying existing software record uses a 0.002 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 162. Linearize a magnetic ball levitator from experimentally measured force curves

### Control Problem Description

This is a magnetic-levitation apparatus in which an electromagnet supports a steel ball while a sensor measures the air gap. The control input is electromagnet current perturbation, and the measured outputs are ball displacement, velocity, coil current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ball displacement starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.0002 s sample interval; after electromagnet current perturbation changes, ball displacement begins within one sample, with its first distinguishable change recorded 0.0002 s after the input change and without a separate silent interval. The path from electromagnet current perturbation actuation to the visible ball displacement response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in ball displacement keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of electromagnet current perturbation changes, magnetic force changes with air gap and coil current, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in electromagnet current perturbation can drive a distinguishable change in the key output ball displacement; electromagnet current perturbation and the recorded readings ball displacement, velocity, coil current share one clock, so all relevant motion can be reconstructed from these synchronized records. One electromagnet current perturbation action affects the recorded readings ball displacement, velocity, coil current; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use m=0.0084 kg, equilibrium current 0.6 A, A=[[0,1],[1667,0]], B=[0,47.6]; test +/-10 mA around equilibrium.

The existing software record supplies a state-space model with state order position_perturbation, velocity; matrix A has rows [0, 1]; [1667, 0]; matrix B has rows [0]; [47.6]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are electromagnet current perturbation, the output channels are ball displacement, velocity, and the initial state is 0.0001, 0.

The accompanying existing software record uses a 0.0002 s sample interval for 1 s, starts the primary output at 0, contains input amplitudes -0.01, -0.005, 0.005, 0.01, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 163. Linearize nonlinear square-root water-tank outflow around an operating point

### Control Problem Description

This is a liquid-storage apparatus whose motion is set by inlet flow, outlet flow, and stored volume. The control input is inlet mass flow, and the measured outputs are tank level and outlet flow, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tank level starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after inlet mass flow changes, tank level begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from inlet mass flow actuation to the visible tank level response contains one or two dominant storage or integration processes. When the input returns to baseline, the tank level response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of inlet mass flow reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in inlet mass flow can drive a distinguishable change in the key output tank level; inlet mass flow and the recorded readings tank level and outlet flow share one clock, so all relevant motion can be reconstructed from these synchronized records. One inlet mass flow action affects the recorded readings tank level and outlet flow; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.


### Profile Measurement Response (Natural Language)

Use A=1 m^2,rho=1000 kg/m^3,R=0.5, h0=1 m, pa=0; perturb inflow by +/-10 kg/s and keep h positive.

The declared software model is a transfer function from inlet mass flow in kg/s to tank level and outlet flow in m. Its numerator coefficients are 0.001; its denominator coefficients are 1, 0.09905; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 164. Cancel pendulum gravity by computed-torque nonlinear feedback

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is computed pivot torque, and the measured outputs are pendulum angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after computed pivot torque changes, pendulum angle begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from computed pivot torque actuation to the visible pendulum angle response contains one or two dominant storage or integration processes. When the input is removed, the pendulum angle response retains an offset or keeps drifting rather than returning through its own restoring action. As the size or operating point of computed pivot torque changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in computed pivot torque can drive a distinguishable change in the key output pendulum angle; computed pivot torque and the recorded readings pendulum angle and angular rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One computed pivot torque action affects the recorded readings pendulum angle and angular rate; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pendulum angle.


### Profile Measurement Response (Natural Language)

Use m=l=1,g=9.81 and computed torque Tc=mgl sin(theta)+u with u=-4(theta-r)-4 theta_dot; test commands up to +/-1 rad.

The declared software model is a transfer function from computed pivot torque in rad to pendulum angle and angular rate in rad. Its numerator coefficients are 4; its denominator coefficients are 1, 4, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 165. Cancel a rapid-thermal-processing lamp square law with an inverse nonlinearity

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is commanded lamp voltage, and the measured outputs are lamp voltage and delivered power, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lamp voltage starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after commanded lamp voltage changes, lamp voltage begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from commanded lamp voltage actuation to the visible lamp voltage response contains one or two dominant storage or integration processes. When the input returns to baseline, the lamp voltage response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of commanded lamp voltage reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in commanded lamp voltage can drive a distinguishable change in the key output lamp voltage; commanded lamp voltage and the recorded readings lamp voltage and delivered power share one clock, so all relevant motion can be reconstructed from these synchronized records. One commanded lamp voltage action affects the recorded readings lamp voltage and delivered power; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lamp voltage.


### Profile Measurement Response (Natural Language)

Use lamp law P=V^2, voltage limit 0..10 V, virtual power 0..100 W, inverse V=sqrt(Pcmd), and thermal G=1/(10s+1).

The declared software model is a transfer function from commanded lamp voltage in W to lamp voltage and delivered power in normalized temperature units. Its numerator coefficients are 1; its denominator coefficients are 10, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 166. Predict amplitude-dependent overshoot caused by actuator saturation

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is amplitude-limited command, and the measured outputs are output, error, saturated control, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after amplitude-limited command changes, output begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from amplitude-limited command actuation to the visible output response contains one or two dominant storage or integration processes. When the input is removed, the output response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of amplitude-limited command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in amplitude-limited command can drive a distinguishable change in the key output output; amplitude-limited command and the recorded readings output, error, saturated control share one clock, so all relevant motion can be reconstructed from these synchronized records. One amplitude-limited command action affects the recorded readings output, error, saturated control; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output.


### Profile Measurement Response (Natural Language)

Use G=(s+1)/s^2,K=1,symmetric actuator limit +/-0.4, and step amplitudes 2,4,6,8,10,12.

The declared software model is a transfer function from amplitude-limited command in normalized input units to output in normalized output units. Its numerator coefficients are 1, 1; its denominator coefficients are 1, 1, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 50 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 167. Expose large-signal instability in a conditionally stable saturated loop

### Control Problem Description

This is a conditionally stable feedback loop whose actuator clips large proportional commands at fixed limits. The control input is saturated proportional command, and the measured outputs are regulated output, loop error, and saturated control signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after saturated proportional command changes, regulated output begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from saturated proportional command actuation to the visible regulated output response contains at least three successive storage or integration processes. When the input is removed, the regulated output response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of saturated proportional command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in saturated proportional command can drive a distinguishable change in the key output regulated output; saturated proportional command and the recorded readings regulated output, loop error, and saturated control signal share one clock, so all relevant motion can be reconstructed from these synchronized records. One saturated proportional command action affects the recorded readings regulated output, loop error, and saturated control signal; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.


### Profile Measurement Response (Natural Language)

Use G=(s+1)^2/s^3,K=2, saturation +/-1, and steps 1,2,3,3.5; stop if state bounds are crossed.

The declared software model is a transfer function from saturated proportional command in normalized input units to regulated output in normalized output units. Its numerator coefficients are 2, 4, 2; its denominator coefficients are 1, 2, 4, 2; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 168. Predict a saturation-induced flexible-mode limit cycle and eliminate it with a notch

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is notch-shaped limited command, and the measured outputs are flexible displacement and saturated command, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in flexible displacement starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after notch-shaped limited command changes, flexible displacement begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from notch-shaped limited command actuation to the visible flexible displacement response contains at least three successive storage or integration processes. When the input is removed, the flexible displacement response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of notch-shaped limited command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in notch-shaped limited command can drive a distinguishable change in the key output flexible displacement; notch-shaped limited command and the recorded readings flexible displacement and saturated command share one clock, so all relevant motion can be reconstructed from these synchronized records. One notch-shaped limited command action affects the recorded readings flexible displacement and saturated command; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for flexible displacement.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s^2+0.2s+1)],K=0.5,saturation +/-0.1; compare with notch 123(s^2+0.18s+0.81)/(s+10)^2.

The declared software model is a transfer function from notch-shaped limited command in normalized input units to flexible displacement and saturated command in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 0.2, 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 200 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 169. Add back-calculation antiwindup to a saturated PI-controlled integrator

### Control Problem Description

This is an integrating plant driven by a PI controller, a saturated actuator, and a back-calculation antiwindup path. The control input is saturated PI command, and the measured outputs are integrator output, plant output, actuator command, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in integrator output starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after saturated PI command changes, integrator output begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from saturated PI command actuation to the visible integrator output response contains one or two dominant storage or integration processes. When the input is removed, the integrator output response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of saturated PI command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in saturated PI command can drive a distinguishable change in the key output integrator output; saturated PI command and the recorded readings integrator output, plant output, actuator command share one clock, so all relevant motion can be reconstructed from these synchronized records. One saturated PI command action affects the recorded readings integrator output, plant output, actuator command; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for integrator output.


### Profile Measurement Response (Natural Language)

Use plant 1/s, PI kp=2,ki=4, actuator +/-1, and back-calculation Ka=10; compare a 4-unit step with Ka=0.

The declared software model is a transfer function from saturated PI command in normalized input units to integrator output in normalized output units. Its numerator coefficients are 2, 4; its denominator coefficients are 1, 2, 4; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 170. Derive the describing function of a saturation nonlinearity

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is bounded sinusoidal nonlinearity test, and the measured outputs are nonlinear input and fundamental output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in nonlinear input starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded sinusoidal nonlinearity test changes, nonlinear input begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded sinusoidal nonlinearity test actuation to the visible nonlinear input response contains one or two dominant storage or integration processes. When the input returns to baseline, the nonlinear input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of bounded sinusoidal nonlinearity test reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in bounded sinusoidal nonlinearity test can drive a distinguishable change in the key output nonlinear input; bounded sinusoidal nonlinearity test and the recorded readings nonlinear input and fundamental output share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded sinusoidal nonlinearity test action affects the recorded readings nonlinear input and fundamental output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for nonlinear input.


### Profile Measurement Response (Natural Language)

Use saturation slope k=1,limit N=0.1 and sine amplitudes 0.05,0.1,0.2,0.5,1 at 1 rad/s; extract the first harmonic.

The declared software model is a transfer function from bounded sinusoidal nonlinearity test in normalized input units to nonlinear input and fundamental output in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 171. Derive the describing function of an ideal relay

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is binary relay command, and the measured outputs are relay input and fundamental output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in relay input starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after binary relay command changes, relay input begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from binary relay command actuation to the visible relay input response contains one or two dominant storage or integration processes. When the input returns to baseline, the relay input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of binary relay command reveals a fixed relay switching law, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in binary relay command can drive a distinguishable change in the key output relay input; binary relay command and the recorded readings relay input and fundamental output share one clock, so all relevant motion can be reconstructed from these synchronized records. One binary relay command action affects the recorded readings relay input and fundamental output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for relay input.


### Profile Measurement Response (Natural Language)

Use ideal relay levels +/-1 and sine amplitudes 0.25,0.5,1,2; extract fundamental and odd harmonics.

The declared software model is a transfer function from binary relay command in normalized input units to relay input and fundamental output in normalized output units. Its numerator coefficients are 1.27324; its denominator coefficients are 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 172. Derive the complex describing function of a relay with hysteresis

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is hysteretic relay command, and the measured outputs are hysteresis input and fundamental output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in hysteresis input starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after hysteretic relay command changes, hysteresis input begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from hysteretic relay command actuation to the visible hysteresis input response contains one or two dominant storage or integration processes. When the input returns to baseline, the hysteresis input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of hysteretic relay command reveals fixed hysteresis and relay switching, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in hysteretic relay command can drive a distinguishable change in the key output hysteresis input; hysteretic relay command and the recorded readings hysteresis input and fundamental output share one clock, so all relevant motion can be reconstructed from these synchronized records. One hysteretic relay command action affects the recorded readings hysteresis input and fundamental output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for hysteresis input.


### Profile Measurement Response (Natural Language)

Use relay levels +/-1,hysteresis h=0.1 and sine amplitudes 0.08,0.12,0.24,0.5; preserve relay memory.

The declared software model is a transfer function from hysteretic relay command in normalized input units to hysteresis input and fundamental output in normalized output units. Its numerator coefficients are 5.30516; its denominator coefficients are 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 173. Predict a saturation limit cycle from a Nyquist/describing-function intersection

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is saturated loop command, and the measured outputs are oscillation amplitude and frequency, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in oscillation amplitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after saturated loop command changes, oscillation amplitude begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from saturated loop command actuation to the visible oscillation amplitude response contains at least three successive storage or integration processes. When the input is removed, the oscillation amplitude response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of saturated loop command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in saturated loop command can drive a distinguishable change in the key output oscillation amplitude; saturated loop command and the recorded readings oscillation amplitude and frequency share one clock, so all relevant motion can be reconstructed from these synchronized records. One saturated loop command action affects the recorded readings oscillation amplitude and frequency; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for oscillation amplitude.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s^2+0.2s+1)] with saturation k=1,N=0.1; start near amplitudes 0.3,0.63,0.9 and measure steady oscillation.

The declared software model is a transfer function from saturated loop command in normalized input units to oscillation amplitude and frequency in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 0.2, 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 174. Predict a hysteresis-induced limit cycle from the same construction

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is hysteretic relay command, and the measured outputs are hysteretic oscillation amplitude and frequency, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in hysteretic oscillation amplitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after hysteretic relay command changes, hysteretic oscillation amplitude begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from hysteretic relay command actuation to the visible hysteretic oscillation amplitude response contains at least three successive storage or integration processes. When the input is removed, the hysteretic oscillation amplitude response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of hysteretic relay command reveals fixed hysteresis and relay switching, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in hysteretic relay command can drive a distinguishable change in the key output hysteretic oscillation amplitude; hysteretic relay command and the recorded readings hysteretic oscillation amplitude and frequency share one clock, so all relevant motion can be reconstructed from these synchronized records. One hysteretic relay command action affects the recorded readings hysteretic oscillation amplitude and frequency; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for hysteretic oscillation amplitude.


### Profile Measurement Response (Natural Language)

Use G=1/[s(s+1)], relay N=1,h=0.1; simulate from several initial relay states and measure the limit cycle.

The declared software model is a transfer function from hysteretic relay command in normalized input units to hysteretic oscillation amplitude and frequency in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 1, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 175. Derive bang-bang minimum-time switching and a chatter-reducing PTOS law for a double integrator

### Control Problem Description

This is a low-friction cart moving on a horizontal track, with a bidirectional drive and negligible passive restoring force. The control input is bounded acceleration command, and the measured outputs are position and velocity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after bounded acceleration command changes, position begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from bounded acceleration command actuation to the visible position response contains one or two dominant storage or integration processes. When the input is removed, the position response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of bounded acceleration command reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in bounded acceleration command can drive a distinguishable change in the key output position; bounded acceleration command and the recorded readings position and velocity share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded acceleration command action affects the recorded readings position and velocity; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for position.


### Profile Measurement Response (Natural Language)

Use double integrator, |u|<=1, initial states (1,0),(1,-1),(-1,1); compare bang-bang switching with a smoothed PTOS band.

The declared software model is a transfer function from bounded acceleration command in normalized input units to position and velocity in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 176. Prove parameter-dependent stability of a second-order linear system with a Lyapunov equation

### Control Problem Description

This is a two-state autonomous linear system whose trajectories rotate and decay at rates set by two physical parameters. The control input is prescribed initial-state release, and the measured outputs are state trajectory and decay behavior, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state trajectory starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after prescribed initial-state release changes, state trajectory begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from prescribed initial-state release actuation to the visible state trajectory response contains one or two dominant storage or integration processes. When the input returns to baseline, the state trajectory response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed initial-state release produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in prescribed initial-state release can drive a distinguishable change in the key output state trajectory; prescribed initial-state release and the recorded readings state trajectory and decay behavior share one clock, so all relevant motion can be reconstructed from these synchronized records. One prescribed initial-state release action affects the recorded readings state trajectory and decay behavior; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state trajectory.


### Profile Measurement Response (Natural Language)

Use alpha=1,beta=2, A=[[-1,2],[-2,-1]], Q=I, and initial states on radii 0.5,1,2.

The existing software record supplies a state-space model with state order x1, x2; matrix A has rows [-1, 2]; [-2, -1]; matrix B has rows [0]; [0]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are prescribed initial-state release, the output channels are state trajectory and decay behavior channel 1, state trajectory and decay behavior channel 2, and the initial state is 1, 0.

The accompanying existing software record uses a 0.005 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 177. Construct a direct Lyapunov function for nonlinear position feedback

### Control Problem Description

This is a damped position servo in which displacement error produces a nonlinear restoring action on the moving state. The control input is nonlinear restoring feedback, and the measured outputs are position error, velocity, and state trajectory, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in position error starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after nonlinear restoring feedback changes, position error begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from nonlinear restoring feedback actuation to the visible position error response contains one or two dominant storage or integration processes. When the input returns to baseline, the position error response settles or remains bounded instead of developing self-growing motion. As the size or operating point of nonlinear restoring feedback changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in nonlinear restoring feedback can drive a distinguishable change in the key output position error; nonlinear restoring feedback and the recorded readings position error, velocity, and state trajectory share one clock, so all relevant motion can be reconstructed from these synchronized records. One nonlinear restoring feedback action affects the recorded readings position error, velocity, and state trajectory; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for position error.


### Profile Measurement Response (Natural Language)

Use T=1 and f(e)=e+e^3; simulate initial states e=+/-2,x2=+/-1 and evaluate V=0.5e^2+0.25e^4+0.5x2^2.

The existing software record supplies a state-space model with state order error, velocity; matrix A has rows [0, -1]; [1, -1]; matrix B has rows [0]; [0]; matrix C has rows [1, 0]; [0, 1]; and matrix D has rows [0]; [0]. The input channels are nonlinear restoring feedback, the output channels are position error, velocity, and the initial state is 2, 1.

The accompanying existing software record uses a 0.002 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 178. Bound a signum nonlinearity by a sector

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is bounded signum test signal, and the measured outputs are nonlinearity input and output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in nonlinearity input starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after bounded signum test signal changes, nonlinearity input begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from bounded signum test signal actuation to the visible nonlinearity input response contains one or two dominant storage or integration processes. When the input returns to baseline, the nonlinearity input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of bounded signum test signal reveals a fixed signum law, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in bounded signum test signal can drive a distinguishable change in the key output nonlinearity input; bounded signum test signal and the recorded readings nonlinearity input and output share one clock, so all relevant motion can be reconstructed from these synchronized records. One bounded signum test signal action affects the recorded readings nonlinearity input and output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for nonlinearity input.


### Profile Measurement Response (Natural Language)

Use f(e)=sign(e) over logarithmic amplitudes 1e-3 to 10 and compute the secant slope f(e)/e.

The declared software model is a transfer function from bounded signum test signal in normalized input units to nonlinearity input and output in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 179. Bound actuator saturation by a sector

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is amplitude-limited actuator command, and the measured outputs are saturation input and output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in saturation input starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after amplitude-limited actuator command changes, saturation input begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from amplitude-limited actuator command actuation to the visible saturation input response contains one or two dominant storage or integration processes. When the input returns to baseline, the saturation input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of amplitude-limited actuator command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in amplitude-limited actuator command can drive a distinguishable change in the key output saturation input; amplitude-limited actuator command and the recorded readings saturation input and output share one clock, so all relevant motion can be reconstructed from these synchronized records. One amplitude-limited actuator command action affects the recorded readings saturation input and output; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for saturation input.


### Profile Measurement Response (Natural Language)

Use unit-slope saturation +/-0.1 and amplitudes from 0.01 to 10; verify sector inequalities pointwise.

The declared software model is a transfer function from amplitude-limited actuator command in normalized input units to saturation input and output in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 10 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 180. Certify absolute stability of a saturated loop with the circle criterion

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is sector-bounded actuator command, and the measured outputs are loop input, output, and closed-loop response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in loop input starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after sector-bounded actuator command changes, loop input begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from sector-bounded actuator command actuation to the visible loop input response contains one or two dominant storage or integration processes. When the input returns to baseline, the loop input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of sector-bounded actuator command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in sector-bounded actuator command can drive a distinguishable change in the key output loop input; sector-bounded actuator command and the recorded readings loop input, output, and closed-loop response share one clock, so all relevant motion can be reconstructed from these synchronized records. One sector-bounded actuator command action affects the recorded readings loop input, output, and closed-loop response; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for loop input.


### Profile Measurement Response (Natural Language)

Use linear block G=(s+1)^2/s^3 with unit-slope saturation sector [0,1]; plot Nyquist against the Re(G)=-1 boundary and simulate bounded initial conditions.

The declared software model is a transfer function from sector-bounded actuator command in normalized input units to loop input in normalized output units. Its numerator coefficients are 1, 2, 1; its denominator coefficients are 1, 0, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 181. Model a flexible two-body satellite and translate pointing specifications into robust design targets

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body control torque, and the measured outputs are two satellite angles, rates, pointing error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in two satellite angles starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after body control torque changes, two satellite angles begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from body control torque actuation to the visible two satellite angles response contains one or two dominant storage or integration processes. When the input is removed, the two satellite angles response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body control torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in body control torque can drive a distinguishable change in the key output two satellite angles; body control torque and the recorded readings two satellite angles, rates, pointing error share one clock, so all relevant motion can be reconstructed from these synchronized records. One body control torque action affects the recorded readings two satellite angles, rates, pointing error; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use J1=1,J2=0.1,k=0.091,b=0.0036 and G=0.036(s+25)/[s^2(s^2+0.04s+1)]; test k,b corners and pointing steps.

The declared software model is a transfer function from body control torque in normalized input units to two satellite angles in normalized output units. Its numerator coefficients are 0.036, 0.9; its denominator coefficients are 1, 0.04, 1, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 200 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 182. Compare gain stabilization and notch-based phase stabilization of the flexible satellite

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is gain-shaped or notch-shaped torque, and the measured outputs are satellite pointing and flexible deflection, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite pointing starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after gain-shaped or notch-shaped torque changes, satellite pointing begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from gain-shaped or notch-shaped torque actuation to the visible satellite pointing response contains one or two dominant storage or integration processes. When the input is removed, the satellite pointing response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in gain-shaped or notch-shaped torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in gain-shaped or notch-shaped torque can drive a distinguishable change in the key output satellite pointing; gain-shaped or notch-shaped torque and the recorded readings satellite pointing and flexible deflection share one clock, so all relevant motion can be reconstructed from these synchronized records. One gain-shaped or notch-shaped torque action affects the recorded readings satellite pointing and flexible deflection; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

On the nominal flexible satellite compare Dc1=0.25(2s+1), Dc2=0.001(30s+1), and Dc3=Dc1[((s/0.9)^2+1)/(s/25+1)^2] over all k,b corners.

The declared software model is a transfer function from gain-shaped or notch-shaped torque in normalized input units to satellite pointing and flexible deflection in normalized output units. Its numerator coefficients are 0.036, 0.9; its denominator coefficients are 1, 0.04, 1, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 500 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 183. Design satellite state feedback and an estimator from symmetric-root-locus pole choices

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is estimated-state feedback torque, and the measured outputs are measured attitude and estimated flexible states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after estimated-state feedback torque changes, measured attitude begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from estimated-state feedback torque actuation to the visible measured attitude response contains one or two dominant storage or integration processes. When the input is removed, the measured attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in estimated-state feedback torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in estimated-state feedback torque can drive a distinguishable change in the key output measured attitude; estimated-state feedback torque and the recorded readings measured attitude and estimated flexible states share one clock, so all relevant motion can be reconstructed from these synchronized records. One estimated-state feedback torque action affects the recorded readings measured attitude and estimated flexible states; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use control poles -0.45+/-j0.34,-0.15+/-j1.05, K=[-0.2788,0.0546,0.6814,1.1655], and L=[222,42.3,1515.4,5503.9].

The declared software model is a transfer function from estimated-state feedback torque in normalized input units to measured attitude and estimated flexible states in normalized output units. Its numerator coefficients are 0.3578625; its denominator coefficients are 1, 1.2, 1.7131, 1.10793, 0.3578625; and its input delay is 0 s.

The accompanying existing software record uses a 0.002 s sample interval for 200 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 184. Redesign the satellite by collocating the attitude sensor with the torque actuator

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is collocated body torque, and the measured outputs are collocated attitude and remote flexible angle, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in collocated attitude starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after collocated body torque changes, collocated attitude begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from collocated body torque actuation to the visible collocated attitude response contains one or two dominant storage or integration processes. When the input is removed, the collocated attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in collocated body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in collocated body torque can drive a distinguishable change in the key output collocated attitude; collocated body torque and the recorded readings collocated attitude and remote flexible angle share one clock, so all relevant motion can be reconstructed from these synchronized records. One collocated body torque action affects the recorded readings collocated attitude and remote flexible angle; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use collocated Gco=[(s+0.018)^2+0.954^2]/{s^2[(s+0.02)^2+1]} and controller 0.25(2s+1); compare with remote sensing.

The declared software model is a transfer function from collocated body torque in normalized input units to collocated attitude and remote flexible angle in normalized output units. Its numerator coefficients are 1, 0.036, 0.91044; its denominator coefficients are 1, 0.04, 1.0004, 0, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 200 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 185. Linearize Boeing 747 longitudinal/lateral dynamics and identify Dutch-roll, spiral, roll, phugoid, and short-period modes

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control inputs are rudder, elevator, aileron, thrust, and the measured outputs are aircraft rates, attitude, speed, altitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in aircraft rates starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.01 s sample interval; after rudder, elevator, aileron, thrust changes, aircraft rates begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from rudder, elevator, aileron, thrust actuation to the visible aircraft rates response contains one or two dominant storage or integration processes. When the input returns to baseline, the aircraft rates response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in rudder, elevator, aileron, thrust produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in rudder, elevator, aileron, thrust can drive a distinguishable change in the key output aircraft rates; rudder, elevator, aileron, thrust and the recorded readings aircraft rates, attitude, speed, altitude share one clock, so all relevant motion can be reconstructed from these synchronized records. One rudder, elevator, aileron, thrust action affects the recorded readings aircraft rates, attitude, speed, altitude; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use a representative Dutch-roll mode wn=1 rad/s,zeta=0.03 plus recorded spiral, roll, phugoid, and short-period modal estimates; excite rudder/elevator separately.

The declared software model is a transfer function from rudder in normalized input units to aircraft rates in normalized output units. Its numerator coefficients are 1; its denominator coefficients are 1, 0.06, 1; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 186. Design a yaw damper with rudder actuation, yaw-rate sensing, actuator dynamics, and washout

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is rudder command, and the measured outputs are yaw rate, sideslip, rudder position, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in yaw rate starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after rudder command changes, yaw rate begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from rudder command actuation to the visible yaw rate response contains one or two dominant storage or integration processes. When the input returns to baseline, the yaw rate response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in rudder command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in rudder command can drive a distinguishable change in the key output yaw rate; rudder command and the recorded readings yaw rate, sideslip, rudder position share one clock, so all relevant motion can be reconstructed from these synchronized records. One rudder command action affects the recorded readings yaw rate, sideslip, rudder position; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use yaw gain Kr=2.6, washout s/(s+1/3), and rudder actuator 10/(s+10); test yaw-rate pulses and steady-turn commands.

The declared software model is a transfer function from rudder command in normalized input units to yaw rate in normalized output units. Its numerator coefficients are 26, 0; its denominator coefficients are 1, 10.333333, 3.333333; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 187. Compare the practical yaw damper with a higher-order SRL controller-estimator design

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is rudder command from low or high order control, and the measured outputs are yaw rate and estimated lateral states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in yaw rate starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.005 s sample interval; after rudder command from low or high order control changes, yaw rate begins within one sample, with its first distinguishable change recorded 0.005 s after the input change and without a separate silent interval. The path from rudder command from low or high order control actuation to the visible yaw rate response contains one or two dominant storage or integration processes. When the input returns to baseline, the yaw rate response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in rudder command from low or high order control produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in rudder command from low or high order control can drive a distinguishable change in the key output yaw rate; rudder command from low or high order control and the recorded readings yaw rate and estimated lateral states share one clock, so all relevant motion can be reconstructed from these synchronized records. One rudder command from low or high order control action affects the recorded readings yaw rate and estimated lateral states; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Compare the practical Kr=2.6 yaw damper with six-state feedback K=[1.059,-0.191,-2.32,0.0992,0.037,0.486] and its estimator under sensor noise.

The declared software model is a transfer function from rudder command from low or high order control in normalized input units to yaw rate and estimated lateral states in normalized output units. Its numerator coefficients are 0.472225; its denominator coefficients are 1, 0.558, 0.472225; and its input delay is 0 s.

The accompanying existing software record uses a 0.005 s sample interval for 200 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 188. Design an altitude-hold autopilot with pitch-rate/pitch inner loops and altitude outer-loop feedback

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is elevator command, and the measured outputs are altitude, pitch angle, pitch rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in altitude first moves in an unfavorable or opposite direction before turning. The synchronized record has a 0.01 s sample interval; after elevator command changes, altitude first begins within one sample, with its first distinguishable change recorded 0.01 s after the input change and without a separate silent interval. The path from elevator command actuation to the visible altitude first response contains at least three successive storage or integration processes. When the input is removed, the altitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in elevator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in elevator command can drive a distinguishable change in the key output altitude first; elevator command and the recorded readings altitude, pitch angle, pitch rate share one clock, so all relevant motion can be reconstructed from these synchronized records. One elevator command action affects the recorded readings altitude, pitch angle, pitch rate; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use an altitude channel with RHP zero +5.61, fast pitch inner loop, slower altitude outer loop, and compare with full-state K=[-0.0009,0.0016,-1.883,-7.603,-0.001].

The declared software model is a transfer function from elevator command in deg to altitude in ft. Its numerator coefficients are -1, 5.61; its denominator coefficients are 1, 3, 2, 0; and its input delay is 0 s.

The accompanying existing software record uses a 0.01 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 189. Model and tune PI feedback for a delayed automotive fuel-air process

### Control Problem Description

This is an automotive fuel-air control system made from fuel injection, engine gas transport, and an exhaust oxygen sensor. The control input is fuel injection command, and the measured outputs are fuel air ratio and oxygen sensor signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in fuel air ratio starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after fuel injection command changes, a visible quiet interval separates the command from the first fuel air ratio change, which is first distinguishable 0.2 s after the input change. The path from fuel injection command actuation to the visible fuel air ratio response contains one or two dominant storage or integration processes. When the input returns to baseline, the fuel air ratio response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in fuel injection command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in fuel injection command can drive a distinguishable change in the key output fuel air ratio; fuel injection command and the recorded readings fuel air ratio and oxygen sensor signal share one clock, so all relevant motion can be reconstructed from these synchronized records. One fuel injection command action affects the recorded readings fuel air ratio and oxygen sensor signal; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use fast/slow fuel time constants 0.02 and 1 s, equal weights 0.5, transport delay 0.2 s, sensor lag 0.1 s, and PI aggregate gain KsKp=2.2.

The declared software model is a transfer function from fuel injection command in normalized input units to fuel air ratio and oxygen sensor signal in normalized output units. Its numerator coefficients are 0.51, 1; its denominator coefficients are 0.002, 0.122, 1.12, 1; and its input delay is 0.2 s.

The accompanying existing software record uses a 0.002 s sample interval for 30 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 190. Predict the nonlinear oxygen-sensor limit cycle by effective gain and describing function

### Control Problem Description

This is an automotive fuel-air control system made from fuel injection, engine gas transport, and an exhaust oxygen sensor. The control input is fuel injection command, and the measured outputs are air fuel error and oxygen sensor oscillation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in air fuel error starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after fuel injection command changes, a visible quiet interval separates the command from the first air fuel error change, which is first distinguishable 0.2 s after the input change. The path from fuel injection command actuation to the visible air fuel error response contains one or two dominant storage or integration processes. When the input returns to baseline, the air fuel error response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of fuel injection command reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in fuel injection command can drive a distinguishable change in the key output air fuel error; fuel injection command and the recorded readings air fuel error and oxygen sensor oscillation share one clock, so all relevant motion can be reconstructed from these synchronized records. One fuel injection command action affects the recorded readings air fuel error and oxygen sensor oscillation; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use the fuel-air dynamics, sensor output 0.1..0.9 with center slope 20, Kp=0.1, small-signal loop gain 6, and preserve saturation; measure the limit cycle.

The declared software model is a transfer function from fuel injection command in normalized input units to air fuel error and oxygen sensor oscillation in normalized output units. Its numerator coefficients are 0.51, 1; its denominator coefficients are 0.002, 0.122, 1.12, 1; and its input delay is 0.2 s.

The accompanying existing software record uses a 0.001 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 191. Replace sensor-slope dependence by relay feedback to obtain robust average stoichiometry

### Control Problem Description

This is an automotive fuel-air control system made from fuel injection, engine gas transport, and an exhaust oxygen sensor. The control input is fuel injection command through relay-conditioned sensing, and the measured outputs are average fuel-air ratio and switching signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in average fuel-air ratio starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after fuel injection command through relay-conditioned sensing changes, a visible quiet interval separates the command from the first average fuel-air ratio change, which is first distinguishable 0.2 s after the input change. The path from fuel injection command through relay-conditioned sensing actuation to the visible average fuel-air ratio response contains one or two dominant storage or integration processes. When the input returns to baseline, the average fuel-air ratio response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of fuel injection command through relay-conditioned sensing reveals a fixed relay switching law, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Every change in fuel injection command through relay-conditioned sensing can drive a distinguishable change in the key output average fuel-air ratio; fuel injection command through relay-conditioned sensing and the recorded readings average fuel-air ratio and switching signal share one clock, so all relevant motion can be reconstructed from these synchronized records. One fuel injection command through relay-conditioned sensing action affects the recorded readings average fuel-air ratio and switching signal; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use relay q=N sign(vs-vstar) with illustrative N=0.05, the same fuel-air/PI dynamics, and test sensor slopes multiplied by 0.5,1,2.

The declared software model is a transfer function from fuel injection command through relay-conditioned sensing in normalized input units to average fuel-air ratio and switching signal in normalized output units. Its numerator coefficients are 0.51, 1; its denominator coefficients are 0.002, 0.122, 1.12, 1; and its input delay is 0.2 s.

The accompanying existing software record uses a 0.001 s sample interval for 100 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 192. Build decoupled longitudinal, lateral, yaw, and altitude state models for a quadrotor and map four rotor commands

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control inputs are four rotor thrust commands, and the measured outputs are position, attitude, angular rates, altitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.002 s sample interval; after four rotor thrust commands changes, position begins within one sample, with its first distinguishable change recorded 0.002 s after the input change and without a separate silent interval. The path from four rotor thrust commands actuation to the visible position response contains at least three successive storage or integration processes. When the input is removed, the position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in four rotor thrust commands produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in four rotor thrust commands can drive a distinguishable change in the key output position; four rotor thrust commands and the recorded readings position, attitude, angular rates, altitude share one clock, so all relevant motion can be reconstructed from these synchronized records. One four rotor thrust commands action affects the recorded readings position, attitude, angular rates, altitude; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use a 1 kg, Iyy=0.02 kg*m^2 VTOL/quadrotor slice with thrust 0..20 N and torque +/-1 Nm; log all states and test rotor mixing columns one at a time.

The existing software record uses the registered nonlinear template vtol_cascaded. Its declared parameters are mass kg 1, pitch inertia kg m2 0.02, gravity m s2 9.81, linear drag n s m 0.25, pitch damping n m s 0.02, thrust min n 0, thrust max n 20, torque limit n m 1; its initial state is x m 0, z m 0, pitch rad 0, x velocity m s 0, z velocity m s 0, pitch rate rad s 0; its input channels are four rotor thrust commands channel 1, four rotor thrust commands channel 2; and its output channels are position, attitude, angular rates, altitude channel 1, altitude channel 2, altitude channel 3.

The accompanying existing software record uses a 0.002 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -0.5, -0.25, 0.25, 0.5, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 193. Design cascaded inner-attitude and outer-position PD loops for quadrotor trajectory following

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is mixed rotor thrusts, and the measured outputs are quadrotor position, attitude, path error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in quadrotor position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after mixed rotor thrusts changes, quadrotor position begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from mixed rotor thrusts actuation to the visible quadrotor position response contains at least three successive storage or integration processes. When the input is removed, the quadrotor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in mixed rotor thrusts produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in mixed rotor thrusts can drive a distinguishable change in the key output quadrotor position; mixed rotor thrusts and the recorded readings quadrotor position, attitude, path error share one clock, so all relevant motion can be reconstructed from these synchronized records. One mixed rotor thrusts action affects the recorded readings quadrotor position, attitude, path error; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use Gtheta=0.4(s+0.25)/[(s^2-3.2s+10.4)(s+3.4)(s+20)] and Gx=-131/[s times the same denominator]; close attitude faster than position.

The declared software model is a transfer function from mixed rotor thrusts in normalized input units to quadrotor position in normalized output units. Its numerator coefficients are 0.4, 0.1; its denominator coefficients are 1, 20.2, 3.52, 25.76, 707.2; and its input delay is 0 s.

The accompanying existing software record uses a 0.001 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 194. Design LQR/estimator controllers for quadrotor longitudinal, lateral, and yaw axes

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control inputs are LQR mixed rotor commands, and the measured outputs are measured and estimated quadrotor axis states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.001 s sample interval; after LQR mixed rotor commands changes, measured begins within one sample, with its first distinguishable change recorded 0.001 s after the input change and without a separate silent interval. The path from LQR mixed rotor commands actuation to the visible measured response contains at least three successive storage or integration processes. When the input is removed, the measured response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in LQR mixed rotor commands produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in LQR mixed rotor commands can drive a distinguishable change in the key output measured; LQR mixed rotor commands and the recorded readings measured and estimated quadrotor axis states share one clock, so all relevant motion can be reconstructed from these synchronized records. One LQR mixed rotor commands action affects the recorded readings measured and estimated quadrotor axis states; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use the complete VTOL state and constraints, then compare the listed longitudinal/lateral/yaw LQR gains with rho and estimator q multiplied by 0.1,1,10.

The existing software record uses the registered nonlinear template vtol_cascaded. Its declared parameters are mass kg 1, pitch inertia kg m2 0.02, gravity m s2 9.81, linear drag n s m 0.25, pitch damping n m s 0.02, thrust min n 0, thrust max n 20, torque limit n m 1; its initial state is x m 0, z m 0, pitch rad 0, x velocity m s 0, z velocity m s 0, pitch rate rad s 0; its input channels are LQR mixed rotor commands channel 1, LQR mixed rotor commands channel 2; and its output channels are measured and estimated quadrotor axis states channel 1, measured and estimated quadrotor axis states channel 2, measured and estimated quadrotor axis states channel 3, measured and estimated quadrotor axis states channel 4, measured and estimated quadrotor axis states channel 5, measured and estimated quadrotor axis states channel 6.

The accompanying existing software record uses a 0.001 s sample interval for 20 s, starts the primary output at 0, contains input amplitudes -0.5, -0.25, 0.25, 0.5, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 195. Identify nonlinear radiation/conduction dynamics and a three-state small-signal model for an RTP chamber

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is common command to three lamps, and the measured outputs are plate center and support temperatures, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in plate center starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after common command to three lamps changes, plate center begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from common command to three lamps actuation to the visible plate center response contains one or two dominant storage or integration processes. When the input returns to baseline, the plate center response settles or remains bounded instead of developing self-growing motion. As the size or operating point of common command to three lamps changes, radiation, lamp effectiveness, and available cooling change with temperature, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in common command to three lamps can drive a distinguishable change in the key output plate center; common command to three lamps and the recorded readings plate center and support temperatures share one clock, so all relevant motion can be reconstructed from these synchronized records. One common command to three lamps action affects the recorded readings plate center and support temperatures; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use the three-state RTP common-input transfer 0.5226(s+0.0876)(s+0.1438)/[(s+0.1482)(s+0.0863)(s+0.0527)] and test three lamp levels.

The declared software model is a transfer function from common command to three lamps in normalized input units to plate center and support temperatures in normalized output units. Its numerator coefficients are 0.5226, 0.12092964, 0.006583129488; its denominator coefficients are 1, 0.2872, 0.02514781, 0.000674015082; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 196. Apply PI temperature-trajectory control while respecting the absence of active cooling

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is nonnegative lamp power, and the measured outputs are temperature trajectory and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in temperature trajectory starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.05 s sample interval; after nonnegative lamp power changes, temperature trajectory begins within one sample, with its first distinguishable change recorded 0.05 s after the input change and without a separate silent interval. The path from nonnegative lamp power actuation to the visible temperature trajectory response contains one or two dominant storage or integration processes. When the input returns to baseline, the temperature trajectory response settles or remains bounded instead of developing self-growing motion. As the size or operating point of nonnegative lamp power changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in nonnegative lamp power can drive a distinguishable change in the key output temperature trajectory; nonnegative lamp power and the recorded readings temperature trajectory and tracking error share one clock, so all relevant motion can be reconstructed from these synchronized records. One nonnegative lamp power action affects the recorded readings temperature trajectory and tracking error; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use the RTP plant and PI D=(s+0.0527)/s with nonnegative lamp power; track heating ramps and physically passive cooling ramps separately.

The declared software model is a transfer function from nonnegative lamp power in normalized input units to temperature trajectory and tracking error in normalized output units. Its numerator coefficients are 0.5226, 0.12092964, 0.006583129488; its denominator coefficients are 1, 0.7571, 0.1337193, 0.006583129488; and its input delay is 0 s.

The accompanying existing software record uses a 0.05 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 197. Design an error-space LQG regulator that balances tracking, actuation, and wafer-temperature uniformity

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is common lamp command, and the measured outputs are center temperature, estimated three-node temperatures, and uniformity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in center temperature starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after common lamp command changes, center temperature begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from common lamp command actuation to the visible center temperature response contains one or two dominant storage or integration processes. When the input returns to baseline, the center temperature response settles or remains bounded instead of developing self-growing motion. As the size or operating point of common lamp command changes, radiation, lamp effectiveness, and available cooling change with temperature, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in common lamp command can drive a distinguishable change in the key output center temperature; common lamp command and the recorded readings center temperature, estimated three-node temperatures, and uniformity share one clock, so all relevant motion can be reconstructed from these synchronized records. One common lamp command action affects the recorded readings center temperature, estimated three-node temperatures, and uniformity; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use the three-state RTP model, K1=1,K0=[0.1221,2.0788,-0.2140], L=[16.1461,16.4710,13.2001], Rw=1,Rv=0.001; log node-temperature spread.

The declared software model is a transfer function from common lamp command in normalized input units to center temperature in normalized output units. Its numerator coefficients are 0.5226, 0.12092964, 0.006583129488; its denominator coefficients are 1, 0.2872, 0.02514781, 0.000674015082; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 198. Verify RTP control with lamp inversion, saturation, antiwindup, and a digital prototype

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is digitally commanded lamp voltage, and the measured outputs are wafer temperatures, lamp voltage, integrator state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in wafer temperatures starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.1 s sample interval; after digitally commanded lamp voltage changes, wafer temperatures begins within one sample, with its first distinguishable change recorded 0.1 s after the input change and without a separate silent interval. The path from digitally commanded lamp voltage actuation to the visible wafer temperatures response contains one or two dominant storage or integration processes. When the input returns to baseline, the wafer temperatures response settles or remains bounded instead of developing self-growing motion. As the size or operating point of digitally commanded lamp voltage changes, radiation, lamp effectiveness, and available cooling change with temperature, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Every change in digitally commanded lamp voltage can drive a distinguishable change in the key output wafer temperatures; digitally commanded lamp voltage and the recorded readings wafer temperatures, lamp voltage, integrator state share one clock, so all relevant motion can be reconstructed from these synchronized records. One digitally commanded lamp voltage action affects the recorded readings wafer temperatures, lamp voltage, integrator state; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Use lamp P=V^1.6, inverse V=P^0.625, voltage limits 1..4 V, reference filter 0.2/(s+0.2), Ts=0.1 s, and antiwindup recovery 1 s as an explicit trial value.

The declared software model is a transfer function from digitally commanded lamp voltage in normalized power units to wafer temperatures in degC. Its numerator coefficients are 0, 0.0521145, -0.10303042, 0.05092241; its denominator coefficients are 1, -2.97144027, 2.94312943, -0.9716885; and its input delay is 0 s.

The accompanying existing software record uses a 0.1 s sample interval for 300 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 199. Model exact adaptation in E. coli chemotaxis as integral feedback of receptor activity

### Control Problem Description

This is a bacterial chemotaxis system made from receptor activity, methylation adaptation, and cell motion. The control input is ligand concentration as the prescribed pathway input, and the measured outputs are receptor activity and methylation state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in receptor activity starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after ligand concentration as the prescribed pathway input changes, receptor activity begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from ligand concentration as the prescribed pathway input actuation to the visible receptor activity response contains one or two dominant storage or integration processes. When the input returns to baseline, the receptor activity response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in ligand concentration as the prescribed pathway input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in ligand concentration as the prescribed pathway input can drive a distinguishable change in the key output receptor activity; ligand concentration as the prescribed pathway input and the recorded readings receptor activity and methylation state share one clock, so all relevant motion can be reconstructed from these synchronized records. One ligand concentration as the prescribed pathway input action affects the recorded readings receptor activity and methylation state; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

For a numerical illustration choose K=1,Km=0.2 s^-1, CheRbar=0.5; step ligand by 1 at 20 s and run 60 s.

The declared software model is a transfer function from ligand concentration as the prescribed pathway input in normalized input units to receptor activity and methylation state in normalized output units. Its numerator coefficients are -1, 0; its denominator coefficients are 1, 0.2; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 60 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.

---

## 200. Map CheY activity into the one-dimensional mean chemotaxis motion model

### Control Problem Description

This is a bacterial chemotaxis system made from receptor activity, methylation adaptation, and cell motion. The control input is ligand perturbation as the prescribed pathway input, and the measured outputs are mean cell position, receptor activity, and methylation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in mean cell position starts in its final direction rather than moving the opposite way first. The synchronized record has a 0.02 s sample interval; after ligand perturbation as the prescribed pathway input changes, mean cell position begins within one sample, with its first distinguishable change recorded 0.02 s after the input change and without a separate silent interval. The path from ligand perturbation as the prescribed pathway input actuation to the visible mean cell position response contains one or two dominant storage or integration processes. When the input is removed, the mean cell position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in ligand perturbation as the prescribed pathway input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Every change in ligand perturbation as the prescribed pathway input can drive a distinguishable change in the key output mean cell position; ligand perturbation as the prescribed pathway input and the recorded readings mean cell position, receptor activity, and methylation share one clock, so all relevant motion can be reconstructed from these synchronized records. One ligand perturbation as the prescribed pathway input action affects the recorded readings mean cell position, receptor activity, and methylation; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.


### Profile Measurement Response (Natural Language)

Continue the chemotaxis illustration with Ka=1,Kx=0.5, baseline w=0; step ligand by 1 and integrate mean position.

The declared software model is a transfer function from ligand perturbation as the prescribed pathway input in normalized input units to mean cell position in normalized output units. Its numerator coefficients are 0.5; its denominator coefficients are 1, 0.2; and its input delay is 0 s.

The accompanying existing software record uses a 0.02 s sample interval for 60 s, starts the primary output at 0, contains input amplitudes -1, -0.5, 0.5, 1, and records parameter-variation multipliers 0.9, 1, 1.1.

All ranges stated here are software-simulation stopping boundaries only; they are not commands or permissions for a physical system.
