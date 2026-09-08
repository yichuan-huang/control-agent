classdef ControllerTest < matlab.unittest.TestCase
    methods (TestClassSetup)
        function sourcePath(testCase)
            testCase.applyFixture(matlab.unittest.fixtures.PathFixture( ...
                fileparts(fileparts(mfilename('fullpath')))));
        end
    end
    methods (Test)
        function outputUsesPreviousIntegral(testCase)
            ir = ControllerTest.ir();
            runtime = cfdcSim.Controller(ir, [-1, 1]);
            sample = runtime.step(0, 0.5, 0.02);
            rf = 0.5 * (-expm1(-0.02));
            testCase.verifyEqual(sample.raw_control, 2 * rf, AbsTol=1e-14);
            testCase.verifyEqual(sample.state.integral_control, rf * 0.02, AbsTol=1e-14);
        end
        function negativeGainStopsWindup(testCase)
            ir = ControllerTest.ir();
            ir.parameters.kp = -10;
            ir.parameters.ki = -2;
            runtime = cfdcSim.Controller(ir, [-1, 1]);
            sample = runtime.step(-2, -0.5, 0.02);
            testCase.verifyEqual(sample.control, -1, AbsTol=1e-14);
            testCase.verifyEqual(sample.state.integral_control, 0, AbsTol=1e-14);
            testCase.verifyEqual(sample.events{1}.kind, 'saturation');
        end
        function resetRestoresInitialResponse(testCase)
            runtime = cfdcSim.Controller(ControllerTest.ir(), [-1, 1]);
            first = runtime.step(0.1, 0.5, 0.02);
            runtime.step(0.2, 0.5, 0.02);
            runtime.reset();
            again = runtime.step(0.1, 0.5, 0.02);
            testCase.verifyEqual(again, first);
        end
        function unsupportedFamilyFails(testCase)
            ir = ControllerTest.ir(); ir.family = 'two_dof_pid';
            testCase.verifyError(@() cfdcSim.Controller(ir, [-1,1]), 'cfdcSim:UnsupportedController');
        end
        function twoDegreeFeedforward(testCase)
            ir = ControllerTest.ir(); ir.family = 'two_dof_PI';
            ir.parameters.feedforward_gain = -0.6; ir.parameter_domains.feedforward_gain=[-20,20];
            runtime = cfdcSim.Controller(ir, [-1,1]);
            sample = runtime.step(0, -0.5, 0.02);
            testCase.verifyEqual(sample.raw_control, 1.4 * (-0.5) * (-expm1(-0.02)), AbsTol=1e-14);
        end
    end
    methods (Static)
        function ir = ir()
            ir = struct('ir_version','cfdc-controller-ir/v2.0', 'family','PI', ...
                'measured_signals',{{'y'}}, 'control_inputs',{{'u'}}, ...
                'parameters',struct('kp',2,'ki',1,'reference_filter_rate',1), ...
                'integral_handling','anti_windup', ...
                'parameter_domains',struct('kp',[-20,20],'ki',[-20,20],'reference_filter_rate',[0.01,20]));
        end
    end
end
