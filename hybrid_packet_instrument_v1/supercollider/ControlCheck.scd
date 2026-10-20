// Isolated language/OSC validation. Run in a fresh sclang with audio server stopped.
// Uses an unallocated Synth handle to inspect receiver validation without audio.
(
thisProcess.interpreter.executeFile(thisProcess.nowExecutingPath.dirname +/+ "HybridPacketAddon.scd");
~hybridWatch.stop;
Routine({
    var addr = NetAddr("127.0.0.1",17920);
    var frame = [1, 0.1, 1, 2, 1, 1] ++ (0.1 ! 16) ++ (0.2 ! 16);
    ~hybridLastSeq = -1; ~hybridLastFrame = -1e9;
    ~hybridNode = Synth.basicNew(\qmwHybridBodyV1,s,999999);
    addr.sendMsg('/qmw/hybrid/control/density', 12); 0.1.wait;
    if(~hybridState[\density] != 12, { Error("integer control fail").throw });
    addr.sendMsg('/qmw/hybrid/control/density', "bad"); 0.1.wait;
    if(~hybridState[\density] != 12, { Error("invalid control fail").throw });
    addr.sendMsg('/qmw/hybrid/projection', *frame); 0.1.wait;
    if(~hybridLastSeq != 1, { Error("valid frame fail").throw });
    frame[0] = 2; frame[8] = "bad";
    addr.sendMsg('/qmw/hybrid/projection', *frame); 0.1.wait;
    if(~hybridLastSeq != 1, { Error("invalid frame accepted").throw });
    frame[0] = 0; frame[8] = 0.1;
    addr.sendMsg('/qmw/hybrid/projection', *frame); 0.1.wait;
    if(~hybridLastSeq != 1, { Error("reorder accepted").throw });
    ~hybridLastFrame = Main.elapsedTime - 2;
    addr.sendMsg('/qmw/hybrid/projection', *frame); 0.1.wait;
    if(~hybridLastSeq != 0, { Error("restart frame rejected").throw });
    ~hybridNode = nil; ~hybridShutdown.();
    "OSC CONTROL/FRAME VALIDATION PASS".postln; 0.exit;
}).play(AppClock);
)
