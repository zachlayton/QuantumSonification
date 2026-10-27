/* Run via run_lifecycle_check.py: language/OSC integration with a protocol stub.
   Tests real addon routines, scheduling, arguments and cleanup; DSP is separately
   tested by RenderCheck. No audio device or third-party UGens required. */
(
var here=thisProcess.nowExecutingPath.dirname, check, synths=List.new, frees=List.new;
var onSynth, onFree, onBus, busUpdates=List.new;
check={ |ok, why| if(ok.not, { ("FAIL: " ++ why).postln; 1.exit }) };
~qefHeadless=true;
s=Server(\qefLifecycle,NetAddr("127.0.0.1", "QMW_TEST_PORT".getenv.asInteger)); Server.default=s;
s.statusWatcher.notified=true; s.statusWatcher.serverRunning=true;
onSynth=OSCFunc({ |msg| synths.add(msg) },'/s_new');
onFree=OSCFunc({ |msg| frees.add(msg) },'/n_free');
onBus=OSCFunc({ |msg| busUpdates.add(msg) },'/c_setn');
thisProcess.interpreter.executeFile(here +/+ "../supercollider/EventFieldAddon.scd");
~qmwQFTV3SourceGroup=Group.head(s);
~qmwQFTV3SourceBus=Bus.audio(s,2); ~qmwQFTV42BFXSendBus=Bus.audio(s,2);
~qefBusPairs.do { |pair| currentEnvironment[pair[1]]=Bus.control(s,1) };
~qmwQFTV3AudioReady=true; ~qmwQFTV3SoundEnabled=1;
Routine({
    var count, tau, wavelets, oldGroup, oldObs, oldMapping, updates;
    ~qefStart.(); 1.5.wait;
    check.(~qefRunning, "start finishes sync"); check.(~qefCount > 0, "flow emits events");
    wavelets=synths.select { |msg| msg[1] == \qefWaveletV1 };
    check.(wavelets.size > 0, "wavelet OSC delivered");
    check.(wavelets.every { |msg| msg.includes(\weightsA) and: { msg.includes(\weightsB) } }, "both spectral endpoints sent");
    check.(wavelets.every { |msg| msg.includes(\obsBus) and: { msg.includes(\mappingBus) }
        and: { msg.includes(\pairIndex) } and: { msg.includes(\pairDirection) } }, "observable routing per voice");
    updates=busUpdates.select { |msg| msg[1]==~qefObsBus.index };
    check.(updates.size>20 and: { updates.every { |msg| msg[2]==16 } }, "live 16-channel observables");
    check.(~qefMappingValues.() == [0,0,0,0], "new mappings default off");
    check.(~qefRecentFrames.size<=64, "bounded headless display queue");
    ~qefSet.(\coherenceDepth,0.65); ~qefSet.(\phaseDepth,1);
    ~qefSet.(\diracDepth,1); ~qefSet.(\diracIndex,2.4); 0.03.wait;
    updates=busUpdates.select { |msg| msg[1]==~qefMappingBus.index };
    check.((updates.last.copyRange(3,6)-[0.65,1,1,2]).abs.maxItem < 1e-6, "live shared mapping controls");
    ~qefSet.(\quantum,0.04); check.(~qefResidual.sum == 0, "sensitivity resets residual");
    ~qefSet.(\gain,100); check.(~qefSettings[\gain] == 0.3, "control clamp");
    ~qefSet.(\gain,inf); check.(~qefSettings[\gain] == 0.3, "nonfinite rejected");
    ~qmwQFTV3SoundEnabled=0; 0.05.wait; count=~qefCount; tau=~qefTau;
    0.15.wait; check.(~qefCount == count, "Sound off stops events");
    check.(~qefTau == tau, "Sound off pauses theory transport");
    ~qmwQFTV3SoundEnabled=1;
    ~qefExpiries=List.newFrom((Main.elapsedTime+10)!96); 0.4.wait;
    check.(~qefDropped > 0, "voice limit reports dropped events");
    check.(~qefExpiries.size == 96, "voice limit bounded");
    oldGroup=~qefGroup.nodeID; oldObs=~qefObsBus; oldMapping=~qefMappingBus;
    ~qefStop.(); 0.3.wait;
    check.(~qefRunning.not and: { ~qefRunner.isNil }, "stop clears transport");
    check.(frees.any { |msg| msg.includes(oldGroup) }, "delayed node cleanup");
    check.(oldObs.index.isNil and: { oldMapping.index.isNil }, "owned observable buses freed");
    ~qefStart.(); 0.4.wait; check.(~qefRunning, "restart");
    ~qmwQFTV3SourceGroup=Group.head(s); 0.1.wait;
    check.(~qefRunning.not, "host rebuild stops field");
    ~qefStart.(); 0.4.wait; check.(~qefRunning, "attach rebuilt host");
    s.statusWatcher.serverRunning=false; 0.1.wait;
    check.(~qefRunning.not and: { ~qefAudio.isNil }, "server quit clears owned resources");
    check.(~qefObsBus.isNil and: { ~qefMappingBus.isNil }, "server quit invalidates observable buses");
    ~qefShutdown.(); onSynth.free; onFree.free; onBus.free;
    "LIFECYCLE PASS: start, event/observable OSC, live mappings, mute, controls, voice cap, cleanup, restart, rebuild, quit".postln;
    0.exit;
}).play(AppClock);
SystemClock.sched(12, { "FAIL: lifecycle timeout".postln; 1.exit });
)
