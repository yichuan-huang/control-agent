# CFDC 数据集：二百个经典控制问题的六字段输入

<!-- EXAMPLE-DATA-AUDIT: chapters 1-10 complete -->

> 每个条目与 control_problems.md 的全局编号一致。安全边界和主导时间尺度都是面向软件仿真的保守归一化调度默认值。对于没有控制器的纯分析例题，“执行器”字段记录给定激励或测试输入。

每个控制问题描述都是一段不含公式的自然语言叙述，先交代装置及其控制输入和测量输出，再连贯说明小幅可逆试验中观察到的运动。Stage 0 的八类证据被自然融入正文，不使用诊断标签，也不按逐句检查表机械排列。

---

## 1. 家庭恒温器的滞环开关控制

### 控制问题描述

这是一个由恒温器监测房间温度并控制电加热器通断的住宅供暖系统。控制输入是二值加热命令，输出是由传感器或同步记录器连续获取的室温、加热器状态。在多次小幅且可逆的试验中，室温开始时就沿最终方向变化，不会先向相反方向运动；二值加热命令改变后，室温在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把二值加热命令恢复到基准值后，室温最终会收敛或保持有界，不会出现自行增长的运动。改变二值加热命令的方向和幅值时，可以观察到固定滞环和继电切换，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。二值加热命令与室温、加热器状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

室温、加热器状态

### 执行器

二值加热命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=80.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

采用室外温度 50 degF、设定值 65 degF、等效热容 20000 Btu/degF、传热系数 500 Btu/(h*degF)、炉子供热率 25000 Btu/h 和滞环半宽 0.5 degF。初温取 64.5 degF 且炉子开启，以 60 s 采样仿真 6 h。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=1 binary_command; steady_output_change=50 degF; response_time_s=144000 s; input_min=0 binary_command; input_max=1 binary_command; output_min=64.5 degF; output_max=65.5 degF;`

### 示例数据（JSON）

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
    "input_signal_id": "二值加热命令",
    "output_signal_id": "室温",
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
    "stability": "Return 二值加热命令 to baseline and verify that 室温、加热器状态 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 室温、加热器状态 direction with its final direction.",
    "delay": "Measure the time from the logged 二值加热命令 edge to the first effective 室温、加热器状态 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 二值加热命令 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 2. 汽车巡航的开环与闭环比较

### 控制问题描述

这是一个在道路上行驶、由发动机牵引力克服空气与滚动阻力的汽车纵向运动系统。控制输入是油门角度，输出是由传感器或同步记录器连续获取的车速。在多次小幅且可逆的试验中，车速开始时就沿最终方向变化，不会先向相反方向运动；油门角度改变后，车速在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把油门角度恢复到基准值后，车速最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的油门角度变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。油门角度与车速采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，车速的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

车速

### 执行器

油门角度

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=100.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在 65 mph 附近令油门角变化 1 deg，并采用每度油门对应 10 mph 稳态车速变化；把 1% 上坡作为 -5 mph 扰动，为动态仿真补入 5 s 响应时间，并比较开环与比例增益 10 的反馈。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=1 deg; steady_output_change=10 mph; response_time_s=5 s; input_min=-3 deg; input_max=3 deg; output_min=45 mph; output_max=80 mph;`

### 示例数据（JSON）

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
    "input_signal_id": "油门角度",
    "output_signal_id": "车速",
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
    "stability": "Return 油门角度 to baseline and verify that 车速 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 车速 direction with its final direction.",
    "delay": "Measure the time from the logged 油门角度 edge to the first effective 车速 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 油门角度 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 3. 手动汽车转向反馈

### 控制问题描述

这是一个由驾驶员通过方向盘修正航向和车道位置的汽车横向运动系统。控制输入是方向盘转角，输出是由传感器或同步记录器连续获取的航向角、车道误差。在多次小幅且可逆的试验中，航向角开始时就沿最终方向变化，不会先向相反方向运动；方向盘转角改变后，航向角在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把方向盘转角恢复到基准值后，航向角最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的方向盘转角变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。方向盘转角与航向角、车道误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

航向角、车道误差

### 执行器

方向盘转角

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 方向盘转角 变化 5 deg，预期 航向角、车道误差 最终变化 8 deg，63% 响应时间取 1.5 s。输入范围取 -30 至 30 deg，输出范围取 -180 至 180 deg；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=5 deg; steady_output_change=8 deg; response_time_s=1.5 s; input_min=-30 deg; input_max=30 deg; output_min=-180 deg; output_max=180 deg;`

### 示例数据（JSON）

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
    "input_signal_id": "方向盘转角",
    "output_signal_id": "航向角",
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
    "stability": "Return 方向盘转角 to baseline and verify that 航向角、车道误差 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 航向角、车道误差 direction with its final direction.",
    "delay": "Measure the time from the logged 方向盘转角 edge to the first effective 航向角、车道误差 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 方向盘转角 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 4. 德雷贝尔孵化器温度调节

### 控制问题描述

这是一个由水套、炉火和机械温度调节机构组成的孵化器。控制输入是空气或燃料阀位置，输出是由传感器或同步记录器连续获取的孵化器温度。在多次小幅且可逆的试验中，孵化器温度开始时就沿最终方向变化，不会先向相反方向运动；空气或燃料阀位置改变后，孵化器温度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把空气或燃料阀位置恢复到基准值后，孵化器温度最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的空气或燃料阀位置变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。空气或燃料阀位置与孵化器温度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

孵化器温度

### 执行器

空气或燃料阀位置

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

在安全仿真中令 空气或燃料阀位置 变化 10 %，预期 孵化器温度 最终变化 2 degC，63% 响应时间取 120 s。输入范围取 0 至 100 %，输出范围取 30 至 42 degC；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=10 %; steady_output_change=2 degC; response_time_s=120 s; input_min=0 %; input_max=100 %; output_min=30 degC; output_max=42 degC;`

### 示例数据（JSON）

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
    "input_signal_id": "空气或燃料阀位置",
    "output_signal_id": "孵化器温度",
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
    "stability": "Return 空气或燃料阀位置 to baseline and verify that 孵化器温度 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 孵化器温度 direction with its final direction.",
    "delay": "Measure the time from the logged 空气或燃料阀位置 edge to the first effective 孵化器温度 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 空气或燃料阀位置 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 5. 浮球阀液位调节

### 控制问题描述

这是一个利用浮球随液面升降并机械改变进水阀开度的储水箱。控制输入是入口阀开度，输出是由传感器或同步记录器连续获取的水箱液位。在多次小幅且可逆的试验中，水箱液位开始时就沿最终方向变化，不会先向相反方向运动；入口阀开度改变后，水箱液位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把入口阀开度恢复到基准值后，水箱液位最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的入口阀开度变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。入口阀开度与水箱液位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

水箱液位

### 执行器

入口阀开度

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 入口阀开度 变化 10 %，预期 水箱液位 最终变化 0.08 m，63% 响应时间取 20 s。输入范围取 0 至 100 %，输出范围取 0.2 至 1.2 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=10 %; steady_output_change=0.08 m; response_time_s=20 s; input_min=0 %; input_max=100 %; output_min=0.2 m; output_max=1.2 m;`

### 示例数据（JSON）

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
    "input_signal_id": "入口阀开度",
    "output_signal_id": "水箱液位",
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
    "stability": "Return 入口阀开度 to baseline and verify that 水箱液位 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 水箱液位 direction with its final direction.",
    "delay": "Measure the time from the logged 入口阀开度 edge to the first effective 水箱液位 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 入口阀开度 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 6. 瓦特飞球调速器

### 控制问题描述

这是一个由飞球、连杆和蒸汽阀共同调节发动机转速的机械调速装置。控制输入是蒸汽阀开度，输出是由传感器或同步记录器连续获取的发动机转速、调速器位移。在多次小幅且可逆的试验中，发动机转速开始时就沿最终方向变化，不会先向相反方向运动；蒸汽阀开度改变后，发动机转速在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把蒸汽阀开度恢复到基准值后，发动机转速最终会收敛或保持有界，不会出现自行增长的运动。改变蒸汽阀开度的方向和幅值时，可以观察到固定的静态非线性，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。蒸汽阀开度与发动机转速、调速器位移采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

发动机转速、调速器位移

### 执行器

蒸汽阀开度

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=80.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 蒸汽阀开度 变化 10 %，预期 发动机转速、调速器位移 最终变化 20 rpm，63% 响应时间取 8 s。输入范围取 0 至 100 %，输出范围取 400 至 900 rpm；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=10 %; steady_output_change=20 rpm; response_time_s=8 s; input_min=0 %; input_max=100 %; output_min=400 rpm; output_max=900 rpm;`

### 示例数据（JSON）

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
    "input_signal_id": "蒸汽阀开度",
    "output_signal_id": "发动机转速",
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
    "stability": "Return 蒸汽阀开度 to baseline and verify that 发动机转速、调速器位移 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 发动机转速、调速器位移 direction with its final direction.",
    "delay": "Measure the time from the logged 蒸汽阀开度 edge to the first effective 发动机转速、调速器位移 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 蒸汽阀开度 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 7. 造纸机浆料浓度控制

### 控制问题描述

这是一个通过调节稀释水来稳定纸浆浓度的造纸机湿端过程。控制输入是稀释水阀，输出是由传感器或同步记录器连续获取的浆料浓度。在多次小幅且可逆的试验中，浆料浓度开始时就沿最终方向变化，不会先向相反方向运动；稀释水阀改变后，浆料浓度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把稀释水阀恢复到基准值后，浆料浓度最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的稀释水阀变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。稀释水阀与浆料浓度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

浆料浓度

### 执行器

稀释水阀

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 稀释水阀 变化 5 %，预期 浆料浓度 最终变化 -0.4 %，63% 响应时间取 30 s。输入范围取 0 至 100 %，输出范围取 2 至 6 %；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=5 %; steady_output_change=-0.4 %; response_time_s=30 s; input_min=0 %; input_max=100 %; output_min=2 %; output_max=6 %;`

### 示例数据（JSON）

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
    "input_signal_id": "稀释水阀",
    "output_signal_id": "浆料浓度",
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
    "stability": "Return 稀释水阀 to baseline and verify that 浆料浓度 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 浆料浓度 direction with its final direction.",
    "delay": "Measure the time from the logged 稀释水阀 edge to the first effective 浆料浓度 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 稀释水阀 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 8. 造纸机纸页含水率控制

### 控制问题描述

这是一个通过干燥滚筒蒸汽调节成品纸含水率的造纸机干燥过程。控制输入是干燥蒸汽命令，输出是由传感器或同步记录器连续获取的纸页含水率。在多次小幅且可逆的试验中，纸页含水率开始时就沿最终方向变化，不会先向相反方向运动；干燥蒸汽命令改变后，纸页含水率在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把干燥蒸汽命令恢复到基准值后，纸页含水率最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的干燥蒸汽命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。干燥蒸汽命令与纸页含水率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

纸页含水率

### 执行器

干燥蒸汽命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 干燥蒸汽命令 变化 10 %，预期 纸页含水率 最终变化 -1.2 %，63% 响应时间取 60 s，并采用 8 s 纯等待时间。输入范围取 0 至 100 %，输出范围取 2 至 12 %；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=10 %; steady_output_change=-1.2 %; response_time_s=60 s; dead_time_s=8 s; input_min=0 %; input_max=100 %; output_min=2 %; output_max=12 %;`

### 示例数据（JSON）

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
    "input_signal_id": "干燥蒸汽命令",
    "output_signal_id": "纸页含水率",
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
    "stability": "Return 干燥蒸汽命令 to baseline and verify that 纸页含水率 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 纸页含水率 direction with its final direction.",
    "delay": "Measure the time from the logged 干燥蒸汽命令 edge to the first effective 纸页含水率 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 干燥蒸汽命令 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 9. 人体血压负反馈

### 控制问题描述

这是一个由心脏、血管和自主神经反射共同维持动脉压力的生理循环系统。控制输入是心脏与血管神经命令，输出是由传感器或同步记录器连续获取的动脉血压、心率。在多次小幅且可逆的试验中，动脉血压开始时就沿最终方向变化，不会先向相反方向运动；心脏与血管神经命令改变后，动脉血压在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把心脏与血管神经命令恢复到基准值后，动脉血压最终会收敛或保持有界，不会出现自行增长的运动。当心脏与血管神经命令的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。心脏与血管神经命令与动脉血压、心率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

动脉血压、心率

### 执行器

心脏与血管神经命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

在安全仿真中令 心脏与血管神经命令 变化 0.1 neural_command，预期 动脉血压、心率 最终变化 8 mmHg，63% 响应时间取 6 s。输入范围取 -0.5 至 0.5 neural_command，输出范围取 60 至 140 mmHg；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=0.1 neural_command; steady_output_change=8 mmHg; response_time_s=6 s; input_min=-0.5 neural_command; input_max=0.5 neural_command; output_min=60 mmHg; output_max=140 mmHg;`

### 示例数据（JSON）

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
    "input_signal_id": "心脏与血管神经命令",
    "output_signal_id": "动脉血压",
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
    "stability": "Return 心脏与血管神经命令 to baseline and verify that 动脉血压、心率 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 动脉血压、心率 direction with its final direction.",
    "delay": "Measure the time from the logged 心脏与血管神经命令 edge to the first effective 动脉血压、心率 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 心脏与血管神经命令 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 10. 人体血糖调节

### 控制问题描述

这是一个由胰岛素和反调节激素共同维持血糖水平的代谢调节系统。控制输入是内源胰岛素与反调节作用，输出是由传感器或同步记录器连续获取的血糖、胰岛素水平。在多次小幅且可逆的试验中，血糖开始时就沿最终方向变化，不会先向相反方向运动；内源胰岛素与反调节作用改变后，血糖在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把内源胰岛素与反调节作用恢复到基准值后，血糖最终会收敛或保持有界，不会出现自行增长的运动。当内源胰岛素与反调节作用的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。内源胰岛素与反调节作用与血糖、胰岛素水平采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

血糖、胰岛素水平

### 执行器

内源胰岛素与反调节作用

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

在安全仿真中令 内源胰岛素与反调节作用 变化 0.1 insulin_command，预期 血糖、胰岛素水平 最终变化 -12 mg/dL，63% 响应时间取 20 s。输入范围取 -0.5 至 0.5 insulin_command，输出范围取 60 至 180 mg/dL；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=0.1 insulin_command; steady_output_change=-12 mg/dL; response_time_s=20 s; input_min=-0.5 insulin_command; input_max=0.5 insulin_command; output_min=60 mg/dL; output_max=180 mg/dL;`

### 示例数据（JSON）

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
    "input_signal_id": "内源胰岛素与反调节作用",
    "output_signal_id": "血糖",
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
    "stability": "Return 内源胰岛素与反调节作用 to baseline and verify that 血糖、胰岛素水平 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 血糖、胰岛素水平 direction with its final direction.",
    "delay": "Measure the time from the logged 内源胰岛素与反调节作用 edge to the first effective 血糖、胰岛素水平 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 内源胰岛素与反调节作用 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 11. 人体心率调节

### 控制问题描述

这是一个由交感与副交感神经共同调节窦房结节律的心率系统。控制输入是交感与副交感驱动，输出是由传感器或同步记录器连续获取的心率。在多次小幅且可逆的试验中，心率开始时就沿最终方向变化，不会先向相反方向运动；交感与副交感驱动改变后，心率在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把交感与副交感驱动恢复到基准值后，心率最终会收敛或保持有界，不会出现自行增长的运动。当交感与副交感驱动的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。交感与副交感驱动与心率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

心率

### 执行器

交感与副交感驱动

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

在安全仿真中令 交感与副交感驱动 变化 0.1 autonomic_command，预期 心率 最终变化 8 bpm，63% 响应时间取 5 s。输入范围取 -0.5 至 0.5 autonomic_command，输出范围取 45 至 160 bpm；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=0.1 autonomic_command; steady_output_change=8 bpm; response_time_s=5 s; input_min=-0.5 autonomic_command; input_max=0.5 autonomic_command; output_min=45 bpm; output_max=160 bpm;`

### 示例数据（JSON）

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
    "input_signal_id": "交感与副交感驱动",
    "output_signal_id": "心率",
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
    "stability": "Return 交感与副交感驱动 to baseline and verify that 心率 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 心率 direction with its final direction.",
    "delay": "Measure the time from the logged 交感与副交感驱动 edge to the first effective 心率 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 交感与副交感驱动 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 12. 眼球注视角控制

### 控制问题描述

这是一个由眼外肌转动眼球并依靠视网膜误差完成注视的视觉运动系统。控制输入是眼肌力矩，输出是由传感器或同步记录器连续获取的眼球角度、视网膜误差。在多次小幅且可逆的试验中，眼球角度开始时就沿最终方向变化，不会先向相反方向运动；眼肌力矩改变后，眼球角度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把眼肌力矩恢复到基准值后，眼球角度最终会收敛或保持有界，不会出现自行增长的运动。当眼肌力矩的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。眼肌力矩与眼球角度、视网膜误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

眼球角度、视网膜误差

### 执行器

眼肌力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

在安全仿真中令 眼肌力矩 变化 0.002 Nm，预期 眼球角度、视网膜误差 最终变化 0.12 rad，63% 响应时间取 0.18 s。输入范围取 -0.01 至 0.01 Nm，输出范围取 -0.5 至 0.5 rad；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=0.002 Nm; steady_output_change=0.12 rad; response_time_s=0.18 s; input_min=-0.01 Nm; input_max=0.01 Nm; output_min=-0.5 rad; output_max=0.5 rad;`

### 示例数据（JSON）

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
    "input_signal_id": "眼肌力矩",
    "output_signal_id": "眼球角度",
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
    "stability": "Return 眼肌力矩 to baseline and verify that 眼球角度、视网膜误差 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 眼球角度、视网膜误差 direction with its final direction.",
    "delay": "Measure the time from the logged 眼肌力矩 edge to the first effective 眼球角度、视网膜误差 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 眼肌力矩 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 13. 瞳孔对光调节

### 控制问题描述

这是一个由虹膜肌改变瞳孔直径以调节入眼光量的视觉反射系统。控制输入是虹膜肌激活，输出是由传感器或同步记录器连续获取的瞳孔直径、视网膜照度。在多次小幅且可逆的试验中，瞳孔直径开始时就沿最终方向变化，不会先向相反方向运动；虹膜肌激活改变后，瞳孔直径在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把虹膜肌激活恢复到基准值后，瞳孔直径最终会收敛或保持有界，不会出现自行增长的运动。当虹膜肌激活的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。虹膜肌激活与瞳孔直径、视网膜照度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

瞳孔直径、视网膜照度

### 执行器

虹膜肌激活

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

在安全仿真中令 虹膜肌激活 变化 0.1 iris_command，预期 瞳孔直径、视网膜照度 最终变化 -0.8 mm，63% 响应时间取 0.8 s。输入范围取 -1 至 1 iris_command，输出范围取 2 至 8 mm；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=0.1 iris_command; steady_output_change=-0.8 mm; response_time_s=0.8 s; input_min=-1 iris_command; input_max=1 iris_command; output_min=2 mm; output_max=8 mm;`

### 示例数据（JSON）

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
    "input_signal_id": "虹膜肌激活",
    "output_signal_id": "瞳孔直径",
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
    "stability": "Return 虹膜肌激活 to baseline and verify that 瞳孔直径、视网膜照度 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 瞳孔直径、视网膜照度 direction with its final direction.",
    "delay": "Measure the time from the logged 虹膜肌激活 edge to the first effective 瞳孔直径、视网膜照度 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 虹膜肌激活 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 14. 电梯粗细测量与钢缆伸长

### 控制问题描述

这是一个由曳引电机、制动器、轿厢和弹性钢缆组成的电梯定位装置。控制输入是曳引电机力矩与制动器，输出是由传感器或同步记录器连续获取的轿厢位置、平层误差、钢缆伸长。在多次小幅且可逆的试验中，轿厢位置开始时就沿最终方向变化，不会先向相反方向运动；曳引电机力矩与制动器改变后，轿厢位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把曳引电机力矩与制动器恢复到基准值后，轿厢位置最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的曳引电机力矩与制动器变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。曳引电机力矩与制动器与轿厢位置、平层误差、钢缆伸长采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

轿厢位置、平层误差、钢缆伸长

### 执行器

曳引电机力矩与制动器

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 曳引电机力矩与制动器 变化 100 Nm，预期 轿厢位置、平层误差、钢缆伸长 最终变化 0.15 m，63% 响应时间取 2.5 s。输入范围取 -1500 至 1500 Nm，输出范围取 0 至 120 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=100 Nm; steady_output_change=0.15 m; response_time_s=2.5 s; input_min=-1500 Nm; input_max=1500 Nm; output_min=0 m; output_max=120 m;`

### 示例数据（JSON）

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
    "input_signal_id": "曳引电机力矩与制动器",
    "output_signal_id": "轿厢位置",
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
    "stability": "Return 曳引电机力矩与制动器 to baseline and verify that 轿厢位置、平层误差、钢缆伸长 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 轿厢位置、平层误差、钢缆伸长 direction with its final direction.",
    "delay": "Measure the time from the logged 曳引电机力矩与制动器 edge to the first effective 轿厢位置、平层误差、钢缆伸长 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 曳引电机力矩与制动器 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 15. 温度的电测量与电加热

### 控制问题描述

这是一个由电加热器、受热体和电温度传感器组成的温控装置。控制输入是电加热器电压，输出是由传感器或同步记录器连续获取的温度、传感器电压。在多次小幅且可逆的试验中，温度开始时就沿最终方向变化，不会先向相反方向运动；电加热器电压改变后，温度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把电加热器电压恢复到基准值后，温度最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的电加热器电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电加热器电压与温度、传感器电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

温度、传感器电压

### 执行器

电加热器电压

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

在安全仿真中令 电加热器电压 变化 5 V，预期 温度、传感器电压 最终变化 8 degC，63% 响应时间取 80 s。输入范围取 0 至 48 V，输出范围取 15 至 90 degC；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=5 V; steady_output_change=8 degC; response_time_s=80 s; input_min=0 V; input_max=48 V; output_min=15 degC; output_max=90 degC;`

### 示例数据（JSON）

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
    "input_signal_id": "电加热器电压",
    "output_signal_id": "温度",
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
    "stability": "Return 电加热器电压 to baseline and verify that 温度、传感器电压 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 温度、传感器电压 direction with its final direction.",
    "delay": "Measure the time from the logged 电加热器电压 edge to the first effective 温度、传感器电压 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 电加热器电压 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 16. 压力的电测量与阀控

### 控制问题描述

这是一个由调节阀、受压容腔和压力变送器组成的压力控制装置。控制输入是阀门命令，输出是由传感器或同步记录器连续获取的压力、传感器电压。在多次小幅且可逆的试验中，压力开始时就沿最终方向变化，不会先向相反方向运动；阀门命令改变后，压力在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把阀门命令恢复到基准值后，压力最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的阀门命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。阀门命令与压力、传感器电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

压力、传感器电压

### 执行器

阀门命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 阀门命令 变化 10 %，预期 压力、传感器电压 最终变化 30 kPa，63% 响应时间取 12 s。输入范围取 0 至 100 %，输出范围取 0 至 500 kPa；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=10 %; steady_output_change=30 kPa; response_time_s=12 s; input_min=0 %; input_max=100 %; output_min=0 kPa; output_max=500 kPa;`

### 示例数据（JSON）

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
    "input_signal_id": "阀门命令",
    "output_signal_id": "压力",
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
    "stability": "Return 阀门命令 to baseline and verify that 压力、传感器电压 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 压力、传感器电压 direction with its final direction.",
    "delay": "Measure the time from the logged 阀门命令 edge to the first effective 压力、传感器电压 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 阀门命令 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 17. 液位的电测量与泵阀控制

### 控制问题描述

这是一个由储液罐、泵阀和液位变送器组成的液位控制装置。控制输入是泵速或阀位，输出是由传感器或同步记录器连续获取的液位、变送器信号。在多次小幅且可逆的试验中，液位开始时就沿最终方向变化，不会先向相反方向运动；泵速或阀位改变后，液位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把泵速或阀位恢复到基准值后，液位最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的泵速或阀位变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。泵速或阀位与液位、变送器信号采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

液位、变送器信号

### 执行器

泵速或阀位

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 泵速或阀位 变化 10 %，预期 液位、变送器信号 最终变化 0.1 m，63% 响应时间取 25 s。输入范围取 0 至 100 %，输出范围取 0.1 至 1.5 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=10 %; steady_output_change=0.1 m; response_time_s=25 s; input_min=0 %; input_max=100 %; output_min=0.1 m; output_max=1.5 m;`

### 示例数据（JSON）

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
    "input_signal_id": "泵速或阀位",
    "output_signal_id": "液位",
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
    "stability": "Return 泵速或阀位 to baseline and verify that 液位、变送器信号 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 液位、变送器信号 direction with its final direction.",
    "delay": "Measure the time from the logged 泵速或阀位 edge to the first effective 液位、变送器信号 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 泵速或阀位 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 18. 管道流量的电测量与阀控

### 控制问题描述

这是一个由管道、调节阀和流量传感器组成的流量控制装置。控制输入是调节阀开度，输出是由传感器或同步记录器连续获取的管道流量。在多次小幅且可逆的试验中，管道流量开始时就沿最终方向变化，不会先向相反方向运动；调节阀开度改变后，管道流量在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把调节阀开度恢复到基准值后，管道流量最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的调节阀开度变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。调节阀开度与管道流量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

管道流量

### 执行器

调节阀开度

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=120.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

在安全仿真中令 调节阀开度 变化 10 %，预期 管道流量 最终变化 0.02 m^3/s，63% 响应时间取 4 s。输入范围取 0 至 100 %，输出范围取 0 至 0.2 m^3/s；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=10 %; steady_output_change=0.02 m^3/s; response_time_s=4 s; input_min=0 %; input_max=100 %; output_min=0 m^3/s; output_max=0.2 m^3/s;`

### 示例数据（JSON）

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
    "input_signal_id": "调节阀开度",
    "output_signal_id": "管道流量",
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
    "stability": "Return 调节阀开度 to baseline and verify that 管道流量 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 管道流量 direction with its final direction.",
    "delay": "Measure the time from the logged 调节阀开度 edge to the first effective 管道流量 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 调节阀开度 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 19. HPA 应激激素负反馈

### 控制问题描述

这是一个由下丘脑、垂体和肾上腺之间的激素反馈构成的应激调节系统。控制输入是内源分泌速率，输出是由传感器或同步记录器连续获取的激素浓度。在多次小幅且可逆的试验中，激素浓度开始时就沿最终方向变化，不会先向相反方向运动；内源分泌速率改变后，激素浓度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把内源分泌速率恢复到基准值后，激素浓度最终会收敛或保持有界，不会出现自行增长的运动。当内源分泌速率的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。内源分泌速率与激素浓度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

激素浓度

### 执行器

内源分泌速率

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

