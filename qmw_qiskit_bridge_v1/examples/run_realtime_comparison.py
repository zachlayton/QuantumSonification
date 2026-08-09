from pathlib import Path
import sys


COMPONENT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = COMPONENT_ROOT.parent
for source_root in (COMPONENT_ROOT, REPOSITORY_ROOT):
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

from qmw_qiskit_bridge_v1.realtime.osc_instrument import main


if __name__ == "__main__":
    main()
