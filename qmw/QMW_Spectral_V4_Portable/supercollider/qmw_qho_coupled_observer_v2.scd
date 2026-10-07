/*
QMW Coupled Quantum Harmonic Oscillator Instrument V2

Scientific frames arrive from qmw.qho.live_osc_v2 on UDP 17840. The
SuperCollider SynthDef is an explicit perceptual adapter and never evolves or
mutates the quantum state. The Python/NumPy model remains authoritative.
*/
(
var dataPort = 17840;
var control = NetAddr("127.0.0.1", 17841);
var window, jointView, populationAView, populationBView;
var status, parameterStatus, temporalStatus, stateMenu, temporalModeMenu;
var quantumRecordMenu, geodesicRecordMenu;
var clockScaleMenu, makeLabel, makeSlider, sendFock, sendAlpha, sendOmega;
var updateEuclideanPattern;

thisProcess.openUDPPort(dataPort);

~qmwQHOV2Revision = -1;
~qmwQHOV2StageValid = false;
~qmwQHOV2Joint = Array.fill(16, 0).put(4, 1);
~qmwQHOV2PopulationA = [0, 1, 0, 0];
~qmwQHOV2PopulationB = [1, 0, 0, 0];
~qmwQHOV2Observables = Array.fill(11, 0);
~qmwQHOV2Parameters = ["single_a", 1, 1, 0.2, 1, 0];
~qmwQHOV2FockA = 1;
~qmwQHOV2FockB = 0;
~qmwQHOV2AlphaARe = 0.8;
~qmwQHOV2AlphaAIm = 0;
~qmwQHOV2AlphaBRe = 0;
~qmwQHOV2AlphaBIm = 0;
~qmwQHOV2OmegaA = 1;
~qmwQHOV2OmegaB = 1;
~qmwQHOV2Temporal = Array.fill(17, 0);
~qmwQHOV2Geodesic = Array.fill(11, 0);
~qmwQHOV2ClockMode = 0;
~qmwQHOV2ClockDivision = 1;
~qmwQHOV2QuantumEuclideanStep = 0;
~qmwQHOV2EuclideanHits = 5;
~qmwQHOV2EuclideanSteps = 8;
~qmwQHOV2EuclideanMask = Array.fill(16, { |index|
    if(index < 8, { (((index * 5) % 8) < 5).asInteger }, { 0 })
});

s.waitForBoot {
    SynthDef(\qmwQHOCoupledInstrumentV2, {
        |out=0, baseHzA=90, baseHzB=90, fallbackHz=7,
        clockMode=0, clockScale=1,
        t_temporal=0, t_geodesic=0, euclidSteps=8, recursiveDepth=3,
        decaySeconds=0.22,
        localMix=1, exchangeMix=0.7,
        masterAmp=0.22, soundEnabled=1, lagSeconds=0.06, gate=1|
        var populationA = NamedControl.kr(
            \populationA, [0, 1, 0, 0], lagSeconds
        ).clip(0, 1);
        var populationB = NamedControl.kr(
            \populationB, [1, 0, 0, 0], lagSeconds
        ).clip(0, 1);
        var meanNA = NamedControl.kr(\meanNA, 1, lagSeconds).max(0);
        var meanNB = NamedControl.kr(\meanNB, 0, lagSeconds).max(0);
        var exchangeRe = NamedControl.kr(\exchangeRe, 0, lagSeconds);
        var exchangeIm = NamedControl.kr(\exchangeIm, 0, lagSeconds);
        var omegaA = NamedControl.kr(\omegaA, 1, lagSeconds).max(0.001);
        var omegaB = NamedControl.kr(\omegaB, 1, lagSeconds).max(0.001);
        var omegaMean = ((omegaA + omegaB) * 0.5).max(0.001);
        // Each audible fundamental is an explicit downstream tuning control.
        // The physical omega ratio remains audible, but model units are never
        // mislabeled as literal Hz and changing either fundamental cannot
        // modify the authoritative Hamiltonian.
        var frequencyA = baseHzA * (omegaA / omegaMean).clip(0.4, 2.5);
        var frequencyB = baseHzB * (omegaB / omegaMean).clip(0.4, 2.5);
        var energyA = (meanNA / 3).sqrt.clip(0, 1.4);
        var energyB = (meanNB / 3).sqrt.clip(0, 1.4);
        var euclidMask = NamedControl.kr(
            \euclidMask, [1, 0, 1, 0, 1, 1, 0, 1]
            ++ Array.fill(8, 0)
        ).clip(0, 1);
        var steadyTrigger = Impulse.ar(
            (fallbackHz * clockScale).clip(0.125, 30)
        );
        var temporalTrigger = K2A.ar(t_temporal);
        var geodesicTrigger = K2A.ar(t_geodesic);
        var euclidIndex = (PulseCount.ar(steadyTrigger) - 1)
            % euclidSteps.clip(1, 16);
        var euclideanTrigger = steadyTrigger
            * Select.ar(euclidIndex, K2A.ar(euclidMask));
        // Quantum-recursive is a downstream time adapter. Each accepted QMW
        // record roots a bounded 1, 1/2, 1/4, 1/8 delay hierarchy; it never
        // feeds back into or reinterprets the coupled oscillator state.
        var recursiveInterval = (
            1 / (fallbackHz * clockScale).clip(0.125, 30)
        );
        var recursiveTrigger = Mix(
            DelayN.ar(
                temporalTrigger,
                8,
                [0, 0.5, 0.25, 0.125] * recursiveInterval
            ) * [
                1,
                recursiveDepth >= 1,
                recursiveDepth >= 2,
                recursiveDepth >= 3
            ]
        );
        var sharedTrigger = Select.ar(
            clockMode.clip(0, 5),
            [
                temporalTrigger,
                steadyTrigger,
                euclideanTrigger,
                temporalTrigger,
                geodesicTrigger,
                recursiveTrigger
            ]
        );
        var triggerA = sharedTrigger;
        var triggerB = sharedTrigger;
        var excitationA = PinkNoise.ar(0.5) * Decay2.ar(
            triggerA * (0.04 + (0.96 * energyA)), 0.001, 0.055
        );
        var excitationB = PinkNoise.ar(0.5) * Decay2.ar(
            triggerB * (0.04 + (0.96 * energyB)), 0.001, 0.055
        );
        // Local Fock populations shape spectral weights. Mean excitation owns
        // amplitude, so an unexcited mode remains silent even though P0 = 1.
        var modeA = Mix(
            Ringz.ar(
                excitationA, frequencyA * (1..4), decaySeconds.clip(0.02, 3)
            )
            * populationA.sqrt
        ) * energyA * 0.16;
        var modeB = Mix(
            Ringz.ar(
                excitationB, frequencyB * (1..4), decaySeconds.clip(0.02, 3)
            )
            * populationB.sqrt
        ) * energyB * 0.16;
        var centerFrequency = (frequencyA + frequencyB) * 0.5;
        // The two quadratures of <a†b> directly drive a shared interaction
        // voice. No random noise is added to represent coherence.
        var exchangeVoice = (
            SinOsc.ar(centerFrequency, 0, exchangeRe)
            + SinOsc.ar(centerFrequency, pi * 0.5, exchangeIm)
        ) * 0.14;
        var exchangePan = (
            exchangeIm / (exchangeRe.abs + exchangeIm.abs + 0.001)
        ).clip(-0.65, 0.65);
        var signal = (Pan2.ar(modeA, -0.72) + Pan2.ar(modeB, 0.72)) * localMix;
        var envelope = EnvGen.kr(
            Env.asr(0.03, 1, 0.2), gate, doneAction: Done.freeSelf
        );
        signal = signal + (Pan2.ar(exchangeVoice, exchangePan) * exchangeMix);
        Out.ar(out, Limiter.ar(
            LeakDC.ar(signal) * masterAmp * soundEnabled * envelope, 0.92
        ));
    }).add;
    s.sync;
    ~qmwQHOV2Synth = Synth(\qmwQHOCoupledInstrumentV2);
};

OSCdef(\qmwQHOV2Begin, { |msg|
    ~qmwQHOV2Revision = msg[1].asInteger;
    ~qmwQHOV2StageValid = true;
}, '/qmw/qho/v2/frame/begin', recvPort: dataPort);

OSCdef(\qmwQHOV2Joint, { |msg|
    if(~qmwQHOV2StageValid and: { msg[1].asInteger == ~qmwQHOV2Revision }) {
        ~qmwQHOV2Joint = msg.copyRange(2, 17).collect(_.asFloat);
    };
}, '/qmw/qho/v2/populations/joint', recvPort: dataPort);

OSCdef(\qmwQHOV2PopulationA, { |msg|
    if(~qmwQHOV2StageValid and: { msg[1].asInteger == ~qmwQHOV2Revision }) {
        ~qmwQHOV2PopulationA = msg.copyRange(2, 5).collect(_.asFloat);
    };
}, '/qmw/qho/v2/populations/a', recvPort: dataPort);

OSCdef(\qmwQHOV2PopulationB, { |msg|
    if(~qmwQHOV2StageValid and: { msg[1].asInteger == ~qmwQHOV2Revision }) {
        ~qmwQHOV2PopulationB = msg.copyRange(2, 5).collect(_.asFloat);
    };
}, '/qmw/qho/v2/populations/b', recvPort: dataPort);

OSCdef(\qmwQHOV2Observables, { |msg|
    if(~qmwQHOV2StageValid and: { msg[1].asInteger == ~qmwQHOV2Revision }) {
        ~qmwQHOV2Observables = msg.copyRange(2, 12).collect(_.asFloat);
    };
}, '/qmw/qho/v2/observables', recvPort: dataPort);

OSCdef(\qmwQHOV2Parameters, { |msg|
    if(~qmwQHOV2StageValid and: { msg[1].asInteger == ~qmwQHOV2Revision }) {
        ~qmwQHOV2Parameters = [
            msg[2].asString, msg[3].asFloat, msg[4].asFloat,
            msg[5].asFloat, msg[6].asInteger, msg[7].asInteger
        ];
    };
}, '/qmw/qho/v2/parameters', recvPort: dataPort);

OSCdef(\qmwQHOV2End, { |msg|
    if(~qmwQHOV2StageValid and: { msg[1].asInteger == ~qmwQHOV2Revision }) {
        if(~qmwQHOV2Synth.notNil) {
            ~qmwQHOV2Synth.setn(\populationA, ~qmwQHOV2PopulationA);
            ~qmwQHOV2Synth.setn(\populationB, ~qmwQHOV2PopulationB);
            ~qmwQHOV2Synth.set(
                \meanNA, ~qmwQHOV2Observables[0],
                \meanNB, ~qmwQHOV2Observables[1],
                \exchangeRe, ~qmwQHOV2Observables[4],
                \exchangeIm, ~qmwQHOV2Observables[5],
                \omegaA, ~qmwQHOV2Parameters[1],
                \omegaB, ~qmwQHOV2Parameters[2]
            );
        };
        {
            if(jointView.notNil) { jointView.value = ~qmwQHOV2Joint };
            if(populationAView.notNil) {
                populationAView.value = ~qmwQHOV2PopulationA
            };
            if(populationBView.notNil) {
                populationBView.value = ~qmwQHOV2PopulationB
            };
            if(status.notNil) {
                status.string = (
                    "frame %    <Na> %    <Nb> %    total %    "
                    ++ "exchange % + %i    Sa %    Sb %"
                ).format(
                    ~qmwQHOV2Revision,
                    ~qmwQHOV2Observables[0].round(0.001),
                    ~qmwQHOV2Observables[1].round(0.001),
                    ~qmwQHOV2Observables[2].round(0.001),
                    ~qmwQHOV2Observables[4].round(0.001),
                    ~qmwQHOV2Observables[5].round(0.001),
                    ~qmwQHOV2Observables[9].round(0.001),
                    ~qmwQHOV2Observables[10].round(0.001)
                );
            };
            if(parameterStatus.notNil) {
                parameterStatus.string = (
                    "state %    omegaA %    omegaB %    detuning %    g %"
                ).format(
                    ~qmwQHOV2Parameters[0],
                    ~qmwQHOV2Parameters[1].round(0.001),
                    ~qmwQHOV2Parameters[2].round(0.001),
                    (~qmwQHOV2Parameters[1] - ~qmwQHOV2Parameters[2]).round(0.001),
                    ~qmwQHOV2Parameters[3].round(0.001)
                );
            };
        }.defer;
        ~qmwQHOV2StageValid = false;
    };
}, '/qmw/qho/v2/frame/end', recvPort: dataPort);

OSCdef(\qmwQHOV2TemporalState, { |msg|
    ~qmwQHOV2Temporal = msg.copyRange(1, 17).collect(_.asFloat);
    {
        if(temporalStatus.notNil) {
            temporalStatus.string = (
                "QMW temporal record %    intrinsic %    dBures %    "
                ++ "pulses %    coherence gain %"
            ).format(
                ~qmwQHOV2Temporal[1].asInteger,
                ~qmwQHOV2Temporal[2].round(0.001),
                ~qmwQHOV2Temporal[3].round(0.0001),
                ~qmwQHOV2Temporal[16].asInteger,
                ~qmwQHOV2Temporal[11].round(0.001)
            );
        };
    }.defer;
}, '/qmw/qho/v2/temporal/state', recvPort: dataPort);

OSCdef(\qmwQHOV2TemporalPulse, { |msg|
    var record = msg[1].asInteger;
    var mode = ~qmwQHOV2ClockMode ? 0;
    var division = ~qmwQHOV2ClockDivision ? 1;
    var step, hit;
    // Division is downstream of the QMW clock: intrinsic time and every
    // temporal record remain intact even when fewer records are sounded.
    if(mode == 3) {
        // Divide first, then advance: clock scaling preserves the declared
        // E(k,n) hit pattern rather than aliasing it against skipped steps.
        if((record % division) == 0) {
            step = ~qmwQHOV2QuantumEuclideanStep
                % ~qmwQHOV2EuclideanSteps;
            hit = ~qmwQHOV2EuclideanMask[step];
            ~qmwQHOV2QuantumEuclideanStep =
                ~qmwQHOV2QuantumEuclideanStep + 1;
            if(hit > 0) {
                ~qmwQHOV2Synth !? { |synth| synth.set(\t_temporal, 1) };
            };
        };
    } {
        if(((mode == 0) or: { mode == 5 })
            and: { (record % division) == 0 }) {
            ~qmwQHOV2Synth !? { |synth| synth.set(\t_temporal, 1) };
        };
    };
}, '/qmw/qho/v2/temporal/pulse', recvPort: dataPort);

OSCdef(\qmwQHOV2GeodesicState, { |msg|
    ~qmwQHOV2Geodesic = msg.copyRange(1, 11).collect(_.asFloat);
    {
        if(temporalStatus.notNil) {
            temporalStatus.string = (
                "QMW record %  intrinsic %  dBures %  pulses %\n"
                ++ "geodesic %  length %  defect %  curvature2 %  pulses %"
            ).format(
                ~qmwQHOV2Temporal[1].asInteger,
                ~qmwQHOV2Temporal[2].round(0.001),
                ~qmwQHOV2Temporal[3].round(0.0001),
                ~qmwQHOV2Temporal[16].asInteger,
                ~qmwQHOV2Geodesic[1].asInteger,
                ~qmwQHOV2Geodesic[2].round(0.001),
                ~qmwQHOV2Geodesic[6].round(0.0001),
                ~qmwQHOV2Geodesic[7].round(0.001),
                ~qmwQHOV2Geodesic[10].asInteger
            );
        };
    }.defer;
}, '/qmw/qho/v2/geodesic/state', recvPort: dataPort);

OSCdef(\qmwQHOV2GeodesicPulse, { |msg|
    var record = msg[1].asInteger;
    if((~qmwQHOV2ClockMode == 4)
        and: { (record % (~qmwQHOV2ClockDivision ? 1)) == 0 }) {
        ~qmwQHOV2Synth !? { |synth| synth.set(\t_geodesic, 1) };
    };
}, '/qmw/qho/v2/geodesic/pulse', recvPort: dataPort);

{
    window = Window(
        "QMW Coupled Quantum Harmonic Oscillators V2",
        Rect(70, 24, 1040, 964)
    );
    ~qmwQHOV2Window = window;
    window.background = Color.grey(0.105);

    makeLabel = { |text, rect|
        StaticText(window, rect)
            .string_(text)
            .stringColor_(Color.grey(0.86));
    };
    makeSlider = { |label, rect, spec, initial, action|
        EZSlider(window, rect, label, spec, action, initial)
            .setColors(
                Color.grey(0.17), Color.grey(0.78),
                Color.cyan(0.7), Color.grey(0.45),
                Color.grey(0.9), Color.cyan(0.8)
            );
    };
    sendFock = {
        control.sendMsg(
            '/qmw/qho/v2/control/fock', ~qmwQHOV2FockA, ~qmwQHOV2FockB
        )
    };
    sendAlpha = {
        control.sendMsg(
            '/qmw/qho/v2/control/alpha',
            ~qmwQHOV2AlphaARe, ~qmwQHOV2AlphaAIm,
            ~qmwQHOV2AlphaBRe, ~qmwQHOV2AlphaBIm
        )
    };
    sendOmega = {
        control.sendMsg(
            '/qmw/qho/v2/control/omega', ~qmwQHOV2OmegaA, ~qmwQHOV2OmegaB
        )
    };
    updateEuclideanPattern = {
        var hits = ~qmwQHOV2EuclideanHits
            .clip(1, ~qmwQHOV2EuclideanSteps);
        var steps = ~qmwQHOV2EuclideanSteps.clip(1, 16);
        ~qmwQHOV2EuclideanHits = hits;
        ~qmwQHOV2EuclideanMask = Array.fill(16, { |index|
            if(index < steps, {
                (((index * hits) % steps) < hits).asInteger
            }, { 0 })
        });
        ~qmwQHOV2Synth !? { |synth|
            synth.set(\euclidSteps, steps);
            synth.setn(\euclidMask, ~qmwQHOV2EuclideanMask);
        };
    };

    makeLabel.("PREPARED TWO-MODE STATE", Rect(20, 16, 260, 22));
    stateMenu = PopUpMenu(window, Rect(20, 42, 210, 28))
        .items_(["single_a", "single_b", "fock_product", "coherent_product"])
        .value_(0)
        .action_({ |menu|
            control.sendMsg('/qmw/qho/v2/control/state', menu.items[menu.value])
        });
    Button(window, Rect(245, 42, 100, 28))
        .states_([["pause"], ["run"]])
        .action_({ |button|
            control.sendMsg('/qmw/qho/v2/control/running', 1 - button.value)
        });
    Button(window, Rect(355, 42, 110, 28))
        .states_([["reset time"]])
        .action_({ control.sendMsg('/qmw/qho/v2/control/reset', 1) });
    makeLabel.(
        "PYTHON PHYSICS → EXPLICIT SUPERCOLLIDER ADAPTER",
        Rect(500, 42, 500, 28)
    );

    makeLabel.("MODE A", Rect(20, 92, 120, 22));
    makeSlider.("Fock nA", Rect(20, 120, 300, 28),
        ControlSpec(0, 3, \lin, 1, 1), 1,
        { |view| ~qmwQHOV2FockA = view.value.asInteger; sendFock.() });
    makeSlider.("alpha A Re", Rect(20, 156, 300, 28),
        ControlSpec(-1.5, 1.5, \lin, 0.01, 0.8), 0.8,
        { |view| ~qmwQHOV2AlphaARe = view.value; sendAlpha.() });
    makeSlider.("alpha A Im", Rect(20, 192, 300, 28),
        ControlSpec(-1.5, 1.5, \lin, 0.01, 0), 0,
        { |view| ~qmwQHOV2AlphaAIm = view.value; sendAlpha.() });
    makeSlider.("omega A", Rect(20, 228, 300, 28),
        ControlSpec(0.1, 3, \exp, 0.001, 1), 1,
        { |view| ~qmwQHOV2OmegaA = view.value; sendOmega.() });

    makeLabel.("MODE B", Rect(350, 92, 120, 22));
    makeSlider.("Fock nB", Rect(350, 120, 300, 28),
        ControlSpec(0, 3, \lin, 1, 0), 0,
        { |view| ~qmwQHOV2FockB = view.value.asInteger; sendFock.() });
    makeSlider.("alpha B Re", Rect(350, 156, 300, 28),
        ControlSpec(-1.5, 1.5, \lin, 0.01, 0), 0,
        { |view| ~qmwQHOV2AlphaBRe = view.value; sendAlpha.() });
    makeSlider.("alpha B Im", Rect(350, 192, 300, 28),
        ControlSpec(-1.5, 1.5, \lin, 0.01, 0), 0,
        { |view| ~qmwQHOV2AlphaBIm = view.value; sendAlpha.() });
    makeSlider.("omega B", Rect(350, 228, 300, 28),
        ControlSpec(0.1, 3, \exp, 0.001, 1), 1,
        { |view| ~qmwQHOV2OmegaB = view.value; sendOmega.() });

    makeLabel.("INTERACTION", Rect(680, 92, 180, 22));
    makeSlider.("coupling g", Rect(680, 120, 320, 28),
        ControlSpec(-1, 1, \lin, 0.001, 0.2), 0.2,
        { |view| control.sendMsg('/qmw/qho/v2/control/coupling', view.value) });
    makeLabel.(
        "H_int = hbar g (a†b + ab†)\nControls reset model time so each trajectory remains reproducible.",
        Rect(680, 162, 330, 62)
    );

    makeLabel.("SOUND ADAPTER", Rect(680, 228, 150, 22));
    Button(window, Rect(845, 226, 155, 26))
        .states_([
            ["sound: on", Color.black, Color.cyan(0.7)],
            ["sound: off", Color.grey(0.85), Color.grey(0.25)]
        ])
        .action_({ |button|
            ~qmwQHOV2Synth !? { |synth| synth.set(\soundEnabled, 1 - button.value) }
        });
    makeSlider.("fundamental A", Rect(680, 254, 155, 28),
        ControlSpec(35, 220, \exp, 0.01, 90), 90,
        { |view| ~qmwQHOV2Synth !? {
            |synth| synth.set(\baseHzA, view.value)
        } });
    makeSlider.("fundamental B", Rect(845, 254, 155, 28),
        ControlSpec(35, 220, \exp, 0.01, 90), 90,
        { |view| ~qmwQHOV2Synth !? {
            |synth| synth.set(\baseHzB, view.value)
        } });
    makeSlider.("local mix", Rect(680, 288, 155, 28),
        ControlSpec(0, 1.5, \lin, 0.01, 1), 1,
        { |view| ~qmwQHOV2Synth !? { |synth| synth.set(\localMix, view.value) } });
    makeSlider.("exchange", Rect(845, 288, 155, 28),
        ControlSpec(0, 1.5, \lin, 0.01, 0.7), 0.7,
        { |view| ~qmwQHOV2Synth !? { |synth| synth.set(\exchangeMix, view.value) } });
    makeSlider.("master", Rect(680, 322, 155, 28),
        ControlSpec(0, 0.7, \lin, 0.001, 0.22), 0.22,
        { |view| ~qmwQHOV2Synth !? { |synth| synth.set(\masterAmp, view.value) } });
    makeSlider.("decay", Rect(845, 322, 155, 28),
        ControlSpec(0.03, 2, \exp, 0.001, 0.22), 0.22,
        { |view| ~qmwQHOV2Synth !? {
            |synth| synth.set(\decaySeconds, view.value)
        } });

    makeLabel.("QMW TEMPORAL ENGINE", Rect(680, 360, 160, 22));
    quantumRecordMenu = PopUpMenu(window, Rect(845, 356, 155, 26))
        .items_(["records: poisson", "records: fixed"])
        .value_(0)
        .action_({ |menu|
            control.sendMsg(
                '/qmw/qho/v2/control/temporal-mode',
                if(menu.value == 0, "poisson", "fixed")
            )
        });
    makeSlider.("distance", Rect(680, 386, 155, 28),
        ControlSpec(0.002, 0.2, \exp, 0.0001, 0.025), 0.025,
        { |view|
            control.sendMsg(
                '/qmw/qho/v2/control/temporal-distance', view.value
            );
            control.sendMsg(
                '/qmw/qho/v2/control/geodesic-distance', view.value
            );
        });
    makeSlider.("coherence", Rect(845, 386, 155, 28),
        ControlSpec(0, 1, \lin, 0.01, 0.35), 0.35,
        { |view| control.sendMsg(
            '/qmw/qho/v2/control/coherence-depth', view.value
        ) });
    temporalModeMenu = PopUpMenu(window, Rect(680, 420, 155, 28))
        .items_([
            "Quantum", "Steady", "Euclidean", "Q-Euclidean",
            "Q-Geodesic", "Q-Recursive"
        ])
        .value_(0)
        .action_({ |menu|
            ~qmwQHOV2ClockMode = menu.value;
            if(menu.value == 3) { ~qmwQHOV2QuantumEuclideanStep = 0 };
            ~qmwQHOV2Synth !? { |synth| synth.set(\clockMode, menu.value) }
        });
    clockScaleMenu = PopUpMenu(window, Rect(845, 420, 155, 28))
        .items_(["clock 1x", "clock 0.5x", "clock 0.25x", "clock 0.125x"])
        .value_(0)
        .action_({ |menu|
            var divisions = [1, 2, 4, 8];
            var scales = [1, 0.5, 0.25, 0.125];
            ~qmwQHOV2ClockDivision = divisions[menu.value];
            ~qmwQHOV2Synth !? { |synth|
                synth.set(\clockScale, scales[menu.value])
            };
        });
    makeSlider.("euclid hits", Rect(680, 454, 155, 28),
        ControlSpec(1, 16, \lin, 1, 5), 5,
        { |view|
            ~qmwQHOV2EuclideanHits = view.value.asInteger;
            updateEuclideanPattern.();
        });
    makeSlider.("euclid steps", Rect(845, 454, 155, 28),
        ControlSpec(2, 16, \lin, 1, 8), 8,
        { |view|
            ~qmwQHOV2EuclideanSteps = view.value.asInteger;
            updateEuclideanPattern.();
        });
    makeSlider.("steady Hz", Rect(680, 488, 155, 28),
        ControlSpec(0.5, 20, \exp, 0.01, 7), 7,
        { |view| ~qmwQHOV2Synth !? {
            |synth| synth.set(\fallbackHz, view.value)
        } });
    makeSlider.("geodesic bend", Rect(845, 488, 155, 28),
        ControlSpec(0, 100, \lin, 0.1, 1), 1,
        { |view| control.sendMsg(
            '/qmw/qho/v2/control/geodesic-bending-depth', view.value
        ) });
    geodesicRecordMenu = PopUpMenu(window, Rect(680, 522, 155, 28))
        .items_(["geodesic: fixed", "geodesic: poisson"])
        .value_(0)
        .action_({ |menu|
            control.sendMsg(
                '/qmw/qho/v2/control/geodesic-mode',
                if(menu.value == 0, "fixed", "poisson")
            )
        });
    makeSlider.("geodesic scale", Rect(845, 522, 155, 28),
        ControlSpec(0.01, 4, \exp, 0.01, 1), 1,
        { |view| control.sendMsg(
            '/qmw/qho/v2/control/geodesic-clock-scale', view.value
        ) });

    makeLabel.(
        "JOINT POPULATIONS |nA,nB> — flat order nA*4+nB",
        Rect(20, 560, 500, 22)
    );
    jointView = MultiSliderView(window, Rect(20, 588, 990, 120))
        .value_(~qmwQHOV2Joint)
        .isFilled_(true)
        .drawLines_(true)
        .fillColor_(Color.cyan(0.62, 0.8))
        .strokeColor_(Color.cyan(0.9))
        .background_(Color.grey(0.16));

    makeLabel.("MODE A POPULATIONS |0>...|3>", Rect(20, 720, 350, 22));
    populationAView = MultiSliderView(window, Rect(20, 748, 480, 72))
        .value_(~qmwQHOV2PopulationA)
        .isFilled_(true)
        .fillColor_(Color.cyan(0.7, 0.78))
        .background_(Color.grey(0.16));
    makeLabel.("MODE B POPULATIONS |0>...|3>", Rect(530, 720, 350, 22));
    populationBView = MultiSliderView(window, Rect(530, 748, 480, 72))
        .value_(~qmwQHOV2PopulationB)
        .isFilled_(true)
        .fillColor_(Color.magenta(0.65, 0.78))
        .background_(Color.grey(0.16));

    status = StaticText(window, Rect(20, 832, 990, 28))
        .string_("waiting for coupled-QHO frames on UDP 17840")
        .stringColor_(Color.grey(0.9));
    parameterStatus = StaticText(window, Rect(20, 864, 990, 28))
        .string_("state single_a    omegaA 1    omegaB 1    detuning 0    g 0.2")
        .stringColor_(Color.cyan(0.8));
    makeLabel.(
        "Reduced entropy is entanglement entropy only when the global state is pure.",
        Rect(20, 896, 760, 22)
    );
    temporalStatus = StaticText(window, Rect(20, 922, 990, 38))
        .string_("QMW temporal clock waiting for density displacement")
        .stringColor_(Color.magenta(0.72));

    window.onClose_({ ~qmwQHOV2Stop.() });
    window.front;
}.defer;

~qmwQHOV2Stop = {
    [\qmwQHOV2Begin, \qmwQHOV2Joint, \qmwQHOV2PopulationA,
        \qmwQHOV2PopulationB, \qmwQHOV2Observables,
        \qmwQHOV2Parameters, \qmwQHOV2End,
        \qmwQHOV2TemporalState, \qmwQHOV2TemporalPulse,
        \qmwQHOV2GeodesicState, \qmwQHOV2GeodesicPulse
    ].do { |key| OSCdef(key).free };
    if(~qmwQHOV2Synth.notNil) { ~qmwQHOV2Synth.set(\gate, 0) };
    control.sendMsg('/qmw/qho/v2/control/quit', 1);
    "QMW coupled QHO V2 instrument stopped.".postln;
};

"QMW coupled QHO V2 instrument ready: data UDP 17840, controls UDP 17841.".postln;
)
