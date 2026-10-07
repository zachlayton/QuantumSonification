#!/usr/bin/env python3
"""Read-only Sophie Germain observer for authoritative QMW V4.2 density frames.

The canonical four-qubit engine remains the sole owner of ``rho`` and its
clock. This process receives complete post-evolution density matrices over a
private OSC port, makes a declared Chladni/eigenmode projection for display,
and serves the existing Sophie Germain web panel. It has no output path back
to the engine, SuperCollider, or the audio buses.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import signal
import threading
import time
from typing import Any, Sequence

import numpy as np

from quantum_chladni_synth_v1.quantum_chladni_controller_v1 import (
    ModalProfile,
    QuantumChladniFrame,
    load_modal_profile,
    projection_probability_current,
    qpe_condition_modal_distribution,
)
from quantum_chladni_synth_v1.sophie_germain_panel_v1 import (
    SophieGermainPanelServer,
    start_sophie_germain_panel,
)
from quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    QuantumEigenfieldEngine,
)


DENSITY_ADDRESS = "/qmw/temporal/source/density"
PANEL_SOURCE = "qmw_v4_2_authoritative_density"


def _validated_density(matrix: Any) -> np.ndarray:
    """Validate one wire-format density matrix and repair only float32 drift."""

    rho = np.asarray(matrix, dtype=np.complex128)
    if rho.shape != (16, 16):
        raise ValueError("V4.2 Sophie observer requires a 16x16 density matrix")
    if np.any(~np.isfinite(rho.real)) or np.any(~np.isfinite(rho.imag)):
        raise ValueError("density matrix entries must be finite")
    if not np.allclose(rho, rho.conj().T, rtol=0.0, atol=2e-5):
        raise ValueError("density matrix must be Hermitian")
    rho = 0.5 * (rho + rho.conj().T)
    trace = complex(np.trace(rho))
    if abs(trace.imag) > 2e-5 or not math.isclose(
        trace.real, 1.0, rel_tol=2e-5, abs_tol=2e-5
    ):
        raise ValueError("density matrix trace must equal one")
    rho /= trace.real
    if float(np.min(np.linalg.eigvalsh(rho))) < -2e-5:
        raise ValueError("density matrix must be positive semidefinite")
    return rho


def decode_density_payload(payload: Sequence[Any]) -> tuple[int, np.ndarray]:
    """Decode the engine's complete revisioned density OSC payload."""

    values = list(payload)
    if len(values) < 2:
        raise ValueError("density payload is missing revision or dimension")
    revision = int(values[0])
    dimension = int(values[1])
    if revision < 0:
        raise ValueError("density revision must be nonnegative")
    if dimension != 16:
        raise ValueError("density payload dimension must be 16")
    expected = 2 + 2 * dimension * dimension
    if len(values) != expected:
        raise ValueError(
            f"density payload has {len(values)} values; expected {expected}"
        )
    components = np.asarray(values[2:], dtype=np.float64)
    flattened = components[0::2] + 1j * components[1::2]
    return revision, _validated_density(flattened.reshape(dimension, dimension))


def authoritative_density_to_panel_frame(
    profile: ModalProfile,
    rho: Any,
    revision: int,
    *,
    qpe_bits: int = 5,
    rng: Any | None = None,
) -> QuantumChladniFrame:
    """Derive one panel-only modal observation from authoritative ``rho``.

    The spatial basis and QPE readout are downstream display mappings. They do
    not collapse, replace, or otherwise feed back into the engine density.
    """

    density = _validated_density(rho)
    count = len(profile.eigenvalues)
    modal_packet = {
        "model": profile.name,
        "eigenvalues": profile.eigenvalues,
        "eigenvectors": profile.eigenvectors,
        "frequencies_hz": profile.frequencies_hz,
        "decay_times_seconds": profile.decay_seconds,
        "mode_weights": profile.mode_weights,
    }
    eigenfield = QuantumEigenfieldEngine(
        density,
        modal_packet=modal_packet,
        config=QuantumEigenfieldConfig(n_geometric_modes=count),
    )
    probabilities, amplitudes = eigenfield.project()
    generator = np.random.default_rng(20260928) if rng is None else rng
    qpe = qpe_condition_modal_distribution(
        probabilities,
        profile.eigenvalues,
        int(qpe_bits),
        generator,
    )
    probabilities = qpe.posterior
    amplitudes = np.sqrt(probabilities) * np.exp(1j * np.angle(amplitudes))
    probability_current = projection_probability_current(profile, amplitudes)
    descriptors = eigenfield.quantum_descriptors
    entropy_normalized = descriptors.entropy_bits / max(
        descriptors.max_mixed_entropy_bits, 1e-12
    )
    coherence_normalized = min(
        1.0,
        descriptors.coherence_l1 / max(descriptors.dimension - 1, 1),
    )
    index = np.arange(count, dtype=np.float64)
    pans = np.sin(index * 2.399963229728653 + np.angle(amplitudes))
    basis_populations = np.maximum(np.real(np.diag(density)), 0.0)
    basis_populations /= max(float(np.sum(basis_populations)), 1e-12)
    density_values, density_vectors = np.linalg.eigh(density)
    principal = density_vectors[:, int(np.argmax(density_values))]
    reference_index = int(np.argmax(np.abs(principal)))
    reference_phase = float(np.angle(principal[reference_index]))
    basis_phases = np.angle(principal * np.exp(-1j * reference_phase))
    return QuantumChladniFrame(
        int(revision),
        descriptors.purity,
        entropy_normalized,
        coherence_normalized,
        profile.frequencies_hz.copy(),
        profile.decay_seconds.copy(),
        profile.mode_weights.copy(),
        probabilities,
        np.angle(amplitudes),
        pans,
        basis_populations,
        basis_phases,
        qpe.bits,
        qpe.measured_integer,
        qpe.measured_phase,
        qpe.dominant_mode,
        qpe.confidence,
        probability_current,
        (
            "Im(conj(psi) * grad(psi)); hbar_over_mass=1; "
            "panel-only projection of authoritative V4.2 rho"
            if probability_current is not None
            else None
        ),
    )


