/* QMW SPSA probe-pair listener. Start this before the Python publisher. */
(
s.waitForBoot {
    SynthDef(\qmwSPSAProbe, { |out=0, value=0, side=1, amp=0.11|
        var midi = value.clip(-1, 1).linlin(-1, 1, 45, 84);
        var freq = midi.midicps * Select.kr(side > 0, [0.997, 1.003]);
        var env = EnvGen.kr(Env.perc(0.006, 0.23, curve: -5), doneAction: 2);
        var tone = SelectX.ar(side > 0, [
            SinOsc.ar(freq) + (0.22 * SinOsc.ar(freq * 2.01)),
            VarSaw.ar(freq, width: 0.23) + (0.18 * SinOsc.ar(freq * 1.5))
        ]);
        Out.ar(out, Pan2.ar(tone * env * amp, side * 0.72));
    }).add;

    SynthDef(\qmwSPSAGradient, { |out=0, norm=0.1, amp=0.08|
        var brightness = norm.clip(0, 2).linexp(0, 2, 700, 6200);
        var freqs = [110, 138.59, 164.81, 207.65] * (1 + (norm.clip(0, 3) * 0.04));
        var env = EnvGen.kr(Env.perc(0.015, 0.48, curve: -4), doneAction: 2);
        var chord = Mix(SinOsc.ar(freqs, 0, [0.35, 0.27, 0.22, 0.18]));
        var air = BPF.ar(PinkNoise.ar(0.5), brightness, 0.16);
        Out.ar(out, Pan2.ar((chord + air) * env * amp, 0));
    }).add;

    SynthDef(\qmwSPSAUpdate, { |out=0, improvement=0, amp=0.12|
        var descended = improvement >= 0;
        var freq = Select.kr(descended, [73.42, 55]);
        var env = EnvGen.kr(Env.perc(0.004, 0.42, curve: -7), doneAction: 2);
        var tone = SinOsc.ar(freq, 0, 0.8) + SinOsc.ar(freq * 2, 0, 0.2);
        Out.ar(out, Pan2.ar(tone * env * amp, 0));
    }).add;

    SynthDef(\qmwSPSAMaster, { |in=0, out=0|
        var signal = In.ar(in, 2);
        var mono = Mix.ar(signal) * 0.5;
        var amplitudeLeft = Amplitude.kr(signal[0], 0.01, 0.18);
        var amplitudeRight = Amplitude.kr(signal[1], 0.01, 0.18);
        var energy = ((amplitudeLeft + amplitudeRight) * 3.5).clip(0, 1);
        var centroid = (SpecCentroid.kr(FFT(LocalBuf(2048), mono)) / 10000).clip(0, 1);
        var flux = (HPZ1.kr(energy).abs * 10).clip(0, 1);
        var balance = ((amplitudeRight - amplitudeLeft) /
            (amplitudeRight + amplitudeLeft + 0.0001)).clip(-1, 1);
        var resonance = ((1 - flux) * (0.5 + (energy * 0.5))).clip(0, 1);
        SendReply.kr(
            Impulse.kr(12),
            '/qmw/spsa/analysis',
            [energy, centroid, flux, balance, resonance]
        );
        Out.ar(out, Limiter.ar(signal, 0.85));
    }).add;

    s.sync;

    ~spsaAudioBus = Bus.audio(s, 2);
    ~spsaFeedbackTarget = NetAddr("127.0.0.1", 17421);
    ~spsaMaster = Synth.tail(s, \qmwSPSAMaster, [\in, ~spsaAudioBus.index]);

    OSCdef(\qmwSPSAAnalysisForward, { |msg|
        ~spsaFeedbackTarget.sendMsg(
            '/qmw/spsa/feedback',
            msg[3].asFloat,
            msg[4].asFloat,
            msg[5].asFloat,
            msg[6].asFloat,
            msg[7].asFloat
        );
    }, '/qmw/spsa/analysis');

    OSCdef(\qmwSPSAPlus, { |msg|
        Synth(\qmwSPSAProbe, [
            \out, ~spsaAudioBus.index, \value, msg[3].asFloat, \side, -1
        ]);
    }, '/qmw/spsa/probe/plus');

    OSCdef(\qmwSPSAMinus, { |msg|
        Synth(\qmwSPSAProbe, [
            \out, ~spsaAudioBus.index, \value, msg[3].asFloat, \side, 1
        ]);
    }, '/qmw/spsa/probe/minus');

    OSCdef(\qmwSPSAGradient, { |msg|
        Synth(\qmwSPSAGradient, [
            \out, ~spsaAudioBus.index, \norm, msg[2].asFloat
        ]);
    }, '/qmw/spsa/gradient');

    OSCdef(\qmwSPSAUpdate, { |msg|
        var before = msg[2].asFloat;
        var after = msg[3].asFloat;
        Synth(\qmwSPSAUpdate, [
            \out, ~spsaAudioBus.index, \improvement, before - after
        ]);
    }, '/qmw/spsa/update');

    "QMW SPSA closed-loop listener: questions on 17420, answers to 17421.".postln;
    thisProcess.openUDPPort(17420);
};
)
