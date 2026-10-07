"""Validated two-spin state input. Kinematics never manufacture a spin state."""

from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
import numpy as np

from collider_001a.backend import ColliderBackend
from collider_001a.io import _reject_constant, _unique_object
from collider_001a.model import nonempty_text

STATE_SCHEMA = "collider-density-bins/1"
TOLERANCE = 1e-10
FREQUENCIES_HZ = (55.0, 110.0, 165.0, 220.0)


@dataclass(frozen=True)
class ValidatedSpectrum:
    eigenvalues: tuple[float, ...]
    rho_real: tuple[tuple[float, ...], ...]
    rho_imag: tuple[tuple[float, ...], ...]
    hermiticity_error: float
    trace_error: float
    minimum_raw_eigenvalue: float
    roundoff_correction_frobenius: float


def validate_density_matrix(rho) -> ValidatedSpectrum:
    """Reject invalid states; report any accepted, tolerance-sized correction.

    eigh alone ignores the unused triangle and imaginary diagonal, so both
    Hermiticity and the full complex trace are checked BEFORE diagonalization.
    Eigenvalues label descending ranks, not persistent eigenvector identities.
    """
    try:
        original = np.array(rho, dtype=np.complex128, copy=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("rho must be a finite complex 4x4 matrix") from exc
    if original.shape != (4, 4) or not np.isfinite(original).all():
        raise ValueError("rho must be a finite complex 4x4 matrix")
    herm_error = float(np.max(np.abs(original - original.conj().T)))
    trace_error = float(abs(np.trace(original) - 1))
    if herm_error > TOLERANCE:
        raise ValueError("rho is not Hermitian")
    if trace_error > TOLERANCE:
        raise ValueError("rho must have trace one")
    hermitian = (original + original.conj().T) / 2
    values, vectors = np.linalg.eigh(hermitian)
    if values[0] < -TOLERANCE:
        raise ValueError("rho is not positive semidefinite")
    if values[-1] > 1 + TOLERANCE:
        raise ValueError("rho eigenvalue exceeds one")
    clipped = np.maximum(values, 0)
    normalized = clipped / clipped.sum()
    canonical = (vectors * normalized) @ vectors.conj().T
    # Only tolerance-sized cleanup is permitted; no general physical-state fit.
    correction = float(np.linalg.norm(canonical - original))
    return ValidatedSpectrum(
        tuple(float(x) for x in normalized[::-1]),
        tuple(tuple(float(x) for x in row) for row in canonical.real),
        tuple(tuple(float(x) for x in row) for row in canonical.imag),
        herm_error, trace_error, float(values[0]), correction,
    )


@dataclass(frozen=True)
class StateTable:
    provenance: dict
    basis: dict
    states: dict[int, ValidatedSpectrum]
    labels: dict[int, str]
    input_sha256: str
    input_path: str
    event_input_sha256: str
    event_dataset_id: str
    edges_gev: tuple[float, ...]


def fixture_document(backend: ColliderBackend) -> dict:
    """An explicitly invented path between a pure state and I/4.

    Mass bins index the fixture; neither event counts nor kinematics estimate rho.
    """
    if backend.dataset.input_sha256 is None:
        raise ValueError("save and load the event dataset first to establish its fingerprint")
    n = len(backend.summary()["bins"])
    psi = np.array([1, 1j, 1, -1j], dtype=complex) / 2
    pure = np.outer(psi, psi.conj())
    rows = []
    for index in range(n):
        alpha = index / (n - 1) if n > 1 else 0.0
        rho = (1 - alpha) * pure + alpha * np.eye(4) / 4
        rows.append({"bin_index": index, "label": f"Test fixture alpha={alpha:.6f}",
                     "rho_real": rho.real.tolist(), "rho_imag": rho.imag.tolist()})
    return {
        "schema_version": STATE_SCHEMA, "axis": "m_ttbar", "mass_unit": "GeV",
        "natural_units": "c=1", "event_dataset_id": backend.dataset.provenance.dataset_id,
        "event_input_sha256": backend.dataset.input_sha256,
        "edges_gev": list(backend.bins.edges_gev),
        "basis": {"order": ["00", "01", "10", "11"],
                  "subsystems": ["top", "antitop"],
                  "description": "Abstract two-qubit computational basis; no collider spin-axis calibration"},
        "provenance": {
            "source_kind": "test_fixture", "source_uri": "fixture://001b/pure-to-mixed-v1",
            "description": "Mathematical test states assigned to mass bins, not reconstructed from collisions.",
            "method": "rho_i=(1-alpha_i)|psi><psi|+alpha_i*I/4; "
                      "psi=(1,i,1,-i)/2; alpha_i=i/(number_of_bins-1), or 0 for one bin",
            "uncertainty": "Not applicable to exact fixtures; no event-derived uncertainty model",
        }, "bins": rows,
    }


def save_fixture(backend: ColliderBackend, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fixture_document(backend), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return path


def load_states(path: str | Path, backend: ColliderBackend) -> StateTable:
    path = Path(path).resolve()
    raw = path.read_bytes()
    try:
        data = json.loads(raw, parse_constant=_reject_constant, object_pairs_hook=_unique_object)
        required = {"schema_version", "axis", "mass_unit", "natural_units", "event_dataset_id",
                    "event_input_sha256", "edges_gev", "basis", "provenance", "bins"}
        if not isinstance(data, dict) or set(data) != required:
            raise ValueError("state document fields do not match collider-density-bins/1")
        if (data["schema_version"], data["axis"], data["mass_unit"], data["natural_units"]) != (
            STATE_SCHEMA, "m_ttbar", "GeV", "c=1"
        ):
            raise ValueError("unsupported state schema, axis or units")
        if backend.dataset.input_sha256 is None or (
            data["event_input_sha256"] != backend.dataset.input_sha256
            or data["event_dataset_id"] != backend.dataset.provenance.dataset_id
        ):
            raise ValueError("state table is not linked to this event dataset and fingerprint")
        if data["edges_gev"] != list(backend.bins.edges_gev):
            raise ValueError("state table mass bins differ from the event backend")
        basis = data["basis"]
        if (basis["order"] != ["00", "01", "10", "11"]
                or basis["subsystems"] != ["top", "antitop"]):
            raise ValueError("basis must declare 00,01,10,11 with top then antitop")
        nonempty_text(basis["description"], "basis description")
        provenance = data["provenance"]
        if provenance["source_kind"] not in ("test_fixture", "supplied_density_matrices"):
            raise ValueError("state source_kind must be test_fixture or supplied_density_matrices")
        for name in ("source_uri", "description", "method", "uncertainty"):
            nonempty_text(provenance[name], name)
        if not isinstance(data["bins"], list):
            raise ValueError("bins must be a list")
        states, labels = {}, {}
        for row in data["bins"]:
            if set(row) != {"bin_index", "label", "rho_real", "rho_imag"}:
                raise ValueError("state row must contain bin_index, label, rho_real, rho_imag")
            index = row["bin_index"]
            if type(index) is not int or not 0 <= index < len(backend.bins.edges_gev) - 1:
                raise ValueError("state bin_index out of range")
            if index in states:
                raise ValueError("duplicate state bin_index")
            nonempty_text(row["label"], "state label")
            parts = []
            for key in ("rho_real", "rho_imag"):
                part = np.asarray(row[key])
                if part.shape != (4, 4) or part.dtype.kind not in "fiu":
                    raise ValueError(f"{key} must be a numeric 4x4 array")
                parts.append(part.astype(float))
            states[index] = validate_density_matrix(parts[0] + 1j * parts[1])
            labels[index] = row["label"]
        return StateTable(provenance, basis, states, labels,
                          hashlib.sha256(raw).hexdigest(), str(path),
                          data["event_input_sha256"], data["event_dataset_id"], tuple(data["edges_gev"]))
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"invalid state table {path.name}: {exc}") from exc


class ColliderSpectralBackend:
    """Join independently supplied ensemble states to an authoritative 001A backend."""

    def __init__(self, kinematics: ColliderBackend, states: StateTable):
        if (states.event_input_sha256 != kinematics.dataset.input_sha256
                or states.event_dataset_id != kinematics.dataset.provenance.dataset_id
                or states.edges_gev != kinematics.bins.edges_gev):
            raise ValueError("state table does not match the kinematic backend")
        self.kinematics = kinematics
        self.states = states
        self._phases = kinematics.summary()["bins"]

    def select_mass(self, mass_gev: float) -> dict:
        self.kinematics.select_mass(mass_gev)
        return self.current_frame

    def select_bin(self, index: int) -> dict:
        self.kinematics.select_bin(index)
        return self.current_frame

    def frame(self, index: int) -> dict:
        if type(index) is not int or not 0 <= index < len(self._phases):
            raise IndexError("bin index is out of range")
        phase = self._phases[index]
        spectrum = self.states.states.get(index)
        status = ("empty_bin" if phase["statistics"]["count"] == 0 else
                  "missing_state" if spectrum is None else "ready")
        usable = spectrum if status == "ready" else None
        return {
            "schema_version": "collider-spectral-frame/1", "phase_space": phase,
            "status": status, "state_source_kind": self.states.provenance["source_kind"],
            "state_label": self.states.labels.get(index),
            "state_file_sha256": self.states.input_sha256,
            "spectrum": asdict(usable) if usable else None,
            "sonification": {"schema_version": "four-mode-gains/1",
                             "frequencies_hz": FREQUENCIES_HZ,
                             "amplitudes": usable.eigenvalues if usable else (0.0,) * 4,
                             "mapping": "amplitude_k = descending_eigenvalue_k",
                             "rank_order": "descending; no eigenvector tracking",
                             "muted": status != "ready"},
        }

    @property
    def current_frame(self) -> dict:
        return self.frame(self.kinematics.selected_index)

    def summary(self) -> dict:
        return {"experiment": "CERN/QMW 001B", "kinematics": self.kinematics.summary(),
                "state_provenance": self.states.provenance, "basis": self.states.basis,
                "state_input_path": self.states.input_path,
                "state_input_sha256": self.states.input_sha256,
                "tolerance": TOLERANCE,
                "frames": [self.frame(i) for i in range(len(self.kinematics.bins.edges_gev) - 1)]}
