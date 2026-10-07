/*
QMW Complete CPS Flow instrument for SuperCollider v1

Python/Qiskit remains the circuit, recursion, Wilson, and Scala authority.
This client receives exact frequency events and renders them without MIDI/MPE.

Run the Python host with its default --supercollider-port 57120, then evaluate
this entire file.  Controls are listed in the post window.
*/

(
s.waitForBoot {
    SynthDef(\qmwCompleteCPSVoiceV1, {
        |out = 0, freq = 220, ratio = 1, amp = 0.3, sustain = 0.2,
        pan = 0, phase = 0, strength = 0.2, role = 1, grade = 2,
        mask = 0.5, theta = 0, beta = 0|

        var attack = Select.kr(role.clip(0, 4), [0.018, 0.004, 0.012, 0.002, 0.025]);
        var release = sustain.clip(0.035, 3.0) *
            Select.kr(role.clip(0, 4), [0.55, 1.0, 1.35, 0.1, 1.7]);
        var envelope = Env.perc(attack, release, curve: -4).ar(doneAction: 2);
        var brightness = (0.12 + (grade / 4) * 0.76 + strength * 0.25).clip(0, 1);
        var harmonic = 1 + (grade * 0.5) + (mask * 1.5);
        var ratioColor = ratio.clip(1, 2).linlin(1, 2, 0, 1);
        var arrival;
        var departure;
        var phaseVoice;
        var signature;
        var signal;

        // The Python frequency is the pitch authority.  Every pitched partial
        // below is an integer multiple of that exact Scala/Wilson frequency;
        // ratio colors timbre only, so the ratio is never accidentally applied
        // twice after Python has already folded it into frequency_hz.
        arrival = Mix([
            SinOsc.ar(freq, phase, 0.62),
            SinOsc.ar(freq * 2, phase + beta, 0.10 + (ratioColor * 0.08)),
            Ringz.ar(Impulse.ar(0), (freq * [2, 3, harmonic]).clip(30, 16000),
                release, [0.10, 0.07, 0.05]).sum
        ]);

        // Departure: edge motion is noisier and less pitch-centered.
        departure = BPF.ar(
            PinkNoise.ar(0.7),
            (freq * (1 + theta.abs / pi)).clip(35, 15000),
            brightness.linexp(0, 1, 0.08, 0.42)
        ) + VarSaw.ar(freq, phase / (2pi), 0.22 + mask * 0.5, 0.24);

        // Phase gates become quadrature/phase-modulated attacks.
        phaseVoice = PMOsc.ar(
            freq,
            (freq * (1 + ratio)).clip(40, 18000),
            (beta.abs / pi * 5 + strength * 3).clip(0, 8),
            phase,
            0.55
        );

        // Circuit-commit fingerprints ring longer and expose the Pascal grade.
        signature = Splay.ar(
            SinOsc.ar(freq * [1, 2, grade + 2], phase, [0.5, 0.2, 0.22]),
            0.35
        ).sum;

        signal = Select.ar(role.clip(0, 4), [
            departure, arrival, phaseVoice, Silent.ar, signature
        ]);
        signal = LeakDC.ar(signal.tanh) * envelope * amp.clip(0, 1) * 0.34;
        Out.ar(out, Pan2.ar(signal, pan.clip(-1, 1)));
    }).add;

    s.sync;

    ~qmwControl = NetAddr("127.0.0.1", 7403);
    ~qmwBasisProbability = Array.fill(16, 0.0);
    ~qmwBasisPhase = Array.fill(16, 0.0);
    ~qmwBasisEnergy = Array.fill(16, 0.0);
    ~qmwScalaRatios = Array.fill(256, 1.0);
    ~qmwScalaCents = Array.fill(256, 0.0);
    ~qmwScalaTokens = Array.fill(256, "");
    ~qmwScalaAssignment = Array.fill(16, 0);
    ~qmwScalaCount = 0;
    ~qmwScalaPeriod = 2.0;
    ~qmwScalaDescription = "no Scala scale loaded";
    ~qmwFlow = [-1, -1, 0.0];
    ~qmwGeneration = 0;
    ~qmwTuningMode = "cps";
    ~qmwArticulation = "arrival";
    ~qmwNoteCount = 0;
    ~qmwRhoFrameCount = 0;
    ~qmwRhoSource = "state16";
    ~qmwStateRhoReal = Array.fill(256, 0.0);
    ~qmwStateRhoImag = Array.fill(256, 0.0);
    ~qmwStateRhoRealRevision = -1;
    ~qmwStateRhoImagRevision = -2;
    ~qmwQACRhoReal = Array.fill(256, 0.0);
    ~qmwQACRhoImag = Array.fill(256, 0.0);
    ~qmwQACRhoRealReady = false;
    ~qmwQACRhoImagReady = false;

    // Commit one complete row-major 16x16 complex density matrix. Population
    // comes from the real diagonal. Phase is measured against the most
    // populated reference basis through rho[basis, reference], which preserves
    // pure-state relative phase while remaining meaningful for mixed states.
    ~qmwCommitRho256 = { |real, imag, revision = 0, source = "state/rho"|
        var reference = 0;
        var peak = -1.0;
        16.do { |basis|
            var probability = real[(basis * 16) + basis].asFloat.max(0);
            if(probability > peak) {
                peak = probability;
                reference = basis;
            };
        };
        16.do { |basis|
            var index = (basis * 16) + reference;
            ~qmwBasisProbability[basis] = real[(basis * 16) + basis].asFloat.clip(0, 1);
            ~qmwBasisPhase[basis] = Complex(
                real[index].asFloat, imag[index].asFloat
            ).phase;
        };
        ~qmwGeneration = revision.asInteger;
        ~qmwRhoFrameCount = ~qmwRhoFrameCount + 1;
        ~qmwRhoSource = source;
        { if(~qmwView.notNil) { ~qmwView.refresh } }.defer;
    };

    ~qmwWindow = Window("QMW Complete CPS Flow · SuperCollider", Rect(80, 80, 1120, 720));
    ~qmwWindow.background = Color.black;
    ~qmwView = UserView(~qmwWindow, ~qmwWindow.view.bounds)
        .resize_(5)
        .background_(Color(0.025, 0.03, 0.045));

    ~qmwView.drawFunc = {
        var bounds = ~qmwView.bounds;
        var leftWidth = bounds.width * 0.42;
        var center = Point(leftWidth + ((bounds.width - leftWidth) * 0.52), bounds.height * 0.53);
        var radius = min(bounds.height * 0.32, (bounds.width - leftWidth) * 0.38);
        var periodCents = 1200 * log2(~qmwScalaPeriod.max(1.000001));
        var scalaPoints = Array.newClear(~qmwScalaCount.max(1));

        Pen.font = Font("Menlo", 12);
        Pen.color = Color.white;
        Pen.stringAtPoint("QMW COMPLETE CPS · exact-frequency SuperCollider client", Point(24, 22));
        Pen.color = Color.gray(0.68);
        Pen.stringAtPoint(
            "generation % · tuning % · articulation % · events % · rho % (%)".format(
                ~qmwGeneration, ~qmwTuningMode, ~qmwArticulation,
                ~qmwNoteCount, ~qmwRhoFrameCount, ~qmwRhoSource
            ),
            Point(24, 44)
        );

        // All sixteen basis states remain visible, including 0000 and 1111.
        16.do { |basis|
            var column = basis % 4;
            var row = (basis / 4).floor;
            var cell = Rect(25 + column * 96, 90 + row * 96, 78, 78);
            var probability = ~qmwBasisProbability[basis].clip(0, 1);
            var energy = ~qmwBasisEnergy[basis].clip(0, 1);
            var hue = ((~qmwBasisPhase[basis] / (2pi)) + 1) % 1;
            Pen.fillColor = Color.hsv(hue, 0.62, 0.22 + (0.68 * energy), 0.9);
            Pen.fillRect(cell);
            Pen.strokeColor = Color.hsv(hue, 0.35, 1, 0.45 + 0.5 * probability.sqrt);
            Pen.width = 1 + 5 * probability.sqrt;
            Pen.strokeRect(cell);
            Pen.color = Color.white;
            Pen.stringCenteredIn(basis.asBinaryDigits(4).join, cell);
        };

        Pen.color = Color.gray(0.7);
        Pen.stringAtPoint("16-state Boolean/CPS field", Point(25, 486));

        if(~qmwScalaCount > 0) {
            ~qmwScalaCount.do { |degree|
                var angle = (~qmwScalaCents[degree] / periodCents * 2pi) - (pi / 2);
                scalaPoints[degree] = center + Point(cos(angle), sin(angle)) * radius;
            };

            // Project four-dimensional one-bit adjacency onto Scala degrees.
            16.do { |basis|
                4.do { |qubit|
                    var neighbor = basis.bitXor(1 << qubit);
                    if(neighbor > basis) {
                        var a = ~qmwScalaAssignment[basis].clip(0, ~qmwScalaCount - 1);
                        var b = ~qmwScalaAssignment[neighbor].clip(0, ~qmwScalaCount - 1);
                        if(a != b) {
                            Pen.strokeColor = Color.hsv((qubit * 0.218) % 1, 0.58, 0.9, 0.12);
                            Pen.width = 1;
                            Pen.line(scalaPoints[a], scalaPoints[b]);
                            Pen.stroke;
                        };
                    };
                };
            };

            ~qmwScalaCount.do { |degree|
                var hue = (~qmwScalaCents[degree] / periodCents) % 1;
                var assignedEnergy = 0.0;
                16.do { |basis|
                    if(~qmwScalaAssignment[basis] == degree) {
                        assignedEnergy = assignedEnergy + ~qmwBasisProbability[basis]
                    };
                };
                Pen.fillColor = Color.hsv(hue, 0.68, 0.92, 0.35 + assignedEnergy.sqrt.clip(0, 1) * 0.65);
                Pen.fillOval(Rect.aboutPoint(scalaPoints[degree], 7 + assignedEnergy.sqrt * 16, 7 + assignedEnergy.sqrt * 16));
                Pen.color = Color.white;
                Pen.stringAtPoint(~qmwScalaTokens[degree], scalaPoints[degree] + Point(9, -5));
            };
        };

        Pen.color = Color.white;
        Pen.stringAtPoint("SCALA GEOMETRY · " ++ ~qmwScalaDescription, Point(leftWidth + 20, 22));
        Pen.color = Color.gray(0.65);
        Pen.stringAtPoint("hue: scale position · size: probability · chords: qubit adjacency", Point(leftWidth + 20, 44));
    };

    ~qmwWindow.onClose = { if(~qmwDecay.notNil) { ~qmwDecay.stop } };
    ~qmwWindow.front;

    ~qmwDecay = Routine {
        inf.do {
            ~qmwBasisEnergy = ~qmwBasisEnergy.collect { |value| value * 0.92 };
            { if(~qmwView.notNil) { ~qmwView.refresh } }.defer;
            0.04.wait;
        }
    }.play(AppClock);

    OSCdef(\qmwCompleteCPSNote, { |message|
        var role = message[2].asInteger;
        var basis = message[3].asInteger.clip(0, 15);
        var note = message[4].asFloat;
        var velocity = message[5].asFloat.clip(0, 127);
        var duration = message[6].asFloat.max(1) / 1000;
        var strength = message[7].asFloat.clip(0, 1);
        var theta = message[8].asFloat;
        var beta = message[9].asFloat;
        var phase = message[10].asFloat;
        var bend = message[11].asFloat;
        var ratio = if(message.size > 15) { message[15].asFloat } { 1.0 };
        var frequency = if(message.size > 16) {
            message[16].asFloat
        } {
            (note + ((bend - 8192) / 8191 * 2)).midicps
        };
        var grade = basis.asBinaryDigits(4).sum;
        var pan = basis.linlin(0, 15, -0.88, 0.88) + (phase.sin * 0.08);

        if(role == 3) {
            s.freeAll;
        } {
            if(velocity > 0) {
                Synth(\qmwCompleteCPSVoiceV1, [
                    \freq, frequency,
                    \ratio, ratio,
                    \amp, (velocity / 127).pow(1.25),
                    \sustain, duration,
                    \pan, pan,
                    \phase, phase,
                    \strength, strength,
                    \role, role,
                    \grade, grade,
                    \mask, basis / 15,
                    \theta, theta,
                    \beta, beta
                ]);
                ~qmwBasisEnergy[basis] = max(~qmwBasisEnergy[basis], velocity / 127);
                ~qmwNoteCount = ~qmwNoteCount + 1;
            };
        };
    }, '/qmw/recursive/cps_flow_note');

    OSCdef(\qmwCompleteCPSState, { |message|
        ~qmwGeneration = message[1].asInteger;
        16.do { |basis|
            ~qmwBasisProbability[basis] = message[basis + 2].asFloat;
            ~qmwBasisPhase[basis] = message[basis + 18].asFloat;
        };
        ~qmwRhoSource = "wilson/state16";
    }, '/qmw/wilson/state16');

    // Revisioned canonical live-state pair:
    // /qmw/state/rho/{real,imag} revision <256 row-major floats>
    OSCdef(\qmwCompleteCPSStateRhoReal, { |message|
        if(message.size == 258) {
            ~qmwStateRhoRealRevision = message[1].asInteger;
            ~qmwStateRhoReal = Array.fill(256, { |index| message[index + 2].asFloat });
            if(~qmwStateRhoImagRevision == ~qmwStateRhoRealRevision) {
                ~qmwCommitRho256.(~qmwStateRhoReal, ~qmwStateRhoImag,
                    ~qmwStateRhoRealRevision, "state/rho");
            };
        } {
            "QMW ignored malformed state/rho/real packet (% atoms).".format(message.size - 1).warn;
        };
    }, '/qmw/state/rho/real');

    OSCdef(\qmwCompleteCPSStateRhoImag, { |message|
        if(message.size == 258) {
            ~qmwStateRhoImagRevision = message[1].asInteger;
            ~qmwStateRhoImag = Array.fill(256, { |index| message[index + 2].asFloat });
            if(~qmwStateRhoRealRevision == ~qmwStateRhoImagRevision) {
                ~qmwCommitRho256.(~qmwStateRhoReal, ~qmwStateRhoImag,
                    ~qmwStateRhoImagRevision, "state/rho");
            };
        } {
            "QMW ignored malformed state/rho/imag packet (% atoms).".format(message.size - 1).warn;
        };
    }, '/qmw/state/rho/imag');

    // QAC compatibility pair has no revision atom.  Commit only after one
    // complete real and imaginary packet have both arrived.
    OSCdef(\qmwCompleteCPSQACRhoReal, { |message|
        if(message.size == 257) {
            ~qmwQACRhoReal = Array.fill(256, { |index| message[index + 1].asFloat });
            ~qmwQACRhoRealReady = true;
            if(~qmwQACRhoImagReady) {
                ~qmwCommitRho256.(~qmwQACRhoReal, ~qmwQACRhoImag,
                    ~qmwGeneration, "qac/rho");
                ~qmwQACRhoRealReady = false;
                ~qmwQACRhoImagReady = false;
            };
        };
    }, '/qmw/qac/rho/real');

    OSCdef(\qmwCompleteCPSQACRhoImag, { |message|
        if(message.size == 257) {
            ~qmwQACRhoImag = Array.fill(256, { |index| message[index + 1].asFloat });
            ~qmwQACRhoImagReady = true;
            if(~qmwQACRhoRealReady) {
                ~qmwCommitRho256.(~qmwQACRhoReal, ~qmwQACRhoImag,
                    ~qmwGeneration, "qac/rho");
                ~qmwQACRhoRealReady = false;
                ~qmwQACRhoImagReady = false;
            };
        };
    }, '/qmw/qac/rho/imag');

    OSCdef(\qmwCompleteCPSTuningMode, { |message|
        ~qmwGeneration = message[1].asInteger;
        ~qmwTuningMode = message[2].asString;
    }, '/qmw/wilson/tuning/mode');

    OSCdef(\qmwCompleteCPSFlow, { |message|
        ~qmwFlow = [message[2].asInteger, message[3].asInteger, message[4].asFloat];
    }, '/qmw/wilson/flow');

    OSCdef(\qmwCompleteCPSScalaBegin, { |message|
        ~qmwScalaDescription = message[3].asString;
        ~qmwScalaCount = message[4].asInteger.clip(0, 256);
        ~qmwScalaPeriod = message[5].asFloat;
    }, '/qmw/wilson/tuning/scala/begin');

    OSCdef(\qmwCompleteCPSScalaDegree, { |message|
        var degree = message[2].asInteger;
        if(degree >= 0 and: { degree < 256 }) {
            ~qmwScalaRatios[degree] = message[3].asFloat;
            ~qmwScalaCents[degree] = message[4].asFloat;
            ~qmwScalaTokens[degree] = message[5].asString;
        };
    }, '/qmw/wilson/tuning/scala/degree');

    OSCdef(\qmwCompleteCPSScalaAssignment, { |message|
        var basis = message[2].asInteger;
        if(basis >= 0 and: { basis < 16 }) {
            ~qmwScalaAssignment[basis] = message[3].asInteger;
        };
    }, '/qmw/wilson/tuning/scala/assignment');

    ~qmwNext = { ~qmwControl.sendMsg('/qmw/recursive/next', 1) };
    ~qmwStart = { ~qmwControl.sendMsg('/qmw/recursive/start', 1) };
    ~qmwStop = { ~qmwControl.sendMsg('/qmw/recursive/stop', 1) };
    ~qmwReset = { ~qmwControl.sendMsg('/qmw/recursive/reset', 1) };
    ~qmwSetArticulation = { |mode = "arrival"|
        var normalized = mode.asString.toLower;
        if(["arrival", "dyad", "gesture"].includes(normalized)) {
            ~qmwArticulation = normalized;
            ~qmwControl.sendMsg('/qmw/recursive/articulation', normalized);
        } {
            "QMW articulation must be arrival, dyad, or gesture.".warn;
        };
    };
    ~qmwTuning = { |mode = "cps"| ~qmwControl.sendMsg('/qmw/wilson/tuning/mode', mode) };
    ~qmwScalaLoad = { |path| ~qmwControl.sendMsg('/qmw/wilson/tuning/scala/load', path.asString) };
    ~qmwScalaSave = { |path| ~qmwControl.sendMsg('/qmw/wilson/tuning/scala/save', path.asString) };
    ~qmwCPSTest = {
        {
            Synth(\qmwCompleteCPSVoiceV1, [
                \freq, 220, \ratio, 3/2, \amp, 0.55, \sustain, 0.7,
                \pan, -0.25, \role, 1, \grade, 2, \mask, 0.4, \strength, 0.7
            ]);
            0.18.wait;
            Synth(\qmwCompleteCPSVoiceV1, [
                \freq, 330, \ratio, 5/4, \amp, 0.5, \sustain, 0.9,
                \pan, 0.25, \role, 2, \grade, 3, \mask, 0.75, \beta, pi/2
            ]);
        }.fork;
    };
    ~qmwCPSFree = {
        [
            \qmwCompleteCPSNote, \qmwCompleteCPSState, \qmwCompleteCPSTuningMode,
            \qmwCompleteCPSFlow, \qmwCompleteCPSScalaBegin,
            \qmwCompleteCPSScalaDegree, \qmwCompleteCPSScalaAssignment,
            \qmwCompleteCPSStateRhoReal, \qmwCompleteCPSStateRhoImag,
            \qmwCompleteCPSQACRhoReal, \qmwCompleteCPSQACRhoImag
        ].do { |name| OSCdef(name).free };
        if(~qmwDecay.notNil) { ~qmwDecay.stop };
        s.freeAll;
        "QMW Complete CPS SuperCollider client stopped.".postln;
    };

    "QMW Complete CPS SuperCollider client listening on language port %.".format(NetAddr.langPort).postln;
    "Try ~qmwCPSTest.(), ~qmwNext.(), ~qmwStart.(), ~qmwStop.(), ~qmwSetArticulation.(\"gesture\"), or ~qmwTuning.(\"scala\").".postln;
};
)
