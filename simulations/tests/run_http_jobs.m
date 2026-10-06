function run_http_jobs(folder)
%RUN_HTTP_JOBS Execute actual downloaded HTTP test packets, one unique run each.
exchangeFile=fullfile(folder,'jobs-exchange.json');
if isfile(exchangeFile)
    exchangeRoot=fileparts(folder);
    root=fullfile(exchangeRoot,'simulations');
    jobs=jsondecode(fileread(exchangeFile));
else
    exchangeRoot='';
    root=fileparts(fileparts(mfilename('fullpath')));
    jobs=jsondecode(fileread(fullfile(folder,'jobs.json')));
end
addpath(root);
for i=1:numel(jobs)
    job=jobs(i);
    if ~isempty(exchangeRoot)
        job.case_dir=fullfile(exchangeRoot,job.case_dir);
        job.package_path=fullfile(exchangeRoot,job.package_path);
        job.response_path=fullfile(exchangeRoot,job.response_path);
    end
    if isfile(job.response_path), continue; end % A completed test invocation is not replayed.
    lab=cfdcSim.setup(job.case_dir,false);
    if strcmp(job.kind,'identification')
        result=cfdcSim.run_identification(lab,job.package_path);
    else
        result=cfdcSim.run_evaluation(lab,job.package_path);
    end
    if ~isempty(exchangeRoot)
        result.run_dir=exchange_relative(result.run_dir,exchangeRoot);
        if isfield(result,'files')
            for j=1:numel(result.files)
                result.files{j}=exchange_relative(result.files{j},exchangeRoot);
            end
        end
        if isfield(result,'result_zip')
            result.result_zip=exchange_relative(result.result_zip,exchangeRoot);
        end
    end
    cfdcSim.write_json(job.response_path,result);
end
end

function path=exchange_relative(path,root)
prefix=[root,filesep];
assert(startsWith(path,prefix),'cfdcSim:ExchangePath','Result escaped the exchange root.');
path=char(extractAfter(string(path),strlength(string(prefix))));
% Exchange metadata is consumed by Linux containers as well as native MATLAB.
path=strrep(path,filesep,'/');
end
