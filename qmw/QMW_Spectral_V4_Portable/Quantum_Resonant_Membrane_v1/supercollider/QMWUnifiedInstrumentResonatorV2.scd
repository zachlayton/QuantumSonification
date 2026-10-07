/* V2 wraps the intact V1 instrument, then adds sealed-frame excitation only. */
(
var root = thisProcess.nowExecutingPath.dirname;
thisProcess.interpreter.executeFile(root +/+ "QMWUnifiedResonantInstrumentV1.scd");
thisProcess.interpreter.executeFile(root +/+ "QMWQuantumFrameResonatorAddonV2.scd");
)
