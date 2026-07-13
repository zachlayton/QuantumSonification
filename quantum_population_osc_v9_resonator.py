import argparse
import contextlib
import io
import time
from pathlib import Path

import numpy as np

from pythonosc.udp_client import SimpleUDPClient

from analysis.audio_descriptors import AudioWindowAnalyzer
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.mutator import HamiltonianMutator

from density.density_matrix_engine_4q import DensityMatrixEngine
from density.density_adapter import DensityAdapter

from feedback.feedback import FeedbackHistory
from feedback.event_detector import EventDetector
from feedback.quantum_memory import QuantumMemory

from field.quantum_field import QuantumField
from field.trajectory import QuantumTrajectory
from field.bohmian_pilot import BohmianPilot1D
from field.density_field_scanner import DensityFieldScanner
from quantum_oscilloscope.scope_engine import (
    QuantumOscilloscope,
    QuantumOscilloscopeConfig,
)
from quantum_oscilloscope.frame_builder import frame_from_engine_snapshot
from quantum_oscilloscope.osc_control import start_visual_control_server
from qmw_circuit_bridge import QMWCircuitBridge


def _safe_float_list(values):
    return [float(value) for value in np.asarray(values, dtype=np.float64).reshape(-1)]


REVERB_PAULI_STRINGS = (
    "XXII",
    "YYII",
    "ZZII",
    "IXXI",
    "IYYI",
    "IZZI",
    "IIXX",
    "IIYY",
)

_PAULI_MATRICES = {
    "I": np.eye(2, dtype=np.complex128),
    "X": np.array([[0, 1], [1, 0]], dtype=np.complex128),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
    "Z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
}


def _pauli_string_operator(name):
    operator = _PAULI_MATRICES[name[0]]
    for symbol in name[1:]:
        operator = np.kron(operator, _PAULI_MATRICES[symbol])
    return operator


REVERB_PAULI_OPERATORS = {
    name: _pauli_string_operator(name)
    for name in REVERB_PAULI_STRINGS
}


def _reverb_pauli_expectations(rho):
    rho = np.asarray(rho, dtype=np.complex128)
    return {
        name: float(np.clip(np.trace(rho @ operator).real, -1.0, 1.0))
        for name, operator in REVERB_PAULI_OPERATORS.items()
    }


def _positive_hamiltonian_gap_ratios(hamiltonian, count=16):
    """Return normalized Hamiltonian energy-gap ratios for resonator partials."""
    try:
        eigenvalues = np.sort(np.linalg.eigvalsh(hamiltonian).real)
    except Exception:
        return [float(index + 1) for index in range(count)]

    gaps = []
    for left in range(len(eigenvalues)):
        for right in range(left + 1, len(eigenvalues)):
            gap = float(abs(eigenvalues[right] - eigenvalues[left]))
            if gap > 1e-9:
                gaps.append(gap)

    if not gaps:
        return [float(index + 1) for index in range(count)]

    gaps = sorted(gaps)
    base = gaps[0]
    ratios = [float(np.clip(gap / base, 0.01, 64.0)) for gap in gaps[:count]]
    while len(ratios) < count:
        ratios.append(float(len(ratios) + 1))
    return ratios[:count]


