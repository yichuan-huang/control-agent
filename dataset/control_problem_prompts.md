# CFDC Dataset: Six-Field Inputs for Two Hundred Classic Control Problems

<!-- EXAMPLE-DATA-AUDIT: chapters 1-10 complete -->

> Each entry matches the global identifier in control_problems.md. Safety limits and dominant time scales are conservative normalized scheduling defaults for software simulation. For analysis-only examples with no controller, the Actuators field records the prescribed excitation or test input.

Every problem description is one formula-free natural-language test narrative with eight sentences in the exact Stage 0 evidence order. Diagnostic labels are not shown; the observable evidence is embedded in problem-specific prose so the engine can proceed without a clarification turn.

---

## 1. Household thermostat with hysteresis

### Control Problem Description

This is a residential heating system in which a thermostat watches room temperature and switches an electric heater on and off. The control input is binary heater command, and the measured outputs are room temperature, heater state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in room temperature starts in its final direction rather than moving the opposite way first; after the input changes, the room temperature response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the room temperature response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of binary heater command reveals fixed hysteresis and relay switching, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the room temperature, heater state measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use an outdoor temperature of 50 degF, a 65 degF setpoint, heat capacity 20000 Btu/degF, heat-loss coefficient 500 Btu/(h*degF), furnace rate 25000 Btu/h, and a 0.5 degF hysteresis half-width. Start at 64.5 degF with the furnace on and simulate for 6 h at 60 s sampling.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=1 binary_command; steady_output_change=50 degF; response_time_s=144000 s; input_min=0 binary_command; input_max=1 binary_command; output_min=64.5 degF; output_max=65.5 degF;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 1,
      "unit": "binary_command"
    },
    {
      "fact_id": "steady_output_change",
      "value": 50,
      "unit": "degF"
    },
    {
      "fact_id": "response_time_s",
      "value": 144000,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "binary_command"
    },
    {
      "fact_id": "input_max",
      "value": 1,
      "unit": "binary_command"
    },
    {
      "fact_id": "output_min",
      "value": 64.5,
      "unit": "degF"
    },
    {
      "fact_id": "output_max",
      "value": 65.5,
      "unit": "degF"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      50
    ],
    "denominator": [
      144000,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "binary heater command",
    "output_signal_id": "room temperature",
    "input_units": "binary_command",
    "output_units": "degF"
  },
  "experiment": {
    "sample_time_s": 60,
    "duration_s": 21600,
    "initial_output": 64.5,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "operating_condition": {
    "outdoor_temperature_degF": 50,
    "setpoint_degF": 65,
    "heat_capacity_Btu_per_degF": 20000,
    "heat_loss_Btu_per_h_degF": 500,
    "furnace_rate_Btu_per_h": 25000,
    "hysteresis_half_width_degF": 0.5
  },
  "initial_conditions": {
    "room_temperature_degF": 64.5,
    "heater_state": 1
  },
  "eight_segment_evidence": {
    "stability": "Return binary heater command to baseline and verify that room temperature, heater state remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective room temperature, heater state direction with its final direction.",
    "delay": "Measure the time from the logged binary heater command edge to the first effective room temperature, heater state change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log binary heater command and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 2. Automobile cruise control, open versus closed loop

### Control Problem Description

This is a road vehicle whose longitudinal speed is set by engine traction acting against rolling and aerodynamic resistance. The control input is throttle angle, and the measured outputs are vehicle speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in vehicle speed starts in its final direction rather than moving the opposite way first; after the input changes, the vehicle speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the vehicle speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in throttle angle produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the vehicle speed measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for vehicle speed.

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

### Example Data (Natural Language)

Around 65 mph, change throttle angle by 1 deg and use a 10 mph steady speed change per degree. Treat a 1% uphill grade as a -5 mph disturbance, use a 5 s response time for the dynamic simulation, and compare open loop with proportional feedback gain 10.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=1 deg; steady_output_change=10 mph; response_time_s=5 s; input_min=-3 deg; input_max=3 deg; output_min=45 mph; output_max=80 mph;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 1,
      "unit": "deg"
    },
    {
      "fact_id": "steady_output_change",
      "value": 10,
      "unit": "mph"
    },
    {
      "fact_id": "response_time_s",
      "value": 5,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -3,
      "unit": "deg"
    },
    {
      "fact_id": "input_max",
      "value": 3,
      "unit": "deg"
    },
    {
      "fact_id": "output_min",
      "value": 45,
      "unit": "mph"
    },
    {
      "fact_id": "output_max",
      "value": 80,
      "unit": "mph"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      10
    ],
    "denominator": [
      5,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "throttle angle",
    "output_signal_id": "vehicle speed",
    "input_units": "deg",
    "output_units": "mph"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 60,
    "initial_output": 65,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "operating_condition": {
    "reference_speed_mph": 65,
    "road_grade_percent": 1,
    "controller_gain": 10
  },
  "eight_segment_evidence": {
    "stability": "Return throttle angle to baseline and verify that vehicle speed remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective vehicle speed direction with its final direction.",
    "delay": "Measure the time from the logged throttle angle edge to the first effective vehicle speed change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log throttle angle and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 3. Manual automobile steering

### Control Problem Description

This is a road vehicle whose driver corrects heading and lane position through the steering wheel. The control input is steering wheel angle, and the measured outputs are heading angle, lane error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heading angle starts in its final direction rather than moving the opposite way first; after the input changes, the heading angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the heading angle response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steering wheel angle produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the heading angle, lane error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change steering wheel angle by 5 deg; expect a final heading angle, lane error change of 8 deg with a 63% response time of 1.5 s. Use an input range of -30 to 30 deg and an output range of -180 to 180 deg; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=5 deg; steady_output_change=8 deg; response_time_s=1.5 s; input_min=-30 deg; input_max=30 deg; output_min=-180 deg; output_max=180 deg;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 5,
      "unit": "deg"
    },
    {
      "fact_id": "steady_output_change",
      "value": 8,
      "unit": "deg"
    },
    {
      "fact_id": "response_time_s",
      "value": 1.5,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -30,
      "unit": "deg"
    },
    {
      "fact_id": "input_max",
      "value": 30,
      "unit": "deg"
    },
    {
      "fact_id": "output_min",
      "value": -180,
      "unit": "deg"
    },
    {
      "fact_id": "output_max",
      "value": 180,
      "unit": "deg"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1.6
    ],
    "denominator": [
      1.5,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "steering wheel angle",
    "output_signal_id": "heading angle",
    "input_units": "deg",
    "output_units": "deg"
  },
  "experiment": {
    "sample_time_s": 0.03,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -5,
      -2.5,
      2.5,
      5
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return steering wheel angle to baseline and verify that heading angle, lane error remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective heading angle, lane error direction with its final direction.",
    "delay": "Measure the time from the logged steering wheel angle edge to the first effective heading angle, lane error change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log steering wheel angle and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 4. Drebbel incubator temperature regulator

### Control Problem Description

This is an incubator made from a heated water jacket, a furnace, and a mechanical temperature-regulating linkage. The control input is air or fuel valve position, and the measured outputs are incubator temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in incubator temperature starts in its final direction rather than moving the opposite way first; after the input changes, the incubator temperature response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the incubator temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in air or fuel valve position produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the incubator temperature measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change air or fuel valve position by 10 %; expect a final incubator temperature change of 2 degC with a 63% response time of 120 s. Use an input range of 0 to 100 % and an output range of 30 to 42 degC; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=10 %; steady_output_change=2 degC; response_time_s=120 s; input_min=0 %; input_max=100 %; output_min=30 degC; output_max=42 degC;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 10,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": 2,
      "unit": "degC"
    },
    {
      "fact_id": "response_time_s",
      "value": 120,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 30,
      "unit": "degC"
    },
    {
      "fact_id": "output_max",
      "value": 42,
      "unit": "degC"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.2
    ],
    "denominator": [
      120,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "air or fuel valve position",
    "output_signal_id": "incubator temperature",
    "input_units": "%",
    "output_units": "degC"
  },
  "experiment": {
    "sample_time_s": 2.4,
    "duration_s": 960,
    "initial_output": 36,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return air or fuel valve position to baseline and verify that incubator temperature remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective incubator temperature direction with its final direction.",
    "delay": "Measure the time from the logged air or fuel valve position edge to the first effective incubator temperature change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log air or fuel valve position and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 5. Float-valve water-level regulator

### Control Problem Description

This is a storage tank whose rising and falling float mechanically changes the inlet-valve opening. The control input is inlet valve opening, and the measured outputs are tank liquid level, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tank liquid level starts in its final direction rather than moving the opposite way first; after the input changes, the tank liquid level response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the tank liquid level response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in inlet valve opening produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the tank liquid level measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change inlet valve opening by 10 %; expect a final tank liquid level change of 0.08 m with a 63% response time of 20 s. Use an input range of 0 to 100 % and an output range of 0.2 to 1.2 m; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=10 %; steady_output_change=0.08 m; response_time_s=20 s; input_min=0 %; input_max=100 %; output_min=0.2 m; output_max=1.2 m;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 10,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": 0.08,
      "unit": "m"
    },
    {
      "fact_id": "response_time_s",
      "value": 20,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 0.2,
      "unit": "m"
    },
    {
      "fact_id": "output_max",
      "value": 1.2,
      "unit": "m"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.008
    ],
    "denominator": [
      20,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "inlet valve opening",
    "output_signal_id": "tank liquid level",
    "input_units": "%",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.4,
    "duration_s": 160,
    "initial_output": 0.7,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return inlet valve opening to baseline and verify that tank liquid level remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective tank liquid level direction with its final direction.",
    "delay": "Measure the time from the logged inlet valve opening edge to the first effective tank liquid level change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log inlet valve opening and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 6. Watt fly-ball steam-engine governor

### Control Problem Description

This is a mechanical engine governor in which fly-balls and linkage reposition a steam valve as shaft speed changes. The control input is steam valve opening, and the measured outputs are engine shaft speed, governor displacement, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in engine shaft speed starts in its final direction rather than moving the opposite way first; after the input changes, the engine shaft speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the engine shaft speed response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of steam valve opening reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the engine shaft speed, governor displacement measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change steam valve opening by 10 %; expect a final engine shaft speed, governor displacement change of 20 rpm with a 63% response time of 8 s. Use an input range of 0 to 100 % and an output range of 400 to 900 rpm; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=10 %; steady_output_change=20 rpm; response_time_s=8 s; input_min=0 %; input_max=100 %; output_min=400 rpm; output_max=900 rpm;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 10,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": 20,
      "unit": "rpm"
    },
    {
      "fact_id": "response_time_s",
      "value": 8,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 400,
      "unit": "rpm"
    },
    {
      "fact_id": "output_max",
      "value": 900,
      "unit": "rpm"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2
    ],
    "denominator": [
      8,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "steam valve opening",
    "output_signal_id": "engine shaft speed",
    "input_units": "%",
    "output_units": "rpm"
  },
  "experiment": {
    "sample_time_s": 0.16,
    "duration_s": 64,
    "initial_output": 650,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return steam valve opening to baseline and verify that engine shaft speed, governor displacement remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective engine shaft speed, governor displacement direction with its final direction.",
    "delay": "Measure the time from the logged steam valve opening edge to the first effective engine shaft speed, governor displacement change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log steam valve opening and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 7. Paper-machine stock-consistency control

### Control Problem Description

This is the wet-end section of a paper machine, where dilution water is used to hold pulp consistency steady. The control input is dilution water valve, and the measured outputs are stock consistency, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in stock consistency starts in its final direction rather than moving the opposite way first; after the input changes, the stock consistency response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the stock consistency response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in dilution water valve produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the stock consistency measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change dilution water valve by 5 %; expect a final stock consistency change of -0.4 % with a 63% response time of 30 s. Use an input range of 0 to 100 % and an output range of 2 to 6 %; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=5 %; steady_output_change=-0.4 %; response_time_s=30 s; input_min=0 %; input_max=100 %; output_min=2 %; output_max=6 %;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 5,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": -0.4,
      "unit": "%"
    },
    {
      "fact_id": "response_time_s",
      "value": 30,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 2,
      "unit": "%"
    },
    {
      "fact_id": "output_max",
      "value": 6,
      "unit": "%"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -0.08
    ],
    "denominator": [
      30,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "dilution water valve",
    "output_signal_id": "stock consistency",
    "input_units": "%",
    "output_units": "%"
  },
  "experiment": {
    "sample_time_s": 0.6,
    "duration_s": 240,
    "initial_output": 4,
    "input_amplitudes": [
      -5,
      -2.5,
      2.5,
      5
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return dilution water valve to baseline and verify that stock consistency remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective stock consistency direction with its final direction.",
    "delay": "Measure the time from the logged dilution water valve edge to the first effective stock consistency change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log dilution water valve and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 8. Paper-machine moisture control

### Control Problem Description

This is the dryer section of a paper machine, where steam delivery determines the moisture left in the sheet. The control input is dryer steam command, and the measured outputs are paper moisture, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in paper moisture starts in its final direction rather than moving the opposite way first; after the input changes, the paper moisture response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the paper moisture response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in dryer steam command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the paper moisture measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change dryer steam command by 10 %; expect a final paper moisture change of -1.2 % with a 63% response time of 60 s and use 8 s pure delay. Use an input range of 0 to 100 % and an output range of 2 to 12 %; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=10 %; steady_output_change=-1.2 %; response_time_s=60 s; dead_time_s=8 s; input_min=0 %; input_max=100 %; output_min=2 %; output_max=12 %;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 10,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": -1.2,
      "unit": "%"
    },
    {
      "fact_id": "response_time_s",
      "value": 60,
      "unit": "s"
    },
    {
      "fact_id": "dead_time_s",
      "value": 8,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 2,
      "unit": "%"
    },
    {
      "fact_id": "output_max",
      "value": 12,
      "unit": "%"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -0.12
    ],
    "denominator": [
      60,
      1
    ],
    "input_delay_s": 8,
    "input_signal_id": "dryer steam command",
    "output_signal_id": "paper moisture",
    "input_units": "%",
    "output_units": "%"
  },
  "experiment": {
    "sample_time_s": 1.2,
    "duration_s": 480,
    "initial_output": 7,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return dryer steam command to baseline and verify that paper moisture remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective paper moisture direction with its final direction.",
    "delay": "Measure the time from the logged dryer steam command edge to the first effective paper moisture change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log dryer steam command and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 9. Human blood-pressure regulation

### Control Problem Description

This is a cardiovascular system in which the heart, blood vessels, and autonomic reflexes jointly regulate arterial pressure. The control input is neural cardiac and vascular commands, and the measured outputs are arterial pressure, heart rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in arterial pressure starts in its final direction rather than moving the opposite way first; after the input changes, the arterial pressure response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the arterial pressure response settles or remains bounded instead of developing self-growing motion. As the size or operating point of neural cardiac and vascular commands changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the arterial pressure, heart rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change neural cardiac and vascular commands by 0.1 neural_command; expect a final arterial pressure, heart rate change of 8 mmHg with a 63% response time of 6 s. Use an input range of -0.5 to 0.5 neural_command and an output range of 60 to 140 mmHg; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=0.1 neural_command; steady_output_change=8 mmHg; response_time_s=6 s; input_min=-0.5 neural_command; input_max=0.5 neural_command; output_min=60 mmHg; output_max=140 mmHg;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 0.1,
      "unit": "neural_command"
    },
    {
      "fact_id": "steady_output_change",
      "value": 8,
      "unit": "mmHg"
    },
    {
      "fact_id": "response_time_s",
      "value": 6,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -0.5,
      "unit": "neural_command"
    },
    {
      "fact_id": "input_max",
      "value": 0.5,
      "unit": "neural_command"
    },
    {
      "fact_id": "output_min",
      "value": 60,
      "unit": "mmHg"
    },
    {
      "fact_id": "output_max",
      "value": 140,
      "unit": "mmHg"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      80
    ],
    "denominator": [
      6,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "neural cardiac and vascular commands",
    "output_signal_id": "arterial pressure",
    "input_units": "neural_command",
    "output_units": "mmHg"
  },
  "experiment": {
    "sample_time_s": 0.12,
    "duration_s": 48,
    "initial_output": 100,
    "input_amplitudes": [
      -0.1,
      -0.05,
      0.05,
      0.1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return neural cardiac and vascular commands to baseline and verify that arterial pressure, heart rate remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective arterial pressure, heart rate direction with its final direction.",
    "delay": "Measure the time from the logged neural cardiac and vascular commands edge to the first effective arterial pressure, heart rate change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log neural cardiac and vascular commands and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 10. Human blood-glucose regulation

### Control Problem Description

This is a metabolic regulation system in which insulin and counter-regulatory hormones jointly maintain blood glucose. The control input is endogenous insulin and counterregulation, and the measured outputs are blood glucose, insulin level, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in blood glucose starts in its final direction rather than moving the opposite way first; after the input changes, the blood glucose response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the blood glucose response settles or remains bounded instead of developing self-growing motion. As the size or operating point of endogenous insulin and counterregulation changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the blood glucose, insulin level measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change endogenous insulin and counterregulation by 0.1 insulin_command; expect a final blood glucose, insulin level change of -12 mg/dL with a 63% response time of 20 s. Use an input range of -0.5 to 0.5 insulin_command and an output range of 60 to 180 mg/dL; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=0.1 insulin_command; steady_output_change=-12 mg/dL; response_time_s=20 s; input_min=-0.5 insulin_command; input_max=0.5 insulin_command; output_min=60 mg/dL; output_max=180 mg/dL;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 0.1,
      "unit": "insulin_command"
    },
    {
      "fact_id": "steady_output_change",
      "value": -12,
      "unit": "mg/dL"
    },
    {
      "fact_id": "response_time_s",
      "value": 20,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -0.5,
      "unit": "insulin_command"
    },
    {
      "fact_id": "input_max",
      "value": 0.5,
      "unit": "insulin_command"
    },
    {
      "fact_id": "output_min",
      "value": 60,
      "unit": "mg/dL"
    },
    {
      "fact_id": "output_max",
      "value": 180,
      "unit": "mg/dL"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -120
    ],
    "denominator": [
      20,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "endogenous insulin and counterregulation",
    "output_signal_id": "blood glucose",
    "input_units": "insulin_command",
    "output_units": "mg/dL"
  },
  "experiment": {
    "sample_time_s": 0.4,
    "duration_s": 160,
    "initial_output": 120,
    "input_amplitudes": [
      -0.1,
      -0.05,
      0.05,
      0.1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return endogenous insulin and counterregulation to baseline and verify that blood glucose, insulin level remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective blood glucose, insulin level direction with its final direction.",
    "delay": "Measure the time from the logged endogenous insulin and counterregulation edge to the first effective blood glucose, insulin level change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log endogenous insulin and counterregulation and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 11. Human heart-rate regulation

### Control Problem Description

This is a heart-rate regulation system in which sympathetic and parasympathetic nerves act on the cardiac pacemaker. The control input is sympathetic and parasympathetic drive, and the measured outputs are heart rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heart rate starts in its final direction rather than moving the opposite way first; after the input changes, the heart rate response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the heart rate response settles or remains bounded instead of developing self-growing motion. As the size or operating point of sympathetic and parasympathetic drive changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the heart rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change sympathetic and parasympathetic drive by 0.1 autonomic_command; expect a final heart rate change of 8 bpm with a 63% response time of 5 s. Use an input range of -0.5 to 0.5 autonomic_command and an output range of 45 to 160 bpm; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=0.1 autonomic_command; steady_output_change=8 bpm; response_time_s=5 s; input_min=-0.5 autonomic_command; input_max=0.5 autonomic_command; output_min=45 bpm; output_max=160 bpm;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 0.1,
      "unit": "autonomic_command"
    },
    {
      "fact_id": "steady_output_change",
      "value": 8,
      "unit": "bpm"
    },
    {
      "fact_id": "response_time_s",
      "value": 5,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -0.5,
      "unit": "autonomic_command"
    },
    {
      "fact_id": "input_max",
      "value": 0.5,
      "unit": "autonomic_command"
    },
    {
      "fact_id": "output_min",
      "value": 45,
      "unit": "bpm"
    },
    {
      "fact_id": "output_max",
      "value": 160,
      "unit": "bpm"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      80
    ],
    "denominator": [
      5,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "sympathetic and parasympathetic drive",
    "output_signal_id": "heart rate",
    "input_units": "autonomic_command",
    "output_units": "bpm"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 40,
    "initial_output": 102.5,
    "input_amplitudes": [
      -0.1,
      -0.05,
      0.05,
      0.1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sympathetic and parasympathetic drive to baseline and verify that heart rate remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective heart rate direction with its final direction.",
    "delay": "Measure the time from the logged sympathetic and parasympathetic drive edge to the first effective heart rate change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log sympathetic and parasympathetic drive and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 12. Eye-pointing-angle control

### Control Problem Description

This is an eye-pointing system in which the extraocular muscles rotate the eyeball to reduce retinal error. The control input is ocular muscle torque, and the measured outputs are eye angle, retinal error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in eye angle starts in its final direction rather than moving the opposite way first; after the input changes, the eye angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the eye angle response settles or remains bounded instead of developing self-growing motion. As the size or operating point of ocular muscle torque changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the eye angle, retinal error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change ocular muscle torque by 0.002 Nm; expect a final eye angle, retinal error change of 0.12 rad with a 63% response time of 0.18 s. Use an input range of -0.01 to 0.01 Nm and an output range of -0.5 to 0.5 rad; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=0.002 Nm; steady_output_change=0.12 rad; response_time_s=0.18 s; input_min=-0.01 Nm; input_max=0.01 Nm; output_min=-0.5 rad; output_max=0.5 rad;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 0.002,
      "unit": "Nm"
    },
    {
      "fact_id": "steady_output_change",
      "value": 0.12,
      "unit": "rad"
    },
    {
      "fact_id": "response_time_s",
      "value": 0.18,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -0.01,
      "unit": "Nm"
    },
    {
      "fact_id": "input_max",
      "value": 0.01,
      "unit": "Nm"
    },
    {
      "fact_id": "output_min",
      "value": -0.5,
      "unit": "rad"
    },
    {
      "fact_id": "output_max",
      "value": 0.5,
      "unit": "rad"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      60
    ],
    "denominator": [
      0.18,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "ocular muscle torque",
    "output_signal_id": "eye angle",
    "input_units": "Nm",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 1.44,
    "initial_output": 0,
    "input_amplitudes": [
      -0.002,
      -0.001,
      0.001,
      0.002
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return ocular muscle torque to baseline and verify that eye angle, retinal error remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective eye angle, retinal error direction with its final direction.",
    "delay": "Measure the time from the logged ocular muscle torque edge to the first effective eye angle, retinal error change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log ocular muscle torque and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 13. Pupil-diameter light regulation

### Control Problem Description

This is a pupillary light-reflex system in which iris muscles change aperture to regulate retinal illumination. The control input is iris muscle activation, and the measured outputs are pupil diameter, retinal illumination, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pupil diameter starts in its final direction rather than moving the opposite way first; after the input changes, the pupil diameter response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the pupil diameter response settles or remains bounded instead of developing self-growing motion. As the size or operating point of iris muscle activation changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the pupil diameter, retinal illumination measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change iris muscle activation by 0.1 iris_command; expect a final pupil diameter, retinal illumination change of -0.8 mm with a 63% response time of 0.8 s. Use an input range of -1 to 1 iris_command and an output range of 2 to 8 mm; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=0.1 iris_command; steady_output_change=-0.8 mm; response_time_s=0.8 s; input_min=-1 iris_command; input_max=1 iris_command; output_min=2 mm; output_max=8 mm;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 0.1,
      "unit": "iris_command"
    },
    {
      "fact_id": "steady_output_change",
      "value": -0.8,
      "unit": "mm"
    },
    {
      "fact_id": "response_time_s",
      "value": 0.8,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -1,
      "unit": "iris_command"
    },
    {
      "fact_id": "input_max",
      "value": 1,
      "unit": "iris_command"
    },
    {
      "fact_id": "output_min",
      "value": 2,
      "unit": "mm"
    },
    {
      "fact_id": "output_max",
      "value": 8,
      "unit": "mm"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -8
    ],
    "denominator": [
      0.8,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "iris muscle activation",
    "output_signal_id": "pupil diameter",
    "input_units": "iris_command",
    "output_units": "mm"
  },
  "experiment": {
    "sample_time_s": 0.016,
    "duration_s": 6.4,
    "initial_output": 5,
    "input_amplitudes": [
      -0.1,
      -0.05,
      0.05,
      0.1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return iris muscle activation to baseline and verify that pupil diameter, retinal illumination remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pupil diameter, retinal illumination direction with its final direction.",
    "delay": "Measure the time from the logged iris muscle activation edge to the first effective pupil diameter, retinal illumination change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log iris muscle activation and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 14. Elevator position control with coarse/fine sensing and cable stretch

### Control Problem Description

This is an elevator positioning apparatus made from a hoist motor, brake, car, and elastic suspension cable. The control input is hoist motor torque and brake, and the measured outputs are car position, landing error, cable stretch, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in car position starts in its final direction rather than moving the opposite way first; after the input changes, the car position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the car position response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in hoist motor torque and brake produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the car position, landing error, cable stretch measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change hoist motor torque and brake by 100 Nm; expect a final car position, landing error, cable stretch change of 0.15 m with a 63% response time of 2.5 s. Use an input range of -1500 to 1500 Nm and an output range of 0 to 120 m; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=100 Nm; steady_output_change=0.15 m; response_time_s=2.5 s; input_min=-1500 Nm; input_max=1500 Nm; output_min=0 m; output_max=120 m;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 100,
      "unit": "Nm"
    },
    {
      "fact_id": "steady_output_change",
      "value": 0.15,
      "unit": "m"
    },
    {
      "fact_id": "response_time_s",
      "value": 2.5,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -1500,
      "unit": "Nm"
    },
    {
      "fact_id": "input_max",
      "value": 1500,
      "unit": "Nm"
    },
    {
      "fact_id": "output_min",
      "value": 0,
      "unit": "m"
    },
    {
      "fact_id": "output_max",
      "value": 120,
      "unit": "m"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.0015
    ],
    "denominator": [
      2.5,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "hoist motor torque and brake",
    "output_signal_id": "car position",
    "input_units": "Nm",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 20,
    "initial_output": 60,
    "input_amplitudes": [
      -100,
      -50,
      50,
      100
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return hoist motor torque and brake to baseline and verify that car position, landing error, cable stretch remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective car position, landing error, cable stretch direction with its final direction.",
    "delay": "Measure the time from the logged hoist motor torque and brake edge to the first effective car position, landing error, cable stretch change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log hoist motor torque and brake and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 15. Electrical temperature sensing and actuation

### Control Problem Description

This is a temperature-control apparatus made from an electric heater, a thermal body, and an electrical temperature sensor. The control input is electrical heater voltage, and the measured outputs are temperature, sensor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in temperature starts in its final direction rather than moving the opposite way first; after the input changes, the temperature response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in electrical heater voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the temperature, sensor voltage measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change electrical heater voltage by 5 V; expect a final temperature, sensor voltage change of 8 degC with a 63% response time of 80 s. Use an input range of 0 to 48 V and an output range of 15 to 90 degC; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=5 V; steady_output_change=8 degC; response_time_s=80 s; input_min=0 V; input_max=48 V; output_min=15 degC; output_max=90 degC;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 5,
      "unit": "V"
    },
    {
      "fact_id": "steady_output_change",
      "value": 8,
      "unit": "degC"
    },
    {
      "fact_id": "response_time_s",
      "value": 80,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "V"
    },
    {
      "fact_id": "input_max",
      "value": 48,
      "unit": "V"
    },
    {
      "fact_id": "output_min",
      "value": 15,
      "unit": "degC"
    },
    {
      "fact_id": "output_max",
      "value": 90,
      "unit": "degC"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1.6
    ],
    "denominator": [
      80,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "electrical heater voltage",
    "output_signal_id": "temperature",
    "input_units": "V",
    "output_units": "degC"
  },
  "experiment": {
    "sample_time_s": 1.6,
    "duration_s": 640,
    "initial_output": 52.5,
    "input_amplitudes": [
      -5,
      -2.5,
      2.5,
      5
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return electrical heater voltage to baseline and verify that temperature, sensor voltage remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective temperature, sensor voltage direction with its final direction.",
    "delay": "Measure the time from the logged electrical heater voltage edge to the first effective temperature, sensor voltage change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log electrical heater voltage and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 16. Electrical pressure sensing and actuation

### Control Problem Description

This is a pressure-control apparatus made from a regulating valve, a pressurized chamber, and a pressure transmitter. The control input is valve command, and the measured outputs are pressure, sensor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pressure starts in its final direction rather than moving the opposite way first; after the input changes, the pressure response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the pressure response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in valve command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the pressure, sensor voltage measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change valve command by 10 %; expect a final pressure, sensor voltage change of 30 kPa with a 63% response time of 12 s. Use an input range of 0 to 100 % and an output range of 0 to 500 kPa; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=10 %; steady_output_change=30 kPa; response_time_s=12 s; input_min=0 %; input_max=100 %; output_min=0 kPa; output_max=500 kPa;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 10,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": 30,
      "unit": "kPa"
    },
    {
      "fact_id": "response_time_s",
      "value": 12,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 0,
      "unit": "kPa"
    },
    {
      "fact_id": "output_max",
      "value": 500,
      "unit": "kPa"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      3
    ],
    "denominator": [
      12,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "valve command",
    "output_signal_id": "pressure",
    "input_units": "%",
    "output_units": "kPa"
  },
  "experiment": {
    "sample_time_s": 0.24,
    "duration_s": 96,
    "initial_output": 250,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return valve command to baseline and verify that pressure, sensor voltage remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pressure, sensor voltage direction with its final direction.",
    "delay": "Measure the time from the logged valve command edge to the first effective pressure, sensor voltage change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log valve command and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 17. Electrical liquid-level sensing and actuation

### Control Problem Description

This is a liquid-level apparatus made from a storage vessel, pump or valve, and a level transmitter. The control input is pump speed or valve position, and the measured outputs are liquid level, transmitter signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in liquid level starts in its final direction rather than moving the opposite way first; after the input changes, the liquid level response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the liquid level response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in pump speed or valve position produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the liquid level, transmitter signal measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change pump speed or valve position by 10 %; expect a final liquid level, transmitter signal change of 0.1 m with a 63% response time of 25 s. Use an input range of 0 to 100 % and an output range of 0.1 to 1.5 m; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=10 %; steady_output_change=0.1 m; response_time_s=25 s; input_min=0 %; input_max=100 %; output_min=0.1 m; output_max=1.5 m;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 10,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": 0.1,
      "unit": "m"
    },
    {
      "fact_id": "response_time_s",
      "value": 25,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 0.1,
      "unit": "m"
    },
    {
      "fact_id": "output_max",
      "value": 1.5,
      "unit": "m"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.01
    ],
    "denominator": [
      25,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "pump speed or valve position",
    "output_signal_id": "liquid level",
    "input_units": "%",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.5,
    "duration_s": 200,
    "initial_output": 0.8,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return pump speed or valve position to baseline and verify that liquid level, transmitter signal remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective liquid level, transmitter signal direction with its final direction.",
    "delay": "Measure the time from the logged pump speed or valve position edge to the first effective liquid level, transmitter signal change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log pump speed or valve position and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 18. Electrical pipe-flow sensing and actuation

### Control Problem Description

This is a pipeline flow-control apparatus made from a pipe, regulating valve, and flow sensor. The control input is control valve position, and the measured outputs are pipe flow rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pipe flow rate starts in its final direction rather than moving the opposite way first; after the input changes, the pipe flow rate response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the pipe flow rate response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in control valve position produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the pipe flow rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change control valve position by 10 %; expect a final pipe flow rate change of 0.02 m^3/s with a 63% response time of 4 s. Use an input range of 0 to 100 % and an output range of 0 to 0.2 m^3/s; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=10 %; steady_output_change=0.02 m^3/s; response_time_s=4 s; input_min=0 %; input_max=100 %; output_min=0 m^3/s; output_max=0.2 m^3/s;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 10,
      "unit": "%"
    },
    {
      "fact_id": "steady_output_change",
      "value": 0.02,
      "unit": "m^3/s"
    },
    {
      "fact_id": "response_time_s",
      "value": 4,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "%"
    },
    {
      "fact_id": "input_max",
      "value": 100,
      "unit": "%"
    },
    {
      "fact_id": "output_min",
      "value": 0,
      "unit": "m^3/s"
    },
    {
      "fact_id": "output_max",
      "value": 0.2,
      "unit": "m^3/s"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.002
    ],
    "denominator": [
      4,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "control valve position",
    "output_signal_id": "pipe flow rate",
    "input_units": "%",
    "output_units": "m^3/s"
  },
  "experiment": {
    "sample_time_s": 0.08,
    "duration_s": 32,
    "initial_output": 0.1,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return control valve position to baseline and verify that pipe flow rate remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pipe flow rate direction with its final direction.",
    "delay": "Measure the time from the logged control valve position edge to the first effective pipe flow rate change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log control valve position and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 19. HPA-axis stress-hormone negative feedback

### Control Problem Description

This is a hormonal stress-regulation system formed by feedback among the hypothalamus, pituitary, and adrenal glands. The control input is endogenous secretion rates, and the measured outputs are hormone concentrations, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in hormone concentrations starts in its final direction rather than moving the opposite way first; after the input changes, the hormone concentrations response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the hormone concentrations response settles or remains bounded instead of developing self-growing motion. As the size or operating point of endogenous secretion rates changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the hormone concentrations measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

In a safe simulation, change endogenous secretion rates by 1 ng/(mL*min); expect a final hormone concentrations change of 0.8 ng/mL with a 63% response time of 600 s. Use an input range of 0 to 5 ng/(mL*min) and an output range of 0 to 20 ng/mL; sample at no more than one fiftieth of the time constant, run for at least eight time constants, and repeat the four amplitude levels and 0.9/1.0/1.1 parameter cases.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=1 ng/(mL*min); steady_output_change=0.8 ng/mL; response_time_s=600 s; input_min=0 ng/(mL*min); input_max=5 ng/(mL*min); output_min=0 ng/mL; output_max=20 ng/mL;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 1,
      "unit": "ng/(mL*min)"
    },
    {
      "fact_id": "steady_output_change",
      "value": 0.8,
      "unit": "ng/mL"
    },
    {
      "fact_id": "response_time_s",
      "value": 600,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "ng/(mL*min)"
    },
    {
      "fact_id": "input_max",
      "value": 5,
      "unit": "ng/(mL*min)"
    },
    {
      "fact_id": "output_min",
      "value": 0,
      "unit": "ng/mL"
    },
    {
      "fact_id": "output_max",
      "value": 20,
      "unit": "ng/mL"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      216000000,
      1080000,
      1800,
      2
    ],
    "input_delay_s": 0,
    "input_signal_id": "endogenous secretion rates",
    "output_signal_id": "hormone concentrations",
    "input_units": "ng/(mL*min)",
    "output_units": "ng/mL"
  },
  "experiment": {
    "sample_time_s": 12,
    "duration_s": 4800,
    "initial_output": 10,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return endogenous secretion rates to baseline and verify that hormone concentrations remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective hormone concentrations direction with its final direction.",
    "delay": "Measure the time from the logged endogenous secretion rates edge to the first effective hormone concentrations change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log endogenous secretion rates and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 20. Oxytocin-mediated childbirth positive feedback

### Control Problem Description

This is a childbirth feedback system in which contractions stimulate oxytocin release and oxytocin strengthens the contractions. The control input is endogenous oxytocin release, and the measured outputs are oxytocin level, contraction intensity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in oxytocin level starts in its final direction rather than moving the opposite way first; after the input changes, the oxytocin level response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in oxytocin level keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of endogenous oxytocin release changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the oxytocin level, contraction intensity measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use a two-state positive-feedback simulation with oxytocin time constant 30 s, contraction time constant 20 s, and loop product 1.2 before the birth-event switch; set the pressure-feedback gain to zero at 180 s.

For one-pass parsing without an LLM, append this exact fact line to the same submission: `input_change=1 release_unit/min; steady_output_change=1 contraction_unit; response_time_s=30 s; input_min=0 release_unit/min; input_max=5 release_unit/min; output_min=0 contraction_unit; output_max=10 contraction_unit;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 1,
      "unit": "release_unit/min"
    },
    {
      "fact_id": "steady_output_change",
      "value": 1,
      "unit": "contraction_unit"
    },
    {
      "fact_id": "response_time_s",
      "value": 30,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "release_unit/min"
    },
    {
      "fact_id": "input_max",
      "value": 5,
      "unit": "release_unit/min"
    },
    {
      "fact_id": "output_min",
      "value": 0,
      "unit": "contraction_unit"
    },
    {
      "fact_id": "output_max",
      "value": 10,
      "unit": "contraction_unit"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      30,
      1
    ],
    "denominator": [
      600,
      50,
      -0.2
    ],
    "input_delay_s": 0,
    "input_signal_id": "endogenous oxytocin release",
    "output_signal_id": "oxytocin level",
    "input_units": "release_unit/min",
    "output_units": "contraction_unit"
  },
  "experiment": {
    "sample_time_s": 0.6,
    "duration_s": 240,
    "initial_output": 5,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "event": {
    "time_s": 180,
    "pressure_feedback_gain_after_event": 0
  },
  "eight_segment_evidence": {
    "stability": "Return endogenous oxytocin release to baseline and verify that oxytocin level, contraction intensity remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective oxytocin level, contraction intensity direction with its final direction.",
    "delay": "Measure the time from the logged endogenous oxytocin release edge to the first effective oxytocin level, contraction intensity change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log endogenous oxytocin release and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 21. First-order automobile cruise dynamics

### Control Problem Description

This is a longitudinal vehicle model that combines vehicle mass, propulsion, and speed-dependent resistance. The control input is longitudinal drive force, and the measured outputs are vehicle speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in vehicle speed starts in its final direction rather than moving the opposite way first; after the input changes, the vehicle speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the vehicle speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in longitudinal drive force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the vehicle speed measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for vehicle speed.

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

### Example Data (Natural Language)

Use vehicle mass 1000 kg, viscous drag 50 N*s/m, and a 500 N force step. The force-to-speed DC gain is 0.02 (m/s)/N, the time constant is 20 s, and the predicted final speed change is 10 m/s.

Without an LLM, append this exact fact line to the same submission: `input_change=500 N; steady_output_change=10 m/s; response_time_s=20 s; input_min=-2000 N; input_max=4000 N; output_min=0 m/s; output_max=50 m/s;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 500,
      "unit": "N"
    },
    {
      "fact_id": "steady_output_change",
      "value": 10,
      "unit": "m/s"
    },
    {
      "fact_id": "response_time_s",
      "value": 20,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -2000,
      "unit": "N"
    },
    {
      "fact_id": "input_max",
      "value": 4000,
      "unit": "N"
    },
    {
      "fact_id": "output_min",
      "value": 0,
      "unit": "m/s"
    },
    {
      "fact_id": "output_max",
      "value": 50,
      "unit": "m/s"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.001
    ],
    "denominator": [
      1,
      0.05
    ],
    "input_delay_s": 0,
    "input_signal_id": "longitudinal drive force",
    "output_signal_id": "vehicle speed",
    "input_units": "N",
    "output_units": "m/s"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 120,
    "initial_output": 25,
    "input_amplitudes": [
      -500,
      -250,
      250,
      500
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return longitudinal drive force to baseline and verify that vehicle speed remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective vehicle speed direction with its final direction.",
    "delay": "Measure from the logged longitudinal drive force edge to the first effective vehicle speed sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log longitudinal drive force and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 22. Quarter-car road-input two-mass suspension

### Control Problem Description

This is a quarter-car apparatus with body and wheel masses connected by suspension springs and dampers. The control input is prescribed road-displacement test input, and the measured outputs are body displacement, wheel displacement, and suspension travel, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in body displacement starts in its final direction rather than moving the opposite way first; after the input changes, the body displacement response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the body displacement response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed road-displacement test input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the body displacement, wheel displacement, and suspension travel measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for body displacement.

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

### Example Data (Natural Language)

Use sprung mass 375 kg, wheel mass 20 kg, suspension stiffness 130000 N/m, tire stiffness 1000000 N/m, and damping 9800 N*s/m. Apply bounded 0.01, 0.025, and 0.05 m road steps and record body displacement, wheel displacement, and suspension travel at 1 ms.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1310000,
      17423000
    ],
    "denominator": [
      1,
      516.1,
      56850,
      1307000,
      17330000
    ],
    "input_delay_s": 0,
    "input_signal_id": "prescribed road-displacement test input",
    "output_signal_id": "body displacement",
    "input_units": "m",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -0.05,
      -0.025,
      0.025,
      0.05
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "physical_parameters": {
    "sprung_mass_kg": 375,
    "wheel_mass_kg": 20,
    "suspension_stiffness_N_per_m": 130000,
    "tire_stiffness_N_per_m": 1000000,
    "damping_N_s_per_m": 9800
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed road-displacement test input to baseline and verify that body displacement, wheel displacement, and suspension travel remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective body displacement, wheel displacement, and suspension travel direction with its final direction.",
    "delay": "Measure from the logged prescribed road-displacement test input edge to the first effective body displacement, wheel displacement, and suspension travel sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed road-displacement test input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 23. Rigid-satellite single-axis attitude

### Control Problem Description

This is a rigid spacecraft body equipped with a single-axis attitude actuator. The control input is thruster force or body torque, and the measured outputs are attitude angle, angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first; after the input changes, the attitude angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in thruster force or body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the attitude angle, angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use a single-axis inertia of 1200 kg*m^2. A 12 Nm torque change gives 0.01 rad/s^2 angular acceleration; keep torque within +/-50 Nm and attitude within +/-0.2 rad.

Without an LLM, append this exact fact line to the same submission: `input_change=12 Nm; acceleration_change=0.01 rad/s^2; motion_time_scale_s=20 s; input_min=-50 Nm; input_max=50 Nm; output_min=-0.2 undefined; output_max=0.2 undefined;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 12,
      "unit": "Nm"
    },
    {
      "fact_id": "acceleration_change",
      "value": 0.01,
      "unit": "rad/s^2"
    },
    {
      "fact_id": "motion_time_scale_s",
      "value": 20,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -50,
      "unit": "Nm"
    },
    {
      "fact_id": "input_max",
      "value": 50,
      "unit": "Nm"
    },
    {
      "fact_id": "output_min",
      "value": -0.2
    },
    {
      "fact_id": "output_max",
      "value": 0.2
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.0008333333333333334
    ],
    "denominator": [
      1,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "thruster force or body torque",
    "output_signal_id": "attitude angle",
    "input_units": "Nm"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 40,
    "initial_output": 0,
    "input_amplitudes": [
      -12,
      -6,
      6,
      12
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return thruster force or body torque to baseline and verify that attitude angle, angular rate remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective attitude angle, angular rate direction with its final direction.",
    "delay": "Measure from the logged thruster force or body torque edge to the first effective attitude angle, angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log thruster force or body torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 24. Flexible-satellite collocated/noncollocated model

### Control Problem Description

This is a satellite structure made from two rigid bodies joined by a flexible element, with torque and angle sensing available at different locations. The control input is body torque on the main inertia, and the measured outputs are both body angles and rates, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in both body angles starts in its final direction rather than moving the opposite way first; after the input changes, the both body angles response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the both body angles response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body torque on the main inertia produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the both body angles and rates measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use main-body inertia 800 kg*m^2, remote inertia 200 kg*m^2, torsional stiffness 80 Nm/rad, and torsional damping 2 Nm*s/rad. Apply +/-5 and +/-10 Nm torque pulses and log both angles and rates at 0.01 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        1,
        0,
        0
      ],
      [
        -0.1,
        -0.0025,
        0.1,
        0.0025
      ],
      [
        0,
        0,
        0,
        1
      ],
      [
        0.4,
        0.01,
        -0.4,
        -0.01
      ]
    ],
    "b": [
      [
        0
      ],
      [
        0.00125
      ],
      [
        0
      ],
      [
        0
      ]
    ],
    "c": [
      [
        1,
        0,
        0,
        0
      ],
      [
        0,
        0,
        1,
        0
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "body_angle",
      "body_rate",
      "instrument_angle",
      "instrument_rate"
    ],
    "input_signal_ids": [
      "body torque on the main inertia"
    ],
    "output_signal_ids": [
      "both body angles and rates channel 1",
      "both body angles and rates channel 2"
    ],
    "initial_state": [
      0,
      0,
      0,
      0
    ],
    "signal_units": {
      "main-body torque": "Nm",
      "main-body attitude": "rad",
      "remote instrument attitude": "rad"
    },
    "parameter_uncertainty": {
      "inertias": 0.1,
      "flexible_stiffness": 0.1,
      "damping": 0.1
    }
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 60,
    "initial_output": 0,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return body torque on the main inertia to baseline and verify that both body angles and rates remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective both body angles and rates direction with its final direction.",
    "delay": "Measure from the logged body torque on the main inertia edge to the first effective both body angles and rates sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log body torque on the main inertia and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 25. Quadrotor roll/pitch/yaw allocation

### Control Problem Description

This is a quadrotor whose four thrust-producing rotors create roll, pitch, and yaw moments through differential thrust. The control inputs are four rotor thrust perturbations, and the measured outputs are roll, pitch, and yaw response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in roll starts in its final direction rather than moving the opposite way first; after the input changes, the roll response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the roll response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in four rotor thrust perturbations produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the roll, pitch, and yaw response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

### Observable Outputs

roll, pitch, and yaw response

### Actuators

four rotor thrust perturbations, rotor 1 torque perturbation, rotor 2 torque perturbation, rotor 3 torque perturbation, rotor 4 torque perturbation

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

### Example Data (Natural Language)

Use roll and pitch inertia 0.02 kg*m^2 and yaw inertia 0.05 kg*m^2. Use four signed rotor-torque deviations limited to +/-0.1 Nm; excite the roll, pitch, and yaw mixer columns separately.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        1,
        0,
        0,
        0,
        0
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0
      ],
      [
        0,
        0,
        0,
        1,
        0,
        0
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0
      ],
      [
        0,
        0,
        0,
        0,
        0,
        1
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0
      ]
    ],
    "b": [
      [
        0,
        0,
        0,
        0
      ],
      [
        50,
        -50,
        -50,
        50
      ],
      [
        0,
        0,
        0,
        0
      ],
      [
        50,
        50,
        -50,
        -50
      ],
      [
        0,
        0,
        0,
        0
      ],
      [
        20,
        -20,
        20,
        -20
      ]
    ],
    "c": [
      [
        1,
        0,
        0,
        0,
        0,
        0
      ],
      [
        0,
        0,
        1,
        0,
        0,
        0
      ],
      [
        0,
        0,
        0,
        0,
        1,
        0
      ]
    ],
    "d": [
      [
        0,
        0,
        0,
        0
      ],
      [
        0,
        0,
        0,
        0
      ],
      [
        0,
        0,
        0,
        0
      ]
    ],
    "state_names": [
      "roll",
      "roll_rate",
      "pitch",
      "pitch_rate",
      "yaw",
      "yaw_rate"
    ],
    "input_signal_ids": [
      "rotor 1 torque perturbation",
      "rotor 2 torque perturbation",
      "rotor 3 torque perturbation",
      "rotor 4 torque perturbation"
    ],
    "output_signal_ids": [
      "roll",
      "pitch",
      "yaw response"
    ],
    "initial_state": [
      0,
      0,
      0,
      0,
      0,
      0
    ],
    "signal_units": {
      "rotor_1_torque": "Nm",
      "rotor_2_torque": "Nm",
      "rotor_3_torque": "Nm",
      "rotor_4_torque": "Nm",
      "roll angle": "rad",
      "pitch angle": "rad",
      "yaw angle": "rad"
    },
    "parameter_uncertainty": {
      "inertias": 0.1,
      "mixer_effectiveness": 0.1
    }
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -0.02,
      -0.01,
      0.01,
      0.02
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return four rotor thrust perturbations to baseline and verify that roll, pitch, and yaw response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective roll, pitch, and yaw response direction with its final direction.",
    "delay": "Measure from the logged four rotor thrust perturbations edge to the first effective roll, pitch, and yaw response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log four rotor thrust perturbations and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 26. Pendulum nonlinear model, small-angle linearization, and nonlinear simulation

### Control Problem Description

This is a pendulum apparatus in which a concentrated mass is attached to a fixed pivot by a rigid link. The control input is pivot torque, and the measured outputs are pendulum angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first; after the input changes, the pendulum angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the pendulum angle response settles or remains bounded instead of developing self-growing motion. As the size or operating point of pivot torque changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the pendulum angle and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use mass 1 kg, length 1 m, gravity 9.81 m/s^2, and compare 1 Nm and 4 Nm torque steps for 10 s at 0.02 s sampling in both the sine model and its small-angle model.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      0,
      9.81
    ],
    "input_delay_s": 0,
    "input_signal_id": "pivot torque",
    "output_signal_id": "pendulum angle and angular rate",
    "input_units": "Nm",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -4,
      -1,
      1,
      4
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "nonlinear_equation": "theta_ddot=-9.81*sin(theta)+torque",
  "linear_equation": "theta_ddot=-9.81*theta+torque",
  "eight_segment_evidence": {
    "stability": "Return pivot torque to baseline and verify that pendulum angle and angular rate remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pendulum angle and angular rate direction with its final direction.",
    "delay": "Measure from the logged pivot torque edge to the first effective pendulum angle and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log pivot torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 27. Hanging-crane and inverted-pendulum coupled model

### Control Problem Description

This is a rail-mounted cart coupled to either a hanging or an upright pendulum. The control input is cart force, and the measured outputs are cart position, pendulum angle, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in cart position first moves in an unfavorable or opposite direction before turning; after the input changes, the cart position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. Even after the input returns to baseline, the deviation in cart position keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of cart force changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the cart position, pendulum angle measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there are fewer independent actuators than controlled coordinates, so some coordinates move only through coupling. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use trolley mass 1 kg, pendulum mass 0.2 kg, center-of-mass length 0.5 m, inertia 0.006 kg*m^2, friction 0.1 N*s/m, force limit 20 N, travel limit 1.5 m, and an initial 0.05 rad angle.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "registered_nonlinear",
    "template_id": "underactuated_cartpole",
    "parameters": {
      "cart_mass_kg": 1,
      "pole_mass_kg": 0.2,
      "com_length_m": 0.5,
      "pole_inertia_kg_m2": 0.006,
      "cart_friction_n_s_m": 0.1,
      "gravity_m_s2": 9.81,
      "force_limit_n": 20,
      "cart_position_limit_m": 1.5
    },
    "initial_state": {
      "position_m": 0,
      "velocity_m_s": 0,
      "angle_rad": 0.05,
      "angular_rate_rad_s": 0
    },
    "input_signal_ids": [
      "cart force"
    ],
    "output_signal_ids": [
      "cart position",
      "pendulum angle"
    ],
    "signal_units": {
      "trolley force": "N",
      "trolley position": "m",
      "pendulum angle": "rad"
    },
    "parameter_uncertainty": {
      "cart_mass_kg": 0.1,
      "pole_mass_kg": 0.1,
      "com_length_m": 0.1
    }
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -5,
      -2.5,
      2.5,
      5
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return cart force to baseline and verify that cart position, pendulum angle remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective cart position, pendulum angle direction with its final direction.",
    "delay": "Measure from the logged cart force edge to the first effective cart position, pendulum angle sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log cart force and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 28. Bridged-tee RC circuit

### Control Problem Description

This is a passive bridged electrical network made from resistors and capacitors. The control input is input voltage, and the measured outputs are output and capacitor voltages, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output starts in its final direction rather than moving the opposite way first; after the input changes, the output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the output and capacitor voltages measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output.

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

### Example Data (Natural Language)

Set R1=R2=10 kohm and C1=C2=10 uF, giving G(s)=(0.01 s^2+0.2 s+1)/(0.01 s^2+0.3 s+1). Use +/-1 V tests to verify the unity low- and high-frequency gains and the bridged mid-band response.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.01,
      0.2,
      1
    ],
    "denominator": [
      0.01,
      0.3,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "input voltage",
    "output_signal_id": "output and capacitor voltages",
    "input_units": "V",
    "output_units": "V"
  },
  "experiment": {
    "sample_time_s": 0.0005,
    "duration_s": 1,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "physical_parameters": {
    "R1_ohm": 10000,
    "R2_ohm": 10000,
    "C1_F": 1e-05,
    "C2_F": 1e-05
  },
  "eight_segment_evidence": {
    "stability": "Return input voltage to baseline and verify that output and capacitor voltages remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective output and capacitor voltages direction with its final direction.",
    "delay": "Measure from the logged input voltage edge to the first effective output and capacitor voltages sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log input voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 29. Current-driven RLC circuit

### Control Problem Description

This is a current-driven energy-storage circuit containing a resistor, an inductor, and two capacitors. The control input is source current, and the measured outputs are two capacitor voltages and inductor current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in two capacitor voltages starts in its final direction rather than moving the opposite way first; after the input changes, the two capacitor voltages response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the two capacitor voltages response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in source current produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the two capacitor voltages and inductor current measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for two capacitor voltages.

### Observable Outputs

capacitor voltage 1, capacitor voltage 2, inductor current

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

### Example Data (Natural Language)

Use R1=R2=10 ohm, C1=C2=0.01 F, and L=0.1 H, with a 0.1 A bounded current step and all capacitor voltages plus inductor current logged.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        -10,
        0,
        -100
      ],
      [
        0,
        -10,
        100
      ],
      [
        10,
        -10,
        0
      ]
    ],
    "b": [
      [
        100
      ],
      [
        0
      ],
      [
        0
      ]
    ],
    "c": [
      [
        1,
        0,
        0
      ],
      [
        0,
        1,
        0
      ],
      [
        0,
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "capacitor_voltage_1",
      "capacitor_voltage_2",
      "inductor_current"
    ],
    "input_signal_ids": [
      "source current"
    ],
    "output_signal_ids": [
      "capacitor voltage 1",
      "capacitor voltage 2",
      "inductor current"
    ],
    "initial_state": [
      0,
      0,
      0
    ],
    "signal_units": {
      "capacitor_voltage_1": "V",
      "capacitor_voltage_2": "V",
      "inductor_current": "A",
      "source_current": "A"
    }
  },
  "experiment": {
    "sample_time_s": 0.0002,
    "duration_s": 2,
    "initial_output": 0,
    "input_amplitudes": [
      -0.1,
      -0.05,
      0.05,
      0.1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "physical_parameters": {
    "R1_ohm": 10,
    "R2_ohm": 10,
    "C1_F": 0.01,
    "C2_F": 0.01,
    "L_H": 0.1
  },
  "eight_segment_evidence": {
    "stability": "Return source current to baseline and verify that two capacitor voltages and inductor current remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective two capacitor voltages and inductor current direction with its final direction.",
    "delay": "Measure from the logged source current edge to the first effective two capacitor voltages and inductor current sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log source current and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 30. Ideal op-amp weighted summer

### Control Problem Description

This is a weighted summing circuit made from an ideal operational amplifier and several input-resistor branches. The control input is input voltages, and the measured outputs are summed output voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in summed output voltage starts in its final direction rather than moving the opposite way first; after the input changes, the summed output voltage response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the summed output voltage response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input voltages produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the summed output voltage measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for summed output voltage.

### Observable Outputs

summed output voltage

### Actuators

input voltages, input voltage 1, input voltage 2

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

### Example Data (Natural Language)

Choose Rf=20 kohm, R1=10 kohm, and R2=20 kohm, giving vout=-2 v1-v2; limit each input to +/-5 V and the output to +/-12 V.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        -1000
      ]
    ],
    "b": [
      [
        2000,
        1000
      ]
    ],
    "c": [
      [
        -1
      ]
    ],
    "d": [
      [
        0,
        0
      ]
    ],
    "state_names": [
      "amplifier_output_state"
    ],
    "input_signal_ids": [
      "input voltage 1",
      "input voltage 2"
    ],
    "output_signal_ids": [
      "summed output voltage"
    ],
    "initial_state": [
      0
    ],
    "signal_units": {
      "input_v1": "V",
      "input_v2": "V",
      "summer output voltage": "V"
    },
    "parameter_uncertainty": {
      "resistor_ratios": 0.1
    }
  },
  "experiment": {
    "sample_time_s": 1e-05,
    "duration_s": 0.02,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return input voltages to baseline and verify that summed output voltage remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective summed output voltage direction with its final direction.",
    "delay": "Measure from the logged input voltages edge to the first effective summed output voltage sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log input voltages and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 31. Ideal op-amp integrator

### Control Problem Description

This is an analog integrator made from an operational amplifier, an input resistor, and a feedback capacitor. The control input is input voltage, and the measured outputs are integrator output voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in integrator output voltage starts in its final direction rather than moving the opposite way first; after the input changes, the integrator output voltage response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the integrator output voltage response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in input voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the integrator output voltage measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for integrator output voltage.

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

### Example Data (Natural Language)

Use Rin=100 kohm and C=10 uF so Rin*C=1 s. A +1 V input produces a -1 V/s output slope; stop before the output reaches +/-10 V.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -1
    ],
    "denominator": [
      1,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "input voltage",
    "output_signal_id": "integrator output voltage",
    "input_units": "V",
    "output_units": "V"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 5,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return input voltage to baseline and verify that integrator output voltage remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective integrator output voltage direction with its final direction.",
    "delay": "Measure from the logged input voltage edge to the first effective integrator output voltage sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log input voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 32. Loudspeaker electromechanical model with drive circuit

### Control Problem Description

This is an electromechanical loudspeaker made from a voice coil, its drive circuit, and a compliant cone. The control input is amplifier voltage, and the measured outputs are cone displacement, coil current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in cone displacement starts in its final direction rather than moving the opposite way first; after the input changes, the cone displacement response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the cone displacement response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in amplifier voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the cone displacement, coil current measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use magnetic flux 0.5 T, 20 turns at 2 cm diameter so Bl=0.63 N/A, together with M=0.02 kg, b=0.2 N*s/m, L=1 mH, and R=8 ohm.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.63
    ],
    "denominator": [
      2e-05,
      0.1602,
      1.9969,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "amplifier voltage",
    "output_signal_id": "cone displacement",
    "input_units": "V",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 5e-05,
    "duration_s": 2,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return amplifier voltage to baseline and verify that cone displacement, coil current remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective cone displacement, coil current direction with its final direction.",
    "delay": "Measure from the logged amplifier voltage edge to the first effective cone displacement, coil current sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log amplifier voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 33. DC-motor position and speed models

### Control Problem Description

This is a DC-motor drive made from an armature circuit, rotor inertia, and a viscous mechanical load. The control input is armature voltage, and the measured outputs are motor position, speed, armature current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position, speed, armature current measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use J=0.01 kg*m^2, b=0.1 Nm*s/rad, Kt=Ke=0.01, R=1 ohm, and L=0.5 H; test +/-1 V and log current, speed, and position.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.01
    ],
    "denominator": [
      0.005,
      0.06,
      0.1001,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "armature voltage",
    "output_signal_id": "motor position",
    "input_units": "V",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.0005,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return armature voltage to baseline and verify that motor position, speed, armature current remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position, speed, armature current direction with its final direction.",
    "delay": "Measure from the logged armature voltage edge to the first effective motor position, speed, armature current sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log armature voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 34. Gear-train torque multiplication and reflected inertia

### Control Problem Description

This is a rotary transmission made from a motor, gears, an elastic shaft, and a load inertia. The control input is motor torque, and the measured outputs are motor and load angle, shaft torque, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor starts in its final direction rather than moving the opposite way first; after the input changes, the motor response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in motor torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor and load angle, shaft torque measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use gear ratio n=4, motor-side inertia J1=0.002 kg*m^2, load inertia J2=0.03 kg*m^2, b1=0.001 and b2=0.02 Nm*s/rad.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4
    ],
    "denominator": [
      0.062,
      0.036,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "motor torque",
    "output_signal_id": "motor and load angle",
    "input_units": "Nm",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return motor torque to baseline and verify that motor and load angle, shaft torque remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor and load angle, shaft torque direction with its final direction.",
    "delay": "Measure from the logged motor torque edge to the first effective motor and load angle, shaft torque sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log motor torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 35. Room heat-loss model

### Control Problem Description

This is a room thermal system whose indoor air stores heat while the enclosure loses heat to the outdoors. The control input is heating rate in the labeled control extension, and the measured outputs are room temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in room temperature starts in its final direction rather than moving the opposite way first; after the input changes, the room temperature response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the room temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heating rate in the labeled control extension produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the room temperature measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use furnace rating 90000 Btu/h. At outdoor temperature 32 degF and indoor temperature 60 degF, heating raises temperature 2 degF in 0.1 h, while furnace-off cooling lowers it 2 degF in 40 min. These measurements give C=3913.04 Btu/degF and R=0.002385 degF/(Btu/h).

Without an LLM, append this exact fact line to the same submission: `input_change=1 binary_command; steady_output_change=214.6597 degF; response_time_s=33600 s; input_min=0 binary_command; input_max=1 binary_command; output_min=32 degF; output_max=90 degF;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 1,
      "unit": "binary_command"
    },
    {
      "fact_id": "steady_output_change",
      "value": 214.6597,
      "unit": "degF"
    },
    {
      "fact_id": "response_time_s",
      "value": 33600,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "binary_command"
    },
    {
      "fact_id": "input_max",
      "value": 1,
      "unit": "binary_command"
    },
    {
      "fact_id": "output_min",
      "value": 32,
      "unit": "degF"
    },
    {
      "fact_id": "output_max",
      "value": 90,
      "unit": "degF"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      214.6597
    ],
    "denominator": [
      33600,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "heating rate in the labeled control extension",
    "output_signal_id": "room temperature",
    "input_units": "binary_command",
    "output_units": "degF"
  },
  "experiment": {
    "sample_time_s": 60,
    "duration_s": 120000,
    "initial_output": 61,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "physical_parameters": {
    "furnace_rating_Btu_per_h": 90000,
    "heat_capacity_Btu_per_degF": 3913.043478,
    "thermal_resistance_degF_per_Btu_per_h": 0.002385185
  },
  "eight_segment_evidence": {
    "stability": "Return heating rate in the labeled control extension to baseline and verify that room temperature remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective room temperature direction with its final direction.",
    "delay": "Measure from the logged heating rate in the labeled control extension edge to the first effective room temperature sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log heating rate in the labeled control extension and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 36. Two-thermal-mass controlled process

### Control Problem Description

This is a temperature process made from a heater and two thermal masses that exchange heat with one another. The control input is heater power, and the measured outputs are two body temperatures, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in two body temperatures starts in its final direction rather than moving the opposite way first; after the input changes, the two body temperatures response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the two body temperatures response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heater power produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the two body temperatures measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use C1=10000 J/degC, C2=15000 J/degC, Hx=200 W/degC, H1=100 W/degC, and H2=150 W/degC; apply 250, 500, 750, and 1000 W heat steps.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      200
    ],
    "denominator": [
      150000000,
      8000000,
      105000
    ],
    "input_delay_s": 0,
    "input_signal_id": "heater power",
    "output_signal_id": "two body temperatures",
    "input_units": "W",
    "output_units": "degC"
  },
  "experiment": {
    "sample_time_s": 0.2,
    "duration_s": 1000,
    "initial_output": 67.5,
    "input_amplitudes": [
      -1000,
      -500,
      500,
      1000
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return heater power to baseline and verify that two body temperatures remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective two body temperatures direction with its final direction.",
    "delay": "Measure from the logged heater power edge to the first effective two body temperatures sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log heater power and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 37. Heat exchanger with nonlinear valve and measurement delay

### Control Problem Description

This is a heat-exchanger process with a steam valve, two dominant thermal lags, and a temperature-measurement element. The control input is steam inlet valve area, and the measured outputs are measured outlet water temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured outlet water temperature starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the measured outlet water temperature response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of steam inlet valve area reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the measured outlet water temperature measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use a two-lag model with 30 s and 60 s thermal time constants, DC gain 0.5 degC/%, and 10 s downstream measurement delay. Test 2.5%, 5%, 7.5%, and 10% valve changes.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.5
    ],
    "denominator": [
      1800,
      90,
      1
    ],
    "input_delay_s": 10,
    "input_signal_id": "steam inlet valve area",
    "output_signal_id": "measured outlet water temperature",
    "input_units": "%",
    "output_units": "degC"
  },
  "experiment": {
    "sample_time_s": 0.2,
    "duration_s": 800,
    "initial_output": 60,
    "input_amplitudes": [
      -10,
      -5,
      5,
      10
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return steam inlet valve area to baseline and verify that measured outlet water temperature remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective measured outlet water temperature direction with its final direction.",
    "delay": "Measure from the logged steam inlet valve area edge to the first effective measured outlet water temperature sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log steam inlet valve area and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 38. Water-tank continuity, square-root outflow, and operating-point linearization

### Control Problem Description

This is a storage tank that receives inlet flow and drains through an outlet whose flow follows the square root of liquid level. The control input is inlet mass flow, and the measured outputs are tank level and outlet flow, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tank level starts in its final direction rather than moving the opposite way first; after the input changes, the tank level response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the tank level response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of inlet mass flow reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the tank level and outlet flow measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use water density 1000 kg/m^3, tank area 0.05 m^2, nominal height 0.15 m, and nominal outflow 200 g/min; linearize the square-root outlet law and test +/-25 and +/-50 g/min pump-flow changes.

Without an LLM, append this exact fact line to the same submission: `input_change=50 g/min; steady_output_change=0.1 m; response_time_s=120 s; input_min=0 g/min; input_max=500 g/min; output_min=0 m; output_max=0.5 m;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 50,
      "unit": "g/min"
    },
    {
      "fact_id": "steady_output_change",
      "value": 0.1,
      "unit": "m"
    },
    {
      "fact_id": "response_time_s",
      "value": 120,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "g/min"
    },
    {
      "fact_id": "input_max",
      "value": 500,
      "unit": "g/min"
    },
    {
      "fact_id": "output_min",
      "value": 0,
      "unit": "m"
    },
    {
      "fact_id": "output_max",
      "value": 0.5,
      "unit": "m"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.002
    ],
    "denominator": [
      120,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "inlet mass flow",
    "output_signal_id": "tank level and outlet flow",
    "input_units": "g/min",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 1,
    "duration_s": 900,
    "initial_output": 0.25,
    "input_amplitudes": [
      -50,
      -25,
      25,
      50
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "operating_condition": {
    "density_kg_per_m3": 1000,
    "tank_area_m2": 0.05,
    "nominal_height_m": 0.15,
    "nominal_outflow_g_per_min": 200
  },
  "eight_segment_evidence": {
    "stability": "Return inlet mass flow to baseline and verify that tank level and outlet flow remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective tank level and outlet flow direction with its final direction.",
    "delay": "Measure from the logged inlet mass flow edge to the first effective tank level and outlet flow sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log inlet mass flow and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 39. Pressure-driven hydraulic piston

### Control Problem Description

This is a hydraulic actuator in which chamber pressure drives a piston and its attached mechanical load. The control input is chamber pressure difference, and the measured outputs are piston position and velocity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in piston position starts in its final direction rather than moving the opposite way first; after the input changes, the piston position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the piston position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in chamber pressure difference produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the piston position and velocity measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use piston mass 50 kg and area 0.01 m^2. A 100 kPa chamber-pressure change gives 1000 N and 20 m/s^2 initial acceleration; limit displacement to +/-0.5 m.

Without an LLM, append this exact fact line to the same submission: `input_change=100 kPa; acceleration_change=20 m/s^2; motion_time_scale_s=2 s; input_min=0 kPa; input_max=500 kPa; output_min=-0.5 undefined; output_max=0.5 undefined;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 100,
      "unit": "kPa"
    },
    {
      "fact_id": "acceleration_change",
      "value": 20,
      "unit": "m/s^2"
    },
    {
      "fact_id": "motion_time_scale_s",
      "value": 2,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": 0,
      "unit": "kPa"
    },
    {
      "fact_id": "input_max",
      "value": 500,
      "unit": "kPa"
    },
    {
      "fact_id": "output_min",
      "value": -0.5
    },
    {
      "fact_id": "output_max",
      "value": 0.5
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.2
    ],
    "denominator": [
      1,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "chamber pressure difference",
    "output_signal_id": "piston position and velocity",
    "input_units": "kPa"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 3,
    "initial_output": 0,
    "input_amplitudes": [
      -100,
      -50,
      50,
      100
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "physical_parameters": {
    "mass_kg": 50,
    "piston_area_m2": 0.01,
    "load_force_N": 0
  },
  "eight_segment_evidence": {
    "stability": "Return chamber pressure difference to baseline and verify that piston position and velocity remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective piston position and velocity direction with its final direction.",
    "delay": "Measure from the logged chamber pressure difference edge to the first effective piston position and velocity sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log chamber pressure difference and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 40. Hydraulic control-surface actuator and load-dependent integrator model

### Control Problem Description

This is a hydraulic position actuator made from a servo valve, cylinder, and externally loaded control surface. The control input is servo valve displacement, and the measured outputs are surface angle and load force, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in surface angle starts in its final direction rather than moving the opposite way first; after the input changes, the surface angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the surface angle response retains an offset or keeps drifting rather than returning through its own restoring action. As the size or operating point of servo valve displacement changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the surface angle and load force measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use a no-load local valve-to-angle-rate gain of 0.8 rad/(s*mm), valve travel +/-5 mm, and angle limit +/-0.5 rad. Repeat with load reducing the gain to 0.72 and 0.64 rad/(s*mm).

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.8
    ],
    "denominator": [
      1,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "servo valve displacement",
    "output_signal_id": "surface angle and load force",
    "input_units": "mm",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 3,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return servo valve displacement to baseline and verify that surface angle and load force remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective surface angle and load force direction with its final direction.",
    "delay": "Measure from the logged servo valve displacement edge to the first effective surface angle and load force sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log servo valve displacement and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 41. Test linearity and time invariance by superposition and shift

### Control Problem Description

This is a repeatable input-output test bench built around one dynamic plant, with timing preserved so shifted and combined excitations can be compared. The control input is prescribed test signal, and the measured outputs are system output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in system output response starts in its final direction rather than moving the opposite way first; after the input changes, the system output response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the system output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed test signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the system output response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for system output response.

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

### Example Data (Natural Language)

Set k=2 s^-1. Use u1(t)=1, u2(t)=sin(t), coefficients 1.5 and -0.5, and a 1 s shift; sample at 0.01 s for 8 s and compare superposed and shifted responses.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      2
    ],
    "input_delay_s": 0,
    "input_signal_id": "prescribed test signal",
    "output_signal_id": "system output response",
    "input_units": "unit/s",
    "output_units": "unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed test signal to baseline and verify that system output response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective system output response direction with its final direction.",
    "delay": "Measure from the logged prescribed test signal edge to the first effective system output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed test signal and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 42. Derive a first-order impulse response and arbitrary-input convolution

### Control Problem Description

This is a stable first-order dynamic element connected to an input generator and a continuous output recorder. The control input is input signal, and the measured outputs are output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output response starts in its final direction rather than moving the opposite way first; after the input changes, the output response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the output response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output response.

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

### Example Data (Natural Language)

Use k=0.5 s^-1. Simulate a unit impulse and a unit step at 0.01 s resolution for 16 s, then compare direct integration with convolution by exp(-0.5 t).

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      0.5
    ],
    "input_delay_s": 0,
    "input_signal_id": "input signal",
    "output_signal_id": "output response",
    "input_units": "impulse_unit",
    "output_units": "unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 16,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return input signal to baseline and verify that output response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective output response direction with its final direction.",
    "delay": "Measure from the logged input signal edge to the first effective output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log input signal and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 43. Convert an ODE to a transfer function under zero initial conditions

### Control Problem Description

This is a dynamic plant governed by a linear differential equation, with an external forcing port and a measured response channel. The control input is prescribed forcing signal, and the measured outputs are system output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in system output response starts in its final direction rather than moving the opposite way first; after the input changes, the system output response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the system output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed forcing signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the system output response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for system output response.

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

### Example Data (Natural Language)

Use y_ddot+5 y_dot+4 y=2 u with zero initial conditions. Apply +/-0.5 and +/-1 N steps, sample at 0.01 s for 8 s, and verify G(s)=2/(s^2+5s+4).

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2
    ],
    "denominator": [
      1,
      5,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "prescribed forcing signal",
    "output_signal_id": "system output response",
    "input_units": "N",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed forcing signal to baseline and verify that system output response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective system output response direction with its final direction.",
    "delay": "Measure from the logged prescribed forcing signal edge to the first effective system output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed forcing signal and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 44. Derive the RC low-pass transfer function and impulse response

### Control Problem Description

This is a resistor-capacitor low-pass circuit whose capacitor stores energy while the resistor dissipates it. The control input is input voltage, and the measured outputs are capacitor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in capacitor voltage starts in its final direction rather than moving the opposite way first; after the input changes, the capacitor voltage response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the capacitor voltage response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the capacitor voltage measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for capacitor voltage.

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

### Example Data (Natural Language)

Use R=10 kohm and C=100 uF, giving RC=1 s. Apply 0.25, 0.5, 0.75, and 1 V steps at 0.01 s sampling for 8 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "input voltage",
    "output_signal_id": "capacitor voltage",
    "input_units": "V",
    "output_units": "V"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return input voltage to baseline and verify that capacitor voltage remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective capacitor voltage direction with its final direction.",
    "delay": "Measure from the logged input voltage edge to the first effective capacitor voltage sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log input voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 45. Compute magnitude and phase of first-order sinusoidal response

### Control Problem Description

This is a stable first-order lag element driven by a sinusoidal source and observed after its transient has decayed. The control input is sinusoidal input, and the measured outputs are sinusoidal output amplitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sinusoidal output amplitude starts in its final direction rather than moving the opposite way first; after the input changes, the sinusoidal output amplitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the sinusoidal output amplitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sinusoidal input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sinusoidal output amplitude and phase measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sinusoidal output amplitude.

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

### Example Data (Natural Language)

Set k=1 s^-1, sinusoidal amplitude 1 V, and omega=10 rad/s. Sample at 0.002 s for 12 s and estimate steady amplitude and phase after the exponential transient.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "sinusoidal input",
    "output_signal_id": "sinusoidal output amplitude and phase",
    "input_units": "V",
    "output_units": "V"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sinusoidal input to baseline and verify that sinusoidal output amplitude and phase remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sinusoidal output amplitude and phase direction with its final direction.",
    "delay": "Measure from the logged sinusoidal input edge to the first effective sinusoidal output amplitude and phase sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sinusoidal input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 46. Transform canonical step, ramp, impulse, and sinusoidal inputs

### Control Problem Description

This is a signal-analysis test bench that applies canonical step, ramp, impulse, and sinusoidal waveforms to a dynamic representation. The control input is canonical test signal, and the measured outputs are transformed system response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in transformed system response starts in its final direction rather than moving the opposite way first; after the input changes, the transformed system response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the transformed system response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in canonical test signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the transformed system response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for transformed system response.

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

### Example Data (Natural Language)

Use G(s)=1/(s+1), step amplitude 2, ramp slope 0.5, unit impulse area 1, and sinusoid omega=3 rad/s. Sample at 0.005 s for 12 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "canonical test signal",
    "output_signal_id": "transformed system response",
    "input_units": "canonical_input",
    "output_units": "unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return canonical test signal to baseline and verify that transformed system response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective transformed system response direction with its final direction.",
    "delay": "Measure from the logged canonical test signal edge to the first effective transformed system response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log canonical test signal and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 47. Recover a time response by partial-fraction expansion

### Control Problem Description

This is a rational dynamic model whose internal modes are reconstructed from a transformed input and a recorded time response. The control input is prescribed transformed input, and the measured outputs are time-domain output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in time-domain output response starts in its final direction rather than moving the opposite way first; after the input changes, the time-domain output response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the time-domain output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed transformed input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the time-domain output response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for time-domain output response.

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

### Example Data (Natural Language)

Use Y(s)=(s+2)(s+4)/[s(s+1)(s+3)]. Simulate a unit impulse at 0.005 s sampling for 12 s and compare residues 8/3, -3/2, and -1/6.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      6,
      8
    ],
    "denominator": [
      1,
      4,
      3,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "prescribed transformed input",
    "output_signal_id": "time-domain output response",
    "input_units": "impulse_unit",
    "output_units": "unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed transformed input to baseline and verify that time-domain output response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective time-domain output response direction with its final direction.",
    "delay": "Measure from the logged prescribed transformed input edge to the first effective time-domain output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed transformed input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 48. Apply the Final Value Theorem and reject invalid unstable use

### Control Problem Description

This is a dynamic plant whose long-time output is checked against the locations of every pole that can influence the response. The control input is test input, and the measured outputs are steady-state output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in steady-state output starts in its final direction rather than moving the opposite way first; after the input changes, the steady-state output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the steady-state output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in test input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the steady-state output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for steady-state output.

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

### Example Data (Natural Language)

Evaluate Y1=3(s+2)/[s(s^2+2s+10)] and Y2=3/[s(s-2)] side by side, using 0.002 s sampling for 8 s and a stop threshold of absolute output 100.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      3,
      6
    ],
    "denominator": [
      1,
      2,
      10,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "test input",
    "output_signal_id": "steady-state output",
    "input_units": "step_unit",
    "output_units": "unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "comparison_model": {
    "kind": "transfer_function",
    "numerator": [
      3
    ],
    "denominator": [
      1,
      -2,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "unstable case input",
    "output_signal_id": "unstable case output",
    "input_units": "step_unit",
    "output_units": "unit"
  },
  "eight_segment_evidence": {
    "stability": "Return test input to baseline and verify that steady-state output remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective steady-state output direction with its final direction.",
    "delay": "Measure from the logged test input edge to the first effective steady-state output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log test input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 49. Compute stable-system DC gain from the transfer function

### Control Problem Description

This is a self-regulating stable plant with a finite static gain between a constant input and its settled output. The control input is unit-step input, and the measured outputs are steady output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in steady output starts in its final direction rather than moving the opposite way first; after the input changes, the steady output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the steady output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in unit-step input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the steady output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for steady output.

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

### Example Data (Natural Language)

Use G(s)=3(s+2)/(s^2+2s+10). Apply step amplitudes 0.25, 0.5, 0.75, and 1, sample at 0.005 s for 12 s, and verify the 0.6 DC gain.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      3,
      6
    ],
    "denominator": [
      1,
      2,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "unit-step input",
    "output_signal_id": "steady output",
    "input_units": "step_unit",
    "output_units": "unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return unit-step input to baseline and verify that steady output remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective steady output direction with its final direction.",
    "delay": "Measure from the logged unit-step input edge to the first effective steady output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log unit-step input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 50. Solve homogeneous and forced ODEs with initial conditions

### Control Problem Description

This is a dynamic state model that can move from stored initial energy as well as from a separately applied external forcing signal. The control input is forcing input and prescribed initial-state release, and the measured outputs are state and output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state starts in its final direction rather than moving the opposite way first; after the input changes, the state response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the state response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in forcing input and prescribed initial-state release produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the state and output response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state.

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

### Example Data (Natural Language)

Use y_ddot+5 y_dot+4 y=u. Run initial states (y0,ydot0)=(1,0) and (0,1), then the zero-initial input u=2 exp(-2t), at 0.005 s for 10 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      5,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "forcing input and prescribed initial-state release",
    "output_signal_id": "state and output response",
    "input_units": "N",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "initial_condition_cases": [
    [
      1,
      0
    ],
    [
      0,
      1
    ]
  ],
  "forced_input": "2*exp(-2*t)",
  "eight_segment_evidence": {
    "stability": "Return forcing input and prescribed initial-state release to baseline and verify that state and output response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective state and output response direction with its final direction.",
    "delay": "Measure from the logged forcing input and prescribed initial-state release edge to the first effective state and output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log forcing input and prescribed initial-state release and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 51. Analyze automobile position dynamics from the cruise model

### Control Problem Description

This is a longitudinal vehicle system whose speed is determined by propulsion, vehicle mass, and road resistance. The control input is drive force, and the measured outputs are vehicle position and speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in vehicle position starts in its final direction rather than moving the opposite way first; after the input changes, the vehicle position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the vehicle position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in drive force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the vehicle position and speed measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for vehicle position.

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

### Example Data (Natural Language)

Use m=1000 kg, b=50 N*s/m, and a 500 N force step. Sample speed and position at 0.05 s for 120 s; position uses Gx=0.001/[s(s+0.05)].

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.001
    ],
    "denominator": [
      1,
      0.05,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "drive force",
    "output_signal_id": "vehicle position and speed",
    "input_units": "N",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 120,
    "initial_output": 0,
    "input_amplitudes": [
      -500,
      -250,
      250,
      500
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return drive force to baseline and verify that vehicle position and speed remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective vehicle position and speed direction with its final direction.",
    "delay": "Measure from the logged drive force edge to the first effective vehicle position and speed sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log drive force and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 52. Analyze DC-motor position and speed poles with numerical parameters

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage, and the measured outputs are motor speed and position, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first; after the input changes, the motor speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor speed response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor speed and position measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.

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

### Example Data (Natural Language)

Use J=0.01 kg*m^2, b=0.001 Nm*s/rad, Kt=Ke=1, Ra=10 ohm, and La=1 H. Test +/-1 V and record current, speed, and angle at 0.001 s for 5 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      100
    ],
    "denominator": [
      1,
      10.1,
      101,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "armature voltage",
    "output_signal_id": "motor speed and position",
    "input_units": "V",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 5,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return armature voltage to baseline and verify that motor speed and position remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor speed and position direction with its final direction.",
    "delay": "Measure from the logged armature voltage edge to the first effective motor speed and position sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log armature voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 53. Predict rigid-satellite response to a finite thrust pulse

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is finite thruster-force pulse, and the measured outputs are attitude angle and rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first; after the input changes, the attitude angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in finite thruster-force pulse produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the attitude angle and rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude angle.

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

### Example Data (Natural Language)

Use lever arm d=1 m and inertia I=5000 kg*m^2. Apply a 25 N pulse from 5.0 to 5.1 s and sample at 0.01 s through 10 s.

Without an LLM, append this exact fact line to the same submission: `input_change=25 N; acceleration_change=0.005 rad/s^2; motion_time_scale_s=10 s; input_min=-50 N; input_max=50 N; output_min=-0.02 output_unit; output_max=0.02 output_unit;`

### Example Data (JSON)

```json
{
  "specification_facts": [
    {
      "fact_id": "input_change",
      "value": 25,
      "unit": "N"
    },
    {
      "fact_id": "acceleration_change",
      "value": 0.005,
      "unit": "rad/s^2"
    },
    {
      "fact_id": "motion_time_scale_s",
      "value": 10,
      "unit": "s"
    },
    {
      "fact_id": "input_min",
      "value": -50,
      "unit": "N"
    },
    {
      "fact_id": "input_max",
      "value": 50,
      "unit": "N"
    },
    {
      "fact_id": "output_min",
      "value": -0.02,
      "unit": "output_unit"
    },
    {
      "fact_id": "output_max",
      "value": 0.02,
      "unit": "output_unit"
    }
  ],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.0002
    ],
    "denominator": [
      1,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "finite thruster-force pulse",
    "output_signal_id": "attitude angle and rate",
    "input_units": "N",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -25,
      -12.5,
      12.5,
      25
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return finite thruster-force pulse to baseline and verify that attitude angle and rate remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective attitude angle and rate direction with its final direction.",
    "delay": "Measure from the logged finite thruster-force pulse edge to the first effective attitude angle and rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log finite thruster-force pulse and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 54. Reduce nested control block diagrams to one transfer function

### Control Problem Description

This is an interconnected feedback system containing reference, controller, plant, sensor, and nested inner-loop signal paths. The control input is reference input, and the measured outputs are closed-loop output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in reference input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.

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

### Example Data (Natural Language)

Use parallel controller branches 2 and 4/s, plant 1/s, and unity negative feedback. Apply +/-0.5 and +/-1 reference steps at 0.005 s for 10 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2,
      4
    ],
    "denominator": [
      1,
      2,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "reference input",
    "output_signal_id": "closed-loop output",
    "input_units": "reference_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return reference input to baseline and verify that closed-loop output remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output direction with its final direction.",
    "delay": "Measure from the logged reference input edge to the first effective closed-loop output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log reference input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 55. Derive a closed-loop transfer function with Mason's signal-flow rule

### Control Problem Description

This is a directed signal-flow network whose branches carry gains among source, internal, feedback, and output nodes. The control input is prescribed source-node signal, and the measured outputs are signal-flow output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in signal-flow output response starts in its final direction rather than moving the opposite way first; after the input changes, the signal-flow output response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the signal-flow output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed source-node signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the signal-flow output response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for signal-flow output response.

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

### Example Data (Natural Language)

Use one forward path P=6 and one signed touching loop L=0.2, so the Mason gain is 6/(1-0.2)=7.5. Repeat after setting the loop to -0.2 and zero.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      6
    ],
    "denominator": [
      1,
      -0.2
    ],
    "input_delay_s": 0,
    "input_signal_id": "prescribed source-node signal",
    "output_signal_id": "signal-flow output response",
    "input_units": "path_input",
    "output_units": "path_output"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed source-node signal to baseline and verify that signal-flow output response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective signal-flow output response direction with its final direction.",
    "delay": "Measure from the logged prescribed source-node signal edge to the first effective signal-flow output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed source-node signal and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 56. Infer transient form and decay rate from pole locations

### Control Problem Description

This is a modal dynamic plant whose free and pulse-driven motion is set by the location of its poles. The control input is bounded impulse test, and the measured outputs are transient output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in transient output response starts in its final direction rather than moving the opposite way first; after the input changes, the transient output response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the transient output response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded impulse test produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the transient output response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for transient output response.

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

### Example Data (Natural Language)

Use H(s)=(2s+1)/(s^2+3s+2). Apply unit signed impulses, sample at 0.005 s for 10 s, and fit the -1 and -2 modes with residues -1 and 3.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2,
      1
    ],
    "denominator": [
      1,
      3,
      2
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded impulse test",
    "output_signal_id": "transient output response",
    "input_units": "impulse_unit",
    "output_units": "unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded impulse test to baseline and verify that transient output response remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective transient output response direction with its final direction.",
    "delay": "Measure from the logged bounded impulse test edge to the first effective transient output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded impulse test and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 57. Map second-order rise time, overshoot, settling time, and peak time to pole regions

### Control Problem Description

This is a damped second-order plant whose dominant pole pair determines rise, peak, overshoot, and settling behavior. The control input is bounded command step, and the measured outputs are step response and its transient features, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in step response starts in its final direction rather than moving the opposite way first; after the input changes, the step response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the step response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded command step produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the step response and its transient features measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for step response.

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

### Example Data (Natural Language)

Use omega_n=3 rad/s and zeta=0.6, with a unit-DC-gain model 9/(s^2+3.6s+9). Sample at 0.002 s for 8 s and measure rise, peak, and 1% settling times.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      9
    ],
    "denominator": [
      1,
      3.6,
      9
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded command step",
    "output_signal_id": "step response and its transient features",
    "input_units": "reference_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.00666666,
    "duration_s": 2.666664,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded command step to baseline and verify that step response and its transient features remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective step response and its transient features direction with its final direction.",
    "delay": "Measure from the logged bounded command step edge to the first effective step response and its transient features sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded command step and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 58. Explain and quantify Boeing 747 nonminimum-phase altitude response

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is impulsive elevator deflection, and the measured outputs are aircraft altitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in aircraft altitude first moves in an unfavorable or opposite direction before turning; after the input changes, the aircraft altitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the aircraft altitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in impulsive elevator deflection produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the aircraft altitude measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use h/delta_e=30(s-6)/[s(s^2+4s+13)] with a -1 deg impulsive elevator input. Sample at 0.002 s for 12 s and retain the initial altitude dip and final offset.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -30,
      180
    ],
    "denominator": [
      1,
      4,
      13,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "impulsive elevator deflection",
    "output_signal_id": "aircraft altitude",
    "input_units": "deg",
    "output_units": "ft"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 4,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return impulsive elevator deflection to baseline and verify that aircraft altitude remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective aircraft altitude direction with its final direction.",
    "delay": "Measure from the logged impulsive elevator deflection edge to the first effective aircraft altitude sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log impulsive elevator deflection and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 59. Test BIBO stability of a current-driven capacitor

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is bounded source current, and the measured outputs are capacitor voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in capacitor voltage starts in its final direction rather than moving the opposite way first; after the input changes, the capacitor voltage response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the capacitor voltage response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded source current produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the capacitor voltage measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for capacitor voltage.

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

### Example Data (Natural Language)

Use C=0.01 F. Apply constant currents +/-0.1 A with a 50 V stop bound; sample at 0.01 s and verify the voltage ramp and BIBO counterexample.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      100
    ],
    "denominator": [
      1,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded source current",
    "output_signal_id": "capacitor voltage",
    "input_units": "A",
    "output_units": "V"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded source current to baseline and verify that capacitor voltage remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective capacitor voltage direction with its final direction.",
    "delay": "Measure from the logged bounded source current edge to the first effective capacitor voltage sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded source current and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 60. Determine proportional and PI gain stability regions with the Routh criterion

### Control Problem Description

This is a dynamic feedback system in which controller settings are swept while closed-loop stability is observed. The control input is bounded controller command during proportional and integral setting sweeps, and the measured outputs are regulated output response across the tested settings, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output response across the tested settings starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response across the tested settings response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. Even after the input returns to baseline, the deviation in regulated output response across the tested settings keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in bounded controller command during proportional and integral setting sweeps produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the regulated output response across the tested settings measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output response across the tested settings.

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

### Example Data (Natural Language)

For the proportional case use K=13, then compare K=7.5 and 25. For the PI case use (K,Ki)=(2,6), compare the boundary Ki=6+3K, and sample at 0.005 s for 20 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      13,
      13
    ],
    "denominator": [
      1,
      5,
      7,
      13
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded controller command during proportional and integral setting sweeps",
    "output_signal_id": "regulated output response across the tested settings",
    "input_units": "reference_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "pi_model": {
    "kind": "transfer_function",
    "numerator": [
      2,
      6
    ],
    "denominator": [
      1,
      3,
      4,
      6
    ],
    "input_delay_s": 0,
    "input_signal_id": "PI reference",
    "output_signal_id": "PI output",
    "input_units": "reference_unit",
    "output_units": "output_unit"
  },
  "eight_segment_evidence": {
    "stability": "Return bounded controller command during proportional and integral setting sweeps to baseline and verify that regulated output response across the tested settings remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output response across the tested settings direction with its final direction.",
    "delay": "Measure from the logged bounded controller command during proportional and integral setting sweeps edge to the first effective regulated output response across the tested settings sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded controller command during proportional and integral setting sweeps and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 61. Derive closed-loop reference, disturbance, sensor-noise, control, and error maps using sensitivity and complementary sensitivity

### Control Problem Description

This is a standard feedback loop with separate reference, plant-disturbance, sensor-noise, controller, and measured-output ports. The control input is reference command with prescribed plant disturbance and sensor noise, and the measured outputs are regulated output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in reference command with prescribed plant disturbance and sensor noise produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the regulated output, tracking error, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.

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

### Example Data (Natural Language)

Use G=1/(s+1), D=9; excite reference, plant disturbance, and sensor noise separately at +/-0.5 and +/-1, sampled at 0.01 s for 8 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      9
    ],
    "denominator": [
      1,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "reference command with prescribed plant disturbance and sensor noise",
    "output_signal_id": "regulated output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return reference command with prescribed plant disturbance and sensor noise to baseline and verify that regulated output, tracking error, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output, tracking error, and control effort direction with its final direction.",
    "delay": "Measure from the logged reference command with prescribed plant disturbance and sensor noise edge to the first effective regulated output, tracking error, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log reference command with prescribed plant disturbance and sensor noise and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 62. Stabilize an unstable inverted-pendulum model by feedback characteristic-equation design

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is bounded dynamic-compensator command, and the measured outputs are pendulum angle and compensator output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first; after the input changes, the pendulum angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in pendulum angle keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in bounded dynamic-compensator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the pendulum angle and compensator output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pendulum angle.

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

### Example Data (Natural Language)

For G=1/(s^2-1), use zeta=0.7, wn=2 rad/s, gamma=1, delta=3.8, K=7.8; sample +/-0.25 steps at 0.005 s for 8 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      7.8,
      7.8
    ],
    "denominator": [
      1,
      3.8,
      6.8,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded dynamic-compensator command",
    "output_signal_id": "pendulum angle and compensator output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -0.25,
      -0.125,
      0.125,
      0.25
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded dynamic-compensator command to baseline and verify that pendulum angle and compensator output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pendulum angle and compensator output direction with its final direction.",
    "delay": "Measure from the logged bounded dynamic-compensator command edge to the first effective pendulum angle and compensator output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded dynamic-compensator command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 63. Quantify feedback reduction of plant-gain sensitivity

### Control Problem Description

This is a feedback-regulated plant whose physical gain can vary while the controller and sensor close the same loop. The control input is bounded controller command, and the measured outputs are regulated output and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded controller command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the regulated output and tracking error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.

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

### Example Data (Natural Language)

Use P=1, C=99 at the test frequency and repeat with P times 0.9 and 1.1; use plant 1/(s+1) for the bounded time response.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      99
    ],
    "denominator": [
      1,
      100
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded controller command",
    "output_signal_id": "regulated output and tracking error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 2,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded controller command to baseline and verify that regulated output and tracking error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output and tracking error direction with its final direction.",
    "delay": "Measure from the logged bounded controller command edge to the first effective regulated output and tracking error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded controller command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 64. Resolve low-frequency plant-disturbance rejection versus high-frequency sensor-noise attenuation

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is plant disturbance and sensor-noise test inputs, and the measured outputs are regulated output, error, and sensor-noise response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in plant disturbance and sensor-noise test inputs produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the regulated output, error, and sensor-noise response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.

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

### Example Data (Natural Language)

Use L=100/(s+1); test a low-frequency plant disturbance and sensor-noise sinusoids at 1, 10, 100, 1000 rad/s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      100
    ],
    "denominator": [
      1,
      101
    ],
    "input_delay_s": 0,
    "input_signal_id": "plant disturbance and sensor-noise test inputs",
    "output_signal_id": "regulated output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.0002,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return plant disturbance and sensor-noise test inputs to baseline and verify that regulated output, error, and sensor-noise response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output, error, and sensor-noise response direction with its final direction.",
    "delay": "Measure from the logged plant disturbance and sensor-noise test inputs edge to the first effective regulated output, error, and sensor-noise response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log plant disturbance and sensor-noise test inputs and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 65. Compute Type 0 speed-control error with proportional feedback

### Control Problem Description

This is a speed-control servo made from a self-regulating plant, proportional controller, and speed sensor. The control input is proportional control command, and the measured outputs are speed and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in speed starts in its final direction rather than moving the opposite way first; after the input changes, the speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional control command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the speed and tracking error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for speed.

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

### Example Data (Natural Language)

Use A=2, tau=5 s, kP=4; apply +/-0.5 and +/-1 speed steps at 0.02 s for 20 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      8
    ],
    "denominator": [
      5,
      9
    ],
    "input_delay_s": 0,
    "input_signal_id": "proportional control command",
    "output_signal_id": "speed and tracking error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return proportional control command to baseline and verify that speed and tracking error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective speed and tracking error direction with its final direction.",
    "delay": "Measure from the logged proportional control command edge to the first effective speed and tracking error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log proportional control command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 66. Raise speed control to Type 1 with integral action

### Control Problem Description

This is a speed-control servo whose proportional-integral controller adds an error-accumulating state to the plant loop. The control input is PI control command, and the measured outputs are speed and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in speed starts in its final direction rather than moving the opposite way first; after the input changes, the speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in PI control command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the speed and tracking error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for speed.

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

### Example Data (Natural Language)

Use A=2, tau=5 s, kP=2, kI=0.5; run unit step and ramp references at 0.02 s for 30 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4,
      1
    ],
    "denominator": [
      5,
      5,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "PI control command",
    "output_signal_id": "speed and tracking error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return PI control command to baseline and verify that speed and tracking error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective speed and tracking error direction with its final direction.",
    "delay": "Measure from the logged PI control command edge to the first effective speed and tracking error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log PI control command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 67. Evaluate system type and velocity constant with tachometer feedback

### Control Problem Description

This is a DC-motor position drive equipped with armature actuation and tachometer speed feedback. The control input is armature voltage under tachometer feedback, and the measured outputs are motor position, speed, and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage under tachometer feedback produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position, speed, and tracking error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.

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

### Example Data (Natural Language)

Use tau=1 s, kP=4, kt=0.25 s; apply step and ramp references at 0.01 s for 15 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4
    ],
    "denominator": [
      1,
      2,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "armature voltage under tachometer feedback",
    "output_signal_id": "motor position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return armature voltage under tachometer feedback to baseline and verify that motor position, speed, and tracking error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position, speed, and tracking error direction with its final direction.",
    "delay": "Measure from the logged armature voltage under tachometer feedback edge to the first effective motor position, speed, and tracking error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log armature voltage under tachometer feedback and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 68. Compare P and PI rejection of DC-motor torque disturbances

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage with prescribed load-torque disturbance, and the measured outputs are motor position, speed, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage with prescribed load-torque disturbance produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position, speed, and disturbance response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.

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

### Example Data (Natural Language)

Use A=B=tau=1; compare P kP=4 with PI kP=4, kI=2 under a unit torque disturbance.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4
    ],
    "denominator": [
      1,
      1,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "armature voltage with prescribed load-torque disturbance",
    "output_signal_id": "motor position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return armature voltage with prescribed load-torque disturbance to baseline and verify that motor position, speed, and disturbance response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position, speed, and disturbance response direction with its final direction.",
    "delay": "Measure from the logged armature voltage with prescribed load-torque disturbance edge to the first effective motor position, speed, and disturbance response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log armature voltage with prescribed load-torque disturbance and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 69. Tune proportional control while exposing speed/offset/damping tradeoffs

### Control Problem Description

This is a self-regulating process operated by a proportional actuator command and observed through its output sensor. The control input is proportional actuator command, and the measured outputs are regulated output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional actuator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the regulated output, tracking error, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.

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

### Example Data (Natural Language)

Use A=1, a1=1.4, a2=1; compare kP=1.5 and 6 for a unit step at 0.01 s for 15 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1.5
    ],
    "denominator": [
      1,
      1.4,
      2.5
    ],
    "input_delay_s": 0,
    "input_signal_id": "proportional actuator command",
    "output_signal_id": "regulated output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return proportional actuator command to baseline and verify that regulated output, tracking error, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output, tracking error, and control effort direction with its final direction.",
    "delay": "Measure from the logged proportional actuator command edge to the first effective regulated output, tracking error, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log proportional actuator command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 70. Use integral control for robust zero step error and constant-disturbance rejection

### Control Problem Description

This is a process-control loop in which an integral controller accumulates tracking error while constant disturbances enter the plant. The control input is integral control command and test disturbance, and the measured outputs are tracking error, plant output, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tracking error starts in its final direction rather than moving the opposite way first; after the input changes, the tracking error response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the tracking error response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in integral control command and test disturbance produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the tracking error, plant output, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for tracking error.

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

### Example Data (Natural Language)

Use G=1/(s^2+1.4s+1), kI=0.5; apply reference and plant-disturbance steps separately with anti-windup.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.5
    ],
    "denominator": [
      1,
      1.4,
      1,
      0.5
    ],
    "input_delay_s": 0,
    "input_signal_id": "integral control command and test disturbance",
    "output_signal_id": "tracking error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return integral control command and test disturbance to baseline and verify that tracking error, plant output, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective tracking error, plant output, and control effort direction with its final direction.",
    "delay": "Measure from the logged integral control command and test disturbance edge to the first effective tracking error, plant output, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log integral control command and test disturbance and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 71. Use derivative/rate feedback to add damping without derivative kick

### Control Problem Description

This is a motion-control plant equipped with both output sensing and rate feedback so damping can be changed independently of the reference step. The control input is proportional and rate command, and the measured outputs are output and output rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output starts in its final direction rather than moving the opposite way first; after the input changes, the output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional and rate command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the output and output rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output.

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

### Example Data (Natural Language)

Use G=1/(s^2+1.4s+1), kP=6; compare kD=0 and output-rate kD=2 at 0.005 s for 12 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      6
    ],
    "denominator": [
      1,
      3.4,
      7
    ],
    "input_delay_s": 0,
    "input_signal_id": "proportional and rate command",
    "output_signal_id": "output and output rate",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 12,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return proportional and rate command to baseline and verify that output and output rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective output and output rate direction with its final direction.",
    "delay": "Measure from the logged proportional and rate command edge to the first effective output and output rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log proportional and rate command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 72. Design PI control for a two-thermal-mass process

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is heater command, and the measured outputs are controlled temperature and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in controlled temperature starts in its final direction rather than moving the opposite way first; after the input changes, the controlled temperature response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the controlled temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heater command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the controlled temperature and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use Ko=1000, tau1=1 s, tau2=10 s; compare P kP=0.03 and PI kP=0.03, kI=0.003 for a 30 degC/s ramp capped at 300 degC.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      3
    ],
    "denominator": [
      1,
      1,
      3
    ],
    "input_delay_s": 0,
    "input_signal_id": "heater command",
    "output_signal_id": "controlled temperature and control effort",
    "input_units": "degC",
    "output_units": "degC"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 50,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return heater command to baseline and verify that controlled temperature and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective controlled temperature and control effort direction with its final direction.",
    "delay": "Measure from the logged heater command edge to the first effective controlled temperature and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log heater command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 73. Compare P, PI, and PID on DC-motor speed

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage with prescribed load-torque disturbance, and the measured outputs are motor speed, tracking error, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first; after the input changes, the motor speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the motor speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in armature voltage with prescribed load-torque disturbance produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor speed, tracking error, and disturbance response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.

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

### Example Data (Natural Language)

Use Jm=0.0113, b=0.028, La=0.1, Ra=1, Kt=Ke=0.067; compare P/PI/PID using kP=3, kI=15, kD=0.3.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.0201,
      0.201,
      1.005
    ],
    "denominator": [
      0.00113,
      0.0342,
      0.233489,
      1.005
    ],
    "input_delay_s": 0,
    "input_signal_id": "armature voltage with prescribed load-torque disturbance",
    "output_signal_id": "motor speed",
    "input_units": "V",
    "output_units": "rad/s"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return armature voltage with prescribed load-torque disturbance to baseline and verify that motor speed, tracking error, and disturbance response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor speed, tracking error, and disturbance response direction with its final direction.",
    "delay": "Measure from the logged armature voltage with prescribed load-torque disturbance edge to the first effective motor speed, tracking error, and disturbance response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log armature voltage with prescribed load-torque disturbance and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 74. Analyze P/PI DC-motor position disturbance types with non-unity sensing

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is motor voltage with prescribed disturbance torque, and the measured outputs are motor position, speed, and sensed error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in motor voltage with prescribed disturbance torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position, speed, and sensed error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.

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

### Example Data (Natural Language)

Use A=B=tau=1, h=0.8; compare P kP=4 and PI kP=4, kI=2 for reference and torque disturbance.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4,
      2
    ],
    "denominator": [
      1,
      1,
      3.2,
      1.6
    ],
    "input_delay_s": 0,
    "input_signal_id": "motor voltage with prescribed disturbance torque",
    "output_signal_id": "motor position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 25,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return motor voltage with prescribed disturbance torque to baseline and verify that motor position, speed, and sensed error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position, speed, and sensed error direction with its final direction.",
    "delay": "Measure from the logged motor voltage with prescribed disturbance torque edge to the first effective motor position, speed, and sensed error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log motor voltage with prescribed disturbance torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 75. Compare satellite PD and PID system type for reference and disturbance inputs

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body-torque command with prescribed disturbance torque, and the measured outputs are attitude angle, angular rate, and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first; after the input changes, the attitude angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body-torque command with prescribed disturbance torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the attitude angle, angular rate, and tracking error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude angle.

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

### Example Data (Natural Language)

Use J=1, kP=4, kD=3; for PID add kI=1. Test reference and torque inputs one at a time.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      3,
      4
    ],
    "denominator": [
      1,
      3,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "body-torque command with prescribed disturbance torque",
    "output_signal_id": "attitude angle",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 25,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return body-torque command with prescribed disturbance torque to baseline and verify that attitude angle, angular rate, and tracking error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective attitude angle, angular rate, and tracking error direction with its final direction.",
    "delay": "Measure from the logged body-torque command with prescribed disturbance torque edge to the first effective attitude angle, angular rate, and tracking error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log body-torque command with prescribed disturbance torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 76. Tune a PID from a process reaction curve for quarter-decay behavior

### Control Problem Description

This is an industrial process loop identified from a small actuator step and its recorded reaction curve before PID tuning. The control inputs are P, PI, or PID process command, and the measured outputs are process output and quarter-decay response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in process output starts in its final direction rather than moving the opposite way first; after the input changes, the process output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the process output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in P, PI, or PID process command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the process output and quarter-decay response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for process output.

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

### Example Data (Natural Language)

Use G=2 exp(-3s)/(20s+1), R=0.1 s^-1, L=3 s; test reaction-curve P/PI/PID at 0.02 s for 100 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2
    ],
    "denominator": [
      20,
      1
    ],
    "input_delay_s": 3,
    "input_signal_id": "P",
    "output_signal_id": "process output and quarter-decay response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return P, PI, or PID process command to baseline and verify that process output and quarter-decay response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective process output and quarter-decay response direction with its final direction.",
    "delay": "Measure from the logged P, PI, or PID process command edge to the first effective process output and quarter-decay response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log P, PI, or PID process command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 77. Tune P/PI/PID from ultimate gain and ultimate period

### Control Problem Description

This is a process feedback loop whose proportional gain can be raised until the measured output reaches sustained oscillation. The control input is proportional or PID process command, and the measured outputs are marginal oscillation and tuned response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in marginal oscillation starts in its final direction rather than moving the opposite way first; after the input changes, the marginal oscillation response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the marginal oscillation response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in proportional or PID process command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the marginal oscillation and tuned response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for marginal oscillation.

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

### Example Data (Natural Language)

Use G=1/[s(s+1)(s+2)], whose Ku=6 and Pu=4.44288 s; measure marginal oscillation then apply P/PI/PID table settings.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      3,
      2,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "proportional or PID process command",
    "output_signal_id": "marginal oscillation and tuned response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 40,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return proportional or PID process command to baseline and verify that marginal oscillation and tuned response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective marginal oscillation and tuned response direction with its final direction.",
    "delay": "Measure from the logged proportional or PID process command edge to the first effective marginal oscillation and tuned response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log proportional or PID process command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 78. Apply reaction-curve Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is steam-valve P or PI command, and the measured outputs are heat-exchanger temperature and step response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heat-exchanger temperature starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the heat-exchanger temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steam-valve P or PI command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the heat-exchanger temperature and step response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use reaction-curve R=1/90 s^-1, L=13 s and model exp(-13s)/(90s+1); compare P 6.92 and PI 6.22, TI=43.3 s, then half gains.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      90,
      1
    ],
    "input_delay_s": 13,
    "input_signal_id": "steam-valve P or PI command",
    "output_signal_id": "heat-exchanger temperature and step response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 500,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return steam-valve P or PI command to baseline and verify that heat-exchanger temperature and step response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective heat-exchanger temperature and step response direction with its final direction.",
    "delay": "Measure from the logged steam-valve P or PI command edge to the first effective heat-exchanger temperature and step response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log steam-valve P or PI command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 79. Apply ultimate-sensitivity Ziegler-Nichols tuning to a heat exchanger

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is steam-valve P or PI command, and the measured outputs are heat-exchanger temperature and oscillation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in heat-exchanger temperature starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the heat-exchanger temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steam-valve P or PI command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the heat-exchanger temperature and oscillation measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use measured Ku=15.3, Pu=42 s; compare P kP=7.65 and PI kP=6.885, TI=35 s, then repeat with half gain.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      90,
      1
    ],
    "input_delay_s": 13,
    "input_signal_id": "steam-valve P or PI command",
    "output_signal_id": "heat-exchanger temperature and oscillation",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 500,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return steam-valve P or PI command to baseline and verify that heat-exchanger temperature and oscillation remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective heat-exchanger temperature and oscillation direction with its final direction.",
    "delay": "Measure from the logged steam-valve P or PI command edge to the first effective heat-exchanger temperature and oscillation sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log steam-valve P or PI command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 80. Add inverse-DC-gain feedforward to DC-motor tracking and measured-disturbance rejection

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage combining feedback and feedforward, and the measured outputs are motor speed, tracking error, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first; after the input changes, the motor speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the motor speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in armature voltage combining feedback and feedforward produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor speed, tracking error, and disturbance response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.

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

### Example Data (Natural Language)

Use G=1/(s^2+1.4s+1), G(0)=1; compare kP=1.5 and 6 with kff=1 for reference and measured-disturbance feedforward.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2.5
    ],
    "denominator": [
      1,
      1.4,
      2.5
    ],
    "input_delay_s": 0,
    "input_signal_id": "armature voltage combining feedback and feedforward",
    "output_signal_id": "motor speed",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return armature voltage combining feedback and feedforward to baseline and verify that motor speed, tracking error, and disturbance response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor speed, tracking error, and disturbance response direction with its final direction.",
    "delay": "Measure from the logged armature voltage combining feedback and feedforward edge to the first effective motor speed, tracking error, and disturbance response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log armature voltage combining feedback and feedforward and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 81. Draw and parameterize the DC-motor position-control root locus

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is motor armature voltage, and the measured outputs are motor position and tracking response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in motor armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position and tracking response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.

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

### Example Data (Natural Language)

Use G=1/[s(s+1)] and sweep K over 0.1, 0.25, 1, 4; sample unit steps at 0.01 s for 20 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "motor armature voltage",
    "output_signal_id": "motor position and tracking response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return motor armature voltage to baseline and verify that motor position and tracking response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position and tracking response direction with its final direction.",
    "delay": "Measure from the logged motor armature voltage edge to the first effective motor position and tracking response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log motor armature voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 82. Draw a root locus with respect to a physical damping/pole parameter

### Control Problem Description

This is a feedback system whose loop strength can be swept while closed-loop poles and motion are recorded. The control input is bounded modal test input while damping is varied, and the measured outputs are modal response and decay envelope, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in modal response starts in its final direction rather than moving the opposite way first; after the input changes, the modal response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the modal response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded modal test input while damping is varied produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the modal response and decay envelope measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for modal response.

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

### Example Data (Natural Language)

Use characteristic s^2+c s+1 and sweep physical damping c=0,1,2,4; sample free and step responses.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      2,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded modal test input while damping is varied",
    "output_signal_id": "modal response and decay envelope",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded modal test input while damping is varied to baseline and verify that modal response and decay envelope remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective modal response and decay envelope direction with its final direction.",
    "delay": "Measure from the logged bounded modal test input while damping is varied edge to the first effective modal response and decay envelope sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded modal test input while damping is varied and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 83. Construct a higher-order locus from Evans phase, real-axis, asymptote, departure, and gain rules

### Control Problem Description

This is a feedback system whose loop strength can be swept while closed-loop poles and motion are recorded. The control input is bounded command during a loop-strength sweep, and the measured outputs are controlled output and transient response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in controlled output starts in its final direction rather than moving the opposite way first; after the input changes, the controlled output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the controlled output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded command during a loop-strength sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the controlled output and transient response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for controlled output.

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

### Example Data (Natural Language)

Use L=1/[s((s+4)^2+16)] and sweep K near 10, 32, 65, 100; sample at 0.01 s for 30 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      65
    ],
    "denominator": [
      1,
      8,
      32,
      65
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded command during a loop-strength sweep",
    "output_signal_id": "controlled output and transient response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded command during a loop-strength sweep to baseline and verify that controlled output and transient response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective controlled output and transient response direction with its final direction.",
    "delay": "Measure from the logged bounded command during a loop-strength sweep edge to the first effective controlled output and transient response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded command during a loop-strength sweep and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 84. Stabilize a satellite double integrator with PD control

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is PD body-torque command, and the measured outputs are satellite attitude and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite attitude starts in its final direction rather than moving the opposite way first; after the input changes, the satellite attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the satellite attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in PD body-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the satellite attitude and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for satellite attitude.

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

### Example Data (Natural Language)

Use satellite G=1/s^2 and PD D=K(s+1); sweep K=0.25,1,4,9 with filtered derivative.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      1
    ],
    "denominator": [
      1,
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "PD body-torque command",
    "output_signal_id": "satellite attitude and angular rate",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return PD body-torque command to baseline and verify that satellite attitude and angular rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective satellite attitude and angular rate direction with its final direction.",
    "delay": "Measure from the logged PD body-torque command edge to the first effective satellite attitude and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log PD body-torque command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 85. Quantify how a finite lead pole changes the satellite PD locus, including the 9:1 transition

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is lead-compensated body torque, and the measured outputs are satellite attitude and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite attitude starts in its final direction rather than moving the opposite way first; after the input changes, the satellite attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the satellite attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the satellite attitude and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for satellite attitude.

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

### Example Data (Natural Language)

Use L=(s+1)/[s^2(s+p)] and compare p=4,9,12 at K=1,5,20, with 0.005 s sampling.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      1
    ],
    "denominator": [
      1,
      12,
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "lead-compensated body torque",
    "output_signal_id": "satellite attitude and angular rate",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return lead-compensated body torque to baseline and verify that satellite attitude and angular rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective satellite attitude and angular rate direction with its final direction.",
    "delay": "Measure from the logged lead-compensated body torque edge to the first effective satellite attitude and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log lead-compensated body torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 86. Analyze collocated satellite flexibility and flexible-mode damping

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is collocated body torque, and the measured outputs are collocated attitude and flexible deflection, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in collocated attitude starts in its final direction rather than moving the opposite way first; after the input changes, the collocated attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the collocated attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in collocated body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the collocated attitude and flexible deflection measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use collocated flexible satellite G=[(s+0.1)^2+36]/{s^2[(s+0.1)^2+43.56]} and lead K(s+1)/(s+12); sweep K.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      1.2,
      36.01
    ],
    "denominator": [
      1,
      12.2,
      45.97,
      522.84,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "collocated body torque",
    "output_signal_id": "collocated attitude and flexible deflection",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return collocated body torque to baseline and verify that collocated attitude and flexible deflection remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective collocated attitude and flexible deflection direction with its final direction.",
    "delay": "Measure from the logged collocated body torque edge to the first effective collocated attitude and flexible deflection sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log collocated body torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 87. Analyze noncollocated satellite flexibility and spillover instability

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is main-body torque, and the measured outputs are remote attitude and flexible deflection, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in remote attitude starts in its final direction rather than moving the opposite way first; after the input changes, the remote attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the remote attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in main-body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the remote attitude and flexible deflection measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use noncollocated G=1/{s^2[(s+0.1)^2+43.56]} with lead K(s+1)/(s+12); start K at 1e-4 and stop on instability.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      1
    ],
    "denominator": [
      1,
      12.2,
      45.97,
      522.84,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "main-body torque",
    "output_signal_id": "remote attitude and flexible deflection",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -0.01,
      -0.005,
      0.005,
      0.01
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return main-body torque to baseline and verify that remote attitude and flexible deflection remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective remote attitude and flexible deflection direction with its final direction.",
    "delay": "Measure from the logged main-body torque edge to the first effective remote attitude and flexible deflection sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log main-body torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 88. Handle complex multiple roots on a fourth-order locus

### Control Problem Description

This is a feedback system whose loop strength can be swept while closed-loop poles and motion are recorded. The control input is bounded command during a loop-strength sweep, and the measured outputs are closed-loop output near the repeated-root condition, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output near the repeated-root condition starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output near the repeated-root condition response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the closed-loop output near the repeated-root condition response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded command during a loop-strength sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output near the repeated-root condition measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output near the repeated-root condition.

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

### Example Data (Natural Language)

Use L=1/[s(s+2)((s+1)^2+4)] and sweep K across 6.25; sample at 0.005 s for 20 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      6.25
    ],
    "denominator": [
      1,
      4,
      8,
      8,
      6.25
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded command during a loop-strength sweep",
    "output_signal_id": "closed-loop output near the repeated-root condition",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded command during a loop-strength sweep to baseline and verify that closed-loop output near the repeated-root condition remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output near the repeated-root condition direction with its final direction.",
    "delay": "Measure from the logged bounded command during a loop-strength sweep edge to the first effective closed-loop output near the repeated-root condition sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded command during a loop-strength sweep and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 89. Design lead compensation to meet rise-time and overshoot limits

### Control Problem Description

This is a motor-driven position servo fitted with a lead compensator to reshape its dominant transient motion. The control input is lead-compensated servo command, and the measured outputs are servo position, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first; after the input changes, the servo position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated servo command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the servo position, tracking error, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.

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

### Example Data (Natural Language)

Use G=1/[s(s+1)] and lead D=91(s+2)/(s+13); test +/-1 steps at 0.002 s for 5 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      91,
      182
    ],
    "denominator": [
      1,
      14,
      104,
      182
    ],
    "input_delay_s": 0,
    "input_signal_id": "lead-compensated servo command",
    "output_signal_id": "servo position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 5,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return lead-compensated servo command to baseline and verify that servo position, tracking error, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective servo position, tracking error, and control effort direction with its final direction.",
    "delay": "Measure from the logged lead-compensated servo command edge to the first effective servo position, tracking error, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log lead-compensated servo command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 90. Add lag compensation to improve velocity-error constant without moving dominant roots

### Control Problem Description

This is a motor-driven position servo fitted with lead-lag compensation to improve tracking without displacing its dominant motion excessively. The control input is lead-lag servo command, and the measured outputs are servo position, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first; after the input changes, the servo position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-lag servo command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the servo position, tracking error, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.

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

### Example Data (Natural Language)

Add lag (s+0.05)/(s+0.01) to the K=91 lead design; run ramp and step tests for 300 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      91,
      186.55,
      9.1
    ],
    "denominator": [
      1,
      14.01,
      104.14,
      186.68,
      9.1
    ],
    "input_delay_s": 0,
    "input_signal_id": "lead-lag servo command",
    "output_signal_id": "servo position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return lead-lag servo command to baseline and verify that servo position, tracking error, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective servo position, tracking error, and control effort direction with its final direction.",
    "delay": "Measure from the logged lead-lag servo command edge to the first effective servo position, tracking error, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log lead-lag servo command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 91. Add notch compensation for an unmodeled flexible resonance

### Control Problem Description

This is a flexible motion plant whose actuator excites a lightly damped structural mode and whose command path includes a notch filter. The control input is notch-filtered actuator command, and the measured outputs are nominal output and flexible displacement, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in nominal output starts in its final direction rather than moving the opposite way first; after the input changes, the nominal output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the nominal output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in notch-filtered actuator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the nominal output and flexible displacement measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use flexible plant 2500/[s(s+1)(s^2+s+2500)], the K=91 lead-lag, and notch (s^2+0.8s+3600)/(s+60)^2; sweep flexible frequency by +/-10%.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2500
    ],
    "denominator": [
      1,
      2,
      2501,
      2500,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "notch-filtered actuator command",
    "output_signal_id": "nominal output and flexible displacement",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.0005,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return notch-filtered actuator command to baseline and verify that nominal output and flexible displacement remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective nominal output and flexible displacement direction with its final direction.",
    "delay": "Measure from the logged notch-filtered actuator command edge to the first effective nominal output and flexible displacement sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log notch-filtered actuator command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 92. Realize a lead compensator with an operational-amplifier circuit

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is input error voltage, and the measured outputs are lead-network output voltage, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lead-network output voltage starts in its final direction rather than moving the opposite way first; after the input changes, the lead-network output voltage response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the lead-network output voltage response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in input error voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the lead-network output voltage measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lead-network output voltage.

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

### Example Data (Natural Language)

Realize -5(s+2)/(s+10) with C=10 uF, R1=50 kohm, R2=200 kohm, Rf=250 kohm; sweep component tolerances +/-10%.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -5,
      -10
    ],
    "denominator": [
      1,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "input error voltage",
    "output_signal_id": "lead-network output voltage",
    "input_units": "V",
    "output_units": "V"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 5,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return input error voltage to baseline and verify that lead-network output voltage remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective lead-network output voltage direction with its final direction.",
    "delay": "Measure from the logged input error voltage edge to the first effective lead-network output voltage sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log input error voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 93. Design quadrotor pitch-axis lead compensation

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is pitch rotor-torque command, and the measured outputs are quadrotor pitch angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in quadrotor pitch angle starts in its final direction rather than moving the opposite way first; after the input changes, the quadrotor pitch angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the quadrotor pitch angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in pitch rotor-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the quadrotor pitch angle and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use quadrotor pitch plant 1/[s^2(s+2)] and lead 30(s+0.5)/(s+15); test +/-0.1 rad commands at 0.002 s for 15 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      30,
      15
    ],
    "denominator": [
      1,
      17,
      30,
      30,
      15
    ],
    "input_delay_s": 0,
    "input_signal_id": "pitch rotor-torque command",
    "output_signal_id": "quadrotor pitch angle and angular rate",
    "input_units": "rad",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return pitch rotor-torque command to baseline and verify that quadrotor pitch angle and angular rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective quadrotor pitch angle and angular rate direction with its final direction.",
    "delay": "Measure from the logged pitch rotor-torque command edge to the first effective quadrotor pitch angle and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log pitch rotor-torque command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 94. Design a small-airplane pitch autopilot and integral trim loop

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is elevator and trim-tab commands, and the measured outputs are pitch attitude, elevator, and trim-tab deflections, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pitch attitude starts in its final direction rather than moving the opposite way first; after the input changes, the pitch attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the pitch attitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in elevator and trim-tab commands produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the pitch attitude, elevator, and trim-tab deflections measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use airplane G=160(s+2.5)(s+0.7)/[(s^2+5s+40)(s^2+0.03s+0.06)], lead K=1.5,z=3,p=20, and trim integrator KI=0.15.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      160,
      512,
      280
    ],
    "denominator": [
      1,
      5.03,
      40.21,
      1.5,
      2.4
    ],
    "input_delay_s": 0,
    "input_signal_id": "elevator and trim-tab commands",
    "output_signal_id": "pitch attitude",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 40,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return elevator and trim-tab commands to baseline and verify that pitch attitude, elevator, and trim-tab deflections remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pitch attitude, elevator, and trim-tab deflections direction with its final direction.",
    "delay": "Measure from the logged elevator and trim-tab commands edge to the first effective pitch attitude, elevator, and trim-tab deflections sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log elevator and trim-tab commands and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 95. Use a negative root locus for nonminimum-phase airplane altitude dynamics

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is elevator command, and the measured outputs are aircraft altitude response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in aircraft altitude response first moves in an unfavorable or opposite direction before turning; after the input changes, the aircraft altitude response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the aircraft altitude response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in elevator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the aircraft altitude response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use airplane altitude G=(6-s)/[s(s^2+4s+13)] and sweep positive physical gain using the corresponding negative root locus; apply +/-1 degree pulses.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -1,
      6
    ],
    "denominator": [
      1,
      4,
      13,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "elevator command",
    "output_signal_id": "aircraft altitude response",
    "input_units": "deg",
    "output_units": "ft"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return elevator command to baseline and verify that aircraft altitude response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective aircraft altitude response direction with its final direction.",
    "delay": "Measure from the logged elevator command edge to the first effective aircraft altitude response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log elevator command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 96. Select tachometer and amplifier gains by successive loop closure

### Control Problem Description

This is a motor-driven servomechanism containing an amplifier, position loop, and tachometer speed-feedback loop. The control input is servo amplifier voltage under tachometer feedback, and the measured outputs are servomechanism position and speed response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servomechanism position starts in its final direction rather than moving the opposite way first; after the input changes, the servomechanism position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the servomechanism position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in servo amplifier voltage under tachometer feedback produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the servomechanism position and speed response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servomechanism position.

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

### Example Data (Natural Language)

Use s^2+s+KA+KT s=0; choose KA=4 then KT=1 and repeat after +/-10% changes.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4
    ],
    "denominator": [
      1,
      2,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "servo amplifier voltage under tachometer feedback",
    "output_signal_id": "servomechanism position and speed response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return servo amplifier voltage under tachometer feedback to baseline and verify that servomechanism position and speed response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective servomechanism position and speed response direction with its final direction.",
    "delay": "Measure from the logged servo amplifier voltage under tachometer feedback edge to the first effective servomechanism position and speed response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log servo amplifier voltage under tachometer feedback and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 97. Design inner-attitude/outer-position quadrotor cascade control

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is outer position command and inner rotor-torque command, and the measured outputs are horizontal position, pitch attitude, and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in horizontal position starts in its final direction rather than moving the opposite way first; after the input changes, the horizontal position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the horizontal position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in outer position command and inner rotor-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the horizontal position, pitch attitude, and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use inner pitch plant 1/[s^2(s+2)] with 30(s+0.5)/(s+15), outer position plant -32.2/s^2, and outer lead 0.081(s+0.1)/(s+10).

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2.6082,
      0.26082
    ],
    "denominator": [
      1,
      10,
      2.6082,
      0.26082
    ],
    "input_delay_s": 0,
    "input_signal_id": "outer position command and inner rotor-torque command",
    "output_signal_id": "horizontal position",
    "input_units": "ft",
    "output_units": "ft"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 40,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return outer position command and inner rotor-torque command to baseline and verify that horizontal position, pitch attitude, and angular rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective horizontal position, pitch attitude, and angular rate direction with its final direction.",
    "delay": "Measure from the logged outer position command and inner rotor-torque command edge to the first effective horizontal position, pitch attitude, and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log outer position command and inner rotor-torque command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 98. Design a lead compensator for a numerically controlled machine-tool servo

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is lead-compensated servo command, and the measured outputs are machine-tool position, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in machine-tool position starts in its final direction rather than moving the opposite way first; after the input changes, the machine-tool position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the machine-tool position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated servo command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the machine-tool position, tracking error, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use machine-tool G=1/[s(s+1)] and lead 10(s+1)/(s+2); test +/-1 position steps and +/-10% pole variation.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      10,
      10
    ],
    "denominator": [
      1,
      3,
      12,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "lead-compensated servo command",
    "output_signal_id": "machine-tool position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return lead-compensated servo command to baseline and verify that machine-tool position, tracking error, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective machine-tool position, tracking error, and control effort direction with its final direction.",
    "delay": "Measure from the logged lead-compensated servo command edge to the first effective machine-tool position, tracking error, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log lead-compensated servo command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 99. Linearize and stabilize an elementary magnetic suspension

### Control Problem Description

This is a magnetic-levitation apparatus in which an electromagnet supports a steel ball while a sensor measures the air gap. The control input is electromagnet current command, and the measured outputs are ball position, sensor voltage, and coil current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ball position starts in its final direction rather than moving the opposite way first; after the input changes, the ball position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in ball position keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in electromagnet current command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the ball position, sensor voltage, and coil current measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use m=0.02 kg, g=9.8, e=100x, f=0.5i+20x, and lead (s+10)/(s+20) with K=1; sample at 0.001 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      50,
      500
    ],
    "denominator": [
      1,
      20,
      1500,
      5000
    ],
    "input_delay_s": 0,
    "input_signal_id": "electromagnet current command",
    "output_signal_id": "ball position",
    "input_units": "V",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return electromagnet current command to baseline and verify that ball position, sensor voltage, and coil current remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective ball position, sensor voltage, and coil current direction with its final direction.",
    "delay": "Measure from the logged electromagnet current command edge to the first effective ball position, sensor voltage, and coil current sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log electromagnet current command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 100. Design yaw-rate-aided heading control for the USCG cutter Tampa under wind disturbance

### Control Problem Description

This is a surface-vessel steering system made from hull yaw motion, a rudder actuator, and heading sensors. The control input is rudder command and prescribed wind-gust input, and the measured outputs are ship heading, yaw rate, rudder angle, and wind response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ship heading starts in its final direction rather than moving the opposite way first; after the input changes, the ship heading response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the ship heading response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in rudder command and prescribed wind-gust input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the ship heading, yaw rate, rudder angle, and wind response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use Tampa rudder plant -0.0184(s+0.0068)/[s(s+0.2647)(s+0.0063)]. With sign absorbed, use Kpsi=0.1, Kr=1, KI=0.0001 and enforce rudder limits.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.00184,
      1.4352e-05,
      1.2512e-08
    ],
    "denominator": [
      1,
      0.2894,
      0.00363273,
      1.4352e-05,
      1.2512e-08
    ],
    "input_delay_s": 0,
    "input_signal_id": "rudder command and prescribed wind-gust input",
    "output_signal_id": "ship heading",
    "input_units": "rad",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 2000,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return rudder command and prescribed wind-gust input to baseline and verify that ship heading, yaw rate, rudder angle, and wind response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective ship heading, yaw rate, rudder angle, and wind response direction with its final direction.",
    "delay": "Measure from the logged rudder command and prescribed wind-gust input edge to the first effective ship heading, yaw rate, rudder angle, and wind response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log rudder command and prescribed wind-gust input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 101. Compute the current response of a voltage-driven capacitor

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is sinusoidal voltage, and the measured outputs are capacitor current magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in capacitor current magnitude starts in its final direction rather than moving the opposite way first; after the input changes, the capacitor current magnitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the capacitor current magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sinusoidal voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the capacitor current magnitude and phase measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for capacitor current magnitude.

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

### Example Data (Natural Language)

Use C=100 uF and voltage sinusoids of 1 V at 1, 10, 100, and 1000 rad/s; sample current with at least 50 points per cycle.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.0001,
      0
    ],
    "denominator": [
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "sinusoidal voltage",
    "output_signal_id": "capacitor current magnitude and phase",
    "input_units": "V",
    "output_units": "A"
  },
  "experiment": {
    "sample_time_s": 5e-05,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sinusoidal voltage to baseline and verify that capacitor current magnitude and phase remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective capacitor current magnitude and phase direction with its final direction.",
    "delay": "Measure from the logged sinusoidal voltage edge to the first effective capacitor current magnitude and phase sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sinusoidal voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 102. Derive the magnitude and phase of a first-order lead element

### Control Problem Description

This is a first-order lead network made from resistive and capacitive elements that advance output phase over a finite frequency band. The control input is sinusoidal error signal, and the measured outputs are lead-compensator magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lead-compensator magnitude starts in its final direction rather than moving the opposite way first; after the input changes, the lead-compensator magnitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the lead-compensator magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sinusoidal error signal produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the lead-compensator magnitude and phase measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lead-compensator magnitude.

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

### Example Data (Natural Language)

Use lead D=(s+1)/(0.1s+1), sweep 0.1 to 100 rad/s, and verify magnitude and phase at 1, sqrt(10), and 10 rad/s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      1
    ],
    "denominator": [
      0.1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "sinusoidal error signal",
    "output_signal_id": "lead-compensator magnitude and phase",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sinusoidal error signal to baseline and verify that lead-compensator magnitude and phase remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective lead-compensator magnitude and phase direction with its final direction.",
    "delay": "Measure from the logged sinusoidal error signal edge to the first effective lead-compensator magnitude and phase sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sinusoidal error signal and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 103. Build an asymptotic Bode plot from real poles and zeros

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is sinusoidal plant input, and the measured outputs are open-loop magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in open-loop magnitude starts in its final direction rather than moving the opposite way first; after the input changes, the open-loop magnitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the open-loop magnitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in sinusoidal plant input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the open-loop magnitude and phase measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for open-loop magnitude.

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

### Example Data (Natural Language)

Use L=2000(s+0.5)/[s(s+10)(s+50)] and evaluate 0.01 to 1000 rad/s on a logarithmic grid.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2000,
      1000
    ],
    "denominator": [
      1,
      60,
      500,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "sinusoidal plant input",
    "output_signal_id": "open-loop magnitude and phase",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sinusoidal plant input to baseline and verify that open-loop magnitude and phase remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective open-loop magnitude and phase direction with its final direction.",
    "delay": "Measure from the logged sinusoidal plant input edge to the first effective open-loop magnitude and phase sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sinusoidal plant input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 104. Include complex pole/zero factors in ordinary and flexible-system Bode plots

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is sinusoidal applied force, and the measured outputs are plant displacement magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in plant displacement magnitude starts in its final direction rather than moving the opposite way first; after the input changes, the plant displacement magnitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the plant displacement magnitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in sinusoidal applied force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the plant displacement magnitude and phase measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for plant displacement magnitude.

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

### Example Data (Natural Language)

Compare L1=10/[s(s^2+0.4s+4)] with the flexible pole-zero doublet 0.01(s^2+0.01s+1)/{s^2(s^2/4+0.01s+1)}.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      10
    ],
    "denominator": [
      1,
      0.4,
      4,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "sinusoidal applied force",
    "output_signal_id": "plant displacement magnitude and phase",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sinusoidal applied force to baseline and verify that plant displacement magnitude and phase remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective plant displacement magnitude and phase direction with its final direction.",
    "delay": "Measure from the logged sinusoidal applied force edge to the first effective plant displacement magnitude and phase sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sinusoidal applied force and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 105. Infer low-frequency error constants and system type from a Bode plot

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is unit-ramp reference, and the measured outputs are tracking error and regulated output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tracking error starts in its final direction rather than moving the opposite way first; after the input changes, the tracking error response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the tracking error response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in unit-ramp reference produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the tracking error and regulated output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for tracking error.

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

### Example Data (Natural Language)

Use L=10/[s(s+1)], run a unit ramp for 50 s at 0.01 s sampling, and fit the final error.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      10
    ],
    "denominator": [
      1,
      1,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "unit-ramp reference",
    "output_signal_id": "tracking error and regulated output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 50,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return unit-ramp reference to baseline and verify that tracking error and regulated output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective tracking error and regulated output direction with its final direction.",
    "delay": "Measure from the logged unit-ramp reference edge to the first effective tracking error and regulated output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log unit-ramp reference and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 106. Apply the Nyquist criterion to a second-order loop stable for every positive gain

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded loop command during a gain sweep, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded loop command during a gain sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output and frequency response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.

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

### Example Data (Natural Language)

Use G=1/(s+1)^2 and sweep K=0.1,1,10,100; also test negative K=-0.5,-1,-2.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4
    ],
    "denominator": [
      1,
      2,
      5
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded loop command during a gain sweep",
    "output_signal_id": "closed-loop output and frequency response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded loop command during a gain sweep to baseline and verify that closed-loop output and frequency response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output and frequency response direction with its final direction.",
    "delay": "Measure from the logged bounded loop command during a gain sweep edge to the first effective closed-loop output and frequency response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded loop command during a gain sweep and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 107. Apply Nyquist indentation to a third-order loop with a pole at the origin

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded loop command during a gain sweep, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded loop command during a gain sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output and frequency response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.

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

### Example Data (Natural Language)

Use G=1/[s(s+1)^2] and sweep K=0.5,1,2,3; apply Nyquist indentation at the origin.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      2,
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded loop command during a gain sweep",
    "output_signal_id": "closed-loop output and frequency response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded loop command during a gain sweep to baseline and verify that closed-loop output and frequency response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output and frequency response direction with its final direction.",
    "delay": "Measure from the logged bounded loop command during a gain sweep edge to the first effective closed-loop output and frequency response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded loop command during a gain sweep and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 108. Compare special Nyquist cases with an RHP pole and imaginary-axis zeros

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded commands used in the two loop tests, and the measured outputs are closed-loop outputs and frequency responses of both cases, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop outputs starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop outputs response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in closed-loop outputs keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in bounded commands used in the two loop tests produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop outputs and frequency responses of both cases measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop outputs.

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

### Example Data (Natural Language)

For G1=(s+1)/[s(s/10-1)] use K=0.5,1,2; separately test G2=(s^2+3)/(s+1)^2 for positive gains.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      20,
      20
    ],
    "denominator": [
      1,
      10,
      20
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded commands used in the two loop tests",
    "output_signal_id": "closed-loop outputs and frequency responses of both cases",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded commands used in the two loop tests to baseline and verify that closed-loop outputs and frequency responses of both cases remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop outputs and frequency responses of both cases direction with its final direction.",
    "delay": "Measure from the logged bounded commands used in the two loop tests edge to the first effective closed-loop outputs and frequency responses of both cases sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded commands used in the two loop tests and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 109. Diagnose conditional stability and misleading gain margin

### Control Problem Description

This is a feedback system whose closed-loop stability changes across distinct ranges of loop gain. The control input is bounded loop command during a gain sweep, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded loop command during a gain sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output and frequency response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.

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

### Example Data (Natural Language)

Use L=K(s+10)^2/s^3 and compare K=4.9,5,7,10; at K=7 measure both directions of gain margin.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      7,
      140,
      700
    ],
    "denominator": [
      1,
      7,
      140,
      700
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded loop command during a gain sweep",
    "output_signal_id": "closed-loop output and frequency response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded loop command during a gain sweep to baseline and verify that closed-loop output and frequency response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output and frequency response direction with its final direction.",
    "delay": "Measure from the logged bounded loop command during a gain sweep edge to the first effective closed-loop output and frequency response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded loop command during a gain sweep and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 110. Interpret multiple unity-gain crossings and stability margins

### Control Problem Description

This is a feedback loop whose open-loop frequency response crosses unit magnitude more than once before high-frequency rolloff. The control input is bounded sinusoidal loop excitation, and the measured outputs are closed-loop output and open-loop frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded sinusoidal loop excitation produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output and open-loop frequency response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.

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

### Example Data (Natural Language)

Use G=85(s+1)(s^2+2s+43.25)/{s^2(s^2+2s+82)(s^2+2s+101)} and resolve every unity crossing.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      85,
      255,
      3846.25,
      3676.25
    ],
    "denominator": [
      1,
      4,
      187,
      366,
      8282,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded sinusoidal loop excitation",
    "output_signal_id": "closed-loop output and open-loop frequency response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.0005,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded sinusoidal loop excitation to baseline and verify that closed-loop output and open-loop frequency response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output and open-loop frequency response direction with its final direction.",
    "delay": "Measure from the logged bounded sinusoidal loop excitation edge to the first effective closed-loop output and open-loop frequency response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded sinusoidal loop excitation and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 111. Use Bode's gain-phase slope rule to design spacecraft PD control

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body-torque command, and the measured outputs are attitude, angular rate, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude starts in its final direction rather than moving the opposite way first; after the input changes, the attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body-torque command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the attitude, angular rate, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude.

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

### Example Data (Natural Language)

Use spacecraft G=1/s^2 and KD=0.01(20s+1); apply +/-0.1 rad steps at 0.05 s for 200 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.2,
      0.01
    ],
    "denominator": [
      1,
      0.2,
      0.01
    ],
    "input_delay_s": 0,
    "input_signal_id": "body-torque command",
    "output_signal_id": "attitude",
    "input_units": "rad",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 200,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return body-torque command to baseline and verify that attitude, angular rate, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective attitude, angular rate, and control effort direction with its final direction.",
    "delay": "Measure from the logged body-torque command edge to the first effective attitude, angular rate, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log body-torque command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 112. Relate crossover frequency, phase margin, resonant peak, and closed-loop bandwidth

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded sinusoidal command sweep, and the measured outputs are closed-loop output and bandwidth response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded sinusoidal command sweep produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output and bandwidth response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.

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

### Example Data (Natural Language)

Use representative L=1/[s(s+1)], calculate exact T=L/(1+L), and compare crossover, phase margin, resonance, and -3 dB bandwidth.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded sinusoidal command sweep",
    "output_signal_id": "closed-loop output and bandwidth response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded sinusoidal command sweep to baseline and verify that closed-loop output and bandwidth response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output and bandwidth response direction with its final direction.",
    "delay": "Measure from the logged bounded sinusoidal command sweep edge to the first effective closed-loop output and bandwidth response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded sinusoidal command sweep and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 113. Design lead compensation for DC-motor position control

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is lead-compensated motor command, and the measured outputs are motor position, error, and step response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lead-compensated motor command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position, error, and step response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.

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

### Example Data (Natural Language)

Use motor G=1/[s(s+1)] and lead D=10(s/2+1)/(s/10+1); test ramp and step commands.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      50,
      100
    ],
    "denominator": [
      1,
      11,
      60,
      100
    ],
    "input_delay_s": 0,
    "input_signal_id": "lead-compensated motor command",
    "output_signal_id": "motor position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return lead-compensated motor command to baseline and verify that motor position, error, and step response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position, error, and step response direction with its final direction.",
    "delay": "Measure from the logged lead-compensated motor command edge to the first effective motor position, error, and step response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log lead-compensated motor command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 114. Design single- and double-lead compensation for a thermal plant and servomechanism

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is single- or double-lead command, and the measured outputs are temperature or servo output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in temperature or servo output starts in its final direction rather than moving the opposite way first; after the input changes, the temperature or servo output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the temperature or servo output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in single- or double-lead command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the temperature or servo output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for temperature or servo output.

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

### Example Data (Natural Language)

For the thermal plant use K=9 and lead (s/1.5+1)/(s/15+1); for the servo use the double lead (s/2+1)(s/4+1)/[(s/20+1)(s/40+1)].

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      3.5,
      3.5,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "single- or double-lead command",
    "output_signal_id": "temperature or servo output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return single- or double-lead command to baseline and verify that temperature or servo output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective temperature or servo output direction with its final direction.",
    "delay": "Measure from the logged single- or double-lead command edge to the first effective temperature or servo output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log single- or double-lead command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 115. Design lag compensation for a thermal plant and DC motor, and compare it with lead

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is lag-compensated command, and the measured outputs are thermal or motor response and slow tail, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in thermal or motor response starts in its final direction rather than moving the opposite way first; after the input changes, the thermal or motor response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the thermal or motor response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in lag-compensated command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the thermal or motor response and slow tail measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for thermal or motor response.

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

### Example Data (Natural Language)

For the thermal plant use lag 3(5s+1)/(15s+1); for the motor use K=10 with lag zero 0.1 and pole 0.01 rad/s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      100,
      10
    ],
    "denominator": [
      100,
      110,
      10,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "lag-compensated command",
    "output_signal_id": "thermal or motor response and slow tail",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return lag-compensated command to baseline and verify that thermal or motor response and slow tail remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective thermal or motor response and slow tail direction with its final direction.",
    "delay": "Measure from the logged lag-compensated command edge to the first effective thermal or motor response and slow tail sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log lag-compensated command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 116. Design spacecraft PID control with a sensor lag and constant torque disturbance

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body-torque command with prescribed disturbance torque, and the measured outputs are attitude, angular rate, and disturbance response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude starts in its final direction rather than moving the opposite way first; after the input changes, the attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body-torque command with prescribed disturbance torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the attitude, angular rate, and disturbance response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude.

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

### Example Data (Natural Language)

Use spacecraft G=0.9/s^2, sensor H=2/(s+2), and PID D=0.05(10s+1)(s+0.005)/s; test command and constant torque separately.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.9,
      0.0945,
      0.00045
    ],
    "denominator": [
      1,
      2,
      0,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "body-torque command with prescribed disturbance torque",
    "output_signal_id": "attitude",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 2000,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return body-torque command with prescribed disturbance torque to baseline and verify that attitude, angular rate, and disturbance response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective attitude, angular rate, and disturbance response direction with its final direction.",
    "delay": "Measure from the logged body-torque command with prescribed disturbance torque edge to the first effective attitude, angular rate, and disturbance response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log body-torque command with prescribed disturbance torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 117. Convert a sinusoidal tracking-error requirement into a loop-gain performance bound

### Control Problem Description

This is a tracking-control loop driven by a sinusoidal reference while error and regulated output are recorded together. The control input is prescribed sinusoidal reference command, and the measured outputs are tracking error and regulated output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tracking error starts in its final direction rather than moving the opposite way first; after the input changes, the tracking error response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the tracking error response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in prescribed sinusoidal reference command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the tracking error and regulated output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for tracking error.

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

### Example Data (Natural Language)

Require unit-amplitude sinusoidal tracking error <=0.005 from 0 to 100 Hz; use an exact sensitivity test with S=1/201 over the band.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      201
    ],
    "input_delay_s": 0,
    "input_signal_id": "prescribed sinusoidal reference command",
    "output_signal_id": "tracking error and regulated output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.0001,
    "duration_s": 2,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed sinusoidal reference command to baseline and verify that tracking error and regulated output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective tracking error and regulated output direction with its final direction.",
    "delay": "Measure from the logged prescribed sinusoidal reference command edge to the first effective tracking error and regulated output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed sinusoidal reference command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 118. Enforce robust-stability and sensitivity bounds under plant uncertainty

### Control Problem Description

This is a feedback system built around an uncertain dynamic plant, with controller and sensor channels used to limit sensitivity. The control input is loop-shaped feedback command under prescribed plant variation, and the measured outputs are regulated output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in loop-shaped feedback command under prescribed plant variation produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the regulated output, tracking error, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use antenna G=1/[s(s+1)] and D=10(0.5s+1)/(0.1s+1); compute S and T, then apply the stated high-frequency uncertainty weight.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.1,
      1.1,
      1,
      0
    ],
    "denominator": [
      0.1,
      1.1,
      6,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "loop-shaped feedback command under prescribed plant variation",
    "output_signal_id": "regulated output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 50,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return loop-shaped feedback command under prescribed plant variation to baseline and verify that regulated output, tracking error, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output, tracking error, and control effort direction with its final direction.",
    "delay": "Measure from the logged loop-shaped feedback command under prescribed plant variation edge to the first effective regulated output, tracking error, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log loop-shaped feedback command under prescribed plant variation and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 119. Quantify the phase-margin loss caused by sampling-equivalent time delay

### Control Problem Description

This is a sampled-data feedback loop made from a sampler, digital command path, hold element, and continuous plant. The control input is digitally sampled control command, and the measured outputs are sampled plant output, tracking error, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled plant output starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the sampled plant output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in digitally sampled control command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sampled plant output, tracking error, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled plant output.

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

### Example Data (Natural Language)

Insert equivalent delay Td=0.025 s into the lead-compensated motor loop with crossover 5 rad/s; compare Ts=0.05 and 0.14 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1
    ],
    "input_delay_s": 0.025,
    "input_signal_id": "digitally sampled control command",
    "output_signal_id": "sampled plant output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digitally sampled control command to baseline and verify that sampled plant output, tracking error, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sampled plant output, tracking error, and control effort direction with its final direction.",
    "delay": "Measure from the logged digitally sampled control command edge to the first effective sampled plant output, tracking error, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digitally sampled control command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 120. Read closed-loop bandwidth, resonant peak, and stability margins from a Nichols chart

### Control Problem Description

This is a frequency-response test system made from a sinusoidal source, dynamic plant, and synchronized magnitude and phase recorders. The control input is bounded frequency-swept input, and the measured outputs are closed-loop output and frequency response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop output starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the closed-loop output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in bounded frequency-swept input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop output and frequency response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for closed-loop output.

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

### Example Data (Natural Language)

Use the PID-loop frequency samples and read Nichols contours; verify bandwidth 0.8 rad/s, resonant peak 1.2, PM 37 degrees, and GM 1.26.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      0.9,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded frequency-swept input",
    "output_signal_id": "closed-loop output and frequency response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded frequency-swept input to baseline and verify that closed-loop output and frequency response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop output and frequency response direction with its final direction.",
    "delay": "Measure from the logged bounded frequency-swept input edge to the first effective closed-loop output and frequency response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded frequency-swept input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 121. Put rigid-satellite attitude dynamics into state-variable form

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is thruster force, and the measured outputs are attitude angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude angle starts in its final direction rather than moving the opposite way first; after the input changes, the attitude angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the attitude angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in thruster force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the attitude angle and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for attitude angle.

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

### Example Data (Natural Language)

Use lever arm d=1 m, inertia I=5000 kg*m^2, state [angle, rate], and +/-25 N pulses; sample at 0.01 s for 20 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        1
      ],
      [
        0,
        0
      ]
    ],
    "b": [
      [
        0
      ],
      [
        0.0002
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "angle",
      "rate"
    ],
    "input_signal_ids": [
      "thruster force"
    ],
    "output_signal_ids": [
      "attitude angle and angular rate channel 1",
      "attitude angle and angular rate channel 2"
    ],
    "initial_state": [
      0,
      0
    ],
    "signal_units": {
      "angle": "rad",
      "rate": "rad/s",
      "thruster_force": "N"
    }
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -25,
      -12.5,
      12.5,
      25
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return thruster force to baseline and verify that attitude angle and angular rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective attitude angle and angular rate direction with its final direction.",
    "delay": "Measure from the logged thruster force edge to the first effective attitude angle and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log thruster force and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 122. Derive a DC-motor state model from coupled mechanical and electrical equations

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is armature voltage, and the measured outputs are motor position, speed, current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in armature voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position, speed, current measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.

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

### Example Data (Natural Language)

Use J=0.0113, b=0.028, La=0.1, Ra=1, Kt=Ke=0.067; apply +/-1 V steps and log angle, speed, current at 0.001 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        1,
        0
      ],
      [
        0,
        -2.477876,
        5.929204
      ],
      [
        0,
        -0.67,
        -10
      ]
    ],
    "b": [
      [
        0
      ],
      [
        0
      ],
      [
        10
      ]
    ],
    "c": [
      [
        1,
        0,
        0
      ],
      [
        0,
        1,
        0
      ],
      [
        0,
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "angle",
      "speed",
      "current"
    ],
    "input_signal_ids": [
      "armature voltage"
    ],
    "output_signal_ids": [
      "motor position",
      "speed",
      "current"
    ],
    "initial_state": [
      0,
      0,
      0
    ],
    "signal_units": {
      "angle": "rad",
      "speed": "rad/s",
      "current": "A",
      "armature_voltage": "V"
    }
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 8,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return armature voltage to baseline and verify that motor position, speed, current remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position, speed, current direction with its final direction.",
    "delay": "Measure from the logged armature voltage edge to the first effective motor position, speed, current sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log armature voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 123. Realize a quarter-car transfer function in real modal canonical form

### Control Problem Description

This is a vehicle suspension apparatus made from body and wheel masses, springs, and dampers. The control input is realization input, and the measured outputs are quarter-car output and modal states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in quarter-car output starts in its final direction rather than moving the opposite way first; after the input changes, the quarter-car output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the quarter-car output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in realization input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the quarter-car output and modal states measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for quarter-car output.

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

### Example Data (Natural Language)

Use G=(2s+4)/[s^2(s^2+2s+4)] and realize the rigid-body and flexible modes separately; sample impulse response at 0.005 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2,
      4
    ],
    "denominator": [
      1,
      2,
      4,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "realization input",
    "output_signal_id": "quarter-car output and modal states",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return realization input to baseline and verify that quarter-car output and modal states remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective quarter-car output and modal states direction with its final direction.",
    "delay": "Measure from the logged realization input edge to the first effective quarter-car output and modal states sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log realization input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 124. Transform a thermal system from control canonical form to modal form

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is heat input, and the measured outputs are thermal modal states and output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in thermal modal states starts in its final direction rather than moving the opposite way first; after the input changes, the thermal modal states response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the thermal modal states response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in heat input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the thermal modal states and output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for thermal modal states.

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

### Example Data (Natural Language)

Use Ac=[[-7,-12],[1,0]], Bc=[1,0], Cc=[1,2] and T=[[4,-3],[-1,1]]; compare transformed trajectories.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      2
    ],
    "denominator": [
      1,
      7,
      12
    ],
    "input_delay_s": 0,
    "input_signal_id": "heat input",
    "output_signal_id": "thermal modal states and output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return heat input to baseline and verify that thermal modal states and output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective thermal modal states and output direction with its final direction.",
    "delay": "Measure from the logged heat input edge to the first effective thermal modal states and output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log heat input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 125. Recover poles, zeros, and transfer function from the Piper Dakota state model

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is elevator input, and the measured outputs are pitch attitude and modal states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pitch attitude starts in its final direction rather than moving the opposite way first; after the input changes, the pitch attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the pitch attitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in elevator input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the pitch attitude and modal states measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pitch attitude.

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

### Example Data (Natural Language)

Use the supplied four-state Piper Dakota matrices; excite elevator by +/-1 degree pulses and compute poles, zeros, and pitch response.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      160,
      512,
      280
    ],
    "denominator": [
      1,
      5.03,
      40.21,
      1.5,
      2.4
    ],
    "input_delay_s": 0,
    "input_signal_id": "elevator input",
    "output_signal_id": "pitch attitude and modal states",
    "input_units": "deg",
    "output_units": "deg"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 40,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return elevator input to baseline and verify that pitch attitude and modal states remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pitch attitude and modal states direction with its final direction.",
    "delay": "Measure from the logged elevator input edge to the first effective pitch attitude and modal states sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log elevator input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 126. Test controllability and observability and interpret pole-zero cancellation physically

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is bounded state-space test excitation, and the measured outputs are state trajectories and declared output response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state trajectories starts in its final direction rather than moving the opposite way first; after the input changes, the state trajectories response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the state trajectories response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded state-space test excitation produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Even with synchronized records of bounded state-space test excitation and state trajectories and declared output response, a pole-zero-cancelled mode is absent from the records and cannot be excited; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state trajectories.

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

### Example Data (Natural Language)

Use A=diag(-3,-4), B=[1,1]^T, C=[0,1], D=0, so the -3 mode is controllable but unobservable; compare internal state and reduced transfer output.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        -3,
        0
      ],
      [
        0,
        -4
      ]
    ],
    "b": [
      [
        1
      ],
      [
        1
      ]
    ],
    "c": [
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ]
    ],
    "state_names": [
      "hidden_mode",
      "visible_mode"
    ],
    "input_signal_ids": [
      "bounded state-space test excitation"
    ],
    "output_signal_ids": [
      "state trajectories and declared output response"
    ],
    "initial_state": [
      1,
      0
    ],
    "signal_units": {}
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded state-space test excitation to baseline and verify that state trajectories and declared output response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective state trajectories and declared output response direction with its final direction.",
    "delay": "Measure from the logged bounded state-space test excitation edge to the first effective state trajectories and declared output response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded state-space test excitation and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 127. Place repeated closed-loop poles for an undamped pendulum by full-state feedback

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is pivot torque, and the measured outputs are pendulum angle and rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first; after the input changes, the pendulum angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the pendulum angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in pivot torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the pendulum angle and rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pendulum angle.

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

### Example Data (Natural Language)

Use omega0=1 rad/s and feedback K=[3,4]; release from angle 0.1 rad and compare with open-loop pendulum.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        1
      ],
      [
        -4,
        -4
      ]
    ],
    "b": [
      [
        0
      ],
      [
        1
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "angle",
      "rate"
    ],
    "input_signal_ids": [
      "pivot torque"
    ],
    "output_signal_ids": [
      "pendulum angle and rate channel 1",
      "pendulum angle and rate channel 2"
    ],
    "initial_state": [
      0.1,
      0
    ],
    "signal_units": {
      "angle": "rad",
      "rate": "rad/s"
    }
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return pivot torque to baseline and verify that pendulum angle and rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pendulum angle and rate direction with its final direction.",
    "delay": "Measure from the logged pivot torque edge to the first effective pendulum angle and rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log pivot torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 128. Apply Ackermann pole placement and diagnose gain growth near a weakly controllable zero

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is bounded state-feedback command, and the measured outputs are closed-loop state response and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in closed-loop state response starts in its final direction rather than moving the opposite way first; after the input changes, the closed-loop state response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the closed-loop state response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in bounded state-feedback command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the closed-loop state response and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use target s^2+2s+4. Compare z0=2 giving K=[-3.8,0.6] with z0=-2.99 giving K=[2052.5,-688.1].

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4
    ],
    "denominator": [
      1,
      2,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded state-feedback command",
    "output_signal_id": "closed-loop state response and control effort",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded state-feedback command to baseline and verify that closed-loop state response and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective closed-loop state response and control effort direction with its final direction.",
    "delay": "Measure from the logged bounded state-feedback command edge to the first effective closed-loop state response and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded state-feedback command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 129. Introduce a step reference robustly into a Type 1 DC-motor loop

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is state feedback voltage, and the measured outputs are motor position and speed, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor position starts in its final direction rather than moving the opposite way first; after the input changes, the motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in state feedback voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor position and speed measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor position.

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

### Example Data (Natural Language)

Use motor A=[[0,1],[0,-1]], B=[0,1], K=[8,3], and reference gain Nbar=8; apply +/-1 position steps.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      8
    ],
    "denominator": [
      1,
      4,
      8
    ],
    "input_delay_s": 0,
    "input_signal_id": "state feedback voltage",
    "output_signal_id": "motor position and speed",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return state feedback voltage to baseline and verify that motor position and speed remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor position and speed direction with its final direction.",
    "delay": "Measure from the logged state feedback voltage edge to the first effective motor position and speed sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log state feedback voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 130. Select dominant second-order poles for a third-order drone model

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is control moment, and the measured outputs are drone attitude response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in drone attitude response starts in its final direction rather than moving the opposite way first; after the input changes, the drone attitude response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the drone attitude response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in control moment produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the drone attitude response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for drone attitude response.

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

### Example Data (Natural Language)

Use the three-state drone model, K=[14,56,96], and Nbar=96; apply unit altitude steps at 0.005 s for 10 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      96
    ],
    "denominator": [
      1,
      16,
      56,
      96
    ],
    "input_delay_s": 0,
    "input_signal_id": "control moment",
    "output_signal_id": "drone attitude response",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return control moment to baseline and verify that drone attitude response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective drone attitude response direction with its final direction.",
    "delay": "Measure from the logged control moment edge to the first effective drone attitude response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log control moment and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 131. Balance tracking error and effort with LQR for the drone

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is optimal control moment, and the measured outputs are drone state and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in drone state starts in its final direction rather than moving the opposite way first; after the input changes, the drone state response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the drone state response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in optimal control moment produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the drone state and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for drone state.

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

### Example Data (Natural Language)

Use the drone model with Q=100 C^T C, R=1 and LQR K=[2.8728,9.8720,10]; compare rho=10,100,1000.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      10
    ],
    "denominator": [
      1,
      4.8728,
      9.872,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "optimal control moment",
    "output_signal_id": "drone state and control effort",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return optimal control moment to baseline and verify that drone state and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective drone state and control effort direction with its final direction.",
    "delay": "Measure from the logged optimal control moment edge to the first effective drone state and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log optimal control moment and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 132. Design and validate a full-order pendulum state estimator

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is known pivot torque, and the measured outputs are measured angle and estimated state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured angle starts in its final direction rather than moving the opposite way first; after the input changes, the measured angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the measured angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in known pivot torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the measured angle and estimated state measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for measured angle.

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

### Example Data (Natural Language)

Use omega0=1 and full-order estimator L=[20,99]; initialize the estimate at [0.2,-0.1] while the plant starts at zero.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        -20,
        1
      ],
      [
        -100,
        0
      ]
    ],
    "b": [
      [
        0
      ],
      [
        0
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "angle_error",
      "rate_error"
    ],
    "input_signal_ids": [
      "known pivot torque"
    ],
    "output_signal_ids": [
      "measured angle and estimated state channel 1",
      "measured angle and estimated state channel 2"
    ],
    "initial_state": [
      0.2,
      -0.1
    ],
    "signal_units": {}
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 2,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return known pivot torque to baseline and verify that measured angle and estimated state remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective measured angle and estimated state direction with its final direction.",
    "delay": "Measure from the logged known pivot torque edge to the first effective measured angle and estimated state sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log known pivot torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 133. Design a reduced-order pendulum estimator without differentiating the measurement

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is known pivot torque, and the measured outputs are measured angle and estimated rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured angle starts in its final direction rather than moving the opposite way first; after the input changes, the measured angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the measured angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in known pivot torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the measured angle and estimated rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for measured angle.

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

### Example Data (Natural Language)

Use omega0=1 and reduced observer gain L=10; estimate rate from measured angle without numerical differentiation.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      10
    ],
    "input_delay_s": 0,
    "input_signal_id": "known pivot torque",
    "output_signal_id": "measured angle and estimated rate",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 5,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return known pivot torque to baseline and verify that measured angle and estimated rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective measured angle and estimated rate direction with its final direction.",
    "delay": "Measure from the logged known pivot torque edge to the first effective measured angle and estimated rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log known pivot torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 134. Select estimator poles from a symmetric root locus under process/sensor noise tradeoffs

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is known plant input, and the measured outputs are state estimate and innovation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state estimate starts in its final direction rather than moving the opposite way first; after the input changes, the state estimate response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the state estimate response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in known plant input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the state estimate and innovation measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state estimate.

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

### Example Data (Natural Language)

Use omega0=1, noise ratio q=365, and estimator poles -3+/-j3.18; compare q/10, q, 10q with identical noise seeds.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      6,
      19.1124
    ],
    "input_delay_s": 0,
    "input_signal_id": "known plant input",
    "output_signal_id": "state estimate and innovation",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return known plant input to baseline and verify that state estimate and innovation remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective state estimate and innovation direction with its final direction.",
    "delay": "Measure from the logged known plant input edge to the first effective state estimate and innovation sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log known plant input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 135. Combine controller and estimator by the separation principle and form a DC-servo compensator

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is dynamic compensator voltage, and the measured outputs are servo output, estimated state, and control effort, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo output starts in its final direction rather than moving the opposite way first; after the input changes, the servo output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the servo output response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in dynamic compensator voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the servo output, estimated state, and control effort measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo output.

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

### Example Data (Natural Language)

Use servo G=10/[s(s+2)(s+8)], K=[-46.4,5.76,-0.65], L=[0.56,1.42,16]; sweep loop gain only within a stopped simulation.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      10
    ],
    "denominator": [
      1,
      10,
      16,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "dynamic compensator voltage",
    "output_signal_id": "servo output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return dynamic compensator voltage to baseline and verify that servo output, estimated state, and control effort remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective servo output, estimated state, and control effort direction with its final direction.",
    "delay": "Measure from the logged dynamic compensator voltage edge to the first effective servo output, estimated state, and control effort sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log dynamic compensator voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 136. Assign controller feedforward zeros to increase a servomechanism velocity constant

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is two-input or equivalent lag-lead command, and the measured outputs are servo position, tracking error, and slow tail, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first; after the input changes, the servo position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in two-input or equivalent lag-lead command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the servo position, tracking error, and slow tail measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.

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

### Example Data (Natural Language)

Use G=1/[s(s+1)], K=[8,3], estimator pole -0.1, controller zero -0.096, and verify Kv=10 with a unit ramp.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      8.32,
      8.32,
      0.8
    ],
    "denominator": [
      1,
      4.0996,
      0.08
    ],
    "input_delay_s": 0,
    "input_signal_id": "two-input or equivalent lag-lead command",
    "output_signal_id": "servo position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 200,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return two-input or equivalent lag-lead command to baseline and verify that servo position, tracking error, and slow tail remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective servo position, tracking error, and slow tail direction with its final direction.",
    "delay": "Measure from the logged two-input or equivalent lag-lead command edge to the first effective servo position, tracking error, and slow tail sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log two-input or equivalent lag-lead command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 137. Add integral state feedback for robust motor-speed tracking and constant-disturbance rejection

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is motor voltage, and the measured outputs are motor speed and integral error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in motor speed starts in its final direction rather than moving the opposite way first; after the input changes, the motor speed response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the motor speed response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in motor voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the motor speed and integral error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for motor speed.

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

### Example Data (Natural Language)

Use motor xdot=-3x+u+w, integral state xI_dot=y-r, gains [25,7], and observer L=7; test reference and constant load separately.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      25
    ],
    "denominator": [
      1,
      10,
      25
    ],
    "input_delay_s": 0,
    "input_signal_id": "motor voltage",
    "output_signal_id": "motor speed and integral error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return motor voltage to baseline and verify that motor speed and integral error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective motor speed and integral error direction with its final direction.",
    "delay": "Measure from the logged motor voltage edge to the first effective motor speed and integral error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log motor voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 138. Embed a sinusoidal internal model for disk-drive tracking and rejection

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is voice-coil force, and the measured outputs are disk-head position and sinusoidal error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in disk-head position starts in its final direction rather than moving the opposite way first; after the input changes, the disk-head position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the disk-head position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in voice-coil force produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the disk-head position and sinusoidal error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for disk-head position.

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

### Example Data (Natural Language)

Use omega0=1 and controller gain vector [2.0718,16.3923,13.9282,4.4641]; track and reject sinusoids at 0.9,1.0,1.1 rad/s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      100
    ],
    "denominator": [
      1,
      8,
      32,
      80,
      100
    ],
    "input_delay_s": 0,
    "input_signal_id": "voice-coil force",
    "output_signal_id": "disk-head position and sinusoidal error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return voice-coil force to baseline and verify that disk-head position and sinusoidal error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective disk-head position and sinusoidal error direction with its final direction.",
    "delay": "Measure from the logged voice-coil force edge to the first effective disk-head position and sinusoidal error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log voice-coil force and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 139. Recover LQR loop shape with an LTR estimator while quantifying sensor-noise actuator activity

### Control Problem Description

This is a state-space control system made from a dynamic plant, measured or estimated states, and a feedback actuation path. The control input is body torque under prescribed sensor noise, and the measured outputs are attitude response and body-torque activity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in attitude response starts in its final direction rather than moving the opposite way first; after the input changes, the attitude response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the attitude response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body torque under prescribed sensor noise produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the attitude response and body-torque activity measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use satellite LQR K=[1,1.414] and LTR estimators q=1,10,100; inject identical unit sensor noise and record control RMS.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      1.414,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "body torque under prescribed sensor noise",
    "output_signal_id": "attitude response and body-torque activity",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return body torque under prescribed sensor noise to baseline and verify that attitude response and body-torque activity remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective attitude response and body-torque activity direction with its final direction.",
    "delay": "Measure from the logged body torque under prescribed sensor noise edge to the first effective attitude response and body-torque activity sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log body torque under prescribed sensor noise and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 140. Control a delayed heat exchanger with a Smith predictor and state-space pole placement

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is steam command through Smith predictor, and the measured outputs are delayed heat-exchanger temperature, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in delayed heat-exchanger temperature starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the delayed heat-exchanger temperature response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in steam command through Smith predictor produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the delayed heat-exchanger temperature measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use G0=1/[(10s+1)(60s+1)] with 5 s delay, K=[5.2,-0.17], L=[0.18,4.2], and Nbar=1.2055; perturb delay to 4.5 and 5.5 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      600,
      70,
      1
    ],
    "input_delay_s": 5,
    "input_signal_id": "steam command through Smith predictor",
    "output_signal_id": "delayed heat-exchanger temperature",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 400,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return steam command through Smith predictor to baseline and verify that delayed heat-exchanger temperature remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective delayed heat-exchanger temperature direction with its final direction.",
    "delay": "Measure from the logged steam command through Smith predictor edge to the first effective delayed heat-exchanger temperature sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log steam command through Smith predictor and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 141. Digitize a DC-motor lead controller with Tustin's bilinear approximation

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is digital motor voltage, and the measured outputs are sampled motor position and error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled motor position starts in its final direction rather than moving the opposite way first; after the input changes, the sampled motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the sampled motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital motor voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sampled motor position and error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled motor position.

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

### Example Data (Natural Language)

Use continuous lead 10(0.5s+1)/(0.1s+1), T=0.025 s, and Tustin coefficients u[k]=0.7778u[k-1]+45.56e[k]-43.33e[k-1].

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      45.56,
      -43.33
    ],
    "denominator": [
      1,
      -0.7778
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.025,
    "input_delay_s": 0,
    "input_signal_id": "digital motor voltage",
    "output_signal_id": "sampled motor position and error",
    "input_units": "error_unit",
    "output_units": "control_unit"
  },
  "experiment": {
    "sample_time_s": 0.025,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital motor voltage to baseline and verify that sampled motor position and error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sampled motor position and error direction with its final direction.",
    "delay": "Measure from the logged digital motor voltage edge to the first effective sampled motor position and error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital motor voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 142. Digitize the same lead controller with the zero-order-hold approximation

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is held motor voltage, and the measured outputs are sampled motor position and error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled motor position starts in its final direction rather than moving the opposite way first; after the input changes, the sampled motor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the sampled motor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in held motor voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sampled motor position and error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled motor position.

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

### Example Data (Natural Language)

Use the same continuous lead and T=0.025 s with ZOH recursion u[k]=0.7788u[k-1]+50e[k]-47.79e[k-1].

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      50,
      -47.79
    ],
    "denominator": [
      1,
      -0.7788
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.025,
    "input_delay_s": 0,
    "input_signal_id": "held motor voltage",
    "output_signal_id": "sampled motor position and error",
    "input_units": "error_unit",
    "output_units": "control_unit"
  },
  "experiment": {
    "sample_time_s": 0.025,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return held motor voltage to baseline and verify that sampled motor position and error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sampled motor position and error direction with its final direction.",
    "delay": "Measure from the logged held motor voltage edge to the first effective sampled motor position and error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log held motor voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 143. Design a space-station attitude controller with matched pole-zero emulation

### Control Problem Description

This is a rigid space-station attitude system whose digital controller preserves a continuous design through matched pole-zero emulation. The control input is digital body torque, and the measured outputs are space station attitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in space station attitude starts in its final direction rather than moving the opposite way first; after the input changes, the space station attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the space station attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the space station attitude measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for space station attitude.

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

### Example Data (Natural Language)

Use space-station G=1/s^2, continuous lead 0.81(s+0.2)/(s+2), MPZ T=1 s controller 0.389(z-0.82)/(z-0.135), then repeat at T=0.5 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.389,
      -0.319
    ],
    "denominator": [
      1,
      -0.135
    ],
    "time_domain": "discrete",
    "sample_time_s": 1,
    "input_delay_s": 0,
    "input_signal_id": "digital body torque",
    "output_signal_id": "space station attitude",
    "input_units": "rad",
    "output_units": "torque_unit"
  },
  "experiment": {
    "sample_time_s": 1,
    "duration_s": 80,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital body torque to baseline and verify that space station attitude remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective space station attitude direction with its final direction.",
    "delay": "Measure from the logged digital body torque edge to the first effective space station attitude sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital body torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 144. Compare continuous and sampled root loci for a first-order plant

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is held proportional command, and the measured outputs are sampled first-order output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled first-order output starts in its final direction rather than moving the opposite way first; after the input changes, the sampled first-order output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the sampled first-order output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in held proportional command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sampled first-order output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled first-order output.

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

### Example Data (Natural Language)

Use a=1 s^-1, T=0.1 s, alpha=exp(-0.1), and sweep proportional K across the exact sampled stability limit.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0,
      0.0951626
    ],
    "denominator": [
      1,
      -0.904837
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.1,
    "input_delay_s": 0,
    "input_signal_id": "held proportional command",
    "output_signal_id": "sampled first-order output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return held proportional command to baseline and verify that sampled first-order output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sampled first-order output direction with its final direction.",
    "delay": "Measure from the logged held proportional command edge to the first effective sampled first-order output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log held proportional command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 145. Design the space-station controller directly in the z-plane

### Control Problem Description

This is a rigid space-station attitude system whose controller dynamics are designed directly in the discrete domain. The control input is digital body torque, and the measured outputs are space station attitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in space station attitude starts in its final direction rather than moving the opposite way first; after the input changes, the space station attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the space station attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the space station attitude measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for space station attitude.

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

### Example Data (Natural Language)

Use exact ZOH Gd=0.5(z+1)/(z-1)^2 at T=1 s and direct controller 0.374(z-0.85)/z.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.374,
      -0.3179
    ],
    "denominator": [
      1,
      0
    ],
    "time_domain": "discrete",
    "sample_time_s": 1,
    "input_delay_s": 0,
    "input_signal_id": "digital body torque",
    "output_signal_id": "space station attitude",
    "input_units": "rad",
    "output_units": "torque_unit"
  },
  "experiment": {
    "sample_time_s": 1,
    "duration_s": 80,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital body torque to baseline and verify that space station attitude remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective space station attitude direction with its final direction.",
    "delay": "Measure from the logged digital body torque edge to the first effective space station attitude sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital body torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 146. Compare continuous, emulated, and direct-discrete damping and step response

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is continuous or digital command, and the measured outputs are continuous and sampled step responses, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in continuous starts in its final direction rather than moving the opposite way first; after the input changes, the continuous response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the continuous response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in continuous or digital command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the continuous and sampled step responses measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for continuous.

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

### Example Data (Natural Language)

At T=1 s compare continuous lead, MPZ 0.389(z-0.82)/(z-0.135), and direct 0.374(z-0.85)/z on the same exact ZOH plant.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.374,
      -0.3179
    ],
    "denominator": [
      1,
      0
    ],
    "time_domain": "discrete",
    "sample_time_s": 1,
    "input_delay_s": 0,
    "input_signal_id": "continuous or digital command",
    "output_signal_id": "continuous and sampled step responses",
    "input_units": "rad",
    "output_units": "torque_unit"
  },
  "experiment": {
    "sample_time_s": 1,
    "duration_s": 80,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return continuous or digital command to baseline and verify that continuous and sampled step responses remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective continuous and sampled step responses direction with its final direction.",
    "delay": "Measure from the logged continuous or digital command edge to the first effective continuous and sampled step responses sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log continuous or digital command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 147. Recover a filter difference equation, pole damping, and stability from its z transfer function

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is discrete filter input, and the measured outputs are filter output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in filter output starts in its final direction rather than moving the opposite way first; after the input changes, the filter output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the filter output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in discrete filter input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the filter output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for filter output.

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

### Example Data (Natural Language)

Use H(z)=(1+0.5z^-1)/[(1-0.5z^-1)(1+z^-1/3)] at 1 Hz and excite impulse, step, and alternating inputs.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      0.5
    ],
    "denominator": [
      1,
      -0.1666667,
      -0.1666667
    ],
    "time_domain": "discrete",
    "sample_time_s": 1,
    "input_delay_s": 0,
    "input_signal_id": "discrete filter input",
    "output_signal_id": "filter output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 1,
    "duration_s": 40,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return discrete filter input to baseline and verify that filter output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective filter output direction with its final direction.",
    "delay": "Measure from the logged discrete filter input edge to the first effective filter output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log discrete filter input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 148. Solve a forced second-order difference equation by the z-transform

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is ramp sequence input, and the measured outputs are discrete sequence output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in discrete sequence output starts in its final direction rather than moving the opposite way first; after the input changes, the discrete sequence output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the discrete sequence output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in ramp sequence input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the discrete sequence output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for discrete sequence output.

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

### Example Data (Natural Language)

Use y[k]-3y[k-1]+2y[k-2]=2u[k-1]-2u[k-2], u[k]=k, and zero prehistory for k=0..15.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0,
      2
    ],
    "denominator": [
      1,
      -2
    ],
    "time_domain": "discrete",
    "sample_time_s": 1,
    "input_delay_s": 0,
    "input_signal_id": "ramp sequence input",
    "output_signal_id": "discrete sequence output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 1,
    "duration_s": 15,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return ramp sequence input to baseline and verify that discrete sequence output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective discrete sequence output direction with its final direction.",
    "delay": "Measure from the logged ramp sequence input edge to the first effective discrete sequence output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log ramp sequence input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 149. Prove and use the mapping properties between the s-plane and z-plane

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is prescribed modal mapping test, and the measured outputs are continuous and sampled free-response modes, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in continuous starts in its final direction rather than moving the opposite way first; after the input changes, the continuous response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the continuous response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed modal mapping test produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the continuous and sampled free-response modes measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for continuous.

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

### Example Data (Natural Language)

With T=0.1 s map s=-1+/-j2 and compare s=-1+/-j(2+2pi/T); verify identical z poles and aliasing.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      -1.773602,
      0.818731
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.1,
    "input_delay_s": 0,
    "input_signal_id": "prescribed modal mapping test",
    "output_signal_id": "continuous and sampled free-response modes",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed modal mapping test to baseline and verify that continuous and sampled free-response modes remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective continuous and sampled free-response modes direction with its final direction.",
    "delay": "Measure from the logged prescribed modal mapping test edge to the first effective continuous and sampled free-response modes sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed modal mapping test and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 150. Map a continuous lag compensator to a 20 Hz digital implementation

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is digital lag command, and the measured outputs are regulated output and digital error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the regulated output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in digital lag command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the regulated output and digital error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.

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

### Example Data (Natural Language)

Use lag (0.8s+1)/(50s+1), fs=20 Hz, and MPZ recursion with zero 0.93941, pole 0.99900, gain 0.01650.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.0165,
      -0.0155
    ],
    "denominator": [
      1,
      -0.999
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.05,
    "input_delay_s": 0,
    "input_signal_id": "digital lag command",
    "output_signal_id": "regulated output and digital error",
    "input_units": "error_unit",
    "output_units": "control_unit"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital lag command to baseline and verify that regulated output and digital error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output and digital error direction with its final direction.",
    "delay": "Measure from the logged digital lag command edge to the first effective regulated output and digital error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital lag command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 151. Compare Tustin and matched pole-zero digitizations of a lead network

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is sampled error, and the measured outputs are lead network magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lead network magnitude starts in its final direction rather than moving the opposite way first; after the input changes, the lead network magnitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the lead network magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sampled error produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the lead network magnitude and phase measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lead network magnitude.

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

### Example Data (Natural Language)

Digitize H=(s+1)/(s+10.1) at T=0.25 s by Tustin and MPZ; compare phase at 3 rad/s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.49724,
      -0.38675
    ],
    "denominator": [
      1,
      0.11602
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.25,
    "input_delay_s": 0,
    "input_signal_id": "sampled error",
    "output_signal_id": "lead network magnitude and phase",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.25,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sampled error to baseline and verify that lead network magnitude and phase remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective lead network magnitude and phase direction with its final direction.",
    "delay": "Measure from the logged sampled error edge to the first effective lead network magnitude and phase sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sampled error and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 152. Compare Tustin and matched pole-zero digitizations of a lag network

### Control Problem Description

This is an electrical signal-processing network made from resistive, capacitive, inductive, or operational-amplifier elements. The control input is sampled error, and the measured outputs are lag network magnitude and phase, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lag network magnitude starts in its final direction rather than moving the opposite way first; after the input changes, the lag network magnitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the lag network magnitude response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sampled error produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the lag network magnitude and phase measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lag network magnitude.

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

### Example Data (Natural Language)

Digitize H=(10s+1)/(100s+1) at T=0.25 s by Tustin and MPZ; evaluate at 3 rad/s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.101124,
      -0.098627
    ],
    "denominator": [
      1,
      -0.997503
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.25,
    "input_delay_s": 0,
    "input_signal_id": "sampled error",
    "output_signal_id": "lag network magnitude and phase",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.25,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sampled error to baseline and verify that lag network magnitude and phase remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective lag network magnitude and phase direction with its final direction.",
    "delay": "Measure from the logged sampled error edge to the first effective lag network magnitude and phase sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sampled error and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 153. Digitize a PID at three sample periods and assess transient degradation

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is digital PID command, and the measured outputs are sampled step response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled step response starts in its final direction rather than moving the opposite way first; after the input changes, the sampled step response response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the sampled step response response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital PID command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sampled step response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled step response.

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

### Example Data (Natural Language)

Use G=1/[s(s+1)] and PID K=15.2,Td=0.3816 s,Ti=0.95 s; discretize at T=1,0.1,0.01 s and record output plus control.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      74.003,
      -130.406,
      58.003
    ],
    "denominator": [
      1,
      -1
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.1,
    "input_delay_s": 0,
    "input_signal_id": "digital PID command",
    "output_signal_id": "sampled step response",
    "input_units": "error_unit",
    "output_units": "control_unit"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital PID command to baseline and verify that sampled step response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sampled step response direction with its final direction.",
    "delay": "Measure from the logged digital PID command edge to the first effective sampled step response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital PID command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 154. Determine the sampled-data stability-gain range of a plant with an unstable mode

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is held proportional command, and the measured outputs are sampled plant output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled plant output starts in its final direction rather than moving the opposite way first; after the input changes, the sampled plant output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in sampled plant output keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in held proportional command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sampled plant output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled plant output.

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

### Example Data (Natural Language)

Use the exact T=1 s ZOH model Gd=(7.96703z^2+1.33509z-0.324537)/(z^3-3.57119z^2+1.000162z-0.0000454) and scan K>0.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      7.96703,
      1.33509,
      -0.324537
    ],
    "denominator": [
      1,
      -3.57119,
      1.000162,
      -4.54e-05
    ],
    "time_domain": "discrete",
    "sample_time_s": 1,
    "input_delay_s": 0,
    "input_signal_id": "held proportional command",
    "output_signal_id": "sampled plant output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 1,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return held proportional command to baseline and verify that sampled plant output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sampled plant output direction with its final direction.",
    "delay": "Measure from the logged held proportional command edge to the first effective sampled plant output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log held proportional command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 155. Design discrete proportional-plus-velocity satellite attitude feedback

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is digital torque, and the measured outputs are satellite attitude and sampled rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite attitude starts in its final direction rather than moving the opposite way first; after the input changes, the satellite attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the satellite attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the satellite attitude and sampled rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for satellite attitude.

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

### Example Data (Natural Language)

Use T=0.1 s exact double-integrator model and state feedback Kp=1.8097,Kv=1.9032 targeting z=exp((-1+/-j1)T).

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0.9909515,
        0.0904841
      ],
      [
        -0.18097,
        0.8096825
      ]
    ],
    "b": [
      [
        0.0090485
      ],
      [
        0.18097
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.1,
    "state_names": [
      "angle",
      "rate"
    ],
    "input_signal_ids": [
      "digital torque"
    ],
    "output_signal_ids": [
      "satellite attitude and sampled rate channel 1",
      "satellite attitude and sampled rate channel 2"
    ],
    "initial_state": [
      0,
      0
    ],
    "signal_units": {}
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital torque to baseline and verify that satellite attitude and sampled rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective satellite attitude and sampled rate direction with its final direction.",
    "delay": "Measure from the logged digital torque edge to the first effective satellite attitude and sampled rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 156. Linearize and digitally stabilize a magnetic-levitation ball subject to sensor/current limits

### Control Problem Description

This is a magnetic-levitation apparatus in which an electromagnet supports a steel ball while a sensor measures the air gap. The control input is electromagnet current, and the measured outputs are ball displacement and current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ball displacement starts in its final direction rather than moving the opposite way first; after the input changes, the ball displacement response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in ball displacement keeps growing instead of returning, so the trial must stop before a limit is crossed. Applying small positive and negative changes in electromagnet current produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the ball displacement and current measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use m=0.02 kg,k1=20 N/m,k2=0.4 N/A,T=0.02 s; test state feedback Kx=94 A/m,Kv=2.08 A*s/m from x0=+/-0.25 cm with 1 A current limit.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        1.206756,
        0.0213603
      ],
      [
        21.360255,
        1.206756
      ]
    ],
    "b": [
      [
        0.00413512
      ],
      [
        0.4272051
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.02,
    "state_names": [
      "position",
      "velocity"
    ],
    "input_signal_ids": [
      "electromagnet current"
    ],
    "output_signal_ids": [
      "ball displacement and current channel 1",
      "ball displacement and current channel 2"
    ],
    "initial_state": [
      0.0025,
      0
    ],
    "signal_units": {
      "position": "m",
      "velocity": "m/s",
      "coil_current": "A"
    }
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 2,
    "initial_output": 0,
    "input_amplitudes": [
      -0.25,
      -0.125,
      0.125,
      0.25
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return electromagnet current to baseline and verify that ball displacement and current remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective ball displacement and current direction with its final direction.",
    "delay": "Measure from the logged electromagnet current edge to the first effective ball displacement and current sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log electromagnet current and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 157. Redesign a lead-lag servomechanism directly in the z-plane

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is digital servo voltage, and the measured outputs are servo position and ramp error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in servo position starts in its final direction rather than moving the opposite way first; after the input changes, the servo position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the servo position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital servo voltage produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the servo position and ramp error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for servo position.

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

### Example Data (Natural Language)

Use G=10/[s(s+1)(s+10)], fs=15 Hz and its exact ZOH coefficients; design directly for Mp<=16%,tr<=0.4 s,Kv_d>1.333.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0,
      0.00041424,
      0.0013906,
      0.00028724
    ],
    "denominator": [
      1,
      -2.4489241,
      1.92922941,
      -0.4803053
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.0666667,
    "input_delay_s": 0,
    "input_signal_id": "digital servo voltage",
    "output_signal_id": "servo position and ramp error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.0666667,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital servo voltage to baseline and verify that servo position and ramp error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective servo position and ramp error direction with its final direction.",
    "delay": "Measure from the logged digital servo voltage edge to the first effective servo position and ramp error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital servo voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 158. Design an antenna-servo controller by emulation and direct z-plane root locus

### Control Problem Description

This is an electromechanical motion apparatus made from a motor, mechanical load, and position or speed sensing. The control input is digital motor torque, and the measured outputs are antenna angle, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in antenna angle starts in its final direction rather than moving the opposite way first; after the input changes, the antenna angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the antenna angle response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in digital motor torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the antenna angle measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use antenna J=600000,B=20000 and T=10 s; compare emulation and direct z design on the same exact ZOH plant.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0,
      7.479697e-05,
      6.693738e-05
    ],
    "denominator": [
      1,
      -1.71653131,
      0.71653131
    ],
    "time_domain": "discrete",
    "sample_time_s": 10,
    "input_delay_s": 0,
    "input_signal_id": "digital motor torque",
    "output_signal_id": "antenna angle",
    "input_units": "Nm",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 10,
    "duration_s": 1000,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital motor torque to baseline and verify that antenna angle remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective antenna angle direction with its final direction.",
    "delay": "Measure from the logged digital motor torque edge to the first effective antenna angle sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital motor torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 159. Design discrete compensation for a two-real-pole plant under rise-time and overshoot limits

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is digital compensated command, and the measured outputs are sampled plant output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in sampled plant output starts in its final direction rather than moving the opposite way first; after the input changes, the sampled plant output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the sampled plant output response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in digital compensated command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the sampled plant output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for sampled plant output.

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

### Example Data (Natural Language)

Use exact T=0.1 s Gd=(0.00451991z+0.00407643)/(z^2-1.73086805z+0.73344696) and D=6.1882(z-0.27594)/z.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      6.1882,
      -1.70762
    ],
    "denominator": [
      1,
      0
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.1,
    "input_delay_s": 0,
    "input_signal_id": "digital compensated command",
    "output_signal_id": "sampled plant output",
    "input_units": "error_unit",
    "output_units": "control_unit"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digital compensated command to baseline and verify that sampled plant output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective sampled plant output direction with its final direction.",
    "delay": "Measure from the logged digital compensated command edge to the first effective sampled plant output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digital compensated command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 160. Explain the unavoidable one-sample delay in a causal discrete derivative

### Control Problem Description

This is a digital control system made from a sampler, numerical controller, hold element, and continuous or discrete plant. The control input is sampled error sequence, and the measured outputs are estimated error-rate response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in estimated error-rate response starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the estimated error-rate response response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in sampled error sequence produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the estimated error-rate response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for estimated error-rate response.

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

### Example Data (Natural Language)

Use backward difference with T=0.1 s and KTd=1, so u[k]=10(e[k]-e[k-1]); compare with the noncausal forward difference offline only.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      10,
      -10
    ],
    "denominator": [
      1
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.1,
    "input_delay_s": 0,
    "input_signal_id": "sampled error sequence",
    "output_signal_id": "estimated error-rate response",
    "input_units": "error_unit",
    "output_units": "control_unit"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sampled error sequence to baseline and verify that estimated error-rate response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective estimated error-rate response direction with its final direction.",
    "delay": "Measure from the logged sampled error sequence edge to the first effective estimated error-rate response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sampled error sequence and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 161. Find pendulum equilibria and classify their small-signal stability

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is pivot torque, and the measured outputs are pendulum angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first; after the input changes, the pendulum angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in pendulum angle keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of pivot torque changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the pendulum angle and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use g=9.81 m/s^2,l=1 m and test equilibria theta=0 and pi with +/-0.05 rad perturbations for 10 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        1
      ],
      [
        -9.81,
        0
      ]
    ],
    "b": [
      [
        0
      ],
      [
        1
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "angle",
      "rate"
    ],
    "input_signal_ids": [
      "pivot torque"
    ],
    "output_signal_ids": [
      "pendulum angle and angular rate channel 1",
      "pendulum angle and angular rate channel 2"
    ],
    "initial_state": [
      0.05,
      0
    ],
    "signal_units": {
      "angle": "rad",
      "rate": "rad/s"
    }
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return pivot torque to baseline and verify that pendulum angle and angular rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pendulum angle and angular rate direction with its final direction.",
    "delay": "Measure from the logged pivot torque edge to the first effective pendulum angle and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log pivot torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 162. Linearize a magnetic ball levitator from experimentally measured force curves

### Control Problem Description

This is a magnetic-levitation apparatus in which an electromagnet supports a steel ball while a sensor measures the air gap. The control input is electromagnet current perturbation, and the measured outputs are ball displacement, velocity, coil current, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in ball displacement starts in its final direction rather than moving the opposite way first; after the input changes, the ball displacement response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. Even after the input returns to baseline, the deviation in ball displacement keeps growing instead of returning, so the trial must stop before a limit is crossed. As the size or operating point of electromagnet current perturbation changes, magnetic force changes with air gap and coil current, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the ball displacement, velocity, coil current measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use m=0.0084 kg, equilibrium current 0.6 A, A=[[0,1],[1667,0]], B=[0,47.6]; test +/-10 mA around equilibrium.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        1
      ],
      [
        1667,
        0
      ]
    ],
    "b": [
      [
        0
      ],
      [
        47.6
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "position_perturbation",
      "velocity"
    ],
    "input_signal_ids": [
      "electromagnet current perturbation"
    ],
    "output_signal_ids": [
      "ball displacement",
      "velocity"
    ],
    "initial_state": [
      0.0001,
      0
    ],
    "signal_units": {
      "position_perturbation": "m",
      "velocity": "m/s",
      "current_perturbation": "A"
    }
  },
  "experiment": {
    "sample_time_s": 0.0002,
    "duration_s": 1,
    "initial_output": 0,
    "input_amplitudes": [
      -0.01,
      -0.005,
      0.005,
      0.01
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return electromagnet current perturbation to baseline and verify that ball displacement, velocity, coil current remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective ball displacement, velocity, coil current direction with its final direction.",
    "delay": "Measure from the logged electromagnet current perturbation edge to the first effective ball displacement, velocity, coil current sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log electromagnet current perturbation and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 163. Linearize nonlinear square-root water-tank outflow around an operating point

### Control Problem Description

This is a liquid-storage apparatus whose motion is set by inlet flow, outlet flow, and stored volume. The control input is inlet mass flow, and the measured outputs are tank level and outlet flow, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in tank level starts in its final direction rather than moving the opposite way first; after the input changes, the tank level response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the tank level response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of inlet mass flow reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the tank level and outlet flow measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, they change the response rate and final level by a modest amount without changing the main direction or channel structure.

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

### Example Data (Natural Language)

Use A=1 m^2,rho=1000 kg/m^3,R=0.5, h0=1 m, pa=0; perturb inflow by +/-10 kg/s and keep h positive.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.001
    ],
    "denominator": [
      1,
      0.09905
    ],
    "input_delay_s": 0,
    "input_signal_id": "inlet mass flow",
    "output_signal_id": "tank level and outlet flow",
    "input_units": "kg/s",
    "output_units": "m"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return inlet mass flow to baseline and verify that tank level and outlet flow remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective tank level and outlet flow direction with its final direction.",
    "delay": "Measure from the logged inlet mass flow edge to the first effective tank level and outlet flow sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log inlet mass flow and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 164. Cancel pendulum gravity by computed-torque nonlinear feedback

### Control Problem Description

This is a mechanical pendulum apparatus made from a pivot, rigid link, and concentrated moving mass. The control input is computed pivot torque, and the measured outputs are pendulum angle and angular rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in pendulum angle starts in its final direction rather than moving the opposite way first; after the input changes, the pendulum angle response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the pendulum angle response retains an offset or keeps drifting rather than returning through its own restoring action. As the size or operating point of computed pivot torque changes, pendulum geometry and gravity change with angle, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the pendulum angle and angular rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for pendulum angle.

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

### Example Data (Natural Language)

Use m=l=1,g=9.81 and computed torque Tc=mgl sin(theta)+u with u=-4(theta-r)-4 theta_dot; test commands up to +/-1 rad.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      4
    ],
    "denominator": [
      1,
      4,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "computed pivot torque",
    "output_signal_id": "pendulum angle and angular rate",
    "input_units": "rad",
    "output_units": "rad"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return computed pivot torque to baseline and verify that pendulum angle and angular rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective pendulum angle and angular rate direction with its final direction.",
    "delay": "Measure from the logged computed pivot torque edge to the first effective pendulum angle and angular rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log computed pivot torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "Tc=m*g*l*sin(theta)+u",
    "m_kg": 1,
    "l_m": 1,
    "g": 9.81
  }
}
```

---

## 165. Cancel a rapid-thermal-processing lamp square law with an inverse nonlinearity

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is commanded lamp voltage, and the measured outputs are lamp voltage and delivered power, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in lamp voltage starts in its final direction rather than moving the opposite way first; after the input changes, the lamp voltage response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the lamp voltage response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of commanded lamp voltage reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the lamp voltage and delivered power measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for lamp voltage.

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

### Example Data (Natural Language)

Use lamp law P=V^2, voltage limit 0..10 V, virtual power 0..100 W, inverse V=sqrt(Pcmd), and thermal G=1/(10s+1).

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      10,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "commanded lamp voltage",
    "output_signal_id": "lamp voltage and delivered power",
    "input_units": "W",
    "output_units": "temperature_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return commanded lamp voltage to baseline and verify that lamp voltage and delivered power remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective lamp voltage and delivered power direction with its final direction.",
    "delay": "Measure from the logged commanded lamp voltage edge to the first effective lamp voltage and delivered power sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log commanded lamp voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "P=V^2; V=sqrt(Pcmd)",
    "voltage_min_V": 0,
    "voltage_max_V": 10
  }
}
```

---

## 166. Predict amplitude-dependent overshoot caused by actuator saturation

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is amplitude-limited command, and the measured outputs are output, error, saturated control, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in output starts in its final direction rather than moving the opposite way first; after the input changes, the output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the output response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of amplitude-limited command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the output, error, saturated control measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for output.

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

### Example Data (Natural Language)

Use G=(s+1)/s^2,K=1,symmetric actuator limit +/-0.4, and step amplitudes 2,4,6,8,10,12.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      1
    ],
    "denominator": [
      1,
      1,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "amplitude-limited command",
    "output_signal_id": "output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 50,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return amplitude-limited command to baseline and verify that output, error, saturated control remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective output, error, saturated control direction with its final direction.",
    "delay": "Measure from the logged amplitude-limited command edge to the first effective output, error, saturated control sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log amplitude-limited command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "u=clip(e,-0.4,0.4)",
    "limit": 0.4
  }
}
```

---

## 167. Expose large-signal instability in a conditionally stable saturated loop

### Control Problem Description

This is a conditionally stable feedback loop whose actuator clips large proportional commands at fixed limits. The control input is saturated proportional command, and the measured outputs are regulated output, loop error, and saturated control signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in regulated output starts in its final direction rather than moving the opposite way first; after the input changes, the regulated output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the regulated output response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of saturated proportional command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the regulated output, loop error, and saturated control signal measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for regulated output.

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

### Example Data (Natural Language)

Use G=(s+1)^2/s^3,K=2, saturation +/-1, and steps 1,2,3,3.5; stop if state bounds are crossed.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2,
      4,
      2
    ],
    "denominator": [
      1,
      2,
      4,
      2
    ],
    "input_delay_s": 0,
    "input_signal_id": "saturated proportional command",
    "output_signal_id": "regulated output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return saturated proportional command to baseline and verify that regulated output, loop error, and saturated control signal remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective regulated output, loop error, and saturated control signal direction with its final direction.",
    "delay": "Measure from the logged saturated proportional command edge to the first effective regulated output, loop error, and saturated control signal sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log saturated proportional command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "unit-slope saturation +/-1",
    "nominal_gain": 2
  }
}
```

---

## 168. Predict a saturation-induced flexible-mode limit cycle and eliminate it with a notch

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is notch-shaped limited command, and the measured outputs are flexible displacement and saturated command, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in flexible displacement starts in its final direction rather than moving the opposite way first; after the input changes, the flexible displacement response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the flexible displacement response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of notch-shaped limited command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the flexible displacement and saturated command measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for flexible displacement.

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

### Example Data (Natural Language)

Use G=1/[s(s^2+0.2s+1)],K=0.5,saturation +/-0.1; compare with notch 123(s^2+0.18s+0.81)/(s+10)^2.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      0.2,
      1,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "notch-shaped limited command",
    "output_signal_id": "flexible displacement and saturated command",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 200,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return notch-shaped limited command to baseline and verify that flexible displacement and saturated command remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective flexible displacement and saturated command direction with its final direction.",
    "delay": "Measure from the logged notch-shaped limited command edge to the first effective flexible displacement and saturated command sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log notch-shaped limited command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "unit-slope saturation +/-0.1",
    "notch_num": [
      123,
      22.14,
      99.63
    ],
    "notch_den": [
      1,
      20,
      100
    ]
  }
}
```

---

## 169. Add back-calculation antiwindup to a saturated PI-controlled integrator

### Control Problem Description

This is an integrating plant driven by a PI controller, a saturated actuator, and a back-calculation antiwindup path. The control input is saturated PI command, and the measured outputs are integrator output, plant output, actuator command, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in integrator output starts in its final direction rather than moving the opposite way first; after the input changes, the integrator output response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the integrator output response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of saturated PI command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the integrator output, plant output, actuator command measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for integrator output.

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

### Example Data (Natural Language)

Use plant 1/s, PI kp=2,ki=4, actuator +/-1, and back-calculation Ka=10; compare a 4-unit step with Ka=0.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      2,
      4
    ],
    "denominator": [
      1,
      2,
      4
    ],
    "input_delay_s": 0,
    "input_signal_id": "saturated PI command",
    "output_signal_id": "integrator output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return saturated PI command to baseline and verify that integrator output, plant output, actuator command remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective integrator output, plant output, actuator command direction with its final direction.",
    "delay": "Measure from the logged saturated PI command edge to the first effective integrator output, plant output, actuator command sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log saturated PI command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "u=clip(v,-1,1); xI_dot=4e+10(u-v)",
    "kp": 2,
    "ki": 4,
    "Ka": 10
  }
}
```

---

## 170. Derive the describing function of a saturation nonlinearity

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is bounded sinusoidal nonlinearity test, and the measured outputs are nonlinear input and fundamental output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in nonlinear input starts in its final direction rather than moving the opposite way first; after the input changes, the nonlinear input response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the nonlinear input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of bounded sinusoidal nonlinearity test reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the nonlinear input and fundamental output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for nonlinear input.

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

### Example Data (Natural Language)

Use saturation slope k=1,limit N=0.1 and sine amplitudes 0.05,0.1,0.2,0.5,1 at 1 rad/s; extract the first harmonic.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded sinusoidal nonlinearity test",
    "output_signal_id": "nonlinear input and fundamental output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded sinusoidal nonlinearity test to baseline and verify that nonlinear input and fundamental output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective nonlinear input and fundamental output direction with its final direction.",
    "delay": "Measure from the logged bounded sinusoidal nonlinearity test edge to the first effective nonlinear input and fundamental output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded sinusoidal nonlinearity test and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "clip(k*x,-N,N)",
    "k": 1,
    "N": 0.1
  }
}
```

---

## 171. Derive the describing function of an ideal relay

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is binary relay command, and the measured outputs are relay input and fundamental output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in relay input starts in its final direction rather than moving the opposite way first; after the input changes, the relay input response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the relay input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of binary relay command reveals a fixed relay switching law, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the relay input and fundamental output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for relay input.

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

### Example Data (Natural Language)

Use ideal relay levels +/-1 and sine amplitudes 0.25,0.5,1,2; extract fundamental and odd harmonics.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1.27324
    ],
    "denominator": [
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "binary relay command",
    "output_signal_id": "relay input and fundamental output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return binary relay command to baseline and verify that relay input and fundamental output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective relay input and fundamental output direction with its final direction.",
    "delay": "Measure from the logged binary relay command edge to the first effective relay input and fundamental output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log binary relay command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "y=sign(x)",
    "N": 1
  }
}
```

---

## 172. Derive the complex describing function of a relay with hysteresis

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is hysteretic relay command, and the measured outputs are hysteresis input and fundamental output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in hysteresis input starts in its final direction rather than moving the opposite way first; after the input changes, the hysteresis input response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the hysteresis input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of hysteretic relay command reveals fixed hysteresis and relay switching, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the hysteresis input and fundamental output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for hysteresis input.

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

### Example Data (Natural Language)

Use relay levels +/-1,hysteresis h=0.1 and sine amplitudes 0.08,0.12,0.24,0.5; preserve relay memory.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      5.30516
    ],
    "denominator": [
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "hysteretic relay command",
    "output_signal_id": "hysteresis input and fundamental output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return hysteretic relay command to baseline and verify that hysteresis input and fundamental output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective hysteresis input and fundamental output direction with its final direction.",
    "delay": "Measure from the logged hysteretic relay command edge to the first effective hysteresis input and fundamental output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log hysteretic relay command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "relay +/-N with thresholds +/-h",
    "N": 1,
    "h": 0.1
  }
}
```

---

## 173. Predict a saturation limit cycle from a Nyquist/describing-function intersection

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is saturated loop command, and the measured outputs are oscillation amplitude and frequency, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in oscillation amplitude starts in its final direction rather than moving the opposite way first; after the input changes, the oscillation amplitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the oscillation amplitude response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of saturated loop command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the oscillation amplitude and frequency measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for oscillation amplitude.

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

### Example Data (Natural Language)

Use G=1/[s(s^2+0.2s+1)] with saturation k=1,N=0.1; start near amplitudes 0.3,0.63,0.9 and measure steady oscillation.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      0.2,
      1,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "saturated loop command",
    "output_signal_id": "oscillation amplitude and frequency",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return saturated loop command to baseline and verify that oscillation amplitude and frequency remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective oscillation amplitude and frequency direction with its final direction.",
    "delay": "Measure from the logged saturated loop command edge to the first effective oscillation amplitude and frequency sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log saturated loop command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "unit-slope saturation +/-0.1"
  }
}
```

---

## 174. Predict a hysteresis-induced limit cycle from the same construction

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is hysteretic relay command, and the measured outputs are hysteretic oscillation amplitude and frequency, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in hysteretic oscillation amplitude starts in its final direction rather than moving the opposite way first; after the input changes, the hysteretic oscillation amplitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the hysteretic oscillation amplitude response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of hysteretic relay command reveals fixed hysteresis and relay switching, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the hysteretic oscillation amplitude and frequency measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for hysteretic oscillation amplitude.

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

### Example Data (Natural Language)

Use G=1/[s(s+1)], relay N=1,h=0.1; simulate from several initial relay states and measure the limit cycle.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      1,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "hysteretic relay command",
    "output_signal_id": "hysteretic oscillation amplitude and frequency",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return hysteretic relay command to baseline and verify that hysteretic oscillation amplitude and frequency remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective hysteretic oscillation amplitude and frequency direction with its final direction.",
    "delay": "Measure from the logged hysteretic relay command edge to the first effective hysteretic oscillation amplitude and frequency sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log hysteretic relay command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "relay +/-1 with thresholds +/-0.1"
  }
}
```

---

## 175. Derive bang-bang minimum-time switching and a chatter-reducing PTOS law for a double integrator

### Control Problem Description

This is a low-friction cart moving on a horizontal track, with a bidirectional drive and negligible passive restoring force. The control input is bounded acceleration command, and the measured outputs are position and velocity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in position starts in its final direction rather than moving the opposite way first; after the input changes, the position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the position response retains an offset or keeps drifting rather than returning through its own restoring action. Changing the direction and size of bounded acceleration command reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the position and velocity measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for position.

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

### Example Data (Natural Language)

Use double integrator, |u|<=1, initial states (1,0),(1,-1),(-1,1); compare bang-bang switching with a smoothed PTOS band.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded acceleration command",
    "output_signal_id": "position and velocity",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded acceleration command to baseline and verify that position and velocity remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective position and velocity direction with its final direction.",
    "delay": "Measure from the logged bounded acceleration command edge to the first effective position and velocity sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded acceleration command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "u=-sign(x1+0.5*x2*abs(x2)), clipped +/-1"
  }
}
```

---

## 176. Prove parameter-dependent stability of a second-order linear system with a Lyapunov equation

### Control Problem Description

This is a two-state autonomous linear system whose trajectories rotate and decay at rates set by two physical parameters. The control input is prescribed initial-state release, and the measured outputs are state trajectory and decay behavior, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in state trajectory starts in its final direction rather than moving the opposite way first; after the input changes, the state trajectory response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the state trajectory response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in prescribed initial-state release produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the state trajectory and decay behavior measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for state trajectory.

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

### Example Data (Natural Language)

Use alpha=1,beta=2, A=[[-1,2],[-2,-1]], Q=I, and initial states on radii 0.5,1,2.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        -1,
        2
      ],
      [
        -2,
        -1
      ]
    ],
    "b": [
      [
        0
      ],
      [
        0
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "x1",
      "x2"
    ],
    "input_signal_ids": [
      "prescribed initial-state release"
    ],
    "output_signal_ids": [
      "state trajectory and decay behavior channel 1",
      "state trajectory and decay behavior channel 2"
    ],
    "initial_state": [
      1,
      0
    ],
    "signal_units": {}
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return prescribed initial-state release to baseline and verify that state trajectory and decay behavior remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective state trajectory and decay behavior direction with its final direction.",
    "delay": "Measure from the logged prescribed initial-state release edge to the first effective state trajectory and decay behavior sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log prescribed initial-state release and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 177. Construct a direct Lyapunov function for nonlinear position feedback

### Control Problem Description

This is a damped position servo in which displacement error produces a nonlinear restoring action on the moving state. The control input is nonlinear restoring feedback, and the measured outputs are position error, velocity, and state trajectory, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in position error starts in its final direction rather than moving the opposite way first; after the input changes, the position error response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the position error response settles or remains bounded instead of developing self-growing motion. As the size or operating point of nonlinear restoring feedback changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the position error, velocity, and state trajectory measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for position error.

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

### Example Data (Natural Language)

Use T=1 and f(e)=e+e^3; simulate initial states e=+/-2,x2=+/-1 and evaluate V=0.5e^2+0.25e^4+0.5x2^2.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "state_space",
    "a": [
      [
        0,
        -1
      ],
      [
        1,
        -1
      ]
    ],
    "b": [
      [
        0
      ],
      [
        0
      ]
    ],
    "c": [
      [
        1,
        0
      ],
      [
        0,
        1
      ]
    ],
    "d": [
      [
        0
      ],
      [
        0
      ]
    ],
    "state_names": [
      "error",
      "velocity"
    ],
    "input_signal_ids": [
      "nonlinear restoring feedback"
    ],
    "output_signal_ids": [
      "position error",
      "velocity"
    ],
    "initial_state": [
      2,
      1
    ],
    "signal_units": {}
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return nonlinear restoring feedback to baseline and verify that position error, velocity, and state trajectory remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective position error, velocity, and state trajectory direction with its final direction.",
    "delay": "Measure from the logged nonlinear restoring feedback edge to the first effective position error, velocity, and state trajectory sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log nonlinear restoring feedback and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "f(e)=e+e^3"
  }
}
```

