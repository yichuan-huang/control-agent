classdef launch_caseTest < matlab.unittest.TestCase
    properties
        Root
        CaseDir
        Package
        Temporary
    end
    properties (TestParameter)
        CaseName = struct('opticalHold', '01_optical_hold', ...
            'vacuumHold', '02_vacuum_hold', 'inkHold', '03_ink_viscosity_hold', ...
            'opticalTransition', '04_optical_transition', ...
            'inkRecovery', '05_ink_disturbance_recovery')
    end
    methods (TestMethodSetup)
        function prepare(test)
            test.Root = fileparts(fileparts(mfilename('fullpath')));
            test.applyFixture(matlab.unittest.fixtures.PathFixture(test.Root));
            test.applyFixture(matlab.unittest.fixtures.PathFixture(fullfile(test.Root, 'tests')));
            temporary = test.applyFixture(matlab.unittest.fixtures.TemporaryFolderFixture);
            test.Temporary = temporary.Folder;
            test.Package = fullfile(temporary.Folder, '采集 包.zip');
            cfdcSim.write_bytes(test.Package, uint8('original'));
            test.CaseDir = fullfile(test.Root, '01_optical_hold');
        end
    end
    methods (Test)
        function everyCaseUsesItsOwnLocation(test, CaseName)
            ui = MenuHarness([1 6], {});
            directory = fullfile(test.Root, CaseName);
            state = cfdcSim.launch_case(directory, ui.services());
            test.verifyEqual(state.lab.case_dir, directory);
            test.verifyTrue(isfile(fullfile(directory, 'run_case.m')));
        end
        function caseLocationSupportsSpacesAndChinese(test)
            directory = fullfile(test.Temporary, '仿真 案例');
            mkdir(directory);
            copyfile(fullfile(test.CaseDir, 'case_config.json'), directory);
            ui = MenuHarness([1 6], {});
            state = cfdcSim.launch_case(directory, ui.services());
            test.verifyEqual(state.lab.case_dir, directory);
            test.verifyEmpty(ui.Errors);
        end
        function cancellationIsHarmless(test)
            ui = MenuHarness([1 2 4 6], {'', ''});
            state = cfdcSim.launch_case(test.CaseDir, ui.services());
            test.verifyEmpty(ui.Errors);
            test.verifyEmpty(ui.Runs);
            test.verifyEmpty(state.acquisition);
        end
        function requiresInitializationAndPreflight(test)
            ui = MenuHarness([2 1 3 6], {});
            cfdcSim.launch_case(test.CaseDir, ui.services());
            test.verifyEqual(ui.Errors, {'cfdcSim:SetupRequired', 'cfdcSim:PreflightRequired'});
            test.verifyEmpty(ui.Runs);
        end
        function wrongPackageCannotAuthorizeAcquisition(test)
            ui = MenuHarness([1 2 3 6], {test.Package});
            ui.Kind = 'evaluation';
            cfdcSim.launch_case(test.CaseDir, ui.services());
            test.verifyEqual(ui.Errors, {'cfdcSim:WrongPackage', 'cfdcSim:PreflightRequired'});
            test.verifyEmpty(ui.Runs);
        end
        function changedPackageClearsPreflight(test)
            ui = MenuHarness([1 2 3 3 6], {test.Package});
            ui.Mutate = test.Package;
            cfdcSim.launch_case(test.CaseDir, ui.services());
            test.verifyEqual(ui.Errors, {'cfdcSim:PackageChanged', 'cfdcSim:PreflightRequired'});
            test.verifyEmpty(ui.Runs);
        end
        function reinitializationClearsPreflight(test)
            ui = MenuHarness([1 2 1 3 6], {test.Package});
            cfdcSim.launch_case(test.CaseDir, ui.services());
            test.verifyEqual(ui.Errors, {'cfdcSim:PreflightRequired'});
        end
        function arbitraryWorkingFolderAndUnicodePath(test)
            test.applyFixture(matlab.unittest.fixtures.WorkingFolderFixture);
            ui = MenuHarness([1 2 3 5 6], {test.Package});
            state = cfdcSim.launch_case(test.CaseDir, ui.services());
            test.verifyEmpty(ui.Errors);
            test.verifyEqual(ui.Runs{1}.path, test.Package);
            test.verifyEqual(state.case_dir, test.CaseDir);
            test.verifyTrue(contains(strjoin(ui.Messages), 'CSV 共 2 份'));
            test.verifyTrue(contains(strjoin(ui.Messages), '是否有重复触发停止：1'));
        end
        function eachEvaluationSelectsFreshPackageAndDisplaysRequest(test)
            ui = MenuHarness([1 4 4 5 6], {test.Package, test.Package});
            ui.Kind = 'evaluation';
            cfdcSim.launch_case(test.CaseDir, ui.services());
            test.verifyEmpty(ui.Errors);
            test.verifyEqual(ui.Selections, 2);
            test.verifyNumElements(ui.Runs, 2);
            test.verifyTrue(contains(strjoin(ui.Messages), 'request-2'));
            test.verifyTrue(contains(strjoin(ui.Messages), 'fresh_confirmation-results.zip'));
        end
        function switchingCaseDoesNotCarryState(test)
            first = MenuHarness([1 2 6], {test.Package});
            cfdcSim.launch_case(test.CaseDir, first.services());
            second = MenuHarness([1 3 5 6], {});
            state = cfdcSim.launch_case(fullfile(test.Root, '02_vacuum_hold'), second.services());
            test.verifyEqual(second.Errors, {'cfdcSim:PreflightRequired'});
            test.verifyEmpty(state.last_result);
            test.verifyTrue(contains(strjoin(second.Messages), '尚无完成结果'));
        end
    end
end
