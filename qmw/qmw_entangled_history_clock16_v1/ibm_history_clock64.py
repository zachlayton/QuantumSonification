"""Optimized ten-qubit IBM circuit for the 64-state history clock.

The circuit uses six clock qubits and the existing four-qubit Floquet system.
For the default exact pi kick, all binary powers above U_F simplify to diagonal
ZZ evolution, avoiding generic controlled 16x16-unitary synthesis.

Importing this module requires Qiskit. Hardware submission additionally
requires qiskit-ibm-runtime and an explicit ``--confirm-ibm`` flag.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate, RZZGate
from qiskit.quantum_info import Statevector

from qmw_temporal_crystal16_v1 import FloquetTimeCrystal16
from qmw_temporal_crystal16_v1.qmw_temporal_core16_v1 import (
    computational_basis_state,
)

from .diagnostics import analyze_history
from .history_state import prepare_floquet_history_state


SYSTEM_QUBITS = tuple(range(4))
CLOCK_QUBITS = tuple(range(4, 10))
CLOCK_COUNT = 64
ACCOUNT_NAME = "quantum-sonification-workshop"


def _validate_optimized_model(model: FloquetTimeCrystal16) -> None:
    config = model.config
    if abs(config.actual_kick_angle - np.pi) > 1e-12:
        raise ValueError("optimized hardware circuit requires the exact pi kick")
    if any(abs(value) > 1e-12 for value in config.transverse_fields):
        raise ValueError("optimized hardware circuit requires zero transverse fields")
    if config.periodic_boundary:
        raise ValueError("optimized hardware reference currently uses open boundaries")


def _append_controlled_rzz(
    circuit: QuantumCircuit,
    control: int,
    left: int,
    right: int,
    angle: float,
) -> None:
    circuit.append(
        RZZGate(float(angle)).control(1),
        [control, left, right],
    )


def build_history_circuit64(
    model: FloquetTimeCrystal16 | None = None,
) -> QuantumCircuit:
    """Build the exact optimized coherent history-state preparation circuit."""

    floquet = model or FloquetTimeCrystal16()
    _validate_optimized_model(floquet)
    config = floquet.config
    circuit = QuantumCircuit(10, name="qmw_history_clock64")
    for clock in CLOCK_QUBITS:
        circuit.h(clock)

    # Binary power U_F^1. Rightmost global X kick acts first.
    first_control = CLOCK_QUBITS[0]
    for system in SYSTEM_QUBITS:
        circuit.crx(config.actual_kick_angle, first_control, system)
    for bond, strength in enumerate(config.interaction_strengths):
        _append_controlled_rzz(
            circuit,
            first_control,
            SYSTEM_QUBITS[bond],
            SYSTEM_QUBITS[bond + 1],
            2.0 * config.interaction_time * strength,
        )
    for system, field in zip(SYSTEM_QUBITS, config.longitudinal_fields):
        circuit.crz(
            2.0 * config.interaction_time * field,
            first_control,
            system,
        )

    # For the exact global pi kick, U_F^(2^k), k>=1, contains only Ising ZZ
    # evolution. Longitudinal fields cancel between the two flipped halves.
    for bit in range(1, 6):
        control = CLOCK_QUBITS[bit]
        power = 1 << bit
        for bond, strength in enumerate(config.interaction_strengths):
            _append_controlled_rzz(
                circuit,
                control,
                SYSTEM_QUBITS[bond],
                SYSTEM_QUBITS[bond + 1],
                2.0 * power * config.interaction_time * strength,
            )
    return circuit


def build_compiled_history_circuit64(
    model: FloquetTimeCrystal16 | None = None,
) -> QuantumCircuit:
    """Prepare the identical default history using its closed-form structure.

    This is an exact state-preparation compilation for the default initial
    state, not a general implementation of arbitrary controlled Floquet powers.
    """

    floquet = model or FloquetTimeCrystal16()
    _validate_optimized_model(floquet)
    history = prepare_floquet_history_state(
        floquet,
        computational_basis_state(0),
        clock_qubits=6,
    )
    branches = history.conditional_states()
    occupied = np.argmax(np.abs(branches), axis=1)
    expected = np.asarray([0 if index % 2 == 0 else 15 for index in range(64)])
    if not np.array_equal(occupied, expected):
        raise RuntimeError("closed-form compilation requires 0/15 alternation")
    phases = np.asarray([
        np.angle(branch[np.argmax(np.abs(branch))]) for branch in branches
    ])
    odd_phase = float(phases[1])
    two_step_phase = float(phases[2])

    circuit = QuantumCircuit(10, name="qmw_history_clock64_compiled")
    for clock in CLOCK_QUBITS:
        circuit.h(clock)
    circuit.p(odd_phase, CLOCK_QUBITS[0])
    for bit in range(1, 6):
        circuit.p(two_step_phase * (1 << (bit - 1)), CLOCK_QUBITS[bit])
    for system in SYSTEM_QUBITS:
        circuit.cx(CLOCK_QUBITS[0], system)
    return circuit


def build_measurement_circuits64(
    model: FloquetTimeCrystal16 | None = None,
) -> dict[str, QuantumCircuit]:
    """Build targeted computational and clock-Fourier sampling circuits."""

    coherent = build_compiled_history_circuit64(model)
    computational = coherent.copy(name="history64_computational")
    computational.measure_all()

    clock_fourier = coherent.copy(name="history64_clock_fourier")
    # Qiskit's inverse QFT has the negative-exponent convention used by the
    # NumPy clock diagnostic. Reversal is handled internally by QFTGate.
    clock_fourier.append(QFTGate(6).inverse(), list(CLOCK_QUBITS))
    clock_fourier.measure_all()
    return {
        "computational": computational,
        "clock_fourier": clock_fourier,
    }


def ideal_validation() -> dict[str, Any]:
    """Compare Qiskit's circuit state and clock spectrum with NumPy exactly."""

    model = FloquetTimeCrystal16()
    circuit = build_history_circuit64(model)
    compiled_circuit = build_compiled_history_circuit64(model)
    state = np.asarray(Statevector.from_instruction(circuit).data)
    compiled_state = np.asarray(
        Statevector.from_instruction(compiled_circuit).data
    )
    history = prepare_floquet_history_state(
        model,
        computational_basis_state(0),
        clock_qubits=6,
    )
    overlap = np.vdot(history.state_vector, state)
    aligned = state * np.exp(-1j * np.angle(overlap))
    state_error = float(np.max(np.abs(aligned - history.state_vector)))
    compiled_overlap = np.vdot(history.state_vector, compiled_state)
    compiled_aligned = compiled_state * np.exp(-1j * np.angle(compiled_overlap))
    compiled_state_error = float(np.max(
        np.abs(compiled_aligned - history.state_vector)
    ))

    qft_circuit = compiled_circuit.copy()
    qft_circuit.append(QFTGate(6).inverse(), list(CLOCK_QUBITS))
    qft_state = np.asarray(Statevector.from_instruction(qft_circuit).data)
    qft_probabilities = np.sum(
        np.abs(qft_state.reshape(CLOCK_COUNT, 16)) ** 2,
        axis=1,
    )
    expected_qft = analyze_history(history).clock_fourier_probabilities
    qft_error = float(np.max(np.abs(qft_probabilities - expected_qft)))
    return {
        "qubits": circuit.num_qubits,
        "clock_qubits": 6,
        "system_qubits": 4,
        "joint_amplitudes": len(state),
        "statevector_max_error": state_error,
        "compiled_statevector_max_error": compiled_state_error,
        "clock_qft_probability_max_error": qft_error,
        "abstract_depth": circuit.depth(),
        "abstract_operations": dict(circuit.count_ops()),
        "compiled_abstract_depth": compiled_circuit.depth(),
        "compiled_abstract_operations": dict(compiled_circuit.count_ops()),
    }


