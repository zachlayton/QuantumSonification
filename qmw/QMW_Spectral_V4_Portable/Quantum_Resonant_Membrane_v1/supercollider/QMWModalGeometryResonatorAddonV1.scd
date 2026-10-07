/*
Prototype A adapter for QMWUnifiedInstrumentResonatorV3.

It accepts complete 20-mode ModalGeometryFrames (a rest frame or an explicitly
declared test-deformed frame) and applies only
the frame's frequency ratios and Q-derived decay scale to the existing body.
It does not generate plucks, alter their admitted energy, alter m0--m19
performer amplitude, read rho, or send OSC upstream.  Quantum deformation,
flow excitation, IR, and spatialization stay deliberately out of this layer:
it has no rho, flow, IR, or event creation authority.
*/
(
var root = "/qmw/modal";
var schema = "qmw.modal_geometry.osc.v1";
var port = (~qmgPort ? ("QMW_MODAL_GEOMETRY_PORT".getenv ? "17882").asInteger).asInteger;
var motionPort = (~qmgMotionControlPort ? ("QMW_MODAL_GEOMETRY_MOTION_CONTROL_PORT".getenv ? "17883").asInteger).asInteger;
var modeCount = 20;
var commitFrame, shapeEvent, refreshPanel, closePanel, openPanel, sendMotion, applyGeometry, geometryChanged;
var defineAuditionSynth, auditionMode, auditionSelected, auditionDynKlank, auditionGrainSin, auditionSpectral;
var diagnosticFrameWeights, diagnosticAuditionFrequencies;
var motionAddress;

~qmgCleanup !? { ~qmgCleanup.value };
thisProcess.openUDPPort(port);

~qmgPort = port;
~qmgMotionControlPort = motionPort;
~qmgEnabled = ~qmgEnabled ? true;
// Zero is an exact legacy-ratio/legacy-decay return. One applies the complete
// reference-relative Laplacian deformation. The frame is always calculated;
// this controls only its sonic influence.
~qmgInfluence = (~qmgInfluence ? 0.35).clip(0.0, 1.0);
// These values address only experiments/tuning_geometry_motion_v1.py.  They
// have no rho or Hamiltonian semantics and do nothing unless that explicitly
// launched local test driver is running.
~qmgMotionEnabled = ~qmgMotionEnabled ? false;
~qmgMotionDepth = (~qmgMotionDepth ? 0.0).clip(0.0, 0.50);
~qmgMotionRateHz = (~qmgMotionRateHz ? 0.08).clip(0.0, 0.50);
~qmgSymmetryBreakAB = false;
~qmgSymmetryBreakRestore = nil;
~qmgStageTimeout = 0.75;
~qmgLastFrameId = -1;
~qmgStage = nil;
~qmgWindow = nil;
~qmgReadout = nil;
~qmgPriorRenderEvent = ~qriRenderEvent;
~qmgPriorUpdatePitchRatios = ~qrmUpdatePitchRatios;
~qmgPriorModalDecaySeconds = ~qrmModalDecaySeconds;
~qmgDynamicRatios = nil;
~qmgFrame = (
    id: -1, time: 0.0, reference: 55.0,
    frequencies: Array.fill(modeCount, 55.0), geometryRatios: Array.fill(modeCount, 1.0), quality: Array.fill(modeCount, 120.0),
    eigenvectors: Array.fill(modeCount * modeCount, 0.0),
    xyz: Array.fill(modeCount * 3, 0.0), eigenvalues: Array.fill(modeCount, 0.0),
    connectivity: [0.0, 0, 0.0]
);

refreshPanel = {
    ~qmgReadout !? { |view|
        view.string_("frame %  /  f0 % Hz  /  lambda1 %  /  components %\n"
            .format(~qmgFrame[\id], ~qmgFrame[\reference].round(0.001),
                ~qmgFrame[\connectivity][0].round(0.0001), ~qmgFrame[\connectivity][1])
            ++ "MODAL GEOMETRY: Scala/Wilson -> dodecahedral W -> L -> eigenmodes -> resonator ratios\n"
            ++ "m0-m19 remain performer amplitude controls. Auditions use an independent normalized diagnostic frame in a +2 octave listening register; they never change that mix.\n"
            ++ "GEOMETRY AMOUNT %  /  TEST MOTION: %  depth %  rate % Hz  (localhost UDP %; non-quantum driver)"
                .format(~qmgInfluence.round(0.001), if(~qmgMotionEnabled, { "ON" }, { "OFF" }),
                    ~qmgMotionDepth.round(0.001), ~qmgMotionRateHz.round(0.001), motionPort))
    };
};

motionAddress = NetAddr("127.0.0.1", motionPort);
sendMotion = { |suffix, value|
    motionAddress.sendMsg(root ++ "/deformation" ++ suffix, value);
};

geometryChanged = { |before, after|
    before.isNil or: { before.size != after.size } or: {
        before.any { |value, index| (value.asFloat - after[index].asFloat).abs > 1e-9 }
    }
};

// The audition path is intentionally separate from the body and from the
// performer M mixer.  It is a Phase-2 acceptance aid, not quantum evolution.
// A muted or zero-gain m0-m19 lane must never make the diagnostic controls
// silent: otherwise there is no reliable way to hear a newly received frame.
diagnosticFrameWeights = { Array.fill(modeCount, 0.42) };
// The canonical frame remains at its declared physical/instrument register.
// Only the acceptance audition is transposed two octaves, so a 55 Hz first
// mode is heard as a pitch rather than a speaker-dependent thump. Ratios,
// splittings, mode order, M mix, and live resonator frequencies are unchanged.
diagnosticAuditionFrequencies = {
    (~qmgFrame[\frequencies] ? Array.fill(modeCount, 55.0))
        .collect { |frequency| (frequency.asFloat * 4.0).clip(55.0, 16000.0) }
};

defineAuditionSynth = {
    SynthDef(\qmgIsolatedModeAuditionV1, { |out=0, frequency=110, amplitude=0.16,
        decay=1.25, pan=0|
        // This is deliberately a pitch reference, not the primary Ringz body:
        // it must identify the selected frame mode without an impulse thump.
        var signal = SinOsc.ar(frequency.max(20));
        var lifetime = EnvGen.ar(
            Env.linen(0, (decay * 1.35).clip(0.08, 5.0), 0.04), doneAction: 2
        );
        Out.ar(out, Pan2.ar(signal * lifetime * amplitude.clip(0, 0.5), pan));
    }).add;

    // This is the direct dynamic resonator-bank alternative to twenty
    // separately written Ringz UGens. Its arrays are live Synth controls.
    SynthDef(\qmgDynKlankFrameAuditionV1, { |out=0, amplitude=0.16, lifetime=2.0|
        var frequencies = NamedControl.kr(\frequencies, Array.fill(modeCount, 110.0));
        var modeAmplitudes = NamedControl.kr(\modeAmplitudes, Array.fill(modeCount, 0.0));
        var decaySeconds = NamedControl.kr(\decaySeconds, Array.fill(modeCount, 0.28));
        var excitation = PinkNoise.ar(0.28) * Decay2.ar(Impulse.ar(0), 0.0008, 0.022);
        var signal = DynKlank.ar(`[frequencies, modeAmplitudes, decaySeconds], excitation);
        var envelope = EnvGen.ar(Env.linen(0, lifetime.clip(0.1, 6.0), 0.04), doneAction: 2);
        Out.ar(out, Pan2.ar(signal * envelope * amplitude.clip(0, 0.5), 0));
    }).add;

    // GrainSin is intentionally a granular rendering adapter: it uses the
    // modal frequencies and M gains, with bounded Q-derived grain lengths.
    SynthDef(\qmgGrainSinFrameAuditionV1, { |out=0, amplitude=0.12, lifetime=3.0|
        var frequencies = NamedControl.kr(\frequencies, Array.fill(modeCount, 110.0));
        var modeAmplitudes = NamedControl.kr(\modeAmplitudes, Array.fill(modeCount, 0.0));
        var decaySeconds = NamedControl.kr(\decaySeconds, Array.fill(modeCount, 0.28));
        var grains = Array.fill(modeCount, { |index|
            GrainSin.ar(
                1,
                Dust.ar(1.2 + (index * 0.065)),
                decaySeconds[index].clip(0.035, 0.18),
                frequencies[index].clip(20, 16000),
                0,
                -1,
                128,
                modeAmplitudes[index].clip(0, 2)
            )
        });
        var envelope = EnvGen.ar(Env.linen(0.02, lifetime.clip(0.1, 6.0), 0.10), doneAction: 2);
        Out.ar(out, Splay.ar(grains, 0.82, amplitude.clip(0, 0.5)) * envelope);
    }).add;

    // A spectral renderer: the same dynamic modal bank is analyzed, gently
    // broadened in Fourier space, then resynthesized by IFFT.
    SynthDef(\qmgSpectralFrameAuditionV1, { |out=0, amplitude=0.15, lifetime=2.5, smear=4.0|
        var frequencies = NamedControl.kr(\frequencies, Array.fill(modeCount, 110.0));
        var modeAmplitudes = NamedControl.kr(\modeAmplitudes, Array.fill(modeCount, 0.0));
        var decaySeconds = NamedControl.kr(\decaySeconds, Array.fill(modeCount, 0.28));
        var excitation = PinkNoise.ar(0.28) * Decay2.ar(Impulse.ar(0), 0.0008, 0.022);
        var modalSignal = DynKlank.ar(`[frequencies, modeAmplitudes, decaySeconds], excitation);
        var chain = FFT(LocalBuf(4096), modalSignal);
        var resynthesized = IFFT(PV_MagSmear(chain, smear.clip(0, 16)));
        var envelope = EnvGen.ar(Env.linen(0, lifetime.clip(0.1, 6.0), 0.04), doneAction: 2);
        Out.ar(out, Pan2.ar(resynthesized * envelope * amplitude.clip(0, 0.5), 0));
    }).add;
};

auditionMode = { |index=0, level=0.28|
    var lane = index.asInteger.clip(0, modeCount - 1);
    var frequency = diagnosticAuditionFrequencies.value[lane];
    var decay = (~qrmModalDecaySeconds ? Array.fill(modeCount, 0.28))[lane].asFloat;
    if(s.serverRunning.not, {
        "QMW modal audition unavailable: audio server is not running.".warn;
    }, {
        Synth(\qmgIsolatedModeAuditionV1, [
            \frequency, frequency.max(20),
            \amplitude, level.clip(0, 0.5),
            \decay, decay.max(0.02),
            \pan, lane.linlin(0, modeCount - 1, -0.7, 0.7)
        ]);
        "QMW diagnostic modal audition: M% at % Hz (+2 octave listening register) for % s (performer M gain/mute unchanged)."
            .format(lane + 1, frequency.round(0.01), decay.round(0.001)).postln;
    });
};
auditionSelected = { auditionMode.value(~qrmSelectedModeIndex ? 0) };
auditionDynKlank = { |level=0.24|
    if(s.serverRunning.not, {
        "QMW DynKlank audition unavailable: audio server is not running.".warn;
    }, {
        Synth(\qmgDynKlankFrameAuditionV1, [
            \frequencies, diagnosticAuditionFrequencies.value,
            \modeAmplitudes, diagnosticFrameWeights.value,
            \decaySeconds, ~qrmModalDecaySeconds,
            \amplitude, level
        ]);
        "QMW DynKlank diagnostic frame audition: 20 modes in +2 octave listening register; performer M mix unchanged.".postln;
    });
};
auditionGrainSin = { |level=0.20|
    if(s.serverRunning.not, {
        "QMW GrainSin audition unavailable: audio server is not running.".warn;
    }, {
        Synth(\qmgGrainSinFrameAuditionV1, [
            \frequencies, diagnosticAuditionFrequencies.value,
            \modeAmplitudes, diagnosticFrameWeights.value,
            \decaySeconds, ~qrmModalDecaySeconds,
            \amplitude, level
        ]);
        "QMW GrainSin diagnostic frame audition: 20 modes in +2 octave listening register; performer M mix unchanged.".postln;
    });
};
auditionSpectral = { |level=0.24|
    if(s.serverRunning.not, {
        "QMW FFT/IFFT audition unavailable: audio server is not running.".warn;
    }, {
        Synth(\qmgSpectralFrameAuditionV1, [
            \frequencies, diagnosticAuditionFrequencies.value,
            \modeAmplitudes, diagnosticFrameWeights.value,
            \decaySeconds, ~qrmModalDecaySeconds,
            \amplitude, level
        ]);
        "QMW FFT/IFFT diagnostic frame audition: 20 modes in +2 octave listening register; performer M mix unchanged.".postln;
    });
};
~qmgAuditionMode = auditionMode;
~qmgAuditionSelected = auditionSelected;
~qmgAuditionDynKlank = auditionDynKlank;
~qmgAuditionGrainSin = auditionGrainSin;
~qmgAuditionSpectral = auditionSpectral;

applyGeometry = { |dynamicRatios|
    var reference = ~qmgFrame[\reference].asFloat.max(1e-6);
    var amount = ~qmgInfluence.clip(0.0, 1.0);
    var baselineRatios = dynamicRatios.collect(_.asFloat.max(1e-9));
    var geometryRatios = ~qmgFrame[\geometryRatios].collect(_.asFloat.max(1e-9));
    var geometryDecay = Array.fill(modeCount, { |index|
        ~qmgFrame[\quality][index].asFloat / (pi * ~qmgFrame[\frequencies][index].asFloat.max(1e-6))
    });
    var baselineDecay = (~qmgPriorModalDecaySeconds ? Array.fill(modeCount, 0.28))
        .collect(_.asFloat.max(1e-6));
    // Geometry is a relative exponent. Amount zero exactly preserves the
    // incoming source's ratios and decays; it cannot erase V4.2 or a future
    // live provider's behavior.
    ~qrmPitchRatios = Array.fill(modeCount, { |index|
        baselineRatios[index] * geometryRatios[index].pow(amount)
    });
    ~qrmModalDecaySeconds = Array.fill(modeCount, { |index|
        baselineDecay[index] * (geometryDecay[index] / baselineDecay[index]).pow(amount)
    });
    ~qrmBody !? { |node|
        node.setn(\frequencyRatios, ~qrmPitchRatios);
        node.setn(\modalDecaySeconds, ~qrmModalDecaySeconds);
    };
};

commitFrame = { |frame|
    var reference = frame[\reference].asFloat.max(1e-6);
    var geometryIsNew = (~qmgFrame[\id] < 0) or: {
        geometryChanged.value(~qmgFrame[\geometryRatios], frame[\geometryRatios])
    };
    ~qmgFrame = frame;
    ~qmgLastFrameId = frame[\id];
    if(~qmgEnabled and: { geometryIsNew or: { ~qmgDynamicRatios.isNil } }) {
        // Let the primary source establish its own living ratios, then apply
        // only the declared geometry-relative factor. M gains are untouched.
        if(~qmgDynamicRatios.isNil) {
            ~qmgPriorUpdatePitchRatios.value;
            ~qmgDynamicRatios = ~qrmPitchRatios.copy;
        };
        applyGeometry.value(~qmgDynamicRatios);
    };
    if((frame[\id] % 600) == 0) {
        "QMW V3 composed ModalGeometryFrame % (f0 % Hz, geometry amount %)"
            .format(frame[\id], reference.round(0.001), ~qmgInfluence.round(0.001)).postln;
    };
    { refreshPanel.value }.defer;
};

// Compose with the ordinary source updater rather than replacing it.
~qrmUpdatePitchRatios = {
    if(~qmgEnabled and: { ~qmgFrame[\id] >= 0 }, {
        ~qmgPriorUpdatePitchRatios.value;
        ~qmgDynamicRatios = ~qrmPitchRatios.copy;
        applyGeometry.value(~qmgDynamicRatios);
    }, {
        ~qmgPriorUpdatePitchRatios.value;
    });
};

shapeEvent = { |event|
    var weights, weightedQuality, baseQuality, qScale, priorScale;
    if(~qmgEnabled.not or: { ~qmgFrame[\id] < 0 }, { event }, {
        weights = event[\weights].collect(_.asFloat.abs);
        baseQuality = ~qmgFrame[\quality].mean.max(1e-6);
        weightedQuality = (weights * ~qmgFrame[\quality]).sum / weights.sum.max(1e-12);
        qScale = (weightedQuality / baseQuality).clip(0.25, 1.75);
        priorScale = (event[\decayScale] ? 1.0).asFloat.clip(0.25, 1.75);
        // Q changes only the existing event's decay time.  Its energy,
        // weights, phases, and performer-controlled amplitude are untouched.
        event.copy.put(\decayScale, (priorScale * qScale).clip(0.25, 1.75))
            .put(\modalGeometryFrameId, ~qmgFrame[\id])
    })
};

// This remains downstream of V1/V2 event admission.  A geometry frame merely
// changes resonator parameters for events that already exist.
~qriRenderEvent = { |event, level=1.0|
    ~qmgPriorRenderEvent.value(shapeEvent.value(event), level)
};

openPanel = {
    if(~qmgWindow.notNil, { ~qmgWindow.front }, {
        var depthReadout, rateReadout, influenceReadout;
        ~qmgWindow = Window("Unified Instrument Resonator V3 — Modal Geometry", Rect(170, 485, 760, 430))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qmgWindow, Rect(16, 12, 728, 30))
            .string_("20-NODE DODECAHEDRAL MODAL GEOMETRY (REST FRAME + DECLARED TEST MOTION)")
            .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("dcecff"));
        Button(~qmgWindow, Rect(16, 52, 250, 25))
            .states_([["MODAL GEOMETRY BYPASSED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["MODAL GEOMETRY APPLIED", Color.black, Color.fromHexString("80ed99")]])
            .value_(~qmgEnabled.asInteger).action_({ |button|
                ~qmgEnabled = button.value > 0;
                if(~qmgEnabled and: { ~qmgFrame[\id] >= 0 }, {
                    ~qmgDynamicRatios = nil;
                    commitFrame.value(~qmgFrame);
                }, {
                    ~qmgDynamicRatios = nil;
                    ~qrmModalDecaySeconds = ~qmgPriorModalDecaySeconds.copy;
                    ~qrmBody !? { |node| node.setn(\modalDecaySeconds, ~qrmModalDecaySeconds) };
                    ~qmgPriorUpdatePitchRatios.value;
                });
            });
        Button(~qmgWindow, Rect(282, 52, 250, 25))
            .states_([["AUDITION SELECTED M (+2 octaves)", Color.black, Color.fromHexString("8ecae6")]])
            .action_({ auditionSelected.value });
        Button(~qmgWindow, Rect(16, 84, 250, 25))
            .states_([["DYNKLANK FRAME (+2 octaves)", Color.black, Color.fromHexString("b8f2e6")]])
            .action_({ auditionDynKlank.value });
        Button(~qmgWindow, Rect(282, 84, 250, 25))
            .states_([["GRAINSIN FRAME (+2 octaves)", Color.black, Color.fromHexString("cdb4db")]])
            .action_({ auditionGrainSin.value });
        Button(~qmgWindow, Rect(16, 116, 250, 25))
            .states_([["FFT/IFFT FRAME (+2 octaves)", Color.black, Color.fromHexString("ffd6a5")]])
            .action_({ auditionSpectral.value });
        StaticText(~qmgWindow, Rect(16, 152, 728, 20))
            .string_("DECLARED TEST GEOMETRY MOTION — W0 -> W(t) -> L(t); requires StartQMWModalGeometryMotionDriverV1.command")
            .font_(Font("Helvetica Neue", 10, true)).stringColor_(Color.fromHexString("ffd166"));
        Button(~qmgWindow, Rect(16, 178, 250, 25))
            .states_([["TEST MOTION OFF", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["TEST MOTION ON (NON-QUANTUM)", Color.black, Color.fromHexString("ff9f1c")]])
            .value_(~qmgMotionEnabled.asInteger).action_({ |button|
                ~qmgMotionEnabled = button.value > 0;
                sendMotion.value("/enabled", ~qmgMotionEnabled.asInteger);
                refreshPanel.value;
            });
        depthReadout = StaticText(~qmgWindow, Rect(282, 178, 120, 25))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("dcecff"));
        Slider(~qmgWindow, Rect(16, 210, 250, 20))
            .value_(~qmgMotionDepth / 0.50).action_({ |slider|
                ~qmgMotionDepth = (slider.value * 0.50).clip(0.0, 0.50);
                depthReadout.string_("depth %".format(~qmgMotionDepth.round(0.001)));
                sendMotion.value("/depth", ~qmgMotionDepth);
                refreshPanel.value;
            });
        depthReadout.string_("depth %".format(~qmgMotionDepth.round(0.001)));
        rateReadout = StaticText(~qmgWindow, Rect(282, 210, 150, 25))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("dcecff"));
        Slider(~qmgWindow, Rect(16, 242, 250, 20))
            .value_(~qmgMotionRateHz / 0.50).action_({ |slider|
                ~qmgMotionRateHz = (slider.value * 0.50).clip(0.0, 0.50);
                rateReadout.string_("rate % Hz".format(~qmgMotionRateHz.round(0.001)));
                sendMotion.value("/rate_hz", ~qmgMotionRateHz);
                refreshPanel.value;
            });
        rateReadout.string_("rate % Hz".format(~qmgMotionRateHz.round(0.001)));
        influenceReadout = StaticText(~qmgWindow, Rect(282, 274, 180, 25))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("80ed99"));
        Slider(~qmgWindow, Rect(16, 274, 250, 20))
            .value_(~qmgInfluence).action_({ |slider|
                ~qmgInfluence = slider.value.clip(0.0, 1.0);
                influenceReadout.string_("geometry amount %".format(~qmgInfluence.round(0.001)));
                if(~qmgEnabled and: { ~qmgFrame[\id] >= 0 }, {
                    if(~qmgDynamicRatios.isNil) {
                        ~qmgPriorUpdatePitchRatios.value;
                        ~qmgDynamicRatios = ~qrmPitchRatios.copy;
                    };
                    applyGeometry.value(~qmgDynamicRatios);
                });
                refreshPanel.value;
            });
        influenceReadout.string_("geometry amount %".format(~qmgInfluence.round(0.001)));
        Button(~qmgWindow, Rect(16, 306, 430, 25))
            .states_([["A/B SYMMETRY BREAK — REST FRAME", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["A/B SYMMETRY BREAK — DEFORMED", Color.black, Color.fromHexString("ff9f1c")]])
            .value_(~qmgSymmetryBreakAB.asInteger).action_({ |button|
                ~qmgSymmetryBreakAB = button.value > 0;
                if(~qmgSymmetryBreakAB, {
                    ~qmgSymmetryBreakRestore = (
                        influence: ~qmgInfluence, depth: ~qmgMotionDepth,
                        rate: ~qmgMotionRateHz, enabled: ~qmgMotionEnabled
                    );
                    ~qmgInfluence = 1.0;
                    ~qmgMotionDepth = 0.50;
                    ~qmgMotionRateHz = 0.08;
                    ~qmgMotionEnabled = true;
                }, {
                    var restore = ~qmgSymmetryBreakRestore ? (influence: 0.35, depth: 0.0, rate: 0.08, enabled: false);
                    ~qmgInfluence = restore[\influence];
                    ~qmgMotionDepth = restore[\depth];
                    ~qmgMotionRateHz = restore[\rate];
                    ~qmgMotionEnabled = restore[\enabled];
                    ~qmgSymmetryBreakRestore = nil;
                });
                if(~qmgDynamicRatios.notNil and: { ~qmgEnabled }, { applyGeometry.value(~qmgDynamicRatios) });
                sendMotion.value("/depth", ~qmgMotionDepth);
                sendMotion.value("/rate_hz", ~qmgMotionRateHz);
                sendMotion.value("/enabled", ~qmgMotionEnabled.asInteger);
                refreshPanel.value;
            });
        // Push the current panel state when the driver is launched before or
        // after the window; UDP is intentionally one-way and local.
        sendMotion.value("/depth", ~qmgMotionDepth);
        sendMotion.value("/rate_hz", ~qmgMotionRateHz);
        sendMotion.value("/enabled", ~qmgMotionEnabled.asInteger);
        ~qmgReadout = StaticText(~qmgWindow, Rect(16, 338, 728, 76))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("8ecae6"));
        ~qmgWindow.onClose = { ~qmgWindow = nil; ~qmgReadout = nil };
        refreshPanel.value;
    });
};
closePanel = { ~qmgWindow !? _.close; ~qmgWindow = nil; ~qmgReadout = nil };
~qmgOpenPanel = openPanel;
// Public scene-recall seam. It reapplies only the currently committed
// geometry frame and optional local test-motion settings; it neither saves nor
// restores a frame, rho, Hamiltonian, or upstream geometry source.
~qmgApplyScene = {
    if(~qmgEnabled and: { ~qmgFrame[\id] >= 0 }, {
        ~qmgDynamicRatios = nil;
        commitFrame.value(~qmgFrame);
    }, {
        ~qmgDynamicRatios = nil;
        ~qrmModalDecaySeconds = ~qmgPriorModalDecaySeconds.copy;
        ~qrmBody !? { |node| node.setn(\modalDecaySeconds, ~qrmModalDecaySeconds) };
        ~qmgPriorUpdatePitchRatios.value;
    });
    sendMotion.value("/depth", ~qmgMotionDepth);
    sendMotion.value("/rate_hz", ~qmgMotionRateHz);
    sendMotion.value("/enabled", ~qmgMotionEnabled.asInteger);
    refreshPanel.value;
};
s.waitForBoot({ defineAuditionSynth.value });

