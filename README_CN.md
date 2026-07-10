# Control Agent

[English README](README.md)

Control Agent 是一个面向非专家用户的控制系统自动化设计研究原型。当前实现聚焦 **Core-Feature-Driven Control (CFDC)**：从自然语言系统描述出发，完成结构化诊断、安全实验设计、确定性核心特征提取、保守控制器合成、在线增益微调和软件仿真验证。

这个项目不是硬件部署包。它目前适合用于结构化软件实验、合成 benchmark，以及 CFDC 工作流的早期验证。

## 项目状态清单

已勾选项目表示当前已有可执行的软件证据和自动化测试覆盖，不代表已经完成全部目标指标复现或真实硬件验证。

### 已完成

- [x] Stage 0 八字段结构化诊断和信息不足时的澄清问题生成。
- [x] 五类 archetype 分类，以及结构化 required features 和安全约束输出。
- [x] 可选的三层 14-card mechanism catalog，作为 supplemental audit labels；默认关闭，且不替代五类 canonical archetype。
- [x] 面向 operator 的 free-decay、ramp/step、pulse、hover-thrust、bounded-scan 安全实验计划。
- [x] step、modal、pulse、hover-thrust、inverse-response 和 coupling 特征的确定性提取。
- [x] Class I-V 保守控制器合成，以及明确的 tunable gain names。
- [x] 结构化 go/no-go 校验、bounded trial report、rollback 和 freeze 行为。
- [x] Cartpole 稳定演示：只使用自然频率的归一化能量摆起和非线性在线 PD 搜索。
- [x] Cartpole 外环位置 NMP 候选搜索：实际欠冲计算、逐级回退和长时 rollback 复验。
- [x] VTOL position 稳定演示：带符号横向耦合和经过二次试验验证的垂向增益更新。
- [x] VTOL NMP boundary 演示：实际欠冲计算、候选历史和回退到上一组安全横向增益。
- [x] VTOL mass/inertia 六场景 variation，对比 stale features 和 updated features。
- [x] Cartpole full-model 与 VTOL full-state LQR baseline，并统一 plant、初态、参考、时域和 actuator limits。
- [x] 主要通道的 final error、settling time、saturation、state boundary 和 rollback 后复验严格 gate。
- [x] 7-case 通用闭环 benchmark：typed `BenchmarkRouteIR` -> 实验 -> 特征 -> 控制器 -> 仿真 -> 性能裁判。
- [x] Class II/III 基于 `input_gain` 的 PD 定尺度，以及 Class I delay-aware PI de-tuning。
- [x] 8 个 prompt case + 4 个复杂 case 的离线诊断评测，包含保存响应，以及 archive 风格的 feature precision/minimality、constraint isolation、dangerous false-positive、evidence、executability、testability 和 missing-information 审计。
- [x] adapter 无关的诊断安全纠正和 release gate，覆盖显式 delay ambiguity、operating-point dependence、underactuated energy exchange 与强 MIMO/NMP 证据。
- [x] 带版本和 SHA-256 指纹的冻结 12-case 诊断规范，以及 deterministic/LLM response snapshot 与逐指标对比工具。
- [x] 一阶与双积分对象的 minimal-core/noisy/full-model 参数化 feature ablation。
- [x] `python main.py --validate-demo` 对 Cartpole、VTOL position、VTOL boundary、VTOL variation 的确定性验证。
- [x] 统一的软件仿真性能摘要，覆盖最终误差、超调、稳定时间、饱和、捕获、分通道状态、边界和违规原因。
- [x] Python 3.11/3.13 CI、`.[test]` editable 安装和自动化回归测试。

### 未完成

- [ ] 复现论文中的 Cartpole 19-20% 欠冲数值；当前软件搜索执行 20% 拒绝阈值，但未复现该精确数值。
- [ ] 复现 VTOL 目标结果：14% undershoot 和 3.1 s settling time。
- [ ] 长期 natural-frequency FLL tracking 和每 30 s 的 `k_theta` RLS 更新。
- [ ] 连续 payload-change adaptation 与长期 hover-thrust、`k_theta` tracking；当前已实现六场景 stale/updated 对照。
- [ ] `vtol-altitude` 和 `vtol-hover` 的默认稳定验证。
- [ ] 独立 Class V MIMO plant 及其闭环 controller validation。
- [ ] 在初始 feature ablation 之外增加噪声、扰动、参数扫描和重复试验。
- [ ] 真实实验 CSV/JSON 导入、硬件审批、actuator deployment 和物理验证。
- [ ] 真实 LLM response snapshot；live comparison 命令已经实现，但仓库和默认环境中没有 API 凭据。