在安全仿真中令 内源分泌速率 变化 1 ng/(mL*min)，预期 激素浓度 最终变化 0.8 ng/mL，63% 响应时间取 600 s。输入范围取 0 至 5 ng/(mL*min)，输出范围取 0 至 20 ng/mL；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=1 ng/(mL*min); steady_output_change=0.8 ng/mL; response_time_s=600 s; input_min=0 ng/(mL*min); input_max=5 ng/(mL*min); output_min=0 ng/mL; output_max=20 ng/mL;`

### 示例数据（JSON）

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
    "input_signal_id": "内源分泌速率",
    "output_signal_id": "激素浓度",
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
    "stability": "Return 内源分泌速率 to baseline and verify that 激素浓度 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 激素浓度 direction with its final direction.",
    "delay": "Measure the time from the logged 内源分泌速率 edge to the first effective 激素浓度 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 内源分泌速率 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 20. 分娩催产素正反馈

### 控制问题描述

这是一个由宫缩刺激催产素释放、催产素又增强宫缩的分娩正反馈系统。控制输入是内源催产素释放，输出是由传感器或同步记录器连续获取的催产素水平、宫缩强度。在多次小幅且可逆的试验中，催产素水平开始时就沿最终方向变化，不会先向相反方向运动；内源催产素释放改变后，催产素水平在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把内源催产素释放撤回基准值，催产素水平的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。当内源催产素释放的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。内源催产素释放与催产素水平、宫缩强度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

催产素水平、宫缩强度

### 执行器

内源催产素释放

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=60.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

10.0

### 示例数据（自然语言）

采用二状态正反馈仿真：催产素时间常数 30 s、宫缩时间常数 20 s，出生事件前环路乘积为 1.2，并在 180 s 时把压力反馈增益切换为零。

为便于未启用 LLM 时一次解析，可在同一次提交末尾附上：`input_change=1 release_unit/min; steady_output_change=1 contraction_unit; response_time_s=30 s; input_min=0 release_unit/min; input_max=5 release_unit/min; output_min=0 contraction_unit; output_max=10 contraction_unit;`

### 示例数据（JSON）

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
    "input_signal_id": "内源催产素释放",
    "output_signal_id": "催产素水平",
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
    "stability": "Return 内源催产素释放 to baseline and verify that 催产素水平、宫缩强度 remains bounded or converges.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 催产素水平、宫缩强度 direction with its final direction.",
    "delay": "Measure the time from the logged 内源催产素释放 edge to the first effective 催产素水平、宫缩强度 change.",
    "order": "Fit the declared numerical model and compare its early and late response residuals.",
    "sensing_and_actuation": "Log 内源催产素释放 and every declared output on the same clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the declared small-change amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant model parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 21. 汽车巡航一阶动力学

### 控制问题描述

这是一个把车辆质量、推进力和速度阻力集中起来描述的汽车纵向动力装置。控制输入是纵向驱动力，输出是由传感器或同步记录器连续获取的车速。在多次小幅且可逆的试验中，车速开始时就沿最终方向变化，不会先向相反方向运动；纵向驱动力改变后，车速在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把纵向驱动力恢复到基准值后，车速最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的纵向驱动力变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。纵向驱动力与车速采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，车速的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

车速

### 执行器

纵向驱动力

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用车辆质量 1000 kg、黏性阻力 50 N*s/m 和 500 N 力阶跃；力到车速的直流增益为 0.02 (m/s)/N，时间常数为 20 s，预测最终车速变化 10 m/s。

未启用 LLM 时可在同一次提交末尾附上：`input_change=500 N; steady_output_change=10 m/s; response_time_s=20 s; input_min=-2000 N; input_max=4000 N; output_min=0 m/s; output_max=50 m/s;`

### 示例数据（JSON）

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
    "input_signal_id": "纵向驱动力",
    "output_signal_id": "车速",
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
    "stability": "Return 纵向驱动力 to baseline and verify that 车速 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 车速 direction with its final direction.",
    "delay": "Measure from the logged 纵向驱动力 edge to the first effective 车速 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 纵向驱动力 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 22. 四分之一车双质量悬架

### 控制问题描述

这是一个用车身与车轮两个质量块、悬架弹簧和减振器表示单个车轮处垂向运动的四分之一车装置。控制输入是给定路面位移测试输入，输出是由传感器或同步记录器连续获取的车身位移、车轮位移与悬架行程。在多次小幅且可逆的试验中，车身位移开始时就沿最终方向变化，不会先向相反方向运动；给定路面位移测试输入改变后，车身位移在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定路面位移测试输入恢复到基准值后，车身位移最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定路面位移测试输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定路面位移测试输入与车身位移、车轮位移与悬架行程采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，车身位移的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

车身位移、车轮位移与悬架行程

### 执行器

给定路面位移测试输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用簧载质量 375 kg、车轮质量 20 kg、悬架刚度 130000 N/m、轮胎刚度 1000000 N/m 和阻尼 9800 N*s/m；施加 0.01、0.025、0.05 m 有界路面阶跃，以 1 ms 同步记录车身、车轮与悬架行程。

### 示例数据（JSON）

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
    "input_signal_id": "给定路面位移测试输入",
    "output_signal_id": "车身位移",
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
    "stability": "Return 给定路面位移测试输入 to baseline and verify that 车身位移、车轮位移与悬架行程 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 车身位移、车轮位移与悬架行程 direction with its final direction.",
    "delay": "Measure from the logged 给定路面位移测试输入 edge to the first effective 车身位移、车轮位移与悬架行程 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 给定路面位移测试输入 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 23. 刚性卫星单轴姿态

### 控制问题描述

这是一个由刚性航天器本体和单轴姿态执行机构组成的姿态运动系统。控制输入是推力器力或机体力矩，输出是由传感器或同步记录器连续获取的姿态角、角速度。在多次小幅且可逆的试验中，姿态角开始时就沿最终方向变化，不会先向相反方向运动；推力器力或机体力矩改变后，姿态角在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把推力器力或机体力矩撤回基准值后，姿态角会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的推力器力或机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。推力器力或机体力矩与姿态角、角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

姿态角、角速度

### 执行器

推力器力或机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

采用单轴转动惯量 1200 kg*m^2；12 Nm 力矩变化产生 0.01 rad/s^2 角加速度，力矩限制为 +/-50 Nm，姿态限制为 +/-0.2 rad。

未启用 LLM 时可在同一次提交末尾附上：`input_change=12 Nm; acceleration_change=0.01 rad/s^2; motion_time_scale_s=20 s; input_min=-50 Nm; input_max=50 Nm; output_min=-0.2 undefined; output_max=0.2 undefined;`

### 示例数据（JSON）

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
    "input_signal_id": "推力器力或机体力矩",
    "output_signal_id": "姿态角",
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
    "stability": "Return 推力器力或机体力矩 to baseline and verify that 姿态角、角速度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 姿态角、角速度 direction with its final direction.",
    "delay": "Measure from the logged 推力器力或机体力矩 edge to the first effective 姿态角、角速度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 推力器力或机体力矩 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 24. 柔性卫星共址与非共址模型

### 控制问题描述

这是一个由两个刚体和柔性连接件组成、可在不同位置施力与测角的卫星结构。控制输入是主惯量上的机体力矩，输出是由传感器或同步记录器连续获取的两刚体角度与角速度。在多次小幅且可逆的试验中，两刚体角度与角速度开始时就沿最终方向变化，不会先向相反方向运动；主惯量上的机体力矩改变后，两刚体角度与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把主惯量上的机体力矩撤回基准值后，两刚体角度与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的主惯量上的机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。主惯量上的机体力矩与两刚体角度与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

两刚体角度与角速度

### 执行器

主惯量上的机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

采用主刚体惯量 800 kg*m^2、远端惯量 200 kg*m^2、扭转刚度 80 Nm/rad、扭转阻尼 2 Nm*s/rad；施加 +/-5 与 +/-10 Nm 力矩脉冲，以 0.01 s 记录两端角度和角速度。

### 示例数据（JSON）

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
      "主惯量上的机体力矩"
    ],
    "output_signal_ids": [
      "两刚体角度与角速度通道 1",
      "两刚体角度与角速度通道 2"
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
    "stability": "Return 主惯量上的机体力矩 to baseline and verify that 两刚体角度与角速度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 两刚体角度与角速度 direction with its final direction.",
    "delay": "Measure from the logged 主惯量上的机体力矩 edge to the first effective 两刚体角度与角速度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 主惯量上的机体力矩 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 25. 四旋翼滚转俯仰偏航控制分配

### 控制问题描述

这是一个通过四个旋翼的推力差产生滚转、俯仰和偏航力矩的四旋翼飞行器。控制输入是四个旋翼推力增量，输出是由传感器或同步记录器连续获取的滚转、俯仰与偏航响应。在多次小幅且可逆的试验中，滚转开始时就沿最终方向变化，不会先向相反方向运动；四个旋翼推力增量改变后，滚转在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把四个旋翼推力增量撤回基准值后，滚转会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的四个旋翼推力增量变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。四个旋翼推力增量与滚转、俯仰与偏航响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；系统具有多个相互作用的通道，改变任一执行器都会明显改变多个输出。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

滚转、俯仰、偏航响应

### 执行器

四个旋翼推力增量、旋翼 1 力矩增量、旋翼 2 力矩增量、旋翼 3 力矩增量、旋翼 4 力矩增量

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
首次辨识测试时同时改变多个执行器通道

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用滚转和俯仰惯量 0.02 kg*m^2、偏航惯量 0.05 kg*m^2；四个旋翼力矩增量均限制为 +/-0.1 Nm，并分别激励滚转、俯仰和偏航混控列。

### 示例数据（JSON）

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
      "旋翼 1 力矩增量",
      "旋翼 2 力矩增量",
      "旋翼 3 力矩增量",
      "旋翼 4 力矩增量"
    ],
    "output_signal_ids": [
      "滚转",
      "俯仰",
      "偏航响应"
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
    "stability": "Return 四个旋翼推力增量 to baseline and verify that 滚转、俯仰与偏航响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 滚转、俯仰与偏航响应 direction with its final direction.",
    "delay": "Measure from the logged 四个旋翼推力增量 edge to the first effective 滚转、俯仰与偏航响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 四个旋翼推力增量 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 26. 单摆非线性模型、小角度线性化与仿真

### 控制问题描述

这是一个质量块通过刚性摆杆连接在固定转轴上的单摆装置。控制输入是枢轴力矩，输出是由传感器或同步记录器连续获取的摆角与角速度。在多次小幅且可逆的试验中，摆角与角速度开始时就沿最终方向变化，不会先向相反方向运动；枢轴力矩改变后，摆角与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把枢轴力矩恢复到基准值后，摆角与角速度最终会收敛或保持有界，不会出现自行增长的运动。当枢轴力矩的幅值或运行点改变时，摆杆几何和重力作用会随摆角改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。枢轴力矩与摆角与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

摆角与角速度

### 执行器

枢轴力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用质量 1 kg、摆长 1 m、重力加速度 9.81 m/s^2；以 0.02 s 采样仿真 10 s，对正弦非线性模型和小角线性模型比较 1 Nm 与 4 Nm 力矩阶跃。

### 示例数据（JSON）

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
    "input_signal_id": "枢轴力矩",
    "output_signal_id": "摆角与角速度",
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
    "stability": "Return 枢轴力矩 to baseline and verify that 摆角与角速度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 摆角与角速度 direction with its final direction.",
    "delay": "Measure from the logged 枢轴力矩 edge to the first effective 摆角与角速度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 枢轴力矩 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 27. 吊车摆与倒立摆耦合

### 控制问题描述

这是一个在水平轨道上移动的小车及其悬挂或倒立摆组成的耦合机械装置。控制输入是小车水平力，输出是由传感器或同步记录器连续获取的小车位置、摆角。在多次小幅且可逆的试验中，小车位置开始时会先沿不利或相反方向运动，随后才转向；小车水平力改变后，小车位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。即使把小车水平力撤回基准值，小车位置的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。当小车水平力的幅值或运行点改变时，摆杆几何和重力作用会随摆角改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。小车水平力与小车位置、摆角采用同一时钟记录，因此这些同步记录足以重建所有相关运动；独立执行器的数量少于受控坐标，部分坐标只能通过耦合运动间接改变。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

小车位置、摆角

### 执行器

小车水平力

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把欠驱动坐标当作具有直接执行器来下达命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用小车质量 1 kg、摆质量 0.2 kg、质心距离 0.5 m、转动惯量 0.006 kg*m^2、摩擦 0.1 N*s/m、推力限制 20 N、行程限制 1.5 m 和初始摆角 0.05 rad。

### 示例数据（JSON）

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
      "小车水平力"
    ],
    "output_signal_ids": [
      "小车位置",
      "摆角"
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
    "stability": "Return 小车水平力 to baseline and verify that 小车位置、摆角 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 小车位置、摆角 direction with its final direction.",
    "delay": "Measure from the logged 小车水平力 edge to the first effective 小车位置、摆角 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 小车水平力 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 28. 桥接 T 型 RC 电路

### 控制问题描述

这是一个由电阻和电容构成、具有桥接支路的无源电路网络。控制输入是输入电压，输出是由传感器或同步记录器连续获取的输出与电容电压。在多次小幅且可逆的试验中，输出与电容电压开始时就沿最终方向变化，不会先向相反方向运动；输入电压改变后，输出与电容电压在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把输入电压恢复到基准值后，输出与电容电压最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的输入电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。输入电压与输出与电容电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，输出与电容电压的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

输出与电容电压

### 执行器

输入电压

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 R1=R2=10 kohm、C1=C2=10 uF，得到 G(s)=(0.01 s^2+0.2 s+1)/(0.01 s^2+0.3 s+1)。用 +/-1 V 试验核对低频和高频的单位增益以及桥接支路的中频响应。

### 示例数据（JSON）

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
    "input_signal_id": "输入电压",
    "output_signal_id": "输出与电容电压",
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
    "stability": "Return 输入电压 to baseline and verify that 输出与电容电压 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 输出与电容电压 direction with its final direction.",
    "delay": "Measure from the logged 输入电压 edge to the first effective 输出与电容电压 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 输入电压 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 29. 电流源驱动的 RLC 电路

### 控制问题描述

这是一个由电流源驱动并含有电阻、电感和两个电容的储能电路。控制输入是源电流，输出是由传感器或同步记录器连续获取的两个电容电压与电感电流。在多次小幅且可逆的试验中，两个电容电压与电感电流开始时就沿最终方向变化，不会先向相反方向运动；源电流改变后，两个电容电压与电感电流在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把源电流恢复到基准值后，两个电容电压与电感电流最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的源电流变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。源电流与两个电容电压与电感电流采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，两个电容电压与电感电流的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电容电压 1、电容电压 2、电感电流

### 执行器

源电流

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 R1=R2=10 ohm、C1=C2=0.01 F、L=0.1 H，施加 0.1 A 有界电流阶跃，并记录全部电容电压和电感电流。

### 示例数据（JSON）

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
      "源电流"
    ],
    "output_signal_ids": [
      "电容电压 1",
      "电容电压 2",
      "电感电流"
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
    "stability": "Return 源电流 to baseline and verify that 两个电容电压与电感电流 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 两个电容电压与电感电流 direction with its final direction.",
    "delay": "Measure from the logged 源电流 edge to the first effective 两个电容电压与电感电流 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 源电流 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 30. 理想运放加权加法器

### 控制问题描述

这是一个由理想运算放大器和多条输入电阻支路组成的加权求和电路。控制输入是输入电压，输出是由传感器或同步记录器连续获取的加权输出电压。在多次小幅且可逆的试验中，加权输出电压开始时就沿最终方向变化，不会先向相反方向运动；输入电压改变后，加权输出电压在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把输入电压恢复到基准值后，加权输出电压最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的输入电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。输入电压与加权输出电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，加权输出电压的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

加权输出电压

### 执行器

输入电压、输入电压 1、输入电压 2

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 Rf=20 kohm、R1=10 kohm、R2=20 kohm，得到 vout=-2 v1-v2；各输入限制为 +/-5 V，输出限制为 +/-12 V。

### 示例数据（JSON）

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
      "输入电压 1",
      "输入电压 2"
    ],
    "output_signal_ids": [
      "加权输出电压"
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
    "stability": "Return 输入电压 to baseline and verify that 加权输出电压 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 加权输出电压 direction with its final direction.",
    "delay": "Measure from the logged 输入电压 edge to the first effective 加权输出电压 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 输入电压 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 31. 理想运放积分器

### 控制问题描述

这是一个由运算放大器、电阻和反馈电容组成的模拟积分电路。控制输入是输入电压，输出是由传感器或同步记录器连续获取的积分器输出电压。在多次小幅且可逆的试验中，积分器输出电压开始时就沿最终方向变化，不会先向相反方向运动；输入电压改变后，积分器输出电压在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把输入电压撤回基准值后，积分器输出电压会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的输入电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。输入电压与积分器输出电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，积分器输出电压的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

积分器输出电压

### 执行器

输入电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 Rin=100 kohm、C=10 uF，使 Rin*C=1 s；+1 V 输入产生 -1 V/s 输出斜率，并在输出达到 +/-10 V 前停止。

### 示例数据（JSON）

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
    "input_signal_id": "输入电压",
    "output_signal_id": "积分器输出电压",
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
    "stability": "Return 输入电压 to baseline and verify that 积分器输出电压 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 积分器输出电压 direction with its final direction.",
    "delay": "Measure from the logged 输入电压 edge to the first effective 积分器输出电压 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 输入电压 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 32. 扬声器及驱动电路机电耦合

### 控制问题描述

这是一个由音圈、电磁驱动电路和弹性锥盆组成的扬声器机电装置。控制输入是放大器电压，输出是由传感器或同步记录器连续获取的锥盆位移、线圈电流。在多次小幅且可逆的试验中，锥盆位移开始时就沿最终方向变化，不会先向相反方向运动；放大器电压改变后，锥盆位移在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把放大器电压撤回基准值后，锥盆位移会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的放大器电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。放大器电压与锥盆位移、线圈电流采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

锥盆位移、线圈电流

### 执行器

放大器电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用磁通密度 0.5 T、直径 2 cm 的 20 匝线圈，得到 Bl=0.63 N/A；再取 M=0.02 kg、b=0.2 N*s/m、L=1 mH、R=8 ohm。

### 示例数据（JSON）

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
    "input_signal_id": "放大器电压",
    "output_signal_id": "锥盆位移",
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
    "stability": "Return 放大器电压 to baseline and verify that 锥盆位移、线圈电流 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 锥盆位移、线圈电流 direction with its final direction.",
    "delay": "Measure from the logged 放大器电压 edge to the first effective 锥盆位移、线圈电流 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 放大器电压 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 33. 直流电机位置与速度模型

### 控制问题描述

这是一个由电枢电路、转子惯量和粘性负载组成的直流电机驱动装置。控制输入是电枢电压，输出是由传感器或同步记录器连续获取的电机位置、转速、电枢电流。在多次小幅且可逆的试验中，电机位置开始时就沿最终方向变化，不会先向相反方向运动；电枢电压改变后，电机位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把电枢电压撤回基准值后，电机位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电枢电压与电机位置、转速、电枢电流采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

电机位置、转速、电枢电流

### 执行器

电枢电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 J=0.01 kg*m^2、b=0.1 Nm*s/rad、Kt=Ke=0.01、R=1 ohm、L=0.5 H；用 +/-1 V 测试并记录电流、转速和位置。

### 示例数据（JSON）

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
    "input_signal_id": "电枢电压",
    "output_signal_id": "电机位置",
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
    "stability": "Return 电枢电压 to baseline and verify that 电机位置、转速、电枢电流 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 电机位置、转速、电枢电流 direction with its final direction.",
    "delay": "Measure from the logged 电枢电压 edge to the first effective 电机位置、转速、电枢电流 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 电枢电压 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 34. 齿轮传动与输出侧等效惯量

### 控制问题描述

这是一个由电机、齿轮组、弹性传动轴和负载惯量组成的旋转传动装置。控制输入是电机力矩，输出是由传感器或同步记录器连续获取的电机与负载角度、轴力矩。在多次小幅且可逆的试验中，电机与负载角度开始时就沿最终方向变化，不会先向相反方向运动；电机力矩改变后，电机与负载角度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把电机力矩撤回基准值后，电机与负载角度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的电机力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电机力矩与电机与负载角度、轴力矩采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

电机与负载角度、轴力矩

### 执行器

电机力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用齿轮比 n=4、电机侧惯量 J1=0.002 kg*m^2、负载惯量 J2=0.03 kg*m^2、b1=0.001 与 b2=0.02 Nm*s/rad。

### 示例数据（JSON）

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
    "input_signal_id": "电机力矩",
    "output_signal_id": "电机与负载角度",
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
    "stability": "Return 电机力矩 to baseline and verify that 电机与负载角度、轴力矩 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 电机与负载角度、轴力矩 direction with its final direction.",
    "delay": "Measure from the logged 电机力矩 edge to the first effective 电机与负载角度、轴力矩 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 电机力矩 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```


---

## 35. 房间热损失一阶模型

### 控制问题描述

这是一个把室内空气等效为热容并通过墙体向室外散热的房间热系统。控制输入是标注为控制扩展的供热率，输出是由传感器或同步记录器连续获取的房间温度。在多次小幅且可逆的试验中，房间温度开始时就沿最终方向变化，不会先向相反方向运动；标注为控制扩展的供热率改变后，房间温度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把标注为控制扩展的供热率恢复到基准值后，房间温度最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的标注为控制扩展的供热率变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。标注为控制扩展的供热率与房间温度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

房间温度

### 执行器

标注为控制扩展的供热率

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

采用 90000 Btu/h 炉子；当室外 32 degF、室内 60 degF 时，开炉 0.1 h 升温 2 degF，停炉 40 min 降温 2 degF。由此得到 C=3913.04 Btu/degF、R=0.002385 degF/(Btu/h)。

未启用 LLM 时可在同一次提交末尾附上：`input_change=1 binary_command; steady_output_change=214.6597 degF; response_time_s=33600 s; input_min=0 binary_command; input_max=1 binary_command; output_min=32 degF; output_max=90 degF;`

### 示例数据（JSON）

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
    "input_signal_id": "标注为控制扩展的供热率",
    "output_signal_id": "房间温度",
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
    "stability": "Return 标注为控制扩展的供热率 to baseline and verify that 房间温度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 房间温度 direction with its final direction.",
    "delay": "Measure from the logged 标注为控制扩展的供热率 edge to the first effective 房间温度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 标注为控制扩展的供热率 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 36. 双热容温控过程

### 控制问题描述

这是一个由加热器和两个相互传热的热容量组成的温度过程。控制输入是加热功率，输出是由传感器或同步记录器连续获取的两个热体温度。在多次小幅且可逆的试验中，两个热体温度开始时就沿最终方向变化，不会先向相反方向运动；加热功率改变后，两个热体温度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把加热功率恢复到基准值后，两个热体温度最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的加热功率变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。加热功率与两个热体温度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

两个热体温度

### 执行器

加热功率

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

采用 C1=10000 J/degC、C2=15000 J/degC、Hx=200 W/degC、H1=100 W/degC、H2=150 W/degC，并施加 250、500、750、1000 W 热流阶跃。

### 示例数据（JSON）

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
    "input_signal_id": "加热功率",
    "output_signal_id": "两个热体温度",
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
    "stability": "Return 加热功率 to baseline and verify that 两个热体温度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 两个热体温度 direction with its final direction.",
    "delay": "Measure from the logged 加热功率 edge to the first effective 两个热体温度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 加热功率 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 37. 带双热惯性与测量延迟的换热器

### 控制问题描述

这是一个由蒸汽阀、两个主导热惯性和温度测量环节组成的换热过程。控制输入是蒸汽入口阀面积，输出是由传感器或同步记录器连续获取的测得的出口水温。在多次小幅且可逆的试验中，测得的出口水温开始时就沿最终方向变化，不会先向相反方向运动；蒸汽入口阀面积改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把蒸汽入口阀面积恢复到基准值后，测得的出口水温最终会收敛或保持有界，不会出现自行增长的运动。改变蒸汽入口阀面积的方向和幅值时，可以观察到固定的静态非线性，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。蒸汽入口阀面积与测得的出口水温采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

测得的出口水温

### 执行器

蒸汽入口阀面积

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

采用 30 s 与 60 s 两个热时间常数、0.5 degC/% 直流增益和 10 s 下游测量迟延；测试 2.5%、5%、7.5%、10% 阀门变化。

### 示例数据（JSON）

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
    "input_signal_id": "蒸汽入口阀面积",
    "output_signal_id": "测得的出口水温",
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
    "stability": "Return 蒸汽入口阀面积 to baseline and verify that 测得的出口水温 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 测得的出口水温 direction with its final direction.",
    "delay": "Measure from the logged 蒸汽入口阀面积 edge to the first effective 测得的出口水温 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 蒸汽入口阀面积 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 38. 水箱平方根出流与工作点线性化

### 控制问题描述

这是一个通过入口补液、并从出口按液位平方根规律排液的储水箱。控制输入是入口质量流量，输出是由传感器或同步记录器连续获取的水箱液位、出口流量。在多次小幅且可逆的试验中，水箱液位开始时就沿最终方向变化，不会先向相反方向运动；入口质量流量改变后，水箱液位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把入口质量流量恢复到基准值后，水箱液位最终会收敛或保持有界，不会出现自行增长的运动。改变入口质量流量的方向和幅值时，可以观察到固定的静态非线性，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。入口质量流量与水箱液位、出口流量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

水箱液位、出口流量

### 执行器

入口质量流量

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用水密度 1000 kg/m^3、槽面积 0.05 m^2、名义液位 0.15 m、名义出流 200 g/min；在线性化平方根出流后测试 +/-25 与 +/-50 g/min 泵流量变化。

未启用 LLM 时可在同一次提交末尾附上：`input_change=50 g/min; steady_output_change=0.1 m; response_time_s=120 s; input_min=0 g/min; input_max=500 g/min; output_min=0 m; output_max=0.5 m;`

### 示例数据（JSON）

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
    "input_signal_id": "入口质量流量",
    "output_signal_id": "水箱液位",
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
    "stability": "Return 入口质量流量 to baseline and verify that 水箱液位、出口流量 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 水箱液位、出口流量 direction with its final direction.",
    "delay": "Measure from the logged 入口质量流量 edge to the first effective 水箱液位、出口流量 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 入口质量流量 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 39. 压力驱动的单腔液压活塞

### 控制问题描述

这是一个由压力油腔推动活塞并带动机械负载直线运动的液压执行装置。控制输入是液压腔压差，输出是由传感器或同步记录器连续获取的活塞位置与速度。在多次小幅且可逆的试验中，活塞位置与速度开始时就沿最终方向变化，不会先向相反方向运动；液压腔压差改变后，活塞位置与速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把液压腔压差撤回基准值后，活塞位置与速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的液压腔压差变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。液压腔压差与活塞位置与速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

活塞位置与速度

### 执行器

液压腔压差

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用活塞质量 50 kg、面积 0.01 m^2；100 kPa 腔压变化产生 1000 N 和 20 m/s^2 初始加速度，位移限制为 +/-0.5 m。

未启用 LLM 时可在同一次提交末尾附上：`input_change=100 kPa; acceleration_change=20 m/s^2; motion_time_scale_s=2 s; input_min=0 kPa; input_max=500 kPa; output_min=-0.5 undefined; output_max=0.5 undefined;`

### 示例数据（JSON）

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
    "input_signal_id": "液压腔压差",
    "output_signal_id": "活塞位置与速度",
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
    "stability": "Return 液压腔压差 to baseline and verify that 活塞位置与速度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 活塞位置与速度 direction with its final direction.",
    "delay": "Measure from the logged 液压腔压差 edge to the first effective 活塞位置与速度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 液压腔压差 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 40. 液压舵面阀位到角度的负载相关积分模型

### 控制问题描述

这是一个由伺服阀、液压缸和承受外载的舵面组成的液压位置执行装置。控制输入是伺服阀位移，输出是由传感器或同步记录器连续获取的舵面角与负载力。在多次小幅且可逆的试验中，舵面角与负载力开始时就沿最终方向变化，不会先向相反方向运动；伺服阀位移改变后，舵面角与负载力在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把伺服阀位移撤回基准值后，舵面角与负载力会保留偏差或继续漂移，而不会依靠自身作用回到原位。当伺服阀位移的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。伺服阀位移与舵面角与负载力采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

舵面角与负载力

### 执行器

伺服阀位移

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用空载阀位到舵面角速度增益 0.8 rad/(s*mm)、阀行程 +/-5 mm、角度限制 +/-0.5 rad，并在负载使增益降为 0.72 与 0.64 rad/(s*mm) 时重复。

### 示例数据（JSON）

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
    "input_signal_id": "伺服阀位移",
    "output_signal_id": "舵面角与负载力",
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
    "stability": "Return 伺服阀位移 to baseline and verify that 舵面角与负载力 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 舵面角与负载力 direction with its final direction.",
    "delay": "Measure from the logged 伺服阀位移 edge to the first effective 舵面角与负载力 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 伺服阀位移 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 41. 用叠加与时移检验线性时不变性

### 控制问题描述

这是一个围绕同一动态对象搭建的可重复输入输出试验台，输入的平移和叠加关系能够在统一时钟下比较。控制输入是给定测试信号，输出是由传感器或同步记录器连续获取的系统输出响应。在多次小幅且可逆的试验中，系统输出响应开始时就沿最终方向变化，不会先向相反方向运动；给定测试信号改变后，系统输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定测试信号恢复到基准值后，系统输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定测试信号变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定测试信号与系统输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，系统输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

系统输出响应

### 执行器

给定测试信号

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 k=2 s^-1；采用 u1(t)=1、u2(t)=sin(t)、系数 1.5 与 -0.5、时移 1 s，以 0.01 s 采样 8 s，并比较叠加与时移响应。

### 示例数据（JSON）

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
    "input_signal_id": "给定测试信号",
    "output_signal_id": "系统输出响应",
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
    "stability": "Return 给定测试信号 to baseline and verify that 系统输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 系统输出响应 direction with its final direction.",
    "delay": "Measure from the logged 给定测试信号 edge to the first effective 系统输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 给定测试信号 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 42. 一阶系统冲激响应与卷积

### 控制问题描述

这是一个连接输入信号源和连续输出记录器的稳定一阶动态环节。控制输入是输入信号，输出是由传感器或同步记录器连续获取的输出响应。在多次小幅且可逆的试验中，输出响应开始时就沿最终方向变化，不会先向相反方向运动；输入信号改变后，输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把输入信号恢复到基准值后，输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的输入信号变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。输入信号与输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

输出响应

### 执行器

输入信号

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 k=0.5 s^-1；以 0.01 s 分辨率仿真 16 s 的单位冲激和单位阶跃，并把直接积分与 exp(-0.5 t) 卷积结果比较。

### 示例数据（JSON）

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
    "input_signal_id": "输入信号",
    "output_signal_id": "输出响应",
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
    "stability": "Return 输入信号 to baseline and verify that 输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 输出响应 direction with its final direction.",
    "delay": "Measure from the logged 输入信号 edge to the first effective 输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 输入信号 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 43. 由常微分方程求传递函数

### 控制问题描述

这是一个由线性微分方程描述、带外部激励端口和测量响应通道的动态对象。控制输入是给定外部激励，输出是由传感器或同步记录器连续获取的系统输出响应。在多次小幅且可逆的试验中，系统输出响应开始时就沿最终方向变化，不会先向相反方向运动；给定外部激励改变后，系统输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定外部激励恢复到基准值后，系统输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定外部激励变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定外部激励与系统输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，系统输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

系统输出响应

### 执行器

给定外部激励

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 y_ddot+5 y_dot+4 y=2 u 且初值为零；施加 +/-0.5 与 +/-1 N 阶跃，以 0.01 s 采样 8 s，并核对 G(s)=2/(s^2+5s+4)。

### 示例数据（JSON）

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
    "input_signal_id": "给定外部激励",
    "output_signal_id": "系统输出响应",
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
    "stability": "Return 给定外部激励 to baseline and verify that 系统输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 系统输出响应 direction with its final direction.",
    "delay": "Measure from the logged 给定外部激励 edge to the first effective 系统输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 给定外部激励 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 44. RC 低通的传递函数与冲激响应

### 控制问题描述

这是一个由电阻、电容、电感或运算放大器构成的电信号处理网络。控制输入是输入电压，输出是由传感器或同步记录器连续获取的电容电压。在多次小幅且可逆的试验中，电容电压开始时就沿最终方向变化，不会先向相反方向运动；输入电压改变后，电容电压在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把输入电压恢复到基准值后，电容电压最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的输入电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。输入电压与电容电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电容电压的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电容电压

### 执行器

输入电压

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 R=10 kohm、C=100 uF，得到 RC=1 s；以 0.01 s 采样 8 s，施加 0.25、0.5、0.75、1 V 阶跃。

### 示例数据（JSON）

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
    "input_signal_id": "输入电压",
    "output_signal_id": "电容电压",
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
    "stability": "Return 输入电压 to baseline and verify that 电容电压 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 电容电压 direction with its final direction.",
    "delay": "Measure from the logged 输入电压 edge to the first effective 电容电压 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 输入电压 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 45. 一阶系统正弦稳态幅相

### 控制问题描述

这是一个由正弦信号源驱动、并在暂态衰减后观察稳态响应的一阶惯性环节。控制输入是正弦输入，输出是由传感器或同步记录器连续获取的正弦输出幅值与相位。在多次小幅且可逆的试验中，正弦输出幅值与相位开始时就沿最终方向变化，不会先向相反方向运动；正弦输入改变后，正弦输出幅值与相位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把正弦输入恢复到基准值后，正弦输出幅值与相位最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的正弦输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。正弦输入与正弦输出幅值与相位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，正弦输出幅值与相位的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

正弦输出幅值与相位

### 执行器

正弦输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 k=1 s^-1、正弦幅值 1 V、omega=10 rad/s；以 0.002 s 采样 12 s，并在指数暂态消失后估计稳态幅值和相位。

### 示例数据（JSON）

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
    "input_signal_id": "正弦输入",
    "output_signal_id": "正弦输出幅值与相位",
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
    "stability": "Return 正弦输入 to baseline and verify that 正弦输出幅值与相位 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 正弦输出幅值与相位 direction with its final direction.",
    "delay": "Measure from the logged 正弦输入 edge to the first effective 正弦输出幅值与相位 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 正弦输入 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 46. 阶跃斜坡冲激与正弦输入的变换

### 控制问题描述

这是一个把阶跃、斜坡、冲激和正弦等典型波形送入动态表示的信号分析试验台。控制输入是典型测试信号，输出是由传感器或同步记录器连续获取的变换后的系统响应。在多次小幅且可逆的试验中，变换后的系统响应开始时就沿最终方向变化，不会先向相反方向运动；典型测试信号改变后，变换后的系统响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把典型测试信号恢复到基准值后，变换后的系统响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的典型测试信号变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。典型测试信号与变换后的系统响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，变换后的系统响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

变换后的系统响应

### 执行器

典型测试信号

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 G(s)=1/(s+1)、阶跃幅值 2、斜坡斜率 0.5、单位冲激面积 1、正弦频率 3 rad/s，以 0.005 s 采样 12 s。

### 示例数据（JSON）

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
    "input_signal_id": "典型测试信号",
    "output_signal_id": "变换后的系统响应",
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
    "stability": "Return 典型测试信号 to baseline and verify that 变换后的系统响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 变换后的系统响应 direction with its final direction.",
    "delay": "Measure from the logged 典型测试信号 edge to the first effective 变换后的系统响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 典型测试信号 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 47. 部分分式展开恢复时域响应

### 控制问题描述

这是一个根据变换域输入和时域记录重建内部模态的有理动态模型。控制输入是给定变换域输入，输出是由传感器或同步记录器连续获取的时域输出响应。在多次小幅且可逆的试验中，时域输出响应开始时就沿最终方向变化，不会先向相反方向运动；给定变换域输入改变后，时域输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定变换域输入恢复到基准值后，时域输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定变换域输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定变换域输入与时域输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，时域输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

时域输出响应

### 执行器

给定变换域输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 Y(s)=(s+2)(s+4)/[s(s+1)(s+3)]；以 0.005 s 采样 12 s 仿真单位冲激，并比较留数 8/3、-3/2、-1/6。

### 示例数据（JSON）

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
    "input_signal_id": "给定变换域输入",
    "output_signal_id": "时域输出响应",
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
    "stability": "Return 给定变换域输入 to baseline and verify that 时域输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 时域输出响应 direction with its final direction.",
    "delay": "Measure from the logged 给定变换域输入 edge to the first effective 时域输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 给定变换域输入 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 48. 终值定理的适用与失效

### 控制问题描述