OSCdef(\qmgBeginV1, { |msg|
    var valid = (msg.size >= 6) and: { msg[3].asString == schema }
        and: { msg[1].asInteger > ~qmgLastFrameId } and: { msg[4].asInteger == modeCount }
        and: { msg[5].asFloat > 0 };
    ~qmgStage = if(valid, {
        (id: msg[1].asInteger, time: msg[2].asFloat, reference: msg[5].asFloat,
            frequencies: nil, geometryRatios: nil, quality: nil, eigenvectors: nil, xyz: nil, eigenvalues: nil, connectivity: nil,
            deadline: Main.elapsedTime + ~qmgStageTimeout)
    }, { nil });
}, root ++ "/frame/begin", recvPort: port);

OSCdef(\qmgFreqsV1, { |msg|
    if(~qmgStage.notNil and: { msg.size == (modeCount + 2) } and: { msg[1].asInteger == ~qmgStage[\id] }) {
        ~qmgStage[\frequencies] = msg.copyRange(2, modeCount + 1).collect(_.asFloat)
    };
}, root ++ "/freqs", recvPort: port);

OSCdef(\qmgGeometryRatiosV1, { |msg|
    if(~qmgStage.notNil and: { msg.size == (modeCount + 2) } and: { msg[1].asInteger == ~qmgStage[\id] }) {
        ~qmgStage[\geometryRatios] = msg.copyRange(2, modeCount + 1).collect(_.asFloat)
    };
}, root ++ "/geometry_ratios", recvPort: port);

