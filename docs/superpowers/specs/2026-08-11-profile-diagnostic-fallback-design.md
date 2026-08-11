# Profile 阶段诊断复核安全回退设计

## 问题与根因

Profile 参数回复会经过两条独立路径：八项结构诊断复核用于发现用户明确提交的新矛盾，
规格提取用于读取输入输出变化量、响应时间和软件仿真边界。当前
`OpenAICompatibleDiagnosticAdapter.extract_measurements()` 只解析 LLM JSON，未在
适配器边界验证新诊断事实是否由本轮原文证明；未经验证的结果随后进入
`submit_profile_measurement_assessment()`，由严格会话校验抛出 `ValueError`。

用户提交的方向盘案例同时包含 `63% 响应时间 1.5 s` 和 `输入延迟 0 s`。LLM 将
Profile 数值错误写入 `significant_delay.numeric_value`，但返回的 `source_excerpt`
不包含同一个数值，最终产生
`measurement numeric_value for significant_delay is not attested in source_excerpt`。
这是 LLM 诊断复核输出错误，不是用户 Profile 数据缺失或冲突。

## 设计

在 `OpenAICompatibleDiagnosticAdapter.extract_measurements()` 返回结构化诊断结果前，
使用现有 `validate_grounded_measurement_assessment()` 对候选结果、当前原文和上一份
assessment 做完全相同的证据校验。

只有当上一份 assessment 已经是 `ready` 时，才启用 Profile 阶段回退：

- 候选 assessment 通过校验：原样返回；明确且有原文证据的新矛盾继续进入会话，
  允许确定性后端清空旧分类和全部下游结果。
- 候选 assessment 因无原文摘录、数值或单位未被摘录证明、无效 conflict 或无效
  schema 而失败：返回上一份 `ready` assessment 的深拷贝，表示本轮没有可信的诊断
  变化；同一原始回复仍继续交给规格提取器。
- 上一份 assessment 不是 `ready`：不启用此回退，诊断测量阶段继续维持现有严格
  失败边界，避免用不完整旧事实掩盖新错误。

会话层 `submit_profile_measurement_assessment()` 与
`validate_grounded_measurement_assessment()` 不放宽，保持它们作为自定义适配器和
直接调用者的严格信任边界。修复仅位于官方 LLM 适配器的输出边界。

## 数据流与原子性

回退只替换 LLM 派生的八项复核对象，不修改用户原文、会话 revision、Profile 回合数
或规格 history。规格提取仍接收用户提交的完整原文，因此七项 Profile 数据不会被
丢弃。若规格提取随后失败，原有会话原子性规则继续生效；若规格完整，则正常编译
模型并生成候选控制器。

适配器只返回上一份 assessment 的深拷贝，不得让调用方或 provider 原地修改会话中
已持久化的可信 assessment。

## 用户体验

对于本次方向盘回复，诊断复核中的未落地 `significant_delay` 改动被忽略，界面不再
显示 traceback。系统继续识别七项数值和单位；数据完整且软件仿真边界已确认时进入
模型与候选控制器阶段，数据不完整时仍停留在原回复框并列出真实缺项。

## 测试与验收

先新增失败回归，再修改生产代码：

- 官方 LLM 适配器返回数值与来源摘录不一致的 `significant_delay` 时，测试在修复前
  重现当前 `ValueError`；修复后返回上一份完整 assessment。
- 使用用户给出的方向盘七项回复走公开 `run_cfdc_route()`，验证同一回复继续进入规格
  提取，最终产生编译模型和 `candidate_unvalidated` 控制器，而不是 traceback。
- 提供原文明示且完整落地的新诊断矛盾，验证它不会被回退吞掉。
- 验证初始诊断测量阶段的无来源事实仍被拒绝，直接会话 API 的严格校验保持不变。
- 最终运行 `pytest -q`、`python -m ruff check .`、
  `python -m compileall -q cfdc tests main.py` 与 `git diff --check`。

## 非目标

本次不修改七项 Profile 模板、不放宽数值/单位证据规则、不改变分类或控制器算法，
也不通过捕获 Gradio 顶层异常来掩盖后端错误。