这是一个需要结合所有相关极点位置来判断长期输出是否存在的动态对象。控制输入是测试输入，输出是由传感器或同步记录器连续获取的稳态输出。在多次小幅且可逆的试验中，稳态输出开始时就沿最终方向变化，不会先向相反方向运动；测试输入改变后，稳态输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把测试输入恢复到基准值后，稳态输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的测试输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。测试输入与稳态输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，稳态输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

稳态输出

### 执行器

测试输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

并行计算 Y1=3(s+2)/[s(s^2+2s+10)] 与 Y2=3/[s(s-2)]，以 0.002 s 采样 8 s，并在输出绝对值达到 100 时停止。

### 示例数据（JSON）

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
    "input_signal_id": "测试输入",
    "output_signal_id": "稳态输出",
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
    "stability": "Return 测试输入 to baseline and verify that 稳态输出 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 稳态输出 direction with its final direction.",
    "delay": "Measure from the logged 测试输入 edge to the first effective 稳态输出 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 测试输入 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 49. 稳定系统的直流增益

### 控制问题描述

这是一个在恒定输入下能够收敛到有限输出、并具有有限静态增益的自平衡对象。控制输入是单位阶跃输入，输出是由传感器或同步记录器连续获取的稳态输出。在多次小幅且可逆的试验中，稳态输出开始时就沿最终方向变化，不会先向相反方向运动；单位阶跃输入改变后，稳态输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把单位阶跃输入恢复到基准值后，稳态输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的单位阶跃输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。单位阶跃输入与稳态输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，稳态输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

稳态输出

### 执行器

单位阶跃输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 G(s)=3(s+2)/(s^2+2s+10)；施加 0.25、0.5、0.75、1 四级阶跃，以 0.005 s 采样 12 s，并核对 0.6 直流增益。

### 示例数据（JSON）

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
    "input_signal_id": "单位阶跃输入",
    "output_signal_id": "稳态输出",
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
    "stability": "Return 单位阶跃输入 to baseline and verify that 稳态输出 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 稳态输出 direction with its final direction.",
    "delay": "Measure from the logged 单位阶跃输入 edge to the first effective 稳态输出 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 单位阶跃输入 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 50. 带初值常微分方程的自由与受迫响应

### 控制问题描述

这是一个既会由初态储存的能量产生自由运动、也会响应独立外部激励的状态模型。控制输入是外部激励与给定初态释放，输出是由传感器或同步记录器连续获取的状态与输出响应。在多次小幅且可逆的试验中，状态与输出响应开始时就沿最终方向变化，不会先向相反方向运动；外部激励与给定初态释放改变后，状态与输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把外部激励与给定初态释放恢复到基准值后，状态与输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的外部激励与给定初态释放变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。外部激励与给定初态释放与状态与输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，状态与输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

状态与输出响应

### 执行器

外部激励与给定初态释放

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 y_ddot+5 y_dot+4 y=u；先运行初值 (y0,ydot0)=(1,0) 与 (0,1)，再运行零初值输入 u=2 exp(-2t)，以 0.005 s 采样 10 s。

### 示例数据（JSON）

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
    "input_signal_id": "外部激励与给定初态释放",
    "output_signal_id": "状态与输出响应",
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
    "stability": "Return 外部激励与给定初态释放 to baseline and verify that 状态与输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 状态与输出响应 direction with its final direction.",
    "delay": "Measure from the logged 外部激励与给定初态释放 edge to the first effective 状态与输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 外部激励与给定初态释放 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 51. 巡航模型的位置动态

### 控制问题描述

这是一个由车辆质量、驱动力和行驶阻力决定速度的汽车纵向运动系统。控制输入是驱动力，输出是由传感器或同步记录器连续获取的车辆位置与速度。在多次小幅且可逆的试验中，车辆位置与速度开始时就沿最终方向变化，不会先向相反方向运动；驱动力改变后，车辆位置与速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把驱动力撤回基准值后，车辆位置与速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的驱动力变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。驱动力与车辆位置与速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，车辆位置与速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

车辆位置与速度

### 执行器

驱动力

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 m=1000 kg、b=50 N*s/m 和 500 N 力阶跃；以 0.05 s 采样 120 s 的速度与位置，位置模型为 Gx=0.001/[s(s+0.05)]。

### 示例数据（JSON）

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
    "input_signal_id": "驱动力",
    "output_signal_id": "车辆位置与速度",
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
    "stability": "Return 驱动力 to baseline and verify that 车辆位置与速度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 车辆位置与速度 direction with its final direction.",
    "delay": "Measure from the logged 驱动力 edge to the first effective 车辆位置与速度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 驱动力 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 52. 直流电机位置与速度极点

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是电枢电压，输出是由传感器或同步记录器连续获取的电机速度与位置。在多次小幅且可逆的试验中，电机速度与位置开始时就沿最终方向变化，不会先向相反方向运动；电枢电压改变后，电机速度与位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把电枢电压撤回基准值后，电机速度与位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电枢电压与电机速度与位置采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机速度与位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机速度与位置

### 执行器

电枢电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 J=0.01 kg*m^2、b=0.001 Nm*s/rad、Kt=Ke=1、Ra=10 ohm、La=1 H；用 +/-1 V 测试，以 0.001 s 记录 5 s 的电流、转速和角度。

### 示例数据（JSON）

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
    "input_signal_id": "电枢电压",
    "output_signal_id": "电机速度与位置",
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
    "stability": "Return 电枢电压 to baseline and verify that 电机速度与位置 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 电机速度与位置 direction with its final direction.",
    "delay": "Measure from the logged 电枢电压 edge to the first effective 电机速度与位置 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 电枢电压 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 53. 刚性卫星有限推力脉冲响应

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是有限推力脉冲，输出是由传感器或同步记录器连续获取的姿态角与角速度。在多次小幅且可逆的试验中，姿态角与角速度开始时就沿最终方向变化，不会先向相反方向运动；有限推力脉冲改变后，姿态角与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有限推力脉冲撤回基准值后，姿态角与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的有限推力脉冲变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有限推力脉冲与姿态角与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，姿态角与角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

姿态角与角速度

### 执行器

有限推力脉冲

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

采用力臂 d=1 m、惯量 I=5000 kg*m^2；在 5.0 至 5.1 s 施加 25 N 脉冲，并以 0.01 s 采样至 10 s。

未启用 LLM 时可在同一次提交末尾附上：`input_change=25 N; acceleration_change=0.005 rad/s^2; motion_time_scale_s=10 s; input_min=-50 N; input_max=50 N; output_min=-0.02 output_unit; output_max=0.02 output_unit;`

### 示例数据（JSON）

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
    "input_signal_id": "有限推力脉冲",
    "output_signal_id": "姿态角与角速度",
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
    "stability": "Return 有限推力脉冲 to baseline and verify that 姿态角与角速度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 姿态角与角速度 direction with its final direction.",
    "delay": "Measure from the logged 有限推力脉冲 edge to the first effective 姿态角与角速度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 有限推力脉冲 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 54. 嵌套控制框图化简

### 控制问题描述

这是一个由参考、控制器、对象、传感器和嵌套内环信号通道组成的反馈系统。控制输入是参考输入，输出是由传感器或同步记录器连续获取的闭环输出。在多次小幅且可逆的试验中，闭环输出开始时就沿最终方向变化，不会先向相反方向运动；参考输入改变后，闭环输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把参考输入恢复到基准值后，闭环输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的参考输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。参考输入与闭环输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，闭环输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

闭环输出

### 执行器

参考输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用并联控制器支路 2 与 4/s、对象 1/s 和单位负反馈；以 0.005 s 采样 10 s，施加 +/-0.5 与 +/-1 参考阶跃。

### 示例数据（JSON）

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
    "input_signal_id": "参考输入",
    "output_signal_id": "闭环输出",
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
    "stability": "Return 参考输入 to baseline and verify that 闭环输出 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 闭环输出 direction with its final direction.",
    "delay": "Measure from the logged 参考输入 edge to the first effective 闭环输出 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 参考输入 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 55. Mason 公式求闭环传递函数

### 控制问题描述

这是一个用有向支路在源节点、内部节点、反馈节点和输出节点之间传递增益的信号流网络。控制输入是给定源节点信号，输出是由传感器或同步记录器连续获取的信号流图输出响应。在多次小幅且可逆的试验中，信号流图输出响应开始时就沿最终方向变化，不会先向相反方向运动；给定源节点信号改变后，信号流图输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定源节点信号恢复到基准值后，信号流图输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定源节点信号变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定源节点信号与信号流图输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，信号流图输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

信号流图输出响应

### 执行器

给定源节点信号

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取前向路径 P=6、带符号接触回路 L=0.2，Mason 增益为 6/(1-0.2)=7.5；再把回路改为 -0.2 与 0 重复。

### 示例数据（JSON）

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
    "input_signal_id": "给定源节点信号",
    "output_signal_id": "信号流图输出响应",
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
    "stability": "Return 给定源节点信号 to baseline and verify that 信号流图输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 信号流图输出响应 direction with its final direction.",
    "delay": "Measure from the logged 给定源节点信号 edge to the first effective 信号流图输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 给定源节点信号 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 56. 由极点判断暂态形态与衰减率

### 控制问题描述

这是一个自由运动和脉冲响应形态都由极点位置决定的模态动态对象。控制输入是有界脉冲测试，输出是由传感器或同步记录器连续获取的瞬态输出响应。在多次小幅且可逆的试验中，瞬态输出响应开始时就沿最终方向变化，不会先向相反方向运动；有界脉冲测试改变后，瞬态输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界脉冲测试恢复到基准值后，瞬态输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的有界脉冲测试变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界脉冲测试与瞬态输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，瞬态输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

瞬态输出响应

### 执行器

有界脉冲测试

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 H(s)=(2s+1)/(s^2+3s+2)；施加正负单位冲激，以 0.005 s 采样 10 s，并拟合 -1、-2 模态及留数 -1、3。

### 示例数据（JSON）

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
    "input_signal_id": "有界脉冲测试",
    "output_signal_id": "瞬态输出响应",
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
    "stability": "Return 有界脉冲测试 to baseline and verify that 瞬态输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 瞬态输出响应 direction with its final direction.",
    "delay": "Measure from the logged 有界脉冲测试 edge to the first effective 瞬态输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 有界脉冲测试 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 57. 二阶性能指标与极点区域

### 控制问题描述

这是一个由主导共轭极点决定上升、峰值、超调和收敛过程的阻尼二阶对象。控制输入是有界指令阶跃，输出是由传感器或同步记录器连续获取的阶跃响应及其瞬态特征。在多次小幅且可逆的试验中，阶跃响应及其瞬态特征开始时就沿最终方向变化，不会先向相反方向运动；有界指令阶跃改变后，阶跃响应及其瞬态特征在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界指令阶跃恢复到基准值后，阶跃响应及其瞬态特征最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的有界指令阶跃变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界指令阶跃与阶跃响应及其瞬态特征采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，阶跃响应及其瞬态特征的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

阶跃响应及其瞬态特征

### 执行器

有界指令阶跃

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 omega_n=3 rad/s、zeta=0.6 及单位直流增益模型 9/(s^2+3.6s+9)；以 0.002 s 采样 8 s，测量上升、峰值和 1% 调节时间。

### 示例数据（JSON）

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
    "input_signal_id": "有界指令阶跃",
    "output_signal_id": "阶跃响应及其瞬态特征",
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
    "stability": "Return 有界指令阶跃 to baseline and verify that 阶跃响应及其瞬态特征 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 阶跃响应及其瞬态特征 direction with its final direction.",
    "delay": "Measure from the logged 有界指令阶跃 edge to the first effective 阶跃响应及其瞬态特征 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 有界指令阶跃 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 58. 波音飞机右半平面零点的逆响应

### 控制问题描述

这是一个由气动力、舵面执行机构和机载运动传感器组成的飞机飞行控制系统。控制输入是升降舵冲激偏角，输出是由传感器或同步记录器连续获取的飞机高度。在多次小幅且可逆的试验中，飞机高度开始时会先沿不利或相反方向运动，随后才转向；升降舵冲激偏角改变后，飞机高度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把升降舵冲激偏角撤回基准值后，飞机高度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的升降舵冲激偏角变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。升降舵冲激偏角与飞机高度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

飞机高度

### 执行器

升降舵冲激偏角

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

采用 h/delta_e=30(s-6)/[s(s^2+4s+13)] 和 -1 deg 升降舵冲激；以 0.002 s 采样 12 s，并保留初始高度下沉与最终偏置。

### 示例数据（JSON）

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
    "input_signal_id": "升降舵冲激偏角",
    "output_signal_id": "飞机高度",
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
    "stability": "Return 升降舵冲激偏角 to baseline and verify that 飞机高度 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 飞机高度 direction with its final direction.",
    "delay": "Measure from the logged 升降舵冲激偏角 edge to the first effective 飞机高度 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 升降舵冲激偏角 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 59. 电流驱动电容的 BIBO 稳定性

### 控制问题描述

这是一个由电阻、电容、电感或运算放大器构成的电信号处理网络。控制输入是有界源电流，输出是由传感器或同步记录器连续获取的电容电压。在多次小幅且可逆的试验中，电容电压开始时就沿最终方向变化，不会先向相反方向运动；有界源电流改变后，电容电压在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界源电流撤回基准值后，电容电压会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的有界源电流变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界源电流与电容电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电容电压的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电容电压

### 执行器

有界源电流

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

采用 C=0.01 F；施加 +/-0.1 A 恒流并设置 50 V 停止边界，以 0.01 s 采样，核对电压斜坡与 BIBO 反例。

### 示例数据（JSON）

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
    "input_signal_id": "有界源电流",
    "output_signal_id": "电容电压",
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
    "stability": "Return 有界源电流 to baseline and verify that 电容电压 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 电容电压 direction with its final direction.",
    "delay": "Measure from the logged 有界源电流 edge to the first effective 电容电压 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 有界源电流 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 60. Routh 判据求比例与 PI 稳定增益区间

### 控制问题描述

这是一个通过扫描控制器设定并观察闭环稳定性的动态反馈系统。控制输入是比例与积分设定扫描中的有界控制命令，输出是由传感器或同步记录器连续获取的不同设定下的受控输出响应。在多次小幅且可逆的试验中，不同设定下的受控输出响应开始时就沿最终方向变化，不会先向相反方向运动；比例与积分设定扫描中的有界控制命令改变后，不同设定下的受控输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。即使把比例与积分设定扫描中的有界控制命令撤回基准值，不同设定下的受控输出响应的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。分别施加小幅正向和反向的比例与积分设定扫描中的有界控制命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。比例与积分设定扫描中的有界控制命令与不同设定下的受控输出响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，不同设定下的受控输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

不同设定下的受控输出响应

### 执行器

比例与积分设定扫描中的有界控制命令

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

比例案例取 K=13，并与 K=7.5、25 比较；PI 案例取 (K,Ki)=(2,6)，再与边界 Ki=6+3K 比较，以 0.005 s 采样 20 s。

