/*
QMW V4.2 QHO Parseval overtone bank

This is a read-only audio adapter for the canonical 16-level QHO. It keeps
V4.2's musical contract: one persistent voice per overtone/lane, with the
existing fundamental, pitch ratios, odd/even stereo placement, and field-lane
mixer downstream. It does not feed a summed carrier through the 20-mode QRM
body and it does not create a new event clock.
*/
(
var qhoRoot = "/qmw/qho/v1";
var qhoSchema = "qmw.qho.osc.v1.2";
var qhoPort = (~qmwQFTV42ParsevalQHOPort ? 17830).asInteger;
var qhoControl = NetAddr(
    "127.0.0.1", (~qmwQFTV42ParsevalQHOControlPort ? 17831).asInteger
);
var defineSynth, computeMapping, pushAudio, refreshControls, openControls;
var installMainButton, cleanup, priorStop;
var modeMenu, basisMenu, stateMenu, targetSlider, gainSlider, phaseSlider;
var powerView, amplitudeView, metrics, status, mainButton;
var textColor = Color.fromHexString("dcecff");
var panelColor = Color.fromHexString("101722");
var fieldColor = Color.fromHexString("080b10");

thisProcess.openUDPPort(qhoPort);

~qmwQFTV42ParsevalMode = ~qmwQFTV42ParsevalMode ? 0;
~qmwQFTV42ParsevalBasis = ~qmwQFTV42ParsevalBasis ? 0;
~qmwQFTV42ParsevalTargetRMS = ~qmwQFTV42ParsevalTargetRMS ? 0.18;
~qmwQFTV42ParsevalGain = 0.0; // safe exact bypass on every launch
~qmwQFTV42ParsevalPhaseDepth = ~qmwQFTV42ParsevalPhaseDepth ? 1.0;
~qmwQFTV42ParsevalFrame = (
    revision: -1, time: 0.0,
    basisPopulations: Array.fill(3, { Array.fill(16, 0.0) }),
    coherenceMagnitudes: Array.fill(15, 0.0),
    coherencePhases: Array.fill(15, 0.0),
    matrixPowerBins: Array.fill(16, 0.0),
    matrixPhaseBins: Array.fill(16, 0.0),
    purity: 0.0, matrixPowerSum: 0.0, parsevalResidual: 0.0
);
~qmwQFTV42ParsevalStage = nil;
~qmwQFTV42ParsevalCompatible = false;
~qmwQFTV42ParsevalLastSeen = -1e9;
~qmwQFTV42ParsevalSynth = nil;
~qmwQFTV42ParsevalSourceGroupID = nil;
~qmwQFTV42ParsevalWindow = nil;
~qmwQFTV42ParsevalCleaning = false;

defineSynth = {
    SynthDef(\qmwQFTV42ParsevalOvertoneBank, {
        |out=0, outputGain=0, stereoWidth=1, gate=1,
        fxSendBus=0, fxSendControlBus=0, fxEnabled=0|
        var frequencies = NamedControl.kr(
            \frequencies, Array.series(16, 72, 72), 0.08
        ).clip(1, SampleRate.ir * 0.45);
        var amplitudes = NamedControl.kr(
            \amplitudes, Array.fill(16, 0.0), 0.08
        ).max(0);
        var phases = NamedControl.kr(
            \phases, Array.fill(16, 0.0), 0.08
        );
        var laneGains = NamedControl.kr(
            \laneGains, Array.fill(16, 1.0), 0.08
        ).clip(0, 2);
        var width = Lag.kr(stereoWidth.clip(0, 1), 0.05);
        var envelope = EnvGen.kr(Env.asr(0.04, 1, 0.16), gate, doneAction: 2);
        // Sixteen independent oscillator voices are mixed only at the stereo
        // output. There is no resonator fan-out and no event-node allocation.
        var voices = Mix.fill(16, { |index|
            Pan2.ar(
                SinOsc.ar(
                    frequencies[index], phases[index],
                    amplitudes[index] * laneGains[index]
                ),
                (((index % 2) * 2) - 1) * width
            )
        });
        var emitted = Limiter.ar(
            LeakDC.ar(voices) * Lag.kr(outputGain.clip(0, 1.5), 0.08)
                * envelope,
            0.95
        );
        var fxSend = Lag.kr(In.kr(fxSendControlBus).clip(0, 1), 0.03)
            * fxEnabled.clip(0, 1);
        Out.ar(out, emitted);
        Out.ar(fxSendBus, emitted * fxSend);
    }).add;
};
~qmwQFTV42ParsevalDefineSynth = defineSynth;

computeMapping = {
    var frame = ~qmwQFTV42ParsevalFrame;
    var powers = if(~qmwQFTV42ParsevalMode == 0, {
        frame[\basisPopulations][~qmwQFTV42ParsevalBasis].copy
    }, {
        frame[\matrixPowerBins].copy
    });
    var ratios = ~qmwQFTV3SitePitchRatios ? Array.series(16, 1, 1);
    var fundamental = (~qmwQFTV3Fundamental ? 72).asFloat;
    var nyquist = ((s.sampleRate ? 48000) * 0.45);
    var frequencies = Array.fill(16, { |index|
        (fundamental * (ratios[index] ? (index + 1))).clip(1, nyquist)
    });
    var activeMask = Array.fill(16, { |index|
        if((fundamental * (ratios[index] ? (index + 1))) < nyquist, {
            1.0
        }, { 0.0 })
    });
    var activePowers = powers * activeMask;
    var activePower = activePowers.sum;
    var normalization = if(~qmwQFTV42ParsevalMode == 0, {
        if(activePower > 1e-12, { activePower.sqrt }, { 1.0 })
    }, { 1.0 });
    var amplitudes = Array.fill(16, { |index|
        activePowers[index].sqrt * 2.sqrt
            * ~qmwQFTV42ParsevalTargetRMS / normalization
    });
    var phases = Array.fill(16, 0.0);
    var predictedRMS;
    if(~qmwQFTV42ParsevalMode == 0, {
        if(~qmwQFTV42ParsevalBasis == 0, {
            15.do { |index|
                var denominator = (
                    frame[\basisPopulations][0][index]
                    * frame[\basisPopulations][0][index + 1]
                ).sqrt.max(1e-12);
                var reliability = (
                    frame[\coherenceMagnitudes][index] / denominator
                ).clip(0, 1);
                phases[index + 1] = phases[index]
                    - (frame[\coherencePhases][index] * reliability
                        * ~qmwQFTV42ParsevalPhaseDepth);
            };
        });
        predictedRMS = if(activePower > 1e-12, {
            ~qmwQFTV42ParsevalTargetRMS
        }, { 0.0 });
    }, {
        phases = frame[\matrixPhaseBins].collect { |phase|
            phase * ~qmwQFTV42ParsevalPhaseDepth
        };
        predictedRMS = ~qmwQFTV42ParsevalTargetRMS * activePower.sqrt;
    });
    (
        powers: powers, frequencies: frequencies, amplitudes: amplitudes,
        phases: phases, activePower: activePower,
        fullPower: powers.sum, predictedRMS: predictedRMS
    )
};
~qmwQFTV42ParsevalComputeMapping = computeMapping;

refreshControls = {
    var mapping = computeMapping.value;
    var frame = ~qmwQFTV42ParsevalFrame;
    var basisNames = ["FOCK", "QFT-16", "WALSH-HADAMARD"];
    var powerPeak = mapping[\powers].maxItem.max(1e-12);
    var amplitudePeak = mapping[\amplitudes].maxItem.max(1e-12);
    var live = (Main.elapsedTime - ~qmwQFTV42ParsevalLastSeen) < 2.0;
    modeMenu !? { |view| view.value_(~qmwQFTV42ParsevalMode) };
    basisMenu !? { |view|
        view.value_(~qmwQFTV42ParsevalBasis)
            .enabled_(~qmwQFTV42ParsevalMode == 0)
    };
    targetSlider !? { |view| view.value_(~qmwQFTV42ParsevalTargetRMS) };
    gainSlider !? { |view| view.value_(~qmwQFTV42ParsevalGain) };
    phaseSlider !? { |view| view.value_(~qmwQFTV42ParsevalPhaseDepth) };
    powerView !? { |view| view.value_(mapping[\powers] / powerPeak) };
    amplitudeView !? { |view| view.value_(mapping[\amplitudes] / amplitudePeak) };
    status !? { |view|
        view.string_(if(live, {
            "QHO v1.2 LIVE  /  revision %  /  sixteen persistent voices"
                .format(frame[\revision])
        }, {
            "WAITING FOR QHO v1.2 FRAMES ON UDP %".format(qhoPort)
        })).stringColor_(if(live, {
            Color.fromHexString("80ed99")
        }, { Color.fromHexString("ffbf69") }))
    };
    metrics !? { |view|
        view.string_(
            (
                "%  /  %  /  target RMS %  /  mapped RMS %\n"
                ++ "active power %  full power %  purity %  residual %"
            ).format(
                if(~qmwQFTV42ParsevalMode == 0, {
                    "FIXED RMS / BASIS TIMBRE"
                }, { "PURITY -> ENERGY" }),
                if(~qmwQFTV42ParsevalMode == 0, {
                    basisNames[~qmwQFTV42ParsevalBasis]
                }, { "unitary FFT2(rho), row-power pooled" }),
                ~qmwQFTV42ParsevalTargetRMS.round(0.0001),
                mapping[\predictedRMS].round(0.0001),
                mapping[\activePower].round(0.000001),
                mapping[\fullPower].round(0.000001),
                frame[\purity].round(0.000001),
                frame[\parsevalResidual].round(0.000000000001)
            )
        )
    };
};

pushAudio = {
    var mapping = computeMapping.value;
    var laneGains = if(~qmwQFTV3EffectiveFieldLaneGains.notNil, {
        ~qmwQFTV3EffectiveFieldLaneGains.()
    }, { Array.fill(16, 1.0) });
    var rendererGate = if((~qmwQFTV3RendererMode ? 2) == 1, { 0.0 }, { 1.0 });
    ~qmwQFTV42ParsevalSynth !? { |synth|
        synth.setn(\frequencies, mapping[\frequencies]);
        synth.setn(\amplitudes, mapping[\amplitudes]);
        synth.setn(\phases, mapping[\phases]);
        synth.setn(\laneGains, laneGains);
        synth.set(
            \outputGain, ~qmwQFTV42ParsevalGain * rendererGate,
            \stereoWidth, ~qmwQFTV3OddEvenStereoWidth ? 1.0
        );
    };
    refreshControls.value;
};
~qmwQFTV42ParsevalPushAudio = pushAudio;

openControls = {
    if(~qmwQFTV42ParsevalWindow.notNil, {
        ~qmwQFTV42ParsevalWindow.front
    }, {
        ~qmwQFTV42ParsevalWindow = Window(
            "V4.2 Parseval Overtone Bank", Rect(250, 58, 760, 650)
        ).front.background_(panelColor);
        StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 12, 728, 24))
            .string_("PARSEVAL OVERTONE BANK  /  SIXTEEN INDEPENDENT V4.2 VOICES")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(textColor);
        StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 42, 728, 42))
            .string_(
                "Power changes lane amplitudes only. V4.2 retains its fundamental, pitch map, "
                ++ "odd/even stereo, field-lane mixer, and separate pluck stream."
            ).stringColor_(textColor);

        StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 96, 92, 20))
            .string_("POWER MODE").stringColor_(Color.fromHexString("8ecae6"));
        modeMenu = PopUpMenu(~qmwQFTV42ParsevalWindow, Rect(110, 92, 306, 26))
            .items_(["FIXED RMS / BASIS TIMBRE", "PURITY -> ENERGY"])
            .value_(~qmwQFTV42ParsevalMode)
            .action_({ |menu|
                ~qmwQFTV42ParsevalMode = menu.value; pushAudio.value
            });
        StaticText(~qmwQFTV42ParsevalWindow, Rect(430, 96, 64, 20))
            .string_("BASIS").stringColor_(Color.fromHexString("8ecae6"));
        basisMenu = PopUpMenu(~qmwQFTV42ParsevalWindow, Rect(496, 92, 248, 26))
            .items_(["FOCK", "QFT-16", "WALSH-HADAMARD"])
            .value_(~qmwQFTV42ParsevalBasis)
            .action_({ |menu|
                ~qmwQFTV42ParsevalBasis = menu.value; pushAudio.value
            });
        targetSlider = EZSlider(
            ~qmwQFTV42ParsevalWindow, Rect(16, 134, 354, 30),
            "target carrier RMS", ControlSpec(0, 0.5, \lin, 0.0001),
            { |view|
                ~qmwQFTV42ParsevalTargetRMS = view.value; pushAudio.value
            }, ~qmwQFTV42ParsevalTargetRMS, labelWidth: 124, numberWidth: 58
        );
        gainSlider = EZSlider(
            ~qmwQFTV42ParsevalWindow, Rect(390, 134, 354, 30),
            "overtone-bank gain", ControlSpec(0, 1.5, \lin, 0.001),
            { |view|
                ~qmwQFTV42ParsevalGain = view.value; pushAudio.value
            }, ~qmwQFTV42ParsevalGain, labelWidth: 124, numberWidth: 58
        );
        phaseSlider = EZSlider(
            ~qmwQFTV42ParsevalWindow, Rect(16, 174, 354, 30),
            "phase depth", ControlSpec(0, 1, \lin, 0.001),
            { |view|
                ~qmwQFTV42ParsevalPhaseDepth = view.value; pushAudio.value
            }, ~qmwQFTV42ParsevalPhaseDepth, labelWidth: 124, numberWidth: 58
        );
        StaticText(~qmwQFTV42ParsevalWindow, Rect(390, 178, 98, 20))
            .string_("QHO STATE").stringColor_(Color.fromHexString("8ecae6"));
        stateMenu = PopUpMenu(~qmwQFTV42ParsevalWindow, Rect(490, 174, 254, 26))
            .items_(["vacuum", "fock", "coherent", "thermal", "squeezed"])
            .value_(2)
            .action_({ |menu|
                qhoControl.sendMsg(
                    "/qmw/qho/v1/control/state", menu.items[menu.value]
                )
            });

        status = StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 220, 728, 24))
            .font_(Font("Menlo", 10, true));
        metrics = StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 250, 728, 52))
            .font_(Font("Menlo", 9, true))
            .stringColor_(Color.fromHexString("f2cc8f"));
        StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 314, 728, 18))
            .string_("POWER SHARES  /  display peak-normalized only")
            .stringColor_(Color.fromHexString("8ecae6"));
        powerView = MultiSliderView(
            ~qmwQFTV42ParsevalWindow, Rect(16, 336, 728, 86)
        ).size_(16).isFilled_(true)
            .fillColor_(Color.fromHexString("ff7ac6")).background_(fieldColor);
        StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 434, 728, 18))
            .string_("MAPPED OVERTONE AMPLITUDES  /  H1 ... H16")
            .stringColor_(Color.fromHexString("8ecae6"));
        amplitudeView = MultiSliderView(
            ~qmwQFTV42ParsevalWindow, Rect(16, 456, 728, 86)
        ).size_(16).isFilled_(true)
            .fillColor_(Color.fromHexString("80ed99")).background_(fieldColor);
        StaticText(~qmwQFTV42ParsevalWindow, Rect(16, 554, 728, 66))
            .string_(
                "Mapped RMS is before overtone-bank gain, the existing 16-lane field mixer, "
                ++ "stereo presentation, limiter, and hardware output. The bank is one persistent "
                ++ "Synth with 16 oscillators; it allocates no per-frame or per-event nodes."
            ).stringColor_(textColor);
        ~qmwQFTV42ParsevalWindow.onClose = {
            ~qmwQFTV42ParsevalWindow = nil;
            modeMenu = nil; basisMenu = nil; stateMenu = nil;
            targetSlider = nil; gainSlider = nil; phaseSlider = nil;
            powerView = nil; amplitudeView = nil; metrics = nil; status = nil;
        };
        refreshControls.value;
    });
};
~qmwQFTV42OpenParsevalOvertoneBank = openControls;

