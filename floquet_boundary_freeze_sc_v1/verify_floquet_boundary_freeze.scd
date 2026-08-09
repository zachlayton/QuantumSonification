(
var here = thisProcess.nowExecutingPath.dirname;
(here +/+ "floquet_boundary_freeze_synthdef.scd").load;
~makeFloquetBoundaryFreezeDef.value.asBytes;
"VERIFY_OK: qmwFloquetBoundaryFreezeV1 compiled".postln;
0.exit;
)
