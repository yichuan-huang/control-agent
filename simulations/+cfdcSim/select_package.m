function path = select_package(lab, title)
%SELECT_PACKAGE Select one ZIP with the native file browser; cancel is harmless.
if nargin < 2, title = '选择本轮从 CFDC 下载的实验包'; end
[file, folder] = uigetfile('*.zip', title, fullfile(lab.case_dir, 'incoming', filesep));
if isequal(file, 0)
    path = '';
else
    path = fullfile(folder, file);
end
end
