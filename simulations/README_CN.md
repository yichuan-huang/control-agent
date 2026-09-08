# CFDC MATLAB/Simulink 软件仿真实验

本目录提供五个外部 Simulink 案例。它们把当前 WebUI 下载的协议或评价请求包交给 MATLAB 执行，再把协议绑定的原始结果传回 WebUI。`case_config.json` 固定案例接口和任务边界；`build_model.m` 可重复生成本地模型；`setup_case.m` 打开案例；`prompts/` 保存可复制的中文输入。生成的 `.slx`、下载包、运行目录和返回结果均为本地工件，不提交到仓库。

| 案例 | 任务 | 预期教学分支 |
| --- | --- | --- |
| [01 光强定点保持](01_optical_hold/README_CN.md) | `local_setpoint_hold` | 历史演练进入 `capability_gap` |
| [02 真空压力定点保持](02_vacuum_hold/README_CN.md) | `local_setpoint_hold` | 历史演练进入有界调优和独立确认 |
| [03 油墨黏度定点保持](03_ink_viscosity_hold/README_CN.md) | `local_setpoint_hold` | 历史演练进入有界调优和独立确认 |
| [04 光强分阶段过渡](04_optical_transition/README_CN.md) | `transition_then_hold` | 历史演练进入 `capability_gap` |
| [05 油墨黏度扰动恢复](05_ink_disturbance_recovery/README_CN.md) | `disturbance_recovery_to_hold` | 历史演练进入有界调优和独立确认 |

这些分支只说明既往开发演练的预期路径，不保证新任务得到相同结论。Kernel 会根据本次上传的原始轨迹、冻结绑定和独立裁决决定实际结果；不要为了得到预期分支而修改阈值或数据。

公共 MATLAB 接口如下。`packagePath` 可省略；省略时会打开文件选择器。识别返回结构包含 `run_dir` 和 `files`，评价返回结构还包含 `result_zip`。下载的请求包是输入，`runs/` 中生成的 CSV 或结果 ZIP 是返回物，两者不能互换。

```matlab
lab = setup_case();
cfdcSim.preflight(lab)
identification = cfdcSim.run_identification(lab);
evaluation = cfdcSim.run_evaluation(lab);
```

默认命令使用仓库当前绝对路径 `/Users/huangyichuan/workspace/THU/control-agent`。仓库移动后，只需将手册第一条 `cd` 改成新位置；包装函数会由案例目录自动找到 `simulations/+cfdcSim`，不需要修改源码。

开发者可使用[验收复现说明](tests/README_CN.md)运行 MATLAB 单元测试、Python 轨迹对照、错包测试和真实 HTTP 上传闭环。