---

## 178. Bound a signum nonlinearity by a sector

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is bounded signum test signal, and the measured outputs are nonlinearity input and output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in nonlinearity input starts in its final direction rather than moving the opposite way first; after the input changes, the nonlinearity input response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the nonlinearity input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of bounded signum test signal reveals a fixed signum law, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the nonlinearity input and output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for nonlinearity input.

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

### Example Data (Natural Language)

Use f(e)=sign(e) over logarithmic amplitudes 1e-3 to 10 and compute the secant slope f(e)/e.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "bounded signum test signal",
    "output_signal_id": "nonlinearity input and output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return bounded signum test signal to baseline and verify that nonlinearity input and output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective nonlinearity input and output direction with its final direction.",
    "delay": "Measure from the logged bounded signum test signal edge to the first effective nonlinearity input and output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log bounded signum test signal and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "sign(e)",
    "sector": [
      0,
      "infinity"
    ]
  }
}
```

---

## 179. Bound actuator saturation by a sector

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is amplitude-limited actuator command, and the measured outputs are saturation input and output, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in saturation input starts in its final direction rather than moving the opposite way first; after the input changes, the saturation input response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the saturation input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of amplitude-limited actuator command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the saturation input and output measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for saturation input.

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

### Example Data (Natural Language)

Use unit-slope saturation +/-0.1 and amplitudes from 0.01 to 10; verify sector inequalities pointwise.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "amplitude-limited actuator command",
    "output_signal_id": "saturation input and output",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 10,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return amplitude-limited actuator command to baseline and verify that saturation input and output remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective saturation input and output direction with its final direction.",
    "delay": "Measure from the logged amplitude-limited actuator command edge to the first effective saturation input and output sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log amplitude-limited actuator command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "clip(e,-0.1,0.1)",
    "sector": [
      0,
      1
    ]
  }
}
```

