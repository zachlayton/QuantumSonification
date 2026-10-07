/*
QMW Binaural Headphone Observer V1

An optional final audio adapter for Unified Instrument V3.  It consumes only
already-admitted event descriptors and the already-declared modal-frequency
ratios.  It never creates events, writes rho/H, changes a geometry frame, or
feeds audio back to the QMW runtime.

This is a transparent headphone approximation, not a measured/calibrated HRTF
decoder: even/odd modal receiver sums form virtual M/S, then bounded ITD, ILD,
far-ear low-pass filtering, and crossfeed render the two headphone channels.
A future HRIR convolution decoder can replace this final stage without changing
the QMW, geometry, field, or event-admission contracts.
*/
(
var modeCount = 20;
var defineVoice, renderEvent, audition, openPanel, closePanel, refreshPanel;

~qmbCleanup !? { ~qmbCleanup.value };
~qmbEnabled = ~qmbEnabled ? false;
~qmbTakeover = ~qmbTakeover ? false;
~qmbMix = (~qmbMix ? 0.42).asFloat.clip(0, 1);
~qmbAzimuth = (~qmbAzimuth ? 0.0).asFloat.clip(-1, 1);
~qmbWidth = (~qmbWidth ? 0.68).asFloat.clip(0, 1);
~qmbCrossfeed = (~qmbCrossfeed ? 0.12).asFloat.clip(0, 0.35);
~qmbNodes = List.new;
~qmbMaxVoices = 12;
~qmbWindow = nil;
~qmbReadout = nil;

refreshPanel = {
    ~qmbReadout !? { |view|
        view.string_(
            "HEADPHONE OBSERVER %  /  %\n"
            ++ "M/S virtual receivers -> bounded ITD, ILD, far-ear filter, crossfeed.\n"
            ++ "This is a SuperCollider headphone approximation, not a calibrated HRTF decoder.\n"
            ++ "Takeover selects this final audio adapter only; QMW state and admitted events remain unchanged."
            .format(
                if(~qmbEnabled, { "ACTIVE" }, { "BYPASSED" }),
                if(~qmbTakeover, { "HEADPHONE ONLY" }, { "PARALLEL AUDITION" })
            )
        )
    };
};

defineVoice = {
    SynthDef(\qmwBinauralHeadphoneEventV1, { |out=0, fundamental=72,
        amplitude=0.05, decay=0.34, azimuth=0, width=0.68, crossfeed=0.12,
        mix=0.42|
        var ratios = NamedControl.kr(\frequencyRatios, Array.fill(modeCount, 1.0));
        var weights = NamedControl.kr(\modalWeights, Array.fill(modeCount, 0.0));
        var phases = NamedControl.kr(\modalPhases, Array.fill(modeCount, 0.0));
        var frequencies = (fundamental * ratios).clip(28, 16000);
        var envelope = EnvGen.kr(
            Env.perc(0.003, decay.clip(0.03, 4.0), 1, -4), gate: 1, doneAction: 2
        );
        // These are virtual modal receiver projections, not independent mode
        // pans and not a claim that the 20-mode field is a speaker layout.
        var modeSignals = Array.fill(modeCount, { |index|
            SinOsc.ar(frequencies[index], phases[index], weights[index].clip(0, 1).sqrt)
        });
        var mid = Mix(modeSignals) / modeCount.sqrt;
        var side = Mix(Array.fill(modeCount, { |index|
            modeSignals[index] * if(index.even, { 1 }, { -1 })
        })) / modeCount.sqrt;
        var virtualLeft = mid + (side * width.clip(0, 1));
        var virtualRight = mid - (side * width.clip(0, 1));
        // Positive azimuth means source right: the left (far) ear is delayed,
        // dimmed, and low-passed.  Maximum ITD is deliberately conservative.
        var lateral = azimuth.clip(-1, 1);
        var maxItd = 0.00072;
        var leftFar = lateral.max(0);
        var rightFar = lateral.neg.max(0);
        var left = LPF.ar(
            DelayC.ar(virtualLeft, maxItd, leftFar * maxItd),
            18000 - (leftFar * 12500)
        ) * (1 - (leftFar * 0.34));
        var right = LPF.ar(
            DelayC.ar(virtualRight, maxItd, rightFar * maxItd),
            18000 - (rightFar * 12500)
        ) * (1 - (rightFar * 0.34));
        var leftCross = LPF.ar(DelayC.ar(virtualRight, 0.00045, 0.00025), 1500)
            * crossfeed.clip(0, 0.35);
        var rightCross = LPF.ar(DelayC.ar(virtualLeft, 0.00045, 0.00025), 1500)
            * crossfeed.clip(0, 0.35);
        var rendered = Limiter.ar(
            LeakDC.ar([left + leftCross, right + rightCross])
            * envelope * amplitude.clip(0, 0.35) * mix.clip(0, 1), 0.72
        );
        Out.ar(out, rendered);
    }).add;
};

renderEvent = { |event, level=1.0|
    var weights, phases, peak, energy, node;
    energy = (event[\energy] ? 0).asFloat.max(0) * level.squared;
    if((~qrmAudioReady ? false) and: { energy > 0 }, {
        weights = event[\weights].collect(_.asFloat.abs);
        phases = event[\phases].collect(_.asFloat);
        peak = weights.maxItem.max(1e-12);
        weights = weights / peak;
        ~qmbNodes = ~qmbNodes.select { |active| active.isPlaying };
        if(~qmbNodes.size < ~qmbMaxVoices, {
            node = Synth(\qmwBinauralHeadphoneEventV1, [
                \fundamental, ~qrmFundamental ? 72,
                \amplitude, (energy.sqrt * (~qrmMaster ? 0.16)
                    * (~qriMix ? 0.45)).clip(0, 0.25),
                \decay, ((~qriDecay ? 0.11)
                    * (event[\decayScale] ? 1.0).asFloat).clip(0.03, 4.0),
                \azimuth, ~qmbAzimuth, \width, ~qmbWidth,
                \crossfeed, ~qmbCrossfeed, \mix, ~qmbMix,
                \frequencyRatios, ~qrmPitchRatios ? Array.fill(modeCount, 1),
                \modalWeights, weights * (~qrmModeAudioWeights !? {
                    ~qrmModeAudioWeights.value
                } ? Array.fill(modeCount, 1)),
                \modalPhases, phases
            ], ~qrmStrikeGroup ? s.defaultGroup, \addToTail);
            node.register;
            ~qmbNodes.add(node);
            node.onFree({ ~qmbNodes.remove(node) });
        });
    });
};

audition = {
    if(s.serverRunning.not or: { (~qrmAudioReady ? false).not }, {
        "QMW headphone audition unavailable: audio server is not ready.".warn;
    }, {
        Synth(\qmwBinauralHeadphoneEventV1, [
            \fundamental, ~qrmFundamental ? 72,
            \amplitude, 0.13, \decay, 0.52, \azimuth, ~qmbAzimuth,
            \width, ~qmbWidth, \crossfeed, ~qmbCrossfeed, \mix, 1.0,
            \frequencyRatios, ~qrmPitchRatios ? Array.fill(modeCount, 1),
            \modalWeights, Array.fill(modeCount, { |index|
                (-0.5 * ((index - 7) / 3.0).squared).exp
            }),
            \modalPhases, Array.fill(modeCount, { |index| index * 0.19 })
        ], ~qrmStrikeGroup ? s.defaultGroup, \addToTail);
        "QMW headphone observer audition: clean modal receiver render; QMW state unchanged.".postln;
    });
};

openPanel = {
    if(~qmbWindow.notNil, {
        ~qmbWindow.front;
    }, {
        ~qmbWindow = Window("Unified Instrument Resonator V3 — Headphone Observer", Rect(300, 220, 700, 310))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qmbWindow, Rect(16, 14, 668, 26))
            .string_("OPTIONAL HEADPHONE BINAURAL OBSERVER  /  READ-ONLY EVENT ADAPTER")
            .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("dcecff"));
        Button(~qmbWindow, Rect(16, 54, 204, 28))
            .states_([["HEADPHONE OBSERVER BYPASSED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["HEADPHONE OBSERVER ACTIVE", Color.black, Color.fromHexString("80ed99")]])
            .value_(~qmbEnabled.asInteger)
            .action_({ |button| ~qmbEnabled = button.value > 0; refreshPanel.value });
        Button(~qmbWindow, Rect(232, 54, 188, 28))
            .states_([["PARALLEL AUDITION", Color.white, Color.fromHexString("17465b")],
                ["HEADPHONE ONLY", Color.black, Color.fromHexString("e06d7b")]])
            .value_(~qmbTakeover.asInteger)
            .action_({ |button| ~qmbTakeover = button.value > 0; refreshPanel.value });
        Button(~qmbWindow, Rect(432, 54, 252, 28))
            .states_([["ISOLATED HEADPHONE AUDITION", Color.white, Color.fromHexString("17465b")]])
            .action_({ audition.value });
        EZSlider(~qmbWindow, Rect(16, 102, 320, 25), "azimuth", ControlSpec(-1, 1, \lin, 0.01),
            { |view| ~qmbAzimuth = view.value }, ~qmbAzimuth, labelWidth: 74, numberWidth: 50);
        EZSlider(~qmbWindow, Rect(354, 102, 330, 25), "M/S width", ControlSpec(0, 1, \lin, 0.01),
            { |view| ~qmbWidth = view.value }, ~qmbWidth, labelWidth: 82, numberWidth: 50);
        EZSlider(~qmbWindow, Rect(16, 140, 320, 25), "crossfeed", ControlSpec(0, 0.35, \lin, 0.01),
            { |view| ~qmbCrossfeed = view.value }, ~qmbCrossfeed, labelWidth: 74, numberWidth: 50);
        EZSlider(~qmbWindow, Rect(354, 140, 330, 25), "observer mix", ControlSpec(0, 1, \lin, 0.01),
            { |view| ~qmbMix = view.value }, ~qmbMix, labelWidth: 82, numberWidth: 50);
        ~qmbReadout = StaticText(~qmbWindow, Rect(16, 186, 668, 96))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("8ecae6"));
        ~qmbWindow.onClose = { ~qmbWindow = nil; ~qmbReadout = nil };
        refreshPanel.value;
    });
};

closePanel = { ~qmbWindow !? _.close; ~qmbWindow = nil; ~qmbReadout = nil };
defineVoice.value;
~qmbPriorRenderEvent = ~qriRenderEvent;
~qriRenderEvent = { |event, level=1.0|
    if(~qmbEnabled and: { ~qmbTakeover }, {
        renderEvent.value(event, level);
    }, {
        ~qmbPriorRenderEvent.value(event, level);
        if(~qmbEnabled, { renderEvent.value(event, level) });
    });
};
~qmbOpenPanel = openPanel;
~qmbAudition = audition;
~qmbCleanup = {
    ~qmbNodes.do { |node| node.free };
    ~qmbNodes.clear;
    ~qriRenderEvent = ~qmbPriorRenderEvent;
    closePanel.value;
};
)
