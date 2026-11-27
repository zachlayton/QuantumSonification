"""Zeeman field and Sommerfeld-style fine structure for the 4-qubit engine.

Four spin-1/2 qubits in a magnetic field B:

    H = H_fine + H_Z
    H_Z    = (nu_L / 2) * sum_q g_q Z_q              nu_L = B * hz_per_tesla
    H_fine = (J / 4)    * sum_ring (XX + YY + ZZ)    J s_q . s_{q+1}, ring 0-1-2-3-0

All energies are in audible Hz.  One spin flip costs g_q * nu_L.  As in
``zeeman_resonator_v1`` the physical scale (mu_B / h, GHz per tesla) is kept as
metadata only.

Both terms conserve total magnetisation M = sum Z / 2, so every eigenstate has
a definite M and polarisation labels are exact:

    sigma lines   Delta M = +-1   matrix elements of S+ = sum_q sigma+_q
    pi lines      Delta M =  0    matrix elements of Sz

Physics the module reproduces (see test_model.py):

* Equal g (normal Zeeman): the isotropic coupling commutes with S+, so every
  sigma line sits exactly at g * nu_L (Larmor's theorem) and the levels group
  by M into degeneracies 1, 4, 6, 4, 1 when J = 0.
* Unequal g (anomalous Zeeman): the sigma line breaks into several.
* Weak field (J >> spread of g * nu_L): lines follow total-spin multiplets with
  an averaged g.  Strong field (Paschen-Back analogue): each qubit flips at its
  own g * nu_L, split by the coupling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment

try:  # keep the physical constant in one place
    from zeeman_resonator_v1.zeeman_model import BOHR_MAGNETON_OVER_H_HZ_PER_T
except ImportError:  # pragma: no cover - standalone use
    BOHR_MAGNETON_OVER_H_HZ_PER_T = 13_996_245_550.0

NUM_QUBITS = 4
DIM = 2 ** NUM_QUBITS
RING_PAIRS = ((0, 1), (1, 2), (2, 3), (3, 0))

_I = np.eye(2, dtype=np.complex128)
_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
_SP = np.array([[0, 1], [0, 0]], dtype=np.complex128)  # |0><1| raises M (Z=+1 is |0>)


def _embed(ops: dict[int, np.ndarray]) -> np.ndarray:
    """Tensor product with qubit 0 leftmost (same order as the density engine)."""
    out = np.array([[1.0 + 0j]])
    for q in range(NUM_QUBITS):
        out = np.kron(out, ops.get(q, _I))
    return out


LOCAL = {name: [_embed({q: op}) for q in range(NUM_QUBITS)]
         for name, op in (("X", _X), ("Y", _Y), ("Z", _Z), ("+", _SP))}
S_PLUS = sum(LOCAL["+"])
S_MINUS = S_PLUS.conj().T
S_Z = 0.5 * sum(LOCAL["Z"])
S_X = 0.5 * (S_PLUS + S_MINUS)
MAGNETISATION = np.real(np.diag(S_Z))  # M of each computational basis state


# ---------------------------------------------------------------------------
# Hamiltonian
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZeemanFineConfig:
    g: tuple[float, float, float, float] = (2.0, 2.0, 2.0, 2.0)
    coupling_hz: float = 0.0          # J, fine-structure coupling
    hz_per_tesla: float = 40.0        # audible Larmor scale (matches resonator v1)

    def larmor_hz(self, field_t: float) -> float:
        return float(field_t) * self.hz_per_tesla

    def physical_larmor_hz(self, field_t: float) -> float:
        return float(field_t) * BOHR_MAGNETON_OVER_H_HZ_PER_T


PRESETS: dict[str, ZeemanFineConfig] = {
    # Lorentz's normal triplet: one g for every qubit.
    "normal": ZeemanFineConfig(g=(2.0, 2.0, 2.0, 2.0), coupling_hz=6.0),
    # Lande values 2, 4/3, 2/3 and 1 (s1/2, p3/2, p1/2, normal): anomalous.
    "anomalous": ZeemanFineConfig(g=(2.0, 4.0 / 3.0, 2.0 / 3.0, 1.0), coupling_hz=6.0),
    # Sommerfeld's scale: coupling alpha^2 of a nominal 1 kHz gross structure.
    "alpha_squared": ZeemanFineConfig(g=(2.0, 4.0 / 3.0, 2.0 / 3.0, 1.0),
                                      coupling_hz=1000.0 / 137.035999 ** 2),
    # No coupling: four independent spins (pure Paschen-Back limit).
    "free_spins": ZeemanFineConfig(g=(2.0, 4.0 / 3.0, 2.0 / 3.0, 1.0), coupling_hz=0.0),
}


def zeeman_operator(config: ZeemanFineConfig, field_t: float) -> np.ndarray:
    nu = config.larmor_hz(field_t)
    return 0.5 * nu * sum(g * z for g, z in zip(config.g, LOCAL["Z"]))


def fine_operator(config: ZeemanFineConfig) -> np.ndarray:
    h = np.zeros((DIM, DIM), dtype=np.complex128)
    for a, b in RING_PAIRS:
        for name in ("X", "Y", "Z"):
            h += LOCAL[name][a] @ LOCAL[name][b]
    return 0.25 * config.coupling_hz * h


def hamiltonian(config: ZeemanFineConfig, field_t: float) -> np.ndarray:
    return fine_operator(config) + zeeman_operator(config, field_t)


# ---------------------------------------------------------------------------
# Spectrum, polarisation, line list
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Line:
    shift_hz: float        # signed: sigma+ at carrier + shift, sigma- at carrier - shift
    strength: float
    polarization: str      # "sigma" or "pi"
    upper: int             # eigen-index (tracked index when produced by a sweep)
    lower: int


@dataclass
class ZeemanFrame:
    field_t: float
    larmor_hz: float
    physical_larmor_hz: float
    energies_hz: np.ndarray
    states: np.ndarray
    magnetisation: np.ndarray
    lines: list[Line] = field(default_factory=list)

    def as_dict(self, carrier_hz: float = 220.0) -> dict[str, object]:
        """Serializable snapshot for OSC/UI, in the style of resonator v1."""
        voices = []
        for line in self.lines:
            voices.append({
                "polarization": line.polarization,
                "shift_hz": line.shift_hz,
                "upper_hz": carrier_hz + abs(line.shift_hz),
                "lower_hz": carrier_hz - abs(line.shift_hz),
                "strength": line.strength,
                "levels": [line.upper, line.lower],
            })
        return {
            "field_t": self.field_t,
            "larmor_hz": self.larmor_hz,
            "physical_larmor_hz": self.physical_larmor_hz,
            "carrier_hz": carrier_hz,
            "energies_hz": [float(e) for e in self.energies_hz],
            "magnetisation": [float(m) for m in self.magnetisation],
            "lines": voices,
        }


def diagonalise(h: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Eigenpairs with definite magnetisation (block-diagonalise by M)."""
    energies = np.empty(DIM)
    states = np.zeros((DIM, DIM), dtype=np.complex128)
    mags = np.empty(DIM)
    col = 0
    for m in np.unique(MAGNETISATION):
        idx = np.flatnonzero(np.isclose(MAGNETISATION, m))
        e, v = np.linalg.eigh(h[np.ix_(idx, idx)])
        for k in range(len(idx)):
            energies[col] = e[k]
            states[idx, col] = v[:, k]
            mags[col] = m
            col += 1
    return energies, states, mags