---

## 180. Certify absolute stability of a saturated loop with the circle criterion

### Control Problem Description

This is a nonlinear feedback system made from a linear dynamic plant and a limited or switching element. The control input is sector-bounded actuator command, and the measured outputs are loop input, output, and closed-loop response, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in loop input starts in its final direction rather than moving the opposite way first; after the input changes, the loop input response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the loop input response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of sector-bounded actuator command reveals fixed actuator limiting, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the loop input, output, and closed-loop response measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When load, components, or operating conditions are varied safely and the trial is repeated, the direction, response timing, and final level stay almost unchanged for loop input.

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

### Example Data (Natural Language)

Use linear block G=(s+1)^2/s^3 with unit-slope saturation sector [0,1]; plot Nyquist against the Re(G)=-1 boundary and simulate bounded initial conditions.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      2,
      1
    ],
    "denominator": [
      1,
      0,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "sector-bounded actuator command",
    "output_signal_id": "loop input",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return sector-bounded actuator command to baseline and verify that loop input, output, and closed-loop response remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective loop input, output, and closed-loop response direction with its final direction.",
    "delay": "Measure from the logged sector-bounded actuator command edge to the first effective loop input, output, and closed-loop response sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log sector-bounded actuator command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "unit-slope saturation in sector [0,1]"
  }
}
```

---

## 181. Model a flexible two-body satellite and translate pointing specifications into robust design targets

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is body control torque, and the measured outputs are two satellite angles, rates, pointing error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in two satellite angles starts in its final direction rather than moving the opposite way first; after the input changes, the two satellite angles response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the two satellite angles response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in body control torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the two satellite angles, rates, pointing error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use J1=1,J2=0.1,k=0.091,b=0.0036 and G=0.036(s+25)/[s^2(s^2+0.04s+1)]; test k,b corners and pointing steps.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.036,
      0.9
    ],
    "denominator": [
      1,
      0.04,
      1,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "body control torque",
    "output_signal_id": "two satellite angles",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 200,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return body control torque to baseline and verify that two satellite angles, rates, pointing error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective two satellite angles, rates, pointing error direction with its final direction.",
    "delay": "Measure from the logged body control torque edge to the first effective two satellite angles, rates, pointing error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log body control torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 182. Compare gain stabilization and notch-based phase stabilization of the flexible satellite

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is gain-shaped or notch-shaped torque, and the measured outputs are satellite pointing and flexible deflection, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in satellite pointing starts in its final direction rather than moving the opposite way first; after the input changes, the satellite pointing response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the satellite pointing response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in gain-shaped or notch-shaped torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the satellite pointing and flexible deflection measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

On the nominal flexible satellite compare Dc1=0.25(2s+1), Dc2=0.001(30s+1), and Dc3=Dc1[((s/0.9)^2+1)/(s/25+1)^2] over all k,b corners.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.036,
      0.9
    ],
    "denominator": [
      1,
      0.04,
      1,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "gain-shaped or notch-shaped torque",
    "output_signal_id": "satellite pointing and flexible deflection",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 500,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return gain-shaped or notch-shaped torque to baseline and verify that satellite pointing and flexible deflection remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective satellite pointing and flexible deflection direction with its final direction.",
    "delay": "Measure from the logged gain-shaped or notch-shaped torque edge to the first effective satellite pointing and flexible deflection sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log gain-shaped or notch-shaped torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 183. Design satellite state feedback and an estimator from symmetric-root-locus pole choices

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is estimated-state feedback torque, and the measured outputs are measured attitude and estimated flexible states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured attitude starts in its final direction rather than moving the opposite way first; after the input changes, the measured attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the measured attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in estimated-state feedback torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the measured attitude and estimated flexible states measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use control poles -0.45+/-j0.34,-0.15+/-j1.05, K=[-0.2788,0.0546,0.6814,1.1655], and L=[222,42.3,1515.4,5503.9].

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.3578625
    ],
    "denominator": [
      1,
      1.2,
      1.7131,
      1.10793,
      0.3578625
    ],
    "input_delay_s": 0,
    "input_signal_id": "estimated-state feedback torque",
    "output_signal_id": "measured attitude and estimated flexible states",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 200,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return estimated-state feedback torque to baseline and verify that measured attitude and estimated flexible states remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective measured attitude and estimated flexible states direction with its final direction.",
    "delay": "Measure from the logged estimated-state feedback torque edge to the first effective measured attitude and estimated flexible states sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log estimated-state feedback torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 184. Redesign the satellite by collocating the attitude sensor with the torque actuator

### Control Problem Description

This is a spacecraft attitude-control system made from a rigid body, attitude actuator, and any modeled flexible appendage. The control input is collocated body torque, and the measured outputs are collocated attitude and remote flexible angle, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in collocated attitude starts in its final direction rather than moving the opposite way first; after the input changes, the collocated attitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the collocated attitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in collocated body torque produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the collocated attitude and remote flexible angle measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use collocated Gco=[(s+0.018)^2+0.954^2]/{s^2[(s+0.02)^2+1]} and controller 0.25(2s+1); compare with remote sensing.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1,
      0.036,
      0.91044
    ],
    "denominator": [
      1,
      0.04,
      1.0004,
      0,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "collocated body torque",
    "output_signal_id": "collocated attitude and remote flexible angle",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 200,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return collocated body torque to baseline and verify that collocated attitude and remote flexible angle remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective collocated attitude and remote flexible angle direction with its final direction.",
    "delay": "Measure from the logged collocated body torque edge to the first effective collocated attitude and remote flexible angle sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log collocated body torque and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 185. Linearize Boeing 747 longitudinal/lateral dynamics and identify Dutch-roll, spiral, roll, phugoid, and short-period modes

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control inputs are rudder, elevator, aileron, thrust, and the measured outputs are aircraft rates, attitude, speed, altitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in aircraft rates starts in its final direction rather than moving the opposite way first; after the input changes, the aircraft rates response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the aircraft rates response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in rudder, elevator, aileron, thrust produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the aircraft rates, attitude, speed, altitude measurements share one clock, all relevant motion can be reconstructed from these synchronized records; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use a representative Dutch-roll mode wn=1 rad/s,zeta=0.03 plus recorded spiral, roll, phugoid, and short-period modal estimates; excite rudder/elevator separately.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      1
    ],
    "denominator": [
      1,
      0.06,
      1
    ],
    "input_delay_s": 0,
    "input_signal_id": "rudder",
    "output_signal_id": "aircraft rates",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return rudder, elevator, aileron, thrust to baseline and verify that aircraft rates, attitude, speed, altitude remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective aircraft rates, attitude, speed, altitude direction with its final direction.",
    "delay": "Measure from the logged rudder, elevator, aileron, thrust edge to the first effective aircraft rates, attitude, speed, altitude sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log rudder, elevator, aileron, thrust and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 186. Design a yaw damper with rudder actuation, yaw-rate sensing, actuator dynamics, and washout

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is rudder command, and the measured outputs are yaw rate, sideslip, rudder position, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in yaw rate starts in its final direction rather than moving the opposite way first; after the input changes, the yaw rate response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the yaw rate response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in rudder command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the yaw rate, sideslip, rudder position measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use yaw gain Kr=2.6, washout s/(s+1/3), and rudder actuator 10/(s+10); test yaw-rate pulses and steady-turn commands.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      26,
      0
    ],
    "denominator": [
      1,
      10.333333,
      3.333333
    ],
    "input_delay_s": 0,
    "input_signal_id": "rudder command",
    "output_signal_id": "yaw rate",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return rudder command to baseline and verify that yaw rate, sideslip, rudder position remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective yaw rate, sideslip, rudder position direction with its final direction.",
    "delay": "Measure from the logged rudder command edge to the first effective yaw rate, sideslip, rudder position sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log rudder command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 187. Compare the practical yaw damper with a higher-order SRL controller-estimator design

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is rudder command from low or high order control, and the measured outputs are yaw rate and estimated lateral states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in yaw rate starts in its final direction rather than moving the opposite way first; after the input changes, the yaw rate response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the yaw rate response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in rudder command from low or high order control produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the yaw rate and estimated lateral states measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Compare the practical Kr=2.6 yaw damper with six-state feedback K=[1.059,-0.191,-2.32,0.0992,0.037,0.486] and its estimator under sensor noise.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.472225
    ],
    "denominator": [
      1,
      0.558,
      0.472225
    ],
    "input_delay_s": 0,
    "input_signal_id": "rudder command from low or high order control",
    "output_signal_id": "yaw rate and estimated lateral states",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.005,
    "duration_s": 200,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return rudder command from low or high order control to baseline and verify that yaw rate and estimated lateral states remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective yaw rate and estimated lateral states direction with its final direction.",
    "delay": "Measure from the logged rudder command from low or high order control edge to the first effective yaw rate and estimated lateral states sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log rudder command from low or high order control and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 188. Design an altitude-hold autopilot with pitch-rate/pitch inner loops and altitude outer-loop feedback

### Control Problem Description

This is an aircraft flight-control system made from aerodynamic motion, control-surface actuators, and onboard motion sensors. The control input is elevator command, and the measured outputs are altitude, pitch angle, pitch rate, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in altitude first moves in an unfavorable or opposite direction before turning; after the input changes, the altitude response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the altitude response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in elevator command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the altitude, pitch angle, pitch rate measurements share one clock, all relevant motion can be reconstructed from these synchronized records; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use an altitude channel with RHP zero +5.61, fast pitch inner loop, slower altitude outer loop, and compare with full-state K=[-0.0009,0.0016,-1.883,-7.603,-0.001].

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -1,
      5.61
    ],
    "denominator": [
      1,
      3,
      2,
      0
    ],
    "input_delay_s": 0,
    "input_signal_id": "elevator command",
    "output_signal_id": "altitude",
    "input_units": "deg",
    "output_units": "ft"
  },
  "experiment": {
    "sample_time_s": 0.01,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return elevator command to baseline and verify that altitude, pitch angle, pitch rate remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective altitude, pitch angle, pitch rate direction with its final direction.",
    "delay": "Measure from the logged elevator command edge to the first effective altitude, pitch angle, pitch rate sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log elevator command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 189. Model and tune PI feedback for a delayed automotive fuel-air process

### Control Problem Description

This is an automotive fuel-air control system made from fuel injection, engine gas transport, and an exhaust oxygen sensor. The control input is fuel injection command, and the measured outputs are fuel air ratio and oxygen sensor signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in fuel air ratio starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the fuel air ratio response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in fuel injection command produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the fuel air ratio and oxygen sensor signal measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use fast/slow fuel time constants 0.02 and 1 s, equal weights 0.5, transport delay 0.2 s, sensor lag 0.1 s, and PI aggregate gain KsKp=2.2.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.51,
      1
    ],
    "denominator": [
      0.002,
      0.122,
      1.12,
      1
    ],
    "input_delay_s": 0.2,
    "input_signal_id": "fuel injection command",
    "output_signal_id": "fuel air ratio and oxygen sensor signal",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 30,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return fuel injection command to baseline and verify that fuel air ratio and oxygen sensor signal remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective fuel air ratio and oxygen sensor signal direction with its final direction.",
    "delay": "Measure from the logged fuel injection command edge to the first effective fuel air ratio and oxygen sensor signal sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log fuel injection command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 190. Predict the nonlinear oxygen-sensor limit cycle by effective gain and describing function

### Control Problem Description

This is an automotive fuel-air control system made from fuel injection, engine gas transport, and an exhaust oxygen sensor. The control input is fuel injection command, and the measured outputs are air fuel error and oxygen sensor oscillation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in air fuel error starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the air fuel error response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of fuel injection command reveals a fixed static nonlinearity, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the air fuel error and oxygen sensor oscillation measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use the fuel-air dynamics, sensor output 0.1..0.9 with center slope 20, Kp=0.1, small-signal loop gain 6, and preserve saturation; measure the limit cycle.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.51,
      1
    ],
    "denominator": [
      0.002,
      0.122,
      1.12,
      1
    ],
    "input_delay_s": 0.2,
    "input_signal_id": "fuel injection command",
    "output_signal_id": "air fuel error and oxygen sensor oscillation",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return fuel injection command to baseline and verify that air fuel error and oxygen sensor oscillation remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective air fuel error and oxygen sensor oscillation direction with its final direction.",
    "delay": "Measure from the logged fuel injection command edge to the first effective air fuel error and oxygen sensor oscillation sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log fuel injection command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "oxygen sensor piecewise saturation 0.1..0.9",
    "sensor_limit": 0.4,
    "center_slope": 20,
    "Kp": 0.1
  }
}
```

