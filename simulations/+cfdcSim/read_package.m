function package=read_package(path)
%READ_PACKAGE Read bounded ZIP members without extracting untrusted paths.
assert(isfile(path),'cfdcSim:PackageMissing','Experiment ZIP does not exist.');
file=java.util.zip.ZipFile(java.io.File(char(path)));
cleanup=onCleanup(@() file.close());
iterator=file.entries(); names={}; entries={}; total=0;
while iterator.hasMoreElements()
    entry=iterator.nextElement(); name=char(entry.getName());
    assert(~startsWith(name,'/') && ~contains(name,'\') && ~contains(name,':') && ...
        ~any(ismember(strsplit(name,'/'),{'.','..'})), 'cfdcSim:InvalidArchive','Unsafe archive member path.');
    assert(~ismember(name,names),'cfdcSim:InvalidArchive','Duplicate archive member.');
    total=total+double(entry.getSize());
    assert(entry.getSize()>=0 && total<=100000000 && numel(names)<10002, ...
        'cfdcSim:InvalidArchive','Archive exceeds supported size or member count.');
    names{end+1}=name; entries{end+1}=entry;
end
members=containers.Map('KeyType','char','ValueType','any');
for i=1:numel(entries)
    if entries{i}.isDirectory(), continue; end
    stream=file.getInputStream(entries{i});
    streamCleanup=onCleanup(@() stream.close());
    buffer=java.nio.ByteBuffer.allocate(int32(entries{i}.getSize()));
    channel=java.nio.channels.Channels.newChannel(stream);
    while buffer.hasRemaining()
        assert(channel.read(buffer)>=0,'cfdcSim:InvalidArchive','Truncated ZIP member.');
    end
    bytes=typecast(int8(buffer.array()),'uint8');
    assert(numel(bytes)==entries{i}.getSize(),'cfdcSim:InvalidArchive','Incomplete ZIP member.');
    members(names{i})=bytes(:).';
    clear streamCleanup
end
package=struct('path',char(java.io.File(char(path)).getCanonicalPath()),'members',members);
end
