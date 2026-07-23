# Control Agent

[English README](README.md)

本仓库是 Core-Feature-Driven Control（CFDC）流程的独立软件实现。项目当前只有软件仿真，不接入实体机器、不读取物理实验日志，也不部署 actuator command。

## 工作流程

```text
自然语言控制问题
-> 严格八字段结构诊断
-> 信息不足时澄清
-> 确定性归入五类 canonical archetype
-> 从版本化方法 Profile catalog 中进行受约束语义选择
-> 针对当前对象追问设备规格
-> 将明确数值和单位确定性编译为对象专属近似模型
-> 从该模型响应中提取最小核心特征
-> 生成对象专属、尚未验证的参数候选
-> 后续真实对象调试（本轮不实现）
```

LLM 只负责自然语言理解、闭 catalog 语义选择，以及把用户明确给出的规格整理为严格事实。它不能估算缺失数值、使用标准对象参数补空、创造 feature ID、动力学方程或控制器增益。单位校验、派生公式、模型编译、特征提取和参数计算均由确定性 Python 实现。

八字段完整只代表结构诊断完成。自然语言主流程此时停在 `awaiting_specifications`，不会调用标准 Profile simulator、特征提取、控制器合成、Algorithm 1 或在线适应。普通用户可以回答针对其设备生成的 1–4 个规格问题或粘贴手册；高级用户可以提供完整数值模型；标准对象必须由用户显式选择演示。

八个诊断字段分别采用严格枚举：稳定性、相位、时延、相对阶次、能控能观性、非线性、耦合和不确定性。五类分类器只读取这些 assessment，不读取解释文字做路由。

## 项目结构

| 路径 | 实现功能 |
| --- | --- |
| `cfdc/` | 当前生效的 Python package。顶层模块提供程序化 pipeline、通用校验、性能指标和 demo 入口，下面各子包分别负责工作流阶段。 |
| `cfdc/web/service.py` | Gradio 应用服务层，负责校验表单、维护澄清 session，并调用共享 runtime。 |
| `cfdc/web/presentation.py` | 将类型化报告转换成阶段表格、状态摘要、性能对比视图和紧凑审计 JSON。 |
| `cfdc/web/ui.py` | 定义 Gradio 页面、CSS、UI 回调和事件绑定。 |
| `cfdc/models/` | 定义各阶段共享的严格 Pydantic 数据契约，包括八字段诊断、profile catalog、仿真实验记录、核心特征、控制器、调优状态、tracking 状态和最终报告。 |
| `cfdc/diagnosis/` | 实现 Stage 0 自然语言诊断、OpenAI-compatible LLM adapter、严格响应校验、五类归类、澄清 session、安全检查及离线诊断评测。 |
| `cfdc/specifications/` | 定义 Class I–V、CartPole 和 VTOL 的允许规格路径，生成对象化问题，校验显式事实并确定性编译近似模型。 |
| `cfdc/evidence/` | 校验完整数值模型、执行用户模型响应、绑定对象/证据哈希，并在用户指标完整时执行闭环模型验证。实测 CSV 后端保留给后续调试，本轮不作为前置入口。 |
| `cfdc/workflow/` | 分离版本化方法 Profile 与 Demo Plant Fixture，并实现 candidate route、能力声明、确定性 route 编译及闭集语义选择校验。 |
| `cfdc/experiments/` | 根据 profile 将安全实验模板参数化并生成实验计划；实际实验记录由仿真器内部自动产生。 |
| `cfdc/sim/` | 实现确定性软件对象和实验后端，包括标量原型、CartPole、VTOL、2x2 MIMO trace、benchmark、参数变化场景及 stale/adapted 对照。 |
| `cfdc/features/` | 将实验 trace 分派给数值 extractor、聚合重复实验、保留 trace hash 并执行 feature quality gate。该模块不会读取自然语言 description 做特征匹配。 |
| `cfdc/controllers/` | 根据质量门放行的核心特征生成保守控制器，包括 PI/PD、非线性/级联模板、MIMO pairing 和半强度解耦。 |
| `cfdc/online/` | 实现 Algorithm 1、安全增益候选、dwell 评估、rollback/freeze、FLL/RLS/hover tracking，以及基于特征变化的控制器更新。 |
| `cfdc/runtime/` | 端到端编排与 bounded trial 执行，将诊断、路由、自动实验、质量门、控制器合成、调优和在线适应连接起来。 |
| `cfdc/pipeline.py` | 面向 Python 调用方的轻量程序接口，用于不经过 CLI 直接调用 CFDC 阶段。 |
| `cfdc/performance.py` | 各仿真后端共用的通道性能和闭环性能指标计算。 |
| `cfdc/validation.py` | route 兼容性、核心特征完整性和 go/no-go 等跨阶段校验。 |
| `tests/` | 单元、集成、CLI、Class I-V 端到端、实验重试/失败、Algorithm 1、tracking、CartPole、VTOL 和 Class V 回归测试。 |
| `dataset/` | 200 条控制问题的知识文档和提示语料。文档中的符号“数学模型”不等于参数完整、可执行的用户对象模型，本轮不会把这些 Markdown 方程接入运行时。 |
| `docs/` | 当前 simulation-first 架构的设计说明和迁移记录。 |
| `archive/` | 仅供历史参考的旧实现，当前运行时代码不得导入。 |
| `outputs/` | 本地生成的报告和仿真输出，不属于源代码并被 Git 忽略。 |
| `tmp/` | 开发或验证过程中的可丢弃临时数据，被 Git 忽略且运行时不会导入。 |
| `main.py` | 自然语言入口、诊断 session、开发验证 route、benchmark 和评测的 CLI 入口。 |
| `app.py` | 轻量 Gradio 启动入口，只负责解析服务参数并启动 `cfdc.web.ui` 中定义的页面。 |

