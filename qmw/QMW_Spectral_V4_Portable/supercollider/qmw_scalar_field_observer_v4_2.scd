/*
QMW Quantum Field Theory Instrument V4.2

Adds the density-derived effective Lagrangian terrain observer to the V4
instrument.  The shared V4 scalar field remains authoritative; this attached
observer is capability-gated and its crossing sonification is an explicit
downstream adapter.
*/
(
// A narrowly extended wrapper (4.2b) may set its own display version before
// loading this complete 4.2 instrument. Plain 4.2 retains the established name.
~qmwQFTDisplayVersion = ~qmwQFTDisplayVersion ? "4.2";
~qmwQFTEffectiveTerrainEnabled = true;
~qmwQFTEffectiveTerrainPort = 17863;
// Add one persistent Bloch-harmonic spatial channel beside the four existing
// event voices. The fifth fader starts at exact zero and never writes upstream.
~qmwQFTV42BlochVoiceEnabled = true;
// V4.2 uses two independent stereo stems: event/pluck audio on hardware
// outputs 1-2 and the continuous field/vacuum stem on outputs 3-4.
~qmwQFTSplitFieldOutput = true;
s.options.numOutputBusChannels = s.options.numOutputBusChannels.max(4);
// The 16-site continuous and four pulse SynthDefs exceed the stock wire-buffer
// budget on installations that also load SuperDirt. This takes effect on the
// next server boot and does not alter any DSP or field dynamics.
s.options.numWireBufs = s.options.numWireBufs.max(4096);
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_scalar_field_observer_v4.scd"
);
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_qho_parseval_v4_2.scd"
);
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_bloch_harmonics_spatial_v4_2.scd"
);
)
