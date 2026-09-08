function cfdc_plant_block(block)
%CFDC_PLANT_BLOCK Advance a fixed state-space plant only on Simulink sample hits.
block.NumDialogPrms=2;
block.DialogPrmsTunable={'Nontunable','Nontunable'};
block.NumInputPorts=1; block.NumOutputPorts=1;
block.SetPreCompInpPortInfoToDynamic(); block.SetPreCompOutPortInfoToDynamic();
block.InputPort(1).Dimensions=1; block.InputPort(1).DirectFeedthrough=false;
block.OutputPort(1).Dimensions=1;
block.SampleTimes=[block.DialogPrm(2).Data,0];
block.SimStateCompliance='DisallowSimState';
block.RegBlockMethod('Outputs',@outputs);
block.RegBlockMethod('Update',@update);
end
function outputs(block)
ctx=cfdcSim.registry('get',block.DialogPrm(1).Data);
block.OutputPort(1).Data=ctx.plant.measure();
end
function update(block)
ctx=cfdcSim.registry('get',block.DialogPrm(1).Data);
ctx.advance(block.InputPort(1).Data,block.CurrentTime);
end
