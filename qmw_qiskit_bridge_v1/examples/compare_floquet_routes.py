from __future__ import annotations

import json

from qmw_qiskit_bridge_v1.experiments import compare_floquet_routes


result = compare_floquet_routes(periods=16)
print(json.dumps(result.as_dict(), indent=2))
