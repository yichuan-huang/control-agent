function run_http_jobs(folder)
%RUN_HTTP_JOBS Execute actual downloaded HTTP test packets, one unique run each.
root=fileparts(fileparts(mfilename('fullpath'))); addpath(root);
jobs=jsondecode(fileread(fullfile(folder,'jobs.json')));
for i=1:numel(jobs)
    job=jobs(i);
    if isfile(job.response_path), continue; end % A completed test invocation is not replayed.
    lab=cfdcSim.setup(job.case_dir,false);
    if strcmp(job.kind,'identification')
        result=cfdcSim.run_identification(lab,job.package_path);
    else
        result=cfdcSim.run_evaluation(lab,job.package_path);
    end
    cfdcSim.write_json(job.response_path,result);
end
end
