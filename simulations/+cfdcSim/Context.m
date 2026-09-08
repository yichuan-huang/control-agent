classdef Context < handle
    %CONTEXT One isolated Simulink trial; no CFDC session or judge access.
    properties (SetAccess=private)
        spec
        plant
        controller
        pending = struct()
        samples = {}
        eventLog = {}
        stop_event
        numericalFailure = false
    end
    properties (Access=private)
        phaseIndex = 1
        phaseEntered = 0
        bandEntered = NaN
        lastTime = -Inf
        disturbanceRecorded = false
    end
    methods
        function obj=Context(spec)
            obj.spec=spec;
            obj.reset();
        end
        function reset(obj)
            obj.plant=cfdcSim.Plant(obj.spec.plant,obj.spec.initial_state);
            obj.controller=[];
            if strcmp(obj.spec.mode,'evaluation')
                obj.controller=cfdcSim.Controller(obj.spec.request.controller,obj.spec.bounds);
            end
            obj.pending=struct(); obj.samples={}; obj.eventLog={};
            obj.phaseIndex=1; obj.phaseEntered=0; obj.bandEntered=NaN;
            obj.lastTime=-Inf; obj.disturbanceRecorded=false; obj.numericalFailure=false;
            obj.stop_event=struct('triggered',false,'time_s',obj.spec.horizon,'reason','horizon_complete');
        end
        function values=preview(obj,y,excitation,t)
            if ~isfinite(y)
                obj.numericalFailure=true; last=max(0,obj.lastTime);
                obj.stop_event=struct('triggered',true,'time_s',last,'reason','numerical_failure');
                values=[0;0;0;0;obj.phaseIndex;1]; return;
            end
            s=obj.spec; events={}; index=obj.phaseIndex;
            entered=obj.phaseEntered; band=obj.bandEntered;
            phaseId='hold'; reference=0; resetState=false;
            stop=struct('triggered',false,'time_s',s.horizon,'reason','horizon_complete');
            if strcmp(s.mode,'evaluation')
                request=s.request; reference=request.references.(s.output_name);
                phases=request.phases;
                if ~isempty(phases)
                    phase=phases(index); phaseId=phase.phase_id;
                    reference=phase.references.(s.output_name);
                    predicate=phase.exit_predicate;
                    distance=abs(y-predicate.target);
                    hysteresis=0;
                    if isfield(phase,'hysteresis'), hysteresis=phase.hysteresis; end
                    if isfinite(band) && distance>predicate.tolerance+hysteresis, band=NaN; end
                    if distance<=predicate.tolerance && isnan(band), band=t; end
                    if isfinite(band) && t-band>=phase.dwell_s-1e-10 && index<numel(phases)
                        before=obj.controller.state; commandBefore=struct();
                        if ~isempty(obj.samples)
                            previous=obj.samples{end};
                            commandBefore.(s.input_name)=previous.control;
                        end
                        oldId=phaseId; index=index+1; phase=phases(index); phaseId=phase.phase_id;
                        resetState=strcmp(phase.state_policy,'reset');
                        stateEntry=before;
                        if resetState, stateEntry=struct(); end
                        reference=phase.references.(s.output_name);
                        entered=t; band=NaN;
                        events{end+1}=struct('kind','handoff','time_s',t, ...
                            'sample_index',numel(obj.samples),'state_policy',phase.state_policy, ...
                            'state_on_entry',stateEntry,'from_phase',oldId,'to_phase',phaseId, ...
                            'state_before',before,'state_after',struct(), ...
                            'command_before',commandBefore,'command_after',struct());
                    elseif t-entered>phase.timeout_s+1e-10
                        stop=struct('triggered',true,'time_s',t,'reason','phase_timeout');
                    end
                end
                sample=obj.controller.preview(y,reference,s.dt,resetState);
                if ~isempty(events) && strcmp(events{end}.kind,'handoff')
                    events{end}.state_after=sample.state;
                    events{end}.command_after.(s.input_name)=sample.control;
                end
                for i=1:numel(sample.events)
                    event=sample.events{i}; event.time_s=t; events{end+1}=event;
                end
                rf=sample.state.reference_filter_state; integral=sample.state.integral_control;
                limits=request;
            else
                sample=struct('raw_control',excitation,'control',excitation,'state',struct(),'events',{{}});
                rf=0; integral=0; limits=s.stop_condition;
            end
            if isfield(limits,'state_stop') && ~isempty(limits.state_stop) && abs(y)>limits.state_stop
                stop=struct('triggered',true,'time_s',t,'reason','state_limit');
            end
            stop=checkBound(limits,'state_bounds',s.output_name,y,'state_limit',t,stop);
            if strcmp(s.mode,'evaluation')
                names={};
                if isfield(limits,'controller_state_bounds'), names=fieldnames(limits.controller_state_bounds); end
                assert(isempty(names) || all(isfield(sample.state,names)),'cfdcSim:MissingState','A declared controller state is absent.');
                for i=1:numel(names)
                    stop=checkBound(limits,'controller_state_bounds',names{i},sample.state.(names{i}), ...
                        'controller_state_limit',t,stop);
                end
            end
            if isfield(limits,'output_bounds') && isnumeric(limits.output_bounds) && ~isempty(limits.output_bounds)
                pair=limits.output_bounds;
                if y<pair(1) || y>pair(2), stop=struct('triggered',true,'time_s',t,'reason','output_limit'); end
            else
                stop=checkBound(limits,'output_bounds',s.output_name,y,'output_limit',t,stop);
            end
            obj.pending=struct('time_s',t,'y',y,'reference',reference,'sample',sample, ...
                'phase_id',phaseId,'phase_index',index,'phase_entered',entered,'band_entered',band, ...
                'events',{events},'stop_event',stop);
            values=[sample.raw_control;reference;rf;integral;index;double(stop.triggered)];
        end
        function commit(obj)
            if obj.numericalFailure, return; end
            if isempty(fieldnames(obj.pending)) || obj.pending.time_s<=obj.lastTime+1e-12, return; end
            p=obj.pending;
            if ~isempty(obj.controller), obj.controller.commit(p.sample); end
            obj.phaseIndex=p.phase_index; obj.phaseEntered=p.phase_entered; obj.bandEntered=p.band_entered;
            row=p.sample; row.time_s=p.time_s; row.phase_id=p.phase_id;
            obj.samples{end+1}=row;
            obj.eventLog=[obj.eventLog,p.events];
            obj.stop_event=p.stop_event; obj.lastTime=p.time_s;
            d=obj.spec.disturbance;
            if ~isempty(d) && ~obj.disturbanceRecorded && ~p.stop_event.triggered && ...
                    p.time_s<obj.spec.horizon-1e-12 && p.time_s<=d.time_s && d.time_s<p.time_s+obj.spec.dt
                event=d; event.kind='disturbance'; event.sample_index=numel(obj.samples)-1;
                obj.eventLog{end+1}=event; obj.disturbanceRecorded=true;
            end
        end
        function advance(obj,u,t)
            if ~obj.numericalFailure && t<obj.spec.horizon-1e-12 && ~obj.pending.stop_event.triggered
                d=obj.spec.disturbance;
                edges=[t,t+obj.spec.dt]; base=u;
                if ~isempty(d)
                    finish=d.time_s+d.duration_s;
                    if t>=d.time_s && t<finish, base=base-d.amplitude; end
                    events=[d.time_s,finish];
                    edges=unique([edges,events(events>t & events<t+obj.spec.dt)]);
                end
                for i=1:numel(edges)-1
                    command=base;
                    if ~isempty(d) && edges(i)>=d.time_s && edges(i)<finish
                        command=command+d.amplitude;
                    end
                    obj.plant.advance(command,edges(i+1)-edges(i));
                end
            end
        end
    end
end

function stop=checkBound(limits,field,name,value,reason,t,stop)
if isfield(limits,field) && isstruct(limits.(field)) && isfield(limits.(field),name)
    pair=limits.(field).(name);
    if value<pair(1) || value>pair(2)
        stop=struct('triggered',true,'time_s',t,'reason',reason);
    end
end
end
