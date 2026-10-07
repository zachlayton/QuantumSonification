/* Bounded acceptance of the actual launched source, production receiver and DSP.
   Does not create a quantum source, edit its state, or terminate any process.
   Audition replays and routing marker are labeled separately from live cadence. */
(
var output="QMW_ROUTED_ACCEPTANCE_DIR".getenv;
var restartRequest="QMW_ROUTED_RESTART_REQUEST".getenv;
var started=Main.elapsedTime, saved, log, packetLog, status, recordPacket, waitUntil;
var configure, setBaseline, restore, capture, replay, freshNote, check, failures=0;
var recordNode=nil, recordBuffer=nil, marker=nil, rehearsal=nil, failed=false;
var savedConfig, baselinePacket, before, firstSession, currentConfig;
var productionReconnect, plannedReconnect=false, lockPanel, sourceRestartVerified=false;
if(output.isNil, { Error("QMW_ROUTED_ACCEPTANCE_DIR required").throw });
File.mkdir(output);
log=File(output +/+ "events.tsv","w");
packetLog=File(output +/+ "accepted_packets.jsonl","w");
status={ |name,details=""|
    var line=Main.elapsedTime.round(0.001).asString ++ "\t" ++ name ++ "\t" ++ details.asString;
    log.write(line ++ "\n");log.flush;
    File.use(output +/+ "status.txt","w", { |f| f.write(line ++ "\n") });
    ("QNT_ACCEPTANCE " ++ line).postln;
    if(Main.elapsedTime-started>260 and: { ["FAILED","COMPLETE"].includes(name).not }, { Error("Acceptance exceeded260seconds").throw });
};
recordPacket={ |name|
    if(~qntLastAcceptedPacket.notNil, {
        packetLog.write([name,Main.elapsedTime,~qntAcceptedCount,~qntAdmittedCount,
            ~qntLastAcceptedPacket].asCompileString ++ "\n");packetLog.flush;
    });
};
waitUntil={ |condition,seconds=12,label="condition"|
    var until=Main.elapsedTime+seconds;
    while({ condition.value.not and: { Main.elapsedTime<until } }, { 0.05.wait });
    if(condition.value.not, { Error("Timeout: " ++ label).throw });
};
check={ |condition,name|
    if(condition, { status.("PASS",name) }, { failures=failures+1;status.("FAIL",name) });
};
lockPanel={
    ~qntWindow !? { |window|
        window.name_("QMW NOTE / BODY — AUTOMATED CHECK; controls temporarily locked");
        window.view.children.do { |view|
            if(view.isKindOf(Button) or: { view.isKindOf(PopUpMenu) }, { view.enabled_(false) });
        };
    };
};
productionReconnect=~qntReconnect;
~qntReconnect={
    status.("RECONNECT_CALL",if(plannedReconnect,{"planned acceptance restart"},{"external control action"}));
    productionReconnect.value;
};
saved=(master:~qrmMaster,mix:~qriMix,eventGain:~qriEventGain,
    gains:~qriVoiceGains.copy,mutes:~qriVoiceMutes.copy,bodyMode:~qriBodyMode,
    enabled:~qriEnabled,sonify:~qrmSonify,level:~qntLevel,rackReturn:~qriVSTRackReturn);
savedConfig=[~qntBasis,~qntExcitation,~qntOctave,~qntHold.asInteger,
    ~qntAmplitudeSource,~qntRhythmSource,~qntQuantization,~qntAnalysisBasis];
currentConfig=savedConfig.copy;
configure={ |name,values|
    var revision;
    status.("CONFIGURE",name ++ " " ++ values.asCompileString);
    ~qntBasis=values[0];~qntExcitation=values[1];~qntOctave=values[2];~qntHold=values[3]==1;
    ~qntAmplitudeSource=values[4];~qntRhythmSource=values[5];~qntQuantization=values[6];~qntAnalysisBasis=values[7];
    [~qntBodyMenu,~qntExcitationMenu,~qntOctaveMenu,~qntHoldButton,
        ~qntAmplitudeMenu,~qntRhythmMenu,~qntQuantizationMenu,~qntAnalysisMenu].do { |view,i| view !? { view.value_(values[i]) } };
    ~qntSendConfig.value;revision=~qntConfigRevision;
    waitUntil.({ ~qntLastAcceptedPacket.notNil and: {
        ~qntLastAcceptedPacket[7]==revision and: {
            [11,9,10,8,102,103,104,105].collect { |i| ~qntLastAcceptedPacket[i] } == values
        }
    } },12,"exact atomic configuration acknowledgement");
    currentConfig=values.copy;
    recordPacket.(name ++ "_ack");
};
setBaseline={
    ~qrmMaster=0.18;~qriMix=0.55;~qriEventGain=0.75;
    ~qriVoiceGains=[1.0,0,0,0,0,0,0,0];~qriVoiceMutes=Array.fill(8,0);~qriPushVoiceGains.value;
    ~qriBodyMode=0;~qriSetPluckAudioEnabled.value(true);
    ~qntLevel=1.0;~qntArmButton.valueAction_(1);~qntSoloButton.valueAction_(1);
};
restore={
    ~qntReconnect=productionReconnect;
    ~qntWindow !? { |window|
        window.name_("QMW NOTE / BODY — ROUTED ANALYSIS");
        window.view.children.do { |view|
            if(view.isKindOf(Button) or: { view.isKindOf(PopUpMenu) }, { view.enabled_(true) });
        };
    };
    OSCdef(\qntCompleteFrame) !? _.enable;
    recordNode !? _.free;recordNode=nil;
    recordBuffer !? { |buffer| buffer.close;buffer.free };recordBuffer=nil;
    marker !? _.free;marker=nil;rehearsal=nil;
    ~qntVoiceGroup !? _.freeAll;
    ~qrmMaster=saved[\master];~qriMix=saved[\mix];~qriEventGain=saved[\eventGain];
    ~qriVoiceGains=saved[\gains].copy;~qriVoiceMutes=saved[\mutes].copy;~qriPushVoiceGains.value;
    ~qriBodyMode=saved[\bodyMode];~qntLevel=saved[\level];
    ~qntArmButton !? { |button| button.valueAction_(0) };
    ~qntSoloButton !? { |button| button.valueAction_(0) };
    // End explicitly safe and visible, regardless of startup arm state.
    ~qriSetPluckAudioEnabled.value(false);
};
capture={ |name,seconds=1.2,expectSilent=false|
    var path=output +/+ (name ++ ".wav"), file, samples, peak, rms;
    status.("CAPTURE",name);recordPacket.(name ++ "_start");
    recordBuffer=Buffer.alloc(s,65536,2);s.sync;
    recordBuffer.write(path,"wav","float",0,0,true);s.sync;
    // After the selector inside its group. Root-tail moves preserve this order.
    recordNode=Synth.after(~qntRouter,\qntAcceptanceRecordV2,[\buf,recordBuffer.bufnum]);s.sync;
    seconds.wait;recordNode.free;recordNode=nil;s.sync;
    recordBuffer.close;s.sync;recordBuffer.free;recordBuffer=nil;s.sync;
    file=SoundFile.openRead(path);
    if(file.isNil, { Error("Cannot read actual recorded output " ++ path).throw });
    samples=FloatArray.newClear(file.numFrames*file.numChannels);file.readData(samples);file.close;
    peak=samples.abs.maxItem ? 0;rms=(samples.squared.sum/samples.size.max(1)).sqrt;
    status.("CAPTURE_RESULT",[name,peak,rms,samples.size].asCompileString);
    if(expectSilent, { check.(peak==0,name ++ " exact digital silence") });
    recordPacket.(name ++ "_end");
    peak
};
replay={ |a,label|
    var rows=a.copyRange(36,99).clump(4);
    status.("AUDITION_REPLAY",label ++ " actual event=" ++ a[17] ++ " audit=" ++ a[16]);
    // A received production note is scheduled at server latency. Let that
    // exact pending bundle land before clearing the owned group for replay.
    ((s.latency ? 0.2) + 0.1).wait;
    rehearsal=nil;
    ~qntVoiceGroup.freeAll;~qntNodes.clear;s.sync;
    // Explicit acoustic replay of an actual previously admitted packet. This
    // does not create, publish or masquerade as a new source/measurement event.
    s.bind({ rehearsal=Synth.tail(~qntVoiceGroup,\qntEventV2,[
        \outBus,~qntPrivateBus.index,\noteHz,a[20],\excitationAmplitude,a[100],
        \excitationMode,a[9],\duration,a[22],\frequencies,rows.collect(_[0]),
        \gains,rows.collect(_[1]),\tau,rows.collect(_[2])]) });
};
freshNote={ |name|
    var count=~qntAdmittedCount;
    waitUntil.({ ~qntAdmittedCount>count },11,"actual admitted source note: " ++ name);
    recordPacket.(name ++ "_actual_admitted");
    ~qntLastAdmittedPacket.copy
};
Routine({
    {
        status.("BEGIN","actual native source; private stereo adapter; bounded260seconds");
        waitUntil.({ ~qntInstalled and: { ~qntLastAcceptedPacket.notNil } },12,"installed native receiver");
        status.("CONTROL_OWNERSHIP","inactive VNF input and native four-qubit navigation");
        ~qfrOpenGeneratorControls.value;0.15.wait;
        check.(~qfrVnfAvailable.not,"VNF source absent is explicit");
        check.(~qfrVnfControls.size==6 and: { ~qfrVnfControls.every { |control| control.enabled.not } },
            "all six real VNF controls disabled without source");
        check.(~qfrVnfSourceLabel.string=="No live VNF input — controls inactive",
            "VNF panel explains inactive input");
        ~qfrVnfHamiltonianButton.doAction;0.1.wait;
        check.(~qriHamiltonianWindow.notNil,"inactive VNF panel opens current four-qubit H controls");
        ~qriHamiltonianWindow !? _.close;~qfrGeneratorWindow !? _.close;
        ~qntHamiltonianButton.doAction;0.1.wait;
        check.(~qriHamiltonianWindow.notNil,"routed panel opens current four-qubit H controls");
        ~qriHamiltonianWindow !? _.close;
        firstSession=~qntSession;lockPanel.();
        configure.("hold_native",[0,0,0,1,0,0,0,0]);setBaseline.();
        SynthDef(\qntAcceptanceRecordV2, { |buf=0| DiskOut.ar(buf,In.ar(0,2)) }).add;
        SynthDef(\qntAcceptanceRoutingMarkerV2, { Out.ar(0,SinOsc.ar(997)*0.001 ! 2) }).add;
        s.sync;
        baselinePacket=freshNote.("baseline");
        replay.(baselinePacket,"baseline amplitude reference");
        check.(capture.("audition_replay_baseline",1.2,false)>1e-8,"actual routed note renders nonzero audio");

        // Natural cadence recording, no synthetic event packets or replay.
        ((s.latency ? 0.2) + 0.1).wait;
        ~qntVoiceGroup.freeAll;~qntNodes.clear;rehearsal=nil;s.sync;0.1.wait;
        status.("NATURAL_CADENCE","real live admitted source notes only; prior replay cleared");
        capture.("natural_energy_gap_cadence",10,false);
        configure.("order_lattice",[0,0,0,1,1,1,1,0]);
        capture.("natural_order_lattice_cadence",10,false);
        configure.("amplitude_activity",[0,0,0,1,2,0,0,0]);
        baselinePacket=freshNote.("activity");
        replay.(baselinePacket,"activity selected by actual router");capture.("activity_replay",1.2,false);
        configure.("body_fourier",[1,0,0,1,0,0,0,0]);
        baselinePacket=freshNote.("fourier");
        replay.(baselinePacket,"actual Fourier body");capture.("fourier_body_replay",1.2,false);
        configure.("pitched_base",[1,1,0,1,0,0,0,0]);
        baselinePacket=freshNote.("pitched_base");
        replay.(baselinePacket,"actual pitched base");capture.("pitched_base_replay",1.2,false);
        configure.("pitched_octave",[1,1,1,1,0,0,0,0]);
        baselinePacket=freshNote.("pitched_octave");
        replay.(baselinePacket,"actual pitched octave");capture.("pitched_octave_replay",1.2,false);
        [1,2,3,0].do { |basis|
            var values=currentConfig.copy;values[7]=basis;
            configure.("analysis_basis_" ++ basis,values);
        };

        configure.("gate_test_reference",[0,0,0,1,0,0,0,0]);
        baselinePacket=freshNote.("gate_reference");
        [
            ["simple_zero",{~qriVoiceGains[0]=0;~qriPushVoiceGains.value}],
            ["simple_mute",{~qriVoiceMutes[0]=1;~qriPushVoiceGains.value}],
            ["all_voices_zero",{~qriVoiceGains=Array.fill(8,0);~qriPushVoiceGains.value}],
            ["sound_locked",{~qrmSonify=false;~qrmSoundButton !? { |b| b.value_(0) };~qrmApplyAudioGate !? _.value}],
            ["qri_disabled",{~qriEnabled=false}],
            ["plucks_disabled",{~qriBodyMode=1}],
            ["master_zero",{~qrmMaster=0}],
            ["mix_zero",{~qriMix=0}],
            ["event_gain_zero",{~qriEventGain=0}],
            ["adapter_level_zero",{~qntLevel=0}],
            ["disarmed",{~qntArmButton.valueAction_(0)}]
        ].do { |test|
            setBaseline.();test[1].value;0.15.wait;
            replay.(baselinePacket,"gate " ++ test[0]);
            capture.("gate_" ++ test[0],1.0,true);
        };

        setBaseline.();0.2.wait;
        status.("TRANSPORT_OUTAGE","disable only owned frame receiver; actual authority continues");
        OSCdef(\qntCompleteFrame).disable;2.0.wait;
        check.(~qntCanSound.value.not,"source timeout gates private return");
        replay.(baselinePacket,"stale actual-packet replay");capture.("gate_source_stale",1.0,true);
        before=~qntAcceptedCount;OSCdef(\qntCompleteFrame).enable;
        waitUntil.({ ~qntAcceptedCount>before and: { ~qntCanSound.value } },12,"real transport resumes");
        check.(~qntSession==firstSession,"same actual source recovered after packet outage");

        status.("CONFIG_RETRY","drop first config by disabling transmission until retry");
        // Suppress exactly one owned send, then restore the same sender before
        // yielding. No packets are sent to an unknown local application.
        before=~qntTransmitConfig;~qntTransmitConfig={ };
        ~qntSendConfig.value;~qntTransmitConfig=before;
        check.(~qntCanSound.value.not,"unacknowledged configuration gates output");
        waitUntil.({ ~qntAppliedRevision==~qntConfigRevision },12,"same-revision automatic retry");
        recordPacket.("config_retry_recovered");

        status.("NORMAL_SOLO","owned997Hz routing marker; no VST-processing claim");
        ~qntArmButton.valueAction_(0);~qntSoloButton.valueAction_(0);1.8.wait;
        marker=Synth.before(~qntRouter,\qntAcceptanceRoutingMarkerV2);s.sync;
        check.(capture.("normal_owned_marker",1.0,false)>0.0001,"NORMAL passes preceding output");
        ~qntSoloButton.valueAction_(1);0.15.wait;capture.("solo_disarmed_masks_old_output",1.0,true);
        ~qntSoloButton.valueAction_(0);0.15.wait;
        check.(capture.("normal_restores_owned_marker",1.0,false)>0.0001,"NORMAL restores preceding output");
        marker.free;marker=nil;s.sync;
        check.(~qriVSTRackReturn==saved[\rackReturn],"rack return owner unchanged");

        status.("WORKSPACE","invoke existing navigation action, close addon, reopen disarmed");
        if(~qmwuWorkspaceButton.isNil, { Error("WORKSPACE button unavailable").throw });
        ~qmwuWorkspaceButton.doAction;0.2.wait;
        check.(~qntWorkspaceEntry.notNil,"WORKSPACE contains NOTE / BODY recovery");
        before=~qntWindow;~qntWorkspaceEntry.doAction;
        check.(~qntWindow===before,"reopening present panel brings same window forward");
        ~qntWindow.close;0.3.wait;
        check.(~qntInstalled.not and: { ~qntWindow.isNil },"close removes only owned addon");
        ~qntWorkspaceEntry.doAction;
        waitUntil.({ ~qntInstalled and: { ~qntWindow.notNil and: { ~qntLastAcceptedPacket.notNil } } },12,"WORKSPACE recreates actual-source addon");
        check.(~qntArmed.not and: { ~qntWindow !== before },"recovery creates fresh DISARMED panel");
        lockPanel.();
        configure.("restored_visible_controls",savedConfig);
        recordPacket.("workspace_recovered");

        status.("RECONNECT","retire actual old session; root must restart owned source for new-session acceptance");
        firstSession=~qntSession;plannedReconnect=true;~qntReconnect.value;plannedReconnect=false;before=~qntAcceptedCount;
        2.0.wait;
        check.(~qntArmed.not and: { ~qntSession.isNil },"reconnect disarms and waits for new source session");
        check.(~qntRetired.includes(firstSession) and: { ~qntAcceptedCount==before },"retired actual source cannot commit further frames");
        status.("NEW_SESSION_RESTART_REQUIRED","request one restart of the actual owned native process");
        if(restartRequest.isNil, { Error("Actual source restart request path missing").throw });
        File.use(restartRequest,"w", { |f| f.write("restart owned actual native process once\n") });
        waitUntil.({ ~qntSession.notNil and: { ~qntSession != firstSession and: {
            ~qntAppliedRevision>=~qntConfigRevision
        } } },35,"new actual native source accepted with visible config acknowledged");
        check.(~qntArmed.not,"new actual source remains DISARMED");
        check.(~qntRetired.includes(firstSession),"prior actual session remains retired after restart");
        recordPacket.("new_actual_source_recovered");
        sourceRestartVerified=~qntArmed.not and: { ~qntRetired.includes(firstSession) };
        status.("NEW_SESSION_RECOVERED",~qntSession);
    }.try({ |error|
        failed=true;failures=failures+1;
        ("QNT_ACCEPTANCE_ERROR " ++ error.errorString).warn;
        log.write(Main.elapsedTime.asString ++ "\tERROR\t" ++ error.errorString ++ "\n");log.flush;
    });
    restore.();
    status.(if(failed or: { failures>0 },{"FAILED"},{"COMPLETE"}),
        "failures=" ++ failures ++ "; ended DISARMED, SOUND LOCKED, NORMAL; source restart verified=" ++ sourceRestartVerified);
    File.use(output +/+ "completion.txt","w", { |f| f.write("failures=" ++ failures ++ "\nnew_source_restart_required=" ++ sourceRestartVerified.not ++ "\n") });
    packetLog.close;log.close;
    "QNT_ACCEPTANCE_DONE".postln;
}).play(AppClock);
)
