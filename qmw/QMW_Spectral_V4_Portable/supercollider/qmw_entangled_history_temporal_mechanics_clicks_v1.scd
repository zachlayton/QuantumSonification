/*
QMW entangled-history temporal mechanics: coherence-coupled clicks v1

Quantum source:
    rho_C(t,t') = (1/16) <psi_t'|psi_t>

For the default Floquet history initialized in |0000>, the conditioned system
alternates between |0000> and |1111>. Normalized clock coherence therefore
has unit magnitude within the eight even clock states and within the eight odd
clock states, and zero magnitude between the two parity communities. The
conditional phases below come directly from the tested NumPy history state.

Sonification transducer:
    d theta_i / dt = omega_i * (1 + depth * K_i)

    K_i = (1/7) sum_j Im[
        c_ij * exp(i * (theta_j - theta_i))
    ]

where c_ij is the normalized clock coherence. This is a coherence-driven
auditory readout, not a claim that Page-Wootters clocks literally obey a
Kuramoto equation. With depth = 0, all off-diagonal influence disappears and
the same synth becomes the matched dephased / fixed-period control.

Every voice retains its clock-basis identity |0000> ... |1111>, its own
10101 gate, and a 48-hit winding. Timing is integrated on the audio server at
control-block resolution rather than scheduled on a conventional tempo grid.

Controls after evaluation:
    ~qmwTemporalStart.(0.24);       // coherent history, audible deformation
    ~qmwTemporalCoupling.(0.0);     // matched dephased/fixed-period control
    ~qmwTemporalCoupling.(0.24);    // restore coherent coupling
    ~qmwTemporalStop.();
    ~qmwTemporalStatus.();

Set ~qmwTemporalOutputMode = \discrete16 before evaluation to route one
clock-basis voice per output bus. The server must have 16 output buses.
*/