def line_list(energies: np.ndarray, states: np.ndarray, mags: np.ndarray,
              populations: np.ndarray | None = None,
              min_strength: float = 1e-9) -> list[Line]:
    """All allowed lines.  Strength = |matrix element|^2 x mean population.

    Population weighting is a perceptual default (uniform = maximally mixed
    state, every allowed line audible); pass populations to follow a state.
    """
    p = np.full(DIM, 1.0 / DIM) if populations is None else np.asarray(populations, float)
    sp = states.conj().T @ S_PLUS @ states
    sz = states.conj().T @ S_Z @ states
    lines: list[Line] = []
    for a in range(DIM):
        for b in range(DIM):
            w = 0.5 * (p[a] + p[b])
            if np.isclose(mags[a], mags[b] + 1.0):
                s = abs(sp[a, b]) ** 2 * w
                if s > min_strength:
                    lines.append(Line(energies[a] - energies[b], s, "sigma", a, b))
            elif a > b and np.isclose(mags[a], mags[b]):
                s = abs(sz[a, b]) ** 2 * w
                if s > min_strength:
                    hi, lo = (a, b) if energies[a] >= energies[b] else (b, a)
                    lines.append(Line(abs(energies[a] - energies[b]), s, "pi", hi, lo))
    return lines


def merge_lines(lines: Iterable[Line], tol_hz: float = 1e-6) -> list[tuple[str, float, float]]:
    """Collapse degenerate lines: [(polarization, shift_hz, total_strength)]."""
    merged: list[list] = []
    for line in sorted(lines, key=lambda l: (l.polarization, l.shift_hz)):
        if merged and merged[-1][0] == line.polarization and abs(merged[-1][1] - line.shift_hz) < tol_hz:
            merged[-1][2] += line.strength
        else:
            merged.append([line.polarization, line.shift_hz, line.strength])
    return [tuple(m) for m in merged]