### 示例数据（JSON）

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
    "input_signal_id": "比例与积分设定扫描中的有界控制命令",
    "output_signal_id": "不同设定下的受控输出响应",
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
    "stability": "Return 比例与积分设定扫描中的有界控制命令 to baseline and verify that 不同设定下的受控输出响应 remains bounded or follows the declared unstable-event handling.",
    "phase": "Apply equal small positive and negative changes and compare the first effective 不同设定下的受控输出响应 direction with its final direction.",
    "delay": "Measure from the logged 比例与积分设定扫描中的有界控制命令 edge to the first effective 不同设定下的受控输出响应 sample.",
    "order": "Compare early- and late-response residuals against the complete numerical model.",
    "sensing_and_actuation": "Log 比例与积分设定扫描中的有界控制命令 and every declared output on one clock.",
    "nonlinearity": "Repeat at 25%, 50%, 75%, and 100% of the local test amplitude.",
    "coupling": "Change one available input at a time while holding the others at baseline.",
    "uncertainty": "Repeat with relevant parameters multiplied by 0.9, 1.0, and 1.1."
  }
}
```

---

## 61. 灵敏度与互补灵敏度的闭环通道

### 控制问题描述

这是一个带参考、对象扰动、传感噪声、控制器和测量输出等独立端口的标准反馈环路。控制输入是参考指令以及给定对象扰动和传感噪声，输出是由传感器或同步记录器连续获取的受控输出、跟踪误差与控制作用。在多次小幅且可逆的试验中，受控输出开始时就沿最终方向变化，不会先向相反方向运动；参考指令以及给定对象扰动和传感噪声改变后，受控输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把参考指令以及给定对象扰动和传感噪声恢复到基准值后，受控输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的参考指令以及给定对象扰动和传感噪声变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。参考指令以及给定对象扰动和传感噪声与受控输出、跟踪误差与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，受控输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

受控输出、跟踪误差与控制作用

### 执行器

参考指令以及给定对象扰动和传感噪声

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/(s+1)、D=9；参考、对象扰动与传感噪声分别施加 ±0.5、±1，以 0.01 s 采样 8 s。

### 示例数据（JSON）

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
    "input_signal_id": "参考指令以及给定对象扰动和传感噪声",
    "output_signal_id": "受控输出",
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
    "stability": "令 参考指令以及给定对象扰动和传感噪声 回到基线，核对 受控输出、跟踪误差与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出、跟踪误差与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 参考指令以及给定对象扰动和传感噪声 边沿量到 受控输出、跟踪误差与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 参考指令以及给定对象扰动和传感噪声 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 62. 用特征方程稳定倒立摆

### 控制问题描述

这是一个由转轴、刚性杆和集中质量构成的摆动机械装置。控制输入是有界动态补偿器命令，输出是由传感器或同步记录器连续获取的摆角与补偿器输出。在多次小幅且可逆的试验中，摆角与补偿器输出开始时就沿最终方向变化，不会先向相反方向运动；有界动态补偿器命令改变后，摆角与补偿器输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把有界动态补偿器命令撤回基准值，摆角与补偿器输出的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。分别施加小幅正向和反向的有界动态补偿器命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界动态补偿器命令与摆角与补偿器输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，摆角与补偿器输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

摆角与补偿器输出

### 执行器

有界动态补偿器命令

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

对 G=1/(s^2-1) 取 zeta=0.7、wn=2 rad/s、gamma=1、delta=3.8、K=7.8；±0.25 阶跃以 0.005 s 采样 8 s。

### 示例数据（JSON）

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
    "input_signal_id": "有界动态补偿器命令",
    "output_signal_id": "摆角与补偿器输出",
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
    "stability": "令 有界动态补偿器命令 回到基线，核对 摆角与补偿器输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 摆角与补偿器输出 的首次有效方向与最终方向。",
    "delay": "从记录的 有界动态补偿器命令 边沿量到 摆角与补偿器输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界动态补偿器命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 63. 反馈降低对象增益灵敏度

### 控制问题描述

这是一个对象物理增益可以变化、而控制器和传感器始终闭合在同一通道上的反馈系统。控制输入是有界控制器命令，输出是由传感器或同步记录器连续获取的受控输出与跟踪误差。在多次小幅且可逆的试验中，受控输出与跟踪误差开始时就沿最终方向变化，不会先向相反方向运动；有界控制器命令改变后，受控输出与跟踪误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界控制器命令恢复到基准值后，受控输出与跟踪误差最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的有界控制器命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界控制器命令与受控输出与跟踪误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，受控输出与跟踪误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

受控输出与跟踪误差

### 执行器

有界控制器命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

检验频率取 P=1、C=99，并把 P 乘 0.9、1.1 重复；时域采用 1/(s+1)。

### 示例数据（JSON）

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
    "input_signal_id": "有界控制器命令",
    "output_signal_id": "受控输出与跟踪误差",
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
    "stability": "令 有界控制器命令 回到基线，核对 受控输出与跟踪误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出与跟踪误差 的首次有效方向与最终方向。",
    "delay": "从记录的 有界控制器命令 边沿量到 受控输出与跟踪误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界控制器命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 64. 扰动抑制与传感噪声衰减权衡

### 控制问题描述

这是一个让对象扰动和传感噪声从不同位置进入、并同时观察输出与误差的反馈环路。控制输入是对象扰动与传感噪声测试输入，输出是由传感器或同步记录器连续获取的受控输出、误差与传感噪声响应。在多次小幅且可逆的试验中，受控输出开始时就沿最终方向变化，不会先向相反方向运动；对象扰动与传感噪声测试输入改变后，受控输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把对象扰动与传感噪声测试输入恢复到基准值后，受控输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的对象扰动与传感噪声测试输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。对象扰动与传感噪声测试输入与受控输出、误差与传感噪声响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，受控输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

受控输出、误差与传感噪声响应

### 执行器

对象扰动与传感噪声测试输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 L=100/(s+1)；测试低频对象扰动及 1、10、100、1000 rad/s 传感噪声。

### 示例数据（JSON）

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
    "input_signal_id": "对象扰动与传感噪声测试输入",
    "output_signal_id": "受控输出",
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
    "stability": "令 对象扰动与传感噪声测试输入 回到基线，核对 受控输出、误差与传感噪声响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出、误差与传感噪声响应 的首次有效方向与最终方向。",
    "delay": "从记录的 对象扰动与传感噪声测试输入 边沿量到 受控输出、误差与传感噪声响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 对象扰动与传感噪声测试输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 65. Type 零比例速度控制的稳态误差

### 控制问题描述

这是一个由自平衡对象、比例控制器和速度传感器组成的速度伺服系统。控制输入是比例控制命令，输出是由传感器或同步记录器连续获取的速度与跟踪误差。在多次小幅且可逆的试验中，速度与跟踪误差开始时就沿最终方向变化，不会先向相反方向运动；比例控制命令改变后，速度与跟踪误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把比例控制命令恢复到基准值后，速度与跟踪误差最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的比例控制命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。比例控制命令与速度与跟踪误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，速度与跟踪误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

速度与跟踪误差

### 执行器

比例控制命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 A=2、tau=5 s、kP=4；±0.5、±1 速度阶跃以 0.02 s 采样 20 s。

### 示例数据（JSON）

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
    "input_signal_id": "比例控制命令",
    "output_signal_id": "速度与跟踪误差",
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
    "stability": "令 比例控制命令 回到基线，核对 速度与跟踪误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 速度与跟踪误差 的首次有效方向与最终方向。",
    "delay": "从记录的 比例控制命令 边沿量到 速度与跟踪误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 比例控制命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 66. 用积分把速度环提升为 Type 一

### 控制问题描述

这是一个由比例积分控制器在对象环路中增加误差累积状态的速度伺服系统。控制输入是PI 控制命令，输出是由传感器或同步记录器连续获取的速度与跟踪误差。在多次小幅且可逆的试验中，速度与跟踪误差开始时就沿最终方向变化，不会先向相反方向运动；PI 控制命令改变后，速度与跟踪误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把PI 控制命令恢复到基准值后，速度与跟踪误差最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的PI 控制命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。PI 控制命令与速度与跟踪误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，速度与跟踪误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

速度与跟踪误差

### 执行器

PI 控制命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 A=2、tau=5 s、kP=2、kI=0.5；阶跃和斜坡分别以 0.02 s 运行 30 s。

### 示例数据（JSON）

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
    "input_signal_id": "PI 控制命令",
    "output_signal_id": "速度与跟踪误差",
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
    "stability": "令 PI 控制命令 回到基线，核对 速度与跟踪误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 速度与跟踪误差 的首次有效方向与最终方向。",
    "delay": "从记录的 PI 控制命令 边沿量到 速度与跟踪误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 PI 控制命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 67. 测速反馈下的系统型别与速度常数

### 控制问题描述

这是一个采用电枢电压驱动并带测速机速度反馈的直流电机位置装置。控制输入是测速反馈下的电枢电压，输出是由传感器或同步记录器连续获取的电机位置、转速与跟踪误差。在多次小幅且可逆的试验中，电机位置开始时就沿最终方向变化，不会先向相反方向运动；测速反馈下的电枢电压改变后，电机位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把测速反馈下的电枢电压撤回基准值后，电机位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的测速反馈下的电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。测速反馈下的电枢电压与电机位置、转速与跟踪误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机位置、转速与跟踪误差

### 执行器

测速反馈下的电枢电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 tau=1 s、kP=4、kt=0.25 s；阶跃和斜坡以 0.01 s 运行 15 s。

### 示例数据（JSON）

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
    "input_signal_id": "测速反馈下的电枢电压",
    "output_signal_id": "电机位置",
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
    "stability": "令 测速反馈下的电枢电压 回到基线，核对 电机位置、转速与跟踪误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机位置、转速与跟踪误差 的首次有效方向与最终方向。",
    "delay": "从记录的 测速反馈下的电枢电压 边沿量到 电机位置、转速与跟踪误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 测速反馈下的电枢电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 68. 直流电机 P 与 PI 的扰动力矩型别

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是带给定负载力矩扰动的电枢电压，输出是由传感器或同步记录器连续获取的电机位置、转速与扰动响应。在多次小幅且可逆的试验中，电机位置开始时就沿最终方向变化，不会先向相反方向运动；带给定负载力矩扰动的电枢电压改变后，电机位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把带给定负载力矩扰动的电枢电压撤回基准值后，电机位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的带给定负载力矩扰动的电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。带给定负载力矩扰动的电枢电压与电机位置、转速与扰动响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机位置、转速与扰动响应

### 执行器

带给定负载力矩扰动的电枢电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 A=B=tau=1；单位转矩扰动下比较 P 的 kP=4 与 PI 的 kP=4、kI=2。

### 示例数据（JSON）

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
    "input_signal_id": "带给定负载力矩扰动的电枢电压",
    "output_signal_id": "电机位置",
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
    "stability": "令 带给定负载力矩扰动的电枢电压 回到基线，核对 电机位置、转速与扰动响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机位置、转速与扰动响应 的首次有效方向与最终方向。",
    "delay": "从记录的 带给定负载力矩扰动的电枢电压 边沿量到 电机位置、转速与扰动响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 带给定负载力矩扰动的电枢电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 69. 比例控制的速度偏差阻尼权衡

### 控制问题描述

这是一个通过比例执行命令操作、并由输出传感器观察的自平衡过程。控制输入是比例执行器命令，输出是由传感器或同步记录器连续获取的受控输出、跟踪误差与控制量。在多次小幅且可逆的试验中，受控输出开始时就沿最终方向变化，不会先向相反方向运动；比例执行器命令改变后，受控输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把比例执行器命令恢复到基准值后，受控输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的比例执行器命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。比例执行器命令与受控输出、跟踪误差与控制量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，受控输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

受控输出、跟踪误差与控制量

### 执行器

比例执行器命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 A=1、a1=1.4、a2=1；单位阶跃比较 kP=1.5 与 6，以 0.01 s 运行 15 s。

### 示例数据（JSON）

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
    "input_signal_id": "比例执行器命令",
    "output_signal_id": "受控输出",
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
    "stability": "令 比例执行器命令 回到基线，核对 受控输出、跟踪误差与控制量 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出、跟踪误差与控制量 的首次有效方向与最终方向。",
    "delay": "从记录的 比例执行器命令 边沿量到 受控输出、跟踪误差与控制量 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 比例执行器命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 70. 积分控制的鲁棒零误差

### 控制问题描述

这是一个由积分控制器累积跟踪误差、同时允许恒定扰动进入对象的过程控制环路。控制输入是积分控制命令与测试扰动，输出是由传感器或同步记录器连续获取的跟踪误差、对象输出与控制量。在多次小幅且可逆的试验中，跟踪误差开始时就沿最终方向变化，不会先向相反方向运动；积分控制命令与测试扰动改变后，跟踪误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把积分控制命令与测试扰动恢复到基准值后，跟踪误差最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的积分控制命令与测试扰动变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。积分控制命令与测试扰动与跟踪误差、对象输出与控制量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，跟踪误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

跟踪误差、对象输出与控制量

### 执行器

积分控制命令与测试扰动

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/(s^2+1.4s+1)、kI=0.5；参考和对象扰动阶跃分开运行并启用 anti-windup。

### 示例数据（JSON）

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
    "input_signal_id": "积分控制命令与测试扰动",
    "output_signal_id": "跟踪误差",
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
    "stability": "令 积分控制命令与测试扰动 回到基线，核对 跟踪误差、对象输出与控制量 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 跟踪误差、对象输出与控制量 的首次有效方向与最终方向。",
    "delay": "从记录的 积分控制命令与测试扰动 边沿量到 跟踪误差、对象输出与控制量 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 积分控制命令与测试扰动 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 71. 微分与速率反馈增加阻尼

### 控制问题描述

这是一个同时具有输出测量和速率反馈、可以独立改变阻尼特性的运动控制对象。控制输入是比例与速率命令，输出是由传感器或同步记录器连续获取的输出及其速率。在多次小幅且可逆的试验中，输出及其速率开始时就沿最终方向变化，不会先向相反方向运动；比例与速率命令改变后，输出及其速率在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把比例与速率命令恢复到基准值后，输出及其速率最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的比例与速率命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。比例与速率命令与输出及其速率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，输出及其速率的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

输出及其速率

### 执行器

比例与速率命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/(s^2+1.4s+1)、kP=6；比较 kD=0 与输出速率 kD=2，以 0.005 s 运行 12 s。

### 示例数据（JSON）

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
    "input_signal_id": "比例与速率命令",
    "output_signal_id": "输出及其速率",
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
    "stability": "令 比例与速率命令 回到基线，核对 输出及其速率 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 输出及其速率 的首次有效方向与最终方向。",
    "delay": "从记录的 比例与速率命令 边沿量到 输出及其速率 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 比例与速率命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 72. 双热容过程 PI 设计

### 控制问题描述

这是一个由加热器、两个相互换热的热容量、温度传感器和 PI 控制器组成的温控过程。控制输入是加热命令，输出是由传感器或同步记录器连续获取的受控温度与控制量。在多次小幅且可逆的试验中，受控温度与控制量开始时就沿最终方向变化，不会先向相反方向运动；加热命令改变后，受控温度与控制量在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把加热命令恢复到基准值后，受控温度与控制量最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的加热命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。加热命令与受控温度与控制量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

受控温度与控制量

### 执行器

加热命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

取 Ko=1000、tau1=1 s、tau2=10 s；对 30 degC/s、上限 300 degC 的参考比较 P(0.03) 与 PI(0.03,0.003)。

### 示例数据（JSON）

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
    "input_signal_id": "加热命令",
    "output_signal_id": "受控温度与控制量",
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
    "stability": "令 加热命令 回到基线，核对 受控温度与控制量 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控温度与控制量 的首次有效方向与最终方向。",
    "delay": "从记录的 加热命令 边沿量到 受控温度与控制量 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 加热命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 73. 直流电机 P、PI 与 PID 比较

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是带给定负载力矩扰动的电枢电压，输出是由传感器或同步记录器连续获取的电机转速、跟踪误差与扰动响应。在多次小幅且可逆的试验中，电机转速开始时就沿最终方向变化，不会先向相反方向运动；带给定负载力矩扰动的电枢电压改变后，电机转速在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把带给定负载力矩扰动的电枢电压恢复到基准值后，电机转速最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的带给定负载力矩扰动的电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。带给定负载力矩扰动的电枢电压与电机转速、跟踪误差与扰动响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机转速的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机转速、跟踪误差与扰动响应

### 执行器

带给定负载力矩扰动的电枢电压

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 Jm=0.0113、b=0.028、La=0.1、Ra=1、Kt=Ke=0.067；用 kP=3、kI=15、kD=0.3 比较 P/PI/PID。

### 示例数据（JSON）

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
    "input_signal_id": "带给定负载力矩扰动的电枢电压",
    "output_signal_id": "电机转速",
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
    "stability": "令 带给定负载力矩扰动的电枢电压 回到基线，核对 电机转速、跟踪误差与扰动响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机转速、跟踪误差与扰动响应 的首次有效方向与最终方向。",
    "delay": "从记录的 带给定负载力矩扰动的电枢电压 边沿量到 电机转速、跟踪误差与扰动响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 带给定负载力矩扰动的电枢电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 74. 非单位传感下的直流电机位置 P/PI 型别

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是带给定扰动力矩的电机电压，输出是由传感器或同步记录器连续获取的电机位置、转速与检测误差。在多次小幅且可逆的试验中，电机位置开始时就沿最终方向变化，不会先向相反方向运动；带给定扰动力矩的电机电压改变后，电机位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把带给定扰动力矩的电机电压撤回基准值后，电机位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的带给定扰动力矩的电机电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。带给定扰动力矩的电机电压与电机位置、转速与检测误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机位置、转速与检测误差

### 执行器

带给定扰动力矩的电机电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 A=B=tau=1、h=0.8；参考与转矩扰动下比较 P(4) 与 PI(4,2)。

### 示例数据（JSON）

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
    "input_signal_id": "带给定扰动力矩的电机电压",
    "output_signal_id": "电机位置",
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
    "stability": "令 带给定扰动力矩的电机电压 回到基线，核对 电机位置、转速与检测误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机位置、转速与检测误差 的首次有效方向与最终方向。",
    "delay": "从记录的 带给定扰动力矩的电机电压 边沿量到 电机位置、转速与检测误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 带给定扰动力矩的电机电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 75. 卫星 PD 与 PID 的参考/扰动型别

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是带给定扰动力矩的机体力矩命令，输出是由传感器或同步记录器连续获取的姿态角、角速度与跟踪误差。在多次小幅且可逆的试验中，姿态角开始时就沿最终方向变化，不会先向相反方向运动；带给定扰动力矩的机体力矩命令改变后，姿态角在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把带给定扰动力矩的机体力矩命令撤回基准值后，姿态角会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的带给定扰动力矩的机体力矩命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。带给定扰动力矩的机体力矩命令与姿态角、角速度与跟踪误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，姿态角的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

姿态角、角速度与跟踪误差

### 执行器

带给定扰动力矩的机体力矩命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取 J=1、kP=4、kD=3；PID 再加 kI=1。参考与转矩输入逐一测试。

### 示例数据（JSON）

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
    "input_signal_id": "带给定扰动力矩的机体力矩命令",
    "output_signal_id": "姿态角",
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
    "stability": "令 带给定扰动力矩的机体力矩命令 回到基线，核对 姿态角、角速度与跟踪误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 姿态角、角速度与跟踪误差 的首次有效方向与最终方向。",
    "delay": "从记录的 带给定扰动力矩的机体力矩命令 边沿量到 姿态角、角速度与跟踪误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 带给定扰动力矩的机体力矩命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 76. 由过程反应曲线整定 PID

### 控制问题描述

这是一个先通过小幅执行器阶跃记录过程反应曲线、再据此整定 PID 的工业过程环路。控制输入是P、PI 或 PID 过程命令，输出是由传感器或同步记录器连续获取的过程输出与四分之一衰减响应。在多次小幅且可逆的试验中，过程输出与四分之一衰减响应开始时就沿最终方向变化，不会先向相反方向运动；P、PI 或 PID 过程命令改变后，过程输出与四分之一衰减响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把P、PI 或 PID 过程命令恢复到基准值后，过程输出与四分之一衰减响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的P、PI 或 PID 过程命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。P、PI 或 PID 过程命令与过程输出与四分之一衰减响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，过程输出与四分之一衰减响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

过程输出与四分之一衰减响应

### 执行器

P、PI 或 PID 过程命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=2 exp(-3s)/(20s+1)、R=0.1 s^-1、L=3 s；以 0.02 s 运行 100 s 测试反应曲线 P/PI/PID。

### 示例数据（JSON）

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
    "output_signal_id": "过程输出与四分之一衰减响应",
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
    "stability": "令 P、PI 或 PID 过程命令 回到基线，核对 过程输出与四分之一衰减响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 过程输出与四分之一衰减响应 的首次有效方向与最终方向。",
    "delay": "从记录的 P、PI 或 PID 过程命令 边沿量到 过程输出与四分之一衰减响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 P、PI 或 PID 过程命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 77. 由极限增益和周期整定 PID

### 控制问题描述

这是一个能够逐步提高比例增益直到测量输出出现持续振荡的过程反馈环路。控制输入是比例或 PID 过程命令，输出是由传感器或同步记录器连续获取的临界振荡与整定响应。在多次小幅且可逆的试验中，临界振荡与整定响应开始时就沿最终方向变化，不会先向相反方向运动；比例或 PID 过程命令改变后，临界振荡与整定响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把比例或 PID 过程命令恢复到基准值后，临界振荡与整定响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的比例或 PID 过程命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。比例或 PID 过程命令与临界振荡与整定响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，临界振荡与整定响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

临界振荡与整定响应

### 执行器

比例或 PID 过程命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s+1)(s+2)]，其 Ku=6、Pu=4.44288 s；测临界振荡后应用 P/PI/PID 表值。

### 示例数据（JSON）

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
    "input_signal_id": "比例或 PID 过程命令",
    "output_signal_id": "临界振荡与整定响应",
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
    "stability": "令 比例或 PID 过程命令 回到基线，核对 临界振荡与整定响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 临界振荡与整定响应 的首次有效方向与最终方向。",
    "delay": "从记录的 比例或 PID 过程命令 边沿量到 临界振荡与整定响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 比例或 PID 过程命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 78. 换热器反应曲线 Ziegler–Nichols 整定

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是蒸汽阀 P 或 PI 命令，输出是由传感器或同步记录器连续获取的换热器温度与阶跃响应。在多次小幅且可逆的试验中，换热器温度与阶跃响应开始时就沿最终方向变化，不会先向相反方向运动；蒸汽阀 P 或 PI 命令改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把蒸汽阀 P 或 PI 命令恢复到基准值后，换热器温度与阶跃响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的蒸汽阀 P 或 PI 命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。蒸汽阀 P 或 PI 命令与换热器温度与阶跃响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

换热器温度与阶跃响应

### 执行器

蒸汽阀 P 或 PI 命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

取反应曲线 R=1/90 s^-1、L=13 s 与模型 exp(-13s)/(90s+1)；比较 P 6.92、PI 6.22、TI=43.3 s，再减半增益。

### 示例数据（JSON）

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
    "input_signal_id": "蒸汽阀 P 或 PI 命令",
    "output_signal_id": "换热器温度与阶跃响应",
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
    "stability": "令 蒸汽阀 P 或 PI 命令 回到基线，核对 换热器温度与阶跃响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 换热器温度与阶跃响应 的首次有效方向与最终方向。",
    "delay": "从记录的 蒸汽阀 P 或 PI 命令 边沿量到 换热器温度与阶跃响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 蒸汽阀 P 或 PI 命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 79. 换热器极限灵敏度整定

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是蒸汽阀 P 或 PI 命令，输出是由传感器或同步记录器连续获取的换热器温度与振荡。在多次小幅且可逆的试验中，换热器温度与振荡开始时就沿最终方向变化，不会先向相反方向运动；蒸汽阀 P 或 PI 命令改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把蒸汽阀 P 或 PI 命令恢复到基准值后，换热器温度与振荡最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的蒸汽阀 P 或 PI 命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。蒸汽阀 P 或 PI 命令与换热器温度与振荡采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

换热器温度与振荡

### 执行器

蒸汽阀 P 或 PI 命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

取测得 Ku=15.3、Pu=42 s；比较 P kP=7.65 与 PI kP=6.885、TI=35 s，再用半增益重复。

### 示例数据（JSON）

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
    "input_signal_id": "蒸汽阀 P 或 PI 命令",
    "output_signal_id": "换热器温度与振荡",
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
    "stability": "令 蒸汽阀 P 或 PI 命令 回到基线，核对 换热器温度与振荡 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 换热器温度与振荡 的首次有效方向与最终方向。",
    "delay": "从记录的 蒸汽阀 P 或 PI 命令 边沿量到 换热器温度与振荡 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 蒸汽阀 P 或 PI 命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 80. 直流电机直流增益逆前馈

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是由反馈和前馈共同形成的电枢电压，输出是由传感器或同步记录器连续获取的电机转速、跟踪误差与扰动响应。在多次小幅且可逆的试验中，电机转速开始时就沿最终方向变化，不会先向相反方向运动；由反馈和前馈共同形成的电枢电压改变后，电机转速在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把由反馈和前馈共同形成的电枢电压恢复到基准值后，电机转速最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的由反馈和前馈共同形成的电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。由反馈和前馈共同形成的电枢电压与电机转速、跟踪误差与扰动响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机转速的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机转速、跟踪误差与扰动响应

### 执行器

由反馈和前馈共同形成的电枢电压

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/(s^2+1.4s+1)、G(0)=1；比较 kP=1.5 与 6，参考前馈 kff=1，并测试可测扰动前馈。

### 示例数据（JSON）

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
    "input_signal_id": "由反馈和前馈共同形成的电枢电压",
    "output_signal_id": "电机转速",
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
    "stability": "令 由反馈和前馈共同形成的电枢电压 回到基线，核对 电机转速、跟踪误差与扰动响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机转速、跟踪误差与扰动响应 的首次有效方向与最终方向。",
    "delay": "从记录的 由反馈和前馈共同形成的电枢电压 边沿量到 电机转速、跟踪误差与扰动响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 由反馈和前馈共同形成的电枢电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 81. 直流电机位置环根轨迹

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是电机电枢电压，输出是由传感器或同步记录器连续获取的电机位置与跟踪响应。在多次小幅且可逆的试验中，电机位置与跟踪响应开始时就沿最终方向变化，不会先向相反方向运动；电机电枢电压改变后，电机位置与跟踪响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把电机电枢电压撤回基准值后，电机位置与跟踪响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的电机电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电机电枢电压与电机位置与跟踪响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机位置与跟踪响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机位置与跟踪响应

### 执行器

电机电枢电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s+1)]，扫描 K=0.1、0.25、1、4；单位阶跃以 0.01 s 运行 20 s。

### 示例数据（JSON）

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
    "input_signal_id": "电机电枢电压",
    "output_signal_id": "电机位置与跟踪响应",
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
    "stability": "令 电机电枢电压 回到基线，核对 电机位置与跟踪响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机位置与跟踪响应 的首次有效方向与最终方向。",
    "delay": "从记录的 电机电枢电压 边沿量到 电机位置与跟踪响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 电机电枢电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 82. 以物理阻尼参数为变量的根轨迹

### 控制问题描述

这是一个可连续扫描环路增益并记录闭环极点与响应的反馈系统。控制输入是改变阻尼时的有界模态测试输入，输出是由传感器或同步记录器连续获取的模态响应与衰减包络。在多次小幅且可逆的试验中，模态响应与衰减包络开始时就沿最终方向变化，不会先向相反方向运动；改变阻尼时的有界模态测试输入改变后，模态响应与衰减包络在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把改变阻尼时的有界模态测试输入撤回基准值后，模态响应与衰减包络会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的改变阻尼时的有界模态测试输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。改变阻尼时的有界模态测试输入与模态响应与衰减包络采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，模态响应与衰减包络的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

模态响应与衰减包络

### 执行器

改变阻尼时的有界模态测试输入

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取特征式 s^2+c s+1，扫描物理阻尼 c=0、1、2、4，并记录自由与阶跃响应。

### 示例数据（JSON）

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
    "input_signal_id": "改变阻尼时的有界模态测试输入",
    "output_signal_id": "模态响应与衰减包络",
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
    "stability": "令 改变阻尼时的有界模态测试输入 回到基线，核对 模态响应与衰减包络 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 模态响应与衰减包络 的首次有效方向与最终方向。",
    "delay": "从记录的 改变阻尼时的有界模态测试输入 边沿量到 模态响应与衰减包络 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 改变阻尼时的有界模态测试输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 83. Evans 规则构造高阶根轨迹

### 控制问题描述

这是一个可连续扫描环路增益并记录闭环极点与响应的反馈系统。控制输入是环路强度扫描中的有界命令，输出是由传感器或同步记录器连续获取的受控输出与瞬态响应。在多次小幅且可逆的试验中，受控输出与瞬态响应开始时就沿最终方向变化，不会先向相反方向运动；环路强度扫描中的有界命令改变后，受控输出与瞬态响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把环路强度扫描中的有界命令撤回基准值后，受控输出与瞬态响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的环路强度扫描中的有界命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。环路强度扫描中的有界命令与受控输出与瞬态响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，受控输出与瞬态响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

受控输出与瞬态响应

### 执行器

环路强度扫描中的有界命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 L=1/[s((s+4)^2+16)]，在 K=10、32、65、100 附近扫描，以 0.01 s 运行 30 s。

### 示例数据（JSON）

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
    "input_signal_id": "环路强度扫描中的有界命令",
    "output_signal_id": "受控输出与瞬态响应",
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
    "stability": "令 环路强度扫描中的有界命令 回到基线，核对 受控输出与瞬态响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出与瞬态响应 的首次有效方向与最终方向。",
    "delay": "从记录的 环路强度扫描中的有界命令 边沿量到 受控输出与瞬态响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 环路强度扫描中的有界命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 84. 用 PD 稳定卫星双积分器

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是PD 机体力矩命令，输出是由传感器或同步记录器连续获取的卫星姿态与角速度。在多次小幅且可逆的试验中，卫星姿态与角速度开始时就沿最终方向变化，不会先向相反方向运动；PD 机体力矩命令改变后，卫星姿态与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把PD 机体力矩命令撤回基准值后，卫星姿态与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的PD 机体力矩命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。PD 机体力矩命令与卫星姿态与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，卫星姿态与角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

卫星姿态与角速度

### 执行器

PD 机体力矩命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取卫星 G=1/s^2 与 PD D=K(s+1)；扫描 K=0.25、1、4、9，并给微分加高频滤波。

### 示例数据（JSON）

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
    "input_signal_id": "PD 机体力矩命令",
    "output_signal_id": "卫星姿态与角速度",
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
    "stability": "令 PD 机体力矩命令 回到基线，核对 卫星姿态与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 卫星姿态与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 PD 机体力矩命令 边沿量到 卫星姿态与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 PD 机体力矩命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 85. 有限超前极点对卫星 PD 的影响

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是超前校正后的机体力矩，输出是由传感器或同步记录器连续获取的卫星姿态与角速度。在多次小幅且可逆的试验中，卫星姿态与角速度开始时就沿最终方向变化，不会先向相反方向运动；超前校正后的机体力矩改变后，卫星姿态与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把超前校正后的机体力矩撤回基准值后，卫星姿态与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的超前校正后的机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。超前校正后的机体力矩与卫星姿态与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，卫星姿态与角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

卫星姿态与角速度

### 执行器

超前校正后的机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取 L=(s+1)/[s^2(s+p)]，比较 p=4、9、12 及 K=1、5、20，以 0.005 s 采样。

### 示例数据（JSON）

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
    "input_signal_id": "超前校正后的机体力矩",
    "output_signal_id": "卫星姿态与角速度",
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
    "stability": "令 超前校正后的机体力矩 回到基线，核对 卫星姿态与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 卫星姿态与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 超前校正后的机体力矩 边沿量到 卫星姿态与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 超前校正后的机体力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 86. 共址柔性卫星的模态阻尼

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是共址机体力矩，输出是由传感器或同步记录器连续获取的共址姿态与柔性挠度。在多次小幅且可逆的试验中，共址姿态与柔性挠度开始时就沿最终方向变化，不会先向相反方向运动；共址机体力矩改变后，共址姿态与柔性挠度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把共址机体力矩撤回基准值后，共址姿态与柔性挠度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的共址机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。共址机体力矩与共址姿态与柔性挠度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

共址姿态与柔性挠度

### 执行器

共址机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

使用共址柔性卫星 G=[(s+0.1)^2+36]/{s^2[(s+0.1)^2+43.56]} 与 lead K(s+1)/(s+12)，扫描 K。

### 示例数据（JSON）

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
    "input_signal_id": "共址机体力矩",
    "output_signal_id": "共址姿态与柔性挠度",
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
    "stability": "令 共址机体力矩 回到基线，核对 共址姿态与柔性挠度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 共址姿态与柔性挠度 的首次有效方向与最终方向。",
    "delay": "从记录的 共址机体力矩 边沿量到 共址姿态与柔性挠度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 共址机体力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 87. 非共址柔性卫星的溢出失稳

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是主刚体力矩，输出是由传感器或同步记录器连续获取的远端姿态与柔性挠度。在多次小幅且可逆的试验中，远端姿态与柔性挠度开始时就沿最终方向变化，不会先向相反方向运动；主刚体力矩改变后，远端姿态与柔性挠度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把主刚体力矩撤回基准值后，远端姿态与柔性挠度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的主刚体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。主刚体力矩与远端姿态与柔性挠度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

远端姿态与柔性挠度

### 执行器

主刚体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

使用非共址 G=1/{s^2[(s+0.1)^2+43.56]} 与 lead K(s+1)/(s+12)；K 从 1e-4 起扫并在失稳时停止。

### 示例数据（JSON）

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
    "input_signal_id": "主刚体力矩",
    "output_signal_id": "远端姿态与柔性挠度",
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
    "stability": "令 主刚体力矩 回到基线，核对 远端姿态与柔性挠度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 远端姿态与柔性挠度 的首次有效方向与最终方向。",
    "delay": "从记录的 主刚体力矩 边沿量到 远端姿态与柔性挠度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 主刚体力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 88. 四阶根轨迹的复重根

### 控制问题描述

这是一个可连续扫描环路增益并记录闭环极点与响应的反馈系统。控制输入是环路强度扫描中的有界命令，输出是由传感器或同步记录器连续获取的重根条件附近的闭环输出。在多次小幅且可逆的试验中，重根条件附近的闭环输出开始时就沿最终方向变化，不会先向相反方向运动；环路强度扫描中的有界命令改变后，重根条件附近的闭环输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把环路强度扫描中的有界命令撤回基准值后，重根条件附近的闭环输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的环路强度扫描中的有界命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。环路强度扫描中的有界命令与重根条件附近的闭环输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，重根条件附近的闭环输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

重根条件附近的闭环输出

### 执行器

环路强度扫描中的有界命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 L=1/[s(s+2)((s+1)^2+4)]，让 K 穿过 6.25，以 0.005 s 运行 20 s。

### 示例数据（JSON）

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
    "input_signal_id": "环路强度扫描中的有界命令",
    "output_signal_id": "重根条件附近的闭环输出",
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
    "stability": "令 环路强度扫描中的有界命令 回到基线，核对 重根条件附近的闭环输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 重根条件附近的闭环输出 的首次有效方向与最终方向。",
    "delay": "从记录的 环路强度扫描中的有界命令 边沿量到 重根条件附近的闭环输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 环路强度扫描中的有界命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 89. 满足上升时间与超调的超前校正

### 控制问题描述

这是一个通过超前校正器重塑主导暂态运动的电机位置伺服装置。控制输入是超前校正后的伺服命令，输出是由传感器或同步记录器连续获取的伺服位置、跟踪误差与控制作用。在多次小幅且可逆的试验中，伺服位置开始时就沿最终方向变化，不会先向相反方向运动；超前校正后的伺服命令改变后，伺服位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把超前校正后的伺服命令撤回基准值后，伺服位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的超前校正后的伺服命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。超前校正后的伺服命令与伺服位置、跟踪误差与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，伺服位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

伺服位置、跟踪误差与控制作用

### 执行器

超前校正后的伺服命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s+1)] 与 lead D=91(s+2)/(s+13)；±1 阶跃以 0.002 s 运行 5 s。

### 示例数据（JSON）

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
    "input_signal_id": "超前校正后的伺服命令",
    "output_signal_id": "伺服位置",
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
    "stability": "令 超前校正后的伺服命令 回到基线，核对 伺服位置、跟踪误差与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 伺服位置、跟踪误差与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 超前校正后的伺服命令 边沿量到 伺服位置、跟踪误差与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 超前校正后的伺服命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 90. 用滞后校正提高速度常数

### 控制问题描述

这是一个采用超前滞后校正提高跟踪能力、同时避免主导运动过度偏移的电机位置伺服装置。控制输入是超前滞后伺服命令，输出是由传感器或同步记录器连续获取的伺服位置、跟踪误差与控制作用。在多次小幅且可逆的试验中，伺服位置开始时就沿最终方向变化，不会先向相反方向运动；超前滞后伺服命令改变后，伺服位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把超前滞后伺服命令撤回基准值后，伺服位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的超前滞后伺服命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。超前滞后伺服命令与伺服位置、跟踪误差与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，伺服位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

伺服位置、跟踪误差与控制作用

### 执行器

超前滞后伺服命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

在 K=91 的 lead 设计后加入 lag (s+0.05)/(s+0.01)；阶跃与斜坡运行 300 s。

### 示例数据（JSON）

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
    "input_signal_id": "超前滞后伺服命令",
    "output_signal_id": "伺服位置",
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
    "stability": "令 超前滞后伺服命令 回到基线，核对 伺服位置、跟踪误差与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 伺服位置、跟踪误差与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 超前滞后伺服命令 边沿量到 伺服位置、跟踪误差与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 超前滞后伺服命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 91. 用陷波校正柔性共振

### 控制问题描述

这是一个执行器会激发轻阻尼结构模态、并在命令通道中加入陷波器的柔性运动装置。控制输入是陷波滤波后的执行器命令，输出是由传感器或同步记录器连续获取的标称输出与柔性位移。在多次小幅且可逆的试验中，标称输出与柔性位移开始时就沿最终方向变化，不会先向相反方向运动；陷波滤波后的执行器命令改变后，标称输出与柔性位移在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把陷波滤波后的执行器命令撤回基准值后，标称输出与柔性位移会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的陷波滤波后的执行器命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。陷波滤波后的执行器命令与标称输出与柔性位移采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

标称输出与柔性位移

### 执行器

陷波滤波后的执行器命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用柔性对象 2500/[s(s+1)(s^2+s+2500)]、K=91 lead-lag 与陷波 (s^2+0.8s+3600)/(s+60)^2；柔性频率扫描 ±10%。

### 示例数据（JSON）

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
    "input_signal_id": "陷波滤波后的执行器命令",
    "output_signal_id": "标称输出与柔性位移",
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
    "stability": "令 陷波滤波后的执行器命令 回到基线，核对 标称输出与柔性位移 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 标称输出与柔性位移 的首次有效方向与最终方向。",
    "delay": "从记录的 陷波滤波后的执行器命令 边沿量到 标称输出与柔性位移 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 陷波滤波后的执行器命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 92. 运放实现超前网络

### 控制问题描述

这是一个由电阻、电容、电感或运算放大器构成的电信号处理网络。控制输入是输入误差电压，输出是由传感器或同步记录器连续获取的超前网络输出电压。在多次小幅且可逆的试验中，超前网络输出电压开始时就沿最终方向变化，不会先向相反方向运动；输入误差电压改变后，超前网络输出电压在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把输入误差电压恢复到基准值后，超前网络输出电压最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的输入误差电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。输入误差电压与超前网络输出电压采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，超前网络输出电压的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

超前网络输出电压

### 执行器

输入误差电压

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

用 C=10 uF、R1=50 kohm、R2=200 kohm、Rf=250 kohm 实现 -5(s+2)/(s+10)，并扫描元件 ±10%。

### 示例数据（JSON）

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
    "input_signal_id": "输入误差电压",
    "output_signal_id": "超前网络输出电压",
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
    "stability": "令 输入误差电压 回到基线，核对 超前网络输出电压 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 超前网络输出电压 的首次有效方向与最终方向。",
    "delay": "从记录的 输入误差电压 边沿量到 超前网络输出电压 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 输入误差电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 93. 四旋翼俯仰轴超前校正

### 控制问题描述

这是一个由机体、旋翼和惯性运动状态组成的多旋翼飞行器控制系统。控制输入是俯仰旋翼力矩命令，输出是由传感器或同步记录器连续获取的四旋翼俯仰角与角速度。在多次小幅且可逆的试验中，四旋翼俯仰角与角速度开始时就沿最终方向变化，不会先向相反方向运动；俯仰旋翼力矩命令改变后，四旋翼俯仰角与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把俯仰旋翼力矩命令撤回基准值后，四旋翼俯仰角与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的俯仰旋翼力矩命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。俯仰旋翼力矩命令与四旋翼俯仰角与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

四旋翼俯仰角与角速度

### 执行器

俯仰旋翼力矩命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取四旋翼俯仰对象 1/[s^2(s+2)] 与 lead 30(s+0.5)/(s+15)；±0.1 rad 命令以 0.002 s 运行 15 s。

### 示例数据（JSON）

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
    "input_signal_id": "俯仰旋翼力矩命令",
    "output_signal_id": "四旋翼俯仰角与角速度",
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
    "stability": "令 俯仰旋翼力矩命令 回到基线，核对 四旋翼俯仰角与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 四旋翼俯仰角与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 俯仰旋翼力矩命令 边沿量到 四旋翼俯仰角与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 俯仰旋翼力矩命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 94. 小型飞机俯仰自动驾驶与积分配平

### 控制问题描述

这是一个由气动力、舵面执行机构和机载运动传感器组成的飞机飞行控制系统。控制输入是升降舵与配平舵命令，输出是由传感器或同步记录器连续获取的俯仰姿态、升降舵与配平舵偏角。在多次小幅且可逆的试验中，俯仰姿态开始时就沿最终方向变化，不会先向相反方向运动；升降舵与配平舵命令改变后，俯仰姿态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把升降舵与配平舵命令恢复到基准值后，俯仰姿态最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的升降舵与配平舵命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。升降舵与配平舵命令与俯仰姿态、升降舵与配平舵偏角采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

俯仰姿态、升降舵与配平舵偏角

### 执行器

升降舵与配平舵命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取飞机对象 160(s+2.5)(s+0.7)/[(s^2+5s+40)(s^2+0.03s+0.06)]，lead K=1.5,z=3,p=20，配平积分 KI=0.15。

### 示例数据（JSON）

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
    "input_signal_id": "升降舵与配平舵命令",
    "output_signal_id": "俯仰姿态",
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
    "stability": "令 升降舵与配平舵命令 回到基线，核对 俯仰姿态、升降舵与配平舵偏角 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 俯仰姿态、升降舵与配平舵偏角 的首次有效方向与最终方向。",
    "delay": "从记录的 升降舵与配平舵命令 边沿量到 俯仰姿态、升降舵与配平舵偏角 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 升降舵与配平舵命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 95. 非最小相位飞机高度的零度根轨迹

### 控制问题描述

这是一个由气动力、舵面执行机构和机载运动传感器组成的飞机飞行控制系统。控制输入是升降舵命令，输出是由传感器或同步记录器连续获取的飞机高度响应。在多次小幅且可逆的试验中，飞机高度响应开始时会先沿不利或相反方向运动，随后才转向；升降舵命令改变后，飞机高度响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把升降舵命令撤回基准值后，飞机高度响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的升降舵命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。升降舵命令与飞机高度响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

飞机高度响应

### 执行器

升降舵命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取飞机高度对象 (6-s)/[s(s^2+4s+13)]，用对应负根轨迹扫描正物理增益，并施加 ±1° 脉冲。

### 示例数据（JSON）

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
    "input_signal_id": "升降舵命令",
    "output_signal_id": "飞机高度响应",
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
    "stability": "令 升降舵命令 回到基线，核对 飞机高度响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 飞机高度响应 的首次有效方向与最终方向。",
    "delay": "从记录的 升降舵命令 边沿量到 飞机高度响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 升降舵命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 96. 测速与放大器两参数的逐次根轨迹

### 控制问题描述

这是一个可连续扫描环路增益并记录闭环极点与响应的反馈系统。控制输入是测速反馈下的伺服放大器电压，输出是由传感器或同步记录器连续获取的伺服机构位置与速度响应。在多次小幅且可逆的试验中，伺服机构位置与速度响应开始时就沿最终方向变化，不会先向相反方向运动；测速反馈下的伺服放大器电压改变后，伺服机构位置与速度响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把测速反馈下的伺服放大器电压撤回基准值后，伺服机构位置与速度响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的测速反馈下的伺服放大器电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。测速反馈下的伺服放大器电压与伺服机构位置与速度响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，伺服机构位置与速度响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

伺服机构位置与速度响应

### 执行器

测速反馈下的伺服放大器电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用 s^2+s+KA+KT s=0；先取 KA=4，再取 KT=1，并在 ±10% 参数下重复。

### 示例数据（JSON）

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
    "input_signal_id": "测速反馈下的伺服放大器电压",
    "output_signal_id": "伺服机构位置与速度响应",
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
    "stability": "令 测速反馈下的伺服放大器电压 回到基线，核对 伺服机构位置与速度响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 伺服机构位置与速度响应 的首次有效方向与最终方向。",
    "delay": "从记录的 测速反馈下的伺服放大器电压 边沿量到 伺服机构位置与速度响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 测速反馈下的伺服放大器电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 97. 四旋翼内姿态外位置级联

### 控制问题描述

这是一个由机体、旋翼和惯性运动状态组成的多旋翼飞行器控制系统。控制输入是外层位置命令与内层旋翼力矩命令，输出是由传感器或同步记录器连续获取的水平位置、俯仰姿态与角速度。在多次小幅且可逆的试验中，水平位置开始时就沿最终方向变化，不会先向相反方向运动；外层位置命令与内层旋翼力矩命令改变后，水平位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把外层位置命令与内层旋翼力矩命令撤回基准值后，水平位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的外层位置命令与内层旋翼力矩命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。外层位置命令与内层旋翼力矩命令与水平位置、俯仰姿态与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；外层运动只能通过一个单独稳定的内环产生，内外环具有不同的时间尺度。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

水平位置、俯仰姿态与角速度

### 执行器

外层位置命令与内层旋翼力矩命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
测试外环命令时关闭内层稳定通道

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

内俯仰对象 1/[s^2(s+2)] 配 30(s+0.5)/(s+15)，外位置对象 -32.2/s^2 配 0.081(s+0.1)/(s+10)。

### 示例数据（JSON）

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
    "input_signal_id": "外层位置命令与内层旋翼力矩命令",
    "output_signal_id": "水平位置",
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
    "stability": "令 外层位置命令与内层旋翼力矩命令 回到基线，核对 水平位置、俯仰姿态与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 水平位置、俯仰姿态与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 外层位置命令与内层旋翼力矩命令 边沿量到 水平位置、俯仰姿态与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 外层位置命令与内层旋翼力矩命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 98. 数控机床伺服的超前设计

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是超前校正后的伺服命令，输出是由传感器或同步记录器连续获取的数控机床位置、跟踪误差与控制作用。在多次小幅且可逆的试验中，数控机床位置开始时就沿最终方向变化，不会先向相反方向运动；超前校正后的伺服命令改变后，数控机床位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把超前校正后的伺服命令撤回基准值后，数控机床位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的超前校正后的伺服命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。超前校正后的伺服命令与数控机床位置、跟踪误差与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

数控机床位置、跟踪误差与控制作用

### 执行器

超前校正后的伺服命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取机床 G=1/[s(s+1)] 与 lead 10(s+1)/(s+2)；测试 ±1 位置阶跃及极点 ±10% 变化。

### 示例数据（JSON）

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
    "input_signal_id": "超前校正后的伺服命令",
    "output_signal_id": "数控机床位置",
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
    "stability": "令 超前校正后的伺服命令 回到基线，核对 数控机床位置、跟踪误差与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 数控机床位置、跟踪误差与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 超前校正后的伺服命令 边沿量到 数控机床位置、跟踪误差与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 超前校正后的伺服命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 99. 磁悬浮线性模型与根轨迹稳定

### 控制问题描述

这是一个由电磁铁吸引钢球并用位置传感器测量气隙的磁悬浮装置。控制输入是电磁铁电流命令，输出是由传感器或同步记录器连续获取的小球位置、传感电压与线圈电流。在多次小幅且可逆的试验中，小球位置开始时就沿最终方向变化，不会先向相反方向运动；电磁铁电流命令改变后，小球位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把电磁铁电流命令撤回基准值，小球位置的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。分别施加小幅正向和反向的电磁铁电流命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电磁铁电流命令与小球位置、传感电压与线圈电流采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

小球位置、传感电压与线圈电流

### 执行器

电磁铁电流命令

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 m=0.02 kg、g=9.8、e=100x、f=0.5i+20x，并用 K=1 的 lead (s+10)/(s+20)，以 0.001 s 采样。

### 示例数据（JSON）

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
    "input_signal_id": "电磁铁电流命令",
    "output_signal_id": "小球位置",
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
    "stability": "令 电磁铁电流命令 回到基线，核对 小球位置、传感电压与线圈电流 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 小球位置、传感电压与线圈电流 的首次有效方向与最终方向。",
    "delay": "从记录的 电磁铁电流命令 边沿量到 小球位置、传感电压与线圈电流 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 电磁铁电流命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 100. Tampa 舰艏向与偏航率反馈

### 控制问题描述

这是一个由船体偏航运动、舵机和航向传感器组成的水面航行器控制系统。控制输入是舵命令与给定风阵输入，输出是由传感器或同步记录器连续获取的舰艏向、偏航率、舵角与风响应。在多次小幅且可逆的试验中，舰艏向开始时就沿最终方向变化，不会先向相反方向运动；舵命令与给定风阵输入改变后，舰艏向在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把舵命令与给定风阵输入撤回基准值后，舰艏向会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的舵命令与给定风阵输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。舵命令与给定风阵输入与舰艏向、偏航率、舵角与风响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

舰艏向、偏航率、舵角与风响应

### 执行器

舵命令与给定风阵输入

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用 Tampa 舵角对象 -0.0184(s+0.0068)/[s(s+0.2647)(s+0.0063)]；吸收符号后取 Kpsi=0.1、Kr=1、KI=0.0001，并执行舵角限幅。

### 示例数据（JSON）

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
    "input_signal_id": "舵命令与给定风阵输入",
    "output_signal_id": "舰艏向",
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
    "stability": "令 舵命令与给定风阵输入 回到基线，核对 舰艏向、偏航率、舵角与风响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 舰艏向、偏航率、舵角与风响应 的首次有效方向与最终方向。",
    "delay": "从记录的 舵命令与给定风阵输入 边沿量到 舰艏向、偏航率、舵角与风响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 舵命令与给定风阵输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 101. 电压驱动电容的频率响应

### 控制问题描述

这是一个由电阻、电容、电感或运算放大器构成的电信号处理网络。控制输入是正弦电压，输出是由传感器或同步记录器连续获取的电容电流幅值与相位。在多次小幅且可逆的试验中，电容电流幅值与相位开始时就沿最终方向变化，不会先向相反方向运动；正弦电压改变后，电容电流幅值与相位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把正弦电压恢复到基准值后，电容电流幅值与相位最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的正弦电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。正弦电压与电容电流幅值与相位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电容电流幅值与相位的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电容电流幅值与相位

### 执行器

正弦电压

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 C=100 uF，输入 1 V、1/10/100/1000 rad/s 正弦电压；每周期至少采样 50 点的电流。

### 示例数据（JSON）

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
    "input_signal_id": "正弦电压",
    "output_signal_id": "电容电流幅值与相位",
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
    "stability": "令 正弦电压 回到基线，核对 电容电流幅值与相位 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电容电流幅值与相位 的首次有效方向与最终方向。",
    "delay": "从记录的 正弦电压 边沿量到 电容电流幅值与相位 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 正弦电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 102. 一阶超前环节的幅相特性

### 控制问题描述

这是一个由电阻和电容构成、能在有限频段内产生相位超前的一阶校正网络。控制输入是正弦误差信号，输出是由传感器或同步记录器连续获取的超前校正器幅值与相位。在多次小幅且可逆的试验中，超前校正器幅值与相位开始时就沿最终方向变化，不会先向相反方向运动；正弦误差信号改变后，超前校正器幅值与相位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把正弦误差信号恢复到基准值后，超前校正器幅值与相位最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的正弦误差信号变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。正弦误差信号与超前校正器幅值与相位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，超前校正器幅值与相位的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

超前校正器幅值与相位

### 执行器

正弦误差信号

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用 lead D=(s+1)/(0.1s+1)，扫描 0.1–100 rad/s，并核对 1、sqrt(10)、10 rad/s 的幅相。

### 示例数据（JSON）

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
    "input_signal_id": "正弦误差信号",
    "output_signal_id": "超前校正器幅值与相位",
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
    "stability": "令 正弦误差信号 回到基线，核对 超前校正器幅值与相位 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 超前校正器幅值与相位 的首次有效方向与最终方向。",
    "delay": "从记录的 正弦误差信号 边沿量到 超前校正器幅值与相位 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 正弦误差信号 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 103. 实极点零点的渐近 Bode 图

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是正弦对象输入，输出是由传感器或同步记录器连续获取的开环幅值与相位。在多次小幅且可逆的试验中，开环幅值与相位开始时就沿最终方向变化，不会先向相反方向运动；正弦对象输入改变后，开环幅值与相位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把正弦对象输入撤回基准值后，开环幅值与相位会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的正弦对象输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。正弦对象输入与开环幅值与相位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，开环幅值与相位的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

开环幅值与相位

### 执行器

正弦对象输入

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 L=2000(s+0.5)/[s(s+10)(s+50)]，在 0.01–1000 rad/s 对数网格计算。

### 示例数据（JSON）

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
    "input_signal_id": "正弦对象输入",
    "output_signal_id": "开环幅值与相位",
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
    "stability": "令 正弦对象输入 回到基线，核对 开环幅值与相位 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 开环幅值与相位 的首次有效方向与最终方向。",
    "delay": "从记录的 正弦对象输入 边沿量到 开环幅值与相位 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 正弦对象输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 104. 复极点零点与柔性卫星 Bode 图

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是正弦作用力，输出是由传感器或同步记录器连续获取的对象位移幅值与相位。在多次小幅且可逆的试验中，对象位移幅值与相位开始时就沿最终方向变化，不会先向相反方向运动；正弦作用力改变后，对象位移幅值与相位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把正弦作用力撤回基准值后，对象位移幅值与相位会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的正弦作用力变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。正弦作用力与对象位移幅值与相位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，对象位移幅值与相位的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

对象位移幅值与相位

### 执行器

正弦作用力

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

比较 L1=10/[s(s^2+0.4s+4)] 与柔性 doublet 0.01(s^2+0.01s+1)/{s^2(s^2/4+0.01s+1)}。

### 示例数据（JSON）

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
    "input_signal_id": "正弦作用力",
    "output_signal_id": "对象位移幅值与相位",
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
    "stability": "令 正弦作用力 回到基线，核对 对象位移幅值与相位 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 对象位移幅值与相位 的首次有效方向与最终方向。",
    "delay": "从记录的 正弦作用力 边沿量到 对象位移幅值与相位 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 正弦作用力 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 105. 由低频 Bode 图识别系统型别与误差常数

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是单位斜坡参考，输出是由传感器或同步记录器连续获取的跟踪误差与受控输出。在多次小幅且可逆的试验中，跟踪误差与受控输出开始时就沿最终方向变化，不会先向相反方向运动；单位斜坡参考改变后，跟踪误差与受控输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把单位斜坡参考撤回基准值后，跟踪误差与受控输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的单位斜坡参考变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。单位斜坡参考与跟踪误差与受控输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，跟踪误差与受控输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

跟踪误差与受控输出

### 执行器

单位斜坡参考

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 L=10/[s(s+1)]，单位斜坡以 0.01 s 运行 50 s，并拟合末段误差。

### 示例数据（JSON）

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
    "input_signal_id": "单位斜坡参考",
    "output_signal_id": "跟踪误差与受控输出",
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
    "stability": "令 单位斜坡参考 回到基线，核对 跟踪误差与受控输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 跟踪误差与受控输出 的首次有效方向与最终方向。",
    "delay": "从记录的 单位斜坡参考 边沿量到 跟踪误差与受控输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 单位斜坡参考 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 106. 二阶环路的 Nyquist 全正增益稳定性

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是增益扫描中的有界环路命令，输出是由传感器或同步记录器连续获取的闭环输出与频率响应。在多次小幅且可逆的试验中，闭环输出与频率响应开始时就沿最终方向变化，不会先向相反方向运动；增益扫描中的有界环路命令改变后，闭环输出与频率响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把增益扫描中的有界环路命令恢复到基准值后，闭环输出与频率响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的增益扫描中的有界环路命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。增益扫描中的有界环路命令与闭环输出与频率响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，闭环输出与频率响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

闭环输出与频率响应

### 执行器

增益扫描中的有界环路命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/(s+1)^2，扫描 K=0.1、1、10、100，并测试负增益 -0.5、-1、-2。

### 示例数据（JSON）

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
    "input_signal_id": "增益扫描中的有界环路命令",
    "output_signal_id": "闭环输出与频率响应",
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
    "stability": "令 增益扫描中的有界环路命令 回到基线，核对 闭环输出与频率响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 闭环输出与频率响应 的首次有效方向与最终方向。",
    "delay": "从记录的 增益扫描中的有界环路命令 边沿量到 闭环输出与频率响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 增益扫描中的有界环路命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 107. 含原点极点的三阶 Nyquist 判稳

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是增益扫描中的有界环路命令，输出是由传感器或同步记录器连续获取的闭环输出与频率响应。在多次小幅且可逆的试验中，闭环输出与频率响应开始时就沿最终方向变化，不会先向相反方向运动；增益扫描中的有界环路命令改变后，闭环输出与频率响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把增益扫描中的有界环路命令撤回基准值后，闭环输出与频率响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的增益扫描中的有界环路命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。增益扫描中的有界环路命令与闭环输出与频率响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，闭环输出与频率响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

闭环输出与频率响应

### 执行器

增益扫描中的有界环路命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s+1)^2]，扫描 K=0.5、1、2、3，并在原点使用 Nyquist 凹入轮廓。

### 示例数据（JSON）

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
    "input_signal_id": "增益扫描中的有界环路命令",
    "output_signal_id": "闭环输出与频率响应",
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
    "stability": "令 增益扫描中的有界环路命令 回到基线，核对 闭环输出与频率响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 闭环输出与频率响应 的首次有效方向与最终方向。",
    "delay": "从记录的 增益扫描中的有界环路命令 边沿量到 闭环输出与频率响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 增益扫描中的有界环路命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 108. 两个特殊 Nyquist 环路的稳定性

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是两个环路测试使用的有界命令，输出是由传感器或同步记录器连续获取的两个算例的闭环输出与频率响应。在多次小幅且可逆的试验中，两个算例的闭环输出与频率响应开始时就沿最终方向变化，不会先向相反方向运动；两个环路测试使用的有界命令改变后，两个算例的闭环输出与频率响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把两个环路测试使用的有界命令撤回基准值，两个算例的闭环输出与频率响应的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。分别施加小幅正向和反向的两个环路测试使用的有界命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。两个环路测试使用的有界命令与两个算例的闭环输出与频率响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，两个算例的闭环输出与频率响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

两个算例的闭环输出与频率响应

### 执行器

两个环路测试使用的有界命令

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

对 G1=(s+1)/[s(s/10-1)] 取 K=0.5、1、2；另对 G2=(s^2+3)/(s+1)^2 测试正增益。

### 示例数据（JSON）

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
    "input_signal_id": "两个环路测试使用的有界命令",
    "output_signal_id": "两个算例的闭环输出与频率响应",
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
    "stability": "令 两个环路测试使用的有界命令 回到基线，核对 两个算例的闭环输出与频率响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 两个算例的闭环输出与频率响应 的首次有效方向与最终方向。",
    "delay": "从记录的 两个环路测试使用的有界命令 边沿量到 两个算例的闭环输出与频率响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 两个环路测试使用的有界命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 109. 条件稳定与误导性增益裕度

### 控制问题描述

这是一个闭环稳定性会随环路增益落入不同区间而改变的反馈系统。控制输入是增益扫描中的有界环路命令，输出是由传感器或同步记录器连续获取的闭环输出与频率响应。在多次小幅且可逆的试验中，闭环输出与频率响应开始时就沿最终方向变化，不会先向相反方向运动；增益扫描中的有界环路命令改变后，闭环输出与频率响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把增益扫描中的有界环路命令撤回基准值后，闭环输出与频率响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的增益扫描中的有界环路命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。增益扫描中的有界环路命令与闭环输出与频率响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，闭环输出与频率响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

闭环输出与频率响应

### 执行器

增益扫描中的有界环路命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 L=K(s+10)^2/s^3，比较 K=4.9、5、7、10；K=7 时测量增益上下两个方向的裕度。

### 示例数据（JSON）

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
    "input_signal_id": "增益扫描中的有界环路命令",
    "output_signal_id": "闭环输出与频率响应",
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
    "stability": "令 增益扫描中的有界环路命令 回到基线，核对 闭环输出与频率响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 闭环输出与频率响应 的首次有效方向与最终方向。",
    "delay": "从记录的 增益扫描中的有界环路命令 边沿量到 闭环输出与频率响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 增益扫描中的有界环路命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 110. 多重交叉频率的稳定裕度解释

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是有界正弦环路激励，输出是由传感器或同步记录器连续获取的闭环输出与开环频率响应。在多次小幅且可逆的试验中，闭环输出与开环频率响应开始时就沿最终方向变化，不会先向相反方向运动；有界正弦环路激励改变后，闭环输出与开环频率响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把有界正弦环路激励撤回基准值后，闭环输出与开环频率响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的有界正弦环路激励变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界正弦环路激励与闭环输出与开环频率响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，闭环输出与开环频率响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

闭环输出与开环频率响应

### 执行器

有界正弦环路激励

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用 G=85(s+1)(s^2+2s+43.25)/{s^2(s^2+2s+82)(s^2+2s+101)}，逐一解析所有单位增益交叉。

### 示例数据（JSON）

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
    "input_signal_id": "有界正弦环路激励",
    "output_signal_id": "闭环输出与开环频率响应",
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
    "stability": "令 有界正弦环路激励 回到基线，核对 闭环输出与开环频率响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 闭环输出与开环频率响应 的首次有效方向与最终方向。",
    "delay": "从记录的 有界正弦环路激励 边沿量到 闭环输出与开环频率响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界正弦环路激励 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 111. 用增益相位斜率准则设计航天器 PD

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是机体力矩命令，输出是由传感器或同步记录器连续获取的姿态、角速度与控制作用。在多次小幅且可逆的试验中，姿态开始时就沿最终方向变化，不会先向相反方向运动；机体力矩命令改变后，姿态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把机体力矩命令撤回基准值后，姿态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的机体力矩命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。机体力矩命令与姿态、角速度与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，姿态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

姿态、角速度与控制作用

### 执行器

机体力矩命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取航天器 G=1/s^2 与 KD=0.01(20s+1)；±0.1 rad 阶跃以 0.05 s 运行 200 s。

### 示例数据（JSON）

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
    "input_signal_id": "机体力矩命令",
    "output_signal_id": "姿态",
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
    "stability": "令 机体力矩命令 回到基线，核对 姿态、角速度与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 姿态、角速度与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 机体力矩命令 边沿量到 姿态、角速度与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 机体力矩命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 112. 交叉频率相位裕度与闭环带宽

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是有界正弦指令扫描，输出是由传感器或同步记录器连续获取的闭环输出与带宽响应。在多次小幅且可逆的试验中，闭环输出与带宽响应开始时就沿最终方向变化，不会先向相反方向运动；有界正弦指令扫描改变后，闭环输出与带宽响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界正弦指令扫描恢复到基准值后，闭环输出与带宽响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的有界正弦指令扫描变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界正弦指令扫描与闭环输出与带宽响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，闭环输出与带宽响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

闭环输出与带宽响应

### 执行器

有界正弦指令扫描

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取代表环路 L=1/[s(s+1)]，计算精确 T=L/(1+L)，比较交叉频率、相位裕度、共振与 -3 dB 带宽。

### 示例数据（JSON）

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
    "input_signal_id": "有界正弦指令扫描",
    "output_signal_id": "闭环输出与带宽响应",
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
    "stability": "令 有界正弦指令扫描 回到基线，核对 闭环输出与带宽响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 闭环输出与带宽响应 的首次有效方向与最终方向。",
    "delay": "从记录的 有界正弦指令扫描 边沿量到 闭环输出与带宽响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界正弦指令扫描 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 113. 直流电机位置环超前设计

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是超前校正电机命令，输出是由传感器或同步记录器连续获取的电机位置、误差与阶跃响应。在多次小幅且可逆的试验中，电机位置开始时就沿最终方向变化，不会先向相反方向运动；超前校正电机命令改变后，电机位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把超前校正电机命令撤回基准值后，电机位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的超前校正电机命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。超前校正电机命令与电机位置、误差与阶跃响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机位置、误差与阶跃响应

### 执行器

超前校正电机命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取电机 G=1/[s(s+1)] 与 lead D=10(s/2+1)/(s/10+1)；测试斜坡与阶跃命令。

### 示例数据（JSON）

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
    "input_signal_id": "超前校正电机命令",
    "output_signal_id": "电机位置",
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
    "stability": "令 超前校正电机命令 回到基线，核对 电机位置、误差与阶跃响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机位置、误差与阶跃响应 的首次有效方向与最终方向。",
    "delay": "从记录的 超前校正电机命令 边沿量到 电机位置、误差与阶跃响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 超前校正电机命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 114. 热过程单超前与伺服双超前设计

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是单段或双段超前命令，输出是由传感器或同步记录器连续获取的温度或伺服输出。在多次小幅且可逆的试验中，温度或伺服输出开始时就沿最终方向变化，不会先向相反方向运动；单段或双段超前命令改变后，温度或伺服输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把单段或双段超前命令撤回基准值后，温度或伺服输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的单段或双段超前命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。单段或双段超前命令与温度或伺服输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，温度或伺服输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

温度或伺服输出

### 执行器

单段或双段超前命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

热对象取 K=9 与 lead (s/1.5+1)/(s/15+1)；伺服取双 lead (s/2+1)(s/4+1)/[(s/20+1)(s/40+1)]。

### 示例数据（JSON）

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
    "input_signal_id": "单段或双段超前命令",
    "output_signal_id": "温度或伺服输出",
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
    "stability": "令 单段或双段超前命令 回到基线，核对 温度或伺服输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 温度或伺服输出 的首次有效方向与最终方向。",
    "delay": "从记录的 单段或双段超前命令 边沿量到 温度或伺服输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 单段或双段超前命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 115. 热过程与电机的滞后校正

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是滞后校正命令，输出是由传感器或同步记录器连续获取的热过程或电机响应与慢尾。在多次小幅且可逆的试验中，热过程或电机响应与慢尾开始时就沿最终方向变化，不会先向相反方向运动；滞后校正命令改变后，热过程或电机响应与慢尾在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把滞后校正命令撤回基准值后，热过程或电机响应与慢尾会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的滞后校正命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。滞后校正命令与热过程或电机响应与慢尾采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，热过程或电机响应与慢尾的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

热过程或电机响应与慢尾

### 执行器

滞后校正命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

热对象使用 lag 3(5s+1)/(15s+1)；电机使用 K=10、lag 零点 0.1、极点 0.01 rad/s。

### 示例数据（JSON）

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
    "input_signal_id": "滞后校正命令",
    "output_signal_id": "热过程或电机响应与慢尾",
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
    "stability": "令 滞后校正命令 回到基线，核对 热过程或电机响应与慢尾 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 热过程或电机响应与慢尾 的首次有效方向与最终方向。",
    "delay": "从记录的 滞后校正命令 边沿量到 热过程或电机响应与慢尾 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 滞后校正命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 116. 带传感器滞后的航天器 PID

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是带给定扰动力矩的机体力矩命令，输出是由传感器或同步记录器连续获取的姿态、角速度与扰动响应。在多次小幅且可逆的试验中，姿态开始时就沿最终方向变化，不会先向相反方向运动；带给定扰动力矩的机体力矩命令改变后，姿态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把带给定扰动力矩的机体力矩命令撤回基准值后，姿态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的带给定扰动力矩的机体力矩命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。带给定扰动力矩的机体力矩命令与姿态、角速度与扰动响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，姿态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

姿态、角速度与扰动响应

### 执行器

带给定扰动力矩的机体力矩命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取航天器 G=0.9/s^2、传感器 H=2/(s+2)、PID D=0.05(10s+1)(s+0.005)/s；命令与常值转矩分开测试。

### 示例数据（JSON）

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
    "input_signal_id": "带给定扰动力矩的机体力矩命令",
    "output_signal_id": "姿态",
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
    "stability": "令 带给定扰动力矩的机体力矩命令 回到基线，核对 姿态、角速度与扰动响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 姿态、角速度与扰动响应 的首次有效方向与最终方向。",
    "delay": "从记录的 带给定扰动力矩的机体力矩命令 边沿量到 姿态、角速度与扰动响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 带给定扰动力矩的机体力矩命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 117. 把跟踪误差要求转成性能边界

### 控制问题描述

这是一个由正弦参考驱动、同时记录跟踪误差和受控输出的跟踪控制环路。控制输入是给定正弦参考指令，输出是由传感器或同步记录器连续获取的跟踪误差与受控输出。在多次小幅且可逆的试验中，跟踪误差与受控输出开始时就沿最终方向变化，不会先向相反方向运动；给定正弦参考指令改变后，跟踪误差与受控输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定正弦参考指令撤回基准值后，跟踪误差与受控输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的给定正弦参考指令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定正弦参考指令与跟踪误差与受控输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，跟踪误差与受控输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

跟踪误差与受控输出

### 执行器

给定正弦参考指令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

要求 0–100 Hz 单位正弦跟踪误差不超过 0.005；在该频带用 S=1/201 作精确核对。

### 示例数据（JSON）

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
    "input_signal_id": "给定正弦参考指令",
    "output_signal_id": "跟踪误差与受控输出",
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
    "stability": "令 给定正弦参考指令 回到基线，核对 跟踪误差与受控输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 跟踪误差与受控输出 的首次有效方向与最终方向。",
    "delay": "从记录的 给定正弦参考指令 边沿量到 跟踪误差与受控输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 给定正弦参考指令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 118. 对象不确定性、鲁棒稳定与灵敏度限制

### 控制问题描述

这是一个围绕不确定动态对象构成、利用控制器和传感通道限制灵敏度的反馈系统。控制输入是给定对象变化下的环路整形反馈命令，输出是由传感器或同步记录器连续获取的受控输出、跟踪误差与控制作用。在多次小幅且可逆的试验中，受控输出开始时就沿最终方向变化，不会先向相反方向运动；给定对象变化下的环路整形反馈命令改变后，受控输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定对象变化下的环路整形反馈命令恢复到基准值后，受控输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定对象变化下的环路整形反馈命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定对象变化下的环路整形反馈命令与受控输出、跟踪误差与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

受控输出、跟踪误差与控制作用

### 执行器

给定对象变化下的环路整形反馈命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=24.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取天线 G=1/[s(s+1)] 与 D=10(0.5s+1)/(0.1s+1)；计算 S、T 并施加高频不确定性权重。

### 示例数据（JSON）

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
    "input_signal_id": "给定对象变化下的环路整形反馈命令",
    "output_signal_id": "受控输出",
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
    "stability": "令 给定对象变化下的环路整形反馈命令 回到基线，核对 受控输出、跟踪误差与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出、跟踪误差与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 给定对象变化下的环路整形反馈命令 边沿量到 受控输出、跟踪误差与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 给定对象变化下的环路整形反馈命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 119. 采样等效延迟造成的相位损失

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是数字采样控制命令，输出是由传感器或同步记录器连续获取的采样对象输出、跟踪误差与控制作用。在多次小幅且可逆的试验中，采样对象输出开始时就沿最终方向变化，不会先向相反方向运动；数字采样控制命令改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字采样控制命令恢复到基准值后，采样对象输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的数字采样控制命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字采样控制命令与采样对象输出、跟踪误差与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，采样对象输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

采样对象输出、跟踪误差与控制作用

### 执行器

数字采样控制命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=24.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

在交叉频率 5 rad/s 的超前电机环加入等效迟延 Td=0.025 s；比较 Ts=0.05 与 0.14 s。

### 示例数据（JSON）

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
    "input_signal_id": "数字采样控制命令",
    "output_signal_id": "采样对象输出",
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
    "stability": "令 数字采样控制命令 回到基线，核对 采样对象输出、跟踪误差与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 采样对象输出、跟踪误差与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 数字采样控制命令 边沿量到 采样对象输出、跟踪误差与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字采样控制命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 120. 用 Nichols 图读取闭环峰值与裕度

### 控制问题描述

这是一个由正弦信号源、动态对象和同步幅相记录器组成的频率响应试验系统。控制输入是有界扫频输入，输出是由传感器或同步记录器连续获取的闭环输出与频率响应。在多次小幅且可逆的试验中，闭环输出与频率响应开始时就沿最终方向变化，不会先向相反方向运动；有界扫频输入改变后，闭环输出与频率响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界扫频输入撤回基准值后，闭环输出与频率响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的有界扫频输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界扫频输入与闭环输出与频率响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，闭环输出与频率响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

闭环输出与频率响应

### 执行器

有界扫频输入

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用 PID 环路频率样本读取 Nichols 等值线；核对带宽 0.8 rad/s、峰值 1.2、PM 37°、GM 1.26。

### 示例数据（JSON）

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
    "input_signal_id": "有界扫频输入",
    "output_signal_id": "闭环输出与频率响应",
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
    "stability": "令 有界扫频输入 回到基线，核对 闭环输出与频率响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 闭环输出与频率响应 的首次有效方向与最终方向。",
    "delay": "从记录的 有界扫频输入 边沿量到 闭环输出与频率响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界扫频输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 121. 刚性卫星的状态变量模型

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是推力器力，输出是由传感器或同步记录器连续获取的姿态角与角速度。在多次小幅且可逆的试验中，姿态角与角速度开始时就沿最终方向变化，不会先向相反方向运动；推力器力改变后，姿态角与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把推力器力撤回基准值后，姿态角与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的推力器力变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。推力器力与姿态角与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，姿态角与角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

姿态角与角速度

### 执行器

推力器力

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取力臂 d=1 m、惯量 I=5000 kg*m^2、状态 [角度,角速度]，施加 ±25 N 脉冲，以 0.01 s 运行 20 s。

### 示例数据（JSON）

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
      "推力器力"
    ],
    "output_signal_ids": [
      "姿态角与角速度通道 1",
      "姿态角与角速度通道 2"
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
    "stability": "令 推力器力 回到基线，核对 姿态角与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 姿态角与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 推力器力 边沿量到 姿态角与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 推力器力 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 122. 直流电机的三阶状态模型

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是电枢电压，输出是由传感器或同步记录器连续获取的电机位置、转速、电流。在多次小幅且可逆的试验中，电机位置开始时就沿最终方向变化，不会先向相反方向运动；电枢电压改变后，电机位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把电枢电压撤回基准值后，电机位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的电枢电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电枢电压与电机位置、转速、电流采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机位置、转速、电流

### 执行器

电枢电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 J=0.0113、b=0.028、La=0.1、Ra=1、Kt=Ke=0.067；施加 ±1 V 阶跃，以 0.001 s 记录角度、转速、电流。

### 示例数据（JSON）

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
      "电枢电压"
    ],
    "output_signal_ids": [
      "电机位置",
      "转速",
      "电流"
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
    "stability": "令 电枢电压 回到基线，核对 电机位置、转速、电流 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机位置、转速、电流 的首次有效方向与最终方向。",
    "delay": "从记录的 电枢电压 边沿量到 电机位置、转速、电流 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 电枢电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 123. 四分之一车的实模态规范形

### 控制问题描述

这是一个由车身、车轮、弹簧和减振器组成的车辆垂向悬架装置。控制输入是实现输入，输出是由传感器或同步记录器连续获取的四分之一车输出与模态状态。在多次小幅且可逆的试验中，四分之一车输出与模态状态开始时就沿最终方向变化，不会先向相反方向运动；实现输入改变后，四分之一车输出与模态状态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把实现输入撤回基准值后，四分之一车输出与模态状态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的实现输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。实现输入与四分之一车输出与模态状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，四分之一车输出与模态状态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

四分之一车输出与模态状态

### 执行器

实现输入

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=(2s+4)/[s^2(s^2+2s+4)]，分别实现刚体与柔性模态，以 0.005 s 采样冲激响应。

### 示例数据（JSON）

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
    "input_signal_id": "实现输入",
    "output_signal_id": "四分之一车输出与模态状态",
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
    "stability": "令 实现输入 回到基线，核对 四分之一车输出与模态状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 四分之一车输出与模态状态 的首次有效方向与最终方向。",
    "delay": "从记录的 实现输入 边沿量到 四分之一车输出与模态状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 实现输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 124. 热系统从控制规范形变换到模态形

### 控制问题描述

这是一个由多个相互传热的储能状态和温度输出通道组成的热状态空间系统。控制输入是热输入，输出是由传感器或同步记录器连续获取的热模态状态与输出。在多次小幅且可逆的试验中，热模态状态与输出开始时就沿最终方向变化，不会先向相反方向运动；热输入改变后，热模态状态与输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把热输入恢复到基准值后，热模态状态与输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的热输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。热输入与热模态状态与输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，热模态状态与输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

热模态状态与输出

### 执行器

热输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=200.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

取 Ac=[[-7,-12],[1,0]]、Bc=[1,0]、Cc=[1,2] 与 T=[[4,-3],[-1,1]]，比较变换前后轨迹。

### 示例数据（JSON）

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
    "input_signal_id": "热输入",
    "output_signal_id": "热模态状态与输出",
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
    "stability": "令 热输入 回到基线，核对 热模态状态与输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 热模态状态与输出 的首次有效方向与最终方向。",
    "delay": "从记录的 热输入 边沿量到 热模态状态与输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 热输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 125. 由 Piper Dakota 状态模型求极点零点

### 控制问题描述

这是一个由动态对象、状态测量或估计器以及反馈执行通道组成的状态空间控制系统。控制输入是升降舵输入，输出是由传感器或同步记录器连续获取的俯仰姿态与模态状态。在多次小幅且可逆的试验中，俯仰姿态与模态状态开始时就沿最终方向变化，不会先向相反方向运动；升降舵输入改变后，俯仰姿态与模态状态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把升降舵输入恢复到基准值后，俯仰姿态与模态状态最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的升降舵输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。升降舵输入与俯仰姿态与模态状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变负载、元件或运行条件并重复试验时，俯仰姿态与模态状态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

俯仰姿态与模态状态

### 执行器

升降舵输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用给定 Piper Dakota 四状态矩阵；施加 ±1° 升降舵脉冲，计算极点、零点与俯仰响应。

### 示例数据（JSON）

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
    "input_signal_id": "升降舵输入",
    "output_signal_id": "俯仰姿态与模态状态",
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
    "stability": "令 升降舵输入 回到基线，核对 俯仰姿态与模态状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 俯仰姿态与模态状态 的首次有效方向与最终方向。",
    "delay": "从记录的 升降舵输入 边沿量到 俯仰姿态与模态状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 升降舵输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 126. 能控性、能观性与极零相消

### 控制问题描述

这是一个由动态对象、状态测量或估计器以及反馈执行通道组成的状态空间控制系统。控制输入是有界状态空间测试激励，输出是由传感器或同步记录器连续获取的状态轨迹与指定输出响应。在多次小幅且可逆的试验中，状态轨迹与指定输出响应开始时就沿最终方向变化，不会先向相反方向运动；有界状态空间测试激励改变后，状态轨迹与指定输出响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界状态空间测试激励恢复到基准值后，状态轨迹与指定输出响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的有界状态空间测试激励变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。即使同步记录有界状态空间测试激励与状态轨迹与指定输出响应，一个被极零相消的模态既不出现在记录中，也无法由输入激发；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，状态轨迹与指定输出响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

状态轨迹与指定输出响应

### 执行器

有界状态空间测试激励

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 A=diag(-3,-4)、B=[1,1]^T、C=[0,1]、D=0，使 -3 模态能控但不可观；比较内部状态与约分后输出。

### 示例数据（JSON）

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
      "有界状态空间测试激励"
    ],
    "output_signal_ids": [
      "状态轨迹与指定输出响应"
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
    "stability": "令 有界状态空间测试激励 回到基线，核对 状态轨迹与指定输出响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 状态轨迹与指定输出响应 的首次有效方向与最终方向。",
    "delay": "从记录的 有界状态空间测试激励 边沿量到 状态轨迹与指定输出响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界状态空间测试激励 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 127. 摆系统的全状态重复极点配置

### 控制问题描述

这是一个由转轴、刚性杆和集中质量构成的摆动机械装置。控制输入是枢轴力矩，输出是由传感器或同步记录器连续获取的摆角与角速度。在多次小幅且可逆的试验中，摆角与角速度开始时就沿最终方向变化，不会先向相反方向运动；枢轴力矩改变后，摆角与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把枢轴力矩撤回基准值后，摆角与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的枢轴力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。枢轴力矩与摆角与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，摆角与角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

摆角与角速度

### 执行器

枢轴力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 omega0=1 rad/s、反馈 K=[3,4]；从 0.1 rad 初角释放并与开环摆比较。

### 示例数据（JSON）

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
      "枢轴力矩"
    ],
    "output_signal_ids": [
      "摆角与角速度通道 1",
      "摆角与角速度通道 2"
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
    "stability": "令 枢轴力矩 回到基线，核对 摆角与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 摆角与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 枢轴力矩 边沿量到 摆角与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 枢轴力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 128. Ackermann 配置与弱能控零点

### 控制问题描述

这是一个由动态对象、状态测量或估计器以及反馈执行通道组成的状态空间控制系统。控制输入是有界状态反馈命令，输出是由传感器或同步记录器连续获取的闭环状态响应与控制作用。在多次小幅且可逆的试验中，闭环状态响应与控制作用开始时就沿最终方向变化，不会先向相反方向运动；有界状态反馈命令改变后，闭环状态响应与控制作用在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界状态反馈命令恢复到基准值后，闭环状态响应与控制作用最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的有界状态反馈命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。有界状态反馈命令与闭环状态响应与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

闭环状态响应与控制作用

### 执行器

有界状态反馈命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=24.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

目标为 s^2+2s+4；比较 z0=2 时 K=[-3.8,0.6] 与 z0=-2.99 时 K=[2052.5,-688.1]。

### 示例数据（JSON）

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
    "input_signal_id": "有界状态反馈命令",
    "output_signal_id": "闭环状态响应与控制作用",
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
    "stability": "令 有界状态反馈命令 回到基线，核对 闭环状态响应与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 闭环状态响应与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 有界状态反馈命令 边沿量到 闭环状态响应与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界状态反馈命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 129. Type 一电机的鲁棒参考引入

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是状态反馈电压，输出是由传感器或同步记录器连续获取的电机位置与速度。在多次小幅且可逆的试验中，电机位置与速度开始时就沿最终方向变化，不会先向相反方向运动；状态反馈电压改变后，电机位置与速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把状态反馈电压撤回基准值后，电机位置与速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的状态反馈电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。状态反馈电压与电机位置与速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机位置与速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机位置与速度

### 执行器

状态反馈电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取电机 A=[[0,1],[0,-1]]、B=[0,1]、K=[8,3]、参考增益 Nbar=8；施加 ±1 位置阶跃。

### 示例数据（JSON）

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
    "input_signal_id": "状态反馈电压",
    "output_signal_id": "电机位置与速度",
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
    "stability": "令 状态反馈电压 回到基线，核对 电机位置与速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机位置与速度 的首次有效方向与最终方向。",
    "delay": "从记录的 状态反馈电压 边沿量到 电机位置与速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 状态反馈电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 130. 无人机三阶对象的主导二阶极点

### 控制问题描述

这是一个由机体、旋翼和惯性运动状态组成的多旋翼飞行器控制系统。控制输入是控制力矩，输出是由传感器或同步记录器连续获取的无人机姿态响应。在多次小幅且可逆的试验中，无人机姿态响应开始时就沿最终方向变化，不会先向相反方向运动；控制力矩改变后，无人机姿态响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把控制力矩撤回基准值后，无人机姿态响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的控制力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。控制力矩与无人机姿态响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，无人机姿态响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

无人机姿态响应

### 执行器

控制力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

使用三状态无人机模型、K=[14,56,96]、Nbar=96；单位高度阶跃以 0.005 s 运行 10 s。

### 示例数据（JSON）

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
    "input_signal_id": "控制力矩",
    "output_signal_id": "无人机姿态响应",
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
    "stability": "令 控制力矩 回到基线，核对 无人机姿态响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 无人机姿态响应 的首次有效方向与最终方向。",
    "delay": "从记录的 控制力矩 边沿量到 无人机姿态响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 控制力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 131. 无人机 LQR 误差—控制权衡

### 控制问题描述

这是一个由机体、旋翼和惯性运动状态组成的多旋翼飞行器控制系统。控制输入是最优控制力矩，输出是由传感器或同步记录器连续获取的无人机状态与控制努力。在多次小幅且可逆的试验中，无人机状态与控制努力开始时就沿最终方向变化，不会先向相反方向运动；最优控制力矩改变后，无人机状态与控制努力在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把最优控制力矩撤回基准值后，无人机状态与控制努力会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的最优控制力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。最优控制力矩与无人机状态与控制努力采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，无人机状态与控制努力的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

无人机状态与控制努力

### 执行器

最优控制力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

无人机取 Q=100 C^T C、R=1、LQR K=[2.8728,9.8720,10]，并比较 rho=10、100、1000。

### 示例数据（JSON）

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
    "input_signal_id": "最优控制力矩",
    "output_signal_id": "无人机状态与控制努力",
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
    "stability": "令 最优控制力矩 回到基线，核对 无人机状态与控制努力 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 无人机状态与控制努力 的首次有效方向与最终方向。",
    "delay": "从记录的 最优控制力矩 边沿量到 无人机状态与控制努力 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 最优控制力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 132. 摆系统全阶状态估计器

### 控制问题描述

这是一个由转轴、刚性杆和集中质量构成的摆动机械装置。控制输入是已知枢轴力矩，输出是由传感器或同步记录器连续获取的测量角与估计状态。在多次小幅且可逆的试验中，测量角与估计状态开始时就沿最终方向变化，不会先向相反方向运动；已知枢轴力矩改变后，测量角与估计状态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把已知枢轴力矩撤回基准值后，测量角与估计状态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的已知枢轴力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。已知枢轴力矩与测量角与估计状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，测量角与估计状态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

测量角与估计状态

### 执行器

已知枢轴力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 omega0=1、全阶估计器 L=[20,99]；对象初态为零而估计初态 [0.2,-0.1]。

### 示例数据（JSON）

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
      "已知枢轴力矩"
    ],
    "output_signal_ids": [
      "测量角与估计状态通道 1",
      "测量角与估计状态通道 2"
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
    "stability": "令 已知枢轴力矩 回到基线，核对 测量角与估计状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 测量角与估计状态 的首次有效方向与最终方向。",
    "delay": "从记录的 已知枢轴力矩 边沿量到 测量角与估计状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 已知枢轴力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 133. 不微分测量的降阶摆估计器

### 控制问题描述

这是一个由转轴、刚性杆和集中质量构成的摆动机械装置。控制输入是已知枢轴力矩，输出是由传感器或同步记录器连续获取的测量角与估计角速度。在多次小幅且可逆的试验中，测量角与估计角速度开始时就沿最终方向变化，不会先向相反方向运动；已知枢轴力矩改变后，测量角与估计角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把已知枢轴力矩撤回基准值后，测量角与估计角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的已知枢轴力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。已知枢轴力矩与测量角与估计角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，测量角与估计角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

测量角与估计角速度

### 执行器

已知枢轴力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 omega0=1、降阶观测器增益 L=10；由测得角度估计角速度，不做数值微分。

### 示例数据（JSON）

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
    "input_signal_id": "已知枢轴力矩",
    "output_signal_id": "测量角与估计角速度",
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
    "stability": "令 已知枢轴力矩 回到基线，核对 测量角与估计角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 测量角与估计角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 已知枢轴力矩 边沿量到 测量角与估计角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 已知枢轴力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 134. 由对称根轨迹选择估计器极点

### 控制问题描述

这是一个由动态对象、状态测量或估计器以及反馈执行通道组成的状态空间控制系统。控制输入是已知对象输入，输出是由传感器或同步记录器连续获取的状态估计与新息。在多次小幅且可逆的试验中，状态估计与新息开始时就沿最终方向变化，不会先向相反方向运动；已知对象输入改变后，状态估计与新息在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把已知对象输入撤回基准值后，状态估计与新息会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的已知对象输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。已知对象输入与状态估计与新息采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，状态估计与新息的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

状态估计与新息

### 执行器

已知对象输入

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 omega0=1、噪声比 q=365、估计器极点 -3±j3.18；用相同随机种子比较 q/10、q、10q。

### 示例数据（JSON）

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
    "input_signal_id": "已知对象输入",
    "output_signal_id": "状态估计与新息",
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
    "stability": "令 已知对象输入 回到基线，核对 状态估计与新息 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 状态估计与新息 的首次有效方向与最终方向。",
    "delay": "从记录的 已知对象输入 边沿量到 状态估计与新息 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 已知对象输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 135. 分离原理与直流伺服动态补偿器

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是动态补偿器电压，输出是由传感器或同步记录器连续获取的伺服输出、估计状态与控制作用。在多次小幅且可逆的试验中，伺服输出开始时就沿最终方向变化，不会先向相反方向运动；动态补偿器电压改变后，伺服输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把动态补偿器电压撤回基准值后，伺服输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的动态补偿器电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。动态补偿器电压与伺服输出、估计状态与控制作用采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，伺服输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

伺服输出、估计状态与控制作用

### 执行器

动态补偿器电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取伺服 G=10/[s(s+2)(s+8)]、K=[-46.4,5.76,-0.65]、L=[0.56,1.42,16]；仅在可停止仿真中扫描环路增益。

### 示例数据（JSON）

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
    "input_signal_id": "动态补偿器电压",
    "output_signal_id": "伺服输出",
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
    "stability": "令 动态补偿器电压 回到基线，核对 伺服输出、估计状态与控制作用 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 伺服输出、估计状态与控制作用 的首次有效方向与最终方向。",
    "delay": "从记录的 动态补偿器电压 边沿量到 伺服输出、估计状态与控制作用 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 动态补偿器电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 136. 用零点配置提高伺服速度常数

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是双输入或等效滞后-超前命令，输出是由传感器或同步记录器连续获取的伺服位置、跟踪误差与慢尾。在多次小幅且可逆的试验中，伺服位置开始时就沿最终方向变化，不会先向相反方向运动；双输入或等效滞后-超前命令改变后，伺服位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把双输入或等效滞后-超前命令撤回基准值后，伺服位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的双输入或等效滞后-超前命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。双输入或等效滞后-超前命令与伺服位置、跟踪误差与慢尾采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，伺服位置的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

伺服位置、跟踪误差与慢尾

### 执行器

双输入或等效滞后-超前命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s+1)]、K=[8,3]、估计器极点 -0.1、控制器零点 -0.096，并用单位斜坡核对 Kv=10。

### 示例数据（JSON）

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
    "input_signal_id": "双输入或等效滞后-超前命令",
    "output_signal_id": "伺服位置",
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
    "stability": "令 双输入或等效滞后-超前命令 回到基线，核对 伺服位置、跟踪误差与慢尾 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 伺服位置、跟踪误差与慢尾 的首次有效方向与最终方向。",
    "delay": "从记录的 双输入或等效滞后-超前命令 边沿量到 伺服位置、跟踪误差与慢尾 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 双输入或等效滞后-超前命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 137. 电机速度的积分状态反馈

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是电机电压，输出是由传感器或同步记录器连续获取的电机速度与积分误差。在多次小幅且可逆的试验中，电机速度与积分误差开始时就沿最终方向变化，不会先向相反方向运动；电机电压改变后，电机速度与积分误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把电机电压恢复到基准值后，电机速度与积分误差最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的电机电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电机电压与电机速度与积分误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，电机速度与积分误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

电机速度与积分误差

### 执行器

电机电压

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取电机 xdot=-3x+u+w、积分状态 xI_dot=y-r、增益 [25,7]、观测器 L=7；参考与常值负载分开测试。

### 示例数据（JSON）

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
    "input_signal_id": "电机电压",
    "output_signal_id": "电机速度与积分误差",
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
    "stability": "令 电机电压 回到基线，核对 电机速度与积分误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 电机速度与积分误差 的首次有效方向与最终方向。",
    "delay": "从记录的 电机电压 边沿量到 电机速度与积分误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 电机电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 138. 磁盘驱动器的正弦内模控制

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是音圈力，输出是由传感器或同步记录器连续获取的磁头位置与正弦误差。在多次小幅且可逆的试验中，磁头位置与正弦误差开始时就沿最终方向变化，不会先向相反方向运动；音圈力改变后，磁头位置与正弦误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把音圈力撤回基准值后，磁头位置与正弦误差会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的音圈力变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。音圈力与磁头位置与正弦误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，磁头位置与正弦误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

磁头位置与正弦误差

### 执行器

音圈力

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 omega0=1、增益向量 [2.0718,16.3923,13.9282,4.4641]；跟踪并抑制 0.9、1.0、1.1 rad/s 正弦。

### 示例数据（JSON）

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
    "input_signal_id": "音圈力",
    "output_signal_id": "磁头位置与正弦误差",
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
    "stability": "令 音圈力 回到基线，核对 磁头位置与正弦误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 磁头位置与正弦误差 的首次有效方向与最终方向。",
    "delay": "从记录的 音圈力 边沿量到 磁头位置与正弦误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 音圈力 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 139. 卫星 LTR 环路恢复与噪声权衡

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是给定传感噪声下的机体力矩，输出是由传感器或同步记录器连续获取的姿态响应与机体力矩活动量。在多次小幅且可逆的试验中，姿态响应与机体力矩活动量开始时就沿最终方向变化，不会先向相反方向运动；给定传感噪声下的机体力矩改变后，姿态响应与机体力矩活动量在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定传感噪声下的机体力矩撤回基准值后，姿态响应与机体力矩活动量会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的给定传感噪声下的机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定传感噪声下的机体力矩与姿态响应与机体力矩活动量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

姿态响应与机体力矩活动量

### 执行器

给定传感噪声下的机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取卫星 LQR K=[1,1.414] 与 q=1、10、100 的 LTR 估计器；注入相同单位传感噪声并记录控制 RMS。

### 示例数据（JSON）

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
    "input_signal_id": "给定传感噪声下的机体力矩",
    "output_signal_id": "姿态响应与机体力矩活动量",
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
    "stability": "令 给定传感噪声下的机体力矩 回到基线，核对 姿态响应与机体力矩活动量 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 姿态响应与机体力矩活动量 的首次有效方向与最终方向。",
    "delay": "从记录的 给定传感噪声下的机体力矩 边沿量到 姿态响应与机体力矩活动量 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 给定传感噪声下的机体力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 140. Smith 预估器控制纯迟延换热器

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是经 Smith 预估器的蒸汽命令，输出是由传感器或同步记录器连续获取的含迟延的换热器温度。在多次小幅且可逆的试验中，含迟延的换热器温度开始时就沿最终方向变化，不会先向相反方向运动；经 Smith 预估器的蒸汽命令改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把经 Smith 预估器的蒸汽命令恢复到基准值后，含迟延的换热器温度最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的经 Smith 预估器的蒸汽命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。经 Smith 预估器的蒸汽命令与含迟延的换热器温度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

含迟延的换热器温度

### 执行器

经 Smith 预估器的蒸汽命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=240.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

取 G0=1/[(10s+1)(60s+1)]、迟延 5 s、K=[5.2,-0.17]、L=[0.18,4.2]、Nbar=1.2055；并把迟延扰动到 4.5、5.5 s。

### 示例数据（JSON）

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
    "input_signal_id": "经 Smith 预估器的蒸汽命令",
    "output_signal_id": "含迟延的换热器温度",
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
    "stability": "令 经 Smith 预估器的蒸汽命令 回到基线，核对 含迟延的换热器温度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 含迟延的换热器温度 的首次有效方向与最终方向。",
    "delay": "从记录的 经 Smith 预估器的蒸汽命令 边沿量到 含迟延的换热器温度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 经 Smith 预估器的蒸汽命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 141. 用 Tustin 法数字化电机超前器

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是数字电机电压，输出是由传感器或同步记录器连续获取的采样电机位置与误差。在多次小幅且可逆的试验中，采样电机位置与误差开始时就沿最终方向变化，不会先向相反方向运动；数字电机电压改变后，采样电机位置与误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字电机电压撤回基准值后，采样电机位置与误差会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的数字电机电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字电机电压与采样电机位置与误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，采样电机位置与误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

采样电机位置与误差

### 执行器

数字电机电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

连续 lead 为 10(0.5s+1)/(0.1s+1)，T=0.025 s；Tustin 递推 u[k]=0.7778u[k-1]+45.56e[k]-43.33e[k-1]。

### 示例数据（JSON）

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
    "input_signal_id": "数字电机电压",
    "output_signal_id": "采样电机位置与误差",
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
    "stability": "令 数字电机电压 回到基线，核对 采样电机位置与误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 采样电机位置与误差 的首次有效方向与最终方向。",
    "delay": "从记录的 数字电机电压 边沿量到 采样电机位置与误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字电机电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 142. 用 ZOH 法数字化同一超前器

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是保持的电机电压，输出是由传感器或同步记录器连续获取的采样电机位置与误差。在多次小幅且可逆的试验中，采样电机位置与误差开始时就沿最终方向变化，不会先向相反方向运动；保持的电机电压改变后，采样电机位置与误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把保持的电机电压撤回基准值后，采样电机位置与误差会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的保持的电机电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。保持的电机电压与采样电机位置与误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，采样电机位置与误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

采样电机位置与误差

### 执行器

保持的电机电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

同一连续 lead 与 T=0.025 s 采用 ZOH 递推 u[k]=0.7788u[k-1]+50e[k]-47.79e[k-1]。

### 示例数据（JSON）

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
    "input_signal_id": "保持的电机电压",
    "output_signal_id": "采样电机位置与误差",
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
    "stability": "令 保持的电机电压 回到基线，核对 采样电机位置与误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 采样电机位置与误差 的首次有效方向与最终方向。",
    "delay": "从记录的 保持的电机电压 边沿量到 采样电机位置与误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 保持的电机电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 143. 空间站姿态的匹配极零数字控制

### 控制问题描述

这是一个由数字姿态控制器和刚性空间站本体组成、并用匹配极零方法保留连续设计特性的航天器系统。控制输入是数字机体力矩，输出是由传感器或同步记录器连续获取的空间站姿态。在多次小幅且可逆的试验中，空间站姿态开始时就沿最终方向变化，不会先向相反方向运动；数字机体力矩改变后，空间站姿态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字机体力矩撤回基准值后，空间站姿态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的数字机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字机体力矩与空间站姿态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，空间站姿态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

空间站姿态

### 执行器

数字机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

空间站 G=1/s^2、连续 lead 0.81(s+0.2)/(s+2)；MPZ 在 T=1 s 为 0.389(z-0.82)/(z-0.135)，再以 T=0.5 s 重算。

### 示例数据（JSON）

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
    "input_signal_id": "数字机体力矩",
    "output_signal_id": "空间站姿态",
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
    "stability": "令 数字机体力矩 回到基线，核对 空间站姿态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 空间站姿态 的首次有效方向与最终方向。",
    "delay": "从记录的 数字机体力矩 边沿量到 空间站姿态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字机体力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 144. 一阶对象连续与离散根轨迹比较

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是保持的比例命令，输出是由传感器或同步记录器连续获取的采样一阶输出。在多次小幅且可逆的试验中，采样一阶输出开始时就沿最终方向变化，不会先向相反方向运动；保持的比例命令改变后，采样一阶输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把保持的比例命令恢复到基准值后，采样一阶输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的保持的比例命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。保持的比例命令与采样一阶输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，采样一阶输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

采样一阶输出

### 执行器

保持的比例命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取 a=1 s^-1、T=0.1 s、alpha=exp(-0.1)，让比例 K 穿过精确采样稳定上界。

### 示例数据（JSON）

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
    "input_signal_id": "保持的比例命令",
    "output_signal_id": "采样一阶输出",
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
    "stability": "令 保持的比例命令 回到基线，核对 采样一阶输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 采样一阶输出 的首次有效方向与最终方向。",
    "delay": "从记录的 保持的比例命令 边沿量到 采样一阶输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 保持的比例命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 145. 空间站姿态的直接 z 平面设计

### 控制问题描述

这是一个由数字姿态控制器和刚性空间站本体组成、直接在离散域内整定动态的航天器系统。控制输入是数字机体力矩，输出是由传感器或同步记录器连续获取的空间站姿态。在多次小幅且可逆的试验中，空间站姿态开始时就沿最终方向变化，不会先向相反方向运动；数字机体力矩改变后，空间站姿态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字机体力矩撤回基准值后，空间站姿态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的数字机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字机体力矩与空间站姿态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，空间站姿态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

空间站姿态

### 执行器

数字机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

T=1 s 时用精确 ZOH 对象 Gd=0.5(z+1)/(z-1)^2 与直接控制器 0.374(z-0.85)/z。

### 示例数据（JSON）

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
    "input_signal_id": "数字机体力矩",
    "output_signal_id": "空间站姿态",
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
    "stability": "令 数字机体力矩 回到基线，核对 空间站姿态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 空间站姿态 的首次有效方向与最终方向。",
    "delay": "从记录的 数字机体力矩 边沿量到 空间站姿态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字机体力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 146. 连续、仿真等效与直接离散响应比较

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是连续或数字命令，输出是由传感器或同步记录器连续获取的连续与采样阶跃响应。在多次小幅且可逆的试验中，连续与采样阶跃响应开始时就沿最终方向变化，不会先向相反方向运动；连续或数字命令改变后，连续与采样阶跃响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把连续或数字命令撤回基准值后，连续与采样阶跃响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的连续或数字命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。连续或数字命令与连续与采样阶跃响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，连续与采样阶跃响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

连续与采样阶跃响应

### 执行器

连续或数字命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

在 T=1 s 的同一精确 ZOH 对象上比较连续 lead、MPZ 0.389(z-0.82)/(z-0.135) 与直接 0.374(z-0.85)/z。

### 示例数据（JSON）

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
    "input_signal_id": "连续或数字命令",
    "output_signal_id": "连续与采样阶跃响应",
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
    "stability": "令 连续或数字命令 回到基线，核对 连续与采样阶跃响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 连续与采样阶跃响应 的首次有效方向与最终方向。",
    "delay": "从记录的 连续或数字命令 边沿量到 连续与采样阶跃响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 连续或数字命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 147. 由 z 传递函数恢复滤波器差分方程

### 控制问题描述

这是一个由电阻、电容、电感或运算放大器构成的电信号处理网络。控制输入是离散滤波器输入，输出是由传感器或同步记录器连续获取的滤波器输出。在多次小幅且可逆的试验中，滤波器输出开始时就沿最终方向变化，不会先向相反方向运动；离散滤波器输入改变后，滤波器输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把离散滤波器输入恢复到基准值后，滤波器输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的离散滤波器输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。离散滤波器输入与滤波器输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，滤波器输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

滤波器输出

### 执行器

离散滤波器输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

采样 1 Hz，使用 H(z)=(1+0.5z^-1)/[(1-0.5z^-1)(1+z^-1/3)]，测试冲激、阶跃与交替输入。

### 示例数据（JSON）

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
    "input_signal_id": "离散滤波器输入",
    "output_signal_id": "滤波器输出",
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
    "stability": "令 离散滤波器输入 回到基线，核对 滤波器输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 滤波器输出 的首次有效方向与最终方向。",
    "delay": "从记录的 离散滤波器输入 边沿量到 滤波器输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 离散滤波器输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 148. 用 z 变换求解受迫二阶差分方程

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是斜坡序列输入，输出是由传感器或同步记录器连续获取的离散序列输出。在多次小幅且可逆的试验中，离散序列输出开始时就沿最终方向变化，不会先向相反方向运动；斜坡序列输入改变后，离散序列输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把斜坡序列输入恢复到基准值后，离散序列输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的斜坡序列输入变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。斜坡序列输入与离散序列输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，离散序列输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

离散序列输出

### 执行器

斜坡序列输入

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

使用 y[k]-3y[k-1]+2y[k-2]=2u[k-1]-2u[k-2]、u[k]=k、负时刻为零，计算 k=0..15。

### 示例数据（JSON）

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
    "input_signal_id": "斜坡序列输入",
    "output_signal_id": "离散序列输出",
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
    "stability": "令 斜坡序列输入 回到基线，核对 离散序列输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 离散序列输出 的首次有效方向与最终方向。",
    "delay": "从记录的 斜坡序列输入 边沿量到 离散序列输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 斜坡序列输入 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 149. 证明 s 到 z 平面的七条映射性质

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是给定模态映射测试，输出是由传感器或同步记录器连续获取的连续与采样自由响应模态。在多次小幅且可逆的试验中，连续与采样自由响应模态开始时就沿最终方向变化，不会先向相反方向运动；给定模态映射测试改变后，连续与采样自由响应模态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定模态映射测试恢复到基准值后，连续与采样自由响应模态最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定模态映射测试变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定模态映射测试与连续与采样自由响应模态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，连续与采样自由响应模态的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

连续与采样自由响应模态

### 执行器

给定模态映射测试

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取 T=0.1 s，映射 s=-1±j2 与 s=-1±j(2+2pi/T)，核对相同 z 极点与混叠。

### 示例数据（JSON）

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
    "input_signal_id": "给定模态映射测试",
    "output_signal_id": "连续与采样自由响应模态",
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
    "stability": "令 给定模态映射测试 回到基线，核对 连续与采样自由响应模态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 连续与采样自由响应模态 的首次有效方向与最终方向。",
    "delay": "从记录的 给定模态映射测试 边沿量到 连续与采样自由响应模态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 给定模态映射测试 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 150. 二十赫兹下滞后器的匹配极零实现

### 控制问题描述

这是一个由固定频率采样器、数字滞后校正器、保持器和连续对象组成的数字控制环路。控制输入是数字滞后命令，输出是由传感器或同步记录器连续获取的受控输出与数字误差。在多次小幅且可逆的试验中，受控输出与数字误差开始时就沿最终方向变化，不会先向相反方向运动；数字滞后命令改变后，受控输出与数字误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字滞后命令恢复到基准值后，受控输出与数字误差最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的数字滞后命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字滞后命令与受控输出与数字误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，受控输出与数字误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

受控输出与数字误差

### 执行器

数字滞后命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取 lag (0.8s+1)/(50s+1)、fs=20 Hz，MPZ 零点 0.93941、极点 0.99900、增益 0.01650。

### 示例数据（JSON）

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
    "input_signal_id": "数字滞后命令",
    "output_signal_id": "受控输出与数字误差",
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
    "stability": "令 数字滞后命令 回到基线，核对 受控输出与数字误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出与数字误差 的首次有效方向与最终方向。",
    "delay": "从记录的 数字滞后命令 边沿量到 受控输出与数字误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字滞后命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 151. 超前网络的 Tustin 与 MPZ 比较

### 控制问题描述

这是一个由电阻、电容、电感或运算放大器构成的电信号处理网络。控制输入是采样误差，输出是由传感器或同步记录器连续获取的超前网络幅值与相位。在多次小幅且可逆的试验中，超前网络幅值与相位开始时就沿最终方向变化，不会先向相反方向运动；采样误差改变后，超前网络幅值与相位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把采样误差恢复到基准值后，超前网络幅值与相位最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的采样误差变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。采样误差与超前网络幅值与相位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，超前网络幅值与相位的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

超前网络幅值与相位

### 执行器

采样误差

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

把 H=(s+1)/(s+10.1) 在 T=0.25 s 下用 Tustin 与 MPZ 数字化，并比较 3 rad/s 相位。

### 示例数据（JSON）

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
    "input_signal_id": "采样误差",
    "output_signal_id": "超前网络幅值与相位",
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
    "stability": "令 采样误差 回到基线，核对 超前网络幅值与相位 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 超前网络幅值与相位 的首次有效方向与最终方向。",
    "delay": "从记录的 采样误差 边沿量到 超前网络幅值与相位 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 采样误差 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 152. 滞后网络的 Tustin 与 MPZ 比较

### 控制问题描述

这是一个由电阻、电容、电感或运算放大器构成的电信号处理网络。控制输入是采样误差，输出是由传感器或同步记录器连续获取的滞后网络幅值与相位。在多次小幅且可逆的试验中，滞后网络幅值与相位开始时就沿最终方向变化，不会先向相反方向运动；采样误差改变后，滞后网络幅值与相位在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把采样误差恢复到基准值后，滞后网络幅值与相位最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的采样误差变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。采样误差与滞后网络幅值与相位采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，滞后网络幅值与相位的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

滞后网络幅值与相位

### 执行器

采样误差

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

把 H=(10s+1)/(100s+1) 在 T=0.25 s 下用 Tustin 与 MPZ 数字化，并在 3 rad/s 评价。

### 示例数据（JSON）

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
    "input_signal_id": "采样误差",
    "output_signal_id": "滞后网络幅值与相位",
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
    "stability": "令 采样误差 回到基线，核对 滞后网络幅值与相位 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 滞后网络幅值与相位 的首次有效方向与最终方向。",
    "delay": "从记录的 采样误差 边沿量到 滞后网络幅值与相位 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 采样误差 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 153. 不同采样周期下的 PID 数字化

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是数字 PID 命令，输出是由传感器或同步记录器连续获取的采样阶跃响应。在多次小幅且可逆的试验中，采样阶跃响应开始时就沿最终方向变化，不会先向相反方向运动；数字 PID 命令改变后，采样阶跃响应在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字 PID 命令撤回基准值后，采样阶跃响应会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的数字 PID 命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字 PID 命令与采样阶跃响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，采样阶跃响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

采样阶跃响应

### 执行器

数字 PID 命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取 G=1/[s(s+1)] 与 PID K=15.2、Td=0.3816 s、Ti=0.95 s；在 T=1、0.1、0.01 s 数字化并记录输出与控制。

### 示例数据（JSON）

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
    "input_signal_id": "数字 PID 命令",
    "output_signal_id": "采样阶跃响应",
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
    "stability": "令 数字 PID 命令 回到基线，核对 采样阶跃响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 采样阶跃响应 的首次有效方向与最终方向。",
    "delay": "从记录的 数字 PID 命令 边沿量到 采样阶跃响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字 PID 命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 154. 含不稳定模态对象的采样增益稳定区间

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是保持的比例命令，输出是由传感器或同步记录器连续获取的采样对象输出。在多次小幅且可逆的试验中，采样对象输出开始时就沿最终方向变化，不会先向相反方向运动；保持的比例命令改变后，采样对象输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把保持的比例命令撤回基准值，采样对象输出的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。分别施加小幅正向和反向的保持的比例命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。保持的比例命令与采样对象输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，采样对象输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

采样对象输出

### 执行器

保持的比例命令

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=3.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

使用 T=1 s 精确 ZOH 模型 Gd=(7.96703z^2+1.33509z-0.324537)/(z^3-3.57119z^2+1.000162z-0.0000454)，扫描 K>0。

### 示例数据（JSON）

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
    "input_signal_id": "保持的比例命令",
    "output_signal_id": "采样对象输出",
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
    "stability": "令 保持的比例命令 回到基线，核对 采样对象输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 采样对象输出 的首次有效方向与最终方向。",
    "delay": "从记录的 保持的比例命令 边沿量到 采样对象输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 保持的比例命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 155. 卫星姿态的离散比例—速度反馈

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是数字力矩，输出是由传感器或同步记录器连续获取的卫星姿态与采样角速度。在多次小幅且可逆的试验中，卫星姿态与采样角速度开始时就沿最终方向变化，不会先向相反方向运动；数字力矩改变后，卫星姿态与采样角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字力矩撤回基准值后，卫星姿态与采样角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的数字力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字力矩与卫星姿态与采样角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，卫星姿态与采样角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

卫星姿态与采样角速度

### 执行器

数字力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取 T=0.1 s 的精确双积分模型，状态反馈 Kp=1.8097、Kv=1.9032，目标 z=exp((-1±j1)T)。

### 示例数据（JSON）

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
      "数字力矩"
    ],
    "output_signal_ids": [
      "卫星姿态与采样角速度通道 1",
      "卫星姿态与采样角速度通道 2"
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
    "stability": "令 数字力矩 回到基线，核对 卫星姿态与采样角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 卫星姿态与采样角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 数字力矩 边沿量到 卫星姿态与采样角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 156. 受传感与电流限制的数字磁悬浮

### 控制问题描述

这是一个由电磁铁吸引钢球并用位置传感器测量气隙的磁悬浮装置。控制输入是电磁铁电流，输出是由传感器或同步记录器连续获取的小球位移与电流。在多次小幅且可逆的试验中，小球位移与电流开始时就沿最终方向变化，不会先向相反方向运动；电磁铁电流改变后，小球位移与电流在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把电磁铁电流撤回基准值，小球位移与电流的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。分别施加小幅正向和反向的电磁铁电流变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。电磁铁电流与小球位移与电流采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

小球位移与电流

### 执行器

电磁铁电流

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=3.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取 m=0.02 kg、k1=20 N/m、k2=0.4 N/A、T=0.02 s；状态反馈 Kx=94 A/m、Kv=2.08 A*s/m，从 ±0.25 cm 初值测试并限流 1 A。

### 示例数据（JSON）

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
      "电磁铁电流"
    ],
    "output_signal_ids": [
      "小球位移与电流通道 1",
      "小球位移与电流通道 2"
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
    "stability": "令 电磁铁电流 回到基线，核对 小球位移与电流 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 小球位移与电流 的首次有效方向与最终方向。",
    "delay": "从记录的 电磁铁电流 边沿量到 小球位移与电流 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 电磁铁电流 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 157. z 平面直接设计超前—滞后伺服

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是数字伺服电压，输出是由传感器或同步记录器连续获取的伺服位置与斜坡误差。在多次小幅且可逆的试验中，伺服位置与斜坡误差开始时就沿最终方向变化，不会先向相反方向运动；数字伺服电压改变后，伺服位置与斜坡误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把数字伺服电压撤回基准值后，伺服位置与斜坡误差会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的数字伺服电压变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字伺服电压与伺服位置与斜坡误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，伺服位置与斜坡误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

伺服位置与斜坡误差

### 执行器

数字伺服电压

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取 G=10/[s(s+1)(s+10)]、fs=15 Hz 及其精确 ZOH 系数；直接设计满足 Mp≤16%、tr≤0.4 s、Kv_d>1.333。

### 示例数据（JSON）

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
    "input_signal_id": "数字伺服电压",
    "output_signal_id": "伺服位置与斜坡误差",
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
    "stability": "令 数字伺服电压 回到基线，核对 伺服位置与斜坡误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 伺服位置与斜坡误差 的首次有效方向与最终方向。",
    "delay": "从记录的 数字伺服电压 边沿量到 伺服位置与斜坡误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字伺服电压 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 158. 天线伺服的仿真等效与直接数字设计

### 控制问题描述

这是一个由电机、机械负载和位置或速度传感器组成的机电运动装置。控制输入是数字电机力矩，输出是由传感器或同步记录器连续获取的天线角度。在多次小幅且可逆的试验中，天线角度开始时就沿最终方向变化，不会先向相反方向运动；数字电机力矩改变后，天线角度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字电机力矩撤回基准值后，天线角度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的数字电机力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字电机力矩与天线角度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

天线角度

### 执行器

数字电机力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=4.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取天线 J=600000、B=20000、T=10 s；在同一精确 ZOH 对象上比较仿真等效与直接 z 设计。

### 示例数据（JSON）

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
    "input_signal_id": "数字电机力矩",
    "output_signal_id": "天线角度",
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
    "stability": "令 数字电机力矩 回到基线，核对 天线角度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 天线角度 的首次有效方向与最终方向。",
    "delay": "从记录的 数字电机力矩 边沿量到 天线角度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字电机力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 159. 两实极点对象的直接数字校正

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是数字校正命令，输出是由传感器或同步记录器连续获取的采样对象输出。在多次小幅且可逆的试验中，采样对象输出开始时就沿最终方向变化，不会先向相反方向运动；数字校正命令改变后，采样对象输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字校正命令恢复到基准值后，采样对象输出最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的数字校正命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。数字校正命令与采样对象输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，采样对象输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

采样对象输出

### 执行器

数字校正命令

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=5.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

使用 T=0.1 s 精确 Gd=(0.00451991z+0.00407643)/(z^2-1.73086805z+0.73344696) 与 D=6.1882(z-0.27594)/z。

### 示例数据（JSON）

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
    "input_signal_id": "数字校正命令",
    "output_signal_id": "采样对象输出",
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
    "stability": "令 数字校正命令 回到基线，核对 采样对象输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 采样对象输出 的首次有效方向与最终方向。",
    "delay": "从记录的 数字校正命令 边沿量到 采样对象输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字校正命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 160. 因果离散微分器的一拍延迟

### 控制问题描述

这是一个由采样器、数字控制器、保持器和连续或离散对象组成的数字控制系统。控制输入是采样误差序列，输出是由传感器或同步记录器连续获取的估计误差变化率响应。在多次小幅且可逆的试验中，估计误差变化率响应开始时就沿最终方向变化，不会先向相反方向运动；采样误差序列改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把采样误差序列恢复到基准值后，估计误差变化率响应最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的采样误差序列变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。采样误差序列与估计误差变化率响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，估计误差变化率响应的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

估计误差变化率响应

### 执行器

采样误差序列

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=6.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

0.5

### 示例数据（自然语言）

取 T=0.1 s、KTd=1，后向差分 u[k]=10(e[k]-e[k-1])；非因果前向差分只作离线比较。

### 示例数据（JSON）

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
    "input_signal_id": "采样误差序列",
    "output_signal_id": "估计误差变化率响应",
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
    "stability": "令 采样误差序列 回到基线，核对 估计误差变化率响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 估计误差变化率响应 的首次有效方向与最终方向。",
    "delay": "从记录的 采样误差序列 边沿量到 估计误差变化率响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 采样误差序列 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 161. 单摆平衡点与小信号稳定性

### 控制问题描述

这是一个由转轴、刚性杆和集中质量构成的摆动机械装置。控制输入是枢轴力矩，输出是由传感器或同步记录器连续获取的摆角与角速度。在多次小幅且可逆的试验中，摆角与角速度开始时就沿最终方向变化，不会先向相反方向运动；枢轴力矩改变后，摆角与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把枢轴力矩撤回基准值，摆角与角速度的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。当枢轴力矩的幅值或运行点改变时，摆杆几何和重力作用会随摆角改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。枢轴力矩与摆角与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

摆角与角速度

### 执行器

枢轴力矩

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 g=9.81 m/s^2、l=1 m，在 theta=0 与 pi 两平衡点施加 ±0.05 rad 扰动并运行 10 s。

### 示例数据（JSON）

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
      "枢轴力矩"
    ],
    "output_signal_ids": [
      "摆角与角速度通道 1",
      "摆角与角速度通道 2"
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
    "stability": "令 枢轴力矩 回到基线，核对 摆角与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 摆角与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 枢轴力矩 边沿量到 摆角与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 枢轴力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 162. 由实验力曲线线性化磁悬浮球

### 控制问题描述

这是一个由电磁铁吸引钢球并用位置传感器测量气隙的磁悬浮装置。控制输入是电磁铁电流微扰，输出是由传感器或同步记录器连续获取的小球位移、速度、线圈电流。在多次小幅且可逆的试验中，小球位移开始时就沿最终方向变化，不会先向相反方向运动；电磁铁电流微扰改变后，小球位移在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。即使把电磁铁电流微扰撤回基准值，小球位移的偏差仍会继续增大而不会自行返回，因此试验必须在越界前停止。当电磁铁电流微扰的幅值或运行点改变时，电磁力会随气隙和线圈电流改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。电磁铁电流微扰与小球位移、速度、线圈电流采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

小球位移、速度、线圈电流

### 执行器

电磁铁电流微扰

### 安全边界

max_abs_reference_normalized=0.1
max_abs_output_normalized=1.0
max_abs_actuator_normalized=0.75
max_test_duration_s=12.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 m=0.0084 kg、平衡电流 0.6 A、A=[[0,1],[1667,0]]、B=[0,47.6]；在工作点附近测试 ±10 mA。

### 示例数据（JSON）

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
      "电磁铁电流微扰"
    ],
    "output_signal_ids": [
      "小球位移",
      "速度"
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
    "stability": "令 电磁铁电流微扰 回到基线，核对 小球位移、速度、线圈电流 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 小球位移、速度、线圈电流 的首次有效方向与最终方向。",
    "delay": "从记录的 电磁铁电流微扰 边沿量到 小球位移、速度、线圈电流 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 电磁铁电流微扰 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 163. 平方根出流水箱的工作点线性化

### 控制问题描述

这是一个由进出流量、储液容积和液位测量共同决定动态的储液装置。控制输入是入口质量流量，输出是由传感器或同步记录器连续获取的水箱液位与出口流量。在多次小幅且可逆的试验中，水箱液位与出口流量开始时就沿最终方向变化，不会先向相反方向运动；入口质量流量改变后，水箱液位与出口流量在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把入口质量流量恢复到基准值后，水箱液位与出口流量最终会收敛或保持有界，不会出现自行增长的运动。改变入口质量流量的方向和幅值时，可以观察到固定的静态非线性，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。入口质量流量与水箱液位与出口流量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道结构。

### 可观察输出

水箱液位与出口流量

### 执行器

入口质量流量

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 A=1 m^2、rho=1000 kg/m^3、R=0.5、h0=1 m、pa=0；入口质量流量扰动 ±10 kg/s，并保持液位为正。

### 示例数据（JSON）

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
    "input_signal_id": "入口质量流量",
    "output_signal_id": "水箱液位与出口流量",
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
    "stability": "令 入口质量流量 回到基线，核对 水箱液位与出口流量 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 水箱液位与出口流量 的首次有效方向与最终方向。",
    "delay": "从记录的 入口质量流量 边沿量到 水箱液位与出口流量 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 入口质量流量 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 164. 计算力矩法消除单摆重力非线性

### 控制问题描述

这是一个由转轴、刚性杆和集中质量构成的摆动机械装置。控制输入是计算得到的枢轴力矩，输出是由传感器或同步记录器连续获取的摆角与角速度。在多次小幅且可逆的试验中，摆角与角速度开始时就沿最终方向变化，不会先向相反方向运动；计算得到的枢轴力矩改变后，摆角与角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把计算得到的枢轴力矩撤回基准值后，摆角与角速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。当计算得到的枢轴力矩的幅值或运行点改变时，摆杆几何和重力作用会随摆角改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。计算得到的枢轴力矩与摆角与角速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，摆角与角速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

摆角与角速度

### 执行器

计算得到的枢轴力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 m=l=1、g=9.81，计算力矩 Tc=mgl sin(theta)+u，u=-4(theta-r)-4 theta_dot；测试最大 ±1 rad 命令。

### 示例数据（JSON）

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
    "input_signal_id": "计算得到的枢轴力矩",
    "output_signal_id": "摆角与角速度",
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
    "stability": "令 计算得到的枢轴力矩 回到基线，核对 摆角与角速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 摆角与角速度 的首次有效方向与最终方向。",
    "delay": "从记录的 计算得到的枢轴力矩 边沿量到 摆角与角速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 计算得到的枢轴力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
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

## 165. RTP 灯功率平方律的逆补偿

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是灯电压命令，输出是由传感器或同步记录器连续获取的灯电压与输出功率。在多次小幅且可逆的试验中，灯电压与输出功率开始时就沿最终方向变化，不会先向相反方向运动；灯电压命令改变后，灯电压与输出功率在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把灯电压命令恢复到基准值后，灯电压与输出功率最终会收敛或保持有界，不会出现自行增长的运动。改变灯电压命令的方向和幅值时，可以观察到固定的静态非线性，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。灯电压命令与灯电压与输出功率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，灯电压与输出功率的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

灯电压与输出功率

### 执行器

灯电压命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

使用灯功率 P=V^2、电压 0..10 V、虚拟功率 0..100 W、逆映射 V=sqrt(Pcmd) 与热对象 G=1/(10s+1)。

### 示例数据（JSON）

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
    "input_signal_id": "灯电压命令",
    "output_signal_id": "灯电压与输出功率",
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
    "stability": "令 灯电压命令 回到基线，核对 灯电压与输出功率 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 灯电压与输出功率 的首次有效方向与最终方向。",
    "delay": "从记录的 灯电压命令 边沿量到 灯电压与输出功率 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 灯电压命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "P=V^2; V=sqrt(Pcmd)",
    "voltage_min_V": 0,
    "voltage_max_V": 10
  }
}
```