OSCdef(\qmgQV1, { |msg|
    if(~qmgStage.notNil and: { msg.size == (modeCount + 2) } and: { msg[1].asInteger == ~qmgStage[\id] }) {
        ~qmgStage[\quality] = msg.copyRange(2, modeCount + 1).collect(_.asFloat)
    };
}, root ++ "/q", recvPort: port);

OSCdef(\qmgEigenvectorsV1, { |msg|
    if(~qmgStage.notNil and: { msg.size == ((modeCount * modeCount) + 2) }
        and: { msg[1].asInteger == ~qmgStage[\id] }) {
        ~qmgStage[\eigenvectors] = msg.copyRange(2, (modeCount * modeCount) + 1).collect(_.asFloat)
    };
}, root ++ "/eigenvectors", recvPort: port);

OSCdef(\qmgXYZV1, { |msg|
    if(~qmgStage.notNil and: { msg.size == ((modeCount * 3) + 2) } and: { msg[1].asInteger == ~qmgStage[\id] }) {
        ~qmgStage[\xyz] = msg.copyRange(2, (modeCount * 3) + 1).collect(_.asFloat)
    };
}, root ++ "/xyz", recvPort: port);

OSCdef(\qmgEigenvaluesV1, { |msg|
    if(~qmgStage.notNil and: { msg.size == (modeCount + 2) } and: { msg[1].asInteger == ~qmgStage[\id] }) {
        ~qmgStage[\eigenvalues] = msg.copyRange(2, modeCount + 1).collect(_.asFloat)
    };
}, root ++ "/eigenvalues", recvPort: port);