class MLXQuantumResonatorEngine:
    def __init__(
        self,
        audio_path=None,
        osc_host="127.0.0.1",
        osc_port=7400,
        visual_osc_port=7401,
        mutation_amount=0.5,
        engine_hz=100.0,
        density_field_hz=30.0,
        diagnostics_hz=5.0,
        status_hz=0.5,
        osc_profile="resonator",
        quiet=False,
        verbose=False,
        enable_circuit_bridge_control=True,
        excitation_source="schrodinger_interference",
        bohmian_n_modes=16,
        bohmian_grid_size=512,
        bohmian_mobility=0.28,
        bohmian_damping=0.86,
        bohmian_field_smoothing=0.14,
    ):
        if audio_path is None:
            project_root = Path(__file__).resolve().parent
            audio_path = project_root / "materials" / "test.wav"

        self.audio_path = str(Path(audio_path))
        self.engine_hz = max(float(engine_hz), 1.0)
        self.interval = 1.0 / self.engine_hz
        self.density_field_interval = 1.0 / max(float(density_field_hz), 0.001)
        self.diagnostics_interval = 1.0 / max(float(diagnostics_hz), 0.001)
        self.status_hz = float(status_hz)
        self.osc_profile = str(osc_profile).strip().lower()
        self.quiet = bool(quiet)
        self.verbose = bool(verbose)
        self.enable_circuit_bridge_control = bool(enable_circuit_bridge_control)

        self.density_field_elapsed = 0.0
        self.diagnostics_elapsed = 0.0
        self.last_status_time = 0.0
        self.step_count = 0
        self.osc_frame_count = 0
        self.time = 0.0

        self.latest_metrics = {}
        self.latest_harmonics = [float(index + 1) for index in range(16)]

        self.audio_analyzer = self.construct_quietly(
            AudioWindowAnalyzer,
            self.audio_path,
            window_seconds=1.0,
            analysis_hop_seconds=0.10,
            playback_rate=1.0,
            loop=True,
        )

        self.osc = SimpleUDPClient(osc_host, osc_port)
        self.visual_osc = SimpleUDPClient(osc_host, visual_osc_port)
        self.oscilloscope = self.construct_quietly(
            QuantumOscilloscope,
            QuantumOscilloscopeConfig(
                osc_host=osc_host,
                osc_port=osc_port,
                visual_osc_port=visual_osc_port,
                send_pauli_aliases=True,
            ),
        )

        self.hamiltonian = HamiltonianState(x=0.0, y=0.0, z=1.0)
        self.mutator = self.construct_quietly(HamiltonianMutator, amount=mutation_amount)
        self.density_engine = self.create_density_engine(excitation_source)
        self.density_adapter = DensityAdapter(self.density_engine)

        self.history = FeedbackHistory()
        self.detector = EventDetector()
        self.quantum_memory = QuantumMemory(decay=0.7)
        self.quantum_field = QuantumField(self.quantum_memory)
        self.trajectory = QuantumTrajectory(self.quantum_field)

        self.visual_perturb = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "gain": 1.0,
        }

        self.bohmian_controls = {
            "mobility": float(bohmian_mobility),
            "damping": float(bohmian_damping),
            "field_smoothing": float(bohmian_field_smoothing),
        }
        self.pilot = BohmianPilot1D(
            n_modes=int(bohmian_n_modes),
            grid_size=int(bohmian_grid_size),
            mobility=self.bohmian_controls["mobility"],
            damping=self.bohmian_controls["damping"],
            field_smoothing=self.bohmian_controls["field_smoothing"],
        )
        self.density_scanner = DensityFieldScanner()
        self.previous_density_field_rho = None
        self.previous_visual_rho = None
        self.density_delta_rho_max = 0.0
        self.density_delta_rho_mean = 0.0

        if not self.quiet:
            print(
                "QMW resonator engine "
                f"engine_hz={self.engine_hz:.1f} "
                f"density_field_hz={1.0 / self.density_field_interval:.1f} "
                f"diagnostics_hz={1.0 / self.diagnostics_interval:.1f} "
                f"osc_profile={self.osc_profile}"
            )

    def construct_quietly(self, factory, *args, **kwargs):
        if self.verbose:
            return factory(*args, **kwargs)
        with contextlib.redirect_stdout(io.StringIO()):
            return factory(*args, **kwargs)

    def silence_context(self):
        if self.verbose:
            return contextlib.nullcontext()
        return contextlib.redirect_stdout(io.StringIO())

    def create_density_engine(self, excitation_source):
        original_start = QMWCircuitBridge.start_control_server

        def disabled_start(_bridge, *_args, **_kwargs):
            return None

        if not self.enable_circuit_bridge_control:
            QMWCircuitBridge.start_control_server = disabled_start
            try:
                return self.construct_quietly(
                    DensityMatrixEngine,
                    excitation_source=excitation_source,
                )
            finally:
                QMWCircuitBridge.start_control_server = original_start

        try:
            return self.construct_quietly(
                DensityMatrixEngine,
                excitation_source=excitation_source,
            )
        except OSError as exc:
            if getattr(exc, "errno", None) != 48:
                raise
            if not self.quiet:
                print(
                    "QMW circuit bridge control port is already in use; "
                    "continuing without starting that internal server."
                )
            QMWCircuitBridge.start_control_server = disabled_start
            try:
                return self.construct_quietly(
                    DensityMatrixEngine,
                    excitation_source=excitation_source,
                )
            finally:
                QMWCircuitBridge.start_control_server = original_start

    def set_visual_perturb(self, axis, value):
        self.visual_perturb[axis] = float(value)
        if self.verbose and not self.quiet:
            print(f"PERTURB RECEIVED: {axis} = {value}")

    def set_bohmian_parameter(self, name, value):
        parameter = str(name).strip().lower()
        value = float(value)
        ranges = {
            "mobility": (0.0, 2.0),
            "damping": (0.0, 0.99),
            "field_smoothing": (0.0, 1.0),
            "smoothing": (0.0, 1.0),
        }
        if parameter not in ranges:
            if not self.quiet:
                print(f"Unknown Bohmian parameter: {parameter}")
            return

        low, high = ranges[parameter]
        value = float(np.clip(value, low, high))
        target = "field_smoothing" if parameter == "smoothing" else parameter
        self.bohmian_controls[target] = value
        setattr(self.pilot, target, value)
        if self.verbose and not self.quiet:
            print(f"BOHMIAN {target}: {value:.4f}")

    def set_wavetable_parameter(self, name, value):
        if self.verbose and not self.quiet:
            print(f"Ignoring wavetable parameter in resonator profile: {name}={value}")

    def step(self):
        audio = self.audio_analyzer.next_window(dt=self.interval)
        self.hamiltonian = self.mutator.mutate_from_audio(self.hamiltonian, audio)
        self.density_adapter.apply_hamiltonian_state(self.hamiltonian)
        with self.silence_context():
            rho = self.density_adapter.step(self.interval)

        rho_np = np.asarray(rho, dtype=np.complex128)
        rho_hermitian = 0.5 * (rho_np + rho_np.conj().T)
        density_scan = self.density_scanner.step(
            rho_hermitian,
            self.previous_density_field_rho,
            self.interval,
        )
        self.previous_density_field_rho = rho_hermitian.copy()

        with self.silence_context():
            density_metrics = self.density_adapter.metrics(rho)
        self.latest_harmonics = self.hamiltonian_harmonics()

        bohm = self.step_bohmian(rho_np)
        bloch = {
            "x": density_metrics.get("bloch_x", 0.0),
            "y": density_metrics.get("bloch_y", 0.0),
            "z": density_metrics.get("bloch_z", 0.0),
        }

        self.quantum_memory.encode(
            rho=rho,
            hamiltonian=self.hamiltonian,
            audio_descriptor=audio,
        )

        metrics = self.build_metrics(density_metrics, density_scan, bohm)
        event_result = self.detector.detect(metrics=metrics, audio_descriptor=audio)
        self.quantum_memory.annotate_latest(
            events=event_result["events"],
            metrics=metrics,
        )
        self.history.add(
            audio_descriptor=audio,
            hamiltonian=self.hamiltonian,
            bloch=bloch,
        )
        self.latest_metrics = metrics

        self.density_field_elapsed += self.interval
        self.diagnostics_elapsed += self.interval

        if self.density_field_elapsed >= self.density_field_interval:
            self.density_field_elapsed %= self.density_field_interval
            self.send_density_field_frame(rho_hermitian, density_scan, metrics)
            self.osc_frame_count += 1

        if self.osc_profile == "full" and self.diagnostics_elapsed >= self.diagnostics_interval:
            self.diagnostics_elapsed %= self.diagnostics_interval
            self.send_full_diagnostics(
                rho_np,
                rho_hermitian,
                density_scan,
                density_metrics,
                metrics,
                bohm,
                bloch,
                event_result,
            )

        if self.verbose:
            self.observe_visual_frame(rho_np, density_metrics, metrics, bohm, bloch)

        self.time += self.interval
        self.step_count += 1
        self.maybe_print_status(time.monotonic())

    def step_bohmian(self, rho_np):
        populations = np.real(np.diag(rho_np))
        populations = np.clip(populations, 0.0, None)
        eigenvalues, eigenvectors = np.linalg.eigh(rho_np)
        dominant_state = eigenvectors[:, np.argmax(eigenvalues)]
        return self.pilot.step(
            amplitudes=np.sqrt(populations),
            phases=np.angle(dominant_state),
            dt=self.interval,
        )

    def hamiltonian_harmonics(self):
        try:
            hamiltonian = self.density_engine.hamiltonian()
        except Exception:
            return [float(index + 1) for index in range(16)]
        return _positive_hamiltonian_gap_ratios(hamiltonian, count=16)

    def build_metrics(self, density_metrics, density_scan, bohm):
        metrics = dict(density_metrics)
        metrics["trajectory_speed"] = self.trajectory.speed()
        metrics["trajectory_acceleration"] = self.trajectory.acceleration_magnitude()
        metrics["trajectory_direction_change"] = self.trajectory.direction_change()
        metrics["bohm_x"] = bohm["x"]
        metrics["bohm_speed"] = bohm["speed"]
        metrics["bohm_density"] = bohm["density"]
        metrics["bohm_node_proximity"] = bohm["node_proximity"]
        metrics["bohm_curvature"] = bohm["curvature"]
        metrics["density_field_delta_frobenius"] = density_scan["delta_frobenius"]
        metrics["density_field_delta_max"] = density_scan["delta_max"]
        metrics["density_field_delta_population"] = density_scan["delta_population"]
        metrics["density_field_delta_coherence"] = density_scan["delta_coherence"]
        metrics["density_field_mean_speed"] = density_scan["mean_speed"]
        metrics["density_field_max_speed"] = density_scan["max_speed"]
        metrics["density_field_speed_spread"] = density_scan["speed_spread"]
        metrics["density_field_magnitude_spread"] = density_scan["magnitude_spread"]
        metrics["density_field_phase_spread"] = density_scan["phase_spread"]
        return metrics

    def send_density_field_frame(self, rho, density_scan, metrics):
        self.osc.send_message(
            "/qmw/density_field/magnitude",
            _safe_float_list(density_scan["magnitudes"]),
        )
        self.osc.send_message(
            "/qmw/density_field/phase",
            _safe_float_list(density_scan["phases"]),
        )
        self.osc.send_message(
            "/qmw/density_field/speed",
            _safe_float_list(density_scan["speeds"]),
        )
        self.osc.send_message(
            "/qmw/density_field/harmonics",
            _safe_float_list(self.latest_harmonics),
        )
        self.osc.send_message(
            "/qmw/density_field/purity",
            float(metrics.get("purity", 0.0)),
        )
        self.osc.send_message(
            "/qmw/density_field/entropy",
            float(metrics.get("entropy", 0.0)),
        )
        self.osc.send_message(
            "/qmw/density_field/coherence",
            float(metrics.get("coherence", 0.0)),
        )

        # Correlation signals consumed by the Platonic geometry reverb.
        # These are part of the default resonator profile and do not depend on
        # verbose visualization or the full diagnostics profile.
        for name, value in _reverb_pauli_expectations(rho).items():
            self.osc.send_message(f"/qmw/pauli/{name}", value)
            # Preserve the original spin-engine namespace for older patches.
            self.osc.send_message(f"/pauli/{name}", value)

        # Backward-compatible global metric aliases.
        self.osc.send_message("/qmw/density/purity", float(metrics.get("purity", 0.0)))
        self.osc.send_message("/qmw/density/coherence_l1", float(metrics.get("coherence", 0.0)))
        self.osc.send_message("/qmw/density/von_neumann_entropy", float(metrics.get("entropy", 0.0)))

        if self.osc_profile == "full":
            self.osc.send_message(
                "/qmw/density_field/real",
                _safe_float_list(density_scan["samples"].real),
            )
            self.osc.send_message(
                "/qmw/density_field/imag",
                _safe_float_list(density_scan["samples"].imag),
            )
            self.osc.send_message(
                "/qmw/density_field/x",
                _safe_float_list(density_scan["positions"][:, 0]),
            )
            self.osc.send_message(
                "/qmw/density_field/y",
                _safe_float_list(density_scan["positions"][:, 1]),
            )
            self.osc.send_message(
                "/qmw/density_field/sample_index",
                [int(value) for value in density_scan["sample_indices"]],
            )

    def send_full_diagnostics(
        self,
        rho_np,
        rho_hermitian,
        density_scan,
        density_metrics,
        metrics,
        bohm,
        bloch,
        event_result,
    ):
        circuit_state = getattr(self.density_engine, "circuit_state", {})
        local_bloch = circuit_state.get("local_bloch", [[0.0, 0.0, 0.0] for _ in range(4)])
        for q in range(4):
            self.osc.send_message(
                f"/qmw/qubit/{q}/bloch",
                [float(local_bloch[q][0]), float(local_bloch[q][1]), float(local_bloch[q][2])],
            )

        self.osc.send_message(
            "/qmw/density/populations",
            [float(value) for value in circuit_state.get("populations", [0.0] * 16)],
        )
        self.osc.send_message(
            "/qmw/density/basis_labels",
            [format(index, "04b") for index in range(16)],
        )
        self.osc.send_message("/qmw/bloch/vector_x", bloch["x"])
        self.osc.send_message("/qmw/bloch/vector_y", bloch["y"])
        self.osc.send_message("/qmw/bloch/vector_z", bloch["z"])
        self.osc.send_message("/qmw/bohm/x", bohm["x"])
        self.osc.send_message("/qmw/bohm/speed", bohm["speed"])
        self.osc.send_message("/qmw/bohm/density", bohm["density"])
        self.osc.send_message("/qmw/bohm/node_proximity", bohm["node_proximity"])
        self.osc.send_message("/qmw/bohm/curvature", bohm["curvature"])

        eigenvalues = np.linalg.eigvalsh(rho_hermitian)
        self.visual_osc.send_message(
            "/qmw/density/eigenvalues",
            [float(value.real) for value in eigenvalues],
        )
        for event in event_result["events"]:
            self.osc.send_message("/qmw/event", event)

        if self.verbose and not self.quiet:
            rho_difference = np.abs(rho_np - self.previous_visual_rho) if self.previous_visual_rho is not None else np.zeros_like(rho_np)
            self.density_delta_rho_max = float(np.max(rho_difference))
            self.density_delta_rho_mean = float(np.mean(rho_difference))
            self.previous_visual_rho = rho_np.copy()

    def observe_visual_frame(self, rho_np, density_metrics, metrics, bohm, bloch):
        perturb_x = self.visual_perturb["x"]
        perturb_y = self.visual_perturb["y"]
        perturb_z = self.visual_perturb["z"]
        visual_gain = self.visual_perturb["gain"]
        perturbed_bloch_x = (bloch["x"] + perturb_x) * visual_gain
        perturbed_bloch_y = (bloch["y"] + perturb_y) * visual_gain
        perturbed_bloch_z = (bloch["z"] + perturb_z) * visual_gain
        perturbed_norm = np.sqrt(
            perturbed_bloch_x ** 2
            + perturbed_bloch_y ** 2
            + perturbed_bloch_z ** 2
        )
        if perturbed_norm > 0.95:
            scale = 0.95 / perturbed_norm
            perturbed_bloch_x *= scale
            perturbed_bloch_y *= scale
            perturbed_bloch_z *= scale

        frame = frame_from_engine_snapshot(
            t=self.time,
            dt=self.interval,
            rho=rho_np,
            hamiltonian=self.hamiltonian,
            density_metrics=density_metrics,
            density_engine=self.density_engine,
            extra_observables=metrics,
            memory={
                "size": self.quantum_memory.size(),
                "purity": self.quantum_memory.purity(),
                "coherence": self.quantum_memory.coherence_l1(),
            },
            bohm=bohm,
            visual={
                "bloch_x": bloch["x"],
                "bloch_y": bloch["y"],
                "bloch_z": bloch["z"],
                "perturbed_bloch_x": perturbed_bloch_x,
                "perturbed_bloch_y": perturbed_bloch_y,
                "perturbed_bloch_z": perturbed_bloch_z,
                "field_strength": metrics["trajectory_speed"],
                "field_acceleration": metrics["trajectory_acceleration"],
            },
        )
        self.oscilloscope.observe(frame)

    def maybe_print_status(self, now):
        if self.quiet or self.status_hz <= 0:
            return
        interval = 1.0 / self.status_hz
        if now - self.last_status_time < interval:
            return
        self.last_status_time = now
        print(
            "\r"
            f"step={self.step_count} "
            f"purity={self.latest_metrics.get('purity', 0.0):.4f} "
            f"entropy={self.latest_metrics.get('entropy', 0.0):.4f} "
            f"coherence={self.latest_metrics.get('coherence', 0.0):.4f} "
            f"osc={self.osc_frame_count}",
            end="",
            flush=True,
        )

    def run(self):
        try:
            while True:
                started = time.monotonic()
                self.step()
                elapsed = time.monotonic() - started
                time.sleep(max(0.0, self.interval - elapsed))
        except KeyboardInterrupt:
            if not self.quiet:
                print("\nQMW resonator engine stopped.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Quiet resonator-focused QMW density-field OSC engine."
    )
    parser.add_argument("--audio-path", type=Path, default=None)
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=7400)
    parser.add_argument("--visual-osc-port", type=int, default=7401)
    parser.add_argument("--control-port", type=int, default=7402)
    parser.add_argument("--engine-hz", type=float, default=100.0)
    parser.add_argument("--density-field-hz", type=float, default=30.0)
    parser.add_argument("--diagnostics-hz", type=float, default=5.0)
    parser.add_argument("--status-hz", type=float, default=0.5)
    parser.add_argument(
        "--osc-profile",
        choices=["resonator", "full"],
        default="resonator",
    )
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--no-control-server",
        action="store_true",
        help="Do not start the v9 visual/control OSC server.",
    )
    parser.add_argument(
        "--disable-circuit-bridge-control",
        action="store_true",
        help="Do not start the internal circuit-builder OSC control server.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    qmw = MLXQuantumResonatorEngine(
        audio_path=args.audio_path,
        osc_host=args.osc_host,
        osc_port=args.osc_port,
        visual_osc_port=args.visual_osc_port,
        engine_hz=args.engine_hz,
        density_field_hz=args.density_field_hz,
        diagnostics_hz=args.diagnostics_hz,
        status_hz=args.status_hz,
        osc_profile=args.osc_profile,
        quiet=args.quiet,
        verbose=args.verbose,
        enable_circuit_bridge_control=not args.disable_circuit_bridge_control,
    )

    if not args.no_control_server and not args.quiet:
        print(f"Starting QMW control server on {args.control_port}...")

    control_server = None
    if not args.no_control_server:
        control_server = start_visual_control_server(
            qmw,
            host=args.osc_host,
            port=args.control_port,
        )

    qmw.run()
