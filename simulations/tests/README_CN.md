# 仿真验收复现

这些工具用于开发验收，普通用户只需各案例的 `README_CN.md`。MATLAB R2026a 与 Simulink 在宿主机运行；Python 和浏览器客户端在 Docker 内使用仓库的锁文件。MATLAB 未启动、缺少产品或许可证失败时，应记录为未执行，不能计为通过。

先按[首次准备](../README_CN.md#first-start)构建 Docker 镜像。每次验收使用新的 `output/docker-validation/<本次名称>` 目录；该目录在宿主机与容器中的 `/exchange` 之间绑定，并在 MATLAB 中作为独立仿真副本，避免改动仓库内的练习结果。以下以 `acceptance` 为本次名称；已有同名目录时请更换名称，不要覆盖旧证据。

**粘贴到仓库根目录的终端：**准备独立测试目录和仿真源码副本，再生成对照包。

```bash
mkdir -p output/docker-validation/acceptance
docker compose --profile checks run --rm -v "$PWD/output/docker-validation/acceptance:/exchange" python-check python -c "import shutil; shutil.copytree('/app/simulations', '/exchange/simulations')"
docker compose --profile checks run --rm -v "$PWD/output/docker-validation/acceptance:/exchange" python-check python simulations/tests/reference_parity.py prepare /exchange/parity
docker compose --profile checks run --rm -v "$PWD/output/docker-validation/acceptance:/exchange" python-check python simulations/tests/package_fixtures.py /exchange/packets
```

在 MATLAB 执行（已有同名结果时，换用新的测试目录）：

```matlab
root = uigetdir(pwd, '选择包含 app.py 的 control-agent 仓库根目录');
assert(~isequal(root, 0) && isfile(fullfile(root, 'app.py')), '请选择正确的仓库根目录。');
exchangeRoot = fullfile(root, 'output', 'docker-validation', 'acceptance');
addpath(fullfile(exchangeRoot, 'simulations'), fullfile(exchangeRoot, 'simulations', 'tests'));
results = runtests(fullfile(exchangeRoot, 'simulations', 'tests'));
assert(all([results.Passed]));
run_reference_parity(fullfile(exchangeRoot, 'parity'));
run_package_acceptance(fullfile(exchangeRoot, 'packets'));
```

回到终端比较完整轨迹、控制器状态、阶段和事件：

```bash
docker compose --profile checks run --rm -v "$PWD/output/docker-validation/acceptance:/exchange" python-check python simulations/tests/reference_parity.py check /exchange/parity
```

数值容差固定为绝对 `1e-10`、相对 `1e-8`。十组对照覆盖五个正常场景、限幅与停止、阶段重置与超时、非采样点扰动。包验收拒绝十三种绑定或试次错误，并真实重跑辨识，检查记录不覆盖及改变输入后输出确实改变。

HTTP 闭环验收使用真实 API 下载和上传，诊断事实来自测试配置，不调用语言模型。先在终端运行：

```bash
docker compose --profile checks run --rm -v "$PWD/output/docker-validation/acceptance:/exchange" python-check python simulations/tests/http_acceptance.py init /exchange/http --case-root /exchange/simulations --cases 02_vacuum_hold 05_ink_disturbance_recovery
```

先确保已经执行上面的 MATLAB `addpath` 代码。按下面顺序交替执行 MATLAB 命令和 Docker 命令，每次等待上一条完成，直至终端显示 `0 MATLAB jobs; 2/2 terminal`：

```matlab
run_http_jobs(fullfile(exchangeRoot, 'http'));
```

```bash
docker compose --profile checks run --rm -v "$PWD/output/docker-validation/acceptance:/exchange" python-check python simulations/tests/http_acceptance.py advance /exchange/http
```

最后核对原基准终态、独立重放和确认种子隔离：

```bash
docker compose --profile checks run --rm -v "$PWD/output/docker-validation/acceptance:/exchange" python-check python simulations/tests/http_acceptance.py verify /exchange/http
```

该 HTTP 验收使用类型化已知诊断事实，不调用模型，不能替代浏览器与真实模型验收。浏览器验收在独立 Compose 项目中启动正式镜像，以免与日常数据混用：

```bash
CFDC_PORT=7868 docker compose -p cfdc-validation up --build --wait -d app
env -u CFDC_LLM_BASE_URL -u CFDC_LLM_MODEL -u CFDC_LLM_API_KEY \
  docker compose --env-file .env -p cfdc-validation --profile checks run --build --rm \
  -e CFDC_RUN_LIVE_LLM=1 -e CFDC_LLM_BASE_URL -e CFDC_LLM_MODEL -e CFDC_LLM_API_KEY \
  -v "$PWD/output/docker-validation/acceptance:/exchange" browser-live \
  python /app/scripts/run_live_llm.py command node scripts/simulation-browser-acceptance.mjs init
```

先按项目 README 的真实 API 验证说明填写本地 `.env`；缺少文件时运行 `bash scripts/test_live_llm.sh service` 创建空白模板。脚本从浏览器为 02、05 新建任务，使用配置的服务、模型和密钥，关闭 RAG，提交案例自然语言诊断，选择外部软件来源，并下载本轮真实请求包。命令通过容器内入口脱敏输出，不会自动选择或准备 Ollama 模型。MATLAB 使用同一交换目录执行：

```matlab
run_http_jobs(fullfile(exchangeRoot, 'browser'));
```

然后回到终端运行 `advance`；按这两条命令交替执行，直到显示 `0 MATLAB jobs; 2/2 terminal`：

```bash
env -u CFDC_LLM_BASE_URL -u CFDC_LLM_MODEL -u CFDC_LLM_API_KEY \
  docker compose --env-file .env -p cfdc-validation --profile checks run --rm \
  -e CFDC_RUN_LIVE_LLM=1 -e CFDC_LLM_BASE_URL -e CFDC_LLM_MODEL -e CFDC_LLM_API_KEY \
  -v "$PWD/output/docker-validation/acceptance:/exchange" browser-live \
  python /app/scripts/run_live_llm.py command node scripts/simulation-browser-acceptance.mjs advance
CFDC_PORT=7868 docker compose -p cfdc-validation --profile checks run --rm \
  -v "$PWD/output/docker-validation/acceptance:/exchange" python-check \
  python simulations/tests/http_acceptance.py verify /exchange/browser
```

最后一条 `verify` 只在全部任务到达终态后执行，核对上传回执、评价重放与独立确认种子。脚本每轮通过页面选择上传文件、核对冻结设置，并保存报告供复核。仓库不附带历史运行数据。真实任务结论由 Kernel 给出，不得为了复制预期路径修改阈值。

相关 Python 回归与代码检查：

```bash
docker compose --profile checks run --build --rm python-check
git diff --check
```

本次验收的原始文件和报告仅放在已忽略的 `output/docker-validation/acceptance/`。记录检查结果后只清理这个测试专属目录；测试目录与历史报告均不是运行五个案例的依赖。默认不带 `--cases` 时，HTTP 验收仍会运行全部五例。