---

## 191. Replace sensor-slope dependence by relay feedback to obtain robust average stoichiometry

### Control Problem Description

This is an automotive fuel-air control system made from fuel injection, engine gas transport, and an exhaust oxygen sensor. The control input is fuel injection command through relay-conditioned sensing, and the measured outputs are average fuel-air ratio and switching signal, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in average fuel-air ratio starts in its final direction rather than moving the opposite way first; after the input changes, a visible quiet interval separates the command from the first change, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the average fuel-air ratio response settles or remains bounded instead of developing self-growing motion. Changing the direction and size of fuel injection command through relay-conditioned sensing reveals a fixed relay switching law, but the nonproportional behavior is confined to this fixed input-output rule and adds no dynamic state. Because the input and the average fuel-air ratio and switching signal measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use relay q=N sign(vs-vstar) with illustrative N=0.05, the same fuel-air/PI dynamics, and test sensor slopes multiplied by 0.5,1,2.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.51,
      1
    ],
    "denominator": [
      0.002,
      0.122,
      1.12,
      1
    ],
    "input_delay_s": 0.2,
    "input_signal_id": "fuel injection command through relay-conditioned sensing",
    "output_signal_id": "average fuel-air ratio and switching signal",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 100,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return fuel injection command through relay-conditioned sensing to baseline and verify that average fuel-air ratio and switching signal remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective average fuel-air ratio and switching signal direction with its final direction.",
    "delay": "Measure from the logged fuel injection command through relay-conditioned sensing edge to the first effective average fuel-air ratio and switching signal sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log fuel injection command through relay-conditioned sensing and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "q=0.05*sign(vs-vstar)",
    "relay_height": 0.05
  }
}
```

---

## 192. Build decoupled longitudinal, lateral, yaw, and altitude state models for a quadrotor and map four rotor commands

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control inputs are four rotor thrust commands, and the measured outputs are position, attitude, angular rates, altitude, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in position starts in its final direction rather than moving the opposite way first; after the input changes, the position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in four rotor thrust commands produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the position, attitude, angular rates, altitude measurements share one clock, all relevant motion can be reconstructed from these synchronized records; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use a 1 kg, Iyy=0.02 kg*m^2 VTOL/quadrotor slice with thrust 0..20 N and torque +/-1 Nm; log all states and test rotor mixing columns one at a time.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "registered_nonlinear",
    "template_id": "vtol_cascaded",
    "parameters": {
      "mass_kg": 1,
      "pitch_inertia_kg_m2": 0.02,
      "gravity_m_s2": 9.81,
      "linear_drag_n_s_m": 0.25,
      "pitch_damping_n_m_s": 0.02,
      "thrust_min_n": 0,
      "thrust_max_n": 20,
      "torque_limit_n_m": 1
    },
    "initial_state": {
      "x_m": 0,
      "z_m": 0,
      "pitch_rad": 0,
      "x_velocity_m_s": 0,
      "z_velocity_m_s": 0,
      "pitch_rate_rad_s": 0
    },
    "input_signal_ids": [
      "four rotor thrust commands channel 1",
      "four rotor thrust commands channel 2"
    ],
    "output_signal_ids": [
      "position",
      "attitude",
      "angular rates",
      "altitude channel 1",
      "altitude channel 2",
      "altitude channel 3"
    ],
    "signal_units": {
      "x_m": "m",
      "z_m": "m",
      "pitch_rad": "rad",
      "x_velocity_m_s": "m/s",
      "z_velocity_m_s": "m/s",
      "pitch_rate_rad_s": "rad/s"
    }
  },
  "experiment": {
    "sample_time_s": 0.002,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -0.5,
      -0.25,
      0.25,
      0.5
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return four rotor thrust commands to baseline and verify that position, attitude, angular rates, altitude remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective position, attitude, angular rates, altitude direction with its final direction.",
    "delay": "Measure from the logged four rotor thrust commands edge to the first effective position, attitude, angular rates, altitude sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log four rotor thrust commands and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 193. Design cascaded inner-attitude and outer-position PD loops for quadrotor trajectory following

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control input is mixed rotor thrusts, and the measured outputs are quadrotor position, attitude, path error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in quadrotor position starts in its final direction rather than moving the opposite way first; after the input changes, the quadrotor position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the quadrotor position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in mixed rotor thrusts produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the quadrotor position, attitude, path error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use Gtheta=0.4(s+0.25)/[(s^2-3.2s+10.4)(s+3.4)(s+20)] and Gx=-131/[s times the same denominator]; close attitude faster than position.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.4,
      0.1
    ],
    "denominator": [
      1,
      20.2,
      3.52,
      25.76,
      707.2
    ],
    "input_delay_s": 0,
    "input_signal_id": "mixed rotor thrusts",
    "output_signal_id": "quadrotor position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return mixed rotor thrusts to baseline and verify that quadrotor position, attitude, path error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective quadrotor position, attitude, path error direction with its final direction.",
    "delay": "Measure from the logged mixed rotor thrusts edge to the first effective quadrotor position, attitude, path error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log mixed rotor thrusts and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 194. Design LQR/estimator controllers for quadrotor longitudinal, lateral, and yaw axes

### Control Problem Description

This is a multirotor flight-control system made from an airframe, thrust-producing rotors, and inertial motion states. The control inputs are LQR mixed rotor commands, and the measured outputs are measured and estimated quadrotor axis states, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in measured starts in its final direction rather than moving the opposite way first; after the input changes, the measured response begins within one sample without a separate silent interval, and the path from actuation to visible response contains at least three successive storage or integration processes. When the input is removed, the measured response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in LQR mixed rotor commands produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the measured and estimated quadrotor axis states measurements share one clock, all relevant motion can be reconstructed from these synchronized records; the interacting channels are strong enough that moving any one of the actuators noticeably changes several outputs. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use the complete VTOL state and constraints, then compare the listed longitudinal/lateral/yaw LQR gains with rho and estimator q multiplied by 0.1,1,10.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "registered_nonlinear",
    "template_id": "vtol_cascaded",
    "parameters": {
      "mass_kg": 1,
      "pitch_inertia_kg_m2": 0.02,
      "gravity_m_s2": 9.81,
      "linear_drag_n_s_m": 0.25,
      "pitch_damping_n_m_s": 0.02,
      "thrust_min_n": 0,
      "thrust_max_n": 20,
      "torque_limit_n_m": 1
    },
    "initial_state": {
      "x_m": 0,
      "z_m": 0,
      "pitch_rad": 0,
      "x_velocity_m_s": 0,
      "z_velocity_m_s": 0,
      "pitch_rate_rad_s": 0
    },
    "input_signal_ids": [
      "LQR mixed rotor commands channel 1",
      "LQR mixed rotor commands channel 2"
    ],
    "output_signal_ids": [
      "measured and estimated quadrotor axis states channel 1",
      "measured and estimated quadrotor axis states channel 2",
      "measured and estimated quadrotor axis states channel 3",
      "measured and estimated quadrotor axis states channel 4",
      "measured and estimated quadrotor axis states channel 5",
      "measured and estimated quadrotor axis states channel 6"
    ],
    "signal_units": {
      "x_m": "m",
      "z_m": "m",
      "pitch_rad": "rad",
      "x_velocity_m_s": "m/s",
      "z_velocity_m_s": "m/s",
      "pitch_rate_rad_s": "rad/s"
    }
  },
  "experiment": {
    "sample_time_s": 0.001,
    "duration_s": 20,
    "initial_output": 0,
    "input_amplitudes": [
      -0.5,
      -0.25,
      0.25,
      0.5
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return LQR mixed rotor commands to baseline and verify that measured and estimated quadrotor axis states remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective measured and estimated quadrotor axis states direction with its final direction.",
    "delay": "Measure from the logged LQR mixed rotor commands edge to the first effective measured and estimated quadrotor axis states sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log LQR mixed rotor commands and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 195. Identify nonlinear radiation/conduction dynamics and a three-state small-signal model for an RTP chamber

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is common command to three lamps, and the measured outputs are plate center and support temperatures, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in plate center starts in its final direction rather than moving the opposite way first; after the input changes, the plate center response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the plate center response settles or remains bounded instead of developing self-growing motion. As the size or operating point of common command to three lamps changes, radiation, lamp effectiveness, and available cooling change with temperature, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the plate center and support temperatures measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use the three-state RTP common-input transfer 0.5226(s+0.0876)(s+0.1438)/[(s+0.1482)(s+0.0863)(s+0.0527)] and test three lamp levels.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.5226,
      0.12092964,
      0.006583129488
    ],
    "denominator": [
      1,
      0.2872,
      0.02514781,
      0.000674015082
    ],
    "input_delay_s": 0,
    "input_signal_id": "common command to three lamps",
    "output_signal_id": "plate center and support temperatures",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return common command to three lamps to baseline and verify that plate center and support temperatures remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective plate center and support temperatures direction with its final direction.",
    "delay": "Measure from the logged common command to three lamps edge to the first effective plate center and support temperatures sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log common command to three lamps and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "radiation terms proportional to absolute temperature^4"
  }
}
```

