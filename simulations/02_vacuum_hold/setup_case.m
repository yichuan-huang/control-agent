function lab = setup_case()
caseDir = fileparts(mfilename('fullpath'));
addpath(fileparts(caseDir));
lab = cfdcSim.setup(caseDir, true);
end
