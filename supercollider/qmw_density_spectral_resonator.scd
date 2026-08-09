/*
QMW density-field spectral resonator for SuperCollider

This is the native SuperCollider counterpart of
max/patches/qmw_density_field_quantum_resonator16.genexpr. The Python QMW
engine remains the authoritative four-qubit density/Hamiltonian solver and
mirrors its qmw-osc-v1 stream here. SuperCollider renders four related voices,
each driven by the same sixteen density-field probes and Hamiltonian gap ratios.

Evaluate the whole file after booting SuperCollider, then start the engine with:

    python quantumsonification_engine.py --sc-osc-port 57120

When running the implementation directly, use:

    python quantum_population_osc_v9_resonator.py --sc-osc-port 57120

The normal Max stream on port 7400 remains active. Evaluate ~qmwSCStop.() to
free the synths and OSC responders.
*/

(
var scriptPath = thisProcess.nowExecutingPath;
var scriptDirectory = if(scriptPath.isNil) {
    // Region evaluation in some IDE versions does not expose a source path.
    "/Users/zlayton/QuantumSonification/supercollider"
} {
    scriptPath.dirname
};

s.waitForBoot {
    var voiceFrequencies = [55, 82.5, 110, 165];

    ~qmwMagnitudes = Array.fill(16, 0.0);
    ~qmwPhases = Array.fill(16, 0.0);
    ~qmwSpeeds = Array.fill(16, 0.0);
    ~qmwHarmonics = (1..16).collect(_.asFloat);
    ~qmwPurity = 1.0;
    ~qmwEntropy = 0.0;
    ~qmwCoherence = 0.0;

    SynthDef(\qmwDensitySpectralResonator16, {
        |out = 0, baseFreq = 55, amp = 0.22, gate = 1,
        attackMs = 12, slowDecayMs = 900, fastDecayMs = 70,
        phaseSmoothMs = 100, partialTriggerThreshold = 0.0005,
        brightness = 0.65, mixVoices = 4, outputCeiling = 0.85,
        densityGain = 3, purity = 1, entropy = 0, coherence = 0,
        pan = 0, spread = 0.8, t_forceTrigger = 0|

        var magnitudes = NamedControl.kr(\magnitude, Array.fill(16, 0.0));
        var phases = NamedControl.kr(\phase, Array.fill(16, 0.0));
        var speeds = NamedControl.kr(\speed, Array.fill(16, 0.0));
        var harmonics = NamedControl.kr(\harmonic, (1..16));
        var pur = purity.clip(0, 1);
        var ent = entropy.clip(0, 1);
        var coh = coherence.clip(0, 1);
        var scaledMagnitude;
        var smoothedPhase;
        var excitationShape;
        var targets;
        var magnitudeMovement;
        var triggers;
        var eventLevels;
        var normalizedSpeed;
        var attackSeconds;
        var decaySeconds;
        var envelopes;
        var bright;
        var frequencies;
        var partials;
        var voiceScale;
        var signal;
        var masterEnvelope;

        scaledMagnitude = (magnitudes * densityGain).clip(0, 1);
        smoothedPhase = Lag.kr(
            phases,
            phaseSmoothMs.max(0.1) * 0.001
        );

        // Every density lane owns a separate transient envelope. HPZ1 sees a
        // one-control-block impulse whenever that lane receives a changed
        // magnitude. The level is latched at the event, while its scanner
        // speed independently determines attack and decay time.
        excitationShape = pur.linlin(0, 1, 0.55, 1.6);
        targets = (scaledMagnitude + 0.00001).pow(excitationShape)
            * ent.linlin(0, 1, 0.35, 1.0);
        magnitudeMovement = HPZ1.kr(magnitudes).abs;
        triggers = Trig1.kr(
            (magnitudeMovement > partialTriggerThreshold.max(0.000001))
                + t_forceTrigger,
            ControlDur.ir
        );
        eventLevels = Latch.kr(targets, triggers);
        normalizedSpeed = speeds.abs.clip(0, 1);
        attackSeconds = attackMs
            * coh.linlin(0, 1, 1.35, 0.65)
            * normalizedSpeed.linlin(0, 1, 1.25, 0.7)
            * 0.001;
        decaySeconds = normalizedSpeed.linlin(
            0, 1, slowDecayMs, fastDecayMs
        ) * 0.001;
        envelopes = Decay2.kr(
            triggers,
            attackSeconds.max(0.0001),
            decaySeconds.max(0.0001)
        ) * eventLevels;

        bright = (brightness + (ent * 0.25)).clip(0, 1);
        frequencies = (baseFreq * harmonics.max(0.01)).clip(
            20,
            SampleRate.ir * 0.45
        );
        partials = SinOsc.ar(frequencies, smoothedPhase)
            * envelopes
            / harmonics.max(1).pow(bright);

        voiceScale = mixVoices.max(1).sqrt.reciprocal;
        // Gen~ sums all modes before its four-voice compensation. Disable
        // Splay's additional sqrt(16) level compensation to match that gain
        // structure while retaining stereo distribution.
        signal = Splay.ar(
            partials,
            spread.clip(0, 1),
            1,
            pan.clip(-1, 1),
            false
        );
        signal = (signal * 0.5).tanh * amp * outputCeiling * voiceScale;
        signal = LeakDC.ar(signal);
        signal = Limiter.ar(signal, outputCeiling.clip(0.05, 1), 0.01);
        masterEnvelope = EnvGen.kr(
            Env.asr(0.03, 1, 0.25),
            gate,
            doneAction: Done.freeSelf
        );
        Out.ar(out, signal * masterEnvelope);
    }).add;

    SynthDef(\qmwResonatorDryOutput, {
        |inBus = 0, out = 0, dry = 0.72, master = 0.9, fadeTime = 0.1|
        var input = In.ar(inBus, 2);
        var level = VarLag.kr(dry.clip(0, 1), fadeTime.max(0.001));
        Out.ar(out, Limiter.ar(input * level * master, 0.95, 0.01));
    }).add;

    SynthDef(\qmwLivingPartConvStereo, {
        |inBus = 0, out = 0, irLeft = 0, irRight = 0,
        wet = 0, wetLevel = 0.3, fadeTime = 0.25, master = 0.9|
        var input = In.ar(inBus, 2).sum * 0.5;
        var fade = VarLag.kr(
            wet.clip(0, 1), fadeTime.max(0.001), 0, \sin
        );
        var convolved = [
            PartConv.ar(input, 2048, irLeft),
            PartConv.ar(input, 2048, irRight)
        ];
        convolved = LeakDC.ar(convolved);
        convolved = (convolved * 0.22).tanh;
        convolved = Limiter.ar(convolved, 0.92, 0.02);
        Out.ar(out, convolved * fade * wetLevel * master);
    }).add;

    s.sync;

    ~qmwSCSourceBus = Bus.audio(s, 2);
    ~qmwSCSourceGroup = Group.head(s);
    ~qmwSCFXGroup = Group.after(~qmwSCSourceGroup);

    ~qmwSCSynths = voiceFrequencies.collect { |frequency, index|
        Synth.head(~qmwSCSourceGroup, \qmwDensitySpectralResonator16, [
            \out, ~qmwSCSourceBus,
            \baseFreq, frequency,
            \pan, index.linlin(0, 3, -0.72, 0.72),
            \magnitude, ~qmwMagnitudes,
            \phase, ~qmwPhases,
            \speed, ~qmwSpeeds,
            \harmonic, ~qmwHarmonics
        ])
    };
    // Preserve the locally chosen event sensitivity.
    ~qmwSCSynths.do { |synth|
        synth.set(\partialTriggerThreshold, 0.02)
    };

    ~qmwSCDrySynth = Synth.tail(~qmwSCFXGroup, \qmwResonatorDryOutput, [
        \inBus, ~qmwSCSourceBus, \out, 0
    ]);

    ~qmwIRFFTSize = 2048;
    ~qmwIRWetLevel = 0.3;
    ~qmwIRAckAddress = NetAddr("127.0.0.1", 7461);
    ~qmwIRPending = nil;
    ~qmwIRActive = nil;
    ~qmwIRManualRevision = 1000000;
    thisProcess.interpreter.executeFile(
        scriptDirectory +/+ "qmw_living_partconv_support.scd"
    );

    ~qmwSCFrameCount = 0;
    ~qmwSCLastFrameTime = nil;

    ~qmwSCSetVector = { |control, values|
        ~qmwSCSynths.do { |synth| synth.setn(control, values) };
    };

    ~qmwSCTake16 = { |message, defaults|
        Array.fill(16, { |index|
            if(message.size > (index + 1)) {
                message[index + 1].asFloat
            } {
                defaults[index]
            }
        })
    };

    OSCdef(\qmwSCMagnitude, { |message|
        ~qmwMagnitudes = ~qmwSCTake16.(message, ~qmwMagnitudes);
        ~qmwSCSetVector.(\magnitude, ~qmwMagnitudes);
        ~qmwSCFrameCount = ~qmwSCFrameCount + 1;
        ~qmwSCLastFrameTime = Main.elapsedTime;
        if(~qmwSCFrameCount == 1) {
            "QMW first density frame received; peak magnitude: %"
                .format(~qmwMagnitudes.maxItem.round(0.0001)).postln;
        };
    }, '/qmw/density_field/magnitude');

    OSCdef(\qmwSCPhase, { |message|
        ~qmwPhases = ~qmwSCTake16.(message, ~qmwPhases);
        ~qmwSCSetVector.(\phase, ~qmwPhases);
    }, '/qmw/density_field/phase');

    OSCdef(\qmwSCSpeed, { |message|
        ~qmwSpeeds = ~qmwSCTake16.(message, ~qmwSpeeds);
        ~qmwSCSetVector.(\speed, ~qmwSpeeds);
    }, '/qmw/density_field/speed');

    OSCdef(\qmwSCHarmonics, { |message|
        ~qmwHarmonics = ~qmwSCTake16.(message, ~qmwHarmonics);
        ~qmwSCSetVector.(\harmonic, ~qmwHarmonics);
    }, '/qmw/density_field/harmonics');

    OSCdef(\qmwSCPurity, { |message|
        ~qmwPurity = message[1].asFloat;
        ~qmwSCSynths.do { |synth| synth.set(\purity, ~qmwPurity) };
    }, '/qmw/density_field/purity');

    OSCdef(\qmwSCEntropy, { |message|
        ~qmwEntropy = message[1].asFloat;
        ~qmwSCSynths.do { |synth| synth.set(\entropy, ~qmwEntropy) };
    }, '/qmw/density_field/entropy');

    OSCdef(\qmwSCCoherence, { |message|
        ~qmwCoherence = message[1].asFloat;
        ~qmwSCSynths.do { |synth| synth.set(\coherence, ~qmwCoherence) };
    }, '/qmw/density_field/coherence');

    OSCdef(\qmwSCIdentity, { |message|
        "QMW engine: %".format(message[1]).postln;
    }, '/qmw/system/engine/implementation');

    // This tone does not depend on Python or OSC. If it is silent, inspect
    // SuperCollider's output device/server volume rather than the QMW ports.
    ~qmwSCTest = {
        var testSynth;
        "QMW audio self-test: two-second resonator tone...".postln;
        testSynth = Synth(\qmwDensitySpectralResonator16, [
            \baseFreq, 82.5,
            \amp, 0.32,
            \densityGain, 1,
            \purity, 0.65,
            \entropy, 0.55,
            \coherence, 0.5,
            \mixVoices, 1,
            \t_forceTrigger, 1,
            \magnitude, Array.fill(16, 0.55),
            \phase, Array.fill(16, 0.0),
            \speed, Array.fill(16, 0.35),
            \harmonic, (1..16)
        ]);
        SystemClock.sched(2.0, {
            testSynth.set(\gate, 0);
            nil
        });
    };

    ~qmwSCStatus = {
        var age;
        age = if(~qmwSCLastFrameTime.isNil) {
            "never"
        } {
            (Main.elapsedTime - ~qmwSCLastFrameTime).round(0.01)
        };
        "QMW status: frames=%, age=% sec, peak=%, synths=%, IR=%"
            .format(
                ~qmwSCFrameCount,
                age,
                ~qmwMagnitudes.maxItem.round(0.0001),
                ~qmwSCSynths.size,
                if(~qmwIRActive.isNil) {
                    "none"
                } {
                    ~qmwIRActive[\revision]
                }
            ).postln;
        s.queryAllNodes;
    };

    ~qmwSCExcite = {
        ~qmwSCSynths.do { |synth| synth.set(\t_forceTrigger, 1) };
    };

    ~qmwSCStop = {
        [
            \qmwSCMagnitude, \qmwSCPhase, \qmwSCSpeed,
            \qmwSCHarmonics, \qmwSCPurity, \qmwSCEntropy,
            \qmwSCCoherence, \qmwSCIdentity
        ].do { |name| OSCdef(name).free };
        if(~qmwSCSynths.notNil) {
            ~qmwSCSynths.do { |synth| synth.set(\gate, 0) };
        };
        if(~qmwIRStop.notNil) { ~qmwIRStop.() };
        if(~qmwSCDrySynth.notNil) { ~qmwSCDrySynth.free };
        if(~qmwSCSourceGroup.notNil) { ~qmwSCSourceGroup.free };
        if(~qmwSCFXGroup.notNil) { ~qmwSCFXGroup.free };
        if(~qmwSCSourceBus.notNil) { ~qmwSCSourceBus.free };
        "QMW SuperCollider resonator stopped.".postln;
    };

    "QMW density spectral resonator ready on UDP port %."
        .format(NetAddr.langPort).postln;
    "Run ~qmwSCTest.() for audio; run ~qmwSCStatus.() for OSC/node status."
        .postln;
};
)



~qmwSCLoadIR.(
    "/Users/zlayton/QuantumSonification/algebraic_surfaces/heart_v1/living/state_000001/ir_surface_laplacian_r000001.wav",
	"/Users/zlayton/QuantumSonification/algebraic_surfaces/tanglecube_v1/living/state_000001/modal_ir.wav",
    500
);

~qmwSCConvolutionMix.(0.85, 0.99, 500);



~qmwSCSynths.do { |synth|
    synth.set(\partialTriggerThreshold, 0.0002);
};
