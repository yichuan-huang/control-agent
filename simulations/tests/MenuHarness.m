classdef MenuHarness < handle
    properties
        Actions
        Paths = {}
        Kind = 'identification'
        Errors = {}
        Messages = {}
        Runs = {}
        Selections = 0
        Mutate = ''
    end
    methods
        function self = MenuHarness(actions, paths)
            self.Actions = actions;
            self.Paths = paths;
        end
        function result = services(self)
            result = struct('menu', @(varargin) self.next(), ...
                'select', @(varargin) self.select(), ...
                'setup', @(directory, show) struct('case_dir', directory), ...
                'preflight', @(varargin) self.preflight(), ...
                'identify', @(lab, path) self.run(lab, path), ...
                'evaluate', @(lab, path) self.run(lab, path), ...
                'display', @(message) self.display(message), ...
                'error', @(exception) self.recordError(exception));
        end
        function action = next(self)
            action = self.Actions(1); self.Actions(1) = [];
            if action == 3 && ~isempty(self.Mutate)
                file = fopen(self.Mutate, 'wb');
                cleanup = onCleanup(@() fclose(file));
                fwrite(file, uint8('changed'));
            end
        end
        function path = select(self)
            self.Selections = self.Selections + 1;
            path = self.Paths{1}; self.Paths(1) = [];
        end
        function check = preflight(self)
            check = struct('kind', self.Kind, 'card', struct('session_id', 'test'), ...
                'manifest', struct('stage', 'fresh_confirmation', 'request_id', 'request-2', 'session_id', 'session-1'));
        end
        function result = run(self, lab, path)
            self.Runs{end+1} = struct('lab', lab, 'path', path);
            result = struct('run_dir', fullfile(lab.case_dir, 'runs', 'test'), ...
                'files', {{'first.csv', 'second.csv'}}, ...
                'repeats', {{struct('stop_event', struct('triggered', true))}});
            if strcmp(self.Kind, 'evaluation')
                result.result_zip = 'fresh_confirmation-results.zip';
                result.stage = 'fresh_confirmation';
            end
        end
        function display(self, message)
            self.Messages{end+1} = message;
        end
        function recordError(self, exception)
            self.Errors{end+1} = exception.identifier;
        end
    end
end
