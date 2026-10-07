"""Check the installed environment and existing local numerical foundations.

This is environment acceptance, not acceptance of the proposed architecture.
No network request, audio output, OSC send, or authoritative state is started.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import platform
import site
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENV = ROOT / ".venv-qmw-architecture"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metal", action="store_true", help="Also check the Mac GPU and legacy resonator import; requires Metal access")
    parser.add_argument("--report", type=Path, help="Save the verification result as JSON")
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != VENV.resolve() or sys.prefix == sys.base_prefix:
        raise RuntimeError("Run with environment/qmw_architecture/run-python")
    if site.ENABLE_USER_SITE:
        raise RuntimeError("User site packages must be disabled")
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("This environment was validated with Python 3.12")
    if "include-system-site-packages = false" not in (VENV / "pyvenv.cfg").read_text():
        raise RuntimeError("The venv must not inherit system site packages")
    versions = {}
    lock = Path(__file__).with_name("requirements.lock.txt")
    for line in lock.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, expected = line.split("==")
        dist = importlib.metadata.distribution(name)
        if dist.version != expected:
            raise RuntimeError(f"{name}: expected {expected}, got {dist.version}")
        if not Path(dist.locate_file("")).resolve().is_relative_to(VENV.resolve()):
            raise RuntimeError(f"{name} imported from outside the isolated environment")
        versions[name] = dist.version
    subprocess.run([sys.executable, "-m", "pip", "--no-cache-dir", "check"], check=True)

    import numpy as np
    from scipy.linalg import expm
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector, partial_trace
    from qmw.qmw_representation_laboratory_v4.transforms.hamiltonian import HamiltonianEigenbasis
    from qmw.qmw_representation_laboratory_v4.transforms.qft import QFTOperator
    from qmw.architecture_v1.upstream import load_collider_runtime, load_decay_runtime, load_lorentz_frame_type

    source_imports = {}
    for name in ["qmw.architecture_v1.basis", "qmw.architecture_v1.resources",
                 "qmw.architecture_v1.measurement", "qmw.architecture_v1.correlations",
                 "qmw.qmw_representation_laboratory_v4", "full4q_tomography_v1"]:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        if not path.is_relative_to(ROOT):
            raise RuntimeError(f"{name} resolved outside this checkout: {path}")
        source_imports[name] = str(path.relative_to(ROOT))
    collider = load_collider_runtime()
    decay = load_decay_runtime()
    load_lorentz_frame_type()
    source_imports["collider_runtime"] = str(Path(collider.root).relative_to(ROOT))
    source_imports["decay_archive"] = str(Path(decay.archive).relative_to(ROOT))

    rng = np.random.default_rng(615)
    a = rng.normal(size=(16, 16)) + 1j * rng.normal(size=(16, 16))
    rho = a @ a.conj().T
    rho /= np.trace(rho)
    h = a + a.conj().T
    original = rho.copy()
    round_trips = {}
    for name, basis in [("hamiltonian", HamiltonianEigenbasis(h)), ("qft", QFTOperator())]:
        u = basis.unitary(16)
        projected = u @ rho @ u.conj().T
        error = float(np.linalg.norm(u.conj().T @ projected @ u - rho))
        if error > 1e-10:
            raise RuntimeError(f"{name} round trip failed: {error}")
        round_trips[name] = error
    np.testing.assert_array_equal(rho, original)
    unitary = expm(-1j * h * 0.01)
    np.testing.assert_allclose(unitary.conj().T @ unitary, np.eye(16), atol=1e-12)
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    state = Statevector.from_instruction(circuit)
    np.testing.assert_allclose(partial_trace(state, [1]).data, np.eye(2) / 2, atol=1e-12)

    # Import actual authority/renderer seams without instantiating a live engine.
    for module in ["pythonosc", "librosa", "sklearn", "density.density_matrix_engine_4q"]:
        importlib.import_module(module)
    metal = {"status": "not_requested", "legacy_resonator_import": "not_requested"}
    if args.metal:
        import mlx.core as mx
        if not mx.metal.is_available():
            raise RuntimeError("Metal is unavailable; run this optional check with host GPU access")
        matrix = mx.array([[1.0, 2.0], [3.0, 4.0]])
        with mx.stream(mx.gpu):
            product = matrix @ matrix
            mx.eval(product)
        np.testing.assert_allclose(np.array(product), [[7.0, 10.0], [15.0, 22.0]])
        importlib.import_module("quantum_population_osc_v9_resonator")
        metal = {"status": "passed", "device": "gpu:0", "legacy_resonator_import": "passed"}
    report = {
        "status": "passed",
        "scope": "isolated local numerical environment and relocated source verification; no live acceptance",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "executable": sys.executable,
        "include_system_site_packages": False,
        "versions": versions,
        "basis_round_trip_errors": round_trips,
        "scipy_unitary_and_qiskit_bell_checks": "passed",
        "density_import": "passed",
        "source_imports": source_imports,
        "approved_upstream_fingerprints": "passed",
        "metal": metal,
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