class V42SophieGermainObserver:
    """Coalesce incoming density frames and publish at a visual cadence."""

    def __init__(
        self,
        profile: ModalProfile,
        panel: SophieGermainPanelServer,
        *,
        qpe_bits: int = 5,
        random_seed: int = 20260928,
    ) -> None:
        self.profile = profile
        self.panel = panel
        self.qpe_bits = int(np.clip(int(qpe_bits), 2, 10))
        self.rng = np.random.default_rng(int(random_seed))
        self._lock = threading.RLock()
        self._latest_received: tuple[int, np.ndarray] | None = None
        self._latest_published_revision = -1
        self._reported_live = False

    @property
    def latest_published_revision(self) -> int:
        with self._lock:
            return self._latest_published_revision

    def _accept_density(self, payload: Sequence[Any]) -> bool:
        revision, rho = decode_density_payload(payload)
        with self._lock:
            if (
                self._latest_received is not None
                and revision <= self._latest_received[0]
            ):
                return False
            if revision <= self._latest_published_revision:
                return False
            self._latest_received = (revision, rho.copy())
        return True

    def receive_density(self, _address: str, *payload: Any) -> None:
        # python-osc treats a non-None handler result as a reply address. Keep
        # this callback strictly receive-only and report malformed frames
        # without terminating its request thread.
        try:
            self._accept_density(payload)
        except ValueError as exc:
            print(f"Rejected Sophie Germain density frame: {exc}", flush=True)

    def publish_latest(self) -> bool:
        with self._lock:
            if self._latest_received is None:
                return False
            revision, rho = self._latest_received
            if revision <= self._latest_published_revision:
                return False
        frame = authoritative_density_to_panel_frame(
            self.profile,
            rho,
            revision,
            qpe_bits=self.qpe_bits,
            rng=self.rng,
        )
        accepted = self.panel.store.observe(frame)
        if accepted:
            with self._lock:
                self._latest_published_revision = revision
            if not self._reported_live:
                print(
                    "Sophie Germain observer receiving authoritative "
                    f"V4.2 density frames (revision {revision}).",
                    flush=True,
                )
                self._reported_live = True
        return accepted


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=17870)
    parser.add_argument("--panel-host", default="127.0.0.1")
    parser.add_argument("--panel-port", type=int, default=8788)
    parser.add_argument("--modal-packet", type=Path)
    parser.add_argument("--modes", type=int, default=24)
    parser.add_argument("--visual-samples", type=int, default=768)
    parser.add_argument("--qpe-bits", type=int, default=5)
    parser.add_argument("--rate-hz", type=float, default=8.0)
    parser.add_argument("--random-seed", type=int, default=20260928)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not 1024 <= args.osc_port <= 65535:
        raise SystemExit("--osc-port must be in [1024, 65535]")
    if not 1024 <= args.panel_port <= 65535:
        raise SystemExit("--panel-port must be in [1024, 65535]")
    if args.rate_hz <= 0.0:
        raise SystemExit("--rate-hz must be positive")

    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer

    profile = load_modal_profile(
        args.modal_packet,
        max(1, int(args.modes)),
        max(64, int(args.visual_samples)),
    )
    panel = start_sophie_germain_panel(
        profile,
        host=args.panel_host,
        port=args.panel_port,
        source=PANEL_SOURCE,
    )
    observer = V42SophieGermainObserver(
        profile,
        panel,
        qpe_bits=args.qpe_bits,
        random_seed=args.random_seed,
    )
    dispatcher = Dispatcher()
    dispatcher.map(DENSITY_ADDRESS, observer.receive_density)
    try:
        osc_server = ThreadingOSCUDPServer(
            (args.osc_host, args.osc_port), dispatcher
        )
    except BaseException:
        panel.close()
        raise
    osc_thread = threading.Thread(
        target=osc_server.serve_forever,
        name="qmw-v42-sophie-density-osc",
        daemon=True,
    )
    osc_thread.start()
    stop = threading.Event()

    def halt(_signum: int, _frame: Any) -> None:
        stop.set()

    signal.signal(signal.SIGINT, halt)
    signal.signal(signal.SIGTERM, halt)
    print(f"Sophie Germain panel: {panel.url}", flush=True)
    print(
        f"Read-only V4.2 density input: {args.osc_host}:{args.osc_port} "
        f"{DENSITY_ADDRESS}",
        flush=True,
    )
    period = 1.0 / float(args.rate_hz)
    try:
        while not stop.wait(period):
            observer.publish_latest()
    finally:
        osc_server.shutdown()
        osc_server.server_close()
        osc_thread.join(timeout=2.0)
        panel.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
