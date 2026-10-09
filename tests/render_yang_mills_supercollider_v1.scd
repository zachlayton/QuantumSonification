// Test fixture: compile the production DSP and write an NRT score.
// A subsequent scsynth -N render needs no audio hardware.
(
var root = thisProcess.nowExecutingPath.dirname.dirname;
var output = "QMW_SC_SCORE_PATH".getenv;
var definition, score, options, pattern;
try {
    if(output.isNil) { Error("Set QMW_SC_SCORE_PATH to a temporary score filename.").throw };
    thisProcess.interpreter.executeFile(root +/+ "supercollider/qmw_yang_mills_support_v1.scd");
    thisProcess.interpreter.executeFile(root +/+ "supercollider/qmw_yang_mills_synth_v1.scd");
    definition = ~qmwYMBuildSynthDef.();
    pattern = ~qmwYMMap.(Array.fill(16, { |i| (i + 1) / 50 }), 0.3 ! 16, 0.75);
    score = Score([
        [0, [\d_recv, definition.asBytes]],
        [0.01, [\s_new, \qmwYangMillsModal16, 1000, 0, 0, \amp, 0.25]],
        [0.02, [\n_setn, 1000, \magnitude, 16] ++ pattern[\magnitude]],
        [0.02, [\n_setn, 1000, \speed, 16] ++ pattern[\speed]],
        [0.5, [\n_free, 1000]],
        [0.51, [\s_new, \qmwYangMillsModal16, 1001, 0, 0, \amp, 0.25, \coupling, 0]],
        [0.52, [\n_setn, 1001, \magnitude, 16] ++ pattern[\magnitude]],
        [0.52, [\n_setn, 1001, \speed, 16] ++ pattern[\speed]],
        [1, [\n_free, 1001]],
        [1.01, [\s_new, \qmwYangMillsModal16, 1002, 0, 0, \amp, 0]],
        [1.02, [\n_setn, 1002, \magnitude, 16] ++ pattern[\magnitude]],
        [1.02, [\n_setn, 1002, \speed, 16] ++ pattern[\speed]],
        [1.5, [\n_free, 1002]],
        [1.51, [\s_new, \qmwYangMillsModal16, 1003, 0, 0, \amp, 0.25]],
        [2, [\n_free, 1003]],
        [2.1, [\c_set, 0, 0]]
    ]);
    score.write(output);
    "PASS: production DSP compiled and NRT score written".postln;
    0.exit;
} { |error|
    error.reportError;
    1.exit;
};
)
