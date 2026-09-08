function cfdc_controller_block(block)
%CFDC_CONTROLLER_BLOCK Discrete ControllerIR and phase execution in Simulink.
block.NumDialogPrms=2;
block.DialogPrmsTunable={'Nontunable','Nontunable'};
block.NumInputPorts=2; block.NumOutputPorts=6;
block.SetPreCompInpPortInfoToDynamic(); block.SetPreCompOutPortInfoToDynamic();
for i=1:2
    block.InputPort(i).Dimensions=1;
    block.InputPort(i).DirectFeedthrough=true;
end
for i=1:6, block.OutputPort(i).Dimensions=1; end
block.SampleTimes=[block.DialogPrm(2).Data,0];
block.SimStateCompliance='DisallowSimState';
block.RegBlockMethod('PostPropagationSetup',@work);
block.RegBlockMethod('Start',@start);
block.RegBlockMethod('Outputs',@outputs);
block.RegBlockMethod('Update',@update);
block.RegBlockMethod('Terminate',@update);
end
function work(block)
block.NumDworks=1;
block.Dwork(1).Name='SampleCounter'; block.Dwork(1).Dimensions=1;
block.Dwork(1).DatatypeID=0; block.Dwork(1).Complexity='Real';
block.Dwork(1).UsedAsDiscState=true;
end
function start(block)
ctx=cfdcSim.registry('get',block.DialogPrm(1).Data);
ctx.reset();
block.Dwork(1).Data=0;
end
function outputs(block)
ctx=cfdcSim.registry('get',block.DialogPrm(1).Data);
values=ctx.preview(block.InputPort(1).Data,block.InputPort(2).Data,block.CurrentTime);
for i=1:6, block.OutputPort(i).Data=values(i); end
end
function update(block)
ctx=cfdcSim.registry('get',block.DialogPrm(1).Data);
ctx.commit();
block.Dwork(1).Data=block.Dwork(1).Data+1;
end
