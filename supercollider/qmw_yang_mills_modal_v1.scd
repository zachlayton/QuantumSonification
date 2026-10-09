/*
Evaluate the whole file. Python keeps the SU(2) physics; SuperCollider renders
sixteen native noise-excited modes and an optional spatial coupling warp.
Run: python -m yang_mills_v1 --osc --port 57120 --steps 0
Replace 57120 with the printed language port. Master starts at zero.
*/
(
var scriptPath = thisProcess.nowExecutingPath;
var scriptDirectory;
var definition;
if(scriptPath.isNil) {
    Error("Evaluate this saved file, or execute it with thisProcess.interpreter.executeFile(path).").throw;
};
scriptDirectory = scriptPath.dirname;
if(~qmwYMStop.notNil) { ~qmwYMStop.() };
thisProcess.interpreter.executeFile(scriptDirectory +/+ "qmw_yang_mills_support_v1.scd");

thisProcess.interpreter.executeFile(scriptDirectory +/+ "qmw_yang_mills_synth_v1.scd");
definition = ~qmwYMBuildSynthDef.();

s.waitForBoot {
    definition.add;
    s.sync;
    ~qmwYMSynth = Synth(\qmwYangMillsModal16);
    ~qmwYMEmit = {
        var mapped = ~qmwYMMap.(~qmwYMRawMagnitude, ~qmwYMRawSpeed, ~qmwYMAmount);
        s.makeBundle(nil, {
            ~qmwYMSynth.setn(\magnitude, mapped[\magnitude]);
            ~qmwYMSynth.setn(\speed, mapped[\speed]);
        });
    };
    ~qmwYMDeformation = { |amount = 0|
        if(~qmwYMFinite.(amount)) {
            ~qmwYMAmount = amount.clip(0, 1);
            ~qmwYMEmit.();
        };
    };
    ~qmwYMCoupling = { |amount = 1|
        if(~qmwYMFinite.(amount)) {
            ~qmwYMCouplingValue = amount.clip(0, 1);
            ~qmwYMSynth.set(\coupling, ~qmwYMCouplingValue);
        };
    };
    ~qmwYMMaster = { |amount = 0|
        if(~qmwYMFinite.(amount)) {
            ~qmwYMMasterValue = amount.clip(0, 1);
            ~qmwYMSynth.set(\amp, ~qmwYMMasterValue);
        };
    };
    ~qmwYMFrequency = { |frequency = 55|
        if(~qmwYMFinite.(frequency)) { ~qmwYMSynth.set(\baseFreq, frequency.clip(20, 1000)) };
    };
    ~qmwYMDecay = { |seconds = 1.25|
        if(~qmwYMFinite.(seconds)) { ~qmwYMSynth.set(\ringSeconds, seconds.clip(0.02, 12)) };
    };
    [\begin, \magnitude, \speed, \diagnostics, \end].do { |kind|
        OSCdef(("qmwYM_" ++ kind).asSymbol, { |message|
            ~qmwYMReceive.(kind, message);
        }, ("/qmw/yang_mills/v1/" ++ kind).asSymbol);
    };
    ~qmwYMWatchdog = Routine({
        loop { ~qmwYMWatchdogCheck.(); 0.05.wait };
    }).play(SystemClock);
    ~qmwYMStatus = {
        "QMW Yang-Mills: frames=%, revision=%, age=%, deformation=%, coupling=%, diagnostics=%"
            .format(~qmwYMFrames, ~qmwYMCommitted,
                if(~qmwYMLastFrame.isNil) { "never" } { Main.elapsedTime - ~qmwYMLastFrame },
                ~qmwYMAmount, ~qmwYMCouplingValue, ~qmwYMDiagnostics).postln;
    };
    ~qmwYMTest = {
        var test = Synth(\qmwYangMillsModal16, [
            \amp, 0.15, \magnitude, Array.fill(16, 0.3),
            \speed, Array.fill(16, 0.25)
        ]);
        ~qmwYMTestSynth = test;
        SystemClock.sched(2, { test.set(\gate, 0); nil });
    };
    ~qmwYMGui = {
        {
            var window = Window("QMW Yang-Mills modal resonator", Rect(100, 100, 460, 220));
            var labels = ["Deformation amount", "Field coupling", "Master"];
            var actions = [~qmwYMDeformation, ~qmwYMCoupling, ~qmwYMMaster];
            var values = [~qmwYMAmount, ~qmwYMCouplingValue, ~qmwYMMasterValue];
            if(~qmwYMWindow.notNil) { ~qmwYMWindow.close };
            3.do { |i|
                StaticText(window, Rect(15, 15 + (i * 50), 150, 24)).string_(labels[i]);
                Slider(window, Rect(165, 15 + (i * 50), 270, 24))
                    .value_(values[i]).action_({ |slider| actions[i].(slider.value) });
            };
            Button(window, Rect(15, 170, 120, 28)).states_([["Mute"]])
                .action_({ ~qmwYMMaster.(0); });
            Button(window, Rect(150, 170, 130, 28)).states_([["Reset stream"]])
                .action_({ ~qmwYMReset.(); });
            ~qmwYMWindow = window;
            window.front;
        }.defer;
    };
    ~qmwYMStop = {
        [\begin, \magnitude, \speed, \diagnostics, \end].do { |kind|
            OSCdef(("qmwYM_" ++ kind).asSymbol).free;
        };
        if(~qmwYMWatchdog.notNil) { ~qmwYMWatchdog.stop };
        if(~qmwYMSynth.notNil) { ~qmwYMSynth.set(\gate, 0) };
        if(~qmwYMTestSynth.notNil) { ~qmwYMTestSynth.set(\gate, 0) };
        if(~qmwYMWindow.notNil) { { ~qmwYMWindow.close }.defer };
        ~qmwYMEmit = nil;
        ~qmwYMPending = nil;
        "QMW Yang-Mills receiver stopped.".postln;
    };
    "QMW Yang-Mills ready on UDP %. Master starts at zero.".format(NetAddr.langPort).postln;
    "Use ~qmwYMMaster.(0.15), ~qmwYMDeformation.(0.5), ~qmwYMGui.(), ~qmwYMStatus.().".postln;
};
)
