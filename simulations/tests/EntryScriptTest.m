classdef EntryScriptTest < matlab.unittest.TestCase
    properties (TestParameter)
        CaseName = struct('opticalHold', '01_optical_hold', ...
            'vacuumHold', '02_vacuum_hold', 'inkHold', '03_ink_viscosity_hold', ...
            'opticalTransition', '04_optical_transition', ...
            'inkRecovery', '05_ink_disturbance_recovery')
    end
    methods (Test)
        function executesActualEntryFromDifferentFolder(test, CaseName)
            sourceRoot = fileparts(fileparts(mfilename('fullpath')));
            temporary = test.applyFixture(matlab.unittest.fixtures.TemporaryFolderFixture);
            copiedRoot = fullfile(temporary.Folder, '仿真 入口');
            caseDir = fullfile(copiedRoot, CaseName);
            mkdir(caseDir);
            mkdir(fullfile(copiedRoot, '+cfdcSim'));
            copyfile(fullfile(sourceRoot, CaseName, 'run_case.m'), fullfile(caseDir, 'run_case.m'));
            EntryScriptTest.writeStub(fullfile(copiedRoot, '+cfdcSim', 'launch_case.m'));
            test.applyFixture(matlab.unittest.fixtures.PathFixture(copiedRoot));
            test.applyFixture(matlab.unittest.fixtures.PathFixture(caseDir));
            test.applyFixture(matlab.unittest.fixtures.WorkingFolderFixture);
            unrelatedFolder = pwd;
            clear('cfdcSim.launch_case');
            test.addTeardown(@() clear('cfdcSim.launch_case'));
            test.verifyEqual(which('run_case'), fullfile(caseDir, 'run_case.m'));
            eval('run_case');
            recorded = load(fullfile(caseDir, 'entry-location.mat'), 'receivedCaseDir');
            test.verifyEqual(recorded.receivedCaseDir, caseDir);
            test.verifyEqual(pwd, unrelatedFolder);
            test.verifyNotEqual(recorded.receivedCaseDir, unrelatedFolder);
        end
    end
    methods (Static, Access = private)
        function writeStub(path)
            file = fopen(path, 'w');
            cleanup = onCleanup(@() fclose(file));
            fprintf(file, '%s\n', ...
                'function launch_case(caseDir)', ...
                'receivedCaseDir = caseDir;', ...
                'save(fullfile(caseDir, ''entry-location.mat''), ''receivedCaseDir'');', ...
                'end');
        end
    end
end
