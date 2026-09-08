function write_bytes(path,bytes)
%WRITE_BYTES Install a new artifact without replacing existing evidence.
assert(~isfile(path) && ~isfolder(path),'cfdcSim:ArtifactExists','Refusing to overwrite %s.',path);
[file,message]=fopen(path,'wb');
assert(file>=0,'cfdcSim:WriteFailed','%s',message);
cleanup=onCleanup(@() fclose(file));
count=fwrite(file,uint8(bytes),'uint8');
assert(count==numel(bytes),'cfdcSim:WriteFailed','Incomplete artifact write.');
end
