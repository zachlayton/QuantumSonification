// Silent contract checks: compile the complete addon, execute only its pure
// availability/control helpers and receiver callbacks with in-memory stubs.
(
var sourcePath = "QMW_VNF_TEST_SOURCE".getenv;
var source, begin, end, helper, scope, audition, checks = 0, failures = List.new;
var assert, extract, runCallback, validFrame, sent = List.new;
Server.all.do { |server| server.sendQuit = false };
assert = { |condition, name|
    checks = checks + 1;
    if(condition != true) { failures.add(name); ("FAIL " ++ name).postln };
};
source = File.readAllString(sourcePath);
assert.(source.compile.notNil, "complete addon compiles without execution");
assert.(File.readAllString("QMW_ACCEPTANCE_TEST_SOURCE".getenv).compile.notNil,
    "latest routed acceptance harness compiles without execution");
extract = { |left, right|
    var start = source.find(left), stop;
    if(start.notNil) { stop = source.find(right, offset: start + left.size) };
    if(start.isNil or: { stop.isNil }) { nil } {
        source.copyRange(start + left.size, stop - 1)
    }
};
helper = extract.("// BEGIN VNF AVAILABILITY HELPERS", "// END VNF AVAILABILITY HELPERS");
assert.(helper.notNil, "production availability helpers exist");
if(helper.notNil) {
    scope = ("{ var quantumPort = 17875; " ++ helper ++ " }").compile;
    assert.(scope.notNil, "production helper block compiles");
    scope.value.value;
    assert.(~qfrVnfControlPort == 18990, "production helper resolves inherited backend control port");
    ~qfrVnfControl = (sendMsg: { |self ... args| sent.add(args) });
    ~qfrVnfControls = [(enabled: true)];
    ~qfrVnfSourceLabel = (string: "");
    ~qfrVnfHamiltonianButton = (enabled: false);
    ~qriOpenHamiltonianControls = {};
    validFrame = (qubits: 2, inputPort: 17875, sourceIP: "127.0.0.1",
        diagnostics: [1.0, 1.0], bures: (pulses: 0), revision: 3,
        sealedAt: 100.0, deadline: 100.5);
    assert.(~qfrVnfParseControlPort.(nil) == 17880, "missing port defaults to 17880");
    assert.(~qfrVnfParseControlPort.("18990") == 18990, "custom backend port matches environment");
    ["", "0", "65536", "17880.5", "17880oops", "-1", " 18990 ", "999999999999", "1e4"].do { |bad|
        assert.(~qfrVnfParseControlPort.(bad) == 17880, "invalid port fallback: " ++ bad);
    };
    assert.(~qfrVnfParseControlPort.("1") == 1, "minimum valid port");
    assert.(~qfrVnfParseControlPort.("65535") == 65535, "maximum valid port");
    assert.(~qfrVnfIsAvailable.(100.0).not, "source absent before sealed input");
    ~qfrRefreshVnfControls.(100.0);
    assert.(~qfrVnfAvailable.not, "observable absence");
    assert.(~qfrVnfControls[0][\enabled].not, "controls disabled while absent");
    assert.(~qfrVnfSourceLabel[\string] == "No live VNF input — controls inactive", "clear inactive message");
    assert.(~qfrVnfHamiltonianButton[\enabled], "four-qubit navigation available while VNF absent");
    assert.(~qfrSendVnfControl.("evolution_rate", [2.0]).not, "absent control send refused");
    assert.(sent.isEmpty, "absent control sends no messages");
    assert.(~qfrVnfFrameMatches.(validFrame), "fresh designated sealed frame eligible");
    [[\qubits, 4], [\inputPort, 17879], [\sourceIP, "192.0.2.1"],
        [\diagnostics, nil], [\bures, nil], [\sealedAt, nil], [\deadline, 99.9]].do { |change|
        var rejected = validFrame.copy.put(change[0], change[1]);
        assert.(~qfrVnfFrameMatches.(rejected).not, "wrong/incomplete frame refused: " ++ change[0]);
        ~qfrObserveVnfFrame.(rejected);
        assert.(~qfrVnfLastFrameAt.isNil, "rejected input cannot refresh availability: " ++ change[0]);
    };
    ~qfrObserveVnfFrame.(validFrame);
    assert.(~qfrVnfIsAvailable.(100.5), "fresh sealed input enables availability");
    assert.(~qfrVnfIsAvailable.(101.5), "freshness boundary inclusive");
    assert.(~qfrVnfIsAvailable.(101.5001).not, "stale input unavailable");
    assert.(~qfrVnfIsAvailable.(99.0).not, "future timestamp unavailable");
    ~qfrRefreshVnfControls.(100.5);
    assert.(~qfrVnfAvailable, "observable fresh state");
    assert.(~qfrVnfControls[0][\enabled], "controls enabled while fresh");
    assert.(~qfrVnfHamiltonianButton[\enabled].not, "alternate navigation limited to inactive VNF");
    assert.(~qfrVnfSourceLabel[\string].find("Live VNF input").notNil, "fresh input status");
    ~qfrVnfLastFrameAt = Main.elapsedTime;
    ["evolution_rate", "bures_distance", "bures_clock_scale", "hamiltonian"].do { |path|
        assert.(~qfrSendVnfControl.(path, [1.0]), "fresh control admitted: " ++ path);
    };
    assert.(sent.size == 4, "all control families use guarded transport");
    assert.(sent[0] == ["/qmw/quantum/v1/control/von_neumann_flow_i/evolution_rate", 1.0],
        "guarded sender preserves wire arguments");
    ~qfrVnfLastFrameAt = Main.elapsedTime - 2.0;
    ["evolution_rate", "bures_distance", "bures_clock_scale", "hamiltonian"].do { |path|
        assert.(~qfrSendVnfControl.(path, [1.0]).not, "stale control refused: " ++ path);
    };
    assert.(sent.size == 4, "stale controls send no messages");
    ~qfrRefreshVnfControls.value;
    assert.(~qfrVnfAvailable.not and: { ~qfrVnfControls[0][\enabled].not }, "stale watchdog disables controls");
    ~qfrObserveVnfFrame.(validFrame.copy.put(\sealedAt, Main.elapsedTime).put(\deadline, Main.elapsedTime + 1));
    ~qfrRefreshVnfControls.value;
    assert.(~qfrVnfAvailable and: { ~qfrVnfControls[0][\enabled] }, "new sealed input re-enables controls");
    audition = extract.("setV2Audition = ", "\n\nopenTemporalControls = {").interpret;
    ~qriEnabled = true; ~qriPluckQueue = List[123];
    ~qfrPriorQriEnabled = nil; ~qfrV2Audition = false;
    ~qfrVnfLastFrameAt = nil;
    assert.(audition.value(true).not, "absent VNF audition refused");
    assert.(~qriEnabled and: { ~qfrV2Audition.not } and: { ~qfrPriorQriEnabled.isNil },
        "absent audition preserves native owner flags");
    assert.(~qriPluckQueue.size == 1, "absent audition preserves queued native events");
    ~qfrVnfLastFrameAt = Main.elapsedTime;
    assert.(audition.value(true), "fresh audition retains existing activation behavior");
    assert.(~qriEnabled.not and: { ~qfrV2Audition } and: { ~qfrPriorQriEnabled },
        "fresh audition retains existing owner semantics");
    assert.(~qriPluckQueue.isEmpty, "fresh audition retains existing queue semantics");
    ~qfrVnfLastFrameAt = Main.elapsedTime - 2.0;
    assert.(audition.value(false), "audition deactivation allowed while stale");
    assert.(~qriEnabled and: { ~qfrV2Audition.not } and: { ~qfrPriorQriEnabled.isNil },
        "stale audition deactivation restores native owner");
    // Ensure transport/UI lifecycle invokes the tested helpers at real seams.
    assert.(source.find("~qfrObserveVnfFrame.value(frame);").notNil, "only committed frame refresh seam exists");
    assert.(source.find("committed[\\sealedAt] = Main.elapsedTime;").notNil, "seal receipt uses receiver clock");
    assert.(source.find("~qfrVnfParseControlPort.value(\"QMW_VNF_CONTROL_PORT\".getenv)").notNil,
        "production control port reads launcher environment");
    assert.(source.find("~qfrRefreshVnfControls.value;\n        0.20.wait;").notNil,
        "existing watchdog refreshes stale UI");
};
("QMW_VNF_AVAILABILITY_TEST checks=% failures=%".format(checks, failures.size)).postln;
if(failures.isEmpty, { 0.exit }, { 1.exit });
)