---

## 166. 执行器饱和导致的幅值相关超调

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是受幅值限制的命令，输出是由传感器或同步记录器连续获取的输出、误差、饱和控制量。在多次小幅且可逆的试验中，输出开始时就沿最终方向变化，不会先向相反方向运动；受幅值限制的命令改变后，输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把受幅值限制的命令撤回基准值后，输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。改变受幅值限制的命令的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。受幅值限制的命令与输出、误差、饱和控制量采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

输出、误差、饱和控制量

### 执行器

受幅值限制的命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=(s+1)/s^2、K=1、执行器对称限幅 ±0.4，阶跃幅值为 2、4、6、8、10、12。

### 示例数据（JSON）

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
    "input_signal_id": "受幅值限制的命令",
    "output_signal_id": "输出",
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
    "stability": "令 受幅值限制的命令 回到基线，核对 输出、误差、饱和控制量 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 输出、误差、饱和控制量 的首次有效方向与最终方向。",
    "delay": "从记录的 受幅值限制的命令 边沿量到 输出、误差、饱和控制量 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 受幅值限制的命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "u=clip(e,-0.4,0.4)",
    "limit": 0.4
  }
}
```

---

## 167. 条件稳定环路的饱和大信号失稳

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是饱和比例命令，输出是由传感器或同步记录器连续获取的受控输出、环路误差与饱和控制信号。在多次小幅且可逆的试验中，受控输出开始时就沿最终方向变化，不会先向相反方向运动；饱和比例命令改变后，受控输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把饱和比例命令撤回基准值后，受控输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。改变饱和比例命令的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。饱和比例命令与受控输出、环路误差与饱和控制信号采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，受控输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

受控输出、环路误差与饱和控制信号

### 执行器

饱和比例命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=(s+1)^2/s^3、K=2、饱和限幅 ±1，阶跃 1、2、3、3.5；状态越界立即停止。

### 示例数据（JSON）

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
    "input_signal_id": "饱和比例命令",
    "output_signal_id": "受控输出",
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
    "stability": "令 饱和比例命令 回到基线，核对 受控输出、环路误差与饱和控制信号 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受控输出、环路误差与饱和控制信号 的首次有效方向与最终方向。",
    "delay": "从记录的 饱和比例命令 边沿量到 受控输出、环路误差与饱和控制信号 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 饱和比例命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "unit-slope saturation +/-1",
    "nominal_gain": 2
  }
}
```

