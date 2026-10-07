/* V3 keeps V2 intact, then adds its independent read-only observer adapters. */
(
var root = thisProcess.nowExecutingPath.dirname;
var temporalMemoryPort = ("QMW_TEMPORAL_MEMORY_PORT".getenv ? "0").asInteger;
var temporalMemoryControlPort = ("QMW_TEMPORAL_MEMORY_CONTROL_PORT".getenv ? "0").asInteger;
var harmonicMemoryInterference = ("QMW_HARMONIC_MEMORY_INTERFERENCE".getenv ? "0").asInteger;
var harmonicMemoryDevelopmentPort = ("QMW_HARMONIC_MEMORY_DEVELOPMENT_PORT".getenv ? "0").asInteger;
var decayMatrixFile = root +/+ "QMWV3DecayMatrixAddonV1.scd";
thisProcess.interpreter.executeFile(root +/+ "QMWUnifiedInstrumentResonatorV2.scd");
thisProcess.interpreter.executeFile(root +/+ "QMWRelationalSpectralResonanceAddonV3.scd");
thisProcess.interpreter.executeFile(root +/+ "QMWModalGeometryResonatorAddonV1.scd");
thisProcess.interpreter.executeFile(root +/+ "QMWModalSpectralVoiceAddonV1.scd");
thisProcess.interpreter.executeFile(root +/+ "QMWRingsBodyAddonV1.scd");
// Optional final headphone adapter. It is disabled on load and observes
// admitted events only; the normal stereo path remains the recovery default.
thisProcess.interpreter.executeFile(root +/+ "QMWBinauralHeadphoneObserverV1.scd");
thisProcess.interpreter.executeFile(root +/+ "QMWV3MatrixAddonV1.scd");
if(PathName(decayMatrixFile).isFile, {
    thisProcess.interpreter.executeFile(decayMatrixFile);
}, {
    "QMW V3 optional decay-matrix add-on is not installed; continuing without it.".postln;
});
// QMF is opt-in and composes after all established body/event adapters. It
// never owns rho, event admission, or the performer m0--m19 controls.
if(("QMW_QUANTUM_METRIC_ENABLED".getenv ? "0").asInteger > 0, {
    thisProcess.interpreter.executeFile(root +/+ "QMWQuantumMetricFieldAddonV1.scd");
});
if(temporalMemoryPort > 0, {
    // Independent stereo observer: no event admission, rho, H, or geometry
    // route is altered.  The V3 launcher sets 17884; port 0 disables it.
    ~qmwTemporalMemoryPort = temporalMemoryPort;
    ~qmwTemporalMemoryControlPort = temporalMemoryControlPort;
    thisProcess.interpreter.executeFile(root +/+ "../../supercollider/qmw_temporal_memory_observer_v1.scd");
    // The QRI post-boot rebuild hook starts this only after qrmStrikeGroup is
    // real, ensuring an ordered event-send -> memory-return signal path.
    ~qmwTemporalMemoryPendingStart = true;
});
if(harmonicMemoryInterference > 0, {
    // Additive eight-path, pluck-send-only baseline. Its H(w) is a coherent
    // temporal phasor sum; scattering and QMW mapping come in later stages.
    thisProcess.interpreter.executeFile(root +/+ "../../supercollider/qmw_harmonic_memory_interference_field_v1.scd");
});
if(harmonicMemoryDevelopmentPort > 0, {
    // Event-clocked four-node audition only. It receives admitted-event
    // observer frames but has no return path into the main instrument.
    ~qmwHmdPort = harmonicMemoryDevelopmentPort;
    thisProcess.interpreter.executeFile(root +/+ "../../supercollider/qmw_harmonic_memory_audition_v1.scd");
});
// Conservative V3_Matrix scene: direct primary stereo, no optional feedback
// or send paths, and only tonal pluck voices until explicitly enabled.
~qmxInitializeStereo.value;
thisProcess.interpreter.executeFile(root +/+ "QMWInstrumentWorkspaceLauncherV1.scd");
// QMWZXDensityResonatorAddonV1.scd remains an explicit later experiment.
// Prototype A must establish Scala/Wilson -> dodecahedral W -> L -> Q/Lambda
// before any rho-derived deformation is permitted to reach this instrument.
)
