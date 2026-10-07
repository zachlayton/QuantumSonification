/*
Unified Instrument Resonator V3 relational-Laplacian sound adapter.

Load after V2. It accepts only complete, monotonic, bounded observer frames.
It never emits an event, changes admitted event energy, changes rho/H, or
retunes the resonator. It reshapes the existing event's modal weights and its
resonator decay only after the V1/V2 event authority has admitted that event.
*/
(
var root = "/qmw/unified/v3/relational_spectral";
var schema = "qmw.unified.relational_spectral.osc.v1";
var port = (~qrsPort ? ("QMW_RELATIONAL_SPECTRAL_PORT".getenv ? "17881").asInteger).asInteger;
var modeCount = 20;
var bandCount = 3;
var commitFrame, shapeEvent, openPanel, closePanel, refreshPanel, styleSlider;

~qrsCleanup !? { ~qrsCleanup.value };
thisProcess.openUDPPort(port);

~qrsPort = port;
~qrsEnabled = ~qrsEnabled ? true;
~qrsExcitationDepth = (~qrsExcitationDepth ? 1.0).clip(0, 1);
~qrsDecayDepth = (~qrsDecayDepth ? 1.0).clip(0, 1);
~qrsBrightnessDepth = (~qrsBrightnessDepth ? 1.0).clip(0, 1);
~qrsStageTimeout = 0.75;
~qrsLastRevision = -1;
~qrsStage = nil;
~qrsWindow = nil;
~qrsReadout = nil;
~qrsPriorRenderEvent = ~qriRenderEvent;
~qrsFrame = (
    revision: -1, time: 0.0, bridge: 0.0, segmentation: 0.0,
    connectivity: 0.0, tension: 0.0, bands: Array.fill(bandCount, 0.0),
    excitation: Array.fill(modeCount, 1.0), decay: Array.fill(modeCount, 1.0),
    brightness: Array.fill(modeCount, 0.5)
);

styleSlider = { |slider|
    slider.labelView.stringColor_(Color.white);
    slider.numberView.normalColor_(Color.white).typingColor_(Color.white)
        .stringColor_(Color.white).background_(Color.fromHexString("080b10"));
    slider.sliderView.background_(Color.fromHexString("080b10"));
    slider
};

refreshPanel = {
    ~qrsReadout !? { |view|
        view.string_("graph rev %  /  bridge %  /  split %  /  connectivity %  /  tension %\n"
            .format(~qrsFrame[\revision], (~qrsFrame[\bridge] * 100).round(0.1),
                (~qrsFrame[\segmentation] * 100).round(0.1),
                (~qrsFrame[\connectivity] * 100).round(0.1),
                (~qrsFrame[\tension] * 100).round(0.1))
            ++ "The graph is a read-only observer. It colors existing modal excitation, decay, and brightness; it does not create plucks or retune geometry spectrum.")
    };
};

commitFrame = { |frame|
    ~qrsFrame = frame;
    ~qrsLastRevision = frame[\revision];
    // OSC callbacks run off the Qt/AppClock thread.  Defer GUI mutation so
    // rapid observer frames cannot flood the live session with Qt errors.
    { refreshPanel.value }.defer;
};

shapeEvent = { |event|
    var sourceWeights, phases, shapedWeights, weightedDecay, peak;
    if(~qrsEnabled.not or: { ~qrsFrame[\revision] < 0 }, { event }, {
        sourceWeights = event[\weights].collect(_.asFloat.abs);
        phases = event[\phases];
        shapedWeights = Array.fill(modeCount, { |index|
            var excitation = 1.0 + (~qrsExcitationDepth * (~qrsFrame[\excitation][index] - 1.0));
            var brightness = 1.0 - (0.35 * ~qrsBrightnessDepth)
                + (0.35 * ~qrsBrightnessDepth * ~qrsFrame[\brightness][index]);
            sourceWeights[index] * excitation * brightness
        });
        peak = shapedWeights.maxItem.max(1e-12);
        shapedWeights = shapedWeights / peak;
        weightedDecay = (sourceWeights.collect { |weight, index|
            weight * (1.0 + (~qrsDecayDepth * (~qrsFrame[\decay][index] - 1.0)))
        }.sum / sourceWeights.sum.max(1e-12)).clip(0.25, 1.75);
        event.copy
            .put(\weights, shapedWeights)
            .put(\phases, phases)
            .put(\decayScale, weightedDecay)
            .put(\relationalSpectralRevision, ~qrsFrame[\revision])
    })
};

// V1/V2 remains the event authority. This hook is deliberately downstream of
// its current/flux admission and leaves event energy untouched.
~qriRenderEvent = { |event, level=1.0|
    ~qrsPriorRenderEvent.value(shapeEvent.value(event), level)
};

openPanel = {
    if(~qrsWindow.notNil, { ~qrsWindow.front }, {
        ~qrsWindow = Window("Unified Instrument Resonator V3 — Relational Spectrum", Rect(145, 145, 760, 306))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qrsWindow, Rect(16, 12, 728, 42))
            .string_("READ-ONLY RELATIONAL LAPLACIAN -> EXISTING 20-MODE RESONATOR")
            .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("dcecff"));
        Button(~qrsWindow, Rect(16, 66, 218, 26))
            .states_([["RELATIONAL SPECTRUM BYPASSED", Color.fromHexString("ffd166"), Color.fromHexString("532b35")],
                ["RELATIONAL SPECTRUM ACTIVE", Color.black, Color.fromHexString("80ed99")]])
            .value_(~qrsEnabled.asInteger).action_({ |button| ~qrsEnabled = button.value > 0 });
        styleSlider.(EZSlider(~qrsWindow, Rect(250, 64, 230, 27), "excitation",
            ControlSpec(0, 1, \lin, 0.01), { |view| ~qrsExcitationDepth = view.value },
            ~qrsExcitationDepth, labelWidth: 74, numberWidth: 48));
        styleSlider.(EZSlider(~qrsWindow, Rect(496, 64, 230, 27), "decay",
            ControlSpec(0, 1, \lin, 0.01), { |view| ~qrsDecayDepth = view.value },
            ~qrsDecayDepth, labelWidth: 52, numberWidth: 48));
        styleSlider.(EZSlider(~qrsWindow, Rect(250, 100, 230, 27), "brightness",
            ControlSpec(0, 1, \lin, 0.01), { |view| ~qrsBrightnessDepth = view.value },
            ~qrsBrightnessDepth, labelWidth: 74, numberWidth: 48));
        ~qrsReadout = StaticText(~qrsWindow, Rect(16, 146, 728, 124))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("8ecae6"));
        ~qrsWindow.onClose = { ~qrsWindow = nil; ~qrsReadout = nil };
        refreshPanel.value;
    });
};
closePanel = { ~qrsWindow !? _.close; ~qrsWindow = nil; ~qrsReadout = nil };
~qrsOpenPanel = openPanel;

