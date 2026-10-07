/*
QMW Unified Instrument Workspace Launcher V1

One recoverable navigation surface for the V3 instrument.  Every button only
fronts or recreates an existing GUI; it never changes rho, geometry, sound
parameters, routing, or the running audio graph.
*/
(
var openWorkspace, closeWorkspace, styleButton, invoke, openHmiUnavailable;

~qmwuCloseWorkspace !? { ~qmwuCloseWorkspace.value };
~qmwuWorkspaceWindow = nil;
~qmwuWorkspaceButton = nil;

invoke = { |opener|
    opener !? { |function| function.value };
};

// The eight-path Field is intentionally an opt-in launch component.  Do not
// leave a Workspace button that silently does nothing when that component was
// disabled for a conservative audio session.
openHmiUnavailable = {
    var window;
    window = Window("Harmonic Memory Field is not loaded", Rect(310, 190, 560, 196))
        .front.background_(Color.fromHexString("11151c"));
    StaticText(window, Rect(18, 16, 524, 24))
        .string_("HARMONIC MEMORY FIELD  /  NOT LOADED IN THIS SESSION")
        .font_(Font("Helvetica Neue", 13, true)).stringColor_(Color.fromHexString("f4a261"));
    StaticText(window, Rect(18, 52, 524, 76))
        .string_("The eight-path interference receiver is opt-in so a conservative session carries no extra continuous delay graph. Relaunch once with QMW_HARMONIC_MEMORY_INTERFERENCE=1 to load its Field panel. The four-node Harmonic Memory Audition is independent and remains available.")
        .stringColor_(Color.white.alpha_(0.82));
    Button(window, Rect(18, 142, 524, 32))
        .states_([["CLOSE", Color.white, Color.fromHexString("264653")]])
        .action_({ window.close });
};

styleButton = { |parent, rect, label, color, action|
    Button(parent, rect)
        .states_([[label, Color.white, color]])
        .font_(Font("Helvetica Neue", 11, true))
        .action_(action)
};

openWorkspace = {
    if(~qmwuWorkspaceWindow.notNil, {
        ~qmwuWorkspaceWindow.front;
    }, {
        ~qmwuWorkspaceWindow = Window(
            "QMW Unified Instrument — Workspace", Rect(220, 82, 700, 450)
        ).front.background_(Color.fromHexString("11151c"));
        StaticText(~qmwuWorkspaceWindow, Rect(18, 14, 664, 28))
            .string_("WORKSPACE  /  REOPEN INSTRUMENT PANELS")
            .font_(Font("Helvetica Neue", 16, true))
            .stringColor_(Color.fromHexString("dcecff"));
        StaticText(~qmwuWorkspaceWindow, Rect(18, 44, 664, 30))
            .string_("These are navigation shortcuts only. Closing a subpanel never changes the sounding state; the main QRM window remains the session owner.")
            .font_(Font("Helvetica Neue", 10))
            .stringColor_(Color.fromHexString("a9c5dd"));

        StaticText(~qmwuWorkspaceWindow, Rect(18, 84, 204, 18))
            .string_("PERFORM").stringColor_(Color.fromHexString("ffd166"));
        styleButton.(~qmwuWorkspaceWindow, Rect(18, 110, 204, 34), "MAIN INSTRUMENT", Color.fromHexString("263241"), {
            ~qrmWindow !? _.front;
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(18, 152, 204, 34), "TIME + FX + PRESETS", Color.fromHexString("263241"), {
            invoke.(~qrmOpenPerformance);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(18, 194, 204, 34), "TUNING + SCALA", Color.fromHexString("263241"), {
            invoke.(~qrmOpenTuning);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(18, 236, 204, 34), "AUDIO ROUTING", Color.fromHexString("263241"), {
            invoke.(~qrmOpenAudioRouting);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(18, 278, 204, 34), "V3_MATRIX ROUTING", Color.fromHexString("17465b"), {
            invoke.(~qmxOpenPanel);
        });

        StaticText(~qmwuWorkspaceWindow, Rect(248, 84, 204, 18))
            .string_("SPECTRAL GEOMETRY").stringColor_(Color.fromHexString("8ecae6"));
        styleButton.(~qmwuWorkspaceWindow, Rect(248, 110, 204, 34), "MODAL SPECTRAL VOICE", Color.fromHexString("17465b"), {
            invoke.(~qmsvOpenPanel);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(248, 152, 204, 34), "MODAL GEOMETRY", Color.fromHexString("17465b"), {
            invoke.(~qmgOpenPanel);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(248, 194, 204, 34), "RELATIONAL SPECTRUM", Color.fromHexString("17465b"), {
            invoke.(~qrsOpenPanel);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(248, 236, 204, 34),
            if(~qmrAvailable ? false, { "RINGS BODY" }, { "RINGS BODY (OFF)" }),
            Color.fromHexString("17465b"), {
            invoke.(~qmrOpenPanel);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(248, 336, 204, 34), "HEADPHONE BINAURAL", Color.fromHexString("17465b"), {
            invoke.(~qmbOpenPanel);
        });
        StaticText(~qmwuWorkspaceWindow, Rect(248, 282, 204, 44))
            .string_("Open these when shaping the shared Laplacian spectral body; use the main instrument for the 20 M-mode gains.")
            .font_(Font("Helvetica Neue", 10)).stringColor_(Color.fromHexString("a9c5dd"));

        StaticText(~qmwuWorkspaceWindow, Rect(478, 84, 204, 18))
            .string_("INTERACTION + OBSERVERS").stringColor_(Color.fromHexString("ff67d4"));
        styleButton.(~qmwuWorkspaceWindow, Rect(478, 110, 204, 34), "HILBERT INTERACTION", Color.fromHexString("4a2849"), {
            invoke.(~qriOpenPanel);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(478, 152, 204, 34), "BOSONIC QHO + FM", Color.fromHexString("4a2849"), {
            invoke.(~qriOpenQHOControls);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(478, 194, 204, 34), "PROJECTION + FLUX", Color.fromHexString("4a2849"), {
            invoke.(~qriOpenMeasurementControls);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(478, 236, 204, 34), "16 PROJECTIVE OUTPUTS", Color.fromHexString("4a2849"), {
            invoke.(~qriOpenProjectiveOutputs);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(478, 278, 204, 34), "FOUR-QUBIT PREPARATION", Color.fromHexString("4a2849"), {
            invoke.(~qriOpenPreparationControls);
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(248, 294, 204, 34),
            if(~qmwHmiOpenPanel.notNil, { "HARMONIC MEMORY FIELD" }, { "HARMONIC FIELD (OFF)" }),
            Color.fromHexString("17465b"), {
            if(~qmwHmiOpenPanel.notNil, {
                invoke.(~qmwHmiOpenPanel);
            }, {
                openHmiUnavailable.value;
            });
        });
        styleButton.(~qmwuWorkspaceWindow, Rect(464, 294, 204, 34), "HARMONIC MEMORY AUDITION", Color.fromHexString("264653"), {
            invoke.(~qmwHmdOpenPanel);
        });

        StaticText(~qmwuWorkspaceWindow, Rect(18, 386, 664, 50))
            .string_("Ergonomic rule: use this Workspace to recover windows, not as another sound-design layer. Main, performance, and modal voice are the everyday path; the other panels are specialized views.")
            .font_(Font("Helvetica Neue", 11)).stringColor_(Color.fromHexString("80ed99"));
        ~qmwuWorkspaceWindow.onClose = { ~qmwuWorkspaceWindow = nil };
    });
};
closeWorkspace = {
    ~qmwuWorkspaceWindow !? _.close;
    ~qmwuWorkspaceWindow = nil;
};
~qmwuOpenWorkspace = openWorkspace;
~qmwuCloseWorkspace = closeWorkspace;

// Keep the navigation control on the session-owner window, without crowding
// its primary performance, routing, and Hilbert-interaction controls.
if(~qrmWindow.notNil, {
    ~qrmPerformanceButton !? { |view|
        view.bounds_(Rect(423, 18, 112, 24));
        view.states_([["TIME + FX", Color.white, Color.fromHexString("263241")]]);
    };
    ~qrmAudioRoutingButton !? { |view|
        view.bounds_(Rect(545, 18, 105, 24));
        view.states_([["AUDIO I/O", Color.white, Color.fromHexString("263241")]]);
    };
    ~qriMainButton !? { |view|
        view.bounds_(Rect(660, 18, 120, 24));
        view.states_([["HILBERT", Color.white, Color.fromHexString("263241")]]);
    };
    ~qmwuWorkspaceButton = Button(~qrmWindow, Rect(790, 18, 110, 24))
        .states_([["WORKSPACE", Color.white, Color.fromHexString("17465b")]])
        .font_(Font("Helvetica Neue", 10, true))
        .action_({ openWorkspace.value });
});
)
