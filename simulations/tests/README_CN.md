# 仿真验收复现

这些工具用于开发验收，普通用户只需各案例的 `README_CN.md`。运行环境为 MATLAB R2026a 与 Simulink；Python 对照工具使用仓库的 `uv.lock`。MATLAB 未启动、缺少产品或许可证失败时，应记录为未执行，不能计为通过。

在仓库根目录的终端准备独立测试目录：

```bash
uv run --locked python simulations/tests/reference_parity.py prepare /tmp/cfdc-parity
uv run --locked python simulations/tests/package_fixtures.py /tmp/cfdc-packets
```

在 MATLAB 执行（已有同名结果时，换用新的测试目录）：

```matlab
root = '/Users/huangyichuan/workspace/THU/control-agent';
addpath(fullfile(root, 'simulations'), fullfile(root, 'simulations', 'tests'));
results = runtests(fullfile(root, 'simulations', 'tests'));
assert(all([results.Passed]));
run_reference_parity('/tmp/cfdc-parity');
run_package_acceptance('/tmp/cfdc-packets');
```

回到终端比较完整轨迹、控制器状态、阶段和事件：

```bash
uv run --locked python simulations/tests/reference_parity.py check /tmp/cfdc-parity
```

数值容差固定为绝对 `1e-10`、相对 `1e-8`。十组对照覆盖五个正常场景、限幅与停止、阶段重置与超时、非采样点扰动。包验收拒绝十三种绑定或试次错误，并真实重跑辨识，检查记录不覆盖及改变输入后输出确实改变。

HTTP 闭环验收使用真实 API 下载和上传，诊断事实来自测试配置，不调用语言模型。先在终端运行：

```bash
uv run --locked python simulations/tests/http_acceptance.py init /tmp/cfdc-http
```

交替执行以下 MATLAB 命令与终端命令，直至显示 `0 MATLAB jobs; 5/5 terminal`：

```matlab
run_http_jobs('/tmp/cfdc-http');
```

```bash
uv run --locked python simulations/tests/http_acceptance.py advance /tmp/cfdc-http
```

最后核对原基准终态、独立重放和确认种子隔离：

```bash
uv run --locked python simulations/tests/http_acceptance.py verify /tmp/cfdc-http
```

该验收不能替代浏览器与真实模型验收。浏览器验收应从五个新任务开始，按各案例的操作手册填写字段，显式选择本地 `gemma4:e4b`，逐轮下载、执行和上传。公开报告中的模型调用记录、上传回执、冻结绑定、评价重放和最终确认共同构成证据。真实任务结论由 Kernel 给出，不得为了复制预期路径修改阈值。

相关 Python 回归与代码检查：

```bash
uv run --locked ruff format --check simulations/tests
uv run --locked ruff check simulations/tests
uv run --locked pytest -q tests/test_external_http_flow.py tests/test_kernel_external.py tests/test_controller_execution.py
git diff --check
```

本地验收报告可放在已忽略的 `simulations/validation/`；实验原始文件仍保存在对应案例的 `runs/`。测试目录与历史报告均不是运行五个案例的依赖。