OSCdef(\qmgConnectivityV1, { |msg|
    if(~qmgStage.notNil and: { msg.size == 5 } and: { msg[1].asInteger == ~qmgStage[\id] }) {
        ~qmgStage[\connectivity] = msg.copyRange(2, 4).collect(_.asFloat)
    };
}, root ++ "/connectivity", recvPort: port);

// Explicit acceptance control: unlike a raw /s_new test, this resolves the
// requested lane through the live M gain and mute state before it makes sound.
OSCdef(\qmgAuditionV1, { |msg|
    auditionMode.value(msg[1] ? (~qrmSelectedModeIndex ? 0), msg[2] ? 0.20);
}, root ++ "/audition", recvPort: port);

OSCdef(\qmgDynKlankAuditionV1, { |msg|
    auditionDynKlank.value(msg[1] ? 0.16);
}, root ++ "/audition/dynklank", recvPort: port);

OSCdef(\qmgGrainSinAuditionV1, { |msg|
    auditionGrainSin.value(msg[1] ? 0.12);
}, root ++ "/audition/grainsin", recvPort: port);

OSCdef(\qmgSpectralAuditionV1, { |msg|
    auditionSpectral.value(msg[1] ? 0.15);
}, root ++ "/audition/spectral", recvPort: port);

OSCdef(\qmgEndV1, { |msg|
    var stage = ~qmgStage;
    if(stage.notNil and: { msg.size >= 2 } and: { msg[1].asInteger == stage[\id] }
        and: { [\frequencies, \geometryRatios, \quality, \eigenvectors, \xyz, \eigenvalues, \connectivity].every { |key| stage[key].notNil } }) {
        if(stage[\frequencies].every { |value| value.isNumber and: { value.abs < inf } and: { value > 0 } }
            and: { stage[\geometryRatios].every { |value| value.isNumber and: { value.abs < inf } and: { value > 0 } } }
            and: { stage[\quality].every { |value| value.isNumber and: { value.abs < inf } and: { value > 0 } } }) {
            commitFrame.value(stage);
        };
    };
    ~qmgStage = nil;
}, root ++ "/frame/end", recvPort: port);

