/*
QMW Quantum Field Theory Instrument V4.3

V4.3 is an additive instrument boundary built directly on the complete V4.2
stack. It retains the V3/V4 four-voice pulse mixer, time engine, field display,
presets, effects, and the V4.2 probability/terrain observer contracts. The
companion file adds geometric tuning and a compact live mirror of the existing
four-voice mixer; it does not replace the inherited sound graph.
*/
(
~qmwQFTDisplayVersion = "4.3";
~qmwQFTEffectiveTerrainEnabled = true;
~qmwQFTEffectiveTerrainPort = 17863;
~qmwQFTV43Enabled = true;
s.options.numWireBufs = s.options.numWireBufs.max(4096);
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_scalar_field_observer_v4.scd"
);
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_scalar_field_observer_v4_3_addon.scd"
);
)
