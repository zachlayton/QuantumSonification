/* Wire-only validator tests: no state authority, sockets, mixer changes or commits. */
(
var a, b, previousReason = ~qntRejectReason, previousSession = ~qntSession, failures = 0, check;
check = { |condition,label|
    if(condition, { ("QNT_PACKET_PASS " ++ label).postln }, {
        failures=failures+1;
        ("QNT_PACKET_FAIL " ++ label ++ " reason=" ++ ~qntRejectReason).warn;
    });
};
a = [2,(~qntSession ? "probe-session").asSymbol,~qntSequence+100,
    ~qntObservedRevision+100,~qntObservedRevision+100,0.02,0.02,
    ~qntAppliedRevision.max(0),0,0,0,0,\IIIZ,0,
    "wire-fixture".asSymbol,"four_qubit_computational:q0-lsb".asSymbol,
    String.fill(64,$a).asSymbol,"fixture-note".asSymbol,0,1,
    247.5,0.25,0.001,1.0,1.0,0.0,0,1.0,0.0,1.0,1.0,
    \model_energy,16,\dimensionless,Main.elapsedTime,1]
    ++ Array.fill(16,{[220.0,0.25,0.18,0.0]}).flat
    ++ [0.5,2.0,1,1,0,0,0,String.fill(64,$b).asSymbol];
check.(~qntValidatePacket.(a.copy),"v2 note accepts independent raw activity and excitation amplitude");
check.(a[1].isKindOf(Symbol) and: { a[107].isKindOf(Symbol) },"caller packet text unchanged");
b=a.copy; b[100]=0;
check.(~qntValidatePacket.(b),"normalized zero amplitude is valid silence");
b=a.copy; b[21]=0;
check.(~qntValidatePacket.(b).not,"admitted raw activity retains its positive diagnostic meaning");
[0,1,2].do { |code| b=a.copy; b[102]=code; check.(~qntValidatePacket.(b),"amplitude source=" ++ code) };
[0,1].do { |code| b=a.copy; b[103]=code; check.(~qntValidatePacket.(b),"rhythm source=" ++ code) };
[0,1].do { |code| b=a.copy; b[104]=code; check.(~qntValidatePacket.(b),"quantization=" ++ code) };
[0,1,2,3].do { |code| b=a.copy; b[105]=code; check.(~qntValidatePacket.(b),"analysis representation=" ++ code) };
[[100,-0.01],[100,1.0000001],[100,1.01],[100,inf],[101,inf],[36,inf],[101,0.49],[101,8.01],[102,3],[103,2],[104,2],
 [105,4],[106,1],[102,0.5],[1,123],[107,42],[107,"broken"],[107,String.fill(64,$z)],[16,String.fill(64,$z)],
 [0,1],[2,~qntSequence],[7,-1]].do { |bad|
    b=a.copy;b[bad[0]]=bad[1];
    check.(~qntValidatePacket.(b).not,"invalid argument=" ++ bad[0] ++ " value=" ++ bad[1]);
};
b=a.copy;b[1]="other-source";
~qntSession=a[1].asString;
check.(~qntValidatePacket.(b).not,"foreign session rejected before explicit reconnect");
~qntSession=previousSession;
~qntRetired.add(a[1].asString);
check.(~qntValidatePacket.(a.copy).not,"retired source session rejected");
~qntRetired.remove(a[1].asString);
check.(~qntValidatePacket.(a.copyRange(0,106)).not,"truncated v2 rejected");
check.(~qntValidatePacket.(a ++ [0]).not,"extra argument rejected");
b=a.copy;b[0]=1;
check.(~qntValidatePacket.(b.copyRange(0,99)).not,"complete legacy v1 rejected");
b=a.copy;b[17]="-";b[18] = -1;b[19] = -1;b[20]=0;b[21]=0;b[22]=0;b[35]=0;b[100]=0;b[101]=0;
check.(~qntValidatePacket.(b.copy),"no-note heartbeat with complete body accepted");
b[100]=0.1;
check.(~qntValidatePacket.(b.copy).not,"no-note nonzero excitation rejected");
b[100]=0;b[101]=0.5;
check.(~qntValidatePacket.(b.copy).not,"no-note nonzero interval rejected");
~qntRejectReason=previousReason;
~qntPacketProbeFailures=failures;
("QNT_PACKET_PROBE failures=" ++ failures).postln;
)
