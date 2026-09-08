function result=run_identification(lab,packagePath)
%RUN_IDENTIFICATION Execute every protocol-bound blank CSV in Simulink.
if nargin<2, packagePath=[]; end
check=cfdcSim.preflight(lab,packagePath);
assert(strcmp(check.kind,'identification'),'cfdcSim:WrongPackage','Select an acquisition operator package.');
runDir=cfdcSim.new_run(lab,check); files={}; records={};
try
    for i=1:numel(check.repeats)
        repeat=check.repeats{i}; card=check.card;
        spec=struct('mode','identification','plant',lab.config.plant, ...
            'initial_state',zeros(numel(lab.config.plant.denominator)-1,1), ...
            'input_name',check.input_name,'output_name',check.output_name, ...
            'dt',card.sample_period_s,'horizon',card.duration_s,'times',repeat.times, ...
            'excitation',repeat.inputs,'bounds',card.input_bounds(:).', ...
            'stop_condition',card.stop_condition,'disturbance',[]);
        trialName=sprintf('repeat-%04d',i);
        trial=cfdcSim.run_simulation(lab,spec,runDir,trialName);
        y=trial.trajectory.outputs.(check.output_name);
        lines=cell(1,numel(y)+1); lines{1}=repeat.header;
        for k=1:numel(y)
            row=repeat.rows(k,:); row{end}=sprintf('%.17g',y{k}); lines{k+1}=strjoin(row,',');
        end
        path=fullfile(runDir,repeat.filename);
        bytes=[uint8([239,187,191]),unicode2native([strjoin(lines,sprintf('\r\n')),sprintf('\r\n')],'UTF-8')];
        cfdcSim.write_bytes(path,bytes); files{end+1}=path;
        cfdcSim.write_json(fullfile(runDir,[trialName,'-events.json']),trial.stop_event);
        cfdcSim.plot_trial(trial,fullfile(runDir,[trialName,'.png']));
        records{end+1}=struct('file',repeat.filename,'samples',numel(y),'stop_event',trial.stop_event);
        fprintf('采集 %d/%d 完成：%s\n',i,numel(check.repeats),path);
    end
    result=struct('run_dir',runDir,'files',{files},'status','completed','repeats',{records});
    cfdcSim.write_json(fullfile(runDir,'completion.json'),result);
catch exception
    cfdcSim.write_json(fullfile(runDir,'failure.json'),struct('identifier',exception.identifier,'message',exception.message));
    rethrow(exception)
end
fprintf('请在 WebUI 一次选择上述全部 %d 份 CSV；停止记录请同时查看本轮日志。\n',numel(files));
end
