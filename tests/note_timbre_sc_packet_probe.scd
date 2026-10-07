/* Evaluate in the existing language session after loading the adapter.
   No sockets, synths, mixer changes or accepted-revision commits. */
(
var a, previousReason = ~qntRejectReason, failures = 0, check;
check = { |condition,label|
    if(condition, { ("QNT_PACKET_PASS " ++ label).postln }, {
        failures=failures+1;
        ("QNT_PACKET_FAIL " ++ label ++ " reason=" ++ ~qntRejectReason).warn;
    });
};
a = [1,(~qntSession ? "probe-session").asSymbol,~qntSequence+100,
    ~qntObservedRevision+100,~qntObservedRevision+100,0.02,0.02,
    ~qntAppliedRevision.max(0),0,0,0,0,\IIIZ,0,
    "runtime.ClosedFourQubitSource".asSymbol,
    "four_qubit_computational:q0-lsb".asSymbol,
    String.fill(64,$a).asSymbol,"-".asSymbol,-1,-1,
    0.0,0.0,0.0,0.0,0.0,0.0,0,1.0,0.0,1.0,1.0,
    \model_energy,16,\dimensionless,Main.elapsedTime,0]
    ++ Array.fill(16,{[220.0,0.25,0.18,0.0]}).flat;
check.(~qntValidatePacket.(a.copy),"OSC Symbol text accepted");
check.(a[1].isKindOf(Symbol),"caller packet remains unchanged when validating its copy");
a[1]=123;
check.(~qntValidatePacket.(a.copy).not,"numeric session is rejected");
a[1]=(~qntSession ? "probe-session").asSymbol;
a[33]=42;
check.(~qntValidatePacket.(a.copy).not,"numeric units are rejected");
a[33]=\dimensionless;
check.(~qntValidatePacket.(a.copyRange(0,98)).not,"incomplete packet is rejected");
a[2]=~qntSequence;
check.(~qntValidatePacket.(a.copy).not,"replayed sequence is rejected");
~qntRejectReason=previousReason;
~qntPacketProbeFailures=failures;
("QNT_PACKET_PROBE failures=" ++ failures).postln;
)
