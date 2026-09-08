function modelPath = build_model()
caseDir = fileparts(mfilename('fullpath'));
addpath(fileparts(caseDir));
modelPath = cfdcSim.build_model(caseDir);
end
