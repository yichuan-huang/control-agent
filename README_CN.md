# Control Agent

[English README](README.md)

本仓库是 Core-Feature-Driven Control（CFDC）流程的独立软件实现。系统只运行软件模型仿真，不向实体硬件发送命令，也不提供硬件安全认证。

## 主流程

```text
1 问题描述
→ 2 AI 测量计划
→ 3 测量回填
→ 4 系统分类
→ 5 初始控制器
→ 6 效果验证与调优
```

通用 Web 与 CLI 流程必须配置 OpenAI-compatible LLM 服务。流程从一段自然语言控制问题描述开始，也可以用一次可选的描述补充加入现有记录或手册中的事实。随后 AI 展示固定八项诊断清单和测量计划。描述补充与测量回填分别最多进行 8 轮；未知事实始终保留为缺口，不会被虚构默认值填补。

所有测量请求都限定为 `existing_records_only`：只说明应查找哪一份现有记录或手册内容，以及如何回填，不会规定实体硬件的幅值、持续时间、动作或命令。系统分类后，仍通过同一个测量回填入口收集所选 Profile 要求的数值事实，不存在绕过证据门的独立入口。

在固定八项诊断事实全部验证前，正式分类和闭集 Profile 选择都保持为空。分类只用于选择模型族，不能提供对象数值。每个系数、矩阵元素、物理参数、工作范围和试验条件都必须来自问题原文、已提交的记录/手册事实，或可复算的确定性派生。信息完整后，后端确定性编译模型并生成初始控制器候选。

运行时不会按题号、案例 ID 或 Profile 查找对象模型。`dataset/` 下的 200 道 Markdown 问题只用于离线研究和评测，不被生产代码导入。

## 支持的模型

- 连续/离散 SISO 传递函数，包括显式输入时延。
- 连续/离散 SISO/MIMO 状态空间模型。
- 注册非线性模板 `underactuated_cartpole` 和 `vtol_cascaded`。
- 用户确认工作点和有效范围附近的局部线性传递函数或状态空间假设。

LLM 只能返回严格类型化数据。任意 Python、MATLAB、ODE 字符串、动态导入、回调、URL、模块路径和表达式求值都会被拒绝。局部模型轨迹一旦越出确认范围，试验立即以 `inconclusive` 终止，不能继续调增益。

## Web 界面

启动：

```bash
python app.py
```

浏览器访问 `http://127.0.0.1:7860`。通用 Web 流程只有一个领域输入“控制问题描述”，并要求填写 Provider Base URL、Model 和 API Key；不存在可选的无 LLM 模式。六个进度阶段严格为：问题描述、AI 测量计划、测量回填、系统分类、初始控制器、效果验证与调优。

八项诊断事实和所选 Profile 的数值事实完整后：

1. 用户确认已声明的输入/输出范围只作为软件仿真的运行与停止边界，不是硬件安全认证。
2. 后端校验 Profile 事实并确定性编译被控对象模型。
3. “控制器”页签展示尚未验证的初始控制器候选。
4. “调优与适应”接收同一个已编译模型和控制器，并运行第一次软件试验。
5. 输出曲线展示参考值、初始控制器输出、存在差异时的最新执行输出，以及每个已展示通道的输出上下界。
6. 稳定性只能由确定性的 `StabilityDecision` 映射为“稳定”“不稳定”或“证据不足”。最新试验若回滚，曲线仍作为“未采纳”证据显示，但不会成为当前安全控制器。

完整规格流程不会再次询问相同的建模信息，也不需要二次确认数学模型。

主界面没有案例选择、独立仿真实验室、固定 MIMO Demo 或连续自动调参按钮。

通用引导流程必须填写 Base URL、Model 和 API Key，系统只从当前 Provider 输入读取这些信息。API Key 不写入 Gradio 状态、诊断/模型/仿真会话、审计 JSON、日志、哈希或导出文件。

## 目录

