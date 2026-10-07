/*
QMW Spectral V4 -> V3 performer/observer bridge
================================================

The Python spectral packet remains a read-only analysis of rho and H. This
adapter does not synthesize a pulse for every analysis frame. Instead it:

1. stores a bounded 16-level performance descriptor for ModalSpectralVoice;
2. lets admitted V3 events excite the existing stateful 20-mode bank; and
3. offers a deliberately muted held monitor for diagnostic isolation only.

Pitch belongs to the canonical Wilson/dodecahedral ModalGeometryFrame. The
four-octave 20-mode frame on UDP 17882 is sampled deterministically for the
16-level monitor. Analysis amplitudes remain sqrt of energy-basis population.
All audio follows QRM's visible SOUND LOCKED / SONIFICATION ON authority.
*/

(
var makeBridge, removeBridge;

removeBridge = {
    OSCdef(\qmwV4SpectralFrame).free;
    ~qmwV4SpectralVoices !? { |voices| voices.do { |voice| voice.free } };
    ~qmwV4SpectralVoices = nil;
    ~qmwV4SpectralGroup !? _.free;
    ~qmwV4SpectralGroup = nil;
    ~qmwV4SpectralPerformance = nil;
    ~qmwV4SpectralReadout = nil;
    ~qmwV4SpectralApplyAudioGate = nil;
};

makeBridge = {
    var fxBusIndex, sourceGroup;
    if(~qriFXSendBus.isNil, {
        "QMW V4 spectral bridge: load V3 first; ~qriFXSendBus is unavailable.".warn;
    }, {
        removeBridge.value;
        fxBusIndex = ~qriFXSendBus.index;
        sourceGroup = if(~qriFXGroup.notNil, {
            Group.before(~qriFXGroup).register;
        }, {
            Group.after(s.defaultGroup).register;
        });
        ~qmwV4SpectralGroup = sourceGroup;

        SynthDef(\qmwV4SpectralVoice, {
            |out=0, fxBus=0, freq=110, amplitude=0, pan=0,
             dryLevel=0, fxSend=0, voiceScale=0.09, voiceIndex=0, texture=0.62,
             mixedness=0, participation=0, commutator=0|
            var quantumMotion = SinOsc.kr(0.11 + (commutator.clip(0, 1) * 3.2), voiceIndex * 0.31)
                * commutator.clip(0, 1) * 0.006;
            var frequency = Lag.kr(freq.clip(20, 18000), 0.08) * (1 + quantumMotion);
            var level = Lag.kr(amplitude.clip(0, 1), 0.10)
                * Lag.kr(voiceScale.clip(0, 0.25), 0.08);
            var index = voiceIndex.clip(0, 15) / 15;
            var sine = SinOsc.ar(frequency, index * 0.37);
            var exciter = VarSaw.ar(frequency, index * 0.19, 0.18 + (index * 0.52)) * 0.55
                + SinOsc.ar(frequency * (1.96 + (index * 0.11)), index * 0.61, 0.18);
            var body = RLPF.ar(exciter, frequency * (1.02 + (index * 0.09)), 0.22)
                + (BPF.ar(exciter, frequency * (2.02 + (index * 0.17)), 0.16) * 0.85);
            var globalTexture = (texture + (mixedness.clip(0, 1) * 0.24)).clip(0, 1);
            var signal = XFade2.ar(sine, LeakDC.ar(body).tanh,
                (globalTexture * 2) - 1) * level;
            var stereo = Balance2.ar(signal, signal,
                pan.clip(-1, 1) * (0.45 + (participation.clip(0, 1) * 0.55)));
            Out.ar(out, stereo * Lag.kr(dryLevel.clip(0, 1), 0.08));
            Out.ar(fxBus, stereo * Lag.kr(fxSend.clip(0, 1), 0.08));
        }).add;
        s.sync;

        // This observer remains silent until deliberately raised. The normal
        // performer is V3's admitted-event -> ModalSpectralVoice route.
        ~qmwV4SpectralDryLevel = 0.0;
        ~qmwV4SpectralFXSend = 0.0;
        ~qmwV4SpectralVoiceScale = 0.09;
        ~qmwV4SpectralTexture = 0.62;
        ~qmwV4SpectralPerformance = (
            time: 0.0, centroid: 0.5, spread: 0.0,
            motion: 0.0, concentration: 1.0,
            purity: 1.0, entropy: 0.0, mixedness: 0.0,
            participation: 1.0, participationNormalized: 0.0,
            commutator: 0.0, commutatorActivity: 0.0,
            populations: Array.fill(16, 0.0)
        );
        ~qmwV4SpectralVoices = Array.fill(16, { |index|
            Synth.tail(sourceGroup, \qmwV4SpectralVoice, [
                \out, 0, \fxBus, fxBusIndex, \freq, 110, \amplitude, 0,
                \pan, index.linlin(0, 15, -0.85, 0.85),
                \dryLevel, 0, \fxSend, 0,
                \voiceScale, ~qmwV4SpectralVoiceScale,
                \voiceIndex, index, \texture, ~qmwV4SpectralTexture
            ]);
        });

        ~qmwV4SpectralApplyAudioGate = {
            var open = (~qrmSonify ? false).asBoolean;
            var monitorRunning = open and: {
                (~qmwV4SpectralDryLevel > 0) or: { ~qmwV4SpectralFXSend > 0 }
            };
            ~qmwV4SpectralVoices.do { |voice|
                voice.set(
                    \dryLevel, if(open) { ~qmwV4SpectralDryLevel } { 0.0 },
                    \fxSend, if(open) { ~qmwV4SpectralFXSend } { 0.0 },
                    \voiceScale, ~qmwV4SpectralVoiceScale,
                    \texture, ~qmwV4SpectralTexture
                );
                // A muted diagnostic layer must not consume audio-rate CPU.
                // Control updates still reach a paused node and are ready if
                // the performer explicitly raises dry or FX send later.
                voice.run(monitorRunning);
            };
        };

        ~qmwV4SpectralSetMix = { |dryLevel=0, fxSend=0, voiceScale=0.09, texture=0.62|
            ~qmwV4SpectralDryLevel = dryLevel.asFloat.clip(0, 1);
            ~qmwV4SpectralFXSend = fxSend.asFloat.clip(0, 1);
            ~qmwV4SpectralVoiceScale = voiceScale.asFloat.clip(0, 0.25);
            ~qmwV4SpectralTexture = texture.asFloat.clip(0, 1);
            ~qmwV4SpectralApplyAudioGate.value;
        };

        ~qmwV4SpectralOpenControls = {
            var window, dry, fx, scale, texture, readout, update;
            window = Window("QMW V4 Spectral Performer + Observer", Rect(900, 170, 500, 404))
                .front.background_(Color.fromHexString("11151c"));
            StaticText(window, Rect(16, 12, 468, 24))
                .string_("V4 SPECTRUM -> V3 GEOMETRIC PERFORMER")
                .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.white);
            StaticText(window, Rect(16, 42, 468, 52))
                .string_("Wilson/dodecahedral geometry owns tuning. rho/H analysis shapes admitted V3 events. The held 16-level monitor below is diagnostic and muted by default.")
                .stringColor_(Color.white);
            Button(window, Rect(16, 102, 224, 26))
                .states_([["OPEN MODAL PERFORMER", Color.black, Color.fromHexString("8ecae6")]])
                .action_({ ~qmsvOpenPanel !? { |open| open.value } });
            Button(window, Rect(256, 102, 228, 26))
                .states_([["MUTE HELD MONITOR", Color.white, Color.fromHexString("532b35")]])
                .action_({ ~qmwV4SpectralSetMix.(0, 0, scale.value, texture.value);
                    dry.value_(0); fx.value_(0) });
            Button(window, Rect(16, 136, 468, 26))
                .states_([["RHO POSITION FOLLOW OFF", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                    ["RHO POSITION + ROTATION FOLLOW", Color.black, Color.fromHexString("80ed99")]])
                .value_((~qmgDensityPositionFollow ? true).asInteger)
                .action_({ |button| ~qmgDensityPositionFollow = button.value > 0 });
            update = { ~qmwV4SpectralSetMix.(dry.value, fx.value, scale.value, texture.value) };
            dry = EZSlider(window, Rect(16, 176, 468, 28), "monitor dry",
                ControlSpec(0, 0.35, \lin, 0.001), { update.value },
                ~qmwV4SpectralDryLevel, labelWidth: 92, numberWidth: 64);
            fx = EZSlider(window, Rect(16, 212, 468, 28), "monitor FX",
                ControlSpec(0, 0.5, \lin, 0.001), { update.value },
                ~qmwV4SpectralFXSend, labelWidth: 92, numberWidth: 64);
            scale = EZSlider(window, Rect(16, 248, 468, 28), "monitor level",
                ControlSpec(0, 0.25, \lin, 0.001), { update.value },
                ~qmwV4SpectralVoiceScale, labelWidth: 92, numberWidth: 64);
            texture = EZSlider(window, Rect(16, 284, 468, 28), "resonant body",
                ControlSpec(0, 1, \lin, 0.001), { update.value },
                ~qmwV4SpectralTexture, labelWidth: 92, numberWidth: 64);
            readout = StaticText(window, Rect(16, 326, 468, 62))
                .string_("Waiting for a V4 spectral frame...\nrho/H remain authoritative; SOUND LOCKED gates all audio.")
                .stringColor_(Color.fromHexString("80ed99"));
            ~qmwV4SpectralReadout = readout;
            window.onClose = { ~qmwV4SpectralReadout = nil };
        };

        OSCdef(\qmwV4SpectralFrame, { |message|
            var count = (message[2] ? 0).asInteger.clip(0, 16);
            var stateMotion = (message[3] ? 0).asFloat.clip(0, 1);
            var purity = (message[4] ? 1).asFloat.clip(0, 1);
            var entropy = (message[5] ? 0).asFloat.max(0);
            var participationRank = (message[6] ? 1).asFloat.clip(1, count.max(1));
            var commutatorNorm = (message[7] ? 0).asFloat.max(0);
            var entropyMaximum = count.max(2).asFloat.log;
            var mixedness = (entropy / entropyMaximum).clip(0, 1);
            var participationNormalized = ((participationRank - 1) / (count - 1).max(1)).clip(0, 1);
            var commutatorActivity = (1 - commutatorNorm.neg.exp).clip(0, 1);
            var amplitudes = Array.fill(16, 0.0);
            var populations, total, positions, centroid, spread, concentration;
            var geometryFrequencies = if(~qmgFrame.notNil
                and: { (~qmgFrame[\frequencies] ? []).size == 20 }, {
                    ~qmgFrame[\frequencies]
                }, { nil });
            count.do { |index|
                var offset = 8 + (index * 2);
                var packetFrequency = (message[offset] ? 110).asFloat.clip(20, 18000);
                var frequency = if(geometryFrequencies.notNil, {
                    geometryFrequencies[(index * 19 / 15).round.asInteger].asFloat
                }, { packetFrequency });
                amplitudes[index] = (message[offset + 1] ? 0).asFloat.clip(0, 1);
                ~qmwV4SpectralVoices[index].set(
                    \freq, frequency, \amplitude, amplitudes[index],
                    \mixedness, mixedness,
                    \participation, participationNormalized,
                    \commutator, commutatorActivity
                );
            };
            if(count < 16, { (count .. 15).do { |index|
                ~qmwV4SpectralVoices[index].set(\amplitude, 0)
            } });
            populations = amplitudes.squared;
            total = populations.sum.max(1e-12);
            populations = populations / total;
            positions = Array.series(16, 0, 1/15);
            centroid = (populations * positions).sum.clip(0, 1);
            spread = ((populations * ((positions - centroid).squared)).sum.sqrt * 2).clip(0, 1);
            concentration = populations.squared.sum.clip(0, 1);
            ~qmwV4SpectralPerformance = (
                time: (message[1] ? 0).asFloat,
                centroid: centroid, spread: spread,
                motion: stateMotion, concentration: concentration,
                purity: purity, entropy: entropy, mixedness: mixedness,
                participation: participationRank,
                participationNormalized: participationNormalized,
                commutator: commutatorNorm,
                commutatorActivity: commutatorActivity,
                populations: populations
            );
            {
                ~qmwV4SpectralReadout !? { |view|
                    view.string_(
                        "purity %   entropy % nats   participation %\ncommutator %   state motion %"
                        .format(
                            purity.round(0.0001), entropy.round(0.0001),
                            participationRank.round(0.001),
                            commutatorNorm.round(0.0001), stateMotion.round(0.001)
                        )
                    )
                }
            }.defer;
        }, '/qmw/v4/spectral/frame', recvPort: 7404);

        // V4 deliberately enables the established event-driven modal bank.
        // Continuous Hilbert-field sound stays opt-in so the event mapping is
        // immediately identifiable during audition.
        ~qmsvEnabled = true;
        ~qmsvHilbertFollow = false;
        ~qmgInfluence = 1.0;
        ~qmgDensityPositionFollow = true;
        ~qmsvApplyAudioGate !? { |apply| apply.value };
        ~qmwV4SpectralApplyAudioGate.value;
        ~qmwV4SpectralCleanup = removeBridge;
        "QMW V4 performer/observer bridge ready: Wilson geometry tuning + admitted V3 events; OSC 7404.".postln;
        "Held 16-level monitor is muted. Open controls: ~qmwV4SpectralOpenControls.value;".postln;
        { ~qmwV4SpectralOpenControls.value }.defer;
    });
};

s.waitForBoot({ makeBridge.value });
)