def _backend_name(backend: Any) -> str:
    value = getattr(backend, "name", "unknown")
    return str(value() if callable(value) else value)


def _job_id(job: Any) -> str:
    value = getattr(job, "job_id")
    return str(value() if callable(value) else value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", default=ACCOUNT_NAME)
    parser.add_argument("--backend")
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--inspect-backend", action="store_true")
    parser.add_argument("--confirm-ibm", action="store_true")
    parser.add_argument("--submit-only", action="store_true")
    parser.add_argument(
        "--save-directory",
        type=Path,
        default=Path("output/entangled_history_clock64_v1/ibm"),
    )
    args = parser.parse_args(argv)
    if args.shots <= 0:
        raise SystemExit("--shots must be positive")

    validation = ideal_validation()
    print(json.dumps({"ideal_validation": validation}, indent=2), flush=True)
    if not args.inspect_backend and not args.confirm_ibm:
        print(
            "Local validation complete. Use --inspect-backend for read-only "
            "hardware transpilation or --confirm-ibm to submit.",
            flush=True,
        )
        return 0

    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService(name=args.account)
    backend = (
        service.backend(args.backend)
        if args.backend
        else service.least_busy(
            operational=True,
            simulator=False,
            min_num_qubits=10,
        )
    )
    circuits = build_measurement_circuits64()
    pass_manager = generate_preset_pass_manager(
        backend=backend,
        optimization_level=2,
    )
    isa_circuits = pass_manager.run(list(circuits.values()))
    backend_report = {
        "backend": _backend_name(backend),
        "circuits": {
            name: {
                "depth": isa.depth(),
                "operations": dict(isa.count_ops()),
            }
            for name, isa in zip(circuits, isa_circuits)
        },
    }
    print(json.dumps({"hardware_readiness": backend_report}, indent=2), flush=True)
    if not args.confirm_ibm:
        print("Read-only hardware inspection complete; no job submitted.", flush=True)
        return 0

    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa_circuits, shots=args.shots)
    current_job_id = _job_id(job)
    submitted_at = datetime.now(timezone.utc).isoformat()
    archive_directory = args.save_directory / current_job_id
    archive_directory.mkdir(parents=True, exist_ok=True)
    archive_path = archive_directory / "history-clock64-job.json"
    archive = {
        "schema": "qmw.entangled_history_clock64.ibm.v1",
        "job": {
            "id": current_job_id,
            "backend": _backend_name(backend),
            "submitted_at": submitted_at,
            "shots_per_circuit": args.shots,
            "status": str(job.status()),
        },
        "ideal_validation": validation,
        "hardware_readiness": backend_report,
    }
    archive_path.write_text(json.dumps(archive, indent=2) + "\n")
    print(f"IBM job submitted: {current_job_id}", flush=True)
    print(f"Job archive: {archive_path.resolve()}", flush=True)
    if args.submit_only:
        return 0

    result = job.result()
    counts: dict[str, dict[str, int]] = {}
    for name, publication in zip(circuits, result):
        counts[name] = {
            str(key): int(value)
            for key, value in publication.data.meas.get_counts().items()
        }
    archive["job"]["status"] = str(job.status())
    archive["counts"] = counts
    archive_path.write_text(json.dumps(archive, indent=2) + "\n")
    print("IBM results retrieved and archived.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