def frame(config: ZeemanFineConfig, field_t: float,
          populations: np.ndarray | None = None) -> ZeemanFrame:
    e, v, m = diagonalise(hamiltonian(config, field_t))
    return ZeemanFrame(field_t, config.larmor_hz(field_t), config.physical_larmor_hz(field_t),
                       e, v, m, line_list(e, v, m, populations))


# ---------------------------------------------------------------------------
# Field sweep with level tracking by overlap
# ---------------------------------------------------------------------------

def sweep(config: ZeemanFineConfig, fields_t: Sequence[float]) -> list[ZeemanFrame]:
    """Frames along a field sweep with levels kept in a consistent order.

    Each new eigenbasis is matched to the previous one by maximum |overlap|^2
    (Hungarian assignment), so a level keeps its index through avoided
    crossings and voices do not jump.  Line indices refer to tracked levels.
    """
    frames: list[ZeemanFrame] = []
    prev = None
    for b in fields_t:
        e, v, m = diagonalise(hamiltonian(config, b))
        if prev is not None:
            overlap = np.abs(prev.conj().T @ v) ** 2
            rows, cols = linear_sum_assignment(-overlap)
            order = cols[np.argsort(rows)]
            e, v, m = e[order], v[:, order], m[order]
            # fix the arbitrary global phase so states move continuously
            phase = np.angle(np.sum(prev.conj() * v, axis=0))
            v = v * np.exp(-1j * phase)
        prev = v
        frames.append(ZeemanFrame(b, config.larmor_hz(b), config.physical_larmor_hz(b),
                                  e, v, m, line_list(e, v, m)))
    return frames


# ---------------------------------------------------------------------------
# Scattering: quantum beats and the Hanle effect
# ---------------------------------------------------------------------------

def coherent_x_state() -> np.ndarray:
    """All four spins along +x: a coherent superposition of every M."""
    plus = np.array([1.0, 1.0], dtype=np.complex128) / np.sqrt(2.0)
    psi = np.array([1.0 + 0j])
    for _ in range(NUM_QUBITS):
        psi = np.kron(psi, plus)
    return psi


