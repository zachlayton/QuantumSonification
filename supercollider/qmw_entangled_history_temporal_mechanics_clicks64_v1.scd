/*
QMW entangled-history temporal mechanics: 64 coherence-coupled clicks v1

Six clock qubits provide 64 clock states; the existing four-qubit Floquet
system provides 16 system states, giving a 1024-amplitude pure history.

For the default Floquet history initialized in |0000>, the exact normalized
clock coherence forms two 32-state communities. Even clock states overlap the
other evens with unit magnitude, odds overlap the other odds, and even/odd
overlaps vanish. Within a community the coherence factorizes as

    c_ij = exp(i * (conditionalPhase_i - conditionalPhase_j)).

The complete 64x64 interaction is therefore evaluated exactly through two
complex mean fields rather than 4096 explicit pairwise couplers.

The quantum history supplies the coherence. The coherence-to-rate equation is
the declared auditory transducer, not an added law of Page-Wootters dynamics.

Controls:
    ~qmwTemporal64Start.(0.20, 2); // coherent, two octave layers
    ~qmwTemporal64Start.(0.0, 1);  // dephased, single-layer control
    ~qmwTemporal64Coupling.(0.20);
    ~qmwTemporal64Stop.();
    ~qmwTemporal64Status.();

The two exact coherence communities compile as synchronized 32-voice synths
and are mixed to stereo. This avoids an oversized monolithic server graph.
*/

