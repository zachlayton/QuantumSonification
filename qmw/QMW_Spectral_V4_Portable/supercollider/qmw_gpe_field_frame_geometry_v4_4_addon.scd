/*
QMW V4.4 FieldFrame Geometry add-on.

This is an additive observer/renderer over atomic FieldFrame OSC v2 messages
on UDP 17869. It leaves the GPE solver and the inherited V4.4 QFT instrument
unchanged. Flow, verified geometry modes, and energy are blended only into
the existing onset-sampled pulse-material state; already sounding tails do
not change.
*/
(
var baseStop = ~qmwQFTV3Stop;
var baseUpdatePulseMaterial = ~qmwQFTV44UpdateGPEPulseTimbre;

~qmwQFTV44FieldFramePort = 17869;
~qmwQFTV44FieldFrameRoot = "/qmw/gpe/field_frame";
~qmwQFTV44FieldFrameRevision = -1;
~qmwQFTV44FieldFrameValid = false;
// Disabled by default so loading this observational sidecar is a true
// no-change baseline for the inherited V4.4 instrument.
~qmwQFTV44FieldFrameEnabled = 0;
~qmwQFTV44FieldFrameFlowDepth = 0.45;
~qmwQFTV44FieldFrameModeDepth = 0.45;
~qmwQFTV44FieldFrameEnergyDepth = 0.45;
~qmwQFTV44FieldFramePhaseDepth = 0.45;
~qmwQFTV44FieldFrameSelectedPhase = 0;
~qmwQFTV44FieldFrameHistory = Array.fill(4, { List.new });
// Rendering is intentionally decimated: every FieldFrame is still accepted
// and stored, but redrawing four long traces and sixteen spectrum bars on
// each 30 Hz transaction can monopolize sclang's language thread.
~qmwQFTV44FieldFrameRefreshInterval = 0.125;
~qmwQFTV44FieldFrameLastRefresh = -1e9;
~qmwQFTV44FieldFrame = (
    time: 0.0, phase: 0.0, norm: 0.0, energy: 0.0,
    flux: 0.0, fourierPower: Array.fill(16, 0.0),
    geometryPower: Array.fill(16, 0.0),
    geometryEigenvalues: Array.fill(16, 0.0),
    geometryPhase: Array.fill(16, 0.0),
    geometryPhaseVelocity: Array.fill(16, 0.0), geometryAvailable: false
);

~qmwQFTV44FieldFramePhaseIndex = { |phase|
    var targets = [0.0, pi / 4.0, pi / 2.0, pi];
    targets.collect { |target| (phase - target).abs }.minIndex
};

// Promote only a received, non-degenerate geometry eigenspectrum into the
// separate V4.3 pitch adapter. This does not select the geometry source or
// alter field evolution; the performer still chooses "geometry spectrum" and
// presses APPLY PITCH SOURCE.
~qmwQFTV44DetectGeometrySpectrum = { |eigenvalues|
    var siteCount = (~qmwQFTSiteCount ? 16).asInteger;
    var values = eigenvalues.copyRange(0, siteCount - 1);
    var origin, offsets, positiveOffsets, referenceGap, ratios;
    if(values.size != siteCount or: { values.any { |value| value.isNaN } }, {
        ~qmwQFTV43GeometryPitchRatios = nil;
        ~qmwQFTV43GeometryDescription = "geometry eigenspectrum invalid";
    }, {
        origin = values.minItem;
        offsets = values.collect { |value| (value - origin).max(0.0) };
        positiveOffsets = offsets.select { |value| value > 1e-9 };
        if(positiveOffsets.isEmpty, {
            ~qmwQFTV43GeometryPitchRatios = nil;
            ~qmwQFTV43GeometryDescription = "geometry eigenspectrum degenerate";
        }, {
            // Eigenvalue gaps are energies. The square-root conversion yields
            // oscillator-frequency ratios relative to the smallest resolved
            // nonzero gap, retaining the actual geometry spectrum ordering.
            referenceGap = positiveOffsets.minItem;
            ratios = offsets.collect { |offset|
                (1.0 + (offset / referenceGap)).sqrt.clip(0.25, 16.0)
            };
            ~qmwQFTV43GeometryPitchRatios = ratios;
            ~qmwQFTV43GeometryDescription =
                "verified GPE eigenvalues / lambda0 % / gap %"
                .format(origin.round(0.0001), referenceGap.round(0.0001));
            if(~qmwQFTV43PitchSource == 5, {
                ~qmwQFTV43ApplyPitchSource !? _.value;
            });
        });
    });
};

~qmwQFTV44FieldFrameRefresh = {
    var now = Main.elapsedTime;
    if((now - ~qmwQFTV44FieldFrameLastRefresh)
        >= ~qmwQFTV44FieldFrameRefreshInterval, {
        ~qmwQFTV44FieldFrameLastRefresh = now;
        { ~qmwQFTV44FieldFrameView !? { |view| view.refresh }; ~qmwQFTV44FieldFrameStatus !? { |view|
            var frame = ~qmwQFTV44FieldFrame;
            var modePower = if(frame[\geometryAvailable], { frame[\geometryPower] }, { frame[\fourierPower] });
            var modeKind = if(frame[\geometryAvailable], { "geometry" }, { "Fourier" });
            var dominant = modePower.maxIndex ? 0;
            view.string_("FRAME %  θ %  norm %  E %  flux %  dominant % mode %".format(
                ~qmwQFTV44FieldFrameRevision, frame[\phase].round(0.001), frame[\norm].round(0.00001),
                frame[\energy].round(0.0001), frame[\flux].round(0.0001), modeKind, dominant
            ))
        } }.defer;
    });
};

// This wrapper preserves V4.4's previous pulse preparation, then adds the
// FieldFrame contribution. It remains a downstream sound-design adapter.
~qmwQFTV44UpdateGPEPulseTimbre = {
    var frame = ~qmwQFTV44FieldFrame;
    var powers = if(frame[\geometryAvailable], { frame[\geometryPower] }, { frame[\fourierPower] });
    var dominant = powers.maxIndex ? 0;
    var flowAmount = (frame[\flux].abs * 3.0).tanh;
    var modeAmount = powers.maxItem.clip(0, 1).sqrt;
    var energyAmount = (frame[\energy].max(0) / (1 + frame[\energy].max(0))).clip(0, 1);
    var modePhase = (frame[\geometryPhase][dominant] ? 0.0);
    var phaseVelocity = (frame[\geometryPhaseVelocity][dominant] ? 0.0);
    // sin(arg a_n) respects the circular phase coordinate; the bounded rate
    // term makes phase motion audible without treating phase as a pitch source.
    var phaseOrbit = (modePhase.sin + (phaseVelocity * 0.25).tanh).clip(-1, 1);
    var ringDetune = 2.pow((~qmwQFTV44FieldFramePhaseDepth.clip(0, 1) * phaseOrbit) / 12);
    var enabled = ~qmwQFTV44FieldFrameEnabled.clip(0, 1);
    var current;
    baseUpdatePulseMaterial.value;
    current = ~qmwQFTV44GPEPulseTimbre.copy;
    if(enabled > 0, {
        ~qmwQFTV44GPEPulseTimbre = (
            ringMix: (current[\ringMix] + (enabled * ~qmwQFTV44FieldFrameFlowDepth.clip(0, 1) * flowAmount)).clip(0, 1),
            ringHarmonic: (current[\ringHarmonic] + (enabled * ~qmwQFTV44FieldFrameModeDepth.clip(0, 1) * dominant)).clip(1, 16),
            ringDetune: (current[\ringDetune] ? 1.0) * ringDetune,
            wavefoldMix: (current[\wavefoldMix] + (enabled * ~qmwQFTV44FieldFrameEnergyDepth.clip(0, 1) * energyAmount)).clip(0, 1),
            wavefoldDrive: (current[\wavefoldDrive] + (12 * enabled * ~qmwQFTV44FieldFrameEnergyDepth.clip(0, 1) * energyAmount * (0.25 + modeAmount))).clip(1, 20),
            fuzzMix: (current[\fuzzMix] + (0.25 * enabled * modeAmount)).clip(0, 1)
        )
    });
};

~qmwQFTV44FieldFrameDraw = { |view|
    var bounds = view.bounds;
    var width = bounds.width, height = bounds.height;
    // The view and OSC callbacks share this observer buffer.  Keep drawing
    // resilient to a stale GUI/Pen object from an interrupted repaint rather
    // than throwing on every 30 Hz refresh and starving the audio language.
    var histories = ~qmwQFTV44FieldFrameHistory.collect { |history|
        history.select { |entry|
            entry.isKindOf(Event) and: {
                entry[\time].isNumber and: {
                    entry[\flux].isNumber and: { entry[\energy].isNumber }
                }
            }
        }
    };
    var colors = [Color.green(0.8), Color.cyan(0.8), Color.yellow(0.85), Color.magenta(0.8)];
    var selected = ~qmwQFTV44FieldFrameSelectedPhase.clip(0, histories.size - 1);
    var selectedHistory = histories[selected];
    var allValues = histories.collect { |history| history.collect { |entry| entry[\flux] } }.flat;
    var maxFlux = (allValues.collect(_.abs).maxItem ? 0.01).max(0.01);
    var top = 24, fluxHeight = 104, lowerTop = 164, lowerHeight = height - 188;
    var energyWidth = ((width - 32) * 0.46), modeX = 22 + ((width - 32) * 0.49);
    var modeWidth = width - modeX - 12;
    var energyValues = selectedHistory.collect { |entry| entry[\energy] };
    var minEnergy = energyValues.minItem ? 0.0, maxEnergy = energyValues.maxItem ? 1.0;
    var frame = ~qmwQFTV44FieldFrame;
    var geometryAvailable = frame[\geometryAvailable] ? false;
    var modePower = if(geometryAvailable, { frame[\geometryPower] }, { frame[\fourierPower] });
    var maxMode = (modePower.maxItem ? 0.01).max(0.01);
    var leader = modePower.maxIndex ? 0;
    Pen.fillColor = Color.black;
    Pen.fillRect(Rect(0, 0, width, height));
    Pen.color = Color.grey(0.33);
    Pen.strokeRect(Rect(10, top, width - 20, fluxHeight));
    Pen.strokeRect(Rect(10, lowerTop, energyWidth, lowerHeight));
    Pen.strokeRect(Rect(modeX, lowerTop, modeWidth, lowerHeight));
    Pen.stringAtPoint("FLOW → TIME  /  regional flux histories", Point(16, 18), Font("Helvetica Neue", 12, true), Color.grey(0.9));
    if(allValues.notEmpty, {
        histories.do { |history, index|
            if(history.size > 1, {
                var time0 = history.first[\time], time1 = history.last[\time];
                var duration = (time1 - time0).max(0.001);
                Pen.color = colors[index].alpha_(if(index == selected, 1.0, 0.42));
                Pen.width = if(index == selected, 2.5, 1.0);
                Pen.moveTo(Point(10, top + (fluxHeight / 2)));
                history.do { |entry|
                    var x = 10 + (((entry[\time] - time0) / duration) * (width - 20));
                    var y = top + (fluxHeight / 2) - ((entry[\flux] / maxFlux) * ((fluxHeight / 2) - 8));
                    Pen.lineTo(Point(x, y));
                };
                Pen.stroke;
                Pen.stringAtPoint("θ=" ++ ["0", "π/4", "π/2", "π"][index], Point(width - 52, top + 18 + (index * 18)), Font("Menlo", 10), colors[index]);
            })
        }
    });
    Pen.stringAtPoint("ENERGY → MATERIALITY  /  selected energy trace", Point(16, lowerTop - 6), Font("Helvetica Neue", 12, true), Color.grey(0.9));
    if(selectedHistory.size > 1, {
        var time0 = selectedHistory.first[\time], time1 = selectedHistory.last[\time];
        var duration = (time1 - time0).max(0.001);
        var energySpan = (maxEnergy - minEnergy).max(0.0001);
        Pen.color = colors[selected];
        Pen.width = 2.5;
        Pen.moveTo(Point(10, lowerTop + lowerHeight - 12));
        selectedHistory.do { |entry|
            var x = 10 + (((entry[\time] - time0) / duration) * energyWidth);
            var y = lowerTop + lowerHeight - 12 - (((entry[\energy] - minEnergy) / energySpan) * (lowerHeight - 30));
            Pen.lineTo(Point(x, y));
        };
        Pen.stroke;
        Pen.stringAtPoint("E %.4f → %.4f".format(selectedHistory.first[\energy], selectedHistory.last[\energy]), Point(18, lowerTop + lowerHeight - 4), Font("Menlo", 10), Color.grey(0.82));
    });
    Pen.stringAtPoint(if(geometryAvailable, { "MODES → SPECTRUM  /  verified geometry-mode power" }, { "MODES → SPECTRUM  /  Fourier power (no geometry basis supplied)" }), Point(modeX + 6, lowerTop - 6), Font("Helvetica Neue", 12, true), Color.grey(0.9));
    modePower.do { |power, index|
        var barWidth = (modeWidth - 16) / modePower.size;
        var barHeight = (power / maxMode).clip(0, 1) * (lowerHeight - 32);
        Pen.fillColor = colors[selected].alpha_(0.85);
        Pen.fillRect(Rect(modeX + 8 + (index * barWidth), lowerTop + lowerHeight - 18 - barHeight, barWidth - 3, barHeight));
        Pen.stringAtPoint(index.asString, Point(modeX + 10 + (index * barWidth), lowerTop + lowerHeight - 4), Font("Menlo", 9), Color.grey(0.75));
    };
    Pen.stringAtPoint(if(geometryAvailable, {
        "dominant mode %; eigenvalue %; power %".format(leader, frame[\geometryEigenvalues][leader].round(0.0001), modePower[leader].round(0.0001))
    }, {
        "dominant Fourier lane %; power %".format(leader, modePower[leader].round(0.0001))
    }), Point(modeX + 8, lowerTop + 16), Font("Menlo", 10), Color.grey(0.82));
};

~qmwQFTV44OpenFieldFrameGeometryPanel = {
    var window, selected;
    ~qmwQFTV44FieldFrameWindow !? { |old| old.close };
    window = Window("QMW V4.4 — GPE FieldFrame Geometry", Rect(760, 110, 660, 610)).front;
    window.background_(Color.grey(0.11));
    StaticText(window, Rect(18, 14, 620, 24)).string_("PHASE COLLISION I / FIELD FRAME v2 / VERIFIED GEOMETRY MODES")
        .font_(Font("Helvetica Neue", 12, true)).stringColor_(Color.cyan(0.82));
    StaticText(window, Rect(18, 42, 620, 34)).string_("Flow → pulse time; mode power → spectrum; mode phase/rate → ring detune; energy → material. All controls are downstream of the GPE field.")
        .stringColor_(Color.grey(0.78));
    Button(window, Rect(18, 82, 186, 28)).states_([["FIELD FRAME MATERIAL OFF", Color.grey(0.8), Color.grey(0.2)], ["FIELD FRAME MATERIAL ON", Color.black, Color.green(0.7)]])
        .value_(~qmwQFTV44FieldFrameEnabled).action_({ |button| ~qmwQFTV44FieldFrameEnabled = button.value; ~qmwQFTV44UpdateGPEPulseTimbre.value });
    EZSlider(window, Rect(220, 80, 190, 30), "flow → ring", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44FieldFrameFlowDepth), { |control| ~qmwQFTV44FieldFrameFlowDepth = control.value; ~qmwQFTV44UpdateGPEPulseTimbre.value }, ~qmwQFTV44FieldFrameFlowDepth, labelWidth: 74, numberWidth: 42);
    EZSlider(window, Rect(420, 80, 210, 30), "modes → harmonic", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44FieldFrameModeDepth), { |control| ~qmwQFTV44FieldFrameModeDepth = control.value; ~qmwQFTV44UpdateGPEPulseTimbre.value }, ~qmwQFTV44FieldFrameModeDepth, labelWidth: 96, numberWidth: 42);
    EZSlider(window, Rect(220, 114, 190, 30), "energy → fold", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44FieldFrameEnergyDepth), { |control| ~qmwQFTV44FieldFrameEnergyDepth = control.value; ~qmwQFTV44UpdateGPEPulseTimbre.value }, ~qmwQFTV44FieldFrameEnergyDepth, labelWidth: 78, numberWidth: 42);
    EZSlider(window, Rect(420, 114, 210, 30), "phase → ring detune", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44FieldFramePhaseDepth), { |control| ~qmwQFTV44FieldFramePhaseDepth = control.value; ~qmwQFTV44UpdateGPEPulseTimbre.value }, ~qmwQFTV44FieldFramePhaseDepth, labelWidth: 112, numberWidth: 42);
    selected = PopUpMenu(window, Rect(18, 116, 180, 24)).items_(["θ = 0", "θ = π/4", "θ = π/2", "θ = π"])
        .value_(~qmwQFTV44FieldFrameSelectedPhase).action_({ |menu| ~qmwQFTV44FieldFrameSelectedPhase = menu.value; ~qmwQFTV44FieldFrameView.refresh });
    Button(window, Rect(18, 146, 250, 26)).states_([["AUDITION CURRENT MATERIAL", Color.black, Color.cyan(0.65)]]).action_({
        // This is a listener check only: it does not write back into the QFT
        // state or GPE frame. Four short pulses make onset-sampled effects
        // plainly audible, including when V4.4 started muted.
        ~qmwQFTV3SoundEnabled = 1;
        ~qmwQFTV3Synth !? { |synth| synth.set(\soundEnabled, 1) };
        4.do { |index| AppClock.sched(index * 0.24, {
            ~qmwQFTV3RenderPulse.value(0, 0.08, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0); nil
        }) };
    });
    ~qmwQFTV44FieldFrameStatus = StaticText(window, Rect(280, 150, 360, 22)).string_("WAITING FOR FIELD FRAME v2 ON UDP 17869")
        .font_(Font("Menlo", 10)).stringColor_(Color.yellow(0.82));
    ~qmwQFTV44FieldFrameView = UserView(window, Rect(18, 182, 624, 404)).drawFunc_(~qmwQFTV44FieldFrameDraw);
    ~qmwQFTV44FieldFrameWindow = window;
};

