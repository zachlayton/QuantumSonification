/*
QMW ZX Processing Companion v1

Evaluate the first block to boot a quiet sonification voice and install exact
OSC receivers for the Processing frontend. Processing sends to language port
57120.
*/

(
s.waitForBoot({
    SynthDef(\qmwZXProcessingVoice, {
        |out = 0, freq = 110, harmonic = 2, entropy = 0,
        coherence = 0, amp = 0.04, pan = 0|

        var drift = (
            LFNoise1.kr(1.5) * entropy * 0.02
        ).midiratio;
        var carrier = SinOsc.ar(freq * drift, 0, 0.68);
        var upper = LFTri.ar(
            freq * harmonic * drift,
            0,
            coherence * 0.24
        );
        var signal = LeakDC.ar(carrier + upper);

        Out.ar(
            out,
            Pan2.ar(
                signal * Lag.kr(amp, 0.08),
                Lag.kr(pan, 0.08)
            )
        );
    }).add;

    SynthDef(\qmwZXRewriteChime, {
        |out = 0, freq = 330, color = 0|

        var envelope = Env.perc(0.006, 0.9, 0.13, -5).ar(doneAction: 2);
        var zTone = SinOsc.ar(freq * [1, 1.005], 0, envelope);
        var xTone = LFTri.ar(freq * [1, 1.008], 0, envelope * 0.8);
        var signal = SelectX.ar(color.clip(0, 1), [zTone, xTone]);

        Out.ar(out, signal);
    }).add;

    s.sync;

    ~qmwZXVoice.tryPerform(\free);
    ~qmwZXVoice = Synth(\qmwZXProcessingVoice);
    ~qmwZXControls = [0.0, 0.5, 0.0, 0.0, 0.5, 0.75];

    ~qmwZXUpdateVoice = {
        ~qmwZXVoice.set(
            \freq, 110 * (2 ** (~qmwZXControls[0] * 2)),
            \harmonic, 1.5 + (2 * ~qmwZXControls[1]),
            \entropy, ~qmwZXControls[2],
            \coherence, ~qmwZXControls[3],
            \pan, -0.75 + (1.5 * ~qmwZXControls[4]),
            \amp, 0.012 + (0.075 * ~qmwZXControls[5])
        );
    };
    ~qmwZXUpdateVoice.value;

    OSCdef(\qmwZXFader, { |message|
        var controlId = message[1].asInteger;
        var value = message[2].asFloat.clip(0, 1);

        if(controlId.inclusivelyBetween(1, 6), {
            ~qmwZXControls[controlId - 1] = value;
            ~qmwZXUpdateVoice.value;
        });
    }, "/qmw/zx/fader", recvPort: 57120);

    OSCdef(\qmwZXNodePosition, { |message|
        ["node position", message[1], message[2], message[3]].postln;
    }, "/qmw/zx/node/position", recvPort: 57120);

    OSCdef(\qmwZXNodePhase, { |message|
        ["node phase", message[1], message[2], message[3]].postln;
    }, "/qmw/zx/node/phase", recvPort: 57120);

    OSCdef(\qmwZXNodeAdd, { |message|
        [
            "node add",
            message[1],
            message[2],
            message[3],
            message[4],
            message[5]
        ].postln;
    }, "/qmw/zx/node/add", recvPort: 57120);

    OSCdef(\qmwZXNodeDelete, { |message|
        ["node delete", message[1]].postln;
    }, "/qmw/zx/node/delete", recvPort: 57120);

    OSCdef(\qmwZXEdgeAdd, { |message|
        ["edge add", message[1], message[2], message[3]].postln;
    }, "/qmw/zx/edge/add", recvPort: 57120);

    OSCdef(\qmwZXGraphScalar, { |message|
        ["graph scalar", message[1], message[2]].postln;
    }, "/qmw/zx/graph/scalar", recvPort: 57120);

    OSCdef(\qmwZXRewriteFuse, { |message|
        var kind = message[3].asString;
        var phase = message[4].asFloat;
        var frequency = 220 * (2 ** ((phase / 2pi) * 2));

        Synth(
            \qmwZXRewriteChime,
            [
                \freq, frequency,
                \color, (kind == "X").asInteger
            ]
        );
        [
            "rewrite fuse",
            message[1],
            message[2],
            message[3],
            message[4]
        ].postln;
    }, "/qmw/zx/rewrite/fuse", recvPort: 57120);

    OSCdef(\qmwZXRewriteApply, { |message|
        var rule = message[1].asString;
        var error = message[2].asFloat;
        var scalarReal = message[3].asFloat;
        var scalarImag = message[4].asFloat;
        var scalarMagnitude = (
            scalarReal.squared + scalarImag.squared
        ).sqrt.max(0.001);
        var frequency = 440 * (2 ** (scalarMagnitude.log2.clip(-1, 1) * 0.25));

        Synth(
            \qmwZXRewriteChime,
            [
                \freq, frequency,
                \color, (rule == "color_change").asInteger
            ]
        );
        [
            "rewrite apply",
            rule,
            "tensor error",
            error,
            "scalar",
            scalarReal,
            scalarImag
        ].postln;
    }, "/qmw/zx/rewrite/apply", recvPort: 57120);

    "QMW ZX companion listening on UDP 57120".postln;
});
)

/*
Cleanup:

(
[
    \qmwZXFader,
    \qmwZXNodePosition,
    \qmwZXNodePhase,
    \qmwZXNodeAdd,
    \qmwZXNodeDelete,
    \qmwZXEdgeAdd,
    \qmwZXGraphScalar,
    \qmwZXRewriteFuse,
    \qmwZXRewriteApply
].do({ |name| OSCdef(name).free });
~qmwZXVoice.tryPerform(\free);
)
*/
