% 在 MATLAB 编辑器打开本文件，点击 Run 启动本案例菜单。
launchThisCase();

function launchThisCase()
caseDir = fileparts(mfilename('fullpath'));
addpath(fileparts(caseDir));
cfdcSim.launch_case(caseDir);
end
