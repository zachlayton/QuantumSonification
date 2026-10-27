/* Offline render: the same six-second field is heard dry, ring-modulated, then
   fuzzed. Output 1-2 = field; 3-4 = identical 0.4 FX-send tap. Final section mutes.
   QMW_EVENT_RENDER, QMW_SCSYNTH, QMW_SC_PLUGINS optionally select paths. */
(
var here=thisProcess.nowExecutingPath.dirname, defs, score=List.new;
var path="QMW_EVENT_RENDER".getenv ? (PathName.tmp +/+ "qmw_event_field_check.wav");
var options=ServerOptions.new.numOutputBusChannels_(4).numInputBusChannels_(0);
var step=0.005, scale=0.8, previous, residual, node=2000;
thisProcess.interpreter.executeFile(here +/+ "../supercollider/Model.scd");
thisProcess.interpreter.executeFile(here +/+ "../supercollider/SynthDefs.scd");
defs=~qefDefine.();
defs.do { |def| score.add([0, [\d_recv, def.asBytes]]) };
score.add([0.01, [\c_setn, 0, 13, 0,110,0,1,0,0,0,2,0.6,0.5,0.3,0,0.5]]);
score.add([0.02, [\s_new, \qefMixerV1,1000,1,0,\inBus,16,\out,0,\fxSendBus,2,
    \gain,0.08,\fxSend,0.4,\ringMixBus,0,\ringFrequencyBus,1,
    \wavefoldMixBus,2,\wavefoldDriveBus,3,\wavefoldWarpAmountBus,4,
    \wavefoldWarpShapeBus,5,\fuzzMixBus,6,\fuzzDriveBus,7,\fuzzSecondBus,8,
    \fuzzThirdBus,9,\fuzzHigherBus,10,\fuzzBiasBus,11,\fuzzToneBus,12]]);
3.do { |pass|
    var offset=0.2+(pass*10);
    previous=~qefFrame.(0); residual=0.0!4;
    score.add([offset, [\c_set,0,if(pass==1,{0.65},{0}),6,if(pass==2,{0.55},{0})]]);
    score.add([offset, [\c_setn,20,4] ++ previous[\p]]);
    1500.do { |i|
        var next=~qefFrame.((i+1)*step);
        ~qefCrossings.(previous,next,residual,0.08,step).do { |e|
            var tau=(i+e[0])*step, frame=~qefFrame.(tau), site=e[1], source=frame[\source][site];
            var time=offset+(tau*scale), duration=~qefDuration.(frame,site,scale);
            score.add([time,[\s_new,\qefWaveletV1,node,2,1000,\out,16,\popBus,20,
                \site,site,\source,source,\duration,duration,\strength,frame[\p][site].sqrt]]);
            score.add([time,[\n_setn,node,\weightsA,4] ++ ~qefModes[site].squared
                ++ [\weightsB,4] ++ ~qefModes[source].squared]);
            node=node+1;
        };
        score.add([offset+((i+1)*step*scale),[\c_setn,20,4] ++ next[\p]]);
        previous=next;
    };
};
// Biased fuzz followed by Sound off must produce silence, including the send.
score.add([29.5,[\c_set,11,0.5,6,1]]);
score.add([30,[\n_set,1000,\enabled,0]]);
score.add([31,[\n_set,1000,\enabled,1,\gain,0]]);
score.add([31.8,[\n_free,1000]]);
"QMW_SCSYNTH".getenv !? { |p| Score.program=p };
"QMW_SC_PLUGINS".getenv !? { |p| options.ugenPluginsPath=p };
options.numWireBufs=4096;
Score(score.asArray).recordNRT(outputFilePath:path, sampleRate:48000,
    headerFormat:"WAV", sampleFormat:"float", options:options, duration:32,
    action:{ |code| ("NRT exit " ++ code ++ " -> " ++ path).postln; code.exit });
)
