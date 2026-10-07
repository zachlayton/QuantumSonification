/*
QMW Gauge Resonant Excitation V1

Opt-in OSC sonic body for qmw.gauge_resonant_excitation.osc.v1.
Port 17875 is dedicated to this receiver.  It accepts only complete
begin/node/edge/end transactions and does not send data back to QMW.

The frequency table below is a fixed resonator-body choice.  Gauge phase,
current, holonomy, and geometry never determine pitch in this script.
WhiteNoise is a sonic-body excitation choice, not quantum noise or decoherence.
*/

(
var root = "/qmw/gauge/v1/resonant_excitation";
var dataPort = 17875;
var maxNodes = 32;
var oscKeys = [
    \qmwGaugeResonantBeginV1,
    \qmwGaugeResonantNodeV1,
    \qmwGaugeResonantEdgeV1,
    \qmwGaugeResonantEndV1
];

oscKeys.do { |key| OSCdef(key).tryPerform(\free) };

s.waitForBoot {
    SynthDef(\qmwGaugeResonantBodyV1, { |
        out = 0, freq = 110, pan = 0, sustain = 0, release = 0,
        strike = 0, gain = 0.16
    |
        var sustained = Lag.kr(sustain.clip(0, 1), 0.06);
        var outgoing = Lag.kr(release.clip(0, 1), 0.06);
        var bodyDecay = (1.5 / (1 + (outgoing * 4))).clip(0.04, 1.5);
        var continuousExciter = HPF.ar(WhiteNoise.ar(sustained * 0.008), 35);
        var strikeExciter = Decay2.ar(K2A.ar(Changed.kr(strike)), 0.002, 0.09)
            * strike.clip(0, 1).sqrt * 0.13;
        var body = Ringz.ar(continuousExciter + strikeExciter, freq, bodyDecay);
        body = body + (Ringz.ar(strikeExciter * 0.35, freq * 2.01, bodyDecay * 0.55));
        Out.ar(out, Pan2.ar(LeakDC.ar(body) * gain, pan));
    }).add;
    s.sync;

    ~qmwGaugeResonantFrequencies = ~qmwGaugeResonantFrequencies ? Array.fill(maxNodes, { |index|
        82.4068892282175 * (2 ** (index / 12))
    });
    ~qmwGaugeResonantVoices = ~qmwGaugeResonantVoices ? Array.newClear(maxNodes);
    ~qmwGaugeResonantEnsureVoice = { |index|
        var pan = ((index / (maxNodes - 1)) * 2) - 1;
        if(~qmwGaugeResonantVoices[index].isNil or: { ~qmwGaugeResonantVoices[index].isRunning.not }) {
            ~qmwGaugeResonantVoices[index] = Synth(\qmwGaugeResonantBodyV1, [
                \freq, ~qmwGaugeResonantFrequencies[index], \pan, pan
            ]);
        };
        ~qmwGaugeResonantVoices[index]
    };
    ~qmwGaugeResonantStage = nil;

    OSCdef(\qmwGaugeResonantBeginV1, { |msg|
        var revision = msg[1].asInteger;
        var schema = msg[3].asString;
        var count = msg[5].asInteger.clip(0, maxNodes);
        if(schema == "qmw.gauge_resonant_excitation.osc.v1") {
            ~qmwGaugeResonantStage = IdentityDictionary[
                \revision -> revision,
                \nodeCount -> count,
                \sustain -> Array.fill(count, 0.0),
                \release -> Array.fill(count, 0.0),
                \transient -> Array.fill(count, 0.0)
            ];
        };
    }, root ++ "/frame/begin", recvPort: dataPort);

    OSCdef(\qmwGaugeResonantNodeV1, { |msg|
        var stage = ~qmwGaugeResonantStage;
        var index = msg[2].asInteger;
        if(stage.notNil and: { msg[1].asInteger == stage[\revision] } and: { index >= 0 and: { index < stage[\nodeCount] } }) {
            stage[\sustain][index] = msg[3].asFloat.max(0.0);
            stage[\release][index] = msg[4].asFloat.max(0.0);
        };
    }, root ++ "/node", recvPort: dataPort);

    OSCdef(\qmwGaugeResonantEdgeV1, { |msg|
        var stage = ~qmwGaugeResonantStage;
        var destination = msg[4].asInteger;
        var transient = msg[7].asFloat.max(0.0);
        if(stage.notNil and: { msg[1].asInteger == stage[\revision] } and: { destination >= 0 and: { destination < stage[\nodeCount] } }) {
            stage[\transient][destination] = stage[\transient][destination].max(transient);
        };
    }, root ++ "/edge", recvPort: dataPort);

    OSCdef(\qmwGaugeResonantEndV1, { |msg|
        var stage = ~qmwGaugeResonantStage;
        if(stage.notNil and: { msg[1].asInteger == stage[\revision] }) {
            s.bind {
                stage[\nodeCount].do { |index|
                    var voice = ~qmwGaugeResonantEnsureVoice.(index);
                    voice.set(
                        \sustain, stage[\sustain][index],
                        \release, stage[\release][index],
                        \strike, stage[\transient][index]
                    );
                };
            };
            ~qmwGaugeResonantStage = nil;
        };
    }, root ++ "/frame/end", recvPort: dataPort);

    "QMW Gauge Resonant Excitation V1: ready on UDP %".format(dataPort).postln;
};
)
