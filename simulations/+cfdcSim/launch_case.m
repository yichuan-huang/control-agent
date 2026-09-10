function state = launch_case(caseDir, services)
%LAUNCH_CASE Run the Chinese desktop menu with state local to this invocation.
% Optional services adapt desktop interaction for automated interface tests.
if nargin < 2, services = struct(); end
defaults = struct('menu', @menu, 'select', @cfdcSim.select_package, ...
    'setup', @cfdcSim.setup, 'preflight', @cfdcSim.preflight, ...
    'identify', @cfdcSim.run_identification, 'evaluate', @cfdcSim.run_evaluation, ...
    'display', @(message) fprintf('%s\n', message), 'error', @showError);
names = fieldnames(defaults);
for i = 1:numel(names)
    if ~isfield(services, names{i}), services.(names{i}) = defaults.(names{i}); end
end
caseDir = char(java.io.File(char(caseDir)).getCanonicalPath());
config = jsondecode(fileread(fullfile(caseDir, 'case_config.json')));
state = struct('case_dir', caseDir, 'lab', [], 'acquisition', [], 'last_result', []);
while true
    action = services.menu(['CFDC 仿真实验｜', config.title_cn], ...
        '初始化／打开模型', '选择采集 ZIP 并预检', ...
        '执行已预检采集（先在 WebUI 完成操作检查）', ...
        '运行本轮评价（每次选择新 ZIP）', '显示上次结果位置', '退出');
    if action == 0 || action == 6, return; end
    try
        switch action
            case 1
                state.acquisition = [];
                state.lab = [];
                state.lab = services.setup(caseDir, true);
            case 2
                requireLab(state);
                selected = services.select(state.lab, '选择本任务刚下载的采集请求 ZIP');
                if isempty(selected), continue; end
                state.acquisition = [];
                digest = fingerprint(selected);
                check = services.preflight(state.lab, selected);
                assert(strcmp(check.kind, 'identification'), 'cfdcSim:WrongPackage', ...
                    '本步需要采集请求 ZIP。');
                assert(strcmp(digest, fingerprint(selected)), 'cfdcSim:PackageChanged', ...
                    '预检期间文件已改变，请重新选择原始包并预检。');
                state.acquisition = struct('path', selected, 'fingerprint', digest);
                services.display(['采集预检通过。操作卡：', newline, evalc('disp(check.card)')]);
                services.display('请回到 WebUI，据实完成操作检查，再选择“执行已预检采集”。');
            case 3
                requireLab(state);
                assert(~isempty(state.acquisition), 'cfdcSim:PreflightRequired', ...
                    '请先选择采集 ZIP 并预检，再在 WebUI 完成操作检查。');
                acquisition = state.acquisition;
                state.acquisition = [];
                assert(strcmp(acquisition.fingerprint, fingerprint(acquisition.path)), ...
                    'cfdcSim:PackageChanged', '采集包已改变，请重新选择原始包并预检。');
                state.last_result = services.identify(state.lab, acquisition.path);
                showResult(state.last_result, services.display);
            case 4
                requireLab(state);
                selected = services.select(state.lab, '选择本轮新下载的完整运行请求 ZIP');
                if isempty(selected), continue; end
                check = services.preflight(state.lab, selected);
                assert(strcmp(check.kind, 'evaluation'), 'cfdcSim:WrongPackage', ...
                    '本步需要冻结的完整运行请求 ZIP。');
                services.display(sprintf('本轮阶段：%s\n请求：%s\n会话：%s', ...
                    check.manifest.stage, check.manifest.request_id, check.manifest.session_id));
                state.last_result = services.evaluate(state.lab, selected);
                showResult(state.last_result, services.display);
            case 5
                showResult(state.last_result, services.display);
        end
    catch exception
        if strcmp(exception.identifier, 'cfdcSim:SelectionCancelled'), continue; end
        services.error(exception);
    end
end
end

function requireLab(state)
assert(~isempty(state.lab), 'cfdcSim:SetupRequired', '请先选择“初始化／打开模型”。');
end

function digest = fingerprint(path)
file = fopen(path, 'rb');
assert(file >= 0, 'cfdcSim:PackageMissing', '无法读取采集请求包：%s', path);
cleanup = onCleanup(@() fclose(file));
digest = cfdcSim.sha256(fread(file, Inf, '*uint8'));
end

function showResult(result, display)
if isempty(result)
    display('本次菜单尚无完成结果。历史文件保留在案例 runs/ 中。');
    return
end
display(['本轮结果目录：', result.run_dir]);
if isfield(result, 'result_zip')
    display(sprintf('本轮阶段：%s\n只上传这个结果 ZIP：\n%s', result.stage, result.result_zip));
else
    display(sprintf('待上传 CSV 共 %d 份：\n%s', numel(result.files), strjoin(result.files, newline)));
    stopped = any(cellfun(@(r) r.stop_event.triggered, result.repeats));
    display(sprintf('是否有重复触发停止：%d（1=是，0=否）', stopped));
end
end

function showError(exception)
fprintf(2, '[%s]\n%s\n', exception.identifier, ...
    getReport(exception, 'extended', 'hyperlinks', 'off'));
end
