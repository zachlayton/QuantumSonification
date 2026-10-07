/* QMW exact/transformed/difference real-time instrument. OSC data: UDP 17670. */
(
var dataPort = 17670;

s.waitForBoot {
    SynthDef(\qmwQiskitCompareV1, { |out=0, referenceMix=1, transformedMix=1,
        differenceMix=1, localMix=1, bondMix=1, traceMix=1, masterAmp=0.72,
        lagSeconds=0.12|
        var carriers = [110, 137.5, 165, 220];
        var bondCarriers = [247.5, 297, 371.25];
        var phases = [0, pi/7, 2*pi/7, 3*pi/7];
        var exactZ = NamedControl.kr(\exactZ, [1, 1, 1, 1], lagSeconds);
        var transformedZ = NamedControl.kr(\transformedZ, [1, 1, 1, 1], lagSeconds);
        var deltaZ = NamedControl.kr(\deltaZ, [0, 0, 0, 0], lagSeconds);
        var deltaZZ = NamedControl.kr(\deltaZZ, [0, 0, 0], lagSeconds);
        var distance = NamedControl.kr(\traceDistance, 0, lagSeconds).clip(0, 1);
        var exactAmp = 0.035 + (0.115 * ((1 + exactZ) * 0.5).clip(0, 1).sqrt);
        var transformedAmp = 0.035 + (0.115 * ((1 + transformedZ) * 0.5).clip(0, 1).sqrt);
        var exact = Mix(SinOsc.ar(carriers, phases, exactAmp));
        var transformed = Mix(SinOsc.ar(carriers, phases, transformedAmp));
        var localDifference = Mix(SinOsc.ar(carriers * 2, phases, 0.18 * deltaZ));
        var bondDifference = Mix(SinOsc.ar(bondCarriers, [0, pi/5, 2*pi/5], 0.12 * deltaZZ));
        var traceDifference = Mix(SinOsc.ar(330 + ([-1, 1] * (28 * distance)), 0, 0.11 * distance));
        var difference = (localDifference * localMix)
            + (bondDifference * bondMix)
            + (traceDifference * traceMix);
        var signal = Pan2.ar(exact * referenceMix, -0.65)
            + Pan2.ar(transformed * transformedMix, 0.65)
            + Pan2.ar(difference * differenceMix, 0);
        Out.ar(out, Limiter.ar(LeakDC.ar(signal * masterAmp), 0.95));
    }).add;

    s.sync;
    ~qmwCompareSynth = Synth(\qmwQiskitCompareV1);
    ~qmwCompareStageRevision = -1;
    ~qmwCompareStageValid = false;
    ~qmwCompareExactZ = [1, 1, 1, 1];
    ~qmwCompareTransformedZ = [1, 1, 1, 1];
    ~qmwCompareDeltaZ = [0, 0, 0, 0];
    ~qmwCompareDeltaZZ = [0, 0, 0];
    ~qmwCompareTraceDistance = 0;

    OSCdef(\qmwCompareBegin, { |msg|
        ~qmwCompareStageRevision = msg[1].asInteger;
        ~qmwCompareStageValid = true;
    }, '/qmw/qiskit_compare/frame/begin');

    OSCdef(\qmwCompareExactZ, { |msg|
        if(~qmwCompareStageValid and: { msg[1].asInteger == ~qmwCompareStageRevision }) {
            ~qmwCompareExactZ = msg.copyRange(2, 5).collect(_.asFloat);
        };
    }, '/qmw/qiskit_compare/exact/z');

    OSCdef(\qmwCompareTransformedZ, { |msg|
        if(~qmwCompareStageValid and: { msg[1].asInteger == ~qmwCompareStageRevision }) {
            ~qmwCompareTransformedZ = msg.copyRange(2, 5).collect(_.asFloat);
        };
    }, '/qmw/qiskit_compare/transformed/z');

    OSCdef(\qmwCompareDeltaZ, { |msg|
        if(~qmwCompareStageValid and: { msg[1].asInteger == ~qmwCompareStageRevision }) {
            ~qmwCompareDeltaZ = msg.copyRange(2, 5).collect(_.asFloat);
        };
    }, '/qmw/qiskit_compare/difference/z');

    OSCdef(\qmwCompareDeltaZZ, { |msg|
        if(~qmwCompareStageValid and: { msg[1].asInteger == ~qmwCompareStageRevision }) {
            ~qmwCompareDeltaZZ = msg.copyRange(2, 4).collect(_.asFloat);
        };
    }, '/qmw/qiskit_compare/difference/zz');

    OSCdef(\qmwCompareMetrics, { |msg|
        if(~qmwCompareStageValid and: { msg[1].asInteger == ~qmwCompareStageRevision }) {
            ~qmwCompareTraceDistance = msg[2].asFloat;
        };
    }, '/qmw/qiskit_compare/metrics');

    OSCdef(\qmwCompareEnd, { |msg|
        if(~qmwCompareStageValid and: { msg[1].asInteger == ~qmwCompareStageRevision }) {
            ~qmwCompareSynth.setn(\exactZ, ~qmwCompareExactZ);
            ~qmwCompareSynth.setn(\transformedZ, ~qmwCompareTransformedZ);
            ~qmwCompareSynth.setn(\deltaZ, ~qmwCompareDeltaZ);
            ~qmwCompareSynth.setn(\deltaZZ, ~qmwCompareDeltaZZ);
            ~qmwCompareSynth.set(\traceDistance, ~qmwCompareTraceDistance);
            ~qmwCompareStageValid = false;
        };
    }, '/qmw/qiskit_compare/frame/end');

    OSCdef(\qmwCompareMix, { |msg|
        ~qmwCompareSynth.set(
            \referenceMix, msg[1].asFloat,
            \transformedMix, msg[2].asFloat,
            \differenceMix, msg[3].asFloat,
            \masterAmp, msg[4].asFloat
        );
    }, '/qmw/qiskit_compare/mix');

    OSCdef(\qmwCompareDifferenceMix, { |msg|
        ~qmwCompareSynth.set(
            \localMix, msg[1].asFloat,
            \bondMix, msg[2].asFloat,
            \traceMix, msg[3].asFloat
        );
    }, '/qmw/qiskit_compare/difference/mix');

    OSCdef(\qmwComparePanic, {
        ~qmwCompareSynth.set(\masterAmp, 0);
    }, '/qmw/qiskit_compare/panic');

    thisProcess.openUDPPort(dataPort);
    "QMW Qiskit comparison instrument ready: OSC data UDP 17670.".postln;
};
)
