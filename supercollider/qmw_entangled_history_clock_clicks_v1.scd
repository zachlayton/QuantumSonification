/*
QMW entangled history clock: sixteen independent click voices v1

Channel / voice identity:
    voice 0  = clock basis |0000>
    ...
    voice 15 = clock basis |1111>

Timing is native milliseconds, not a TempoClock grid. Every voice repeats
10101, has a fixed local period, begins at the same release point, and stops
after 48 hits. Equal hit budgets preserve the uniform computational-clock
probabilities; unequal periods create the progressive Ligeti-form thinning.

Default output is stereo. For one hardware/virtual output per basis state,
evaluate this before loading the file and reboot the server if necessary:

    ~qmwHistoryClockOutputMode = \discrete16;
    s.options.numOutputBusChannels = 16;
    s.reboot;

Controls after evaluation:
    ~qmwHistoryClockStart.();
    ~qmwHistoryClockStop.();
    ~qmwHistoryClockStatus.();
*/

(
~qmwHistoryClockOutputMode = ~qmwHistoryClockOutputMode ? \stereo;
~qmwHistoryClockAutoStart = ~qmwHistoryClockAutoStart ? true;
~qmwHistoryClockPattern = [1, 0, 1, 0, 1];
~qmwHistoryClockReferenceMs = 150.0;
~qmwHistoryClockBinsPerOctave = 16.0;
~qmwHistoryClockHitBudget = 48;
~qmwHistoryClockBasisLabels = Array.fill(16, { |index|
    index.asBinaryDigits(4).join;
});
~qmwHistoryClockIntervalsMs = Array.fill(16, { |index|
    ~qmwHistoryClockReferenceMs
        * (2 ** ((index - 7.5) / ~qmwHistoryClockBinsPerOctave));
});
~qmwHistoryClockRoutines = Array.newClear(16);
~qmwHistoryClockGroup = nil;
~qmwHistoryClockRunning = false;

~qmwHistoryClockStop = {
    ~qmwHistoryClockRunning = false;
    if(~qmwHistoryClockRoutines.notNil) {
        ~qmwHistoryClockRoutines.do { |routine|
            if(routine.notNil) { routine.stop };
        };
    };
    ~qmwHistoryClockRoutines = Array.newClear(16);
    if(~qmwHistoryClockGroup.notNil) {
        ~qmwHistoryClockGroup.free;
        ~qmwHistoryClockGroup = nil;
    };
    "QMW history clocks stopped.".postln;
};

~qmwHistoryClockStatus = {
    "QMW history clock | running: % | mode: % | pattern: % | hits: %"
        .format(
            ~qmwHistoryClockRunning,
            ~qmwHistoryClockOutputMode,
            ~qmwHistoryClockPattern,
            ~qmwHistoryClockHitBudget
        ).postln;
    ~qmwHistoryClockIntervalsMs.do { |interval, index|
        "voice % |%> | % ms | audio out %"
            .format(
                index + 1,
                ~qmwHistoryClockBasisLabels[index],
                interval.round(0.001),
                if(~qmwHistoryClockOutputMode == \discrete16) {
                    index + 1
                } {
                    "stereo"
                }
            ).postln;
    };
};

s.waitForBoot {
    SynthDef(\qmwHistoryClockClickStereoV1, {
        |out = 0, frequency = 700, amplitude = 0.035, pan = 0,
        release = 0.024|

        var envelope = EnvGen.ar(
            Env.perc(0.0003, release, curve: -9),
            doneAction: 2
        );
        var body = SinOsc.ar(frequency, 0, 0.72);
        var edge = SinOsc.ar(frequency * 2.31, pi * 0.5, 0.28);
        var signal = LeakDC.ar((body + edge) * envelope * amplitude);
        Out.ar(out, Pan2.ar(signal, pan.clip(-1, 1)));
    }).add;

    SynthDef(\qmwHistoryClockClickMonoV1, {
        |out = 0, frequency = 700, amplitude = 0.035, release = 0.024|

        var envelope = EnvGen.ar(
            Env.perc(0.0003, release, curve: -9),
            doneAction: 2
        );
        var body = SinOsc.ar(frequency, 0, 0.72);
        var edge = SinOsc.ar(frequency * 2.31, pi * 0.5, 0.28);
        var signal = LeakDC.ar((body + edge) * envelope * amplitude);
        Out.ar(out, signal);
    }).add;

    s.sync;

    ~qmwHistoryClockStart = {
        var commonReleaseDelay = 0.20;

        ~qmwHistoryClockStop.();
        ~qmwHistoryClockRunning = true;
        ~qmwHistoryClockGroup = Group.head(s);

        SystemClock.sched(commonReleaseDelay, {
            if(~qmwHistoryClockRunning) {
                16.do { |voice|
                    var intervalSeconds =
                        ~qmwHistoryClockIntervalsMs[voice] / 1000.0;
                    var frequency = 480.0 * (2 ** (voice / 12.0));
                    var pan = sin(2pi * voice / 16.0);
                    var basisLabel = ~qmwHistoryClockBasisLabels[voice];

                    ~qmwHistoryClockRoutines[voice] = Routine({
                        var cell = 0;
                        var hits = 0;

                        while {
                            ~qmwHistoryClockRunning
                            and: { hits < ~qmwHistoryClockHitBudget }
                        } {
                            if(~qmwHistoryClockPattern.wrapAt(cell) == 1) {
                                if(~qmwHistoryClockOutputMode == \discrete16) {
                                    Synth.tail(
                                        ~qmwHistoryClockGroup,
                                        \qmwHistoryClockClickMonoV1,
                                        [
                                            \out, voice,
                                            \frequency, frequency,
                                            \amplitude, 0.055,
                                            \release, 0.022
                                        ]
                                    );
                                } {
                                    Synth.tail(
                                        ~qmwHistoryClockGroup,
                                        \qmwHistoryClockClickStereoV1,
                                        [
                                            \out, 0,
                                            \frequency, frequency,
                                            \amplitude, 0.035,
                                            \pan, pan,
                                            \release, 0.022
                                        ]
                                    );
                                };
                                hits = hits + 1;
                            };
                            cell = cell + 1;
                            intervalSeconds.wait;
                        };

                        "voice % |%> exhausted after % hits at % ms"
                            .format(
                                voice + 1,
                                basisLabel,
                                hits,
                                (cell * intervalSeconds * 1000).round(1)
                            ).postln;
                    }).play(SystemClock);
                };
                "QMW sixteen-clock common release.".postln;
            };
            nil
        });
    };

    "QMW history-clock click ensemble ready: |0000> through |1111>.".postln;
    ~qmwHistoryClockStatus.();
    if(~qmwHistoryClockAutoStart) { ~qmwHistoryClockStart.() };
};
)
