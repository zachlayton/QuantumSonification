/*
QMW Quantum Harmonic Oscillator Instrument v1.1

Scientific frames arrive from qmw.qho.live_osc on UDP 17830. This file is a
perceptual adapter: it does not evolve or mutate the density matrix.
*/
(
var dataPort = 17830;
var control = NetAddr("127.0.0.1", 17831);
var window, status, populationView, stateMenu;
var makeLabel, makeSlider;

thisProcess.openUDPPort(dataPort);

s.waitForBoot {
    ~qmwQHORevision = -1;
    ~qmwQHOStageValid = false;
    ~qmwQHOPopulations = [1] ++ Array.fill(15, 0);
    ~qmwQHOCoh1Mag = Array.fill(15, 0);
    ~qmwQHOCoh1Phase = Array.fill(15, 0);
    ~qmwQHOCoh2Mag = Array.fill(14, 0);
    ~qmwQHOCoh2Phase = Array.fill(14, 0);
    ~qmwQHOObservables = [0, 0.5, 0, 0, 0.5, 0.5, 1, 0, 1];
    ~qmwQHOStateIndex = 2;

    SynthDef(\qmwQHOInstrumentV1, {
        |out=0, baseHz=55, pulseHz=8, masterAmp=0.22, populationMix=1,
        coherenceMix=0.8, uncertaintyMix=0, decayScale=1, lagSeconds=0.06,
        equalLoudness=1, sparseBoost=3.2, zeroPointBed=0.12,
        fockSustain=0.16, stateClass=2, gate=1|
        var populations = NamedControl.kr(
            \populations, [1] ++ Array.fill(15, 0), lagSeconds
        ).clip(0, 1);
        var coh1Mag = NamedControl.kr(
            \coh1Mag, Array.fill(15, 0), lagSeconds
        ).clip(0, 1);
        var coh1Phase = NamedControl.kr(
            \coh1Phase, Array.fill(15, 0), lagSeconds
        );
        var coh2Mag = NamedControl.kr(
            \coh2Mag, Array.fill(14, 0), lagSeconds
        ).clip(0, 1);
        var coh2Phase = NamedControl.kr(
            \coh2Phase, Array.fill(14, 0), lagSeconds
        );
        var meanX = NamedControl.kr(\meanX, 0, lagSeconds);
        var meanP = NamedControl.kr(\meanP, 0, lagSeconds);
        var varX = NamedControl.kr(\varX, 0.5, lagSeconds).max(0.001);
        var varP = NamedControl.kr(\varP, 0.5, lagSeconds).max(0.001);
        var trig = Impulse.ar(pulseHz.clip(0.25, 40));
        var step = PulseCount.kr(A2K.kr(trig)) % 16;
        var accent = Select.kr(step, populations).sqrt;
        var excitation = PinkNoise.ar(0.6) * Decay2.ar(
            trig * (0.04 + (0.96 * accent)), 0.001, 0.035
        );
        var uncertainty = (varX + varP).sqrt.clip(0.3, 4);
        var anisotropy = ((varP - varX) / (varP + varX)).clip(-1, 1);
        var decay = (0.06 + (0.42 * uncertainty)) * decayScale;
        var popFreqs = baseHz.clip(25, 240) * (1..16);
        var popModes = Ringz.ar(
            excitation,
            popFreqs.clip(30, 18000),
            decay.clip(0.04, 3)
        ) * populations.sqrt;
        var popSignal = Splay.ar(popModes, 0.88, 0.22);
        var coh1Modes = Ringz.ar(
            excitation,
            (baseHz * ((1..15) + 0.5)).clip(30, 18000),
            (decay * 0.72).clip(0.03, 2)
        ) * coh1Mag.sqrt;
        var coh2Modes = Ringz.ar(
            excitation,
            (baseHz * ((1..14) + 1)).clip(30, 18000),
            (decay * 1.15).clip(0.04, 3)
        ) * coh2Mag.sqrt;
        var coh1Signal = Mix(Pan2.ar(coh1Modes, coh1Phase.sin, 0.07));
        var coh2Signal = Mix(Pan2.ar(coh2Modes, coh2Phase.sin, 0.075));
        var spectralNoise = BPF.ar(
            PinkNoise.ar(0.08),
            (900 * uncertainty * (2 ** anisotropy)).clip(100, 12000),
            (0.12 + (0.2 * uncertainty)).clip(0.08, 0.8)
        );
        var orbitRadius = (meanX.squared + meanP.squared).sqrt;
        var orbitPan = (meanP / (1 + orbitRadius)).clip(-0.95, 0.95);
        var isVacuum = stateClass < 0.5;
        var isFock = (stateClass >= 0.5) * (stateClass < 1.5);
        // These are explicitly perceptual reference layers. The zero-point
        // bed does not claim that a ground-state oscillator radiates energy.
        var zeroPointSignal = Pan2.ar(
            SinOsc.ar(baseHz.clip(25, 240), 0, zeroPointBed * isVacuum),
            0
        );
        var fockLevel = (populations * (0..15)).sum;
        var fockSignal = Pan2.ar(
            SinOsc.ar(
                (baseHz * (1 + fockLevel)).clip(30, 18000),
                0,
                fockSustain * isFock
            ),
            ((fockLevel / 15) * 1.4 - 0.7).clip(-0.8, 0.8)
        );
        var sparseState = (isVacuum + isFock).clip(0, 1);
        var auditionGain = Select.kr(
            equalLoudness.clip(0, 1),
            [1, 1 + (sparseState * (sparseBoost - 1))]
        );
        var signal = (popSignal * populationMix)
            + ((coh1Signal + coh2Signal) * coherenceMix)
            + (Pan2.ar(spectralNoise, anisotropy) * uncertaintyMix)
            + zeroPointSignal
            + fockSignal;
        var envelope = EnvGen.kr(
            Env.asr(0.03, 1, 0.2), gate, doneAction: Done.freeSelf
        );
        signal = Balance2.ar(signal[0], signal[1], orbitPan);
        Out.ar(out, Limiter.ar(
            LeakDC.ar(signal) * masterAmp * auditionGain * envelope,
            0.92
        ));
    }).add;

    s.sync;
    ~qmwQHOSynth = Synth(\qmwQHOInstrumentV1);

    OSCdef(\qmwQHOBeginV1, { |msg|
        ~qmwQHORevision = msg[1].asInteger;
        ~qmwQHOStageValid = true;
    }, '/qmw/qho/v1/frame/begin', recvPort: dataPort);

    OSCdef(\qmwQHOPopulationsV1, { |msg|
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            ~qmwQHOPopulations = msg.copyRange(2, 17).collect(_.asFloat);
        };
    }, '/qmw/qho/v1/populations', recvPort: dataPort);

    OSCdef(\qmwQHOCoh1MagV1, { |msg|
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            ~qmwQHOCoh1Mag = msg.copyRange(2, 16).collect(_.asFloat);
        };
    }, '/qmw/qho/v1/coherence/1/magnitude', recvPort: dataPort);

    OSCdef(\qmwQHOCoh1PhaseV1, { |msg|
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            ~qmwQHOCoh1Phase = msg.copyRange(2, 16).collect(_.asFloat);
        };
    }, '/qmw/qho/v1/coherence/1/phase', recvPort: dataPort);

    OSCdef(\qmwQHOCoh2MagV1, { |msg|
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            ~qmwQHOCoh2Mag = msg.copyRange(2, 15).collect(_.asFloat);
        };
    }, '/qmw/qho/v1/coherence/2/magnitude', recvPort: dataPort);

    OSCdef(\qmwQHOCoh2PhaseV1, { |msg|
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            ~qmwQHOCoh2Phase = msg.copyRange(2, 15).collect(_.asFloat);
        };
    }, '/qmw/qho/v1/coherence/2/phase', recvPort: dataPort);

    OSCdef(\qmwQHOObservablesV1, { |msg|
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            ~qmwQHOObservables = msg.copyRange(2, 10).collect(_.asFloat);
        };
    }, '/qmw/qho/v1/observables', recvPort: dataPort);

    OSCdef(\qmwQHOStateV1, { |msg|
        var names = ["vacuum", "fock", "coherent", "thermal", "squeezed"];
        var index;
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            index = names.indexOfEqual(msg[2].asString);
            if(index.notNil) { ~qmwQHOStateIndex = index };
        };
    }, '/qmw/qho/v1/state', recvPort: dataPort);

    OSCdef(\qmwQHOEndV1, { |msg|
        if(~qmwQHOStageValid and: { msg[1].asInteger == ~qmwQHORevision }) {
            ~qmwQHOSynth.setn(\populations, ~qmwQHOPopulations);
            ~qmwQHOSynth.setn(\coh1Mag, ~qmwQHOCoh1Mag);
            ~qmwQHOSynth.setn(\coh1Phase, ~qmwQHOCoh1Phase);
            ~qmwQHOSynth.setn(\coh2Mag, ~qmwQHOCoh2Mag);
            ~qmwQHOSynth.setn(\coh2Phase, ~qmwQHOCoh2Phase);
            ~qmwQHOSynth.set(
                \meanX, ~qmwQHOObservables[2],
                \meanP, ~qmwQHOObservables[3],
                \varX, ~qmwQHOObservables[4],
                \varP, ~qmwQHOObservables[5],
                \stateClass, ~qmwQHOStateIndex
            );
            {
                if(populationView.notNil) {
                    populationView.value = ~qmwQHOPopulations;
                };
                if(status.notNil) {
                    status.string = "frame %   <n> %   X %   P %   purity %   C_l1 %".format(
                        ~qmwQHORevision,
                        ~qmwQHOObservables[0].round(0.001),
                        ~qmwQHOObservables[2].round(0.001),
                        ~qmwQHOObservables[3].round(0.001),
                        ~qmwQHOObservables[6].round(0.001),
                        ~qmwQHOObservables[7].round(0.001)
                    );
                };
            }.defer;
            ~qmwQHOStageValid = false;
        };
    }, '/qmw/qho/v1/frame/end', recvPort: dataPort);

    {
        window = Window("QMW Quantum Harmonic Oscillator v1.1", Rect(80, 80, 920, 760));
        ~qmwQHOWindow = window;
        window.background = Color.grey(0.11);

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

        makeLabel.("CANONICAL STATE", Rect(20, 16, 180, 22));
        stateMenu = PopUpMenu(window, Rect(20, 42, 180, 28))
            .items_(["vacuum", "fock", "coherent", "thermal", "squeezed"])
            .value_(2)
            .action_({ |menu|
                control.sendMsg('/qmw/qho/v1/control/state', menu.items[menu.value]);
            });

        Button(window, Rect(215, 42, 100, 28))
            .states_([["pause"], ["run"]])
            .action_({ |button|
                control.sendMsg('/qmw/qho/v1/control/running', 1 - button.value);
            });
        Button(window, Rect(325, 42, 100, 28))
            .states_([["reset phase"]])
            .action_({ control.sendMsg('/qmw/qho/v1/control/reset', 1) });
        Button(window, Rect(435, 42, 100, 28))
            .states_([["mute"], ["unmute"]])
            .action_({ |button|
                ~qmwQHOSynth.set(\masterAmp, if(button.value == 0, 0.22, 0));
            });

        makeSlider.("Fock n", Rect(20, 88, 280, 28),
            ControlSpec(0, 15, \lin, 1, 3), 3,
            { |view| control.sendMsg('/qmw/qho/v1/control/fock', view.value.asInteger) });
        makeSlider.("alpha Re", Rect(20, 124, 280, 28),
            ControlSpec(-2.5, 2.5, \lin, 0.01, 0.9), 0.9,
            { |view| ~qmwAlphaRe = view.value; control.sendMsg(
                '/qmw/qho/v1/control/alpha', ~qmwAlphaRe, ~qmwAlphaIm ? 0) });
        makeSlider.("alpha Im", Rect(20, 160, 280, 28),
            ControlSpec(-2.5, 2.5, \lin, 0.01, 0), 0,
            { |view| ~qmwAlphaIm = view.value; control.sendMsg(
                '/qmw/qho/v1/control/alpha', ~qmwAlphaRe ? 0.9, ~qmwAlphaIm) });
        makeSlider.("thermal <n>", Rect(20, 196, 280, 28),
            ControlSpec(0, 8, \lin, 0.01, 1.5), 1.5,
            { |view| control.sendMsg('/qmw/qho/v1/control/thermal', view.value) });
        makeSlider.("squeeze r", Rect(20, 232, 280, 28),
            ControlSpec(0, 1.2, \lin, 0.01, 0.55), 0.55,
            { |view| ~qmwSqueezeR = view.value; control.sendMsg(
                '/qmw/qho/v1/control/squeeze', ~qmwSqueezeR, ~qmwSqueezePhase ? 0) });
        makeSlider.("squeeze phase", Rect(20, 268, 280, 28),
            ControlSpec(-pi, pi, \lin, 0.01, 0), 0,
            { |view| ~qmwSqueezePhase = view.value; control.sendMsg(
                '/qmw/qho/v1/control/squeeze', ~qmwSqueezeR ? 0.55, ~qmwSqueezePhase) });
        makeSlider.("quantum omega", Rect(20, 304, 280, 28),
            ControlSpec(0.05, 8, \exp, 0.001, 1), 1,
            { |view| control.sendMsg('/qmw/qho/v1/control/omega', view.value) });

        makeLabel.("PERCEPTUAL ADAPTER", Rect(330, 88, 220, 22));
        makeSlider.("base Hz", Rect(330, 124, 280, 28),
            ControlSpec(30, 180, \exp, 0.01, 55), 55,
            { |view| ~qmwQHOSynth.set(\baseHz, view.value) });
        makeSlider.("pulse Hz", Rect(330, 160, 280, 28),
            ControlSpec(0.5, 24, \exp, 0.01, 8), 8,
            { |view| ~qmwQHOSynth.set(\pulseHz, view.value) });
        makeSlider.("population", Rect(330, 196, 280, 28),
            ControlSpec(0, 1.5, \lin, 0.01, 1), 1,
            { |view| ~qmwQHOSynth.set(\populationMix, view.value) });
        makeSlider.("coherence", Rect(330, 232, 280, 28),
            ControlSpec(0, 1.5, \lin, 0.01, 0.8), 0.8,
            { |view| ~qmwQHOSynth.set(\coherenceMix, view.value) });
        makeSlider.("uncertainty noise", Rect(330, 268, 280, 28),
            ControlSpec(0, 1, \lin, 0.01, 0), 0,
            { |view| ~qmwQHOSynth.set(\uncertaintyMix, view.value) });
        makeSlider.("decay", Rect(330, 304, 280, 28),
            ControlSpec(0.2, 3, \exp, 0.01, 1), 1,
            { |view| ~qmwQHOSynth.set(\decayScale, view.value) });
        makeSlider.("master", Rect(330, 340, 280, 28),
            ControlSpec(0, 0.7, \lin, 0.001, 0.22), 0.22,
            { |view| ~qmwQHOSynth.set(\masterAmp, view.value) });

        makeLabel.("AUDITION BALANCE", Rect(640, 88, 220, 22));
        Button(window, Rect(640, 124, 240, 28))
            .states_([
                ["equal loudness: on", Color.black, Color.cyan(0.7)],
                ["equal loudness: off", Color.grey(0.85), Color.grey(0.25)]
            ])
            .value_(0)
            .action_({ |button|
                ~qmwQHOSynth.set(\equalLoudness, 1 - button.value);
            });
        makeSlider.("sparse boost", Rect(640, 160, 240, 28),
            ControlSpec(1, 6, \lin, 0.05, 3.2), 3.2,
            { |view| ~qmwQHOSynth.set(\sparseBoost, view.value) });
        makeSlider.("zero-point bed", Rect(640, 196, 240, 28),
            ControlSpec(0, 0.3, \lin, 0.001, 0.12), 0.12,
            { |view| ~qmwQHOSynth.set(\zeroPointBed, view.value) });
        makeSlider.("Fock sustain", Rect(640, 232, 240, 28),
            ControlSpec(0, 0.35, \lin, 0.001, 0.16), 0.16,
            { |view| ~qmwQHOSynth.set(\fockSustain, view.value) });
        makeLabel.(
            "Turn equal loudness off for literal amplitude comparison.",
            Rect(640, 272, 250, 48)
        );

        makeLabel.("OPEN-SYSTEM PHYSICS", Rect(20, 348, 280, 22));
        makeSlider.("dephasing gamma", Rect(20, 376, 280, 28),
            ControlSpec(0, 2, \lin, 0.001, 0), 0,
            { |view| control.sendMsg('/qmw/qho/v1/control/dephasing', view.value) });
        makeSlider.("relaxation kappa", Rect(20, 412, 280, 28),
            ControlSpec(0, 2, \lin, 0.001, 0), 0,
            { |view| control.sendMsg('/qmw/qho/v1/control/damping', view.value) });
        makeSlider.("bath <n>", Rect(20, 448, 280, 28),
            ControlSpec(0, 8, \lin, 0.01, 0), 0,
            { |view| control.sendMsg('/qmw/qho/v1/control/bath', view.value) });
        makeLabel.(
            "These controls evolve rho; they do not inject audio noise.",
            Rect(330, 396, 400, 28)
        );

        makeLabel.("FOCK POPULATIONS |0> ... |15>", Rect(20, 500, 380, 22));
        populationView = MultiSliderView(window, Rect(20, 528, 880, 120))
            .value_(~qmwQHOPopulations)
            .isFilled_(true)
            .drawLines_(true)
            .fillColor_(Color.cyan(0.65, 0.75))
            .strokeColor_(Color.cyan(0.9))
            .background_(Color.grey(0.16));
        status = StaticText(window, Rect(20, 662, 880, 28))
            .string_("waiting for QHO frames on UDP 17830")
            .stringColor_(Color.grey(0.85));
        makeLabel.(
            "Physics: Python/NumPy QHO   |   Sound: explicit SuperCollider adapter",
            Rect(20, 708, 700, 20)
        );

        window.onClose_({ ~qmwQHOStop.() });
        window.front;
    }.defer;

    ~qmwQHOStop = {
        [\qmwQHOBeginV1, \qmwQHOPopulationsV1, \qmwQHOCoh1MagV1,
            \qmwQHOCoh1PhaseV1, \qmwQHOCoh2MagV1, \qmwQHOCoh2PhaseV1,
            \qmwQHOObservablesV1, \qmwQHOStateV1,
            \qmwQHOEndV1].do { |key| OSCdef(key).free };
        if(~qmwQHOSynth.notNil) { ~qmwQHOSynth.set(\gate, 0) };
        control.sendMsg('/qmw/qho/v1/control/quit', 1);
        "QMW QHO instrument stopped.".postln;
    };

    "QMW QHO instrument ready: data UDP 17830, controls UDP 17831.".postln;
};
)