def quantum_beats(config: ZeemanFineConfig, field_t: float, duration_s: float,
                  sample_rate: int = 44_100, decay_hz: float = 2.0,
                  psi0: np.ndarray | None = None,
                  observable: np.ndarray = S_X) -> np.ndarray:
    """<O(t)> exp(-Gamma t) after a coherent excitation, sampled at audio rate.

    Frequencies are Bohr differences in audible Hz, so the result is directly
    an audio signal: the Zeeman sublevels beating as they dephase.
    """
    psi0 = coherent_x_state() if psi0 is None else np.asarray(psi0, np.complex128)
    e, v, _ = diagonalise(hamiltonian(config, field_t))
    c = v.conj().T @ psi0
    o = v.conj().T @ observable @ v
    amp = (np.conj(c)[:, None] * c[None, :]) * o          # A_ab
    freq = e[:, None] - e[None, :]                         # Hz
    keep = np.abs(amp) > 1e-12
    amp, freq = amp[keep], freq[keep]
    t = np.arange(int(duration_s * sample_rate)) / sample_rate
    signal = np.zeros_like(t)
    for chunk in range(0, t.size, 8192):
        tt = t[chunk:chunk + 8192]
        signal[chunk:chunk + 8192] = np.real(
            np.exp(2j * np.pi * np.outer(tt, freq)) @ amp)
    return signal * np.exp(-decay_hz * t)


def hanle_polarization(config: ZeemanFineConfig, field_t: float | np.ndarray,
                       g: float, lifetime_s: float) -> np.ndarray:
    """Linear polarisation of resonance-scattered light vs field (Hanle 1924).

    P(B) / P(0) = 1 / (1 + (2 omega_L tau)^2),  omega_L = 2 pi g nu_L(B).
    Half polarisation where 2 omega_L tau = 1.
    """
    omega = 2.0 * np.pi * g * np.asarray(field_t, float) * config.hz_per_tesla
    return 1.0 / (1.0 + (2.0 * omega * lifetime_s) ** 2)


# ---------------------------------------------------------------------------
# Directivity and Ambisonic encoding
# ---------------------------------------------------------------------------

def dipole_pattern(polarization: str, cos_theta: np.ndarray) -> np.ndarray:
    """Radiated intensity vs angle to the field axis.

    pi (Delta M = 0): sin^2 theta.  sigma (Delta M = +-1): (1 + cos^2 theta) / 2.
    pi + sigma+ + sigma- is isotropic (= 2).
    """
    c2 = np.asarray(cos_theta) ** 2
    if polarization == "pi":
        return 1.0 - c2
    if polarization in ("sigma", "sigma+", "sigma-"):
        return 0.5 * (1.0 + c2)
    raise ValueError(polarization)


def _fibonacci_sphere(n: int = 4000) -> np.ndarray:
    k = np.arange(n) + 0.5
    z = 1.0 - 2.0 * k / n
    r = np.sqrt(1.0 - z * z)
    phi = np.pi * (1.0 + 5 ** 0.5) * k
    return np.column_stack([r * np.cos(phi), r * np.sin(phi), z])


def real_sh_sn3d(dirs: np.ndarray) -> np.ndarray:
    """Real spherical harmonics, ACN order, SN3D (AmbiX), orders 0-2."""
    x, y, z = dirs[:, 0], dirs[:, 1], dirs[:, 2]
    s3 = np.sqrt(3.0)
    return np.column_stack([
        np.ones_like(x),                 # 0  W
        y, z, x,                         # 1-3 Y Z X
        s3 * x * y,                      # 4  V
        s3 * y * z,                      # 5  T
        0.5 * (3.0 * z * z - 1.0),       # 6  R
        s3 * x * z,                      # 7  S
        0.5 * s3 * (x * x - y * y),      # 8  U
    ])


_GRID = _fibonacci_sphere()
_SH = real_sh_sn3d(_GRID)


def directivity_ambisonics(polarization: str, field_axis: Sequence[float] = (0.0, 0.0, 1.0)) -> np.ndarray:
    """Second-order AmbiX coefficients of a Zeeman component's radiation pattern.

    The pattern is spread around the listener as an extended source and
    normalised so W = 1.  With the field along z: pi gives R = -0.2,
    sigma gives R = +0.1, and all first-order terms vanish.
    """
    axis = np.asarray(field_axis, float)
    axis = axis / np.linalg.norm(axis)
    f = dipole_pattern(polarization, _GRID @ axis)
    return (f @ _SH) / f.sum()
