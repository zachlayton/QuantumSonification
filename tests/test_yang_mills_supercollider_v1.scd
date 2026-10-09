// Run with: sclang -D tests/test_yang_mills_supercollider_v1.scd
(
var root = thisProcess.nowExecutingPath.dirname.dirname;
var check = { |condition, message| if(condition.not) { Error(message).throw } };
var near = { |a, b, tolerance = 1e-10| (a - b).abs.maxItem < tolerance };
var magnitude = Array.fill(16, { |i| (i + 1) / 40 });
var speed = Array.fill(16, { |i| i / 20 });
var emitCount = 0;
var send;
var definition;
try {
    thisProcess.interpreter.executeFile(root +/+ "supercollider/qmw_yang_mills_support_v1.scd");
    check.(thisProcess.interpreter.compileFile(root +/+ "supercollider/qmw_yang_mills_modal_v1.scd").notNil,
        "live receiver and GUI compile");
    thisProcess.interpreter.executeFile(root +/+ "supercollider/qmw_yang_mills_synth_v1.scd");
    definition = ~qmwYMBuildSynthDef.();
    check.(definition.asBytes.size > 1000, "native modal DSP compiles");
    check.(~qmwYMValidRevision.(2147483647), "maximum OSC int32 revision is accepted");
    ~qmwYMEmit = { emitCount = emitCount + 1 };
    [0, 0.25, 0.5, 1].do { |amount|
        var result = ~qmwYMMap.(magnitude, speed, amount);
        check.((result[\power].sum - magnitude.squared.sum).abs < 1e-12, "power is conserved");
        check.(result[\magnitude].every { |v| v >= 0 }, "nonnegative magnitude");
        check.(result[\speed].every { |v| (v >= 0) and: { v <= 1 } }, "bounded motion");
        16.do { |source|
            check.(((result[\weights].collect { |row| row[source] }).sum - 1).abs < 1e-12,
                "every source distributes exactly one unit of power");
        };
    };
    check.(near.(~qmwYMMap.(magnitude, speed, 0)[\magnitude], magnitude), "zero warp is identity");
    check.(near.(~qmwYMMap.(magnitude, speed, 0)[\speed], speed), "zero warp preserves speed");
    check.(near.(~qmwYMMap.(magnitude, speed, 0.5)[\magnitude],
        ~qmwYMMap.(magnitude, speed, 0.500001)[\magnitude], 1e-5), "amount is continuous");
    check.(near.(~qmwYMMap.(magnitude, speed, 1)[\magnitude], magnitude).not, "full warp changes participation");
    check.(~qmwYMMap.(0 ! 16, speed, 1)[\magnitude].sum == 0, "warp cannot excite vacuum");
    check.((~qmwYMMap.(1 ! 16, speed, 1)[\power].sum - 16).abs < 1e-12,
        "concentrated lanes preserve power even when an amplitude exceeds one");
    send = { |revision, time = 10|
        ~qmwYMReceive.(\begin, ["/begin", revision, 0.1, 16], time);
        ~qmwYMReceive.(\magnitude, ["/magnitude", revision] ++ magnitude, time);
        ~qmwYMReceive.(\speed, ["/speed", revision] ++ speed, time);
        ~qmwYMReceive.(\diagnostics, ["/diagnostics", revision, 4, 1e-5, 1e-15, 1e-15, 1e-15], time);
        ~qmwYMReceive.(\end, ["/end", revision], time);
    };
    send.(1);
    check.(~qmwYMFrames == 1, "complete frame commits");
    check.(emitCount == 1, "one atomic synth update");
    send.(1);
    check.(~qmwYMFrames == 1, "stale frame rejected");
    ~qmwYMReceive.(\begin, ["/begin", 2, 0.2, 16], 10.1);
    ~qmwYMReceive.(\magnitude, ["/magnitude", 2] ++ magnitude, 10.1);
    ~qmwYMReceive.(\end, ["/end", 2], 10.1);
    check.(~qmwYMFrames == 1, "incomplete frame rejected");
    ~qmwYMReceive.(\begin, ["/begin", 3, 0.3, 16], 10.2);
    ~qmwYMReceive.(\begin, ["/begin", 2, 0.2, 16], 10.2);
    check.(~qmwYMPending[\revision] == 3, "older begin cannot replace pending revision");
    ~qmwYMReceive.(\magnitude, ["/magnitude", 3] ++ ([-1] ++ magnitude.copyRange(1, 15)), 10.2);
    ~qmwYMReceive.(\speed, ["/speed", 3] ++ speed, 10.2);
    ~qmwYMReceive.(\diagnostics, ["/diagnostics", 3, 4, 0, 0, 0, 0], 10.2);
    ~qmwYMReceive.(\end, ["/end", 3], 10.2);
    check.(~qmwYMFrames == 1, "invalid vector rejected");
    ~qmwYMWatchdogCheck.(10.8);
    check.(~qmwYMRawMagnitude.sum == 0, "timeout clears source excitation");
    check.(~qmwYMMap.(~qmwYMRawMagnitude, ~qmwYMRawSpeed, 1)[\power].sum == 0,
        "changing warp after timeout cannot restore stale energy");
    ~qmwYMReset.();
    send.(0, 11);
    check.(~qmwYMCommitted == 0, "reset permits sender restart");
    "PASS: SuperCollider power conservation, identity, continuity, atomic frames, watchdog and reset".postln;
    0.exit;
} { |error|
    error.reportError;
    1.exit;
};
)
