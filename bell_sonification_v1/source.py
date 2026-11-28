"""Shot sources for the Bell-pair sonification.

Three sources, one output shape: a list of shots, each a pair (a, b) of bits,
plus a provenance dict that says where the shots came from.

* ``ideal``  exact quantum probabilities sampled with numpy (no Qiskit needed;
             fast enough for live control)
* ``aer``    the Qiskit circuit run on the Aer simulator, shot by shot
* ``ibm``    the same circuit on IBM hardware through SamplerV2 (needs a saved
             QiskitRuntimeService account; untested in this repo's CI)

Circuits
--------
``entangled``    H on A, CNOT A->B: the Bell state (|00> + |11>)/sqrt2
``independent``  H on A and H on B: two separate fair coins

Before measurement B can be rotated by an angle theta (Ry(-theta)), which
measures B along an axis tilted by theta in the x-z plane. For the Bell state
P(agree) = cos^2(theta/2) and the correlation E = P(agree) - P(disagree) = cos(theta).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

KINDS = ("entangled", "independent")


@dataclass
class ShotRun:
    kind: str
    theta: float
    shots: np.ndarray              # shape (n, 2): columns a, b
    provenance: dict = field(default_factory=dict)

    @property
    def agree(self) -> np.ndarray:
        return self.shots[:, 0] == self.shots[:, 1]

    @property
    def correlation(self) -> float:
        return float(np.mean(np.where(self.agree, 1.0, -1.0)))


def ideal_probabilities(kind: str, theta: float) -> np.ndarray:
    """P(00), P(01), P(10), P(11) with bits written (a, b)."""
    if kind == "entangled":
        c, s = np.cos(theta / 2) ** 2, np.sin(theta / 2) ** 2
        return np.array([c, s, s, c]) / 2.0
    if kind == "independent":
        return np.full(4, 0.25)
    raise ValueError(kind)


def sample_ideal(kind: str, theta: float, n: int, seed: int | None = None) -> ShotRun:
    rng = np.random.default_rng(seed)
    idx = rng.choice(4, size=n, p=ideal_probabilities(kind, theta))
    shots = np.column_stack([idx >> 1, idx & 1]).astype(np.int8)
    return ShotRun(kind, theta, shots, {"source": "ideal", "seed": seed, "shots": n,
                                       "created": _now()})


def bell_circuit(kind: str = "entangled", theta: float = 0.0):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2, 2, name=f"{kind}_theta{theta:.4f}")
    qc.h(0)
    if kind == "entangled":
        qc.cx(0, 1)
    elif kind == "independent":
        qc.h(1)
    else:
        raise ValueError(kind)
    if theta:
        qc.ry(-theta, 1)
    qc.measure(0, 0)   # clbit 0 = A
    qc.measure(1, 1)   # clbit 1 = B
    return qc


def _bits_from_strings(strings: Iterable[str]) -> np.ndarray:
    # Qiskit writes clbits right to left: "b a"
    return np.array([[int(s[-1]), int(s[-2])] for s in strings], dtype=np.int8)


def sample_aer(kind: str, theta: float, n: int, seed: int | None = None) -> ShotRun:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    qc = transpile(bell_circuit(kind, theta), sim)
    mem = sim.run(qc, shots=n, memory=True, seed_simulator=seed).result().get_memory()
    return ShotRun(kind, theta, _bits_from_strings(mem),
                   {"source": "aer", "backend": "aer_simulator", "seed": seed,
                    "shots": n, "created": _now()})


def sample_ibm(kind: str, thetas: Sequence[float], n: int, account: str | None = None,
               backend_name: str | None = None, archive_dir: Path | None = None) -> list[ShotRun]:
    """Run one circuit per angle on IBM hardware; returns shots in measured order.

    Writes a provenance archive (backend, job id, date, shots, circuits) so the
    source can be named from the stage.
    """
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    service = QiskitRuntimeService(name=account) if account else QiskitRuntimeService()
    backend = (service.backend(backend_name) if backend_name
               else service.least_busy(operational=True, simulator=False, min_num_qubits=2))
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    circuits = [bell_circuit(kind, t) for t in thetas]
    job = SamplerV2(mode=backend).run(pm.run(circuits), shots=n)
    result = job.result()
    bname = backend.name if hasattr(backend, "name") else str(backend)
    prov = {"source": "ibm", "backend": bname, "job_id": job.job_id(), "shots": n,
            "kind": kind, "thetas": [float(t) for t in thetas], "created": _now()}
    runs = []
    for t, pub in zip(thetas, result):
        strings = pub.data.c.get_bitstrings()
        runs.append(ShotRun(kind, float(t), _bits_from_strings(strings), dict(prov, theta=float(t))))
    if archive_dir is not None:
        archive_dir = Path(archive_dir)
        archive_dir.mkdir(parents=True, exist_ok=True)
        payload = dict(prov, runs=[{"theta": r.theta, "shots": r.shots.tolist()} for r in runs])
        (archive_dir / f"bell_{prov['job_id']}.json").write_text(json.dumps(payload))
    return runs


def load_archive(path: Path) -> list[ShotRun]:
    """Replay recorded hardware shots (archived source)."""
    payload = json.loads(Path(path).read_text())
    prov = {k: v for k, v in payload.items() if k != "runs"}
    prov["source"] = "archived " + prov.get("source", "")
    return [ShotRun(prov.get("kind", "entangled"), r["theta"], np.array(r["shots"], dtype=np.int8),
                    dict(prov, theta=r["theta"])) for r in payload["runs"]]


def sample(source: str, kind: str, theta: float, n: int, seed: int | None = None) -> ShotRun:
    if source == "ideal":
        return sample_ideal(kind, theta, n, seed)
    if source == "aer":
        return sample_aer(kind, theta, n, seed)
    raise ValueError("use sample_ibm() or load_archive() for hardware shots")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
