/*
QMW GPE observables instrument V1

Listen on UDP 17864 to the scalar/revisioned stream from qmw.osc.gpe_osc.
The companion Max patch uses UDP 17866 so both receivers can run together
when the publisher is configured with two clients.
This is a sound adapter: it reads density, current and modal observations; it
does not publish feedback or alter the Gross--Pitaevskii evolution.
*/
(
~qmwGPEPort = 17864;
~qmwGPEModalCount = 16;
~qmwGPERevision = -1;
~qmwGPEStage = IdentityDictionary.new;
~qmwGPEStage.putAll((density: 0.0, peak: 0.0, flowX: 0.0, flowY: 0.0, speed: 0.0,
    magnitudes: Array.fill(~qmwGPEModalCount, 0.0), phases: Array.fill(~qmwGPEModalCount, 0.0)));

~qmwGPEStop = {
    [\qmwGPEBegin, \qmwGPEDensity, \qmwGPEPeak, \qmwGPEFlowX, \qmwGPEFlowY,
        \qmwGPEFlowSpeed, \qmwGPEEnd].do { |key| OSCdef(key).free };
    ~qmwGPEModalCount.do { |index|
        OSCdef(("qmwGPEMag" ++ index).asSymbol).free;
        OSCdef(("qmwGPEPhase" ++ index).asSymbol).free;
    };
    ~qmwGPESynth !? { |synth| synth.free };
    ~qmwGPESynth = nil;
};

s.waitForBoot {
    SynthDef(\qmwGPEObservablesV1, { |out=0, density=0, densityPeak=0, flowPan=0, flowMotion=0,
        modeMagnitudes=#[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        modePhases=#[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]|
        var modes = Mix.fill(16, { |index|
            var magnitude = modeMagnitudes[index].clip(0, 1);
            var phase = modePhases[index];
            SinOsc.ar(55 * (index + 1), phase, magnitude / (index + 1))
        });
        var amp = density.sqrt.clip(0, 0.22) * (0.35 + (densityPeak.sqrt.clip(0, 1) * 0.65));
        var cutoff = 350 + (flowMotion.clip(0, 1) * 7000);
        var sound = RLPF.ar(modes, cutoff, 0.25 + (1 - flowMotion.clip(0, 1)) * 0.65) * amp;
        Out.ar(out, Pan2.ar(sound, flowPan.clip(-1, 1)));
    }).add;
    s.sync;
    ~qmwGPESynth = Synth(\qmwGPEObservablesV1);

    OSCdef(\qmwGPEBegin, { |msg|
        ~qmwGPERevision = msg[1].asInteger;
    }, "/qmw/gpe/frame/begin", recvPort: ~qmwGPEPort);
    OSCdef(\qmwGPEDensity, { |msg| if(msg[1].asInteger == ~qmwGPERevision) { ~qmwGPEStage[\density] = msg[2].asFloat } }, "/qmw/gpe/density/mean", recvPort: ~qmwGPEPort);
    OSCdef(\qmwGPEPeak, { |msg| if(msg[1].asInteger == ~qmwGPERevision) { ~qmwGPEStage[\peak] = msg[2].asFloat } }, "/qmw/gpe/density/max", recvPort: ~qmwGPEPort);
    OSCdef(\qmwGPEFlowX, { |msg| if(msg[1].asInteger == ~qmwGPERevision) { ~qmwGPEStage[\flowX] = msg[2].asFloat } }, "/qmw/gpe/flow/x", recvPort: ~qmwGPEPort);
    OSCdef(\qmwGPEFlowY, { |msg| if(msg[1].asInteger == ~qmwGPERevision) { ~qmwGPEStage[\flowY] = msg[2].asFloat } }, "/qmw/gpe/flow/y", recvPort: ~qmwGPEPort);
    OSCdef(\qmwGPEFlowSpeed, { |msg| if(msg[1].asInteger == ~qmwGPERevision) { ~qmwGPEStage[\speed] = msg[2].asFloat } }, "/qmw/gpe/flow/speed", recvPort: ~qmwGPEPort);
    ~qmwGPEModalCount.do { |index|
        OSCdef(("qmwGPEMag" ++ index).asSymbol, { |msg| if(msg[1].asInteger == ~qmwGPERevision) { ~qmwGPEStage[\magnitudes][index] = msg[2].asFloat } }, "/qmw/gpe/mode/" ++ index ++ "/magnitude", recvPort: ~qmwGPEPort);
        OSCdef(("qmwGPEPhase" ++ index).asSymbol, { |msg| if(msg[1].asInteger == ~qmwGPERevision) { ~qmwGPEStage[\phases][index] = msg[2].asFloat } }, "/qmw/gpe/mode/" ++ index ++ "/phase", recvPort: ~qmwGPEPort);
    };
    OSCdef(\qmwGPEEnd, { |msg|
        if(msg[1].asInteger == ~qmwGPERevision) {
            ~qmwGPESynth.set(\density, ~qmwGPEStage[\density], \densityPeak, ~qmwGPEStage[\peak],
                \flowPan, ~qmwGPEStage[\flowX].tanh, \flowMotion, ~qmwGPEStage[\speed].tanh);
            ~qmwGPESynth.setn(\modeMagnitudes, ~qmwGPEStage[\magnitudes]);
            ~qmwGPESynth.setn(\modePhases, ~qmwGPEStage[\phases]);
        }
    }, "/qmw/gpe/frame/end", recvPort: ~qmwGPEPort);
    "QMW GPE observables instrument V1 listening on UDP %".format(~qmwGPEPort).postln;
};
)
