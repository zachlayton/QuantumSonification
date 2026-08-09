/*
QMW exact Grover-statevector sonification for SuperCollider v1

The Python process evolves all 65,536 complex amplitudes.  This file does not
recreate Grover's analytic probability curve: it renders the exact OSC frames
measured after each oracle and diffusion operation.

Evaluate this file, then run from the project root:

    python feedback/grover_statevector_osc_v1.py --port 7494

Mapping:
    64 complex Walsh projections -> 64 persistent quadrature modes
    complex sign/phase            -> oscillator quadrature and spatial phase
    measured Grover-plane angle   -> rotation through the stereo/FDN field
    unresolved projection energy  -> geometry deformation / brightness
    FOUND                         -> freeze post-geometry spectrum and fade motion

The Tangle Cube modal frequencies below are copied from the authoritative
state_000002 surface-Laplacian packet.  Wet gain = 0.7, geometry depth = 0.7,
and wet-only ring-mod depth = 0.8.

Evaluate ~qmwGroverSCStop.() to remove responders and free audio resources.
*/

(
thisProcess.openUDPPort(7494);

s.waitForBoot {
    var modeCount = 64;
    var tangleFrequencies = [
        111.952149, 112.040920, 112.040920, 167.205124,
        167.295490, 167.295490, 222.271248, 352.987897,
        352.987897, 353.901371, 353.901371, 354.472443,
        374.425955, 375.755786, 375.755786, 384.003442,
        384.925740, 384.925740, 389.608952, 458.782840,
        459.598844, 459.624105, 460.084351, 460.084351
    ];
    var tangleDecays = [
        0.875255, 0.875012, 0.875012, 0.760604,
        0.760460, 0.760460, 0.688473, 0.585572,
        0.585572, 0.585042, 0.585042, 0.584712,
        0.573612, 0.572900, 0.572900, 0.568563,
        0.568086, 0.568086, 0.565687, 0.534236,
        0.533904, 0.533894, 0.533707, 0.533707
    ];

    SynthDef(\qmwGroverWalsh64V1, {
        |out = 0, probability = 0, rotation = 0, relativePhase = 0,
        residual = 0, slew = 0.04, master = 0.82|

        var real = NamedControl.kr(\coeffReal, Array.fill(64, 0.0));
        var imag = NamedControl.kr(\coeffImag, Array.fill(64, 0.0));
        var smoothReal = VarLag.kr(real, slew.max(0.002), 0, \sin);
        var smoothImag = VarLag.kr(imag, slew.max(0.002), 0, \sin);
        var energy = (smoothReal.squared + smoothImag.squared).sum.sqrt.max(0.000001);
        var confidenceGain = 0.75 + (0.25 * probability.clip(0, 1).sqrt);
        var rot = VarLag.kr(rotation, slew.max(0.002), 0, \sin);
        var phaseControl = VarLag.kr(relativePhase, slew.max(0.002), 0, \sin);
        var stereo;

        // Re(a * exp(iwt)) = real(a) cos(wt) - imag(a) sin(wt).
        // Slewing the two Cartesian components prevents discontinuities when
        // the oracle reverses a coefficient's phase by pi.
        stereo = Mix.fill(64, { |index|
            var frequency = 42 * (2 ** (index / 12));
            var coefficient = (
                (SinOsc.ar(frequency, pi * 0.5) * smoothReal[index])
                - (SinOsc.ar(frequency, 0) * smoothImag[index])
            ) / energy;
            var coefficientPhase = smoothImag[index].atan2(smoothReal[index]);
            var pan = sin(
                (2pi * index / 64) + (2 * rot) + coefficientPhase + (0.2 * phaseControl)
            ) * 0.92;
            Pan2.ar(coefficient * 0.14 * confidenceGain, pan);
        });

        stereo = LeakDC.ar(stereo * master);
        Out.ar(out, stereo);
    }).add;

    SynthDef(\qmwGroverTangleHoldV1, {
        |inBus = 0, out = 0, probability = 0, rotation = 0,
        relativePhase = 0, residual = 0, freeze = 0,
        wetGain = 0.7, dryGain = 0.3, geometryDepth = 0.7,
        ringDepth = 0.8, master = 0.9|

        var input = In.ar(inBus, 2);
        var mono = input.sum * 0.5;
        var rot = VarLag.kr(rotation, 0.09, 0, \sin);
        var phaseControl = VarLag.kr(relativePhase, 0.09, 0, \sin);
        var deformation = VarLag.kr(residual.clip(0, 1), 0.12, 0, \sin);
        var confidence = VarLag.kr(probability.clip(0, 1), 0.09, 0, \sin);
        var modal;
        var fdn;
        var ringFrequency;
        var ringCarrier;
        var movingWet;
        var frozenWet;
        var freezeLag;
        var output;

        // Literal state controls deform the fixed, measured Tangle Cube modal
        // packet. No independent LFO advances the geometry.
        modal = Mix.fill(24, { |index|
            var ratio = 1 + (
                geometryDepth * 0.18
                * sin((rot * (index + 1)) + phaseControl + (index * 0.73))
            );
            Ringz.ar(
                mono * (0.018 + (0.018 * deformation)),
                (tangleFrequencies[index] * ratio).clip(35, 9000),
                tangleDecays[index] * confidence.linlin(0, 1, 0.7, 2.4)
            )
        }) / 24.sqrt;

        // Eight geometry-dependent allpass paths form a compact FDN-like
        // chamber. Rotation changes path length and stereo orientation.
        fdn = Mix.fill(8, { |index|
            var baseDelay = [0.0173, 0.0211, 0.0269, 0.0317,
                0.0379, 0.0433, 0.0511, 0.0617][index];
            var pathScale = 1 + (
                geometryDepth * 0.42
                * sin(rot * (index + 1.37) + phaseControl + (index * 0.91))
            );
            var delay = (baseDelay * pathScale).clip(0.003, 0.11);
            var path = AllpassC.ar(
                mono + (modal * 0.12),
                0.12,
                delay,
                confidence.linlin(0, 1, 0.65, 3.8)
            );
            Pan2.ar(path, sin((index * 0.83) + (rot * 2)) * 0.88)
        }) / 8.sqrt;

        ringFrequency = (
            1.5 + (38 * (rot / (pi * 0.5)).clip(0, 1))
            + (6 * phaseControl.abs / pi)
        );
        ringCarrier = (1 - ringDepth) + (ringDepth * SinOsc.ar(ringFrequency));
        movingWet = (fdn + Pan2.ar(modal * 0.45, sin(rot * 2))) * ringCarrier;
        movingWet = LeakDC.ar(movingWet.tanh);

        // Freeze the spectrum only after geometry, modal resonance, and ring
        // modulation. The dry/moving path simultaneously fades away, leaving
        // a stable resonant structure instead of a stopped or silent process.
        frozenWet = [
            IFFT(PV_MagFreeze(FFT(LocalBuf(2048), movingWet[0]), freeze)),
            IFFT(PV_MagFreeze(FFT(LocalBuf(2048), movingWet[1]), freeze))
        ];
        freezeLag = Lag.kr(freeze.clip(0, 1), 0.7);
        output = (input * dryGain * (1 - freezeLag))
            + (XFade2.ar(movingWet, frozenWet, (freezeLag * 2) - 1) * wetGain);
        output = LeakDC.ar(output);
        output = Limiter.ar((output * master).tanh, 0.9, 0.01);
        Out.ar(out, output);
    }).add;

    s.sync;

    ~qmwGroverSCBus = Bus.audio(s, 2);
    ~qmwGroverSCSource = Synth(\qmwGroverWalsh64V1, [\out, ~qmwGroverSCBus]);
    ~qmwGroverSCFX = Synth.after(
        ~qmwGroverSCSource,
        \qmwGroverTangleHoldV1,
        [\inBus, ~qmwGroverSCBus, \out, 0]
    );
    ~qmwGroverSCState = "WAITING";
    ~qmwGroverSCFrame = 0;

    OSCdef(\qmwGroverSCFrame, { |message|
        var iteration = message[1].asInteger;
        var operator = message[2].asInteger;
        var probability = message[3].asFloat.clip(0, 1);
        var rotation = message[4].asFloat;
        var relativePhase = message[5].asFloat;
        var norm = message[6].asFloat;
        var residual = message[8].asFloat.clip(0, 1);

        ~qmwGroverSCFrame = iteration;
        ~qmwGroverSCSource.set(
            \probability, probability,
            \rotation, rotation,
            \relativePhase, relativePhase,
            \residual, residual
        );
        ~qmwGroverSCFX.set(
            \probability, probability,
            \rotation, rotation,
            \relativePhase, relativePhase,
            \residual, residual
        );
        if((operator == 2) and: { (iteration % 20) == 0 }) {
            "Grover k=% | p=% | norm=%"
                .format(iteration, probability.round(0.000000001), norm.round(0.0000001))
                .postln;
        };
    }, '/qmw/grover/statevector/frame', nil, 7494);

    OSCdef(\qmwGroverSCModes, { |message|
        var real = Array.fill(64, { |index| message[3 + (index * 2)].asFloat });
        var imag = Array.fill(64, { |index| message[4 + (index * 2)].asFloat });
        ~qmwGroverSCSource.setn(\coeffReal, real);
        ~qmwGroverSCSource.setn(\coeffImag, imag);
    }, '/qmw/grover/statevector/modes', nil, 7494);

    OSCdef(\qmwGroverSCFound, { |message|
        var iteration = message[1].asInteger;
        var probability = message[2].asFloat;
        ~qmwGroverSCFX.set(\freeze, 1);
        "FOUND -> STABILIZING | k=% | exact p=%"
            .format(iteration, probability.round(0.000000001)).postln;
    }, '/qmw/grover/statevector/found', nil, 7494);

    OSCdef(\qmwGroverSCState, { |message|
        ~qmwGroverSCState = message[1].asString;
        if(~qmwGroverSCState == "SEARCHING") {
            ~qmwGroverSCFX.set(\freeze, 0)
        };
        ("Grover state: " ++ ~qmwGroverSCState).postln;
    }, '/qmw/grover/statevector/state', nil, 7494);

    ~qmwGroverSCStop = {
        [
            \qmwGroverSCFrame,
            \qmwGroverSCModes,
            \qmwGroverSCFound,
            \qmwGroverSCState
        ].do { |name| OSCdef(name).free };
        ~qmwGroverSCSource.free;
        ~qmwGroverSCFX.free;
        ~qmwGroverSCBus.free;
        thisProcess.closeUDPPort(7494);
        "QMW Grover statevector sonification stopped.".postln;
    };

    "QMW Grover statevector sonification ready on dedicated UDP 7494.".postln;
    "Run: python feedback/grover_statevector_osc_v1.py --port 7494".postln;
};
)