---

## 168. 柔性模态的饱和极限环与陷波消除

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是经陷波整形的限幅命令，输出是由传感器或同步记录器连续获取的柔性位移与饱和命令。在多次小幅且可逆的试验中，柔性位移与饱和命令开始时就沿最终方向变化，不会先向相反方向运动；经陷波整形的限幅命令改变后，柔性位移与饱和命令在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把经陷波整形的限幅命令撤回基准值后，柔性位移与饱和命令会保留偏差或继续漂移，而不会依靠自身作用回到原位。改变经陷波整形的限幅命令的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。经陷波整形的限幅命令与柔性位移与饱和命令采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，柔性位移与饱和命令的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

柔性位移与饱和命令

### 执行器

经陷波整形的限幅命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s^2+0.2s+1)]、K=0.5、饱和 ±0.1；比较加入陷波 123(s^2+0.18s+0.81)/(s+10)^2 前后。

### 示例数据（JSON）

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
    "input_signal_id": "经陷波整形的限幅命令",
    "output_signal_id": "柔性位移与饱和命令",
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
    "stability": "令 经陷波整形的限幅命令 回到基线，核对 柔性位移与饱和命令 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 柔性位移与饱和命令 的首次有效方向与最终方向。",
    "delay": "从记录的 经陷波整形的限幅命令 边沿量到 柔性位移与饱和命令 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 经陷波整形的限幅命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
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

