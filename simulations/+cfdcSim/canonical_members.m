function [members,encoded]=canonical_members(bytes)
%CANONICAL_MEMBERS Sort downloaded JSON keys without losing 1 versus 1.0.
% CFDC uses Python's JSON number tokens in both pretty and canonical exports.
% Retaining those tokens avoids MATLAB's otherwise lossy float/int conversion.
source=native2unicode(uint8(bytes),'UTF-8'); pos=1;
[encoded,members]=value(0); whitespace();
assert(pos>numel(source) && isa(members,'containers.Map'), ...
    'cfdcSim:InvalidPackage','Expected one JSON object.');
    function whitespace()
        while pos<=numel(source) && ismember(source(pos),sprintf(' \t\r\n')), pos=pos+1; end
    end
    function [out,map]=value(depth)
        assert(depth<64,'cfdcSim:InvalidPackage','JSON nesting exceeds supported depth.');
        whitespace(); map=[];
        assert(pos<=numel(source),'cfdcSim:InvalidPackage','Truncated JSON.');
        if source(pos)=='{'
            pos=pos+1; whitespace(); map=containers.Map('KeyType','char','ValueType','char');
            while source(pos)~='}'
                key=jsondecode(stringToken()); whitespace();
                assert(source(pos)==':' && ~isKey(map,key),'cfdcSim:InvalidPackage','Invalid or duplicate JSON key.');
                pos=pos+1; map(key)=value(depth+1); whitespace();
                if source(pos)=='}', break; end
                assert(source(pos)==',','cfdcSim:InvalidPackage','Expected JSON comma.');
                pos=pos+1; whitespace();
            end
            pos=pos+1; out=cfdcSim.encode_members(map);
        elseif source(pos)=='['
            pos=pos+1; whitespace(); parts={};
            while source(pos)~=']'
                parts{end+1}=value(depth+1); %#ok<AGROW> Bounded JSON array.
                whitespace(); if source(pos)==']', break; end
                assert(source(pos)==',','cfdcSim:InvalidPackage','Expected JSON comma.');
                pos=pos+1; whitespace();
            end
            pos=pos+1; out=['[',strjoin(parts,','),']'];
        elseif source(pos)=='"'
            out=jsonencode(jsondecode(stringToken()));
        else
            token=regexp(source(pos:end),'^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)','match','once');
            assert(~isempty(token),'cfdcSim:InvalidPackage','Invalid JSON scalar.');
            pos=pos+numel(token); out=token;
        end
    end
    function token=stringToken()
        whitespace(); first=pos;
        assert(source(pos)=='"','cfdcSim:InvalidPackage','Expected JSON string.');
        pos=pos+1;
        while pos<=numel(source)
            if source(pos)=='"', pos=pos+1; token=source(first:pos-1); return; end
            if source(pos)=='\', pos=pos+1; end
            pos=pos+1;
        end
        error('cfdcSim:InvalidPackage','Truncated JSON string.');
    end
end
