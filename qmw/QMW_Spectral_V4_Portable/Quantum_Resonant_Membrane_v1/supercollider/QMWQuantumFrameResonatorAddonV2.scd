/*
Unified Instrument Resonator V2: a bounded receiver for the authoritative
QuantumFrame OSC schema and the optional QHO configuration-flow sidecar.

This is a sound adapter. It never evolves rho, performs a measurement, or
turns a Hilbert-basis current into spatial flux. It reuses V1's 20-mode,
ring/fuzz, five-voice, pluck, and output-routing body through ~qriRenderEvent.
*/
(
var quantumRoot = "/qmw/quantum/v1";
var quantumSchema = "qmw.quantum_frame.osc.v1";
var quantumPort = (~qfrQuantumPort ? 17875).asInteger;
var configurationRoot = "/qmw/qho_configuration/v1";
var configurationSchema = "qmw.qho_configuration.osc.v1";
var configurationPort = (~qfrConfigurationPort ? 17879).asInteger;
var modeCount = 20;
var commitQuantumFrame, commitConfigurationFrame, scheduleQuantumCommit, scheduleConfigurationCommit;
var makeEvent, updateView, texturedMode, pauliGainFor, pauliGateFor, refreshPauliDesk;
var processCurrentQuanta, processBuresPulses, renderFluxEvents, modeForLabel, modeForCurrent;
var openPanel, closePanel, openTemporalControls, closeTemporalControls;
var openPauliDesk, closePauliDesk, openSourceDock, closeSourceDock, setV2Audition;
var openGeneratorControls, closeGeneratorControls, sendVnfHamiltonian;
var styleSlider;

~qfrCleanup !? { ~qfrCleanup.value };
thisProcess.openUDPPort(quantumPort);
thisProcess.openUDPPort(configurationPort);

~qfrQuantumPort = quantumPort;
~qfrConfigurationPort = configurationPort;
~qfrVnfControlPort = (~qfrVnfControlPort ? 17880).asInteger;
~qfrVnfControl = NetAddr("127.0.0.1", ~qfrVnfControlPort);
~qfrEnabled = ~qfrEnabled ? true;
~qfrCurrentQuantum = ~qfrCurrentQuantum ? 0.015;
~qfrPauliMix = ~qfrPauliMix ? 0.55;
~qfrCurrentMix = ~qfrCurrentMix ? 1.0;
~qfrFluxMix = ~qfrFluxMix ? 0.80;
~qfrMaxEventsPerFrame = 8;
~qfrStageTimeout = 0.75;
// The following are deliberately acoustic-response controls.  They never
// feed back into rho, H, a current, or a configuration-space projection.
~qfrMemorySeconds = ~qfrMemorySeconds ? 0.18;
~qfrRefractorySeconds = ~qfrRefractorySeconds ? 0.075;
~qfrTextureSpread = (~qfrTextureSpread ? 0).asInteger.clip(0, 8);
~qfrTextureSeed = (~qfrTextureSeed ? 17).asInteger;
~qfrTextureStep = 0;
~qfrDriftDepth = ~qfrDriftDepth ? 0.0;
~qfrDriftRate = ~qfrDriftRate ? 0.08;
~qfrCurrentAccumulator = IdentityDictionary.new;
~qfrLastEventTime = IdentityDictionary.new;
~qfrPauliGains = Dictionary.new;
~qfrPauliMuted = Dictionary.new;
~qfrPauliGateEnabled = ~qfrPauliGateEnabled ? true;
~qfrV2Audition = false;
~qfrPriorQriEnabled = nil;
~qfrLastQuantumTime = nil;
~qfrLastDriveWallTime = nil;
~qfrPreviousDrives = Array.fill(modeCount, Complex(0, 0));
~qfrLastQuantumRevision = -1;
~qfrLastConfigurationRevision = -1;
~qfrQuantumStage = nil;
~qfrConfigurationStage = nil;
// AppClock owns Qt.  Keep exactly one deferred commit per source so a fast
// sender cannot turn sealed OSC frames into an unbounded GUI work queue.
~qfrPendingQuantumFrame = nil;
~qfrPendingConfigurationFrame = nil;
~qfrQuantumCommitScheduled = false;
~qfrConfigurationCommitScheduled = false;
~qfrWindow = nil;
~qfrModeView = nil;
~qfrStatus = nil;
~qfrQuantumSlider = nil;
~qfrTemporalWindow = nil;
~qfrPauliDeskWindow = nil;
~qfrPauliReadouts = Dictionary.new;
~qfrLastPauliDeskRefresh = 0.0;
~qfrSourceDockWindow = nil;
~qfrGeneratorWindow = nil;
~qfrVnfOmega1 = ~qfrVnfOmega1 ? 1.17;
~qfrVnfOmega2 = ~qfrVnfOmega2 ? 0.73;
~qfrVnfCoupling = ~qfrVnfCoupling ? 0.61;
~qfrVnfEvolutionRate = ~qfrVnfEvolutionRate ? 1.0;
~qfrVnfBuresDistance = ~qfrVnfBuresDistance ? 0.025;
~qfrVnfBuresClockScale = ~qfrVnfBuresClockScale ? 1.0;
~qfrFrame = (
    revision: -1, time: 0.0, populations: Array.new,
    paulis: Array.new, currents: Array.new,
    drives: Array.fill(modeCount, Complex(0, 0)), phases: Array.fill(modeCount, 0.0),
    diagnostics: nil, bures: nil
);
~qfrConfigurationFrame = (
    revision: -1, time: 0.0, regions: Array.new, events: Array.new, summary: nil
);

modeForLabel = { |label|
    // A stable label-derived lane retains a Pauli observable's sonic identity
    // even though the OSC publisher reorders lanes by instantaneous velocity.
    // ``String.collect`` attempts to rebuild a String; convert first so the
    // character codes remain an integer Array rather than a malformed String.
    (label.asString.ascii.asArray.sum % modeCount).asInteger
};
modeForCurrent = { |destination, source|
    ((destination.asInteger * 7) + (source.asInteger * 3)) % modeCount
};

// Qt otherwise uses black slider/number text on dark V2 control panels.
styleSlider = { |slider|
    slider.labelView.stringColor_(Color.white);
    slider.numberView
        .normalColor_(Color.white)
        .typingColor_(Color.white)
        .stringColor_(Color.white)
        .background_(Color.fromHexString("080b10"));
    slider.sliderView.background_(Color.fromHexString("080b10"));
    slider
};

pauliGainFor = { |label|
    var name = label.asString;
    if((~qfrPauliMuted[name] ? false), { 0.0 }, { (~qfrPauliGains[name] ? 1.0).asFloat })
};

pauliGateFor = { |paulis|
    var total = 0.0, active = 0.0;
    if(~qfrPauliGateEnabled.not, { 1.0 }, {
        paulis.do { |pauli|
            var amount = pauli[\unitaryVelocity].abs;
            total = total + amount;
            active = active + (amount * pauliGainFor.value(pauli[\label]));
        };
        if(total <= 1e-9, { 1.0 }, { (active / total).clip(0.0, 1.0) })
    })
};

texturedMode = { |baseMode, identity|
    var spread = ~qfrTextureSpread.asInteger.clip(0, 8);
    var step = ~qfrTextureStep;
    var code = identity.asString.ascii.asArray.sum + ~qfrTextureSeed;
    var offset = if(spread <= 0, { 0 }, {
        ((code + (step * 13)) % ((spread * 2) + 1)) - spread
    });
    ~qfrTextureStep = step + 1;
    (mode: (baseMode + offset) % modeCount, offset: offset)
};

makeEvent = { |kind, energy, dominant=0, textureOffset=0|
    var weights = ~qfrFrame[\drives].collect(_.abs);
    var phases = ~qfrFrame[\phases].copy;
    var center, driftDepth = ~qfrDriftDepth.clip(0.0, 1.0);
    if(weights.sum <= 1e-12) { weights[dominant.clip(0, modeCount - 1)] = 1.0 };
    // A slow resonator-only focus moves through the already-derived modal
    // descriptor.  It is not a rotation of a Pauli observable or of rho.
    if(driftDepth > 0.0) {
        center = (Main.elapsedTime * ~qfrDriftRate.max(0.0) * modeCount).floor.asInteger % modeCount;
        weights = weights.collect { |weight, index|
            var distance = (index - center).abs;
            distance = distance.min(modeCount - distance);
            weight * (1.0 + (driftDepth * (1.0 - ((2.0 * distance) / (modeCount / 2)))))
        };
    };
    if(textureOffset != 0) {
        weights = Array.fill(modeCount, { |index| weights.wrapAt(index - textureOffset) });
        phases = Array.fill(modeCount, { |index| phases.wrapAt(index - textureOffset) });
    };
    weights = weights / weights.maxItem.max(1e-12);
    (
        id: "qfr-%-%".format(~qfrFrame[\revision], kind),
        channel: "sealed_quantum_frame", kind: kind,
        real: 0.0, imag: 0.0,
        // This is a bounded perceptual excitation amount, not probability.
        energy: (energy * (~qfrFrame[\pauliExcitationGate] ? 1.0)).clip(0.0, 0.35), azimuth: 0.0,
        dominant: dominant.clip(0, modeCount - 1), inputs: [0], outputs: [0],
        weights: weights, phases: phases
    )
};

processCurrentQuanta = { |frame|
    var dt, emitted = 0, now = Main.elapsedTime;
    dt = if(~qfrLastQuantumTime.isNil, { 0.0 }, {
        (frame[\time] - ~qfrLastQuantumTime).max(0.0)
    });
    // A V2 receiver never queues obsolete OSC packets. One accepted snapshot
    // aggregates each edge's elapsed passage into at most one bounded pluck.
    frame[\currents].do { |current|
        var destination = current[\destination], source = current[\source];
        var key = "%<-%".format(destination, source);
        var total = (~qfrCurrentAccumulator[key] ? 0.0)
            + (current[\magnitude].max(0.0) * dt);
        var count = (total / ~qfrCurrentQuantum.max(1e-6)).floor.asInteger;
        var mode = modeForCurrent.(destination, source), texture;
        if(count > 0) {
            ~qfrCurrentAccumulator[key] = total - (count * ~qfrCurrentQuantum);
            if(emitted < ~qfrMaxEventsPerFrame and: { ~qfrEnabled }
                and: { (now - (~qfrLastEventTime[key] ? -1e9)) >= ~qfrRefractorySeconds.max(0.0) }) {
                texture = texturedMode.value(mode, key);
                ~qriRenderEvent !? { |renderer|
                    renderer.value(makeEvent.("basis_current", count * ~qfrCurrentQuantum,
                        texture[\mode], texture[\offset]))
                };
                ~qfrLastEventTime[key] = now;
                emitted = emitted + 1;
            };
        } {
            ~qfrCurrentAccumulator[key] = total
        };
    };
    ~qfrLastQuantumTime = frame[\time];
};

processBuresPulses = { |frame|
    var metric = frame[\bures], pulses, magnitudes, dominant;
    // Bures records are a read-only metric observation.  They deliberately
    // render only in the explicitly selected Quantum / Bures timing mode;
    // live Event Threshold remains driven by Hilbert-basis current crossings.
    if(metric.notNil and: { ~qrmTimeMode == 1 }) {
        pulses = metric[\pulses].asInteger.clip(0, ~qfrMaxEventsPerFrame);
        if(pulses > 0 and: { ~qfrEnabled }) {
            magnitudes = frame[\drives].collect(_.abs);
            dominant = magnitudes.maxIndex ? 0;
            pulses.do { |index|
                ~qriRenderEvent !? { |renderer|
                    renderer.value(makeEvent.("bures_clock",
                        (metric[\delta].max(0.0) / metric[\distance].max(1e-6))
                            * 0.035, dominant, index))
                };
            };
        };
    };
};

renderFluxEvents = { |frame|
    var now = Main.elapsedTime;
    if(frame[\events].notEmpty) {
        frame[\events].copyRange(0, (frame[\events].size - 1).min(~qfrMaxEventsPerFrame - 1)).do { |event|
            var key = "flux-%<-%".format(event[\destination], event[\source]);
            var mode = ((event[\source] * 5) + event[\destination]) % modeCount, texture;
            if(~qfrEnabled and: { (now - (~qfrLastEventTime[key] ? -1e9)) >= ~qfrRefractorySeconds.max(0.0) }) {
                texture = texturedMode.value(mode, key);
                ~qriRenderEvent !? { |renderer|
                    renderer.value(makeEvent.("configuration_flux", event[\magnitude] * ~qfrFluxMix,
                        texture[\mode], texture[\offset]))
                };
                ~qfrLastEventTime[key] = now;
            };
        };
    };
};

updateView = {
    var magnitudes = ~qfrFrame[\drives].collect(_.abs);
    var peak = magnitudes.maxItem.max(1e-12);
    ~qfrModeView !? { |view| view.value_(magnitudes / peak) };
    ~qfrStatus !? { |view|
        view.string_(
            "rho rev % / % Pauli lanes / Pauli gate % / % current lanes / QHO flux rev % / no OSC queue"
            .format(~qfrFrame[\revision], ~qfrFrame[\paulis].size,
                ((~qfrFrame[\pauliExcitationGate] ? 1.0) * 100).round(1),
                ~qfrFrame[\currents].size, ~qfrConfigurationFrame[\revision])
        )
    };
    refreshPauliDesk.value;
};

refreshPauliDesk = {
    var now = Main.elapsedTime;
    if(~qfrPauliDeskWindow.notNil and: { (now - ~qfrLastPauliDeskRefresh) >= 0.10 }) {
        ~qfrLastPauliDeskRefresh = now;
        ~qfrFrame[\paulis].do { |pauli|
            var name = pauli[\label].asString;
            ~qfrPauliReadouts[name] !? { |view|
                view.string_("value %   d/dt %   %"
                    .format(pauli[\value].round(0.001), pauli[\velocity].round(0.001),
                        if(pauli[\conserved] > 0, { "CONSERVED" }, { "dynamic" })))
            };
        };
    };
};

commitQuantumFrame = { |frame|
    var drives = Array.fill(modeCount, { Complex(0, 0) });
    var phases = Array.fill(modeCount, 0.0), now = Main.elapsedTime, retention = 0.0;
    var pauliExcitationGate = pauliGateFor.value(frame[\paulis]);
    if(~qfrLastDriveWallTime.notNil and: { ~qfrMemorySeconds > 0.001 }) {
        retention = (((now - ~qfrLastDriveWallTime).max(0.0) / ~qfrMemorySeconds) * -1.0).exp
    };
    frame[\populations].do { |population|
        var mode = population[\index] % modeCount;
        // Population is a passive modal weight; it never causes a pluck.
        drives[mode] = drives[mode] + Complex(population[\value].max(0).sqrt * 0.08, 0);
    };
    frame[\paulis].do { |pauli|
        var velocity = pauli[\unitaryVelocity] * ~qfrPauliMix * pauliGainFor.value(pauli[\label]);
        var mode = modeForLabel.(pauli[\label]);
        // These descriptors use only phases 0 and pi, so the signed real
        // component is the precise and portable polar-to-complex form.
        drives[mode] = drives[mode] + Complex(velocity, 0);
        phases[mode] = if(velocity >= 0, { 0.0 }, { pi });
    };
    frame[\currents].do { |current|
        var mode = modeForCurrent.(current[\destination], current[\source]);
        var signPhase = if(current[\destination] >= current[\source], { 0.0 }, { pi });
        drives[mode] = drives[mode] + Complex(
            current[\magnitude].max(0).sqrt * ~qfrCurrentMix
            * if(current[\destination] >= current[\source], { 1 }, { -1 }), 0
        );
        phases[mode] = signPhase;
    };
    if(retention > 0.0) {
        drives = Array.fill(modeCount, { |index|
            (~qfrPreviousDrives[index] * retention) + (drives[index] * (1.0 - retention))
        });
    };
    ~qfrPreviousDrives = drives.copy;
    ~qfrLastDriveWallTime = now;
    ~qfrFrame = frame.copy.put(\drives, drives).put(\phases, phases)
        .put(\pauliExcitationGate, pauliExcitationGate);
    processCurrentQuanta.(~qfrFrame);
    processBuresPulses.(~qfrFrame);
    updateView.value;
};

commitConfigurationFrame = { |frame|
    frame[\regions].do { |region|
        var mode = (region[\index] * 11) % modeCount;
        var flux = region[\flux] * ~qfrFluxMix;
        ~qfrFrame[\drives][mode] = ~qfrFrame[\drives][mode] + Complex(flux, 0);
        ~qfrFrame[\phases][mode] = if(flux >= 0, { 0.0 }, { pi });
    };
    ~qfrConfigurationFrame = frame;
    renderFluxEvents.(frame);
    updateView.value;
};

scheduleQuantumCommit = { |frame|
    // Latest sealed frame wins.  Intermediate observation frames have no
    // separate ownership once a newer revision is available to this adapter.
    ~qfrPendingQuantumFrame = frame;
    if(~qfrQuantumCommitScheduled.not) {
        ~qfrQuantumCommitScheduled = true;
        {
            var pending = ~qfrPendingQuantumFrame;
            ~qfrPendingQuantumFrame = nil;
            ~qfrQuantumCommitScheduled = false;
            pending !? { commitQuantumFrame.value(pending) };
        }.defer;
    };
};

scheduleConfigurationCommit = { |frame|
    ~qfrPendingConfigurationFrame = frame;
    if(~qfrConfigurationCommitScheduled.not) {
        ~qfrConfigurationCommitScheduled = true;
        {
            var pending = ~qfrPendingConfigurationFrame;
            ~qfrPendingConfigurationFrame = nil;
            ~qfrConfigurationCommitScheduled = false;
            pending !? { commitConfigurationFrame.value(pending) };
        }.defer;
    };
};

closePanel = {
    ~qfrWindow !? _.close;
    ~qfrWindow = nil; ~qfrModeView = nil; ~qfrStatus = nil; ~qfrQuantumSlider = nil;
};
closeTemporalControls = { ~qfrTemporalWindow !? _.close; ~qfrTemporalWindow = nil };
closePauliDesk = {
    ~qfrPauliDeskWindow !? _.close;
    ~qfrPauliDeskWindow = nil; ~qfrPauliReadouts = Dictionary.new;
};
closeSourceDock = { ~qfrSourceDockWindow !? _.close; ~qfrSourceDockWindow = nil };
closeGeneratorControls = { ~qfrGeneratorWindow !? _.close; ~qfrGeneratorWindow = nil };
sendVnfHamiltonian = {
    ~qfrVnfControl.sendMsg("/qmw/quantum/v1/control/von_neumann_flow_i/hamiltonian",
        ~qfrVnfOmega1, ~qfrVnfOmega2, ~qfrVnfCoupling);
};
setV2Audition = { |active|
    if(active) {
        if(~qfrPriorQriEnabled.isNil) { ~qfrPriorQriEnabled = ~qriEnabled ? true };
        ~qriEnabled = false;
        ~qriPluckQueue !? _.clear;
        ~qfrV2Audition = true;
    } {
        ~qfrPriorQriEnabled !? { |prior| ~qriEnabled = prior };
        ~qfrPriorQriEnabled = nil;
        ~qfrV2Audition = false;
    };
};

openTemporalControls = {
    if(~qfrTemporalWindow.notNil, { ~qfrTemporalWindow.front }, {
        ~qfrTemporalWindow = Window("V2 Temporal Behavior", Rect(150, 135, 700, 348))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qfrTemporalWindow, Rect(16, 12, 668, 40))
            .string_("ACOUSTIC RESPONSE TO SEALED OBSERVABLES  /  NO CHANGE TO rho, H, OR CURRENT")
            .font_(Font("Helvetica Neue", 12, true)).stringColor_(Color.fromHexString("dcecff"));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(16, 68, 324, 28), "modal memory",
            ControlSpec(0.001, 4.0, \exp, 0.001), { |view| ~qfrMemorySeconds = view.value },
            ~qfrMemorySeconds, labelWidth: 96, numberWidth: 58));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(360, 68, 324, 28), "refractory",
            ControlSpec(0.0, 1.0, \lin, 0.001), { |view| ~qfrRefractorySeconds = view.value },
            ~qfrRefractorySeconds, labelWidth: 92, numberWidth: 58));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(16, 108, 324, 28), "texture spread",
            ControlSpec(0, 8, \lin, 1), { |view|
                ~qfrTextureSpread = view.value.round.asInteger; ~qfrTextureStep = 0
            }, ~qfrTextureSpread, labelWidth: 96, numberWidth: 58));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(360, 108, 324, 28), "texture seed",
            ControlSpec(0, 999, \lin, 1), { |view|
                ~qfrTextureSeed = view.value.round.asInteger; ~qfrTextureStep = 0
            }, ~qfrTextureSeed, labelWidth: 92, numberWidth: 58));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(16, 148, 324, 28), "drift depth",
            ControlSpec(0, 1, \lin, 0.001), { |view| ~qfrDriftDepth = view.value },
            ~qfrDriftDepth, labelWidth: 96, numberWidth: 58));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(360, 148, 324, 28), "drift rate",
            ControlSpec(0, 1.5, \lin, 0.001), { |view| ~qfrDriftRate = view.value },
            ~qfrDriftRate, labelWidth: 92, numberWidth: 58));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(16, 204, 324, 28), "basis current",
            ControlSpec(0, 2, \lin, 0.01), { |view| ~qfrCurrentMix = view.value },
            ~qfrCurrentMix, labelWidth: 96, numberWidth: 58));
        styleSlider.(EZSlider(~qfrTemporalWindow, Rect(360, 204, 324, 28), "QHO flux",
            ControlSpec(0, 2, \lin, 0.01), { |view| ~qfrFluxMix = view.value },
            ~qfrFluxMix, labelWidth: 92, numberWidth: 58));
        StaticText(~qfrTemporalWindow, Rect(16, 258, 668, 68))
            .string_("Memory smooths modal coloration. Refractory removes near-repeat triggers per current/flux edge. Texture uses a seeded deterministic modal offset for eligible events. Drift is a slow resonator focus. All controls are sound-adapter controls.")
            .stringColor_(Color.white.alpha_(0.72));
        ~qfrTemporalWindow.onClose = { ~qfrTemporalWindow = nil };
    });
};

