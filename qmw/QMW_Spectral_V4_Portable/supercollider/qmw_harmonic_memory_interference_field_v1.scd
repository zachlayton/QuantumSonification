/* QMW Harmonic Memory Interference Field V1.
   An additive, non-recursive eight-path baseline for the transfer function
       H(w) = sum_k a_k exp(-i w tau_k).
   It is driven only by an audio send from admitted plucks. It does not read or
   alter rho, event admission, or the existing temporal-memory observer. */
(
var pathCount = 8;
var defaultRatios = [
    1.0, 53 / 37, 71 / 37, 89 / 37, 113 / 37, 137 / 37, 163 / 37, 191 / 37
];

~qmwHmiSynth !? _.free;
~qmwHmiInputBus !? _.free;
~qmwHmiInputBus = Bus.audio(s, 2);
~qmwHmiPathCount = pathCount;
~qmwHmiRatios = (~qmwHmiRatios ? defaultRatios).collect(_.asFloat);
~qmwHmiBaseDelaySeconds = (~qmwHmiBaseDelaySeconds ? 0.037).asFloat.clip(0.020, 0.090);
~qmwHmiHarmonicExponent = (~qmwHmiHarmonicExponent ? 1.0).asFloat.clip(0.5, 3.0);
~qmwHmiMix = (~qmwHmiMix ? 0.32).asFloat.clip(0, 0.5);
~qmwHmiGlideSeconds = (~qmwHmiGlideSeconds ? 0.08).asFloat.clip(0.005, 0.5);

SynthDef(\qmwHarmonicMemoryInterferenceFieldV1, {
    |out=0, inBus=0, master=0.32, baseDelay=0.037, harmonicExponent=1, glideSeconds=0.08|
    var ratios = NamedControl.kr(\ratios, defaultRatios);
    var input, delays, rawWeights, weights, taps, sum, envelope;
    var base = Lag.kr(baseDelay.clip(0.020, 0.090), glideSeconds.clip(0.005, 0.5));
    var exponent = Lag.kr(harmonicExponent.clip(0.5, 3.0), 0.05);
    ratios = Lag.kr(ratios, glideSeconds.clip(0.005, 0.5));
    input = InFeedback.ar(inBus, 2);
    delays = ratios * base;
    rawWeights = Array.fill(pathCount, { |index| (index + 1).asFloat.pow(exponent.neg) });
    weights = rawWeights / rawWeights.sum.max(1e-9);
    // Coherent recombination preserves the actual phasor sum: each path is a
    // delayed copy of the same stereo source, so cancellation/reinforcement
    // is governed by its physical delay phase at every audio frequency.
    taps = Array.fill(pathCount, { |index|
        DelayC.ar(input, 1.2, delays[index].clip(0.001, 1.1)) * weights[index]
    });
    sum = Mix(taps) * pathCount.sqrt;
    envelope = Lag.kr(master.clip(0, 0.5), 0.03);
    Out.ar(out, Limiter.ar(LeakDC.ar(sum) * envelope, 0.84));
}).add;

SynthDef(\qmwHarmonicMemoryInterferenceAuditionV1, { |out=0|
    var envelope = EnvGen.ar(Env.perc(0.002, 0.16, 1, -6), doneAction: 2);
    var source = (WhiteNoise.ar(0.82) + (SinOsc.ar(220, 0, 0.34))) * envelope;
    Out.ar(out, Pan2.ar(source, -0.12));
}).add;

~qmwHmiStart = { |out=0|
    ~qmwHmiSynth !? _.free;
    ~qmwHmiSynth = Synth(\qmwHarmonicMemoryInterferenceFieldV1, [
        \out, out, \inBus, ~qmwHmiInputBus.index,
        \master, ~qmwHmiMix, \baseDelay, ~qmwHmiBaseDelaySeconds,
        \harmonicExponent, ~qmwHmiHarmonicExponent,
        \glideSeconds, ~qmwHmiGlideSeconds, \ratios, ~qmwHmiRatios
    ], s.defaultGroup, \addToTail);
};
~qmwHmiSetMixer = { |mix|
    ~qmwHmiMix = mix.asFloat.clip(0, 0.5);
    ~qmwHmiSynth !? { |synth| synth.set(\master, ~qmwHmiMix) };
};
~qmwHmiSetBaseDelay = { |seconds|
    ~qmwHmiBaseDelaySeconds = seconds.asFloat.clip(0.020, 0.090);
    ~qmwHmiSynth !? { |synth| synth.set(\baseDelay, ~qmwHmiBaseDelaySeconds) };
};
~qmwHmiSetHarmonicExponent = { |exponent|
    ~qmwHmiHarmonicExponent = exponent.asFloat.clip(0.5, 3.0);
    ~qmwHmiSynth !? { |synth| synth.set(\harmonicExponent, ~qmwHmiHarmonicExponent) };
};
~qmwHmiSetGlideSeconds = { |seconds|
    ~qmwHmiGlideSeconds = seconds.asFloat.clip(0.005, 0.5);
    ~qmwHmiSynth !? { |synth| synth.set(\glideSeconds, ~qmwHmiGlideSeconds) };
};
~qmwHmiAuditionReturn = {
    ~qmwHmiInputBus !? { |bus|
        Synth(\qmwHarmonicMemoryInterferenceAuditionV1,
            [\out, bus.index], s.defaultGroup, \addToTail)
    };
};

~qmwHmiWindow = nil;
~qmwHmiOpenPanel = {
    if(~qmwHmiWindow.notNil, { ~qmwHmiWindow.front }, {
        ~qmwHmiWindow = Window(
            "QMW Harmonic Memory Interference Field", Rect(250, 130, 720, 312)
        ).front.background_(Color.fromHexString("11151c"));
        StaticText(~qmwHmiWindow, Rect(16, 12, 688, 24))
            .string_("EIGHT-PATH HARMONIC MEMORY INTERFERENCE FIELD  /  V1")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(~qmwHmiWindow, Rect(16, 42, 688, 34))
            .string_("H(w) = sum a_k exp(-i w tau_k).  This baseline is pluck-send only: no feedback, scattering, quantum mapping, or observer oscillator bed.")
            .stringColor_(Color.white);
        EZSlider(~qmwHmiWindow, Rect(16, 88, 334, 27), "HMI return mix",
            ControlSpec(0, 0.5, \lin, 0.001), { |view| ~qmwHmiSetMixer.value(view.value) },
            ~qmwHmiMix, labelWidth: 96, numberWidth: 56);
        EZSlider(~qmwHmiWindow, Rect(370, 88, 334, 27), "pluck -> HMI send",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qriHmiSend = view.value },
            ~qriHmiSend ? 0, labelWidth: 114, numberWidth: 56);
        EZSlider(~qmwHmiWindow, Rect(16, 130, 334, 27), "base delay",
            ControlSpec(0.020, 0.090, \exp, 0.001), { |view| ~qmwHmiSetBaseDelay.value(view.value) },
            ~qmwHmiBaseDelaySeconds, labelWidth: 80, numberWidth: 56);
        EZSlider(~qmwHmiWindow, Rect(370, 130, 334, 27), "harmonic exponent r",
            ControlSpec(0.5, 3, \lin, 0.01), { |view| ~qmwHmiSetHarmonicExponent.value(view.value) },
            ~qmwHmiHarmonicExponent, labelWidth: 128, numberWidth: 56);
        EZSlider(~qmwHmiWindow, Rect(16, 172, 334, 27), "glide",
            ControlSpec(0.005, 0.5, \exp, 0.001), { |view| ~qmwHmiSetGlideSeconds.value(view.value) },
            ~qmwHmiGlideSeconds, labelWidth: 54, numberWidth: 56);
        Button(~qmwHmiWindow, Rect(370, 172, 334, 34))
            .states_([["AUDITION INTERFERENCE RETURN ONLY", Color.white, Color.fromHexString("264653")]])
            .action_({ ~qmwHmiAuditionReturn.value });
        StaticText(~qmwHmiWindow, Rect(16, 224, 688, 52))
            .string_("Start here: audition with r = 1, then sweep base delay. Raise r toward 3 to privilege early paths. The next increment adds the scattering operator S and explicit feedback g.")
            .stringColor_(Color.fromHexString("80ed99"));
        ~qmwHmiWindow.onClose = { ~qmwHmiWindow = nil };
    });
};

~qmwHmiStart.value;
"QMW Harmonic Memory Interference Field V1 ready (8 paths, pluck-send baseline)".postln;
)
