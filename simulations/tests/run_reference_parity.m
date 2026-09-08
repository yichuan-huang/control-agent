function run_reference_parity(folder)
%RUN_REFERENCE_PARITY Execute fixtures prepared by reference_parity.py in Simulink.
addpath(fileparts(fileparts(mfilename('fullpath'))));
fixtures=jsondecode(fileread(fullfile(folder,'fixtures.json')));
for i=1:numel(fixtures)
    f=fixtures(i); lab=cfdcSim.setup(f.case_dir,false); req=f.request;
    times=linspace(0,req.horizon_s,ceil(req.horizon_s/req.sample_time_s)+1).';
    u=req.control_inputs{1}; y=req.measured_signals{1};
    spec=struct('mode','evaluation','plant',lab.config.plant,'initial_state',f.initial_state(:), ...
        'input_name',u,'output_name',y,'dt',times(2),'horizon',req.horizon_s,'times',times, ...
        'excitation',zeros(size(times)),'bounds',req.input_bounds.(u)(:).', ...
        'request',req,'disturbance',req.disturbance);
    trial=cfdcSim.run_simulation(lab,spec,'',f.name);
    trial.trial_id=f.scenario.trial_id; trial.scenario_id=f.scenario.scenario_id; trial.seed=f.scenario.seed;
    cfdcSim.write_json(fullfile(folder,[f.name,'_actual.json']),trial);
    fprintf('Simulink parity trace %d/%d: %s\n',i,numel(fixtures),f.name);
end
end