openGeneratorControls = {
    if(~qfrGeneratorWindow.notNil, { ~qfrGeneratorWindow.front }, {
        ~qfrGeneratorWindow = Window("VNF I Time / Metric / Hamiltonian", Rect(165, 120, 700, 392))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qfrGeneratorWindow, Rect(16, 12, 668, 44))
            .string_("VON NEUMANN FLOW I AUTHORITY  /  GENERATOR, MODEL-TIME RATE, READ-ONLY BURES CLOCK")
            .font_(Font("Helvetica Neue", 12, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(~qfrGeneratorWindow, Rect(16, 58, 668, 36))
            .string_("These controls address only the sealed 2-qubit VNF I source. QHO, four-qubit Hilbert/gauge, and resonator texture remain separate authorities.")
            .stringColor_(Color.white.alpha_(0.72));
        styleSlider.(EZSlider(~qfrGeneratorWindow, Rect(16, 108, 324, 28), "model-time x",
            ControlSpec(0.05, 8.0, \exp, 0.001), { |view|
                ~qfrVnfEvolutionRate = view.value;
                ~qfrVnfControl.sendMsg("/qmw/quantum/v1/control/von_neumann_flow_i/evolution_rate", view.value);
            }, ~qfrVnfEvolutionRate, labelWidth: 100, numberWidth: 58));
        styleSlider.(EZSlider(~qfrGeneratorWindow, Rect(360, 108, 324, 28), "Bures d / pulse",
            ControlSpec(0.001, 0.2, \exp, 0.0005), { |view|
                ~qfrVnfBuresDistance = view.value;
                ~qfrVnfControl.sendMsg("/qmw/quantum/v1/control/von_neumann_flow_i/bures_distance", view.value);
            }, ~qfrVnfBuresDistance, labelWidth: 112, numberWidth: 58));
        styleSlider.(EZSlider(~qfrGeneratorWindow, Rect(16, 148, 324, 28), "Bures clock x",
            ControlSpec(0.01, 8.0, \exp, 0.001), { |view|
                ~qfrVnfBuresClockScale = view.value;
                ~qfrVnfControl.sendMsg("/qmw/quantum/v1/control/von_neumann_flow_i/bures_clock_scale", view.value);
            }, ~qfrVnfBuresClockScale, labelWidth: 100, numberWidth: 58));
        StaticText(~qfrGeneratorWindow, Rect(360, 150, 324, 24))
            .string_("Bures pulses render in Quantum / Bures mode only.")
            .font_(Font("Menlo", 9)).stringColor_(Color.fromHexString("ffd166"));
        StaticText(~qfrGeneratorWindow, Rect(16, 198, 668, 24))
            .string_("H = omega1 ZI + omega2 IZ + J XX   /   updates at the next sealed model-time boundary")
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("8ecae6"));
        styleSlider.(EZSlider(~qfrGeneratorWindow, Rect(16, 232, 210, 28), "omega1 (ZI)",
            ControlSpec(-4, 4, \lin, 0.001), { |view| ~qfrVnfOmega1 = view.value; sendVnfHamiltonian.value },
            ~qfrVnfOmega1, labelWidth: 86, numberWidth: 58));
        styleSlider.(EZSlider(~qfrGeneratorWindow, Rect(244, 232, 210, 28), "omega2 (IZ)",
            ControlSpec(-4, 4, \lin, 0.001), { |view| ~qfrVnfOmega2 = view.value; sendVnfHamiltonian.value },
            ~qfrVnfOmega2, labelWidth: 86, numberWidth: 58));
        styleSlider.(EZSlider(~qfrGeneratorWindow, Rect(472, 232, 212, 28), "J (XX)",
            ControlSpec(-4, 4, \lin, 0.001), { |view| ~qfrVnfCoupling = view.value; sendVnfHamiltonian.value },
            ~qfrVnfCoupling, labelWidth: 58, numberWidth: 58));
        StaticText(~qfrGeneratorWindow, Rect(16, 284, 668, 72))
            .string_("model-time x is the master evolution pace: it changes how much VNF I model time advances per wall second, so both live-current and Quantum / Bures observations change. Bures controls measure rho snapshots and never alter rho. The three H coefficients are the actual VNF I Hamiltonian, not the four-qubit interaction-omega sound/field control.")
            .stringColor_(Color.white.alpha_(0.72));
        ~qfrGeneratorWindow.onClose = { ~qfrGeneratorWindow = nil };
    });
};