## 仿真 Profile

论文中的五类动力学原型仍是唯一分类。Profile 只是每类内部的仿真实现路由：

- Class I：一阶惯性，可带显著时延。
- Class II：二阶振荡器。
- Class III：纯积分或双积分。
- Class IV：逆响应、通用不稳定/高阶、欠驱动 CartPole、级联 VTOL。
- Class V：通用 2x2 强耦合对象，使用矩阵特征、全局 pairing 和半强度静态解耦。

方法 Profile 只声明所需特征、信号和控制器模板，不再携带用户对象数值。能够由白名单规格模板表达的对象，可由用户明确规格编译近似模型；无法覆盖的高阶或不稳定对象必须停下并要求完整数值模型。CartPole、VTOL 和标准标量对象只保留为显式 Demo Fixture，结果固定标记 `demo_fixture_only`。

## 运行

安装并测试：

```bash
python -m pip install -e '.[test]'
pytest -q
python main.py --validate-demo
```

启动 Gradio 应用：

```bash
python app.py
```

浏览器访问 `http://127.0.0.1:7860`。应用与 CLI 使用同一条确定性流程，按“结构诊断 → 规格模型 → 核心特征 → 参数候选 → 效果验证”展示状态。八字段完成后，页面默认显示自然语言规格对话，并同时提供完整数值模型和标准对象演示两个可选入口；初始阶段不展示 CSV 上传。审计 JSON 位于独立标签页。需要监听其他网卡或端口时使用 `python app.py --host 0.0.0.0 --port 7860`。

默认运行方式是自然语言主流程，可以使用配置好的 LLM 诊断用户输入。CartPole 和 VTOL 属于开发验证场景，始终使用预注册 description、诊断和 profile，绝不会调用 LLM，也会在后端忽略自然语言表单。切换到开发验证时表单只会暂时禁用而不会清空，切回主流程后用户草稿仍然保留。

先从自然语言完成结构诊断并获得对象化规格问题：

```bash
python main.py \
  --description "一个一阶温度过程在加热功率改变后会逐渐稳定。" \
  --observed-output temperature \
  --actuator heater
```

继续提交已知规格（可重复使用 `--specification-answer`）：

```bash
python main.py \
  --description "一个一阶温度过程在加热功率改变后会逐渐稳定。" \
  --observed-output temperature \
  --actuator heater \
  --specification-text "手册：input_change=1 kW; steady_output_change=10 degC; response_time_s=30 s; input_min=0 kW; input_max=2 kW; output_min=-20 degC; output_max=80 degC"
```

无 LLM 时也可以在 Web 中按当前问题顺序逐行填写“数值 + 单位”；CLI 的内部字段写法主要用于脚本化和审计。由自然语言规格编译的结果始终标记 `declared_specification_model_only`，控制器始终为 `candidate_unvalidated`，即使规格近似模型的响应正常，也不表示真实对象已经验证。

所有数值规格都必须带单位，但界面列出的单位只是示例而不是有限白名单。常见写法会归一化并换算到规范单位（例如 `rad/s²` → `rad/s^2`、`1000 mV` → `1 V`、`100 ms` → `0.1 s`）；设备自己的命令或传感器单位（例如 `DAC_count`）也可以使用，只要同一组输入或输出规格保持一致。缺少单位时流程会继续追问；自定义单位混用时会要求换算关系；质量、时间、加速度等物理参数仍执行量纲检查。

高级用户可以使用 `--model-spec model.json` 提供完整数值传递函数、状态空间模型或白名单非线性模板。只有同时提供 `--validation-spec validation.json`，才会在该用户模型及其安全边界、场景和性能指标下产生 `validated_in_simulation`。使用 `--demo-fixture` 会显式运行标准对象，且不能与用户规格或模型同时使用。