---

## 196. Apply PI temperature-trajectory control while respecting the absence of active cooling

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is nonnegative lamp power, and the measured outputs are temperature trajectory and tracking error, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in temperature trajectory starts in its final direction rather than moving the opposite way first; after the input changes, the temperature trajectory response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the temperature trajectory response settles or remains bounded instead of developing self-growing motion. As the size or operating point of nonnegative lamp power changes, geometry, actuator authority, or plant gain changes with the current state, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the temperature trajectory and tracking error measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use the RTP plant and PI D=(s+0.0527)/s with nonnegative lamp power; track heating ramps and physically passive cooling ramps separately.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.5226,
      0.12092964,
      0.006583129488
    ],
    "denominator": [
      1,
      0.7571,
      0.1337193,
      0.006583129488
    ],
    "input_delay_s": 0,
    "input_signal_id": "nonnegative lamp power",
    "output_signal_id": "temperature trajectory and tracking error",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.05,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return nonnegative lamp power to baseline and verify that temperature trajectory and tracking error remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective temperature trajectory and tracking error direction with its final direction.",
    "delay": "Measure from the logged nonnegative lamp power edge to the first effective temperature trajectory and tracking error sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log nonnegative lamp power and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 197. Design an error-space LQG regulator that balances tracking, actuation, and wafer-temperature uniformity

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is common lamp command, and the measured outputs are center temperature, estimated three-node temperatures, and uniformity, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in center temperature starts in its final direction rather than moving the opposite way first; after the input changes, the center temperature response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the center temperature response settles or remains bounded instead of developing self-growing motion. As the size or operating point of common lamp command changes, radiation, lamp effectiveness, and available cooling change with temperature, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the center temperature, estimated three-node temperatures, and uniformity measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use the three-state RTP model, K1=1,K0=[0.1221,2.0788,-0.2140], L=[16.1461,16.4710,13.2001], Rw=1,Rv=0.001; log node-temperature spread.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.5226,
      0.12092964,
      0.006583129488
    ],
    "denominator": [
      1,
      0.2872,
      0.02514781,
      0.000674015082
    ],
    "input_delay_s": 0,
    "input_signal_id": "common lamp command",
    "output_signal_id": "center temperature",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return common lamp command to baseline and verify that center temperature, estimated three-node temperatures, and uniformity remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective center temperature, estimated three-node temperatures, and uniformity direction with its final direction.",
    "delay": "Measure from the logged common lamp command edge to the first effective center temperature, estimated three-node temperatures, and uniformity sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log common lamp command and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 198. Verify RTP control with lamp inversion, saturation, antiwindup, and a digital prototype

