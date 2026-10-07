/* QMW Temporal-Memory V1: a downstream, read-only fractional-delay adapter.
   Evaluate after booting the local server. It receives complete transactions
   on UDP 17884 and never sends state-changing controls back to Python. */
(
var lineCount = 16;
var root = "/qmw/temporal_memory/v1";
var port = (~qmwTemporalMemoryPort ? 17884).asInteger;
var controlPort = ("QMW_TEMPORAL_MEMORY_CONTROL_PORT".getenv ? "0").asInteger;
var schema = "qmw.temporal_memory.osc.v1";

~qmwTemporalMemoryRevision = -1;
~qmwTemporalMemoryStageRevision = -1;
~qmwTemporalMemoryStageActive = false;
~qmwTemporalMemoryStageLines = Array.fill(lineCount, false);
~qmwTemporalMemoryDelay = Array.fill(lineCount, 0.137);
// A non-sounding fallback map lets an explicitly sent pluck be heard
// immediately, even before the first complete observer transaction arrives.
// observerBed remains zero, so this never becomes an autonomous oscillator.
~qmwTemporalMemoryExcitation = Array.fill(lineCount, 0.78);
~qmwTemporalMemoryPersistence = Array.fill(lineCount, 0.0);
~qmwTemporalMemoryWeight = Array.fill(lineCount, 1 / lineCount);
~qmwTemporalMemoryCross = Array.fill(lineCount * lineCount, 0.0);
~qmwTemporalMemorySynth = nil;
// Created after the live strike group, so incoming event writes always occur
// before this return processor reads its input bus in the same server block.
~qmwTemporalMemoryGroup = nil;
~qmwTemporalMemoryInputBus !? _.free;
~qmwTemporalMemoryInputBus = Bus.audio(s, 2);
~qmwTemporalMemoryMix = (~qmwTemporalMemoryMix ? 0.18).asFloat.clip(0, 0.5);
~qmwTemporalMemoryFuzzSend = (~qmwTemporalMemoryFuzzSend ? 0.0).asFloat.clip(0, 1);
// This is the audible recurrence gain.  It is separate from the downstream
// observer's cross-line matrix amount below, so a performer can hear a clear
// repeat even when the current observer frame has no cross coupling.
~qmwTemporalMemorySelfFeedback = (~qmwTemporalMemorySelfFeedback ? 0.62)
    .asFloat.clip(0, 0.92);
// 0 = full sixteen-line memory lattice; 1 = foreground one-tap echo.
~qmwTemporalMemoryTapFocus = (~qmwTemporalMemoryTapFocus ? 0.0).asFloat.clip(0, 1);
// This display-side value is sent to Python's downstream control owner.  The
// next atomic observer frame carries the new per-line DelayC values back here.
~qmwTemporalMemoryBaseDelaySeconds = (~qmwTemporalMemoryBaseDelaySeconds ? 0.137)
    .asFloat.clip(0.020, 2.500);
~qmwTemporalMemoryControlPort = controlPort;
~qmwTemporalMemoryControlAddress = if(controlPort > 0, {
    NetAddr("127.0.0.1", controlPort)
}, { nil });
~qmwTemporalMemoryRatioPreset = ~qmwTemporalMemoryRatioPreset ? "rational";
~qmwTemporalMemoryPhaseWarp = (~qmwTemporalMemoryPhaseWarp ? 0.23).asFloat.clip(0, 0.40);
~qmwTemporalMemoryFeedbackAmount = (~qmwTemporalMemoryFeedbackAmount ? 0.42).asFloat.clip(0, 0.42);
~qmwTemporalMemoryDiffusion = (~qmwTemporalMemoryDiffusion ? 0.0).asFloat.clip(0, 1);
~qmwTemporalMemoryFeedbackTone = (~qmwTemporalMemoryFeedbackTone ? 6200).asFloat.clip(700, 12000);
~qmwTemporalMemoryWidth = (~qmwTemporalMemoryWidth ? 0.7).asFloat.clip(0, 1);
~qmwTemporalMemoryGlideSeconds = (~qmwTemporalMemoryGlideSeconds ? 0.16).asFloat.clip(0.005, 0.5);
~qmwTemporalMemoryFrozen = ~qmwTemporalMemoryFrozen ? false;
// No autonomous bed at startup: the delay is heard only from an admitted
// channel send or the explicit audition button.
~qmwTemporalMemoryObserverBed = (~qmwTemporalMemoryObserverBed ? 0.0).asFloat.clip(0, 1);

SynthDef(\qmwTemporalMemoryObserverV1, {
    |out=0, gate=1, master=0.18, fuzzSend=0, fuzzDrive=8, fuzzBias=0.12, fuzzTone=5200,
    feedbackTone=6200, width=0.7, glideSeconds=0.16, inBus=0, observerBed=0.18,
    selfFeedback=0.62, tapFocus=0|
    var excitation = NamedControl.kr(\excitation, Array.fill(lineCount, 0.0));
    var persistence = NamedControl.kr(\persistence, Array.fill(lineCount, 0.0));
    var weights = NamedControl.kr(\weights, Array.fill(lineCount, 0.0));
    var delays = NamedControl.kr(\delays, Array.fill(lineCount, 0.137));
    var cross = NamedControl.kr(\cross, Array.fill(lineCount * lineCount, 0.0));
    var feedback, delayedFeedback, drives, returns, signal, envelope, fuzzTemporal, glide, feedbackToneLag, feedbackGain, focus, masterGain;
    var externalInput, inputTaps;
    var latticeSignal, foregroundTap;
    glide = Lag.kr(glideSeconds.clip(0.005, 0.5), 0.03);
    feedbackToneLag = Lag.kr(feedbackTone.clip(700, 12000), 0.03);
    // The exposed feedback range is intentionally sub-unity. A long repeat is
    // still available at 0.92, while short transient voices cannot become a
    // stream of limiter clicks at the edge of a recursive loop.
    feedbackGain = LagUD.kr(selfFeedback.clip(0, 0.92), 0.10, 0.28);
    focus = Lag.kr(tapFocus.clip(0, 1), 0.08);
    masterGain = LagUD.kr(master.clip(0, 0.5), 0.06, 0.12);
    excitation = Lag.kr(excitation, glide);
    persistence = Lag.kr(persistence, glide);
    weights = Lag.kr(weights, glide);
    delays = Lag.kr(delays, glide);
    cross = Lag.kr(cross, glide);
    // This is the actual pluck-layer return: every incoming hit crosses its
    // own declared DelayC before it enters the memory recurrence. The synth is
    // deliberately placed after the strike group, so In.ar reads this block's
    // summed sends rather than a stale or unordered feedback-bus value.
    externalInput = LeakDC.ar(Mix(In.ar(inBus, 2)));
    // Full sends from several independent event voices can sum well above
    // unity. Smoothly bound that sum *before* it reaches any delay buffer;
    // tanh avoids the discontinuities and digital ticks of hard clipping.
    externalInput = (externalInput * 0.38).tanh * 0.90;
    inputTaps = Array.fill(lineCount, { |index|
        DelayC.ar(externalInput, 5.5, delays[index].clip(0.001, 5.25))
            * weights[index].sqrt * (0.20 + (excitation[index].clip(0, 1) * 0.80))
    });
    fuzzTemporal = { |source, send|
        var amount = Lag.kr(send.clip(0, 1), 0.03);
        var drive = Lag.kr(fuzzDrive.clip(1, 40), 0.03);
        var bias = Lag.kr(fuzzBias.clip(-0.45, 0.45), 0.03);
        var firstStage = ((HPF.ar(source, 24) * drive) + bias).tanh;
        var secondStage = ((firstStage * (1.6 + (drive.sqrt * 0.32)))
            + (bias * 0.55)).tanh;
        var fuzzed = LPF.ar(
            LeakDC.ar(secondStage.clip(-0.72 + (bias * 0.12), 0.50 + (bias * 0.12))),
            fuzzTone.clip(800, 12000)
        ) * 0.92;
        XFade2.ar(source, fuzzed, (amount * 2) - 1)
    };
    // LocalIn/LocalOut make the matrix a genuine delayed recurrence.  Every
    // path crosses DelayC, so no instantaneous algebraic feedback loop exists.
    feedback = LocalIn.ar(lineCount);
    // Propagation belongs to a source path, not to every source/destination
    // pair. Reusing these 16 delayed paths preserves C_ij * D_j while avoiding
    // 256 independent long DelayC buffers in the 16 x 16 scatter matrix.
    delayedFeedback = Array.fill(lineCount, { |source|
        LPF.ar(
            DelayC.ar(feedback[source], 5.5, delays[source].clip(0.001, 5.25)),
            feedbackToneLag
        )
    });
    drives = Array.fill(lineCount, { |index|
        var frequency = 55 * ((index + 1) ** 0.58);
        SinOsc.ar(frequency, 0,
            excitation[index].clip(0, 1) * weights[index].sqrt * observerBed.clip(0, 1)
        ) + inputTaps[index]
    });
    returns = Array.fill(lineCount, { |destination|
        var coupled = Mix.fill(lineCount, { |source|
            var amount = cross[(destination * lineCount) + source].clip(0, 0.42);
            delayedFeedback[source] * amount
        });
        var selfReturn = LeakDC.ar((delayedFeedback[destination] * feedbackGain).tanh) * 0.86;
        var crossReturn = LeakDC.ar(coupled) * persistence[destination].clip(0, 0.96);
        // Bound the complete state, not merely one feedback branch. This is a
        // continuous soft limiter before LocalOut, preserving tail character
        // while preventing summed return spikes from becoming digital clicks.
        LeakDC.ar(((drives[destination] + selfReturn + crossReturn) * 0.78).tanh) * 0.88
    });
    LocalOut.ar(returns);
    latticeSignal = Splay.ar(returns, Lag.kr(width.clip(0, 1), 0.03), 0.55);
    // The first memory line contains the same delayed/recurrent signal as
    // the lattice, but foregrounds one countable echo for performance use.
    foregroundTap = Pan2.ar(returns[0], 0, 0.92);
    signal = XFade2.ar(latticeSignal, foregroundTap, (focus * 2) - 1);
    envelope = EnvGen.kr(Env.asr(0.02, 1, 0.2), gate, doneAction: 2);
    Out.ar(out, Limiter.ar(fuzzTemporal.(signal, fuzzSend) * masterGain * envelope, 0.85));
}).add;

~qmwTemporalMemoryApply = {
    ~qmwTemporalMemorySynth !? { |synth|
        synth.setn(\excitation, ~qmwTemporalMemoryExcitation);
        synth.setn(\persistence, ~qmwTemporalMemoryPersistence);
        synth.setn(\weights, ~qmwTemporalMemoryWeight);
        synth.setn(\delays, ~qmwTemporalMemoryDelay);
        synth.setn(\cross, ~qmwTemporalMemoryCross);
    };
};

~qmwTemporalMemoryStart = { |out=0|
    if(s.serverRunning.not, {
        "QMW Temporal Memory: waiting for the live audio graph.".postln;
    }, {
        // QRM owns the strike group. Appending an effects group after it gives
        // this observer a deterministic, audible source-to-return ordering.
        ~qmwTemporalMemorySynth !? _.free;
        ~qmwTemporalMemoryGroup !? _.free;
        s.bind({
            ~qmwTemporalMemoryGroup = Group.after(~qrmStrikeGroup ? s.defaultGroup);
            ~qmwTemporalMemorySynth = Synth.tail(~qmwTemporalMemoryGroup,
                \qmwTemporalMemoryObserverV1, [
                    \out, out, \master, ~qmwTemporalMemoryMix,
                    \fuzzSend, ~qmwTemporalMemoryFuzzSend,
                    \fuzzDrive, ~qrmFuzzDrive ? 8, \fuzzBias, ~qrmFuzzBias ? 0.12,
                    \fuzzTone, ~qrmFuzzTone ? 5200,
                    \feedbackTone, ~qmwTemporalMemoryFeedbackTone,
                    \width, ~qmwTemporalMemoryWidth,
                    \glideSeconds, ~qmwTemporalMemoryGlideSeconds,
                    \selfFeedback, ~qmwTemporalMemorySelfFeedback,
                    \tapFocus, ~qmwTemporalMemoryTapFocus,
                    \inBus, ~qmwTemporalMemoryInputBus.index,
                    \observerBed, ~qmwTemporalMemoryObserverBed
                ]
            );
        });
        ~qmwTemporalMemoryApply.value;
        "QMW Temporal Memory return is live after the strike group.".postln;
    });
};
~qmwTemporalMemoryStop = { ~qmwTemporalMemorySynth !? _.set(\gate, 0); };
~qmwTemporalMemorySetMixer = { |mix, fuzzSend|
    ~qmwTemporalMemoryMix = mix.asFloat.clip(0, 0.5);
    ~qmwTemporalMemoryFuzzSend = fuzzSend.asFloat.clip(0, 1);
    ~qmwTemporalMemorySynth !? { |synth|
        synth.set(\master, ~qmwTemporalMemoryMix, \fuzzSend, ~qmwTemporalMemoryFuzzSend)
    };
};
~qmwTemporalMemorySetSelfFeedback = { |amount|
    ~qmwTemporalMemorySelfFeedback = amount.asFloat.clip(0, 0.92);
    ~qmwTemporalMemorySynth !? { |synth|
        synth.set(\selfFeedback, ~qmwTemporalMemorySelfFeedback)
    };
};
~qmwTemporalMemorySetTapFocus = { |amount|
    ~qmwTemporalMemoryTapFocus = amount.asFloat.clip(0, 1);
    ~qmwTemporalMemorySynth !? { |synth|
        synth.set(\tapFocus, ~qmwTemporalMemoryTapFocus)
    };
};
~qmwTemporalMemorySetBaseDelaySeconds = { |seconds|
    var prior = ~qmwTemporalMemoryBaseDelaySeconds.max(0.020);
    var next = seconds.asFloat.clip(0.020, 2.500);
    // Retune the live DelayC lines immediately. Python receives the same
    // value for subsequent observer frames, so the audible change is both
    // instant and persistent rather than waiting for a future transaction.
    ~qmwTemporalMemoryDelay = ~qmwTemporalMemoryDelay.collect { |delay|
        (delay * (next / prior)).clip(0.001, 5.25)
    };
    ~qmwTemporalMemoryBaseDelaySeconds = next;
    ~qmwTemporalMemorySynth !? { |synth|
        synth.setn(\delays, ~qmwTemporalMemoryDelay)
    };
};
~qmwTemporalMemorySetFeedbackTone = { |hertz|
    ~qmwTemporalMemoryFeedbackTone = hertz.asFloat.clip(700, 12000);
    ~qmwTemporalMemorySynth !? { |synth| synth.set(\feedbackTone, ~qmwTemporalMemoryFeedbackTone) };
};
~qmwTemporalMemorySetWidth = { |amount|
    ~qmwTemporalMemoryWidth = amount.asFloat.clip(0, 1);
    ~qmwTemporalMemorySynth !? { |synth| synth.set(\width, ~qmwTemporalMemoryWidth) };
};
~qmwTemporalMemorySetGlideSeconds = { |seconds|
    ~qmwTemporalMemoryGlideSeconds = seconds.asFloat.clip(0.005, 0.5);
    ~qmwTemporalMemorySynth !? { |synth| synth.set(\glideSeconds, ~qmwTemporalMemoryGlideSeconds) };
};
~qmwTemporalMemorySetFreeze = { |freeze=false|
    ~qmwTemporalMemoryFrozen = if(freeze == true, { true }, { freeze.asInteger > 0 });
};
~qmwTemporalMemorySetObserverBed = { |amount|
    ~qmwTemporalMemoryObserverBed = amount.asFloat.clip(0, 1);
    ~qmwTemporalMemorySynth !? { |synth| synth.set(\observerBed, ~qmwTemporalMemoryObserverBed) };
};
SynthDef(\qmwTemporalMemoryInputAuditionV1, { |out=0|
    var envelope = EnvGen.ar(Env.perc(0.004, 0.38, 1, -5), doneAction: 2);
    var source = (PinkNoise.ar(0.75) + (SinOsc.ar(164, 0, 0.42))) * envelope;
    Out.ar(out, Pan2.ar(source, SinOsc.kr(0.31) * 0.45));
}).add;
~qmwTemporalMemoryAuditionReturn = {
    ~qmwTemporalMemoryInputBus !? { |bus|
        // Keep the proof impulse before the return group as well. This is the
        // same source ordering used by real QRI event voices.
        Synth(\qmwTemporalMemoryInputAuditionV1, [\out, bus.index],
            ~qrmStrikeGroup ? s.defaultGroup, \addToTail)
    };
};
~qmwTemporalMemoryPushFuzz = {
    ~qmwTemporalMemorySynth !? { |synth|
        synth.set(\fuzzDrive, ~qrmFuzzDrive ? 8, \fuzzBias, ~qrmFuzzBias ? 0.12,
            \fuzzTone, ~qrmFuzzTone ? 5200)
    };
};
~qmwTemporalMemoryTest = {
    ~qmwTemporalMemoryDelay = Array.series(lineCount, 0.081, 0.013);
    ~qmwTemporalMemoryWeight = Array.fill(lineCount, { |index| 1 / (index + 1) }).normalizeSum;
    ~qmwTemporalMemoryExcitation = Array.fill(lineCount, { |index| if(index % 3 == 0, 0.85, 0.25) });
    ~qmwTemporalMemoryPersistence = Array.fill(lineCount, 0.45);
    ~qmwTemporalMemoryCross = Array.fill(lineCount * lineCount, { |index|
        var row = (index / lineCount).floor; var column = index % lineCount;
        if(row == column, 0, if(column == ((row + 1) % lineCount), 0.12, 0))
    });
    ~qmwTemporalMemoryStart.value;
};

OSCdef(\qmwTemporalMemoryBegin, { |message|
    var revision = message[1].asInteger;
    if((message.size >= 5) and: { message[3].asString == schema }
        and: { message[4].asInteger == lineCount } and: { revision > ~qmwTemporalMemoryRevision }) {
        ~qmwTemporalMemoryStageRevision = revision;
        ~qmwTemporalMemoryStageActive = true;
        ~qmwTemporalMemoryStageLines = Array.fill(lineCount, false);
        ~qmwTemporalMemoryStageDelay = Array.fill(lineCount, 0.137);
        ~qmwTemporalMemoryStageExcitation = Array.fill(lineCount, 0.0);
        ~qmwTemporalMemoryStagePersistence = Array.fill(lineCount, 0.0);
        ~qmwTemporalMemoryStageWeight = Array.fill(lineCount, 0.0);
        ~qmwTemporalMemoryStageCross = Array.fill(lineCount * lineCount, 0.0);
    }
}, root ++ "/frame/begin", recvPort: port);

OSCdef(\qmwTemporalMemoryLine, { |message|
    var index = message[2].asInteger;
    if(~qmwTemporalMemoryStageActive and: { message[1].asInteger == ~qmwTemporalMemoryStageRevision } and: { index >= 0 and: { index < lineCount } }) {
        ~qmwTemporalMemoryStageWeight[index] = message[3].asFloat;
        ~qmwTemporalMemoryStageDelay[index] = message[4].asFloat;
        ~qmwTemporalMemoryStageExcitation[index] = message[5].asFloat;
        ~qmwTemporalMemoryStagePersistence[index] = message[6].asFloat;
        ~qmwTemporalMemoryStageLines[index] = true;
    }
}, root ++ "/line", recvPort: port);

OSCdef(\qmwTemporalMemoryCross, { |message|
    var destination = message[2].asInteger; var source = message[3].asInteger;
    if(~qmwTemporalMemoryStageActive and: { message[1].asInteger == ~qmwTemporalMemoryStageRevision } and: { destination >= 0 and: { destination < lineCount } } and: { source >= 0 and: { source < lineCount } }) {
        ~qmwTemporalMemoryStageCross[(destination * lineCount) + source] = message[4].asFloat.clip(0, 0.42);
    }
}, root ++ "/cross", recvPort: port);

OSCdef(\qmwTemporalMemoryEnd, { |message|
    if(~qmwTemporalMemoryStageActive and: { message[1].asInteger == ~qmwTemporalMemoryStageRevision }
        and: { ~qmwTemporalMemoryStageLines.every { |received| received } }) {
        if(~qmwTemporalMemoryFrozen.not, {
            ~qmwTemporalMemoryRevision = ~qmwTemporalMemoryStageRevision;
            ~qmwTemporalMemoryDelay = ~qmwTemporalMemoryStageDelay;
            ~qmwTemporalMemoryExcitation = ~qmwTemporalMemoryStageExcitation;
            ~qmwTemporalMemoryPersistence = ~qmwTemporalMemoryStagePersistence;
            ~qmwTemporalMemoryWeight = ~qmwTemporalMemoryStageWeight;
            ~qmwTemporalMemoryCross = ~qmwTemporalMemoryStageCross;
            ~qmwTemporalMemoryApply.value;
        });
    };
    ~qmwTemporalMemoryStageActive = false;
}, root ++ "/frame/end", recvPort: port);

"QMW temporal-memory observer V1 ready on UDP % (base-delay control %)"
    .format(port, controlPort).postln;
)
