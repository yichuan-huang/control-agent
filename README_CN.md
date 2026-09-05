# Control Agent

[English README](README.md)

本仓库是 Core-Feature-Driven Control（CFDC）流程的独立软件实现。`v0.3.4` 以带审计记录的 Python Kernel 为核心，提供引导式 WebUI、专家 JSON 接口、确定性软件实验、物理实验交接和 CLI 兼容入口。系统不会向实体硬件发送命令，也不提供硬件安全认证。

## 快速开始

你可以通过 Ollama 使用本地模型，也可以使用 DeepSeek API、OpenAI API 等在线服务。请按自己的需要选择服务商和模型，Ollama 不是必需依赖。模型负责理解自然语言回复；路线、实验、控制器、数值评价和最终结论仍由 Kernel 决定。

1. 安装 Git、`uv` 和 [Node.js 与 npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)。npm 通常随 Node.js 一同安装。Node.js 需要 20.19+ 或 22.12+。然后下载项目、安装依赖、检查 Python 文件、验证 Node 与 npm，并完成首次前端安装和构建：

```bash
git clone https://github.com/yichuan-huang/control-agent.git
cd control-agent
uv sync --locked
uv run --locked python -m compileall -q -x '(^|/)(frontend|gradio_archive)(/|$)' cfdc tests main.py app.py
node --version
npm --version
npm --prefix cfdc/web/frontend ci
npm --prefix cfdc/web/frontend run build
```

`uv` 会读取 `.python-version` 中的 Python 版本并管理 `.venv`。使用 `uv run` 时不需要手动激活环境。

2. 完成首次 `npm ci` 和构建后，日常使用只需运行以下命令启动 WebUI：

```bash
uv run python app.py
```

默认入口是 React + FastAPI，同源监听 `127.0.0.1:7860`。RAG 依赖默认安装，并在后台准备；页面与设置仍可使用，首次下载 encoder 可能较慢。RAG 处于准备中或失败时，要求使用 RAG 的任务不能启动，页面会明确显示错误。关闭 RAG 只影响未来创建任务的绑定，已有任务的 snapshot 保持不可变。Hugging Face 使用当前用户的默认模型缓存。

3. 打开 `http://127.0.0.1:7860`。使用自然语言回复时，按照下表中你选择的服务商填写 Base URL、Model 和 API Key。在“引导工作台”选择一个内置案例，例如“01｜直流电机转速”。

4. 按四步填写任务与目标、观测与输入、约束与偏好，并在最后核对摘要和确认软件试验边界。内置案例的合同锁定；“转为自己的任务”保留表单值并解除案例执行绑定。默认开启的 RAG 仅绑定服务端已准备好的 snapshot。任务启动后，工作台按 Kernel 状态显示当前主要操作，直到需要用户决定或到达终态。

每次运行前可执行 `uv run --locked python main.py --doctor`。它与 WebUI 的“环境自检”共用同一非破坏性服务，检查 Python、资源目录、可写会话目录、公开案例注册表、可选 RAG，以及（仅对 loopback 地址）本地 Ollama 服务和模型。会话目录检查会创建并立即删除一个受限探针文件。

首次使用建议先选择内置软件案例。自定义对象不会自动获得仿真模型；实体或外部实验也不会由页面直接执行，而是通过 operator bundle、操作员确认和协议绑定的数据上传继续。

内置权限只由服务端案例 ID 和带 fingerprint 的 `RegisteredCaseBinding` 授予，修改浏览器 JSON 不能替换 Provider。要练习教学闭环，请选择内置案例并点击“创建教学练习任务”。生成的 ZIP 只用于软件练习，会消耗预留的软件实验预算，但在下载并重新上传、通过正常审计门之前不会写入 evidence。

## 选择模型服务商

选择并配置其中一种服务即可。模型需要支持 OpenAI-compatible Chat Completions 和 JSON 输出（`response_format: {"type": "json_object"}`），以及应用使用的请求参数。兼容性和模型访问权限以服务商为准，仅填写模型名称不代表一定兼容。

