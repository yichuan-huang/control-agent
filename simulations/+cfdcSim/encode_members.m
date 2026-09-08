function encoded=encode_members(members)
%ENCODE_MEMBERS Encode a map whose values are already canonical JSON tokens.
names=sort(keys(members)); parts=cell(size(names));
for i=1:numel(names), parts{i}=[jsonencode(names{i}),':',members(names{i})]; end
encoded=['{',strjoin(parts,','),'}'];
end
