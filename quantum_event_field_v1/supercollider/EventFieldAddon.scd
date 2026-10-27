/* Evaluate after v4.2b, or use StartEventField.scd. No Python backend required. */
(
var here = thisProcess.nowExecutingPath.dirname;
~qefShutdown !? { ~qefShutdown.() };
thisProcess.interpreter.executeFile(here +/+ "Model.scd");
thisProcess.interpreter.executeFile(here +/+ "Observables.scd");
thisProcess.interpreter.executeFile(here +/+ "SynthDefs.scd");
~qefSettings = (quantum: 0.08, secondsPerTau: 0.8, decayScale: 1,
    gain: 0.08, fxSend: 0, initial: 0, coherenceDepth: 0, phaseDepth: 0,
    diracDepth: 0, diracIndex: 0);
~qefRanges = (quantum: [0.02, 0.5], secondsPerTau: [0.25, 4],
    decayScale: [0.1, 4], gain: [0, 0.3], fxSend: [0, 1],
    coherenceDepth: [0,1], phaseDepth: [0,1], diracDepth: [0,1], diracIndex: [0,3]);
~qefMappingKeys = [\coherenceDepth, \phaseDepth, \diracDepth, \diracIndex];
~qefMappingValues = { ~qefMappingKeys.collect { |key| ~qefSettings[key] } };
~qefRecentFrames = List.new;
~qefDisplayed = (frame: ~qefFrame.(0));
~qefDisplayed[\observables] = ~qefObservables.(~qefDisplayed[\frame]);
~qefLatency = 0.12; ~qefEpoch = ~qefEpoch ? 0;
~qefRunning = false; ~qefCount = 0; ~qefDropped = 0;
~qefBusPairs = [
    [\ringMixBus, \qmwQFTV3RingModMixBus],
    [\ringFrequencyBus, \qmwQFTV3RingModFrequencyBus],
    [\wavefoldMixBus, \qmwQFTV3WavefoldMixBus],
    [\wavefoldDriveBus, \qmwQFTV3WavefoldDriveBus],
    [\wavefoldWarpAmountBus, \qmwQFTV3WavefoldWarpAmountBus],
    [\wavefoldWarpShapeBus, \qmwQFTV3WavefoldWarpShapeBus],
    [\fuzzMixBus, \qmwQFTV3FuzzMixBus], [\fuzzDriveBus, \qmwQFTV3FuzzDriveBus],
    [\fuzzSecondBus, \qmwQFTV3FuzzSecondBus], [\fuzzThirdBus, \qmwQFTV3FuzzThirdBus],
    [\fuzzHigherBus, \qmwQFTV3FuzzHigherBus], [\fuzzBiasBus, \qmwQFTV3FuzzBiasBus],
    [\fuzzToneBus, \qmwQFTV3FuzzToneBus]
];
~qefHostReady = {
    s.serverRunning and: { ~qmwQFTV3AudioReady == true }
    and: { ~qmwQFTV3SourceGroup.notNil } and: { ~qmwQFTV3SourceBus.notNil }
    and: { ~qmwQFTV42BFXSendBus.notNil }
    and: { ~qefBusPairs.every { |pair| currentEnvironment[pair[1]].notNil } }
};
~qefStop = {
    var group = ~qefGroup, audio = ~qefAudio, pop = ~qefPop, epoch = ~qefEpoch;
    var obs = ~qefObsBus, mapping = ~qefMappingBus;
    ~qefRunning = false;
    ~qefStartRoutine !? { |r| r.stop }; ~qefStartRoutine = nil;
    ~qefRunner !? { |r| r.stop }; ~qefRunner = nil;
    ~qefMixer !? { |n| if(s.serverRunning, { n.set(\enabled, 0) }) };
    // Keep IDs allocated until all already-timestamped bundles have passed.
    SystemClock.sched(~qefLatency + 0.05, {
        if(epoch == ~qefEpoch, {
            if(s.serverRunning, { group !? { |g| g.free } });
            audio !? { |b| b.free }; pop !? { |b| b.free };
            obs !? { |b| b.free }; mapping !? { |b| b.free };
        }); nil
    });
    ~qefGroup = nil; ~qefAudio = nil; ~qefPop = nil; ~qefMixer = nil;
    ~qefObsBus = nil; ~qefMappingBus = nil; ~qefRecentFrames.clear;
};
~qefOnQuit = {
    ~qefEpoch = ~qefEpoch + 1;
    ~qefStartRoutine !? { |r| r.stop }; ~qefStartRoutine = nil;
    ~qefRunner !? { |r| r.stop }; ~qefRunner = nil;
    ~qefRunning = false;
    ~qefGroup = nil; ~qefAudio = nil; ~qefPop = nil; ~qefMixer = nil;
    ~qefObsBus = nil; ~qefMappingBus = nil; ~qefRecentFrames.clear;
};
s.onQuitAdd(~qefOnQuit);
~qefSet = { |key, value|
    var range = ~qefRanges[key];
    if(range.notNil and: { value.isNumber } and: { value.isNaN.not }
        and: { value.abs < 1e12 }, {
        ~qefSettings[key] = value.clip(*range);
        if(key == \diracIndex, { ~qefSettings[key] = ~qefSettings[key].round.asInteger });
        if([\gain, \fxSend].includes(key), {
            ~qefMixer !? { |n| n.set(key, ~qefSettings[key]) }
        });
        // A sensitivity change begins a fresh flow integral, without a burst.
        if(key == \quantum, { ~qefResidual = 0.0 ! 4 });
        if(~qefMappingKeys.includes(key), {
            ~qefMappingBus !? { |bus| bus.setn(~qefMappingValues.()) }
        });
    });
};
~qefStart = {
    if(~qefHostReady.(), {
        ~qefStop.();
        ~qefStartRoutine = Routine({
            var args, host = ~qmwQFTV3SourceGroup, startEpoch = ~qefEpoch;
            ~qefDefine.().do { |definition| definition.add }; s.sync;
            if(~qefHostReady.() and: { host === ~qmwQFTV3SourceGroup }
                and: { startEpoch == ~qefEpoch }, {
                ~qefBaseGroup = host;
                ~qefGroup = Group.tail(host);
                ~qefVoiceGroup = Group.head(~qefGroup);
                ~qefAudio = Bus.audio(s, 2); ~qefPop = Bus.control(s, 4);
                ~qefObsBus = Bus.control(s, 16); ~qefMappingBus = Bus.control(s, 4);
                ~qefMappingBus.setn(~qefMappingValues.());
                args = [\inBus, ~qefAudio.index, \out, ~qmwQFTV3SourceBus.index,
                    \fxSendBus, ~qmwQFTV42BFXSendBus.index,
                    \gain, ~qefSettings[\gain], \fxSend, ~qefSettings[\fxSend],
                    \enabled, ~qmwQFTV3SoundEnabled ? 1];
                ~qefBusPairs.do { |pair|
                    args = args ++ [pair[0], currentEnvironment[pair[1]].index]
                };
                ~qefMixer = Synth.tail(~qefGroup, \qefMixerV1, args); s.sync;
                ~qefTau = 0.0; ~qefResidual = 0.0 ! 4;
                ~qefInitial = ~qefSettings[\initial];
                ~qefPrevious = ~qefFrame.(0, ~qefInitial);
                ~qefLatestObservables = ~qefObservables.(~qefPrevious);
                ~qefDisplayed = (frame: ~qefPrevious, observables: ~qefLatestObservables);
                ~qefRecentFrames.clear;
                ~qefPop.setn(~qefPrevious[\p]);
                ~qefObsBus.setn(~qefLatestObservables[\audio]);
                ~qefExpiries = List.new; ~qefCount = 0; ~qefDropped = 0;
                ~qefRunning = true;
                ~qefRunner = Routine({
                    var last = Main.elapsedTime;
                    while { ~qefRunning } {
                        var now, dt, next, crossings, enabled, observables;
                        0.005.wait;
                        now = Main.elapsedTime; dt = now - last; last = now;
                        if(~qefHostReady.().not or: { host !== ~qmwQFTV3SourceGroup }
                            or: { dt > 0.1 }, {
                            "Event field stopped: host changed or scheduling stalled. Restart the field.".warn;
                            ~qefStop.();
                        }, {
                            enabled = ~qmwQFTV3SoundEnabled ? 1;
                            ~qefMixer.set(\enabled, enabled);
                            if(enabled > 0, {
                                ~qefTau = ~qefTau + (dt / ~qefSettings[\secondsPerTau]);
                                next = ~qefFrame.(~qefTau, ~qefInitial);
                                crossings = ~qefCrossings.(~qefPrevious, next, ~qefResidual,
                                    ~qefSettings[\quantum], next[\tau] - ~qefPrevious[\tau]);
                                ~qefExpiries = ~qefExpiries.select { |end| end > now };
                                crossings.do { |event|
                                    var fraction = event[0], site = event[1], frame, duration, source, delay;
                                    frame = ~qefFrame.(~qefPrevious[\tau].blend(next[\tau], fraction), ~qefInitial);
                                    source = frame[\source][site];
                                    duration = ~qefDuration.(frame, site,
                                        ~qefSettings[\secondsPerTau], ~qefSettings[\decayScale]);
                                    delay = ~qefLatency - (dt * (1-fraction));
                                    if(~qefExpiries.size < 96, {
                                        s.makeBundle(delay, {
                                            Synth.tail(~qefVoiceGroup, \qefWaveletV1,
                                                [\out, ~qefAudio.index, \popBus, ~qefPop.index,
                                                \obsBus, ~qefObsBus.index, \mappingBus, ~qefMappingBus.index,
                                                \mappingEnabled, 1, \pairIndex, ~qefPairLookup[site][source],
                                                \pairDirection, if(site < source, { 1 }, { -1 }),
                                                \site, site, \source, source, \duration, duration,
                                                \strength, frame[\p][site].sqrt,
                                                \weightsA, ~qefModes[site].squared,
                                                \weightsB, ~qefModes[source].squared]);
                                        });
                                        ~qefExpiries.add(now + delay + duration + 0.02);
                                        ~qefCount = ~qefCount + 1;
                                    }, { ~qefDropped = ~qefDropped + 1 });
                                };
                                observables = ~qefObservables.(next);
                                s.makeBundle(~qefLatency, {
                                    ~qefPop.setn(next[\p]); ~qefObsBus.setn(observables[\audio]);
                                });
                                ~qefLatestObservables = observables;
                                ~qefRecentFrames.add((time: now + ~qefLatency, frame: next, observables: observables));
                                // Bounded even in headless runs with no GUI consumer.
                                if(~qefRecentFrames.size > 64, { ~qefRecentFrames.removeAt(0) });
                                ~qefPrevious = next;
                            }, { ~qefResidual = 0.0 ! 4 });
                        });
                    };
                }).play(SystemClock);
                "Event field running: exact XX model -> v4.2b source and FX buses.".postln;
            }, { "Base audio changed during startup. Start the field again.".warn });
            ~qefStartRoutine = nil;
        }).play(AppClock);
    }, { "Start v4.2b audio first, then Start field.".warn });
};
~qefShutdown = {
    ~qefStop.(); ~qefWatch !? { |r| r.stop }; ~qefWatch = nil;
    s.onQuitRemove(~qefOnQuit); CmdPeriod.remove(~qefStop);
    ~qefObserverWindow !? { |w| w.close }; ~qefObserverWindow = nil;
    ~qefWindow !? { |w| w.onClose = nil; w.close }; ~qefWindow = nil;
};
CmdPeriod.add(~qefStop);
if(~qefHeadless != true, {
    thisProcess.interpreter.executeFile(here +/+ "ObservablesPanel.scd");
    ~qefWindow = Window("QMW probability-flow event field v1.1", Rect(80, 80, 620, 530)).front;
    StaticText(~qefWindow, Rect(12, 10, 596, 42)).string_(
        "Four-site XX theory | harmonics of 110 Hz | no measurement stream\nRing, fold and fuzz: base controls. Clouds / VST: base return mixer.");
    Button(~qefWindow, Rect(12, 58, 130, 28)).states_([["Start field / reset"]]).action_({ ~qefStart.() });
    Button(~qefWindow, Rect(150, 58, 100, 28)).states_([["Stop field"]]).action_({ ~qefStop.() });
    StaticText(~qefWindow, Rect(270, 60, 120, 24)).string_("Initial site");
    PopUpMenu(~qefWindow, Rect(400, 60, 170, 24)).items_(["1: |1000>", "2: |0100>", "3: |0010>", "4: |0001>"])
        .action_({ |view| ~qefSettings[\initial] = view.value });
    [[\quantum, "Flow per event (lower = denser)"], [\secondsPerTau, "Seconds / model time unit"],
        [\decayScale, "Flow-persistence decay scale"], [\gain, "Field output level"],
        [\fxSend, "Send to Clouds / VST"], [\coherenceDepth, "Coherence -> upper partials"],
        [\phaseDepth, "Coherence -> phase / interference"], [\diracDepth, "Dirac expectation -> stereo motion"]].do { |pair, i|
        var key = pair[0], range = ~qefRanges[key];
        StaticText(~qefWindow, Rect(12, 100+(i*34), 310, 26)).string_(pair[1]);
        NumberBox(~qefWindow, Rect(335, 100+(i*34), 120, 26))
            .value_(~qefSettings[key]).clipLo_(range[0]).clipHi_(range[1])
            .action_({ |view| ~qefSet.(key, view.value) });
    };
    Button(~qefWindow, Rect(12, 378, 170, 28)).states_([["Observables / matrices"]])
        .action_({ ~qefOpenObservables.() });
    StaticText(~qefWindow, Rect(195, 378, 400, 28)).string_("Select the Dirac operator in the observables window.");
    ~qefStatus = StaticText(~qefWindow, Rect(12, 416, 596, 55));
    StaticText(~qefWindow, Rect(12, 480, 596, 40)).string_(
        "Decay = bounded local turnover time, not a quantum lifetime.\nSpectral morph = population-weighted audio interpolation, not state evolution.");
    ~qefWindow.view.children.do { |view| view.font_(Font("Helvetica",12)) };
    ~qefWatch = Routine({ loop {
        var audible = ~qefRunning and: { (~qmwQFTV3SoundEnabled ? 1) > 0 };
        var rate = if(audible, {
            ~qefPrevious[\incoming].sum / (~qefSettings[\quantum] * ~qefSettings[\secondsPerTau])
        }, { 0 });
        while { ~qefRecentFrames.notEmpty and: { ~qefRecentFrames.first[\time] <= Main.elapsedTime } } {
            ~qefDisplayed = ~qefRecentFrames.removeAt(0);
        };
        ~qefObserverView !? { |view| view.refresh };
        ~qefDiracMenu !? { |view| view.value_(~qefSettings[\diracIndex]) };
        ~qefStatus.string_("% | tau % | events % | voices <= % | dropped %\nIncoming-flow rate: % events/s".format(
            if(~qefRunning, { if(audible, { "running" }, { "paused: base Sound off" }) }, { "stopped" }),
            (~qefTau ? 0).round(0.01), ~qefCount,
            if(~qefRunning, { ~qefExpiries.size }, { 0 }), ~qefDropped, rate.round(0.1)));
        0.04.wait;
    } }).play(AppClock);
    ~qefWindow.onClose = { ~qefShutdown.() };
});
"Event field loaded. Start base audio, then Start field. Existing presets are unchanged.".postln;
)
