/* Directed Hilbert-current receiver and source/destination lane router. */
(
~qmw44AcceptCurrentEdge = { |msg|
    var stage = ~qmw44QuantumStage;
    if(~qmw44QuantumCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }, {
        stage[\currents] = stage[\currents].add((
            index: msg[2].asInteger,
            source: msg[3].asInteger,
            destination: msg[4].asInteger,
            magnitude: msg[5].asFloat,
            dominantPauli: msg[6].asString,
            contribution: msg[7].asFloat
        ));
    });
};

~qmw44RouteCurrentFrame = { |frame|
    var netInflow = Array.fill(16, 0.0);
    frame[\currents].do { |edge|
        var source = edge[\source].clip(0, 15).asInteger;
        var destination = edge[\destination].clip(0, 15).asInteger;
        var magnitude = edge[\magnitude].max(0.0);
        netInflow[source] = netInflow[source] - magnitude;
        netInflow[destination] = netInflow[destination] + magnitude;
    };
    frame.put(\netInflow, netInflow);
    // A performance body opts in by defining this function. Routing never
    // alters rho, H, or the source that produced the observation.
    ~qmw44CurrentFrameObserver !? { |function| function.value(frame) };
    frame
};
)