installMainButton = Routine({
    while({ ~qmwQFTV3Window.isNil }, { 0.1.wait });
    {
        mainButton = Button(~qmwQFTV3Window, Rect(730, 2690, 360, 30))
            .states_([[
                "PARSEVAL OVERTONE BANK  /  16 independent voices",
                Color.black, Color.fromHexString("80ed99")
            ]])
            .action_({ openControls.value });
    }.defer;
}).play(AppClock);

OSCdef(\qmwQFTV42ParsevalBegin, { |msg|
    ~qmwQFTV42ParsevalCompatible = (msg[3].asString == qhoSchema);
    if(~qmwQFTV42ParsevalCompatible) {
        ~qmwQFTV42ParsevalStage = ~qmwQFTV42ParsevalFrame.copy;
        ~qmwQFTV42ParsevalStage[\revision] = msg[1].asInteger;
        ~qmwQFTV42ParsevalStage[\time] = msg[2].asFloat;
        ~qmwQFTV42ParsevalStage[\populationSeen] = false;
        ~qmwQFTV42ParsevalStage[\coherenceMagnitudeSeen] = false;
        ~qmwQFTV42ParsevalStage[\coherencePhaseSeen] = false;
        ~qmwQFTV42ParsevalStage[\qftSeen] = false;
        ~qmwQFTV42ParsevalStage[\hadamardSeen] = false;
        ~qmwQFTV42ParsevalStage[\matrixPowerSeen] = false;
        ~qmwQFTV42ParsevalStage[\matrixPhaseSeen] = false;
        ~qmwQFTV42ParsevalStage[\parsevalSeen] = false;
    };
}, qhoRoot ++ "/frame/begin", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalPopulations, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qmwQFTV42ParsevalStage[\fockPopulations] =
            msg.copyRange(2, 17).collect(_.asFloat);
        ~qmwQFTV42ParsevalStage[\populationSeen] = true;
    };
}, qhoRoot ++ "/populations", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalCoherenceMagnitude, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 17 }) {
        ~qmwQFTV42ParsevalStage[\coherenceMagnitudes] =
            msg.copyRange(2, 16).collect(_.asFloat);
        ~qmwQFTV42ParsevalStage[\coherenceMagnitudeSeen] = true;
    };
}, qhoRoot ++ "/coherence/1/magnitude", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalCoherencePhase, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 17 }) {
        ~qmwQFTV42ParsevalStage[\coherencePhases] =
            msg.copyRange(2, 16).collect(_.asFloat);
        ~qmwQFTV42ParsevalStage[\coherencePhaseSeen] = true;
    };
}, qhoRoot ++ "/coherence/1/phase", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalQFT, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qmwQFTV42ParsevalStage[\qftPopulations] =
            msg.copyRange(2, 17).collect(_.asFloat);
        ~qmwQFTV42ParsevalStage[\qftSeen] = true;
    };
}, qhoRoot ++ "/basis/qft/populations", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalHadamard, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qmwQFTV42ParsevalStage[\hadamardPopulations] =
            msg.copyRange(2, 17).collect(_.asFloat);
        ~qmwQFTV42ParsevalStage[\hadamardSeen] = true;
    };
}, qhoRoot ++ "/basis/hadamard/populations", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalMatrixPower, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qmwQFTV42ParsevalStage[\matrixPowerBins] =
            msg.copyRange(2, 17).collect(_.asFloat);
        ~qmwQFTV42ParsevalStage[\matrixPowerSeen] = true;
    };
}, qhoRoot ++ "/matrix-spectrum/power", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalMatrixPhase, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 18 }) {
        ~qmwQFTV42ParsevalStage[\matrixPhaseBins] =
            msg.copyRange(2, 17).collect(_.asFloat);
        ~qmwQFTV42ParsevalStage[\matrixPhaseSeen] = true;
    };
}, qhoRoot ++ "/matrix-spectrum/phase", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalDiagnostics, { |msg|
    if(~qmwQFTV42ParsevalCompatible
        and: { ~qmwQFTV42ParsevalStage.notNil }
        and: { msg[1].asInteger == ~qmwQFTV42ParsevalStage[\revision] }
        and: { msg.size >= 6 }) {
        ~qmwQFTV42ParsevalStage[\purity] = msg[3].asFloat;
        ~qmwQFTV42ParsevalStage[\matrixPowerSum] = msg[4].asFloat;
        ~qmwQFTV42ParsevalStage[\parsevalResidual] = msg[5].asFloat;
        ~qmwQFTV42ParsevalStage[\parsevalSeen] = true;
    };
}, qhoRoot ++ "/parseval", recvPort: qhoPort);

