classdef FailureTest < matlab.unittest.TestCase
    methods (TestClassSetup)
        function sourcePath(testCase)
            testCase.applyFixture(matlab.unittest.fixtures.PathFixture(fileparts(fileparts(mfilename('fullpath')))));
        end
    end
    methods (Test)
        function finitePrefixStopsOnNonfiniteMeasurement(testCase)
            plant=struct('numerator',1,'denominator',[1,1],'input_delay_s',0);
            spec=struct('mode','identification','plant',plant,'initial_state',0,'dt',0.02, ...
                'horizon',1,'times',(0:0.02:1)','bounds',[-1,1],'disturbance',[], ...
                'stop_condition',struct(),'input_name','u','output_name','y');
            ctx=cfdcSim.Context(spec);
            ctx.preview(0,0.2,0); ctx.commit(); ctx.preview(0.01,0.2,0.02); ctx.commit();
            signal=ctx.preview(NaN,0.2,0.04); ctx.commit();
            testCase.verifyEqual(signal(end),1);
            testCase.verifyEqual(numel(ctx.samples),2);
            testCase.verifyEqual(ctx.stop_event,struct('triggered',true,'time_s',0.02,'reason','numerical_failure'));
        end
        function missingDomainFailsClosed(testCase)
            ir=ControllerTest.ir(); ir.parameter_domains=rmfield(ir.parameter_domains,'kp');
            testCase.verifyError(@() cfdcSim.Controller(ir,[-1,1]),'cfdcSim:InvalidController');
        end
        function simulinkRetainsFinitePrefix(testCase)
            root=fileparts(fileparts(mfilename('fullpath')));
            lab=cfdcSim.setup(fullfile(root,'01_optical_hold'),false);
            % Deliberately unstable test apparatus; the five case definitions stay fixed.
            plant=struct('numerator',1,'denominator',[1,-1000],'input_delay_s',0);
            spec=struct('mode','identification','plant',plant,'initial_state',1,'dt',0.02, ...
                'horizon',1,'times',(0:0.02:1)','bounds',[-1,1],'disturbance',[], ...
                'stop_condition',struct(),'input_name','u','output_name','y', ...
                'excitation',zeros(51,1));
            trial=cfdcSim.run_simulation(lab,spec,'','numerical_failure');
            time=cell2mat(trial.trajectory.time_s);
            testCase.verifyTrue(all(isfinite(cell2mat(trial.trajectory.outputs.y))));
            testCase.verifyGreaterThan(numel(time),2);
            testCase.verifyLessThan(time(end),1);
            testCase.verifyEqual(trial.stop_event, ...
                struct('triggered',true,'time_s',time(end),'reason','numerical_failure'));
        end
        function outOfDomainFailsClosed(testCase)
            ir=ControllerTest.ir(); ir.parameters.kp=25;
            testCase.verifyError(@() cfdcSim.Controller(ir,[-1,1]),'cfdcSim:InvalidController');
        end
    end
end
