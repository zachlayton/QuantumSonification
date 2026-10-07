/* Typed current-event receiver. Silent until a renderer explicitly opts in. */
(
~qmw44AcceptEvent = { |msg|
    var stage = ~qmw44QuantumStage;
    if(~qmw44QuantumCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }, {
        stage[\events] = stage[\events].add((
            index: msg[2].asInteger, domain: msg[3].asString,
            source: msg[4].asInteger, destination: msg[5].asInteger,
            magnitude: msg[6].asFloat, phase: msg[7].asFloat,
            hasPhase: msg[8].asInteger > 0, provenance: msg[9].asString
        ));
    });
};

~qmw44RouteEventFrame = { |frame|
    ~qmw44CurrentEvents = frame[\events].sortBy(\index);
    // Merely loading QMW 4.4 never sonifies an event. A sound adapter must
    // deliberately supply this callback and document its mapping.
    ~qmw44EventFrameRenderer !? { |function| function.value(frame) };
    frame
};
)