OSCdef(\qmwQFTV42ParsevalEnd, { |msg|
    var stage = ~qmwQFTV42ParsevalStage;
    if(~qmwQFTV42ParsevalCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }) {
        if(stage[\populationSeen]
            and: { stage[\coherenceMagnitudeSeen] }
            and: { stage[\coherencePhaseSeen] }
            and: { stage[\qftSeen] }
            and: { stage[\hadamardSeen] }
            and: { stage[\matrixPowerSeen] }
            and: { stage[\matrixPhaseSeen] }
            and: { stage[\parsevalSeen] }) {
            stage[\basisPopulations] = [
                stage[\fockPopulations], stage[\qftPopulations],
                stage[\hadamardPopulations]
            ];
            [\populationSeen, \coherenceMagnitudeSeen, \coherencePhaseSeen,
                \qftSeen, \hadamardSeen, \matrixPowerSeen,
                \matrixPhaseSeen, \parsevalSeen, \fockPopulations,
                \qftPopulations, \hadamardPopulations].do { |key|
                stage.removeAt(key)
            };
            ~qmwQFTV42ParsevalFrame = stage;
            ~qmwQFTV42ParsevalLastSeen = Main.elapsedTime;
            ~qmwQFTV42ParsevalStage = nil;
            ~qmwQFTV42ParsevalCompatible = false;
            { pushAudio.value }.defer;
        } {
            ~qmwQFTV42ParsevalStage = nil;
            ~qmwQFTV42ParsevalCompatible = false;
        };
    };
}, qhoRoot ++ "/frame/end", recvPort: qhoPort);

