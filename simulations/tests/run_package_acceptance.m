function run_package_acceptance(folder)
%RUN_PACKAGE_ACCEPTANCE Check binding rejection and real acquisition exports.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(root);
lab=cfdcSim.setup(fullfile(root,'01_optical_hold'),false);
cfdcSim.preflight(lab,fullfile(folder,'operator_valid.zip'));
cfdcSim.preflight(lab,fullfile(folder,'execution_valid.zip'));
for name={'operator_stop','operator_timing','operator_bounds','operator_cross_session', ...
        'execution_controller','execution_timing','execution_phases','execution_disturbance', ...
        'execution_seed','execution_split','execution_session'}
    try
        cfdcSim.preflight(lab,fullfile(folder,[name{1},'.zip']));
        error('test:AcceptedInvalid','Invalid packet accepted: %s',name{1});
    catch exception
        assert(strcmp(exception.identifier,'cfdcSim:BindingMismatch'),exception.message);
    end
end
for name={'operator_missing','execution_missing'}
    try
        cfdcSim.preflight(lab,fullfile(folder,[name{1},'.zip']));
        error('test:AcceptedInvalid','Incomplete packet accepted.');
    catch exception
        assert(strcmp(exception.identifier,'cfdcSim:MissingTrials'),exception.message);
    end
end
first=cfdcSim.run_identification(lab,fullfile(folder,'operator_valid.zip'));
again=cfdcSim.run_identification(lab,fullfile(folder,'operator_valid.zip'));
changed=cfdcSim.run_identification(lab,fullfile(folder,'operator_changed_input.zip'));
assert(~strcmp(first.run_dir,again.run_dir) && isfile(first.files{1}));
a=readmatrix(first.files{1},'NumHeaderLines',1); b=readmatrix(changed.files{1},'NumHeaderLines',1);
assert(max(abs(a(:,end)-b(:,end)))>0.1,'Changed excitation did not change actual Simulink output.');
cfdcSim.write_json(fullfile(folder,'acceptance.json'),struct('binding_rejections',13, ...
    'original_run',first,'rerun',again,'changed_input',changed));
fprintf('Packet acceptance passed: 13 rejections, immutable rerun and changed-input response.\n');
end
