// Run with sclang; constructs SynthDefs without starting audio.
(
var here = thisProcess.nowExecutingPath.dirname;
thisProcess.interpreter.executeFile(here +/+ "HybridPacketAddon.scd");
~hybridSpatialConfigured = false; ~hybridDefine.();
~hybridSpatialConfigured = true; ~hybridDefine.();
~hybridShutdown.();
"HYBRID SYNTHDEF COMPILE PASS (stereo + spatial)".postln;
0.exit;
)