## 169. 饱和 PI 积分器的回算反饱和

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是饱和 PI 命令，输出是由传感器或同步记录器连续获取的积分器输出、对象输出、执行器命令。在多次小幅且可逆的试验中，积分器输出开始时就沿最终方向变化，不会先向相反方向运动；饱和 PI 命令改变后，积分器输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把饱和 PI 命令撤回基准值后，积分器输出会保留偏差或继续漂移，而不会依靠自身作用回到原位。改变饱和 PI 命令的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。饱和 PI 命令与积分器输出、对象输出、执行器命令采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，积分器输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

积分器输出、对象输出、执行器命令

### 执行器

饱和 PI 命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取对象 1/s、PI kp=2、ki=4、执行器 ±1、回算 Ka=10；4 单位阶跃与 Ka=0 比较。

### 示例数据（JSON）

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
    "input_signal_id": "饱和 PI 命令",
    "output_signal_id": "积分器输出",
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
    "stability": "令 饱和 PI 命令 回到基线，核对 积分器输出、对象输出、执行器命令 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 积分器输出、对象输出、执行器命令 的首次有效方向与最终方向。",
    "delay": "从记录的 饱和 PI 命令 边沿量到 积分器输出、对象输出、执行器命令 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 饱和 PI 命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
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

## 170. 饱和非线性的描述函数

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是有界正弦非线性测试，输出是由传感器或同步记录器连续获取的非线性输入与基波输出。在多次小幅且可逆的试验中，非线性输入与基波输出开始时就沿最终方向变化，不会先向相反方向运动；有界正弦非线性测试改变后，非线性输入与基波输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界正弦非线性测试恢复到基准值后，非线性输入与基波输出最终会收敛或保持有界，不会出现自行增长的运动。改变有界正弦非线性测试的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。有界正弦非线性测试与非线性输入与基波输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，非线性输入与基波输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

非线性输入与基波输出

### 执行器

有界正弦非线性测试

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取饱和斜率 k=1、限幅 N=0.1，1 rad/s 正弦幅值为 0.05、0.1、0.2、0.5、1，并提取基波。

### 示例数据（JSON）

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
    "input_signal_id": "有界正弦非线性测试",
    "output_signal_id": "非线性输入与基波输出",
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
    "stability": "令 有界正弦非线性测试 回到基线，核对 非线性输入与基波输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 非线性输入与基波输出 的首次有效方向与最终方向。",
    "delay": "从记录的 有界正弦非线性测试 边沿量到 非线性输入与基波输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界正弦非线性测试 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "clip(k*x,-N,N)",
    "k": 1,
    "N": 0.1
  }
}
```

---

## 171. 理想继电器的描述函数

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是二值继电命令，输出是由传感器或同步记录器连续获取的继电器输入与基波输出。在多次小幅且可逆的试验中，继电器输入与基波输出开始时就沿最终方向变化，不会先向相反方向运动；二值继电命令改变后，继电器输入与基波输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把二值继电命令恢复到基准值后，继电器输入与基波输出最终会收敛或保持有界，不会出现自行增长的运动。改变二值继电命令的方向和幅值时，可以观察到固定的继电开关规律，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。二值继电命令与继电器输入与基波输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，继电器输入与基波输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

继电器输入与基波输出

### 执行器

二值继电命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取理想继电器输出 ±1，正弦幅值 0.25、0.5、1、2；提取基波及奇次谐波。

### 示例数据（JSON）

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
    "input_signal_id": "二值继电命令",
    "output_signal_id": "继电器输入与基波输出",
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
    "stability": "令 二值继电命令 回到基线，核对 继电器输入与基波输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 继电器输入与基波输出 的首次有效方向与最终方向。",
    "delay": "从记录的 二值继电命令 边沿量到 继电器输入与基波输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 二值继电命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "y=sign(x)",
    "N": 1
  }
}
```

---

## 172. 带滞环继电器的复描述函数

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是滞环继电命令，输出是由传感器或同步记录器连续获取的滞环输入与基波输出。在多次小幅且可逆的试验中，滞环输入与基波输出开始时就沿最终方向变化，不会先向相反方向运动；滞环继电命令改变后，滞环输入与基波输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把滞环继电命令恢复到基准值后，滞环输入与基波输出最终会收敛或保持有界，不会出现自行增长的运动。改变滞环继电命令的方向和幅值时，可以观察到固定滞环和继电切换，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。滞环继电命令与滞环输入与基波输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，滞环输入与基波输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

滞环输入与基波输出

### 执行器

滞环继电命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取继电器输出 ±1、滞环半宽 h=0.1，正弦幅值 0.08、0.12、0.24、0.5；保留继电器记忆。

### 示例数据（JSON）

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
    "input_signal_id": "滞环继电命令",
    "output_signal_id": "滞环输入与基波输出",
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
    "stability": "令 滞环继电命令 回到基线，核对 滞环输入与基波输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 滞环输入与基波输出 的首次有效方向与最终方向。",
    "delay": "从记录的 滞环继电命令 边沿量到 滞环输入与基波输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 滞环继电命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "relay +/-N with thresholds +/-h",
    "N": 1,
    "h": 0.1
  }
}
```

---

## 173. 用 Nyquist 与描述函数预测饱和极限环

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是饱和环路命令，输出是由传感器或同步记录器连续获取的振荡幅值与频率。在多次小幅且可逆的试验中，振荡幅值与频率开始时就沿最终方向变化，不会先向相反方向运动；饱和环路命令改变后，振荡幅值与频率在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把饱和环路命令撤回基准值后，振荡幅值与频率会保留偏差或继续漂移，而不会依靠自身作用回到原位。改变饱和环路命令的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。饱和环路命令与振荡幅值与频率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，振荡幅值与频率的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

振荡幅值与频率

### 执行器

饱和环路命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s^2+0.2s+1)] 与饱和 k=1、N=0.1；从幅值 0.3、0.63、0.9 附近启动并测稳态振荡。

### 示例数据（JSON）

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
    "input_signal_id": "饱和环路命令",
    "output_signal_id": "振荡幅值与频率",
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
    "stability": "令 饱和环路命令 回到基线，核对 振荡幅值与频率 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 振荡幅值与频率 的首次有效方向与最终方向。",
    "delay": "从记录的 饱和环路命令 边沿量到 振荡幅值与频率 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 饱和环路命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "unit-slope saturation +/-0.1"
  }
}
```

---

## 174. 用复描述函数预测滞环极限环

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是带滞环继电器命令，输出是由传感器或同步记录器连续获取的滞环振荡幅值与频率。在多次小幅且可逆的试验中，滞环振荡幅值与频率开始时就沿最终方向变化，不会先向相反方向运动；带滞环继电器命令改变后，滞环振荡幅值与频率在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把带滞环继电器命令撤回基准值后，滞环振荡幅值与频率会保留偏差或继续漂移，而不会依靠自身作用回到原位。改变带滞环继电器命令的方向和幅值时，可以观察到固定滞环和继电切换，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。带滞环继电器命令与滞环振荡幅值与频率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，滞环振荡幅值与频率的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

滞环振荡幅值与频率

### 执行器

带滞环继电器命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 G=1/[s(s+1)]、继电器 N=1、h=0.1；从多个继电器初始状态仿真并测量极限环。

### 示例数据（JSON）

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
    "input_signal_id": "带滞环继电器命令",
    "output_signal_id": "滞环振荡幅值与频率",
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
    "stability": "令 带滞环继电器命令 回到基线，核对 滞环振荡幅值与频率 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 滞环振荡幅值与频率 的首次有效方向与最终方向。",
    "delay": "从记录的 带滞环继电器命令 边沿量到 滞环振荡幅值与频率 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 带滞环继电器命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "relay +/-1 with thresholds +/-0.1"
  }
}
```

---

## 175. 双积分器最短时间开关与 PTOS

### 控制问题描述

这是一个在水平轨道上运动的低摩擦小车，装置带有双向驱动且几乎没有被动恢复力。控制输入是有界加速度命令，输出是由传感器或同步记录器连续获取的位置与速度。在多次小幅且可逆的试验中，位置与速度开始时就沿最终方向变化，不会先向相反方向运动；有界加速度命令改变后，位置与速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界加速度命令撤回基准值后，位置与速度会保留偏差或继续漂移，而不会依靠自身作用回到原位。改变有界加速度命令的方向和幅值时，可以观察到固定的静态非线性，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。有界加速度命令与位置与速度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，位置与速度的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

位置与速度

### 执行器

有界加速度命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取双积分器、|u|≤1，初态 (1,0)、(1,-1)、(-1,1)；比较 bang-bang 切换与带平滑区的 PTOS。

### 示例数据（JSON）

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
    "input_signal_id": "有界加速度命令",
    "output_signal_id": "位置与速度",
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
    "stability": "令 有界加速度命令 回到基线，核对 位置与速度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 位置与速度 的首次有效方向与最终方向。",
    "delay": "从记录的 有界加速度命令 边沿量到 位置与速度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界加速度命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "u=-sign(x1+0.5*x2*abs(x2)), clipped +/-1"
  }
}
```

---

## 176. Lyapunov 方程证明参数化二阶稳定性

### 控制问题描述

这是一个轨迹会旋转并衰减、且两种运动速率分别由两个物理参数决定的二状态自治线性系统。控制输入是给定初态释放，输出是由传感器或同步记录器连续获取的状态轨迹与衰减行为。在多次小幅且可逆的试验中，状态轨迹与衰减行为开始时就沿最终方向变化，不会先向相反方向运动；给定初态释放改变后，状态轨迹与衰减行为在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把给定初态释放恢复到基准值后，状态轨迹与衰减行为最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的给定初态释放变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。给定初态释放与状态轨迹与衰减行为采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，状态轨迹与衰减行为的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

状态轨迹与衰减行为

### 执行器

给定初态释放

### 安全边界

max_abs_reference_normalized=0.5
max_abs_output_normalized=2.0
max_abs_actuator_normalized=1.5
max_test_duration_s=20.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
把归一化激励增大到规定局部工作区间之外

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 alpha=1、beta=2、A=[[-1,2],[-2,-1]]、Q=I，并从半径 0.5、1、2 的初态运行。

### 示例数据（JSON）

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
      "给定初态释放"
    ],
    "output_signal_ids": [
      "状态轨迹与衰减行为通道 1",
      "状态轨迹与衰减行为通道 2"
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
    "stability": "令 给定初态释放 回到基线，核对 状态轨迹与衰减行为 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 状态轨迹与衰减行为 的首次有效方向与最终方向。",
    "delay": "从记录的 给定初态释放 边沿量到 状态轨迹与衰减行为 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 给定初态释放 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 177. 非线性位置反馈的直接 Lyapunov 构造

### 控制问题描述

这是一个由位置误差产生非线性恢复作用、同时具有速度耗散的阻尼位置伺服系统。控制输入是非线性恢复反馈，输出是由传感器或同步记录器连续获取的位置误差、速度与状态轨迹。在多次小幅且可逆的试验中，位置误差开始时就沿最终方向变化，不会先向相反方向运动；非线性恢复反馈改变后，位置误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把非线性恢复反馈恢复到基准值后，位置误差最终会收敛或保持有界，不会出现自行增长的运动。当非线性恢复反馈的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。非线性恢复反馈与位置误差、速度与状态轨迹采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，位置误差的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

位置误差、速度与状态轨迹

### 执行器

非线性恢复反馈

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取 T=1、f(e)=e+e^3；从 e=±2、x2=±1 仿真，并计算 V=0.5e^2+0.25e^4+0.5x2^2。

### 示例数据（JSON）

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
      "非线性恢复反馈"
    ],
    "output_signal_ids": [
      "位置误差",
      "速度与状态轨迹"
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
    "stability": "令 非线性恢复反馈 回到基线，核对 位置误差、速度与状态轨迹 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 位置误差、速度与状态轨迹 的首次有效方向与最终方向。",
    "delay": "从记录的 非线性恢复反馈 边沿量到 位置误差、速度与状态轨迹 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 非线性恢复反馈 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "f(e)=e+e^3"
  }
}
```

---

## 178. 符号非线性的扇区界

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是有界符号函数测试信号，输出是由传感器或同步记录器连续获取的非线性输入与输出。在多次小幅且可逆的试验中，非线性输入与输出开始时就沿最终方向变化，不会先向相反方向运动；有界符号函数测试信号改变后，非线性输入与输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把有界符号函数测试信号恢复到基准值后，非线性输入与输出最终会收敛或保持有界，不会出现自行增长的运动。改变有界符号函数测试信号的方向和幅值时，可以观察到固定的符号函数规律，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。有界符号函数测试信号与非线性输入与输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，非线性输入与输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

非线性输入与输出

### 执行器

有界符号函数测试信号

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

对 f(e)=sign(e) 在 1e-3–10 的对数幅值上计算割线斜率 f(e)/e。

### 示例数据（JSON）

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
    "input_signal_id": "有界符号函数测试信号",
    "output_signal_id": "非线性输入与输出",
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
    "stability": "令 有界符号函数测试信号 回到基线，核对 非线性输入与输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 非线性输入与输出 的首次有效方向与最终方向。",
    "delay": "从记录的 有界符号函数测试信号 边沿量到 非线性输入与输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 有界符号函数测试信号 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
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

## 179. 执行器饱和的扇区界

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是限幅执行器命令，输出是由传感器或同步记录器连续获取的饱和环节输入与输出。在多次小幅且可逆的试验中，饱和环节输入与输出开始时就沿最终方向变化，不会先向相反方向运动；限幅执行器命令改变后，饱和环节输入与输出在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把限幅执行器命令恢复到基准值后，饱和环节输入与输出最终会收敛或保持有界，不会出现自行增长的运动。改变限幅执行器命令的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。限幅执行器命令与饱和环节输入与输出采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，饱和环节输入与输出的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

饱和环节输入与输出

### 执行器

限幅执行器命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

对单位斜率、限幅 ±0.1 的饱和器，在 0.01–10 幅值上逐点核对扇区不等式。

### 示例数据（JSON）

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
    "input_signal_id": "限幅执行器命令",
    "output_signal_id": "饱和环节输入与输出",
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
    "stability": "令 限幅执行器命令 回到基线，核对 饱和环节输入与输出 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 饱和环节输入与输出 的首次有效方向与最终方向。",
    "delay": "从记录的 限幅执行器命令 边沿量到 饱和环节输入与输出 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 限幅执行器命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
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

## 180. 用圆判据认证饱和环路绝对稳定

### 控制问题描述

这是一个由线性动态对象和受限或开关型执行环节组成的非线性反馈系统。控制输入是扇区有界执行器命令，输出是由传感器或同步记录器连续获取的环路输入、输出与闭环响应。在多次小幅且可逆的试验中，环路输入开始时就沿最终方向变化，不会先向相反方向运动；扇区有界执行器命令改变后，环路输入在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把扇区有界执行器命令恢复到基准值后，环路输入最终会收敛或保持有界，不会出现自行增长的运动。改变扇区有界执行器命令的方向和幅值时，可以观察到固定的执行器限幅，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。扇区有界执行器命令与环路输入、输出与闭环响应采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，环路输入的运动方向、响应时机和最终水平都几乎不变。

### 可观察输出

环路输入、输出与闭环响应

### 执行器

扇区有界执行器命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=16.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

2.0

### 示例数据（自然语言）

取线性块 G=(s+1)^2/s^3 与扇区 [0,1] 单位饱和；绘制 Nyquist 与 Re(G)=-1 边界并仿真有界初态。

### 示例数据（JSON）

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
    "input_signal_id": "扇区有界执行器命令",
    "output_signal_id": "环路输入",
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
    "stability": "令 扇区有界执行器命令 回到基线，核对 环路输入、输出与闭环响应 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 环路输入、输出与闭环响应 的首次有效方向与最终方向。",
    "delay": "从记录的 扇区有界执行器命令 边沿量到 环路输入、输出与闭环响应 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 扇区有界执行器命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "unit-slope saturation in sector [0,1]"
  }
}
```

