# Control Agent

[English README](README.md)

本仓库是 Core-Feature-Driven Control（CFDC）流程的独立软件实现。系统只运行软件模型仿真，不向实体硬件发送命令，也不提供硬件安全认证。

## 主流程

```text
自然语言控制问题
→ 结构诊断与五类归类
→ 八字段与补充数值规格
→ 后端确定性编译对象模型
→ 第五步生成尚未验证的初始控制器
→ 运行初始控制器效果验证
→ 判断稳定性
→ AI 提出受限增益更新并由用户批准
→ 首次稳定或终止条件出现时停止
```

分类结果只帮助选择模型族，不能提供对象数值。每个系数、矩阵元素、物理参数、工作范围和试验条件都必须来自问题原文、已提交的规格信息，或可复算的确定性派生。一旦这些输入足以编译模型，主流程不会再次采集相同信息。

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

浏览器访问 `http://127.0.0.1:7860`。八字段与补充数值规格完整后：

1. 后端校验规格并直接编译被控对象数学模型。
2. “控制器”页签展示第五步选出的初始控制器。
3. “调优与适应”自动接收该模型和控制器。
4. 运行初始控制器效果验证。
5. 试验稳定后，“5 效果验证”显示绿色勾；否则请求一次白名单 AI 增益更新，查看差异后批准或拒绝下一轮试验。

完整规格流程不会再次询问相同的建模信息，也不需要二次确认数学模型。

主界面没有案例选择、独立仿真实验室、固定 MIMO Demo 或连续自动调参按钮。

只有试验不稳定、需要请求 AI 增益建议时，才读取当前 Base URL、Model 和 API Key 输入。API Key 不写入 Gradio 状态、模型/仿真会话、审计 JSON、日志、哈希或导出文件。

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

```bash
python -m pip install -e '.[test]'
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
  --observed-output position \
  --actuator force
```

也可通过命令行传入同一配置：

```bash
python main.py --use-llm \
  --llm-base-url "https://api.deepseek.com" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "加热器改变箱体内测得的温度。" \
  --observed-output temperature \
  --actuator heater
```

## 证据边界

“稳定”只说明当前用户确认的软件模型通过了已实现的稳定判据。`example_hypothesis` 仍是可重复演示假设；`local_linear_hypothesis` 只在确认范围内有效。任何结果都不代表真实对象的稳定性、鲁棒性、性能或安全性。

## 许可证

Copyright (C) 2026 Yichuan Huang

本项目采用 [GNU Affero General Public License v3.0 only](LICENSE)，SPDX 标识为 `AGPL-3.0-only`。该许可证允许商业使用，但必须遵守许可证条款。通过网络向用户提供修改版服务时，须遵守许可证中的相应源代码义务。

仓库地址：https://github.com/yichuan-huang/control-agent
