/*
QMW Rings-style body adapter V1

This is an optional, deliberately small SuperCollider rendering adapter for
already-admitted QMW events.  It uses the `Rongs` UGen supplied by the GPL-3.0
PortedPlugins extension, whose modal voice is Rings-derived; no Mutable Instruments source is copied or vendored here.  QMW remains the event and
frequency authority.  In particular, this file never reads or writes rho,
does not produce events, and never changes the existing QRM resonator body.

Install PortedPlugins and recompile the SuperCollider class library before
launching V3.  The adapter is disabled by default and its output follows the
visible QRI interaction mix as well as its own RINGS BODY mix.
*/
(
var modeCount = 20;
var defineVoice, renderEvent, openPanel, closePanel, refreshPanel, audition;

~qmrCleanup !? { ~qmrCleanup.value };
~qmrAvailable = \Rongs.asClass.notNil;
~qmrEnabled = ~qmrEnabled ? false;
~qmrMix = (~qmrMix ? 0.22).clip(0.0, 1.0);
~qmrBrightness = (~qmrBrightness ? 0.52).clip(0.0, 1.0);
~qmrDamping = (~qmrDamping ? 0.68).clip(0.0, 1.0);
~qmrWindow = nil;
~qmrReadout = nil;
~qmrNodes = List.new;
~qmrPriorRenderEvent = ~qriRenderEvent;

refreshPanel = {
    ~qmrReadout !? { |view|
        view.string_(if(~qmrAvailable, {
            "Rongs is a Rings-derived modal sound adapter. QMW events and the existing 20-mode body still render first.\n"
            ++ "frequency = QRM fundamental x admitted event's dominant modal ratio; f0 is normalized by SampleRate.\n"
            ++ "RINGS BODY %  /  local mix %  /  QRI MIX %  /  output follows both."
                .format(if(~qmrEnabled, { "ACTIVE" }, { "BYPASSED" }), ~qmrMix.round(0.01), (~qriMix ? 0.55).round(0.01))
        }, {
            "Rongs is unavailable. Install PortedPlugins, recompile the SuperCollider class library, then relaunch this session.\n"
            ++ "The QMW instrument is unchanged; this optional adapter has not been installed."
        }))
    };
};

openPanel = {
    if(~qmrWindow.notNil, {
        ~qmrWindow.front;
    }, {
        ~qmrWindow = Window("Unified Instrument Resonator V3 — Rings Body", Rect(270, 205, 690, 300))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qmrWindow, Rect(16, 14, 658, 34))
            .string_("OPTIONAL RONGS / RINGS-DERIVED EVENT BODY  /  QMW STAYS AUTHORITATIVE")
            .font_(Font("Helvetica Neue", 12, true)).stringColor_(Color.fromHexString("dcecff"));
        if(~qmrAvailable, {
            Button(~qmrWindow, Rect(16, 64, 210, 28))
                .states_([["RINGS BODY BYPASSED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                    ["RINGS BODY ACTIVE", Color.black, Color.fromHexString("80ed99")]])
                .value_(~qmrEnabled.asInteger)
                .action_({ |button| ~qmrEnabled = button.value > 0; refreshPanel.value });
            EZSlider(~qmrWindow, Rect(246, 64, 202, 26), "body mix", ControlSpec(0, 1, \lin, 0.01),
                { |view| ~qmrMix = view.value }, ~qmrMix, labelWidth: 64, numberWidth: 44);
            EZSlider(~qmrWindow, Rect(464, 64, 202, 26), "brightness", ControlSpec(0, 1, \lin, 0.01),
                { |view| ~qmrBrightness = view.value }, ~qmrBrightness, labelWidth: 68, numberWidth: 44);
            EZSlider(~qmrWindow, Rect(246, 102, 202, 26), "damping", ControlSpec(0, 1, \lin, 0.01),
                { |view| ~qmrDamping = view.value }, ~qmrDamping, labelWidth: 64, numberWidth: 44);
            Button(~qmrWindow, Rect(16, 102, 210, 28))
                .states_([["ISOLATED RONGS AUDITION", Color.white, Color.fromHexString("17465b")]])
                .action_({ audition.value });
        });
        ~qmrReadout = StaticText(~qmrWindow, Rect(16, 150, 658, 110))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("8ecae6"));
        ~qmrWindow.onClose = { ~qmrWindow = nil; ~qmrReadout = nil };
        refreshPanel.value;
    });
};
closePanel = { ~qmrWindow !? _.close; ~qmrWindow = nil; ~qmrReadout = nil };
~qmrOpenPanel = openPanel;

if(~qmrAvailable, {
    defineVoice = {
        SynthDef(\qmrRongsEventVoiceV1, { |out=0, frequency=220, amplitude=0.05,
            sustainSeconds=0.08, pan=0, structure=0.5, brightness=0.5, damping=0.68,
            accent=0.5, position=0.5|
            // Rongs f0 is normalized frequency.  This preserves QRM's Hz
            // tuning contract instead of treating an Hz value as a UGen ratio.
            var trigger = Trig.kr(1, sustainSeconds.clip(0.004, 0.45));
            // A Symbol lookup keeps the file parseable when PortedPlugins is
            // absent. This SynthDef is constructed only after the availability
            // gate above succeeds.
            var signal = \Rongs.asClass.ar(
                trigger: trigger,
                sustain: trigger,
                f0: frequency.clip(20, 16000) / SampleRate.ir,
                structure: structure.clip(0, 1),
                brightness: brightness.clip(0, 1),
                damping: damping.clip(0, 1),
                accent: accent.clip(0, 1),
                stretch: 0.5,
                position: position.clip(0, 1),
                loss: 0.15,
                modeNum: 2,
                cosFreq: 0.15
            );
            var envelope = EnvGen.kr(Env.linen(0, sustainSeconds.clip(0.02, 2.0) * 2.4, 0.05), doneAction: 2);
            Out.ar(out, Limiter.ar(Pan2.ar(LeakDC.ar(signal) * envelope * amplitude.clip(0, 0.35), pan), 0.75));
        }).add;
    };

    renderEvent = { |event, level=1.0|
        var dominant, ratios, frequency, energy, decayScale, normalizedMode;
        // Always preserve the upstream rendering path before adding this
        // optional parallel body.  This hook neither modifies event metadata
        // nor suppresses the canonical QRM output.
        ~qmrPriorRenderEvent.value(event, level);
        energy = (event[\energy] ? 0).asFloat.max(0) * level.squared;
        if(~qmrEnabled and: { (~qrmAudioReady ? false) } and: { energy > 0 }, {
            dominant = (event[\dominant] ? 0).asInteger.clip(0, modeCount - 1);
            ratios = ~qrmPitchRatios ? Array.fill(modeCount, 1.0);
            frequency = (~qrmFundamental ? 72.0) * (ratios[dominant] ? 1.0).asFloat;
            decayScale = (event[\decayScale] ? 1.0).asFloat.clip(0.25, 1.75);
            normalizedMode = dominant / (modeCount - 1);
            ~qmrNodes = ~qmrNodes.select { |node| node.isPlaying };
            if(~qmrNodes.size < 12, {
                var node = Synth(\qmrRongsEventVoiceV1, [
                    \frequency, frequency.clip(20, 16000),
                    \amplitude, (energy.sqrt * (~qrmMaster ? 0.16) * (~qriMix ? 0.55) * ~qmrMix).clip(0, 0.28),
                    \sustainSeconds, ((~qriDecay ? 0.11) * decayScale).clip(0.02, 0.60),
                    \pan, normalizedMode.linlin(0, 1, -0.72, 0.72),
                    \structure, normalizedMode,
                    \brightness, (~qmrBrightness * 0.75 + (normalizedMode * 0.25)).clip(0, 1),
                    \damping, ~qmrDamping,
                    \accent, (energy / 0.35).sqrt.clip(0.08, 1.0),
                    \position, normalizedMode
                ], ~qrmStrikeGroup, \addToTail);
                node.register;
                ~qmrNodes.add(node);
                node.onFree({ ~qmrNodes.remove(node) });
            });
        });
    };

    audition = {
        if(s.serverRunning.not or: { (~qrmAudioReady ? false).not }, {
            "QMW Rings body audition unavailable: audio server is not ready.".warn;
        }, {
            Synth(\qmrRongsEventVoiceV1, [
                \frequency, ((~qrmFundamental ? 72.0) * ((~qrmPitchRatios ? [1.0])[~qrmSelectedModeIndex ? 0])).clip(55, 16000),
                \amplitude, 0.10, \sustainSeconds, 0.16, \pan, 0,
                \structure, 0.45, \brightness, ~qmrBrightness,
                \damping, ~qmrDamping, \accent, 0.78, \position, 0.35
            ], ~qrmStrikeGroup, \addToTail);
            "QMW isolated Rongs audition: current selected modal frequency; main QRM mix unchanged.".postln;
        });
    };
    defineVoice.value;
    ~qmrPriorRenderEvent = ~qriRenderEvent;
    ~qriRenderEvent = renderEvent;
}, {
    audition = { "QMW Rings body requires the PortedPlugins Rongs UGen. Recompile the SuperCollider class library after installing it.".warn };
    "QMW Rings body adapter is available as a panel, but Rongs is not installed; keeping the QMW session unchanged.".postln;
});

~qmrAudition = audition;
~qmrCleanup = {
    if(~qmrAvailable and: { ~qmrPriorRenderEvent.notNil }, { ~qriRenderEvent = ~qmrPriorRenderEvent });
    ~qmrNodes !? { |nodes| nodes.do(_.free) };
    ~qmrNodes = List.new;
    closePanel.value;
};
)
