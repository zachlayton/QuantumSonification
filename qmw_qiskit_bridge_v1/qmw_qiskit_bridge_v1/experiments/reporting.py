"""Deterministic JSON and NPZ artifacts for the Floquet comparison study."""

from __future__ import annotations

import json
from importlib.metadata import version
from pathlib import Path
import platform
from typing import Any

import numpy as np

from .floquet_convergence import run_floquet_convergence_study
from .floquet_noise_controls import run_floquet_noise_control_study


SCHEMA = "qmw.floquet_execution_comparison.v1"


def generate_floquet_comparison_report(
    output_directory: str | Path,
    *,
    periods: int = 16,
    repetitions: tuple[int, ...] = (1, 2, 4, 8),
    noise_scales: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0),
) -> tuple[Path, Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    convergence = run_floquet_convergence_study(
        periods=periods, repetitions=repetitions
    )
    noise = run_floquet_noise_control_study(
        periods=periods, noise_scales=noise_scales
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "title": "QMW Hamiltonian execution and comparison bridge",
        "scientific_status": (
            "finite four-qubit benchmark; not evidence of a thermodynamic phase"
        ),
        "software": {
            "python": platform.python_version(),
            "numpy": version("numpy"),
            "qiskit": version("qiskit"),
            "qiskit_aer": version("qiskit-aer"),
        },
        "conventions": {
            "basis_order": "|q3 q2 q1 q0>",
            "integer_basis_index": "q0 + 2*q1 + 4*q2 + 8*q3",
            "reference_route": "qmw_dense_exact",
            "primary_state_metric": "density-matrix trace distance",
        },
        "convergence": convergence.as_dict(),
        "noise_controls": noise.as_dict(),
        "hardware": {
            "route": "ibm_runtime_v2",
            "status": "deferred",
            "requirements": [
                "credentials",
                "backend selection",
                "ISA circuit transpilation",
                "observable layout",
                "real queued execution",
            ],
        },
    }
    json_path = output / "floquet_comparison_v1.json"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    convergence_rows = convergence.points
    noise_rows = noise.points
    npz_path = output / "floquet_comparison_v1.npz"
    np.savez_compressed(
        npz_path,
        convergence_configuration=np.asarray(
            [row.configuration for row in convergence_rows]
        ),
        convergence_order=np.asarray([row.order for row in convergence_rows]),
        convergence_repetitions=np.asarray(
            [row.repetitions for row in convergence_rows]
        ),
        convergence_maximum_trace_distance=np.asarray(
            [row.maximum_trace_distance for row in convergence_rows]
        ),
        convergence_final_trace_distance=np.asarray(
            [row.final_trace_distance for row in convergence_rows]
        ),
        convergence_magnetization_rmse=np.asarray(
            [row.magnetization_rmse for row in convergence_rows]
        ),
        convergence_maximum_magnetization_error=np.asarray(
            [row.maximum_magnetization_error for row in convergence_rows]
        ),
        convergence_gates_per_period=np.asarray(
            [row.gates_per_period for row in convergence_rows]
        ),
        convergence_depth_per_period=np.asarray(
            [row.depth_per_period for row in convergence_rows]
        ),
        convergence_two_qubit_gates_per_period=np.asarray(
            [row.two_qubit_gates_per_period for row in convergence_rows]
        ),
        noise_scale=np.asarray([row.noise_scale for row in noise_rows]),
        noise_single_qubit_error=np.asarray(
            [row.single_qubit_error for row in noise_rows]
        ),
        noise_two_qubit_error=np.asarray(
            [row.two_qubit_error for row in noise_rows]
        ),
        noise_maximum_trace_distance_from_qmw=np.asarray(
            [row.maximum_trace_distance_from_qmw for row in noise_rows]
        ),
        noise_maximum_trace_distance_from_zero=np.asarray(
            [row.maximum_trace_distance_from_zero_noise for row in noise_rows]
        ),
        noise_final_purity=np.asarray([row.final_purity for row in noise_rows]),
        noise_minimum_purity=np.asarray([row.minimum_purity for row in noise_rows]),
    )
    return json_path, npz_path
