import numpy as np
import pytest

from qmw.core.physics_frame import (
    PhysicsFrame,
    QuantumFrameAccumulator,
)
from qmw.core.state_frame import QuantumStateFrame


def _four_qubit_ground_frame(samples: int = 2048) -> PhysicsFrame:
    t = np.linspace(0.0, 1.0, samples)
    psi = np.zeros((samples, 16), dtype=complex)
    psi[:, 0] = 1.0
    rho = np.einsum("ti,tj->tij", psi, psi.conj())

    return PhysicsFrame(
        t=t,
        psi=psi,
        rho=rho,
        observables={
            "site_populations": np.zeros((samples, 4)),
            "pauli_x": np.zeros((samples, 4)),
            "pauli_y": np.zeros((samples, 4)),
            "pauli_z": np.ones((samples, 4)),
            "edge_currents": np.zeros((samples, 3)),
        },
        diagnostics={
            "energy": np.zeros(samples),
            "commutator_activity": np.zeros(samples),
        },
    )


def test_canonical_four_qubit_shapes_and_quantum_invariants() -> None:
    frame = _four_qubit_ground_frame()

    assert frame.t.shape == (2048,)
    assert frame.psi.shape == (2048, 16)
    assert frame.rho.shape == (2048, 16, 16)

    assert frame.observables["site_populations"].shape == (2048, 4)
    assert frame.observables["pauli_x"].shape == (2048, 4)
    assert frame.observables["pauli_y"].shape == (2048, 4)
    assert frame.observables["pauli_z"].shape == (2048, 4)
    assert frame.observables["edge_currents"].shape == (2048, 3)

    assert frame.diagnostics["energy"].shape == (2048,)
    assert frame.diagnostics["commutator_activity"].shape == (2048,)

    assert np.allclose(frame.purity(), 1.0)

    result = frame.validate_quantum()
    assert result["trace_error_max"] < 1e-12
    assert result["state_norm_error_max"] < 1e-12
    assert result["positive_semidefinite"]


def test_rejects_mismatched_sample_axis() -> None:
    with pytest.raises(ValueError):
        PhysicsFrame(
            t=np.arange(8),
            rho=np.zeros((7, 2, 2), dtype=complex),
        )


def test_accumulator_stacks_live_quantum_state_frames() -> None:
    acc = QuantumFrameAccumulator(samples=4)

    for i in range(4):
        rho = np.array(
            [[1.0, 0.0], [0.0, 0.0]],
            dtype=complex,
        )
        acc.append(
            QuantumStateFrame(
                t=float(i) * 0.1,
                dt=0.1,
                rho=rho,
                source_name="test-engine",
                arrays={
                    "psi": np.array(
                        [1.0, 0.0],
                        dtype=complex,
                    )
                },
                observables={"energy": float(i)},
            )
        )

    assert acc.ready

    frame = acc.to_physics_frame()
    assert frame.t.shape == (4,)
    assert frame.psi.shape == (4, 2)
    assert frame.rho.shape == (4, 2, 2)
    assert frame.observables["energy"].shape == (4,)
    assert frame.metadata["source_names"] == ["test-engine"]
