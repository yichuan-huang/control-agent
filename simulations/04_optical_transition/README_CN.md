# 04｜光强分阶段过渡并保持

本案例只运行软件仿真：以归一化 `led_current` 调节归一化 `optical_intensity`，从 `0` 经中间目标 `0.25` 到最终目标 `0.5`。任务要求至少 3 个阶段、2 次已验证交接、进入目标区域并最终保持至少 2 秒；向导中的到达目标时间上限为 10 秒。输入边界 `[-1, 1]`、软件停止阈值 `3`，评价采用 `0.02` 秒采样、20 秒时长、20 次重复和 `0.8` 成功率 Wilson 下界。历史演练预期进入 `capability_gap`，但本次结论只由本次证据决定。

## 1. 准备环境并启动 CFDC

```bash
cd "/Users/huangyichuan/workspace/THU/control-agent"
uv sync --locked
uv run python app.py
```

打开 `http://127.0.0.1:7860`。在“设置”中填写你选择的 Base URL、Model 和 API Key并点击“测试当前配置”。用户可选择 Ollama、DeepSeek API 或 OpenAI API；开发验证使用本地 `gemma4:e4b`。本练习建议关闭“新任务使用内置知识库”。不要保存真实密钥。

```matlab
cd('/Users/huangyichuan/workspace/THU/control-agent/simulations/04_optical_transition')
lab = setup_case();
```

仓库移动后只改 `cd`；包装函数会自动找到公共运行时。`lab` 包含 `case_dir`、`config`、`model_name`、`model_path`；需要重建时运行 `modelPath = build_model();`。

## 2. 按字段新建任务

在“引导工作台”新建自定义任务：

| 页面字段 | 填写值 |
| --- | --- |
| 设备与目标 | [01_task_description.txt](prompts/01_task_description.txt) |
| 任务类型 | 变化到新目标后保持 |
| 开始区域 / 初始输出值 | 归一化光强 0 附近 / `0` |
| 中间目标（逗号分隔） | `0.25` |
| 目标区域 | 归一化光强 0.5 附近 |
| 到达目标时间上限 / 最少验证阶段切换次数 | `10` / `2` |
| 输出 1 名称 / 单位 | `optical_intensity` / `normalized` |
| 输入 1 名称 / 输入单位 | `led_current` / `normalized` |
| 输入下限 / 输入上限 / 软件试验停止阈值 | `-1` / `1` / `3` |
| 参考目标 | `0.5` |
| 评价区域（适用的工作范围） | 归一化光强由 0 过渡到 0.5 的软件仿真工作区 |
| 采样间隔 / 每次运行时长 / 重复运行次数 | `0.02` / `20` / `20` |
| 稳定后允许偏离目标多少 | `0.03` |

展开“性能要求与预算（可选）”，勾选并填写允许超过目标 `0.1`、希望多少秒内稳定 `10`、至少保持多少秒 `2`、重复试验成功率下限 `0.8`。点击“校验并核对”，核对页面生成的 3 个阶段、2 次交接、目标进入与最终保持约定，再勾选“我已核对目标、软件试验边界与预算”并点击“确认软件边界并开始”。

## 3. 提交真实的设计来源说明

把 [02_diagnosis.txt](prompts/02_diagnosis.txt) 完整复制到当前自然语言步骤。它以“以下来自固定仿真模型的设计说明，不是本任务实测结果”开头，列出固定模型的设计条件，同时明确实际响应、阶段交接、重复性和性能表现仍未测得。它不声称已经运行实验，也不提供控制器数值或性能结论。逐维追问时只从 [03_clarifications.txt](prompts/03_clarifications.txt) 复制对应的完整段落并保留段首来源说明；页面追问实测现象时仍应如实回答“不知道”。

页面记录完这些设计条件并显示“继续下一步”后，点击“继续下一步”，再进入软件来源选择。

## 4. 选择软件来源并完成预检查

选择“外部软件仿真”，点击“确认数据来源”，下载“下载采集请求包 ZIP”。先在 MATLAB 运行：

```matlab
cfdcSim.preflight(lab)
```

省略路径会打开选择器；也可直接传入实际下载位置：

```matlab
cfdcSim.preflight(lab, '/absolute/path/to/downloaded-operator-package.zip')
```

预检查通过后，人工核对通道、单位、三个阶段与两次交接、记录工具、停止条件和初始条件。只有全部实际完成才选择“检查完成，可以继续”并使用 [04_operator_note.txt](prompts/04_operator_note.txt)；否则选择“需要澄清”。

## 5. 运行识别并上传全部 CSV

```matlab
identification = cfdcSim.run_identification(lab);
identification.run_dir
identification.files
```

也可显式传入下载包绝对路径。在“选择实验数据”中上传 `identification.files` 列出的全部 CSV，再点击“检查上传数据”。不要把请求模板当结果，不要漏掉阶段或重复记录。

## 6. 核对并冻结评价约定

上传通过、系统形成候选后，核对冻结页面的三个阶段、两次交接、最终目标、边界、采样、重复次数和最终保持。勾选“我已核对冻结约定，确认进入开发评价”，点击“确认并冻结评价约定”。

## 7. 运行开发评价并上传结果 ZIP

点击“准备本轮外部运行包”和“下载本轮完整运行包 ZIP”，然后运行：

```matlab
evaluation = cfdcSim.run_evaluation(lab);
evaluation.run_dir
evaluation.files
evaluation.result_zip
```

下载包是输入；`evaluation.result_zip` 是 MATLAB 返回物。在“选择完整结果 ZIP”中选择后者，点击“校验并提交本轮轨迹”。

## 8. 按实际分支继续候选或全新确认

若进入 `capability_gap`，阅读原因并保留全部产物；这不代表性能通过。若页面提供“开始有界外部调优”，每个候选必须使用自己的新运行包。若进入“独立确认”，重新下载确认包并生成全新轨迹，不得复用开发评价或调优数据。不要为匹配历史分支而改变阈值。

## 9. 导出最终记录

在“评价结果”查看状态与指标，使用“下载原始报告”保存报告；打开“专家工具”，在“下载”中选择“下载完整产物”保存完整审计。分别保留请求包、`runs/` 返回物和最终导出，不要将本地生成工件提交到 Git。
