/*
QMW 4.4 centralized bounded quantum observer.

Loads independent state, current, Pauli, and event modules. It receives the
atomic qmw.4_4.quantum_frame.osc.v1 transaction on UDP 17873 and exposes one
committed ~qmw44QuantumFrame to any integrated performance body. GPE is not
required and no sound is created unless a downstream callback opts in.
*/
(
var moduleRoot = thisProcess.nowExecutingPath.dirname;
var oscKeys = [
    \qmw44FrameBegin, \qmw44Population, \qmw44CurrentEdge,
    \qmw44Preparation, \qmw44Pauli, \qmw44Diagnostics, \qmw44Event, \qmw44FrameEnd
];

// Safe for re-evaluation: replace only this layer's old OSC responders.
oscKeys.do { |key| OSCdef(key).free };
thisProcess.interpreter.executeFile(moduleRoot +/+ "qmw_4_4_quantum_buses.scd");
thisProcess.interpreter.executeFile(moduleRoot +/+ "qmw_4_4_current_router.scd");
thisProcess.interpreter.executeFile(moduleRoot +/+ "qmw_4_4_pauli_field.scd");
thisProcess.interpreter.executeFile(moduleRoot +/+ "qmw_4_4_event_router.scd");

~qmw44CommitQuantumFrame = { |msg|
    var stage = ~qmw44QuantumStage;
    var populationCount, valid, committed, now;
    if(~qmw44QuantumCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }, {
        populationCount = stage[\populationSeen].collect(_.asInteger).sum;
        valid = (populationCount == 16)
            and: { stage[\currents].size == stage[\expectedCurrents] }
            and: { stage[\paulis].size == stage[\expectedPaulis] }
            and: { stage[\events].size == stage[\expectedEvents] }
            and: { stage[\diagnostics].notNil };
        if(valid, {
            committed = stage.copy;
            committed.removeAt(\populationSeen);
            [\expectedCurrents, \expectedPaulis, \expectedEvents].do {
                |key| committed.removeAt(key)
            };
            ~qmw44RouteCurrentFrame.value(committed);
            ~qmw44RoutePauliFrame.value(committed);
            ~qmw44RouteEventFrame.value(committed);
            ~qmw44QuantumFrame = committed;
            ~qmw44QuantumFrameObserver !? { |function| function.value(committed) };
            now = Main.elapsedTime;
            if(~qmw44LastStatusPost.isNil or: { (now - ~qmw44LastStatusPost) >= 1.0 }, {
                "QMW 4.4 frame % t=% currents=% Pauli=% source=Hilbert (GPE optional)".format(
                    committed[\revision], committed[\time].round(0.001),
                    committed[\currents].size, committed[\paulis].size
                ).postln;
                ~qmw44LastStatusPost = now;
            });
        }, {
            "QMW 4.4 rejected incomplete atomic frame %".format(stage[\revision]).warn;
        });
        ~qmw44QuantumStage = nil;
        ~qmw44QuantumCompatible = false;
    });
};

thisProcess.openUDPPort(~qmw44QuantumPort);
OSCdef(\qmw44FrameBegin, { |msg| ~qmw44BeginQuantumFrame.value(msg) },
    ~qmw44QuantumRoot ++ "/frame/begin", recvPort: ~qmw44QuantumPort);
OSCdef(\qmw44Population, { |msg| ~qmw44AcceptPopulation.value(msg) },
    ~qmw44QuantumRoot ++ "/population", recvPort: ~qmw44QuantumPort);
OSCdef(\qmw44Preparation, { |msg| ~qmw44AcceptPreparation.value(msg) },
    ~qmw44QuantumRoot ++ "/preparation", recvPort: ~qmw44QuantumPort);
OSCdef(\qmw44CurrentEdge, { |msg| ~qmw44AcceptCurrentEdge.value(msg) },
    ~qmw44QuantumRoot ++ "/current_edge", recvPort: ~qmw44QuantumPort);
OSCdef(\qmw44Pauli, { |msg| ~qmw44AcceptPauli.value(msg) },
    ~qmw44QuantumRoot ++ "/pauli", recvPort: ~qmw44QuantumPort);
OSCdef(\qmw44Diagnostics, { |msg| ~qmw44AcceptDiagnostics.value(msg) },
    ~qmw44QuantumRoot ++ "/diagnostics", recvPort: ~qmw44QuantumPort);
OSCdef(\qmw44Event, { |msg| ~qmw44AcceptEvent.value(msg) },
    ~qmw44QuantumRoot ++ "/event", recvPort: ~qmw44QuantumPort);
OSCdef(\qmw44FrameEnd, { |msg| ~qmw44CommitQuantumFrame.value(msg) },
    ~qmw44QuantumRoot ++ "/frame/end", recvPort: ~qmw44QuantumPort);

~qmw44Stop = {
    oscKeys.do { |key| OSCdef(key).free };
    ~qmw44QuantumStage = nil;
    ~qmw44QuantumCompatible = false;
};
"QMW 4.4 centralized observer ready on UDP % (GPE optional).".format(
    ~qmw44QuantumPort
).postln;
)