### Control Problem Description

This is a thermal process made from a heating actuator, interacting thermal bodies, and temperature sensors. The control input is digitally commanded lamp voltage, and the measured outputs are wafer temperatures, lamp voltage, integrator state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in wafer temperatures starts in its final direction rather than moving the opposite way first; after the input changes, the wafer temperatures response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the wafer temperatures response settles or remains bounded instead of developing self-growing motion. As the size or operating point of digitally commanded lamp voltage changes, radiation, lamp effectiveness, and available cooling change with temperature, so the response law itself changes as the state evolves and one local gain cannot cover the full motion. Because the input and the wafer temperatures, lamp voltage, integrator state measurements share one clock, all relevant motion can be reconstructed from these synchronized records; several readings describe shared internal motion, with only limited cross-channel influence. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Use lamp P=V^1.6, inverse V=P^0.625, voltage limits 1..4 V, reference filter 0.2/(s+0.2), Ts=0.1 s, and antiwindup recovery 1 s as an explicit trial value.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0,
      0.0521145,
      -0.10303042,
      0.05092241
    ],
    "denominator": [
      1,
      -2.97144027,
      2.94312943,
      -0.9716885
    ],
    "time_domain": "discrete",
    "sample_time_s": 0.1,
    "input_delay_s": 0,
    "input_signal_id": "digitally commanded lamp voltage",
    "output_signal_id": "wafer temperatures",
    "input_units": "power_unit",
    "output_units": "degC"
  },
  "experiment": {
    "sample_time_s": 0.1,
    "duration_s": 300,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return digitally commanded lamp voltage to baseline and verify that wafer temperatures, lamp voltage, integrator state remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective wafer temperatures, lamp voltage, integrator state direction with its final direction.",
    "delay": "Measure from the logged digitally commanded lamp voltage edge to the first effective wafer temperatures, lamp voltage, integrator state sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log digitally commanded lamp voltage and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "nonlinear_law": "P=V^1.6; V=P^0.625; clip V to [1,4]",
    "antiwindup_recovery_s": 1
  }
}
```

---

## 199. Model exact adaptation in E. coli chemotaxis as integral feedback of receptor activity

### Control Problem Description

This is a bacterial chemotaxis system made from receptor activity, methylation adaptation, and cell motion. The control input is ligand concentration as the prescribed pathway input, and the measured outputs are receptor activity and methylation state, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in receptor activity starts in its final direction rather than moving the opposite way first; after the input changes, the receptor activity response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input returns to baseline, the receptor activity response settles or remains bounded instead of developing self-growing motion. Applying small positive and negative changes in ligand concentration as the prescribed pathway input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the receptor activity and methylation state measurements share one clock, all relevant motion can be reconstructed from these synchronized records; there is one main physical route from actuation to the measured motion, while any listed quantity enters only as a disturbance. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

For a numerical illustration choose K=1,Km=0.2 s^-1, CheRbar=0.5; step ligand by 1 at 20 s and run 60 s.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      -1,
      0
    ],
    "denominator": [
      1,
      0.2
    ],
    "input_delay_s": 0,
    "input_signal_id": "ligand concentration as the prescribed pathway input",
    "output_signal_id": "receptor activity and methylation state",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 60,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return ligand concentration as the prescribed pathway input to baseline and verify that receptor activity and methylation state remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective receptor activity and methylation state direction with its final direction.",
    "delay": "Measure from the logged ligand concentration as the prescribed pathway input edge to the first effective receptor activity and methylation state sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log ligand concentration as the prescribed pathway input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "integral_feedback": "a=m-l; m_dot=0.2(0.5-a)"
  }
}
```