| 路径 | 职责 |
| --- | --- |
| `cfdc/lab/model_contracts.py` | 严格模型问题、事实、模型信封、有效范围和试验契约。 |
| `cfdc/lab/model_discovery.py` | 带 revision 与内容哈希的模型发现状态机。 |
| `cfdc/lab/model_discovery_llm.py` | 对 `need_more`、`ready`、`rejected` 的脱敏 LLM 调用和校验。 |
| `cfdc/lab/controller_compatibility.py` | 控制器/模型兼容性与类型化确定性替代建议。 |
| `cfdc/lab/model_validity.py` | 局部线性假设的运行时有效范围门。 |
| `cfdc/lab/resources/` | 与 200 题无关的版本化通用建模问题示例。 |
| `cfdc/web/linked_tuning_service.py` | 已编译对象模型与第五步控制器到效果验证会话的链接服务。 |
| `cfdc/web/model_discovery_presentation.py` | 通俗语言与数学方程混合模型卡。 |
| `cfdc/web/linked_tuning_ui.py` | “调优与适应”中的效果验证、AI 增益建议和审批界面。 |
| `cfdc/sim/` | 确定性线性、CartPole 和 VTOL 仿真后端。 |
| `dataset/` | 原始 200 题 Markdown 数据集；生产代码不导入。 |
| `tests/` | 契约、安全、状态机、仿真、Web 和端到端测试。 |

## 安装与测试

1. 克隆仓库并进入项目目录：

```bash
git clone https://github.com/yichuan-huang/control-agent.git
cd control-agent
```

2. 创建并激活 Conda 环境：

```bash
conda create -n control-agent python=3.11
conda activate control-agent
```

3. 安装项目及测试依赖：

```bash
python -m pip install -e '.[test]'
```

4. 运行测试套件并检查源代码是否可编译：

```bash
pytest -q
python -m compileall -q cfdc tests
```

可使用任意 OpenAI-compatible 服务：

```bash
export CFDC_LLM_BASE_URL="https://your-provider.example"
export CFDC_LLM_MODEL="your-provider-model"
export CFDC_LLM_API_KEY="..."

python main.py --use-llm \
  --description "一个弹簧质量系统在施加力脉冲后会振荡。" \
  --diagnostic-session-output session-v4.json
```

也可通过命令行传入同一配置：

```bash
python main.py --use-llm \
  --llm-base-url "https://api.deepseek.com" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "加热器改变箱体内测得的温度。" \
  --diagnostic-session-output session-v4.json
```

以下继续命令假定上文导出的 `CFDC_LLM_BASE_URL`、`CFDC_LLM_MODEL` 和
`CFDC_LLM_API_KEY` 环境变量仍然有效。继续处理已保存的 v4 会话时，可以在命令行直接回填，
也可以使用一个 UTF-8 文本文件：

```bash
python main.py --use-llm \
  --diagnostic-session-input session-v4.json \
  --diagnostic-session-output session-v4-next.json \
  --measurement-response "在此粘贴现有记录或手册中的发现。"

python main.py --use-llm \
  --diagnostic-session-input session-v4.json \
  --diagnostic-session-output session-v4-next.json \
  --measurement-response-file measurement-response.txt
```

`--measurement-response` 与 `--measurement-response-file` 互斥；测量回填必须同时提供 `--diagnostic-session-input`。如需补充问题描述，应在单独一轮使用 `--diagnostic-description`。当所选 Profile 的回填已包含完整数值仿真范围时，还必须传入 `--confirm-simulation-bounds`，确认这些范围只用于软件仿真。

持久化引导会话的 schema 版本为 `4.0`。版本 3 会话会被明确拒绝而不会迁移；更早的已保存会话同样与本流程不兼容，应使用原始问题描述重新创建 v4 会话。

## 证据边界

应用不会向硬件发送命令。确认输入/输出边界只允许执行有界软件仿真，不代表允许驱动实体硬件，也不是硬件安全认证。“稳定”只说明当前用户确认的软件模型通过了确定性稳定判据。`example_hypothesis` 仍是可重复演示假设；`local_linear_hypothesis` 只在确认范围内有效。任何结果都不代表真实对象的稳定性、鲁棒性、性能或安全性。

## 许可证

Copyright (C) 2026 Yichuan Huang

本项目采用 [GNU Affero General Public License v3.0 only](LICENSE)，SPDX 标识为 `AGPL-3.0-only`。该许可证允许商业使用，但必须遵守许可证条款。通过网络向用户提供修改版服务时，须遵守许可证中的相应源代码义务。

仓库地址：https://github.com/yichuan-huang/control-agent
