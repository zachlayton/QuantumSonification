/* Ranked Pauli-coordinate activity receiver. This is an observer, not H. */
(
~qmw44AcceptPauli = { |msg|
    var stage = ~qmw44QuantumStage;
    if(~qmw44QuantumCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }, {
        stage[\paulis] = stage[\paulis].add((
            index: msg[2].asInteger, label: msg[3].asString,
            weight: msg[4].asInteger, expectation: msg[5].asFloat,
            derivative: msg[6].asFloat, coefficient: msg[7].asFloat,
            transport: msg[8].asFloat, score: msg[9].asFloat
        ));
    });
};

~qmw44RoutePauliFrame = { |frame|
    ~qmw44PauliField = frame[\paulis].sortBy(\index);
    ~qmw44PauliFrameObserver !? { |function| function.value(frame) };
    frame
};
)
