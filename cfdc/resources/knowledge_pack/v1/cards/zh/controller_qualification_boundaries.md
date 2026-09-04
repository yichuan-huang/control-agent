# 控制器资格审查、有界增益变化、回滚与权限边界

## 定义

控制器候选只有通过确定性的约束、稳定性和性能检查后才能成为冻结的软件 artifact。去调、限幅、有界增益更新和回滚是审查策略，不是 RAG 授权。

## 适用前提

路线、Profile、特征、控制器拓扑、输入和速率边界必须由 Registry 与 Kernel 明确，评价数据必须独立且可追溯。

## 所需证据

需要 FeatureArtifact、Controller IR、饱和和 slew limits、资格报告、冻结版本、独立评价、前一版本以及更新理由。

## 提取方法

逐项核对幅值、速率、饱和时间、稳定与性能指标；每次只允许有界增益变化，保留旧 freeze，并在资格恶化时回滚。

## 数据质量检查

检查训练与评价数据是否混用、边界是否缺失、饱和是否被裁剪、指标是否跨试次一致，以及 revision 和哈希是否匹配。

## 控制器影响

本卡只解释 Registry 已注册的 detuned PI、damping 或 saturated PD、cascade、NMP outer-loop、delay-aware PI 和 MIMO 配对解耦路线，不创建新控制器或重复 Profile artifacts。

## Critic 检查

拒绝超幅或超速执行器命令、无证据增益变更、不安全零点消除、无回滚目标、未注册拓扑和把 RAG 内容当作参数事实。

## 不能证明

软件仿真 qualification 不能授予实体硬件操作权限；`ready_for_operator_review` 也不是执行授权。

## 来源引用

`repo-knowledge-registry-v1`、`repo-kernel-boundaries-v0.3.2`、`ntnu-simc-2003`、`caltech-feedback-systems-2008`。
