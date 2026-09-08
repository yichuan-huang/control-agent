function write_json(path,value)
%WRITE_JSON Write a new UTF-8 JSON artifact; scientific arrays remain explicit.
cfdcSim.write_bytes(path,unicode2native([jsonencode(value,PrettyPrint=true),newline],'UTF-8'));
end