~qmwQFTV42ParsevalAudioRoutine = Routine({
    inf.do {
        var groupID;
        if(s.serverRunning and: { ~qmwQFTV3AudioReady ? false }
            and: { ~qmwQFTV3SourceGroup.notNil }
            and: { ~qmwQFTV3FieldBus.notNil }) {
            groupID = ~qmwQFTV3SourceGroup.nodeID;
            if(~qmwQFTV42ParsevalSynth.isNil
                or: { ~qmwQFTV42ParsevalSourceGroupID != groupID }) {
                ~qmwQFTV42ParsevalSynth !? { |synth| synth.free };
                defineSynth.value;
                s.sync;
                ~qmwQFTV42ParsevalSynth = Synth.tail(
                    ~qmwQFTV3SourceGroup,
                    \qmwQFTV42ParsevalOvertoneBank,
                    [
                        \out, ~qmwQFTV3FieldBus,
                        \fxSendBus, if(~qmwQFTV42BFXSendBus.notNil, {
                            ~qmwQFTV42BFXSendBus.index
                        }, { 0 }),
                        \fxSendControlBus, if(~qmwQFTV42BFXSendControlBus.notNil, {
                            ~qmwQFTV42BFXSendControlBus.index + 6
                        }, { 0 }),
                        \fxEnabled, (~qmwQFTV42BFXEnabled ? false).asInteger
                    ]
                );
                ~qmwQFTV42ParsevalSourceGroupID = groupID;
            };
            pushAudio.value;
        } {
            ~qmwQFTV42ParsevalSynth = nil;
            ~qmwQFTV42ParsevalSourceGroupID = nil;
        };
        0.1.wait;
    }
}).play(AppClock);

