/*
QMW ModalSpectralVoice V1

An explicitly downstream, stateful rendering layer for the canonical 20-mode
ModalGeometryFrame. It does not evolve rho, generate quantum events, or alter
the existing membrane/interaction body. Existing admitted events provide an
exciter; the bank retains its own resonant state between those events.

Rings-informed design, without importing its harmonic assumptions:
  Patch:        f, Q, q (eigenvectors), centroid, brightness, damping, position
  Performance:  admitted event energy, M gains, and current event timing
  Sonic body:   continuous 20-filter Laplacian bank with source/receiver modes
*/
(
var modeCount = 20;
var defineSynths, rebuild, pushPatch, pushHilbertField, exciteEvent, openPanel, closePanel, refreshPanel;
var frameIsUsable, geometryWeights, styleSlider;

~qmsvCleanup !? { ~qmsvCleanup.value };
~qmsvEnabled = ~qmsvEnabled ? false;
~qmsvLevel = (~qmsvLevel ? 0.34).clip(0.0, 1.0);
~qmsvExciterColor = (~qmsvExciterColor ? 0.56).clip(0.0, 1.0);
~qmsvCentroid = (~qmsvCentroid ? 0.45).clip(0.0, 1.0);
~qmsvWidth = (~qmsvWidth ? 0.62).clip(0.08, 1.0);
~qmsvBrightness = (~qmsvBrightness ? 0.35).clip(-2.0, 2.0);
~qmsvDecay = (~qmsvDecay ? 1.0).clip(0.15, 4.0);
~qmsvDecaySlope = (~qmsvDecaySlope ? -0.20).clip(-2.0, 2.0);
// The interaction frame is continuous even when its probability accumulator
// admits no discrete pluck.  Keep this observer-controlled source separate
// from the transient event exciter so that a visible Hilbert-current change
// has a direct, audible route into the same geometric filter bank.
~qmsvHilbertFollow = ~qmsvHilbertFollow ? true;
~qmsvHilbertLevel = (~qmsvHilbertLevel ? 0.20).clip(0.0, 0.5);
~qmsvHilbertMotionDepth = (~qmsvHilbertMotionDepth ? 0.72).clip(0.0, 1.0);
~qmsvHilbertAttack = (~qmsvHilbertAttack ? 0.035).clip(0.004, 0.5);
~qmsvHilbertRelease = (~qmsvHilbertRelease ? 0.38).clip(0.02, 3.0);
~qmsvPriorHilbertPhases = ~qmsvPriorHilbertPhases ? nil;
~qmsvHilbertMotionPeak = 0.0;
~qmsvStrikeNode = (~qmsvStrikeNode ? 0).asInteger.clip(0, modeCount - 1);
~qmsvLeftNode = (~qmsvLeftNode ? 0).asInteger.clip(0, modeCount - 1);
~qmsvRightNode = (~qmsvRightNode ? 1).asInteger.clip(0, modeCount - 1);
~qmsvWindow = nil;
~qmsvReadout = nil;
~qmsvExciterBus = nil;
~qmsvExciterGroup = nil;
~qmsvBankGroup = nil;
~qmsvBank = nil;
~qmsvHilbertExciter = nil;
~qmsvAudioReady = false;
~qmsvPriorRenderEvent = ~qriRenderEvent;
~qmsvPriorBuildAudio = ~qrmBuildAudio;

frameIsUsable = {
    ~qmgFrame.notNil and: { (~qmgFrame[\id] ? -1) >= 0 }
        and: { (~qmgFrame[\eigenvectors] ? []).size == (modeCount * modeCount) }
};

styleSlider = { |slider|
    slider.labelView.stringColor_(Color.white);
    slider.numberView.normalColor_(Color.white).typingColor_(Color.white)
        .stringColor_(Color.white).background_(Color.fromHexString("080b10"));
    slider.sliderView.background_(Color.fromHexString("080b10"));
    slider
};

defineSynths = {
    SynthDef(\qmsvExciterV1, { |out=0, amplitude=0.1, color=0.5, duration=0.035|
        var cutoff = color.clip(0, 1).linexp(0, 1, 180, 12500);
        var envelope = EnvGen.ar(Env.perc(0.0015, duration.clip(0.006, 0.22), 1, -5), doneAction: 2);
        var excitation = HPF.ar(LPF.ar(WhiteNoise.ar(1), cutoff), 28);
        Out.ar(out, excitation * envelope * amplitude.clip(0, 0.45));
    }).add;

    // A sustained, band-limited source made only from the committed complex
    // interaction drives.  It is deliberately not an oscillator substitute
    // for the resonator: every component must still pass through the 20
    // Laplacian filters below.  Drive magnitude controls presence; the real
    // component supplies a small, smooth detuning, so changing Hilbert drive
    // changes beating and resonant balance even when no event is admitted.
    SynthDef(\qmsvHilbertFieldExciterV1, { |out=0, master=0.0, attack=0.035, release=0.38|
        var frequencies = NamedControl.kr(\frequencies, Array.fill(modeCount, 110.0));
        var amplitudes = NamedControl.kr(\amplitudes, Array.fill(modeCount, 0.0));
        var realDrives = NamedControl.kr(\realDrives, Array.fill(modeCount, 0.0));
        var phases = NamedControl.kr(\phases, Array.fill(modeCount, 0.0));
        var motion = NamedControl.kr(\motion, Array.fill(modeCount, 0.0));
        var motionDepth = \motionDepth.kr(0.72);
        var source = Mix.fill(modeCount, { |index|
            var frequency = Lag.kr(frequencies[index].clip(20, 16000), 0.14);
            // Each modal drive receives its own attack/release follower. The
            // scale varies gently by mode so a shared Hilbert change becomes
            // a coordinated spectral gesture, not a 20-oscillator volume step.
            var modeAttack = (attack.clip(0.004, 0.5) * (0.72 + (index / modeCount * 0.56))).clip(0.004, 0.8);
            var modeRelease = (release.clip(0.02, 3.0) * (1.18 - (index / modeCount * 0.42))).clip(0.02, 4.0);
            var amount = LagUD.kr(amplitudes[index].clip(0, 1), modeAttack, modeRelease);
            var detune = Lag.kr(realDrives[index].clip(-1, 1), 0.18) * 0.0018;
            var phase = Lag.kr(phases[index], 0.18);
            var movement = Lag.kr(motion[index].clip(0, 1), 0.15) * motionDepth.clip(0, 1);
            // Temporal change of a committed complex descriptor is mapped to
            // slow, mode-local detuning and amplitude breathing. This is not
            // a new dynamical law: it is a read-only sonic observation of
            // the change already present in the Hilbert interaction frame.
            var flutter = SinOsc.kr(0.07 + (movement * 5.4), phase * 0.382)
                * movement * 0.0042;
            var breathing = (0.72 + (SinOsc.kr(0.05 + (movement * 3.2), phase)
                * movement * 0.28)).clip(0.35, 1.0);
            // The paired component keeps the source lively without adding a
            // second tuning system: it remains a close, interaction-shaped
            // excitation at the bank's own modal frequency.
            var carrier = SinOsc.ar(frequency * (1 + detune + flutter), phase);
            var companion = SinOsc.ar(frequency * (1 - (detune * 0.61) - (flutter * 0.47)), phase * 0.618);
            (carrier + (companion * 0.42)) * amount * breathing
        });
        Out.ar(out, LeakDC.ar(source) * Lag.kr(master, 0.12));
    }).add;

    // This is a continuously running filter bank.  BPF retains modal state
    // between event excitations; f/Q/gain controls arrive as smoothed arrays.
    SynthDef(\qmsvModalBankV1, { |in=0, out=0, master=0.34, decay=1.0, decaySlope=(-0.2)|
        var frequencies = NamedControl.kr(\frequencies, Array.fill(modeCount, 110.0));
        var quality = NamedControl.kr(\quality, Array.fill(modeCount, 80.0));
        var leftWeights = NamedControl.kr(\leftWeights, Array.fill(modeCount, 0.0));
        var rightWeights = NamedControl.kr(\rightWeights, Array.fill(modeCount, 0.0));
        var input = In.ar(in, 1);
        var reference = frequencies[0].max(20);
        var left = Mix.fill(modeCount, { |index|
            var frequency = Lag.kr(frequencies[index].clip(20, 16000), 0.08);
            var slope = (frequency / reference).pow(decaySlope.clip(-2, 2));
            var effectiveQ = (quality[index] * decay.clip(0.15, 4.0) * slope).clip(2, 500);
            BPF.ar(input, frequency, effectiveQ.reciprocal.clip(0.002, 0.5))
                * Lag.kr(leftWeights[index], 0.07);
        });
        var right = Mix.fill(modeCount, { |index|
            var frequency = Lag.kr(frequencies[index].clip(20, 16000), 0.08);
            var slope = (frequency / reference).pow(decaySlope.clip(-2, 2));
            var effectiveQ = (quality[index] * decay.clip(0.15, 4.0) * slope).clip(2, 500);
            BPF.ar(input, frequency, effectiveQ.reciprocal.clip(0.002, 0.5))
                * Lag.kr(rightWeights[index], 0.07);
        });
        Out.ar(out, Limiter.ar(LeakDC.ar([left, right]) * Lag.kr(master, 0.05), 0.85));
    }).add;
};

geometryWeights = {
    var eigenvectors = ~qmgFrame[\eigenvectors];
    var source = ~qmsvStrikeNode;
    var leftNode = ~qmsvLeftNode;
    var rightNode = ~qmsvRightNode;
    var sourceFrequencies = (~qrmPitchRatios ? []).collect { |ratio|
        ((~qrmFundamental ? 72.0) * ratio.asFloat).clip(20, 16000)
    };
    var frequencies = if(sourceFrequencies.size == modeCount, {
        sourceFrequencies
    }, {
        ~qmgFrame[\frequencies].collect(_.asFloat)
    });
    var low = frequencies.minItem.max(20);
    var high = frequencies.maxItem.max(low * 1.001);
    var center = low * (high / low).pow(~qmsvCentroid);
    var widthOctaves = ~qmsvWidth.linexp(0.08, 1.0, 0.22, 4.0);
    var mWeights = (~qrmModeAudioWeights ? { Array.fill(modeCount, 1.0) }).value;
    var left, right, magnitude;
    left = Array.fill(modeCount, { |index|
        var modeShape = eigenvectors[(source * modeCount) + index]
            * eigenvectors[(leftNode * modeCount) + index];
        var distance = (frequencies[index].max(1e-6) / center).log2.abs;
        var envelope = (-0.5 * (distance / widthOctaves).squared).exp;
        var tilt = (frequencies[index] / center).pow(~qmsvBrightness);
        modeShape * envelope * tilt * mWeights[index].asFloat.max(0);
    });
    right = Array.fill(modeCount, { |index|
        var modeShape = eigenvectors[(source * modeCount) + index]
            * eigenvectors[(rightNode * modeCount) + index];
        var distance = (frequencies[index].max(1e-6) / center).log2.abs;
        var envelope = (-0.5 * (distance / widthOctaves).squared).exp;
        var tilt = (frequencies[index] / center).pow(~qmsvBrightness);
        modeShape * envelope * tilt * mWeights[index].asFloat.max(0);
    });
    magnitude = (left.collect(_.abs) ++ right.collect(_.abs)).maxItem.max(1e-9);
    (frequencies: frequencies, left: left / magnitude, right: right / magnitude);
};

pushPatch = {
    var weights;
    if(~qmsvAudioReady and: { ~qmsvBank.notNil } and: { frameIsUsable.value }, {
        weights = geometryWeights.value;
        ~qmsvBank.setn(\frequencies, weights[\frequencies]);
        ~qmsvBank.setn(\quality, ~qmgFrame[\quality]);
        ~qmsvBank.setn(\leftWeights, weights[\left]);
        ~qmsvBank.setn(\rightWeights, weights[\right]);
        ~qmsvBank.set(\master, if(~qmsvEnabled, { ~qmsvLevel }, { 0.0 }),
            \decay, ~qmsvDecay, \decaySlope, ~qmsvDecaySlope);
    });
    { refreshPanel.value }.defer;
};

pushHilbertField = {
    var drives, magnitudes, peak, frequencies, phases, motion, mixerGain;
    if(~qmsvAudioReady and: { ~qmsvHilbertExciter.notNil }
        and: { frameIsUsable.value }, {
        drives = (~qriFrame ? (drives: Array.fill(modeCount, Complex(0, 0))))[\drives]
            ? Array.fill(modeCount, Complex(0, 0));
        // The QRI transport contract declares 20 complex observer drives.
        // Reject an incomplete external frame rather than inventing a drive.
        if(drives.size != modeCount) { drives = Array.fill(modeCount, Complex(0, 0)) };
        magnitudes = drives.collect(_.abs);
        peak = magnitudes.maxItem.max(1e-9);
        phases = drives.collect(_.theta);
        motion = if(~qmsvPriorHilbertPhases.isNil, {
            Array.fill(modeCount, 0.0)
        }, {
            Array.fill(modeCount, { |index|
                // Wrapped phase difference prevents a 2pi crossing from
                // creating a false maximum-rate gesture.
                ((phases[index] - ~qmsvPriorHilbertPhases[index] + pi)
                    .mod(2 * pi) - pi).abs / pi
            })
        });
        ~qmsvPriorHilbertPhases = phases.copy;
        ~qmsvHilbertMotionPeak = motion.maxItem;
        frequencies = geometryWeights.value[\frequencies];
        ~qmsvHilbertExciter.setn(\frequencies, frequencies);
        ~qmsvHilbertExciter.setn(\amplitudes, magnitudes / peak);
        ~qmsvHilbertExciter.setn(\realDrives, drives.collect(_.real));
        ~qmsvHilbertExciter.setn(\phases, phases);
        ~qmsvHilbertExciter.setn(\motion, motion);
        // The continuous field is an interaction-layer voice. Its dedicated
        // level is additionally gated by the visible Hilbert mixer, so
        // bringing all five QRI voice sliders down now silences it as well.
        mixerGain = if(~qriEffectiveVoiceGains.notNil, {
            ~qriEffectiveVoiceGains.value.mean
        }, { 1.0 });
        mixerGain = mixerGain * ((~qriMix ? 0.55) / 0.55).clip(0, 1.82);
        ~qmsvHilbertExciter.set(\master, if(~qmsvEnabled and: { ~qmsvHilbertFollow }, {
            ~qmsvHilbertLevel * mixerGain.clip(0, 1)
        }, { 0.0 }), \motionDepth, ~qmsvHilbertMotionDepth,
            \attack, ~qmsvHilbertAttack, \release, ~qmsvHilbertRelease);
    });
};

rebuild = {
    var weights, frequencies, quality, left, right;
    if(s.serverRunning and: { ~qrmAudioReady ? false }, {
        ~qmsvAudioReady = false;
        defineSynths.value;
        s.sync;
        ~qmsvBank !? _.free;
        ~qmsvExciterGroup !? _.freeAll;
        ~qmsvExciterGroup !? _.free;
        ~qmsvBankGroup !? _.free;
        ~qmsvExciterBus !? _.free;
        if(frameIsUsable.value, {
            weights = geometryWeights.value;
            frequencies = weights[\frequencies];
            quality = ~qmgFrame[\quality];
            left = weights[\left];
            right = weights[\right];
        }, {
            frequencies = Array.fill(modeCount, 110.0);
            quality = Array.fill(modeCount, 80.0);
            left = Array.fill(modeCount, 0.0);
            right = Array.fill(modeCount, 0.0);
        });
        s.bind({
            ~qmsvExciterBus = Bus.audio(s, 1);
            ~qmsvExciterGroup = Group.after(~qrmStrikeGroup ? s.defaultGroup);
            ~qmsvBankGroup = Group.after(~qmsvExciterGroup);
            ~qmsvHilbertExciter = Synth.tail(~qmsvExciterGroup, \qmsvHilbertFieldExciterV1, [
                \out, ~qmsvExciterBus.index, \master, 0.0
            ]);
            ~qmsvBank = Synth.tail(~qmsvBankGroup, \qmsvModalBankV1, [
                \in, ~qmsvExciterBus.index, \out, 0, \master, 0.0,
                \decay, ~qmsvDecay, \decaySlope, ~qmsvDecaySlope
            ]);
            // Same server bundle: a newly allocated bank cannot receive an
            // array update before its /s_new is committed.
            ~qmsvBank.setn(\frequencies, frequencies);
            ~qmsvBank.setn(\quality, quality);
            ~qmsvBank.setn(\leftWeights, left);
            ~qmsvBank.setn(\rightWeights, right);
        });
        // s.bind is scheduled at the server latency. Do not let the 10 Hz
        // patch task address the new node until that bundle has landed.
        AppClock.sched(s.latency + 0.06, {
            ~qmsvAudioReady = true;
            pushPatch.value;
            pushHilbertField.value;
            "QMW ModalSpectralVoice ready: stateful 20-mode geometry bank.".postln;
            { openPanel.value }.defer;
            nil
        });
    });
};

exciteEvent = { |event, level=1.0|
    var energy = (event[\energy] ? 0.0).asFloat.max(0) * level.squared;
    var peak = (event[\weights] ? []).collect(_.asFloat.abs).maxItem ? 1.0;
    if(~qmsvEnabled and: { ~qmsvAudioReady } and: { ~qmsvBank.notNil } and: { ~qmsvExciterBus.notNil }
        and: { energy > 0 }, {
        Synth.tail(~qmsvExciterGroup, \qmsvExciterV1, [
            \out, ~qmsvExciterBus.index,
            \amplitude, (energy.sqrt * (0.08 + (peak * 0.14))).clip(0.015, 0.32),
            \color, ~qmsvExciterColor,
            \duration, (0.014 + (energy.sqrt * 0.07)).clip(0.010, 0.13)
        ]);
    });
};

refreshPanel = {
    ~qmsvReadout !? { |view|
        view.string_("STATEFUL MODAL FILTER BANK  /  Geometry frame id %  /  %\n"
            .format(~qmgFrame[\id] ? -1, if(~qmsvEnabled, { "ACTIVE" }, { "BYPASSED" }))
            ++ "M0-M19 are the performer gains. Strike/listen nodes select q_n(s) q_n(r); centroid and brightness redistribute energy over the same eigenmodes.\n"
            ++ "Hilbert field follow is a continuous read-only source from the committed interaction drives; motion peak % drives slow spectral breathing. Its level follows the five Hilbert voice faders plus pluck mix, with 20 independent attack/release followers. This layer never writes rho, flow, topology, or geometry."
                .format(~qmsvHilbertMotionPeak.round(0.001)))
    };
};

openPanel = {
    if(~qmsvWindow.notNil, { ~qmsvWindow.front }, {
        ~qmsvWindow = Window("Unified Instrument Resonator V3 — ModalSpectralVoice", Rect(190, 315, 812, 430))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qmsvWindow, Rect(16, 12, 780, 28))
            .string_("MODALSPECTRALVOICE — STATEFUL LAPLACIAN FILTER BANK")
            .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("dcecff"));
        Button(~qmsvWindow, Rect(16, 52, 248, 26))
            .states_([["MODAL SPECTRAL VOICE BYPASSED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["MODAL SPECTRAL VOICE ACTIVE", Color.black, Color.fromHexString("80ed99")]])
            .value_(~qmsvEnabled.asInteger).action_({ |button|
                ~qmsvEnabled = button.value > 0; pushPatch.value;
            });
        Button(~qmsvWindow, Rect(280, 52, 248, 26))
            .states_([["AUDITION FILTER BANK", Color.black, Color.fromHexString("8ecae6")]])
            .action_({
                if(~qmsvEnabled.not, { "Enable ModalSpectralVoice before auditioning it.".warn }, {
                    exciteEvent.value((energy: 0.8, weights: Array.fill(modeCount, 1.0)), 1.0)
                });
            });
        Button(~qmsvWindow, Rect(544, 52, 252, 26))
            .states_([["HILBERT FIELD MUTED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["HILBERT FIELD FOLLOWING", Color.black, Color.fromHexString("80ed99")]])
            .value_(~qmsvHilbertFollow.asInteger).action_({ |button|
                ~qmsvHilbertFollow = button.value > 0; pushHilbertField.value; refreshPanel.value;
            });
        styleSlider.(EZSlider(~qmsvWindow, Rect(16, 92, 246, 26), "voice level",
            ControlSpec(0, 1, \lin, 0.01), { |view| ~qmsvLevel = view.value; pushPatch.value }, ~qmsvLevel, labelWidth: 82, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(280, 92, 246, 26), "exciter color",
            ControlSpec(0, 1, \lin, 0.01), { |view| ~qmsvExciterColor = view.value }, ~qmsvExciterColor, labelWidth: 92, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(544, 92, 246, 26), "Hilbert level",
            ControlSpec(0, 0.5, \lin, 0.005), { |view| ~qmsvHilbertLevel = view.value; pushHilbertField.value }, ~qmsvHilbertLevel, labelWidth: 92, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(544, 126, 246, 26), "Hilbert motion",
            ControlSpec(0, 1, \lin, 0.01), { |view| ~qmsvHilbertMotionDepth = view.value; pushHilbertField.value }, ~qmsvHilbertMotionDepth, labelWidth: 102, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(16, 126, 246, 26), "centroid",
            ControlSpec(0, 1, \lin, 0.01), { |view| ~qmsvCentroid = view.value; pushPatch.value }, ~qmsvCentroid, labelWidth: 82, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(280, 126, 246, 26), "spectral width",
            ControlSpec(0.08, 1, \lin, 0.01), { |view| ~qmsvWidth = view.value; pushPatch.value }, ~qmsvWidth, labelWidth: 92, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(16, 160, 246, 26), "brightness",
            ControlSpec(-2, 2, \lin, 0.01), { |view| ~qmsvBrightness = view.value; pushPatch.value }, ~qmsvBrightness, labelWidth: 82, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(280, 160, 246, 26), "decay",
            ControlSpec(0.15, 4, \lin, 0.01), { |view| ~qmsvDecay = view.value; pushPatch.value }, ~qmsvDecay, labelWidth: 92, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(544, 160, 246, 26), "field attack",
            ControlSpec(0.004, 0.5, \exp, 0.001), { |view| ~qmsvHilbertAttack = view.value; pushHilbertField.value }, ~qmsvHilbertAttack, labelWidth: 92, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(16, 194, 246, 26), "decay slope",
            ControlSpec(-2, 2, \lin, 0.01), { |view| ~qmsvDecaySlope = view.value; pushPatch.value }, ~qmsvDecaySlope, labelWidth: 82, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(280, 194, 246, 26), "strike node",
            ControlSpec(0, modeCount - 1, \lin, 1), { |view| ~qmsvStrikeNode = view.value.round.asInteger; pushPatch.value }, ~qmsvStrikeNode, labelWidth: 92, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(544, 194, 246, 26), "field release",
            ControlSpec(0.02, 3, \exp, 0.005), { |view| ~qmsvHilbertRelease = view.value; pushHilbertField.value }, ~qmsvHilbertRelease, labelWidth: 92, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(16, 228, 246, 26), "listen node L",
            ControlSpec(0, modeCount - 1, \lin, 1), { |view| ~qmsvLeftNode = view.value.round.asInteger; pushPatch.value }, ~qmsvLeftNode, labelWidth: 82, numberWidth: 46));
        styleSlider.(EZSlider(~qmsvWindow, Rect(280, 228, 246, 26), "listen node R",
            ControlSpec(0, modeCount - 1, \lin, 1), { |view| ~qmsvRightNode = view.value.round.asInteger; pushPatch.value }, ~qmsvRightNode, labelWidth: 92, numberWidth: 46));
        ~qmsvReadout = StaticText(~qmsvWindow, Rect(16, 278, 780, 110))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("8ecae6"));
        ~qmsvWindow.onClose = { ~qmsvWindow = nil; ~qmsvReadout = nil };
        refreshPanel.value;
    });
};
closePanel = { ~qmsvWindow !? _.close; ~qmsvWindow = nil; ~qmsvReadout = nil };
~qmsvOpenPanel = openPanel;
// Public scene-recall seam. The preset owner restores scalar controls first,
// then asks this add-on to resend its derived filter-bank and Hilbert-field
// values without recreating any audio graph or touching QMW state.
~qmsvApplyScene = {
    pushPatch.value;
    pushHilbertField.value;
    refreshPanel.value;
};

// Compose after geometry's event hook. The legacy renderer remains untouched;
// this additive layer can be auditioned or bypassed independently.
~qriRenderEvent = { |event, level=1.0|
    ~qmsvPriorRenderEvent.value(event, level);
    exciteEvent.value(event, level);
};

// Rebuild whenever QRM recreates its server-side audio graph.
~qrmBuildAudio = {
    ~qmsvPriorBuildAudio.value;
    Routine({ 0.10.wait; rebuild.value }).play(AppClock);
};

// Geometry frames and M gains can change without a new event. Update the
// stateful bank at a bounded control rate; no audio graph is recreated.
~qmsvControlTask = Routine({ loop {
    pushPatch.value;
    pushHilbertField.value;
    0.10.wait;
} }).play(AppClock);

if(s.serverRunning and: { ~qrmAudioReady ? false }) {
    Routine({ rebuild.value; 0.12.wait; openPanel.value }).play(AppClock)
};

~qmsvCleanup = {
    ~qmsvControlTask !? _.stop; ~qmsvControlTask = nil;
    if(~qmsvPriorRenderEvent.notNil) { ~qriRenderEvent = ~qmsvPriorRenderEvent };
    if(~qmsvPriorBuildAudio.notNil) { ~qrmBuildAudio = ~qmsvPriorBuildAudio };
    ~qmsvBank !? _.free; ~qmsvBank = nil;
    ~qmsvHilbertExciter !? _.free; ~qmsvHilbertExciter = nil;
    ~qmsvAudioReady = false;
    ~qmsvExciterGroup !? _.freeAll; ~qmsvExciterGroup !? _.free; ~qmsvExciterGroup = nil;
    ~qmsvBankGroup !? _.free; ~qmsvBankGroup = nil;
    ~qmsvExciterBus !? _.free; ~qmsvExciterBus = nil;
    closePanel.value;
};
)