| 服务商 | Base URL | Model | API Key |
| --- | --- | --- | --- |
| Ollama（本地，可选） | `http://127.0.0.1:11434/v1` | `ollama list` 中显示的完整模型名称 | 默认本地服务填写 `ollama` |
| DeepSeek API | `https://api.deepseek.com` | 例如 `deepseek-v4-pro` | 你的 DeepSeek API Key |
| OpenAI API | `https://api.openai.com/v1` | 你的 API 账户可用且兼容的 Chat Completions 模型 | 你的 OpenAI API Key |

服务商文档：[Ollama 兼容接口](https://docs.ollama.com/api/openai-compatibility)、[DeepSeek 配置](https://api-docs.deepseek.com/)、[OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat)。在线服务使用你自己的账户权限并按服务商规则计费；仅安装项目不需要调用在线 API。

如果选择 Ollama，请先安装并启动本地服务。桌面应用可能已经启动了服务；否则另开终端运行 `ollama serve`。将下方的 `your-model` 替换为你选择的模型名称，再将相同名称填入 WebUI：

```bash
ollama pull your-model
ollama list
```

如果选择 DeepSeek 或 OpenAI，跳过 Ollama 步骤，直接填写对应配置即可。不要将真实 API Key 写入源码、截图或共享报告。下方 Kernel CLI 部分说明了环境变量及命令行配置方式。

## Kernel 主流程

WebUI 只运行当前 CFDC Kernel，并严格展示九阶段状态机：

```text
1 任务 -> 2 诊断 -> 3 取证 -> 4 路线／特征
-> 5 控制器 -> 6 冻结 -> 7 评价
-> 8 调优／确认 -> 9 结果
```

Kernel 使用带 revision 的 `TaskContract`、只追加事件、确定性 action ID、过期 revision 检查和类型化公开产物。系统不执行生成代码。Provider 可以返回类型化回复和公开 JSON/CSV 证据；路线解析、控制器 IR 校验、冻结绑定、评价和有界调优均受确定性 Kernel 契约约束。

当前注册的软件任务类型为：

- `local_setpoint_hold`
- `transition_then_hold`
- `disturbance_recovery_to_hold`

其他目标会明确拒绝。RAG 在后台准备；每个任务可选择是否使用，启用后会话固定使用一个已校验的索引快照。

运行时定义 Diagnosis、Modeling、Controller 和 Critic 四个角色边界。当前 Web 自然语言回复实际调用 Diagnosis 提取八维诊断、Modeling 提取白名单参数，再由 Critic 审查合并后的类型化 candidate，并最多允许一次修正。Controller 角色保留给受约束的解释或 proposal 接口；Web 自动主线的控制器由确定性合成器生成。Python Kernel 是状态迁移、数值计算、路线选择、安全门和最终主张的唯一权威。Agent 调用失败时，本次用户回复不会写入业务状态，页面会返回明确错误；已经记录的 Kernel artifact 不会被模型输出覆盖。

RAG 是按任务选择的本地参考层。WebUI 启动后，服务端在后台构建或复用 `output/rag-index`，校验 schema、Registry fingerprint、知识包版本、已校准检索参数和文件 checksum，并加载、预热 encoder。启用 RAG 的会话会固定使用该精确 snapshot。当前 Web 的 `user_reply` 提取操作有意不注入检索片段，避免参考资料被误当成用户事实；RAG 用于其他显式的角色操作和扩展入口。页面显示“RAG 已启用”表示准备好的 snapshot 已绑定到该任务，不表示每一次 Agent 调用都执行了检索。

## 核心能力

Kernel 通过版本化合同提供以下能力，使实验、证据、控制器决策和结果都可以检查与验证。

- `cfdc-protocol/v2` 支持有界 SISO、重复时序、阶梯实验、Class IV 频率／幅值／release、局部不稳定平衡、2x2 MIMO 和多阶段协议。Provider 执行前会重新编译并核对全部绑定和 fingerprint。
- Operator handoff 会生成操作卡、预检查清单、JSON schema、重复 CSV 模板和 ZIP。CSV/JSON 上传必须依次通过操作员授权、格式、会话／协议、重复次数、时间轴、输入波形、安全边界和信号质量八道门。拒绝的尝试只追加失败回执，不计入有效实验次数；但失败尝试和已请求的激励时间仍分别消耗预注册预算。
- 注册案例还支持教学练习包：ZIP 固定包含公开 manifest、协议绑定 CSV 和中文说明。生成时只预留软件实验预算，不写入 evidence；下载后重新上传仍必须通过同一套确定性审计门。七个 `audit_class_*` 案例使用现版独立动力学和评价 Provider，不再是五个工程模型的别名。
- `cfdc-features/v2` 自动生成带来源和区间的 SISO 相邻结构、时延／NMP／积分／二阶、Step-B 非线性、Class IV、局部不稳定平衡和 2x2 静态／动态耦合特征，同时生成有界参数域。证据不足时返回明确 feature gap。
- 包内路线注册表提供 20 个可执行控制器合同，并保留明确的 capability-gap 路线。Controller proposal 必须是受限 `ControllerIR`；确定性合成和 `cfdc-qualification/v2` 只返回 `offline_qualified`、`diagnostic_trial_only` 或 `not_qualified`。
- Identification Provider 与 Evaluation Provider 使用两个独立且不可混淆的绑定。独立 `cfdc-independent-judge/v2.0` 从完整逐采样轨迹和停止事件重新计算逐通道指标，先判断硬稳定性与边界，再判断任务性能、扰动重复、最差试次和 95% Wilson 下界。只有稳定但性能不足才允许有界调优；接受的候选会创建新 freeze，并且必须通过 fresh confirmation。
- `cfdc-session/v4.0` 增加从案例目录重算的 `RegisteredCaseBinding`，并保留 revision、幂等 action、stale revision 拒绝、不可覆盖的 artifact 历史和只追加事件链。

工作流公开三个彼此独立的就绪门：合法取证、证据支持的路线选择、控制器综合。未知维度只阻塞实际消费它的动作。每次 Provider 调用都在执行前预留预算，因此重试次数、激励时间、有效实验数和不同协议数会分别审计。旧会话可以读取但不能修改；派生会话只复制任务和人工先验，不继承旧特征、资格或性能授权。

可执行能力目录明确区分“合同已注册”和“端到端已验证”。以下 20 个 family 都有提交到仓库的验收：由公开证据综合类型化控制器、恢复稳定资格、冻结、执行非零逐采样闭环并由独立裁判复算；每个 family 另有与其机制相关的拒绝反例。

- SISO 与积分对象：`PI`、`delay_aware_PI`、`notch_then_PI`、`two_dof_pid`、`P_integrator`、`PD_integrator`、`lead_lag_series`、`two_dof_PI`。
- 静态非线性：`local_PI_without_inverse`、`partial_inverse_then_PI`、`deadzone_right_inverse_then_PI`。
- 高阶频带：`reduced_low_order_PI`、`phase_guarded_2dof_PI`。
- 局部状态与非线性：`cascaded_control`、`local_fixed_PID`、`scheduled_damping_PID`、`self_excitation_energy_guarded_PID`。级联运行时覆盖已声明的 CartPole 局部平衡和二维 VTOL 近悬停工作区，不主张摆起或全局恢复。
- MIMO：`decentralized_channel_PI`、`static_decoupler_then_PI`、`lag_dynamic_decoupler_then_PI`。

## 开发检查与可选 RAG

前端本地检查与开发：

```bash
npm --prefix cfdc/web/frontend ci
npm --prefix cfdc/web/frontend run typecheck
npm --prefix cfdc/web/frontend run lint
npm --prefix cfdc/web/frontend run format:check
npm --prefix cfdc/web/frontend test
npm --prefix cfdc/web/frontend run build
cd cfdc/web/frontend && npx playwright install chromium && cd ../../..
npm --prefix cfdc/web/frontend run test:e2e
npm --prefix cfdc/web/frontend run dev
```

Playwright 会在 `127.0.0.1:7867` 自动启动构建后的界面与真实 FastAPI 服务，使用临时数据且不调用模型。设置 `CFDC_E2E_URL` 可检查已运行的服务。CI 使用 Node 22 执行这些前端检查，同时保留 Python 3.11–3.13 检查。使用 Vite 开发时，在另一个终端运行 FastAPI；Vite 位于 `127.0.0.1:5173`，`/api` 代理到 `127.0.0.1:7860`。

在项目目录中运行自动化测试和 Python 检查：

```bash
uv lock --check
uv sync --locked
uv run --locked ruff format .
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked python main.py --benchmark > /tmp/cfdc-benchmark.json
uv run --locked python main.py --validate-demo
uv run --locked python scripts/benchmark_web_api.py
git diff --check
```

`uv` 会读取 `.python-version` 中固定的 Python 版本，创建 `.venv`，并安装项目及开发工具。使用 `uv run` 时不需要手动激活环境。

新建索引默认包含两类随包资源：由 Registry 生成的权威 artifact，以及 12 个控制概念组的中英文版本化 advisory 知识卡。同组语言版本共享稳定 group identity 和语义版本，但保留各自的内容哈希与 provenance。知识包采用中央 JSON manifest 与 schema，记录有效期、引用元数据和 192 条冻结评估案例：原英文/中文集合、一个已曝光的 regression 集，以及 replacement challenge holdout。卡片只能解释已注册选择，不能改变路线、数值结果、资格审查或授权。新索引使用不可变 `cfdc-rag/v3` snapshot；合法 `v2` 和旧策略 `v3` snapshot 仍可只读加载，系统不会原地重写。

如需加入本地 Markdown 或 PDF，可放在 `references` 目录。没有 metadata 的旧文档仍按“全 scope 可见”的兼容语义进入统一过滤。`--knowledge-pack` 可指定另一份通过校验的知识包，`--no-curated` 可排除随包卡片，`--relevance-threshold` 可把显式阈值固化到新 snapshot：

```bash
uv run --locked python -m cfdc.rag index --source-dir ./references --index-dir ./rag-index
uv run --locked python -m cfdc.rag inspect --index-dir ./rag-index
uv run --locked python -m cfdc.rag query --index-dir ./rag-index \
  --role critic --operation check --stage review \
  --language auto \
  --query "为什么不能消除不确定的右半平面零点？"
uv run --locked python -m cfdc.rag eval --index-dir ./rag-index \
  --bundled --split holdout --assert-acceptance
```

`--language` 支持 `auto`、`en` 和 `zh`。自动模式只检查查询 summary 是否含汉字；显式选项覆盖自动判断。只有 summary 正文直接包含 artifact、profile 或 rule ID 时才返回 Registry reference；结构化 class/profile 字段只用于 scope 过滤，不会拼入语义查询。Advisory 检索先查首选语言，合格的双语 group 可投影为指定语言；每次最多返回两个不同的内置知识卡概念组，其余槽位仍可由外部文档补充。`rag eval --bundled` 会分别报告各门禁数据集和 combined 指标；可用 `--suite en`、`--suite zh` 或 `--suite challenge` 选择单个集合，`--assert-acceptance` 在失败时非零退出。本地来源目录和生成索引都不属于仓库 artifact。`user_reply` 路径永远不会收到 RAG reference；其他 Agent reference 均以不可信 advisory material 标记，并在审计中记录实际语言、group、snapshot、citation 与 provenance。

运行历史使用独立的离线索引，不与 RAG 混合，也不会注入 Agent prompt。其 JSON schema 支持设备手册、FeatureArtifact、ControllerFreeze、资格报告、性能基线、适应 episode、退化事件、回滚报告和维护记录。导入时会校验 payload、配置和工作区哈希，以及有效期和同身份 supersedes 关系；不可变 snapshot 只保存摘要与 provenance。查询必须先精确匹配 plant、configuration 和 operating-region fingerprint，之后才应用有效期、记录类型、lexical 或 dense 排序。系统不会跨身份 fallback，也不会自动扫描 session、写回、监控或授予硬件权限。

可通过独立 CLI 构建、检查和查询本地历史索引。源文件必须符合随包 schema；生成的 `operational-history` 数据会被 Git 忽略：

```bash
uv run python -m cfdc.history index \
  --source ./operational-history/records.json \
  --index-dir ./operational-history/index
uv run python -m cfdc.history inspect \
  --index-dir ./operational-history/index
uv run python -m cfdc.history query \
  --index-dir ./operational-history/index \
  --plant-id plant-a \
  --configuration-fingerprint 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --operating-region-fingerprint fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210 \
  --record-type rollback_report \
  --as-of 2026-09-03T00:00:00Z
```

历史 Gradio 应用可从 [v0.3.3 源码](https://github.com/yichuan-huang/control-agent/tree/v0.3.3) 获取。当前版本独立运行，不依赖历史检出目录。

## Web 界面

启动应用后访问 `http://127.0.0.1:7860`：

```bash
uv run python app.py
```

内置知识库依赖默认安装。服务端管理的索引只包含 Registry artifact 和随包发布的中英文知识卡。`CFDC_RAG_INDEX_DIR` 可覆盖服务端存储位置，浏览器输入不能选择索引路径。

“引导工作台”通过显式结构化表单创建 Kernel 任务。所有任务都必须填写任务描述、至少一个观测输出、至少一个控制输入、有限的输入上下界，以及正数 `state_stop`。输出上下界可选，但必须成对填写。`transition_then_hold` 还必须填写初始区域和目标区域；`disturbance_recovery_to_hold` 还必须填写扰动事件、恢复起点条件和恢复后保持区域。表单也支持工程单位、性能阈值、实验预算、时间偏好、初始数值和 intermediate targets。

工作台在每个状态突出一个主要操作：诊断回复、证据交接或上传、有界调优及全新结果确认，并保留九阶段只追加审计时间线。注册案例展示学习目标和证据边界。协议预览、记录轨迹、指标、置信度与就绪情况均来自 Kernel artifact。完整 JSON 树、审计记录和可选择曲线在专家与结果视图按需加载；显示抽样不改变数值评价或重放。

“专家合同”页可以提交完整 `TaskContract`、加载 Kernel session、执行 typed action JSON，并校验下载 artifact 的 fingerprint。可单独导出协议、operator bundle、上传回执、特征、Controller IR、qualification、freeze、evaluation、feedback、confirmation、最终结果和完整会话审计，也可导出完整结果 ZIP。

在设置中填写 Base URL、Model 和 API Key 后，点击 **测试当前配置** 即可探测。当前页面的模型请求直接使用表单值，无需另行保存或设置环境变量。探测成功表示服务可连接且模型存在，不代表完整推理兼容性已验证。**高级设置** 中可选用“从启动环境导入地址和模型”，密钥始终保留在页面内存中。

Web Agent 编排固定为 `multi`。页面没有工作流版本和 Agent 模式控件；Provider 配置和默认开启的内置 RAG 开关继续保留，本地索引目录由服务端管理，不属于浏览器输入。高级 JSON 也继续保留，因为它属于 Kernel 的类型化公开证据与动作接口。

Kernel 输入契约决定当前动作接受自然语言、类型化 JSON，还是无需输入的按钮。每次修改均检查会话修订号和请求标识。刷新后会重新连接已记录的操作；中断操作会明确显示，不自动重放，由用户显式重试。

WebUI 不加载也不运行 legacy 会话，不提供 `single` 基线，不会自动回退到兼容流程。缺失、未知或非 Kernel 的 Web state 会返回明确错误。需要 legacy 时，请使用下方 CLI 步骤。

未完成草稿保存在当前浏览器标签页的 `sessionStorage`。Provider 凭据仅保留在易失内存，刷新后需要重新填写；API Key 不进入草稿、Kernel 会话、审计 JSON、日志、哈希或导出文件。历史导入 API 只接受 `request_id` 和已上传的 `file_id`。导入的公开事实必须重新确认边界，不继承注册案例执行权限或 RAG 绑定。

内置选择器包含 18 个公开案例：

- 5 个工程训练案例：`dc_motor_speed_v1`、`tclab_single_heater_v1`、`dc_motor_position_v1`、`quadruple_tank_nmp_v1`、`tclab_dual_heater_v1`。
- 6 个 transition 变体：直流电机转速、单加热器和四水箱各自的单段及 staged transition-hold 版本。
- 7 个审计案例：`audit_class_i_level`、`audit_class_ii_thermal`、`audit_class_ii_oscillator`、`audit_class_iii_motion`、`audit_class_iv_nmp`、`audit_class_iv_high_order`、`audit_class_v_mimo`。

## Kernel CLI

CLI 同时保留两套工作流的兼容接口。创建自定义 Kernel 任务时应显式选择 Kernel。命令会停在下一个用户或证据边界，并输出 session ID 与当前 input contract：

```bash
uv run python main.py --workflow-version kernel \
  --kernel-session-dir ./output/kernel-sessions \
  --description "加热器保持箱体温度。" \
  --observed-output temperature --actuator voltage \
  --safety-bound input_min=-1 --safety-bound input_max=1 \
  --safety-bound state_stop=3
```

续跑时使用 `--kernel-session SESSION_ID`、唯一的 `--kernel-action`，以及 `pending_actions` 要求的类型化参数。`--kernel-auto` 会自动执行确定性步骤，直到需要用户、外部数据、确认、遇到 capability gap 或到达终态。

注册工程案例在提供公开诊断后，可以一次跑完整个软件 Provider 链：

```bash
DIAGNOSIS_JSON='{
  "open_loop_stability":{"status":"known","assessment":"stable","evidence":"有界公开试验","confidence":0.95},
  "nonminimum_phase":{"status":"known","assessment":"minimum_phase","evidence":"有界公开试验","confidence":0.95},
  "significant_delay":{"status":"known","assessment":"not_significant","evidence":"有界公开试验","confidence":0.95},
  "relative_degree":{"status":"known","assessment":"low","evidence":"有界公开试验","confidence":0.95},
  "sensing_actuation_adequacy":{"status":"known","assessment":"adequate","evidence":"操作记录","confidence":0.95},
  "nonlinearity_strength":{"status":"known","assessment":"weak","evidence":"有界公开试验","confidence":0.95},
  "coupling_underactuation":{"status":"known","assessment":"siso","evidence":"已声明接口","confidence":0.95},
  "uncertainty_variation":{"status":"known","assessment":"small","evidence":"重复公开试验","confidence":0.95}
}'

uv run python main.py --workflow-version kernel \
  --kernel-case dc_motor_speed_v1 \
  --kernel-action motor-run-001 \
  --confirm-kernel-budget \
  --kernel-answer "$DIAGNOSIS_JSON" \
  --kernel-advance --kernel-auto \
  --kernel-result-dir ./output/results \
  --kernel-export-bundle
```

如需教学练习而非自动写入软件 evidence，可增加
`--kernel-evidence-mode exercise_bundle --kernel-prepare-training-exercise`。
命令会停在 `awaiting_evidence`；把下载的
`training_exercise_bundle.zip` 通过后续 `--kernel-upload` 重新提交，系统才会执行正常审计门。

对于实体或外部操作实验，在诊断和路线解析后绑定公开 Provider 合同，再生成 handoff：

```bash
uv run python main.py --workflow-version kernel --kernel-session SESSION_ID \
  --kernel-action physical-001 \
  --kernel-provider physical-provider.json \
  --kernel-compile-protocol --kernel-prepare-operator-handoff \
  --kernel-result-dir ./output/results

uv run python main.py --workflow-version kernel --kernel-session SESSION_ID \
  --kernel-action physical-002 \
  --kernel-operator-report operator-report.json \
  --kernel-upload repeat-01.csv --kernel-upload repeat-02.csv \
  --kernel-upload repeat-03.csv --kernel-auto
```

如果声明的停止条件曾触发，应增加 `--kernel-upload-stopped-on-limit`；该上传会作为安全门失败记录，系统不会修补数据，也不会把它计作已接受证据。

自然语言 Agent 使用的 Provider 可通过 `CFDC_LLM_BASE_URL`、`CFDC_LLM_MODEL`、`CFDC_LLM_API_KEY` 或对应 `--llm-*` 参数配置。它们只影响角色内 proposal 和解释，路线、数值结果与授权仍由 Kernel 决定。

下面以 DeepSeek 为例，请先在本地环境中设置 `DEEPSEEK_API_KEY`。使用其他服务商时，将 Base URL、模型和密钥替换为上表中的对应配置：

```bash
uv run python main.py --use-llm \
  --workflow-version kernel \
  --llm-base-url "https://api.deepseek.com" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "加热器改变箱体内测得的温度。" \
  --observed-output temperature --actuator voltage \
  --safety-bound input_min=-1 --safety-bound input_max=1 \
  --safety-bound state_stop=3
```

## Legacy CLI 分步操作

Legacy 只在 CLI 中提供。每条命令都应显式选择兼容工作流、`single` Agent 基线并关闭 RAG。请把示例 Provider 和中文占位文本替换为实际控制问题的事实。

1. 配置 OpenAI-compatible Provider：

```bash
export CFDC_LLM_BASE_URL="https://your-provider.example/v1"
export CFDC_LLM_MODEL="your-model"
export CFDC_LLM_API_KEY="..."
```

2. 创建第一份 legacy 诊断会话：

```bash
uv run python main.py --workflow-version legacy \
  --use-llm --agent-mode single --no-rag \
  --description "控制问题描述" \
  --diagnostic-session-output legacy-01.json
```

3. 如果 `legacy-01.json` 仍要求补充描述事实，就补充缺少的对象、传感器、执行器或行为信息，并写入新文件：

```bash
uv run python main.py --workflow-version legacy \
  --use-llm --agent-mode single --no-rag \
  --diagnostic-session-input legacy-01.json \
  --diagnostic-description "补充缺少的对象、传感器或执行器信息" \
  --diagnostic-session-output legacy-02.json
```

4. 当最新 JSON 开始要求所选 Profile 的参数时，提交已知数值、单位、来源和软件仿真范围：

```bash
uv run python main.py --workflow-version legacy \
  --use-llm --agent-mode single --no-rag \
  --diagnostic-session-input legacy-02.json \
  --measurement-response "已知参数、单位、来源和软件仿真范围" \
  --confirm-simulation-bounds \
  --diagnostic-session-output legacy-03.json
```

每次续跑都应使用新的 `--diagnostic-session-output` 路径。这样会保留每个 revision 的审计记录，也不会覆盖输入会话。每次续跑前先检查最新 JSON：状态仍要求描述或诊断事实时使用 `--diagnostic-description`；只有状态开始要求 Profile 参数后才使用 `--measurement-response`。也可以改用 `--measurement-response-file` 读取 UTF-8 文本，但它与 `--measurement-response` 互斥。

## 支持模型、能力缺口与物理边界

确定性运行时支持连续或离散 SISO 传递函数、连续或离散 SISO/MIMO 状态空间模型、注册非线性模板 `underactuated_cartpole` 与 `vtol_cascaded`，以及确认工作点和有效范围附近的局部线性假设。

LLM 输出不能包含可执行 Python、MATLAB、ODE 代码、动态导入、回调、模块路径、URL 或表达式。局部模型轨迹一旦离开确认的有效范围，试验立即以 `inconclusive` 终止。未注册拓扑、缺少判别特征、未解析的高阶／动态非线性、输入符号权威不足或不支持的 MIMO 分配会进入带名称的 `capability_gap`；注册表不会悄悄替换成相邻控制器。

WebUI 永远不会控制硬件。物理能力止于工程单位规范化、preflight、操作员 handoff、协议绑定的数据回收、冻结控制器绑定和独立裁决。`ready_for_operator_review` 不等于执行授权。确认软件边界只允许有界软件仿真，不代表允许驱动实体硬件，也不是硬件安全认证。

## 许可证

Copyright (C) 2026 Yichuan Huang

本项目采用 [GNU Affero General Public License v3.0 only](LICENSE)，SPDX 标识为 `AGPL-3.0-only`。该许可证允许商业使用，但必须遵守许可证条款。通过网络向用户提供修改版服务时，须履行相应的源代码义务。

仓库地址：https://github.com/yichuan-huang/control-agent
