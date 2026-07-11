# Control Agent

[English README](README.md)

本仓库是 `IEEE TCST.pdf` 中 Core-Feature-Driven Control（CFDC）流程的独立软件实现。项目当前只有软件仿真，不接入实体机器、不读取物理实验日志，也不部署 actuator command。

## 工作流程

```text
自然语言控制问题
-> 严格八字段结构诊断
-> 信息不足时澄清
-> 确定性归入五类 canonical archetype
-> 从版本化仿真 profile catalog 中进行受约束语义选择
-> 自动执行安全仿真实验（默认 3 次，质量不足时最多 5 次）
-> 确定性提取最小核心特征
-> 生成保守初始控制器
-> 使用 Algorithm 1 进行受约束闭环调优
-> 模拟系统变化后的特征跟踪与控制器适应
```

LLM 只负责自然语言理解和闭 catalog 的语义选择，不能创造 feature ID、实验、控制器、动力学方程或增益。所有数值计算均由确定性 Python 实现。

八个诊断字段分别采用严格枚举：稳定性、相位、时延、相对阶次、能控能观性、非线性、耦合和不确定性。五类分类器只读取这些 assessment，不读取解释文字做路由。

## 项目结构

| 路径 | 实现功能 |
| --- | --- |
| `cfdc/` | 当前生效的 Python package。顶层模块提供程序化 pipeline、通用校验、性能指标和 demo 入口，下面各子包分别负责工作流阶段。 |
| `cfdc/app.py` | Gradio 应用服务层，负责校验表单、维护澄清 session、调用共享 runtime，并把类型化报告转换成阶段摘要和性能对比视图。 |
| `cfdc/models/` | 定义各阶段共享的严格 Pydantic 数据契约，包括八字段诊断、profile catalog、仿真实验记录、核心特征、控制器、调优状态、tracking 状态和最终报告。 |
| `cfdc/diagnosis/` | 实现 Stage 0 自然语言诊断、OpenAI-compatible LLM adapter、严格响应校验、五类归类、澄清 session、安全检查及离线诊断评测。 |
| `cfdc/workflow/` | 实现版本化仿真 profile catalog、candidate route 构造、能力声明、确定性 route 编译以及闭集语义选择校验。 |
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
| `docs/` | 当前 simulation-first 架构的设计说明和迁移记录。 |
| `archive/` | 仅供历史参考的旧实现，当前运行时代码不得导入。 |
| `outputs/` | 本地生成的报告和仿真输出，不属于源代码并被 Git 忽略。 |
| `tmp/` | 开发或验证过程中的可丢弃临时数据，被 Git 忽略且运行时不会导入。 |
| `main.py` | 自然语言入口、诊断 session、开发验证 route、benchmark 和评测的 CLI 入口。 |
| `app.py` | Gradio UI 入口和本地 Web 服务启动器。 |

## 仿真 Profile

论文中的五类动力学原型仍是唯一分类。Profile 只是每类内部的仿真实现路由：

- Class I：一阶惯性，可带显著时延。
- Class II：二阶振荡器。
- Class III：纯积分或双积分。
- Class IV：逆响应、通用不稳定/高阶、欠驱动 CartPole、级联 VTOL。
- Class V：通用 2x2 强耦合对象，使用矩阵特征、全局 pairing 和半强度静态解耦。

当用户描述的具体对象没有专用 simulator 时，系统映射到标准化 profile。结果只验证该 archetype/profile 的软件流程，不代表用户具体设备的物理性能。

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

浏览器访问 `http://127.0.0.1:7860`。应用与 CLI 使用同一条确定性流程，但会按阶段展示诊断、路由、实验、特征、控制器、调优和适应结果；信息不足时可以直接在页面回答澄清问题，审计 JSON 位于独立标签页。需要监听其他网卡或端口时使用 `python app.py --host 0.0.0.0 --port 7860`。

默认运行方式是自然语言主流程，可以使用配置好的 LLM 诊断用户输入。CartPole 和 VTOL 属于开发验证场景，始终使用预注册 description、诊断和 profile，绝不会调用 LLM，也会在后端忽略自然语言表单。切换到开发验证时表单只会暂时禁用而不会清空，切回主流程后用户草稿仍然保留。

直接从自然语言运行完整自动仿真：

```bash
python main.py \
  --description "一个一阶温度过程在加热功率改变后会逐渐稳定。" \
  --observed-output temperature \
  --actuator heater
```

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

`SimulationExperimentRecord` 是 simulator 自动产生的内部数据载体。CLI 和 route API 均不接受用户上传实验结果或 feature packet。

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

## 证据边界

所有顶层报告统一声明 `software_simulation_only`。当前软件能够验证流程完整性、确定性控制计算、rollback/freeze 行为和仿真中的在线适应，但不声明实体机器安全或物理验证。

后续研究仍包括：精确复现论文中的 CartPole/VTOL 数值指标、更长期的 tracking、更多噪声与扰动扫描，以及更多经过验证的 Class IV/V profile backend。
