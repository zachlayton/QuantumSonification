/* Offline DSP test; no audio interface or base instrument required.
Output: QMW_HYBRID_RENDER env path, or OS temp directory/qmw_hybrid_check.wav.
Optional QMW_SCSYNTH and QMW_SC_PLUGINS select an unpacked SC runtime. */
(
var here = thisProcess.nowExecutingPath.dirname;
var options = ServerOptions.new.numOutputBusChannels_(20).numInputBusChannels_(0);
var path = "QMW_HYBRID_RENDER".getenv ? (PathName.tmp +/+ "qmw_hybrid_check.wav");
var events, env;
thisProcess.interpreter.executeFile(here +/+ "HybridPacketAddon.scd");
~hybridSpatialConfigured = true; ~hybridDefine.();
"QMW_SCSYNTH".getenv !? { |p| Score.program = p };
"QMW_SC_PLUGINS".getenv !? { |p| options.ugenPluginsPath = p };
options.numWireBufs = 4096;
env = Array.fill(1024, { |i| var x = ((i/1023)*8)-4; ((x.squared * -0.5).exp - (-8).exp).max(0) });
events = [
    [0, [\d_recv, SynthDescLib.global.at(\qmwHybridBodyV1).def.asBytes]],
    [0, [\b_alloc, 0, 1024, 1]],
    [0.01, [\b_setn, 0, 0, 1024] ++ env],
    [0.01, [\c_set, 0, 0, 1, 110, 2, 1, 3, 2]],
    [0.02, [\s_new, \qmwHybridBodyV1, 1000, 0, 0,
        \out, 0, \fxSendBus, 20, \envBuf, 0, \gain, 0.03,
        \density, 40, \duration, 0.04, \decay, 0.2,
        \ringMixBus, 0, \ringFrequencyBus, 1,
        \wavefoldMixBus, 0, \wavefoldDriveBus, 2,
        \fuzzMixBus, 0, \fuzzDriveBus, 3,
        \spatial, 1, \spatialAvailable, 1]],
    [1, [\n_set, 1000, \blend, 1, \alive, 1]],
    [1, [\n_setn, 1000, \re, 16] ++ [1.0] ++ (0.0 ! 15)],
    [1, [\n_setn, 1000, \im, 16] ++ [0.0, 0.5] ++ (0.0 ! 14)],
    [2, [\n_set, 1000, \density, 0]],
    [3.8, [\n_free, 1000]]
];
Score(events).recordNRT(outputFilePath: path, sampleRate: 48000,
    headerFormat: "WAV", sampleFormat: "float", options: options, duration: 4,
    action: { |code| { ~hybridShutdown.(); ("NRT exit " ++ code ++ " -> " ++ path).postln; code.exit }.defer });
)