openPauliDesk = {
    var labels = List.new, height;
    ~qfrFrame[\paulis].do { |pauli|
        var name = pauli[\label].asString;
        if(labels.includes(name).not) { labels.add(name) };
    };
    labels = labels.asArray.sort;
    if(labels.isEmpty) { labels = ["waiting for sealed Pauli frame"] };
    if(~qfrPauliDeskWindow.notNil, { ~qfrPauliDeskWindow.front }, {
        height = (124 + (labels.size * 30)).min(620);
        ~qfrPauliDeskWindow = Window("V2 Pauli Desk", Rect(185, 95, 720, height))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qfrPauliDeskWindow, Rect(16, 12, 688, 42))
            .string_("READ-ONLY PAULI OBSERVABLES  /  PER-STRING SONIC ENABLE + GAIN  /  STABLE MODE IDENTITY")
            .font_(Font("Helvetica Neue", 12, true)).stringColor_(Color.fromHexString("dcecff"));
        Button(~qfrPauliDeskWindow, Rect(16, 56, 384, 24))
            .states_([[
                "PAULI COLOR ONLY (events ungated)", Color.white, Color.fromHexString("263241")
            ], [
                "ACTIVE PAULI GATES V2 EVENTS", Color.black, Color.fromHexString("80ed99")
            ]])
            .value_(~qfrPauliGateEnabled.asInteger)
            .action_({ |button| ~qfrPauliGateEnabled = button.value > 0 });
        StaticText(~qfrPauliDeskWindow, Rect(414, 58, 290, 20))
            .string_("all muted = V2 event energy 0")
            .font_(Font("Menlo", 9)).stringColor_(Color.fromHexString("ffd166"));
        labels.do { |name, index|
            var y = 94 + (index * 30), mode = modeForLabel.value(name);
            Button(~qfrPauliDeskWindow, Rect(16, y, 152, 24))
                .states_([["%  M%  active".format(name, mode + 1), Color.black, Color.fromHexString("80ed99")],
                    ["%  M%  muted".format(name, mode + 1), Color.fromHexString("ffd166"), Color.fromHexString("532b35")]])
                .value_((~qfrPauliMuted[name] ? false).asInteger)
                .action_({ |button| ~qfrPauliMuted[name] = button.value > 0 });
            styleSlider.(EZSlider(~qfrPauliDeskWindow, Rect(180, y, 220, 24), "gain",
                ControlSpec(0, 2, \lin, 0.01), { |view| ~qfrPauliGains[name] = view.value },
                ~qfrPauliGains[name] ? 1.0, labelWidth: 42, numberWidth: 46));
            ~qfrPauliReadouts[name] = StaticText(~qfrPauliDeskWindow, Rect(414, y + 3, 290, 20))
                .font_(Font("Menlo", 9)).stringColor_(Color.fromHexString("8ecae6"))
                .string_(if(name == "waiting for sealed Pauli frame", { "" }, { "awaiting refresh" }));
        };
        ~qfrPauliDeskWindow.onClose = {
            ~qfrPauliDeskWindow = nil; ~qfrPauliReadouts = Dictionary.new
        };
        ~qfrLastPauliDeskRefresh = 0.0;
        refreshPauliDesk.value;
    });
};

