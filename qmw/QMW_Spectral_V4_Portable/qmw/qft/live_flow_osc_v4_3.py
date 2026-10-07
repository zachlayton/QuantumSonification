"""V4.3 launcher boundary over the unchanged V4.2 observer engine.

V4.3 changes the instrument integration and downstream tuning interface, not
the scientific schemas emitted by V4, V4.1, or V4.2. Reusing the established
runner keeps those independent streams byte-for-byte compatible.
"""

from . import live_flow_osc_v4_2 as _v42
from .effective_terrain_v4_3 import V43DensityTerrainObserver


# V4.3 retains the V4.2 runner and schemas, replacing only the attached
# mesoscopic observer with its runtime-derived stability implementation.
_v42.DensityTerrainObserver = V43DensityTerrainObserver
main = _v42.main


if __name__ == "__main__":
    main()
