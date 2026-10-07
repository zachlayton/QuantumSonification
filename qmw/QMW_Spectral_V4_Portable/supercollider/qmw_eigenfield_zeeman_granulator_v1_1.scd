/*
QMW eigenfield-directed Zeeman granulator v1

Python conductor: quantum state + 4x4 eigenfield grid
SuperCollider: rich-source grains -> per-cell Zeeman splitting -> resonator bank

Evaluate this file, then run:
  python quantumsonification_conductor.py --supercollider-port 57120

The initial renderer uses /qmw/conductor/eigenfield/grid/4. Evaluate
~qmwZGTest.() without Python to verify the complete audio path.
*/
(
var sourcePath = Platform.resourceDir +/+ "sounds/a11wlk01.wav";

s.waitForBoot {
    ~qmwZGCells = 16;
    ~qmwZGSource = Buffer.readChannel(s, sourcePath, channels: [0]);
    ~qmwZGField = 1.0;
    ~qmwZGCarrier = 110.0;
    ~qmwZGSpread = 60.0;
    ~qmwZGLevel = 0.18;
    ~qmwZGPreset = \normal;
    ~qmwZGLastFrame = nil;
    ~qmwZGFrameCount = 0;

    SynthDef(\qmwZGCell, {
        |outBus=0, buf=0, density=0, fieldDensity=0, phase=0,
        occupancy=0, x=0.5, y=0.5, motion=0, field=1,
        splitFactor=1, transitionStrength=1, master=0.16, gate=1|
        var triggerRate = density.clip(0, 1).pow(1.6).linexp(0.001, 1, 0.08, 28);
        var trig = Dust.kr(triggerRate) * (density > 0.012);
        var duration = motion.clip(0, 1).linlin(0, 1, 0.32, 0.035);
        var position = (y + TRand.kr(-0.06, 0.06, trig)).wrap(0, 1);
        var semitones = field * splitFactor * 1.75;
        var baseRate = (phase * 0.5).midiratio;
        var direction = Select.kr(phase < 0, [1, -1]);
        var gliss = Line.kr(1, (motion * 5).midiratio, duration);
        var lowerRate = baseRate * semitones.neg.midiratio * direction * gliss;
        var upperRate = baseRate * semitones.midiratio * direction * gliss.reciprocal;
        var spread = fieldDensity.linlin(0, 1, 0.12, 0.92);
        var panCenter = x.linlin(0, 1, -0.85, 0.85);
        var lower = GrainBuf.ar(
            1, trig, duration, buf, lowerRate, position, 2, 0,
            maxGrains: 64
        );
        var upper = GrainBuf.ar(
            1, trig, duration, buf, upperRate, position, 2, 0,
            maxGrains: 64
        );
        var strength = transitionStrength.sqrt
            * fieldDensity.sqrt
            * occupancy.linlin(0, 1, 0.35, 1);
        var signal = Pan2.ar(lower, panCenter - spread)
            + Pan2.ar(upper, panCenter + spread);
        var envelope = EnvGen.kr(Env.asr(0.05, 1, 0.2), gate, doneAction: Done.freeSelf);
        Out.ar(outBus, LeakDC.ar(signal) * strength * master * envelope);
    }).add;

    SynthDef(\qmwZGResonator, {
        |inBus=0, out=0, carrier=110, field=1, spreadHz=60,
        coherence=0.5, level=0.18, wet=0.72, gate=1|
        var input = In.ar(inBus, 2);
        var factors = [-1.6667, -1, -0.3333, 0.3333, 1, 1.6667];
        var strengths = [0.333, 1, 0.667, 0.667, 1, 0.333];
        var frequencies = (carrier + (factors * field * spreadHz)).abs.clip(30, 16000);
        var decay = coherence.clip(0, 1).linexp(0, 1, 0.08, 1.8);
        var mono = input.sum * 0.5;
        var modes = Ringz.ar(mono, frequencies, decay) * strengths.sqrt;
        var resonant = Splay.ar(modes, 0.9, 0.18);
        var signal = XFade2.ar(input, resonant, wet.linlin(0, 1, -1, 1));
        var envelope = EnvGen.kr(Env.asr(0.03, 1, 0.3), gate, doneAction: Done.freeSelf);
        Out.ar(out, Limiter.ar((signal * level * envelope).tanh, 0.92, 0.01));
    }).add;

    s.sync;
    ~qmwZGBus = Bus.audio(s, 2);
    ~qmwZGSourceGroup = Group.head(s);
    ~qmwZGFXGroup = Group.after(~qmwZGSourceGroup);
    ~qmwZGVoices = Array.fill(~qmwZGCells, { |index|
        Synth.head(~qmwZGSourceGroup, \qmwZGCell, [
            \outBus, ~qmwZGBus, \buf, ~qmwZGSource.bufnum,
            \x, (index % 4 + 0.5) / 4,
            \y, (index.div(4) + 0.5) / 4,
            \splitFactor, [-1, -0.333, 0.333, 1].wrapAt(index),
            \transitionStrength, [0.333, 1, 1, 0.333].wrapAt(index)
        ])
    });
    ~qmwZGResonator = Synth.tail(~qmwZGFXGroup, \qmwZGResonator, [
        \inBus, ~qmwZGBus, \out, 0
    ]);

    ~qmwZGApplyGrid4 = { |message|
        var values = message.copyRange(1, message.size - 1).collect(_.asFloat);
        if(values.size >= 48) {
            16.do { |index|
                var offset = index * 3;
                var density = values[offset].clip(0, 1);
                var phase = values[offset + 1].clip(-1, 1) * pi;
                var occupancy = values[offset + 2].clip(0, 1);
                ~qmwZGVoices[index].set(
                    \density, density * occupancy.linlin(0, 1, 0.25, 1),
                    \fieldDensity, density,
                    \phase, phase,
                    \occupancy, occupancy,
                    \motion, (density - (~qmwZGPreviousDensity ? Array.fill(16, 0))[index]).abs * 4,
                    \field, ~qmwZGField
                );
            };
            ~qmwZGPreviousDensity = Array.fill(16, { |i| values[i * 3] });
            ~qmwZGFrameCount = ~qmwZGFrameCount + 1;
            ~qmwZGLastFrame = Main.elapsedTime;
        };
    };

    OSCdef(\qmwZGGrid4, { |message| ~qmwZGApplyGrid4.(message) },
        '/qmw/conductor/eigenfield/grid/4');
    OSCdef(\qmwZGZeeman, { |message|
        if(message.size >= 5) {
            ~qmwZGField = message[1].asFloat;
            ~qmwZGCarrier = message[2].asFloat;
            ~qmwZGSpread = message[3].asFloat;
            ~qmwZGLevel = message[4].asFloat;
            ~qmwZGVoices.do { |voice| voice.set(\field, ~qmwZGField) };
            ~qmwZGResonator.set(
                \field, ~qmwZGField, \carrier, ~qmwZGCarrier,
                \spreadHz, ~qmwZGSpread, \level, ~qmwZGLevel
            );
        };
    }, '/qmw/conductor/zeeman');
    OSCdef(\qmwZGCoherence, { |message|
        ~qmwZGResonator.set(\coherence, message[1].asFloat.clip(0, 1));
    }, '/qmw/density_field/coherence');

    ~qmwZGTest = {
        var frame = Array.fill(16, { |i|
            var x = i % 4;
            var y = i.div(4);
            var occupied = if((i % 3) == 0) { 1 } { 0 };
            [(((x-1.5).squared + (y-1.5).squared) * 0.7).neg.exp,
             (x-y) / 3,
             0.35 + (0.65 * occupied)]
        }).flat;
        ~qmwZGApplyGrid4.(['/qmw/conductor/eigenfield/grid/4'] ++ frame);
        "QMW Zeeman-granulator test field applied.".postln;
    };
    ~qmwZGStatus = {
        "QMW ZG frames=%, age=%, field=%, carrier=%"
            .format(~qmwZGFrameCount,
                if(~qmwZGLastFrame.isNil) { "never" } { (Main.elapsedTime-~qmwZGLastFrame).round(0.01) },
                ~qmwZGField.round(0.001), ~qmwZGCarrier.round(0.1)).postln;
    };
    ~qmwZGStop = {
        [\qmwZGGrid4, \qmwZGZeeman, \qmwZGCoherence].do { |name| OSCdef(name).free };
        if(~qmwZGVoices.notNil) { ~qmwZGVoices.do { |voice| voice.set(\gate, 0) } };
        if(~qmwZGResonator.notNil) { ~qmwZGResonator.set(\gate, 0) };
        if(~qmwZGSource.notNil) { ~qmwZGSource.free };
        if(~qmwZGBus.notNil) { ~qmwZGBus.free };
        "QMW eigenfield Zeeman granulator stopped.".postln;
    };
    "QMW eigenfield Zeeman granulator ready. Run ~qmwZGTest.() or start the conductor mirror.".postln;
};
)


~qmwZGTest.()