(
~qmwTemporal64AutoStart = ~qmwTemporal64AutoStart ? true;
~qmwTemporal64ReferenceMs = 150.0;
~qmwTemporal64BinsPerOctave = 64.0;
~qmwTemporal64HitBudget = 48;
~qmwTemporal64DefaultCoupling = 0.20;
~qmwTemporal64DefaultLayers = 2;
~qmwTemporal64ParityPan = 0.32;
~qmwTemporal64Synths = Array.newClear(8);

// Exact occupied-component phases from the 64-branch NumPy history.
~qmwTemporal64ConditionalPhases = [
    0.000000000000,
    -2.690000000000,
    0.663185307180,
    -2.026814692820,
    1.326370614359,
    -1.363629385641,
    1.989555921539,
    -0.700444078461,
    2.652741228718,
    -0.037258771282,
    -2.967258771282,
    0.625926535898,
    -2.304073464102,
    1.289111843078,
    -1.640888156922,
    1.952297150257,
    -0.977702849743,
    2.615482457437,
    -0.314517542563,
    -3.004517542563,
    0.348667764616,
    -2.341332235384,
    1.011853071796,
    -1.678146928204,
    1.675038378975,
    -1.014961621025,
    2.338223686155,
    -0.351776313845,
    3.001408993335,
    0.311408993335,
    -2.618591006665,
    0.974594300514,
    -1.955405699486,
    1.637779607694,
    -1.292220392306,
    2.300964914873,
    -0.629035085127,
    2.964150222053,
    0.034150222053,
    -2.655849777947,
    0.697335529233,
    -1.992664470767,
    1.360520836412,
    -1.329479163588,
    2.023706143592,
    -0.666293856408,
    2.686891450771,
    -0.003108549229,
    -2.933108549229,
    0.660076757951,
    -2.269923242049,
    1.323262065131,
    -1.606737934869,
    1.986447372310,
    -0.943552627690,
    2.649632679490,
    -0.280367320510,
    -2.970367320510,
    0.382817986669,
    -2.307182013331,
    1.046003293849,
    -1.643996706151,
    1.709188601028,
    -0.980811398972
];

// This keeps an approximately 2:1 period span across all 64 voices.
~qmwTemporal64IntervalsMs = Array.fill(64, { |index|
    ~qmwTemporal64ReferenceMs
        * (2 ** ((index - 31.5) / ~qmwTemporal64BinsPerOctave));
});

~qmwTemporal64Stop = {
    ~qmwTemporal64Synths.do { |synth|
        if(synth.notNil) { synth.free };
    };
    ~qmwTemporal64Synths = Array.newClear(8);
    "QMW 64-clock temporal mechanics stopped.".postln;
};

~qmwTemporal64Status = {
    "QMW temporal64 | synths: % | layers: % | coupling: %"
        .format(
            ~qmwTemporal64Synths.select(_.notNil).size,
            ~qmwTemporal64DefaultLayers,
            ~qmwTemporal64DefaultCoupling
        ).postln;
    "64 clock states | 1024 joint amplitudes | purity 0.5 | E2 0.5"
        .postln;
    "two exact 32-state parity-coherence communities".postln;
};

s.waitForBoot {
    var phases = ~qmwTemporal64ConditionalPhases.copy;
    var periods = ~qmwTemporal64IntervalsMs.copy;
    var buildSynth;

    buildSynth = { |name, parity = 0|
        var indices = Array.fill(32, { |index| (index * 2) + parity });
        var communityPhases = indices.collect { |index| phases[index] };
        var communityPeriods = indices.collect { |index| periods[index] };

        SynthDef(name, {
            |out = 0, couplingDepth = 0.20, amplitude = 0.014,
            octaveShift = 0, parityPan = 0.32|

            var previousPhases = LocalIn.kr(32, 0);
            var transformed = Array.fill(32, { |localVoice|
                (2pi * previousPhases[localVoice])
                    - communityPhases[localVoice]
            });
            var transformedSin = transformed.collect(_.sin);
            var transformedCos = transformed.collect(_.cos);
            var groupSin = Mix(transformedSin);
            var groupCos = Mix(transformedCos);
            var currentPhases = Array.newClear(32);
            var voiceSignals = Array.newClear(32);
            var initialRelease = Trig1.kr(1, ControlDur.ir);

            32.do { |localVoice|
                var voice = indices[localVoice];
                var x = transformed[localVoice];
                // Self contributes exactly zero; /31 averages the other nodes.
                var coherenceForce = (
                    (groupSin * x.cos) - (groupCos * x.sin)
                ) / 31.0;
                var baseCyclesPerSecond =
                    1000.0 / communityPeriods[localVoice];
                var instantaneousCyclesPerSecond = baseCyclesPerSecond
                    * (1 + (
                        couplingDepth.clip(0, 0.40) * coherenceForce
                    ));
                var phase = Phasor.kr(
                    0,
                    instantaneousCyclesPerSecond * ControlDur.ir,
                    0,
                    1,
                    0
                );
                var wrapTrigger = HPZ1.kr(phase) < 0;
                var cell = PulseCount.kr(wrapTrigger);
                var bit = Select.kr(cell % 5, [1, 0, 1, 0, 1]);
                var candidate = Trig1.kr(
                    ((wrapTrigger + initialRelease).clip(0, 1)) * bit,
                    ControlDur.ir
                );
                var hitCount = PulseCount.kr(candidate);
                var trigger = candidate * (hitCount <= ~qmwTemporal64HitBudget);
                var envelope = Decay2.ar(K2A.ar(trigger), 0.00025, 0.018);
                var frequency = 220.0
                    * (2 ** (voice / 24.0))
                    * (2 ** octaveShift);
                var body = SinOsc.ar(frequency, 0, 0.74);
                var edgeRatio = 2.27 + (0.08 * (voice % 2));
                var edge = SinOsc.ar(
                    frequency * edgeRatio,
                    pi * 0.5,
                    0.26
                );

                currentPhases[localVoice] = phase;
                voiceSignals[localVoice] = LeakDC.ar(
                    (body + edge) * envelope * amplitude
                );
            };

            LocalOut.kr(currentPhases);
            Out.ar(out, Mix(Array.fill(32, { |localVoice|
                    var voice = indices[localVoice];
                    var communityOffset = if(parity == 0) {
                        parityPan.neg
                    } {
                        parityPan
                    };
                    var pan = (
                        (sin(2pi * voice / 64.0) * 0.62)
                        + communityOffset
                    ).clip(-1, 1);
                    Pan2.ar(
                        voiceSignals[localVoice],
                        pan
                    )
                })));
            DetectSilence.ar(Mix(voiceSignals), time: 1.0, doneAction: 2);
        }).add;
    };

    buildSynth.(\qmwTemporalMechanicsClicks64EvenV1, 0);
    buildSynth.(\qmwTemporalMechanicsClicks64OddV1, 1);
    s.sync;

    ~qmwTemporal64Start = { |coupling = 0.20, layers = 2|
        var octaveOffsets = [0, 1, -1, 2];
        var layerAmplitude;
        var newSynths;
        ~qmwTemporal64Stop.();
        ~qmwTemporal64DefaultCoupling = coupling.clip(0, 0.40);
        ~qmwTemporal64DefaultLayers = layers.asInteger.clip(1, 4);
        layerAmplitude = 0.014 / ~qmwTemporal64DefaultLayers.sqrt;
        newSynths = List.new;
        // One OSC bundle gives every octave layer and community a common release.
        s.bind {
            ~qmwTemporal64DefaultLayers.do { |layer|
                newSynths.add(Synth(
                    \qmwTemporalMechanicsClicks64EvenV1,
                    [
                        \out, 0,
                        \couplingDepth, ~qmwTemporal64DefaultCoupling,
                        \octaveShift, octaveOffsets[layer],
                        \parityPan, ~qmwTemporal64ParityPan,
                        \amplitude, layerAmplitude
                    ]
                ));
                newSynths.add(Synth(
                    \qmwTemporalMechanicsClicks64OddV1,
                    [
                        \out, 0,
                        \couplingDepth, ~qmwTemporal64DefaultCoupling,
                        \octaveShift, octaveOffsets[layer],
                        \parityPan, ~qmwTemporal64ParityPan,
                        \amplitude, layerAmplitude
                    ]
                ));
            };
            ~qmwTemporal64Synths = newSynths.asArray;
        };
        "QMW 64-clock release | coupling % | octave layers %"
            .format(
                ~qmwTemporal64DefaultCoupling,
                ~qmwTemporal64DefaultLayers
            ).postln;
    };

    ~qmwTemporal64Coupling = { |depth = 0.20|
        ~qmwTemporal64DefaultCoupling = depth.clip(0, 0.40);
        ~qmwTemporal64Synths.do { |synth|
            if(synth.notNil) {
                synth.set(
                    \couplingDepth,
                    ~qmwTemporal64DefaultCoupling
                )
            };
        };
        "QMW temporal64 coupling = %"
            .format(~qmwTemporal64DefaultCoupling).postln;
    };

    "QMW coherence-coupled 64-state history clock ready.".postln;
    "Use coupling 0 for dephased control; 0.20 for coherent history."
        .postln;
    if(~qmwTemporal64AutoStart) {
        ~qmwTemporal64Start.(
            ~qmwTemporal64DefaultCoupling,
            ~qmwTemporal64DefaultLayers
        )
    };
};
)