### 需要改进

- [ ] 在保持直立 handoff 和轨道边界的同时，降低 Cartpole actuator saturation。
- [ ] 继续改善 VTOL position settling time 以接近论文指标；当前已增加明确的 settling-time 验收阈值。
- [ ] 将手工给定的 boundary candidate 序列替换为可复用的约束搜索策略。
- [ ] 通过重复试验、滤波校验和数据质量拒绝规则强化 confidence interval。
- [ ] 让实验幅值和持续时间真正依赖 diagnosis、time-scale hint、forbidden actions 和 safety bounds。
- [ ] 增加持久化多轮诊断状态，并评测一个或多个已配置 LLM API 的保存响应。
- [ ] 增加 evidence ledger，包括原始数据哈希、配置版本和 claim-boundary summary。
- [ ] 为所有稳定和实验性 route 生成紧凑的机器可读报告与 operator-facing 报告。

## 设计原则

- LLM 只负责 Stage 0 的语言理解和结构化诊断。
- 数值控制逻辑全部由确定性 Python 代码实现。
- 运行时接口使用 Pydantic model 和 JSON-compatible dictionary，不依赖自由文本。
- 不做完整参数辨识，只提取 CFDC 当前 route 所需的 scalar core features。
- 每条 route 都输出可审计 artifact，例如 `go_no_go`、`evidence_boundary`、features、controller candidate 和 trial report。

## CFDC 流程

当前 runtime 遵循六段式闭环：

1. **Stage 0: AI Diagnostic Engine and Language Understanding**
   - 读取非专家自然语言系统描述。
   - 如果信息不足，生成澄清问题。
   - 填写八个结构诊断字段：`open_loop_stability`, `minimum_phase`, `significant_delay`, `relative_degree`, `controllability_observability`, `nonlinearity_strength`, `coupling_severity`, `uncertainty_magnitude`。

2. **Stage 1: Structural Diagnosis and Archetype Classification**
   - 将系统映射到五类 CFDC canonical class。
   - 输出推荐控制架构、required core features 和安全约束。
   - 用户可显式启用 mechanism-card supplemental labels，用于审计与解释；该可选层不改变 canonical class、required features、安全约束、实验 route 或 controller。

3. **Stage 2: Safe Experiment Design**
   - 生成面向 operator 的安全实验说明。
   - 支持 free decay、ramp/step、pulse、hover-thrust、bounded scan 等实验 primitive。

4. **Stage 3: Core Feature Extraction**
   - 从结构化实验 trace 中提取 scalar core features。
   - 使用 matched-filter-style frequency lock、low-pass steady-state detection、pulse integration、ratio estimation 等确定性估计器。
   - 输出 feature value、confidence bounds 和 data-quality flags。

5. **Stage 4: Conservative Controller Synthesis**
   - 根据提取到的 features 合成保守初始 controller。
   - 按 canonical class 使用 de-tuning、saturation、cascaded architecture、online gain search 或 MIMO pairing。

6. **Online Optimization and Adaptation**
   - 每次只做 5-10% 小幅 gain refinement。
   - 监测 overshoot、settling time、integral absolute error、high-frequency control RMS、actuator saturation 和 inverse-response undershoot。
   - 违反约束时 rollback，并在配置的长时域内再次验证。
   - 运行确定性的 VTOL mass/inertia variation，对比 stale features 与从变化后软件 plant 重新提取的 features。

## 项目结构

```text
.
├── cfdc/
│   ├── diagnosis/
│   ├── experiments/
│   ├── features/
│   ├── controllers/
│   ├── online/
│   ├── runtime/
│   ├── sim/
│   ├── models/
│   ├── performance.py
│   ├── pipeline.py
│   └── validation.py
├── tests/
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── README_CN.md
```

## 主要模块

### `cfdc/models/`

`cfdc/models/schemas.py` 定义项目中的公开结构化 artifact：