OSCdef(\qmwQFTV44FieldFrameBegin, { |msg|
    ~qmwQFTV44FieldFrameRevision = msg[1].asInteger;
    ~qmwQFTV44FieldFrameStage = (
        time: msg[2].asFloat, phase: 0.0, norm: 0.0, energy: 0.0,
        regions: Array.fill(4, { (population: 0.0, flux: 0.0) }),
        fourierPower: Array.fill(16, 0.0),
        geometryPower: Array.fill(16, 0.0), geometryEigenvalues: Array.fill(16, 0.0),
        geometryPhase: Array.fill(16, 0.0), geometryPhaseVelocity: Array.fill(16, 0.0),
        geometryAvailable: false
    );
    ~qmwQFTV44FieldFrameValid = true;
}, ~qmwQFTV44FieldFrameRoot ++ "/begin", recvPort: ~qmwQFTV44FieldFramePort);
OSCdef(\qmwQFTV44FieldFramePhase, { |msg| if(~qmwQFTV44FieldFrameValid and: { msg[1].asInteger == ~qmwQFTV44FieldFrameRevision }) { ~qmwQFTV44FieldFrameStage[\phase] = msg[2].asFloat } }, ~qmwQFTV44FieldFrameRoot ++ "/phase", recvPort: ~qmwQFTV44FieldFramePort);
OSCdef(\qmwQFTV44FieldFrameNorm, { |msg| if(~qmwQFTV44FieldFrameValid and: { msg[1].asInteger == ~qmwQFTV44FieldFrameRevision }) { ~qmwQFTV44FieldFrameStage[\norm] = msg[2].asFloat } }, ~qmwQFTV44FieldFrameRoot ++ "/norm", recvPort: ~qmwQFTV44FieldFramePort);
OSCdef(\qmwQFTV44FieldFrameEnergy, { |msg| if(~qmwQFTV44FieldFrameValid and: { msg[1].asInteger == ~qmwQFTV44FieldFrameRevision }) { ~qmwQFTV44FieldFrameStage[\energy] = msg[2].asFloat } }, ~qmwQFTV44FieldFrameRoot ++ "/energy", recvPort: ~qmwQFTV44FieldFramePort);
4.do { |index|
    OSCdef(("qmwQFTV44FieldFrameRegion" ++ index).asSymbol, { |msg| if(~qmwQFTV44FieldFrameValid and: { msg[1].asInteger == ~qmwQFTV44FieldFrameRevision }) { ~qmwQFTV44FieldFrameStage[\regions][index] = (population: msg[2].asFloat, flux: msg[3].asFloat) } }, ~qmwQFTV44FieldFrameRoot ++ "/region/" ++ index, recvPort: ~qmwQFTV44FieldFramePort);
};
16.do { |index|
    OSCdef(("qmwQFTV44FieldFrameMode" ++ index).asSymbol, { |msg| if(~qmwQFTV44FieldFrameValid and: { msg[1].asInteger == ~qmwQFTV44FieldFrameRevision }) {
        ~qmwQFTV44FieldFrameStage[\fourierPower][index] = msg[3].asFloat;
    } }, ~qmwQFTV44FieldFrameRoot ++ "/mode/" ++ index, recvPort: ~qmwQFTV44FieldFramePort);
};
16.do { |index|
    OSCdef(("qmwQFTV44FieldFrameGeometry" ++ index).asSymbol, { |msg| if(~qmwQFTV44FieldFrameValid and: { msg[1].asInteger == ~qmwQFTV44FieldFrameRevision }) {
        ~qmwQFTV44FieldFrameStage[\geometryEigenvalues][index] = msg[3].asFloat;
        ~qmwQFTV44FieldFrameStage[\geometryPower][index] = msg[4].asFloat;
        ~qmwQFTV44FieldFrameStage[\geometryPhase][index] = msg[5].asFloat;
        ~qmwQFTV44FieldFrameStage[\geometryPhaseVelocity][index] = msg[6].asFloat;
        ~qmwQFTV44FieldFrameStage[\geometryAvailable] = true;
    } }, ~qmwQFTV44FieldFrameRoot ++ "/geometry_mode/" ++ index, recvPort: ~qmwQFTV44FieldFramePort);
};
OSCdef(\qmwQFTV44FieldFrameEnd, { |msg|
    if(~qmwQFTV44FieldFrameValid and: { msg[1].asInteger == ~qmwQFTV44FieldFrameRevision }) {
        var stage = ~qmwQFTV44FieldFrameStage;
        var phaseIndex = ~qmwQFTV44FieldFramePhaseIndex.value(stage[\phase]);
        var flux = stage[\regions].collect { |region| region[\flux].abs }.maxItem ? 0.0;
        var history = List.new;
        ~qmwQFTV44FieldFrame = (
            time: stage[\time], phase: stage[\phase], norm: stage[\norm], energy: stage[\energy], flux: flux,
            fourierPower: stage[\fourierPower].copy,
            geometryPower: stage[\geometryPower].copy, geometryEigenvalues: stage[\geometryEigenvalues].copy,
            geometryPhase: stage[\geometryPhase].copy,
            geometryPhaseVelocity: stage[\geometryPhaseVelocity].copy,
            geometryAvailable: stage[\geometryAvailable]
        );
        // Normalize the stored history at its transaction boundary as well as
        // in the renderer.  This removes any object left by an interrupted UI
        // draw before the next frame can schedule another repaint.
        ~qmwQFTV44FieldFrameHistory[phaseIndex].do { |entry|
            if(entry.isKindOf(Event) and: {
                entry[\time].isNumber and: {
                    entry[\flux].isNumber and: { entry[\energy].isNumber }
                }
            }, { history.add(entry) });
        };
        history.add((time: stage[\time], flux: flux, energy: stage[\energy]));
        while { history.size > 480 } { history.removeAt(0) };
        ~qmwQFTV44FieldFrameHistory[phaseIndex] = history;
        if(stage[\geometryAvailable], {
            ~qmwQFTV44DetectGeometrySpectrum.value(stage[\geometryEigenvalues]);
        });
        ~qmwQFTV44FieldFrameValid = false;
        ~qmwQFTV44UpdateGPEPulseTimbre.value;
        ~qmwQFTV44FieldFrameRefresh.value;
    }
}, ~qmwQFTV44FieldFrameRoot ++ "/end", recvPort: ~qmwQFTV44FieldFramePort);

~qmwQFTV3Stop = {
    [\qmwQFTV44FieldFrameBegin, \qmwQFTV44FieldFramePhase, \qmwQFTV44FieldFrameNorm, \qmwQFTV44FieldFrameEnergy, \qmwQFTV44FieldFrameEnd].do { |key| OSCdef(key).free };
    4.do { |index| OSCdef(("qmwQFTV44FieldFrameRegion" ++ index).asSymbol).free };
    16.do { |index| OSCdef(("qmwQFTV44FieldFrameMode" ++ index).asSymbol).free; OSCdef(("qmwQFTV44FieldFrameGeometry" ++ index).asSymbol).free };
    { ~qmwQFTV44FieldFrameWindow !? _.close; ~qmwQFTV44FieldFrameWindow = nil }.defer;
    baseStop.value
};
{ ~qmwQFTV44OpenFieldFrameGeometryPanel.value; "QMW V4.4 FieldFrame geometry panel ready on UDP 17869".postln }.defer;
)
