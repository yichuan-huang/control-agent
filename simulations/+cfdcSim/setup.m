function lab=setup(caseDir,showModel)
%SETUP Check the two required products and prepare this independent apparatus.
if nargin<2, showModel=true; end
assert(license('test','Simulink') && ~isempty(ver('simulink')), ...
    'cfdcSim:MissingSimulink','MATLAB and an available Simulink license are required.');
root=fileparts(fileparts(mfilename('fullpath'))); addpath(root);
caseDir=char(java.io.File(caseDir).getCanonicalPath());
config=jsondecode(fileread(fullfile(caseDir,'case_config.json')));
assert(strcmp(config.schema_version,'cfdc-simulink-case/v1'),'cfdcSim:InvalidCase','Unsupported case version.');
modelPath=fullfile(caseDir,'model',[config.model_name,'.slx']);
if ~isfile(modelPath), modelPath=cfdcSim.build_model(caseDir); end
load_system(modelPath);
wasDirty=get_param(config.model_name,'Dirty');
lab=struct('case_dir',caseDir,'config',config,'model_name',config.model_name,'model_path',modelPath);
for folder={'incoming','runs'}
    path=fullfile(caseDir,folder{1}); if ~isfolder(path), mkdir(path); end
end
% Direct Run is an explicit zero-initial-state open-loop preview, not evidence.
spec=struct('mode','identification','plant',config.plant, ...
    'initial_state',zeros(numel(config.plant.denominator)-1,1), ...
    'dt',0.02,'horizon',20,'times',(0:0.02:20)','bounds',[-1,1], ...
    'disturbance',[],'stop_condition',struct('state_stop',3), ...
    'input_name',config.task.control_input,'output_name',config.task.measured_signals{1});
spec.excitation=0.2*ones(size(spec.times));
key=['preview_',config.model_name];
assert(strcmp(get_param(config.model_name,'SimulationStatus'),'stopped'),'cfdcSim:ModelBusy','Stop this model before setup.');
cfdcSim.registry('remove',key); cfdcSim.registry('put',key,cfdcSim.Context(spec));
workspace=get_param(config.model_name,'ModelWorkspace');
workspace.assignin('cfdc_run_key',key); workspace.assignin('cfdc_dt',spec.dt);
workspace.assignin('cfdc_bounds',spec.bounds);
set_param(config.model_name,'Dirty',wasDirty);
if showModel, open_system(config.model_name); end
fprintf('已准备 %s：%s\nMATLAB %s；Simulink 许可证可用。\n',config.title_cn,modelPath,version);
fprintf('实验请使用 cfdcSim.run_identification / run_evaluation 读取本轮下载包。\n');
end
