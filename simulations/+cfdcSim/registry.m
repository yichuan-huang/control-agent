function value=registry(action,key,value)
%REGISTRY Isolate callback state by an unguessable per-simulation key.
persistent contexts
if isempty(contexts), contexts=containers.Map('KeyType','char','ValueType','any'); end
switch action
    case 'put'
        assert(~isKey(contexts,key),'cfdcSim:ContextConflict','Simulation context already exists.');
        contexts(key)=value;
    case 'get'
        assert(isKey(contexts,key),'cfdcSim:ContextMissing','Run setup_case before starting this model.');
        value=contexts(key);
    case 'remove'
        if isKey(contexts,key), remove(contexts,key); end
        value=[];
    otherwise
        error('cfdcSim:InvalidAction','Unknown simulation registry action.');
end
end
