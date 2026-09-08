classdef Controller < handle
    %CONTROLLER Execute the supported frozen CFDC scalar ControllerIR families.
    properties (SetAccess=private)
        ir
        bounds
        state = struct()
    end
    methods
        function obj = Controller(ir, bounds)
            supported = {'PI','delay_aware_PI','two_dof_PI'};
            assert(isstruct(ir) && isscalar(ir) && isfield(ir,'family') && ...
                ismember(ir.family,supported), 'cfdcSim:UnsupportedController', ...
                'Supported controller families: PI, delay_aware_PI, two_dof_PI.');
            assert(isfield(ir,'ir_version') && strcmp(ir.ir_version,'cfdc-controller-ir/v2.0'), ...
                'cfdcSim:UnsupportedContract','Unsupported ControllerIR version.');
            assert(numel(ir.measured_signals)==1 && numel(ir.control_inputs)==1, ...
                'cfdcSim:UnsupportedController','Only SISO controller interfaces are supported.');
            assert(isnumeric(bounds) && numel(bounds)==2 && all(isfinite(bounds)) && bounds(1)<bounds(2), ...
                'cfdcSim:InvalidBounds','Controller requires finite ordered input bounds.');
            required = {'kp','ki','reference_filter_rate'};
            if strcmp(ir.family,'two_dof_PI'), required{end+1}='feedforward_gain'; end
            assert(isfield(ir,'integral_handling') && ismember(ir.integral_handling, ...
                {'none','anti_windup','clamped','reset_on_phase_entry','back_calculation'}), ...
                'cfdcSim:UnsupportedController','Unsupported integral policy.');
            if strcmp(ir.integral_handling,'back_calculation'), required{end+1}='antiwindup_gain'; end
            assert(isstruct(ir.parameters) && all(isfield(ir.parameters,required)), ...
                'cfdcSim:InvalidController','Required controller parameters are missing.');
            names=fieldnames(ir.parameters);
            assert(isfield(ir,'parameter_domains') && isstruct(ir.parameter_domains) && ...
                all(isfield(ir.parameter_domains,names)),'cfdcSim:InvalidController','Every parameter needs a domain.');
            for i=1:numel(names)
                validateattributes(ir.parameters.(names{i}),{'numeric'},{'scalar','finite','real'});
                domain=ir.parameter_domains.(names{i}); value=ir.parameters.(names{i});
                assert(isnumeric(domain) && numel(domain)==2 && all(isfinite(domain)) && ...
                    domain(1)<domain(2) && value>=domain(1) && value<=domain(2), ...
                    'cfdcSim:InvalidController','Controller parameter lies outside its frozen domain.');
            end
            assert(ir.parameters.reference_filter_rate>0, 'cfdcSim:InvalidController','Filter rate must be positive.');
            if isfield(ir.parameters,'antiwindup_gain')
                assert(ir.parameters.antiwindup_gain>=0,'cfdcSim:InvalidController','Antiwindup gain must be nonnegative.');
            end
            if isfield(ir.parameters,'reference_weight')
                assert(ir.parameters.reference_weight>=0 && ir.parameters.reference_weight<=1, ...
                    'cfdcSim:InvalidController','Reference weight must lie in [0,1].');
            end
            obj.ir=ir; obj.bounds=double(bounds(:).');
        end
        function reset(obj)
            obj.state=struct();
        end
        function sample = preview(obj,y,reference,dt,resetState)
            if nargin<5, resetState=false; end
            validateattributes(y,{'numeric'},{'scalar','real','finite'});
            validateattributes(reference,{'numeric'},{'scalar','real','finite'});
            validateattributes(dt,{'numeric'},{'scalar','real','finite','positive'});
            s=obj.state;
            if resetState, s=struct(); end
            rf=0; integral=0;
            if isfield(s,'reference_filter_state'), rf=s.reference_filter_state; end
            if isfield(s,'integral_control'), integral=s.integral_control; end
            p=obj.ir.parameters;
            rf=rf-expm1(-p.reference_filter_rate*dt)*(reference-rf);
            weight=1;
            if isfield(p,'reference_weight'), weight=p.reference_weight; end
            raw=p.kp*(weight*rf-y)+integral;
            if strcmp(obj.ir.family,'two_dof_PI'), raw=raw+p.feedforward_gain*rf; end
            applied=min(max(raw,obj.bounds(1)),obj.bounds(2));
            delta=p.ki*(rf-y)*dt;
            if strcmp(obj.ir.integral_handling,'back_calculation')
                delta=delta+dt*p.antiwindup_gain*(applied-raw);
            elseif ~strcmp(obj.ir.integral_handling,'none') && (raw-applied)*delta>0
                delta=0;
            end
            s.reference_filter_state=rf; s.integral_control=integral+delta;
            assert(all(isfinite([raw,applied,rf,s.integral_control])), ...
                'cfdcSim:NumericalFailure','Controller produced a nonfinite sample.');
            events={};
            if raw~=applied
                events={struct('kind','saturation','channel',obj.ir.control_inputs{1}, ...
                    'raw_control',raw,'control',applied)};
            end
            sample=struct('raw_control',raw,'control',applied,'state',s,'events',{events});
        end
        function commit(obj,sample)
            obj.state=sample.state;
        end
        function sample=step(obj,y,reference,dt)
            sample=obj.preview(y,reference,dt);
            obj.commit(sample);
        end
    end
end
