function result=run_evaluation(lab,packagePath)
%RUN_EVALUATION Execute one frozen development, tuning, or confirmation packet.
if nargin<2, packagePath=[]; end
check=cfdcSim.preflight(lab,packagePath);
assert(strcmp(check.kind,'evaluation'),'cfdcSim:WrongPackage','Select a frozen execution package.');
runDir=cfdcSim.new_run(lab,check); files={}; initializations={};
request=check.request; manifest=check.manifest;
payloadDir=fullfile(runDir,'upload'); mkdir(payloadDir);
cfdcSim.write_bytes(fullfile(payloadDir,'manifest.json'),check.package.members('manifest.json'));
try
    for i=1:numel(request.trials)
        scenario=request.trials(i);
        count=ceil(request.horizon_s/request.sample_time_s);
        times=linspace(0,request.horizon_s,count+1).';
        stream=RandStream('mt19937ar','Seed',scenario.seed);
        n=numel(lab.config.plant.denominator)-1;
        x0=(2*rand(stream,n,1)-1)*lab.config.plant.initial_perturbation;
        disturbance=request.disturbance;
        if isfield(scenario,'disturbance'), disturbance=scenario.disturbance; end
        spec=struct('mode','evaluation','plant',lab.config.plant,'initial_state',x0, ...
            'input_name',check.input_name,'output_name',check.output_name,'dt',times(2), ...
            'horizon',request.horizon_s,'times',times,'excitation',zeros(size(times)), ...
            'bounds',request.input_bounds.(check.input_name)(:).', ...
            'request',request,'disturbance',disturbance);
        trialName=sprintf('trial-%04d',i);
        trial=cfdcSim.run_simulation(lab,spec,runDir,trialName);
        trial.trial_id=scenario.trial_id; trial.scenario_id=scenario.scenario_id; trial.seed=scenario.seed;
        path=fullfile(payloadDir,manifest.trials(i).file);
        cfdcSim.write_json(path,trial); files{end+1}=path;
        initializations{end+1}=struct('trial_id',scenario.trial_id,'seed',scenario.seed, ...
            'generator','mt19937ar','initial_state',x0(:).');
        if i==1, cfdcSim.plot_trial(trial,fullfile(runDir,'first-trial.png')); end
        fprintf('%s %d/%d：%s；停止=%d\n',manifest.stage,i,numel(request.trials),scenario.trial_id,trial.stop_event.triggered);
    end
    resultZip=fullfile(runDir,[manifest.stage,'-results.zip']);
    zip(resultZip,[{'manifest.json'},{manifest.trials.file}],payloadDir);
    result=struct('run_dir',runDir,'files',{files},'result_zip',resultZip,'status','completed','stage',manifest.stage);
    cfdcSim.write_json(fullfile(runDir,'initializations.json'),initializations);
    cfdcSim.write_json(fullfile(runDir,'completion.json'),result);
catch exception
    cfdcSim.write_json(fullfile(runDir,'failure.json'),struct('identifier',exception.identifier,'message',exception.message));
    rethrow(exception)
end
fprintf('本轮完整结果 ZIP：\n%s\n请上传此文件，由 CFDC 判定并重放。\n',resultZip);
end
