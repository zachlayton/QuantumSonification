/* Routed v2 stereo note/body junction; Analysis sources are declared upstream. No rho reconstruction or quantum controls.
   Private dry return only. Final output solo is reversible; old sources run.
   Ringz decaytime is T60 = amplitude tau * ln(1000). */
(
var generation, finite, validPacket, install, adapterFile;
adapterFile = "QMW_NOTE_TIMBRE_SC_FILE".getenv ? thisProcess.nowExecutingPath;
~qntDetachNavigation !? { ~qntDetachNavigation.value };
~qntRemove !? { ~qntRemove.value };
generation = Object.new;
~qntGeneration = generation;
~qntArmed = false;
~qntSolo = false;
~qntHold = false;
~qntBasis = 0; ~qntExcitation = 0; ~qntOctave = 0;
~qntAmplitudeSource = 1; ~qntRhythmSource = 1; ~qntQuantization = 0; ~qntAnalysisBasis = 0;
~qntLastConfigSentAt = -1e9; ~qntRouteLabel = "ANALYSIS: waiting for routed source metadata";
~qntConfigRevision = 0; ~qntAppliedRevision = -1;
~qntSession = nil; ~qntRetired = Set.new;
~qntSequence = -1; ~qntObservedRevision = -1; ~qntSourceRevision = -1;
~qntLastValidAt = -1e9; ~qntLastEventAt = -1e9;
~qntNodes = List.new; ~qntLevel = 1.0;
// Read-only acceptance telemetry: copies of fully accepted/admitted actual packets.
~qntLastAcceptedPacket = nil; ~qntLastAdmittedPacket = nil;
~qntAcceptedCount = 0; ~qntAdmittedCount = 0;
~qntInstalled = false; ~qntSourceLabel = "Waiting for actual runtime H/rho";
~qntConfigTarget = NetAddr("127.0.0.1", 17931);

finite = { |value| value.isNumber and: { value.abs < 1e12 } };
validPacket = { |a|
    var good = true, strings, modes, require;
    ~qntRejectReason = nil;
    require = { |condition, reason|
        if(good and: { condition.not }, { good=false; ~qntRejectReason=reason });
        good
    };
    strings = [1,12,14,15,16,17,31,33,107];
    require.(a.size == 108, "argument count=" ++ a.size ++ " expected108");
    if(good, {
        require.((a[0] == 2) and: { a[32] == 16 }, "schema or mode count");
        strings.do { |i|
            // sclang decodes OSC type-tag s as Symbol. Normalize only these
            // declared text fields; never coerce numeric or arbitrary objects.
            if(a[i].isKindOf(Symbol), { a[i] = a[i].asString });
            require.(a[i].isKindOf(String) and: { a[i].size > 0 },
                "text argument=" ++ i ++ " class=" ++ a[i].class ++ " value=" ++ a[i]);
        };
        a.do { |v,i| if(strings.includes(i).not, {
            require.(finite.(v), "nonfinite numeric argument=" ++ i ++ " class=" ++ v.class);
        }) };
    });
    if(good, {
        [2,3,4,7,13].do { |i|
            require.(a[i] >= 0 and: { a[i].asInteger == a[i] }, "integer argument=" ++ i);
        };
        [8,9,10,11,26,35].do { |i|
            require.([0,1].includes(a[i]), "flag argument=" ++ i ++ " value=" ++ a[i]);
        };
        require.(a[6] >= 0 and: { a[30] == 1 and: { a[31] == "model_energy"
            and: { a[33] == "dimensionless" } } }, "source dt/hbar/units");
        require.(a[15] == "four_qubit_computational:q0-lsb" and: { a[16].size == 64
            and: { a[16].every { |c| "0123456789abcdef".includes(c) } } }, "basis/provenance identity");
        require.(a[12].size == 4 and: { a[12].every { |c| "IXYZ".includes(c) } }, "Pauli operator label");
        require.(~qntRetired.includes(a[1]).not, "retired source session");
        require.(~qntSession.isNil or: { ~qntSession == a[1] }, "foreign session: reconnect required");
        require.(a[2] > ~qntSequence, "sequence=" ++ a[2] ++ " previous=" ++ ~qntSequence);
        require.(a[7] >= ~qntAppliedRevision, "configuration revision moved backward");
        require.(a[4] > ~qntObservedRevision, "observed revision=" ++ a[4] ++ " previous=" ++ ~qntObservedRevision);
        require.(a[3] <= a[4], "source revision exceeds observed revision");
        require.((a[8] == 1) or: { a[3] >= ~qntSourceRevision }, "unheld source revision moved backward");
        require.([0,1,2].includes(a[102]) and: { [0,1].includes(a[103])
            and: { [0,1].includes(a[104]) and: { [0,1,2,3].includes(a[105])
            and: { a[106] == 0 } } } }, "routing source/quantization/representation/ANALYSIS enum");
        require.(a[107].size == 64 and: { a[107].every { |c| "0123456789abcdef".includes(c) } },
            "routing configuration digest");
        require.(a[100] >= 0 and: { a[100] <= 1.0 }, "normalized excitation amplitude=" ++ a[100]);
        if(a[35] == 1, {
            require.(a[101] >= 0.5 and: { a[101] <= 8.0 }, "mapped musical interval=" ++ a[101]);
            [18,19].do { |i| require.(a[i] >= 0 and: { a[i] < 16 and: { a[i].asInteger == a[i] } }, "note endpoint=" ++ i) };
            require.(a[18] != a[19] and: { a[17] != "-" }, "note identity/endpoints");
            require.(a[20] > 0 and: { a[20] < (s.sampleRate * 0.45) }, "note Hz=" ++ a[20] ++ " sampleRate=" ++ s.sampleRate);
            require.(a[21] > 0 and: { a[21] <= 1.000001 }, "raw diagnostic activity=" ++ a[21]);
            require.((a[22] - if(a[9] == 1, { 0.25 }, { 0.001 })).abs < 1e-7, "note duration=" ++ a[22]);
        }, {
            require.(a[17] == "-" and: { a[18] == -1 and: { a[19] == -1 and: { a[21] == 0 and: { a[100] == 0 and: { a[101] == 0 } } } } }, "no-note sentinel fields");
        });
        modes = a.copyRange(36,99).clump(4);
        modes.do { |row,i|
            require.(row[0] > 0 and: { row[0] < (s.sampleRate * 0.45) }, "mode=" ++ i ++ " Hz=" ++ row[0]);
            require.(row[1] >= 0 and: { row[1] <= 1.000001 }, "mode=" ++ i ++ " gain=" ++ row[1]);
            require.(row[2] > 0 and: { row[2] <= 2 and: { row[3] == 0 } }, "mode=" ++ i ++ " tau/phase");
        };
    });
    good
};
~qntValidatePacket = validPacket; // Read-only diagnostic/testing seam.
~qntLastRejectAt = -1e9;

~qntSendConfig = {
    ~qntConfigRevision = (~qntConfigRevision.max(~qntAppliedRevision)) + 1;
    ~qntTransmitConfig.value;
};
~qntTransmitConfig = {
    // Retries keep the same revision and complete configuration. Python accepts
    // an identical retry idempotently; a differing equal revision is rejected.
    ~qntLastConfigSentAt = Main.elapsedTime;
    ~qntConfigTarget.sendMsg("/qmw/note_timbre/v2/config", ~qntConfigRevision,
        ~qntBasis, ~qntExcitation, ~qntOctave, ~qntHold.asInteger,
        ~qntAmplitudeSource, ~qntRhythmSource, ~qntQuantization, ~qntAnalysisBasis);
};
~qntReconnect = {
    ~qntSession !? { ~qntRetired.add(~qntSession) };
    ~qntArmed = false; ~qntArmButton !? { |v| v.value_(0) };
    ~qntSession = nil; ~qntSequence = -1; ~qntObservedRevision = -1;
    ~qntSourceRevision = -1; ~qntAppliedRevision = -1; ~qntLastValidAt = -1e9;
    ~qntVoiceGroup !? _.freeAll;
    ~qntNodes.clear;
    ~qntSourceLabel = "Reconnect: waiting for a new native source session";
};
~qntCanSound = {
    ~qntInstalled and: { ~qntArmed and: { ~qrmSonify ? false } }
        and: { ~qriEnabled ? false } and: { ~qriPlucksEnabled.notNil and: { ~qriPlucksEnabled.value } }
        and: { Main.elapsedTime - ~qntLastValidAt < 1.5 }
        and: { ~qntAppliedRevision >= ~qntConfigRevision }
};

~qntRemove = {
    ~qntArmed = false; ~qntInstalled = false; ~qntGeneration = nil;
    OSCdef(\qntCompleteFrame).free;
    // Removing the final selector restores the original stereo mix. Free only
    // this adapter's groups/buses; never stop server, old sources, or authority.
    ~qntRouterGroup !? _.free; ~qntRouterGroup = nil;
    ~qntVoiceGroup !? _.free; ~qntVoiceGroup = nil;
    ~qntPrivateBus !? _.free; ~qntPrivateBus = nil;
    ~qntGateBus !? _.free; ~qntGateBus = nil;
    ~qntNodes !? _.clear;
    ~qntWindow !? { |v| v.onClose_(nil); v.close }; ~qntWindow = nil;
};

// Keep a navigation-only recovery entry after the opt-in layer is removed.
// Bringing an existing panel forward changes no audio controls. Reopening a
// removed layer evaluates this addon again and therefore starts DISARMED.
~qntOpenPanel = {
    if(~qntWindow.notNil, { ~qntWindow.front }, {
        if(adapterFile.notNil and: { File.exists(adapterFile) }, {
            thisProcess.interpreter.executeFile(adapterFile);
        }, { "QMW NOTE/BODY: recovery requires its original addon path.".warn });
    });
};
~qntEnsureWorkspaceEntry = {
    if(~qmwuWorkspaceWindow.notNil and: { ~qntWorkspaceParent !== ~qmwuWorkspaceWindow }, {
        ~qntWorkspaceParent = ~qmwuWorkspaceWindow;
        ~qntWorkspaceEntry = Button(~qmwuWorkspaceWindow,Rect(18,336,204,34))
            .states_([["NOTE / BODY",Color.white,Color.fromHexString("17465b")]])
            .font_(Font("Helvetica Neue",11,true))
            .toolTip_("Bring the note/body panel forward. A removed layer reopens disarmed.")
            .action_({ ~qntOpenPanel.value });
    });
};
~qntInstallNavigation = {
    var owner = ~qmwuWorkspaceButton, originalAction, wrappedAction;
    if(owner.notNil, {
        originalAction = owner.action;
        wrappedAction = { |view|
            originalAction !? { |action| action.value(view) };
            ~qntEnsureWorkspaceEntry.value;
        };
        owner.action_(wrappedAction);
        ~qntDetachNavigation = {
            if(owner.action === wrappedAction, { owner.action_(originalAction) });
            if(~qntWorkspaceParent.notNil and: { ~qntWorkspaceParent === ~qmwuWorkspaceWindow }, {
                ~qntWorkspaceEntry !? _.remove;
            });
            ~qntWorkspaceParent=nil; ~qntWorkspaceEntry=nil;
        };
        ~qntEnsureWorkspaceEntry.value;
    }, { "QMW NOTE/BODY: WORKSPACE unavailable; use ~qntOpenPanel.value to recover.".warn });
};
~qntInstallNavigation.value;

install = {
    if((~qrmOutputChannels ? 2) != 2 or: { s.options.numOutputBusChannels != 2 }, {
        "QMW NOTE/TIMBRE: this opt-in adapter requires a declared two-output stereo session.".warn;
    }, {
        if(~qriVoiceGainBus.isNil or: { ~qriFXSendBus.isNil }, {
            "QMW NOTE/TIMBRE: waiting for V3 mixer/FX bus ownership; no fallback output.".warn;
        }, {
            SynthDef(\qntEventV2, { |outBus=0, noteHz=220, excitationAmplitude=0, excitationMode=0, duration=0.001|
                var frequencies = \frequencies.kr(Array.fill(16,220));
                var gains = \gains.kr(Array.fill(16,0));
                var tau = \tau.kr(Array.fill(16,0.18));
                var strike = EnvGen.ar(Env([0,1,0],[0.0005,0.0005],\lin));
                var pitched = SinOsc.ar(noteHz,0) * EnvGen.ar(Env([0,1,0],[duration*0.5,duration*0.5],\sine));
                // Declared acoustic profile calibration, independent of rho.
                var excitation = Select.ar(excitationMode,[strike,pitched*0.02]) * excitationAmplitude;
                var signal = Mix(Ringz.ar(excitation,frequencies,tau*6.907755) * gains)
                    * (48000 / SampleRate.ir);
                var life = EnvGen.kr(Env([1,1,0],[duration+1.45,0.03]),doneAction:2);
                // Fixed acoustic headroom, independent of source/body values.
                // Keeps tested normal mixer levels below the protective limiter.
                Out.ar(outBus, (LeakDC.ar(signal)*life).dup * (0.125 / 1.4142135623730951));
            }).add;
            SynthDef(\qntStereoReturnV1, { |privateBus=0, gateBus=0, voiceGainBus=0|
                var previous = In.ar(0,2);
                var tail = In.ar(privateBus,2);
                var gate = In.kr(gateBus,3);
                var simple = In.kr(voiceGainBus, 8)[0].clip(0,1.5);
                var selected = Limiter.ar(tail * gate[0] * simple * gate[2],0.7);
                // Gate AFTER limiter too: no buffered tail when mute/lock reaches
                // this control block. Lag is intentionally absent on downward mute.
                selected = selected * (gate[0] > 0) * (simple > 0) * (gate[2] > 0);
                ReplaceOut.ar(0, Select.ar(gate[1],[previous + selected,selected]));
            }).add;
            s.sync;
            ~qntPrivateBus = Bus.audio(s,2);
            ~qntGateBus = Bus.control(s,3); ~qntGateBus.setn([0,0,1]);
            ~qntRoot = Group.basicNew(s,0);
            ~qntVoiceGroup = Group.tail(~qntRoot).register;
            ~qntRouterGroup = Group.tail(~qntRoot).register;
            ~qntRouter = Synth.tail(~qntRouterGroup,\qntStereoReturnV1,[
                \privateBus,~qntPrivateBus.index,\gateBus,~qntGateBus.index,
                \voiceGainBus,~qriVoiceGainBus.index]);
            ~qntInstalled = true;
            OSCdef(\qntCompleteFrame, { |message,time,address|
                var a = message.copyRange(1,message.size-1);
                var rows, node, gain, newSession, now = Main.elapsedTime;
                if(address.ip == "127.0.0.1" and: { validPacket.(a) }, {
                    ~qntLastAcceptedPacket = a.copy; ~qntAcceptedCount = ~qntAcceptedCount + 1;
                    newSession = ~qntSession.isNil;
                    ~qntSession = a[1]; ~qntSequence = a[2]; ~qntSourceRevision = a[3];
                    ~qntObservedRevision = a[4]; ~qntAppliedRevision = a[7]; ~qntLastValidAt = now;
                    // Reapply the visible observer controls after a source
                    // restart or SC reload. Gate until that atomic config lands.
                    if(newSession, { ~qntSendConfig.value });
                    ~qntSourceLabel = if(a[8] == 1, { "HELD NATIVE SNAPSHOT" }, { "LIVE NATIVE H/RHO" })
                        ++ " rev=" ++ a[3] ++ " observed=" ++ a[4] ++ " cfg=" ++ a[7]
                        ++ "\n" ++ a[14] ++ " A=" ++ a[12] ++ " targetHz=" ++ a[20].round(0.01);
                    if(a[35] == 1, {
                        ~qntRouteLabel = "ANALYSIS: amplitude " ++ ["|A|", "|A| sqrt(population)", "diagnostic activity"][a[102].asInteger]
                            ++ " -> " ++ a[100].round(0.0001) ++ "; raw activity=" ++ a[21].round(0.0001)
                            ++ "\nRhythm " ++ ["|energy gap|", "absolute transition order"][a[103].asInteger]
                            ++ " -> " ++ a[101].round(0.001) ++ " s; " ++ ["continuous", "ratio lattice"][a[104].asInteger]
                            ++ "; basis " ++ ["computational", "Hamiltonian", "QHO", "QFT"][a[105].asInteger];
                    });
                    rows = a.copyRange(36,99).clump(4);
                    ~qntNodes = ~qntNodes.select { |n| n.isPlaying };
                    gain = (~qriEffectiveVoiceGains.value[0] ? 0);
                    if(a[35] == 1 and: { ~qntCanSound.value } and: { gain > 0 }
                        and: { now - ~qntLastEventAt >= 0.5 } and: { ~qntNodes.size < 4 }, {
                        ~qntLastEventAt = now;
                        ~qntLastAdmittedPacket = a.copy; ~qntAdmittedCount = ~qntAdmittedCount + 1;
                        // Sender uses the routed interval (a[101]) with no catchup.
                        // The 0.5s receipt guard and four voices only bound resource
                        // use; SC never recalculates or substitutes a rhythm source.
                        // One server bundle contains node creation and every
                        // array, so no partially populated body can ring.
                        s.bind({
                            node = Synth.tail(~qntVoiceGroup,\qntEventV2,[
                                \outBus,~qntPrivateBus.index,\noteHz,a[20],\excitationAmplitude,a[100],
                                \excitationMode,a[9],\duration,a[22],
                                \frequencies,rows.collect { |r| r[0] },
                                \gains,rows.collect { |r| r[1] },\tau,rows.collect { |r| r[2] }]).register;
                            ~qntNodes.add(node);
                        });
                    });
                }, {
                    if(now - ~qntLastRejectAt >= 5, {
                        ~qntLastRejectAt = now;
                        ("QMW NOTE/TIMBRE rejected frame: " ++ (~qntRejectReason ? "non-loopback sender")).warn;
                    });
                });
            }, "/qmw/note_timbre/v2/frame", recvPort:17930);

            ~qntWindow = Window("QMW NOTE / BODY — ROUTED ANALYSIS",Rect(580,150,620,530)).front;
            StaticText(~qntWindow,Rect(15,12,590,38)).string_(
                "Native H/rho → declared Analysis routes + independent abstract body\nSIMPLE gain/mute and SOUND LOCKED remain the audio owners.");
            ~qntArmButton = Button(~qntWindow,Rect(15,60,280,30))
                .states_([["DISARMED",Color.white,Color.red(0.5)],["ARM NEW LAYER",Color.black,Color.green]])
                .action_({ |v| ~qntArmed = v.value==1; if(~qntArmed.not,{~qntVoiceGroup.freeAll;~qntNodes.clear}) });
            ~qntSoloButton = Button(~qntWindow,Rect(310,60,290,30))
                .states_([["NORMAL: EXISTING + NEW"],["SOLO OUTPUT 1–2",Color.black,Color.yellow]])
                .action_({ |v| ~qntSolo = v.value==1 });
            ~qntHoldButton = Button(~qntWindow,Rect(15,102,280,28))
                .states_([["FOLLOW LIVE SNAPSHOTS"],["HOLD SNAPSHOT (OBSERVER)"]])
                .toolTip_("HOLD freezes this layer's input. Source controls keep acting on the source; select FOLLOW to hear their results here.")
                .action_({ |v| ~qntHold = v.value==1; ~qntSendConfig.value });
            Button(~qntWindow,Rect(310,102,290,28)).states_([["RECONNECT NEW SOURCE SESSION"]])
                .action_({ ~qntReconnect.value });
            ~qntBodyMenu = PopUpMenu(~qntWindow,Rect(15,145,190,27)).items_(["Identity Hilbert modes","Fourier Hilbert modes"])
                .action_({ |v| ~qntBasis=v.value;~qntSendConfig.value });
            ~qntExcitationMenu = PopUpMenu(~qntWindow,Rect(215,145,190,27)).items_(["Broad strike / 1 ms","Pitched note / 250 ms"])
                .action_({ |v| ~qntExcitation=v.value;~qntSendConfig.value });
            ~qntOctaveMenu = PopUpMenu(~qntWindow,Rect(415,145,185,27)).items_(["Note octave: base","Note octave: +1"])
                .action_({ |v| ~qntOctave=v.value;~qntSendConfig.value });
            StaticText(~qntWindow,Rect(15,184,280,16)).string_("Amplitude source — fixed unit reference");
            StaticText(~qntWindow,Rect(310,184,290,16)).string_("Rhythm source — bounded musical seconds");
            ~qntAmplitudeMenu = PopUpMenu(~qntWindow,Rect(15,203,280,26))
                .items_(["|A|", "|A| × sqrt(population)", "Diagnostic activity: population × |A|²"])
                .value_(~qntAmplitudeSource)
                .action_({ |v| ~qntAmplitudeSource=v.value;~qntSendConfig.value });
            ~qntRhythmMenu = PopUpMenu(~qntWindow,Rect(310,203,290,26))
                .items_(["Absolute energy gap", "Absolute transition order"])
                .toolTip_("Energy gap responds to level spacing. Order responds to endpoint separation. Older VNF and membrane clocks control separate layers.")
                .value_(~qntRhythmSource)
                .action_({ |v| ~qntRhythmSource=v.value;~qntSendConfig.value });
            ~qntQuantizationMenu = PopUpMenu(~qntWindow,Rect(15,237,280,26))
                .items_(["Rhythm: continuous", "Rhythm: ratio lattice"])
                .action_({ |v| ~qntQuantization=v.value;~qntSendConfig.value });
            ~qntAnalysisMenu = PopUpMenu(~qntWindow,Rect(310,237,290,26))
                .items_(["Analysis: computational", "Analysis: Hamiltonian", "Analysis: QHO", "Analysis: QFT"])
                .toolTip_("Observer representation only. Neither state evolution nor the independent body basis changes.")
                .action_({ |v| ~qntAnalysisBasis=v.value;~qntSendConfig.value });
            EZSlider(~qntWindow,Rect(15,276,585,26),"adapter level",ControlSpec(0,2,\lin),
                { |v| ~qntLevel=v.value },1,labelWidth:110);
            ~qntReadout = StaticText(~qntWindow,Rect(15,310,585,52)).string_(~qntSourceLabel);
            ~qntAnalysisReadout = StaticText(~qntWindow,Rect(15,364,585,38)).string_(~qntRouteLabel);
            ~qntRoutingReadout = StaticText(~qntWindow,Rect(15,406,585,52)).string_(
                "ANALYSIS: one declared primary source per audible destination.\nSOLO masks old output and FX tails; close restores original output.");
            ~qntHamiltonianButton = Button(~qntWindow,Rect(15,480,585,28))
                .states_([["FOUR-QUBIT H — stage sliders, then COMMIT"]])
                .toolTip_("Opens the current four-qubit source controls. FOLLOW observes the result; HOLD preserves this audition input.")
                .action_({
                    if(~qriOpenHamiltonianControls.notNil, { ~qriOpenHamiltonianControls.value },
                        { ~qntSourceLabel="Four-qubit source controls are unavailable in this session" });
                });
            ~qntWindow.onClose_({ ~qntWindow=nil;~qntRemove.value });
            AppClock.sched(0.02, {
                var gate;
                if(~qntGeneration === generation and: { ~qntInstalled }, {
                    gate=if(~qntCanSound.value, {
                        (~qrmMaster ? 0).clip(0,0.9) * (~qriMix ? 0).clip(0,1) * (~qriEventGain ? 0).clip(0,2)
                    }, { 0 });
                    if(~qntAppliedRevision < ~qntConfigRevision and: {
                        Main.elapsedTime - ~qntLastConfigSentAt >= 0.5
                    }, { ~qntTransmitConfig.value });
                    ~qntGateBus.setn([gate,~qntSolo.asInteger,~qntLevel]);
                    ~qntRouterGroup.moveToTail(~qntRoot);
                    ~qntRoutingReadout.string_(
                        if(~qntSolo, { "SOLO: existing mix and VST return excluded. Select NORMAL for FX." },
                            { "NORMAL: existing mix and VST return included." })
                        ++ "\nVST Rack return: " ++ (~qriVSTRackReturn ? 0).round(0.001).asString
                        ++ if((~qriVSTRackReturn ? 0)<=0, { " — raise Rack return in VST FX RACK to hear it." }, { "" })
                        ++ "\nNOTE / BODY is a private dry layer. Closing restores the existing output."
                    );
                    ~qntAnalysisReadout.string_(~qntRouteLabel);
                    ~qntReadout.string_(~qntSourceLabel
                        ++ if(~qntAppliedRevision < ~qntConfigRevision,
                            { "\nAPPLYING ROUTES — output gated until cfg=" ++ ~qntConfigRevision }, { "" }) ++ if(Main.elapsedTime-~qntLastValidAt>1.5,
                        { "\nSOURCE STALE — private output gated" }, { "" }));
                    0.02
                }, { nil });
            });
            "QMW_NOTE_TIMBRE_SC_V2_READY: routed ANALYSIS, disarmed, SIMPLE lane 0, private dry bus, complete UDP 17930.".postln;
        });
    });
};
// The opt-in bootstrap calls this only after the existing V3 server/mixer boot.
Routine({ install.value }).play(AppClock);
)