(
~qmwTemporalOutputMode = ~qmwTemporalOutputMode ? \stereo;
~qmwTemporalAutoStart = ~qmwTemporalAutoStart ? true;
~qmwTemporalReferenceMs = 150.0;
~qmwTemporalBinsPerOctave = 16.0;
~qmwTemporalHitBudget = 48;
~qmwTemporalDefaultCoupling = 0.24;
~qmwTemporalSynth = nil;

// Exact phases of the occupied component of each conditioned |psi_t>.
~qmwTemporalConditionalPhases = [
    0.0,
    -2.69,
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
    1.952297150257
];

~qmwTemporalIntervalsMs = Array.fill(16, { |index|
    ~qmwTemporalReferenceMs
        * (2 ** ((index - 7.5) / ~qmwTemporalBinsPerOctave));
});

~qmwTemporalStop = {
    if(~qmwTemporalSynth.notNil) {
        ~qmwTemporalSynth.free;
        ~qmwTemporalSynth = nil;
    };
    "QMW coherence-coupled temporal mechanics stopped.".postln;
};

~qmwTemporalStatus = {
    "QMW temporal mechanics | synth: % | mode: % | coupling: %"
        .format(
            ~qmwTemporalSynth.notNil,
            ~qmwTemporalOutputMode,
            ~qmwTemporalDefaultCoupling
        ).postln;
    "clock coherence: two exact eight-state parity communities; E2 = 0.5"
        .postln;
};

s.waitForBoot {
    var phases = ~qmwTemporalConditionalPhases.copy;
    var periods = ~qmwTemporalIntervalsMs.copy;
    var outputMode = ~qmwTemporalOutputMode;

    SynthDef(\qmwTemporalMechanicsClicksStereoV1, {
        |out = 0, couplingDepth = 0.24, amplitude = 0.032|

        var previousPhases = LocalIn.kr(16, 0);
        var currentPhases = Array.newClear(16);
        var voiceSignals = Array.newClear(16);
        var initialRelease = Trig1.kr(1, ControlDur.ir);

        16.do { |voice|
            var baseCyclesPerSecond = 1000.0 / periods[voice];
            var coherenceForce = Mix(Array.fill(16, { |other|
                if((voice != other) and: {
                    (voice % 2) == (other % 2)
                }) {
                    (
                        (2pi * (previousPhases[other] - previousPhases[voice]))
                        + phases[voice]
                        - phases[other]
                    ).sin
                } {
                    0
                }
            })) / 7.0;
            var instantaneousCyclesPerSecond = baseCyclesPerSecond
                * (1 + (couplingDepth.clip(0, 0.45) * coherenceForce));
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
            var trigger = candidate * (hitCount <= ~qmwTemporalHitBudget);
            var envelope = Decay2.ar(K2A.ar(trigger), 0.0003, 0.022);
            var frequency = 480.0 * (2 ** (voice / 12.0));
            var body = SinOsc.ar(frequency, 0, 0.72);
            var edge = SinOsc.ar(frequency * 2.31, pi * 0.5, 0.28);

            currentPhases[voice] = phase;
            voiceSignals[voice] = LeakDC.ar((body + edge) * envelope * amplitude);
        };

        LocalOut.kr(currentPhases);
        Out.ar(out, Mix(Array.fill(16, { |voice|
            Pan2.ar(
                voiceSignals[voice],
                sin(2pi * voice / 16.0)
            )
        })));
        DetectSilence.ar(Mix(voiceSignals), time: 1.0, doneAction: 2);
    }).add;

    SynthDef(\qmwTemporalMechanicsClicksDiscrete16V1, {
        |out = 0, couplingDepth = 0.24, amplitude = 0.048|

        var previousPhases = LocalIn.kr(16, 0);
        var currentPhases = Array.newClear(16);
        var voiceSignals = Array.newClear(16);
        var initialRelease = Trig1.kr(1, ControlDur.ir);

        16.do { |voice|
            var baseCyclesPerSecond = 1000.0 / periods[voice];
            var coherenceForce = Mix(Array.fill(16, { |other|
                if((voice != other) and: {
                    (voice % 2) == (other % 2)
                }) {
                    (
                        (2pi * (previousPhases[other] - previousPhases[voice]))
                        + phases[voice]
                        - phases[other]
                    ).sin
                } {
                    0
                }
            })) / 7.0;
            var instantaneousCyclesPerSecond = baseCyclesPerSecond
                * (1 + (couplingDepth.clip(0, 0.45) * coherenceForce));
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
            var trigger = candidate * (hitCount <= ~qmwTemporalHitBudget);
            var envelope = Decay2.ar(K2A.ar(trigger), 0.0003, 0.022);
            var frequency = 480.0 * (2 ** (voice / 12.0));
            var body = SinOsc.ar(frequency, 0, 0.72);
            var edge = SinOsc.ar(frequency * 2.31, pi * 0.5, 0.28);

            currentPhases[voice] = phase;
            voiceSignals[voice] = LeakDC.ar((body + edge) * envelope * amplitude);
        };

        LocalOut.kr(currentPhases);
        Out.ar(out, voiceSignals);
        DetectSilence.ar(Mix(voiceSignals), time: 1.0, doneAction: 2);
    }).add;

    s.sync;

    ~qmwTemporalStart = { |coupling = 0.24|
        var synthName;
        ~qmwTemporalStop.();
        ~qmwTemporalDefaultCoupling = coupling.clip(0, 0.45);
        synthName = if(outputMode == \discrete16) {
            \qmwTemporalMechanicsClicksDiscrete16V1
        } {
            \qmwTemporalMechanicsClicksStereoV1
        };
        ~qmwTemporalSynth = Synth(synthName, [
            \out, 0,
            \couplingDepth, ~qmwTemporalDefaultCoupling
        ]);
        "QMW temporal mechanics common release | coupling %"
            .format(~qmwTemporalDefaultCoupling).postln;
    };

    ~qmwTemporalCoupling = { |depth = 0.24|
        ~qmwTemporalDefaultCoupling = depth.clip(0, 0.45);
        if(~qmwTemporalSynth.notNil) {
            ~qmwTemporalSynth.set(
                \couplingDepth,
                ~qmwTemporalDefaultCoupling
            );
        };
        "QMW temporal coupling = %"
            .format(~qmwTemporalDefaultCoupling).postln;
    };

    "QMW coherence-coupled history clock ready.".postln;
    "Use coupling 0 for the dephased control; 0.24 for the coherent history."
        .postln;
    if(~qmwTemporalAutoStart) {
        ~qmwTemporalStart.(~qmwTemporalDefaultCoupling)
    };
};
)
