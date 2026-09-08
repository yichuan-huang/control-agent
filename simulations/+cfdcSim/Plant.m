classdef Plant < handle
    %PLANT Strictly proper state-space realization with exact ZOH and delay.
    properties (SetAccess=private)
        A
        B
        C
        state
        delay
        time = 0
    end
    properties (Access=private)
        historyTime = []
        historyInput = []
        cache
    end
    methods
        function obj=Plant(config,initialState)
            denominator=double(config.denominator(:).');
            numerator=double(config.numerator(:).');
            assert(numel(numerator)==1 && numel(denominator)>=2 && ...
                numel(denominator)<=3 && all(isfinite([denominator,numerator])) && denominator(1)~=0, ...
                'cfdcSim:InvalidPlant','Only the configured scalar first/second-order plants are supported.');
            n=numel(denominator)-1;
            obj.A=[-denominator(2:end)/denominator(1); eye(n-1),zeros(n-1,1)];
            obj.B=[1;zeros(n-1,1)];
            obj.C=[zeros(1,n-1),numerator/denominator(1)];
            validateattributes(initialState,{'numeric'},{'vector','numel',n,'finite','real'});
            validateattributes(config.input_delay_s,{'numeric'},{'scalar','finite','nonnegative'});
            obj.state=double(initialState(:)); obj.delay=double(config.input_delay_s);
            obj.cache=containers.Map('KeyType','char','ValueType','any');
        end
        function y=measure(obj)
            y=obj.C*obj.state;
        end
        function advance(obj,u,dt)
            validateattributes(u,{'numeric'},{'scalar','real','finite'});
            validateattributes(dt,{'numeric'},{'scalar','real','finite','positive'});
            obj.historyTime(end+1)=obj.time;
            obj.historyInput(end+1)=u;
            finish=obj.time+dt;
            arrivals=obj.historyTime+obj.delay;
            boundaries=unique([obj.time,arrivals(arrivals>obj.time+1e-12 & arrivals<finish-1e-12),finish]);
            for i=1:numel(boundaries)-1
                left=boundaries(i); right=boundaries(i+1);
                index=find(obj.historyTime<=left-obj.delay+1e-12,1,'last');
                applied=0;
                if ~isempty(index), applied=obj.historyInput(index); end
                duration=right-left;
                key=sprintf('%.13f',duration);
                if ~isKey(obj.cache,key)
                    n=size(obj.A,1);
                    matrix=expm([obj.A,obj.B;zeros(1,n+1)]*duration);
                    obj.cache(key)={matrix(1:n,1:n),matrix(1:n,n+1)};
                end
                matrices=obj.cache(key);
                obj.state=matrices{1}*obj.state+matrices{2}*applied;
            end
            obj.time=finish;
            threshold=finish-obj.delay-dt;
            while numel(obj.historyTime)>2 && obj.historyTime(2)<threshold
                obj.historyTime(1)=[]; obj.historyInput(1)=[];
            end
        end
    end
end