使用 OpenAI-compatible LLM 完成结构化诊断和受约束 profile 选择：

```bash
# 三项配置共同指定实际服务商，并不限定为 OpenAI 或 GPT。
export CFDC_LLM_BASE_URL="https://your-provider.example/v1"
export CFDC_LLM_API_KEY="..."
export CFDC_LLM_MODEL="your-provider-model"

python main.py --use-llm \
  --description "小车上的杆在直立时会倒下，可以测量小车位置和杆角度。" \
  --observed-output "cart position" \
  --observed-output "rod angle" \
  --actuator "cart motor force"
```

`CFDC_LLM_BASE_URL` 应指向服务商的 OpenAI-compatible API 根路径，通常以 `/v1` 结尾，不必写成 `/chat/completions`；adapter 会兼容并规范化这两种形式。配置优先级依次为 CLI 参数、`CFDC_LLM_*`、`CONTROL_PROJECT_LLM_*`、标准 `OPENAI_*` 环境变量。

也可以完全通过命令行指定非 GPT 服务：

```bash
python main.py --use-llm \
  --llm-base-url "https://api.deepseek.com/v1" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "一个弹簧质量系统在施加力脉冲后会振荡。" \
  --observed-output position \
  --actuator force
```

使用 Ollama 等本地 OpenAI-compatible 服务时：

```bash
export CFDC_LLM_BASE_URL="http://localhost:11434/v1"
export CFDC_LLM_MODEL="qwen2.5:14b"
export CFDC_LLM_API_KEY="ollama"
```

项目根目录的 [`.env.example`](.env.example) 是与服务商无关的配置模板。CLI 不会自动加载 `.env`，需要在 shell 中 export（或开启 shell 自动导出后 source），也可以直接使用上述 CLI 参数。

开发验证用的内置 route 不需要 LLM：

```bash
python main.py --run-route cartpole
python main.py --run-route vtol-position
python main.py --run-route vtol-boundary
python main.py --run-route vtol-variation
python main.py --benchmark
python main.py --diagnostic-eval
```

`SimulationExperimentRecord` 是受审计模型或数据适配器产生的内部载体。用户不能直接上传核心特征。`--trace-manifest` 后端暂时保留给后续真实调试集成，但 Gradio 前置规格阶段不会要求普通用户上传 CSV 或重复做实验。

## 澄清 Session

为不完整描述创建 session：

```bash
python main.py --description "我有一台机器。" \
  --diagnostic-session-output session.json
```

报告会给出稳定 question ID。恢复时可以回答问题，也可以补充一段新描述：

```bash
python main.py --diagnostic-session-input session.json \
  --diagnostic-answer "q_1234567890=小输入后输出会逐渐稳定。" \
  --diagnostic-session-output session.json

python main.py --diagnostic-session-input session.json \
  --diagnostic-description "这是一个由加热器驱动、可以测量温度的热过程。" \
  --diagnostic-session-output session.json
```

结构诊断完成后，同一个 schema v3 session 保存规格模板、历次自然语言回答、已确认事实、缺口/冲突和编译模型哈希。可继续使用：

```bash
python main.py --diagnostic-session-input session.json \
  --specification-answer "input_change=1 kW" \
  --specification-answer "steady_output_change=10 degC" \
  --diagnostic-session-output session.json
```

旧 schema v1/v2 的完整会话会迁移到 `awaiting_specifications`，不会恢复旧控制器放行状态。

## 证据边界

报告会明确区分：`structural_diagnosis_only`、`declared_specification_model_only`、`user_object_model_validated_in_simulation` 和 `demo_fixture_only`。自然语言规格只能产生未验证候选；完整用户数值模型也只有在用户验证条件齐全且仿真通过时，才能声明“在用户模型中验证”。任何状态都不声明实体机器安全或物理验证，软件也不会向硬件下发控制命令。

后续研究仍包括：精确复现论文中的 CartPole/VTOL 数值指标、更长期的 tracking、更多噪声与扰动扫描，以及更多经过验证的 Class IV/V profile backend。

## 许可证

Copyright (C) 2026 Yichuan Huang.

本项目是采用 [GNU Affero General Public License v3.0 only](LICENSE)（`AGPL-3.0-only`）发布的自由软件。该许可证允许商业使用，但必须遵守许可证条款。分发修改版，或通过网络向用户提供修改版服务时，必须按照 GNU AGPLv3 提供对应源码。规范源码仓库为 [github.com/yichuan-huang/control-agent](https://github.com/yichuan-huang/control-agent)。完整且具有约束力的条款以 [LICENSE](LICENSE) 英文原文为准。
