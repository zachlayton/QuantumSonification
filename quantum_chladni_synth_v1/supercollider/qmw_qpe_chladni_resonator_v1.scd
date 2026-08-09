/*
QMW QPE x Quantum Chladni Resonator v1

Python performs the density evolution, finite-register QPE, and Bayesian
conditioning. SuperCollider receives the resulting modal posterior and renders
the physical coupling

    gain_j = sqrt(P(j|y)) * material_j
             * V_j(strike) * V_j(pickup).

Evaluate this file after booting the server. It listens on the active sclang
UDP port printed in the post window (often 57120 or 57121). Then run, replacing
57120 if the printed port differs:

    python -m quantum_chladni_synth_v1.quantum_chladni_controller_v1 \
        --out-port 57120 --control-port 7473 --modes 24 --qpe-bits 5

Use ~qpeChladniStrike.(), ~qpeChladniStatus.(), and ~qpeChladniStop.().
*/

(
~qpeChladniModeCount = 24;
~qpeChladniController = NetAddr("127.0.0.1", 7473);
~qpeChladniRevision = -1;
~qpeChladniFrameValid = false;
~qpeChladniReceived = Array.fill(~qpeChladniModeCount, false);
~qpeChladniFreqs = Array.fill(~qpeChladniModeCount, 220.0);
~qpeChladniDecays = Array.fill(~qpeChladniModeCount, 1.5);
~qpeChladniWeights = Array.fill(~qpeChladniModeCount, 0.0);
~qpeChladniPosterior = Array.fill(~qpeChladniModeCount, 0.0);
~qpeChladniPhases = Array.fill(~qpeChladniModeCount, 0.0);
~qpeChladniPans = Array.fill(~qpeChladniModeCount, 0.0);

~qpeChladniGeometrySamples = 0;
~qpeChladniGeometryModes = 0;
~qpeChladniGeometryReceived = Array.new;
~qpeChladniVertices = Array.new;
~qpeChladniEigenRows = Array.new;
~qpeChladniGeometryReady = false;

~qpeChladniStrikePoint = [0.0, 0.0, 0.0];
~qpeChladniLeftPickup = [-0.55, 0.0, 0.0];
~qpeChladniRightPickup = [0.55, 0.0, 0.0];
~qpeChladniLastStatus = "waiting for QPE frame";
~qpeChladniLastFrameTime = nil;

SynthDef(\qmwQPEChladni24, {
    |out = 0, master = 0.24, gate = 1, t_strike = 0|
    var frequencies = NamedControl.kr(
        \freqs, Array.fill(~qpeChladniModeCount, 220.0)
    );
    var decays = NamedControl.kr(
        \decays, Array.fill(~qpeChladniModeCount, 1.5)
    );
    var leftGains = NamedControl.kr(
        \leftGains, Array.fill(~qpeChladniModeCount, 0.0)
    );
    var rightGains = NamedControl.kr(
        \rightGains, Array.fill(~qpeChladniModeCount, 0.0)
    );
    var trigger = Trig1.kr(t_strike, 0.001);
    var excitation = PinkNoise.ar * Decay2.kr(trigger, 0.0015, 0.035);
    var resonances = Ringz.ar(
        excitation,
        frequencies.clip(20.0, SampleRate.ir * 0.45),
        decays.clip(0.02, 12.0)
    );
    var left = Mix(resonances * Lag.kr(leftGains, 0.025));
    var right = Mix(resonances * Lag.kr(rightGains, 0.025));
    var envelope = EnvGen.kr(
        Env.asr(0.02, 1.0, 0.2), gate, doneAction: Done.freeSelf
    );
    var stereo = LeakDC.ar([left, right]);
    stereo = Limiter.ar((stereo * master).tanh, 0.92, 0.01);
    Out.ar(out, stereo * envelope);
}).add;

~qpeChladniNearestVertex = { |point|
    var bestIndex = 0;
    var bestDistance = inf;
    ~qpeChladniVertices.do { |vertex, index|
        if(vertex.notNil) {
            var dx = vertex[0] - point[0];
            var dy = vertex[1] - point[1];
            var dz = vertex[2] - point[2];
            var distance = (dx * dx) + (dy * dy) + (dz * dz);
            if(distance < bestDistance) {
                bestDistance = distance;
                bestIndex = index;
            };
        };
    };
    bestIndex
};

~qpeChladniNormalizeStereo = { |left, right|
    var energy = ((left.squared.sum + right.squared.sum).sqrt).max(0.000001);
    [left / energy, right / energy]
};

~qpeChladniApplyFrame = {
    var base;
    var left;
    var right;
    var normalized;

    if(~qpeChladniSynth.notNil and: { ~qpeChladniFrameValid }) {
        base = Array.fill(~qpeChladniModeCount, { |index|
            ~qpeChladniPosterior[index].max(0.0).sqrt
                * ~qpeChladniWeights[index].max(0.0)
        });

        if(~qpeChladniGeometryReady
            and: { ~qpeChladniGeometryModes == ~qpeChladniModeCount }) {
            var strikeIndex = ~qpeChladniNearestVertex.(~qpeChladniStrikePoint);
            var leftIndex = ~qpeChladniNearestVertex.(~qpeChladniLeftPickup);
            var rightIndex = ~qpeChladniNearestVertex.(~qpeChladniRightPickup);
            var strikeModes = ~qpeChladniEigenRows[strikeIndex];
            var leftModes = ~qpeChladniEigenRows[leftIndex];
            var rightModes = ~qpeChladniEigenRows[rightIndex];
            left = Array.fill(~qpeChladniModeCount, { |index|
                base[index] * strikeModes[index] * leftModes[index]
            });
            right = Array.fill(~qpeChladniModeCount, { |index|
                base[index] * strikeModes[index] * rightModes[index]
            });
        } {
            // Audible fallback while the geometry transaction is still arriving.
            left = Array.fill(~qpeChladniModeCount, { |index|
                base[index] * ((1.0 - ~qpeChladniPans[index]) * 0.5).sqrt
            });
            right = Array.fill(~qpeChladniModeCount, { |index|
                base[index] * ((1.0 + ~qpeChladniPans[index]) * 0.5).sqrt
            });
        };

        normalized = ~qpeChladniNormalizeStereo.(left, right);
        s.bind {
            ~qpeChladniSynth.setn(\freqs, ~qpeChladniFreqs);
            ~qpeChladniSynth.setn(\decays, ~qpeChladniDecays);
            ~qpeChladniSynth.setn(\leftGains, normalized[0]);
            ~qpeChladniSynth.setn(\rightGains, normalized[1]);
        };
    };
};

~qpeChladniUpdateStatusView = {
    {
        if(~qpeChladniStatusView.notNil) {
            ~qpeChladniStatusView.string_(~qpeChladniLastStatus)
        };
    }.defer;
};

OSCdef(\qpeChladniBegin, { |message|
    var count = message[2].asInteger;
    if(count == ~qpeChladniModeCount) {
        ~qpeChladniRevision = message[1].asInteger;
        ~qpeChladniReceived = Array.fill(count, false);
        ~qpeChladniFrameValid = false;
    } {
        ~qpeChladniLastStatus = "rejected frame: expected 24 modes, received " ++ count;
        ~qpeChladniUpdateStatusView.();
    };
}, "/qmw/chladni/begin");

OSCdef(\qpeChladniMode, { |message|
    var revision = message[1].asInteger;
    var index = message[2].asInteger;
    if((revision == ~qpeChladniRevision)
        and: { index >= 0 and: { index < ~qpeChladniModeCount } }) {
        ~qpeChladniFreqs[index] = message[3].asFloat;
        ~qpeChladniDecays[index] = message[4].asFloat;
        ~qpeChladniWeights[index] = message[5].asFloat;
        ~qpeChladniPosterior[index] = message[6].asFloat;
        ~qpeChladniPhases[index] = message[7].asFloat;
        ~qpeChladniPans[index] = message[8].asFloat.clip(-1.0, 1.0);
        ~qpeChladniReceived[index] = true;
    };
}, "/qmw/chladni/mode");

OSCdef(\qpeChladniEnd, { |message|
    if((message[1].asInteger == ~qpeChladniRevision)
        and: { ~qpeChladniReceived.every({ |received| received }) }) {
        ~qpeChladniFrameValid = true;
        ~qpeChladniLastFrameTime = Main.elapsedTime;
        ~qpeChladniApplyFrame.();
    } {
        ~qpeChladniLastStatus = "incomplete QPE modal frame";
        ~qpeChladniUpdateStatusView.();
    };
}, "/qmw/chladni/end");

OSCdef(\qpeChladniGeometryBegin, { |message|
    ~qpeChladniGeometrySamples = message[1].asInteger;
    ~qpeChladniGeometryModes = message[2].asInteger;
    ~qpeChladniGeometryReady = false;
    ~qpeChladniGeometryReceived = Array.fill(
        ~qpeChladniGeometrySamples, false
    );
    ~qpeChladniVertices = Array.newClear(~qpeChladniGeometrySamples);
    ~qpeChladniEigenRows = Array.newClear(~qpeChladniGeometrySamples);
}, "/qmw/chladni/geometry/begin");

OSCdef(\qpeChladniGeometryVertex, { |message|
    var index = message[1].asInteger;
    if(index >= 0 and: { index < ~qpeChladniGeometrySamples }) {
        if(message.size == (5 + ~qpeChladniGeometryModes)) {
            ~qpeChladniVertices[index] = [
                message[2].asFloat,
                message[3].asFloat,
                message[4].asFloat
            ];
            ~qpeChladniEigenRows[index] = Array.fill(
                ~qpeChladniGeometryModes,
                { |mode| message[5 + mode].asFloat }
            );
            ~qpeChladniGeometryReceived[index] = true;
        };
    };
}, "/qmw/chladni/geometry/vertex");

OSCdef(\qpeChladniGeometryEnd, { |message|
    if((message[1].asInteger == ~qpeChladniGeometrySamples)
        and: { ~qpeChladniGeometryReceived.every({ |received| received }) }) {
        ~qpeChladniGeometryReady = true;
        ~qpeChladniLastStatus = "eigengeometry ready: "
            ++ ~qpeChladniGeometrySamples ++ " samples x "
            ++ ~qpeChladniGeometryModes ++ " modes";
        ~qpeChladniApplyFrame.();
        ~qpeChladniUpdateStatusView.();
    } {
        ~qpeChladniLastStatus = "incomplete eigengeometry transaction";
        ~qpeChladniUpdateStatusView.();
    };
}, "/qmw/chladni/geometry/end");

OSCdef(\qpeChladniStrikeOSC, { |message|
    if(~qpeChladniSynth.notNil) {
        ~qpeChladniSynth.set(\t_strike, message[1].asFloat.clip(0.0, 1.0))
    };
}, "/qmw/chladni/strike");

OSCdef(\qpeChladniStatusOSC, { |message|
    ~qpeChladniLastStatus = message[1..].collect(_.asString).join(" ");
    ~qpeChladniUpdateStatusView.();
}, "/qmw/chladni/status");

~qpeChladniStrike = { |amplitude = 0.72|
    if(~qpeChladniSynth.notNil) {
        ~qpeChladniSynth.set(\t_strike, amplitude.asFloat.clip(0.0, 1.0))
    };
};

~qpeChladniSetQPEBits = { |bits = 5|
    var selected = bits.asInteger.clip(2, 10);
    ~qpeChladniController.sendMsg(
        "/qmw/chladni/control/qpe-bits", selected
    );
    selected
};

~qpeChladniMeasure = {
    ~qpeChladniController.sendMsg("/qmw/chladni/control/measure", 1);
};

~qpeChladniSetStrikePoint = { |x = 0.0, y = 0.0, z = 0.0|
    ~qpeChladniStrikePoint = [x, y, z].collect(_.asFloat.clip(-1.0, 1.0));
    ~qpeChladniApplyFrame.();
};

~qpeChladniSetPickupSpread = { |spread = 0.55|
    var position = spread.asFloat.clip(0.0, 1.0);
    ~qpeChladniLeftPickup = [position.neg, 0.0, 0.0];
    ~qpeChladniRightPickup = [position, 0.0, 0.0];
    ~qpeChladniApplyFrame.();
};

~qpeChladniStatus = {
    (
        languagePort: NetAddr.langPort,
        revision: ~qpeChladniRevision,
        frameValid: ~qpeChladniFrameValid,
        geometryReady: ~qpeChladniGeometryReady,
        geometrySamples: ~qpeChladniGeometrySamples,
        frameAge: if(~qpeChladniLastFrameTime.isNil) {
            nil
        } {
            Main.elapsedTime - ~qpeChladniLastFrameTime
        },
        status: ~qpeChladniLastStatus
    ).postln;
};

~qpeChladniStop = {
    [
        \qpeChladniBegin, \qpeChladniMode, \qpeChladniEnd,
        \qpeChladniGeometryBegin, \qpeChladniGeometryVertex,
        \qpeChladniGeometryEnd, \qpeChladniStrikeOSC,
        \qpeChladniStatusOSC
    ].do { |name| OSCdef(name).free };
    if(~qpeChladniSynth.notNil) {
        ~qpeChladniSynth.set(\gate, 0);
        ~qpeChladniSynth = nil;
    };
    if(~qpeChladniWindow.notNil) {
        { ~qpeChladniWindow.close }.defer;
        ~qpeChladniWindow = nil;
    };
};

s.waitForBoot {
    s.sync;
    ~qpeChladniSynth = Synth(\qmwQPEChladni24);
    ~qpeChladniController.sendMsg("/qmw/chladni/control/geometry", 1);

    {
        var window = Window("QPE x Quantum Chladni", Rect(120, 120, 640, 260));
        var strikeButton;
        var measureButton;
        var bitsBox;
        var strikeX;
        var strikeY;
        var pickupSpread;
        var master;

        ~qpeChladniWindow = window;
        StaticText(window, Rect(18, 14, 600, 24))
            .string_("FINITE-REGISTER QPE → EIGENMODE SHAPE → MODAL RESONANCE")
            .font_(Font.default.boldVariant);

        strikeButton = Button(window, Rect(18, 50, 110, 32))
            .states_([["STRIKE"]])
            .action_({ ~qpeChladniStrike.(0.72) });
        measureButton = Button(window, Rect(140, 50, 110, 32))
            .states_([["MEASURE"]])
            .action_({ ~qpeChladniMeasure.() });

        StaticText(window, Rect(270, 55, 90, 20)).string_("QPE qubits");
        bitsBox = NumberBox(window, Rect(360, 52, 52, 26))
            .value_(5)
            .action_({ |view| view.value_(~qpeChladniSetQPEBits.(view.value)) });

        StaticText(window, Rect(18, 102, 90, 20)).string_("strike X");
        strikeX = Slider(window, Rect(105, 102, 220, 20))
            .value_(0.5)
            .action_({ |view|
                ~qpeChladniSetStrikePoint.(
                    view.value.linlin(0, 1, -1, 1),
                    strikeY.value.linlin(0, 1, -1, 1), 0
                )
            });
        StaticText(window, Rect(340, 102, 90, 20)).string_("strike Y");
        strikeY = Slider(window, Rect(420, 102, 195, 20))
            .value_(0.5)
            .action_({ |view|
                ~qpeChladniSetStrikePoint.(
                    strikeX.value.linlin(0, 1, -1, 1),
                    view.value.linlin(0, 1, -1, 1), 0
                )
            });

        StaticText(window, Rect(18, 137, 90, 20)).string_("pickup spread");
        pickupSpread = Slider(window, Rect(105, 137, 220, 20))
            .value_(0.55)
            .action_({ |view| ~qpeChladniSetPickupSpread.(view.value) });
        StaticText(window, Rect(340, 137, 90, 20)).string_("master");
        master = Slider(window, Rect(420, 137, 195, 20))
            .value_(0.24)
            .action_({ |view|
                if(~qpeChladniSynth.notNil) {
                    ~qpeChladniSynth.set(\master, view.value.linlin(0, 1, 0, 0.7))
                }
            });

        ~qpeChladniStatusView = StaticText(window, Rect(18, 180, 600, 48))
            .string_(~qpeChladniLastStatus);
        window.onClose_({ ~qpeChladniWindow = nil });
        window.front;
    }.defer;

    "QPE x Chladni ready on sclang UDP port %".format(NetAddr.langPort).postln;
    "Start Python with --out-port % --control-port 7473".format(NetAddr.langPort).postln;
};
)
