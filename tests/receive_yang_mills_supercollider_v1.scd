// Headless real-UDP fixture for the Python integration test.
(
var root = thisProcess.nowExecutingPath.dirname.dirname;
var ready = "QMW_SC_READY_PATH".getenv;
thisProcess.interpreter.executeFile(root +/+ "supercollider/qmw_yang_mills_support_v1.scd");
[\begin, \magnitude, \speed, \diagnostics, \end].do { |kind|
    OSCdef(("qmwYMTest_" ++ kind).asSymbol, { |message|
        ~qmwYMReceive.(kind, message);
        if((kind == \end) and: { ~qmwYMFrames >= 3 }
            and: { ~qmwYMRawMagnitude.sum == 0 }) {
            "PASS: actual Python OSC bundles committed and shutdown excitation released".postln;
            0.exit;
        };
    }, ("/qmw/yang_mills/v1/" ++ kind).asSymbol);
};
File.use(ready, "w", { |file| file.write(NetAddr.langPort.asString) });
SystemClock.sched(8, { "FAIL: no complete Python OSC stream".postln; 1.exit; nil });
)