cleanup = {
    if(~qmwQFTV42ParsevalCleaning.not) {
        ~qmwQFTV42ParsevalCleaning = true;
        ~qmwQFTV42ParsevalAudioRoutine !? { |routine| routine.stop };
        installMainButton !? { |routine| routine.stop };
        ~qmwQFTV42ParsevalSynth !? { |synth| synth.set(\gate, 0) };
        ~qmwQFTV42ParsevalWindow !? { |window| window.close };
        [\qmwQFTV42ParsevalBegin, \qmwQFTV42ParsevalPopulations,
            \qmwQFTV42ParsevalCoherenceMagnitude,
            \qmwQFTV42ParsevalCoherencePhase, \qmwQFTV42ParsevalQFT,
            \qmwQFTV42ParsevalHadamard, \qmwQFTV42ParsevalMatrixPower,
            \qmwQFTV42ParsevalMatrixPhase,
            \qmwQFTV42ParsevalDiagnostics,
            \qmwQFTV42ParsevalEnd].do { |key| OSCdef(key).free };
        ~qmwQFTV42ParsevalSynth = nil;
        ~qmwQFTV42ParsevalSourceGroupID = nil;
    };
};
~qmwQFTV42ParsevalCleanup = cleanup;

priorStop = ~qmwQFTV3Stop;
~qmwQFTV3Stop = {
    cleanup.value;
    priorStop.value;
};

"QMW V4.2 Parseval overtone bank ready: QHO UDP %, gain defaults to zero."
    .format(qhoPort).postln;
)
