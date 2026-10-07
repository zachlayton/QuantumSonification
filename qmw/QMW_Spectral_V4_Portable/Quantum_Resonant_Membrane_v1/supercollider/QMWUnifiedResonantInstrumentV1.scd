/* One process: QRM body, bounded QMW 4.4 observer, interaction layer. */
(
var root = thisProcess.nowExecutingPath.dirname;
var repoRoot = root.dirname.dirname;
s.options.numWireBufs = s.options.numWireBufs.max(2048);
thisProcess.interpreter.executeFile(root +/+ "QuantumResonantMembraneV1.scd");
thisProcess.interpreter.executeFile(repoRoot +/+ "supercollider/4_4/qmw_4_4.scd");
thisProcess.interpreter.executeFile(root +/+ "QMWResonantInteractionAddonV1.scd");
)
