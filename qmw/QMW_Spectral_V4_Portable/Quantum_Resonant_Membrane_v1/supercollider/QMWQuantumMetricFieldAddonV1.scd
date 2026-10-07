/*
Quantum Metric Field -> Unified Resonant Instrument V3 adapter.

Complete revisioned 20-mode frames deform the existing resonant body. The
trajectory profile shapes only events already admitted by ~qriRenderEvent.
This adapter never receives rho, creates events, or writes m0--m19 controls.
*/
(
var root = "/qmw/metric/unified";
var schema = "qmw.metric.unified.v1";
var modeCount = 20;
var port = ("QMW_QUANTUM_METRIC_PORT".getenv ? "17890").asInteger;
var commitFrame, stagePart, shapeEvent, refresh;

~qmfCleanup !? { ~qmfCleanup.value };
thisProcess.openUDPPort(port);

~qmfEnabled = ("QMW_QUANTUM_METRIC_ENABLED".getenv ? "0").asInteger > 0;
~qmfGeometryInfluence = ("QMW_QUANTUM_METRIC_INFLUENCE".getenv ? "0.65")
    .asFloat.clip(0, 1);
~qmfExcitationInfluence = ("QMW_QUANTUM_METRIC_EXCITATION".getenv ? "0.75")
    .asFloat.clip(0, 1);
~qmfDecayInfluence = ("QMW_QUANTUM_METRIC_DECAY".getenv ? "0.35")
    .asFloat.clip(0, 1);
~qmfLastFrameId = -1;
~qmfStage = nil;
~qmfFrame = nil;
~qmfWindow = nil;
~qmfReadout = nil;
~qmfPriorRenderEvent = ~qriRenderEvent;
~qmfPriorUpdatePitchRatios = ~qrmUpdatePitchRatios;
~qmfCurrentRatios = nil;
~qmfTargetRatios = nil;
~qmfCurrentDecay = nil;
~qmfTargetDecay = nil;

refresh = {
    ~qmfReadout !? { |view|
        var frame = ~qmfFrame;
        view.string_(if(frame.isNil, {
            "WAITING FOR COMPLETE QMF FRAME"
        }, {
            "frame % / source % / t % / mode %\nratio %..% / pan % / |A| %\nQMF changes body and admitted-event distribution; m0-m19 and event energy remain upstream."
                .format(
                    frame[\id], frame[\sourceRevision], frame[\time].round(0.001),
                    frame[\topography], frame[\ratios].minItem.round(0.001),
                    frame[\ratios].maxItem.round(0.001), frame[\pan].round(0.001),
                    frame[\connection].squared.sum.sqrt.round(0.001)
                )
        }))
    }
};

commitFrame = { |frame|
    var baselineRatios, baselineDecay, decayMean, decayShape;
    ~qmfFrame = frame;
    ~qmfLastFrameId = frame[\id];
    if(~qmfEnabled, {
        // Re-evaluate every older tuning owner first, then compose QMF once.
        ~qmfPriorUpdatePitchRatios.value;
        baselineRatios = ~qrmPitchRatios.copy;
        baselineDecay = (~qrmModalDecaySeconds ? Array.fill(modeCount, 0.28)).copy;
        decayMean = frame[\decay].mean.max(1e-9);
        decayShape = frame[\decay].collect { |value| (value / decayMean).clip(0.25, 4) };
        ~qmfTargetRatios = Array.fill(modeCount, { |index|
            baselineRatios[index] * frame[\ratios][index].clip(0.25, 4)
                .pow(~qmfGeometryInfluence)
        });
        ~qmfTargetDecay = Array.fill(modeCount, { |index|
            baselineDecay[index] * decayShape[index].pow(~qmfDecayInfluence)
        });
        ~qmfCurrentRatios = ~qmfCurrentRatios ? baselineRatios.copy;
        ~qmfCurrentDecay = ~qmfCurrentDecay ? baselineDecay.copy;
    });
    { refresh.value }.defer;
};

stagePart = { |msg, key, expected|
    var frameId = msg[1].asInteger;
    if(~qmfStage.notNil and: { ~qmfStage[\id] == frameId }
        and: { msg.size == (expected + 2) }, {
        ~qmfStage[key] = msg.copyRange(2, msg.size - 1).collect(_.asFloat);
    });
};

OSCdef(\qmfBegin, { |msg|
    var frameId = msg[1].asInteger;
    if(msg.size == 7 and: { msg[4].asString == schema }
        and: { msg[5].asInteger == modeCount }
        and: { frameId > ~qmfLastFrameId }, {
        ~qmfStage = (
            id: frameId, sourceRevision: msg[2].asInteger,
            time: msg[3].asFloat, topography: msg[6].asString
        );
    });
}, root ++ "/frame/begin", recvPort: port);
OSCdef(\qmfRatios, { |msg| stagePart.value(msg, \ratios, modeCount) },
    root ++ "/geometry_ratios", recvPort: port);
OSCdef(\qmfDecay, { |msg| stagePart.value(msg, \decay, modeCount) },
    root ++ "/decay_seconds", recvPort: port);
OSCdef(\qmfExcitation, { |msg| stagePart.value(msg, \excitation, modeCount) },
    root ++ "/excitation", recvPort: port);
OSCdef(\qmfConnection, { |msg| stagePart.value(msg, \connection, modeCount * modeCount) },
    root ++ "/connection", recvPort: port);
OSCdef(\qmfPan, { |msg|
    var frameId = msg[1].asInteger;
    if(~qmfStage.notNil and: { ~qmfStage[\id] == frameId } and: { msg.size == 3 }, {
        ~qmfStage[\pan] = msg[2].asFloat.clip(-1, 1);
    });
}, root ++ "/trajectory_pan", recvPort: port);
OSCdef(\qmfEnd, { |msg|
    var frameId = msg[1].asInteger;
    var required = [\ratios, \decay, \excitation, \connection, \pan];
    if(~qmfStage.notNil and: { ~qmfStage[\id] == frameId }
        and: { required.every { |key| ~qmfStage[key].notNil } }, {
        commitFrame.value(~qmfStage.copy);
        ~qmfStage = nil;
    });
}, root ++ "/frame/end", recvPort: port);

shapeEvent = { |event|
    var original, profile, shaped, mixed, originalNorm, shapedNorm, mixedNorm;
    if(~qmfEnabled.not or: { ~qmfFrame.isNil }, { event }, {
        original = event[\weights].collect(_.asFloat);
        profile = ~qmfFrame[\excitation].collect(_.asFloat.abs);
        originalNorm = original.squared.sum.sqrt;
        shaped = original * profile;
        shapedNorm = shaped.squared.sum.sqrt;
        if((originalNorm > 1e-12) and: { shapedNorm > 1e-12 }, {
            shaped = shaped * (originalNorm / shapedNorm);
            mixed = (original * (1 - ~qmfExcitationInfluence))
                + (shaped * ~qmfExcitationInfluence);
            mixedNorm = mixed.squared.sum.sqrt.max(1e-12);
            mixed = mixed * (originalNorm / mixedNorm);
            event.copy.put(\weights, mixed)
                .put(\quantumMetricFrameId, ~qmfFrame[\id])
                .put(\quantumMetricPan, ~qmfFrame[\pan]);
        }, { event });
    })
};

// Compose after every existing event observer; no event is generated here.
~qriRenderEvent = { |event, level=1.0|
    ~qmfPriorRenderEvent.value(shapeEvent.value(event), level)
};

// Smooth body retuning independently of the incoming frame rate.
~qmfControlTask = Routine({ loop {
    if(~qmfEnabled and: { ~qmfTargetRatios.notNil }, {
        ~qmfCurrentRatios = ~qmfCurrentRatios
            + ((~qmfTargetRatios - ~qmfCurrentRatios) * 0.18);
        ~qmfCurrentDecay = ~qmfCurrentDecay
            + ((~qmfTargetDecay - ~qmfCurrentDecay) * 0.18);
        ~qrmPitchRatios = ~qmfCurrentRatios.copy;
        ~qrmModalDecaySeconds = ~qmfCurrentDecay.copy;
        ~qrmBody !? { |node|
            node.setn(\frequencyRatios, ~qrmPitchRatios);
            node.setn(\modalDecaySeconds, ~qrmModalDecaySeconds);
        };
    });
    0.02.wait;
} }).play(AppClock);

~qmfOpenPanel = {
    if(~qmfWindow.notNil, { ~qmfWindow.front }, {
        ~qmfWindow = Window("Unified Instrument — Quantum Metric Field", Rect(920, 470, 650, 205))
            .front.background_(Color.fromHexString("101522"));
        Button(~qmfWindow, Rect(16, 14, 220, 26))
            .states_([["QMF BYPASSED"], ["QMF APPLIED"]])
            .value_(~qmfEnabled.asInteger).action_({ |button|
                ~qmfEnabled = button.value > 0;
                if(~qmfEnabled.not, {
                    ~qmfCurrentRatios = nil; ~qmfTargetRatios = nil;
                    ~qmfCurrentDecay = nil; ~qmfTargetDecay = nil;
                    ~qmfPriorUpdatePitchRatios.value;
                }, {
                    ~qmfFrame !? { |frame| commitFrame.value(frame) };
                });
            });
        ~qmfReadout = StaticText(~qmfWindow, Rect(16, 52, 618, 132))
            .font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("a8dadc"));
        ~qmfWindow.onClose = { ~qmfWindow = nil; ~qmfReadout = nil };
        refresh.value;
    });
};

~qmfCleanup = {
    ~qmfControlTask !? _.stop; ~qmfControlTask = nil;
    [\qmfBegin, \qmfRatios, \qmfDecay, \qmfExcitation,
        \qmfConnection, \qmfPan, \qmfEnd].do { |key| OSCdef(key).free };
    if(~qmfPriorRenderEvent.notNil) { ~qriRenderEvent = ~qmfPriorRenderEvent };
    ~qmfWindow !? _.close; ~qmfWindow = nil; ~qmfReadout = nil;
};

Routine({ 0.8.wait; ~qmfOpenPanel.value }).play(AppClock);
"Quantum Metric Field adapter listening on UDP %".format(port).postln;
)
