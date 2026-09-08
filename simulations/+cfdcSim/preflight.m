function check=preflight(lab,packagePath)
%PREFLIGHT Validate the actual packet before any experiment or operator check.
if nargin<2, packagePath=[]; end
packagePath=cfdcSim.choose_package(lab,packagePath);
package=cfdcSim.read_package(packagePath);
members=package.members;
inputName=lab.config.task.control_input;
outputName=lab.config.task.measured_signals{1};
if isKey(members,'operator_card.json')
    assert(~isKey(members,'execution-request.json'),'cfdcSim:WrongPackage','Ambiguous package kind.');
    card=decode(members,'operator_card.json');
    require(card,{'handoff_version','session_id','task_fingerprint','protocol_fingerprint', ...
        'handoff_fingerprint','data_kind','requested_signals','control_inputs','units','repeats','duration_s','sample_period_s','input_bounds','stop_condition'});
    assert(strcmp(card.handoff_version,'cfdc-operator-handoff/v1') && ...
        ismember(card.data_kind,{'siso_repeated_timeseries','step_b_repeated_staircase', ...
        'class_iv_frequency_repeats','class_iv_amplitude_release_repeats','class_iv_release_repeats'}), 'cfdcSim:UnsupportedContract','Unsupported acquisition contract.');
    bound=cfdcSim.canonical_members(members('operator_card.json'));
    remove(bound,'handoff_fingerprint');
    assert(strcmp(cfdcSim.sha256(unicode2native(cfdcSim.encode_members(bound),'UTF-8')),card.handoff_fingerprint), ...
        'cfdcSim:BindingMismatch','Operator card fingerprint mismatch. Download the original packet again.');
    channels(card.control_inputs,card.requested_signals,inputName,outputName);
    assert(strcmp(card.units.input,'normalized') && strcmp(card.units.outputs.(outputName),'normalized') && ...
        strcmp(card.units.time,'s'),'cfdcSim:UnitMismatch','These cases require normalized input/output and seconds.');
    bounds(card.input_bounds); limits(card.stop_condition,outputName);
    timing(card.sample_period_s,card.duration_s); positiveInteger(card.repeats,10000);
    names=sort(keys(members));
    names=names(endsWith(names,'.csv'));
    assert(numel(names)==card.repeats,'cfdcSim:MissingTrials','All acquisition repeat templates are required.');
    expected={'session_id','protocol_fingerprint','repeat','time_s',inputName,outputName};
    repeats=cell(1,numel(names)); numbers=zeros(1,numel(names));
    for i=1:numel(names)
        bytes=members(names{i}); text=native2unicode(bytes,'UTF-8');
        if ~isempty(text) && text(1)==char(65279), text(1)=[]; end
        assert(~contains(text,'"'),'cfdcSim:UnsupportedCSV','Expected the unmodified CFDC scalar CSV template.');
        lines=regexp(text,'\r\n|\n|\r','split');
        if isempty(lines{end}), lines(end)=[]; end
        assert(numel(lines)>=3 && isequal(strsplit(lines{1},','),expected), ...
            'cfdcSim:ChannelMismatch','CSV columns must exactly match the operator card.');
        rows=cellfun(@(line) strsplit(line,',','CollapseDelimiters',false),lines(2:end),'UniformOutput',false);
        assert(all(cellfun(@numel,rows)==numel(expected)),'cfdcSim:InvalidCSV','CSV row width mismatch.');
        rows=vertcat(rows{:});
        assert(all(strcmp(rows(:,1),card.session_id)) && all(strcmp(rows(:,2),card.protocol_fingerprint)), ...
            'cfdcSim:BindingMismatch','CSV session/protocol differs from the operator card.');
        repeatNumbers=str2double(rows(:,3)); times=str2double(rows(:,4)); inputs=str2double(rows(:,5));
        assert(all(repeatNumbers==repeatNumbers(1)),'cfdcSim:BindingMismatch','Mixed repeat identifiers.');
        positiveInteger(repeatNumbers(1),card.repeats);
        assert(all(cellfun(@isempty,rows(:,6))),'cfdcSim:WrongPackage','Acquisition requires blank downloaded templates.');
        expectedCount=round(card.duration_s/card.sample_period_s)+1;
        assert(numel(times)==expectedCount && all(isfinite(times)) && ...
            max(abs(times-(0:numel(times)-1)'*card.sample_period_s))<=1e-9 && ...
            abs(times(end)-card.duration_s)<=1e-9,'cfdcSim:InvalidTimeline','Acquisition time axis differs from its contract.');
        assert(all(isfinite(inputs)) && all(inputs>=card.input_bounds(1)) && all(inputs<=card.input_bounds(2)), ...
            'cfdcSim:InvalidBounds','Excitation exceeds the declared bounds.');
        numbers(i)=repeatNumbers(1);
        [~,name,ext]=fileparts(names{i});
        repeats{i}=struct('filename',[name,ext],'header',lines{1},'rows',{rows},'times',times,'inputs',inputs);
    end
    assert(isequal(sort(numbers),1:card.repeats),'cfdcSim:MissingTrials','Repeat identifiers are missing or duplicated.');
    check=struct('kind','identification','package',package,'card',card,'repeats',{repeats});
else
    assert(isKey(members,'execution-request.json') && isKey(members,'manifest.json'), ...
        'cfdcSim:WrongPackage','Select a downloaded execution package, not a result ZIP.');
    request=decode(members,'execution-request.json'); manifest=decode(members,'manifest.json');
    require(request,{'request_version','session_id','task_fingerprint','freeze_fingerprint','controller', ...
        'sample_time_s','horizon_s','measured_signals','tracked_signals','control_inputs','input_bounds', ...
        'references','trials','phases','disturbance','evaluation_split', ...
        'output_bounds','state_bounds','controller_state_bounds','state_stop'});
    require(manifest,{'format_version','request_id','session_id','task_fingerprint','freeze_fingerprint', ...
        'request_fingerprint','candidate_id','stage','trials'});
    assert(strcmp(request.request_version,'cfdc-execution/v1') && ...
        strcmp(manifest.format_version,'cfdc-external-workflow/v1'), ...
        'cfdcSim:UnsupportedContract','Unsupported execution package version.');
    bound=cfdcSim.canonical_members(members('manifest.json'));
    remove(bound,{'format_version','trials','request_fingerprint'});
    [~,requestJson]=cfdcSim.canonical_members(members('execution-request.json'));
    bound('execution_request')=requestJson;
    requestFields=cfdcSim.canonical_members(members('execution-request.json'));
    controllerFields=cfdcSim.canonical_members(unicode2native(requestFields('controller'),'UTF-8'));
    if isKey(controllerFields,'controller_fingerprint')
        expected=jsondecode(controllerFields('controller_fingerprint')); remove(controllerFields,'controller_fingerprint');
        assert(strcmp(cfdcSim.sha256(unicode2native(cfdcSim.encode_members(controllerFields),'UTF-8')),expected), ...
            'cfdcSim:BindingMismatch','ControllerIR fingerprint mismatch.');
    end
    assert(strcmp(cfdcSim.sha256(unicode2native(cfdcSim.encode_members(bound),'UTF-8')),manifest.request_fingerprint), ...
        'cfdcSim:BindingMismatch','Frozen request fingerprint mismatch. Download the original packet again.');
    fields={'session_id','task_fingerprint','freeze_fingerprint'};
    for i=1:numel(fields)
        assert(isequal(request.(fields{i}),manifest.(fields{i})),'cfdcSim:BindingMismatch','Manifest/request binding mismatch.');
    end
    assert(ismember(manifest.stage,{'development','tuning_probe','fresh_confirmation'}), ...
        'cfdcSim:BindingMismatch','Unknown execution stage.');
    split='development';
    if strcmp(manifest.stage,'fresh_confirmation'), split='fresh_confirmation'; end
    assert(strcmp(request.evaluation_split,split),'cfdcSim:BindingMismatch','Development and fresh confirmation cannot be mixed.');
    channels(request.control_inputs,request.measured_signals,inputName,outputName);
    assert(isequal(request.tracked_signals(:),{outputName}),'cfdcSim:ChannelMismatch','Tracked signal differs from this case.');
    assert(isequal(fieldnames(request.input_bounds),{inputName}) && ...
        isequal(fieldnames(request.references),{outputName}),'cfdcSim:ChannelMismatch','Bounds/reference channels differ.');
    channels(request.controller.control_inputs,request.controller.measured_signals,inputName,outputName);
    bounds(request.input_bounds.(inputName)); limits(request,outputName);
    validateattributes(request.references.(outputName),{'numeric'},{'scalar','real','finite'});
    timing(request.sample_time_s,request.horizon_s);
    cfdcSim.Controller(request.controller,request.input_bounds.(inputName));
    validatePhases(request.phases,outputName);
    validateDisturbance(request.disturbance,inputName,request.horizon_s);
    assert(isstruct(request.trials) && isstruct(manifest.trials) && ...
        numel(request.trials)==numel(manifest.trials) && ~isempty(request.trials), ...
        'cfdcSim:MissingTrials','Trial manifest is incomplete.');
    trialIds={request.trials.trial_id}; files={manifest.trials.file};
    assert(numel(unique(trialIds))==numel(trialIds) && numel(unique(files))==numel(files), ...
        'cfdcSim:MissingTrials','Duplicate trial IDs or result filenames.');
    for i=1:numel(manifest.trials)
        row=manifest.trials(i); scenario=request.trials(i);
        assert(strcmp(row.trial_id,scenario.trial_id),'cfdcSim:BindingMismatch','Trial ordering/identity mismatch.');
        assert(~isempty(regexp(row.file,'^trial-[0-9]+\.json$','once')) && ...
            ~isKey(members,row.file) && isKey(members,['templates/',row.file]), ...
            'cfdcSim:MissingTrials','Missing or invalid blank trial template.');
        template=decode(members,['templates/',row.file]);
        assert(strcmp(template.trial_id,scenario.trial_id) && strcmp(template.scenario_id,scenario.scenario_id) && ...
            template.seed==scenario.seed && isempty(template.trajectory.time_s), ...
            'cfdcSim:BindingMismatch','Template differs from its fixed trial.');
        validateattributes(scenario.seed,{'numeric'},{'scalar','finite','integer','nonnegative','<=',2^32-1});
        if isfield(scenario,'disturbance'), validateDisturbance(scenario.disturbance,inputName,request.horizon_s); end
    end
    check=struct('kind','evaluation','package',package,'request',request,'manifest',manifest);
end
check.input_name=inputName; check.output_name=outputName;
fprintf('预检通过：%s；输入 %s；输出 %s。\n',check.kind,inputName,outputName);
fprintf('已核对包绑定、通道、单位约定、记录格式、时间轴和停止阈值；模型初态与操作检查请据实确认。\n');
end

function value=decode(members,name)
assert(isKey(members,name),'cfdcSim:WrongPackage','Required ZIP member is missing: %s',name);
value=jsondecode(native2unicode(members(name),'UTF-8'));
assert(isstruct(value) && isscalar(value),'cfdcSim:InvalidPackage','JSON member must contain one object.');
end
function require(value,fields)
assert(isstruct(value) && all(isfield(value,fields)),'cfdcSim:InvalidPackage','Missing required contract fields.');
end
function channels(inputs,outputs,inputName,outputName)
assert(iscell(inputs) && iscell(outputs) && isequal(inputs(:),{inputName}) && isequal(outputs(:),{outputName}), ...
    'cfdcSim:ChannelMismatch','This package belongs to a different apparatus/interface.');
end
function bounds(pair)
assert(isnumeric(pair) && numel(pair)==2 && all(isfinite(pair)) && pair(1)<pair(2), ...
    'cfdcSim:InvalidBounds','Expected finite ordered bounds.');
end
function timing(dt,horizon)
validateattributes(dt,{'numeric'},{'scalar','real','finite','positive'});
validateattributes(horizon,{'numeric'},{'scalar','real','finite','>',dt});
assert(ceil(horizon/dt)<=1000000,'cfdcSim:InvalidTimeline','Sample budget exceeded.');
end
function positiveInteger(value,maximum)
validateattributes(value,{'numeric'},{'scalar','finite','integer','positive','<=',maximum});
end
function limits(value,outputName)
if isfield(value,'state_stop') && ~isempty(value.state_stop)
    validateattributes(value.state_stop,{'numeric'},{'scalar','finite','positive'});
end
for field={'output_bounds','state_bounds','controller_state_bounds'}
    name=field{1};
    if ~isfield(value,name) || isempty(value.(name)), continue; end
    mapping=value.(name);
    if isnumeric(mapping) && strcmp(name,'output_bounds'), bounds(mapping); continue; end
    assert(isstruct(mapping),'cfdcSim:InvalidBounds','Bound maps must be JSON objects.');
    names=fieldnames(mapping);
    allowed={outputName};
    if strcmp(name,'controller_state_bounds'), allowed={'reference_filter_state','integral_control'}; end
    assert(all(ismember(names,allowed)),'cfdcSim:UnsupportedContract','Unknown bounded state.');
    for i=1:numel(names), bounds(mapping.(names{i})); end
end
end
function validatePhases(phases,outputName)
if isempty(phases), return; end
assert(isstruct(phases),'cfdcSim:UnsupportedContract','Phases must be objects.');
for i=1:numel(phases)
    p=phases(i);
    require(p,{'phase_id','references','exit_predicate','dwell_s','timeout_s','state_policy'});
    assert(isequal(fieldnames(p.references),{outputName}) && ...
        strcmp(p.exit_predicate.kind,'within_band') && strcmp(p.exit_predicate.signal,outputName) && ...
        ismember(p.state_policy,{'inherit','reset'}),'cfdcSim:UnsupportedContract','Unsupported phase predicate or state policy.');
    validateattributes(p.references.(outputName),{'numeric'},{'scalar','finite'});
    validateattributes(p.exit_predicate.target,{'numeric'},{'scalar','finite'});
    validateattributes(p.exit_predicate.tolerance,{'numeric'},{'scalar','finite','positive'});
    validateattributes(p.dwell_s,{'numeric'},{'scalar','finite','positive'});
    validateattributes(p.timeout_s,{'numeric'},{'scalar','finite','positive'});
    if isfield(p,'hysteresis'), validateattributes(p.hysteresis,{'numeric'},{'scalar','finite','nonnegative'}); end
end
assert(numel(unique({phases.phase_id}))==numel(phases),'cfdcSim:UnsupportedContract','Duplicate phase IDs.');
end
function validateDisturbance(d,inputName,horizon)
if isempty(d), return; end
require(d,{'channel','time_s','duration_s','amplitude'});
assert(strcmp(d.channel,inputName),'cfdcSim:ChannelMismatch','Unknown disturbance input.');
validateattributes(d.time_s,{'numeric'},{'scalar','finite','nonnegative'});
validateattributes(d.duration_s,{'numeric'},{'scalar','finite','positive'});
validateattributes(d.amplitude,{'numeric'},{'scalar','finite'});
assert(d.time_s+d.duration_s<horizon,'cfdcSim:InvalidTimeline','Disturbance must finish inside the trial.');
end
