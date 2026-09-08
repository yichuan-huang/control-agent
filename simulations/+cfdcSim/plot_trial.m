function plot_trial(trial,path)
%PLOT_TRIAL Plot recorded evidence without making a performance decision.
t=cell2mat(trial.trajectory.time_s);
names=fieldnames(trial.trajectory.outputs); outputName=names{1};
names=fieldnames(trial.trajectory.control_inputs); inputName=names{1};
f=figure('Visible','off','Color','white','Position',[100 100 1000 620]);
cleanup=onCleanup(@() close(f));
tiledlayout(f,2,1);
nexttile; plot(t,cell2mat(trial.trajectory.outputs.(outputName)),'LineWidth',1.3);
hold on; plot(t,cell2mat(trial.trajectory.references.(outputName)),'--','LineWidth',1.1);
grid on; ylabel(outputName,'Interpreter','none'); legend('Output','Reference','Location','best');
nexttile; stairs(t,cell2mat(trial.trajectory.control_inputs.(inputName)),'LineWidth',1.2);
hold on; plot(t,cell2mat(trial.trajectory.raw_control_inputs.(inputName)),':');
grid on; ylabel(inputName,'Interpreter','none'); xlabel('Time (s)'); legend('Applied command','Raw command','Location','best');
exportgraphics(f,path,'Resolution',140);
end
