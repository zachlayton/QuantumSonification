(
var here = thisProcess.nowExecutingPath.dirname, defs;
~qefHeadless = true;
thisProcess.interpreter.executeFile(here +/+ "../supercollider/EventFieldAddon.scd");
defs = ~qefDefine.();
if(defs.size != 2, { "FAIL: missing SynthDefs".postln; 1.exit });
defs.do { |def| def.asBytes; ("Compiled " ++ def.name).postln };
~qefStart.(); // Must refuse cleanly without a running host.
~qefShutdown.();
"ADDON COMPILE PASS".postln; 0.exit;
)
