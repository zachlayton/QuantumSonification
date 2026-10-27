/* Evaluate this file, start the base audio, then press Start field.
   All existing v4.2b files and presets are used without modification. */
(
var here = thisProcess.nowExecutingPath.dirname;
thisProcess.interpreter.executeFile(here +/+ "../../qmw/QMW_Spectral_V4_Portable/supercollider/qmw_scalar_field_observer_v4_2b.scd");
thisProcess.interpreter.executeFile(here +/+ "EventFieldAddon.scd");
)