openSourceDock = {
    if(~qfrSourceDockWindow.notNil, { ~qfrSourceDockWindow.front }, {
        ~qfrSourceDockWindow = Window("QMW Source / Observer / Excitation Dock", Rect(175, 160, 700, 382))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qfrSourceDockWindow, Rect(16, 12, 668, 44))
            .string_("ONE SESSION, SEPARATE AUTHORITIES  /  OPEN AN ADAPTER; DO NOT COERCE ONE WORLD INTO ANOTHER")
            .font_(Font("Helvetica Neue", 12, true)).stringColor_(Color.fromHexString("dcecff"));
        Button(~qfrSourceDockWindow, Rect(16, 70, 210, 28)).states_([["HILBERT / PROJECTIVE", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qriOpenPanel !? { |function| function.value } });
        Button(~qfrSourceDockWindow, Rect(240, 70, 210, 28)).states_([["PROJECTION / GAUGE", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qriOpenMeasurementControls !? { |function| function.value } });
        Button(~qfrSourceDockWindow, Rect(464, 70, 220, 28)).states_([["FOUR-QUBIT PREPARATION", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qriOpenPreparationControls !? { |function| function.value } });
        Button(~qfrSourceDockWindow, Rect(16, 110, 210, 28)).states_([["BOSONIC QHO + FM", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qriOpenQHOControls !? { |function| function.value } });
        Button(~qfrSourceDockWindow, Rect(240, 110, 210, 28)).states_([["MEMBRANE PERFORMANCE", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qrmOpenPerformance !? { |function| function.value } });
        Button(~qfrSourceDockWindow, Rect(464, 110, 220, 28)).states_([["GEOMETRIC TUNING", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qrmOpenTuning !? { |function| function.value } });
        Button(~qfrSourceDockWindow, Rect(16, 150, 210, 28))
            .states_([["20-MODE MIXER", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qrmWindow !? { |window| window.front } });
        Button(~qfrSourceDockWindow, Rect(240, 150, 444, 28))
            .states_([[
                "ALL ADAPTERS AUDIBLE", Color.white, Color.fromHexString("263241")
            ], [
                "V2 AUDITION / V1 HILBERT PLUCKS MUTED", Color.black, Color.fromHexString("80ed99")
            ]])
            .value_(~qfrV2Audition.asInteger)
            .action_({ |button| setV2Audition.value(button.value > 0) });
        Button(~qfrSourceDockWindow, Rect(16, 190, 668, 28))
            .states_([["VNF I TIME / METRIC / HAMILTONIAN", Color.white, Color.fromHexString("263241")]])
            .action_({ openGeneratorControls.value });
        Button(~qfrSourceDockWindow, Rect(16, 228, 668, 28))
            .states_([["RELATIONAL LAPLACIAN SPECTRUM (V3)", Color.white, Color.fromHexString("263241")]])
            .action_({ ~qrsOpenPanel !? { |function| function.value } });
        StaticText(~qfrSourceDockWindow, Rect(16, 268, 668, 94))
            .string_("Von Neumann Flow I is a 2-qubit Pauli/current observer. The QHO sidecar is a separate 16-level Fock source. The Hilbert / projective panel owns its four-qubit and gauge-capable observers. V3 relational spectrum observes that native four-qubit rho and shapes only admitted resonator events. Each is available here, but this dock does not claim that a 2-qubit frame is four-qubit geometry.")
            .stringColor_(Color.white.alpha_(0.72));
        ~qfrSourceDockWindow.onClose = { ~qfrSourceDockWindow = nil };
    });
};
openPanel = {
    if(~qfrWindow.notNil, { ~qfrWindow.front }, {
        ~qfrWindow = Window("Unified Instrument Resonator V2", Rect(100, 110, 760, 330))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qfrWindow, Rect(16, 12, 728, 42))
            .string_("SEALED QUANTUM FRAME -> PAULI VELOCITY / BASIS CURRENT / QHO FLUX -> V1 RESONATOR")
            .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(~qfrWindow, Rect(16, 56, 728, 38))
            .string_("Pauli and population lanes color the 20 resonator weights. Only accumulated basis current or declared QHO flux events pluck. These are sonic mappings, not state dynamics.")
            .stringColor_(Color.white.alpha_(0.72));
        Button(~qfrWindow, Rect(16, 106, 160, 26))
            .states_([["V2 EXCITATION MUTED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["V2 EXCITATION ACTIVE", Color.black, Color.fromHexString("80ed99")]])
            .value_(~qfrEnabled.asInteger).action_({ |button| ~qfrEnabled = button.value > 0 });
        ~qfrQuantumSlider = styleSlider.(EZSlider(~qfrWindow, Rect(192, 106, 248, 26), "current quantum",
            ControlSpec(0.001, 0.2, \exp, 0.0005), { |view| ~qfrCurrentQuantum = view.value },
            ~qfrCurrentQuantum, labelWidth: 94, numberWidth: 58));
        styleSlider.(EZSlider(~qfrWindow, Rect(452, 106, 292, 26), "Pauli color",
            ControlSpec(0, 2, \lin, 0.01), { |view| ~qfrPauliMix = view.value },
            ~qfrPauliMix, labelWidth: 76, numberWidth: 58));
        Button(~qfrWindow, Rect(16, 140, 160, 26)).states_([["PAULI DESK", Color.white, Color.fromHexString("263241")]])
            .action_({ openPauliDesk.value });
        Button(~qfrWindow, Rect(188, 140, 180, 26)).states_([["TEMPORAL BEHAVIOR", Color.white, Color.fromHexString("263241")]])
            .action_({ openTemporalControls.value });
        Button(~qfrWindow, Rect(380, 140, 364, 26)).states_([["SOURCE / OBSERVER / EXCITATION DOCK", Color.white, Color.fromHexString("263241")]])
            .action_({ openSourceDock.value });
        StaticText(~qfrWindow, Rect(16, 178, 728, 18)).string_("M1-M20 V2 excitation descriptor (display-normalized)")
            .stringColor_(Color.fromHexString("8ecae6"));
        ~qfrModeView = MultiSliderView(~qfrWindow, Rect(16, 202, 728, 54))
            .size_(modeCount).isFilled_(true).fillColor_(Color.fromHexString("ff67d4"))
            .background_(Color.fromHexString("080b10"));
        ~qfrStatus = StaticText(~qfrWindow, Rect(16, 274, 728, 24))
            .font_(Font("Menlo", 9)).stringColor_(Color.fromHexString("80ed99"));
        ~qfrWindow.onClose = { ~qfrWindow = nil; ~qfrModeView = nil; ~qfrStatus = nil };
        updateView.value;
    });
};
~qfrOpenPanel = openPanel;
~qfrOpenTemporalControls = openTemporalControls;
~qfrOpenPauliDesk = openPauliDesk;
~qfrOpenSourceDock = openSourceDock;
~qfrOpenGeneratorControls = openGeneratorControls;

OSCdef(\qfrQuantumBeginV2, { |msg|
    var valid = (msg.size >= 8) and: { msg[3].asString == quantumSchema }
        and: { msg[1].asInteger > ~qfrLastQuantumRevision }
        and: { msg[5].asInteger <= 16 } and: { msg[6].asInteger <= 16 } and: { msg[7].asInteger <= 16 };
    ~qfrQuantumStage = if(valid, {
        (revision: msg[1].asInteger, time: msg[2].asFloat,
            expectedPopulation: msg[5].asInteger, expectedPauli: msg[6].asInteger,
            expectedCurrent: msg[7].asInteger, populations: Array.new, paulis: Array.new,
            currents: Array.new, diagnostics: nil, bures: nil,
            deadline: Main.elapsedTime + ~qfrStageTimeout)
    }, { nil });
}, quantumRoot ++ "/frame/begin", recvPort: quantumPort);

OSCdef(\qfrQuantumDiagnosticsV2, { |msg|
    if(~qfrQuantumStage.notNil and: { msg[1].asInteger == ~qfrQuantumStage[\revision] }) {
        ~qfrQuantumStage[\diagnostics] = msg.copyRange(2, msg.size - 1).collect(_.asFloat)
    };
}, quantumRoot ++ "/diagnostics", recvPort: quantumPort);

OSCdef(\qfrQuantumBuresV2, { |msg|
    if(~qfrQuantumStage.notNil and: { msg[1].asInteger == ~qfrQuantumStage[\revision] }
        and: { msg.size >= 8 }) {
        ~qfrQuantumStage[\bures] = (
            delta: msg[2].asFloat, intrinsic: msg[3].asFloat, remainder: msg[4].asFloat,
            pulses: msg[5].asInteger, distance: msg[6].asFloat, clockScale: msg[7].asFloat
        );
    };
}, quantumRoot ++ "/metric/bures", recvPort: quantumPort);

OSCdef(\qfrQuantumPopulationV2, { |msg|
    if(~qfrQuantumStage.notNil and: { msg[1].asInteger == ~qfrQuantumStage[\revision] }
        and: { ~qfrQuantumStage[\populations].size < ~qfrQuantumStage[\expectedPopulation] }) {
        ~qfrQuantumStage[\populations] = ~qfrQuantumStage[\populations].add((
            lane: msg[2].asInteger, index: msg[3].asInteger, value: msg[4].asFloat, rate: msg[5].asFloat
        ));
    };
}, quantumRoot ++ "/population", recvPort: quantumPort);

OSCdef(\qfrQuantumPauliV2, { |msg|
    if(~qfrQuantumStage.notNil and: { msg[1].asInteger == ~qfrQuantumStage[\revision] }
        and: { ~qfrQuantumStage[\paulis].size < ~qfrQuantumStage[\expectedPauli] }) {
        ~qfrQuantumStage[\paulis] = ~qfrQuantumStage[\paulis].add((
            lane: msg[2].asInteger, label: msg[3].asString, value: msg[4].asFloat,
            unitaryVelocity: msg[5].asFloat, dissipativeVelocity: msg[6].asFloat,
            velocity: msg[7].asFloat, conserved: msg[8].asInteger
        ));
    };
}, quantumRoot ++ "/pauli", recvPort: quantumPort);

OSCdef(\qfrQuantumCurrentV2, { |msg|
    if(~qfrQuantumStage.notNil and: { msg[1].asInteger == ~qfrQuantumStage[\revision] }
        and: { ~qfrQuantumStage[\currents].size < ~qfrQuantumStage[\expectedCurrent] }) {
        ~qfrQuantumStage[\currents] = ~qfrQuantumStage[\currents].add((
            lane: msg[2].asInteger, destination: msg[3].asInteger,
            source: msg[4].asInteger, magnitude: msg[5].asFloat
        ));
    };
}, quantumRoot ++ "/current", recvPort: quantumPort);

OSCdef(\qfrQuantumEndV2, { |msg|
    var committed;
    if(~qfrQuantumStage.notNil and: { msg[1].asInteger == ~qfrQuantumStage[\revision] }
        and: { ~qfrQuantumStage[\populations].size == ~qfrQuantumStage[\expectedPopulation] }
        and: { ~qfrQuantumStage[\paulis].size == ~qfrQuantumStage[\expectedPauli] }
        and: { ~qfrQuantumStage[\currents].size == ~qfrQuantumStage[\expectedCurrent] }) {
        committed = ~qfrQuantumStage; ~qfrQuantumStage = nil;
        ~qfrLastQuantumRevision = committed[\revision];
        scheduleQuantumCommit.value(committed);
    } { ~qfrQuantumStage = nil };
}, quantumRoot ++ "/frame/end", recvPort: quantumPort);

OSCdef(\qfrConfigurationBeginV2, { |msg|
    var valid = (msg.size >= 6) and: { msg[3].asString == configurationSchema }
        and: { msg[1].asInteger > ~qfrLastConfigurationRevision }
        and: { msg[4].asInteger <= 16 } and: { msg[5].asInteger <= 16 };
    ~qfrConfigurationStage = if(valid, {
        (revision: msg[1].asInteger, time: msg[2].asFloat, expectedRegions: msg[4].asInteger,
            expectedEvents: msg[5].asInteger, regions: Array.new, events: Array.new,
            summary: nil, deadline: Main.elapsedTime + ~qfrStageTimeout)
    }, { nil });
}, configurationRoot ++ "/frame/begin", recvPort: configurationPort);

OSCdef(\qfrConfigurationSummaryV2, { |msg|
    if(~qfrConfigurationStage.notNil and: { msg[1].asInteger == ~qfrConfigurationStage[\revision] }) {
        ~qfrConfigurationStage[\summary] = msg.copyRange(2, msg.size - 1).collect(_.asFloat)
    };
}, configurationRoot ++ "/summary", recvPort: configurationPort);

OSCdef(\qfrConfigurationRegionV2, { |msg|
    if(~qfrConfigurationStage.notNil and: { msg[1].asInteger == ~qfrConfigurationStage[\revision] }
        and: { ~qfrConfigurationStage[\regions].size < ~qfrConfigurationStage[\expectedRegions] }) {
        ~qfrConfigurationStage[\regions] = ~qfrConfigurationStage[\regions].add((
            index: msg[2].asInteger, population: msg[3].asFloat, flux: msg[4].asFloat
        ));
    };
}, configurationRoot ++ "/region", recvPort: configurationPort);

OSCdef(\qfrConfigurationEventV2, { |msg|
    if(~qfrConfigurationStage.notNil and: { msg[1].asInteger == ~qfrConfigurationStage[\revision] }
        and: { ~qfrConfigurationStage[\events].size < ~qfrConfigurationStage[\expectedEvents] }) {
        ~qfrConfigurationStage[\events] = ~qfrConfigurationStage[\events].add((
            index: msg[2].asInteger, source: msg[3].asInteger, destination: msg[4].asInteger,
            direction: msg[5].asInteger, magnitude: msg[6].asFloat
        ));
    };
}, configurationRoot ++ "/event", recvPort: configurationPort);

OSCdef(\qfrConfigurationEndV2, { |msg|
    var committed;
    if(~qfrConfigurationStage.notNil and: { msg[1].asInteger == ~qfrConfigurationStage[\revision] }
        and: { ~qfrConfigurationStage[\regions].size == ~qfrConfigurationStage[\expectedRegions] }
        and: { ~qfrConfigurationStage[\events].size == ~qfrConfigurationStage[\expectedEvents] }) {
        committed = ~qfrConfigurationStage; ~qfrConfigurationStage = nil;
        ~qfrLastConfigurationRevision = committed[\revision];
        scheduleConfigurationCommit.value(committed);
    } { ~qfrConfigurationStage = nil };
}, configurationRoot ++ "/frame/end", recvPort: configurationPort);

~qfrWatchdog = Routine({
    loop {
        if(~qfrQuantumStage.notNil and: { Main.elapsedTime > ~qfrQuantumStage[\deadline] }) {
            ~qfrQuantumStage = nil
        };
        if(~qfrConfigurationStage.notNil and: { Main.elapsedTime > ~qfrConfigurationStage[\deadline] }) {
            ~qfrConfigurationStage = nil
        };
        0.20.wait;
    }
}).play(AppClock);

~qfrCleanup = {
    [\qfrQuantumBeginV2, \qfrQuantumDiagnosticsV2, \qfrQuantumBuresV2, \qfrQuantumPopulationV2,
        \qfrQuantumPauliV2, \qfrQuantumCurrentV2, \qfrQuantumEndV2,
        \qfrConfigurationBeginV2, \qfrConfigurationSummaryV2, \qfrConfigurationRegionV2,
        \qfrConfigurationEventV2, \qfrConfigurationEndV2].do { |key| OSCdef(key).free };
    ~qfrWatchdog !? _.stop; ~qfrWatchdog = nil;
    ~qfrQuantumStage = nil; ~qfrConfigurationStage = nil;
    ~qfrPendingQuantumFrame = nil; ~qfrPendingConfigurationFrame = nil;
    ~qfrQuantumCommitScheduled = false; ~qfrConfigurationCommitScheduled = false;
    ~qfrCurrentAccumulator = IdentityDictionary.new;
    ~qfrLastEventTime = IdentityDictionary.new;
    ~qfrPreviousDrives = Array.fill(modeCount, Complex(0, 0));
    ~qfrLastDriveWallTime = nil;
    setV2Audition.value(false);
    closePanel.value;
    closeTemporalControls.value; closePauliDesk.value; closeSourceDock.value; closeGeneratorControls.value;
};

{ openPanel.value }.defer;
"QMW Unified Instrument Resonator V2 listening on QuantumFrame UDP % and QHO configuration UDP %"
    .format(quantumPort, configurationPort).postln;
)
