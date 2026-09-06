# CFDC 数据集：二百题逐页填写指南

本指南对应当前 Kernel WebUI 的目标、信号、边界与要求、核对四页。第 1–200 题均从“自己的任务”创建；案例列表只用于独立附录。先在模型设置中配置 Base URL `http://127.0.0.1:11434/v1`、Model `gemma4:e4b`、API Key `ollama`，确保本地模型可用并显式测试连接。本指南的复现测试关闭 RAG。这是开发测试配置，不限制用户选择其他模型服务。

逐题按三张表填写；字段标识只是定位，界面只输入“填写值”。双引号包围文字但不输入引号；`true` 表示勾选，`false` 表示取消；`null` 和 `""` 表示留空；数组中的每一行分别新增信号，选择数组仅勾选列出的项目，`[]` 表示全部取消。未适用的条件项保持表中空值，不要切换任务类型来填写它们。中英文信号标识故意一致，便于导入数据核对。

表中软件停止阈值针对测量值绝对值，不是目标误差；输出上下限独立检查。输入增量不是绝对物理命令：偏置和单位须按条目解释。表单通过只证明合同完整，不证明动力学、可达性、可观性或性能。原模型/数学推导是背景；未经新协议取得的数据不得称为已有记录。CFDC 不执行文字里的公式或模型代码，不授权对实体硬件下发命令。

任务类型按显示名称选择：`local_setpoint_hold` → 保持在目标附近；`transition_then_hold` → 变化到新目标后保持；`disturbance_recovery_to_hold` → 受到扰动后恢复并保持。性能要求和预算的英文标识对应各条边界表中的中文界面项目，只勾选 selection 行列出的项目。

---

## 1. 家庭恒温器的滞环开关控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 1 题 [Ch1-01]。定位：Section 1.1, PDF 52-58。

原题保留：家庭恒温器的滞环开关控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用室外温度 50 degF、设定值 65 degF、等效热容 20000 Btu/degF、传热系数 500 Btu/(h*degF)、炉子供热率 25000 Btu/h 和滞环半宽 0.5 degF。初温取 64.5 degF 且炉子开启，以 60 s 采样仿真 6 h。 原加热命令严格为二值 {0,1}；范围不允许分数加热命令。固定滞环半宽 0.5 degF 对应本次容差 0.5 degF。连续控制器路线不能静默改成占空比平均对象：除非外部协议支持二值继电和记忆，否则必须保留能力边界。 来源模型方程（按原变量定义，仅作数学背景）：C\dot T=q_H\sigma-H(T-T_o). ; T(t)=T_\infty^{(\sigma)}+[T_0-T_\infty^{(\sigma)}]e^{-(t-t_0)/\tau}. ; T_o<r-\Delta<r+\Delta<T_o+q_H/H. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：家庭恒温器的滞环开关控制。本次仅做外部软件模型的适配子任务：使 room_temperature 保持在 65 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 1 题 [Ch1-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["room_temperature", "degF"]]` |
| 输入行 [名称] | `inputs` | `[["binary_heater_command"]]` |
| 输入单位 | `input_unit` | `"binary-command level"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `65` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `78.6` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `64.5` |
| 输出上限 | `output_max` | `65.5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.5` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `600.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：固定加热分支按 tau=C/H 衰减；滞环产生有界开关周期，不收敛为单个精确温度.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：一个连续热状态加继电器离散记忆；热分支相对阶次 1.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：双阈值滞环有记忆，不是无记忆静态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用室外温度 50 degF、设定值 65 degF、等效热容 20000 Btu/degF、传热系数 500 Btu/(h*degF)、炉子供热率 25000 Btu/h 和滞环半宽 0.5 degF。初温取 64.5 degF 且炉子开启，以 60 s 采样仿真 6 h。 原加热命令严格为二值 {0,1}；范围不允许分数加热命令。固定滞环半宽 0.5 degF 对应本次容差 0.5 degF。连续控制器路线不能静默改成占空比平均对象：除非外部协议支持二值继电和记忆，否则必须保留能力边界。 来源模型方程（按原变量定义，仅作数学背景）：C\dot T=q_H\sigma-H(T-T_o). ; T(t)=T_\infty^{(\sigma)}+[T_0-T_\infty^{(\sigma)}]e^{-(t-t_0)/\tau}. ; T_o<r-\Delta<r+\Delta<T_o+q_H/H.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 2. 汽车巡航的开环与闭环比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 2 题 [Ch1-02]。定位：Section 1.2, PDF 59-65。

原题保留：汽车巡航的开环与闭环比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：原静态巡航模型 delta_v=10 delta_u-5 grade，单位 mph、deg 和坡度百分比；新增动态仿真 G(s)=10/(5s+1) 是假设。绝对速度为 65+speed_deviation mph，绝对油门角为 6.5+throttle_angle_deviation deg；有符号范围 [-3,3] 对应绝对角 [3.5,9.5] deg。本次保持 +5 mph 增量，即 70 mph。 来源模型方程（按原变量定义，仅作数学背景）：y=10(u-0.5w)=10u-5w. ; y_{ol}=r-5w,\qquad e_{ol}=r-y_{ol}=5w. ; (1+10K_c)y_{cl}=10K_cr-5w, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：汽车巡航的开环与闭环比较。本次仅做外部软件模型的适配子任务：使 speed_deviation 保持在 5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 2 题 [Ch1-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["speed_deviation", "mph"]]` |
| 输入行 [名称] | `inputs` | `[["throttle_angle_deviation"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `5` |
| 输入下限 | `input_min` | `-3` |
| 输入上限 | `input_max` | `3` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `24.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-20` |
| 输出上限 | `output_max` | `20` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.8` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原巡航比较为静态模型，无动态极点；新增 G=10/(5s+1) 滞后仅为仿真假设，极点 -0.2.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：原静态巡航模型 delta_v=10 delta_u-5 grade，单位 mph、deg 和坡度百分比；新增动态仿真 G(s)=10/(5s+1) 是假设。绝对速度为 65+speed_deviation mph，绝对油门角为 6.5+throttle_angle_deviation deg；有符号范围 [-3,3] 对应绝对角 [3.5,9.5] deg。本次保持 +5 mph 增量，即 70 mph。 来源模型方程（按原变量定义，仅作数学背景）：y=10(u-0.5w)=10u-5w. ; y_{ol}=r-5w,\qquad e_{ol}=r-y_{ol}=5w. ; (1+10K_c)y_{cl}=10K_cr-5w,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 3. 手动汽车转向反馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 3 题 [Ch1-03]。定位：Problem 1.1(a), PDF 94。

原题保留：手动汽车转向反馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 方向盘转角 变化 5 deg，预期 heading_angle 最终变化 8 deg，63% 响应时间取 1.5 s。输入范围取 -30 至 30 deg，输出范围取 -180 至 180 deg；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\tau_h\dot\delta+\delta=K_h e, ; \dot\theta+a\theta=b\delta+d, ; \frac{\Theta}{R}=\frac{bK_h}{(s+a)(\tau_hs+1)+bK_h}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：手动汽车转向反馈。本次仅做外部软件模型的适配子任务：使 heading_angle 保持在 3.6 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 3 题 [Ch1-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["heading_angle", "deg"]]` |
| 输入行 [名称] | `inputs` | `[["steering_wheel_angle"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `3.6` |
| 输入下限 | `input_min` | `-30.0` |
| 输入上限 | `input_max` | `30.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `216.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-180.0` |
| 输出上限 | `output_max` | `180.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `7.2` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：来源驾驶员模型显式含符号迟延 tau_h，此处没有确认其数值.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 方向盘转角 变化 5 deg，预期 heading_angle 最终变化 8 deg，63% 响应时间取 1.5 s。输入范围取 -30 至 30 deg，输出范围取 -180 至 180 deg；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\tau_h\dot\delta+\delta=K_h e, ; \dot\theta+a\theta=b\delta+d, ; \frac{\Theta}{R}=\frac{bK_h}{(s+a)(\tau_hs+1)+bK_h},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 4. 德雷贝尔孵化器温度调节

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 4 题 [Ch1-04]。定位：Problem 1.1(b), PDF 94。

原题保留：德雷贝尔孵化器温度调节。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 空气或燃料阀位置 变化 10 %，预期 incubator_temperature 最终变化 2 degC，63% 响应时间取 120 s。输入范围取 0 至 100 %，输出范围取 30 至 42 degC；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\delta x_s=k_T\delta T, ; \delta q=k_q\delta u, ; C\,\delta\dot T+(H+k_qk_\ell k_T)\delta T =k_qk_r\delta r+H\delta T_o. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：德雷贝尔孵化器温度调节。本次仅做外部软件模型的适配子任务：使 incubator_temperature 保持在 33.6 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 4 题 [Ch1-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["incubator_temperature", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["air"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `33.6` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `50.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `30.0` |
| 输出上限 | `output_max` | `42.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.24` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 空气或燃料阀位置 变化 10 %，预期 incubator_temperature 最终变化 2 degC，63% 响应时间取 120 s。输入范围取 0 至 100 %，输出范围取 30 至 42 degC；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\delta x_s=k_T\delta T, ; \delta q=k_q\delta u, ; C\,\delta\dot T+(H+k_qk_\ell k_T)\delta T =k_qk_r\delta r+H\delta T_o.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 5. 浮球阀液位调节

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 5 题 [Ch1-05]。定位：Problem 1.1(c), PDF 94。

原题保留：浮球阀液位调节。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 入口阀开度 变化 10 %，预期 tank_liquid_level 最终变化 0.08 m，63% 响应时间取 20 s。输入范围取 0 至 100 %，输出范围取 0.2 至 1.2 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：A\dot h=q_{in}(u,p_s)-q_{out}(h)+d_q, ; \delta q_{in}=k_v\delta u+k_p\delta p_s,\qquad \delta q_{out}=k_o\delta h, ; A\,\delta\dot h+(k_o+k_vk_\ell)\delta h =k_vk_\ell\delta r+k_p\delta p_s+d_q. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：浮球阀液位调节。本次仅做外部软件模型的适配子任务：使 tank_liquid_level 保持在 0.7 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 5 题 [Ch1-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["tank_liquid_level", "m"]]` |
| 输入行 [名称] | `inputs` | `[["inlet_valve_opening"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.7` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.44` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0.2` |
| 输出上限 | `output_max` | `1.2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 入口阀开度 变化 10 %，预期 tank_liquid_level 最终变化 0.08 m，63% 响应时间取 20 s。输入范围取 0 至 100 %，输出范围取 0.2 至 1.2 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：A\dot h=q_{in}(u,p_s)-q_{out}(h)+d_q, ; \delta q_{in}=k_v\delta u+k_p\delta p_s,\qquad \delta q_{out}=k_o\delta h, ; A\,\delta\dot h+(k_o+k_vk_\ell)\delta h =k_vk_\ell\delta r+k_p\delta p_s+d_q.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 6. 瓦特飞球调速器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 6 题 [Ch1-06]。定位：Problem 1.1(d), PDF 94。

原题保留：瓦特飞球调速器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 蒸汽阀开度 变化 10 %，预期 engine_shaft_speed 最终变化 20 rpm，63% 响应时间取 8 s。输入范围取 0 至 100 %，输出范围取 400 至 900 rpm；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：J\dot\omega=T_s(u)-T_L-b\omega, ; \delta x_f=\left.\frac{\partial x_f}{\partial\omega}\right|_0\delta\omega =2k_{\omega2}\omega_0\delta\omega\equiv k_\omega\delta\omega. ; J\,\delta\dot\omega+(b+k_sk_gk_\omega)\delta\omega=-\delta T_L. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：瓦特飞球调速器。本次仅做外部软件模型的适配子任务：使 engine_shaft_speed 保持在 650.0 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 6 题 [Ch1-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["engine_shaft_speed", "rpm"]]` |
| 输入行 [名称] | `inputs` | `[["steam_valve_opening"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `650.0` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1080.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `400.0` |
| 输出上限 | `output_max` | `900.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `10.0` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 蒸汽阀开度 变化 10 %，预期 engine_shaft_speed 最终变化 20 rpm，63% 响应时间取 8 s。输入范围取 0 至 100 %，输出范围取 400 至 900 rpm；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：J\dot\omega=T_s(u)-T_L-b\omega, ; \delta x_f=\left.\frac{\partial x_f}{\partial\omega}\right|_0\delta\omega =2k_{\omega2}\omega_0\delta\omega\equiv k_\omega\delta\omega. ; J\,\delta\dot\omega+(b+k_sk_gk_\omega)\delta\omega=-\delta T_L.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 7. 造纸机浆料浓度控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 7 题 [Ch1-07]。定位：Problem 1.3(a), PDF 95。

原题保留：造纸机浆料浓度控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 稀释水阀 变化 5 %，预期 stock_consistency 最终变化 -0.4 %，63% 响应时间取 30 s。输入范围取 0 至 100 %，输出范围取 2 至 6 %；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\frac{d(Vc)}{dt}=q_sc_s+q_wc_w-(q_s+q_w)c. ; V\dot c=q_s(c_s-c)+q_w(c_w-c). ; V\,\delta\dot c+(q_{s0}+q_{w0})\delta c =(c_{s0}-c_0)\delta q_s+q_{s0}\delta c_s +(c_{w0}-c_0)\delta q_w+q_{w0}\delta c_w. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：造纸机浆料浓度控制。本次仅做外部软件模型的适配子任务：使 stock_consistency 保持在 4.0 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 7 题 [Ch1-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["stock_consistency", "%"]]` |
| 输入行 [名称] | `inputs` | `[["dilution_water_valve"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `4.0` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `7.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `2.0` |
| 输出上限 | `output_max` | `6.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：白水阀增益为负，因为稀释降低浓度；负增益不是右半平面零点证据.
3. significant_delay: 来源模型先验：来源允许另加 exp(-Ls) 传输迟延，L 需新证据.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 稀释水阀 变化 5 %，预期 stock_consistency 最终变化 -0.4 %，63% 响应时间取 30 s。输入范围取 0 至 100 %，输出范围取 2 至 6 %；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\frac{d(Vc)}{dt}=q_sc_s+q_wc_w-(q_s+q_w)c. ; V\dot c=q_s(c_s-c)+q_w(c_w-c). ; V\,\delta\dot c+(q_{s0}+q_{w0})\delta c =(c_{s0}-c_0)\delta q_s+q_{s0}\delta c_s +(c_{w0}-c_0)\delta q_w+q_{w0}\delta c_w.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 8. 造纸机纸页含水率控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 8 题 [Ch1-08]。定位：Problem 1.3(b), PDF 95。

原题保留：造纸机纸页含水率控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 干燥蒸汽命令 变化 10 %，预期 paper_moisture 最终变化 -1.2 %，63% 响应时间取 60 s，并采用 8 s 纯等待时间。输入范围取 0 至 100 %，输出范围取 2 至 12 %；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\dot M_w=q_{w,in}(d_m)-q_{evap}(M_w,u). ; \delta\dot M_w+k_m\delta M_w=-k_u'\delta u+k_d'\delta d_m. ; \tau\,\delta\dot m+\delta m=-K_u\delta u+K_d\delta d_m,\qquad y(t)=m(t-L)+n(t). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：造纸机纸页含水率控制。本次仅做外部软件模型的适配子任务：使 paper_moisture 保持在 7.0 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 8 题 [Ch1-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["paper_moisture", "%"]]` |
| 输入行 [名称] | `inputs` | `[["dryer_steam_command"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `7.0` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `14.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `2.0` |
| 输出上限 | `output_max` | `12.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.2` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：加热增加而含水率降低，名义增益为负；仅此不构成逆响应.
3. significant_delay: 来源模型先验：来源通道显式包含 exp(-Ls) 迟延；需辨识 L，不能用上升时间样本替代.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 干燥蒸汽命令 变化 10 %，预期 paper_moisture 最终变化 -1.2 %，63% 响应时间取 60 s，并采用 8 s 纯等待时间。输入范围取 0 至 100 %，输出范围取 2 至 12 %；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\dot M_w=q_{w,in}(d_m)-q_{evap}(M_w,u). ; \delta\dot M_w+k_m\delta M_w=-k_u'\delta u+k_d'\delta d_m. ; \tau\,\delta\dot m+\delta m=-K_u\delta u+K_d\delta d_m,\qquad y(t)=m(t-L)+n(t).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 9. 人体血压负反馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 9 题 [Ch1-09]。定位：Problem 1.4(a), PDF 96。

原题保留：人体血压负反馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 心脏与血管神经命令 变化 0.1 neural_command，预期 arterial_pressure 最终变化 8 mmHg，63% 响应时间取 6 s。输入范围取 -0.5 至 0.5 neural_command，输出范围取 60 至 140 mmHg；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：C_v\dot P=Q_h-\frac{P}{R_v}. ; \delta Q_h-\delta(P/R_v)=k_a\delta a+k_d\delta d-\frac{1}{R_0}\delta P. ; C_v\,\delta\dot P+\left(\frac1{R_0}+k_aK_b\right)\delta P =k_aK_b\delta r+k_d\delta d. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：人体血压负反馈。本次仅做外部软件模型的适配子任务：使 arterial_pressure 保持在 100 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 9 题 [Ch1-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["arterial_pressure", "mmHg"]]` |
| 输入行 [名称] | `inputs` | `[["cardiac_neural_drive"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `100` |
| 输入下限 | `input_min` | `-0.5` |
| 输入上限 | `input_max` | `0.5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `168.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `60` |
| 输出上限 | `output_max` | `140` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `1.6` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 心脏与血管神经命令 变化 0.1 neural_command，预期 arterial_pressure 最终变化 8 mmHg，63% 响应时间取 6 s。输入范围取 -0.5 至 0.5 neural_command，输出范围取 60 至 140 mmHg；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：C_v\dot P=Q_h-\frac{P}{R_v}. ; \delta Q_h-\delta(P/R_v)=k_a\delta a+k_d\delta d-\frac{1}{R_0}\delta P. ; C_v\,\delta\dot P+\left(\frac1{R_0}+k_aK_b\right)\delta P =k_aK_b\delta r+k_d\delta d.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 10. 人体血糖调节

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 10 题 [Ch1-10]。定位：Problem 1.4(b), PDF 96。

原题保留：人体血糖调节。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

来源方程只把进餐输入 d_m 加入葡萄糖动态，没有定义可命令的胰岛素释放通道。本指南仅为软件仿真明确新增该通道：d(delta_G)/dt=-0.05 delta_G-1.0 I+d_m；dI/dt=0.0025 delta_G-0.05 I+0.1 u。u=insulin_release_deviation 是有符号 normalized_input 命令；I 是有符号、无量纲的内部有效作用偏差，不是胰岛素浓度或剂量；delta_G 单位 mg/dL，时间单位 s。系数单位分别为 0.05 s^-1、1.0 (mg/dL)/s 每归一化 I、0.0025 归一化 I/((mg/dL)*s)、0.1 归一化 I/(normalized_input*s)。本保持练习令 d_m=0，初始 delta_G=0、I=0。测得的绝对血糖定义为 blood_glucose=100+delta_G mg/dL。全部系数、归一化执行作用及 100 mg/dL 偏置都是新增软件假设，不是已辨识生理参数或已有记录。新增命令从 B_u=[0,0.1]^T 进入，区别于原进餐 B_m=[1,0]^T。取 C=[1,0]，新增命令到血糖偏差模型为 G_u(s)=-0.1/(s^2+0.1s+0.005)，因此 u=+0.1 预测稳态 delta_G=-2 mg/dL、blood_glucose=98 mg/dL。来源中 -12 mg/dL、20 s 一阶响应的示例没有明确此输入位置，不能校准新增二阶通道，本次不采用。这里没有人体剂量、临床验证或硬件执行设置。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：人体血糖调节。本次仅做外部软件模型的适配子任务：使 blood_glucose 保持在 100 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 10 题 [Ch1-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 明确新增软件模型：d(delta_G)/dt=-0.05 delta_G-I+d_m；dI/dt=0.0025 delta_G-0.05 I+0.1 u；u=insulin_release_deviation、d_m=0、blood_glucose=100+delta_G mg/dL。该归一化命令通道为新增假设，区别于来源进餐输入。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["blood_glucose", "mg/dL"]]` |
| 输入行 [名称] | `inputs` | `[["insulin_release_deviation"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `100` |
| 输入下限 | `input_min` | `-0.5` |
| 输入上限 | `input_max` | `0.5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `216.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `60` |
| 输出上限 | `output_max` | `180` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `2.4` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 新增模型先验：极点 -0.05 +/- 0.05j 稳定，仅为软件模型结论
2. nonminimum_phase: 新增模型先验：常数分子 -0.1 无有限零点；负稳态增益不等于逆响应
3. significant_delay: 新增模型假设：方程无纯迟延，真实迟延未知
4. relative_degree: 新增模型先验：u 到 delta_G 相对阶次 2；来源进餐通道分子不同、相对阶次 1
5. sensing_actuation_adequacy: 新增模型先验：A=[[-0.05,-1],[0.0025,-0.05]]、B_u=[0,0.1]^T、C=[1,0] 理论上可控可观；I 不是独立测量，实际传感能力未知
6. nonlinearity_strength: 新增模型假设：局部线性二状态动态，不声明完整生理过程的非线性性质
7. coupling_underactuation: 单命令 u、单绝对血糖测量；进餐 d_m 是另定义的扰动，不是胰岛素命令
8. uncertainty_variation: 未知，没有参数重复试验或执行作用实测标定
模型与范围：来源方程只把进餐输入 d_m 加入葡萄糖动态，没有定义可命令的胰岛素释放通道。本指南仅为软件仿真明确新增该通道：d(delta_G)/dt=-0.05 delta_G-1.0 I+d_m；dI/dt=0.0025 delta_G-0.05 I+0.1 u。u=insulin_release_deviation 是有符号 normalized_input 命令；I 是有符号、无量纲的内部有效作用偏差，不是胰岛素浓度或剂量；delta_G 单位 mg/dL，时间单位 s。系数单位分别为 0.05 s^-1、1.0 (mg/dL)/s 每归一化 I、0.0025 归一化 I/((mg/dL)*s)、0.1 归一化 I/(normalized_input*s)。本保持练习令 d_m=0，初始 delta_G=0、I=0。测得的绝对血糖定义为 blood_glucose=100+delta_G mg/dL。全部系数、归一化执行作用及 100 mg/dL 偏置都是新增软件假设，不是已辨识生理参数或已有记录。新增命令从 B_u=[0,0.1]^T 进入，区别于原进餐 B_m=[1,0]^T。取 C=[1,0]，新增命令到血糖偏差模型为 G_u(s)=-0.1/(s^2+0.1s+0.005)，因此 u=+0.1 预测稳态 delta_G=-2 mg/dL、blood_glucose=98 mg/dL。来源中 -12 mg/dL、20 s 一阶响应的示例没有明确此输入位置，不能校准新增二阶通道，本次不采用。这里没有人体剂量、临床验证或硬件执行设置。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 11. 人体心率调节

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 11 题 [Ch1-11]。定位：Problem 1.4(c), PDF 96。

原题保留：人体心率调节。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 交感与副交感驱动 变化 0.1 autonomic_command，预期 heart_rate 最终变化 8 bpm，63% 响应时间取 5 s。输入范围取 -0.5 至 0.5 autonomic_command，输出范围取 45 至 160 bpm；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\tau_h\dot h+h=k_uu+k_dd, ; u=K_h(r_h-h),\qquad K_h>0. ; \tau_h\dot h+(1+k_uK_h)h=k_uK_hr_h+k_dd, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：人体心率调节。本次仅做外部软件模型的适配子任务：使 heart_rate 保持在 80 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 11 题 [Ch1-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["heart_rate", "bpm"]]` |
| 输入行 [名称] | `inputs` | `[["sympathetic_drive_deviation"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `80` |
| 输入下限 | `input_min` | `-0.5` |
| 输入上限 | `input_max` | `0.5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `192.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `45` |
| 输出上限 | `output_max` | `160` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `2.3` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 交感与副交感驱动 变化 0.1 autonomic_command，预期 heart_rate 最终变化 8 bpm，63% 响应时间取 5 s。输入范围取 -0.5 至 0.5 autonomic_command，输出范围取 45 至 160 bpm；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\tau_h\dot h+h=k_uu+k_dd, ; u=K_h(r_h-h),\qquad K_h>0. ; \tau_h\dot h+(1+k_uK_h)h=k_uK_hr_h+k_dd,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 12. 眼球注视角控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 12 题 [Ch1-12]。定位：Problem 1.4(d), PDF 96。

原题保留：眼球注视角控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 眼肌力矩 变化 0.002 Nm，预期 eye_angle 最终变化 0.12 rad，63% 响应时间取 0.18 s。输入范围取 -0.01 至 0.01 Nm，输出范围取 -0.5 至 0.5 rad；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：J\ddot\theta+B\dot\theta+K_e\theta=T_m+d. ; T_m=K_p(r-\theta)-K_d\dot\theta, ; J\ddot\theta+(B+K_d)\dot\theta+(K_e+K_p)\theta=K_pr+d. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：眼球注视角控制。本次仅做外部软件模型的适配子任务：使 eye_angle 保持在 0.01 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 12 题 [Ch1-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["eye_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["ocular_muscle_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.01` |
| 输入下限 | `input_min` | `-0.01` |
| 输入上限 | `input_max` | `0.01` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.6` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.5` |
| 输出上限 | `output_max` | `0.5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 眼肌力矩 变化 0.002 Nm，预期 eye_angle 最终变化 0.12 rad，63% 响应时间取 0.18 s。输入范围取 -0.01 至 0.01 Nm，输出范围取 -0.5 至 0.5 rad；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：J\ddot\theta+B\dot\theta+K_e\theta=T_m+d. ; T_m=K_p(r-\theta)-K_d\dot\theta, ; J\ddot\theta+(B+K_d)\dot\theta+(K_e+K_p)\theta=K_pr+d.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 13. 瞳孔对光调节

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 13 题 [Ch1-13]。定位：Problem 1.4(e), PDF 96。

原题保留：瞳孔对光调节。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

明确输入符号：dilation_command_deviation 是来源中“扩瞳为正”的神经命令增量，单位 iris_command。输出 pupil_diameter 为绝对直径 D，单位 mm，D=5+delta_D。来源方程 tau_D d(delta_D)/dt+delta_D=k_u delta_u 满足 k_u>0；原米制通过 D_mm=1000 D_m 换算。本次局部软件练习新增假设 k_u=+8.0 mm/iris_command（即 0.008 m/iris_command）、tau_D=0.8 s、delta_u 范围 [-0.1,0.1]。因此 delta_u=+0.1 iris_command 预测 delta_D=+0.8 mm、D=5.8 mm；-0.1 预测 4.2 mm。这些是未经实测的仿真假设。来源示例把正虹膜命令写成负直径变化，与自身扩瞳为正的方程冲突，不能用于本通道。光照增加是另一个扰动，可经负反馈导致缩瞳，不是这里的控制输入。视网膜照度也不是以毫米计的被控输出。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：瞳孔对光调节。本次仅做外部软件模型的适配子任务：使 pupil_diameter 保持在 5.0 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 13 题 [Ch1-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 输入是扩瞳为正的命令增量；D=5+delta_D mm 和 k_u=+8.0 mm/iris_command 是明确软件假设，不是观察记录。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pupil_diameter", "mm"]]` |
| 输入行 [名称] | `inputs` | `[["dilation_command_deviation"]]` |
| 输入单位 | `input_unit` | `"iris_command"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `5.0` |
| 输入下限 | `input_min` | `-0.1` |
| 输入上限 | `input_max` | `0.1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `9.6` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `2.0` |
| 输出上限 | `output_max` | `8.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.12` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：扩瞳为正命令的名义增益为 +8.0 mm/iris_command，无有限零点；光照引起的缩瞳属于另一通道。
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：视网膜照度随瞳孔直径平方变化；线性增益依赖直径和照度偏置.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：明确输入符号：dilation_command_deviation 是来源中“扩瞳为正”的神经命令增量，单位 iris_command。输出 pupil_diameter 为绝对直径 D，单位 mm，D=5+delta_D。来源方程 tau_D d(delta_D)/dt+delta_D=k_u delta_u 满足 k_u>0；原米制通过 D_mm=1000 D_m 换算。本次局部软件练习新增假设 k_u=+8.0 mm/iris_command（即 0.008 m/iris_command）、tau_D=0.8 s、delta_u 范围 [-0.1,0.1]。因此 delta_u=+0.1 iris_command 预测 delta_D=+0.8 mm、D=5.8 mm；-0.1 预测 4.2 mm。这些是未经实测的仿真假设。来源示例把正虹膜命令写成负直径变化，与自身扩瞳为正的方程冲突，不能用于本通道。光照增加是另一个扰动，可经负反馈导致缩瞳，不是这里的控制输入。视网膜照度也不是以毫米计的被控输出。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 14. 电梯粗细测量与钢缆伸长

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 14 题 [Ch1-14]。定位：Problem 1.5, PDF 96。

原题保留：电梯粗细测量与钢缆伸长。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 曳引电机力矩与制动器 变化 100 Nm，预期 car_position 最终变化 0.15 m，63% 响应时间取 2.5 s。输入范围取 -1500 至 1500 Nm，输出范围取 0 至 120 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\delta_c=\frac{T_c}{k_c}\approx\frac{Mg}{k_c}, \qquad z_c=z_m-\delta_c. ; M\ddot z_c+b\dot z_c=F_m-Mg+d_F. ; \hat z_c=z_m-\frac{\hat M g}{k_c}+W_f(\rho)y_f, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：电梯粗细测量与钢缆伸长。本次仅做外部软件模型的适配子任务：使 car_position 保持在 61.2 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 14 题 [Ch1-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 60 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 60，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 61.2 附近，误差不超过 2.4"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `60` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["car_position", "m"]]` |
| 输入行 [名称] | `inputs` | `[["hoist_torque_deviation"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `61.2` |
| 输入下限 | `input_min` | `-1500` |
| 输入上限 | `input_max` | `1500` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `144.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `120` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `2.4` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 来源模型先验：仅电机编码器不能重建载荷相关绳伸长；需要轿厢平层测量或载荷证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 曳引电机力矩与制动器 变化 100 Nm，预期 car_position 最终变化 0.15 m，63% 响应时间取 2.5 s。输入范围取 -1500 至 1500 Nm，输出范围取 0 至 120 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\delta_c=\frac{T_c}{k_c}\approx\frac{Mg}{k_c}, \qquad z_c=z_m-\delta_c. ; M\ddot z_c+b\dot z_c=F_m-Mg+d_F. ; \hat z_c=z_m-\frac{\hat M g}{k_c}+W_f(\rho)y_f,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 15. 温度的电测量与电加热

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 15 题 [Ch1-15]。定位：Problems 1.6(a)/1.7(a), PDF 96-97。

原题保留：温度的电测量与电加热。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 电加热器电压 变化 5 V，预期 temperature 最终变化 8 degC，63% 响应时间取 80 s。输入范围取 0 至 48 V，输出范围取 15 至 90 degC；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\delta v_s=K_T\delta T, ; \delta q=\frac{2\eta v_{a0}}{R_H}\delta v_a\equiv K_H\delta v_a. ; C\delta\dot T+(H+K_HK_cK_T)\delta T =K_HK_cK_T\delta r+H\delta T_o. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：温度的电测量与电加热。本次仅做外部软件模型的适配子任务：使 temperature 保持在 52.5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 15 题 [Ch1-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["temperature", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["electrical_heater_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `52.5` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `48.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `108.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `15.0` |
| 输出上限 | `output_max` | `90.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `1.5` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：加热功率依赖电压平方；电压到温度线性化依赖非零电压偏置.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 电加热器电压 变化 5 V，预期 temperature 最终变化 8 degC，63% 响应时间取 80 s。输入范围取 0 至 48 V，输出范围取 15 至 90 degC；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\delta v_s=K_T\delta T, ; \delta q=\frac{2\eta v_{a0}}{R_H}\delta v_a\equiv K_H\delta v_a. ; C\delta\dot T+(H+K_HK_cK_T)\delta T =K_HK_cK_T\delta r+H\delta T_o.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 16. 压力的电测量与阀控

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 16 题 [Ch1-16]。定位：Problems 1.6(b)/1.7(b), PDF 96-97。

原题保留：压力的电测量与阀控。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 阀门命令 变化 10 %，预期 pressure 最终变化 30 kPa，63% 响应时间取 12 s。输入范围取 0 至 100 %，输出范围取 0 至 500 kPa；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：C_p\dot p=q_{in}(u,p_s,p)-q_{out}(p)+d_q. ; \delta q_{in}=k_u\delta u+k_s\delta p_s-k_{ip}\delta p, \qquad \delta q_{out}=k_o\delta p, ; C_p\delta\dot p+(k_{ip}+k_o+k_uK_cK_p)\delta p =k_uK_cK_p\delta r+k_s\delta p_s+d_q. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：压力的电测量与阀控。本次仅做外部软件模型的适配子任务：使 pressure 保持在 250.0 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 16 题 [Ch1-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pressure", "kPa"]]` |
| 输入行 [名称] | `inputs` | `[["valve_command"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `250.0` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `600.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0.0` |
| 输出上限 | `output_max` | `500.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `10.0` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 阀门命令 变化 10 %，预期 pressure 最终变化 30 kPa，63% 响应时间取 12 s。输入范围取 0 至 100 %，输出范围取 0 至 500 kPa；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：C_p\dot p=q_{in}(u,p_s,p)-q_{out}(p)+d_q. ; \delta q_{in}=k_u\delta u+k_s\delta p_s-k_{ip}\delta p, \qquad \delta q_{out}=k_o\delta p, ; C_p\delta\dot p+(k_{ip}+k_o+k_uK_cK_p)\delta p =k_uK_cK_p\delta r+k_s\delta p_s+d_q.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 17. 液位的电测量与泵阀控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 17 题 [Ch1-17]。定位：Problems 1.6(c)/1.7(c), PDF 96-97。

原题保留：液位的电测量与泵阀控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 泵速或阀位 变化 10 %，预期 liquid_level 最终变化 0.1 m，63% 响应时间取 25 s。输入范围取 0 至 100 %，输出范围取 0.1 至 1.5 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：A\dot h=q_p(u)-q_o(h)+d_q. ; \delta q_p=k_p\delta u,\qquad \delta q_o=k_o\delta h,\qquad \delta v_s=K_h\delta h. ; A\delta\dot h+(k_o+k_pK_cK_h)\delta h =k_pK_cK_h\delta r+d_q. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：液位的电测量与泵阀控制。本次仅做外部软件模型的适配子任务：使 liquid_level 保持在 0.8 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 17 题 [Ch1-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["liquid_level", "m"]]` |
| 输入行 [名称] | `inputs` | `[["pump_speed"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.8` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.8` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0.1` |
| 输出上限 | `output_max` | `1.5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.028` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：平方根出流使局部增益依赖液位，线性化要求正工作液位.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 泵速或阀位 变化 10 %，预期 liquid_level 最终变化 0.1 m，63% 响应时间取 25 s。输入范围取 0 至 100 %，输出范围取 0.1 至 1.5 m；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：A\dot h=q_p(u)-q_o(h)+d_q. ; \delta q_p=k_p\delta u,\qquad \delta q_o=k_o\delta h,\qquad \delta v_s=K_h\delta h. ; A\delta\dot h+(k_o+k_pK_cK_h)\delta h =k_pK_cK_h\delta r+d_q.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 18. 管道流量的电测量与阀控

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 18 题 [Ch1-18]。定位：Problems 1.6(d)/1.7(d), PDF 96-97。

原题保留：管道流量的电测量与阀控。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 调节阀开度 变化 10 %，预期 pipe_flow_rate 最终变化 0.02 m^3/s，63% 响应时间取 4 s。输入范围取 0 至 100 %，输出范围取 0 至 0.2 m^3/s；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：L_f\dot q+\Delta p_R(q)=\Delta p_v(u)+d_p. ; L_f\delta\dot q+R_f\delta q=K_v\delta u+d_p. ; L_f\delta\dot q+(R_f+K_vK_cK_q)\delta q =K_vK_cK_q\delta r+d_p. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：管道流量的电测量与阀控。本次仅做外部软件模型的适配子任务：使 pipe_flow_rate 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 18 题 [Ch1-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pipe_flow_rate", "m^3/s"]]` |
| 输入行 [名称] | `inputs` | `[["control_valve_position"]]` |
| 输入单位 | `input_unit` | `"%"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `0.0` |
| 输入上限 | `input_max` | `100.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.24` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0.0` |
| 输出上限 | `output_max` | `0.2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.004` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 调节阀开度 变化 10 %，预期 pipe_flow_rate 最终变化 0.02 m^3/s，63% 响应时间取 4 s。输入范围取 0 至 100 %，输出范围取 0 至 0.2 m^3/s；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：L_f\dot q+\Delta p_R(q)=\Delta p_v(u)+d_p. ; L_f\delta\dot q+R_f\delta q=K_v\delta u+d_p. ; L_f\delta\dot q+(R_f+K_vK_cK_q)\delta q =K_vK_cK_q\delta r+d_p.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 19. HPA 应激激素负反馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 19 题 [Ch1-19]。定位：Problem 1.8(a), PDF 97-98。

原题保留：HPA 应激激素负反馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 内源分泌速率 变化 1 ng/(mL*min)，预期 hormone_concentration 最终变化 0.8 ng/mL，63% 响应时间取 600 s。输入范围取 0 至 5 ng/(mL*min)，输出范围取 0 至 20 ng/mL；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\tau_c\dot c+c=K_s d_s-K_f g. ; \tau_a\dot a+a=K_a c, \qquad \tau_g\dot g+g=K_g a. ; \frac{G(s)}{D_s(s)}= \frac{K_sK_aK_g} {(\tau_cs+1)(\tau_as+1)(\tau_gs+1)+K_fK_aK_g}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：HPA 应激激素负反馈。本次仅做外部软件模型的适配子任务：使 hormone_concentration 保持在 5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 19 题 [Ch1-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["hormone_concentration", "ng/mL"]]` |
| 输入行 [名称] | `inputs` | `[["secretion_rate"]]` |
| 输入单位 | `input_unit` | `"ng/(mL*min)"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `5` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `24.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `20` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.4` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：三个滞后加负反馈需满足三阶 Routh 条件，负反馈本身不能证明稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：三个储能状态，不能无证据把激素级联降成单滞后.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在安全仿真中令 内源分泌速率 变化 1 ng/(mL*min)，预期 hormone_concentration 最终变化 0.8 ng/mL，63% 响应时间取 600 s。输入范围取 0 至 5 ng/(mL*min)，输出范围取 0 至 20 ng/mL；以不大于时间常数五十分之一的步长采样，运行至少八个时间常数，并按四级幅值与 0.9/1.0/1.1 倍参数重复。 来源模型方程（按原变量定义，仅作数学背景）：\tau_c\dot c+c=K_s d_s-K_f g. ; \tau_a\dot a+a=K_a c, \qquad \tau_g\dot g+g=K_g a. ; \frac{G(s)}{D_s(s)}= \frac{K_sK_aK_g} {(\tau_cs+1)(\tau_as+1)(\tau_gs+1)+K_fK_aK_g}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 20. 分娩催产素正反馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 20 题 [Ch1-20]。定位：Problem 1.8(b), PDF 98。

原题保留：分娩催产素正反馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用二状态正反馈仿真：催产素时间常数 30 s、宫缩时间常数 20 s，出生事件前环路乘积为 1.2，并在 180 s 时把压力反馈增益切换为零。 来源模型方程（按原变量定义，仅作数学背景）：\tau_o\dot o+o=K_op. ; \tau_s\dot s_c+s_c=K_co+d_b, \qquad p=K_ps_c. ; \frac{S_c(s)}{D_b(s)}= \frac{\tau_os+1} {(\tau_os+1)(\tau_ss+1)-K_oK_pK_c}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：分娩催产素正反馈。本次仅做外部软件模型的适配子任务：使 oxytocin_level 保持在 5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 20 题 [Ch1-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["oxytocin_level", "normalized_concentration"]]` |
| 输入行 [名称] | `inputs` | `[["oxytocin_release"]]` |
| 输入单位 | `input_unit` | `"normalized_release/min"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `5` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `12.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `10` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.2` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：出生事件前正反馈乘积 L=1.2 大于 1，产生右半平面极点.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：事件切断反馈改变模型，整个试验不是同一固定线性对象.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用二状态正反馈仿真：催产素时间常数 30 s、宫缩时间常数 20 s，出生事件前环路乘积为 1.2，并在 180 s 时把压力反馈增益切换为零。 来源模型方程（按原变量定义，仅作数学背景）：\tau_o\dot o+o=K_op. ; \tau_s\dot s_c+s_c=K_co+d_b, \qquad p=K_ps_c. ; \frac{S_c(s)}{D_b(s)}= \frac{\tau_os+1} {(\tau_os+1)(\tau_ss+1)-K_oK_pK_c}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 21. 汽车巡航一阶动力学

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 21 题 [Ch2-01]。定位：Example 2.1, PDF 107-113。

原题保留：汽车巡航一阶动力学。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

1000 d(delta_v)/dt + 50 delta_v = delta_F；G(s)=1/(1000s+50)。绝对速度 v=25+delta_v m/s，绝对驱动力 F=1250+delta_F N；500 N 增量预测最终速度增量 10 m/s，时间常数 20 s。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：汽车巡航一阶动力学。本次仅做外部软件模型的适配子任务：使 speed_deviation 保持在 5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 21 题 [Ch2-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 1000 d(delta_v)/dt + 50 delta_v = delta_F；G(s)=1/(1000s+50)。绝对速度 v=25+delta_v m/s，绝对驱动力 F=1250+delta_F N；500 N 增量预测最终速度增量 10 m/s，时间常数 20 s。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["speed_deviation", "m/s"]]` |
| 输入行 [名称] | `inputs` | `[["drive_force_deviation"]]` |
| 输入单位 | `input_unit` | `"N"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `5` |
| 输入下限 | `input_min` | `-500` |
| 输入上限 | `input_max` | `500` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `18.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-15` |
| 输出上限 | `output_max` | `15` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.5` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `20` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `20` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 极点 -0.05，名义稳定.
2. nonminimum_phase: 无有限零点.
3. significant_delay: 假设方程无纯迟延.
4. relative_degree: 相对阶次 1.
5. sensing_actuation_adequacy: 该一阶实现由速度可观、由力可控.
6. nonlinearity_strength: 局部模型为线性.
7. coupling_underactuation: 单输入、单主要输出.
8. uncertainty_variation: 未知，没有参数复测.
模型与范围：1000 d(delta_v)/dt + 50 delta_v = delta_F；G(s)=1/(1000s+50)。绝对速度 v=25+delta_v m/s，绝对驱动力 F=1250+delta_F N；500 N 增量预测最终速度增量 10 m/s，时间常数 20 s。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 22. 四分之一车双质量悬架

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 22 题 [Ch2-02]。定位：Example 2.2, PDF 114-122。

原题保留：四分之一车双质量悬架。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用簧载质量 375 kg、车轮质量 20 kg、悬架刚度 130000 N/m、轮胎刚度 1000000 N/m 和阻尼 9800 N*s/m；施加 0.01、0.025、0.05 m 有界路面阶跃，以 1 ms 同步记录车身、车轮与悬架行程。 来源模型方程（按原变量定义，仅作数学背景）：m_1\ddot x+b(\dot x-\dot y)+k_s(x-y)+k_w(x-r)=0. ; m_2\ddot y+b(\dot y-\dot x)+k_s(y-x)=0. ; \begin{bmatrix} m_1s^2+bs+k_s+k_w&-(bs+k_s)\\ -(bs+k_s)&m_2s^2+bs+k_s \end{bmatrix} \begin{bmatrix}X\\Y\end{bmatrix} =\begin{bmatrix}k_wR\\0\end{bmatrix}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四分之一车双质量悬架。本次仅做外部软件模型的适配子任务：使 body_displacement 保持在 0.002 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 22 题 [Ch2-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["body_displacement", "m"]]` |
| 输入行 [名称] | `inputs` | `[["road_displacement"]]` |
| 输入单位 | `input_unit` | `"m"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.002` |
| 输入下限 | `input_min` | `-0.05` |
| 输入上限 | `input_max` | `0.05` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.12` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.1` |
| 输出上限 | `output_max` | `0.1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.004` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：两个质量产生四状态；来源路面到车身通道同时含分子零点和柔性动态.
5. sensing_actuation_adequacy: 来源模型先验：仅车身位移不能评价轮胎贴地和悬架行程，这些原目标在标量子任务之外.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用簧载质量 375 kg、车轮质量 20 kg、悬架刚度 130000 N/m、轮胎刚度 1000000 N/m 和阻尼 9800 N*s/m；施加 0.01、0.025、0.05 m 有界路面阶跃，以 1 ms 同步记录车身、车轮与悬架行程。 来源模型方程（按原变量定义，仅作数学背景）：m_1\ddot x+b(\dot x-\dot y)+k_s(x-y)+k_w(x-r)=0. ; m_2\ddot y+b(\dot y-\dot x)+k_s(y-x)=0. ; \begin{bmatrix} m_1s^2+bs+k_s+k_w&-(bs+k_s)\\ -(bs+k_s)&m_2s^2+bs+k_s \end{bmatrix} \begin{bmatrix}X\\Y\end{bmatrix} =\begin{bmatrix}k_wR\\0\end{bmatrix}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 23. 刚性卫星单轴姿态

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 23 题 [Ch2-03]。定位：Example 2.3, PDF 123-130。

原题保留：刚性卫星单轴姿态。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

I=1200 kg*m^2，I theta_ddot=torque；G(s)=1/(1200s^2)。输入固定为机体力矩 Nm，不是推力 N。12 Nm 阶跃预测角加速度 0.01 rad/s^2，没有有限稳态角度；角速度仅为辅助记录。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：刚性卫星单轴姿态。本次仅做外部软件模型的适配子任务：使 attitude_angle 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 23 题 [Ch2-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 I=1200 kg*m^2，I theta_ddot=torque；G(s)=1/(1200s^2)。输入固定为机体力矩 Nm，不是推力 N。12 Nm 阶跃预测角加速度 0.01 rad/s^2，没有有限稳态角度；角速度仅为辅助记录。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["attitude_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-50` |
| 输入上限 | `input_max` | `50` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.24` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.2` |
| 输出上限 | `output_max` | `0.2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.01` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `20` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `20` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
第 1–7 项仅对给定适配名义数学模型及主要输入输出已知，第 8 项未知。这些是模型先验，不是硬件观测或协议绑定记录；真实传感器、标定和执行器仍未验证.
1. open_loop_stability: unstable（不稳定）：名义双积分器在非零初始角速度下会产生无界角度.
2. nonminimum_phase: minimum-phase（最小相位）：名义力矩到角度传递函数无有限零点.
3. significant_delay: not_significant（无显著迟延）：名义刚体方程不含纯迟延.
4. relative_degree: 相对阶次 2.
5. sensing_actuation_adequacy: adequate（对名义模型充分）：理想角度时序使两个状态可观，机体力矩使其可控.
6. nonlinearity_strength: weak（弱）：适配后的名义小角度方程为线性方程.
7. coupling_underactuation: siso：一个机体力矩输入控制一个主要角度；角速度是内部状态，不是另一独立控制输出.
8. uncertainty_variation: 未知，未复测惯量和扰动.
模型与范围：I=1200 kg*m^2，I theta_ddot=torque；G(s)=1/(1200s^2)。输入固定为机体力矩 Nm，不是推力 N。12 Nm 阶跃预测角加速度 0.01 rad/s^2，没有有限稳态角度；角速度仅为辅助记录。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 24. 柔性卫星共址与非共址模型

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 24 题 [Ch2-04]。定位：Example 2.4, PDF 129-135。

原题保留：柔性卫星共址与非共址模型。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用主刚体惯量 800 kg*m^2、远端惯量 200 kg*m^2、扭转刚度 80 Nm/rad、扭转阻尼 2 Nm*s/rad；施加 +/-5 与 +/-10 Nm 力矩脉冲，以 0.01 s 记录两端角度和角速度。 来源模型方程（按原变量定义，仅作数学背景）：I_1\ddot\theta_1+b(\dot\theta_1-\dot\theta_2)+k(\theta_1-\theta_2)=T_c, ; I_2\ddot\theta_2+b(\dot\theta_2-\dot\theta_1)+k(\theta_2-\theta_1)=0. ; \begin{bmatrix}I_1s^2+k&-k\\-k&I_2s^2+k\end{bmatrix} \begin{bmatrix}\Theta_1\\\Theta_2\end{bmatrix} =\begin{bmatrix}T_c\\0\end{bmatrix}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：柔性卫星共址与非共址模型。本次仅做外部软件模型的适配子任务：使 main_body_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 24 题 [Ch2-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["main_body_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["main_body_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-10` |
| 输入上限 | `input_max` | `10` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：共址角度含柔性零点，远端通道不同；此处仅选择主机体角度.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用主刚体惯量 800 kg*m^2、远端惯量 200 kg*m^2、扭转刚度 80 Nm/rad、扭转阻尼 2 Nm*s/rad；施加 +/-5 与 +/-10 Nm 力矩脉冲，以 0.01 s 记录两端角度和角速度。 来源模型方程（按原变量定义，仅作数学背景）：I_1\ddot\theta_1+b(\dot\theta_1-\dot\theta_2)+k(\theta_1-\theta_2)=T_c, ; I_2\ddot\theta_2+b(\dot\theta_2-\dot\theta_1)+k(\theta_2-\theta_1)=0. ; \begin{bmatrix}I_1s^2+k&-k\\-k&I_2s^2+k\end{bmatrix} \begin{bmatrix}\Theta_1\\\Theta_2\end{bmatrix} =\begin{bmatrix}T_c\\0\end{bmatrix}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 25. 四旋翼滚转俯仰偏航控制分配

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 25 题 [Ch2-05]。定位：Example 2.5, PDF 135-141。

原题保留：四旋翼滚转俯仰偏航控制分配。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

假定外部分配器能够实现下列等效机体力矩，未提供已验证的分配器标定：Ix=Iy=0.02，Iz=0.05 kg*m^2；phi_ddot=roll_torque/Ix，theta_ddot=pitch_torque/Iy，psi_ddot=yaw_torque/Iz。这是三轴局部子任务，不是四旋翼推力模型；未提供旋翼混控或高度控制器。三路主要姿态角共同目标为 0.1 rad。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四旋翼滚转俯仰偏航控制分配。本次仅做外部软件模型的适配子任务：使 roll_angle, pitch_angle, yaw_angle 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 25 题 [Ch2-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 假定外部分配器能够实现下列等效机体力矩，未提供已验证的分配器标定：Ix=Iy=0.02，Iz=0.05 kg*m^2；phi_ddot=roll_torque/Ix，theta_ddot=pitch_torque/Iy，psi_ddot=yaw_torque/Iz。这是三轴局部子任务，不是四旋翼推力模型；未提供旋翼混控或高度控制器。三路主要姿态角共同目标为 0.1 rad。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["roll_angle", "rad"], ["pitch_angle", "rad"], ["yaw_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["roll_torque"], ["pitch_torque"], ["yaw_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-0.02` |
| 输入上限 | `input_max` | `0.02` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.01` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `4` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `4` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下先验仅针对适配后的名义三轴虚拟力矩模型，来自数学模型，不是飞行实测。实际旋翼与分配器不在本任务内，未提供标定或实验记录。
1. open_loop_stability: 不稳定：每个独立的角度/力矩通道均为双积分器。
2. nonminimum_phase: 最小相位：名义角度/力矩通道无有限零点。
3. significant_delay: 无显著迟延：名义虚拟力矩方程不含迟延。
4. relative_degree: 每个主要角度/虚拟力矩通道的相对阶次为 2。
5. sensing_actuation_adequacy: 对名义模型充分：三路理想主要角度时序使其六个状态可观，三个独立虚拟力矩使其可控。
6. nonlinearity_strength: 弱：本次适配的小角度模型为线性模型。
7. coupling_underactuation: 解耦：名义三输入三输出虚拟力矩模型为对角结构，每个角度有独立力矩输入。
8. uncertainty_variation: 未知：未进行惯量或分配误差变化试验。
范围：第1节保留数值惯量和方程作为模型背景。本回复只给诊断先验，不提供旋翼混控、已验证的分配器标定或真实飞行证据；不能从这个虚拟通道任务推断整架飞机的驱动或传感性质。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。 当前三输入三输出任务超出已有 2×2 控制器路线能力；不能将其冒充双加热器验证。

---

## 26. 单摆非线性模型、小角度线性化与仿真

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 26 题 [Ch2-06]。定位：Examples 2.6-2.7, PDF 141-151。

原题保留：单摆非线性模型、小角度线性化与仿真。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用质量 1 kg、摆长 1 m、重力加速度 9.81 m/s^2；以 0.02 s 采样仿真 10 s，对正弦非线性模型和小角线性模型比较 1 Nm 与 4 Nm 力矩阶跃。 来源模型方程（按原变量定义，仅作数学背景）：T_c-mg\ell\sin\theta=m\ell^2\ddot\theta, ; \ddot\theta+\frac g\ell\sin\theta=\frac{T_c}{m\ell^2}. ; \ddot\theta+\frac g\ell\theta=\frac{T_c}{m\ell^2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：单摆非线性模型、小角度线性化与仿真。本次仅做外部软件模型的适配子任务：使 pendulum_angle 保持在 0.01 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 26 题 [Ch2-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pendulum_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["pivot_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.01` |
| 输入下限 | `input_min` | `-4` |
| 输入上限 | `input_max` | `4` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.6` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.5` |
| 输出上限 | `output_max` | `0.5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：下垂小角度摆极点为纯虚数；无阻尼振荡不等于渐近稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：重力含 sin(theta)，局部近似误差随角度增大.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用质量 1 kg、摆长 1 m、重力加速度 9.81 m/s^2；以 0.02 s 采样仿真 10 s，对正弦非线性模型和小角线性模型比较 1 Nm 与 4 Nm 力矩阶跃。 来源模型方程（按原变量定义，仅作数学背景）：T_c-mg\ell\sin\theta=m\ell^2\ddot\theta, ; \ddot\theta+\frac g\ell\sin\theta=\frac{T_c}{m\ell^2}. ; \ddot\theta+\frac g\ell\theta=\frac{T_c}{m\ell^2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 27. 吊车摆与倒立摆耦合

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 27 题 [Ch2-07]。定位：Example 2.8, PDF 151-159。

原题保留：吊车摆与倒立摆耦合。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用小车质量 1 kg、摆质量 0.2 kg、质心距离 0.5 m、转动惯量 0.006 kg*m^2、摩擦 0.1 N*s/m、推力限制 20 N、行程限制 1.5 m 和初始摆角 0.05 rad。 来源模型方程（按原变量定义，仅作数学背景）：(I+m_p\ell^2)\ddot\theta+m_pg\ell\theta=-m_p\ell\ddot x, ; (m_t+m_p)\ddot x+b\dot x+m_p\ell\ddot\theta=u. ; D_m=(I+m_p\ell^2)(m_t+m_p)-m_p^2\ell^2, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：吊车摆与倒立摆耦合。本次仅做外部软件模型的适配子任务：使 cart_position 保持在 0.03 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 27 题 [Ch2-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["cart_position", "m"]]` |
| 输入行 [名称] | `inputs` | `[["cart_force"]]` |
| 输入单位 | `input_unit` | `"N"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.03` |
| 输入下限 | `input_min` | `-20` |
| 输入上限 | `input_max` | `20` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.8` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.5` |
| 输出上限 | `output_max` | `1.5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.06` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：倒立平衡点含不稳定实极点；下垂平衡结论不能证明倒立平衡.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：摆车动力学包含随角度变化的非线性耦合.
7. coupling_underactuation: 来源模型先验：一个小车推力不能独立控制车位和摆角；标量车位保持不能证明摆平衡.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用小车质量 1 kg、摆质量 0.2 kg、质心距离 0.5 m、转动惯量 0.006 kg*m^2、摩擦 0.1 N*s/m、推力限制 20 N、行程限制 1.5 m 和初始摆角 0.05 rad。 来源模型方程（按原变量定义，仅作数学背景）：(I+m_p\ell^2)\ddot\theta+m_pg\ell\theta=-m_p\ell\ddot x, ; (m_t+m_p)\ddot x+b\dot x+m_p\ell\ddot\theta=u. ; D_m=(I+m_p\ell^2)(m_t+m_p)-m_p^2\ell^2,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 28. 桥接 T 型 RC 电路

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 28 题 [Ch2-08]。定位：Example 2.9, PDF 172-173。

原题保留：桥接 T 型 RC 电路。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 R1=R2=10 kohm、C1=C2=10 uF，得到 G(s)=(0.01 s^2+0.2 s+1)/(0.01 s^2+0.3 s+1)。用 +/-1 V 试验核对低频和高频的单位增益以及桥接支路的中频响应。 来源模型方程（按原变量定义，仅作数学背景）：v_1=v_i. ; -\frac{v_1-v_2}{R_1}+\frac{v_2-v_3}{R_2}+C_1\dot v_2=0. ; \frac{v_3-v_2}{R_2}+C_2\frac{d(v_3-v_1)}{dt}=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：桥接 T 型 RC 电路。本次仅做外部软件模型的适配子任务：使 output_voltage 保持在 0.04 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 28 题 [Ch2-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["output_voltage", "V"]]` |
| 输入行 [名称] | `inputs` | `[["input_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.04` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想来源网络有直接通道，相对阶次 0；不能改称严格真有理一阶对象.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 R1=R2=10 kohm、C1=C2=10 uF，得到 G(s)=(0.01 s^2+0.2 s+1)/(0.01 s^2+0.3 s+1)。用 +/-1 V 试验核对低频和高频的单位增益以及桥接支路的中频响应。 来源模型方程（按原变量定义，仅作数学背景）：v_1=v_i. ; -\frac{v_1-v_2}{R_1}+\frac{v_2-v_3}{R_2}+C_1\dot v_2=0. ; \frac{v_3-v_2}{R_2}+C_2\frac{d(v_3-v_1)}{dt}=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 29. 电流源驱动的 RLC 电路

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 29 题 [Ch2-09]。定位：Example 2.10, PDF 173-175。

原题保留：电流源驱动的 RLC 电路。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 R1=R2=10 ohm、C1=C2=0.01 F、L=0.1 H，施加 0.1 A 有界电流阶跃，并记录全部电容电压和电感电流。 来源模型方程（按原变量定义，仅作数学背景）：i(t)=\frac{v_1}{R_1}+C_1\dot v_1+i_L. ; i_L=C_2\dot v_2+\frac{v_2}{R_2},\qquad v_1-v_2=L\dot i_L. ; \begin{bmatrix}\dot v_1\\\dot v_2\\\dot i_L\end{bmatrix} = \begin{bmatrix} -1/(R_1C_1)&0&-1/C_1\\ 0&-1/(R_2C_2)&1/C_2\\ 1/L&-1/L&0 \end{bmatrix} \begin{bmatrix}v_1\\v_2\\i_L\end{bmatrix} +\begin{bmatrix}1/C_1\\0\\0\end{bmatrix}i. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：电流源驱动的 RLC 电路。本次仅做外部软件模型的适配子任务：使 capacitor_1_voltage 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 29 题 [Ch2-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["capacitor_1_voltage", "V"]]` |
| 输入行 [名称] | `inputs` | `[["source_current"]]` |
| 输入单位 | `input_unit` | `"A"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-0.1` |
| 输入上限 | `input_max` | `0.1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `6.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-5` |
| 输出上限 | `output_max` | `5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.2` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：C1、C2、L 形成三个储能状态；电流输入为 A、电容电压输出为 V.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 R1=R2=10 ohm、C1=C2=0.01 F、L=0.1 H，施加 0.1 A 有界电流阶跃，并记录全部电容电压和电感电流。 来源模型方程（按原变量定义，仅作数学背景）：i(t)=\frac{v_1}{R_1}+C_1\dot v_1+i_L. ; i_L=C_2\dot v_2+\frac{v_2}{R_2},\qquad v_1-v_2=L\dot i_L. ; \begin{bmatrix}\dot v_1\\\dot v_2\\\dot i_L\end{bmatrix} = \begin{bmatrix} -1/(R_1C_1)&0&-1/C_1\\ 0&-1/(R_2C_2)&1/C_2\\ 1/L&-1/L&0 \end{bmatrix} \begin{bmatrix}v_1\\v_2\\i_L\end{bmatrix} +\begin{bmatrix}1/C_1\\0\\0\end{bmatrix}i.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 30. 理想运放加权加法器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 30 题 [Ch2-10]。定位：Example 2.11, PDF 177-178。

原题保留：理想运放加权加法器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Rf=20 kohm、R1=10 kohm、R2=20 kohm，得到 vout=-2 v1-v2；各输入限制为 +/-5 V，输出限制为 +/-12 V。 来源模型方程（按原变量定义，仅作数学背景）：i_i=\frac{v_i-v_-}{R_i}=\frac{v_i}{R_i}. ; i_f=\frac{v_--v_o}{R_f}=-\frac{v_o}{R_f}. ; \sum_i\frac{v_i}{R_i}+\frac{v_o}{R_f}=0, \qquad v_o=-R_f\sum_i\frac{v_i}{R_i}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：理想运放加权加法器。本次仅做外部软件模型的适配子任务：使 output_voltage 保持在 0.24 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 30 题 [Ch2-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["output_voltage", "V"]]` |
| 输入行 [名称] | `inputs` | `[["voltage_1"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.24` |
| 输入下限 | `input_min` | `-5` |
| 输入上限 | `input_max` | `5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `14.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-12` |
| 输出上限 | `output_max` | `12` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.48` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 来源模型先验：vout=-2v1-v2 是负静态加权和，不是逆向暂态.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想来源网络有直接通道，相对阶次 0；不能改称严格真有理一阶对象.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：标量适配固定 v2=0、调节 v1；原题具有两个求和电压输入.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Rf=20 kohm、R1=10 kohm、R2=20 kohm，得到 vout=-2 v1-v2；各输入限制为 +/-5 V，输出限制为 +/-12 V。 来源模型方程（按原变量定义，仅作数学背景）：i_i=\frac{v_i-v_-}{R_i}=\frac{v_i}{R_i}. ; i_f=\frac{v_--v_o}{R_f}=-\frac{v_o}{R_f}. ; \sum_i\frac{v_i}{R_i}+\frac{v_o}{R_f}=0, \qquad v_o=-R_f\sum_i\frac{v_i}{R_i}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 31. 理想运放积分器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 31 题 [Ch2-11]。定位：Example 2.12, PDF 179-180。

原题保留：理想运放积分器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 Rin=100 kohm、C=10 uF，使 Rin*C=1 s；+1 V 输入产生 -1 V/s 输出斜率，并在输出达到 +/-10 V 前停止。 来源模型方程（按原变量定义，仅作数学背景）：i_{in}=\frac{v_i-v_-}{R}=\frac{v_i}{R}. ; i_C=C\frac{d(v_--v_o)}{dt}=-C\dot v_o. ; \frac{v_i}{R}+C\dot v_o=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：理想运放积分器。本次仅做外部软件模型的适配子任务：使 integrator_output_voltage 保持在 0.2 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 31 题 [Ch2-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["integrator_output_voltage", "V"]]` |
| 输入行 [名称] | `inputs` | `[["input_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.2` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `12.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-10.0` |
| 输出上限 | `output_max` | `10.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.4` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想输入输出通道为单积分器，相对阶次 1.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 Rin=100 kohm、C=10 uF，使 Rin*C=1 s；+1 V 输入产生 -1 V/s 输出斜率，并在输出达到 +/-10 V 前停止。 来源模型方程（按原变量定义，仅作数学背景）：i_{in}=\frac{v_i-v_-}{R}=\frac{v_i}{R}. ; i_C=C\frac{d(v_--v_o)}{dt}=-C\dot v_o. ; \frac{v_i}{R}+C\dot v_o=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 32. 扬声器及驱动电路机电耦合

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 32 题 [Ch2-12]。定位：Examples 2.13-2.14, PDF 183-187。

原题保留：扬声器及驱动电路机电耦合。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用磁通密度 0.5 T、直径 2 cm 的 20 匝线圈，得到 Bl=0.63 N/A；再取 M=0.02 kg、b=0.2 N*s/m、L=1 mH、R=8 ohm。 来源模型方程（按原变量定义，仅作数学背景）：F=B\ell_w i\equiv K_fi,\qquad K_f=0.5(1.26)=0.63\,\mathrm{N/A}. ; M\ddot x+b\dot x=K_fi. ; e=B\ell_w\dot x\equiv K_e\dot x,\qquad K_e=0.63. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：扬声器及驱动电路机电耦合。本次仅做外部软件模型的适配子任务：使 cone_displacement 保持在 0.0002 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 32 题 [Ch2-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["cone_displacement", "m"]]` |
| 输入行 [名称] | `inputs` | `[["amplifier_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0002` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.012` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.01` |
| 输出上限 | `output_max` | `0.01` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0004` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用磁通密度 0.5 T、直径 2 cm 的 20 匝线圈，得到 Bl=0.63 N/A；再取 M=0.02 kg、b=0.2 N*s/m、L=1 mH、R=8 ohm。 来源模型方程（按原变量定义，仅作数学背景）：F=B\ell_w i\equiv K_fi,\qquad K_f=0.5(1.26)=0.63\,\mathrm{N/A}. ; M\ddot x+b\dot x=K_fi. ; e=B\ell_w\dot x\equiv K_e\dot x,\qquad K_e=0.63.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 33. 直流电机位置与速度模型

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 33 题 [Ch2-13]。定位：Example 2.15, PDF 190-194。

原题保留：直流电机位置与速度模型。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

J=0.01，b=0.1，Kt=Ke=0.01，R=1，L=0.5（SI）。电压到速度 G=0.01/(0.005s^2+0.06s+0.1001)，电压到位置为 G/s。位置是唯一主要输出；速度 rad/s 和电流 A 是协议辅助通道，不是独立被控输出。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机位置与速度模型。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.2 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 33 题 [Ch2-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 J=0.01，b=0.1，Kt=Ke=0.01，R=1，L=0.5（SI）。电压到速度 G=0.01/(0.005s^2+0.06s+0.1001)，电压到位置为 G/s。位置是唯一主要输出；速度 rad/s 和电流 A 是协议辅助通道，不是独立被控输出。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["armature_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.2` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `4` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `4` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
第 1–7 项仅对给定适配名义数学模型及主要输入输出已知，第 8 项未知。这些是模型先验，不是硬件观测或协议绑定记录；真实传感器、标定和执行器仍未验证.
1. open_loop_stability: unstable（BIBO 意义下不稳定）：位置通道包含积分器；其零输入状态不渐近稳定.
2. nonminimum_phase: minimum-phase（最小相位）：名义电压到位置通道无有限零点.
3. significant_delay: not_significant（无显著迟延）：名义电气/机械方程不含纯迟延.
4. relative_degree: high（高）：主要位置通道相对阶次为 3；辅助速度相对阶次为 2，并非第二个主要输出.
5. sensing_actuation_adequacy: adequate（对名义模型充分）：理想位置时序使三个状态可观，电压使其可控.
6. nonlinearity_strength: weak（弱）：名义机电方程为线性方程.
7. coupling_underactuation: siso：一个电压输入和一个主要位置输出；辅助电流、速度是内部观测量，不是独立控制通道，也不构成欠驱动证据.
8. uncertainty_variation: 未知，没有摩擦和负载复测.
模型与范围：J=0.01，b=0.1，Kt=Ke=0.01，R=1，L=0.5（SI）。电压到速度 G=0.01/(0.005s^2+0.06s+0.1001)，电压到位置为 G/s。位置是唯一主要输出；速度 rad/s 和电流 A 是协议辅助通道，不是独立被控输出。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 34. 齿轮传动与输出侧等效惯量

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 34 题 [Ch2-14]。定位：Section 2.3.3, PDF 197-201。

原题保留：齿轮传动与输出侧等效惯量。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用齿轮比 n=4、电机侧惯量 J1=0.002 kg*m^2、负载惯量 J2=0.03 kg*m^2、b1=0.001 与 b2=0.02 Nm*s/rad。 来源模型方程（按原变量定义，仅作数学背景）：n=\frac{r_2}{r_1}=\frac{N_2}{N_1}. ; \frac{T_2}{T_1}=\frac{r_2}{r_1}=n. ; \frac{\omega_1}{\omega_2}=\frac{\theta_1}{\theta_2}=n. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：齿轮传动与输出侧等效惯量。本次仅做外部软件模型的适配子任务：使 motor_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 34 题 [Ch2-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["motor_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用齿轮比 n=4、电机侧惯量 J1=0.002 kg*m^2、负载惯量 J2=0.03 kg*m^2、b1=0.001 与 b2=0.02 Nm*s/rad。 来源模型方程（按原变量定义，仅作数学背景）：n=\frac{r_2}{r_1}=\frac{N_2}{N_1}. ; \frac{T_2}{T_1}=\frac{r_2}{r_1}=n. ; \frac{\omega_1}{\omega_2}=\frac{\theta_1}{\theta_2}=n.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 35. 房间热损失一阶模型

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 35 题 [Ch2-15]。定位：Example 2.16, PDF 203-205。

原题保留：房间热损失一阶模型。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 90000 Btu/h 炉子；当室外 32 degF、室内 60 degF 时，开炉 0.1 h 升温 2 degF，停炉 40 min 降温 2 degF。由此得到 C=3913.04 Btu/degF、R=0.002385 degF/(Btu/h)。 来源模型方程（按原变量定义，仅作数学背景）：q_1=\frac{T_O-T_I}{R_1},\qquad q_2=\frac{T_O-T_I}{R_2}. ; C_I\dot T_I=q_1+q_2 =\left(\frac1{R_1}+\frac1{R_2}\right)(T_O-T_I). ; \frac{T_I(s)}{T_O(s)}=\frac{H}{C_Is+H} =\frac1{\tau s+1},\qquad \tau=\frac{C_I}{H}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：房间热损失一阶模型。本次仅做外部软件模型的适配子任务：使 room_temperature 保持在 60 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 35 题 [Ch2-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["room_temperature", "degF"]]` |
| 输入行 [名称] | `inputs` | `[["heater_fraction"]]` |
| 输入单位 | `input_unit` | `"fraction"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `60` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `108.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `32` |
| 输出上限 | `output_max` | `90` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `1.16` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：一个自然热状态；可控制热输入是对原自由降温模型明确新增的扩展.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 90000 Btu/h 炉子；当室外 32 degF、室内 60 degF 时，开炉 0.1 h 升温 2 degF，停炉 40 min 降温 2 degF。由此得到 C=3913.04 Btu/degF、R=0.002385 degF/(Btu/h)。 来源模型方程（按原变量定义，仅作数学背景）：q_1=\frac{T_O-T_I}{R_1},\qquad q_2=\frac{T_O-T_I}{R_2}. ; C_I\dot T_I=q_1+q_2 =\left(\frac1{R_1}+\frac1{R_2}\right)(T_O-T_I). ; \frac{T_I(s)}{T_O(s)}=\frac{H}{C_Is+H} =\frac1{\tau s+1},\qquad \tau=\frac{C_I}{H}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 36. 双热容温控过程

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 36 题 [Ch2-16]。定位：Example 2.17, PDF 206-209。

原题保留：双热容温控过程。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 C1=10000 J/degC、C2=15000 J/degC、Hx=200 W/degC、H1=100 W/degC、H2=150 W/degC，并施加 250、500、750、1000 W 热流阶跃。 来源模型方程（按原变量定义，仅作数学背景）：C_1\dot T_1=u-H_1T_1-H_x(T_1-T_2). ; C_2\dot T_2=H_x(T_1-T_2)-H_2T_2. ; \begin{bmatrix} C_1s+H_1+H_x&-H_x\\ -H_x&C_2s+H_2+H_x \end{bmatrix} \begin{bmatrix}T_1\\T_2\end{bmatrix} =\begin{bmatrix}U\\0\end{bmatrix}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：双热容温控过程。本次仅做外部软件模型的适配子任务：使 body_1_temperature_rise 保持在 0.15 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 36 题 [Ch2-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["body_1_temperature_rise", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["heater_power"]]` |
| 输入单位 | `input_unit` | `"W"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.15` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `1000` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `18.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `15` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.3` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：两个热储能状态加正散热系数构成二阶热通道.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 C1=10000 J/degC、C2=15000 J/degC、Hx=200 W/degC、H1=100 W/degC、H2=150 W/degC，并施加 250、500、750、1000 W 热流阶跃。 来源模型方程（按原变量定义，仅作数学背景）：C_1\dot T_1=u-H_1T_1-H_x(T_1-T_2). ; C_2\dot T_2=H_x(T_1-T_2)-H_2T_2. ; \begin{bmatrix} C_1s+H_1+H_x&-H_x\\ -H_x&C_2s+H_2+H_x \end{bmatrix} \begin{bmatrix}T_1\\T_2\end{bmatrix} =\begin{bmatrix}U\\0\end{bmatrix}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 37. 带双热惯性与测量延迟的换热器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 37 题 [Ch2-17]。定位：Example 2.18, PDF 209-212。

原题保留：带双热惯性与测量延迟的换热器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

局部模型 G(s)=0.5 exp(-10s)/[(30s+1)(60s+1)]，输入为阀开度百分点增量、输出为摄氏温差。仿真假定阀偏置 50%、温度偏置 60 degC；绝对阀开度为 50+delta_u，范围 [40,60]%。原始阀门与温差乘积为非线性项。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：带双热惯性与测量延迟的换热器。本次仅做外部软件模型的适配子任务：使 outlet_temperature_deviation 保持在 2 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 37 题 [Ch2-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 局部模型 G(s)=0.5 exp(-10s)/[(30s+1)(60s+1)]，输入为阀开度百分点增量、输出为摄氏温差。仿真假定阀偏置 50%、温度偏置 60 degC；绝对阀开度为 50+delta_u，范围 [40,60]%。原始阀门与温差乘积为非线性项。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["outlet_temperature_deviation", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["valve_opening_deviation"]]` |
| 输入单位 | `input_unit` | `"percentage_point"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `2` |
| 输入下限 | `input_min` | `-10` |
| 输入上限 | `input_max` | `10` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `12.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-10` |
| 输出上限 | `output_max` | `10` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.2` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `90` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `90` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
第 1–7 项仅对给定适配名义数学模型及主要输入输出已知，第 8 项未知。这些是模型先验，不是硬件观测或协议绑定记录；真实传感器、标定和执行器仍未验证.
1. open_loop_stability: stable（稳定）：名义极点为 -1/30 和 -1/60.
2. nonminimum_phase: minimum-phase（不含迟延的有理部分为最小相位）：该部分无有限零点；显式测量迟延单独诊断.
3. significant_delay: significant（显著）：名义模型明确包含 10 s 测量迟延.
4. relative_degree: low（低）：不含迟延的有理动态部分相对阶次为 2.
5. sensing_actuation_adequacy: adequate（对名义迟延输出模型充分）：其二状态有理实现可控，考虑已知测量迟延后的理想出口温度时序可观测这些状态.
6. nonlinearity_strength: weak（本次局部适配为弱）：阀门到温度的模型已在给定偏置附近线性化；原非线性乘积属于原题更宽的工作范围.
7. coupling_underactuation: siso：一个阀门开度偏差输入和一个主要出口温度偏差输出.
8. uncertainty_variation: 未知，未复测阀门或传热参数.
模型与范围：局部模型 G(s)=0.5 exp(-10s)/[(30s+1)(60s+1)]，输入为阀开度百分点增量、输出为摄氏温差。仿真假定阀偏置 50%、温度偏置 60 degC；绝对阀开度为 50+delta_u，范围 [40,60]%。原始阀门与温差乘积为非线性项。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 38. 水箱平方根出流与工作点线性化

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 38 题 [Ch2-18]。定位：Examples 2.19/2.21, PDF 213-219。

原题保留：水箱平方根出流与工作点线性化。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用水密度 1000 kg/m^3、槽面积 0.05 m^2、名义液位 0.15 m、名义出流 200 g/min；在线性化平方根出流后测试 +/-25 与 +/-50 g/min 泵流量变化。 来源模型方程（按原变量定义，仅作数学背景）：A\rho\dot h=w_{in}-w_{out}. ; w_{out}=\frac1R\sqrt{p_1-p_a} =\frac1R\sqrt{\rho gh}, ; \dot h=\frac1{A\rho}\left(w_{in}-\frac1R\sqrt{\rho gh}\right). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：水箱平方根出流与工作点线性化。本次仅做外部软件模型的适配子任务：使 level_deviation 保持在 0.002 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 38 题 [Ch2-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["level_deviation", "m"]]` |
| 输入行 [名称] | `inputs` | `[["inlet_flow_deviation"]]` |
| 输入单位 | `input_unit` | `"g/min"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.002` |
| 输入下限 | `input_min` | `-50` |
| 输入上限 | `input_max` | `50` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.12` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.1` |
| 输出上限 | `output_max` | `0.1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.004` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：平方根出流是非线性；增量模型要求正 h0 和平衡名义进流.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用水密度 1000 kg/m^3、槽面积 0.05 m^2、名义液位 0.15 m、名义出流 200 g/min；在线性化平方根出流后测试 +/-25 与 +/-50 g/min 泵流量变化。 来源模型方程（按原变量定义，仅作数学背景）：A\rho\dot h=w_{in}-w_{out}. ; w_{out}=\frac1R\sqrt{p_1-p_a} =\frac1R\sqrt{\rho gh}, ; \dot h=\frac1{A\rho}\left(w_{in}-\frac1R\sqrt{\rho gh}\right).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 39. 压力驱动的单腔液压活塞

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 39 题 [Ch2-19]。定位：Example 2.20, PDF 214-215。

原题保留：压力驱动的单腔液压活塞。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：活塞质量 50 kg、面积 0.01 m^2：100 kPa 压差对应 1000 N 和 20 m/s^2 加速度。位置单位 m；速度仅为辅助量，单位 m/s。 来源模型方程（按原变量定义，仅作数学背景）：F_p=Ap. ; M\ddot x=Ap-F_D. ; Ms^2X=AP-F_D, \quad \frac{X}{P}=\frac{A}{Ms^2}, \quad \frac{X}{F_D}=-\frac1{Ms^2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：压力驱动的单腔液压活塞。本次仅做外部软件模型的适配子任务：使 piston_position 保持在 0.01 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 39 题 [Ch2-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["piston_position", "m"]]` |
| 输入行 [名称] | `inputs` | `[["chamber_pressure_difference"]]` |
| 输入单位 | `input_unit` | `"kPa"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.01` |
| 输入下限 | `input_min` | `-100` |
| 输入上限 | `input_max` | `100` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.6` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.5` |
| 输出上限 | `output_max` | `0.5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：活塞质量 50 kg、面积 0.01 m^2：100 kPa 压差对应 1000 N 和 20 m/s^2 加速度。位置单位 m；速度仅为辅助量，单位 m/s。 来源模型方程（按原变量定义，仅作数学背景）：F_p=Ap. ; M\ddot x=Ap-F_D. ; Ms^2X=AP-F_D, \quad \frac{X}{P}=\frac{A}{Ms^2}, \quad \frac{X}{F_D}=-\frac1{Ms^2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 40. 液压舵面阀位到角度的负载相关积分模型

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 40 题 [Ch2-20]。定位：Example 2.22, PDF 220-224。

原题保留：液压舵面阀位到角度的负载相关积分模型。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用空载阀位到舵面角速度增益 0.8 rad/(s*mm)、阀行程 +/-5 mm、角度限制 +/-0.5 rad，并在负载使增益降为 0.72 与 0.64 rad/(s*mm) 时重复。 来源模型方程（按原变量定义，仅作数学背景）：Q_1=\frac{x}{\rho R_1}\sqrt{p_s-p_1},\qquad Q_2=\frac{x}{\rho R_2}\sqrt{p_2-p_e}. ; A\dot y=Q_1=Q_2. ; A(p_1-p_2)-F=m\ddot y,\qquad y=\ell\sin\theta. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：液压舵面阀位到角度的负载相关积分模型。本次仅做外部软件模型的适配子任务：使 surface_angle 保持在 0.01 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 40 题 [Ch2-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["surface_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["servo_valve_displacement"]]` |
| 输入单位 | `input_unit` | `"mm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.01` |
| 输入下限 | `input_min` | `-5` |
| 输入上限 | `input_max` | `5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.6` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.5` |
| 输出上限 | `output_max` | `0.5` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想输入输出通道为单积分器，相对阶次 1.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用空载阀位到舵面角速度增益 0.8 rad/(s*mm)、阀行程 +/-5 mm、角度限制 +/-0.5 rad，并在负载使增益降为 0.72 与 0.64 rad/(s*mm) 时重复。 来源模型方程（按原变量定义，仅作数学背景）：Q_1=\frac{x}{\rho R_1}\sqrt{p_s-p_1},\qquad Q_2=\frac{x}{\rho R_2}\sqrt{p_2-p_e}. ; A\dot y=Q_1=Q_2. ; A(p_1-p_2)-F=m\ddot y,\qquad y=\ell\sin\theta.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 41. 用叠加与时移检验线性时不变性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 41 题 [Ch3-01]。定位：Examples 3.1-3.2, PDF 277-279。

原题保留：用叠加与时移检验线性时不变性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 k=2 s^-1；采用 u1(t)=1、u2(t)=sin(t)、系数 1.5 与 -0.5、时移 1 s，以 0.01 s 采样 8 s，并比较叠加与时移响应。 来源模型方程（按原变量定义，仅作数学背景）：\mathcal L[y]=\alpha_1(\dot y_1+k(t)y_1)+\alpha_2(\dot y_2+k(t)y_2) =\alpha_1u_1+\alpha_2u_2, ; \dot y(t-\tau)+k(t)y(t-\tau). ; [k(t)-k(t-\tau)]y(t-\tau)=\tau y(t-\tau), 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用叠加与时移检验线性时不变性。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 41 题 [Ch3-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：稳定性依赖给定 k(t)，线性本身不证明稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：ydot+k(t)y=u 是线性方程，但除非 k(t) 恒定，否则为时变系统.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 k=2 s^-1；采用 u1(t)=1、u2(t)=sin(t)、系数 1.5 与 -0.5、时移 1 s，以 0.01 s 采样 8 s，并比较叠加与时移响应。 来源模型方程（按原变量定义，仅作数学背景）：\mathcal L[y]=\alpha_1(\dot y_1+k(t)y_1)+\alpha_2(\dot y_2+k(t)y_2) =\alpha_1u_1+\alpha_2u_2, ; \dot y(t-\tau)+k(t)y(t-\tau). ; [k(t)-k(t-\tau)]y(t-\tau)=\tau y(t-\tau),
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 42. 一阶系统冲激响应与卷积

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 42 题 [Ch3-02]。定位：Example 3.3, PDF 286-288。

原题保留：一阶系统冲激响应与卷积。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 k=0.5 s^-1；以 0.01 s 分辨率仿真 16 s 的单位冲激和单位阶跃，并把直接积分与 exp(-0.5 t) 卷积结果比较。 来源模型方程（按原变量定义，仅作数学背景）：\int_{0^-}^{0^+}\dot h\,dt+k\int_{0^-}^{0^+}h\,dt =\int_{0^-}^{0^+}\delta(t)\,dt=1. ; h(t)=e^{-kt}1(t). ; y(t)=(h*u)(t)=\int_0^t e^{-k(t-\tau)}u(\tau)\,d\tau. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：一阶系统冲激响应与卷积。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 42 题 [Ch3-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 k=0.5 s^-1；以 0.01 s 分辨率仿真 16 s 的单位冲激和单位阶跃，并把直接积分与 exp(-0.5 t) 卷积结果比较。 来源模型方程（按原变量定义，仅作数学背景）：\int_{0^-}^{0^+}\dot h\,dt+k\int_{0^-}^{0^+}h\,dt =\int_{0^-}^{0^+}\delta(t)\,dt=1. ; h(t)=e^{-kt}1(t). ; y(t)=(h*u)(t)=\int_0^t e^{-k(t-\tau)}u(\tau)\,d\tau.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 43. 由常微分方程求传递函数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 43 题 [Ch3-03]。定位：Example 3.4 and Eq. 3.26, PDF 292-295。

原题保留：由常微分方程求传递函数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 y_ddot+5 y_dot+4 y=2 u 且初值为零；施加 +/-0.5 与 +/-1 N 阶跃，以 0.01 s 采样 8 s，并核对 G(s)=2/(s^2+5s+4)。 来源模型方程（按原变量定义，仅作数学背景）：a_n y^{(n)}+\cdots+a_1\dot y+a_0y =b_m u^{(m)}+\cdots+b_1\dot u+b_0u. ; \mathcal L\{y^{(q)}\}=s^qY-s^{q-1}y(0^-)-\cdots-y^{(q-1)}(0^-). ; (a_ns^n+\cdots+a_0)Y=(b_ms^m+\cdots+b_0)U. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由常微分方程求传递函数。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 43 题 [Ch3-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 y_ddot+5 y_dot+4 y=2 u 且初值为零；施加 +/-0.5 与 +/-1 N 阶跃，以 0.01 s 采样 8 s，并核对 G(s)=2/(s^2+5s+4)。 来源模型方程（按原变量定义，仅作数学背景）：a_n y^{(n)}+\cdots+a_1\dot y+a_0y =b_m u^{(m)}+\cdots+b_1\dot u+b_0u. ; \mathcal L\{y^{(q)}\}=s^qY-s^{q-1}y(0^-)-\cdots-y^{(q-1)}(0^-). ; (a_ns^n+\cdots+a_0)Y=(b_ms^m+\cdots+b_0)U.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 44. RC 低通的传递函数与冲激响应

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 44 题 [Ch3-04]。定位：Example 3.5, PDF 296-297。

原题保留：RC 低通的传递函数与冲激响应。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 R=10 kohm、C=100 uF，得到 RC=1 s；以 0.01 s 采样 8 s，施加 0.25、0.5、0.75、1 V 阶跃。 来源模型方程（按原变量定义，仅作数学背景）：\frac{v_i-v_o}{R}=C\dot v_o. ; (RCs+1)V_o=V_i,\qquad G(s)=\frac{V_o}{V_i}=\frac1{RCs+1}. ; h(t)=\frac1{RC}e^{-t/(RC)}1(t). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：RC 低通的传递函数与冲激响应。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 44 题 [Ch3-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 R=10 kohm、C=100 uF，得到 RC=1 s；以 0.01 s 采样 8 s，施加 0.25、0.5、0.75、1 V 阶跃。 来源模型方程（按原变量定义，仅作数学背景）：\frac{v_i-v_o}{R}=C\dot v_o. ; (RCs+1)V_o=V_i,\qquad G(s)=\frac{V_o}{V_i}=\frac1{RCs+1}. ; h(t)=\frac1{RC}e^{-t/(RC)}1(t).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 45. 一阶系统正弦稳态幅相

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 45 题 [Ch3-05]。定位：Examples 3.6-3.7, PDF 299-305。

原题保留：一阶系统正弦稳态幅相。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 k=1 s^-1、正弦幅值 1 V、omega=10 rad/s；以 0.002 s 采样 12 s，并在指数暂态消失后估计稳态幅值和相位。 来源模型方程（按原变量定义，仅作数学背景）：H(j\omega)=\frac1{k+j\omega} =\frac{k-j\omega}{k^2+\omega^2}. ; |H(j\omega)|=\frac1{\sqrt{k^2+\omega^2}},\qquad \angle H(j\omega)=-\tan^{-1}\frac{\omega}{k}, ; y_{\rm ss}(t)=\frac{A}{\sqrt{k^2+\omega^2}} \cos\!\left(\omega t-\tan^{-1}\frac{\omega}{k}\right). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：一阶系统正弦稳态幅相。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 45 题 [Ch3-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 k=1 s^-1、正弦幅值 1 V、omega=10 rad/s；以 0.002 s 采样 12 s，并在指数暂态消失后估计稳态幅值和相位。 来源模型方程（按原变量定义，仅作数学背景）：H(j\omega)=\frac1{k+j\omega} =\frac{k-j\omega}{k^2+\omega^2}. ; |H(j\omega)|=\frac1{\sqrt{k^2+\omega^2}},\qquad \angle H(j\omega)=-\tan^{-1}\frac{\omega}{k}, ; y_{\rm ss}(t)=\frac{A}{\sqrt{k^2+\omega^2}} \cos\!\left(\omega t-\tan^{-1}\frac{\omega}{k}\right).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 46. 阶跃斜坡冲激与正弦输入的变换

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 46 题 [Ch3-06]。定位：Examples 3.8-3.10, PDF 311-312。

原题保留：阶跃斜坡冲激与正弦输入的变换。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 G(s)=1/(s+1)、阶跃幅值 2、斜坡斜率 0.5、单位冲激面积 1、正弦频率 3 rad/s，以 0.005 s 采样 12 s。 来源模型方程（按原变量定义，仅作数学背景）：\mathcal L\{a1(t)\}=\int_0^\infty ae^{-st}dt=\frac a s,\qquad \mathcal L\{bt1(t)\}=b\!\left(-\frac d{ds}\frac1s\right)=\frac b{s^2}. ; \mathcal L\{\delta(t)\}=1,\qquad \mathcal L\{\sin\omega t\}=\frac{\omega}{s^2+\omega^2}. ; \frac{aG(s)}s,\quad \frac{bG(s)}{s^2},\quad G(s),\quad \frac{\omega G(s)}{s^2+\omega^2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：阶跃斜坡冲激与正弦输入的变换。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 46 题 [Ch3-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 G(s)=1/(s+1)、阶跃幅值 2、斜坡斜率 0.5、单位冲激面积 1、正弦频率 3 rad/s，以 0.005 s 采样 12 s。 来源模型方程（按原变量定义，仅作数学背景）：\mathcal L\{a1(t)\}=\int_0^\infty ae^{-st}dt=\frac a s,\qquad \mathcal L\{bt1(t)\}=b\!\left(-\frac d{ds}\frac1s\right)=\frac b{s^2}. ; \mathcal L\{\delta(t)\}=1,\qquad \mathcal L\{\sin\omega t\}=\frac{\omega}{s^2+\omega^2}. ; \frac{aG(s)}s,\quad \frac{bG(s)}{s^2},\quad G(s),\quad \frac{\omega G(s)}{s^2+\omega^2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 47. 部分分式展开恢复时域响应

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 47 题 [Ch3-07]。定位：Example 3.11, PDF 319-321。

原题保留：部分分式展开恢复时域响应。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 Y(s)=(s+2)(s+4)/[s(s+1)(s+3)]；以 0.005 s 采样 12 s 仿真单位冲激，并比较留数 8/3、-3/2、-1/6。 来源模型方程（按原变量定义，仅作数学背景）：Y(s)=\frac{(s+2)(s+4)}{s(s+1)(s+3)}, ; Y(s)=\frac{A}{s}+\frac{B}{s+1}+\frac{C}{s+3}. ; A=\frac{(2)(4)}{(1)(3)}=\frac83,\quad B=\frac{(1)(3)}{(-1)(2)}=-\frac32,\quad C=\frac{(-1)(1)}{(-3)(-2)}=-\frac16. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：部分分式展开恢复时域响应。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 47 题 [Ch3-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 Y(s)=(s+2)(s+4)/[s(s+1)(s+3)]；以 0.005 s 采样 12 s 仿真单位冲激，并比较留数 8/3、-3/2、-1/6。 来源模型方程（按原变量定义，仅作数学背景）：Y(s)=\frac{(s+2)(s+4)}{s(s+1)(s+3)}, ; Y(s)=\frac{A}{s}+\frac{B}{s+1}+\frac{C}{s+3}. ; A=\frac{(2)(4)}{(1)(3)}=\frac83,\quad B=\frac{(1)(3)}{(-1)(2)}=-\frac32,\quad C=\frac{(-1)(1)}{(-3)(-2)}=-\frac16.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 48. 终值定理的适用与失效

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 48 题 [Ch3-08]。定位：Examples 3.12-3.13, PDF 323-324。

原题保留：终值定理的适用与失效。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：并行计算 Y1=3(s+2)/[s(s^2+2s+10)] 与 Y2=3/[s(s-2)]，以 0.002 s 采样 8 s，并在输出绝对值达到 100 时停止。 来源模型方程（按原变量定义，仅作数学背景）：Y_1(s)=\frac{3(s+2)}{s(s^2+2s+10)},\qquad Y_2(s)=\frac{3}{s(s-2)}. ; \lim_{t\to\infty}y(t)=\lim_{s\to0}sY(s). ; y_1(\infty)=\frac{3(2)}{10}=0.6. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：终值定理的适用与失效。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 48 题 [Ch3-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源比较一个稳定终值例和一个发散例；终值定理要求满足极点条件.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：并行计算 Y1=3(s+2)/[s(s^2+2s+10)] 与 Y2=3/[s(s-2)]，以 0.002 s 采样 8 s，并在输出绝对值达到 100 时停止。 来源模型方程（按原变量定义，仅作数学背景）：Y_1(s)=\frac{3(s+2)}{s(s^2+2s+10)},\qquad Y_2(s)=\frac{3}{s(s-2)}. ; \lim_{t\to\infty}y(t)=\lim_{s\to0}sY(s). ; y_1(\infty)=\frac{3(2)}{10}=0.6.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 49. 稳定系统的直流增益

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 49 题 [Ch3-09]。定位：Example 3.14, PDF 325。

原题保留：稳定系统的直流增益。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 G(s)=3(s+2)/(s^2+2s+10)；施加 0.25、0.5、0.75、1 四级阶跃，以 0.005 s 采样 12 s，并核对 0.6 直流增益。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{3(s+2)}{s^2+2s+10} ; s^2+2s+10=(s+1)^2+3^2, ; Y(s)=G(s)\frac1s =\frac{3(s+2)}{s(s^2+2s+10)}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：稳定系统的直流增益。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 49 题 [Ch3-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 G(s)=3(s+2)/(s^2+2s+10)；施加 0.25、0.5、0.75、1 四级阶跃，以 0.005 s 采样 12 s，并核对 0.6 直流增益。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{3(s+2)}{s^2+2s+10} ; s^2+2s+10=(s+1)^2+3^2, ; Y(s)=G(s)\frac1s =\frac{3(s+2)}{s(s^2+2s+10)}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 50. 带初值常微分方程的自由与受迫响应

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 50 题 [Ch3-10]。定位：Examples 3.15-3.17, PDF 326-329。

原题保留：带初值常微分方程的自由与受迫响应。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 y_ddot+5 y_dot+4 y=u；先运行初值 (y0,ydot0)=(1,0) 与 (0,1)，再运行零初值输入 u=2 exp(-2t)，以 0.005 s 采样 10 s。 来源模型方程（按原变量定义，仅作数学背景）：\ddot y+5\dot y+4y=3 ; (s^2+1)Y=s\alpha+\beta,\qquad y(t)=\alpha\cos t+\beta\sin t. ; (s+1)(s+4)Y=s\alpha+\beta+5\alpha+\frac3s. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：带初值常微分方程的自由与受迫响应。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 50 题 [Ch3-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 y_ddot+5 y_dot+4 y=u；先运行初值 (y0,ydot0)=(1,0) 与 (0,1)，再运行零初值输入 u=2 exp(-2t)，以 0.005 s 采样 10 s。 来源模型方程（按原变量定义，仅作数学背景）：\ddot y+5\dot y+4y=3 ; (s^2+1)Y=s\alpha+\beta,\qquad y(t)=\alpha\cos t+\beta\sin t. ; (s+1)(s+4)Y=s\alpha+\beta+5\alpha+\frac3s.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 51. 巡航模型的位置动态

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 51 题 [Ch3-11]。定位：Example 3.18, PDF 334-335。

原题保留：巡航模型的位置动态。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 m=1000 kg、b=50 N*s/m 和 500 N 力阶跃；以 0.05 s 采样 120 s 的速度与位置，位置模型为 Gx=0.001/[s(s+0.05)]。 来源模型方程（按原变量定义，仅作数学背景）：m\dot v=u-bv\quad\Longrightarrow\quad (ms+b)V(s)=U(s). ; \frac{V}{U}=\frac1{1000s+50} =\frac{0.001}{s+0.05}. ; \frac{X}{U}=\frac1{s(ms+b)} =\frac{0.001}{s(s+0.05)}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：巡航模型的位置动态。本次仅做外部软件模型的适配子任务：使 vehicle_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 51 题 [Ch3-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["vehicle_position", "m"]]` |
| 输入行 [名称] | `inputs` | `[["drive_force"]]` |
| 输入单位 | `input_unit` | `"N"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-500.0` |
| 输入上限 | `input_max` | `500.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 m=1000 kg、b=50 N*s/m 和 500 N 力阶跃；以 0.05 s 采样 120 s 的速度与位置，位置模型为 Gx=0.001/[s(s+0.05)]。 来源模型方程（按原变量定义，仅作数学背景）：m\dot v=u-bv\quad\Longrightarrow\quad (ms+b)V(s)=U(s). ; \frac{V}{U}=\frac1{1000s+50} =\frac{0.001}{s+0.05}. ; \frac{X}{U}=\frac1{s(ms+b)} =\frac{0.001}{s(s+0.05)}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 52. 直流电机位置与速度极点

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 52 题 [Ch3-12]。定位：Example 3.19, PDF 335-337。

原题保留：直流电机位置与速度极点。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 J=0.01 kg*m^2、b=0.001 Nm*s/rad、Kt=Ke=1、Ra=10 ohm、La=1 H；用 +/-1 V 测试，以 0.001 s 记录 5 s 的电流、转速和角度。 来源模型方程（按原变量定义，仅作数学背景）：L_a\dot i+R_ai+K_e\omega=v_a,\qquad J\dot\omega+b\omega=K_ti,\qquad \dot\theta=\omega. ; (L_as+R_a)I+K_e\Omega=V_a,\qquad (Js+b)\Omega=K_tI. ; \frac{\Omega}{V_a} =\frac{K_t}{(Js+b)(L_as+R_a)+K_tK_e}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机位置与速度极点。本次仅做外部软件模型的适配子任务：使 motor_speed 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 52 题 [Ch3-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_speed", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["armature_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 J=0.01 kg*m^2、b=0.001 Nm*s/rad、Kt=Ke=1、Ra=10 ohm、La=1 H；用 +/-1 V 测试，以 0.001 s 记录 5 s 的电流、转速和角度。 来源模型方程（按原变量定义，仅作数学背景）：L_a\dot i+R_ai+K_e\omega=v_a,\qquad J\dot\omega+b\omega=K_ti,\qquad \dot\theta=\omega. ; (L_as+R_a)I+K_e\Omega=V_a,\qquad (Js+b)\Omega=K_tI. ; \frac{\Omega}{V_a} =\frac{K_t}{(Js+b)(L_as+R_a)+K_tK_e}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 53. 刚性卫星有限推力脉冲响应

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 53 题 [Ch3-13]。定位：Example 3.21, PDF 340-341。

原题保留：刚性卫星有限推力脉冲响应。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用力臂 d=1 m、惯量 I=5000 kg*m^2；在 5.0 至 5.1 s 施加 25 N 脉冲，并以 0.01 s 采样至 10 s。  来源模型方程（按原变量定义，仅作数学背景）：F(t)=25[1(t-5)-1(t-5.1)], \quad F(s)=\frac{25}{s}(e^{-5s}-e^{-5.1s}). ; \alpha=0.0002(25)=0.005\ \mathrm{rad/s^2}. ; \theta(t)=\frac{\alpha}{2} [(t-5)^2 1(t-5)-(t-5.1)^2 1(t-5.1)]. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：刚性卫星有限推力脉冲响应。本次仅做外部软件模型的适配子任务：使 attitude_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 53 题 [Ch3-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0.0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0.0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.02 附近，误差不超过 0.04"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0.0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["attitude_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["finite_thruster_force_pulse"]]` |
| 输入单位 | `input_unit` | `"N"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-50.0` |
| 输入上限 | `input_max` | `50.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用力臂 d=1 m、惯量 I=5000 kg*m^2；在 5.0 至 5.1 s 施加 25 N 脉冲，并以 0.01 s 采样至 10 s。  来源模型方程（按原变量定义，仅作数学背景）：F(t)=25[1(t-5)-1(t-5.1)], \quad F(s)=\frac{25}{s}(e^{-5s}-e^{-5.1s}). ; \alpha=0.0002(25)=0.005\ \mathrm{rad/s^2}. ; \theta(t)=\frac{\alpha}{2} [(t-5)^2 1(t-5)-(t-5.1)^2 1(t-5.1)].
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 54. 嵌套控制框图化简

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 54 题 [Ch3-14]。定位：Examples 3.22-3.23, PDF 352-355。

原题保留：嵌套控制框图化简。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用并联控制器支路 2 与 4/s、对象 1/s 和单位负反馈；以 0.005 s 采样 10 s，施加 +/-0.5 与 +/-1 参考阶跃。 来源模型方程（按原变量定义，仅作数学背景）：G_c=2+\frac4s=\frac{2s+4}{s}, ; T=\frac{L}{1+L} =\frac{2s+4}{s^2+2s+4}. ; T=\frac{G_1G_2}{1-G_1G_3+G_1G_2G_4} \left(G_5+\frac{G_6}{G_2}\right). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：嵌套控制框图化简。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 54 题 [Ch3-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用并联控制器支路 2 与 4/s、对象 1/s 和单位负反馈；以 0.005 s 采样 10 s，施加 +/-0.5 与 +/-1 参考阶跃。 来源模型方程（按原变量定义，仅作数学背景）：G_c=2+\frac4s=\frac{2s+4}{s}, ; T=\frac{L}{1+L} =\frac{2s+4}{s^2+2s+4}. ; T=\frac{G_1G_2}{1-G_1G_3+G_1G_2G_4} \left(G_5+\frac{G_6}{G_2}\right).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 55. Mason 公式求闭环传递函数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 55 题 [Ch3-15]。定位：Section 3.2.3, PDF 357-358 (the PDF正文仅指向 online appendix；数据条目明确标注标准公式为自包含补充)。

原题保留：Mason 公式求闭环传递函数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取前向路径 P=6、带符号接触回路 L=0.2，Mason 增益为 6/(1-0.2)=7.5；再把回路改为 -0.2 与 0 重复。 来源模型方程（按原变量定义，仅作数学背景）：\Delta=1-\sum_iL_i+\sum_{i<j}L_iL_j -\sum_{i<j<q}L_iL_jL_q+\cdots, ; T=\frac{\sum_kP_k\Delta_k}{\Delta}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Mason 公式求闭环传递函数。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 55 题 [Ch3-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取前向路径 P=6、带符号接触回路 L=0.2，Mason 增益为 6/(1-0.2)=7.5；再把回路改为 -0.2 与 0 重复。 来源模型方程（按原变量定义，仅作数学背景）：\Delta=1-\sum_iL_i+\sum_{i<j}L_iL_j -\sum_{i<j<q}L_iL_jL_q+\cdots, ; T=\frac{\sum_kP_k\Delta_k}{\Delta}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 56. 由极点判断暂态形态与衰减率

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 56 题 [Ch3-16]。定位：Example 3.25, PDF 363-368。

原题保留：由极点判断暂态形态与衰减率。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 H(s)=(2s+1)/(s^2+3s+2)；施加正负单位冲激，以 0.005 s 采样 10 s，并拟合 -1、-2 模态及留数 -1、3。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{2s+1}{s^2+3s+2} =\frac{2s+1}{(s+1)(s+2)}. ; H(s)=\frac{A}{s+1}+\frac{B}{s+2}, \quad A=\left.\frac{2s+1}{s+2}\right|_{-1}=-1,\quad B=\left.\frac{2s+1}{s+1}\right|_{-2}=3. ; h(t)=(-e^{-t}+3e^{-2t})1(t). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由极点判断暂态形态与衰减率。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 56 题 [Ch3-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 来源模型先验：来源冲激在稳定极点下仍穿越符号，方向分析必须保留分子零点.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 H(s)=(2s+1)/(s^2+3s+2)；施加正负单位冲激，以 0.005 s 采样 10 s，并拟合 -1、-2 模态及留数 -1、3。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{2s+1}{s^2+3s+2} =\frac{2s+1}{(s+1)(s+2)}. ; H(s)=\frac{A}{s+1}+\frac{B}{s+2}, \quad A=\left.\frac{2s+1}{s+2}\right|_{-1}=-1,\quad B=\left.\frac{2s+1}{s+1}\right|_{-2}=3. ; h(t)=(-e^{-t}+3e^{-2t})1(t).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 57. 二阶性能指标与极点区域

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 57 题 [Ch3-17]。定位：Example 3.26, Section 3.4, and Example 3.27, PDF 379-398。

原题保留：二阶性能指标与极点区域。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 omega_n=3 rad/s、zeta=0.6 及单位直流增益模型 9/(s^2+3.6s+9)；以 0.002 s 采样 8 s，测量上升、峰值和 1% 调节时间。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{\omega_n^2}{s^2+2\zeta\omega_ns+\omega_n^2}, \quad 0<\zeta<1, ; s_{1,2}=-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2} =-\sigma\pm j\omega_d. ; y(t)=1-\frac{e^{-\sigma t}}{\sqrt{1-\zeta^2}} \cos(\omega_dt-\sin^{-1}\zeta). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：二阶性能指标与极点区域。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 57 题 [Ch3-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 omega_n=3 rad/s、zeta=0.6 及单位直流增益模型 9/(s^2+3.6s+9)；以 0.002 s 采样 8 s，测量上升、峰值和 1% 调节时间。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{\omega_n^2}{s^2+2\zeta\omega_ns+\omega_n^2}, \quad 0<\zeta<1, ; s_{1,2}=-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2} =-\sigma\pm j\omega_d. ; y(t)=1-\frac{e^{-\sigma t}}{\sqrt{1-\zeta^2}} \cos(\omega_dt-\sin^{-1}\zeta).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 58. 波音飞机右半平面零点的逆响应

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 58 题 [Ch3-18]。定位：Example 3.30, PDF 417-421。

原题保留：波音飞机右半平面零点的逆响应。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原高度/升降舵模型 G(s)=30(s-6)/[s(s^2+4s+13)]。原题理想负冲激在时域实现时的面积为 -1 度秒，预测初始斜率 -30、最终偏置 180/13=13.846 原高度单位；有界实现必须遵守新协议。-1 deg 阶跃不是该冲激，且没有有限稳态高度。来源未确定 SI 高度标定，因此保留 source_altitude_unit，不能虚构为米。适配目标为小高度偏差保持。

-2 与 +/-3 分别描述复极点对的实部和虚部，并非已给出的整对象 natural_frequency。完整对象包含积分器与二阶因子。本回复未直接给出可提交的整对象 natural_frequency 数值和单位；不提交该参数，也不将极点分量或仅属于二阶因子的频率改名为它。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：波音飞机右半平面零点的逆响应。本次仅做外部软件模型的适配子任务：使 altitude_deviation 保持在 1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 58 题 [Ch3-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 原高度/升降舵模型 G(s)=30(s-6)/[s(s^2+4s+13)]。原题理想负冲激在时域实现时的面积为 -1 度秒，预测初始斜率 -30、最终偏置 180/13=13.846 原高度单位；有界实现必须遵守新协议。-1 deg 阶跃不是该冲激，且没有有限稳态高度。来源未确定 SI 高度标定，因此保留 source_altitude_unit，不能虚构为米。适配目标为小高度偏差保持。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["altitude_deviation", "source_altitude_unit"]]` |
| 输入行 [名称] | `inputs` | `[["elevator_deflection"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `1` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `24.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-20` |
| 输出上限 | `output_max` | `20` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.1` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `10` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
第 1–7 项仅对给定适配名义数学模型及主要输入输出已知，第 8 项未知。这些是模型先验，不是硬件观测或协议绑定记录；真实传感器、标定和执行器仍未验证.
1. open_loop_stability: unstable（BIBO 意义下不稳定）：名义高度通道包含积分器及稳定复极点对；本回复未直接给出整对象 natural_frequency 数值和单位，不提交该参数.
2. nonminimum_phase: nonminimum_phase（非最小相位）：名义通道有右半平面零点 +6，冲激存在逆响应.
3. significant_delay: not_significant（无显著迟延）：名义传递函数不含纯迟延.
4. relative_degree: low（低）：名义升降舵到高度通道相对阶次为 2.
5. sensing_actuation_adequacy: adequate（对名义最小 SISO 模型充分）：理想高度时序可观测其状态，升降舵输入使其可控.
6. nonlinearity_strength: weak（弱）：这里只诊断名义飞机线性近似.
7. coupling_underactuation: siso：适配对象是给定的单输入单输出（SISO）升降舵/高度模型. 省略飞行状态不在本任务内，不构成欠驱动证据.
8. uncertainty_variation: 未知，没有气动参数复测.
模型与范围：原高度/升降舵模型 G(s)=30(s-6)/[s(s^2+4s+13)]。原题理想负冲激在时域实现时的面积为 -1 度秒，预测初始斜率 -30、最终偏置 180/13=13.846 原高度单位；有界实现必须遵守新协议。-1 deg 阶跃不是该冲激，且没有有限稳态高度。来源未确定 SI 高度标定，因此保留 source_altitude_unit，不能虚构为米。适配目标为小高度偏差保持。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 59. 电流驱动电容的 BIBO 稳定性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 59 题 [Ch3-19]。定位：Example 3.31, PDF 431-432。

原题保留：电流驱动电容的 BIBO 稳定性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 C=0.01 F；施加 +/-0.1 A 恒流并设置 50 V 停止边界，以 0.01 s 采样，核对电压斜坡与 BIBO 反例。 来源模型方程（按原变量定义，仅作数学背景）：I(s)=CsV(s),\qquad G(s)=\frac{V}{I}=\frac1{Cs}. ; h(t)=\mathcal L^{-1}\!\left\{\frac1{Cs}\right\} =\frac1C1(t). ; \int_{-\infty}^{\infty}|h(t)|dt =\frac1C\int_0^\infty dt=\infty, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：电流驱动电容的 BIBO 稳定性。本次仅做外部软件模型的适配子任务：使 capacitor_voltage 保持在 1.0 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 59 题 [Ch3-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["capacitor_voltage", "V"]]` |
| 输入行 [名称] | `inputs` | `[["source_current"]]` |
| 输入单位 | `input_unit` | `"A"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `1.0` |
| 输入下限 | `input_min` | `-0.1` |
| 输入上限 | `input_max` | `0.1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `60.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-50` |
| 输出上限 | `output_max` | `50` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `2.0` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想输入输出通道为单积分器，相对阶次 1.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用 C=0.01 F；施加 +/-0.1 A 恒流并设置 50 V 停止边界，以 0.01 s 采样，核对电压斜坡与 BIBO 反例。 来源模型方程（按原变量定义，仅作数学背景）：I(s)=CsV(s),\qquad G(s)=\frac{V}{I}=\frac1{Cs}. ; h(t)=\mathcal L^{-1}\!\left\{\frac1{Cs}\right\} =\frac1C1(t). ; \int_{-\infty}^{\infty}|h(t)|dt =\frac1C\int_0^\infty dt=\infty,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 60. Routh 判据求比例与 PI 稳定增益区间

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 60 题 [Ch3-20]。定位：Examples 3.33-3.34, PDF 441-449。

原题保留：Routh 判据求比例与 PI 稳定增益区间。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：比例案例取 K=13，并与 K=7.5、25 比较；PI 案例取 (K,Ki)=(2,6)，再与边界 Ki=6+3K 比较，以 0.005 s 采样 20 s。 来源模型方程（按原变量定义，仅作数学背景）：p_1(s)=s^3+5s^2+(K-6)s+K, ; p_2(s)=s^3+3s^2+(2+K)s+K_I. ; \begin{array}{c|cc} s^3&1&K-6\\ s^2&5&K\\ s^1&(4K-30)/5&0\\ s^0&K& \end{array}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Routh 判据求比例与 PI 稳定增益区间。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 60 题 [Ch3-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：P 比较仅在 K>7.5 稳定；PI 比较需 KI>0 且 K>KI/3-2；这是独立来源控制器研究.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：比例案例取 K=13，并与 K=7.5、25 比较；PI 案例取 (K,Ki)=(2,6)，再与边界 Ki=6+3K 比较，以 0.005 s 采样 20 s。 来源模型方程（按原变量定义，仅作数学背景）：p_1(s)=s^3+5s^2+(K-6)s+K, ; p_2(s)=s^3+3s^2+(2+K)s+K_I. ; \begin{array}{c|cc} s^3&1&K-6\\ s^2&5&K\\ s^1&(4K-30)/5&0\\ s^0&K& \end{array}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 61. 灵敏度与互补灵敏度的闭环通道

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 61 题 [Ch4-01]。定位：Section 4.1, PDF 515-517。

原题保留：灵敏度与互补灵敏度的闭环通道。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s+1)、D=9；参考、对象扰动与传感噪声分别施加 ±0.5、±1，以 0.01 s 采样 8 s。 来源模型方程（按原变量定义，仅作数学背景）：U=D_{cl}(R-Y-V),\qquad Y=G(U+W). ; S=\frac1{1+L},\qquad T=\frac{L}{1+L}, ; Y=TR+GSW-TV. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：灵敏度与互补灵敏度的闭环通道。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 61 题 [Ch4-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s+1)、D=9；参考、对象扰动与传感噪声分别施加 ±0.5、±1，以 0.01 s 采样 8 s。 来源模型方程（按原变量定义，仅作数学背景）：U=D_{cl}(R-Y-V),\qquad Y=G(U+W). ; S=\frac1{1+L},\qquad T=\frac{L}{1+L}, ; Y=TR+GSW-TV.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 62. 用特征方程稳定倒立摆

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 62 题 [Ch4-02]。定位：Section 4.1.1 exercise, PDF 517-520。

原题保留：用特征方程稳定倒立摆。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对 G=1/(s^2-1) 取 zeta=0.7、wn=2 rad/s、gamma=1、delta=3.8、K=7.8；±0.25 阶跃以 0.005 s 采样 8 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s^2-1}=\frac1{(s-1)(s+1)}, ; D_{cl}(s)=K\frac{s+\gamma}{s+\delta}. ; (s-1)(s+1)(s+\delta)+K(s+\gamma)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用特征方程稳定倒立摆。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 62 题 [Ch4-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源倒立摆对象不稳定；补偿后的稳定极点不是对象极点.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对 G=1/(s^2-1) 取 zeta=0.7、wn=2 rad/s、gamma=1、delta=3.8、K=7.8；±0.25 阶跃以 0.005 s 采样 8 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s^2-1}=\frac1{(s-1)(s+1)}, ; D_{cl}(s)=K\frac{s+\gamma}{s+\delta}. ; (s-1)(s+1)(s+\delta)+K(s+\gamma)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 63. 反馈降低对象增益灵敏度

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 63 题 [Ch4-03]。定位：Section 4.1.4, PDF 522-526。

原题保留：反馈降低对象增益灵敏度。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：检验频率取 P=1、C=99，并把 P 乘 0.9、1.1 重复；时域采用 1/(s+1)。 来源模型方程（按原变量定义，仅作数学背景）：T(P)=\frac{P C}{1+P C}, ; \frac{\partial T}{\partial P} =\frac{C(1+PC)-PC^2}{(1+PC)^2} =\frac{C}{(1+PC)^2}. ; S_T^P=\frac1{1+PC}=S. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：反馈降低对象增益灵敏度。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 63 题 [Ch4-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：检验频率取 P=1、C=99，并把 P 乘 0.9、1.1 重复；时域采用 1/(s+1)。 来源模型方程（按原变量定义，仅作数学背景）：T(P)=\frac{P C}{1+P C}, ; \frac{\partial T}{\partial P} =\frac{C(1+PC)-PC^2}{(1+PC)^2} =\frac{C}{(1+PC)^2}. ; S_T^P=\frac1{1+PC}=S.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 64. 扰动抑制与传感噪声衰减权衡

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 64 题 [Ch4-04]。定位：Section 4.1.3 and Eq. 4.26, PDF 521-527。

原题保留：扰动抑制与传感噪声衰减权衡。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=100/(s+1)；测试低频对象扰动及 1、10、100、1000 rad/s 传感噪声。 来源模型方程（按原变量定义，仅作数学背景）：E_W=-GSW=-\frac{G}{1+GD_{cl}}W,\qquad E_V=TV=\frac{GD_{cl}}{1+GD_{cl}}V. ; GS\approx\frac{G}{GD_{cl}}=\frac1{D_{cl}}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：扰动抑制与传感噪声衰减权衡。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 64 题 [Ch4-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=100/(s+1)；测试低频对象扰动及 1、10、100、1000 rad/s 传感噪声。 来源模型方程（按原变量定义，仅作数学背景）：E_W=-GSW=-\frac{G}{1+GD_{cl}}W,\qquad E_V=TV=\frac{GD_{cl}}{1+GD_{cl}}V. ; GS\approx\frac{G}{GD_{cl}}=\frac1{D_{cl}},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 65. Type 零比例速度控制的稳态误差

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 65 题 [Ch4-05]。定位：Example 4.1, PDF 534。

原题保留：Type 零比例速度控制的稳态误差。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=2、tau=5 s、kP=4；±0.5、±1 速度阶跃以 0.02 s 采样 20 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{A}{\tau s+1},\qquad A,\tau>0, ; L(s)=GD_{cl}=\frac{k_PA}{\tau s+1} ; K_p=\lim_{s\to0}L(s)=k_PA. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Type 零比例速度控制的稳态误差。本次仅做外部软件模型的适配子任务：使 speed 保持在 0.0234666 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 65 题 [Ch4-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["speed", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["proportional_control_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0234666` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.407996` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.17333` |
| 输出上限 | `output_max` | `1.17333` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0469332` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=2、tau=5 s、kP=4；±0.5、±1 速度阶跃以 0.02 s 采样 20 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{A}{\tau s+1},\qquad A,\tau>0, ; L(s)=GD_{cl}=\frac{k_PA}{\tau s+1} ; K_p=\lim_{s\to0}L(s)=k_PA.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 66. 用积分把速度环提升为 Type 一

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 66 题 [Ch4-06]。定位：Example 4.2, PDF 534-535。

原题保留：用积分把速度环提升为 Type 一。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=2、tau=5 s、kP=2、kI=0.5；阶跃和斜坡分别以 0.02 s 运行 30 s。 来源模型方程（按原变量定义，仅作数学背景）：D_{cl}(s)=k_P+\frac{k_I}{s} =\frac{k_Ps+k_I}{s}, ; L(s)=\frac{A(k_Ps+k_I)}{s(\tau s+1)} ; K_v=\lim_{s\to0}sL(s)=Ak_I. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用积分把速度环提升为 Type 一。本次仅做外部软件模型的适配子任务：使 speed 保持在 0.026868 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 66 题 [Ch4-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["speed", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["PI_control_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.026868` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.61208` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.3434` |
| 输出上限 | `output_max` | `1.3434` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.053736` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=2、tau=5 s、kP=2、kI=0.5；阶跃和斜坡分别以 0.02 s 运行 30 s。 来源模型方程（按原变量定义，仅作数学背景）：D_{cl}(s)=k_P+\frac{k_I}{s} =\frac{k_Ps+k_I}{s}, ; L(s)=\frac{A(k_Ps+k_I)}{s(\tau s+1)} ; K_v=\lim_{s\to0}sL(s)=Ak_I.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 67. 测速反馈下的系统型别与速度常数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 67 题 [Ch4-07]。定位：Example 4.3, PDF 537-538。

原题保留：测速反馈下的系统型别与速度常数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 tau=1 s、kP=4、kt=0.25 s；阶跃和斜坡以 0.01 s 运行 15 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(\tau s+1)},\qquad D_c=k_P,\qquad H(s)=1+k_ts. ; T(s)=\frac{Y}{R} =\frac{k_P}{s(\tau s+1)+k_P(1+k_ts)}. ; 1-T= \frac{s(\tau s+1)+k_Pk_ts} {s(\tau s+1)+k_P(1+k_ts)} =s\,\frac{\tau s+1+k_Pk_t}{s(\tau s+1)+k_P(1+k_ts)}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：测速反馈下的系统型别与速度常数。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 67 题 [Ch4-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["armature_voltage_under_tachometer_feedback"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 tau=1 s、kP=4、kt=0.25 s；阶跃和斜坡以 0.01 s 运行 15 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(\tau s+1)},\qquad D_c=k_P,\qquad H(s)=1+k_ts. ; T(s)=\frac{Y}{R} =\frac{k_P}{s(\tau s+1)+k_P(1+k_ts)}. ; 1-T= \frac{s(\tau s+1)+k_Pk_ts} {s(\tau s+1)+k_P(1+k_ts)} =s\,\frac{\tau s+1+k_Pk_t}{s(\tau s+1)+k_P(1+k_ts)}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 68. 直流电机 P 与 PI 的扰动力矩型别

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 68 题 [Ch4-08]。定位：Example 4.4, PDF 540-542。

原题保留：直流电机 P 与 PI 的扰动力矩型别。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=B=tau=1；单位转矩扰动下比较 P 的 kP=4 与 PI 的 kP=4、kI=2。 来源模型方程（按原变量定义，仅作数学背景）：T_w(s)=\frac{E}{W} =-\frac{B}{s(\tau s+1)+Ak_P}. ; e_{ss}=T_w(0)=-\frac{B}{Ak_P}, ; T_w(s)=-\frac{Bs}{s^2(\tau s+1)+A(k_Ps+k_I)} =sT_{0,w}(s). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机 P 与 PI 的扰动力矩型别。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 68 题 [Ch4-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["armature_voltage_with_prescribed_load_torque_disturbance"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=B=tau=1；单位转矩扰动下比较 P 的 kP=4 与 PI 的 kP=4、kI=2。 来源模型方程（按原变量定义，仅作数学背景）：T_w(s)=\frac{E}{W} =-\frac{B}{s(\tau s+1)+Ak_P}. ; e_{ss}=T_w(0)=-\frac{B}{Ak_P}, ; T_w(s)=-\frac{Bs}{s^2(\tau s+1)+A(k_Ps+k_I)} =sT_{0,w}(s).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 69. 比例控制的速度偏差阻尼权衡

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 69 题 [Ch4-09]。定位：Section 4.3.1, PDF 543-547。

原题保留：比例控制的速度偏差阻尼权衡。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=1、a1=1.4、a2=1；单位阶跃比较 kP=1.5 与 6，以 0.01 s 运行 15 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{A}{s^2+a_1s+a_2} ; T=\frac{k_PA}{s^2+a_1s+a_2+k_PA}, ; \omega_n=\sqrt{a_2+k_PA},\qquad \zeta=\frac{a_1}{2\sqrt{a_2+k_PA}}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：比例控制的速度偏差阻尼权衡。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 69 题 [Ch4-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=1、a1=1.4、a2=1；单位阶跃比较 kP=1.5 与 6，以 0.01 s 运行 15 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{A}{s^2+a_1s+a_2} ; T=\frac{k_PA}{s^2+a_1s+a_2+k_PA}, ; \omega_n=\sqrt{a_2+k_PA},\qquad \zeta=\frac{a_1}{2\sqrt{a_2+k_PA}}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 70. 积分控制的鲁棒零误差

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 70 题 [Ch4-10]。定位：Section 4.3.2, PDF 548-553。

原题保留：积分控制的鲁棒零误差。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s^2+1.4s+1)、kI=0.5；参考和对象扰动阶跃分开运行并启用 anti-windup。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=\frac{k_I}{s},\qquad u(t)=k_I\int_0^t e(\tau)d\tau, ; \frac{E}{R}=\frac{s}{s+k_IG},\quad \frac{U}{R}=\frac{k_I}{s+k_IG},\quad \frac{Y}{R}=\frac{k_IG}{s+k_IG}. ; e(\infty)=0,\qquad y(\infty)=1,\qquad u(\infty)=\frac1{G(0)}=1. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：积分控制的鲁棒零误差。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 70 题 [Ch4-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s^2+1.4s+1)、kI=0.5；参考和对象扰动阶跃分开运行并启用 anti-windup。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=\frac{k_I}{s},\qquad u(t)=k_I\int_0^t e(\tau)d\tau, ; \frac{E}{R}=\frac{s}{s+k_IG},\quad \frac{U}{R}=\frac{k_I}{s+k_IG},\quad \frac{Y}{R}=\frac{k_IG}{s+k_IG}. ; e(\infty)=0,\qquad y(\infty)=1,\qquad u(\infty)=\frac1{G(0)}=1.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 71. 微分与速率反馈增加阻尼

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 71 题 [Ch4-11]。定位：Section 4.3.3, PDF 553-555。

原题保留：微分与速率反馈增加阻尼。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s^2+1.4s+1)、kP=6；比较 kD=0 与输出速率 kD=2，以 0.005 s 运行 12 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{A}{s^2+a_1s+a_2}, ; 1+G(k_P+k_Ds)=0 ; s^2+(a_1+Ak_D)s+(a_2+Ak_P)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：微分与速率反馈增加阻尼。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 71 题 [Ch4-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s^2+1.4s+1)、kP=6；比较 kD=0 与输出速率 kD=2，以 0.005 s 运行 12 s。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{A}{s^2+a_1s+a_2}, ; 1+G(k_P+k_Ds)=0 ; s^2+(a_1+Ak_D)s+(a_2+Ak_P)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 72. 双热容过程 PI 设计

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 72 题 [Ch4-12]。定位：Example 4.5, PDF 557-565。

原题保留：双热容过程 PI 设计。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Ko=1000、tau1=1 s、tau2=10 s；对 30 degC/s、上限 300 degC 的参考比较 P(0.03) 与 PI(0.03,0.003)。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{K_o}{(\tau_1s+1)(\tau_2s+1)}, \quad K_o=1000,\ \tau_1=1,\ \tau_2=10. ; T(0)=\frac{k_PK_o}{1+k_PK_o}=\frac{30}{31}, ; D_c=0.03+\frac{0.003}{s} =0.03\frac{s+0.1}{s}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：双热容过程 PI 设计。本次仅做外部软件模型的适配子任务：使 controlled_temperature 保持在 0.036638 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 72 题 [Ch4-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["controlled_temperature", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["heater_command"]]` |
| 输入单位 | `input_unit` | `"degC"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.036638` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.19828` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.8319` |
| 输出上限 | `output_max` | `1.8319` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.073276` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Ko=1000、tau1=1 s、tau2=10 s；对 30 degC/s、上限 300 degC 的参考比较 P(0.03) 与 PI(0.03,0.003)。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{K_o}{(\tau_1s+1)(\tau_2s+1)}, \quad K_o=1000,\ \tau_1=1,\ \tau_2=10. ; T(0)=\frac{k_PK_o}{1+k_PK_o}=\frac{30}{31}, ; D_c=0.03+\frac{0.003}{s} =0.03\frac{s+0.1}{s}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 73. 直流电机 P、PI 与 PID 比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 73 题 [Ch4-13]。定位：Example 4.6, PDF 566-568。

原题保留：直流电机 P、PI 与 PID 比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原电压到速度对象为 G(s)=0.067/(0.00113s^2+0.0141s+0.032489)，J=0.0113、b=0.028、L=0.1、R=1、Kt=Ke=0.067。负载力矩通道为 -(0.1s+1)/(0.00113s^2+0.0141s+0.032489)。P/PI/PID 参数 3、15、0.3 属于比较控制器，不是对象。新假设：外部模拟器在 10 s 施加 +0.01 Nm 反向负载，11 s 撤除，之后恢复并保持 5 rad/s；这不是已有数据。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机 P、PI 与 PID 比较。本次仅做外部软件模型的适配子任务：使 motor_speed 保持在 5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 73 题 [Ch4-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 原电压到速度对象为 G(s)=0.067/(0.00113s^2+0.0141s+0.032489)，J=0.0113、b=0.028、L=0.1、R=1、Kt=Ke=0.067。负载力矩通道为 -(0.1s+1)/(0.00113s^2+0.0141s+0.032489)。P/PI/PID 参数 3、15、0.3 属于比较控制器，不是对象。新假设：外部模拟器在 10 s 施加 +0.01 Nm 反向负载，11 s 撤除，之后恢复并保持 5 rad/s；这不是已有数据。 本次任务类型为扰动后恢复并保持。"` |
| 任务类型 | `task_type` | `"disturbance_recovery_to_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `"仿真 t=10 s 施加 +0.01 Nm 反向负载力矩，t=11 s 撤除"` |
| 恢复起点 | `recovery_start_condition` | `"t=11 s 负载撤除时开始恢复；施加扰动前已经保持 5 rad/s"` |
| 恢复后保持区域 | `disturbance_hold_region` | `"恢复至 5 rad/s，绝对误差 <=0.25 rad/s 并至少保持 4 s"` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_speed", "rad/s"]]` |
| 输入行 [名称] | `inputs` | `[["armature_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `5` |
| 输入下限 | `input_min` | `-6` |
| 输入上限 | `input_max` | `6` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `18.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-15` |
| 输出上限 | `output_max` | `15` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.25` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `4` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `4` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 对象两个极点稳定，二阶分母系数为正.
2. nonminimum_phase: 电压对象无有限零点.
3. significant_delay: 名义方程无纯迟延.
4. relative_degree: 电压/速度相对阶次 2.
5. sensing_actuation_adequacy: 电压是唯一控制输入；负载是预设扰动；速度是主要输出.
6. nonlinearity_strength: 局部线性机电模型.
7. coupling_underactuation: 单控制通道，负载力矩不是另一个被控执行器.
8. uncertainty_variation: 未知，没有独立负载和摩擦复测.
模型与范围：原电压到速度对象为 G(s)=0.067/(0.00113s^2+0.0141s+0.032489)，J=0.0113、b=0.028、L=0.1、R=1、Kt=Ke=0.067。负载力矩通道为 -(0.1s+1)/(0.00113s^2+0.0141s+0.032489)。P/PI/PID 参数 3、15、0.3 属于比较控制器，不是对象。新假设：外部模拟器在 10 s 施加 +0.01 Nm 反向负载，11 s 撤除，之后恢复并保持 5 rad/s；这不是已有数据。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 74. 非单位传感下的直流电机位置 P/PI 型别

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 74 题 [Ch4-14]。定位：Example 4.7, PDF 569-571。

原题保留：非单位传感下的直流电机位置 P/PI 型别。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=B=tau=1、h=0.8；参考与转矩扰动下比较 P(4) 与 PI(4,2)。 来源模型方程（按原变量定义，仅作数学背景）：T_w(s)=\frac{E}{W} =-\frac{B}{s(\tau s+1)+Ak_Ph}. ; e_{ss}=T_w(0)=-\frac{B}{Ak_Ph},\qquad K_{0,w}=-\frac{Ak_Ph}{B}. ; T_w=-\frac{Bs} {s^2(\tau s+1)+A(k_Ps+k_I)h}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：非单位传感下的直流电机位置 P/PI 型别。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 74 题 [Ch4-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["motor_voltage_with_prescribed_disturbance_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=B=tau=1、h=0.8；参考与转矩扰动下比较 P(4) 与 PI(4,2)。 来源模型方程（按原变量定义，仅作数学背景）：T_w(s)=\frac{E}{W} =-\frac{B}{s(\tau s+1)+Ak_Ph}. ; e_{ss}=T_w(0)=-\frac{B}{Ak_Ph},\qquad K_{0,w}=-\frac{Ak_Ph}{B}. ; T_w=-\frac{Bs} {s^2(\tau s+1)+A(k_Ps+k_I)h}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 75. 卫星 PD 与 PID 的参考/扰动型别

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 75 题 [Ch4-15]。定位：Example 4.8, PDF 571-574。

原题保留：卫星 PD 与 PID 的参考/扰动型别。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 J=1、kP=4、kD=3；PID 再加 kI=1。参考与转矩输入逐一测试。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{Js^2}, ; L=\frac{k_Ds+k_P}{Js^2} ; T_w(s)=\frac1{Js^2+k_Ds+k_P}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：卫星 PD 与 PID 的参考/扰动型别。本次仅做外部软件模型的适配子任务：使 attitude_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 75 题 [Ch4-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["attitude_angle", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque_command_with_prescribed_disturbance_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 J=1、kP=4、kD=3；PID 再加 kI=1。参考与转矩输入逐一测试。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{Js^2}, ; L=\frac{k_Ds+k_P}{Js^2} ; T_w(s)=\frac1{Js^2+k_Ds+k_P}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 76. 由过程反应曲线整定 PID

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 76 题 [Ch4-16]。定位：Section 4.3.6/Table 4.2, PDF 575-578。

原题保留：由过程反应曲线整定 PID。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=2 exp(-3s)/(20s+1)、R=0.1 s^-1、L=3 s；以 0.02 s 运行 100 s 测试反应曲线 P/PI/PID。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{Ae^{-Ls}}{\tau s+1}. ; D_c=k_P\left(1+\frac1{T_Is}+T_Ds\right). ; \begin{array}{c|ccc} P&k_P=1/(RL)&&\\ PI&k_P=0.9/(RL)&T_I=L/0.3&\\ PID&k_P=1.2/(RL)&T_I=2L&T_D=0.5L \end{array}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由过程反应曲线整定 PID。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 76 题 [Ch4-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=2 exp(-3s)/(20s+1)、R=0.1 s^-1、L=3 s；以 0.02 s 运行 100 s 测试反应曲线 P/PI/PID。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{Ae^{-Ls}}{\tau s+1}. ; D_c=k_P\left(1+\frac1{T_Is}+T_Ds\right). ; \begin{array}{c|ccc} P&k_P=1/(RL)&&\\ PI&k_P=0.9/(RL)&T_I=L/0.3&\\ PID&k_P=1.2/(RL)&T_I=2L&T_D=0.5L \end{array}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 77. 由极限增益和周期整定 PID

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 77 题 [Ch4-17]。定位：Section 4.3.6/Table 4.3, PDF 578-581 (preserve this supplied PDF's printed PID factor 1.6 Ku)。

原题保留：由极限增益和周期整定 PID。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)(s+2)]，其 Ku=6、Pu=4.44288 s；测临界振荡后应用 P/PI/PID 表值。 来源模型方程（按原变量定义，仅作数学背景）：D_c=k_P\left(1+\frac1{T_Is}+T_Ds\right). ; \begin{array}{c|ccc} P&k_P=0.5K_u&&\\ PI&k_P=0.45K_u&T_I=P_u/1.2&\\ PID&k_P=1.6K_u&T_I=0.5P_u&T_D=0.125P_u \end{array}. ; k_I=k_P/T_I,\qquad k_D=k_PT_D 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由极限增益和周期整定 PID。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 77 题 [Ch4-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：来源 G=1/[s(s+1)(s+2)] 相对阶次 3，不能由极限周期推成一阶过程.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)(s+2)]，其 Ku=6、Pu=4.44288 s；测临界振荡后应用 P/PI/PID 表值。 来源模型方程（按原变量定义，仅作数学背景）：D_c=k_P\left(1+\frac1{T_Is}+T_Ds\right). ; \begin{array}{c|ccc} P&k_P=0.5K_u&&\\ PI&k_P=0.45K_u&T_I=P_u/1.2&\\ PID&k_P=1.6K_u&T_I=0.5P_u&T_D=0.125P_u \end{array}. ; k_I=k_P/T_I,\qquad k_D=k_PT_D
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 78. 换热器反应曲线 Ziegler–Nichols 整定

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 78 题 [Ch4-18]。定位：Example 4.9, PDF 584-586。

原题保留：换热器反应曲线 Ziegler–Nichols 整定。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取反应曲线 R=1/90 s^-1、L=13 s 与模型 exp(-13s)/(90s+1)；比较 P 6.92、PI 6.22、TI=43.3 s，再减半增益。 来源模型方程（按原变量定义，仅作数学背景）：R\approx\frac1{90},\qquad L\approx13\ \mathrm s. ; k_P=\frac1{RL} =\frac1{(1/90)(13)} =\frac{90}{13}=6.923. ; k_P=\frac{0.9}{RL} =0.9\frac{90}{13}=6.231\approx6.22, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：换热器反应曲线 Ziegler–Nichols 整定。本次仅做外部软件模型的适配子任务：使 heat_exchanger_temperature 保持在 0.026298 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 78 题 [Ch4-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["heat_exchanger_temperature", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["steam_valve_P"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.026298` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.57788` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.3149` |
| 输出上限 | `output_max` | `1.3149` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.052596` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取反应曲线 R=1/90 s^-1、L=13 s 与模型 exp(-13s)/(90s+1)；比较 P 6.92、PI 6.22、TI=43.3 s，再减半增益。 来源模型方程（按原变量定义，仅作数学背景）：R\approx\frac1{90},\qquad L\approx13\ \mathrm s. ; k_P=\frac1{RL} =\frac1{(1/90)(13)} =\frac{90}{13}=6.923. ; k_P=\frac{0.9}{RL} =0.9\frac{90}{13}=6.231\approx6.22,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 79. 换热器极限灵敏度整定

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 79 题 [Ch4-19]。定位：Example 4.10, PDF 587-589。

原题保留：换热器极限灵敏度整定。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取测得 Ku=15.3、Pu=42 s；比较 P kP=7.65 与 PI kP=6.885、TI=35 s，再用半增益重复。 来源模型方程（按原变量定义，仅作数学背景）：K_u=15.3,\qquad P_u=42\ \mathrm s. ; k_P=0.5K_u=0.5(15.3)=7.65. ; k_P=0.45K_u=0.45(15.3)=6.885, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：换热器极限灵敏度整定。本次仅做外部软件模型的适配子任务：使 heat_exchanger_temperature 保持在 0.026298 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 79 题 [Ch4-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["heat_exchanger_temperature", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["steam_valve_P"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.026298` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.57788` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.3149` |
| 输出上限 | `output_max` | `1.3149` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.052596` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取测得 Ku=15.3、Pu=42 s；比较 P kP=7.65 与 PI kP=6.885、TI=35 s，再用半增益重复。 来源模型方程（按原变量定义，仅作数学背景）：K_u=15.3,\qquad P_u=42\ \mathrm s. ; k_P=0.5K_u=0.5(15.3)=7.65. ; k_P=0.45K_u=0.45(15.3)=6.885,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 80. 直流电机直流增益逆前馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 80 题 [Ch4-20]。定位：Example 4.11, PDF 591-596。

原题保留：直流电机直流增益逆前馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s^2+1.4s+1)、G(0)=1；比较 kP=1.5 与 6，参考前馈 kff=1，并测试可测扰动前馈。 来源模型方程（按原变量定义，仅作数学背景）：U=k_P(R-Y)+k_{ff}R. ; \frac{Y}{R} =\frac{G(k_P+k_{ff})}{1+k_PG}. ; T(0)=\frac{g_0k_P+1}{1+g_0k_P}=1. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机直流增益逆前馈。本次仅做外部软件模型的适配子任务：使 motor_speed 保持在 0.0319968 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 80 题 [Ch4-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_speed", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["armature_voltage_combining_feedback_and_feedforward"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0319968` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.919808` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.59984` |
| 输出上限 | `output_max` | `1.59984` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0639936` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s^2+1.4s+1)、G(0)=1；比较 kP=1.5 与 6，参考前馈 kff=1，并测试可测扰动前馈。 来源模型方程（按原变量定义，仅作数学背景）：U=k_P(R-Y)+k_{ff}R. ; \frac{Y}{R} =\frac{G(k_P+k_{ff})}{1+k_PG}. ; T(0)=\frac{g_0k_P+1}{1+g_0k_P}=1.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 81. 直流电机位置环根轨迹

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 81 题 [Ch5-01]。定位：Example 5.1, PDF 665-668。

原题保留：直流电机位置环根轨迹。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)]，扫描 K=0.1、0.25、1、4；单位阶跃以 0.01 s 运行 20 s。 来源模型方程（按原变量定义，仅作数学背景）：1+\frac{K}{s(s+1)}=0 \quad\Longrightarrow\quad s^2+s+K=0. ; s_{1,2}=-\frac12\pm\frac{\sqrt{1-4K}}2. ; s=-\frac12\pm j\frac{\sqrt{4K-1}}2,\quad \omega_n=\sqrt K,\quad \zeta=\frac1{2\sqrt K}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机位置环根轨迹。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 81 题 [Ch5-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["motor_armature_voltage"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)]，扫描 K=0.1、0.25、1、4；单位阶跃以 0.01 s 运行 20 s。 来源模型方程（按原变量定义，仅作数学背景）：1+\frac{K}{s(s+1)}=0 \quad\Longrightarrow\quad s^2+s+K=0. ; s_{1,2}=-\frac12\pm\frac{\sqrt{1-4K}}2. ; s=-\frac12\pm j\frac{\sqrt{4K-1}}2,\quad \omega_n=\sqrt K,\quad \zeta=\frac1{2\sqrt K}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 82. 以物理阻尼参数为变量的根轨迹

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 82 题 [Ch5-02]。定位：Example 5.2, PDF 668-671。

原题保留：以物理阻尼参数为变量的根轨迹。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取特征式 s^2+c s+1，扫描物理阻尼 c=0、1、2、4，并记录自由与阶跃响应。 来源模型方程（按原变量定义，仅作数学背景）：s^2+cs+1=0 \quad\Longleftrightarrow\quad 1+c\frac{s}{s^2+1}=0. ; s_{1,2}=-\frac c2\pm\frac{\sqrt{c^2-4}}2. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：以物理阻尼参数为变量的根轨迹。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 82 题 [Ch5-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取特征式 s^2+c s+1，扫描物理阻尼 c=0、1、2、4，并记录自由与阶跃响应。 来源模型方程（按原变量定义，仅作数学背景）：s^2+cs+1=0 \quad\Longleftrightarrow\quad 1+c\frac{s}{s^2+1}=0. ; s_{1,2}=-\frac c2\pm\frac{\sqrt{c^2-4}}2.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 83. Evans 规则构造高阶根轨迹

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 83 题 [Ch5-03]。定位：Section 5.2/Eq. 5.20, PDF 672-698。

原题保留：Evans 规则构造高阶根轨迹。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=1/[s((s+4)^2+16)]，在 K=10、32、65、100 附近扫描，以 0.01 s 运行 30 s。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac1{s[(s+4)^2+16]} =\frac1{s(s+4-4j)(s+4+4j)}. ; \alpha=\frac{0-4-4}{3}=-\frac83, ; K=\frac1{|L(s_0)|} =|s_0||s_0+4-4j||s_0+4+4j|. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Evans 规则构造高阶根轨迹。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 83 题 [Ch5-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=1/[s((s+4)^2+16)]，在 K=10、32、65、100 附近扫描，以 0.01 s 运行 30 s。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac1{s[(s+4)^2+16]} =\frac1{s(s+4-4j)(s+4+4j)}. ; \alpha=\frac{0-4-4}{3}=-\frac83, ; K=\frac1{|L(s_0)|} =|s_0||s_0+4-4j||s_0+4+4j|.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 84. 用 PD 稳定卫星双积分器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 84 题 [Ch5-04]。定位：Example 5.3, PDF 700-703。

原题保留：用 PD 稳定卫星双积分器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取卫星 G=1/s^2 与 PD D=K(s+1)；扫描 K=0.25、1、4、9，并给微分加高频滤波。 来源模型方程（按原变量定义，仅作数学背景）：1+K\frac{s+1}{s^2}=0 \quad\Longrightarrow\quad s^2+Ks+K=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用 PD 稳定卫星双积分器。本次仅做外部软件模型的适配子任务：使 satellite_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 84 题 [Ch5-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["satellite_attitude", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["PD_body_torque_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取卫星 G=1/s^2 与 PD D=K(s+1)；扫描 K=0.25、1、4、9，并给微分加高频滤波。 来源模型方程（按原变量定义，仅作数学背景）：1+K\frac{s+1}{s^2}=0 \quad\Longrightarrow\quad s^2+Ks+K=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 85. 有限超前极点对卫星 PD 的影响

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 85 题 [Ch5-05]。定位：Examples 5.4-5.7, PDF 704-715。

原题保留：有限超前极点对卫星 PD 的影响。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=(s+1)/[s^2(s+p)]，比较 p=4、9、12 及 K=1、5、20，以 0.005 s 采样。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac{s+1}{s^2(s+p)},\qquad p>1, ; s^2(s+p)+K(s+1)=s^3+ps^2+Ks+K. ; s^3+ps^2+Ks+K=(s+3)^3 =s^3+9s^2+27s+27, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：有限超前极点对卫星 PD 的影响。本次仅做外部软件模型的适配子任务：使 satellite_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 85 题 [Ch5-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["satellite_attitude", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["lead_compensated_body_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=(s+1)/[s^2(s+p)]，比较 p=4、9、12 及 K=1、5、20，以 0.005 s 采样。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac{s+1}{s^2(s+p)},\qquad p>1, ; s^2(s+p)+K(s+1)=s^3+ps^2+Ks+K. ; s^3+ps^2+Ks+K=(s+3)^3 =s^3+9s^2+27s+27,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 86. 共址柔性卫星的模态阻尼

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 86 题 [Ch5-06]。定位：Example 5.8, PDF 716-720。

原题保留：共址柔性卫星的模态阻尼。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用共址柔性卫星 G=[(s+0.1)^2+36]/{s^2[(s+0.1)^2+43.56]} 与 lead K(s+1)/(s+12)，扫描 K。 来源模型方程（按原变量定义，仅作数学背景）：G=\frac{(s+0.1)^2+6^2}{s^2[(s+0.1)^2+6.6^2]},\qquad D_c=K\frac{s+1}{s+12}. ; \phi_{\rm dep}=142.6^\circ 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：共址柔性卫星的模态阻尼。本次仅做外部软件模型的适配子任务：使 collocated_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 86 题 [Ch5-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["collocated_attitude", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["collocated_body_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用共址柔性卫星 G=[(s+0.1)^2+36]/{s^2[(s+0.1)^2+43.56]} 与 lead K(s+1)/(s+12)，扫描 K。 来源模型方程（按原变量定义，仅作数学背景）：G=\frac{(s+0.1)^2+6^2}{s^2[(s+0.1)^2+6.6^2]},\qquad D_c=K\frac{s+1}{s+12}. ; \phi_{\rm dep}=142.6^\circ
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 87. 非共址柔性卫星的溢出失稳

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 87 题 [Ch5-07]。定位：Example 5.9, PDF 720-724。

原题保留：非共址柔性卫星的溢出失稳。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用非共址 G=1/{s^2[(s+0.1)^2+43.56]} 与 lead K(s+1)/(s+12)；K 从 1e-4 起扫并在失稳时停止。 来源模型方程（按原变量定义，仅作数学背景）：G=\frac1{s^2[(s+0.1)^2+6.6^2]},\qquad D_c=K\frac{s+1}{s+12}. ; \phi_{\rm dep} =81.4^\circ-90^\circ-90^\circ-90^\circ-28.8^\circ-180^\circ \equiv-37.4^\circ. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：非共址柔性卫星的溢出失稳。本次仅做外部软件模型的适配子任务：使 remote_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 87 题 [Ch5-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["remote_attitude", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["main_body_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-0.01` |
| 输入上限 | `input_max` | `0.01` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用非共址 G=1/{s^2[(s+0.1)^2+43.56]} 与 lead K(s+1)/(s+12)；K 从 1e-4 起扫并在失稳时停止。 来源模型方程（按原变量定义，仅作数学背景）：G=\frac1{s^2[(s+0.1)^2+6.6^2]},\qquad D_c=K\frac{s+1}{s+12}. ; \phi_{\rm dep} =81.4^\circ-90^\circ-90^\circ-90^\circ-28.8^\circ-180^\circ \equiv-37.4^\circ.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 88. 四阶根轨迹的复重根

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 88 题 [Ch5-08]。定位：Example 5.10, PDF 725-728。

原题保留：四阶根轨迹的复重根。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=1/[s(s+2)((s+1)^2+4)]，让 K 穿过 6.25，以 0.005 s 运行 20 s。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac1{s(s+2)[(s+1)^2+4]} ; s(s+2)[(s+1)^2+4] =(q^2-1)(q^2+4)=q^4+3q^2-4. ; 4q^3+6q=2q(2q^2+3)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四阶根轨迹的复重根。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 88 题 [Ch5-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=1/[s(s+2)((s+1)^2+4)]，让 K 穿过 6.25，以 0.005 s 运行 20 s。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac1{s(s+2)[(s+1)^2+4]} ; s(s+2)[(s+1)^2+4] =(q^2-1)(q^2+4)=q^4+3q^2-4. ; 4q^3+6q=2q(2q^2+3)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 89. 满足上升时间与超调的超前校正

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 89 题 [Ch5-09]。定位：Example 5.11, PDF 736-746。

原题保留：满足上升时间与超调的超前校正。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)] 与 lead D=91(s+2)/(s+13)；±1 阶跃以 0.002 s 运行 5 s。 来源模型方程（按原变量定义，仅作数学背景）：D_c=K\frac{s+z}{s+p},\qquad z<p. ; D_c=91\frac{s+2}{s+13}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：满足上升时间与超调的超前校正。本次仅做外部软件模型的适配子任务：使 servo_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 89 题 [Ch5-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["servo_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["lead_compensated_servo_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)] 与 lead D=91(s+2)/(s+13)；±1 阶跃以 0.002 s 运行 5 s。 来源模型方程（按原变量定义，仅作数学背景）：D_c=K\frac{s+z}{s+p},\qquad z<p. ; D_c=91\frac{s+2}{s+13}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 90. 用滞后校正提高速度常数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 90 题 [Ch5-10]。定位：Section 5.4.2, PDF 747-751。

原题保留：用滞后校正提高速度常数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在 K=91 的 lead 设计后加入 lag (s+0.05)/(s+0.01)；阶跃与斜坡运行 300 s。 来源模型方程（按原变量定义，仅作数学背景）：K_v=\lim_{s\to0}s \frac{91(s+2)}{s(s+1)(s+13)} =91\frac2{13}=14. ; D_{\rm lag}=\frac{s+z}{s+p},\qquad \frac zp=5, ; K_v=91\frac{2(0.05)}{13(0.01)}=70. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用滞后校正提高速度常数。本次仅做外部软件模型的适配子任务：使 servo_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 90 题 [Ch5-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["servo_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["lead_lag_servo_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在 K=91 的 lead 设计后加入 lag (s+0.05)/(s+0.01)；阶跃与斜坡运行 300 s。 来源模型方程（按原变量定义，仅作数学背景）：K_v=\lim_{s\to0}s \frac{91(s+2)}{s(s+1)(s+13)} =91\frac2{13}=14. ; D_{\rm lag}=\frac{s+z}{s+p},\qquad \frac zp=5, ; K_v=91\frac{2(0.05)}{13(0.01)}=70.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 91. 用陷波校正柔性共振

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 91 题 [Ch5-11]。定位：Section 5.4.3, PDF 752-758。

原题保留：用陷波校正柔性共振。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用柔性对象 2500/[s(s+1)(s^2+s+2500)]、K=91 lead-lag 与陷波 (s^2+0.8s+3600)/(s+60)^2；柔性频率扫描 ±10%。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{2500}{s(s+1)(s^2+s+2500)}, ; D_{\ell\ell}(s)=91\frac{s+2}{s+13}\frac{s+0.05}{s+0.01} ; \omega_f=50\ {\rm rad/s},\qquad \zeta_f=\frac{1}{2(50)}=0.01, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用陷波校正柔性共振。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 91 题 [Ch5-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用柔性对象 2500/[s(s+1)(s^2+s+2500)]、K=91 lead-lag 与陷波 (s^2+0.8s+3600)/(s+60)^2；柔性频率扫描 ±10%。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{2500}{s(s+1)(s^2+s+2500)}, ; D_{\ell\ell}(s)=91\frac{s+2}{s+13}\frac{s+0.05}{s+0.01} ; \omega_f=50\ {\rm rad/s},\qquad \zeta_f=\frac{1}{2(50)}=0.01,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 92. 运放实现超前网络

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 92 题 [Ch5-12]。定位：Section 5.4.4, PDF 758-759。

原题保留：运放实现超前网络。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：用 C=10 uF、R1=50 kohm、R2=200 kohm、Rf=250 kohm 实现 -5(s+2)/(s+10)，并扫描元件 ±10%。 来源模型方程（按原变量定义，仅作数学背景）：D_{\rm lead}(s)=-a\frac{s+z}{s+p},\qquad 0<z<p,\qquad a=\frac{p}{z}. ; z=\frac{1}{R_1C},\qquad p=\frac{R_1+R_2}{R_2}\frac{1}{R_1C}. ; \frac{p}{z}=1+\frac{R_1}{R_2}>1, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：运放实现超前网络。本次仅做外部软件模型的适配子任务：使 lead_network_output_voltage 保持在 0.132 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 92 题 [Ch5-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["lead_network_output_voltage", "V"]]` |
| 输入行 [名称] | `inputs` | `[["input_error_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.132` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `7.92` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-6.6` |
| 输出上限 | `output_max` | `6.6` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.264` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想来源网络有直接通道，相对阶次 0；不能改称严格真有理一阶对象.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：用 C=10 uF、R1=50 kohm、R2=200 kohm、Rf=250 kohm 实现 -5(s+2)/(s+10)，并扫描元件 ±10%。 来源模型方程（按原变量定义，仅作数学背景）：D_{\rm lead}(s)=-a\frac{s+z}{s+p},\qquad 0<z<p,\qquad a=\frac{p}{z}. ; z=\frac{1}{R_1C},\qquad p=\frac{R_1+R_2}{R_2}\frac{1}{R_1C}. ; \frac{p}{z}=1+\frac{R_1}{R_2}>1,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 93. 四旋翼俯仰轴超前校正

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 93 题 [Ch5-13]。定位：Example 5.12, PDF 760-769。

原题保留：四旋翼俯仰轴超前校正。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取四旋翼俯仰对象 1/[s^2(s+2)] 与 lead 30(s+0.5)/(s+15)；±0.1 rad 命令以 0.002 s 运行 15 s。 来源模型方程（按原变量定义，仅作数学背景）：G_1(s)=\frac{1}{s^2(s+2)}, ; D_c(s)=K\frac{s+z}{s+p},\qquad p>z. ; s^2(s+2)+K=s^3+2s^2+K. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四旋翼俯仰轴超前校正。本次仅做外部软件模型的适配子任务：使 quadrotor_pitch_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 93 题 [Ch5-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0.0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0.0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.02 附近，误差不超过 0.04"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0.0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["quadrotor_pitch_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["pitch_rotor_torque_command"]]` |
| 输入单位 | `input_unit` | `"rad"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取四旋翼俯仰对象 1/[s^2(s+2)] 与 lead 30(s+0.5)/(s+15)；±0.1 rad 命令以 0.002 s 运行 15 s。 来源模型方程（按原变量定义，仅作数学背景）：G_1(s)=\frac{1}{s^2(s+2)}, ; D_c(s)=K\frac{s+z}{s+p},\qquad p>z. ; s^2(s+2)+K=s^3+2s^2+K.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 94. 小型飞机俯仰自动驾驶与积分配平

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 94 题 [Ch5-14]。定位：Example 5.13, PDF 769-782。

原题保留：小型飞机俯仰自动驾驶与积分配平。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取飞机对象 160(s+2.5)(s+0.7)/[(s^2+5s+40)(s^2+0.03s+0.06)]，lead K=1.5,z=3,p=20，配平积分 KI=0.15。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{160(s+2.5)(s+0.7)} {(s^2+5s+40)(s^2+0.03s+0.06)}. ; D_c(s)=\frac{s+3}{s+20},\qquad K=1.5. ; D_{\rm eq}=KD_c\left(1+\frac{K_I}{s}\right), 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：小型飞机俯仰自动驾驶与积分配平。本次仅做外部软件模型的适配子任务：使 pitch_angle 保持在 0.2 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 94 题 [Ch5-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pitch_angle", "deg"]]` |
| 输入行 [名称] | `inputs` | `[["elevator_deflection"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.2` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `12.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-10` |
| 输出上限 | `output_max` | `10` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.4` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取飞机对象 160(s+2.5)(s+0.7)/[(s^2+5s+40)(s^2+0.03s+0.06)]，lead K=1.5,z=3,p=20，配平积分 KI=0.15。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{160(s+2.5)(s+0.7)} {(s^2+5s+40)(s^2+0.03s+0.06)}. ; D_c(s)=\frac{s+3}{s+20},\qquad K=1.5. ; D_{\rm eq}=KD_c\left(1+\frac{K_I}{s}\right),
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 95. 非最小相位飞机高度的零度根轨迹

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 95 题 [Ch5-15]。定位：Example 5.14, PDF 787-789。

原题保留：非最小相位飞机高度的零度根轨迹。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取飞机高度对象 (6-s)/[s(s^2+4s+13)]，用对应负根轨迹扫描正物理增益，并施加 ±1° 脉冲。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{6-s}{s(s^2+4s+13)} =-\frac{s-6}{s(s^2+4s+13)} ; \sigma_a=\frac{(0-2-2)-6}{2}=-5. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：非最小相位飞机高度的零度根轨迹。本次仅做外部软件模型的适配子任务：使 aircraft_altitude_response 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 95 题 [Ch5-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["aircraft_altitude_response", "ft"]]` |
| 输入行 [名称] | `inputs` | `[["elevator_command"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：来源高度通道含右半平面零点，符号约定要求负增益根轨迹.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取飞机高度对象 (6-s)/[s(s^2+4s+13)]，用对应负根轨迹扫描正物理增益，并施加 ±1° 脉冲。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{6-s}{s(s^2+4s+13)} =-\frac{s-6}{s(s^2+4s+13)} ; \sigma_a=\frac{(0-2-2)-6}{2}=-5.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 96. 测速与放大器两参数的逐次根轨迹

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 96 题 [Ch5-16]。定位：Example 5.15, PDF 790-795。

原题保留：测速与放大器两参数的逐次根轨迹。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 s^2+s+KA+KT s=0；先取 KA=4，再取 KT=1，并在 ±10% 参数下重复。 来源模型方程（按原变量定义，仅作数学背景）：s^2+s+K_A+K_Ts=0. ; 1+K_T\frac{s}{s^2+s+4}=0. ; s^2+2s+4=0, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：测速与放大器两参数的逐次根轨迹。本次仅做外部软件模型的适配子任务：使 servomechanism_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 96 题 [Ch5-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["servomechanism_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["servo_amplifier_voltage_under_tachometer_feedback"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 s^2+s+KA+KT s=0；先取 KA=4，再取 KT=1，并在 ±10% 参数下重复。 来源模型方程（按原变量定义，仅作数学背景）：s^2+s+K_A+K_Ts=0. ; 1+K_T\frac{s}{s^2+s+4}=0. ; s^2+2s+4=0,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 97. 四旋翼内姿态外位置级联

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 97 题 [Ch5-17]。定位：Example 5.16, PDF 796-801。

原题保留：四旋翼内姿态外位置级联。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：内俯仰对象 1/[s^2(s+2)] 配 30(s+0.5)/(s+15)，外位置对象 -32.2/s^2 配 0.081(s+0.1)/(s+10)。 来源模型方程（按原变量定义，仅作数学背景）：L_1(s)=\frac{G_1}{1+G_1\,30(s+0.5)/(s+15)} =\frac{s+15}{s^4+17s^3+30s^2+30s+15}. ; 1+D_2(s)\frac{32.2}{s^2}L_1(s)=0. ; D_2(s)=0.081\frac{s+0.1}{s+10}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四旋翼内姿态外位置级联。本次仅做外部软件模型的适配子任务：使 horizontal_position_deviation 保持在 0.04 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 97 题 [Ch5-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.04 附近，误差不超过 0.08"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["horizontal_position_deviation", "ft"]]` |
| 输入行 [名称] | `inputs` | `[["equivalent_pitch_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_torque"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.04` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：内俯仰对象 1/[s^2(s+2)] 配 30(s+0.5)/(s+15)，外位置对象 -32.2/s^2 配 0.081(s+0.1)/(s+10)。 来源模型方程（按原变量定义，仅作数学背景）：L_1(s)=\frac{G_1}{1+G_1\,30(s+0.5)/(s+15)} =\frac{s+15}{s^4+17s^3+30s^2+30s+15}. ; 1+D_2(s)\frac{32.2}{s^2}L_1(s)=0. ; D_2(s)=0.081\frac{s+0.1}{s+10}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 98. 数控机床伺服的超前设计

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 98 题 [Ch5-18]。定位：Problem 5.25, PDF 833-834。

原题保留：数控机床伺服的超前设计。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取机床 G=1/[s(s+1)] 与 lead 10(s+1)/(s+2)；测试 ±1 位置阶跃及极点 ±10% 变化。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)}, ; D(s)=K\frac{s+z}{s+p},\qquad p>z>0. ; (s+1-j3)(s+1+j3)=s^2+2s+10. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：数控机床伺服的超前设计。本次仅做外部软件模型的适配子任务：使 machine_tool_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 98 题 [Ch5-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["machine_tool_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["lead_compensated_servo_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取机床 G=1/[s(s+1)] 与 lead 10(s+1)/(s+2)；测试 ±1 位置阶跃及极点 ±10% 变化。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)}, ; D(s)=K\frac{s+z}{s+p},\qquad p>z>0. ; (s+1-j3)(s+1+j3)=s^2+2s+10.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 99. 磁悬浮线性模型与根轨迹稳定

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 99 题 [Ch5-19]。定位：Problem 5.28, PDF 835-837。

原题保留：磁悬浮线性模型与根轨迹稳定。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=0.02 kg、g=9.8、e=100x、f=0.5i+20x，并用 K=1 的 lead (s+10)/(s+20)，以 0.001 s 采样。 来源模型方程（按原变量定义，仅作数学背景）：e=100x,\quad f=0.5i+20x,\quad i=u+V_0,\quad m=0.02\ {\rm kg},\quad g=9.8\ {\rm m/s^2}. ; 0.5V_0=mg=0.196,\qquad V_0=0.392\ {\rm A}. ; 0.02\ddot x=0.5u+20x, \qquad \frac{X}{U}=\frac{25}{s^2-1000}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：磁悬浮线性模型与根轨迹稳定。本次仅做外部软件模型的适配子任务：使 ball_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 99 题 [Ch5-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["ball_position", "m"]]` |
| 输入行 [名称] | `inputs` | `[["electromagnet_current_command"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：磁悬浮线性化开环不稳定，来源超前器是独立反馈设计.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：磁力仅在平衡点附近线性化.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=0.02 kg、g=9.8、e=100x、f=0.5i+20x，并用 K=1 的 lead (s+10)/(s+20)，以 0.001 s 采样。 来源模型方程（按原变量定义，仅作数学背景）：e=100x,\quad f=0.5i+20x,\quad i=u+V_0,\quad m=0.02\ {\rm kg},\quad g=9.8\ {\rm m/s^2}. ; 0.5V_0=mg=0.196,\qquad V_0=0.392\ {\rm A}. ; 0.02\ddot x=0.5u+20x, \qquad \frac{X}{U}=\frac{25}{s^2-1000},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 100. Tampa 舰艏向与偏航率反馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 100 题 [Ch5-20]。定位：Problem 5.38, PDF 846-849。

原题保留：Tampa 舰艏向与偏航率反馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 Tampa 舵角对象 -0.0184(s+0.0068)/[s(s+0.2647)(s+0.0063)]；吸收符号后取 Kpsi=0.1、Kr=1、KI=0.0001，并执行舵角限幅。 来源模型方程（按原变量定义，仅作数学背景）：G_\delta=\frac{\Psi}{\Delta} =\frac{-0.0184(s+0.0068)}{s(s+0.2647)(s+0.0063)},\qquad G_w=\frac{\Psi}{W} =\frac{6.4\times10^{-6}}{s(s+0.2647)(s+0.0063)}. ; \frac{R}{\Delta} =\frac{-0.0184(s+0.0068)} {(s+0.2647)(s+0.0063)}. ; D_0+0.0184(K_\psi+K_rs)(s+0.0068)=0, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Tampa 舰艏向与偏航率反馈。本次仅做外部软件模型的适配子任务：使 ship_heading 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 100 题 [Ch5-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["ship_heading", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["rudder_command_and_prescribed_wind_gust_input"]]` |
| 输入单位 | `input_unit` | `"rad"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 Tampa 舵角对象 -0.0184(s+0.0068)/[s(s+0.2647)(s+0.0063)]；吸收符号后取 Kpsi=0.1、Kr=1、KI=0.0001，并执行舵角限幅。 来源模型方程（按原变量定义，仅作数学背景）：G_\delta=\frac{\Psi}{\Delta} =\frac{-0.0184(s+0.0068)}{s(s+0.2647)(s+0.0063)},\qquad G_w=\frac{\Psi}{W} =\frac{6.4\times10^{-6}}{s(s+0.2647)(s+0.0063)}. ; \frac{R}{\Delta} =\frac{-0.0184(s+0.0068)} {(s+0.2647)(s+0.0063)}. ; D_0+0.0184(K_\psi+K_rs)(s+0.0068)=0,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 101. 电压驱动电容的频率响应

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 101 题 [Ch6-01]。定位：Example 6.1, PDF 870-871。

原题保留：电压驱动电容的频率响应。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 C=100 uF，输入 1 V、1/10/100/1000 rad/s 正弦电压；每周期至少采样 50 点的电流。 来源模型方程（按原变量定义，仅作数学背景）：I(s)=CsV(s),\qquad G(s)=\frac{I(s)}{V(s)}=Cs. ; G(j\omega)=jC\omega,\quad |G(j\omega)|=C\omega,\quad \angle G(j\omega)=90^\circ. ; i_{\rm ss}(t)=AC\omega\sin(\omega t+90^\circ) =AC\omega\cos\omega t. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：电压驱动电容的频率响应。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 101 题 [Ch6-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想电容电流/电压关系是微分，相对阶次 -1、非真有理；未提供通常的严格真有理对象.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 C=100 uF，输入 1 V、1/10/100/1000 rad/s 正弦电压；每周期至少采样 50 点的电流。 来源模型方程（按原变量定义，仅作数学背景）：I(s)=CsV(s),\qquad G(s)=\frac{I(s)}{V(s)}=Cs. ; G(j\omega)=jC\omega,\quad |G(j\omega)|=C\omega,\quad \angle G(j\omega)=90^\circ. ; i_{\rm ss}(t)=AC\omega\sin(\omega t+90^\circ) =AC\omega\cos\omega t.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 102. 一阶超前环节的幅相特性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 102 题 [Ch6-02]。定位：Example 6.2, PDF 871-874。

原题保留：一阶超前环节的幅相特性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 lead D=(s+1)/(0.1s+1)，扫描 0.1–100 rad/s，并核对 1、sqrt(10)、10 rad/s 的幅相。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=K\frac{Ts+1}{\alpha Ts+1}, \qquad K>0,\ T>0,\ 0<\alpha<1. ; |D_c|=K\sqrt{\frac{1+(\omega T)^2} {1+(\alpha\omega T)^2}},\quad \phi=\tan^{-1}(\omega T)-\tan^{-1}(\alpha\omega T). ; |D_c(0)|=K,\qquad |D_c(j\infty)|=\frac K\alpha,\qquad \phi(0)=\phi(\infty)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：一阶超前环节的幅相特性。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 102 题 [Ch6-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：理想来源网络有直接通道，相对阶次 0；不能改称严格真有理一阶对象.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 lead D=(s+1)/(0.1s+1)，扫描 0.1–100 rad/s，并核对 1、sqrt(10)、10 rad/s 的幅相。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=K\frac{Ts+1}{\alpha Ts+1}, \qquad K>0,\ T>0,\ 0<\alpha<1. ; |D_c|=K\sqrt{\frac{1+(\omega T)^2} {1+(\alpha\omega T)^2}},\quad \phi=\tan^{-1}(\omega T)-\tan^{-1}(\alpha\omega T). ; |D_c(0)|=K,\qquad |D_c(j\infty)|=\frac K\alpha,\qquad \phi(0)=\phi(\infty)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 103. 实极点零点的渐近 Bode 图

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 103 题 [Ch6-03]。定位：Example 6.3, PDF 898-901。

原题保留：实极点零点的渐近 Bode 图。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=2000(s+0.5)/[s(s+10)(s+50)]，在 0.01–1000 rad/s 对数网格计算。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac{2000(s+0.5)}{s(s+10)(s+50)} =\frac{2(s/0.5+1)} {s(s/10+1)(s/50+1)}. ; L(j\omega)\simeq\frac2{j\omega},\qquad |L|\simeq\frac2\omega,\quad\angle L\simeq-90^\circ. ; -1\ \longrightarrow\ 0\ \longrightarrow\ -1 \ \longrightarrow\ -2 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：实极点零点的渐近 Bode 图。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 103 题 [Ch6-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=2000(s+0.5)/[s(s+10)(s+50)]，在 0.01–1000 rad/s 对数网格计算。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac{2000(s+0.5)}{s(s+10)(s+50)} =\frac{2(s/0.5+1)} {s(s/10+1)(s/50+1)}. ; L(j\omega)\simeq\frac2{j\omega},\qquad |L|\simeq\frac2\omega,\quad\angle L\simeq-90^\circ. ; -1\ \longrightarrow\ 0\ \longrightarrow\ -1 \ \longrightarrow\ -2
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 104. 复极点零点与柔性卫星 Bode 图

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 104 题 [Ch6-04]。定位：Examples 6.4-6.6, PDF 901-907。

原题保留：复极点零点与柔性卫星 Bode 图。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：比较 L1=10/[s(s^2+0.4s+4)] 与柔性 doublet 0.01(s^2+0.01s+1)/{s^2(s^2/4+0.01s+1)}。 来源模型方程（按原变量定义，仅作数学背景）：L_1(s)=\frac{10}{s(s^2+0.4s+4)} =\frac{2.5}{s[(s/2)^2+2(0.1)(s/2)+1]}. ; L_2(s)=\frac{0.01(s^2+0.01s+1)} {s^2[s^2/4+0.01s+1]}. ; -2\ \xrightarrow{\omega=1}\ 0 \ \xrightarrow{\omega=2}\ -2, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：复极点零点与柔性卫星 Bode 图。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 104 题 [Ch6-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：比较 L1=10/[s(s^2+0.4s+4)] 与柔性 doublet 0.01(s^2+0.01s+1)/{s^2(s^2/4+0.01s+1)}。 来源模型方程（按原变量定义，仅作数学背景）：L_1(s)=\frac{10}{s(s^2+0.4s+4)} =\frac{2.5}{s[(s/2)^2+2(0.1)(s/2)+1]}. ; L_2(s)=\frac{0.01(s^2+0.01s+1)} {s^2[s^2/4+0.01s+1]}. ; -2\ \xrightarrow{\omega=1}\ 0 \ \xrightarrow{\omega=2}\ -2,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 105. 由低频 Bode 图识别系统型别与误差常数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 105 题 [Ch6-05]。定位：Example 6.7, PDF 912-914。

原题保留：由低频 Bode 图识别系统型别与误差常数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=10/[s(s+1)]，单位斜坡以 0.01 s 运行 50 s，并拟合末段误差。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac{10}{s(s+1)}, ; L(j\omega)\simeq\frac{10}{j\omega}, ; E(s)=\frac{R(s)}{1+L(s)} 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由低频 Bode 图识别系统型别与误差常数。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 105 题 [Ch6-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0.0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0.0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.1 附近，误差不超过 0.08"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0.0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=10/[s(s+1)]，单位斜坡以 0.01 s 运行 50 s，并拟合末段误差。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=\frac{10}{s(s+1)}, ; L(j\omega)\simeq\frac{10}{j\omega}, ; E(s)=\frac{R(s)}{1+L(s)}
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 106. 二阶环路的 Nyquist 全正增益稳定性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 106 题 [Ch6-06]。定位：Example 6.8, PDF 936-943。

原题保留：二阶环路的 Nyquist 全正增益稳定性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s+1)^2，扫描 K=0.1、1、10、100，并测试负增益 -0.5、-1、-2。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{(s+1)^2}. ; G(j\omega)=\frac{(1-\omega^2)-j2\omega} {(1+\omega^2)^2}. ; (s+1)^2+K=0,\qquad s=-1\pm j\sqrt K, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：二阶环路的 Nyquist 全正增益稳定性。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 106 题 [Ch6-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/(s+1)^2，扫描 K=0.1、1、10、100，并测试负增益 -0.5、-1、-2。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{(s+1)^2}. ; G(j\omega)=\frac{(1-\omega^2)-j2\omega} {(1+\omega^2)^2}. ; (s+1)^2+K=0,\qquad s=-1\pm j\sqrt K,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 107. 含原点极点的三阶 Nyquist 判稳

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 107 题 [Ch6-07]。定位：Example 6.9, PDF 943-951。

原题保留：含原点极点的三阶 Nyquist 判稳。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)^2]，扫描 K=0.5、1、2、3，并在原点使用 Nyquist 凹入轮廓。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)^2} ; |G(j\omega)|=\frac1{\omega(1+\omega^2)},\qquad \angle G=-90^\circ-2\tan^{-1}\omega. ; |G(j)|=\frac1{1(1+1)}=0.5. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：含原点极点的三阶 Nyquist 判稳。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 107 题 [Ch6-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)^2]，扫描 K=0.5、1、2、3，并在原点使用 Nyquist 凹入轮廓。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)^2} ; |G(j\omega)|=\frac1{\omega(1+\omega^2)},\qquad \angle G=-90^\circ-2\tan^{-1}\omega. ; |G(j)|=\frac1{1(1+1)}=0.5.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 108. 两个特殊 Nyquist 环路的稳定性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 108 题 [Ch6-08]。定位：Examples 6.10-6.11, PDF 951-964。

原题保留：两个特殊 Nyquist 环路的稳定性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对 G1=(s+1)/[s(s/10-1)] 取 K=0.5、1、2；另对 G2=(s^2+3)/(s+1)^2 测试正增益。 来源模型方程（按原变量定义，仅作数学背景）：G_1(s)=\frac{s+1}{s(s/10-1)},\qquad G_2(s)=\frac{s^2+3}{(s+1)^2}. ; s(s/10-1)+K(s+1) =0.1s^2+(K-1)s+K=0. ; (s+1)^2+K(s^2+3) =(1+K)s^2+2s+(1+3K)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：两个特殊 Nyquist 环路的稳定性。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 108 题 [Ch6-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对 G1=(s+1)/[s(s/10-1)] 取 K=0.5、1、2；另对 G2=(s^2+3)/(s+1)^2 测试正增益。 来源模型方程（按原变量定义，仅作数学背景）：G_1(s)=\frac{s+1}{s(s/10-1)},\qquad G_2(s)=\frac{s^2+3}{(s+1)^2}. ; s(s/10-1)+K(s+1) =0.1s^2+(K-1)s+K=0. ; (s+1)^2+K(s^2+3) =(1+K)s^2+2s+(1+3K)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 109. 条件稳定与误导性增益裕度

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 109 题 [Ch6-09]。定位：Example 6.12, PDF 980-983。

原题保留：条件稳定与误导性增益裕度。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=K(s+10)^2/s^3，比较 K=4.9、5、7、10；K=7 时测量增益上下两个方向的裕度。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=K\frac{(s+10)^2}{s^3},\qquad K>0. ; s^3+K(s+10)^2 =s^3+Ks^2+20Ks+100K. ; 1,\quad K,\quad 20(K-5),\quad100K. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：条件稳定与误导性增益裕度。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 109 题 [Ch6-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 L=K(s+10)^2/s^3，比较 K=4.9、5、7、10；K=7 时测量增益上下两个方向的裕度。 来源模型方程（按原变量定义，仅作数学背景）：L(s)=K\frac{(s+10)^2}{s^3},\qquad K>0. ; s^3+K(s+10)^2 =s^3+Ks^2+20Ks+100K. ; 1,\quad K,\quad 20(K-5),\quad100K.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 110. 多重交叉频率的稳定裕度解释

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 110 题 [Ch6-10]。定位：Example 6.13, PDF 984-987。

原题保留：多重交叉频率的稳定裕度解释。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 G=85(s+1)(s^2+2s+43.25)/{s^2(s^2+2s+82)(s^2+2s+101)}，逐一解析所有单位增益交叉。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{85(s+1)(s^2+2s+43.25)} {s^2(s^2+2s+82)(s^2+2s+101)} ; \omega_c=0.75,\ 9.0,\ 10.1\ {\rm rad/s}, ; |G(j10.4)|=0.79,\qquad GM=\frac1{0.79}=1.26. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：多重交叉频率的稳定裕度解释。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 110 题 [Ch6-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 G=85(s+1)(s^2+2s+43.25)/{s^2(s^2+2s+82)(s^2+2s+101)}，逐一解析所有单位增益交叉。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{85(s+1)(s^2+2s+43.25)} {s^2(s^2+2s+82)(s^2+2s+101)} ; \omega_c=0.75,\ 9.0,\ 10.1\ {\rm rad/s}, ; |G(j10.4)|=0.79,\qquad GM=\frac1{0.79}=1.26.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 111. 用增益相位斜率准则设计航天器 PD

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 111 题 [Ch6-11]。定位：Example 6.14, PDF 994-1000。

原题保留：用增益相位斜率准则设计航天器 PD。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取航天器 G=1/s^2 与 KD=0.01(20s+1)；±0.1 rad 阶跃以 0.05 s 运行 200 s。 来源模型方程（按原变量定义，仅作数学背景）：K D_c(s)=K(T_Ds+1) ; \frac1{T_D}=0.05\ {\rm rad/s},\qquad T_D=20\ {\rm s}. ; \left|\frac{20j\omega+1}{(j\omega)^2}\right| =\frac{\sqrt{17}}{0.04}\approx103, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用增益相位斜率准则设计航天器 PD。本次仅做外部软件模型的适配子任务：使 attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 111 题 [Ch6-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["attitude", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque_command"]]` |
| 输入单位 | `input_unit` | `"rad"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取航天器 G=1/s^2 与 KD=0.01(20s+1)；±0.1 rad 阶跃以 0.05 s 运行 200 s。 来源模型方程（按原变量定义，仅作数学背景）：K D_c(s)=K(T_Ds+1) ; \frac1{T_D}=0.05\ {\rm rad/s},\qquad T_D=20\ {\rm s}. ; \left|\frac{20j\omega+1}{(j\omega)^2}\right| =\frac{\sqrt{17}}{0.04}\approx103,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 112. 交叉频率相位裕度与闭环带宽

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 112 题 [Ch6-12]。定位：Section 6.6, PDF 1002-1004。

原题保留：交叉频率相位裕度与闭环带宽。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取代表环路 L=1/[s(s+1)]，计算精确 T=L/(1+L)，比较交叉频率、相位裕度、共振与 -3 dB 带宽。 来源模型方程（按原变量定义，仅作数学背景）：T(j\omega)=\frac{L(j\omega)}{1+L(j\omega)}. ; L=e^{j(-180^\circ+PM)}. ; |1+L|=2\sin\frac{PM}{2},\qquad |T(j\omega_c)|=\frac1{2\sin(PM/2)}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：交叉频率相位裕度与闭环带宽。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 112 题 [Ch6-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取代表环路 L=1/[s(s+1)]，计算精确 T=L/(1+L)，比较交叉频率、相位裕度、共振与 -3 dB 带宽。 来源模型方程（按原变量定义，仅作数学背景）：T(j\omega)=\frac{L(j\omega)}{1+L(j\omega)}. ; L=e^{j(-180^\circ+PM)}. ; |1+L|=2\sin\frac{PM}{2},\qquad |T(j\omega_c)|=\frac1{2\sin(PM/2)}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 113. 直流电机位置环超前设计

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 113 题 [Ch6-13]。定位：Example 6.15, PDF 1014-1023。

原题保留：直流电机位置环超前设计。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取电机 G=1/[s(s+1)] 与 lead D=10(s/2+1)/(s/10+1)；测试斜坡与阶跃命令。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)} ; D(s)=K\frac{s/2+1}{s/10+1}. ; K_v=\lim_{s\to0}sD(s)G(s)=K, \qquad e_{\rm ss}=\frac1{K_v}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机位置环超前设计。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 113 题 [Ch6-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["lead_compensated_motor_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取电机 G=1/[s(s+1)] 与 lead D=10(s/2+1)/(s/10+1)；测试斜坡与阶跃命令。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)} ; D(s)=K\frac{s/2+1}{s/10+1}. ; K_v=\lim_{s\to0}sD(s)G(s)=K, \qquad e_{\rm ss}=\frac1{K_v},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 114. 热过程单超前与伺服双超前设计

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 114 题 [Ch6-14]。定位：Examples 6.16-6.17, PDF 1023-1032。

原题保留：热过程单超前与伺服双超前设计。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：热对象取 K=9 与 lead (s/1.5+1)/(s/15+1)；伺服取双 lead (s/2+1)(s/4+1)/[(s/20+1)(s/40+1)]。 来源模型方程（按原变量定义，仅作数学背景）：G_T(s)=\frac1{(s/0.5+1)(s+1)(s/2+1)} ; G_S(s)=\frac{10}{s(s/2.5+1)(s/6+1)} ; D_T(s)=\frac{s/1.5+1}{s/15+1}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：热过程单超前与伺服双超前设计。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 114 题 [Ch6-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：热对象取 K=9 与 lead (s/1.5+1)/(s/15+1)；伺服取双 lead (s/2+1)(s/4+1)/[(s/20+1)(s/40+1)]。 来源模型方程（按原变量定义，仅作数学背景）：G_T(s)=\frac1{(s/0.5+1)(s+1)(s/2+1)} ; G_S(s)=\frac{10}{s(s/2.5+1)(s/6+1)} ; D_T(s)=\frac{s/1.5+1}{s/15+1},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 115. 热过程与电机的滞后校正

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 115 题 [Ch6-15]。定位：Examples 6.18-6.19, PDF 1037-1047。

原题保留：热过程与电机的滞后校正。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：热对象使用 lag 3(5s+1)/(15s+1)；电机使用 K=10、lag 零点 0.1、极点 0.01 rad/s。 来源模型方程（按原变量定义，仅作数学背景）：G_T=\frac1{(s/0.5+1)(s+1)(s/2+1)}, ; D_{\rm lag,T}=3\frac{5s+1}{15s+1}. ; K_p=K D_{\rm lag,T}(0)G_T(0)=3\times3=9. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：热过程与电机的滞后校正。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 115 题 [Ch6-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：热对象使用 lag 3(5s+1)/(15s+1)；电机使用 K=10、lag 零点 0.1、极点 0.01 rad/s。 来源模型方程（按原变量定义，仅作数学背景）：G_T=\frac1{(s/0.5+1)(s+1)(s/2+1)}, ; D_{\rm lag,T}=3\frac{5s+1}{15s+1}. ; K_p=K D_{\rm lag,T}(0)G_T(0)=3\times3=9.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 116. 带传感器滞后的航天器 PID

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 116 题 [Ch6-16]。定位：Example 6.20, PDF 1050-1062。

原题保留：带传感器滞后的航天器 PID。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取航天器 G=0.9/s^2、传感器 H=2/(s+2)、PID D=0.05(10s+1)(s+0.005)/s；命令与常值转矩分开测试。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{0.9}{s^2},\qquad H(s)=\frac2{s+2}, ; D_c(s)=\frac K s(T_Ds+1)(s+1/T_I). ; \frac{\Theta}{\Theta_c}=\frac{D_cG}{1+D_cGH}, \qquad \frac{\Theta}{T_d}=\frac{G}{1+D_cGH}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：带传感器滞后的航天器 PID。本次仅做外部软件模型的适配子任务：使 attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 116 题 [Ch6-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["attitude", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque_command_with_prescribed_disturbance_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取航天器 G=0.9/s^2、传感器 H=2/(s+2)、PID D=0.05(10s+1)(s+0.005)/s；命令与常值转矩分开测试。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{0.9}{s^2},\qquad H(s)=\frac2{s+2}, ; D_c(s)=\frac K s(T_Ds+1)(s+1/T_I). ; \frac{\Theta}{\Theta_c}=\frac{D_cG}{1+D_cGH}, \qquad \frac{\Theta}{T_d}=\frac{G}{1+D_cGH}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 117. 把跟踪误差要求转成性能边界

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 117 题 [Ch6-17]。定位：Example 6.21, PDF 1074-1076。

原题保留：把跟踪误差要求转成性能边界。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：要求 0–100 Hz 单位正弦跟踪误差不超过 0.005；在该频带用 S=1/201 作精确核对。 来源模型方程（按原变量定义，仅作数学背景）：S=\frac1{1+L},\qquad E=SR. ; W_1(\omega)=\frac{|R(j\omega)|}{e_b}. ; 0\le\omega\le2\pi(100)=200\pi\ {\rm rad/s}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：把跟踪误差要求转成性能边界。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 117 题 [Ch6-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0.0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0.0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.1 附近，误差不超过 0.08"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0.0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：要求 0–100 Hz 单位正弦跟踪误差不超过 0.005；在该频带用 S=1/201 作精确核对。 来源模型方程（按原变量定义，仅作数学背景）：S=\frac1{1+L},\qquad E=SR. ; W_1(\omega)=\frac{|R(j\omega)|}{e_b}. ; 0\le\omega\le2\pi(100)=200\pi\ {\rm rad/s}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 118. 对象不确定性、鲁棒稳定与灵敏度限制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 118 题 [Ch6-18]。定位：Examples 6.22-6.24, PDF 1080-1090。

原题保留：对象不确定性、鲁棒稳定与灵敏度限制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取天线 G=1/[s(s+1)] 与 D=10(0.5s+1)/(0.1s+1)；计算 S、T 并施加高频不确定性权重。 来源模型方程（按原变量定义，仅作数学背景）：G=G_0(1+W_2\Delta),\qquad|\Delta(j\omega)|\le1, ; 1+D_cG=(1+L_0)\,[1+T W_2\Delta]. ; |T(j\omega)|W_2(\omega)<1. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：对象不确定性、鲁棒稳定与灵敏度限制。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 118 题 [Ch6-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取天线 G=1/[s(s+1)] 与 D=10(0.5s+1)/(0.1s+1)；计算 S、T 并施加高频不确定性权重。 来源模型方程（按原变量定义，仅作数学背景）：G=G_0(1+W_2\Delta),\qquad|\Delta(j\omega)|\le1, ; 1+D_cG=(1+L_0)\,[1+T W_2\Delta]. ; |T(j\omega)|W_2(\omega)<1.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 119. 采样等效延迟造成的相位损失

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 119 题 [Ch6-19]。定位：Example 6.25, PDF 1091-1095。

原题保留：采样等效延迟造成的相位损失。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在交叉频率 5 rad/s 的超前电机环加入等效迟延 Td=0.025 s；比较 Ts=0.05 与 0.14 s。 来源模型方程（按原变量定义，仅作数学背景）：G_D(s)=e^{-sT_d} ; |G_D(j\omega)|=1,\qquad \angle G_D(j\omega)=-\omega T_d\ {\rm rad}. ; \Delta PM=5(0.025)=0.125\ {\rm rad} =7.16^\circ, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：采样等效延迟造成的相位损失。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 119 题 [Ch6-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在交叉频率 5 rad/s 的超前电机环加入等效迟延 Td=0.025 s；比较 Ts=0.05 与 0.14 s。 来源模型方程（按原变量定义，仅作数学背景）：G_D(s)=e^{-sT_d} ; |G_D(j\omega)|=1,\qquad \angle G_D(j\omega)=-\omega T_d\ {\rm rad}. ; \Delta PM=5(0.025)=0.125\ {\rm rad} =7.16^\circ,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 120. 用 Nichols 图读取闭环峰值与裕度

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 120 题 [Ch6-20]。定位：Examples 6.26-6.27, PDF 1101-1105。

原题保留：用 Nichols 图读取闭环峰值与裕度。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 PID 环路频率样本读取 Nichols 等值线；核对带宽 0.8 rad/s、峰值 1.2、PM 37°、GM 1.26。 来源模型方程（按原变量定义，仅作数学背景）：T=\frac{L}{1+L}. ; |T|=\frac{\rho} {\sqrt{1+\rho^2+2\rho\cos\phi}}. ; \omega_{BW}=0.8\ {\rm rad/s},\qquad M_r=1.2, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用 Nichols 图读取闭环峰值与裕度。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 120 题 [Ch6-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 PID 环路频率样本读取 Nichols 等值线；核对带宽 0.8 rad/s、峰值 1.2、PM 37°、GM 1.26。 来源模型方程（按原变量定义，仅作数学背景）：T=\frac{L}{1+L}. ; |T|=\frac{\rho} {\sqrt{1+\rho^2+2\rho\cos\phi}}. ; \omega_{BW}=0.8\ {\rm rad/s},\qquad M_r=1.2,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 121. 刚性卫星的状态变量模型

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 121 题 [Ch7-01]。定位：Example 7.1, PDF 1189-1190。

原题保留：刚性卫星的状态变量模型。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取力臂 d=1 m、惯量 I=5000 kg*m^2、状态 [角度,角速度]，施加 ±25 N 脉冲，以 0.01 s 运行 20 s。 来源模型方程（按原变量定义，仅作数学背景）：I\dot\omega=dF_c+M_D. ; \dot x= \begin{bmatrix}0&1\\0&0\end{bmatrix}x+ \begin{bmatrix}0\\d/I\end{bmatrix}F_c,\qquad y=\begin{bmatrix}1&0\end{bmatrix}x+0F_c. ; \frac{\Theta(s)}{F_c(s)}=\frac{d}{Is^2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：刚性卫星的状态变量模型。本次仅做外部软件模型的适配子任务：使 attitude_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 121 题 [Ch7-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["attitude_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["thruster_force"]]` |
| 输入单位 | `input_unit` | `"N"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-25.0` |
| 输入上限 | `input_max` | `25.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取力臂 d=1 m、惯量 I=5000 kg*m^2、状态 [角度,角速度]，施加 ±25 N 脉冲，以 0.01 s 运行 20 s。 来源模型方程（按原变量定义，仅作数学背景）：I\dot\omega=dF_c+M_D. ; \dot x= \begin{bmatrix}0&1\\0&0\end{bmatrix}x+ \begin{bmatrix}0\\d/I\end{bmatrix}F_c,\qquad y=\begin{bmatrix}1&0\end{bmatrix}x+0F_c. ; \frac{\Theta(s)}{F_c(s)}=\frac{d}{Is^2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 122. 直流电机的三阶状态模型

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 122 题 [Ch7-02]。定位：Example 7.5, PDF 1196-1197。

原题保留：直流电机的三阶状态模型。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 J=0.0113、b=0.028、La=0.1、Ra=1、Kt=Ke=0.067；施加 ±1 V 阶跃，以 0.001 s 记录角度、转速、电流。 来源模型方程（按原变量定义，仅作数学背景）：J_m\dot\omega_m+b\omega_m=K_ti_a, ; v_a=L_a\dot i_a+R_ai_a+K_e\omega_m, ; \dot x= \begin{bmatrix} 0&1&0\\ 0&-b/J_m&K_t/J_m\\ 0&-K_e/L_a&-R_a/L_a \end{bmatrix}x+ \begin{bmatrix}0\\0\\1/L_a\end{bmatrix}v_a. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：直流电机的三阶状态模型。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 122 题 [Ch7-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["armature_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 J=0.0113、b=0.028、La=0.1、Ra=1、Kt=Ke=0.067；施加 ±1 V 阶跃，以 0.001 s 记录角度、转速、电流。 来源模型方程（按原变量定义，仅作数学背景）：J_m\dot\omega_m+b\omega_m=K_ti_a, ; v_a=L_a\dot i_a+R_ai_a+K_e\omega_m, ; \dot x= \begin{bmatrix} 0&1&0\\ 0&-b/J_m&K_t/J_m\\ 0&-K_e/L_a&-R_a/L_a \end{bmatrix}x+ \begin{bmatrix}0\\0\\1/L_a\end{bmatrix}v_a.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 123. 四分之一车的实模态规范形

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 123 题 [Ch7-03]。定位：Example 7.8, PDF 1212-1213。

原题保留：四分之一车的实模态规范形。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=(2s+4)/[s^2(s^2+2s+4)]，分别实现刚体与柔性模态，以 0.005 s 采样冲激响应。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{2s+4}{s^2(s^2+2s+4)} =\frac1{s^2}-\frac1{s^2+2s+4}. ; A_r=\begin{bmatrix}0&0\\1&0\end{bmatrix},\quad B_r=\begin{bmatrix}1\\0\end{bmatrix},\quad C_r=[0\ 1]. ; \dot x_3=-2x_3-4x_4+u,\qquad \dot x_4=x_3, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四分之一车的实模态规范形。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 123 题 [Ch7-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：给定模态实现极点 0、0、-1 +/- j sqrt(3)；两个原点极点保留积分运动.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=(2s+4)/[s^2(s^2+2s+4)]，分别实现刚体与柔性模态，以 0.005 s 采样冲激响应。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{2s+4}{s^2(s^2+2s+4)} =\frac1{s^2}-\frac1{s^2+2s+4}. ; A_r=\begin{bmatrix}0&0\\1&0\end{bmatrix},\quad B_r=\begin{bmatrix}1\\0\end{bmatrix},\quad C_r=[0\ 1]. ; \dot x_3=-2x_3-4x_4+u,\qquad \dot x_4=x_3,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 124. 热系统从控制规范形变换到模态形

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 124 题 [Ch7-04]。定位：Example 7.9, PDF 1226-1228。

原题保留：热系统从控制规范形变换到模态形。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Ac=[[-7,-12],[1,0]]、Bc=[1,0]、Cc=[1,2] 与 T=[[4,-3],[-1,1]]，比较变换前后轨迹。 来源模型方程（按原变量定义，仅作数学背景）：A_c=\begin{bmatrix}-7&-12\\1&0\end{bmatrix},\quad B_c=\begin{bmatrix}1\\0\end{bmatrix},\quad C_c=[1\ 2],\quad D_c=0. ; \det(pI-A_c)=p^2+7p+12=(p+3)(p+4) ; T=\begin{bmatrix}4&-3\\-1&1\end{bmatrix},\qquad T^{-1}=\begin{bmatrix}1&3\\1&4\end{bmatrix}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：热系统从控制规范形变换到模态形。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 124 题 [Ch7-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Ac=[[-7,-12],[1,0]]、Bc=[1,0]、Cc=[1,2] 与 T=[[4,-3],[-1,1]]，比较变换前后轨迹。 来源模型方程（按原变量定义，仅作数学背景）：A_c=\begin{bmatrix}-7&-12\\1&0\end{bmatrix},\quad B_c=\begin{bmatrix}1\\0\end{bmatrix},\quad C_c=[1\ 2],\quad D_c=0. ; \det(pI-A_c)=p^2+7p+12=(p+3)(p+4) ; T=\begin{bmatrix}4&-3\\-1&1\end{bmatrix},\qquad T^{-1}=\begin{bmatrix}1&3\\1&4\end{bmatrix}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 125. 由 Piper Dakota 状态模型求极点零点

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 125 题 [Ch7-05]。定位：Examples 7.10-7.13, PDF 1229-1242。

原题保留：由 Piper Dakota 状态模型求极点零点。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用给定 Piper Dakota 四状态矩阵；施加 ±1° 升降舵脉冲，计算极点、零点与俯仰响应。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix} -5.03&-40.21&-1.5&-2.4\\ 1&0&0&0\\0&1&0&0\\0&0&1&0 \end{bmatrix},\ B=\begin{bmatrix}1\\0\\0\\0\end{bmatrix},\ C=[0\ 160\ 512\ 280],\ D=0. ; -2.5\pm j5.8095,\qquad -0.015\pm j0.2445. ; \det\begin{bmatrix}zI-A&-B\\C&D\end{bmatrix}=0 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由 Piper Dakota 状态模型求极点零点。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 125 题 [Ch7-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用给定 Piper Dakota 四状态矩阵；施加 ±1° 升降舵脉冲，计算极点、零点与俯仰响应。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix} -5.03&-40.21&-1.5&-2.4\\ 1&0&0&0\\0&1&0&0\\0&0&1&0 \end{bmatrix},\ B=\begin{bmatrix}1\\0\\0\\0\end{bmatrix},\ C=[0\ 160\ 512\ 280],\ D=0. ; -2.5\pm j5.8095,\qquad -0.015\pm j0.2445. ; \det\begin{bmatrix}zI-A&-B\\C&D\end{bmatrix}=0
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 126. 能控性、能观性与极零相消

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 126 题 [Ch7-06]。定位：Sections 7.4.1 and 7.7.1, PDF 1217-1223 and 1311-1317。

原题保留：能控性、能观性与极零相消。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

来源示例 A=diag(-3,-4)，B=[1,1]^T，C=[0,1]，D=0，x(0)=[1,0]。唯一测量输出为 y=x2；隐藏状态 x1 不可测。能控矩阵秩 2、能观矩阵秩 1；约分 G(s)=1/(s+4) 看不到 x1。输出保持子任务不能证明完整内部状态或替代原可观性练习。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：能控性、能观性与极零相消。本次仅做外部软件模型的适配子任务：使 visible_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 126 题 [Ch7-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 来源示例 A=diag(-3,-4)，B=[1,1]^T，C=[0,1]，D=0，x(0)=[1,0]。唯一测量输出为 y=x2；隐藏状态 x1 不可测。能控矩阵秩 2、能观矩阵秩 1；约分 G(s)=1/(s+4) 看不到 x1。输出保持子任务不能证明完整内部状态或替代原可观性练习。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["visible_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["state_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `1` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `1` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
第 1–7 项仅对给定适配名义数学模型及主要输入输出已知，第 8 项未知。这些是模型先验，不是硬件观测或协议绑定记录；真实传感器、标定和执行器仍未验证.
1. open_loop_stability: stable（稳定）：完整状态的两个特征值 -3 和 -4 均稳定.
2. nonminimum_phase: minimum-phase（最小相位）：实测通道 G(s)=1/(s+4) 无有限零点；稳定隐藏模态的消去不会产生右半平面零点.
3. significant_delay: not_significant（无显著迟延）：给定线性状态空间模型不含纯迟延.
4. relative_degree: low（低）：实测通道相对阶次为 1，完整状态维数仍为 2.
5. sensing_actuation_adequacy: inadequate（对完整状态重构不足）：可观性秩 1 < 2，隐藏 x1 未被测量；这不等于说实测 y 通道本身不可控.
6. nonlinearity_strength: weak（弱）：给定名义状态空间模型为线性模型.
7. coupling_underactuation: siso：一个控制输入和一个实际测量输出；隐藏状态不是第二个独立控制输出.
8. uncertainty_variation: 未知，仅凭 y 不能评价隐藏状态变化.
模型与范围：来源示例 A=diag(-3,-4)，B=[1,1]^T，C=[0,1]，D=0，x(0)=[1,0]。唯一测量输出为 y=x2；隐藏状态 x1 不可测。能控矩阵秩 2、能观矩阵秩 1；约分 G(s)=1/(s+4) 看不到 x1。输出保持子任务不能证明完整内部状态或替代原可观性练习。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。 特别保留能观性不足，不可添加 x1 测量来绕过原题。

---

## 127. 摆系统的全状态重复极点配置

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 127 题 [Ch7-07]。定位：Example 7.14, PDF 1248-1250。

原题保留：摆系统的全状态重复极点配置。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1 rad/s、反馈 K=[3,4]；从 0.1 rad 初角释放并与开环摆比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\-\omega_0^2&0\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}u,\qquad x=[\theta,\dot\theta]^T, ; A-BK=\begin{bmatrix}0&1\\-(\omega_0^2+K_1)&-K_2\end{bmatrix}. ; \det[sI-(A-BK)] =s^2+K_2s+\omega_0^2+K_1. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：摆系统的全状态重复极点配置。本次仅做外部软件模型的适配子任务：使 pendulum_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 127 题 [Ch7-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pendulum_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["pivot_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：未控摆无阻尼，极点 +/-j omega0；重复 -2 omega0 极点属于状态反馈.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1 rad/s、反馈 K=[3,4]；从 0.1 rad 初角释放并与开环摆比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\-\omega_0^2&0\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}u,\qquad x=[\theta,\dot\theta]^T, ; A-BK=\begin{bmatrix}0&1\\-(\omega_0^2+K_1)&-K_2\end{bmatrix}. ; \det[sI-(A-BK)] =s^2+K_2s+\omega_0^2+K_1.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 128. Ackermann 配置与弱能控零点

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 128 题 [Ch7-08]。定位：Examples 7.15-7.16, PDF 1257-1263。

原题保留：Ackermann 配置与弱能控零点。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：目标为 s^2+2s+4；比较 z0=2 时 K=[-3.8,0.6] 与 z0=-2.99 时 K=[2052.5,-688.1]。 来源模型方程（按原变量定义，仅作数学背景）：K=[0\ \cdots\ 0\ 1]\mathcal C^{-1}\alpha_c(A). ; A=\begin{bmatrix}-7&1\\-12&0\end{bmatrix},\quad B=\begin{bmatrix}1\\-z_0\end{bmatrix} ; s^2+(7+K_1-z_0K_2)s+ 12-z_0K_1-(12+7z_0)K_2. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Ackermann 配置与弱能控零点。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 128 题 [Ch7-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：目标为 s^2+2s+4；比较 z0=2 时 K=[-3.8,0.6] 与 z0=-2.99 时 K=[2052.5,-688.1]。 来源模型方程（按原变量定义，仅作数学背景）：K=[0\ \cdots\ 0\ 1]\mathcal C^{-1}\alpha_c(A). ; A=\begin{bmatrix}-7&1\\-12&0\end{bmatrix},\quad B=\begin{bmatrix}1\\-z_0\end{bmatrix} ; s^2+(7+K_1-z_0K_2)s+ 12-z_0K_1-(12+7z_0)K_2.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 129. Type 一电机的鲁棒参考引入

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 129 题 [Ch7-09]。定位：Example 7.18, PDF 1269-1273。

原题保留：Type 一电机的鲁棒参考引入。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取电机 A=[[0,1],[0,-1]]、B=[0,1]、K=[8,3]、参考增益 Nbar=8；施加 ±1 位置阶跃。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\0&-1\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}u,\qquad y=[1\ 0]x, ; \begin{bmatrix}A&B\\C&D\end{bmatrix} \begin{bmatrix}N_x\\N_u\end{bmatrix} =\begin{bmatrix}0\\1\end{bmatrix}. ; \bar N=N_u+KN_x=K_1. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Type 一电机的鲁棒参考引入。本次仅做外部软件模型的适配子任务：使 motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 129 题 [Ch7-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["state_feedback_voltage"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取电机 A=[[0,1],[0,-1]]、B=[0,1]、K=[8,3]、参考增益 Nbar=8；施加 ±1 位置阶跃。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\0&-1\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}u,\qquad y=[1\ 0]x, ; \begin{bmatrix}A&B\\C&D\end{bmatrix} \begin{bmatrix}N_x\\N_u\end{bmatrix} =\begin{bmatrix}0\\1\end{bmatrix}. ; \bar N=N_u+KN_x=K_1.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 130. 无人机三阶对象的主导二阶极点

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 130 题 [Ch7-10]。定位：Example 7.19, PDF 1276-1279。

原题保留：无人机三阶对象的主导二阶极点。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用三状态无人机模型、K=[14,56,96]、Nbar=96；单位高度阶跃以 0.005 s 运行 10 s。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}-2&0&0\\1&0&0\\0&1&0\end{bmatrix},\quad B=\begin{bmatrix}1\\0\\0\end{bmatrix},\quad C=[0\ 0\ 1], ; \det[sI-(A-BK)] =s^3+(2+K_1)s^2+K_2s+K_3. ; (s+12)[(s+2)^2+2^2] =(s+12)(s^2+4s+8) =s^3+16s^2+56s+96. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：无人机三阶对象的主导二阶极点。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 130 题 [Ch7-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用三状态无人机模型、K=[14,56,96]、Nbar=96；单位高度阶跃以 0.005 s 运行 10 s。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}-2&0&0\\1&0&0\\0&1&0\end{bmatrix},\quad B=\begin{bmatrix}1\\0\\0\end{bmatrix},\quad C=[0\ 0\ 1], ; \det[sI-(A-BK)] =s^3+(2+K_1)s^2+K_2s+K_3. ; (s+12)[(s+2)^2+2^2] =(s+12)(s^2+4s+8) =s^3+16s^2+56s+96.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 131. 无人机 LQR 误差—控制权衡

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 131 题 [Ch7-11]。定位：Example 7.23, PDF 1293-1300。

原题保留：无人机 LQR 误差—控制权衡。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：无人机取 Q=100 C^T C、R=1、LQR K=[2.8728,9.8720,10]，并比较 rho=10、100、1000。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}-2&0&0\\1&0&0\\0&1&0\end{bmatrix},\quad B=\begin{bmatrix}1\\0\\0\end{bmatrix},\quad C=[0\ 0\ 1], ; J=\int_0^\infty(\rho y^2+u^2)\,dt,\qquad Q=\rho C^TC,\ R=1, ; A^TP+PA-PBR^{-1}B^TP+Q=0, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：无人机 LQR 误差—控制权衡。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 131 题 [Ch7-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：无人机取 Q=100 C^T C、R=1、LQR K=[2.8728,9.8720,10]，并比较 rho=10、100、1000。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}-2&0&0\\1&0&0\\0&1&0\end{bmatrix},\quad B=\begin{bmatrix}1\\0\\0\end{bmatrix},\quad C=[0\ 0\ 1], ; J=\int_0^\infty(\rho y^2+u^2)\,dt,\qquad Q=\rho C^TC,\ R=1, ; A^TP+PA-PBR^{-1}B^TP+Q=0,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 132. 摆系统全阶状态估计器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 132 题 [Ch7-12]。定位：Example 7.24, PDF 1307-1310。

原题保留：摆系统全阶状态估计器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、全阶估计器 L=[20,99]；对象初态为零而估计初态 [0.2,-0.1]。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}0&1\\-\omega_0^2&0\end{bmatrix},\quad B=\begin{bmatrix}0\\1\end{bmatrix},\quad C=[1\ 0],\quad y=Cx. ; \dot{\hat x}=A\hat x+Bu+L(y-C\hat x), ; \dot{\tilde x}=(A-LC)\tilde x. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：摆系统全阶状态估计器。本次仅做外部软件模型的适配子任务：使 measured_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 132 题 [Ch7-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["measured_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["known_pivot_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 来源模型先验：角度可测；角速度由估计器产生，不是第二个实测传感器.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、全阶估计器 L=[20,99]；对象初态为零而估计初态 [0.2,-0.1]。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}0&1\\-\omega_0^2&0\end{bmatrix},\quad B=\begin{bmatrix}0\\1\end{bmatrix},\quad C=[1\ 0],\quad y=Cx. ; \dot{\hat x}=A\hat x+Bu+L(y-C\hat x), ; \dot{\tilde x}=(A-LC)\tilde x.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 133. 不微分测量的降阶摆估计器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 133 题 [Ch7-13]。定位：Example 7.25, PDF 1321-1325。

原题保留：不微分测量的降阶摆估计器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、降阶观测器增益 L=10；由测得角度估计角速度，不做数值微分。 来源模型方程（按原变量定义，仅作数学背景）：\dot y=x_2,\qquad \dot x_2=-\omega_0^2y+u. ; \dot{\hat x}_2=-\omega_0^2y+u+L(\dot y-\hat x_2). ; L=10\omega_0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：不微分测量的降阶摆估计器。本次仅做外部软件模型的适配子任务：使 measured_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 133 题 [Ch7-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["measured_angle", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["known_pivot_torque"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 来源模型先验：降阶观测器使用实测角度和一个内部估计速度状态，不能把估计状态宣称为测量.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、降阶观测器增益 L=10；由测得角度估计角速度，不做数值微分。 来源模型方程（按原变量定义，仅作数学背景）：\dot y=x_2,\qquad \dot x_2=-\omega_0^2y+u. ; \dot{\hat x}_2=-\omega_0^2y+u+L(\dot y-\hat x_2). ; L=10\omega_0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 134. 由对称根轨迹选择估计器极点

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 134 题 [Ch7-14]。定位：Example 7.26, PDF 1330-1332。

原题保留：由对称根轨迹选择估计器极点。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、噪声比 q=365、估计器极点 -3±j3.18；用相同随机种子比较 q/10、q、10q。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\-\omega_0^2&0\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}w,\qquad y=[1\ 0]x+\nu, ; G_e(s)=C(sI-A)^{-1}B_1=\frac1{s^2+\omega_0^2}. ; 1+qG_e(-s)G_e(s)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由对称根轨迹选择估计器极点。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 134 题 [Ch7-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、噪声比 q=365、估计器极点 -3±j3.18；用相同随机种子比较 q/10、q、10q。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\-\omega_0^2&0\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}w,\qquad y=[1\ 0]x+\nu, ; G_e(s)=C(sI-A)^{-1}B_1=\frac1{s^2+\omega_0^2}. ; 1+qG_e(-s)G_e(s)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 135. 分离原理与直流伺服动态补偿器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 135 题 [Ch7-15]。定位：Example 7.29, PDF 1349-1353。

原题保留：分离原理与直流伺服动态补偿器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取伺服 G=10/[s(s+2)(s+8)]、K=[-46.4,5.76,-0.65]、L=[0.56,1.42,16]；仅在可停止仿真中扫描环路增益。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{10}{s(s+2)(s+8)} ; A=\begin{bmatrix}-10&1&0\\-16&0&1\\0&0&0\end{bmatrix},\ B=\begin{bmatrix}0\\0\\10\end{bmatrix},\ C=[1\ 0\ 0]. ; p_c=-1.42,\quad -1.04\pm j2.14; 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：分离原理与直流伺服动态补偿器。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 135 题 [Ch7-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取伺服 G=10/[s(s+2)(s+8)]、K=[-46.4,5.76,-0.65]、L=[0.56,1.42,16]；仅在可停止仿真中扫描环路增益。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{10}{s(s+2)(s+8)} ; A=\begin{bmatrix}-10&1&0\\-16&0&1\\0&0&0\end{bmatrix},\ B=\begin{bmatrix}0\\0\\10\end{bmatrix},\ C=[1\ 0\ 0]. ; p_c=-1.42,\quad -1.04\pm j2.14;
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 136. 用零点配置提高伺服速度常数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 136 题 [Ch7-16]。定位：Example 7.33, PDF 1378-1385。

原题保留：用零点配置提高伺服速度常数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)]、K=[8,3]、估计器极点 -0.1、控制器零点 -0.096，并用单位斜坡核对 Kv=10。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)},\quad A=\begin{bmatrix}0&1\\0&-1\end{bmatrix},\ B=\begin{bmatrix}0\\1\end{bmatrix},\ C=[1\ 0]. ; \det[sI-(A-BK)]=s^2+4s+8, ; \frac1{K_v}=\sum_i\frac1{z_i}-\sum_i\frac1{p_i}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用零点配置提高伺服速度常数。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 136 题 [Ch7-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0.0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0.0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.1 附近，误差不超过 0.08"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0.0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)]、K=[8,3]、估计器极点 -0.1、控制器零点 -0.096，并用单位斜坡核对 Kv=10。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)},\quad A=\begin{bmatrix}0&1\\0&-1\end{bmatrix},\ B=\begin{bmatrix}0\\1\end{bmatrix},\ C=[1\ 0]. ; \det[sI-(A-BK)]=s^2+4s+8, ; \frac1{K_v}=\sum_i\frac1{z_i}-\sum_i\frac1{p_i}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 137. 电机速度的积分状态反馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 137 题 [Ch7-17]。定位：Example 7.34, PDF 1394-1397。

原题保留：电机速度的积分状态反馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取电机 xdot=-3x+u+w、积分状态 xI_dot=y-r、增益 [25,7]、观测器 L=7；参考与常值负载分开测试。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=-3x+u+w,\qquad y=x, ; \dot x_I=y-r, ; \begin{bmatrix}\dot x_I\\\dot x\end{bmatrix} = \begin{bmatrix}0&1\\0&-3\end{bmatrix} \begin{bmatrix}x_I\\x\end{bmatrix} +\begin{bmatrix}0\\1\end{bmatrix}(u+w) -\begin{bmatrix}1\\0\end{bmatrix}r. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：电机速度的积分状态反馈。本次仅做外部软件模型的适配子任务：使 motor_speed 保持在 0.0264 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 137 题 [Ch7-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["motor_speed", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["motor_voltage"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0264` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.584` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.32` |
| 输出上限 | `output_max` | `1.32` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0528` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取电机 xdot=-3x+u+w、积分状态 xI_dot=y-r、增益 [25,7]、观测器 L=7；参考与常值负载分开测试。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=-3x+u+w,\qquad y=x, ; \dot x_I=y-r, ; \begin{bmatrix}\dot x_I\\\dot x\end{bmatrix} = \begin{bmatrix}0&1\\0&-3\end{bmatrix} \begin{bmatrix}x_I\\x\end{bmatrix} +\begin{bmatrix}0\\1\end{bmatrix}(u+w) -\begin{bmatrix}1\\0\end{bmatrix}r.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 138. 磁盘驱动器的正弦内模控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 138 题 [Ch7-18]。定位：Example 7.35, PDF 1404-1420。

原题保留：磁盘驱动器的正弦内模控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、增益向量 [2.0718,16.3923,13.9282,4.4641]；跟踪并抑制 0.9、1.0、1.1 rad/s 正弦。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\0&-1\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}u,\qquad y=[1\ 0]x, ; A_s=\begin{bmatrix} 0&1&0&0\\-\omega_0^2&0&1&0\\ 0&0&0&1\\0&0&0&-1 \end{bmatrix},\qquad B_s=\begin{bmatrix}0\\0\\0\\1\end{bmatrix}. ; s^4+(1+K_{02})s^3+(\omega_0^2+K_{01})s^2 +[K_1+\omega_0^2(1+K_{02})]s +(K_2+\omega_0^2K_{01}). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：磁盘驱动器的正弦内模控制。本次仅做外部软件模型的适配子任务：使 disk_head_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 138 题 [Ch7-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["disk_head_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["voice_coil_force"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 omega0=1、增益向量 [2.0718,16.3923,13.9282,4.4641]；跟踪并抑制 0.9、1.0、1.1 rad/s 正弦。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=\begin{bmatrix}0&1\\0&-1\end{bmatrix}x+ \begin{bmatrix}0\\1\end{bmatrix}u,\qquad y=[1\ 0]x, ; A_s=\begin{bmatrix} 0&1&0&0\\-\omega_0^2&0&1&0\\ 0&0&0&1\\0&0&0&-1 \end{bmatrix},\qquad B_s=\begin{bmatrix}0\\0\\0\\1\end{bmatrix}. ; s^4+(1+K_{02})s^3+(\omega_0^2+K_{01})s^2 +[K_1+\omega_0^2(1+K_{02})]s +(K_2+\omega_0^2K_{01}).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 139. 卫星 LTR 环路恢复与噪声权衡

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 139 题 [Ch7-19]。定位：Example 7.39, PDF 1448-1457。

原题保留：卫星 LTR 环路恢复与噪声权衡。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取卫星 LQR K=[1,1.414] 与 q=1、10、100 的 LTR 估计器；注入相同单位传感噪声并记录控制 RMS。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}0&1\\0&0\end{bmatrix},\quad B=\begin{bmatrix}0\\1\end{bmatrix},\quad C=[1\ 0]. ; K=[1,\sqrt2]\approx[1,1.414], ; L_{\rm LQR}=K(sI-A)^{-1}B =\frac{1+\sqrt2s}{s^2} =\frac{1.414(s+0.707)}{s^2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：卫星 LTR 环路恢复与噪声权衡。本次仅做外部软件模型的适配子任务：使 attitude_response 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 139 题 [Ch7-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["attitude_response", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque_under_prescribed_sensor_noise"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取卫星 LQR K=[1,1.414] 与 q=1、10、100 的 LTR 估计器；注入相同单位传感噪声并记录控制 RMS。 来源模型方程（按原变量定义，仅作数学背景）：A=\begin{bmatrix}0&1\\0&0\end{bmatrix},\quad B=\begin{bmatrix}0\\1\end{bmatrix},\quad C=[1\ 0]. ; K=[1,\sqrt2]\approx[1,1.414], ; L_{\rm LQR}=K(sI-A)^{-1}B =\frac{1+\sqrt2s}{s^2} =\frac{1.414(s+0.707)}{s^2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 140. Smith 预估器控制纯迟延换热器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 140 题 [Ch7-20]。定位：Example 7.42, PDF 1471-1477。

原题保留：Smith 预估器控制纯迟延换热器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G0=1/[(10s+1)(60s+1)]、迟延 5 s、K=[5.2,-0.17]、L=[0.18,4.2]、Nbar=1.2055；并把迟延扰动到 4.5、5.5 s。 来源模型方程（按原变量定义，仅作数学背景）：P(s)=G_0(s)e^{-5s},\qquad G_0(s)=\frac1{(10s+1)(60s+1)}. ; A=\begin{bmatrix}-0.017&0.017\\0&-0.1\end{bmatrix},\ B=\begin{bmatrix}0\\0.1\end{bmatrix},\ C=[1\ 0], ; K=[5.2,-0.17],\qquad L=[0.18,4.2]^T. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Smith 预估器控制纯迟延换热器。本次仅做外部软件模型的适配子任务：使 delayed_heat_exchanger_temperature 保持在 0.0263596 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 140 题 [Ch7-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["delayed_heat_exchanger_temperature", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["steam_command_through_Smith_predictor"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0263596` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.581576` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.31798` |
| 输出上限 | `output_max` | `1.31798` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0527192` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：来源名义换热迟延显式为 5 s；Smith 补偿不移除物理迟延或其不确定性.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G0=1/[(10s+1)(60s+1)]、迟延 5 s、K=[5.2,-0.17]、L=[0.18,4.2]、Nbar=1.2055；并把迟延扰动到 4.5、5.5 s。 来源模型方程（按原变量定义，仅作数学背景）：P(s)=G_0(s)e^{-5s},\qquad G_0(s)=\frac1{(10s+1)(60s+1)}. ; A=\begin{bmatrix}-0.017&0.017\\0&-0.1\end{bmatrix},\ B=\begin{bmatrix}0\\0.1\end{bmatrix},\ C=[1\ 0], ; K=[5.2,-0.17],\qquad L=[0.18,4.2]^T.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 141. 用 Tustin 法数字化电机超前器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 141 题 [Ch8-01]。定位：Example 8.1, PDF 1582-1586。

原题保留：用 Tustin 法数字化电机超前器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：连续 lead 为 10(0.5s+1)/(0.1s+1)，T=0.025 s；Tustin 递推 u[k]=0.7778u[k-1]+45.56e[k]-43.33e[k-1]。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=10\frac{s/2+1}{s/10+1} =10\frac{0.5s+1}{0.1s+1}. ; s=\frac2T\frac{1-z^{-1}}{1+z^{-1}} =80\frac{1-z^{-1}}{1+z^{-1}}. ; 0.5s+1=\frac{41-39z^{-1}}{1+z^{-1}},\qquad 0.1s+1=\frac{9-7z^{-1}}{1+z^{-1}}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用 Tustin 法数字化电机超前器。本次仅做外部软件模型的适配子任务：使 sampled_motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 141 题 [Ch8-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["sampled_motor_position", "normalized_control"]]` |
| 输入行 [名称] | `inputs` | `[["digital_motor_voltage"]]` |
| 输入单位 | `input_unit` | `"normalized_error"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：连续 lead 为 10(0.5s+1)/(0.1s+1)，T=0.025 s；Tustin 递推 u[k]=0.7778u[k-1]+45.56e[k]-43.33e[k-1]。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=10\frac{s/2+1}{s/10+1} =10\frac{0.5s+1}{0.1s+1}. ; s=\frac2T\frac{1-z^{-1}}{1+z^{-1}} =80\frac{1-z^{-1}}{1+z^{-1}}. ; 0.5s+1=\frac{41-39z^{-1}}{1+z^{-1}},\qquad 0.1s+1=\frac{9-7z^{-1}}{1+z^{-1}}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 142. 用 ZOH 法数字化同一超前器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 142 题 [Ch8-02]。定位：Example 8.2, PDF 1589-1592。

原题保留：用 ZOH 法数字化同一超前器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：同一连续 lead 与 T=0.025 s 采用 ZOH 递推 u[k]=0.7788u[k-1]+50e[k]-47.79e[k-1]。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=10\frac{0.5s+1}{0.1s+1},\qquad T=0.025\ {\rm s}. ; D_d(z)=(1-z^{-1})\mathcal Z\!\left\{\frac{D_c(s)}s\right\}. ; p_d=e^{-10T}=e^{-0.25}=0.7788. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用 ZOH 法数字化同一超前器。本次仅做外部软件模型的适配子任务：使 sampled_motor_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 142 题 [Ch8-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["sampled_motor_position", "normalized_control"]]` |
| 输入行 [名称] | `inputs` | `[["held_motor_voltage"]]` |
| 输入单位 | `input_unit` | `"normalized_error"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：同一连续 lead 与 T=0.025 s 采用 ZOH 递推 u[k]=0.7788u[k-1]+50e[k]-47.79e[k-1]。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=10\frac{0.5s+1}{0.1s+1},\qquad T=0.025\ {\rm s}. ; D_d(z)=(1-z^{-1})\mathcal Z\!\left\{\frac{D_c(s)}s\right\}. ; p_d=e^{-10T}=e^{-0.25}=0.7788.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 143. 空间站姿态的匹配极零数字控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 143 题 [Ch8-03]。定位：Example 8.3, PDF 1595-1602。

原题保留：空间站姿态的匹配极零数字控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：空间站 G=1/s^2、连续 lead 0.81(s+0.2)/(s+2)；MPZ 在 T=1 s 为 0.389(z-0.82)/(z-0.135)，再以 T=0.5 s 重算。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s^2}, ; D_c(s)=0.81\frac{s+0.2}{s+2}, ; z_0=e^{-0.2}=0.8187\approx0.82,\qquad p_0=e^{-2}=0.1353\approx0.135. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：空间站姿态的匹配极零数字控制。本次仅做外部软件模型的适配子任务：使 space_station_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 143 题 [Ch8-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["space_station_attitude", "normalized_torque"]]` |
| 输入行 [名称] | `inputs` | `[["digital_body_torque"]]` |
| 输入单位 | `input_unit` | `"rad"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：空间站 G=1/s^2、连续 lead 0.81(s+0.2)/(s+2)；MPZ 在 T=1 s 为 0.389(z-0.82)/(z-0.135)，再以 T=0.5 s 重算。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s^2}, ; D_c(s)=0.81\frac{s+0.2}{s+2}, ; z_0=e^{-0.2}=0.8187\approx0.82,\qquad p_0=e^{-2}=0.1353\approx0.135.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 144. 一阶对象连续与离散根轨迹比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 144 题 [Ch8-04]。定位：Example 8.4, PDF 1627-1629。

原题保留：一阶对象连续与离散根轨迹比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 a=1 s^-1、T=0.1 s、alpha=exp(-0.1)，让比例 K 穿过精确采样稳定上界。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{a}{s+a},\qquad a>0, ; G_d(z)=(1-z^{-1})\mathcal Z\!\left\{\frac{G(s)}s\right\} =\frac{1-\alpha}{z-\alpha}. ; 1+KG_d=0 \quad\Longrightarrow\quad z=\alpha-K(1-\alpha). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：一阶对象连续与离散根轨迹比较。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 144 题 [Ch8-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 a=1 s^-1、T=0.1 s、alpha=exp(-0.1)，让比例 K 穿过精确采样稳定上界。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{a}{s+a},\qquad a>0, ; G_d(z)=(1-z^{-1})\mathcal Z\!\left\{\frac{G(s)}s\right\} =\frac{1-\alpha}{z-\alpha}. ; 1+KG_d=0 \quad\Longrightarrow\quad z=\alpha-K(1-\alpha).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 145. 空间站姿态的直接 z 平面设计

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 145 题 [Ch8-05]。定位：Example 8.5, PDF 1632-1638。

原题保留：空间站姿态的直接 z 平面设计。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：T=1 s 时用精确 ZOH 对象 Gd=0.5(z+1)/(z-1)^2 与直接控制器 0.374(z-0.85)/z。 来源模型方程（按原变量定义，仅作数学背景）：G_d(z)=\frac{T^2}{2}\frac{z+1}{(z-1)^2} =\frac12\frac{z+1}{(z-1)^2}. ; z_d=0.78\pm j0.18. ; \angle\!\left[\frac{(z_d-\alpha)(z_d+1)} {z_d(z_d-1)^2}\right]=(2\ell+1)\pi 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：空间站姿态的直接 z 平面设计。本次仅做外部软件模型的适配子任务：使 space_station_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 145 题 [Ch8-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["space_station_attitude", "normalized_torque"]]` |
| 输入行 [名称] | `inputs` | `[["digital_body_torque"]]` |
| 输入单位 | `input_unit` | `"rad"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：T=1 s 时用精确 ZOH 对象 Gd=0.5(z+1)/(z-1)^2 与直接控制器 0.374(z-0.85)/z。 来源模型方程（按原变量定义，仅作数学背景）：G_d(z)=\frac{T^2}{2}\frac{z+1}{(z-1)^2} =\frac12\frac{z+1}{(z-1)^2}. ; z_d=0.78\pm j0.18. ; \angle\!\left[\frac{(z_d-\alpha)(z_d+1)} {z_d(z_d-1)^2}\right]=(2\ell+1)\pi
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 146. 连续、仿真等效与直接离散响应比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 146 题 [Ch8-06]。定位：Example 8.6, PDF 1638-1642。

原题保留：连续、仿真等效与直接离散响应比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在 T=1 s 的同一精确 ZOH 对象上比较连续 lead、MPZ 0.389(z-0.82)/(z-0.135) 与直接 0.374(z-0.85)/z。 来源模型方程（按原变量定义，仅作数学背景）：D_{e}(z)=0.389\frac{z-0.82}{z-0.135}, ; D_{z}(z)=0.374\frac{z-0.85}{z}. ; T_i(z)=\frac{D_i(z)G_d(z)}{1+D_i(z)G_d(z)}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：连续、仿真等效与直接离散响应比较。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 146 题 [Ch8-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在 T=1 s 的同一精确 ZOH 对象上比较连续 lead、MPZ 0.389(z-0.82)/(z-0.135) 与直接 0.374(z-0.85)/z。 来源模型方程（按原变量定义，仅作数学背景）：D_{e}(z)=0.389\frac{z-0.82}{z-0.135}, ; D_{z}(z)=0.374\frac{z-0.85}{z}. ; T_i(z)=\frac{D_i(z)G_d(z)}{1+D_i(z)G_d(z)}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 147. 由 z 传递函数恢复滤波器差分方程

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 147 题 [Ch8-07]。定位：Problem 8.1, PDF 1651。

原题保留：由 z 传递函数恢复滤波器差分方程。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采样 1 Hz，使用 H(z)=(1+0.5z^-1)/[(1-0.5z^-1)(1+z^-1/3)]，测试冲激、阶跃与交替输入。 来源模型方程（按原变量定义，仅作数学背景）：H(z)=\frac{Y}{U} =\frac{1+\frac12z^{-1}} {(1-\frac12z^{-1})(1+\frac13z^{-1})}. ; (1-\tfrac12z^{-1})(1+\tfrac13z^{-1}) =1-\tfrac16z^{-1}-\tfrac16z^{-2}. ; y[k]=\tfrac16y[k-1]+\tfrac16y[k-2]+u[k]+\tfrac12u[k-1]. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由 z 传递函数恢复滤波器差分方程。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 147 题 [Ch8-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源滤波器极点 0.5、-1/3 位于单位圆内，名义 BIBO 稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采样 1 Hz，使用 H(z)=(1+0.5z^-1)/[(1-0.5z^-1)(1+z^-1/3)]，测试冲激、阶跃与交替输入。 来源模型方程（按原变量定义，仅作数学背景）：H(z)=\frac{Y}{U} =\frac{1+\frac12z^{-1}} {(1-\frac12z^{-1})(1+\frac13z^{-1})}. ; (1-\tfrac12z^{-1})(1+\tfrac13z^{-1}) =1-\tfrac16z^{-1}-\tfrac16z^{-2}. ; y[k]=\tfrac16y[k-1]+\tfrac16y[k-2]+u[k]+\tfrac12u[k-1].
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 148. 用 z 变换求解受迫二阶差分方程

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 148 题 [Ch8-08]。定位：Problem 8.2, PDF 1651。

原题保留：用 z 变换求解受迫二阶差分方程。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 y[k]-3y[k-1]+2y[k-2]=2u[k-1]-2u[k-2]、u[k]=k、负时刻为零，计算 k=0..15。 来源模型方程（按原变量定义，仅作数学背景）：y[k]-3y[k-1]+2y[k-2] =2u[k-1]-2u[k-2], ; u[k]=k\ (k\ge0),\qquad y[k]=u[k]=0\ (k<0). ; (1-3z^{-1}+2z^{-2})Y =(2z^{-1}-2z^{-2})U. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用 z 变换求解受迫二阶差分方程。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 148 题 [Ch8-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源差分方程含 z=2 模态，不稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 y[k]-3y[k-1]+2y[k-2]=2u[k-1]-2u[k-2]、u[k]=k、负时刻为零，计算 k=0..15。 来源模型方程（按原变量定义，仅作数学背景）：y[k]-3y[k-1]+2y[k-2] =2u[k-1]-2u[k-2], ; u[k]=k\ (k\ge0),\qquad y[k]=u[k]=0\ (k<0). ; (1-3z^{-1}+2z^{-2})Y =(2z^{-1}-2z^{-2})U.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 149. 证明 s 到 z 平面的七条映射性质

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 149 题 [Ch8-09]。定位：Problem 8.4, PDF 1652。

原题保留：证明 s 到 z 平面的七条映射性质。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=0.1 s，映射 s=-1±j2 与 s=-1±j(2+2pi/T)，核对相同 z 极点与混叠。 来源模型方程（按原变量定义，仅作数学背景）：z=e^{sT}=e^{\sigma T}e^{j\omega T},\qquad \omega_s=\frac{2\pi}{T}. ; z=e^{sT}\approx1+sT, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：证明 s 到 z 平面的七条映射性质。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 149 题 [Ch8-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=0.1 s，映射 s=-1±j2 与 s=-1±j(2+2pi/T)，核对相同 z 极点与混叠。 来源模型方程（按原变量定义，仅作数学背景）：z=e^{sT}=e^{\sigma T}e^{j\omega T},\qquad \omega_s=\frac{2\pi}{T}. ; z=e^{sT}\approx1+sT,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 150. 二十赫兹下滞后器的匹配极零实现

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 150 题 [Ch8-10]。定位：Problem 8.5, PDF 1653。

原题保留：二十赫兹下滞后器的匹配极零实现。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 lag (0.8s+1)/(50s+1)、fs=20 Hz，MPZ 零点 0.93941、极点 0.99900、增益 0.01650。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=\frac{s/1.25+1}{50s+1} =\frac{0.8s+1}{50s+1}, ; z_0=e^{-1.25T}=e^{-0.0625}=0.93941,\qquad p_0=e^{-0.02T}=e^{-0.001}=0.99900. ; K_d=\frac{1-p_0}{1-z_0}=0.01650. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：二十赫兹下滞后器的匹配极零实现。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 150 题 [Ch8-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 lag (0.8s+1)/(50s+1)、fs=20 Hz，MPZ 零点 0.93941、极点 0.99900、增益 0.01650。 来源模型方程（按原变量定义，仅作数学背景）：D_c(s)=\frac{s/1.25+1}{50s+1} =\frac{0.8s+1}{50s+1}, ; z_0=e^{-1.25T}=e^{-0.0625}=0.93941,\qquad p_0=e^{-0.02T}=e^{-0.001}=0.99900. ; K_d=\frac{1-p_0}{1-z_0}=0.01650.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 151. 超前网络的 Tustin 与 MPZ 比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 151 题 [Ch8-11]。定位：Problem 8.6, PDF 1653-1654。

原题保留：超前网络的 Tustin 与 MPZ 比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：把 H=(s+1)/(s+10.1) 在 T=0.25 s 下用 Tustin 与 MPZ 数字化，并比较 3 rad/s 相位。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{s+1}{s+10.1}, ; H_T(z)=\frac{9z-7}{18.1z+2.1} =0.49724\frac{z-0.77778}{z+0.11602}. ; z_0=e^{-0.25}=0.77880,\qquad p_0=e^{-2.525}=0.08006. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：超前网络的 Tustin 与 MPZ 比较。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 151 题 [Ch8-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：把 H=(s+1)/(s+10.1) 在 T=0.25 s 下用 Tustin 与 MPZ 数字化，并比较 3 rad/s 相位。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{s+1}{s+10.1}, ; H_T(z)=\frac{9z-7}{18.1z+2.1} =0.49724\frac{z-0.77778}{z+0.11602}. ; z_0=e^{-0.25}=0.77880,\qquad p_0=e^{-2.525}=0.08006.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 152. 滞后网络的 Tustin 与 MPZ 比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 152 题 [Ch8-12]。定位：Problem 8.7, PDF 1654。

原题保留：滞后网络的 Tustin 与 MPZ 比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：把 H=(10s+1)/(100s+1) 在 T=0.25 s 下用 Tustin 与 MPZ 数字化，并在 3 rad/s 评价。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{10s+1}{100s+1}, ; H_T(z)=\frac{81z-79}{801z-799} =0.101124\frac{z-0.975309}{z-0.997503}. ; z_0=e^{-0.025}=0.975310,\qquad p_0=e^{-0.0025}=0.997503, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：滞后网络的 Tustin 与 MPZ 比较。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 152 题 [Ch8-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：把 H=(10s+1)/(100s+1) 在 T=0.25 s 下用 Tustin 与 MPZ 数字化，并在 3 rad/s 评价。 来源模型方程（按原变量定义，仅作数学背景）：H(s)=\frac{10s+1}{100s+1}, ; H_T(z)=\frac{81z-79}{801z-799} =0.101124\frac{z-0.975309}{z-0.997503}. ; z_0=e^{-0.025}=0.975310,\qquad p_0=e^{-0.0025}=0.997503,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 153. 不同采样周期下的 PID 数字化

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 153 题 [Ch8-13]。定位：Problem 8.8, PDF 1655。

原题保留：不同采样周期下的 PID 数字化。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)] 与 PID K=15.2、Td=0.3816 s、Ti=0.95 s；在 T=1、0.1、0.01 s 数字化并记录输出与控制。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)}, ; D_c(s)=K\left(1+T_ds+\frac1{T_is}\right). ; s^3+(1+KT_d)s^2+Ks+\frac K{T_i}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：不同采样周期下的 PID 数字化。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 153 题 [Ch8-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)] 与 PID K=15.2、Td=0.3816 s、Ti=0.95 s；在 T=1、0.1、0.01 s 数字化并记录输出与控制。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)}, ; D_c(s)=K\left(1+T_ds+\frac1{T_is}\right). ; s^3+(1+KT_d)s^2+Ks+\frac K{T_i}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 154. 含不稳定模态对象的采样增益稳定区间

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 154 题 [Ch8-14]。定位：Problem 8.9, PDF 1656-1657。

原题保留：含不稳定模态对象的采样增益稳定区间。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 T=1 s 精确 ZOH 模型 Gd=(7.96703z^2+1.33509z-0.324537)/(z^3-3.57119z^2+1.000162z-0.0000454)，扫描 K>0。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{40(s+2)}{(s+10)(s^2-1.4)}, ; G_d(z)=\frac{7.96703z^2+1.33509z-0.324537} {z^3-3.57119z^2+1.000162z-0.0000454}. ; P=z^3+az^2+bz+c,\quad Q=(1-c^2)z^2+(a-cb)z+(b-ca). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：含不稳定模态对象的采样增益稳定区间。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 154 题 [Ch8-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源 T=1 s 采样环路不存在可稳定的正比例增益，不能套用连续稳定区间.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 T=1 s 精确 ZOH 模型 Gd=(7.96703z^2+1.33509z-0.324537)/(z^3-3.57119z^2+1.000162z-0.0000454)，扫描 K>0。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{40(s+2)}{(s+10)(s^2-1.4)}, ; G_d(z)=\frac{7.96703z^2+1.33509z-0.324537} {z^3-3.57119z^2+1.000162z-0.0000454}. ; P=z^3+az^2+bz+c,\quad Q=(1-c^2)z^2+(a-cb)z+(b-ca).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 155. 卫星姿态的离散比例—速度反馈

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 155 题 [Ch8-15]。定位：Problem 8.10, PDF 1657-1660。

原题保留：卫星姿态的离散比例—速度反馈。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=0.1 s 的精确双积分模型，状态反馈 Kp=1.8097、Kv=1.9032，目标 z=exp((-1±j1)T)。 来源模型方程（按原变量定义，仅作数学背景）：\ddot\theta=u+w_d. ; x_{k+1}= \begin{bmatrix}1&T\\0&1\end{bmatrix}x_k+ \begin{bmatrix}T^2/2\\T\end{bmatrix}u_k. ; \operatorname{tr}A_c=2-TK_v-\frac{T^2K_p}{2},\qquad \det A_c=1-TK_v+\frac{T^2K_p}{2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：卫星姿态的离散比例—速度反馈。本次仅做外部软件模型的适配子任务：使 satellite_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 155 题 [Ch8-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["satellite_attitude", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["digital_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=0.1 s 的精确双积分模型，状态反馈 Kp=1.8097、Kv=1.9032，目标 z=exp((-1±j1)T)。 来源模型方程（按原变量定义，仅作数学背景）：\ddot\theta=u+w_d. ; x_{k+1}= \begin{bmatrix}1&T\\0&1\end{bmatrix}x_k+ \begin{bmatrix}T^2/2\\T\end{bmatrix}u_k. ; \operatorname{tr}A_c=2-TK_v-\frac{T^2K_p}{2},\qquad \det A_c=1-TK_v+\frac{T^2K_p}{2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 156. 受传感与电流限制的数字磁悬浮

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 156 题 [Ch8-16]。定位：Problem 8.11, PDF 1660-1663。

原题保留：受传感与电流限制的数字磁悬浮。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=0.02 kg、k1=20 N/m、k2=0.4 N/A、T=0.02 s；状态反馈 Kx=94 A/m、Kv=2.08 A*s/m，从 ±0.25 cm 初值测试并限流 1 A。 来源模型方程（按原变量定义，仅作数学背景）：m\ddot x=k_1x+k_2i, \quad m=0.02\ {\rm kg},\ k_1=20\ {\rm N/m},\ k_2=0.4\ {\rm N/A}. ; \frac XI=\frac{20}{s^2-1000},\quad A=\begin{bmatrix}0&1\\1000&0\end{bmatrix},\ B=\begin{bmatrix}0\\20\end{bmatrix}. ; \Phi=\begin{bmatrix}c&\sinh(aT)/a\\a\sinh(aT)&c\end{bmatrix}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：受传感与电流限制的数字磁悬浮。本次仅做外部软件模型的适配子任务：使 ball_displacement 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 156 题 [Ch8-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["ball_displacement", "m"]]` |
| 输入行 [名称] | `inputs` | `[["electromagnet_current"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-0.25` |
| 输入上限 | `input_max` | `0.25` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=0.02 kg、k1=20 N/m、k2=0.4 N/A、T=0.02 s；状态反馈 Kx=94 A/m、Kv=2.08 A*s/m，从 ±0.25 cm 初值测试并限流 1 A。 来源模型方程（按原变量定义，仅作数学背景）：m\ddot x=k_1x+k_2i, \quad m=0.02\ {\rm kg},\ k_1=20\ {\rm N/m},\ k_2=0.4\ {\rm N/A}. ; \frac XI=\frac{20}{s^2-1000},\quad A=\begin{bmatrix}0&1\\1000&0\end{bmatrix},\ B=\begin{bmatrix}0\\20\end{bmatrix}. ; \Phi=\begin{bmatrix}c&\sinh(aT)/a\\a\sinh(aT)&c\end{bmatrix},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 157. z 平面直接设计超前—滞后伺服

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 157 题 [Ch8-17]。定位：Problem 8.12 and referenced Problem 5.26, PDF 1663 and 834-835。

原题保留：z 平面直接设计超前—滞后伺服。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=10/[s(s+1)(s+10)]、fs=15 Hz 及其精确 ZOH 系数；直接设计满足 Mp≤16%、tr≤0.4 s、Kv_d>1.333。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{10}{s(s+1)(s+10)}, ; G_d(z)= \frac{0.00041424z^2+0.00139060z+0.00028724} {z^3-2.448924z^2+1.929229z-0.480305}. ; s_d=-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2} 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：z 平面直接设计超前—滞后伺服。本次仅做外部软件模型的适配子任务：使 servo_position 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 157 题 [Ch8-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["servo_position", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["digital_servo_voltage"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=10/[s(s+1)(s+10)]、fs=15 Hz 及其精确 ZOH 系数；直接设计满足 Mp≤16%、tr≤0.4 s、Kv_d>1.333。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{10}{s(s+1)(s+10)}, ; G_d(z)= \frac{0.00041424z^2+0.00139060z+0.00028724} {z^3-2.448924z^2+1.929229z-0.480305}. ; s_d=-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2}
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 158. 天线伺服的仿真等效与直接数字设计

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 158 题 [Ch8-18]。定位：Problem 8.13, PDF 1663。

原题保留：天线伺服的仿真等效与直接数字设计。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取天线 J=600000、B=20000、T=10 s；在同一精确 ZOH 对象上比较仿真等效与直接 z 设计。 来源模型方程（按原变量定义，仅作数学背景）：J\ddot\theta+B\dot\theta=T_c,\qquad J=600000,\quad B=20000, ; G(s)=\frac{\Theta}{T_c} =\frac1{600000s^2+20000s} =\frac1{600000s(s+1/30)}. ; \Phi=\begin{bmatrix}1&(1-e^{-aT})/a\\0&e^{-aT}\end{bmatrix}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：天线伺服的仿真等效与直接数字设计。本次仅做外部软件模型的适配子任务：使 antenna_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 158 题 [Ch8-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["antenna_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["digital_motor_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取天线 J=600000、B=20000、T=10 s；在同一精确 ZOH 对象上比较仿真等效与直接 z 设计。 来源模型方程（按原变量定义，仅作数学背景）：J\ddot\theta+B\dot\theta=T_c,\qquad J=600000,\quad B=20000, ; G(s)=\frac{\Theta}{T_c} =\frac1{600000s^2+20000s} =\frac1{600000s(s+1/30)}. ; \Phi=\begin{bmatrix}1&(1-e^{-aT})/a\\0&e^{-aT}\end{bmatrix},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 159. 两实极点对象的直接数字校正

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 159 题 [Ch8-19]。定位：Problem 8.14, PDF 1663-1664。

原题保留：两实极点对象的直接数字校正。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 T=0.1 s 精确 Gd=(0.00451991z+0.00407643)/(z^2-1.73086805z+0.73344696) 与 D=6.1882(z-0.27594)/z。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{(s+0.1)(s+3)},\qquad T=0.1\ {\rm s}, ; G_d(z)=\frac{0.00451991z+0.00407643} {z^2-1.73086805z+0.73344696}. ; z_d=e^{(-1.54\pm j1.571)0.1} \approx0.84671\pm j0.13413. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：两实极点对象的直接数字校正。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 159 题 [Ch8-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 T=0.1 s 精确 Gd=(0.00451991z+0.00407643)/(z^2-1.73086805z+0.73344696) 与 D=6.1882(z-0.27594)/z。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{(s+0.1)(s+3)},\qquad T=0.1\ {\rm s}, ; G_d(z)=\frac{0.00451991z+0.00407643} {z^2-1.73086805z+0.73344696}. ; z_d=e^{(-1.54\pm j1.571)0.1} \approx0.84671\pm j0.13413.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 160. 因果离散微分器的一拍延迟

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 160 题 [Ch8-20]。定位：Problem 8.15, PDF 1664。

原题保留：因果离散微分器的一拍延迟。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=0.1 s、KTd=1，后向差分 u[k]=10(e[k]-e[k-1])；非因果前向差分只作离线比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot e(kT)\approx\frac{e[k]-e[k-1]}T. ; D_d(z)=c(1-z^{-1})=\frac{KT_D(z-1)}{Tz}. ; u[k]=c(e[k]-e[k-1]), 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：因果离散微分器的一拍延迟。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 160 题 [Ch8-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：因果后向差分增加一拍迟延；无预测消除它需要不可用的未来数据.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=0.1 s、KTd=1，后向差分 u[k]=10(e[k]-e[k-1])；非因果前向差分只作离线比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot e(kT)\approx\frac{e[k]-e[k-1]}T. ; D_d(z)=c(1-z^{-1})=\frac{KT_D(z-1)}{Tz}. ; u[k]=c(e[k]-e[k-1]),
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 161. 单摆平衡点与小信号稳定性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 161 题 [Ch9-01]。定位：Example 9.1, PDF 1678-1679。

原题保留：单摆平衡点与小信号稳定性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 g=9.81 m/s^2、l=1 m，在 theta=0 与 pi 两平衡点施加 ±0.05 rad 扰动并运行 10 s。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_1=x_2,\qquad \dot x_2=-\omega_0^2\sin x_1+u,\qquad \omega_0=\sqrt{g/\ell}. ; -\omega_0^2\sin\theta_o+u_o=0. ; A(\theta_o)= \begin{bmatrix}0&1\\-\omega_0^2\cos\theta_o&0\end{bmatrix}, \qquad B=\begin{bmatrix}0\\1\end{bmatrix}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：单摆平衡点与小信号稳定性。本次仅做外部软件模型的适配子任务：使 pendulum_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 161 题 [Ch9-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pendulum_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["pivot_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：下垂平衡为无阻尼中心，倒立平衡不稳定；本次适配为下垂点附近保持.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：摆的正弦恢复力为非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 g=9.81 m/s^2、l=1 m，在 theta=0 与 pi 两平衡点施加 ±0.05 rad 扰动并运行 10 s。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_1=x_2,\qquad \dot x_2=-\omega_0^2\sin x_1+u,\qquad \omega_0=\sqrt{g/\ell}. ; -\omega_0^2\sin\theta_o+u_o=0. ; A(\theta_o)= \begin{bmatrix}0&1\\-\omega_0^2\cos\theta_o&0\end{bmatrix}, \qquad B=\begin{bmatrix}0\\1\end{bmatrix},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 162. 由实验力曲线线性化磁悬浮球

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 162 题 [Ch9-02]。定位：Example 9.2, PDF 1679-1685。

原题保留：由实验力曲线线性化磁悬浮球。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=0.0084 kg、平衡电流 0.6 A、A=[[0,1],[1667,0]]、B=[0,47.6]；在工作点附近测试 ±10 mA。 来源模型方程（按原变量定义，仅作数学背景）：m\ddot x=f_m(x,i)-mg. ; f_m(x_1+\delta x,i_2+\delta i) \approx mg+K_x\delta x+K_i\delta i. ; K_i\approx\frac{122-42}{700-500}\frac{\mathrm{mN}}{\mathrm{mA}} =0.4\,\mathrm{N/A}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由实验力曲线线性化磁悬浮球。本次仅做外部软件模型的适配子任务：使 ball_displacement 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 162 题 [Ch9-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["ball_displacement", "m"]]` |
| 输入行 [名称] | `inputs` | `[["electromagnet_current_perturbation"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-0.01` |
| 输入上限 | `input_max` | `0.01` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.0` |
| 输出上限 | `output_max` | `1.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：A=[[0,1],[1667,0]] 极点 +/-sqrt(1667)，磁悬浮平衡开环不稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：力曲线在 0.6 A 附近局部线性化，有符号输入是电流增量.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=0.0084 kg、平衡电流 0.6 A、A=[[0,1],[1667,0]]、B=[0,47.6]；在工作点附近测试 ±10 mA。 来源模型方程（按原变量定义，仅作数学背景）：m\ddot x=f_m(x,i)-mg. ; f_m(x_1+\delta x,i_2+\delta i) \approx mg+K_x\delta x+K_i\delta i. ; K_i\approx\frac{122-42}{700-500}\frac{\mathrm{mN}}{\mathrm{mA}} =0.4\,\mathrm{N/A}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 163. 平方根出流水箱的工作点线性化

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 163 题 [Ch9-03]。定位：Example 9.3, PDF 1685-1687。

原题保留：平方根出流水箱的工作点线性化。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=1 m^2、rho=1000 kg/m^3、R=0.5、h0=1 m、pa=0；入口质量流量扰动 ±10 kg/s，并保持液位为正。 来源模型方程（按原变量定义，仅作数学背景）：\dot h=f(h,w_{in}) =-\frac{1}{A\rho R}\sqrt{\rho gh-p_a} +\frac{1}{A\rho}w_{in}. ; w_{in,o}=\frac1R\sqrt{\rho gh_o-p_a} =\frac1R\sqrt{p_o-p_a}. ; \left.\frac{\partial f}{\partial h}\right|_o =-\frac{g}{2AR\sqrt{\rho gh_o-p_a}},\qquad \left.\frac{\partial f}{\partial w_{in}}\right|_o =\frac1{A\rho}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：平方根出流水箱的工作点线性化。本次仅做外部软件模型的适配子任务：使 level_deviation 保持在 0.004 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 163 题 [Ch9-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["level_deviation", "m"]]` |
| 输入行 [名称] | `inputs` | `[["inlet_flow_deviation"]]` |
| 输入单位 | `input_unit` | `"kg/s"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.004` |
| 输入下限 | `input_min` | `-10` |
| 输入上限 | `input_max` | `10` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `0.24` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-0.2` |
| 输出上限 | `output_max` | `0.2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.008` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：选定名义动态通道为一阶，相对阶次 1；静态增益或可另加的传输迟延不增加储能状态.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 A=1 m^2、rho=1000 kg/m^3、R=0.5、h0=1 m、pa=0；入口质量流量扰动 ±10 kg/s，并保持液位为正。 来源模型方程（按原变量定义，仅作数学背景）：\dot h=f(h,w_{in}) =-\frac{1}{A\rho R}\sqrt{\rho gh-p_a} +\frac{1}{A\rho}w_{in}. ; w_{in,o}=\frac1R\sqrt{\rho gh_o-p_a} =\frac1R\sqrt{p_o-p_a}. ; \left.\frac{\partial f}{\partial h}\right|_o =-\frac{g}{2AR\sqrt{\rho gh_o-p_a}},\qquad \left.\frac{\partial f}{\partial w_{in}}\right|_o =\frac1{A\rho}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 164. 计算力矩法消除单摆重力非线性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 164 题 [Ch9-04]。定位：Example 9.4, PDF 1687-1689。

原题保留：计算力矩法消除单摆重力非线性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=l=1、g=9.81，计算力矩 Tc=mgl sin(theta)+u，u=-4(theta-r)-4 theta_dot；测试最大 ±1 rad 命令。 来源模型方程（按原变量定义，仅作数学背景）：m\ell^2\ddot\theta+mg\ell\sin\theta=T_c. ; T_c=mg\ell\sin\theta+u. ; m\ell^2\ddot\theta=u,\qquad \frac{\Theta(s)}{U(s)}=\frac1{m\ell^2s^2} 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：计算力矩法消除单摆重力非线性。本次仅做外部软件模型的适配子任务：使 pendulum_angle 保持在 0.024 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 164 题 [Ch9-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pendulum_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["virtual_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.024` |
| 输入下限 | `input_min` | `-4` |
| 输入上限 | `input_max` | `4` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.44` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.2` |
| 输出上限 | `output_max` | `1.2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.048` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：外部计算力矩仅在 m、l、theta 准确且无饱和时抵消重力；CFDC 文字不执行该逆映射.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 m=l=1、g=9.81，计算力矩 Tc=mgl sin(theta)+u，u=-4(theta-r)-4 theta_dot；测试最大 ±1 rad 命令。 来源模型方程（按原变量定义，仅作数学背景）：m\ell^2\ddot\theta+mg\ell\sin\theta=T_c. ; T_c=mg\ell\sin\theta+u. ; m\ell^2\ddot\theta=u,\qquad \frac{\Theta(s)}{U(s)}=\frac1{m\ell^2s^2}
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 165. RTP 灯功率平方律的逆补偿

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 165 题 [Ch9-05]。定位：Example 9.5, PDF 1690-1691。

原题保留：RTP 灯功率平方律的逆补偿。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原灯规律 P=k V^2；新增单位标定 k=1 W/V^2，0<=V<=10 V。本次外部仿真假定功率到温升 G(s)=1 degC/W /(10s+1)，来源中的 G 本来是符号模型。输入选择虚拟功率 u，单位 W、范围 0..100 W；外部映射 V=sqrt(u/k)。不能把电压标为 W，也不能把灯电压作为温升输出。CFDC 不会通过文字执行或授权该映射。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：RTP 灯功率平方律的逆补偿。本次仅做外部软件模型的适配子任务：使 temperature_rise 保持在 20 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 165 题 [Ch9-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 原灯规律 P=k V^2；新增单位标定 k=1 W/V^2，0<=V<=10 V。本次外部仿真假定功率到温升 G(s)=1 degC/W /(10s+1)，来源中的 G 本来是符号模型。输入选择虚拟功率 u，单位 W、范围 0..100 W；外部映射 V=sqrt(u/k)。不能把电压标为 W，也不能把灯电压作为温升输出。CFDC 不会通过文字执行或授权该映射。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["temperature_rise", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["virtual_power_command"]]` |
| 输入单位 | `input_unit` | `"W"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `20` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `100` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `120.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `100` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `1` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `10` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
第 1–7 项仅对给定适配名义数学模型及主要输入输出已知，第 8 项未知。这些是模型先验，不是硬件观测或协议绑定记录；真实传感器、标定和执行器仍未验证.
1. open_loop_stability: stable（稳定）：明确补充的热模型极点为 -0.1.
2. nonminimum_phase: minimum-phase（最小相位）：补充的虚拟功率到温度模型无有限零点.
3. significant_delay: not_significant（无显著迟延）：补充的名义模型假设无纯迟延.
4. relative_degree: low（低）：虚拟功率到主要温升通道相对阶次为 1.
5. sensing_actuation_adequacy: adequate（对补充的名义模型充分）：单一温度状态被测量，并受虚拟功率控制；这是实现的数学性质，不是对真实逆映射标定的验证；约束下的局部控制仅限正功率区间内部的升温/保持工作点，不保证零输入边界的任意双向控制或全域约束可达性.
6. nonlinearity_strength: weak（弱）：适配后的虚拟功率到温度模型在给定正分支上为线性模型；原电压平方律不属于当前输入定义.
7. coupling_underactuation: siso：一个虚拟功率输入和一个主要温升输出；电压、功率遥测仅为辅助观测.
8. uncertainty_variation: 未知，未复测灯规律和热参数.
新增仿真假设，非实测：G(s)=1 degC/W /(10s+1)、k=1 W/V^2、外部映射 V=sqrt(u/k)；CFDC 不执行该映射。
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 166. 执行器饱和导致的幅值相关超调

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 166 题 [Ch9-06]。定位：Example 9.6, PDF 1696-1699。

原题保留：执行器饱和导致的幅值相关超调。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=(s+1)/s^2、K=1、执行器对称限幅 ±0.4，阶跃幅值为 2、4、6、8、10、12。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{s+1}{s^2}, ; 1+K\frac{s+1}{s^2}=0 \quad\Longrightarrow\quad s^2+Ks+K=0. ; \omega_n=\sqrt K,\qquad \zeta=\frac{\sqrt K}{2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：执行器饱和导致的幅值相关超调。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 166 题 [Ch9-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：执行器硬饱和是无记忆静态非线性，动态响应仍由外部对象决定.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=(s+1)/s^2、K=1、执行器对称限幅 ±0.4，阶跃幅值为 2、4、6、8、10、12。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{s+1}{s^2}, ; 1+K\frac{s+1}{s^2}=0 \quad\Longrightarrow\quad s^2+Ks+K=0. ; \omega_n=\sqrt K,\qquad \zeta=\frac{\sqrt K}{2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 167. 条件稳定环路的饱和大信号失稳

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 167 题 [Ch9-07]。定位：Example 9.7, PDF 1700-1703。

原题保留：条件稳定环路的饱和大信号失稳。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=(s+1)^2/s^3、K=2、饱和限幅 ±1，阶跃 1、2、3、3.5；状态越界立即停止。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{(s+1)^2}{s^3}, ; s^3+K(s+1)^2 =s^3+Ks^2+2Ks+K=0. ; 1,\quad K,\quad 2K-1,\quad K. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：条件稳定环路的饱和大信号失稳。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 167 题 [Ch9-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源环路为条件稳定，饱和可能把等效增益降至稳定阈值以下.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：执行器饱和使等效环路增益随幅值变化.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=(s+1)^2/s^3、K=2、饱和限幅 ±1，阶跃 1、2、3、3.5；状态越界立即停止。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{(s+1)^2}{s^3}, ; s^3+K(s+1)^2 =s^3+Ks^2+2Ks+K=0. ; 1,\quad K,\quad 2K-1,\quad K.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 168. 柔性模态的饱和极限环与陷波消除

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 168 题 [Ch9-08]。定位：Example 9.8, PDF 1704-1712。

原题保留：柔性模态的饱和极限环与陷波消除。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s^2+0.2s+1)]、K=0.5、饱和 ±0.1；比较加入陷波 123(s^2+0.18s+0.81)/(s+10)^2 前后。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s^2+0.2s+1)}, ; s(s^2+0.2s+1)+K_e =s^3+0.2s^2+s+K_e. ; 1,\quad0.2,\quad\frac{0.2-K_e}{0.2},\quad K_e. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：柔性模态的饱和极限环与陷波消除。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 168 题 [Ch9-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：饱和可能产生自限振荡，描述函数近似不是精确非线性证据.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s^2+0.2s+1)]、K=0.5、饱和 ±0.1；比较加入陷波 123(s^2+0.18s+0.81)/(s+10)^2 前后。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s^2+0.2s+1)}, ; s(s^2+0.2s+1)+K_e =s^3+0.2s^2+s+K_e. ; 1,\quad0.2,\quad\frac{0.2-K_e}{0.2},\quad K_e.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 169. 饱和 PI 积分器的回算反饱和

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 169 题 [Ch9-09]。定位：Example 9.9, PDF 1719-1726。

原题保留：饱和 PI 积分器的回算反饱和。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取对象 1/s、PI kp=2、ki=4、执行器 ±1、回算 Ka=10；4 单位阶跃与 Ka=0 比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_I=k_i e=4e,\qquad v=2e+x_I. ; \dot x_I=4e+K_a(u-v) =4e+10(u-2e-x_I). ; x_I\approx u-2e+\frac{4}{10}e=u-1.6e. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：饱和 PI 积分器的回算反饱和。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 169 题 [Ch9-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：PI 积分器有动态记忆，执行器饱和和回算改变状态演化.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取对象 1/s、PI kp=2、ki=4、执行器 ±1、回算 Ka=10；4 单位阶跃与 Ka=0 比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_I=k_i e=4e,\qquad v=2e+x_I. ; \dot x_I=4e+K_a(u-v) =4e+10(u-2e-x_I). ; x_I\approx u-2e+\frac{4}{10}e=u-1.6e.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 170. 饱和非线性的描述函数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 170 题 [Ch9-10]。定位：Example 9.10, PDF 1731-1735。

原题保留：饱和非线性的描述函数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取饱和斜率 k=1、限幅 N=0.1，1 rad/s 正弦幅值为 0.05、0.1、0.2、0.5、1，并提取基波。 来源模型方程（按原变量定义，仅作数学背景）：y= \begin{cases} kx,&|kx|\le N,\\ N\,\operatorname{sgn}x,&|kx|>N. \end{cases} ; \theta_s=\sin^{-1}\frac{N}{ka}. ; b_1=\frac4\pi\left[ \int_0^{\theta_s}ka\sin^2\theta\,d\theta+ \int_{\theta_s}^{\pi/2}N\sin\theta\,d\theta \right]. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：饱和非线性的描述函数。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 170 题 [Ch9-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：饱和描述函数为实数并依赖幅值，仅描述基波.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取饱和斜率 k=1、限幅 N=0.1，1 rad/s 正弦幅值为 0.05、0.1、0.2、0.5、1，并提取基波。 来源模型方程（按原变量定义，仅作数学背景）：y= \begin{cases} kx,&|kx|\le N,\\ N\,\operatorname{sgn}x,&|kx|>N. \end{cases} ; \theta_s=\sin^{-1}\frac{N}{ka}. ; b_1=\frac4\pi\left[ \int_0^{\theta_s}ka\sin^2\theta\,d\theta+ \int_{\theta_s}^{\pi/2}N\sin\theta\,d\theta \right].
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 171. 理想继电器的描述函数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 171 题 [Ch9-11]。定位：Example 9.11, PDF 1734-1736。

原题保留：理想继电器的描述函数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取理想继电器输出 ±1，正弦幅值 0.25、0.5、1、2；提取基波及奇次谐波。 来源模型方程（按原变量定义，仅作数学背景）：y(t)=N\,\operatorname{sgn}x(t),\qquad x(t)=a\sin\omega t,\quad a>0. ; b_1=\frac1\pi\int_{-\pi}^{\pi}y(\theta)\sin\theta\,d\theta =\frac2\pi\int_0^\pi N\sin\theta\,d\theta =\frac{4N}{\pi}. ; K_{eq}(a)=\frac{b_1}{a} =\frac{4N}{\pi a}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：理想继电器的描述函数。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 171 题 [Ch9-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：理想继电器不连续、无记忆；基波增益为 4N/(pi a).
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取理想继电器输出 ±1，正弦幅值 0.25、0.5、1、2；提取基波及奇次谐波。 来源模型方程（按原变量定义，仅作数学背景）：y(t)=N\,\operatorname{sgn}x(t),\qquad x(t)=a\sin\omega t,\quad a>0. ; b_1=\frac1\pi\int_{-\pi}^{\pi}y(\theta)\sin\theta\,d\theta =\frac2\pi\int_0^\pi N\sin\theta\,d\theta =\frac{4N}{\pi}. ; K_{eq}(a)=\frac{b_1}{a} =\frac{4N}{\pi a}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 172. 带滞环继电器的复描述函数

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 172 题 [Ch9-12]。定位：Example 9.12, PDF 1738-1742。

原题保留：带滞环继电器的复描述函数。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取继电器输出 ±1、滞环半宽 h=0.1，正弦幅值 0.08、0.12、0.24、0.5；保留继电器记忆。 来源模型方程（按原变量定义，仅作数学背景）：\phi=\sin^{-1}\frac{h}{a}. ; y_1(t)=\frac{4N}{\pi}\sin(\omega t-\phi). ; K_{eq}(a)=\frac{4N}{\pi a}e^{-j\phi}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：带滞环继电器的复描述函数。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 172 题 [Ch9-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：滞环继电器有记忆；幅值<=h 时周期依赖初始继电状态.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取继电器输出 ±1、滞环半宽 h=0.1，正弦幅值 0.08、0.12、0.24、0.5；保留继电器记忆。 来源模型方程（按原变量定义，仅作数学背景）：\phi=\sin^{-1}\frac{h}{a}. ; y_1(t)=\frac{4N}{\pi}\sin(\omega t-\phi). ; K_{eq}(a)=\frac{4N}{\pi a}e^{-j\phi}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 173. 用 Nyquist 与描述函数预测饱和极限环

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 173 题 [Ch9-13]。定位：Example 9.13, PDF 1744-1747。

原题保留：用 Nyquist 与描述函数预测饱和极限环。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s^2+0.2s+1)] 与饱和 k=1、N=0.1；从幅值 0.3、0.63、0.9 附近启动并测稳态振荡。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s^2+0.2s+1)}. ; 1+K_{eq}(a)G(j\omega)=0 \quad\Longleftrightarrow\quad G(j\omega)=-\frac1{K_{eq}(a)}. ; G(j)=\frac1{j[\,j^2+0.2j+1\,]} =\frac1{j(0.2j)} =-5. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用 Nyquist 与描述函数预测饱和极限环。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 173 题 [Ch9-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：饱和加动态环路可产生极限环；来源给的是幅值预测，不是实测.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s^2+0.2s+1)] 与饱和 k=1、N=0.1；从幅值 0.3、0.63、0.9 附近启动并测稳态振荡。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s^2+0.2s+1)}. ; 1+K_{eq}(a)G(j\omega)=0 \quad\Longleftrightarrow\quad G(j\omega)=-\frac1{K_{eq}(a)}. ; G(j)=\frac1{j[\,j^2+0.2j+1\,]} =\frac1{j(0.2j)} =-5.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 174. 用复描述函数预测滞环极限环

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 174 题 [Ch9-14]。定位：Example 9.14, PDF 1747-1751。

原题保留：用复描述函数预测滞环极限环。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)]、继电器 N=1、h=0.1；从多个继电器初始状态仿真并测量极限环。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)} ; K_{eq}=\frac{4N}{\pi a} \left[\frac{\sqrt{a^2-h^2}}a-j\frac ha\right] ; -\frac1{K_{eq}(a)} =-\frac{\pi}{4N}\left[\sqrt{a^2-h^2}+jh\right]. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用复描述函数预测滞环极限环。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 174 题 [Ch9-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：继电滞环保留离散状态；来源极限环预测要求完整跨越阈值.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 G=1/[s(s+1)]、继电器 N=1、h=0.1；从多个继电器初始状态仿真并测量极限环。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac1{s(s+1)} ; K_{eq}=\frac{4N}{\pi a} \left[\frac{\sqrt{a^2-h^2}}a-j\frac ha\right] ; -\frac1{K_{eq}(a)} =-\frac{\pi}{4N}\left[\sqrt{a^2-h^2}+jh\right].
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 175. 双积分器最短时间开关与 PTOS

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 175 题 [Ch9-15]。定位：Section 9.5.1, PDF 1761-1768。

原题保留：双积分器最短时间开关与 PTOS。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取双积分器、|u|≤1，初态 (1,0)、(1,-1)、(-1,1)；比较 bang-bang 切换与带平滑区的 PTOS。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_1=x_2,\qquad \dot x_2=u,\qquad |u|\le1. ; \frac{dx_2}{dx_1}=\frac{u}{x_2} \quad\Longrightarrow\quad x_2\,dx_2=u\,dx_1. ; s(x)=x_1+\frac12x_2|x_2|=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：双积分器最短时间开关与 PTOS。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 175 题 [Ch9-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0.0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0.0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.1 附近，误差不超过 0.08"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0.0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 来源模型先验：声明的单滞后/积分核心无有限右半平面零点；传输迟延、传感器与新增控制器需另行考虑.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 来源模型先验：底层力矩/力到角度/位置通道为双积分器，相对阶次 2；控制器状态另计.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：有界 bang-bang 切换不连续；PTOS 加平滑假设，是不同控制器.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取双积分器、|u|≤1，初态 (1,0)、(1,-1)、(-1,1)；比较 bang-bang 切换与带平滑区的 PTOS。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_1=x_2,\qquad \dot x_2=u,\qquad |u|\le1. ; \frac{dx_2}{dx_1}=\frac{u}{x_2} \quad\Longrightarrow\quad x_2\,dx_2=u\,dx_1. ; s(x)=x_1+\frac12x_2|x_2|=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 176. Lyapunov 方程证明参数化二阶稳定性

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 176 题 [Ch9-16]。定位：Example 9.15, PDF 1775-1776。

原题保留：Lyapunov 方程证明参数化二阶稳定性。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 alpha=1、beta=2、A=[[-1,2],[-2,-1]]、Q=I，并从半径 0.5、1、2 的初态运行。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=Ax,\qquad A=\begin{bmatrix}-\alpha&\beta\\-\beta&-\alpha\end{bmatrix}, ; -2\alpha p-2\beta q=-1, ; \beta p-2\alpha q-\beta r=0, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：Lyapunov 方程证明参数化二阶稳定性。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 176 题 [Ch9-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：alpha=1、beta=2 时自治矩阵极点 -1 +/- 2j 并衰减；该自治证明未声明可操纵输入.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 来源模型先验：初态释放不是可连续控制的执行器，当前框架必须保留此能力边界.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 alpha=1、beta=2、A=[[-1,2],[-2,-1]]、Q=I，并从半径 0.5、1、2 的初态运行。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=Ax,\qquad A=\begin{bmatrix}-\alpha&\beta\\-\beta&-\alpha\end{bmatrix}, ; -2\alpha p-2\beta q=-1, ; \beta p-2\alpha q-\beta r=0,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 177. 非线性位置反馈的直接 Lyapunov 构造

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 177 题 [Ch9-17]。定位：Example 9.16, PDF 1776-1778。

原题保留：非线性位置反馈的直接 Lyapunov 构造。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=1、f(e)=e+e^3；从 e=±2、x2=±1 仿真，并计算 V=0.5e^2+0.25e^4+0.5x2^2。 来源模型方程（按原变量定义，仅作数学背景）：\dot e=-x_2,\qquad \dot x_2=-\frac1T x_2+\frac1T f(e). ; V(e,x_2)=\frac{T}{2}x_2^2+\int_0^e f(\sigma)\,d\sigma. ; \dot V=T x_2\dot x_2+f(e)\dot e =Tx_2\left(-\frac{x_2}{T}+\frac{f(e)}T\right) +f(e)(-x_2). 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：非线性位置反馈的直接 Lyapunov 构造。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 177 题 [Ch9-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源 Lyapunov/LaSalle 论证在其假设下证明恢复力平衡点稳定，不是任意新对象.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：f(e)=e+e^3 为非线性恢复反馈，具有速度状态.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 T=1、f(e)=e+e^3；从 e=±2、x2=±1 仿真，并计算 V=0.5e^2+0.25e^4+0.5x2^2。 来源模型方程（按原变量定义，仅作数学背景）：\dot e=-x_2,\qquad \dot x_2=-\frac1T x_2+\frac1T f(e). ; V(e,x_2)=\frac{T}{2}x_2^2+\int_0^e f(\sigma)\,d\sigma. ; \dot V=T x_2\dot x_2+f(e)\dot e =Tx_2\left(-\frac{x_2}{T}+\frac{f(e)}T\right) +f(e)(-x_2).
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 178. 符号非线性的扇区界

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 178 题 [Ch9-18]。定位：Example 9.17, PDF 1786-1788。

原题保留：符号非线性的扇区界。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对 f(e)=sign(e) 在 1e-3–10 的对数幅值上计算割线斜率 f(e)/e。 来源模型方程（按原变量定义，仅作数学背景）：f(e)=\operatorname{sgn}(e),\qquad f(0)=0. ; k_1e^2\le e\,f(e)\le k_2e^2, ; e f(e)=e\,\operatorname{sgn}(e)=|e|>0, \qquad \frac{f(e)}e=\frac1{|e|}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：符号非线性的扇区界。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 178 题 [Ch9-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：sign(e) 不连续，位于扇区 [0,infinity)，无有限全局斜率界.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对 f(e)=sign(e) 在 1e-3–10 的对数幅值上计算割线斜率 f(e)/e。 来源模型方程（按原变量定义，仅作数学背景）：f(e)=\operatorname{sgn}(e),\qquad f(0)=0. ; k_1e^2\le e\,f(e)\le k_2e^2, ; e f(e)=e\,\operatorname{sgn}(e)=|e|>0, \qquad \frac{f(e)}e=\frac1{|e|}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 179. 执行器饱和的扇区界

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 179 题 [Ch9-19]。定位：Example 9.18, PDF 1788-1789。

原题保留：执行器饱和的扇区界。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对单位斜率、限幅 ±0.1 的饱和器，在 0.01–10 幅值上逐点核对扇区不等式。 来源模型方程（按原变量定义，仅作数学背景）：f(e)= \begin{cases} e,&|e|\le0.1,\\ 0.1\,\operatorname{sgn}(e),&|e|>0.1. \end{cases} ; \frac{f(e)}e=1. ; \frac{f(e)}e=\frac{0.1}{|e|}, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：执行器饱和的扇区界。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 179 题 [Ch9-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：斜率为一的 +/-0.1 饱和位于扇区 [0,1]，不增加动态状态.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：对单位斜率、限幅 ±0.1 的饱和器，在 0.01–10 幅值上逐点核对扇区不等式。 来源模型方程（按原变量定义，仅作数学背景）：f(e)= \begin{cases} e,&|e|\le0.1,\\ 0.1\,\operatorname{sgn}(e),&|e|>0.1. \end{cases} ; \frac{f(e)}e=1. ; \frac{f(e)}e=\frac{0.1}{|e|},
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 180. 用圆判据认证饱和环路绝对稳定

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 180 题 [Ch9-20]。定位：Example 9.19, PDF 1798-1799。

原题保留：用圆判据认证饱和环路绝对稳定。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 数学/设计题中的 source_input_u、source_output_y 是来源所研究通道的归一化输入输出；尺度各取一个来源单位、偏置为零，是新增仿真约定。若原题只有闭环参考响应，该通道仍是参考到输出的整体，不能当成裸对象或让 CFDC 自动拆除原控制器。若原题没有可操纵动态输入，当前只能完成任务定义和取证需求，必须停在能力边界，不能用虚构一阶代理补齐。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取线性块 G=(s+1)^2/s^3 与扇区 [0,1] 单位饱和；绘制 Nyquist 与 Re(G)=-1 边界并仿真有界初态。 来源模型方程（按原变量定义，仅作数学背景）：k_1y^2\le y f(t,y)\le k_2y^2,\qquad 0\le k_1<k_2, ; F(j\omega)=\frac{1+k_2G(j\omega)} {1+k_1G(j\omega)}. ; G=-\frac1{k_2}\quad(F=0),\qquad G=-\frac1{k_1}\quad(F=\infty) 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：用圆判据认证饱和环路绝对稳定。本次仅做外部软件模型的适配子任务：使 source_output_y 保持在 0.1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 180 题 [Ch9-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["source_output_y", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["source_input_u"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.1` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2.0` |
| 输出上限 | `output_max` | `2.0` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：圆判据是扇区非线性的充分条件证书，不是测量或必要失稳判据.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取线性块 G=(s+1)^2/s^3 与扇区 [0,1] 单位饱和；绘制 Nyquist 与 Re(G)=-1 边界并仿真有界初态。 来源模型方程（按原变量定义，仅作数学背景）：k_1y^2\le y f(t,y)\le k_2y^2,\qquad 0\le k_1<k_2, ; F(j\omega)=\frac{1+k_2G(j\omega)} {1+k_1G(j\omega)}. ; G=-\frac1{k_2}\quad(F=0),\qquad G=-\frac1{k_1}\quad(F=\infty)
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 181. 柔性双体卫星建模与设计指标转换

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 181 题 [Ch10-01]。定位：Section 10.2, PDF 1856-1862。

原题保留：柔性双体卫星建模与设计指标转换。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 J1=1、J2=0.1、k=0.091、b=0.0036 与 G=0.036(s+25)/[s^2(s^2+0.04s+1)]；测试 k,b 边界及指向阶跃。 来源模型方程（按原变量定义，仅作数学背景）：0.09\le k\le0.4,\qquad 0.038\sqrt{k/10}\le b\le0.2\sqrt{k/10}. ; J_1\ddot\theta_1+b(\dot\theta_1-\dot\theta_2) +k(\theta_1-\theta_2)=T_c, ; J_2\ddot\theta_2+b(\dot\theta_2-\dot\theta_1) +k(\theta_2-\theta_1)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：柔性双体卫星建模与设计指标转换。本次仅做外部软件模型的适配子任务：使 main_body_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 181 题 [Ch10-01]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["main_body_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 J1=1、J2=0.1、k=0.091、b=0.0036 与 G=0.036(s+25)/[s^2(s^2+0.04s+1)]；测试 k,b 边界及指向阶跃。 来源模型方程（按原变量定义，仅作数学背景）：0.09\le k\le0.4,\qquad 0.038\sqrt{k/10}\le b\le0.2\sqrt{k/10}. ; J_1\ddot\theta_1+b(\dot\theta_1-\dot\theta_2) +k(\theta_1-\theta_2)=T_c, ; J_2\ddot\theta_2+b(\dot\theta_2-\dot\theta_1) +k(\theta_2-\theta_1)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 182. 柔性卫星的增益稳定与陷波相位稳定比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 182 题 [Ch10-02]。定位：Section 10.2, PDF 1862-1887。

原题保留：柔性卫星的增益稳定与陷波相位稳定比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在名义柔性卫星上比较 Dc1=0.25(2s+1)、Dc2=0.001(30s+1)、Dc3=Dc1[((s/0.9)^2+1)/(s/25+1)^2]，并覆盖所有 k,b 边界。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{0.036(s+25)}{s^2(s^2+0.04s+1)}. ; D_{c3}=0.25(2s+1) \frac{(s/0.9)^2+1}{[(s/25)+1]^2}. ; s^2+0.5s+0.25=0 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：柔性卫星的增益稳定与陷波相位稳定比较。本次仅做外部软件模型的适配子任务：使 main_body_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 182 题 [Ch10-02]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["main_body_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：在名义柔性卫星上比较 Dc1=0.25(2s+1)、Dc2=0.001(30s+1)、Dc3=Dc1[((s/0.9)^2+1)/(s/25+1)^2]，并覆盖所有 k,b 边界。 来源模型方程（按原变量定义，仅作数学背景）：G(s)=\frac{0.036(s+25)}{s^2(s^2+0.04s+1)}. ; D_{c3}=0.25(2s+1) \frac{(s/0.9)^2+1}{[(s/25)+1]^2}. ; s^2+0.5s+0.25=0
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 183. 卫星对称根轨迹状态反馈与估计器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 183 题 [Ch10-03]。定位：Section 10.2, PDF 1888-1900。

原题保留：卫星对称根轨迹状态反馈与估计器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取控制极点 -0.45±j0.34、-0.15±j1.05，K=[-0.2788,0.0546,0.6814,1.1655]、L=[222,42.3,1515.4,5503.9]。 来源模型方程（按原变量定义，仅作数学背景）：x=[\theta_2,\dot\theta_2,\theta_1,\dot\theta_1]^T,\qquad C=[1,0,0,0]. ; \dot{\hat x}=A\hat x+Bu+L(y-C\hat x). ; p_c=-0.45\pm j0.34,\quad-0.15\pm j1.05. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：卫星对称根轨迹状态反馈与估计器。本次仅做外部软件模型的适配子任务：使 measured_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 183 题 [Ch10-03]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["measured_attitude", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取控制极点 -0.45±j0.34、-0.15±j1.05，K=[-0.2788,0.0546,0.6814,1.1655]、L=[222,42.3,1515.4,5503.9]。 来源模型方程（按原变量定义，仅作数学背景）：x=[\theta_2,\dot\theta_2,\theta_1,\dot\theta_1]^T,\qquad C=[1,0,0,0]. ; \dot{\hat x}=A\hat x+Bu+L(y-C\hat x). ; p_c=-0.45\pm j0.34,\quad-0.15\pm j1.05.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 184. 传感器与执行器共址的卫星重设计

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 184 题 [Ch10-04]。定位：Section 10.2, PDF 1901-1908。

原题保留：传感器与执行器共址的卫星重设计。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用共址 Gco=[(s+0.018)^2+0.954^2]/{s^2[(s+0.02)^2+1]} 与控制器 0.25(2s+1)，并与远端传感比较。 来源模型方程（按原变量定义，仅作数学背景）：C_{co}=[0,0,1,0]. ; \Delta=s^2[J_1J_2s^2+(J_1+J_2)bs+(J_1+J_2)k]. ; G_{co}(s)=\frac{s^2+10bs+10k} {s^2(s^2+11bs+11k)}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：传感器与执行器共址的卫星重设计。本次仅做外部软件模型的适配子任务：使 collocated_attitude 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 184 题 [Ch10-04]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["collocated_attitude", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["body_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用共址 Gco=[(s+0.018)^2+0.954^2]/{s^2[(s+0.02)^2+1]} 与控制器 0.25(2s+1)，并与远端传感比较。 来源模型方程（按原变量定义，仅作数学背景）：C_{co}=[0,0,1,0]. ; \Delta=s^2[J_1J_2s^2+(J_1+J_2)bs+(J_1+J_2)k]. ; G_{co}(s)=\frac{s^2+10bs+10k} {s^2(s^2+11bs+11k)}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 185. 波音 747 纵横向线性化与模态识别

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 185 题 [Ch10-05]。定位：Section 10.3, PDF 1909-1921 and 1936-1940。

原题保留：波音 747 纵横向线性化与模态识别。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用代表荷兰滚 wn=1 rad/s、zeta=0.03，并记录螺旋、滚转、长周期、短周期模态估计；方向舵与升降舵分开激励。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_d=A_dx_d+B_d\delta_r,\qquad y=r. ; \frac{r}{\delta_r}= \frac{-0.475(s+0.498)(s+0.012\pm j0.488)} {(s+0.0073)(s+0.563)(s+0.033\pm j0.947)}. ; \omega_n\approx0.948,\qquad \zeta\approx0.033/0.948\approx0.035. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：波音 747 纵横向线性化与模态识别。本次仅做外部软件模型的适配子任务：使 yaw_rate 保持在 0.04 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 185 题 [Ch10-05]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["yaw_rate", "deg/s"]]` |
| 输入行 [名称] | `inputs` | `[["rudder_deflection"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.04` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用代表荷兰滚 wn=1 rad/s、zeta=0.03，并记录螺旋、滚转、长周期、短周期模态估计；方向舵与升降舵分开激励。 来源模型方程（按原变量定义，仅作数学背景）：\dot x_d=A_dx_d+B_d\delta_r,\qquad y=r. ; \frac{r}{\delta_r}= \frac{-0.475(s+0.498)(s+0.012\pm j0.488)} {(s+0.0073)(s+0.563)(s+0.033\pm j0.947)}. ; \omega_n\approx0.948,\qquad \zeta\approx0.033/0.948\approx0.035.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 186. 含执行器与洗出环节的偏航阻尼器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 186 题 [Ch10-06]。定位：Section 10.3.1, PDF 1917-1930。

原题保留：含执行器与洗出环节的偏航阻尼器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取偏航增益 Kr=2.6、洗出 s/(s+1/3)、方向舵舵机 10/(s+10)；测试偏航率脉冲与稳态转弯命令。 来源模型方程（按原变量定义，仅作数学背景）：A(s)=\frac{10}{s+10}, ; H_w(s)=\frac{s}{s+1/\tau},\qquad \tau=3\ {\rm s}, ; H_w(0)=0,\qquad \lim_{\omega\to\infty}H_w(j\omega)=1. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：含执行器与洗出环节的偏航阻尼器。本次仅做外部软件模型的适配子任务：使 yaw_rate 保持在 0.04 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 186 题 [Ch10-06]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["yaw_rate", "deg/s"]]` |
| 输入行 [名称] | `inputs` | `[["rudder_deflection"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.04` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取偏航增益 Kr=2.6、洗出 s/(s+1/3)、方向舵舵机 10/(s+10)；测试偏航率脉冲与稳态转弯命令。 来源模型方程（按原变量定义，仅作数学背景）：A(s)=\frac{10}{s+10}, ; H_w(s)=\frac{s}{s+1/\tau},\qquad \tau=3\ {\rm s}, ; H_w(0)=0,\qquad \lim_{\omega\to\infty}H_w(j\omega)=1.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 187. 实用偏航阻尼器与高阶状态估计方案比较

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 187 题 [Ch10-07]。定位：Section 10.3.1, PDF 1931-1936。

原题保留：实用偏航阻尼器与高阶状态估计方案比较。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：比较 Kr=2.6 的实用偏航阻尼器与六状态反馈 K=[1.059,-0.191,-2.32,0.0992,0.037,0.486] 及其估计器，并注入传感噪声。 来源模型方程（按原变量定义，仅作数学背景）：x_a=[x_A,\beta,r,p,\phi,x_{wo}]^T. ; -0.0051,\ -0.468,\ -0.279\pm j0.628,\ -1.106,\ -9.89, ; K=[1.059,-0.191,-2.320,0.0992,0.0370,0.486]. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：实用偏航阻尼器与高阶状态估计方案比较。本次仅做外部软件模型的适配子任务：使 yaw_rate 保持在 0.04 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 187 题 [Ch10-07]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["yaw_rate", "deg/s"]]` |
| 输入行 [名称] | `inputs` | `[["rudder_deflection"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.04` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：比较 Kr=2.6 的实用偏航阻尼器与六状态反馈 K=[1.059,-0.191,-2.32,0.0992,0.037,0.486] 及其估计器，并注入传感噪声。 来源模型方程（按原变量定义，仅作数学背景）：x_a=[x_A,\beta,r,p,\phi,x_{wo}]^T. ; -0.0051,\ -0.468,\ -0.279\pm j0.628,\ -1.106,\ -9.89, ; K=[1.059,-0.191,-2.320,0.0992,0.0370,0.486].
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 188. 俯仰内环与高度外环的高度保持

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 188 题 [Ch10-08]。定位：Section 10.3.2, PDF 1936-1951。

原题保留：俯仰内环与高度外环的高度保持。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用含 RHP 零点 +5.61 的高度通道、快速俯仰内环、较慢高度外环，并与全状态 K=[-0.0009,0.0016,-1.883,-7.603,-0.001] 比较。 来源模型方程（按原变量定义，仅作数学背景）：x=[u,w,q,\theta,h]^T, ; A_q=A+k_qBC_q,\qquad C_q=[0,0,1,0,0] ; K_{\theta q}=[0,0,-0.8,-6,0], \qquad A_{\theta q}=A_q-BK_{\theta q}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：俯仰内环与高度外环的高度保持。本次仅做外部软件模型的适配子任务：使 altitude_deviation 保持在 0.4 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 188 题 [Ch10-08]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["altitude_deviation", "source_altitude_unit"]]` |
| 输入行 [名称] | `inputs` | `[["elevator_deflection"]]` |
| 输入单位 | `input_unit` | `"deg"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.4` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `24.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-20` |
| 输出上限 | `output_max` | `20` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.8` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 来源模型先验：来源高度/升降舵通道有右半平面零点 +5.61，初始逆响应.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用含 RHP 零点 +5.61 的高度通道、快速俯仰内环、较慢高度外环，并与全状态 K=[-0.0009,0.0016,-1.883,-7.603,-0.001] 比较。 来源模型方程（按原变量定义，仅作数学背景）：x=[u,w,q,\theta,h]^T, ; A_q=A+k_qBC_q,\qquad C_q=[0,0,1,0,0] ; K_{\theta q}=[0,0,-0.8,-6,0], \qquad A_{\theta q}=A_q-BK_{\theta q}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 189. 含迟延燃油空气过程的 PI 整定

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 189 题 [Ch10-09]。定位：Section 10.4, PDF 1952-1965。

原题保留：含迟延燃油空气过程的 PI 整定。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取燃油快/慢时间常数 0.02、1 s、各权重 0.5、运输迟延 0.2 s、传感器滞后 0.1 s、PI 聚合增益 KsKp=2.2。 来源模型方程（按原变量定义，仅作数学背景）：\tau_1=0.02,\quad\tau_2=1,\quad T_d=0.2,\quad\tau=0.1\ {\rm s}. ; P(s)=\left[\frac{0.5}{\tau_1s+1} +\frac{0.5}{\tau_2s+1}\right]e^{-T_ds}. ; D_c(s)=K_p+\frac{K_I}{s} =K_p\frac{s+z}{s},\qquad z=K_I/K_p=0.3. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：含迟延燃油空气过程的 PI 整定。本次仅做外部软件模型的适配子任务：使 fuel_air_ratio 保持在 0.0264 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 189 题 [Ch10-09]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["fuel_air_ratio", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["fuel_injection_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0264` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.584` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.32` |
| 输出上限 | `output_max` | `1.32` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0528` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：发动机/传感模型显式含迟延，PI 不消除它.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取燃油快/慢时间常数 0.02、1 s、各权重 0.5、运输迟延 0.2 s、传感器滞后 0.1 s、PI 聚合增益 KsKp=2.2。 来源模型方程（按原变量定义，仅作数学背景）：\tau_1=0.02,\quad\tau_2=1,\quad T_d=0.2,\quad\tau=0.1\ {\rm s}. ; P(s)=\left[\frac{0.5}{\tau_1s+1} +\frac{0.5}{\tau_2s+1}\right]e^{-T_ds}. ; D_c(s)=K_p+\frac{K_I}{s} =K_p\frac{s+z}{s},\qquad z=K_I/K_p=0.3.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 190. 非线性氧传感器导致的极限环

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 190 题 [Ch10-10]。定位：Section 10.4, PDF 1966-1968。

原题保留：非线性氧传感器导致的极限环。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用燃空动态、氧传感器输出 0.1..0.9、中心斜率 20、Kp=0.1、小信号环增益 6，并保留饱和；测量极限环。 来源模型方程（按原变量定义，仅作数学背景）：f(v)= \begin{cases} 0.1,&v<0.0606,\\ 0.1+20(v-0.0606),&0.0606\le v<0.0741,\\ 0.9,&v\ge0.0741. \end{cases} ; K_{s,eq}(a)\approx\frac{4N}{\pi a}. ; a=\frac{4N}{\pi K_{s,eq}} =\frac{4(0.4)}{28\pi}\approx0.0182. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：非线性氧传感器导致的极限环。本次仅做外部软件模型的适配子任务：使 air_fuel_error 保持在 0.0264 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 190 题 [Ch10-10]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["air_fuel_error", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["fuel_injection_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0264` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.584` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.32` |
| 输出上限 | `output_max` | `1.32` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0528` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：非线性氧传感器可产生幅值相关增益和极限环.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用燃空动态、氧传感器输出 0.1..0.9、中心斜率 20、Kp=0.1、小信号环增益 6，并保留饱和；测量极限环。 来源模型方程（按原变量定义，仅作数学背景）：f(v)= \begin{cases} 0.1,&v<0.0606,\\ 0.1+20(v-0.0606),&0.0606\le v<0.0741,\\ 0.9,&v\ge0.0741. \end{cases} ; K_{s,eq}(a)\approx\frac{4N}{\pi a}. ; a=\frac{4N}{\pi K_{s,eq}} =\frac{4(0.4)}{28\pi}\approx0.0182.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 191. 继电整形实现稳健平均化学计量比

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 191 题 [Ch10-11]。定位：Section 10.4, PDF 1968-1971。

原题保留：继电整形实现稳健平均化学计量比。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用继电 q=N sign(vs-vstar)，示例取 N=0.05，沿用燃空/PI 动态，并把传感器斜率乘 0.5、1、2。 来源模型方程（按原变量定义，仅作数学背景）：q(t)=N\,\operatorname{sgn}\!\bigl(v_s(t)-v_\star\bigr). ; b_1=\frac{2}{\pi}\int_0^\pi N\sin\theta\,d\theta=\frac{4N}{\pi}. ; 1+N_R(a)L_0(j\omega)=0. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：继电整形实现稳健平均化学计量比。本次仅做外部软件模型的适配子任务：使 average_fuel_air_ratio 保持在 0.0264 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 191 题 [Ch10-11]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["average_fuel_air_ratio", "normalized_output"]]` |
| 输入行 [名称] | `inputs` | `[["fuel_injection_command_through_relay_conditioned_sensing"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.0264` |
| 输入下限 | `input_min` | `-1.0` |
| 输入上限 | `input_max` | `1.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.584` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1.32` |
| 输出上限 | `output_max` | `1.32` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.0528` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：继电处理传感保留切换行为；平均调节不代表逐点恒定输出.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：采用继电 q=N sign(vs-vstar)，示例取 N=0.05，沿用燃空/PI 动态，并把传感器斜率乘 0.5、1、2。 来源模型方程（按原变量定义，仅作数学背景）：q(t)=N\,\operatorname{sgn}\!\bigl(v_s(t)-v_\star\bigr). ; b_1=\frac{2}{\pi}\int_0^\pi N\sin\theta\,d\theta=\frac{4N}{\pi}. ; 1+N_R(a)L_0(j\omega)=0.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 192. 四旋翼解耦轴模型与旋翼混控

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 192 题 [Ch10-12]。定位：Section 10.5, PDF 1972-1981。

原题保留：四旋翼解耦轴模型与旋翼混控。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用质量 1 kg、Iyy=0.02 kg*m^2 的 VTOL/四旋翼切片，推力 0..20 N、力矩 ±1 Nm；记录全部状态并逐列测试旋翼混控。 来源模型方程（按原变量定义，仅作数学背景）：x_\ell=[x,u,q,\theta,T_\theta]^T, ; \dot x_\ell= \begin{bmatrix} 0&1&0&0&0\\ 0&X_u&0&-g&0\\ 0&M_u&0&0&M_\theta\\ 0&0&1&0&0\\ 0&0&0&0&-a \end{bmatrix}x_\ell+ \begin{bmatrix}0\\0\\0\\0\\a\end{bmatrix}T_{\rm lon}. ; \frac{\Theta}{T_{\rm lon}}=\frac{a/I_y}{s^2(s+a)},\qquad \frac{X}{\Theta}=-\frac{g}{s^2}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四旋翼解耦轴模型与旋翼混控。本次仅做外部软件模型的适配子任务：使 pitch_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 192 题 [Ch10-12]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pitch_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["equivalent_pitch_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-0.5` |
| 输入上限 | `input_max` | `0.5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用质量 1 kg、Iyy=0.02 kg*m^2 的 VTOL/四旋翼切片，推力 0..20 N、力矩 ±1 Nm；记录全部状态并逐列测试旋翼混控。 来源模型方程（按原变量定义，仅作数学背景）：x_\ell=[x,u,q,\theta,T_\theta]^T, ; \dot x_\ell= \begin{bmatrix} 0&1&0&0&0\\ 0&X_u&0&-g&0\\ 0&M_u&0&0&M_\theta\\ 0&0&1&0&0\\ 0&0&0&0&-a \end{bmatrix}x_\ell+ \begin{bmatrix}0\\0\\0\\0\\a\end{bmatrix}T_{\rm lon}. ; \frac{\Theta}{T_{\rm lon}}=\frac{a/I_y}{s^2(s+a)},\qquad \frac{X}{\Theta}=-\frac{g}{s^2}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 193. 四旋翼姿态内环与位置外环串级 PD

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 193 题 [Ch10-13]。定位：Section 10.5, PDF 1981-1995。

原题保留：四旋翼姿态内环与位置外环串级 PD。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Gtheta=0.4(s+0.25)/[(s^2-3.2s+10.4)(s+3.4)(s+20)]、Gx=-131/[s 乘同一分母]；姿态内环快于位置外环。 来源模型方程（按原变量定义，仅作数学背景）：M_u=1.1,\quad X_u=-0.25,\quad M_\theta=0.02,\quad g=32.2,\quad a=20 ; G_\theta(s)=\frac{0.4(s+0.25)} {(s^2-3.2s+10.4)(s+3.4)(s+20)},\quad G_x(s)=\frac{-131} {s(s^2-3.2s+10.4)(s+3.4)(s+20)}. ; T_\theta(s)=\frac{D_1G_\theta}{1+D_1G_\theta}. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四旋翼姿态内环与位置外环串级 PD。本次仅做外部软件模型的适配子任务：使 horizontal_position_deviation 保持在 0.04 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 193 题 [Ch10-13]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 本次先从 0 转移，依次经过 无中间目标，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 0.04 附近，误差不超过 0.08"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["horizontal_position_deviation", "m"]]` |
| 输入行 [名称] | `inputs` | `[["equivalent_pitch_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.04` |
| 输入下限 | `input_min` | `-1` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-2` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.08` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取 Gtheta=0.4(s+0.25)/[(s^2-3.2s+10.4)(s+3.4)(s+20)]、Gx=-131/[s 乘同一分母]；姿态内环快于位置外环。 来源模型方程（按原变量定义，仅作数学背景）：M_u=1.1,\quad X_u=-0.25,\quad M_\theta=0.02,\quad g=32.2,\quad a=20 ; G_\theta(s)=\frac{0.4(s+0.25)} {(s^2-3.2s+10.4)(s+3.4)(s+20)},\quad G_x(s)=\frac{-131} {s(s^2-3.2s+10.4)(s+3.4)(s+20)}. ; T_\theta(s)=\frac{D_1G_\theta}{1+D_1G_\theta}.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 194. 四旋翼各轴 LQR 与状态估计器

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 194 题 [Ch10-14]。定位：Section 10.5, PDF 1995-2003。

原题保留：四旋翼各轴 LQR 与状态估计器。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用完整 VTOL 状态与约束，并把给出的纵向/侧向/偏航 LQR 增益对应的 rho 与估计器 q 乘 0.1、1、10 比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=Ax+Bu,\qquad y=Cx,\qquad u=-K\hat x+\bar Nr, ; \dot{\hat x}=A\hat x+Bu+L(y-C\hat x) ; \begin{bmatrix}A&B\\C&0\end{bmatrix} \begin{bmatrix}N_x\\N_u\end{bmatrix} = \begin{bmatrix}0\\1\end{bmatrix},\qquad \bar N=N_u+KN_x. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：四旋翼各轴 LQR 与状态估计器。本次仅做外部软件模型的适配子任务：使 pitch_angle 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 194 题 [Ch10-14]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["pitch_angle", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["equivalent_pitch_torque"]]` |
| 输入单位 | `input_unit` | `"Nm"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `-0.5` |
| 输入上限 | `input_max` | `0.5` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `-1` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：原开环通道含积分或刚体运动，零输入并不保证渐近回到初始位置；来源稳定反馈不能冒充对象自身稳定.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用完整 VTOL 状态与约束，并把给出的纵向/侧向/偏航 LQR 增益对应的 rho 与估计器 q 乘 0.1、1、10 比较。 来源模型方程（按原变量定义，仅作数学背景）：\dot x=Ax+Bu,\qquad y=Cx,\qquad u=-K\hat x+\bar Nr, ; \dot{\hat x}=A\hat x+Bu+L(y-C\hat x) ; \begin{bmatrix}A&B\\C&0\end{bmatrix} \begin{bmatrix}N_x\\N_u\end{bmatrix} = \begin{bmatrix}0\\1\end{bmatrix},\qquad \bar N=N_u+KN_x.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 195. RTP 辐射传导非线性与三状态小信号模型

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 195 题 [Ch10-15]。定位：Section 10.6, PDF 2004-2021。

原题保留：RTP 辐射传导非线性与三状态小信号模型。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 RTP 三状态公共输入传函 0.5226(s+0.0876)(s+0.1438)/[(s+0.1482)(s+0.0863)(s+0.0527)]，测试三档灯功率。 来源模型方程（按原变量定义，仅作数学背景）：M\dot T=A_r \begin{bmatrix}T^{\circ4}\\T_\infty^4\end{bmatrix} A_c\begin{bmatrix}T\\T_\infty\end{bmatrix} B_3u_3, ; (T_i)^4\approx \bar T_i^4+4\bar T_i^3\delta T_i. ; \delta\dot T=A\delta T+B\,\delta u,\qquad A=M^{-1}\!\left(A_rJ_4+A_cJ_1\right), 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：RTP 辐射传导非线性与三状态小信号模型。本次仅做外部软件模型的适配子任务：使 center_temperature_rise 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 195 题 [Ch10-15]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["center_temperature_rise", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["common_lamp_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：辐射依赖绝对温度四次方，三状态线性模型只适用工作点附近.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 RTP 三状态公共输入传函 0.5226(s+0.0876)(s+0.1438)/[(s+0.1482)(s+0.0863)(s+0.0527)]，测试三档灯功率。 来源模型方程（按原变量定义，仅作数学背景）：M\dot T=A_r \begin{bmatrix}T^{\circ4}\\T_\infty^4\end{bmatrix} A_c\begin{bmatrix}T\\T_\infty\end{bmatrix} B_3u_3, ; (T_i)^4\approx \bar T_i^4+4\bar T_i^3\delta T_i. ; \delta\dot T=A\delta T+B\,\delta u,\qquad A=M^{-1}\!\left(A_rJ_4+A_cJ_1\right),
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 196. 无主动冷却条件下的 RTP PI 轨迹控制

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 196 题 [Ch10-16]。定位：Section 10.6, PDF 2021-2024。

原题保留：无主动冷却条件下的 RTP PI 轨迹控制。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原公共灯命令到中心温度模型 G(s)=0.5226(s+0.0876)(s+0.1438)/[(s+0.1482)(s+0.0863)(s+0.0527)]，静态增益约 9.767 单位/命令。新增标定为 1 输出单位=1 degC 温升。输入为 0..1 非负归一化公共灯命令，不是瓦特。将原连续轨迹适配为 0.3、0.6、1 degC 分段保持，从零温升开始，只允许被动降温。原 PI (s+0.0527)/s 仅为背景，未经自动批准；降温速率跟踪与独立灯区控制不在本子任务范围内。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：无主动冷却条件下的 RTP PI 轨迹控制。本次仅做外部软件模型的适配子任务：使 center_temperature_rise 保持在 1 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 196 题 [Ch10-16]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。 原公共灯命令到中心温度模型 G(s)=0.5226(s+0.0876)(s+0.1438)/[(s+0.1482)(s+0.0863)(s+0.0527)]，静态增益约 9.767 单位/命令。新增标定为 1 输出单位=1 degC 温升。输入为 0..1 非负归一化公共灯命令，不是瓦特。将原连续轨迹适配为 0.3、0.6、1 degC 分段保持，从零温升开始，只允许被动降温。原 PI (s+0.0527)/s 仅为背景，未经自动批准；降温速率跟踪与独立灯区控制不在本子任务范围内。 本次先从 0 转移，依次经过 0.3, 0.6，最后保持。原连续轨迹或全局目标只作背景。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 开始区域 | `initial_region` | `"仿真初始主要输出为 0，位于声明边界内"` |
| 目标区域 | `goal_region` | `"最终主要输出 1 附近，误差不超过 0.1"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `"0.3, 0.6"` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["center_temperature_rise", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["common_lamp_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `1` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.1` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `60` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `60` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
第 1–7 项仅对给定适配名义数学模型及主要输入输出已知，第 8 项未知。这些是模型先验，不是硬件观测或协议绑定记录；真实传感器、标定和执行器仍未验证.
1. open_loop_stability: stable（稳定）：三个名义热极点均为负实数.
2. nonminimum_phase: minimum-phase（最小相位）：两个零点 -0.0876 和 -0.1438 均在左半平面，无右半平面零点.
3. significant_delay: not_significant（无显著迟延）：名义传递函数不含纯迟延.
4. relative_degree: low（低）：公共灯指令到中心温度通道相对阶次为 1，尽管有三个状态.
5. sensing_actuation_adequacy: adequate（对名义最小三状态中心温度实现充分）：理想中心温度时序使状态可观，公共灯输入使其可控；这不验证真实传感器、任意物理热节点状态或冷却性能；约束下的局部控制仅限正指令区间内部的升温/保持工作点，不保证零输入边界的任意双向控制或全域约束可达性.
6. nonlinearity_strength: weak（弱）：名义热动态在声明指令边界内为线性，非负输入约束仍须单独执行.
7. coupling_underactuation: siso：一个公共灯指令控制一个主要中心温升；辅助热节点不是独立目标通道，没有主动冷却是输入限制，不是所选通道欠驱动的证据.
8. uncertainty_variation: 未知，没有灯标定和散热复测.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 197. 兼顾温度均匀性的误差空间 LQG

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 197 题 [Ch10-17]。定位：Section 10.6, PDF 2024-2032。

原题保留：兼顾温度均匀性的误差空间 LQG。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 RTP 三状态模型、K1=1、K0=[0.1221,2.0788,-0.2140]、L=[16.1461,16.4710,13.2001]、Rw=1、Rv=0.001；记录节点温差。 来源模型方程（按原变量定义，仅作数学背景）：\begin{bmatrix}\dot e\\\dot\xi\end{bmatrix} = \underbrace{\begin{bmatrix}0&C\\0&A\end{bmatrix}}_{A_e} \begin{bmatrix}e\\\xi\end{bmatrix} + \underbrace{\begin{bmatrix}D\\B\end{bmatrix}}_{B_e}\mu. ; J=\int_0^\infty(z^TQz+\mu^2)\,dt,\quad Q=\begin{bmatrix} 1&0&0&0\\ 0&20&-10&-10\\ 0&-10&20&-10\\ 0&-10&-10&20 \end{bmatrix}. ; \dot x_c=-K_1e,\qquad u=x_c-K_0\hat T, 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：兼顾温度均匀性的误差空间 LQG。本次仅做外部软件模型的适配子任务：使 center_temperature_rise 保持在 0.02 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 197 题 [Ch10-17]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["center_temperature_rise", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["common_lamp_command"]]` |
| 输入单位 | `input_unit` | `"normalized_input"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.02` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `1` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.4` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `2` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：来源中满足正参数条件的名义耗散模型具有衰减模态；结论仅限来源模型和所选工作点，不代表尚未验证的反馈实现.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：所示名义微分方程或有理通道没有显式纯时间迟延；实际传输和传感迟延未测量.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 来源模型先验：仅中心温度为测量；三个热节点状态是估计量，不是独立实测.
6. nonlinearity_strength: 来源模型先验：所示来源通道方程是线性方程或注明的局部线性化；这不等于实测装置线性。原设计控制器是背景，不默认已经安装.
7. coupling_underactuation: 来源模型先验：三盏灯接收一个公共命令；均匀性不是独立多变量执行.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：使用 RTP 三状态模型、K1=1、K0=[0.1221,2.0788,-0.2140]、L=[16.1461,16.4710,13.2001]、Rw=1、Rv=0.001；记录节点温差。 来源模型方程（按原变量定义，仅作数学背景）：\begin{bmatrix}\dot e\\\dot\xi\end{bmatrix} = \underbrace{\begin{bmatrix}0&C\\0&A\end{bmatrix}}_{A_e} \begin{bmatrix}e\\\xi\end{bmatrix} + \underbrace{\begin{bmatrix}D\\B\end{bmatrix}}_{B_e}\mu. ; J=\int_0^\infty(z^TQz+\mu^2)\,dt,\quad Q=\begin{bmatrix} 1&0&0&0\\ 0&20&-10&-10\\ 0&-10&20&-10\\ 0&-10&-10&20 \end{bmatrix}. ; \dot x_c=-K_1e,\qquad u=x_c-K_0\hat T,
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 198. RTP 灯逆补偿、饱和、反饱和与数字验证

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 198 题 [Ch10-18]。定位：Section 10.6, PDF 2032-2042。

原题保留：RTP 灯逆补偿、饱和、反饱和与数字验证。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取灯功率 P=V^1.6、逆映射 V=P^0.625、电压限幅 1..4 V、参考滤波 0.2/(s+0.2)、Ts=0.1 s，并明确试用 1 s 反饱和恢复时间。 来源模型方程（按原变量定义，仅作数学背景）：P=V^{1.6},\qquad V=P^{1/1.6}=P^{0.625}, ; V_{\rm raw}=P_{\rm raw}^{0.625},\qquad V_{\rm sat}=\operatorname{sat}_{[1,4]}(V_{\rm raw}). ; \dot x_c=A_cx_c+B_ce,\qquad u_{\rm raw}=C_cx_c. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：RTP 灯逆补偿、饱和、反饱和与数字验证。本次仅做外部软件模型的适配子任务：使 temperature_rise 保持在 0.2 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 198 题 [Ch10-18]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["temperature_rise", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["lamp_voltage"]]` |
| 输入单位 | `input_unit` | `"V"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.2` |
| 输入下限 | `input_min` | `1` |
| 输入上限 | `input_max` | `4` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `24.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `20` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.4` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 未知：需要初始方向、最终方向及零点分析；不能把响应时间当纯时延.
3. significant_delay: 来源模型先验：来源采样周期为 0.1 s，须计入零阶保持和数字运算.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 来源模型先验：P=V^1.6、逆映射 V=P^0.625、电压限幅与抗饱和构成非线性采样环路.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：取灯功率 P=V^1.6、逆映射 V=P^0.625、电压限幅 1..4 V、参考滤波 0.2/(s+0.2)、Ts=0.1 s，并明确试用 1 s 反饱和恢复时间。 来源模型方程（按原变量定义，仅作数学背景）：P=V^{1.6},\qquad V=P^{1/1.6}=P^{0.625}, ; V_{\rm raw}=P_{\rm raw}^{0.625},\qquad V_{\rm sat}=\operatorname{sat}_{[1,4]}(V_{\rm raw}). ; \dot x_c=A_cx_c+B_ce,\qquad u_{\rm raw}=C_cx_c.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 199. 大肠杆菌趋化的积分反馈精确适应

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 199 题 [Ch10-19]。定位：Section 10.7, PDF 2052-2060。

原题保留：大肠杆菌趋化的积分反馈精确适应。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：数值示例取 K=1、Km=0.2 s^-1、CheRbar=0.5；20 s 时配体阶跃 1，并运行 60 s。 来源模型方程（按原变量定义，仅作数学背景）：a=K(m-\ell),\qquad \dot m=K_m(\overline{\mathrm{CheR}}-a), ; \bar a=\overline{\mathrm{CheR}},\qquad \bar m=\bar\ell+\frac{\bar a}{K}. ; \delta\dot m=-K_m\delta a. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：大肠杆菌趋化的积分反馈精确适应。本次仅做外部软件模型的适配子任务：使 receptor_activity 保持在 0.5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 199 题 [Ch10-19]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["receptor_activity", "normalized_activity"]]` |
| 输入行 [名称] | `inputs` | `[["ligand_concentration"]]` |
| 输入单位 | `input_unit` | `"normalized_concentration"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.5` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `2` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 来源模型先验：K、Km 为正时适应过程按 1/(K Km) 时间常数衰减，受体活动回基线.
2. nonminimum_phase: 来源模型先验：精确适应使恒定配体扰动的直流响应为零；任意新活动度目标不保证可达.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 未知：仅声明表中测量和执行接口，没有可观可控实测证据.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：数值示例取 K=1、Km=0.2 s^-1、CheRbar=0.5；20 s 时配体阶跃 1，并运行 60 s。 来源模型方程（按原变量定义，仅作数学背景）：a=K(m-\ell),\qquad \dot m=K_m(\overline{\mathrm{CheR}}-a), ; \bar a=\overline{\mathrm{CheR}},\qquad \bar m=\bar\ell+\frac{\bar a}{K}. ; \delta\dot m=-K_m\delta a.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 200. 由 CheY 活动映射一维平均趋化运动

### 1. 原题、来源与适配范围

来源：[已提交技术语料](control_problems.md)，第 200 题 [Ch10-20]。定位：Section 10.7, PDF 2048-2062。

原题保留：由 CheY 活动映射一维平均趋化运动。当前填写的是上述局部目标保持/转移/恢复子任务；不声称完成原题全部分析、控制器比较、轨迹或硬件任务。 信号页仅列本次主要输出；原题其他传感器/状态仅作为辅助取证背景，不默认可测，也不接受同一个标量目标。所有未由来源确定的初值、目标、限制、性能容差和预算都是本次软件练习假设；目标可达性仍需模型和数据检验。

原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：延续趋化示例，取 Ka=1、Kx=0.5、基线 w=0；配体阶跃 1 并积分平均位置。 来源模型方程（按原变量定义，仅作数学背景）：y_{\rm CheY}=K_a a ; \dot x=w+K_x(\bar y-y_{\rm CheY}) ; \delta y_{\rm CheY}=K_a\delta a,\qquad \delta\dot x=-K_xK_a\delta a. 以上原题例算设置仅作背景比较；本次边界以表格为准，实际激励仅按新生成协议，不把原题多输出共用一个单位，也不把例算拟合值当实测。

### 2. 目标页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"原题背景：由 CheY 活动映射一维平均趋化运动。本次仅做外部软件模型的适配子任务：使 receptor_activity 保持在 0.5 附近。仅表中输出是主要被控量。来源为 dataset/control_problems.md 第 200 题 [Ch10-20]；方程/参数是模型信息，不是已有实验记录。当前没有协议绑定数据；不选择注册案例，不授权硬件。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |

### 3. 信号页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 输出行 [名称, 单位] | `outputs` | `[["receptor_activity", "normalized_activity"]]` |
| 输入行 [名称] | `inputs` | `[["ligand_concentration"]]` |
| 输入单位 | `input_unit` | `"normalized_concentration"` |

### 4. 边界与要求页

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.5` |
| 输入下限 | `input_min` | `0` |
| 输入上限 | `input_max` | `2` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `1.2` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `true` |
| 输出下限 | `output_min` | `0` |
| 输出上限 | `output_max` | `1` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "hold_duration_min_s"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.02` |
| 允许超过目标多少 | `overshoot_max` | `null` |
| 希望多少秒内稳定 | `settling_time_max_s` | `null` |
| 至少保持多少秒 | `hold_duration_min_s` | `10.0` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `null` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `false` |
| 响应时间偏好 (s) | `response_time_preference_s` | `null` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `["distinct_experiments", "cumulative_excitation_time_s"]` |
| 最多尝试几种实验 | `distinct_experiments` | `4` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `1800.0` |

### 5. 核对页

逐项核对目标/任务类型、主要输出与单位、输入上下限、输出边界、绝对值停止阈值和所勾选要求。实验预算显式为 4 种、累计 1800 s；Kernel 还补入澄清 6 轮、同故障重试 1 次、总耗时 7200 s，检查实际摘要。未勾选的性能指标没有额外保证。勾选“我已核对目标、软件试验边界与预算”，点击“确认软件边界并开始”。

### 6. 启动后的回复与操作

仅当“当前步骤回复”允许自然语言时，粘贴下方八项回复；后续只回答当前问题，不重复提交整个草稿。若要求实验，点击“下载协议”及“下载操作包”，在外部受控软件模拟器按该协议生成同任务、同版本、同通道和单位的数据；完整保留协议标识、时钟、边界、来源及停止信息。只有输入合同显示上传时才点“选择实验数据”并提交。当前文本没有提供这些文件，不能上传模型公式、旧样本或其他案例数据冒充。若要求操作员核对，仅依据实际协议完成并报告；无法完成则选择“需要澄清”或“拒绝执行”。

```text
以下只有来源数学结论和明确仿真假设，未生成或上传实验数据。不要把它们当作实测记录，也不要授予 Provider 权限。
1. open_loop_stability: 未知：原题计算/公式不等于该次任务回基线实测；需要稳定性证据.
2. nonminimum_phase: 来源模型先验：来源适应零点与运动积分器在配体到位置通道相消；这不产生可独立操纵的位置执行器.
3. significant_delay: 未知：缺少同一时钟下输入改变到首响应的记录.
4. relative_degree: 未知：完整状态维数不能直接冒充输入输出相对阶次.
5. sensing_actuation_adequacy: 来源模型先验：适配受体活动保持与原趋化位置目标不同，后者仍不支持.
6. nonlinearity_strength: 未知：需区分局部线性、静态非线性、滞环记忆及动态非线性.
7. coupling_underactuation: 来源模型先验：表中选定来源的标量通道；其他内部量未声明为传感器。通道数已知，物理解耦和欠驱动仍未验证.
8. uncertainty_variation: 未知：没有负载、工况或参数重复试验.
模型与范围：原题数值背景（仅为来源例算或待实施假设，尚未取得数据）：延续趋化示例，取 Ka=1、Kx=0.5、基线 w=0；配体阶跃 1 并积分平均位置。 来源模型方程（按原变量定义，仅作数学背景）：y_{\rm CheY}=K_a a ; \dot x=w+K_x(\bar y-y_{\rm CheY}) ; \delta y_{\rm CheY}=K_a\delta a,\qquad \delta\dot x=-K_xK_a\delta a.
未知项请保留未知，只按当前任务输入合同请求补充信息或新的协议绑定外部数据。
```

### 7. 预期阶段与结果

本条验收点是：草稿和 TaskContract 有效、八项信息能进入当前诊断流程，并如实生成补充/取证请求。没有匹配的外部协议数据时停在等待信息或等待外部数据；若 Kernel 明确判定路由、模型、测量或执行能力不支持，则记录能力边界及原因。两者都不是“性能达标”。只有该任务真实产生并通过冻结评价及新鲜独立确认的证据，才可按已勾选的容差和保持时间宣称性能达标；不以任意终态作为成功。

---

## 附录：独立注册案例操作示范

这些注册案例是框架自带的软件训练对象，不是上面同名原题的对象或验证结果。从案例列表选择原始案例，不粘贴第 1–200 题草稿，也不改锁定字段。表中的空预算选择仍产生 Kernel 默认预算 4 种实验、1800 s 激励、6 轮澄清、1 次重试、7200 s 总耗时。

### `dc_motor_speed_v1` — 01｜直流电机转速：电枢电压 → 转轴角速度

从案例列表选上方名称，核对下表中的完整原始草稿值（无需重新输入）；同时保留案例内原始 objective、operating_region、engineering_units 和来源绑定，不得转为自定义任务再冒称案例权限。

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"一台实验室直流电机工作在空载附近。我可以在驱动器允许范围内改变电枢电压，并用编码器记录转轴角速度。目标是在不超过电压和转速停止边界的前提下，让转速达到一个小幅目标并保持。当前没有可用的实验记录。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 输出行 [名称, 单位] | `outputs` | `[["转轴角速度_rad_s", "rad/s"]]` |
| 输入行 [名称] | `inputs` | `[["电枢电压_V"]]` |
| 输入单位 | `input_unit` | `"V"` |
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `20.0` |
| 输入下限 | `input_min` | `-6.0` |
| 输入上限 | `input_max` | `6.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `60.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `false` |
| 输出下限 | `output_min` | `null` |
| 输出上限 | `output_max` | `null` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "overshoot_max", "settling_time_max_s", "perturbed_success_rate_min"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `1.5` |
| 允许超过目标多少 | `overshoot_max` | `4.0` |
| 希望多少秒内稳定 | `settling_time_max_s` | `3.0` |
| 至少保持多少秒 | `hold_duration_min_s` | `null` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `0.8` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `2.0` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `[]` |
| 最多尝试几种实验 | `distinct_experiments` | `null` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `null` |

当前软件回归的明确预期路径：tuning_eligible → run_feedback_iteration → capability_gap（有界调优耗尽）。这是可检验预期；本次仍须运行并读取实际证据，失败不能改称性能达标。

选择“自动案例实验”，关闭 RAG，核对并确认开始。按当前步骤按钮运行协议、形成方案和评价；自动模式使用该案例专属软件 Provider。当前页面若要求补充信息，未知就如实回复未知。最终读取实际状态、失败原因与最终报告；不能预先承诺每个案例达到性能目标。

### `dc_motor_position_v1` — 03｜直流电机定位：电枢电压 → 转轴角度

从案例列表选上方名称，核对下表中的完整原始草稿值（无需重新输入）；同时保留案例内原始 objective、operating_region、engineering_units 和来源绑定，不得转为自定义任务再冒称案例权限。

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"一台实验室直流电机通过编码器测量转轴角度。我可以施加正负电枢电压，目标是让转轴从当前零点转到一个小角度并保持；若电压或角度超过边界必须停止。当前没有可用的实验记录。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 输出行 [名称, 单位] | `outputs` | `[["转轴角度_rad", "rad"]]` |
| 输入行 [名称] | `inputs` | `[["电枢电压_V"]]` |
| 输入单位 | `input_unit` | `"V"` |
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `0.5` |
| 输入下限 | `input_min` | `-6.0` |
| 输入上限 | `input_max` | `6.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `2.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `false` |
| 输出下限 | `output_min` | `null` |
| 输出上限 | `output_max` | `null` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "overshoot_max", "settling_time_max_s", "perturbed_success_rate_min"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.04` |
| 允许超过目标多少 | `overshoot_max` | `0.15` |
| 希望多少秒内稳定 | `settling_time_max_s` | `6.0` |
| 至少保持多少秒 | `hold_duration_min_s` | `null` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `0.8` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `4.0` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `[]` |
| 最多尝试几种实验 | `distinct_experiments` | `null` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `null` |

当前软件回归的明确预期路径：capability_gap：diagnostic_trial_only；特征不确定性过大，无法构造有界首次试验。这是可检验预期；本次仍须运行并读取实际证据，失败不能改称性能达标。

选择“自动案例实验”，关闭 RAG，核对并确认开始。按当前步骤按钮运行协议、形成方案和评价；自动模式使用该案例专属软件 Provider。当前页面若要求补充信息，未知就如实回复未知。最终读取实际状态、失败原因与最终报告；不能预先承诺每个案例达到性能目标。

### `tclab_single_heater_v1` — 02｜单加热器温控：功率变化 → 温升

从案例列表选上方名称，核对下表中的完整原始草稿值（无需重新输入）；同时保留案例内原始 objective、operating_region、engineering_units 和来源绑定，不得转为自定义任务再冒称案例权限。

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"一套桌面温控实验台在室温附近运行。我可以在当前偏置功率上下改变一号加热器功率，并记录一号温度传感器相对室温的温升。目标是在功率变化和温升停止边界内，把温升保持在目标值附近。当前没有可用的实验记录。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 输出行 [名称, 单位] | `outputs` | `[["一号温升_degC", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["一号加热功率变化_percentage_point"]]` |
| 输入单位 | `input_unit` | `"percentage_point"` |
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `8.0` |
| 输入下限 | `input_min` | `-20.0` |
| 输入上限 | `input_max` | `20.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `25.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `false` |
| 输出下限 | `output_min` | `null` |
| 输出上限 | `output_max` | `null` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "overshoot_max", "settling_time_max_s", "perturbed_success_rate_min"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.6` |
| 允许超过目标多少 | `overshoot_max` | `2.0` |
| 希望多少秒内稳定 | `settling_time_max_s` | `160.0` |
| 至少保持多少秒 | `hold_duration_min_s` | `null` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `0.8` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `120.0` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `[]` |
| 最多尝试几种实验 | `distinct_experiments` | `null` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `null` |

当前软件回归的明确预期路径：tuning_eligible → run_feedback_iteration → awaiting_confirmation → confirm_result → performance_met。这是可检验预期；本次仍须运行并读取实际证据，失败不能改称性能达标。

选择“自动案例实验”，关闭 RAG，核对并确认开始。按当前步骤按钮运行协议、形成方案和评价；自动模式使用该案例专属软件 Provider。当前页面若要求补充信息，未知就如实回复未知。最终读取实际状态、失败原因与最终报告；不能预先承诺每个案例达到性能目标。

### `quadruple_tank_nmp_v1` — 04｜四水箱通道：泵电压变化 → 下层液位变化

从案例列表选上方名称，核对下表中的完整原始草稿值（无需重新输入）；同时保留案例内原始 objective、operating_region、engineering_units 和来源绑定，不得转为自定义任务再冒称案例权限。

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"一套四水箱实验装置工作在固定液位偏置附近。我可以在偏置上下改变一号泵电压，并记录指定下层水箱相对工作点的液位变化；本练习不提供内部流量或上层水箱状态。目标是在泵电压和液位停止边界内保持一个小液位目标。当前没有可用的实验记录。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 输出行 [名称, 单位] | `outputs` | `[["下层水箱液位变化_cm", "cm"]]` |
| 输入行 [名称] | `inputs` | `[["一号泵电压变化_V"]]` |
| 输入单位 | `input_unit` | `"V"` |
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `2.0` |
| 输入下限 | `input_min` | `-2.0` |
| 输入上限 | `input_max` | `2.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `8.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `false` |
| 输出下限 | `output_min` | `null` |
| 输出上限 | `output_max` | `null` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "overshoot_max", "settling_time_max_s", "perturbed_success_rate_min"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.2` |
| 允许超过目标多少 | `overshoot_max` | `0.8` |
| 希望多少秒内稳定 | `settling_time_max_s` | `120.0` |
| 至少保持多少秒 | `hold_duration_min_s` | `null` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `0.8` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `80.0` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `[]` |
| 最多尝试几种实验 | `distinct_experiments` | `null` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `null` |

当前软件回归的明确预期路径：案例绑定取证和评价后 performance_met。这是可检验预期；本次仍须运行并读取实际证据，失败不能改称性能达标。

选择“自动案例实验”，关闭 RAG，核对并确认开始。按当前步骤按钮运行协议、形成方案和评价；自动模式使用该案例专属软件 Provider。当前页面若要求补充信息，未知就如实回复未知。最终读取实际状态、失败原因与最终报告；不能预先承诺每个案例达到性能目标。

### `tclab_dual_heater_v1` — 05｜双加热器温控：两路功率变化 → 两路温升

从案例列表选上方名称，核对下表中的完整原始草稿值（无需重新输入）；同时保留案例内原始 objective、operating_region、engineering_units 和来源绑定，不得转为自定义任务再冒称案例权限。

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"一套双加热器桌面温控实验台在室温附近运行。两路输入分别是两个加热器的功率变化，可以独立设置；两路输出是两个温度传感器相对室温的温升，可以同时记录。目标是在各自功率和温升边界内，让两个温升分别保持在同一个小幅目标附近。当前没有可用的实验记录。"` |
| 任务类型 | `task_type` | `"local_setpoint_hold"` |
| 输出行 [名称, 单位] | `outputs` | `[["一号温升_degC", "degC"], ["二号温升_degC", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["一号加热功率变化_percentage_point"], ["二号加热功率变化_percentage_point"]]` |
| 输入单位 | `input_unit` | `"percentage_point"` |
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `6.0` |
| 输入下限 | `input_min` | `-15.0` |
| 输入上限 | `input_max` | `15.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `20.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `false` |
| 输出下限 | `output_min` | `null` |
| 输出上限 | `output_max` | `null` |
| 开始区域 | `initial_region` | `""` |
| 目标区域 | `goal_region` | `""` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `false` |
| 初始输出值 | `initial_output_value` | `null` |
| 中间目标（逗号分隔） | `intermediate_targets` | `""` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "overshoot_max", "settling_time_max_s", "perturbed_success_rate_min"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.7` |
| 允许超过目标多少 | `overshoot_max` | `2.0` |
| 希望多少秒内稳定 | `settling_time_max_s` | `240.0` |
| 至少保持多少秒 | `hold_duration_min_s` | `null` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `0.8` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `40.0` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `[]` |
| 最多尝试几种实验 | `distinct_experiments` | `null` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `null` |

当前软件回归的明确预期路径：案例绑定取证和评价后 performance_met。这是可检验预期；本次仍须运行并读取实际证据，失败不能改称性能达标。

选择“自动案例实验”，关闭 RAG，核对并确认开始。按当前步骤按钮运行协议、形成方案和评价；自动模式使用该案例专属软件 Provider。当前页面若要求补充信息，未知就如实回复未知。最终读取实际状态、失败原因与最终报告；不能预先承诺每个案例达到性能目标。

### `tclab_single_heater_staged_transition_hold_v1` — 10｜单加热器：3 → 6 → 8 degC 分段保持

从案例列表选上方名称，核对下表中的完整原始草稿值（无需重新输入）；同时保留案例内原始 objective、operating_region、engineering_units 和来源绑定，不得转为自定义任务再冒称案例权限。

| 界面项目 | 字段标识 | 填写值 |
|---|---|---|
| 设备与目标 | `description` | `"一套桌面温控实验台在室温附近运行。我可以在当前偏置功率上下改变一号加热器功率，并记录一号温度传感器相对室温的温升。目标是在功率变化和温升停止边界内，把温升保持在目标值附近。当前没有可用的实验记录。"` |
| 任务类型 | `task_type` | `"transition_then_hold"` |
| 输出行 [名称, 单位] | `outputs` | `[["一号温升_degC", "degC"]]` |
| 输入行 [名称] | `inputs` | `[["一号加热功率变化_percentage_point"]]` |
| 输入单位 | `input_unit` | `"percentage_point"` |
| 设置参考目标（勾选） | `reference_enabled` | `true` |
| 参考目标 | `reference` | `8.0` |
| 输入下限 | `input_min` | `-20.0` |
| 输入上限 | `input_max` | `20.0` |
| 软件试验停止阈值（测量值绝对值） | `state_stop` | `25.0` |
| 设置输出边界（勾选） | `output_bounds_enabled` | `false` |
| 输出下限 | `output_min` | `null` |
| 输出上限 | `output_max` | `null` |
| 开始区域 | `initial_region` | `"温升接近 0 degC"` |
| 目标区域 | `goal_region` | `"温升 8 degC 附近"` |
| 填写初始输出值（勾选） | `initial_output_value_enabled` | `true` |
| 初始输出值 | `initial_output_value` | `0.0` |
| 中间目标（逗号分隔） | `intermediate_targets` | `"3.0, 6.0"` |
| 扰动事件 | `disturbance_event` | `""` |
| 恢复起点 | `recovery_start_condition` | `""` |
| 恢复后保持区域 | `disturbance_hold_region` | `""` |
| 性能要求：仅勾选列出的项 | `success_requirement_fields` | `["final_abs_error_max", "overshoot_max", "settling_time_max_s", "perturbed_success_rate_min"]` |
| 稳定后允许偏离目标多少 | `final_abs_error_max` | `0.6` |
| 允许超过目标多少 | `overshoot_max` | `2.0` |
| 希望多少秒内稳定 | `settling_time_max_s` | `160.0` |
| 至少保持多少秒 | `hold_duration_min_s` | `null` |
| 重复试验成功率下限 | `perturbed_success_rate_min` | `0.8` |
| 填写响应时间偏好（勾选） | `response_time_preference_enabled` | `true` |
| 响应时间偏好 (s) | `response_time_preference_s` | `120.0` |
| 实验预算：仅勾选列出的项 | `budget_fields` | `[]` |
| 最多尝试几种实验 | `distinct_experiments` | `null` |
| 累计激励时间上限 (s) | `cumulative_excitation_time_s` | `null` |

当前软件回归的明确预期路径：capability_gap 并保留阶段评价证据；记录失败阶段或交接原因。这是可检验预期；本次仍须运行并读取实际证据，失败不能改称性能达标。

选择“自动案例实验”，关闭 RAG，核对并确认开始。按当前步骤按钮运行协议、形成方案和评价；自动模式使用该案例专属软件 Provider。当前页面若要求补充信息，未知就如实回复未知。最终读取实际状态、失败原因与最终报告；不能预先承诺每个案例达到性能目标。

### 教学练习包下载和上传

用 `dc_motor_speed_v1` 新建另一任务，在核对页选择“教学练习包上传”，保留原始合同。确认后，仅在生成协议和练习包的阶段点击“下载练习包”。需要操作员核对时，按该任务显示的检查项逐项核对，并选择“检查完成，可以继续”；到上传阶段点击“选择实验数据”，选择刚刚生成、未修改的本任务 ZIP，然后按当前按钮提交。不要把练习包上传到别的会话、复用旧协议包或修改不合格数据。等待上传操作完整结束，不把中间 API 阶段当作操作结果。此锁定合同的 ZIP 通过后进入 `tuning_eligible`，显示“运行有界调优”；按该有界步骤继续，当前电机转速示范在调优预算耗尽后结束于 `capability_gap`，不算性能达标。其他任务若产生新确认协议，应另取该协议自己的全新练习包。

### 单加热器调优与 fresh confirmation

用 `tclab_single_heater_v1` 原合同及自动案例实验单独验证。初次评价不达标时，按当前步骤进入有界调优；每轮读取实际指标和预算。调优候选通过仍不等于完成：冻结最终控制器后必须按新的确认协议取得独立新数据，并核对确认使用的任务、控制器、工况、协议和评价绑定。失败或预算耗尽就保留失败及能力边界；不得重用调优数据伪装 fresh confirmation，也不得为了成功放宽原合同。
