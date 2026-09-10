classdef ModelSafetyTest < matlab.unittest.TestCase
    properties
        Lab
    end
    methods (TestMethodSetup)
        function createIndependentModel(test)
            root = fileparts(fileparts(mfilename('fullpath')));
            test.applyFixture(matlab.unittest.fixtures.PathFixture(root));
            temporary = test.applyFixture(matlab.unittest.fixtures.TemporaryFolderFixture);
            config = jsondecode(fileread(fullfile(root, '01_optical_hold', 'case_config.json')));
            config.model_name = ['cfdc_safety_', strrep(char(java.util.UUID.randomUUID()), '-', '_')];
            cfdcSim.write_json(fullfile(temporary.Folder, 'case_config.json'), config);
            test.addTeardown(@() ModelSafetyTest.closeOwnedModel(config.model_name));
            test.Lab = cfdcSim.setup(temporary.Folder, false);
        end
    end
    methods (Test)
        function runningModelIsRejectedWithoutStopping(test)
            set_param(test.Lab.model_name, 'StopTime', 'inf', 'SimulationCommand', 'start');
            ModelSafetyTest.waitForStatus(test.Lab.model_name, 'running');
            test.verifyError(@() cfdcSim.setup(test.Lab.case_dir, false), 'cfdcSim:ModelBusy');
            test.verifyEqual(get_param(test.Lab.model_name, 'SimulationStatus'), 'running');
        end
        function pausedModelIsRejectedWithoutStopping(test)
            set_param(test.Lab.model_name, 'StopTime', 'inf', 'SimulationCommand', 'start');
            ModelSafetyTest.waitForStatus(test.Lab.model_name, 'running');
            set_param(test.Lab.model_name, 'SimulationCommand', 'pause');
            ModelSafetyTest.waitForStatus(test.Lab.model_name, 'paused');
            test.verifyError(@() cfdcSim.setup(test.Lab.case_dir, false), 'cfdcSim:ModelBusy');
            test.verifyEqual(get_param(test.Lab.model_name, 'SimulationStatus'), 'paused');
        end
        function setupPreservesUnsavedUserEditAndDiskModel(test)
            before = ModelSafetyTest.fileHash(test.Lab.model_path);
            set_param(test.Lab.model_name, 'Description', 'Unsaved test-owned user edit');
            cfdcSim.setup(test.Lab.case_dir, false);
            test.verifyEqual(get_param(test.Lab.model_name, 'Dirty'), 'on');
            test.verifyEqual(get_param(test.Lab.model_name, 'Description'), 'Unsaved test-owned user edit');
            test.verifyEqual(ModelSafetyTest.fileHash(test.Lab.model_path), before);
        end
        function newRunRejectsDirtyModelWithoutSaving(test)
            before = ModelSafetyTest.fileHash(test.Lab.model_path);
            set_param(test.Lab.model_name, 'Description', 'Unsaved test-owned user edit');
            packagePath = fullfile(test.Lab.case_dir, 'request.zip');
            cfdcSim.write_bytes(packagePath, uint8('No package parsing occurs before the dirty-model guard.'));
            check = struct('package', struct('path', packagePath), 'kind', 'identification');
            test.verifyError(@() cfdcSim.new_run(test.Lab, check), 'cfdcSim:UnsavedModel');
            test.verifyEqual(get_param(test.Lab.model_name, 'Dirty'), 'on');
            test.verifyEqual(get_param(test.Lab.model_name, 'Description'), 'Unsaved test-owned user edit');
            test.verifyEqual(ModelSafetyTest.fileHash(test.Lab.model_path), before);
        end
    end
    methods (Static, Access = private)
        function waitForStatus(name, expected)
            started = tic;
            while ~strcmp(get_param(name, 'SimulationStatus'), expected) && toc(started) < 15
                pause(0.05);
            end
            assert(strcmp(get_param(name, 'SimulationStatus'), expected), ...
                'test:SimulationStatus', 'Test-owned model did not enter the requested status.');
        end
        function digest = fileHash(path)
            file = fopen(path, 'rb');
            cleanup = onCleanup(@() fclose(file));
            digest = cfdcSim.sha256(fread(file, Inf, '*uint8'));
        end
        function closeOwnedModel(name)
            if ~bdIsLoaded(name), return; end
            if ~strcmp(get_param(name, 'SimulationStatus'), 'stopped')
                set_param(name, 'SimulationCommand', 'stop');
                ModelSafetyTest.waitForStatus(name, 'stopped');
            end
            workspace = get_param(name, 'ModelWorkspace');
            workspace.clear();
            close_system(name, 0);
        end
    end
end
