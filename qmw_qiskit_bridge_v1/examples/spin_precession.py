from __future__ import annotations

import json

import numpy as np

from qmw_qiskit_bridge_v1 import QMWOperator, StatevectorProvider
from qmw_qiskit_bridge_v1.hamiltonian import expectation_trajectory


hamiltonian = QMWOperator.from_mapping("half-X", {"X": 0.5})
observables = [
    QMWOperator.from_mapping("X", {"X": 1}),
    QMWOperator.from_mapping("Y", {"Y": 1}),
    QMWOperator.from_mapping("Z", {"Z": 1}),
]
frames = expectation_trajectory(
    StatevectorProvider(), hamiltonian, observables, np.linspace(0, 2 * np.pi, 17)
)
print(json.dumps([frame.as_dict() for frame in frames], indent=2))
