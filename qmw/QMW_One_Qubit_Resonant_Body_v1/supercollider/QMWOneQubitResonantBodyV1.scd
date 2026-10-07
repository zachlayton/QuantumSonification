/*
QMW One-Qubit Resonant Body V1
================================

One downstream acoustic body. It receives complete, revisioned observer
frames on /qmw/one_qubit/v1/frame and never sends anything upstream.

The probe burst and modal decay are sound design, not decoherence. T1 and
Tphi are applied only by the Python density-matrix engine. Signed weights are
monopole/dipole/quadrupole observation coefficients; they are not amplitudes
or probabilities. There are no carrier oscillators and no detuned chord: one
band-limited probe excites a stateful nine-mode Ringz bank.
*/

(
var makeInstrument, removeInstrument, modeCount = 9;

~qmw1QCleanup !? { ~qmw1QCleanup.value };
~qmw1QPort = ~qmw1QPort ? 57120;
~qmw1QLatestRevision = -1;
~qmw1QBody = nil;

removeInstrument = {
    OSCdef(\qmwOneQubitFrameV1).free;
    ~qmw1QBody !? _.free;
    ~qmw1QBody = nil;
    "QMW_ONE_QUBIT_BODY_STOPPED".postln;
};

makeInstrument = {
    SynthDef(\qmwOneQubitResonantBodyV1, {
        |out=0, soundLocked=0, master=0, probeRate=3, brightness=0.55|
        var frequencies = NamedControl.kr(\frequencies, Array.fill(modeCount, 110));
        var decays = NamedControl.kr(\decays, Array.fill(modeCount, 0.8));
        var weights = NamedControl.kr(\weights, [1, 0, 0, 0, 0, 0, 0, 0, 0]);
        var trigger, envelope, cutoff, probe, modes, left, right, gate;
        // Fixed seed makes repeated launches comparable. This acoustic noise
        // is merely the virtual probe striking the body.
        RandSeed.ir(1, 1979);
        trigger = Impulse.ar(Lag.kr(probeRate.clip(0.25, 16), 0.08));
        envelope = Decay2.ar(trigger, 0.0008, 0.020);
        cutoff = brightness.clip(0, 1).linexp(0, 1, 450, 12500);
        probe = LPF.ar(HPF.ar(WhiteNoise.ar(0.34), 55), cutoff) * envelope;
        modes = Ringz.ar(
            probe,
            Lag.kr(frequencies.clip(30, 18000), 0.06),
            Lag.kr(decays.clip(0.04, 5), 0.08)
        ) * Lag.kr(weights.clip(-1, 1), 0.045);
        // Two fixed virtual pickups observe the same body. This is ordinary
        // stereo and a declared perceptual projection, not quantum space.
        left = Mix(modes * [0.82, 1.0, 0.38, 0.74, -0.48, 0.64, -0.31, 0.53, 0.27]);
        right = Mix(modes * [0.82, 0.38, 1.0, 0.74, 0.48, -0.31, 0.64, 0.27, 0.53]);
        // soundLocked=1 is a hard mute. Clearing the lock permits the
        // downstream master gain to open; neither control reaches Python.
        gate = Lag.kr((1 - soundLocked.clip(0, 1)) * master.clip(0, 1), 0.035);
        Out.ar(out, Limiter.ar(LeakDC.ar([left, right]).tanh * gate, 0.92, 0.01));
    }).add;
    s.sync;

    ~qmw1QBody = Synth.tail(s.defaultGroup, \qmwOneQubitResonantBodyV1, [
        \soundLocked, 0, \master, 0
    ]);
    thisProcess.openUDPPort(~qmw1QPort);

    OSCdef(\qmwOneQubitFrameV1, { |message|
        // address + 20 scalar arguments + 9 frequency/decay/weight triples.
        if(message.size != 48, {
            "QMW one-qubit: rejected incomplete frame".warn;
        }, {
            var revision = message[1].asInteger;
            if(revision > ~qmw1QLatestRevision, {
                var frequencies = Array.fill(modeCount, { |index| message[21 + (index * 3)].asFloat });
                var decays = Array.fill(modeCount, { |index| message[22 + (index * 3)].asFloat });
                var weights = Array.fill(modeCount, { |index| message[23 + (index * 3)].asFloat });
                ~qmw1QLatestRevision = revision;
                ~qmw1QBody.set(
                    \soundLocked, message[16].asFloat.clip(0, 1),
                    \master, message[17].asFloat.clip(0, 1),
                    \probeRate, message[18].asFloat.clip(0.25, 16),
                    \brightness, message[19].asFloat.clip(0, 1)
                );
                ~qmw1QBody.setn(\frequencies, frequencies);
                ~qmw1QBody.setn(\decays, decays);
                ~qmw1QBody.setn(\weights, weights);
            });
        });
    }, '/qmw/one_qubit/v1/frame', recvPort: ~qmw1QPort);

    ~qmw1QSelfTest = {
        var northWeights = [0, 0, 0, 0.74161985, 0, 0, 0, 0, 0.67082039];
        if(northWeights.squared.sum.round(0.0001) != 1.0, {
            Error("one-qubit modal normalization self-test failed").throw;
        });
        if(~qmw1QBody.isNil, {
            Error("one-qubit resonant body was not created").throw;
        });
        "QMW_ONE_QUBIT_SC_SELF_TEST_OK".postln;
    };
    ~qmw1QCleanup = removeInstrument;
    ~qmw1QSelfTest.value;
    "QMW one-qubit body listening on UDP %; audio remains gated by SOUND LOCK and master.".format(~qmw1QPort).postln;
};

s.waitForBoot({ makeInstrument.value });
s.boot;
)
