# 自然语言描述容错与空心圈 Checklist 设计

## 目标

任何非空控制问题描述都应先发送给已配置的 AI，再进入八项诊断引导界面。描述不完整或 AI 返回的 JSON 含兼容性偏差时，不得把 Pydantic traceback 暴露给用户。界面必须始终显示固定八项 checklist，并用勾号与空心圈明确区分已有原文线索、缺少描述和测量已验证。

Gradio 首屏不再提供任何示例案例，也不提供点击示例自动填充描述的入口。

## 根因

当前 AI 在每个 `DescriptionGuidance` 中返回了额外的 `response: "unknown"`。公共模型采用 `extra="forbid"`，因此会话尚未创建就抛出校验错误。此外，描述阶段直接复用了面向基准模型的结构诊断启发式；仅出现“温度”也会推断多个八项字段已有线索，不能作为 checklist 的可靠勾选依据。

## 数据契约

`DescriptionGuidance` 增加一个可选的自然语言 `response`，默认值为 `unknown`：

- `unknown` 表示当前描述没有覆盖该项；
- 其他值必须是用户描述中的逐字原文片段；
- AI 仍必须原样保留固定八项 guidance 的 ID、提示、用途和允许来源；
- AI 返回无法解析、字段缺失、非原文证据或其他非法结构时，只丢弃本次 AI enrichment，回退到八项全部未描述的固定 guidance。

AI Provider 的认证、网络和超时错误不属于“用户描述不完整”，仍返回简洁、可操作的 Provider 错误。只有已经成功获得响应但响应结构不合约时才 fail-soft。

测量计划的 AI 转写同样是可选 enrichment：返回结构无效时使用后端确定性的安全测量计划，不阻止 checklist 展示。

## Checklist 语义

描述阶段不再根据“温度”“水箱”等对象关键词推断八项已完成，而只使用 AI 提供且能在用户原文中逐字定位的 `response`：

- `○ 缺少描述`：没有该项的原文证据；
- `✓ 已有线索`：描述中存在该项的逐字证据，但尚未测量验证；
- `✓ 测量已验证`：后续测量 assessment 中存在该项的已校验 fact。

恒温器示例描述可识别房间温度和电加热器等信号，但没有说明恢复趋势、初始方向、时延、快慢阶段、可控可观、非线性、耦合和工况变化，因此八项保持空心圈，并展示对应填空问题和测量引导。

## Gradio UI

- 删除 `EXAMPLES` 常量及 `gr.Examples` 组件；
- 删除只用于验证或驱动示例案例的测试依赖；
- 保留唯一的“控制问题描述”输入框；
- checklist 状态文本加入 `✓` 或 `○`，不改变三态数据语义；
- 不向用户显示 AI schema traceback。

## 错误处理

1. Provider 调用成功且返回合约正确：使用 AI 原文 evidence 更新 checklist。
2. Provider 调用成功但返回 JSON/字段不合约：回退固定八项 guidance 和安全测量计划，继续 `awaiting_measurements`。
3. Provider 配置、认证、网络或超时失败：保留简洁 Provider 错误，避免误导用户认为 AI 已成功处理。

## 测试

- 使用用户给出的恒温器中文描述和带八个额外 `response: "unknown"` 的 fake AI 输出，证明会话正常创建、八项均为空心圈且不泄露 traceback。
- 使用一个逐字覆盖部分诊断项的描述，证明只有对应项显示 `✓ 已有线索`。
- 使用非原文 response、无效 JSON 和无效测量计划输出，证明回退后仍进入引导流程。
- 验证测量 fact 仍优先显示 `✓ 测量已验证`。
- 验证 Gradio 配置中不存在 Examples 组件、示例标签或示例数据。
- 运行 Gradio、guided flow、session 测试及全仓验证。
