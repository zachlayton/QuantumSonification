/*
QMW V4.2 Bloch-harmonic spatial voice

Native SuperCollider port of:
  BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v8/
  qmw_qubit_resonator.gendsp

Four reduced-qubit Bloch vectors drive four independent eight-partial
resonators. Their stereo positions retain the v8 azimuth, radius/distance and
aperture controls as a bounded stereo reduction; the source identities remain
separate so an HOA encoder can replace only this output stage later.

This is a read-only downstream adapter. It receives the canonical full-engine
OSC mirror and never evolves, reduces or writes back to rho. In V4.2 it is the
fifth channel of the live voice mixer, joins the other voice channels on the
main output pair, and starts at an exact zero-gain bypass.
*/
(
var blochPort = (
    ~qmwQFTV42BlochPort
    ? ("QMW_BLOCH_SC_PORT".getenv ? "17832").asInteger
).asInteger;
var defineSynth, pushAudio, refreshControls, openControls;
var parseRatioText, formatRatioText, applyRatioText;
var installMainButton, cleanup, priorStop;
var frequencySliders, gainView, muteButtons, amplitudeSlider;
var spatialWidthSlider, distanceDepthSlider, interpolationSlider;
var pitchModeMenu, ratioField, ratioStatus;
var status, vectorStatus, mainButton;
var textColor = Color.fromHexString("dcecff");
var panelColor = Color.fromHexString("101722");

~qmwQFTV42BlochCleanup !? { |function| function.value };
thisProcess.openUDPPort(blochPort);

~qmwQFTV42BlochPort = blochPort;
~qmwQFTV42BlochVectors = Array.fill(4, { [0.0, 0.0, 1.0] });
// These defaults are copied from the user's authoritative local v8 patch.
~qmwQFTV42BlochBaseFrequencies = [55.0, 110.0, 220.0, 275.0];
// Neutral only until the first live Hamiltonian packet arrives. Do not invent
// an interval structure when the engine has not yet supplied energy gaps.
~qmwQFTV42BlochHamiltonianRatios = Array.fill(4, { 1.0 });
// Ratio mode treats the V4.2 fundamental as one frequency unit. These default
// partial numbers reproduce the authoritative Max-v8 bases at a 55 Hz root.
~qmwQFTV42BlochUserRatios = (~qmwQFTV42BlochUserRatios
    ? [1.0, 2.0, 4.0, 5.0]).asArray;
if(~qmwQFTV42BlochUserRatios.size != 4, {
    ~qmwQFTV42BlochUserRatios = [1.0, 2.0, 4.0, 5.0]
});
~qmwQFTV42BlochUserRatios = ~qmwQFTV42BlochUserRatios.collect { |ratio|
    ratio.asFloat.clip(0.01, 64)
};
// 0 = four independent Max-v8 bases, 1 = user-entered partial ratios times
// the shared V4.2 fundamental, 2 = live Hamiltonian energy-gap ratios.
~qmwQFTV42BlochPitchMode = 0;
~qmwQFTV42BlochInterpolationSeconds = 0.35;
~qmwQFTV42BlochQubitGains = Array.fill(4, 1.0);
~qmwQFTV42BlochQubitMutes = Array.fill(4, 0);
~qmwQFTV42BlochLocalAmplitude = 0.12;
~qmwQFTV42BlochSpatialWidth = 1.0;
~qmwQFTV42BlochDistanceDepth = 1.0;
~qmwQFTV42BlochPurity = 1.0;
~qmwQFTV42BlochEntropy = 0.0;
~qmwQFTV42BlochCoherence = 0.0;
~qmwQFTV42BlochLastSeen = Array.fill(4, -1e9);
~qmwQFTV42BlochSynth = nil;
~qmwQFTV42BlochSourceGroupID = nil;
~qmwQFTV42BlochVoiceOnline = false;
~qmwQFTV42BlochWindow = nil;
~qmwQFTV42BlochCleaning = false;

parseRatioText = { |text|
    var tokens = text.asString.split($:).collect { |token|
        token.stripWhiteSpace
    };
    var values;
    if(tokens.size != 4 or: { tokens.any { |token| token.isEmpty } }, {
        nil
    }, {
        values = tokens.collect { |token| token.asFloat };
        if(values.any { |value| value < 0.01 or: { value > 64 } }, {
            nil
        }, {
            values
        })
    })
};
~qmwQFTV42BlochParseRatioText = parseRatioText;

formatRatioText = {
    ~qmwQFTV42BlochUserRatios.collect { |ratio|
        ratio.round(0.0001).asString
    }.join(":")
};

applyRatioText = { |text|
    var ratios = parseRatioText.(text);
    if(ratios.isNil, {
        ratioStatus !? { |view|
            view.string_("Enter four positive ratios separated by colons (0.01–64).")
                .stringColor_(Color.fromHexString("ffbf69"))
        }
    }, {
        ~qmwQFTV42BlochUserRatios = ratios;
        ~qmwQFTV42BlochPitchMode = 1;
        ratioField !? { |view| view.string_(formatRatioText.value) };
        pitchModeMenu !? { |menu| menu.value_(1) };
        ratioStatus !? { |view|
            view.string_("fundamental × [%]".format(formatRatioText.value))
                .stringColor_(Color.fromHexString("80ed99"))
        };
        pushAudio.value
    })
};
~qmwQFTV42BlochApplyRatioText = applyRatioText;

~qmwQFTV42BlochEffectiveFrequencies = {
    case
    { ~qmwQFTV42BlochPitchMode == 1 } {
        ~qmwQFTV42BlochUserRatios.collect { |ratio|
            (~qmwQFTV3Fundamental ? 55.0) * ratio
        }
    }
    { ~qmwQFTV42BlochPitchMode == 2 } {
        ~qmwQFTV42BlochHamiltonianRatios.collect { |ratio|
            (~qmwQFTV3Fundamental ? 55.0) * ratio
        }
    }
    {
        ~qmwQFTV42BlochBaseFrequencies
    }
};

~qmwQFTV42BlochEffectiveQubitGains = {
    Array.fill(4, { |qubit|
        ~qmwQFTV42BlochQubitGains[qubit].clip(0, 2)
        * (1 - ~qmwQFTV42BlochQubitMutes[qubit].clip(0, 1))
    })
};

defineSynth = {
    SynthDef(\qmwQFTV42BlochSpatialVoice, {
        |out=0, outputGain=1, rendererGate=1, voiceGainBus=0,
        localAmplitude=0.12, spatialWidth=1, distanceDepth=1,
        interpolationSeconds=0.35, gate=1,
        fxSendBus=0, fxSendControlBus=0, fxEnabled=0|
        var xs = NamedControl.kr(\x, Array.fill(4, 0.0));
        var ys = NamedControl.kr(\y, Array.fill(4, 0.0));
        var zs = NamedControl.kr(\z, Array.fill(4, 1.0));
        var baseFrequencies = NamedControl.kr(
            \baseFrequencies, [55.0, 110.0, 220.0, 275.0]
        );
        var qubitGains = NamedControl.kr(
            \qubitGains, Array.fill(4, 1.0), 0.08
        );
        var purity = NamedControl.kr(\purity, 1.0, 0.08).clip(0, 1);
        var entropy = NamedControl.kr(\entropy, 0.0, 0.08).clip(0, 1);
        var coherence = NamedControl.kr(\coherence, 0.0, 0.08).clip(0, 1);
        var glide = Lag.kr(interpolationSeconds.clip(0.02, 4), 0.08);
        // The V4.2 mixer reserves 0..4 for this quieter persistent voice;
        // transient pluck lanes retain their established 0..2 ceiling.
        var fifthVoiceGain = In.kr(voiceGainBus, 1).clip(0, 4);
        var envelope = EnvGen.kr(Env.asr(0.04, 1, 0.16), gate, doneAction: 2);
        var sources = Array.fill(4, { |qubit|
            var sx, sy, sz, radius, horizontalRadius, shape, tilt, base;
            var magnitudes, phaseSigns, frequencies, partials, signal;
            var distance, aperture, directionalSpread, pan, distanceGain;
            // The engine publisher is discrete control data. This adjustable
            // exponential interpolation is downstream audio smoothing: it
            // does not alter the authoritative Bloch vectors or Python clock.
            sx = Lag.kr(xs[qubit], glide);
            sy = Lag.kr(ys[qubit], glide);
            sz = Lag.kr(zs[qubit] - 1, glide) + 1;
            base = Lag.kr(baseFrequencies[qubit], glide);
            radius = (sx.squared + sy.squared + sz.squared).sqrt.clip(0, 1);
            horizontalRadius = (sx.squared + sy.squared).sqrt;
            shape = purity.linlin(0, 1, 0.65, 1.45);
            tilt = (0.90 - (0.75 * coherence) + (0.25 * entropy))
                .clip(0.05, 1);

            // Exact signed degree-one/two polynomial bank from the v8 GenExpr.
            // Magnitude drives level and sign selects oscillator phase 0 or pi.
            magnitudes = [
                sx, sy, sz, 2 * sx * sy, 2 * sy * sz, 2 * sz * sx,
                sx.squared - sy.squared,
                0.5 * ((3 * sz.squared) - radius.squared)
            ].collect { |value| (value.abs + 0.0001).pow(shape) };
            phaseSigns = [
                sx < 0, sy < 0, sz < 0, (sx * sy) < 0,
                (sy * sz) < 0, (sz * sx) < 0,
                (sx.squared - sy.squared) < 0,
                ((3 * sz.squared) - radius.squared) < 0
            ];
            frequencies = Array.series(8, 1, 1).collect { |harmonic|
                base.clip(
                    1, (SampleRate.ir * 0.45) / harmonic
                ) * harmonic
            };
            partials = Mix.fill(8, { |index|
                SinOsc.ar(
                    frequencies[index], phaseSigns[index] * pi,
                    magnitudes[index] / (index + 1).pow(tilt)
                )
            });
            signal = (partials * 0.42).tanh
                * localAmplitude.clip(0, 0.5)
                * (0.35 + (0.65 * radius))
                * qubitGains[qubit].clip(0, 2);

            // Stereo fold-down of v8 Spat control:
            // distance = 1 + 1.5(1-r), aperture = 20 + 140(1-r),
            // azimuth = atan2(y,x). Elevation is preserved in the resonator's
            // signed Z harmonics; a future HOA stage can consume XYZ directly.
            distance = 1 + (1.5 * (1 - radius));
            aperture = 20 + (140 * (1 - radius));
            directionalSpread = (1 - (aperture / 180)).clip(0, 1);
            pan = (sy / horizontalRadius.max(0.000001))
                * spatialWidth.clip(0, 1.5) * directionalSpread;
            distanceGain = 1 / (
                1 + (distanceDepth.clip(0, 1) * (distance - 1))
            );
            Pan2.ar(signal * distanceGain, pan.clip(-1, 1));
        });
        var emitted = Limiter.ar(
            LeakDC.ar(Mix(sources) * 0.5)
                * Lag.kr(
                    outputGain.clip(0, 1.5)
                    * rendererGate.clip(0, 1)
                    * fifthVoiceGain,
                    0.08
                ) * envelope,
            0.95
        );
        var fxSend = Lag.kr(In.kr(fxSendControlBus).clip(0, 1), 0.03)
            * fxEnabled.clip(0, 1);
        Out.ar(out, emitted);
        Out.ar(fxSendBus, emitted * fxSend);
    }).add;
};
~qmwQFTV42BlochDefineSynth = defineSynth;

refreshControls = {
    var now = Main.elapsedTime;
    var effectiveFrequencies = ~qmwQFTV42BlochEffectiveFrequencies.();
    var liveCount = ~qmwQFTV42BlochLastSeen.count { |time|
        (now - time) < 2.0
    };
    frequencySliders !? { |views|
        views.do { |view, qubit|
            view.value_(effectiveFrequencies[qubit]);
            view.enabled_(~qmwQFTV42BlochPitchMode == 0)
        }
    };
    pitchModeMenu !? { |menu|
        menu.value_(~qmwQFTV42BlochPitchMode.clip(0, 2))
    };
    ratioField !? { |view|
        view.enabled_(~qmwQFTV42BlochPitchMode == 1)
    };
    gainView !? { |view| view.value_(~qmwQFTV42BlochQubitGains / 2) };
    muteButtons !? { |buttons|
        buttons.do { |button, qubit|
            button.value_(~qmwQFTV42BlochQubitMutes[qubit])
        }
    };
    amplitudeSlider !? { |view| view.value_(~qmwQFTV42BlochLocalAmplitude) };
    spatialWidthSlider !? { |view| view.value_(~qmwQFTV42BlochSpatialWidth) };
    distanceDepthSlider !? { |view| view.value_(~qmwQFTV42BlochDistanceDepth) };
    interpolationSlider !? { |view|
        view.value_(~qmwQFTV42BlochInterpolationSeconds)
    };
    status !? { |view|
        view.string_(if(liveCount == 4, {
            "FULL 4-QUBIT MIRROR LIVE ON UDP %  /  fifth mixer channel"
                .format(blochPort)
        }, {
            "WAITING FOR FULL-ENGINE MIRROR ON UDP %  /  % OF 4 QUBITS LIVE"
                .format(blochPort, liveCount)
        })).stringColor_(if(liveCount == 4, {
            Color.fromHexString("80ed99")
        }, { Color.fromHexString("ffbf69") }))
    };
    vectorStatus !? { |view|
        view.string_(~qmwQFTV42BlochVectors.collect { |vector, qubit|
            "q%  x %  y %  z %".format(
                qubit,
                vector[0].round(0.001),
                vector[1].round(0.001),
                vector[2].round(0.001)
            )
        }.join("\n"))
    };
};

pushAudio = {
    var vectors = ~qmwQFTV42BlochVectors;
    // The Bloch engine is a fifth mixer voice, not part of the continuous
    // scalar-field renderer. Its own fader selects it in any renderer mode;
    // the instrument-wide sound button remains the final safety gate.
    var rendererGate = (~qmwQFTV3SoundEnabled ? 1).asFloat.clip(0, 1);
    ~qmwQFTV42BlochSynth !? { |synth|
        synth.setn(\x, vectors.collect { |vector| vector[0] });
        synth.setn(\y, vectors.collect { |vector| vector[1] });
        synth.setn(\z, vectors.collect { |vector| vector[2] });
        synth.setn(\baseFrequencies, ~qmwQFTV42BlochEffectiveFrequencies.());
        synth.setn(\qubitGains, ~qmwQFTV42BlochEffectiveQubitGains.());
        synth.set(
            \purity, ~qmwQFTV42BlochPurity,
            \entropy, ~qmwQFTV42BlochEntropy,
            \coherence, ~qmwQFTV42BlochCoherence,
            \localAmplitude, ~qmwQFTV42BlochLocalAmplitude,
            \spatialWidth, ~qmwQFTV42BlochSpatialWidth,
            \distanceDepth, ~qmwQFTV42BlochDistanceDepth,
            \interpolationSeconds, ~qmwQFTV42BlochInterpolationSeconds,
            \rendererGate, rendererGate
        );
    };
    refreshControls.value;
};
~qmwQFTV42BlochPushAudio = pushAudio;

openControls = {
    if(~qmwQFTV42BlochWindow.notNil, {
        ~qmwQFTV42BlochWindow.front
    }, {
        ~qmwQFTV42BlochWindow = Window(
            "V4.2 Bloch-Harmonic Spatial Voice", Rect(270, 40, 780, 770)
        ).front.background_(panelColor);
        StaticText(~qmwQFTV42BlochWindow, Rect(16, 12, 748, 24))
            .string_("VOICE 5  /  FOUR BLOCH-HARMONIC RESONATORS  /  STEREO SPATIAL")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(textColor);
        StaticText(~qmwQFTV42BlochWindow, Rect(16, 42, 748, 48))
            .string_(
                "Native port of qmw_qubit_resonator.gendsp. The canonical four-qubit "
                ++ "engine is mirrored here read-only; raise the Bloch fader in V4.2's "
                ++ "5-voice mixer to hear it on the main output pair 1–2."
            ).stringColor_(textColor);

        status = StaticText(~qmwQFTV42BlochWindow, Rect(16, 96, 748, 24));
        frequencySliders = Array.fill(4, { |qubit|
            EZSlider(
                ~qmwQFTV42BlochWindow,
                Rect(16, 130 + (qubit * 38), 360, 30),
                "q% base Hz".format(qubit),
                ControlSpec(20, 1200, \exp, 0.01),
                { |view|
                    ~qmwQFTV42BlochBaseFrequencies[qubit] = view.value;
                    pushAudio.value
                },
                ~qmwQFTV42BlochBaseFrequencies[qubit],
                labelWidth: 84, numberWidth: 66
            )
        });
        vectorStatus = StaticText(
            ~qmwQFTV42BlochWindow, Rect(404, 130, 360, 144)
        ).font_(Font("Menlo", 12)).stringColor_(Color.fromHexString("8ecae6"));

        pitchModeMenu = PopUpMenu(
            ~qmwQFTV42BlochWindow, Rect(16, 282, 360, 28)
        )
            .items_([
                "pitch: manual q0–q3 bases",
                "pitch: user ratio × fundamental",
                "pitch: Hamiltonian gap ratios"
            ])
            .value_(~qmwQFTV42BlochPitchMode)
            .action_({ |menu|
                ~qmwQFTV42BlochPitchMode = menu.value;
                if(menu.value == 1, {
                    applyRatioText.(ratioField.string)
                }, {
                    ratioField.enabled_(false);
                    ratioStatus.string_(if(menu.value == 0, {
                        "Ratio entry is inactive in manual-Hz mode."
                    }, {
                        "Ratio entry is inactive in Hamiltonian-gap mode."
                    })).stringColor_(Color.fromHexString("a9c5dd"));
                    pushAudio.value
                })
            });

        ratioField = TextField(
            ~qmwQFTV42BlochWindow, Rect(16, 320, 266, 28)
        ).string_(formatRatioText.value)
            .stringColor_(textColor).background_(Color.fromHexString("18212b"))
            .enabled_(~qmwQFTV42BlochPitchMode == 1)
            .action_({ |view| applyRatioText.(view.string) });
        Button(~qmwQFTV42BlochWindow, Rect(290, 320, 86, 28))
            .states_([["APPLY", Color.black, Color.fromHexString("80ed99")]])
            .action_({ applyRatioText.(ratioField.string) });
        ratioStatus = StaticText(
            ~qmwQFTV42BlochWindow, Rect(16, 352, 360, 20)
        ).string_(if(~qmwQFTV42BlochPitchMode == 1, {
            "fundamental × [%]".format(formatRatioText.value)
        }, {
            "Type four ratios, then APPLY to enter Ratio mode."
        })).stringColor_(Color.fromHexString("a9c5dd"));

        StaticText(~qmwQFTV42BlochWindow, Rect(16, 380, 360, 20))
            .string_("QUBIT SOURCE GAINS  /  q0 q1 q2 q3")
            .stringColor_(Color.fromHexString("8ecae6"));
        gainView = MultiSliderView(~qmwQFTV42BlochWindow, Rect(16, 404, 360, 84))
            .value_(~qmwQFTV42BlochQubitGains / 2)
            .elasticMode_(true).gap_(5).drawLines_(true).isFilled_(true)
            .fillColor_(Color(0.20, 0.78, 1.0, 0.86))
            .background_(Color.grey(0.12))
            .action_({ |view|
                ~qmwQFTV42BlochQubitGains = view.value.collect { |value|
                    (value * 2).clip(0, 2)
                };
                pushAudio.value
            });
        muteButtons = Array.fill(4, { |qubit|
            Button(~qmwQFTV42BlochWindow, Rect(16 + (qubit * 90), 494, 86, 26))
                .states_([
                    ["q% on".format(qubit), Color.grey(0.85), Color.grey(0.24)],
                    ["q% mute".format(qubit), Color.white, Color.red(0.58)]
                ])
                .value_(~qmwQFTV42BlochQubitMutes[qubit])
                .action_({ |button|
                    ~qmwQFTV42BlochQubitMutes[qubit] = button.value;
                    pushAudio.value
                })
        });

        interpolationSlider = EZSlider(
            ~qmwQFTV42BlochWindow, Rect(404, 282, 360, 30),
            "state glide s", ControlSpec(0.02, 4, \exp, 0.001),
            { |view|
                ~qmwQFTV42BlochInterpolationSeconds = view.value;
                pushAudio.value
            },
            ~qmwQFTV42BlochInterpolationSeconds,
            labelWidth: 92, numberWidth: 64
        );
        amplitudeSlider = EZSlider(
            ~qmwQFTV42BlochWindow, Rect(404, 322, 360, 30),
            "local amp", ControlSpec(0, 0.5, \lin, 0.001),
            { |view| ~qmwQFTV42BlochLocalAmplitude = view.value; pushAudio.value },
            ~qmwQFTV42BlochLocalAmplitude, labelWidth: 92, numberWidth: 64
        );
        spatialWidthSlider = EZSlider(
            ~qmwQFTV42BlochWindow, Rect(404, 362, 360, 30),
            "stereo width", ControlSpec(0, 1.5, \lin, 0.01),
            { |view| ~qmwQFTV42BlochSpatialWidth = view.value; pushAudio.value },
            ~qmwQFTV42BlochSpatialWidth, labelWidth: 92, numberWidth: 64
        );
        distanceDepthSlider = EZSlider(
            ~qmwQFTV42BlochWindow, Rect(404, 402, 360, 30),
            "distance depth", ControlSpec(0, 1, \lin, 0.01),
            { |view| ~qmwQFTV42BlochDistanceDepth = view.value; pushAudio.value },
            ~qmwQFTV42BlochDistanceDepth, labelWidth: 92, numberWidth: 64
        );
        Button(~qmwQFTV42BlochWindow, Rect(404, 442, 360, 26))
            .states_([["LOAD STATIC FOUR-DIRECTION TEST", Color.black, Color.yellow(0.78)]])
            .action_({
                ~qmwQFTV42BlochVectors = [
                    [1.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                    [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0]
                ];
                ~qmwQFTV42BlochLastSeen = Array.fill(4, Main.elapsedTime);
                pushAudio.value
            });

        StaticText(~qmwQFTV42BlochWindow, Rect(16, 538, 748, 64))
            .string_((
                "OSC input: /qmw/qubit/0..3/bloch plus purity, coherence_l1 and "
                ++ "von_neumann_entropy on UDP %. The V4.2 launcher manages the canonical "
                ++ "full-profile engine and this mirror. State glide interpolates only "
                ++ "the audio controls; it never changes rho, event timing, or field evolution."
            ).format(blochPort)
            ).stringColor_(Color.yellow(0.75));
        StaticText(~qmwQFTV42BlochWindow, Rect(16, 612, 748, 126))
            .string_(
                "The eight-mode equation, signed 0/pi phases, adjustable vector glide, "
                ++ "purity shape and entropy/coherence tilt are ported from the local v8 "
                ++ "GenExpr source. Stereo is a bounded fold-down of v8 azimuth, distance "
                ++ "and aperture—not a replacement for its 16-channel HOA/CRAIVE output. "
                ++ "Manual pitch matches Max v8. Ratio mode multiplies the V4.2 fundamental "
                ++ "by four typed partial numbers (for example 1:2:4:5 or 2:5:7:11); "
                ++ "gap mode uses live Hamiltonian energy gaps. The density matrix alone has no pitch."
            ).stringColor_(textColor);
        ~qmwQFTV42BlochWindow.onClose = {
            ~qmwQFTV42BlochWindow = nil;
            frequencySliders = nil; gainView = nil; muteButtons = nil;
            amplitudeSlider = nil; spatialWidthSlider = nil;
            distanceDepthSlider = nil; interpolationSlider = nil;
            pitchModeMenu = nil; ratioField = nil; ratioStatus = nil;
            status = nil; vectorStatus = nil;
        };
        refreshControls.value;
    });
};
~qmwQFTV42OpenBlochSpatialVoice = openControls;

installMainButton = Routine({
    while({ ~qmwQFTV3Window.isNil }, { 0.1.wait });
    {
        mainButton = Button(~qmwQFTV3Window, Rect(730, 2730, 360, 30))
            .states_([[
                "BLOCH SPATIAL VOICE  /  fifth mixer channel",
                Color.black, Color.fromHexString("8ecae6")
            ]])
            .action_({ openControls.value });
    }.defer;
}).play(AppClock);

4.do { |qubit|
    OSCdef(("qmwQFTV42BlochQ" ++ qubit).asSymbol, { |msg|
        if(msg.size >= 4) {
            ~qmwQFTV42BlochVectors[qubit] = [
                msg[1].asFloat.clip(-1, 1),
                msg[2].asFloat.clip(-1, 1),
                msg[3].asFloat.clip(-1, 1)
            ];
            ~qmwQFTV42BlochLastSeen[qubit] = Main.elapsedTime;
            { pushAudio.value }.defer;
        };
    }, "/qmw/qubit/%/bloch".format(qubit), recvPort: blochPort);
};
OSCdef(\qmwQFTV42BlochPurity, { |msg|
    if(msg.size >= 2) {
        ~qmwQFTV42BlochPurity = msg[1].asFloat.clip(0, 1);
        { pushAudio.value }.defer
    };
}, "/qmw/density/purity", recvPort: blochPort);
OSCdef(\qmwQFTV42BlochCoherence, { |msg|
    if(msg.size >= 2) {
        // Four-qubit l1 coherence ranges from 0 to d-1 = 15.
        ~qmwQFTV42BlochCoherence = (msg[1].asFloat / 15).clip(0, 1);
        { pushAudio.value }.defer
    };
}, "/qmw/density/coherence_l1", recvPort: blochPort);
OSCdef(\qmwQFTV42BlochEntropy, { |msg|
    if(msg.size >= 2) {
        // DensityMatrixEngine reports base-2 entropy; log2(16) = 4.
        ~qmwQFTV42BlochEntropy = (msg[1].asFloat / 4).clip(0, 1);
        { pushAudio.value }.defer
    };
}, "/qmw/density/von_neumann_entropy", recvPort: blochPort);
OSCdef(\qmwQFTV42BlochHamiltonianRatios, { |msg|
    if(msg.size >= 5) {
        // These ratios come from positive gaps of the engine Hamiltonian,
        // not from rho alone. The pitch mapping remains a downstream choice.
        ~qmwQFTV42BlochHamiltonianRatios = msg.copyRange(1, 4).collect {
            |value| value.asFloat.clip(0.01, 64)
        };
        if(~qmwQFTV42BlochPitchMode == 2, {
            { pushAudio.value }.defer
        });
    };
}, "/qmw/density_field/harmonics", recvPort: blochPort);

~qmwQFTV42BlochAudioRoutine = Routine({
    inf.do {
        var groupID;
        if(s.serverRunning and: { ~qmwQFTV3AudioReady ? false }
            and: { ~qmwQFTV3SourceGroup.notNil }
            and: { ~qmwQFTV3FieldBus.notNil }
            and: { ~qmwQFTV3VoiceGainBus.notNil }
            and: { (~qmwQFTV3VoiceCount ? 4) >= 5 }) {
            groupID = ~qmwQFTV3SourceGroup.nodeID;
            if(~qmwQFTV42BlochSynth.isNil
                or: { ~qmwQFTV42BlochSourceGroupID != groupID }) {
                ~qmwQFTV42BlochSynth !? { |synth| synth.free };
                defineSynth.value;
                s.sync;
                ~qmwQFTV42BlochSynth = Synth.tail(
                    ~qmwQFTV3SourceGroup,
                    \qmwQFTV42BlochSpatialVoice,
                    [
                        // Voice-mixer channels belong on the main source bus.
                        // The former field-bus route silently sent Bloch to
                        // hardware 3–4 while every adjacent voice used 1–2.
                        \out, ~qmwQFTV3SourceBus,
                        \voiceGainBus, ~qmwQFTV3VoiceGainBus.index + 4,
                        \fxSendBus, if(~qmwQFTV42BFXSendBus.notNil, {
                            ~qmwQFTV42BFXSendBus.index
                        }, { 0 }),
                        \fxSendControlBus, if(~qmwQFTV42BFXSendControlBus.notNil, {
                            ~qmwQFTV42BFXSendControlBus.index + 4
                        }, { 0 }),
                        \fxEnabled, (~qmwQFTV42BFXEnabled ? false).asInteger
                    ]
                );
                ~qmwQFTV42BlochSourceGroupID = groupID;
                ~qmwQFTV42BlochVoiceOnline = true;
                "QMW V4.2 Bloch audio online: mixer lane 5 / main outputs 1-2."
                    .postln;
            };
            pushAudio.value;
        } {
            ~qmwQFTV42BlochSynth = nil;
            ~qmwQFTV42BlochSourceGroupID = nil;
            ~qmwQFTV42BlochVoiceOnline = false;
        };
        0.1.wait;
    }
}).play(AppClock);

~qmwQFTV42BlochStatusRoutine = Routine({
    inf.do { { refreshControls.value }.defer; 0.5.wait }
}).play(AppClock);

cleanup = {
    if(~qmwQFTV42BlochCleaning.not) {
        ~qmwQFTV42BlochCleaning = true;
        ~qmwQFTV42BlochAudioRoutine !? { |routine| routine.stop };
        ~qmwQFTV42BlochStatusRoutine !? { |routine| routine.stop };
        installMainButton !? { |routine| routine.stop };
        ~qmwQFTV42BlochSynth !? { |synth| synth.set(\gate, 0) };
        ~qmwQFTV42BlochWindow !? { |window| window.close };
        4.do { |qubit|
            OSCdef(("qmwQFTV42BlochQ" ++ qubit).asSymbol).free
        };
        [\qmwQFTV42BlochPurity, \qmwQFTV42BlochCoherence,
            \qmwQFTV42BlochEntropy,
            \qmwQFTV42BlochHamiltonianRatios].do { |key| OSCdef(key).free };
        ~qmwQFTV42BlochSynth = nil;
        ~qmwQFTV42BlochSourceGroupID = nil;
        ~qmwQFTV42BlochVoiceOnline = false;
    };
};
~qmwQFTV42BlochCleanup = cleanup;

priorStop = ~qmwQFTV3Stop;
~qmwQFTV3Stop = {
    cleanup.value;
    priorStop.value;
};

"QMW V4.2 Bloch spatial voice ready: mirror UDP %, fifth-channel gain defaults to zero."
    .format(blochPort).postln;
)
