/*
QMW ecological sonification V1 — SuperCollider reference renderer.

Receives the same semantic vector as the Max comparison instrument on UDP
57120.  LivingSpectralGeometry frequencies are the pitches; ecological and
quantum descriptors shape excitation, texture, and decay.  Evaluate this file
after booting the server.  Stop with ~qmwEcologySCStop.().
*/
(
thisProcess.openUDPPort(57120);

s.waitForBoot {
    ~qmwEcologyFrequencies = [110.0, 164.8138, 220.0, 329.6276];
    ~qmwEcologyStressDrive = 0.0;
    ~qmwEcologyFrame = -1;

    SynthDef(\qmwEcologicalSonificationV1, {
        |out=0, pulseHz=0.5, excitationGain=0.04, noiseMix=0.05,
        decaySeconds=0.08, filterHz=400, masterGain=0.12,
        eventGain=0.5, t_measurement=0, t_commit=0, gate=1|
        var frequencies = NamedControl.kr(
            \frequencies, [110.0, 164.8138, 220.0, 329.6276]
        );
        var pulse = Decay2.ar(Impulse.ar(pulseHz.clip(0.1, 20)), 0.001, 0.025)
            * excitationGain.clip(0, 1);
        var event = Decay2.kr(t_measurement, 0.002, 0.18)
            * eventGain.clip(0, 1);
        var commit = Decay2.kr(t_commit, 0.005, 0.5) * 0.65;
        var noise = LPF.ar(
            PinkNoise.ar(noiseMix.clip(0, 1) * 0.028),
            filterHz.clip(80, 16000)
        );
        var source = pulse + event + commit + noise;
        var modes = Ringz.ar(
            source,
            frequencies.clip(30, 16000),
            decaySeconds.clip(0.04, 3.0)
        );
        var signal = Splay.ar(modes, 0.82, 0.25);
        var envelope = EnvGen.kr(
            Env.asr(0.03, 1, 0.2), gate, doneAction: Done.freeSelf
        );
        Out.ar(out, Limiter.ar(LeakDC.ar(signal) * masterGain, 0.9, 0.01)
            * envelope);
    }).add;

    s.sync;
    ~qmwEcologySynth = Synth(\qmwEcologicalSonificationV1, [
        \frequencies, ~qmwEcologyFrequencies
    ]);

    OSCdef(\qmwEcologySemanticV1, { |message|
        var purity = message[3].asFloat.clip(0, 1);
        var entropyNormalized = message[5].asFloat.clip(0, 1);
        var coherence = message[6].asFloat.clip(0, 1);
        var alignment = message[7].asFloat.clip(0, 1);
        var kineticDrive = message[9].asFloat.clip(0, 1);
        var densityDrive = message[11].asFloat.clip(0, 1);
        ~qmwEcologyStressDrive = message[13].asFloat.clip(0, 1);
        ~qmwEcologyFrame = message[1].asInteger;
        ~qmwEcologySynth.set(
            \pulseHz, 0.5 + (11.5 * densityDrive),
            \excitationGain, 0.04 + (0.38 * coherence),
            \noiseMix, 0.05 + (0.55 * entropyNormalized),
            \decaySeconds, 0.08 + (2.42 * alignment),
            \filterHz, 400 + (7600 * kineticDrive),
            \masterGain, 0.08 + (0.12 * purity.sqrt)
        );
    }, '/qmw/ecology/v1/sonification', recvPort: 57120);

    OSCdef(\qmwEcologyMeasurementV1, { |message|
        var probability = message[4].asFloat.clip(0, 1);
        var gain = probability.sqrt
            * (0.35 + (0.65 * ~qmwEcologyStressDrive));
        ~qmwEcologySynth.set(\eventGain, gain, \t_measurement, 1);
    }, '/qmw/ecology/v1/measurement', recvPort: 57120);

    OSCdef(\qmwEcologyCommitV1, { |message|
        "QMW ecology spectral commit r%".format(message[1]).postln;
        ~qmwEcologySynth.set(\t_commit, 1);
    }, '/qmw/ecology/v1/commit', recvPort: 57120);

    OSCdef(\qmwEcologyFrequenciesV1, { |message|
        var octaveScale;
        // The Python contract rejects NaN/Inf before publication. Omit only
        // zero/DC, then transpose the whole spectrum by octaves so its lowest
        // nonzero mode is audible while every geometric frequency ratio stays
        // unchanged.
        var audible = message.copyRange(1, message.size - 1).collect(_.asFloat)
            .select { |frequency| frequency > 0.001 };
        if(audible.size > 0) {
            octaveScale = 2.pow((55 / audible.minItem).log2.ceil.max(0));
            ~qmwEcologyFrequencies = Array.fill(4, { |index|
                (audible.wrapAt(index) * octaveScale).clip(30, 16000)
            });
            ~qmwEcologySynth.setn(\frequencies, ~qmwEcologyFrequencies);
            "QMW ecology committed modes: %".format(
                ~qmwEcologyFrequencies.round(0.01)
            ).postln;
        };
    }, '/living/spectrum/frequencies', recvPort: 57120);

    ~qmwEcologySCStop = {
        [\qmwEcologySemanticV1, \qmwEcologyMeasurementV1,
            \qmwEcologyCommitV1, \qmwEcologyFrequenciesV1].do { |key|
            OSCdef(key).free
        };
        if(~qmwEcologySynth.notNil) { ~qmwEcologySynth.set(\gate, 0) };
        "QMW ecological SC renderer stopped.".postln;
    };

    "QMW ecological SC renderer listening on UDP 57120.".postln;
};
)