- `SystemDescription`: 用户描述、观测量、执行器和安全边界。
- `StructuralDiagnosis`: Stage 0 诊断字段和澄清问题。
- `ArchetypeClassification`: canonical class、控制架构、required features、constraints 和可选 supplemental mechanism-card labels。
- `ExperimentPlan`, `ExperimentInstruction`: 安全实验计划。
- `ExperimentTrace`, `ExperimentResult`: 结构化实验数据。
- `CoreFeatureArtifact`: 带 confidence 和 data-quality metadata 的 scalar feature 输出。
- `ControllerCandidate`: controller architecture、gains、明确的 tunable gain names、feedforward、saturation 和 constraints。
- `OnlineTuningState`, `SafeGainSearchState`, `FeatureTrackingUpdate`: online refinement 和 adaptation 状态。
- `TrialReport`: bounded safe trial 执行报告。
- `ChannelPerformanceMetrics`, `SimulationPerformanceSummary`: 类型化的分通道与 route 级性能报告。
- `CartpoleSimulationResult`, `VtolSimulationResult`: 保留兼容 `metrics` 并新增结构化 `performance` 输出的软件仿真结果。
- `CartpoleBoundaryResult`, `VtolVariationResult`: 结构化 NMP 搜索/rollback 和六场景 variation artifact。
- `ControllerComparison`: 同条件 CFDC/LQR 性能对照。
- `BenchmarkRouteIR`, `ClosedLoopBenchmarkCaseResult`: 类型化通用 benchmark route 与闭环结果。
- `DiagnosticEvaluationResult`, `FeatureAblationResult`: 离线诊断评分与结构化 feature ablation 结果。
- `CFDCRunReport`: `run_cfdc_route()` 的端到端 route report。
- `GoNoGoDecision`: route、class、required features 的 deterministic validation 结果。

所有模型都继承自 `CFDCModel`，默认禁止额外字段和非有限浮点数，并支持 JSON round trip。

### `cfdc/diagnosis/`

这一层实现 Stage 0 和 Stage 1。

- `engine.py` 通过 `infer_structural_diagnosis()` 提供本地 deterministic diagnostic adapter。
- `classify_archetype()` 将八个诊断字段映射到 CFDC canonical classes。
- `mechanism_cards.py` 加载并校验完整的三层 14-card catalog，并确定性选择可选 supplemental labels。catalog 默认关闭，labels 不替代或修改 canonical archetype route。
- `control_mechanism_card_catalog.json` 保留 catalog metadata、evidence boundary、card roles、机制说明和 layer membership。
- `llm.py` 提供 `OpenAICompatibleDiagnosticAdapter`，通过 OpenAI Python SDK 调用 OpenAI-compatible `/chat/completions` API，并要求模型返回严格 JSON。它只用于语言诊断，不负责数值 controller synthesis。
- `evaluation.py` 在 8+4 case catalog 上分别评分八字段、required-feature recall/precision/minimality、constraint isolation、dangerous false-positive control、evidence discipline、missing-information quality、experiment executability、controller testability、archetype 分类和 controller-release gate；同时明确报告多余特征及被误选为核心特征的约束。`saved_evaluation_responses.json` 用于可重复的离线评分。
- `safety.py` 在所有 adapter 之后统一应用 description-evidence rules 和 controller-release gate，因此 LLM 与 deterministic diagnosis 共用同一 fail-closed 边界。
- 12-case catalog 与 archive-audit 评分规则冻结为 `cfdc-diagnostic-12-v2-archive-audit` 并绑定 SHA-256 指纹；catalog、评分策略、成员或顺序不一致的 snapshot 会被拒绝。

LLM 环境变量：

```bash
export CFDC_LLM_BASE_URL="https://api.openai.com/v1"
export CFDC_LLM_MODEL="gpt-4o-mini"
export CFDC_LLM_API_KEY="..."
```

### `cfdc/experiments/`

`planner.py` 通过 `plan_safe_experiments()` 实现 Stage 2。每个 `ExperimentInstruction` 包含 primitive、operator steps、需要记录的信号、要估计的 features、stop conditions 和 safety note。

### `cfdc/features/`

这一层用确定性的 NumPy/SciPy/Python extractor 实现 Stage 3。低通递推、periodogram 和衰减峰检测使用 SciPy；CFDC 特定的 matched-filter refinement、特征公式、confidence bounds 和 data-quality rules 仍在项目中显式实现。

核心函数包括：

- `estimate_natural_frequency()`
- `estimate_damping_ratio()`
- `estimate_step_features()`
- `estimate_dead_time()`
- `estimate_inverse_response_severity()`
- `estimate_pulse_input_gain()`
- `estimate_hover_thrust()`
- `estimate_coupling_gain()`

`dispatcher.py` 会把 `ExperimentResult` 分发到对应 extractor，并处理常见信号别名。

### `cfdc/controllers/`

`synthesis.py` 通过 `synthesize_controller()` 实现 Stage 4。

当前支持的 synthesis 分支：

- Class I: `detuned_PI`
- Class II: `detuned_PD`
- Class III: `small_saturated_PD`
- Class IV stable inverse-response process: `detuned_PI_with_NMP_undershoot_guard`
- Class IV unstable pendulum-like process: `safe_online_gain_search`
- Class IV VTOL-like process: `cascaded_PD_with_hover_feedforward`
- Class V: `conservative_mimo_pairing`

