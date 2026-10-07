"""V4.1 observer for coherent first-moment energy transport on a QFT lattice.

This module is deliberately an observer.  ``ScalarFieldFrame`` remains the
authoritative Gaussian quantum-field state; its covariance is neither thrown
away nor reinterpreted as a sixteen-state density matrix here.  The V4.1
payload describes only the transport carried by the field's first moments.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from .live_osc_v4 import SCHEMA as SOURCE_SCHEMA
from .model import ScalarFieldModel
from .schema import ScalarFieldFrame


SCHEMA = "qmw.scalar_field.first_moment_flow.v4_1"
OSC_ROOT = "/qmw/qft/v4_1/flow"
OUTPUT_PORT = 17862
EPSILON = 1.0e-12


@dataclass(frozen=True)
class FirstMomentFlowContinuity:
    """Finite-difference check of the discrete first-moment energy balance."""

    dt: float | None = None
    local_l2: float | None = None
    local_linf: float | None = None
    global_residual: float | None = None


@dataclass(frozen=True)
class FirstMomentFlowFrame:
    """Site- and real-Fourier-basis transport derived from one field frame."""

    time: float
    sites: int
    lattice_spacing: float
    mass: float
    propagation_speed: float
    mean_phi: np.ndarray
    mean_pi: np.ndarray
    site_energy: np.ndarray
    bond_current: np.ndarray
    net_inflow: np.ndarray
    mode_phi: np.ndarray
    mode_pi: np.ndarray
    mode_energy: np.ndarray
    mode_wave_numbers: np.ndarray
    mode_component_codes: np.ndarray
    total_coherent_energy: float
    current_l1: float
    conservation_error: float
    continuity_residual: np.ndarray | None
    continuity: FirstMomentFlowContinuity


def _finite_vector(name: str, values: Any, sites: int) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.shape != (sites,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must be a finite vector with {sites} values")
    return np.array(vector, dtype=float, copy=True)


def _mode_wave_numbers(sites: int) -> np.ndarray:
    values = [0]
    for wave_number in range(1, (sites + 1) // 2):
        values.extend((wave_number, wave_number))
    if sites % 2 == 0:
        values.append(sites // 2)
    return np.asarray(values, dtype=int)


def _mode_component_codes(sites: int) -> np.ndarray:
    """0=DC, 1=cosine, 2=sine, 3=Nyquist in model.mode_vectors order."""

    values = [0]
    for _ in range(1, (sites + 1) // 2):
        values.extend((1, 2))
    if sites % 2 == 0:
        values.append(3)
    return np.asarray(values, dtype=int)


def build_first_moment_flow_frame(
    frame: ScalarFieldFrame,
    model: ScalarFieldModel,
    *,
    previous: FirstMomentFlowFrame | None = None,
) -> FirstMomentFlowFrame:
    """Project a scalar-field frame into exact lattice first-moment transport.

    With bond ``j`` directed from site ``j`` to ``j + 1 (mod N)``, the current
    is ``-g/2 * (pi_j + pi_{j+1}) * (phi_{j+1} - phi_j)`` where
    ``g = (c / a)^2``.  The symmetric site-energy convention makes
    ``d e_j / dt = J_{j-1} - J_j`` for the free lattice first moments.
    """

    sites = model.spec.sites
    if frame.sites != sites:
        raise ValueError("frame and model must have the same site count")
    time = float(frame.time)
    if not math.isfinite(time):
        raise ValueError("frame time must be finite")

    phi = _finite_vector("frame.mean_phi", frame.mean_phi, sites)
    pi = _finite_vector("frame.mean_pi", frame.mean_pi, sites)
    right_phi = np.roll(phi, -1)
    right_pi = np.roll(pi, -1)
    left_phi = np.roll(phi, 1)
    coupling = (model.spec.propagation_speed / model.spec.lattice_spacing) ** 2

    site_energy = (
        0.5 * pi**2
        + 0.5 * model.spec.mass**2 * phi**2
        + 0.25 * coupling * ((right_phi - phi) ** 2 + (phi - left_phi) ** 2)
    )
    bond_current = -0.5 * coupling * (pi + right_pi) * (right_phi - phi)
    net_inflow = np.roll(bond_current, 1) - bond_current

    mode_phi = model.mode_vectors.T @ phi
    mode_pi = model.mode_vectors.T @ pi
    mode_energy = 0.5 * (mode_pi**2 + (model.frequencies * mode_phi) ** 2)
    total_coherent_energy = float(np.sum(site_energy))
    modal_total = float(np.sum(mode_energy))
    conservation_error = abs(total_coherent_energy - modal_total)

    continuity_residual: np.ndarray | None = None
    continuity = FirstMomentFlowContinuity()
    if previous is not None:
        if previous.sites != sites:
            raise ValueError("previous frame must use the same site count")
        dt = time - previous.time
        if dt <= 0.0:
            raise ValueError("frame time must increase relative to previous")
        energy_rate = (site_energy - previous.site_energy) / dt
        midpoint_inflow = 0.5 * (net_inflow + previous.net_inflow)
        continuity_residual = energy_rate - midpoint_inflow
        continuity = FirstMomentFlowContinuity(
            dt=dt,
            local_l2=float(np.linalg.norm(continuity_residual)),
            local_linf=float(np.max(np.abs(continuity_residual))),
            global_residual=abs(float(np.sum(energy_rate))),
        )

    return FirstMomentFlowFrame(
        time=time,
        sites=sites,
        lattice_spacing=model.spec.lattice_spacing,
        mass=model.spec.mass,
        propagation_speed=model.spec.propagation_speed,
        mean_phi=phi,
        mean_pi=pi,
        site_energy=np.asarray(site_energy, dtype=float),
        bond_current=np.asarray(bond_current, dtype=float),
        net_inflow=np.asarray(net_inflow, dtype=float),
        mode_phi=np.asarray(mode_phi, dtype=float),
        mode_pi=np.asarray(mode_pi, dtype=float),
        mode_energy=np.asarray(mode_energy, dtype=float),
        mode_wave_numbers=_mode_wave_numbers(sites),
        mode_component_codes=_mode_component_codes(sites),
        total_coherent_energy=total_coherent_energy,
        current_l1=float(np.sum(np.abs(bond_current))),
        conservation_error=conservation_error,
        continuity_residual=(
            None
            if continuity_residual is None
            else np.asarray(continuity_residual, dtype=float)
        ),
        continuity=continuity,
    )


class FirstMomentFlowObserver:
    """Stateful observer that adds continuity diagnostics across field frames."""

    def __init__(self) -> None:
        self._previous: FirstMomentFlowFrame | None = None

    @property
    def previous(self) -> FirstMomentFlowFrame | None:
        return self._previous

    def reset(self) -> None:
        self._previous = None

    def observe(
        self, frame: ScalarFieldFrame, model: ScalarFieldModel
    ) -> FirstMomentFlowFrame:
        # A source reset starts a new authoritative trajectory.  It is not an
        # observer failure and must not produce a false continuity diagnostic.
        if self._previous is not None and frame.time <= self._previous.time:
            self.reset()
        result = build_first_moment_flow_frame(
            frame, model, previous=self._previous
        )
        self._previous = result
        return result


class FirstMomentFlowPublisher:
    """Publish the V4.1 observer on its independent, revisioned OSC stream."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client
        self.revision = 0

    def publish(self, frame: FirstMomentFlowFrame, *, source_revision: int) -> int:
        self.revision += 1
        revision = self.revision
        self.client.send_message(
            f"{OSC_ROOT}/frame/begin",
            [revision, int(source_revision), frame.time, SCHEMA, SOURCE_SCHEMA],
        )
        self.client.send_message(
            f"{OSC_ROOT}/basis/site",
            [revision, "site", frame.sites, "periodic", frame.lattice_spacing],
        )
        self.client.send_message(
            f"{OSC_ROOT}/basis/mode",
            [revision, "real_fourier", frame.sites],
        )
        self.client.send_message(
            f"{OSC_ROOT}/mode/wave-number",
            [revision, *frame.mode_wave_numbers.tolist()],
        )
        self.client.send_message(
            f"{OSC_ROOT}/mode/component",
            [revision, *frame.mode_component_codes.tolist()],
        )
        for site in range(frame.sites):
            self.client.send_message(
                f"{OSC_ROOT}/site",
                [
                    revision,
                    site,
                    frame.mean_phi[site],
                    frame.mean_pi[site],
                    frame.site_energy[site],
                    frame.net_inflow[site],
                ],
            )
            self.client.send_message(
                f"{OSC_ROOT}/bond",
                [
                    revision,
                    site,
                    (site + 1) % frame.sites,
                    frame.bond_current[site],
                ],
            )
            self.client.send_message(
                f"{OSC_ROOT}/mode",
                [
                    revision,
                    site,
                    int(frame.mode_wave_numbers[site]),
                    int(frame.mode_component_codes[site]),
                    frame.mode_phi[site],
                    frame.mode_pi[site],
                    frame.mode_energy[site],
                ],
            )
        continuity = frame.continuity
        self.client.send_message(
            f"{OSC_ROOT}/global",
            [
                revision,
                frame.total_coherent_energy,
                frame.current_l1,
                frame.conservation_error,
                -1.0 if continuity.dt is None else continuity.dt,
                -1.0 if continuity.local_l2 is None else continuity.local_l2,
                -1.0 if continuity.local_linf is None else continuity.local_linf,
                -1.0
                if continuity.global_residual is None
                else continuity.global_residual,
            ],
        )
        self.client.send_message(f"{OSC_ROOT}/frame/end", revision)
        return revision


__all__ = [
    "EPSILON",
    "FirstMomentFlowContinuity",
    "FirstMomentFlowFrame",
    "FirstMomentFlowObserver",
    "FirstMomentFlowPublisher",
    "OSC_ROOT",
    "OUTPUT_PORT",
    "SCHEMA",
    "SOURCE_SCHEMA",
    "build_first_moment_flow_frame",
]