---

## 181. 柔性双体卫星建模与设计指标转换

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是机体控制力矩，输出是由传感器或同步记录器连续获取的两卫星体角度、角速度、指向误差。在多次小幅且可逆的试验中，两卫星体角度开始时就沿最终方向变化，不会先向相反方向运动；机体控制力矩改变后，两卫星体角度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把机体控制力矩撤回基准值后，两卫星体角度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的机体控制力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。机体控制力矩与两卫星体角度、角速度、指向误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

两卫星体角度、角速度、指向误差

### 执行器

机体控制力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取 J1=1、J2=0.1、k=0.091、b=0.0036 与 G=0.036(s+25)/[s^2(s^2+0.04s+1)]；测试 k,b 边界及指向阶跃。

### 示例数据（JSON）

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
    "input_signal_id": "机体控制力矩",
    "output_signal_id": "两卫星体角度",
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
    "stability": "令 机体控制力矩 回到基线，核对 两卫星体角度、角速度、指向误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 两卫星体角度、角速度、指向误差 的首次有效方向与最终方向。",
    "delay": "从记录的 机体控制力矩 边沿量到 两卫星体角度、角速度、指向误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 机体控制力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 182. 柔性卫星的增益稳定与陷波相位稳定比较

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是增益整形或陷波整形力矩，输出是由传感器或同步记录器连续获取的卫星指向与柔性挠曲。在多次小幅且可逆的试验中，卫星指向与柔性挠曲开始时就沿最终方向变化，不会先向相反方向运动；增益整形或陷波整形力矩改变后，卫星指向与柔性挠曲在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把增益整形或陷波整形力矩撤回基准值后，卫星指向与柔性挠曲会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的增益整形或陷波整形力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。增益整形或陷波整形力矩与卫星指向与柔性挠曲采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

卫星指向与柔性挠曲

### 执行器

增益整形或陷波整形力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

在名义柔性卫星上比较 Dc1=0.25(2s+1)、Dc2=0.001(30s+1)、Dc3=Dc1[((s/0.9)^2+1)/(s/25+1)^2]，并覆盖所有 k,b 边界。

### 示例数据（JSON）

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
    "input_signal_id": "增益整形或陷波整形力矩",
    "output_signal_id": "卫星指向与柔性挠曲",
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
    "stability": "令 增益整形或陷波整形力矩 回到基线，核对 卫星指向与柔性挠曲 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 卫星指向与柔性挠曲 的首次有效方向与最终方向。",
    "delay": "从记录的 增益整形或陷波整形力矩 边沿量到 卫星指向与柔性挠曲 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 增益整形或陷波整形力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 183. 卫星对称根轨迹状态反馈与估计器

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是估计状态反馈力矩，输出是由传感器或同步记录器连续获取的测量姿态与估计柔性状态。在多次小幅且可逆的试验中，测量姿态与估计柔性状态开始时就沿最终方向变化，不会先向相反方向运动；估计状态反馈力矩改变后，测量姿态与估计柔性状态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把估计状态反馈力矩撤回基准值后，测量姿态与估计柔性状态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的估计状态反馈力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。估计状态反馈力矩与测量姿态与估计柔性状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

测量姿态与估计柔性状态

### 执行器

估计状态反馈力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取控制极点 -0.45±j0.34、-0.15±j1.05，K=[-0.2788,0.0546,0.6814,1.1655]、L=[222,42.3,1515.4,5503.9]。

### 示例数据（JSON）

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
    "input_signal_id": "估计状态反馈力矩",
    "output_signal_id": "测量姿态与估计柔性状态",
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
    "stability": "令 估计状态反馈力矩 回到基线，核对 测量姿态与估计柔性状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 测量姿态与估计柔性状态 的首次有效方向与最终方向。",
    "delay": "从记录的 估计状态反馈力矩 边沿量到 测量姿态与估计柔性状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 估计状态反馈力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 184. 传感器与执行器共址的卫星重设计

### 控制问题描述

这是一个由刚性本体、姿态执行机构和必要柔性附件组成的航天器姿态控制系统。控制输入是共址机体力矩，输出是由传感器或同步记录器连续获取的共址姿态与远端柔性角。在多次小幅且可逆的试验中，共址姿态与远端柔性角开始时就沿最终方向变化，不会先向相反方向运动；共址机体力矩改变后，共址姿态与远端柔性角在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把共址机体力矩撤回基准值后，共址姿态与远端柔性角会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的共址机体力矩变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。共址机体力矩与共址姿态与远端柔性角采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

共址姿态与远端柔性角

### 执行器

共址机体力矩

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
对临界稳定或不稳定模态施加无界开环命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

使用共址 Gco=[(s+0.018)^2+0.954^2]/{s^2[(s+0.02)^2+1]} 与控制器 0.25(2s+1)，并与远端传感比较。

### 示例数据（JSON）

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
    "input_signal_id": "共址机体力矩",
    "output_signal_id": "共址姿态与远端柔性角",
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
    "stability": "令 共址机体力矩 回到基线，核对 共址姿态与远端柔性角 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 共址姿态与远端柔性角 的首次有效方向与最终方向。",
    "delay": "从记录的 共址机体力矩 边沿量到 共址姿态与远端柔性角 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 共址机体力矩 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 185. 波音 747 纵横向线性化与模态识别

### 控制问题描述

这是一个由气动力、舵面执行机构和机载运动传感器组成的飞机飞行控制系统。控制输入是方向舵、升降舵、副翼、推力，输出是由传感器或同步记录器连续获取的飞机角速度、姿态、速度、高度。在多次小幅且可逆的试验中，飞机角速度开始时就沿最终方向变化，不会先向相反方向运动；方向舵、升降舵、副翼、推力改变后，飞机角速度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把方向舵、升降舵、副翼、推力恢复到基准值后，飞机角速度最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的方向舵、升降舵、副翼、推力变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。方向舵、升降舵、副翼、推力与飞机角速度、姿态、速度、高度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；系统具有多个相互作用的通道，改变任一执行器都会明显改变多个输出。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

飞机角速度、姿态、速度、高度

### 执行器

方向舵、升降舵、副翼、推力

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
首次辨识测试时同时改变多个执行器通道

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

采用代表荷兰滚 wn=1 rad/s、zeta=0.03，并记录螺旋、滚转、长周期、短周期模态估计；方向舵与升降舵分开激励。

### 示例数据（JSON）

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
    "input_signal_id": "方向舵",
    "output_signal_id": "飞机角速度",
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
    "stability": "令 方向舵、升降舵、副翼、推力 回到基线，核对 飞机角速度、姿态、速度、高度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 飞机角速度、姿态、速度、高度 的首次有效方向与最终方向。",
    "delay": "从记录的 方向舵、升降舵、副翼、推力 边沿量到 飞机角速度、姿态、速度、高度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 方向舵、升降舵、副翼、推力 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 186. 含执行器与洗出环节的偏航阻尼器

### 控制问题描述

这是一个由船体偏航运动、舵机和航向传感器组成的水面航行器控制系统。控制输入是方向舵命令，输出是由传感器或同步记录器连续获取的偏航率、侧滑角、方向舵位置。在多次小幅且可逆的试验中，偏航率开始时就沿最终方向变化，不会先向相反方向运动；方向舵命令改变后，偏航率在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把方向舵命令恢复到基准值后，偏航率最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的方向舵命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。方向舵命令与偏航率、侧滑角、方向舵位置采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

偏航率、侧滑角、方向舵位置

### 执行器

方向舵命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取偏航增益 Kr=2.6、洗出 s/(s+1/3)、方向舵舵机 10/(s+10)；测试偏航率脉冲与稳态转弯命令。

### 示例数据（JSON）

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
    "input_signal_id": "方向舵命令",
    "output_signal_id": "偏航率",
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
    "stability": "令 方向舵命令 回到基线，核对 偏航率、侧滑角、方向舵位置 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 偏航率、侧滑角、方向舵位置 的首次有效方向与最终方向。",
    "delay": "从记录的 方向舵命令 边沿量到 偏航率、侧滑角、方向舵位置 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 方向舵命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 187. 实用偏航阻尼器与高阶状态估计方案比较

### 控制问题描述

这是一个由船体偏航运动、舵机和航向传感器组成的水面航行器控制系统。控制输入是低阶或高阶控制的方向舵命令，输出是由传感器或同步记录器连续获取的偏航率与估计横侧向状态。在多次小幅且可逆的试验中，偏航率与估计横侧向状态开始时就沿最终方向变化，不会先向相反方向运动；低阶或高阶控制的方向舵命令改变后，偏航率与估计横侧向状态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把低阶或高阶控制的方向舵命令恢复到基准值后，偏航率与估计横侧向状态最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的低阶或高阶控制的方向舵命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。低阶或高阶控制的方向舵命令与偏航率与估计横侧向状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

偏航率与估计横侧向状态

### 执行器

低阶或高阶控制的方向舵命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

比较 Kr=2.6 的实用偏航阻尼器与六状态反馈 K=[1.059,-0.191,-2.32,0.0992,0.037,0.486] 及其估计器，并注入传感噪声。

### 示例数据（JSON）

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
    "input_signal_id": "低阶或高阶控制的方向舵命令",
    "output_signal_id": "偏航率与估计横侧向状态",
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
    "stability": "令 低阶或高阶控制的方向舵命令 回到基线，核对 偏航率与估计横侧向状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 偏航率与估计横侧向状态 的首次有效方向与最终方向。",
    "delay": "从记录的 低阶或高阶控制的方向舵命令 边沿量到 偏航率与估计横侧向状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 低阶或高阶控制的方向舵命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 188. 俯仰内环与高度外环的高度保持

### 控制问题描述

这是一个由气动力、舵面执行机构和机载运动传感器组成的飞机飞行控制系统。控制输入是升降舵命令，输出是由传感器或同步记录器连续获取的高度、俯仰角、俯仰率。在多次小幅且可逆的试验中，高度开始时会先沿不利或相反方向运动，随后才转向；升降舵命令改变后，高度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把升降舵命令撤回基准值后，高度会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的升降舵命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。升降舵命令与高度、俯仰角、俯仰率采用同一时钟记录，因此这些同步记录足以重建所有相关运动；外层运动只能通过一个单独稳定的内环产生，内外环具有不同的时间尺度。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

高度、俯仰角、俯仰率

### 执行器

升降舵命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
测试外环命令时关闭内层稳定通道

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

使用含 RHP 零点 +5.61 的高度通道、快速俯仰内环、较慢高度外环，并与全状态 K=[-0.0009,0.0016,-1.883,-7.603,-0.001] 比较。

### 示例数据（JSON）

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
    "input_signal_id": "升降舵命令",
    "output_signal_id": "高度",
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
    "stability": "令 升降舵命令 回到基线，核对 高度、俯仰角、俯仰率 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 高度、俯仰角、俯仰率 的首次有效方向与最终方向。",
    "delay": "从记录的 升降舵命令 边沿量到 高度、俯仰角、俯仰率 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 升降舵命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 189. 含迟延燃油空气过程的 PI 整定

### 控制问题描述

这是一个由燃油喷射、发动机进气过程和排气氧传感器组成的汽车燃空比控制系统。控制输入是燃油喷射命令，输出是由传感器或同步记录器连续获取的燃空比与氧传感器信号。在多次小幅且可逆的试验中，燃空比与氧传感器信号开始时就沿最终方向变化，不会先向相反方向运动；燃油喷射命令改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把燃油喷射命令恢复到基准值后，燃空比与氧传感器信号最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的燃油喷射命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。燃油喷射命令与燃空比与氧传感器信号采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

燃空比与氧传感器信号

### 执行器

燃油喷射命令

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取燃油快/慢时间常数 0.02、1 s、各权重 0.5、运输迟延 0.2 s、传感器滞后 0.1 s、PI 聚合增益 KsKp=2.2。

### 示例数据（JSON）

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
    "input_signal_id": "燃油喷射命令",
    "output_signal_id": "燃空比与氧传感器信号",
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
    "stability": "令 燃油喷射命令 回到基线，核对 燃空比与氧传感器信号 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 燃空比与氧传感器信号 的首次有效方向与最终方向。",
    "delay": "从记录的 燃油喷射命令 边沿量到 燃空比与氧传感器信号 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 燃油喷射命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 190. 非线性氧传感器导致的极限环

### 控制问题描述

这是一个由燃油喷射、发动机进气过程和排气氧传感器组成的汽车燃空比控制系统。控制输入是燃油喷射命令，输出是由传感器或同步记录器连续获取的空燃误差与氧传感器振荡。在多次小幅且可逆的试验中，空燃误差与氧传感器振荡开始时就沿最终方向变化，不会先向相反方向运动；燃油喷射命令改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把燃油喷射命令恢复到基准值后，空燃误差与氧传感器振荡最终会收敛或保持有界，不会出现自行增长的运动。改变燃油喷射命令的方向和幅值时，可以观察到固定的静态非线性，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。燃油喷射命令与空燃误差与氧传感器振荡采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

空燃误差与氧传感器振荡

### 执行器

燃油喷射命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

使用燃空动态、氧传感器输出 0.1..0.9、中心斜率 20、Kp=0.1、小信号环增益 6，并保留饱和；测量极限环。

### 示例数据（JSON）

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
    "input_signal_id": "燃油喷射命令",
    "output_signal_id": "空燃误差与氧传感器振荡",
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
    "stability": "令 燃油喷射命令 回到基线，核对 空燃误差与氧传感器振荡 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 空燃误差与氧传感器振荡 的首次有效方向与最终方向。",
    "delay": "从记录的 燃油喷射命令 边沿量到 空燃误差与氧传感器振荡 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 燃油喷射命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
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

## 191. 继电整形实现稳健平均化学计量比

### 控制问题描述

这是一个由燃油喷射、发动机进气过程和排气氧传感器组成的汽车燃空比控制系统。控制输入是经继电整形传感通道的燃油喷射命令，输出是由传感器或同步记录器连续获取的平均燃空比与切换信号。在多次小幅且可逆的试验中，平均燃空比与切换信号开始时就沿最终方向变化，不会先向相反方向运动；经继电整形传感通道的燃油喷射命令改变后，命令与首次变化之间有一段清楚可见的静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把经继电整形传感通道的燃油喷射命令恢复到基准值后，平均燃空比与切换信号最终会收敛或保持有界，不会出现自行增长的运动。改变经继电整形传感通道的燃油喷射命令的方向和幅值时，可以观察到固定的继电开关规律，但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。经继电整形传感通道的燃油喷射命令与平均燃空比与切换信号采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

平均燃空比与切换信号

### 执行器

经继电整形传感通道的燃油喷射命令

### 安全边界

max_abs_reference_normalized=0.25
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
迟延响应尚未显现时再次增大命令

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

采用继电 q=N sign(vs-vstar)，示例取 N=0.05，沿用燃空/PI 动态，并把传感器斜率乘 0.5、1、2。

### 示例数据（JSON）

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
    "input_signal_id": "经继电整形传感通道的燃油喷射命令",
    "output_signal_id": "平均燃空比与切换信号",
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
    "stability": "令 经继电整形传感通道的燃油喷射命令 回到基线，核对 平均燃空比与切换信号 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 平均燃空比与切换信号 的首次有效方向与最终方向。",
    "delay": "从记录的 经继电整形传感通道的燃油喷射命令 边沿量到 平均燃空比与切换信号 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 经继电整形传感通道的燃油喷射命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "q=0.05*sign(vs-vstar)",
    "relay_height": 0.05
  }
}
```

---

## 192. 四旋翼解耦轴模型与旋翼混控

### 控制问题描述

这是一个由机体、旋翼和惯性运动状态组成的多旋翼飞行器控制系统。控制输入是四个旋翼推力命令，输出是由传感器或同步记录器连续获取的位置、姿态、角速度、高度。在多次小幅且可逆的试验中，位置开始时就沿最终方向变化，不会先向相反方向运动；四个旋翼推力命令改变后，位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把四个旋翼推力命令撤回基准值后，位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的四个旋翼推力命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。四个旋翼推力命令与位置、姿态、角速度、高度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；系统具有多个相互作用的通道，改变任一执行器都会明显改变多个输出。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

位置、姿态、角速度、高度

### 执行器

四个旋翼推力命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
首次辨识测试时同时改变多个执行器通道

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

使用质量 1 kg、Iyy=0.02 kg*m^2 的 VTOL/四旋翼切片，推力 0..20 N、力矩 ±1 Nm；记录全部状态并逐列测试旋翼混控。

### 示例数据（JSON）

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
      "四个旋翼推力命令通道 1",
      "四个旋翼推力命令通道 2"
    ],
    "output_signal_ids": [
      "位置",
      "姿态",
      "角速度",
      "高度通道 1",
      "高度通道 2",
      "高度通道 3"
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
    "stability": "令 四个旋翼推力命令 回到基线，核对 位置、姿态、角速度、高度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 位置、姿态、角速度、高度 的首次有效方向与最终方向。",
    "delay": "从记录的 四个旋翼推力命令 边沿量到 位置、姿态、角速度、高度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 四个旋翼推力命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 193. 四旋翼姿态内环与位置外环串级 PD

### 控制问题描述

这是一个由机体、旋翼和惯性运动状态组成的多旋翼飞行器控制系统。控制输入是混控后的旋翼推力，输出是由传感器或同步记录器连续获取的四旋翼位置、姿态、轨迹误差。在多次小幅且可逆的试验中，四旋翼位置开始时就沿最终方向变化，不会先向相反方向运动；混控后的旋翼推力改变后，四旋翼位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把混控后的旋翼推力撤回基准值后，四旋翼位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的混控后的旋翼推力变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。混控后的旋翼推力与四旋翼位置、姿态、轨迹误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；外层运动只能通过一个单独稳定的内环产生，内外环具有不同的时间尺度。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

四旋翼位置、姿态、轨迹误差

### 执行器

混控后的旋翼推力

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
测试外环命令时关闭内层稳定通道

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

取 Gtheta=0.4(s+0.25)/[(s^2-3.2s+10.4)(s+3.4)(s+20)]、Gx=-131/[s 乘同一分母]；姿态内环快于位置外环。

### 示例数据（JSON）

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
    "input_signal_id": "混控后的旋翼推力",
    "output_signal_id": "四旋翼位置",
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
    "stability": "令 混控后的旋翼推力 回到基线，核对 四旋翼位置、姿态、轨迹误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 四旋翼位置、姿态、轨迹误差 的首次有效方向与最终方向。",
    "delay": "从记录的 混控后的旋翼推力 边沿量到 四旋翼位置、姿态、轨迹误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 混控后的旋翼推力 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 194. 四旋翼各轴 LQR 与状态估计器

### 控制问题描述

这是一个由机体、旋翼和惯性运动状态组成的多旋翼飞行器控制系统。控制输入是LQR 混控旋翼命令，输出是由传感器或同步记录器连续获取的测量与估计的四旋翼轴状态。在多次小幅且可逆的试验中，测量与估计的四旋翼轴状态开始时就沿最终方向变化，不会先向相反方向运动；LQR 混控旋翼命令改变后，测量与估计的四旋翼轴状态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应至少涉及三个连续的储能或积分过程。把LQR 混控旋翼命令撤回基准值后，测量与估计的四旋翼轴状态会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的LQR 混控旋翼命令变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。LQR 混控旋翼命令与测量与估计的四旋翼轴状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；系统具有多个相互作用的通道，改变任一执行器都会明显改变多个输出。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

测量与估计的四旋翼轴状态

### 执行器

LQR 混控旋翼命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
首次辨识测试时同时改变多个执行器通道

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

使用完整 VTOL 状态与约束，并把给出的纵向/侧向/偏航 LQR 增益对应的 rho 与估计器 q 乘 0.1、1、10 比较。

### 示例数据（JSON）

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
      "LQR 混控旋翼命令通道 1",
      "LQR 混控旋翼命令通道 2"
    ],
    "output_signal_ids": [
      "测量与估计的四旋翼轴状态通道 1",
      "测量与估计的四旋翼轴状态通道 2",
      "测量与估计的四旋翼轴状态通道 3",
      "测量与估计的四旋翼轴状态通道 4",
      "测量与估计的四旋翼轴状态通道 5",
      "测量与估计的四旋翼轴状态通道 6"
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
    "stability": "令 LQR 混控旋翼命令 回到基线，核对 测量与估计的四旋翼轴状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 测量与估计的四旋翼轴状态 的首次有效方向与最终方向。",
    "delay": "从记录的 LQR 混控旋翼命令 边沿量到 测量与估计的四旋翼轴状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 LQR 混控旋翼命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 195. RTP 辐射传导非线性与三状态小信号模型

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是三盏灯的公共命令，输出是由传感器或同步记录器连续获取的板中心与支撑处温度。在多次小幅且可逆的试验中，板中心与支撑处温度开始时就沿最终方向变化，不会先向相反方向运动；三盏灯的公共命令改变后，板中心与支撑处温度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把三盏灯的公共命令恢复到基准值后，板中心与支撑处温度最终会收敛或保持有界，不会出现自行增长的运动。当三盏灯的公共命令的幅值或运行点改变时，辐射换热、灯效率和可用冷却能力会随温度改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。三盏灯的公共命令与板中心与支撑处温度采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

板中心与支撑处温度

### 执行器

三盏灯的公共命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

使用 RTP 三状态公共输入传函 0.5226(s+0.0876)(s+0.1438)/[(s+0.1482)(s+0.0863)(s+0.0527)]，测试三档灯功率。

### 示例数据（JSON）

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
    "input_signal_id": "三盏灯的公共命令",
    "output_signal_id": "板中心与支撑处温度",
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
    "stability": "令 三盏灯的公共命令 回到基线，核对 板中心与支撑处温度 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 板中心与支撑处温度 的首次有效方向与最终方向。",
    "delay": "从记录的 三盏灯的公共命令 边沿量到 板中心与支撑处温度 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 三盏灯的公共命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "radiation terms proportional to absolute temperature^4"
  }
}
```

---

## 196. 无主动冷却条件下的 RTP PI 轨迹控制

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是非负灯功率，输出是由传感器或同步记录器连续获取的温度轨迹与跟踪误差。在多次小幅且可逆的试验中，温度轨迹与跟踪误差开始时就沿最终方向变化，不会先向相反方向运动；非负灯功率改变后，温度轨迹与跟踪误差在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把非负灯功率恢复到基准值后，温度轨迹与跟踪误差最终会收敛或保持有界，不会出现自行增长的运动。当非负灯功率的幅值或运行点改变时，辐射换热、灯效率和可用冷却能力会随温度改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。非负灯功率与温度轨迹与跟踪误差采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

温度轨迹与跟踪误差

### 执行器

非负灯功率

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

使用 RTP 对象与 PI D=(s+0.0527)/s，并限制灯功率非负；升温轨迹与被动降温轨迹分开测试。

### 示例数据（JSON）

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
    "input_signal_id": "非负灯功率",
    "output_signal_id": "温度轨迹与跟踪误差",
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
    "stability": "令 非负灯功率 回到基线，核对 温度轨迹与跟踪误差 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 温度轨迹与跟踪误差 的首次有效方向与最终方向。",
    "delay": "从记录的 非负灯功率 边沿量到 温度轨迹与跟踪误差 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 非负灯功率 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 197. 兼顾温度均匀性的误差空间 LQG

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是公共灯命令，输出是由传感器或同步记录器连续获取的中心温度、估计三节点温度与均匀性。在多次小幅且可逆的试验中，中心温度开始时就沿最终方向变化，不会先向相反方向运动；公共灯命令改变后，中心温度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把公共灯命令恢复到基准值后，中心温度最终会收敛或保持有界，不会出现自行增长的运动。当公共灯命令的幅值或运行点改变时，几何关系、执行能力或对象增益会随当前状态改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。公共灯命令与中心温度、估计三节点温度与均匀性采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

中心温度、估计三节点温度与均匀性

### 执行器

公共灯命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

使用 RTP 三状态模型、K1=1、K0=[0.1221,2.0788,-0.2140]、L=[16.1461,16.4710,13.2001]、Rw=1、Rv=0.001；记录节点温差。

### 示例数据（JSON）

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
    "input_signal_id": "公共灯命令",
    "output_signal_id": "中心温度",
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
    "stability": "令 公共灯命令 回到基线，核对 中心温度、估计三节点温度与均匀性 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 中心温度、估计三节点温度与均匀性 的首次有效方向与最终方向。",
    "delay": "从记录的 公共灯命令 边沿量到 中心温度、估计三节点温度与均匀性 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 公共灯命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  }
}
```

---

## 198. RTP 灯逆补偿、饱和、反饱和与数字验证

### 控制问题描述

这是一个由加热执行器、相互传热的热体和温度传感器组成的热过程。控制输入是数字灯电压命令，输出是由传感器或同步记录器连续获取的晶圆温度、灯电压、积分状态。在多次小幅且可逆的试验中，晶圆温度开始时就沿最终方向变化，不会先向相反方向运动；数字灯电压命令改变后，晶圆温度在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把数字灯电压命令恢复到基准值后，晶圆温度最终会收敛或保持有界，不会出现自行增长的运动。当数字灯电压命令的幅值或运行点改变时，辐射换热、灯效率和可用冷却能力会随温度改变，因此响应规律本身会随状态演化，单一局部增益不能覆盖整个运动范围。数字灯电压命令与晶圆温度、灯电压、积分状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；多个读数描述的是彼此共享的内部运动，各通道之间只有有限的交叉影响。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

晶圆温度、灯电压、积分状态

### 执行器

数字灯电压命令

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=160.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
安全验证时把题目声明的非线性替换为无限制线性环节

### 主导时间尺度（秒）

20.0

### 示例数据（自然语言）

取灯功率 P=V^1.6、逆映射 V=P^0.625、电压限幅 1..4 V、参考滤波 0.2/(s+0.2)、Ts=0.1 s，并明确试用 1 s 反饱和恢复时间。

### 示例数据（JSON）

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
    "input_signal_id": "数字灯电压命令",
    "output_signal_id": "晶圆温度",
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
    "stability": "令 数字灯电压命令 回到基线，核对 晶圆温度、灯电压、积分状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 晶圆温度、灯电压、积分状态 的首次有效方向与最终方向。",
    "delay": "从记录的 数字灯电压命令 边沿量到 晶圆温度、灯电压、积分状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 数字灯电压命令 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "nonlinear_law": "P=V^1.6; V=P^0.625; clip V to [1,4]",
    "antiwindup_recovery_s": 1
  }
}
```

---

## 199. 大肠杆菌趋化的积分反馈精确适应

### 控制问题描述

这是一个由受体活性、甲基化适应和细胞运动共同构成的细菌趋化系统。控制输入是作为给定通路输入的配体浓度，输出是由传感器或同步记录器连续获取的受体活性与甲基化状态。在多次小幅且可逆的试验中，受体活性与甲基化状态开始时就沿最终方向变化，不会先向相反方向运动；作为给定通路输入的配体浓度改变后，受体活性与甲基化状态在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把作为给定通路输入的配体浓度恢复到基准值后，受体活性与甲基化状态最终会收敛或保持有界，不会出现自行增长的运动。分别施加小幅正向和反向的作为给定通路输入的配体浓度变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。作为给定通路输入的配体浓度与受体活性与甲基化状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

受体活性与甲基化状态

### 执行器

作为给定通路输入的配体浓度

### 安全边界

max_abs_reference_normalized=0.3
max_abs_output_normalized=1.5
max_abs_actuator_normalized=1.25
max_test_duration_s=60.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
未经有界验证就在规定工作区间之外沿用标称增益

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

数值示例取 K=1、Km=0.2 s^-1、CheRbar=0.5；20 s 时配体阶跃 1，并运行 60 s。

### 示例数据（JSON）

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
    "input_signal_id": "作为给定通路输入的配体浓度",
    "output_signal_id": "受体活性与甲基化状态",
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
    "stability": "令 作为给定通路输入的配体浓度 回到基线，核对 受体活性与甲基化状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 受体活性与甲基化状态 的首次有效方向与最终方向。",
    "delay": "从记录的 作为给定通路输入的配体浓度 边沿量到 受体活性与甲基化状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 作为给定通路输入的配体浓度 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "integral_feedback": "a=m-l; m_dot=0.2(0.5-a)"
  }
}
```

---

## 200. 由 CheY 活动映射一维平均趋化运动

### 控制问题描述

这是一个由受体活性、甲基化适应和细胞运动共同构成的细菌趋化系统。控制输入是作为给定通路输入的配体扰动，输出是由传感器或同步记录器连续获取的细胞平均位置、受体活性与甲基化状态。在多次小幅且可逆的试验中，细胞平均位置开始时就沿最终方向变化，不会先向相反方向运动；作为给定通路输入的配体扰动改变后，细胞平均位置在一个采样周期内就开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。把作为给定通路输入的配体扰动撤回基准值后，细胞平均位置会保留偏差或继续漂移，而不会依靠自身作用回到原位。分别施加小幅正向和反向的作为给定通路输入的配体扰动变化时，响应平滑、可逆且近似成比例，在限定范围内没有明显死区、滞回或幅值截断。作为给定通路输入的配体扰动与细胞平均位置、受体活性与甲基化状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；外层运动只能通过一个单独稳定的内环产生，内外环具有不同的时间尺度。在安全范围内改变工作点、负载或执行能力并重复试验时，这些变化可能大幅改变响应速度、最终水平或安全活动范围。

### 可观察输出

细胞平均位置、受体活性与甲基化状态

### 执行器

作为给定通路输入的配体扰动

### 安全边界

max_abs_reference_normalized=0.2
max_abs_output_normalized=1.25
max_abs_actuator_normalized=1.0
max_test_duration_s=40.0

### 禁止实验动作

向真实物理硬件下发命令
关闭仿真饱和或自动停止检查
输出或执行器越界后继续运行
测试外环命令时关闭内层稳定通道

### 主导时间尺度（秒）

5.0

### 示例数据（自然语言）

延续趋化示例，取 Ka=1、Kx=0.5、基线 w=0；配体阶跃 1 并积分平均位置。

### 示例数据（JSON）

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
    "input_signal_id": "作为给定通路输入的配体扰动",
    "output_signal_id": "细胞平均位置",
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
    "stability": "令 作为给定通路输入的配体扰动 回到基线，核对 细胞平均位置、受体活性与甲基化状态 有界或按声明的不稳定事件停止。",
    "phase": "施加等幅小正负变化，比较 细胞平均位置、受体活性与甲基化状态 的首次有效方向与最终方向。",
    "delay": "从记录的 作为给定通路输入的配体扰动 边沿量到 细胞平均位置、受体活性与甲基化状态 首个有效样本。",
    "order": "用完整数值模型比较早期与后期响应残差。",
    "sensing_and_actuation": "在同一时钟记录 作为给定通路输入的配体扰动 与全部声明输出。",
    "nonlinearity": "在局部试验幅值的 25%、50%、75%、100% 重复。",
    "coupling": "每次只改变一个可用输入，其余保持基线。",
    "uncertainty": "把相关参数乘以 0.9、1.0、1.1 后重复。"
  },
  "physical_parameters": {
    "mean_motion": "yCheY=a; x_dot=0.5(ybar-yCheY)"
  }
}
```

---
