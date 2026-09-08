classdef PlantTest < matlab.unittest.TestCase
    methods (TestClassSetup)
        function sourcePath(testCase)
            testCase.applyFixture(matlab.unittest.fixtures.PathFixture( ...
                fileparts(fileparts(mfilename('fullpath')))));
        end
    end
    methods (Test)
        function exactOpticalResponse(testCase)
            plant = cfdcSim.Plant(PlantTest.config('optical'), 0);
            plant.advance(0.5, 1.1);
            testCase.verifyEqual(plant.measure(), 0.8 * (1-exp(-1)), AbsTol=1e-13);
        end
        function delaySplitsSampleExactly(testCase)
            plant = cfdcSim.Plant(PlantTest.config('vacuum'), 0);
            plant.advance(0.5, 0.3);
            testCase.verifyEqual(plant.measure(), 0, AbsTol=1e-14);
            plant.advance(0.5, 0.3);
            testCase.verifyEqual(plant.measure(), -0.7 * (1-exp(-0.2/1.3)), AbsTol=1e-13);
        end
        function secondOrderStep(testCase)
            plant = cfdcSim.Plant(PlantTest.config('ink'), [0;0]);
            plant.advance(0.5, 3);
            expected = -0.9 * (1 - 1.5*exp(-2) + 0.5*exp(-6));
            testCase.verifyEqual(plant.measure(), expected, AbsTol=1e-13);
        end
    end
    methods (Static)
        function cfg = config(kind)
            definitions = struct('optical',{{1.6,[1.1,1],0}}, ...
                'vacuum',{{-1.4,[1.3,1],0.4}},'ink',{{-1.8,[0.75,2,1],0}});
            row = definitions.(kind);
            cfg = struct('kind',kind,'numerator',row{1},'denominator',row{2}, ...
                'input_delay_s',row{3},'initial_perturbation',1e-6);
        end
    end
end
