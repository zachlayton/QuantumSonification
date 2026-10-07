/*
QMW GRW sonification adapter receiver v1

The authoritative Python engine publishes one committed GRW render frame to
Max, SuperCollider, and Processing. Evaluate this file after booting the SC
server, then run the Python engine with:

    python quantumsonification_engine.py --sc-osc-port 57120

Mapping:
    trace distance          -> hit amplitude
    coherence loss         -> noise bandwidth and grain density
    affected qubit         -> one of four resonator branches
    dominant Pauli delta   -> X/Y/Z source orientation and sign
    post-event rho         -> continuing four-branch resonance level

Evaluate ~qmwGRWStop.() to remove responders and free synths.
*/

(
s.waitForBoot {
    var branchFrequencies = [55, 82.5, 110, 165];

    SynthDef(\qmwGRWBranchV1, {
        |out = 0, baseFreq = 55, pan = 0, postLevel = 0, persistentGain = 0,
        hitAmplitude = 0, bandwidth = 0.04, grainStructure = 0,
        axis = 1, orientationSign = 1, pauliDelta = 0, t_hit = 0|

        var trigger = Trig1.kr(t_hit, ControlDur.ir);
        var rq = bandwidth.clip(0.001, 1).linexp(0.001, 1, 0.008, 0.72);
        var decay = bandwidth.clip(0, 1).linexp(0.001, 1, 1.8, 0.10);
        var eventEnvelope = Decay2.kr(trigger, 0.003, decay) * hitAmplitude.clip(0, 1);
        var ratios = [1, 1.5, 2, 2.75, 4];
        var frequencies = (baseFreq * ratios).clip(25, SampleRate.ir * 0.42);
        var phase = orientationSign.sign * (pi * 0.5);
        var xSource;
        var ySource;
        var zSource;
        var selected;
        var persistent;
        var signal;

        // X: coherent quadrature strike.
        xSource = Mix(SinOsc.ar(frequencies, phase)) / ratios.size;

        // Y: coherence loss opens a progressively broader noise band.
        ySource = Mix(BPF.ar(WhiteNoise.ar(0.45), frequencies, rq))
            / ratios.size.sqrt;

        // Z: discrete grains excite the same branch resonances.
        zSource = Mix(Ringz.ar(
            Dust2.ar(grainStructure.clip(0, 1).linexp(0.001, 1, 1, 95), 0.2),
            frequencies,
            decay
        )) / ratios.size.sqrt;

        selected = Select.ar((axis.clip(1, 3) - 1), [xSource, ySource, zSource]);
        selected = selected * eventEnvelope * (1 + pauliDelta.abs.clip(0, 1));

        // rho+ remains after the flash as a quiet resonant condition.
        persistent = Mix(SinOsc.ar(
            frequencies,
            phase,
            postLevel.clip(0, 1) * persistentGain.clip(0, 1) * 0.012 / ratios
        ));

        signal = LeakDC.ar((selected + persistent).tanh);
        signal = Limiter.ar(signal, 0.82, 0.01);
        Out.ar(out, Pan2.ar(signal, pan.clip(-1, 1)));
    }).add;

    s.sync;

    ~qmwGRWBranchLevels = Array.fill(4, 0.0);
    ~qmwGRWPopulation = Array.fill(16, 0.0);
    ~qmwGRWSynths = branchFrequencies.collect { |frequency, index|
        Synth(\qmwGRWBranchV1, [
            \baseFreq, frequency,
            \pan, index.linlin(0, 3, -0.78, 0.78),
            \postLevel, 0
        ])
    };

    OSCdef(\qmwGRWBranchLevels, { |message|
        ~qmwGRWBranchLevels = Array.fill(4, { |index|
            if(message.size > (index + 1)) { message[index + 1].asFloat } { 0.0 }
        });
        ~qmwGRWSynths.do { |synth, index|
            synth.set(\postLevel, ~qmwGRWBranchLevels[index])
        };
    }, '/qmw/grw/sonification/post/branch_levels');

    OSCdef(\qmwGRWPopulation, { |message|
        ~qmwGRWPopulation = Array.fill(16, { |index|
            if(message.size > (index + 1)) { message[index + 1].asFloat } { 0.0 }
        });
    }, '/qmw/grw/sonification/post/population');

    OSCdef(\qmwGRWEvent, { |message|
        var eventId = message[1].asInteger;
        var branch = message[2].asInteger.clip(0, 3);
        var amplitude = message[3].asFloat.clip(0, 1);
        var coherenceLoss = message[4].asFloat.clip(0, 1);
        var bandwidth = message[5].asFloat.clip(0, 1);
        var grains = message[6].asFloat.clip(0, 1);
        var axis = message[7].asInteger.clip(1, 3);
        var sign = message[8].asFloat.sign;
        var delta = message[9].asFloat;
        var audible = message[10].asInteger;

        if(audible > 0) {
            ~qmwGRWSynths[branch].set(
                \hitAmplitude, amplitude,
                \bandwidth, bandwidth,
                \grainStructure, grains,
                \axis, axis,
                \orientationSign, sign,
                \pauliDelta, delta,
                \t_hit, 1
            );
        };
        "GRW event % | q% | amp % | loss % | axis %"
            .format(eventId, branch, amplitude.round(0.001),
                coherenceLoss.round(0.001), axis).postln;
    }, '/qmw/grw/sonification/event');

    ~qmwGRWStop = {
        [\qmwGRWBranchLevels, \qmwGRWPopulation, \qmwGRWEvent].do { |name|
            OSCdef(name).free
        };
        ~qmwGRWSynths.do(_.free);
        "QMW GRW resonator stopped.".postln;
    };

    "QMW GRW resonator listening on SuperCollider language port 57120.".postln;
};
)