---

## 200. Map CheY activity into the one-dimensional mean chemotaxis motion model

### Control Problem Description

This is a bacterial chemotaxis system made from receptor activity, methylation adaptation, and cell motion. The control input is ligand perturbation as the prescribed pathway input, and the measured outputs are mean cell position, receptor activity, and methylation, recorded continuously by sensors or synchronized software channels. Across several small reversible trials, the first useful change in mean cell position starts in its final direction rather than moving the opposite way first; after the input changes, the mean cell position response begins within one sample without a separate silent interval, and the path from actuation to visible response contains one or two dominant storage or integration processes. When the input is removed, the mean cell position response retains an offset or keeps drifting rather than returning through its own restoring action. Applying small positive and negative changes in ligand perturbation as the prescribed pathway input produces smooth, reversible, and nearly proportional responses, with no evident dead zone, hysteresis, or clipping inside the stated range. Because the input and the mean cell position, receptor activity, and methylation measurements share one clock, all relevant motion can be reconstructed from these synchronized records; outer motion is produced only through a separately stabilized inner loop operating on a faster time scale. When operating point, load, or actuator authority is varied safely and the trial is repeated, those changes can substantially change the response rate, final level, or safe excursion.

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

### Example Data (Natural Language)

Continue the chemotaxis illustration with Ka=1,Kx=0.5, baseline w=0; step ligand by 1 and integrate mean position.

