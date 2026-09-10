function path=choose_package(lab,path)
%CHOOSE_PACKAGE Select the current downloaded experiment ZIP.
if nargin<2 || isempty(path)
    path=cfdcSim.select_package(lab);
    assert(~isempty(path),'cfdcSim:SelectionCancelled','Package selection cancelled.');
end
path=char(path);
end