controller synthesis 前会先校验 required features，因此不完整输入会返回结构化错误，而不是运行时 `KeyError`。
Class II/III 的 PD gains 使用实测 `input_gain` 定尺度；Class I 在存在 delay 时使用 `dead_time/time_constant` 进一步降调。
Class V loop pairing 使用 SciPy 的全局最大权重 linear assignment，不再逐行贪心选择，并会把未配对通道标记为需要 centralized review。

### `cfdc/online/`

`refinement.py` 复用统一的 channel-performance 计算，并实现保守 gain increments、rollback/freeze、unstable plant 的 safe gain search，以及 tracked-feature adaptation。

### `cfdc/runtime/`

这一层把 Stage 0-4、online refinement 和 simulation 连接成可执行 route。

- `trial.py`: `SafeTrialRunner`，bounded software trial executor。
- `safety.py`: sample-level safety checks。
- `orchestrator.py`: `run_cfdc_route()`，端到端 route 入口。

稳定演示 route：

- `cartpole`
- `vtol-position`
- `vtol-boundary`
- `vtol-variation`

实验性 route：

- `generic`
- `cartpole-boundary`（显式 Cartpole boundary route；当前执行与 `cartpole` 相同的完整协议）
- `vtol-altitude`
- `vtol-hover`

### `cfdc/validation.py`

这个模块提供 deterministic gates：

- `validate_route_compatibility()`
- `validate_required_features()`
- `merge_go_no_go()`

这些 gate 会把 route/class mismatch 和 missing features 保持为结构化 no-go report。

### `cfdc/sim/`

这一层包含软件 plant 和 synthetic benchmarks。

- `cartpole.py`: cartpole / inverted-pendulum plant、外环位置 NMP 搜索、长时 rollback 复验和 full-model LQR baseline。
- `vtol.py`: planar VTOL plant、full-state LQR baseline 和 mass/inertia variation。横向输出采用相对质心有固定偏置的测量点，使软件对象能够呈现 boundary 演示所需的 RHP-zero 反向响应。
- `generic.py`: first-order、delay、double-integrator、oscillator 和 inverse-response route 的共享标量闭环 plant 与统一 performance gate。
- `benchmarks.py`: 7 个 typed benchmark route 和结构化 feature ablation；Cartpole/VTOL 复用已有 simulation module。
- `integrators.py`: control input 保持不变时使用的共享 fixed-step RK4 积分器。
- `traces.py`: 共享的 synthetic step、modal、pulse、hover 和 coupling trace。

Cartpole reference LQR 路径使用 SciPy 求解 continuous algebraic Riccati equation，不再手工恢复 Hamiltonian stable eigenspace。

每个 Cartpole 和 VTOL 仿真都会输出主通道字段，包括 `final_error`、`abs_final_error`、`overshoot`、`settling_time_s`、`final_output`、`saturation_fraction` 和 `success`。结构化 `performance` 还会给出全部输出通道、各执行器饱和比例、状态边界、配置限制、捕获状态和违规原因。主要 route 会拒绝 final error 或显式 settling-time 超限、saturation/state boundary 超限，以及 rollback 长时复验失败的响应。

## 使用 Conda 安装

conda 只用于创建和激活 Python 环境。所有 Python 包统一使用 pip 安装。

```bash
conda create -n control-agent python=3.11 -y
conda activate control-agent
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
```

项目要求 Python 3.11 或更高版本。

## 快速检查

```bash
python -m compileall cfdc tests main.py
python -m pytest
python main.py --benchmark
python main.py --validate-demo
```

## CLI 示例

运行 benchmark suite：

```bash
python main.py --benchmark
```

该 benchmark 会让 7 条 route 全部经过 diagnosis、experiment planning、feature extraction、controller synthesis、closed-loop simulation 和统一 performance judge。每条结果都会报告 `closed_loop_executed=true` 及 execution backend。

运行 feature ablation 和离线诊断评测：

```bash
python main.py --feature-ablation
python main.py --diagnostic-eval
python main.py --diagnostic-eval-current
python main.py --diagnostic-eval-llm
python main.py --diagnostic-eval-llm-saved
```

`--diagnostic-eval` 重放保存的 deterministic responses；`--diagnostic-eval-current` 评测当前 deterministic engine 的新 snapshot。`--diagnostic-eval-llm` 会用相同的冻结 12 cases 调用已配置 API，仅保存结构化诊断 artifact，并对比全部诊断及 archive-audit 指标。可用 `--diagnostic-llm-output PATH` 指定 snapshot 路径；`--diagnostic-eval-llm-saved` 不再次调用 API，直接重放保存结果。

