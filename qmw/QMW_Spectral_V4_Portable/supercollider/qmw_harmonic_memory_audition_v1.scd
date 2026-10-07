/* QMW Harmonic Memory Audition V1.
   A downstream four-node listener for admitted-event HarmonicMemoryClock
   frames. It is deliberately non-recursive: it never writes to rho, event
   admission, the 16-line temporal field, or the primary pluck output. */
(
var root = "/qmw/harmonic_memory_development/v1";
var port = (~qmwHmdPort ? 17886).asInteger;
var schema = "qmw.harmonic_memory_development.osc.v1";
var nodeCount = 4;

~qmwHmdRevision = 0;
~qmwHmdStageActive = false;
~qmwHmdStageNodes = Array.fill(nodeCount, false);
~qmwHmdStageSeries = false;
~qmwHmdMix = (~qmwHmdMix ? 0.0).asFloat.clip(0, 0.5);
~qmwHmdNodes = List.new;
~qmwHmdMaxVoices = 2;
// These are local audition controls only.  They reshape copies of received
// frames for the Lab button and never alter the incoming event clock.
~qmwHmdLabMode = \follow;
~qmwHmdLabIndex = 1;
~qmwHmdLabAmounts = (write: 1.0, persistence: 1.0, topology: 1.0, instability: 1.0);
~qmwHmdLabA = nil;
~qmwHmdLabB = nil;
~qmwHmdProbeDelay = (~qmwHmdProbeDelay ? 0.55).asFloat.clip(0.020, 2.5);
~qmwHmdProbeNodes = List.new;
~qmwHmdProbeMaxVoices = 1;
~qmwHmdFrame = (
    eventIndex: 1, eventWrite: 1.0, persistence: 0.21,
    topology: 0.61, instability: 1.0,
    population: [0.25, 0.25, 0.25, 0.25],
    injection: [0.5, 0.5, 0.5, 0.5],
    nodePersistence: [0.12, 0.12, 0.12, 0.12],
    delays: [0.137, 0.171, 0.183, 0.206]
);

SynthDef(\qmwHarmonicMemoryAuditionVoiceV1, {
    |out=0, master=0.25, eventWrite=1, persistence=0.2, topology=0.6, instability=0.2|
    var injection = NamedControl.kr(\injection, Array.fill(nodeCount, 0.0));
    var nodePersistence = NamedControl.kr(\nodePersistence, Array.fill(nodeCount, 0.0));
    var delays = NamedControl.kr(\delays, [0.137, 0.171, 0.183, 0.206]);
    var sourceEnvelope, life, source, taps, sparse, diffuse, signal;
    sourceEnvelope = EnvGen.ar(Env.perc(0.002, 0.070, 1, -6));
    // The fixed life covers the declared 5.25-second maximum path plus its
    // bounded resonant tail. There is no feedback loop in this audition body.
    life = EnvGen.kr(Env.linen(0.004, 8.6, 0.12), doneAction: 2);
    source = (PinkNoise.ar(0.56) + SinOsc.ar(154, 0, 0.26)) * sourceEnvelope;
    taps = Array.fill(nodeCount, { |index|
        var signed = [-1.0, -0.35, 0.35, 1.0][index];
        var frequency = [116, 174, 232, 348][index]
            * (1 + (instability.clip(0, 1) * signed * 0.035));
        var decay = (0.16 + (nodePersistence[index].clip(0, 1) * 3.1)
            + (persistence.clip(0, 1) * 0.7)).clip(0.08, 4.0);
        Ringz.ar(
            DelayC.ar(source, 5.5, delays[index].clip(0.001, 5.25)),
            frequency.clip(40, 6000), decay
        ) * injection[index].clip(0, 1) * eventWrite.clip(0, 1)
    });
    // H_n^(2) blends distinct lanes toward a shared field. It changes the
    // temporal shape and stereo image, never the state or feedback amount.
    sparse = Mix.fill(nodeCount, { |index|
        Pan2.ar(taps[index], [-0.92, -0.31, 0.31, 0.92][index])
    });
    diffuse = Splay.ar(Array.fill(nodeCount, { |index|
        (taps.sum * 0.26) + (taps[index] * 0.34)
    }), 0.95, 0.76);
    signal = XFade2.ar(sparse, diffuse, (topology.clip(0, 1) * 2) - 1);
    Out.ar(out, Limiter.ar(LeakDC.ar(signal) * life * master.clip(0, 0.5), 0.76));
}).add;

// A timing diagnostic, separate from the resonator listener: one source
// marker is followed by four direct returns.  It does not share the main
// instrument input and has no LocalIn/LocalOut feedback path.
SynthDef(\qmwHarmonicMemoryDelayProbeV1, {
    |out=0, master=0.24|
    var delays = NamedControl.kr(\delays, [0.55, 0.6875, 0.733, 0.825]);
    var marker, life, returns, signal;
    marker = (HPF.ar(WhiteNoise.ar(0.28), 2600) + SinOsc.ar(1760, 0, 0.16))
        * EnvGen.ar(Env.perc(0.001, 0.012, 1, -7));
    life = EnvGen.kr(Env.linen(0.001, 4.15, 0.05), doneAction: 2);
    returns = Array.fill(nodeCount, { |index|
        Pan2.ar(
            DelayC.ar(marker, 5.5, delays[index].clip(0.020, 5.25)) * [0.72, 0.66, 0.60, 0.54][index],
            [-0.9, -0.3, 0.3, 0.9][index]
        )
    });
    // The centred marker is a timing ruler, not a main-voice dry path.
    signal = Pan2.ar(marker * 0.70, 0) + Mix(returns);
    Out.ar(out, Limiter.ar(LeakDC.ar(signal) * life * master.clip(0, 0.4), 0.72));
}).add;

~qmwHmdRender = { |frame, level=1.0|
    var node, oldNode;
    if(level > 0 and: { frame.notNil }) {
        if(~qmwHmdNodes.size >= ~qmwHmdMaxVoices) {
            oldNode = ~qmwHmdNodes.removeAt(0);
            if(oldNode.isRunning) { oldNode.free };
        };
        node = Synth(\qmwHarmonicMemoryAuditionVoiceV1, [
            \out, 0, \master, level.clip(0, 0.5),
            \eventWrite, frame[\eventWrite], \persistence, frame[\persistence],
            \topology, frame[\topology], \instability, frame[\instability],
            \injection, frame[\injection], \nodePersistence, frame[\nodePersistence],
            \delays, frame[\delays]
        ], s.defaultGroup, \addToTail);
        node.register;
        ~qmwHmdNodes.add(node);
        node.onFree({ ~qmwHmdNodes.remove(node) });
    };
};

~qmwHmdSetMix = { |value|
    ~qmwHmdMix = value.asFloat.clip(0, 0.5);
};
~qmwHmdAudition = {
    ~qmwHmdRender.value(~qmwHmdFrame, 0.28);
};

// This mirrors the bounded descriptors in harmonic_memory_series().  The
// finite index is a listening reference, not an event-clock writeback.
~qmwHmdLabSeriesAt = { |requestedIndex|
    var n = requestedIndex.asInteger.clip(1, 64);
    var harmonic = (1..n).collect { |index| 1.0 / index }.sum;
    var harmonic2 = (1..n).collect { |index| 1.0 / (index * index) }.sum;
    var residual = harmonic - n.asFloat.log - 0.5772156649;
    (
        eventIndex: n,
        eventWrite: 1.0 / n,
        persistence: (0.84 * (harmonic / 4.0).tanh).clip(0, 1),
        topology: (harmonic2 / (pi.squared / 6.0)).clip(0, 1),
        instability: (residual.abs / (1.0 - 0.5772156649)).clip(0, 1)
    )
};

~qmwHmdLabFrameFor = { |requestedIndex|
    var source = ~qmwHmdFrame.copy;
    var series = ~qmwHmdLabSeriesAt.value(requestedIndex);
    var population = source[\population];
    var baseDelay, residualShape = [-1.0, -1.0 / 3.0, 1.0 / 3.0, 1.0];
    var ratios = [1.0, 5.0 / 4.0, 4.0 / 3.0, 3.0 / 2.0];
    // Recover the incoming base from node zero, then apply the selected
    // clock's deterministic epsilon shape.  No random timing is introduced.
    baseDelay = (source[\delays][0] / (1.0 - (0.04 * source[\instability]))).clip(0.020, 2.5);
    source[\eventIndex] = series[\eventIndex];
    source[\eventWrite] = series[\eventWrite];
    source[\persistence] = series[\persistence];
    source[\topology] = series[\topology];
    source[\instability] = series[\instability];
    // The Lab keeps the received four-node distribution at unity write gain;
    // the voice applies 1/n once.  This makes n=16 and n=64 audible enough
    // to compare their persistence/topology instead of squaring their fade.
    source[\injection] = population.collect { |value| value.sqrt };
    source[\nodePersistence] = population.collect { |value|
        series[\persistence] * (0.25 + (0.75 * value))
    };
    source[\delays] = Array.fill(nodeCount, { |index|
        baseDelay * ratios[index] * (1.0 + (0.04 * series[\instability] * residualShape[index]))
    });
    source
};

~qmwHmdLabApplyAmounts = { |source|
    var frame = source.copy;
    var amounts = ~qmwHmdLabAmounts;
    frame[\eventWrite] = frame[\eventWrite] * amounts[\write];
    frame[\persistence] = frame[\persistence] * amounts[\persistence];
    frame[\nodePersistence] = frame[\nodePersistence].collect { |value| value * amounts[\persistence] };
    frame[\topology] = frame[\topology] * amounts[\topology];
    frame[\instability] = frame[\instability] * amounts[\instability];
    frame
};

~qmwHmdLabCurrentFrame = {
    var source = if(~qmwHmdLabMode == \follow, {
        ~qmwHmdFrame.copy
    }, {
        ~qmwHmdLabFrameFor.value(~qmwHmdLabIndex)
    });
    ~qmwHmdLabApplyAmounts.value(source)
};

~qmwHmdLabAudition = { |frame|
    // The lab is effect-only and has a fixed output level, so A/B comparisons
    // do not accidentally inherit the live memory mix or the primary voices.
    ~qmwHmdRender.value((frame ? ~qmwHmdLabCurrentFrame.value), 0.28);
};

~qmwHmdDelayProbe = { |baseDelay|
    var base = (baseDelay ? ~qmwHmdProbeDelay).asFloat.clip(0.020, 2.5);
    var node, oldNode, delays = base * [1.0, 5.0 / 4.0, 4.0 / 3.0, 3.0 / 2.0];
    if(~qmwHmdProbeNodes.size >= ~qmwHmdProbeMaxVoices) {
        oldNode = ~qmwHmdProbeNodes.removeAt(0);
        if(oldNode.isRunning) { oldNode.free };
    };
    node = Synth(\qmwHarmonicMemoryDelayProbeV1, [
        \out, 0, \master, 0.24, \delays, delays
    ], s.defaultGroup, \addToTail);
    node.register;
    ~qmwHmdProbeNodes.add(node);
    node.onFree({ ~qmwHmdProbeNodes.remove(node) });
};

~qmwHmdOpenPanel = {
    var refresh, setClock, makeClockButton, addAmount;
    if(~qmwHmdWindow.notNil, { ~qmwHmdWindow.front }, {
        ~qmwHmdWindow = Window("QMW Harmonic Memory Audition + Lab", Rect(240, 60, 660, 570))
            .front.background_(Color.fromHexString("11151c"));
        StaticText(~qmwHmdWindow, Rect(16, 14, 628, 24))
            .string_("HARMONIC MEMORY AUDITION  /  ADMITTED EVENT CLOCK")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(Color.fromHexString("dcecff"));
        StaticText(~qmwHmdWindow, Rect(16, 42, 628, 32))
            .string_("Four delayed resonator lanes only. The Lab is a local, fixed-level listening reference: no feedback, no state mutation.")
            .stringColor_(Color.white.alpha_(0.78));
        EZSlider(~qmwHmdWindow, Rect(16, 84, 628, 28), "audition mix",
            ControlSpec(0, 0.5, \lin, 0.001), { |view| ~qmwHmdSetMix.value(view.value) },
            ~qmwHmdMix, labelWidth: 92, numberWidth: 58);
        Button(~qmwHmdWindow, Rect(16, 124, 300, 38))
            .states_([["AUDITION FOUR-NODE MEMORY / no dry voice", Color.white, Color.fromHexString("264653")]])
            .action_({ ~qmwHmdAudition.value });
        StaticText(~qmwHmdWindow, Rect(16, 174, 628, 18))
            .string_("HARMONIC MEMORY LAB  /  fixed output level  /  source distributions held from the latest received frame")
            .font_(Font("Helvetica Neue", 10, true)).stringColor_(Color.fromHexString("f4a261"));
        setClock = { |mode, index|
            ~qmwHmdLabMode = mode;
            ~qmwHmdLabIndex = index;
            ~qmwHmdRefresh !? { |update| update.value };
        };
        makeClockButton = { |rect, label, mode, index|
            Button(~qmwHmdWindow, rect)
                .states_([[label, Color.white, Color.fromHexString("5b3b5b")]])
                .action_({ setClock.value(mode, index) });
        };
        makeClockButton.value(Rect(16, 198, 116, 28), "FOLLOW LIVE", \follow, 1);
        makeClockButton.value(Rect(140, 198, 70, 28), "n = 1", \fixed, 1);
        makeClockButton.value(Rect(218, 198, 70, 28), "n = 4", \fixed, 4);
        makeClockButton.value(Rect(296, 198, 70, 28), "n = 16", \fixed, 16);
        makeClockButton.value(Rect(374, 198, 70, 28), "n = 64", \fixed, 64);
        Button(~qmwHmdWindow, Rect(456, 198, 188, 28))
            .states_([["PLAY LAB FRAME / no dry voice", Color.white, Color.fromHexString("7b4f27")]])
            .action_({ ~qmwHmdLabAudition.value });
        addAmount = { |top, key, label|
            EZSlider(~qmwHmdWindow, Rect(16, top, 628, 25), label,
                ControlSpec(0, 1, \lin, 0.001), { |view|
                    ~qmwHmdLabAmounts[key] = view.value;
                    ~qmwHmdRefresh !? { |update| update.value };
                }, ~qmwHmdLabAmounts[key], labelWidth: 118, numberWidth: 58);
        };
        addAmount.value(236, \write, "write 1/n amount");
        addAmount.value(265, \persistence, "persistence H_n");
        addAmount.value(294, \topology, "topology H_n^(2)");
        addAmount.value(323, \instability, "settling epsilon_n");
        StaticText(~qmwHmdWindow, Rect(16, 354, 628, 16))
            .string_("DELAY PROBE  /  centre marker + four direct delayed returns  /  no main-voice signal, no feedback")
            .font_(Font("Helvetica Neue", 10, true)).stringColor_(Color.fromHexString("f4a261"));
        EZSlider(~qmwHmdWindow, Rect(16, 374, 408, 25), "probe base delay",
            ControlSpec(0.020, 2.5, \lin, 0.001), { |view| ~qmwHmdProbeDelay = view.value },
            ~qmwHmdProbeDelay, labelWidth: 118, numberWidth: 58);
        Button(~qmwHmdWindow, Rect(432, 374, 212, 25))
            .states_([["AUDITION DELAY GEOMETRY", Color.white, Color.fromHexString("7b4f27")]])
            .action_({ ~qmwHmdDelayProbe.value });
        Button(~qmwHmdWindow, Rect(16, 414, 150, 28))
            .states_([["CAPTURE A", Color.white, Color.fromHexString("355070")]])
            .action_({ ~qmwHmdLabA = ~qmwHmdLabCurrentFrame.value; ~qmwHmdRefresh.value });
        Button(~qmwHmdWindow, Rect(174, 414, 150, 28))
            .states_([["PLAY A", Color.white, Color.fromHexString("355070")]])
            .action_({ ~qmwHmdLabA !? { |frame| ~qmwHmdLabAudition.value(frame) } });
        Button(~qmwHmdWindow, Rect(332, 414, 150, 28))
            .states_([["CAPTURE B", Color.white, Color.fromHexString("355070")]])
            .action_({ ~qmwHmdLabB = ~qmwHmdLabCurrentFrame.value; ~qmwHmdRefresh.value });
        Button(~qmwHmdWindow, Rect(490, 414, 154, 28))
            .states_([["PLAY B", Color.white, Color.fromHexString("355070")]])
            .action_({ ~qmwHmdLabB !? { |frame| ~qmwHmdLabAudition.value(frame) } });
        refresh = StaticText(~qmwHmdWindow, Rect(16, 456, 628, 82))
            .stringColor_(Color.fromHexString("8ecae6"));
        ~qmwHmdRefresh = {
            var lab = ~qmwHmdLabCurrentFrame.value;
            refresh.string_(("live event n: %  |  lab: %  |  A: %  B: %\n"
                ++ "lab write: %  persistence: %  topology: %  epsilon: %\n"
                ++ "selected frame -> write: %  H_n: %  H_n^(2): %  epsilon: %").format(
                    ~qmwHmdFrame[\eventIndex],
                    if(~qmwHmdLabMode == \follow, { "follow" }, { "n = " ++ ~qmwHmdLabIndex }),
                    if(~qmwHmdLabA.isNil, { "empty" }, { "ready" }), if(~qmwHmdLabB.isNil, { "empty" }, { "ready" }),
                    ~qmwHmdLabAmounts[\write].round(0.001), ~qmwHmdLabAmounts[\persistence].round(0.001),
                    ~qmwHmdLabAmounts[\topology].round(0.001), ~qmwHmdLabAmounts[\instability].round(0.001),
                    lab[\eventWrite].round(0.001), lab[\persistence].round(0.001),
                    lab[\topology].round(0.001), lab[\instability].round(0.001)
                ));
        };
        ~qmwHmdRefresh.value;
        ~qmwHmdWindow.onClose = { ~qmwHmdWindow = nil; ~qmwHmdRefresh = nil };
    });
};

OSCdef(\qmwHmdBegin, { |message|
    var revision = message[1].asInteger;
    if(message.size >= 6 and: { message[4].asString == schema }
        and: { revision > ~qmwHmdRevision }) {
        ~qmwHmdStageRevision = revision;
        ~qmwHmdStageActive = true;
        ~qmwHmdStageNodes = Array.fill(nodeCount, false);
        ~qmwHmdStageSeries = false;
        ~qmwHmdStageFrame = (
            eventIndex: message[5].asInteger, eventWrite: 0.0, persistence: 0.0,
            topology: 0.0, instability: 0.0,
            population: Array.fill(nodeCount, 0.0), injection: Array.fill(nodeCount, 0.0),
            nodePersistence: Array.fill(nodeCount, 0.0), delays: Array.fill(nodeCount, 0.137)
        );
    };
}, root ++ "/frame/begin", recvPort: port);

OSCdef(\qmwHmdSeries, { |message|
    if(~qmwHmdStageActive and: { message[1].asInteger == ~qmwHmdStageRevision }
        and: { message.size >= 13 }) {
        ~qmwHmdStageFrame[\eventWrite] = message[7].asFloat.clip(0, 1);
        ~qmwHmdStageFrame[\persistence] = message[8].asFloat.clip(0, 1);
        ~qmwHmdStageFrame[\topology] = message[9].asFloat.clip(0, 1);
        ~qmwHmdStageFrame[\instability] = message[11].asFloat.clip(0, 1);
        ~qmwHmdStageSeries = true;
    };
}, root ++ "/series", recvPort: port);

OSCdef(\qmwHmdNode, { |message|
    var index = message[2].asInteger;
    if(~qmwHmdStageActive and: { message[1].asInteger == ~qmwHmdStageRevision }
        and: { index >= 0 and: { index < nodeCount } }) {
        ~qmwHmdStageFrame[\population][index] = message[3].asFloat.clip(0, 1);
        ~qmwHmdStageFrame[\injection][index] = message[4].asFloat.clip(0, 1);
        ~qmwHmdStageFrame[\nodePersistence][index] = message[5].asFloat.clip(0, 1);
        ~qmwHmdStageFrame[\delays][index] = message[6].asFloat.clip(0.001, 5.25);
        ~qmwHmdStageNodes[index] = true;
    };
}, root ++ "/node", recvPort: port);

OSCdef(\qmwHmdEnd, { |message|
    if(~qmwHmdStageActive and: { message[1].asInteger == ~qmwHmdStageRevision }
        and: { ~qmwHmdStageSeries } and: { ~qmwHmdStageNodes.every { |received| received } }) {
        ~qmwHmdRevision = ~qmwHmdStageRevision;
        ~qmwHmdFrame = ~qmwHmdStageFrame;
        ~qmwHmdRefresh !? { |refresh| { refresh.value }.defer };
        if(~qmwHmdMix > 0) { ~qmwHmdRender.value(~qmwHmdFrame, ~qmwHmdMix) };
    };
    ~qmwHmdStageActive = false;
}, root ++ "/frame/end", recvPort: port);

"QMW Harmonic Memory Audition V1 ready on UDP % (mix defaults to silent)".format(port).postln;
)
