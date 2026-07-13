/*
QMW FluCoMa SuperCollider bridge

Run this in SuperCollider, then run:

    env NUMBA_CACHE_DIR=/private/tmp/numba_cache /Users/zlayton/miniconda3/envs/music/bin/python quantum_population_osc_v8_flucoma_sc.py

The v8 wrapper mirrors the normal QMW OSC stream to SuperCollider's default
language port, 57120, while keeping Max on 7400 and Processing on 7401.
*/

(
s.waitForBoot {
    var makePlayer;

    "QMW FluCoMa SC bridge booting...".postln;
    "Listening on SuperCollider language port: %".format(NetAddr.langPort).postln;

    ~qmwCurrentBuffer = nil;
    ~qmwLastPath = nil;
    ~qmwDepth = 0.5;
    ~qmwScatter = 0.0;
    ~qmwRate = 0.0;

    SynthDef(\qmwCorpusPlayer, { |out = 0, buf = 0, amp = 0.28, rate = 1.0, pan = 0.0|
        var sig;
        sig = PlayBuf.ar(
            1,
            buf,
            BufRateScale.kr(buf) * rate.clip(0.125, 4.0),
            doneAction: 2
        );
        sig = LeakDC.ar(sig);
        sig = Pan2.ar(sig, pan.clip(-1, 1), amp.clip(0, 1));
        Out.ar(out, sig);
    }).add;

    SynthDef(\qmwSpinTone, { |out = 0, amp = 0.055, freq = 220, depth = 0.5, scatter = 0.0, rate = 0.0, pan = 0.0, gate = 1|
        var wobble, carrier, rq, cutoff, env, sig;
        wobble = SinOsc.kr(rate.linexp(0.001, 1, 0.08, 14)).range(0.96, 1.04);
        carrier = Saw.ar(freq.clip(40, 2400) * [1, 1.003] * wobble);
        cutoff = freq * depth.linexp(0.001, 1, 1.5, 14);
        rq = scatter.linlin(0, 1, 0.82, 0.12).clip(0.08, 0.98);
        sig = RLPF.ar(carrier, cutoff.clip(80, 12000), rq);
        env = EnvGen.kr(Env.asr(0.02, 1, 0.25), gate, doneAction: 2);
        Out.ar(out, Pan2.ar(Mix(sig) * amp * env, pan.clip(-1, 1)));
    }).add;

    s.sync;

    ~qmwSpinSynth = Synth(\qmwSpinTone);

    makePlayer = { |path, amp = 0.32|
        if(path.notNil and: { path.size > 0 }) {
            if(~qmwCurrentBuffer.notNil) {
                ~qmwCurrentBuffer.free;
                ~qmwCurrentBuffer = nil;
            };
            Buffer.read(s, path, action: { |buf|
                ~qmwCurrentBuffer = buf;
                "QMW playing nearest material: %".format(path).postln;
                Synth(\qmwCorpusPlayer, [
                    \buf, buf,
                    \amp, amp,
                    \rate, ~qmwRate.linexp(0.001, 1, 0.75, 1.6),
                    \pan, 0
                ]);
            });
        };
    };

    OSCdef(\qmwNearestAudioPath, { |msg|
        var path = msg[1].asString;
        if(path != ~qmwLastPath) {
            ~qmwLastPath = path;
            makePlayer.(path);
        };
    }, '/qmw/flucoma/audio/nearest/path');

    OSCdef(\qmwNearestAudioChanged, { |msg|
        if(msg[1].asInteger == 1) {
            "QMW nearest audio changed".postln;
        };
    }, '/qmw/flucoma/audio/nearest/changed');

    OSCdef(\qmwCursor, { |msg|
        var x = msg[1].asFloat.clip(0.001, 1.0);
        var y = msg[2].asFloat.clip(0.0, 1.0);
        ~qmwSpinSynth.set(
            \freq, x.linexp(0.001, 1, 80, 1200),
            \pan, y.linlin(0, 1, -0.85, 0.85)
        );
    }, '/qmw/flucoma/cursor');

    OSCdef(\qmwDepth, { |msg|
        ~qmwDepth = msg[1].asFloat.clip(0, 1);
        ~qmwSpinSynth.set(\depth, ~qmwDepth);
    }, '/qmw/flucoma/depth');

    OSCdef(\qmwScatter, { |msg|
        ~qmwScatter = msg[1].asFloat.clip(0, 1);
        ~qmwSpinSynth.set(\scatter, ~qmwScatter);
    }, '/qmw/flucoma/scatter');

    OSCdef(\qmwRate, { |msg|
        ~qmwRate = msg[1].asFloat.clip(0, 1);
        ~qmwSpinSynth.set(\rate, ~qmwRate);
    }, '/qmw/flucoma/rate');

    OSCdef(\qmwMosaicExplanation, { |msg|
        "QMW mosaic: %".format(msg[1].asString).postln;
    }, '/qmw/flucoma/mosaic/explanation');

    ~qmwPlayTestMaterial = {
        makePlayer.("/Users/zlayton/QuantumSonification/materials/test.wav", 0.35);
    };

    ~qmwStop = {
        OSCdef(\qmwNearestAudioPath).free;
        OSCdef(\qmwNearestAudioChanged).free;
        OSCdef(\qmwCursor).free;
        OSCdef(\qmwDepth).free;
        OSCdef(\qmwScatter).free;
        OSCdef(\qmwRate).free;
        OSCdef(\qmwMosaicExplanation).free;
        if(~qmwSpinSynth.notNil) { ~qmwSpinSynth.set(\gate, 0) };
        if(~qmwCurrentBuffer.notNil) { ~qmwCurrentBuffer.free };
        "QMW FluCoMa SC bridge stopped.".postln;
    };

    ~qmwNMFCross = { |sourcePath, targetPath|
        var source, target, output;
        Buffer.read(s, sourcePath, action: { |src|
            source = src;
            Buffer.read(s, targetPath, action: { |tgt|
                target = tgt;
                output = Buffer.alloc(s, target.numFrames, 1);
                FluidBufNMFCross.process(
                    s,
                    source: source,
                    target: target,
                    output: output,
                    timeSparsity: 7,
                    polyphony: 9,
                    continuity: 7,
                    iterations: 30,
                    action: {
                        "QMW FluidBufNMFCross complete.".postln;
                        Synth(\qmwCorpusPlayer, [\buf, output, \amp, 0.38]);
                    }
                );
            });
        });
    };

    "Ready. Try ~qmwPlayTestMaterial.() to confirm audio.".postln;
    "Try ~qmwStop.() to free OSCdefs and synths.".postln;
};
)
