/* QMW geometric optimization listener. Python replays to UDP 17430. */
(
s.waitForBoot {
    SynthDef(\qmwGeoProbe, { |out=0, value=0, side=1, amp=0.10|
        var freq = value.clip(0, 1).linexp(0, 1, 82.4, 880);
        var env = EnvGen.kr(Env.perc(0.006, 0.20, curve: -5), doneAction: 2);
        var tone = SinOsc.ar(freq) + (0.18 * VarSaw.ar(freq * 1.5, width: 0.3));
        Out.ar(out, Pan2.ar(tone * env * amp, side * 0.72));
    }).add;

    SynthDef(\qmwGeoUpdate, { |out=0, improvement=0, geodesic=0, amp=0.12|
        var base = Select.kr(improvement >= 0, [82.41, 55]);
        var spread = geodesic.clip(0, 0.3).linlin(0, 0.3, 1, 1.12);
        var env = EnvGen.kr(Env.perc(0.01, 0.42, curve: -6), doneAction: 2);
        var tone = Mix(SinOsc.ar(base * [1, spread, 1.5], 0, [0.6, 0.25, 0.15]));
        Out.ar(out, Pan2.ar(tone * env * amp));
    }).add;

    s.sync;
    ~qmwGeoBus = Bus.audio(s, 2);
    ~qmwGeoMaster = { Out.ar(0, Limiter.ar(In.ar(~qmwGeoBus, 2), 0.85)) }.play(addAction: \addToTail);

    OSCdef(\qmwGeoPlus, { |msg|
        Synth(\qmwGeoProbe, [\out, ~qmwGeoBus.index, \value, msg[5].asFloat, \side, -1]);
    }, '/qmw/geometric_opt/frame/probe/plus');

    OSCdef(\qmwGeoMinus, { |msg|
        Synth(\qmwGeoProbe, [\out, ~qmwGeoBus.index, \value, msg[5].asFloat, \side, 1]);
    }, '/qmw/geometric_opt/frame/probe/minus');

    OSCdef(\qmwGeoSummary, { |msg|
        var before = msg[4].asFloat;
        var after = msg[5].asFloat;
        var geodesic = msg[12].asFloat;
        Synth(\qmwGeoUpdate, [
            \out, ~qmwGeoBus.index,
            \improvement, before - after,
            \geodesic, geodesic
        ]);
    }, '/qmw/geometric_opt/frame/summary');

    thisProcess.openUDPPort(17430);
    "QMW geometric optimization listener ready on UDP 17430.".postln;
};
)