### Example Data (JSON)

```json
{
  "specification_facts": [],
  "model": {
    "kind": "transfer_function",
    "numerator": [
      0.5
    ],
    "denominator": [
      1,
      0.2
    ],
    "input_delay_s": 0,
    "input_signal_id": "ligand perturbation as the prescribed pathway input",
    "output_signal_id": "mean cell position",
    "input_units": "input_unit",
    "output_units": "output_unit"
  },
  "experiment": {
    "sample_time_s": 0.02,
    "duration_s": 60,
    "initial_output": 0,
    "input_amplitudes": [
      -1,
      -0.5,
      0.5,
      1
    ],
    "uncertainty_multipliers": [
      0.9,
      1,
      1.1
    ]
  },
  "eight_segment_evidence": {
    "stability": "Return ligand perturbation as the prescribed pathway input to baseline and verify that mean cell position, receptor activity, and methylation remains bounded or follows the declared unstable-event stop.",
    "phase": "Apply equal small positive and negative changes and compare the first effective mean cell position, receptor activity, and methylation direction with its final direction.",
    "delay": "Measure from the logged ligand perturbation as the prescribed pathway input edge to the first effective mean cell position, receptor activity, and methylation sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log ligand perturbation as the prescribed pathway input and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  },
  "physical_parameters": {
    "mean_motion": "yCheY=a; x_dot=0.5(ybar-yCheY)"
  }
}
```

---