验证稳定软件演示 route：

```bash
python main.py --validate-demo
```

运行 route-level simulation：

```bash
python main.py --run-route cartpole
python main.py --run-route cartpole-boundary
python main.py --run-route vtol-position
python main.py --run-route vtol-boundary
python main.py --run-route vtol-variation
```

运行 generic pipeline：

```bash
python main.py \
  --description "A first order temperature process settles after a small heater change." \
  --observed-output temperature \
  --actuator heater
```

显式启用 supplemental mechanism-card labels：

```bash
python main.py --run-route cartpole --use-mechanism-cards
```

不传 `--use-mechanism-cards` 时，`classification.supplemental_mechanism_cards` 固定为空列表。程序接口同样要求在 `DiagnosticEngine`、`run_cfdc_pipeline()` 或 `run_cfdc_route()` 显式传入 `use_mechanism_cards=True`。

运行 LLM-assisted diagnosis：

```bash
python main.py \
  --use-llm \
  --description "A rod on a cart falls over when upright. I can measure cart position and rod angle." \
  --observed-output "cart position" \
  --observed-output "rod angle" \
  --actuator "cart motor force"
```

输出完整 route report：

```bash
python main.py --run-route cartpole --full-report
```

包含模拟 trajectory 输出：

```bash
python main.py --run-route cartpole --include-trajectory
```

## 测试

测试覆盖：

- Pydantic model round trip、diagnosis 和 classification。
- 完整 mechanism-card catalog 校验、默认关闭、确定性 opt-in labels，以及启用后 controller synthesis 不变的验证。
- 安全实验设计、feature extraction、不完整 feature 的 no-go behavior。
- feature-scaled/delay-aware controller synthesis、safe gain search、rollback/freeze、feature tracking 和 MIMO pairing。
- runtime safety check 和 `SafeTrialRunner`。
- Cartpole/VTOL route report、NMP rollback history、variation scenarios 和 LQR comparison。
- 7-case 闭环 benchmark、参数化 feature ablation 和 8+4 离线诊断评分。

运行测试：

```bash
python -m pytest
```

## 当前验证快照

最近的软件原型本地验证快照：

```text
python -m compileall cfdc tests main.py
tests passed=95

cartpole      completed go True NMP boundary / rollback verified
vtol-position completed go True accepted
vtol-boundary completed go True boundary_triggered / nmp_undershoot
vtol-variation completed go True 6 / 6 expectations met
demo          4 / 4 stable routes passed
benchmark     7 / 7 generic closed-loop cases passed
ablation      2 cases / 6 trials, expected comparisons passed
diagnosis     12 / 12 strict archive-audit cases passed, 0 premature releases or dangerous false-positive controls detected
```

这说明稳定演示 route 可以确定性复现，但不代表已经完成全部目标指标复现或真实硬件验证。

## 已知边界

- `vtol-altitude` 和 `vtol-hover` route 可以运行 CFDC controller，但默认仿真 metric 仍可能返回 `metric_limit`。
- `vtol-variation` 会针对变化后的软件 plant 分别重新提取 features；它不等价于连续飞行中的 hover-thrust 或 `k_theta` tracking。
- natural-frequency continuous tracking 还不是完整长期 small-dither FLL 实现。
- VTOL `k_theta` RLS tracking 还没有集成为长期 route-level closed loop。
- MIMO 当前有 pairing 和 decoupling synthesis，但还没有专门的 MIMO plant simulation。
- 共享 gate 已阻止此前检测到的三类错误放行。复杂 CSTR、Acrobot 和 matrix-valued MIMO route 仍仅生成实验计划，因为相应 deterministic controller synthesis 尚未实现。
- 当前尚未提交真实 LLM comparison snapshot；`--diagnostic-eval-llm` 需要 API 凭据，并会在结构化 artifact 中记录 model 与 prompt version。
- 真实实验日志导入、硬件审批和 actuator command deployment 尚未实现。

## 建议下一步

1. 使用可复用的受约束候选策略复现论文中的 Cartpole 19-20% 欠冲数值。
2. 复现 VTOL 14% undershoot / 3.1 s settling。
3. 将六场景 payload study 扩展为长期 hover-thrust 与 `k_theta` tracking。
4. 运行并保存 LLM response snapshot，与冻结 deterministic baseline 对比。
5. 增加噪声、扰动、参数扫描和重复统计实验。
6. 将真实实验 CSV/JSON 日志导入 `ExperimentResult`。
