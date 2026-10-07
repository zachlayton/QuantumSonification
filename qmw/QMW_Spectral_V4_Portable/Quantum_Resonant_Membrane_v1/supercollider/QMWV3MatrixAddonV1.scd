/*
QMW V3_Matrix V1

An additive, language-side routing scene and panel for Unified Instrument V3.
It owns no rho/H evolution, server-output topology, or physical delivery.
This first vertical slice establishes the eight-domain navigation, typed route
cells, per-continuous-route attenuverter/CV controls, and an explicit armed
intervention boundary. The decay-CV child matrix is the first real parameter
route; a later named-bus refactor will make process-to-process audio routes real.
*/
(
var domains, colors, routeKind, routeTarget, ensureRoute, selectedRoute, initializeStereo;
var refresh, selectRoute, openPanel, closePanel, updateSelectedControls, styleSlider;

~qmxCleanup !? { ~qmxCleanup.value };
domains = ["TIME", "QMW", "GEOM", "SOURCE", "EXCITE", "OPS", "ROUTE", "SPACE"];
colors = [
    Color.fromHexString("d99b2d"), Color.fromHexString("9b6ee8"),
    Color.fromHexString("3faeca"), Color.fromHexString("3aaa7e"),
    Color.fromHexString("e5ae4e"), Color.fromHexString("e06d7b"),
    Color.fromHexString("8492a6"), Color.fromHexString("d66459")
];
~qmxDomains = domains;
~qmxRoutes = ~qmxRoutes ? Array.fill(8, { Array.fill(8, { nil }) });
~qmxSelectedSource = (~qmxSelectedSource ? 3).asInteger.clip(0, 7);
~qmxSelectedDestination = (~qmxSelectedDestination ? 5).asInteger.clip(0, 7);
~qmxWindow = nil;
~qmxCells = nil;
~qmxStatus = nil;
~qmxAmount = nil;
~qmxCVSource = nil;
~qmxCVAmount = nil;
~qmxSlew = nil;
~qmxDelay = nil;
~qmxArmButton = nil;
~qmxConnectButton = nil;

routeKind = { |source, destination|
    if(destination == 1, { \intervention }, {
        if(source == 1, { \frame }, {
            if((source == 0) or: { source == 4 }, { \event }, {
                if((source == 3) or: { destination == 5 } or: { destination == 7 }, { \audio }, { \cv })
            })
        })
    })
};
routeTarget = { |source, destination|
    case
    { (source == 3) and: { destination == 7 } } { "primary stereo output buses 1-2 (direct V3 normal)" }
    { destination == 1 } { "declared QMW operation gateway (armed + committed separately)" }
    { source == 1 } { "read-only observer descriptor" }
    { destination == 4 } { "excitation / event admission descriptor" }
    { destination == 5 } { "operator port (VCA, ring, fuzz, filter, feedback)" }
    { destination == 7 } { "space / mix / M-S destination descriptor" }
    { destination == 3 } { "source or modal-field descriptor" }
    { true } { "typed V3_Matrix adapter descriptor" }
};
ensureRoute = { |source, destination|
    var route = ~qmxRoutes[source][destination];
    if(route.isNil, {
        route = (
            source: source, destination: destination,
            kind: routeKind.(source, destination), target: routeTarget.(source, destination),
            active: false, amount: 0.0, cvSource: -1, cvAmount: 0.0,
            slew: 0.0, delay: 0.0, armed: false
        );
        ~qmxRoutes[source][destination] = route;
    });
    route
};
selectedRoute = { ensureRoute.(~qmxSelectedSource, ~qmxSelectedDestination) };
initializeStereo = {
    var observer, event, stereo;
    // Recoverable zero-complexity scene: direct primary stereo on outputs 1-2,
    // no feedback or V3_Matrix cross-route, and no armed QMW intervention.
    ~qmxRoutes = Array.fill(8, { Array.fill(8, { nil }) });
    observer = ensureRoute.(1, 2);
    observer[\active] = true; observer[\amount] = 1.0;
    event = ensureRoute.(0, 4);
    event[\active] = true; event[\amount] = 1.0;
    stereo = ensureRoute.(3, 7);
    stereo[\active] = true; stereo[\amount] = 1.0;
    ~qmxSelectedSource = 3; ~qmxSelectedDestination = 7;

    // Keep V3's existing direct stereo body, while bypassing optional
    // processor/send paths that do not belong in a normal-stereo baseline.
    ~qrmRingMix = 0.0; ~qrmFuzzMix = 0.0;
    ~qrmPushPerformanceFx !? { |push| push.value };
    ~qrmBody !? { |body| body.set(\ringMix, 0.0, \fuzzMix, 0.0) };
    ~qrmRingMixSlider !? { |view| view.value_(0.0) };
    ~qrmFuzzMixSlider !? { |view| view.value_(0.0) };

    // Simple resonant attack + QHO-FM are the tonal startup pair. The three
    // overlapping noise bodies and every fuzz/send path remain opt-in.
    ~qriVoiceGains = [0.82, 0.0, 0.0, 0.82, 0.0, 0.0, 0.0, 0.0];
    ~qriVoiceMutes = Array.fill(8, 0);
    ~qriVoiceDecays = Array.fill(8, 0.11);
    ~qriVoiceFuzzSends = Array.fill(8, 0.0);
    ~qriVoiceTemporalSends = Array.fill(8, 0.0);
    ~qriVoiceFXSends = Array.fill(8, 0.0);
    ~qriMix = 0.45; ~qriEventGain = 0.60; ~qriDecay = 0.11;
    ~qriHmiSend = 0.0;
    ~qmxResetDecayMatrix !? { |reset| reset.value };
    // Normal-stereo recovery must not overwrite the performer's live event
    // density. Re-assert the current request instead of forcing the old 0.20
    // safe-start value, which could make the instrument nearly silent.
    ~qriSetPluckThreshold !? { |setter|
        setter.value(~qriRequestedPluckThreshold ? 0.10)
    };
    ~qriPushVoiceGains !? { |push| push.value };
    ~qriPushVoiceDecays !? { |push| push.value };
    ~qriPushVoiceFuzzSends !? { |push| push.value };
    ~qriPushVoiceTemporalSends !? { |push| push.value };
    ~qriPushVoiceFXSends !? { |push| push.value };
    ~qmwHmiSetMixer !? { |setter| setter.value(0.0) };
    ~qmsvEnabled = false;
    ~qmsvBank !? { |bank| bank.set(\master, 0.0) };
    ~qmsvHilbertExciter !? { |exciter| exciter.set(\master, 0.0) };
    updateSelectedControls.value; refresh.value;
};
styleSlider = { |slider|
    slider.labelView.stringColor_(Color.white);
    slider.numberView.normalColor_(Color.white).typingColor_(Color.white)
        .stringColor_(Color.white).background_(Color.fromHexString("080b10"));
    slider.sliderView.background_(Color.fromHexString("080b10"));
    slider
};

refresh = {
    var route = selectedRoute.value;
    ~qmxCells !? { |cells|
        8.do { |source|
            8.do { |destination|
                var cellRoute = ~qmxRoutes[source][destination];
                var selected = (source == ~qmxSelectedSource) and: { destination == ~qmxSelectedDestination };
                var color = if(selected, { Color.fromHexString("ffd166") }, {
                    if(cellRoute.notNil and: { cellRoute[\active] }, { colors[source].alpha_(0.92) }, { Color.fromHexString("263241") })
                });
                cells[source][destination].background_(color);
                cells[source][destination].string_(if(cellRoute.notNil and: { cellRoute[\active] }, { "●" }, { "·" }));
            };
        };
    };
    ~qmxStatus !? { |view|
        view.string_("% → %  /  %  /  %\n%"
            .format(domains[route[\source]], domains[route[\destination]], route[\kind].asString.toUpper,
                if(route[\active], { "ACTIVE" }, { "STAGED" }), route[\target]));
    };
    ~qmxConnectButton !? { |button|
        button.states_([[if(route[\active], { "DISCONNECT ROUTE" }, { "CONNECT ROUTE" }), Color.white,
            if(route[\active], { Color.fromHexString("8a3342") }, { Color.fromHexString("17465b") })]]);
    };
};
updateSelectedControls = {
    var route = selectedRoute.value;
    ~qmxAmount !? { |view| view.value_(route[\amount]) };
    ~qmxCVSource !? { |view| view.value_(route[\cvSource] + 1) };
    ~qmxCVAmount !? { |view| view.value_(route[\cvAmount]) };
    ~qmxSlew !? { |view| view.value_(route[\slew]) };
    ~qmxDelay !? { |view| view.value_(route[\delay]) };
    ~qmxArmButton !? { |button|
        button.enabled_(route[\kind] == \intervention);
        button.value_(route[\armed].asInteger);
    };
};
selectRoute = { |source, destination|
    ~qmxSelectedSource = source; ~qmxSelectedDestination = destination;
    updateSelectedControls.value; refresh.value;
};
openPanel = {
    if(~qmxWindow.notNil, { ~qmxWindow.front }, {
        var sourceMenu, destinationMenu, x0 = 138, y0 = 112, step = 66;
        ~qmxWindow = Window("Unified Instrument Resonator V3_Matrix", Rect(120, 95, 860, 620))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qmxWindow, Rect(18, 14, 824, 26))
            .string_("V3_MATRIX  /  8 DOMAIN TYPED ROUTING FABRIC")
            .font_(Font("Helvetica Neue", 15, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(~qmxWindow, Rect(18, 42, 824, 36))
            .string_("Select an intersection, then connect it and shape its route. AUDIO and CV routes have a bipolar attenuverter and one assignable CV input. QMW is frame-out only; its input is an armed, declared intervention request.")
            .font_(Font("Helvetica Neue", 10)).stringColor_(Color.fromHexString("a9c5dd"));
        StaticText(~qmxWindow, Rect(18, 84, 110, 18)).string_("SOURCE ↓")
            .font_(Font("Helvetica Neue", 10, true)).stringColor_(Color.fromHexString("8ecae6"));
        8.do { |index|
            StaticText(~qmxWindow, Rect(x0 + (index * step), 84, 60, 18)).string_(domains[index])
                .align_(\center).font_(Font("Helvetica Neue", 9, true)).stringColor_(colors[index]);
            StaticText(~qmxWindow, Rect(18, y0 + (index * 48), 112, 22)).string_(domains[index] ++ " →")
                .font_(Font("Helvetica Neue", 10, true)).stringColor_(colors[index]);
        };
        ~qmxCells = Array.fill(8, { |source|
            Array.fill(8, { |destination|
                Button(~qmxWindow, Rect(x0 + (destination * step), y0 + (source * 48), 58, 34))
                    .font_(Font("Menlo", 16, true)).action_({ selectRoute.(source, destination) })
            })
        });
        sourceMenu = PopUpMenu(~qmxWindow, Rect(18, 505, 146, 26)).items_(domains)
            .value_(~qmxSelectedSource).action_({ |view| selectRoute.(view.value, ~qmxSelectedDestination) });
        destinationMenu = PopUpMenu(~qmxWindow, Rect(174, 505, 146, 26)).items_(domains)
            .value_(~qmxSelectedDestination).action_({ |view| selectRoute.(~qmxSelectedSource, view.value) });
        sourceMenu.background_(Color.fromHexString("080b10")).stringColor_(Color.white);
        destinationMenu.background_(Color.fromHexString("080b10")).stringColor_(Color.white);
        ~qmxConnectButton = Button(~qmxWindow, Rect(330, 505, 180, 26)).font_(Font("Helvetica Neue", 10, true))
            .action_({ |button| var route = selectedRoute.value; route[\active] = route[\active].not; refresh.value });
        ~qmxArmButton = Button(~qmxWindow, Rect(520, 505, 150, 26))
            .states_([["INTERVENTION SAFE", Color.fromHexString("ffd166"), Color.fromHexString("532b35")], ["INTERVENTION ARMED", Color.black, Color.fromHexString("80ed99")]])
            .action_({ |button| selectedRoute.value[\armed] = button.value > 0; refresh.value });
        Button(~qmxWindow, Rect(680, 505, 160, 26)).states_([["INITIALIZE STEREO", Color.white, Color.fromHexString("17465b")]])
            .action_({ initializeStereo.value });
        ~qmxAmount = styleSlider.(EZSlider(~qmxWindow, Rect(18, 548, 194, 25), "amount", ControlSpec(-1, 1, \lin, 0.01),
            { |view| selectedRoute.value[\amount] = view.value; refresh.value }, selectedRoute.value[\amount], labelWidth: 66, numberWidth: 42));
        ~qmxCVSource = PopUpMenu(~qmxWindow, Rect(222, 548, 120, 25)).items_(["CV: none"] ++ domains)
            .value_(selectedRoute.value[\cvSource] + 1).action_({ |view| selectedRoute.value[\cvSource] = view.value - 1; refresh.value });
        ~qmxCVSource.background_(Color.fromHexString("080b10")).stringColor_(Color.white);
        ~qmxCVAmount = styleSlider.(EZSlider(~qmxWindow, Rect(350, 548, 160, 25), "CV depth", ControlSpec(-1, 1, \lin, 0.01),
            { |view| selectedRoute.value[\cvAmount] = view.value; refresh.value }, selectedRoute.value[\cvAmount], labelWidth: 72, numberWidth: 42));
        ~qmxSlew = styleSlider.(EZSlider(~qmxWindow, Rect(520, 548, 150, 25), "slew s", ControlSpec(0, 2, \lin, 0.005),
            { |view| selectedRoute.value[\slew] = view.value; refresh.value }, selectedRoute.value[\slew], labelWidth: 50, numberWidth: 42));
        ~qmxDelay = styleSlider.(EZSlider(~qmxWindow, Rect(680, 548, 160, 25), "delay s", ControlSpec(0, 2, \lin, 0.005),
            { |view| selectedRoute.value[\delay] = view.value; refresh.value }, selectedRoute.value[\delay], labelWidth: 56, numberWidth: 42));
        ~qmxStatus = StaticText(~qmxWindow, Rect(18, 578, 650, 30)).font_(Font("Menlo", 10)).stringColor_(Color.fromHexString("80ed99"));
        Button(~qmxWindow, Rect(680, 578, 160, 26))
            .states_([["DECAY CV MATRIX", Color.black, Color.fromHexString("ffcf70")]])
            .action_({ ~qmxOpenDecayMatrix !? { |open| open.value } });
        ~qmxWindow.onClose = { ~qmxWindow = nil; ~qmxCells = nil; ~qmxStatus = nil; ~qmxAmount = nil; ~qmxCVSource = nil; ~qmxCVAmount = nil; ~qmxSlew = nil; ~qmxDelay = nil; ~qmxArmButton = nil; ~qmxConnectButton = nil };
        updateSelectedControls.value; refresh.value;
    });
};
closePanel = { ~qmxWindow !? _.close; ~qmxWindow = nil };
~qmxOpenPanel = openPanel;
~qmxClosePanel = closePanel;
~qmxInitializeStereo = initializeStereo;
// Public scene-recall seam. Routes here are language-side descriptors only;
// recalling them does not enact an intervention or mutate QMW state.
~qmxApplyScene = { updateSelectedControls.value; refresh.value };
~qmxCleanup = {
    ~qmxDecayCleanup !? { |cleanup| cleanup.value };
    closePanel.value
};
)