~qmgWatchdog = Routine({ loop {
    if(~qmgStage.notNil and: { Main.elapsedTime > ~qmgStage[\deadline] }) { ~qmgStage = nil };
    0.20.wait;
} }).play(AppClock);

~qmgCleanup = {
    [\qmgBeginV1, \qmgFreqsV1, \qmgGeometryRatiosV1, \qmgQV1, \qmgEigenvectorsV1, \qmgXYZV1, \qmgEigenvaluesV1,
        \qmgConnectivityV1, \qmgAuditionV1, \qmgDynKlankAuditionV1,
        \qmgGrainSinAuditionV1, \qmgSpectralAuditionV1, \qmgEndV1].do { |key| OSCdef(key).free };
    ~qmgWatchdog !? _.stop; ~qmgWatchdog = nil;
    ~qmgStage = nil;
    if(~qmgPriorRenderEvent.notNil) { ~qriRenderEvent = ~qmgPriorRenderEvent };
    if(~qmgPriorUpdatePitchRatios.notNil) {
        ~qrmUpdatePitchRatios = ~qmgPriorUpdatePitchRatios;
    };
    ~qrmModalDecaySeconds = ~qmgPriorModalDecaySeconds.copy;
    ~qrmBody !? { |node| node.setn(\modalDecaySeconds, ~qrmModalDecaySeconds) };
    closePanel.value;
};

{ openPanel.value }.defer;
"QMW Unified Instrument Resonator V3 modal-geometry receiver listening on UDP %".format(port).postln;
)
