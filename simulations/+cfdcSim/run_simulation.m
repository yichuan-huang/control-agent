function trial=run_simulation(lab,spec,runDir,trialName)
%RUN_SIMULATION Obtain every measured sample from the actual Simulink model.
key=char(java.util.UUID.randomUUID());
ctx=cfdcSim.Context(spec);
cfdcSim.registry('put',key,ctx);
cleanup=onCleanup(@() cfdcSim.registry('remove',key));
ds=Simulink.SimulationData.Dataset;
excitation=timeseries(spec.excitation,spec.times);
excitation=setinterpmethod(excitation,'zoh'); ds=ds.addElement(excitation,'Excitation');
disturbance=zeros(size(spec.times));
if ~isempty(spec.disturbance)
    d=spec.disturbance;
    disturbance(spec.times>=d.time_s & spec.times<d.time_s+d.duration_s)=d.amplitude;
end
pulse=timeseries(disturbance,spec.times);
pulse=setinterpmethod(pulse,'zoh'); ds=ds.addElement(pulse,'Disturbance');
in=Simulink.SimulationInput(lab.model_name);
in=in.setVariable('cfdc_run_key',key,'Workspace',lab.model_name);
in=in.setVariable('cfdc_dt',spec.dt,'Workspace',lab.model_name);
in=in.setVariable('cfdc_bounds',spec.bounds,'Workspace',lab.model_name);
in=in.setExternalInput(ds);
in=in.setModelParameter('StopTime',sprintf('%.17g',spec.horizon), ...
    'FixedStep',sprintf('%.17g',spec.dt),'SimulationMode','normal');
out=sim(in);
ctx.commit();
record=out.cfdc_record;
time=double(record.Time(:)); data=double(squeeze(record.Data));
if size(data,1)~=numel(time), data=data.'; end
if ctx.numericalFailure
    % The nonfinite measurement is never replaced or exported as evidence.
    keep=numel(ctx.samples); time=time(1:keep); data=data(1:keep,:);
    assert(keep>0,'cfdcSim:NumericalFailure','No finite sample was obtained.');
end
assert(size(data,2)==8 && size(data,1)==numel(ctx.samples), ...
    'cfdcSim:RecorderMismatch','Simulink logger and controller sample counts differ.');
assert(all(isfinite(data(:))) && numel(time)<=numel(spec.times) && ...
    max(abs(time-spec.times(1:numel(time))))<=1e-9, ...
    'cfdcSim:RecorderMismatch','Simulink produced an invalid sample timeline.');
assert(max(abs(data(:,3)-min(max(data(:,4),spec.bounds(1)),spec.bounds(2))))<=1e-12, ...
    'cfdcSim:RecorderMismatch','Actual actuator signal differs from frozen clipping.');
states=cellfun(@(s) s.state,ctx.samples,'UniformOutput',false);
phaseIds=cellfun(@(s) s.phase_id,ctx.samples,'UniformOutput',false);
trace=struct('time_s',{num2cell(time.')}, ...
    'outputs',struct(spec.output_name,{num2cell(data(:,1).')}), ...
    'measurements',struct(spec.output_name,{num2cell(data(:,1).')}), ...
    'references',struct(spec.output_name,{num2cell(data(:,2).')}), ...
    'control_inputs',struct(spec.input_name,{num2cell(data(:,3).')}), ...
    'raw_control_inputs',struct(spec.input_name,{num2cell(data(:,4).')}), ...
    'controller_states',{states},'phase_ids',{phaseIds});
trial=struct('trajectory',trace,'events',{ctx.eventLog},'stop_event',ctx.stop_event);
if ~isempty(runDir)
    save(fullfile(runDir,[trialName,'-simulink.mat']),'out','spec','-v7');
end
end
