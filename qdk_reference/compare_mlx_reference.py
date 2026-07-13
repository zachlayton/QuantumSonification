"""Compare an MLX-produced 4-qubit rho with the canonical reference rho.

Usage from the QuantumSonification project root:
    python qdk_reference/compare_mlx_reference.py

Before use, edit `get_live_mlx_rho()` to import the existing engine and
return its current 16x16 density matrix as an MLX array or NumPy array.
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from qdk_reference_simulator import reference_density_matrix, density_metrics


def to_numpy(value) -> np.ndarray:
    """Accept NumPy or MLX arrays without hard-depending on MLX."""
    if hasattr(value, "tolist"):
        return np.asarray(value.tolist(), dtype=np.complex128)
    return np.asarray(value, dtype=np.complex128)


def compare_density_matrices(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    if reference.shape != (16, 16) or candidate.shape != (16, 16):
        raise ValueError(
            f"Expected two 16x16 matrices; got {reference.shape} and {candidate.shape}."
        )

    delta = candidate - reference
    return {
        "max_abs_error": float(np.max(np.abs(delta))),
        "frobenius_error": float(np.linalg.norm(delta)),
        "candidate_trace_real": float(np.trace(candidate).real),
        "candidate_purity": float(np.trace(candidate @ candidate).real),
    }


def get_live_mlx_rho():
    # Replace this block after identifying the live engine's exact accessor.
    #
    # Example:
    # from density.density_matrix_engine_4q import DensityMatrixEngine
    # engine = DensityMatrixEngine()
    # engine.set_circuit_score(...)  # only after we add this API
    # engine.step(0.0)
    # return engine.rho
    raise NotImplementedError(
        "Wire this function to the current MLX engine's density matrix accessor."
    )


if __name__ == "__main__":
    reference = reference_density_matrix()
    print("Reference invariants:", density_metrics(reference))

    try:
        candidate = to_numpy(get_live_mlx_rho())
    except NotImplementedError as error:
        print(f"\n{error}")
        print("The canonical reference simulator itself is working.")
        raise SystemExit(0)

    report = compare_density_matrices(reference, candidate)
    print("\nMLX comparison:")
    for key, value in report.items():
        print(f"{key}: {value:.12e}")