OSCdef(\qrsBeginV3, { |msg|
    var valid = (msg.size >= 6) and: { msg[3].asString == schema }
        and: { msg[1].asInteger > ~qrsLastRevision }
        and: { msg[4].asInteger == modeCount } and: { msg[5].asInteger == bandCount };
    ~qrsStage = if(valid, {
        (revision: msg[1].asInteger, time: msg[2].asFloat, scalars: nil,
            bands: Array.fill(bandCount, nil), modes: Array.fill(modeCount, nil),
            deadline: Main.elapsedTime + ~qrsStageTimeout)
    }, { nil });
}, root ++ "/frame/begin", recvPort: port);

OSCdef(\qrsScalarsV3, { |msg|
    if(~qrsStage.notNil and: { msg.size >= 6 } and: { msg[1].asInteger == ~qrsStage[\revision] }) {
        ~qrsStage[\scalars] = msg.copyRange(2, 5).collect(_.asFloat)
    };
}, root ++ "/scalars", recvPort: port);

OSCdef(\qrsBandV3, { |msg|
    var index;
    if(~qrsStage.notNil and: { msg.size >= 4 } and: { msg[1].asInteger == ~qrsStage[\revision] }) {
        index = msg[2].asInteger;
        if(index >= 0 and: { index < bandCount }) { ~qrsStage[\bands][index] = msg[3].asFloat };
    };
}, root ++ "/band", recvPort: port);

OSCdef(\qrsModeV3, { |msg|
    var index;
    if(~qrsStage.notNil and: { msg.size >= 6 } and: { msg[1].asInteger == ~qrsStage[\revision] }) {
        index = msg[2].asInteger;
        if(index >= 0 and: { index < modeCount }) {
            ~qrsStage[\modes][index] = [msg[3].asFloat, msg[4].asFloat, msg[5].asFloat]
        };
    };
}, root ++ "/mode", recvPort: port);

OSCdef(\qrsEndV3, { |msg|
    var stage = ~qrsStage, scalars;
    if(stage.notNil and: { msg.size >= 2 } and: { msg[1].asInteger == stage[\revision] }
        and: { stage[\scalars].notNil } and: { stage[\bands].includes(nil).not }
        and: { stage[\modes].includes(nil).not }) {
        scalars = stage[\scalars];
        commitFrame.value((revision: stage[\revision], time: stage[\time],
            bridge: scalars[0].clip(0, 1), segmentation: scalars[1].clip(0, 1),
            connectivity: scalars[2].clip(0, 1), tension: scalars[3].clip(0, 1),
            bands: stage[\bands].collect(_.clip(0, 1)),
            excitation: stage[\modes].collect { |triple| triple[0].clip(0.20, 1.80) },
            decay: stage[\modes].collect { |triple| triple[1].clip(0.25, 1.75) },
            brightness: stage[\modes].collect { |triple| triple[2].clip(0, 1) }
        ));
    };
    ~qrsStage = nil;
}, root ++ "/frame/end", recvPort: port);

~qrsWatchdog = Routine({ loop {
    if(~qrsStage.notNil and: { Main.elapsedTime > ~qrsStage[\deadline] }) { ~qrsStage = nil };
    0.20.wait;
} }).play(AppClock);

~qrsCleanup = {
    [\qrsBeginV3, \qrsScalarsV3, \qrsBandV3, \qrsModeV3, \qrsEndV3].do { |key| OSCdef(key).free };
    ~qrsWatchdog !? _.stop; ~qrsWatchdog = nil;
    ~qrsStage = nil;
    if(~qrsPriorRenderEvent.notNil) { ~qriRenderEvent = ~qrsPriorRenderEvent };
    closePanel.value;
};

{ openPanel.value }.defer;
"QMW Unified Instrument Resonator V3 relational spectral receiver listening on UDP %".format(port).postln;
)
