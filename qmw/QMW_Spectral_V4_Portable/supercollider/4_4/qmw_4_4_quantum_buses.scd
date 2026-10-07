/* QMW 4.4 bounded language-side quantum state buses. No synthesis. */
(
~qmw44QuantumPort = ~qmw44QuantumPort ? 17873;
~qmw44QuantumRoot = "/qmw/4_4/quantum";
~qmw44QuantumSchema = "qmw.4_4.quantum_frame.osc.v1";
~qmw44QuantumRevision = -1;
~qmw44QuantumCompatible = false;
~qmw44QuantumStage = nil;
~qmw44QuantumFrame = (
    revision: -1, time: 0.0,
    populations: Array.fill(16, 0.0),
    currents: Array.new, paulis: Array.new, events: Array.new,
    preparation: (mode: "coherent", localizedIndex: 0, coherentTheta: 0.95,
        coherentPhase: 0.55, squeezeMagnitude: 0.62, squeezePhase: pi/2,
        temperature: 0.8, revision: 0),
    diagnostics: (trace: 0.0, purity: 0.0, minimumEigenvalue: 0.0,
        hermiticityError: 0.0, antisymmetryError: 0.0, continuityError: 0.0),
    netInflow: Array.fill(16, 0.0)
);
~qmw44Capabilities = ~qmw44Capabilities ? IdentityDictionary.new;
~qmw44Capabilities.put(\densityStateObserver, true);
~qmw44Capabilities.put(\hilbertCurrent, true);
~qmw44Capabilities.put(\pauliActivity, true);
~qmw44Capabilities.put(\currentEvents, true);
~qmw44Capabilities.put(\gpeRequired, false);

~qmw44BeginQuantumFrame = { |msg|
    var compatible = (msg.size >= 8)
        and: { msg[3].asString == ~qmw44QuantumSchema }
        and: { msg[4].asInteger == 16 };
    ~qmw44QuantumCompatible = compatible;
    if(compatible, {
        ~qmw44QuantumRevision = msg[1].asInteger;
        ~qmw44QuantumStage = (
            revision: msg[1].asInteger, time: msg[2].asFloat,
            expectedCurrents: msg[5].asInteger,
            expectedPaulis: msg[6].asInteger,
            expectedEvents: msg[7].asInteger,
            populations: Array.fill(16, 0.0),
            populationSeen: Array.fill(16, false),
            currents: Array.new, paulis: Array.new, events: Array.new,
            preparation: nil,
            diagnostics: nil
        );
    }, {
        ~qmw44QuantumStage = nil;
    });
};

~qmw44AcceptPreparation = { |msg|
    var stage = ~qmw44QuantumStage;
    if(~qmw44QuantumCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }, {
        stage[\preparation] = (
            mode: msg[2].asString, localizedIndex: msg[3].asInteger,
            coherentTheta: msg[4].asFloat, coherentPhase: msg[5].asFloat,
            squeezeMagnitude: msg[6].asFloat, squeezePhase: msg[7].asFloat,
            temperature: msg[8].asFloat, revision: msg[9].asInteger
        );
    });
};

~qmw44AcceptPopulation = { |msg|
    var stage = ~qmw44QuantumStage;
    var lane;
    if(~qmw44QuantumCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }, {
        lane = msg[2].asInteger;
        if(lane.inclusivelyBetween(0, 15), {
            stage[\populations][lane] = msg[3].asFloat;
            stage[\populationSeen][lane] = true;
        });
    });
};

~qmw44AcceptDiagnostics = { |msg|
    var stage = ~qmw44QuantumStage;
    if(~qmw44QuantumCompatible and: { stage.notNil }
        and: { msg[1].asInteger == stage[\revision] }, {
        stage[\diagnostics] = (
            trace: msg[2].asFloat, purity: msg[3].asFloat,
            minimumEigenvalue: msg[4].asFloat,
            hermiticityError: msg[5].asFloat,
            antisymmetryError: msg[6].asFloat,
            continuityError: msg[7].asFloat
        );
    });
};
)
