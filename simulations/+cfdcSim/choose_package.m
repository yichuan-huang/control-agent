function path=choose_package(lab,path)
%CHOOSE_PACKAGE Select the current downloaded experiment ZIP.
if nargin<2 || isempty(path)
    [file,directory]=uigetfile('*.zip','选择本轮从 CFDC 下载的实验包', ...
        fullfile(lab.case_dir,'incoming',filesep));
    assert(~isequal(file,0),'cfdcSim:SelectionCancelled','Package selection cancelled.');
    path=fullfile(directory,file);
end
path=char(path);
end
