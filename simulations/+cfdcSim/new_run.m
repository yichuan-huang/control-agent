function runDir=new_run(lab,check)
%NEW_RUN Capture the immutable inputs of one external simulation invocation.
token=char(java.util.UUID.randomUUID());
runDir=fullfile(lab.case_dir,'runs',[char(datetime('now',Format='yyyyMMdd_HHmmss')), '_',token]);
assert(~isfolder(runDir),'cfdcSim:ArtifactExists','Run directory already exists.');
mkdir(runDir);
copyfile(check.package.path,fullfile(runDir,'source-package.zip'));
copyfile(fullfile(lab.case_dir,'case_config.json'),fullfile(runDir,'case_config.json'));
assert(strcmp(get_param(lab.model_name,'Dirty'),'off'),'cfdcSim:UnsavedModel', ...
    'Save the model before recording an experiment.');
copyfile(lab.model_path,fullfile(runDir,'model.slx'));
sourceRoot=fileparts(fileparts(mfilename('fullpath')));
sourceDir=fullfile(runDir,'source'); mkdir(sourceDir);
copyfile(fullfile(sourceRoot,'+cfdcSim'),fullfile(sourceDir,'+cfdcSim'));
copyfile(fullfile(sourceRoot,'cfdc_controller_block.m'),sourceDir);
copyfile(fullfile(sourceRoot,'cfdc_plant_block.m'),sourceDir);
fid=fopen(check.package.path,'rb'); cleaner=onCleanup(@() fclose(fid));
sourceBytes=fread(fid,Inf,'*uint8');
record=struct('format_version','cfdc-simulink-run/v1','source_kind','software', ...
    'case_id',lab.config.case_id,'model_name',lab.model_name,'model_version','1.0.0', ...
    'matlab_version',version,'source_package_sha256',cfdcSim.sha256(sourceBytes), ...
    'kind',check.kind,'created_at',char(datetime('now',TimeZone='UTC',Format="yyyy-MM-dd'T'HH:mm:ssXXX")));
cfdcSim.write_json(fullfile(runDir,'run-input.json'),record);
end
