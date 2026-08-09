import argparse
import contextlib
import io
import os
import threading
import time
from pathlib import Path

import numpy as np

from analysis.audio_descriptors import AudioWindowAnalyzer
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.mutator import HamiltonianMutator

from density.density_matrix_engine_4q import DensityMatrixEngine
from density.density_adapter import DensityAdapter
from density.cnmat_resonator_model import density_matrix_to_cnmat_resonators
from density.density_spectral_wavetable import (
    density_matrix_to_spectral_wavetable,
)
from density.grw_sonification_adapter_v1 import GRWSonificationAdapter
from density.live_gate_injection import apply_live_gate
from density.density_state_injection import bit_reversal_permutation

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
from quantum_oscilloscope.resilient_udp import ResilientSimpleUDPClient
from qmw_circuit_bridge import QMWCircuitBridge
from qmw_temporal_crystal16_v1 import (
    TEMPORAL_CRYSTAL_MODES,
    build_live_temporal_layer,
)

# Preserve the long-standing patch/injection point used by tests and external
# launchers while retaining the resilient implementation underneath it.
SimpleUDPClient = ResilientSimpleUDPClient


ENGINE_IMPLEMENTATION = os.environ.get(
    "QMW_ENGINE_IMPLEMENTATION", "resonator_v9"
)
ENGINE_NAME = os.environ.get("QMW_ENGINE_NAME", "resonator")
ENGINE_VERSION = os.environ.get("QMW_ENGINE_VERSION", "9")
OSC_PROTOCOL = os.environ.get("QMW_OSC_PROTOCOL", "qmw-osc-v1")
ENGINE_CAPABILITIES = tuple(
    capability
    for capability in os.environ.get(
        "QMW_ENGINE_CAPABILITIES",
        (
            "density,mutual_information,pauli,bohmian,external_clock,"
            "circuit_bridge,resonance_events"
            ",density_state_injection,eigenfield_conductor_lanes"
            ",cnmat_density_resonator"
            ",density_spectral_wavetable"
            ",grw_sonification_v1"
            ",temporal_crystal16"
        ),
    ).split(",")
    if capability
)


def _safe_float_list(values):
    return [float(value) for value in np.asarray(values, dtype=np.float64).reshape(-1)]


def grainflow_conductor_state(metrics, density_scan):
    """Derive one coordinated GrainFlow/Zeeman state from density telemetry."""
    purity = float(np.clip(metrics.get("purity", 0.0), 0.0, 1.0))
    coherence = float(np.clip(metrics.get("coherence", 0.0), 0.0, 1.0))
    entropy = float(np.clip(metrics.get("entropy", 0.0) / np.log(16.0), 0.0, 1.0))
    magnitudes = np.asarray(density_scan.get("magnitudes", [0.0]), dtype=np.float64)
    phases = np.asarray(density_scan.get("phases", [0.0]), dtype=np.float64)
    count = min(magnitudes.size, phases.size)
    weights = np.maximum(magnitudes[:count], 0.0)
    phase_vector = np.sum(weights * np.exp(1j * phases[:count]))
    phase = float(np.angle(phase_vector)) if abs(phase_vector) > 1e-12 else 0.0
    magnitude = float(np.clip(np.sqrt(np.mean(np.square(magnitudes))), 0.0, 1.0))
    motion = float(np.tanh(max(0.0, metrics.get("density_field_mean_speed", 0.0))))

    transpose = 12.0 * phase / np.pi
    grainflow = [
        1.0,                              # state
        0.25 + 0.75 * purity,             # density
        0.35 + 0.65 * np.sqrt(purity),    # amp
        0.50 * (1.0 - coherence),         # ampRandom
        125.0 * (phase / np.pi + 1.0),    # delay ms
        15.0 + 485.0 * entropy,           # delayRandom ms
        transpose,                        # transpose semitones
        12.0 * entropy,                   # transposeRandom semitones
        0.05 + 0.65 * (1.0 - coherence),  # space
        0.50 * entropy,                   # spaceRandom
        12.0 * motion * (2.0 * purity - 1.0),
        12.0 * entropy * (1.0 - purity),
        float(np.clip(2.0 ** (transpose / 12.0), 0.25, 4.0)),
        0.15 + 0.85 * coherence,
    ]
    preset = "normal" if entropy < 0.34 else ("sodium_d1" if entropy < 0.67 else "sodium_d2")
    zeeman = [
        float(np.clip(0.5 + 5.0 * magnitude + 2.0 * motion + 1.5 * abs(np.sin(phase)), 0.0, 12.0)),
        55.0 + 110.0 * purity + 55.0 * (phase / (2.0 * np.pi) + 0.5),
        20.0 + 80.0 * coherence + 80.0 * motion,
        0.08 + 0.22 * np.sqrt(purity),
    ]
    return grainflow, zeeman, preset


def grainflow_full_conductor_state(metrics, density_scan):
    """Full, safely bounded GrainFlow attribute frame (protocol v2)."""
    basic, _, _ = grainflow_conductor_state(metrics, density_scan)
    purity = float(np.clip(metrics.get("purity", 0.0), 0.0, 1.0))
    coherence = float(np.clip(metrics.get("coherence", 0.0), 0.0, 1.0))
    entropy = float(np.clip(metrics.get("entropy", 0.0) / np.log(16.0), 0.0, 1.0))
    magnitudes = np.asarray(density_scan.get("magnitudes", [0.0]), dtype=np.float64)
    magnitude_peak = max(float(np.max(magnitudes)), 1e-12)
    field_activity = float(np.clip(np.mean(magnitudes) / magnitude_peak, 0.0, 1.0))
    field_motion = float(np.tanh(max(0.0, metrics.get("density_field_mean_speed", 0.0))))
    global_density = float(np.clip(
        0.06 + (0.62 * field_activity + 0.22 * field_motion) * (0.35 + 0.65 * purity),
        0.06,
        0.82,
    ))
    phase = float(np.clip(basic[6] / 12.0, -1.0, 1.0)) * np.pi
    motion = float(np.tanh(max(0.0, metrics.get("density_field_mean_speed", 0.0))))
    transpose = 12.0 * phase / np.pi
    rate_motion = 2.0 ** ((motion - 0.5) * 0.5)
    # Order is the public /qmw/conductor/grainflow/v2 contract.
    return [
        1.0, global_density,
        0.30 + 0.65 * np.sqrt(purity), 0.0, 0.45 * (1.0 - coherence),
        125.0 * (phase / np.pi + 1.0), 0.0, 15.0 + 235.0 * entropy,
        1.0 - 2.0 * entropy,
        8.0 * motion * (2.0 * purity - 1.0), 0.0, 8.0 * entropy * (1.0 - purity),
        rate_motion, 0.0, 0.20 * entropy,
        0.05 + 0.55 * (1.0 - coherence), 0.0, 0.35 * entropy,
        transpose, 0.0, 8.0 * entropy,
        float(np.clip(phase / (2.0 * np.pi) + 0.5, 0.0, 1.0)), 0.0, 0.75 * entropy,
        0.0, 1.0,
        1.0 + 0.20 * (rate_motion - 1.0),
        0.20 + 0.80 * coherence,
    ]


def grainflow_eigenfield_stream_events(metrics, density_scan, stream_count=8):
    """Project moving density-field particles into independent grain streams."""
    positions = np.asarray(density_scan.get("positions", []), dtype=np.float64)
    magnitudes = np.asarray(density_scan.get("magnitudes", []), dtype=np.float64)
    phases = np.asarray(density_scan.get("phases", []), dtype=np.float64)
    speeds = np.asarray(density_scan.get("speeds", []), dtype=np.float64)
    count = min(len(positions), len(magnitudes), len(phases), len(speeds))
    if count == 0:
        return []
    positions, magnitudes = positions[:count], magnitudes[:count]
    phases, speeds = phases[:count], speeds[:count]
    purity = float(np.clip(metrics.get("purity", 0.0), 0.0, 1.0))
    entropy = float(np.clip(metrics.get("entropy", 0.0) / np.log(16.0), 0.0, 1.0))
    peak_magnitude = max(float(np.max(magnitudes)), 1e-12)
    sectors = np.minimum((positions[:, 0] * stream_count).astype(int), stream_count - 1)
    peak_occupancy = max(int(np.max(np.bincount(sectors, minlength=stream_count))), 1)
    events = [["streamSet", "auto", int(stream_count)]]
    for sector in range(stream_count):
        mask = sectors == sector
        stream = sector + 1
        if not np.any(mask):
            events.extend([["stream", stream, "density", 0.0], ["stream", stream, "amp", 0.0]])
            continue
        local_magnitude = float(np.mean(magnitudes[mask]) / peak_magnitude)
        occupancy = float(np.count_nonzero(mask) / peak_occupancy)
        activity = float(np.clip(0.60 * local_magnitude + 0.40 * occupancy, 0.0, 1.0))
        phase_vector = np.sum(magnitudes[mask] * np.exp(1j * phases[mask]))
        local_phase = float(np.angle(phase_vector)) if abs(phase_vector) > 1e-12 else 0.0
        local_y = float(np.mean(positions[mask, 1]))
        local_speed = float(np.tanh(np.mean(speeds[mask])))
        density = float(np.clip(activity ** 1.6 * (0.18 + 0.62 * purity), 0.0, 0.85))
        events.extend([
            ["stream", stream, "density", density],
            ["stream", stream, "amp", 0.15 + 0.75 * np.sqrt(activity)],
            ["stream", stream, "startPoint", local_y],
            ["stream", stream, "stopPoint", min(1.0, local_y + 0.08 + 0.16 * activity)],
            ["stream", stream, "space", 0.08 + 0.72 * (1.0 - activity)],
            ["stream", stream, "transpose", 12.0 * local_phase / np.pi],
            ["stream", stream, "rateRandom", 0.04 + 0.26 * entropy * local_speed],
        ])
    return events


def eigenfield_conductor_lanes(density_scan, lane_count=8):
    """Return reusable spatial lanes: density, phase, y, speed, occupancy."""
    positions = np.asarray(density_scan.get("positions", []), dtype=np.float64)
    magnitudes = np.asarray(density_scan.get("magnitudes", []), dtype=np.float64)
    phases = np.asarray(density_scan.get("phases", []), dtype=np.float64)
    speeds = np.asarray(density_scan.get("speeds", []), dtype=np.float64)
    count = min(len(positions), len(magnitudes), len(phases), len(speeds))
    lanes = np.zeros((lane_count, 5), dtype=np.float64)
    if count == 0:
        return lanes
    positions, magnitudes = positions[:count], magnitudes[:count]
    phases, speeds = phases[:count], speeds[:count]
    sectors = np.minimum((positions[:, 0] * lane_count).astype(int), lane_count - 1)
    peak = max(float(np.max(magnitudes)), 1e-12)
    for lane in range(lane_count):
        mask = sectors == lane
        occupancy = int(np.count_nonzero(mask))
        if not occupancy:
            continue
        weights = np.maximum(magnitudes[mask], 1e-12)
        phase_vector = np.sum(weights * np.exp(1j * phases[mask]))
        lanes[lane] = [
            float(np.mean(magnitudes[mask]) / peak),
            float(np.angle(phase_vector)),
            float(np.average(positions[mask, 1], weights=weights)),
            float(np.mean(speeds[mask])),
            float(occupancy / count),
        ]
    return lanes


def eigenfield_conductor_grid(rho, density_scan, resolution):
    """Pool the 16x16 complex field into a selectable spatial grid."""
    resolution = int(resolution)
    if resolution not in (4, 8, 16):
        raise ValueError("eigenfield conductor resolution must be 4, 8, or 16")
    field = np.asarray(rho, dtype=np.complex128)
    if field.shape != (16, 16):
        raise ValueError("eigenfield conductor expects a 16x16 density field")
    block = 16 // resolution
    pooled = field.reshape(resolution, block, resolution, block).mean(axis=(1, 3))
    magnitude = np.abs(pooled)
    peak = max(float(np.max(magnitude)), 1e-12)
    density = magnitude / peak
    phase = np.angle(pooled) / np.pi
    occupancy = np.zeros((resolution, resolution), dtype=np.float64)
    positions = np.asarray(density_scan.get("positions", []), dtype=np.float64)
    if positions.size:
        columns = np.minimum((positions[:, 0] * resolution).astype(int), resolution - 1)
        rows = np.minimum((positions[:, 1] * resolution).astype(int), resolution - 1)
        for row, column in zip(rows, columns):
            occupancy[row, column] += 1.0
        occupancy /= max(float(np.max(occupancy)), 1.0)
    # Interleaved per cell: density, normalized phase, particle occupancy.
    return np.stack([density, phase, occupancy], axis=-1)


class MirroredOSCClient:
    """Send one QMW OSC stream to a primary renderer and optional mirrors."""

    def __init__(self, host, primary_port, mirror_ports=()):
        ports = [int(primary_port)]
        ports.extend(int(port) for port in mirror_ports if port is not None)
        # Preserve order while avoiding duplicate packets when the requested
        # SuperCollider port is already the primary renderer port.
        unique_ports = list(dict.fromkeys(ports))
        self.clients = [SimpleUDPClient(host, port) for port in unique_ports]

    def send_message(self, address, value):
        for client in self.clients:
            client.send_message(address, value)


LOCAL_PAULI_STRINGS = (
    "XIII",
    "IXII",
    "IIXI",
    "IIIX",
    "YIII",
    "IYII",
    "IIYI",
    "IIIY",
    "ZIII",
    "IZII",
    "IIZI",
    "IIIZ",
)

NEAREST_NEIGHBOR_PAULI_STRINGS = (
    "XXII",
    "YYII",
    "ZZII",
    "IXXI",
    "IYYI",
    "IZZI",
    "IIXX",
    "IIYY",
    "IIZZ",
)

# Kept under the original name for compatibility with existing reverb code.
# The stream is now a general Pauli field: twelve local Bloch components plus
# the complete XX/YY/ZZ nearest-neighbor correlation set.
REVERB_PAULI_STRINGS = (
    LOCAL_PAULI_STRINGS + NEAREST_NEIGHBOR_PAULI_STRINGS
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
        # Tr(rho P) only needs an elementwise contraction. Avoiding a full
        # 16x16 matrix multiply keeps the expanded 21-observable field cheap
        # enough to publish on every resonator frame.
        name: float(
            np.clip(
                np.einsum("ij,ji->", rho, operator).real,
                -1.0,
                1.0,
            )
        )
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
        sc_osc_port=None,
        temporal_state_port=None,
        visual_osc_port=7401,
        grw_timing_port=None,
        grw_geometry_port=None,
        status_osc_port=7410,
        mutation_amount=0.5,
        engine_hz=100.0,
        density_field_hz=30.0,
        diagnostics_hz=8.0,
        status_hz=0.5,
        osc_profile="resonator",
        clock_source="internal",
        temporal_crystal_mode=None,
        temporal_crystal_rate=2.0,
        quiet=False,
        verbose=False,
        enable_circuit_bridge_control=True,
        excitation_source="schrodinger_interference",
        excitation_drive=None,
        born_species="H-1",
        born_selection_mode="sequential",
        born_time_scale=100_000_000.0,
        born_duration_min_ms=80.0,
        born_duration_max_ms=2_000.0,
        bohmian_n_modes=16,
        bohmian_grid_size=512,
        bohmian_mobility=0.28,
        bohmian_damping=0.86,
        bohmian_field_smoothing=0.14,
        zx_density_matrix_port=7498,
        zx_density_matrix_hz=10.0,
    ):
        if audio_path is None:
            project_root = Path(__file__).resolve().parent
            audio_path = project_root / "materials" / "test.wav"

        self.audio_path = str(Path(audio_path))
        self.engine_hz = max(float(engine_hz), 1.0)
        self.interval = 1.0 / self.engine_hz
        self.density_field_interval = 1.0 / max(float(density_field_hz), 0.001)
        self.zx_density_matrix_interval = (
            1.0 / max(float(zx_density_matrix_hz), 0.001)
        )
        self.diagnostics_interval = 1.0 / max(float(diagnostics_hz), 0.001)
        self.status_hz = float(status_hz)
        self.osc_profile = str(osc_profile).strip().lower()
        self.clock_source = str(clock_source).strip().lower()
        if self.clock_source not in {"internal", "external"}:
            raise ValueError("clock_source must be 'internal' or 'external'")
        self.temporal_crystal_mode = (
            None
            if temporal_crystal_mode is None
            else str(temporal_crystal_mode).strip().lower()
        )
        if (
            self.temporal_crystal_mode is not None
            and self.temporal_crystal_mode not in TEMPORAL_CRYSTAL_MODES
        ):
            choices = ", ".join(TEMPORAL_CRYSTAL_MODES)
            raise ValueError(
                f"temporal_crystal_mode must be one of: {choices}"
            )
        self.temporal_crystal_rate = float(temporal_crystal_rate)
        if self.temporal_crystal_rate <= 0.0:
            raise ValueError("temporal_crystal_rate must be positive")
        self.temporal_layer = (
            build_live_temporal_layer(
                self.temporal_crystal_mode,
                rate_hz=self.temporal_crystal_rate,
            )
            if self.temporal_crystal_mode is not None
            else None
        )
        self.quiet = bool(quiet)
        self.verbose = bool(verbose)
        self.enable_circuit_bridge_control = bool(enable_circuit_bridge_control)

        self.density_field_elapsed = 0.0
        self.zx_density_matrix_elapsed = 0.0
        self.diagnostics_elapsed = 0.0
        self.last_status_time = 0.0
        self.step_count = 0
        self.osc_frame_count = 0
        self.cnmat_resonator_revision = 0
        self.density_wavetable_revision = 0
        self.zx_density_matrix_revision = 0
        self.time = 0.0
        self.system_identity_interval = 5.0
        self.last_system_identity_time = 0.0
        self.resonance_event_count = 0
        self.resonance_event_threshold = float(
            os.environ.get("QMW_RESONANCE_EVENT_THRESHOLD", "0.012")
        )
        self.resonance_event_refractory = float(
            os.environ.get("QMW_RESONANCE_EVENT_REFRACTORY_MS", "140")
        ) / 1000.0
        self.resonance_event_cooldown = 0.0
        self.resonance_previous_salience = None
        self.last_born_transition_event_id = None
        self.last_born_catalog_time = None
        self.born_catalog_interval = 5.0
        self.born_catalog_revision = 1

        # External-clock requests are deliberately coalesced. The OSC server
        # may receive ticks while a quantum step is still running, but the
        # engine keeps only the newest pending tick so control traffic can
        # never build an unbounded backlog.
        self.external_tick_event = threading.Event()
        self.external_tick_lock = threading.Lock()
        self.pending_external_dt = None
        self.coalesced_tick_count = 0
        self.external_tick_count = 0
        self.external_tick_hz = 0.0
        self.last_external_tick_time = None

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

        self.osc = MirroredOSCClient(
            osc_host,
            osc_port,
            mirror_ports=(sc_osc_port,),
        )
        self.visual_osc = ResilientSimpleUDPClient(osc_host, visual_osc_port)
        self.grw_timing_osc = (
            ResilientSimpleUDPClient(osc_host, grw_timing_port)
            if grw_timing_port is not None
            else None
        )
        self.grw_geometry_osc = (
            ResilientSimpleUDPClient(osc_host, grw_geometry_port)
            if grw_geometry_port is not None
            else None
        )
        # self.osc reaches Max and the optional SuperCollider mirror; the
        # visual and timing clients receive the same committed GRW frame.
        self.grw_sonification = GRWSonificationAdapter(
            (
                self.osc,
                self.visual_osc,
                self.grw_timing_osc,
                self.grw_geometry_osc,
            )
        )
        self.status_osc = ResilientSimpleUDPClient(osc_host, status_osc_port)
        self.zx_density_matrix_osc = (
            ResilientSimpleUDPClient(osc_host, zx_density_matrix_port)
            if zx_density_matrix_port is not None
            else None
        )
        self.temporal_state_osc = (
            ResilientSimpleUDPClient(osc_host, temporal_state_port)
            if temporal_state_port is not None
            else None
        )
        self.send_system_identity(force=True)
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
        self.density_engine = self.create_density_engine(
            excitation_source,
            osc_telemetry_hz=1.0 / self.diagnostics_interval,
            born_species=born_species,
            born_selection_mode=born_selection_mode,
            born_time_scale=born_time_scale,
            born_duration_min_ms=born_duration_min_ms,
            born_duration_max_ms=born_duration_max_ms,
            temporal_layer=self.temporal_layer,
        )
        if excitation_drive is not None:
            drive = float(excitation_drive)
            if drive < 0.0:
                raise ValueError("excitation_drive must be non-negative")
            self.density_engine.set_param("excitation_drive", drive)
        self.density_adapter = DensityAdapter(self.density_engine)
        self.density_state_lock = threading.RLock()
        self.density_state_revision = -1

        # The live engine uses only the recent feedback path. Match the
        # quantum-memory window so both allocations settle within seconds.
        self.history = FeedbackHistory(max_frames=512)
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
                f"zx_density_matrix_hz="
                f"{1.0 / self.zx_density_matrix_interval:.1f} "
                f"diagnostics_hz={1.0 / self.diagnostics_interval:.1f} "
                f"clock_source={self.clock_source} "
                f"temporal_crystal={self.temporal_crystal_mode or 'off'} "
                f"temporal_rate={self.temporal_crystal_rate:.3g}Hz "
                f"osc_profile={self.osc_profile}"
            )

    def construct_quietly(self, factory, *args, **kwargs):
        if self.verbose:
            return factory(*args, **kwargs)
        with contextlib.redirect_stdout(io.StringIO()):
            return factory(*args, **kwargs)

    def send_system_identity(self, force=False):
        """Publish the stable protocol and replaceable backend identity."""
        now = time.monotonic()
        if (
            not force
            and now - self.last_system_identity_time
            < self.system_identity_interval
        ):
            return
        self.last_system_identity_time = now
        self.osc.send_message("/qmw/system/engine/name", ENGINE_NAME)
        self.osc.send_message(
            "/qmw/system/engine/implementation", ENGINE_IMPLEMENTATION
        )
        self.osc.send_message(
            "/qmw/system/engine/version", ENGINE_VERSION
        )
        self.osc.send_message("/qmw/system/protocol", OSC_PROTOCOL)
        self.osc.send_message(
            "/qmw/system/capabilities", list(ENGINE_CAPABILITIES)
        )
        self.osc.send_message(
            "/qmw/time/enabled",
            int(self.temporal_crystal_mode is not None),
        )
        self.osc.send_message(
            "/qmw/time/mode",
            self.temporal_crystal_mode or "off",
        )
        self.osc.send_message(
            "/qmw/time/rate_hz",
            self.temporal_crystal_rate,
        )

    def silence_context(self):
        if self.verbose:
            return contextlib.nullcontext()
        return contextlib.redirect_stdout(io.StringIO())

    def create_density_engine(
        self,
        excitation_source,
        osc_telemetry_hz=None,
        born_species="H-1",
        born_selection_mode="sequential",
        born_time_scale=100_000_000.0,
        born_duration_min_ms=80.0,
        born_duration_max_ms=2_000.0,
        temporal_layer=None,
    ):
        original_start = QMWCircuitBridge.start_control_server
        density_kwargs = {
            "excitation_source": excitation_source,
            "osc_telemetry_hz": osc_telemetry_hz,
            "born_species": born_species,
            "born_selection_mode": born_selection_mode,
            "born_time_scale": born_time_scale,
            "born_duration_min_ms": born_duration_min_ms,
            "born_duration_max_ms": born_duration_max_ms,
            "temporal_layer": temporal_layer,
        }

        def disabled_start(_bridge, *_args, **_kwargs):
            return None

        if not self.enable_circuit_bridge_control:
            QMWCircuitBridge.start_control_server = disabled_start
            try:
                return self.construct_quietly(
                    DensityMatrixEngine,
                    **density_kwargs,
                )
            finally:
                QMWCircuitBridge.start_control_server = original_start

        try:
            return self.construct_quietly(
                DensityMatrixEngine,
                **density_kwargs,
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
                    **density_kwargs,
                )
            finally:
                QMWCircuitBridge.start_control_server = original_start

    def set_visual_perturb(self, axis, value):
        self.visual_perturb[axis] = float(value)
        if self.verbose and not self.quiet:
            print(f"PERTURB RECEIVED: {axis} = {value}")

    def commit_density_state(self, rho, revision, source_order):
        """Atomically replace the live density material between engine steps."""
        matrix = np.asarray(rho, dtype=np.complex128)
        with self.density_state_lock:
            if int(revision) <= self.density_state_revision:
                raise ValueError(
                    f"Stale density revision {revision}; current is {self.density_state_revision}"
                )
            self.density_engine.rho = matrix.copy()
            self.density_state_revision = int(revision)
            self.previous_density_field_rho = matrix.copy()
        acknowledgement = [self.density_state_revision, str(source_order)]
        self.osc.send_message("/qmw/state/committed", acknowledgement)
        self.status_osc.send_message("/qmw/state/committed", acknowledgement)
        self.publish_density_commit_snapshot(matrix, self.density_state_revision)
        if not self.quiet:
            print(
                f"Committed QAC density revision {revision} "
                f"({source_order} converted to engine axes)"
            )

    def apply_live_density_gate(self, event_id, gate, qubits, source_order="q0_lsb"):
        """Atomically transform the continuously evolving density material."""
        if str(source_order) not in {"q0_lsb", "engine"}:
            raise ValueError(f"Unknown live-gate ordering: {source_order}")
        gate_name = str(gate).strip().lower()
        logical_qubits = tuple(int(qubit) for qubit in qubits)
        with self.density_state_lock:
            transformed, delta = apply_live_gate(
                self.density_engine.rho,
                gate_name,
                logical_qubits,
                n_qubits=4,
            )
            self.density_engine.rho = transformed
            self.previous_density_field_rho = transformed.copy()
        acknowledgement = [
            int(event_id), gate_name, *logical_qubits, float(delta), str(source_order)
        ]
        self.osc.send_message("/qmw/qac/gate/applied", acknowledgement)
        self.status_osc.send_message("/qmw/qac/gate/applied", acknowledgement)
        if not self.quiet:
            print(
                f"Applied live QAC gate {gate_name}{logical_qubits} "
                f"to evolving density (delta={delta:.6g})"
            )
        return transformed

    def report_density_state_error(self, message):
        self.osc.send_message("/qmw/state/error", str(message))
        self.status_osc.send_message("/qmw/state/error", str(message))
        if not self.quiet:
            print(f"Density state rejected: {message}")

    def publish_density_commit_snapshot(self, rho, revision):
        """Publish immutable material metrics before evolution resumes."""
        matrix = np.asarray(rho, dtype=np.complex128)
        probabilities = np.clip(np.diag(matrix).real, 0.0, 1.0)
        purity_value = float(np.trace(matrix @ matrix).real)
        off_diagonal = matrix - np.diag(np.diag(matrix))
        coherence_value = float(np.sum(np.abs(off_diagonal)))
        eigenvalues = np.linalg.eigvalsh(matrix).real
        eigenvalues = eigenvalues[eigenvalues > 1e-12]
        entropy_value = float(-np.sum(eigenvalues * np.log2(eigenvalues)))
        prefix = "/qmw/state/snapshot"
        self.status_osc.send_message(f"{prefix}/revision", int(revision))
        self.status_osc.send_message(
            f"{prefix}/probabilities", probabilities.astype(float).tolist()
        )
        self.status_osc.send_message(f"{prefix}/purity", purity_value)
        self.status_osc.send_message(f"{prefix}/coherence_l1", coherence_value)
        self.status_osc.send_message(f"{prefix}/entropy", entropy_value)
        for name, value in _reverb_pauli_expectations(matrix).items():
            self.status_osc.send_message(f"{prefix}/pauli/{name}", value)

    @staticmethod
    def _reduced_q0_lsb_density(matrix, qubit):
        reduced = np.zeros((2, 2), dtype=np.complex128)
        bit = 1 << int(qubit)
        for base in range(16):
            if base & bit:
                continue
            indices = (base, base | bit)
            for row_bit in (0, 1):
                for column_bit in (0, 1):
                    reduced[row_bit, column_bit] += matrix[
                        indices[row_bit],
                        indices[column_bit],
                    ]
        return reduced

    @staticmethod
    def _matrix_entropy(matrix):
        eigenvalues = np.clip(
            np.linalg.eigvalsh(matrix).real,
            0.0,
            1.0,
        )
        eigenvalues = eigenvalues[eigenvalues > 1e-12]
        if eigenvalues.size == 0:
            return 0.0
        return float(-np.sum(eigenvalues * np.log2(eigenvalues)))

    def send_zx_density_matrix_frame(self, rho):
        """Publish one complete post-evolution matrix to the Max ZX engine."""
        if self.zx_density_matrix_osc is None:
            return False
        matrix_engine = np.asarray(rho, dtype=np.complex128)
        permutation = bit_reversal_permutation(4)
        matrix = matrix_engine[np.ix_(permutation, permutation)]
        trace = float(np.trace(matrix).real)
        purity = float(np.trace(matrix @ matrix).real)
        off_diagonal = matrix - np.diag(np.diag(matrix))
        coherence = float(np.sum(np.abs(off_diagonal)))
        entropy = self._matrix_entropy(matrix)
        minimum_eigenvalue = float(np.linalg.eigvalsh(matrix).real.min())
        probabilities = np.clip(np.diag(matrix).real, 0.0, 1.0)
        self.zx_density_matrix_revision += 1
        revision = self.zx_density_matrix_revision
        prefix = "/qmw/zx/density"
        self.zx_density_matrix_osc.send_message(
            f"{prefix}/begin",
            [revision, "engine_evolution", 16, 1.0],
        )
        self.zx_density_matrix_osc.send_message(
            f"{prefix}/meta",
            [
                revision,
                trace,
                purity,
                coherence,
                entropy,
                minimum_eigenvalue,
                1.0,
            ],
        )
        self.zx_density_matrix_osc.send_message(
            f"{prefix}/probabilities",
            [revision, *probabilities.astype(float).tolist()],
        )
        for row in range(16):
            self.zx_density_matrix_osc.send_message(
                f"{prefix}/row",
                [
                    revision,
                    row,
                    *matrix.real[row].astype(float).tolist(),
                    *matrix.imag[row].astype(float).tolist(),
                ],
            )
        pauli_x = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
        pauli_y = np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128)
        pauli_z = np.asarray([[1, 0], [0, -1]], dtype=np.complex128)
        for qubit in range(4):
            reduced = self._reduced_q0_lsb_density(matrix, qubit)
            self.zx_density_matrix_osc.send_message(
                f"{prefix}/bloch",
                [
                    revision,
                    qubit,
                    float(np.trace(reduced @ pauli_x).real),
                    float(np.trace(reduced @ pauli_y).real),
                    float(np.trace(reduced @ pauli_z).real),
                    float(np.trace(reduced @ reduced).real),
                    self._matrix_entropy(reduced),
                ],
            )
        self.zx_density_matrix_osc.send_message(
            f"{prefix}/end",
            [
                revision,
                f"live resonator density after evolution step {self.step_count}",
            ],
        )
        return True

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

    def set_temporal_crystal_mode(self, mode):
        """Replace the live temporal protocol without restarting the engine."""

        normalized = str(mode).strip().lower()
        if normalized not in TEMPORAL_CRYSTAL_MODES:
            choices = ", ".join(TEMPORAL_CRYSTAL_MODES)
            raise ValueError(f"temporal mode must be one of: {choices}")

        replacement = build_live_temporal_layer(
            normalized,
            rate_hz=self.temporal_crystal_rate,
        )
        with self.density_state_lock:
            self.temporal_layer = replacement
            self.density_engine.temporal_layer = replacement
            self.temporal_crystal_mode = normalized

        # The Max receiver uses these identity fields as an acknowledgement.
        self.send_system_identity(force=True)
        if not self.quiet:
            print(f"QMW temporal-crystal mode set to: {normalized}")
        return normalized

    def request_external_tick(self, interval_ms=None):
        """Schedule one externally clocked step without queueing a backlog.

        ``interval_ms`` is optional. When supplied by Max it becomes the
        quantum/audio-analysis time delta for this step; otherwise the
        nominal ``--engine-hz`` interval is used.
        """
        if self.clock_source != "external":
            return False

        dt = self.interval
        if interval_ms is not None:
            try:
                dt = float(interval_ms) * 0.001
            except (TypeError, ValueError):
                dt = self.interval
        dt = float(np.clip(dt, 0.001, 1.0))

        with self.external_tick_lock:
            now = time.monotonic()
            if self.last_external_tick_time is not None:
                elapsed = now - self.last_external_tick_time
                if elapsed > 0.0:
                    instantaneous_hz = 1.0 / elapsed
                    if self.external_tick_hz <= 0.0:
                        self.external_tick_hz = instantaneous_hz
                    else:
                        self.external_tick_hz = (
                            0.85 * self.external_tick_hz
                            + 0.15 * instantaneous_hz
                        )
            self.last_external_tick_time = now
            self.external_tick_count += 1
            if self.external_tick_event.is_set():
                self.coalesced_tick_count += 1
            self.pending_external_dt = dt
            self.external_tick_event.set()
        return True

    def step(self, dt=None):
        self.send_system_identity()
        step_interval = self.interval if dt is None else max(float(dt), 0.001)
        audio = self.audio_analyzer.next_window(dt=step_interval)
        self.hamiltonian = self.mutator.mutate_from_audio(self.hamiltonian, audio)
        self.density_adapter.apply_hamiltonian_state(self.hamiltonian)
        with self.density_state_lock:
            with self.silence_context():
                rho = self.density_adapter.step(step_interval)
        self.send_grw_sonification_events()
        self.send_born_transition_catalog()
        self.send_born_transition_frame()

        rho_np = np.asarray(rho, dtype=np.complex128)
        rho_hermitian = 0.5 * (rho_np + rho_np.conj().T)
        density_scan = self.density_scanner.step(
            rho_hermitian,
            self.previous_density_field_rho,
            step_interval,
        )
        self.previous_density_field_rho = rho_hermitian.copy()

        with self.silence_context():
            density_metrics = self.density_adapter.metrics(rho)
        bohm = self.step_bohmian(rho_np, step_interval)
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
        self.maybe_send_resonance_event(metrics, bloch, step_interval)

        self.density_field_elapsed += step_interval
        self.zx_density_matrix_elapsed += step_interval
        self.diagnostics_elapsed += step_interval

        if (
            self.density_state_revision >= 0
            and self.zx_density_matrix_elapsed
            >= self.zx_density_matrix_interval
        ):
            self.zx_density_matrix_elapsed %= self.zx_density_matrix_interval
            self.send_zx_density_matrix_frame(rho_hermitian)

        if self.density_field_elapsed >= self.density_field_interval:
            self.density_field_elapsed %= self.density_field_interval
            # Harmonics are consumed only by the density-field packet. Their
            # eigendecomposition used to rebuild the complete Hamiltonian on
            # every engine step, duplicating the evolution cost at 100 Hz.
            self.latest_harmonics = self.hamiltonian_harmonics()
            self.send_density_field_frame(rho_hermitian, density_scan, metrics)
            self.send_cnmat_density_resonator_frame(rho_hermitian)
            self.send_density_spectral_wavetable_frame(rho_hermitian)
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
            self.observe_visual_frame(
                rho_np,
                density_metrics,
                metrics,
                bohm,
                bloch,
                step_interval,
            )

        self.time += step_interval
        self.step_count += 1
        self.maybe_print_status(time.monotonic())

    def send_grw_sonification_events(self):
        """Publish every GRW event produced by the just-committed engine step."""

        frames = []
        for event in tuple(getattr(self.density_engine, "grw_events", ())):
            frame = self.grw_sonification.publish_event(event)
            if frame is not None:
                frames.append(frame)
        return frames

    def send_born_transition_frame(self):
        """Publish a Born transition once when its lifetime-scaled event begins."""
        source = getattr(self.density_engine, "excitation_source", None)
        state = getattr(source, "state", None)
        required = (
            "event_id",
            "index",
            "initial_label",
            "final_label",
            "audio_frequency_hz",
            "event_probability",
            "sonic_duration_seconds",
            "sonic_linewidth_hz",
            "relative_phase_rad",
            "photon_frequency_hz",
            "wavelength_nm",
            "delta_energy_ev",
            "frequency_mapping",
            "audio_scale_factor",
        )
        if state is None or not all(hasattr(state, name) for name in required):
            return False

        event_id = int(state.event_id)
        if event_id == self.last_born_transition_event_id:
            return False
        self.last_born_transition_event_id = event_id

        packet = [
            event_id,
            int(state.index),
            str(state.initial_label),
            str(state.final_label),
            float(state.audio_frequency_hz),
            float(state.event_probability),
            float(state.sonic_duration_seconds * 1000.0),
            float(state.sonic_linewidth_hz),
            float(state.relative_phase_rad),
            float(state.photon_frequency_hz),
            float(state.wavelength_nm),
            float(state.delta_energy_ev),
            str(state.frequency_mapping),
            float(state.audio_scale_factor),
        ]
        prefix = "/qmw/excitation/born"
        self.osc.send_message(f"{prefix}/transition", packet)
        self.osc.send_message(
            f"{prefix}/active_index",
            [event_id, int(state.index)],
        )
        self.osc.send_message(
            f"{prefix}/audio_frequency_hz",
            float(state.audio_frequency_hz),
        )
        self.osc.send_message(
            f"{prefix}/probability",
            float(state.event_probability),
        )
        self.osc.send_message(
            f"{prefix}/duration_ms",
            float(state.sonic_duration_seconds * 1000.0),
        )
        self.osc.send_message(
            f"{prefix}/linewidth_hz",
            float(state.sonic_linewidth_hz),
        )
        return True

    def send_born_transition_catalog(self, force=False):
        """Publish the complete line set so Max can maintain a stable table."""
        source = getattr(self.density_engine, "excitation_source", None)
        transitions = getattr(source, "transitions", None)
        if not transitions:
            return False
        now = time.monotonic()
        previous = getattr(self, "last_born_catalog_time", None)
        interval = float(getattr(self, "born_catalog_interval", 5.0))
        if not force and previous is not None and now - previous < interval:
            return False
        self.last_born_catalog_time = now
        revision = int(getattr(self, "born_catalog_revision", 1))
        species = str(getattr(source, "species", "unknown"))
        prefix = "/qmw/excitation/born/catalog"
        self.osc.send_message(
            f"{prefix}/begin",
            [revision, len(transitions), species, str(source.frequency_mapping)],
        )
        for index, transition in enumerate(transitions):
            self.osc.send_message(
                f"{prefix}/row",
                [
                    index,
                    species,
                    str(transition.initial.label),
                    str(transition.final.label),
                    float(transition.audio_frequency_hz),
                    float(transition.event_probability),
                    float(transition.sonic_duration_seconds * 1000.0),
                    float(transition.sonic_linewidth_hz),
                    float(transition.photon_frequency_hz * 1.0e-12),
                    float(transition.wavelength_nm),
                    float(transition.delta_energy_ev),
                    float(transition.branching_probability),
                ],
            )
        self.osc.send_message(f"{prefix}/end", [revision, len(transitions)])
        return True

    def set_born_species(self, species):
        """Switch the one-electron isotope preset from the OSC control port."""
        with self.density_state_lock:
            self.density_engine.set_born_species(str(species))
            self.last_born_transition_event_id = None
            self.last_born_catalog_time = None
            self.born_catalog_revision = int(
                getattr(self, "born_catalog_revision", 1)
            ) + 1
        self.send_born_transition_catalog(force=True)
        self.send_born_transition_frame()

    def maybe_send_resonance_event(self, metrics, bloch, dt):
        """Publish threshold-qualified quantum onsets for the Max grain layer.

        A grain is warranted by a positive salience onset in the density
        field, rather than by a continuously running entropy-derived clock.
        A short refractory interval suppresses clustered retriggers.
        """
        entropy = float(np.clip(metrics.get("entropy", 0.0), 0.0, 1.0))
        purity = float(np.clip(metrics.get("purity", 0.0), 0.0, 1.0))
        coherence = float(np.clip(metrics.get("coherence", 0.0), 0.0, 1.0))
        motion = float(
            np.tanh(max(0.0, float(metrics.get("density_field_mean_speed", 0.0))))
        )
        frobenius_delta = abs(float(metrics.get("density_field_delta_frobenius", 0.0)))
        population_delta = abs(float(metrics.get("density_field_delta_population", 0.0)))
        coherence_delta = abs(float(metrics.get("density_field_delta_coherence", 0.0)))
        maximum_delta = abs(float(metrics.get("density_field_delta_max", 0.0)))
        salience = float(
            np.clip(
                0.35 * np.tanh(8.0 * frobenius_delta)
                + 0.25 * np.tanh(16.0 * population_delta)
                + 0.20 * np.tanh(16.0 * coherence_delta)
                + 0.10 * np.tanh(10.0 * maximum_delta)
                + 0.10 * motion,
                0.0,
                1.0,
            )
        )

        circuit_state = getattr(self.density_engine, "circuit_state", {})
        populations = np.asarray(
            circuit_state.get("populations", [1.0] + [0.0] * 15),
            dtype=np.float64,
        ).reshape(-1)
        population_frame = np.zeros(16, dtype=np.float64)
        population_frame[: min(16, populations.size)] = populations[:16]
        population_frame = np.clip(population_frame, 0.0, 1.0)
        basis_index = int(np.argmax(population_frame))
        basis_probability = float(
            population_frame[basis_index]
        )
        qbit_probabilities = []
        for qbit in range(4):
            mask = 1 << (3 - qbit)
            probability_one = sum(
                float(population_frame[index])
                for index in range(16)
                if index & mask
            )
            qbit_probabilities.append(float(np.clip(probability_one, 0.0, 1.0)))
        local_bloch = circuit_state.get(
            "local_bloch", [[0.0, 0.0, 0.0] for _ in range(4)]
        )
        qbit_phases = []
        for qbit in range(4):
            vector = local_bloch[qbit] if qbit < len(local_bloch) else [0.0, 0.0, 0.0]
            qbit_phases.append(
                float(np.clip(np.arctan2(float(vector[1]), float(vector[0])) / np.pi, -1.0, 1.0))
            )
        # This compact stream lets Max own the audible threshold and exposes
        # the actual four-bit pattern plus probability/phase microtiming data.
        self.osc.send_message(
            "/qmw/grain/quantum_state",
            [
                salience,
                basis_index,
                purity,
                coherence,
                entropy,
                basis_probability,
                *qbit_probabilities,
                *qbit_phases,
                *[float(value) for value in population_frame],
            ],
        )

        self.resonance_event_cooldown = max(
            0.0, self.resonance_event_cooldown - max(float(dt), 0.0)
        )
        if self.resonance_previous_salience is None:
            salience_onset = 0.0
        else:
            salience_onset = max(0.0, salience - self.resonance_previous_salience)
        self.resonance_previous_salience = salience
        if (
            self.resonance_event_cooldown > 0.0
            or salience_onset < self.resonance_event_threshold
        ):
            return None

        self.resonance_event_cooldown = self.resonance_event_refractory
        amplitude = float(
            np.clip(0.20 + 0.45 * salience + 0.25 * purity + 0.10 * motion, 0.1, 1.0)
        )
        duration_ms = float(
            np.clip(70.0 + 430.0 * (1.0 - coherence) + 120.0 * entropy, 50.0, 700.0)
        )
        spectral_position = float(
            np.clip(0.5 + 0.5 * float(bloch.get("z", 0.0)), 0.0, 1.0)
        )
        spatial_bias = float(np.clip(float(bloch.get("x", 0.0)), -1.0, 1.0))
        payload = [amplitude, duration_ms, spectral_position, spatial_bias]
        self.osc.send_message("/qmw/event/resonance", payload)
        self.osc.send_message("/qmw/cnmat/density_resonator/trigger", amplitude)
        self.resonance_event_count += 1
        return payload

    def step_bohmian(self, rho_np, dt):
        populations = np.real(np.diag(rho_np))
        populations = np.clip(populations, 0.0, None)
        eigenvalues, eigenvectors = np.linalg.eigh(rho_np)
        dominant_state = eigenvectors[:, np.argmax(eigenvalues)]
        return self.pilot.step(
            amplitudes=np.sqrt(populations),
            phases=np.angle(dominant_state),
            dt=dt,
        )

    def hamiltonian_harmonics(self):
        try:
            hamiltonian = self.density_engine.hamiltonian()
        except Exception:
            return [float(index + 1) for index in range(16)]
        return _positive_hamiltonian_gap_ratios(hamiltonian, count=16)

    def build_metrics(self, density_metrics, density_scan, bohm):
        metrics = dict(density_metrics)
        trajectory = self.trajectory.kinematics()
        metrics["trajectory_speed"] = trajectory["speed"]
        metrics["trajectory_acceleration"] = trajectory["acceleration"]
        metrics["trajectory_direction_change"] = trajectory["direction_change"]
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
        if self.temporal_state_osc is not None:
            flat = np.asarray(rho, dtype=np.complex128).reshape(-1)
            interleaved = np.empty(flat.size * 2, dtype=np.float64)
            interleaved[0::2] = flat.real
            interleaved[1::2] = flat.imag
            self.temporal_state_osc.send_message(
                "/qmw/temporal/source/density",
                [int(self.step_count), int(rho.shape[0]), *interleaved.tolist()],
            )
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

        grainflow_state, zeeman_state, zeeman_preset = grainflow_conductor_state(
            metrics, density_scan
        )
        self.osc.send_message("/qmw/conductor/grainflow", grainflow_state)
        self.osc.send_message(
            "/qmw/conductor/grainflow/v2",
            grainflow_full_conductor_state(metrics, density_scan),
        )
        for event in grainflow_eigenfield_stream_events(metrics, density_scan):
            self.osc.send_message("/qmw/conductor/grainflow/event", event)
        eigenfield_lanes = eigenfield_conductor_lanes(density_scan)
        self.osc.send_message(
            "/qmw/conductor/eigenfield/layout",
            ["x_sectors", 8, "density", "phase", "centroid_y", "speed", "occupancy"],
        )
        self.osc.send_message(
            "/qmw/conductor/eigenfield/lanes",
            _safe_float_list(eigenfield_lanes),
        )
        self.osc.send_message(
            "/qmw/conductor/eigenfield/grid/layout",
            ["row_major", "density", "phase_pi", "occupancy"],
        )
        for resolution in (4, 8, 16):
            self.osc.send_message(
                f"/qmw/conductor/eigenfield/grid/{resolution}",
                _safe_float_list(
                    eigenfield_conductor_grid(rho, density_scan, resolution)
                ),
            )
        self.osc.send_message("/qmw/conductor/zeeman", zeeman_state)
        self.osc.send_message("/qmw/conductor/zeeman/preset", zeeman_preset)

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

    def send_cnmat_density_resonator_frame(self, rho):
        """Publish one atomic 256-mode CNMAT model as sixteen OSC rows."""
        try:
            hamiltonian = self.density_engine.hamiltonian()
            frame = density_matrix_to_cnmat_resonators(rho, hamiltonian)
        except (AttributeError, TypeError, ValueError, np.linalg.LinAlgError):
            return False

        self.cnmat_resonator_revision += 1
        revision = self.cnmat_resonator_revision
        prefix = "/qmw/cnmat/density_resonator"
        self.osc.send_message(
            f"{prefix}/begin",
            [revision, frame.dimension, frame.resonance_count],
        )
        for row_index, triples in enumerate(frame.triple_rows()):
            self.osc.send_message(
                f"{prefix}/row",
                [revision, row_index, *triples],
            )
        self.osc.send_message(f"{prefix}/end", [revision])
        return True

    def send_density_spectral_wavetable_frame(self, rho):
        """Publish one atomic 256-sample harmonic wavetable in four chunks."""

        try:
            hamiltonian = self.density_engine.hamiltonian()
            frame = density_matrix_to_spectral_wavetable(rho, hamiltonian)
        except (AttributeError, TypeError, ValueError, np.linalg.LinAlgError):
            return False

        self.density_wavetable_revision = (
            getattr(self, "density_wavetable_revision", 0) + 1
        )
        revision = self.density_wavetable_revision
        prefix = "/qmw/density/wavetable"
        chunk_size = 64
        chunks = [
            frame.samples[index : index + chunk_size].astype(float).tolist()
            for index in range(0, frame.sample_count, chunk_size)
        ]
        self.osc.send_message(
            f"{prefix}/begin",
            [
                revision,
                frame.sample_count,
                frame.harmonic_count,
                frame.reference_index,
            ],
        )
        for index, values in enumerate(chunks):
            self.osc.send_message(
                f"{prefix}/chunk",
                [revision, index, len(chunks), *values],
            )
        self.osc.send_message(
            f"{prefix}/harmonics",
            [
                revision,
                *frame.harmonic_amplitudes.astype(float).tolist(),
                *frame.harmonic_phases.astype(float).tolist(),
            ],
        )
        self.osc.send_message(f"{prefix}/end", [revision])
        return True

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
            [
                str(value)
                for value in circuit_state.get(
                    "basis_labels",
                    [format(index, "04b") for index in range(16)],
                )
            ],
        )
        self.osc.send_message(
            "/qmw/density/phase_reference",
            int(circuit_state.get("phase_reference", 0)),
        )
        self.osc.send_message(
            "/qmw/density/phases",
            [
                float(value)
                for value in circuit_state.get("basis_phases", [0.0] * 16)
            ],
        )
        self.osc.send_message(
            "/qmw/density/phase_quality",
            [
                float(value)
                for value in circuit_state.get("phase_quality", [0.0] * 16)
            ],
        )
        self.osc.send_message("/qmw/bloch/vector_x", bloch["x"])
        self.osc.send_message("/qmw/bloch/vector_y", bloch["y"])
        self.osc.send_message("/qmw/bloch/vector_z", bloch["z"])
        self.osc.send_message("/qmw/bohm/x", bohm["x"])
        self.osc.send_message("/qmw/bohm/phase", bohm["phase"])
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

        rho_difference = (
            np.abs(rho_np - self.previous_visual_rho)
            if self.previous_visual_rho is not None
            else np.zeros(rho_np.shape, dtype=np.float64)
        )
        self.density_delta_rho_max = float(np.max(rho_difference))
        self.density_delta_rho_mean = float(np.mean(rho_difference))
        self.previous_visual_rho = rho_np.copy()

    def observe_visual_frame(
        self,
        rho_np,
        density_metrics,
        metrics,
        bohm,
        bloch,
        dt,
    ):
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

        # Compute the weighted matrix once. Previously purity() and
        # coherence_l1() each traversed the complete lifetime independently
        # on every diagnostics frame.
        memory_rho = self.quantum_memory.weighted_density_matrix()
        frame = frame_from_engine_snapshot(
            t=self.time,
            dt=dt,
            rho=rho_np,
            hamiltonian=self.hamiltonian,
            density_metrics=density_metrics,
            density_engine=self.density_engine,
            extra_observables=metrics,
            memory={
                "size": self.quantum_memory.size(),
                "purity": self.quantum_memory.purity(memory_rho),
                "coherence": self.quantum_memory.coherence_l1(memory_rho),
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
        fields = [
            f"step={self.step_count}",
            f"purity={self.latest_metrics.get('purity', 0.0):.4f}",
            f"entropy={self.latest_metrics.get('entropy', 0.0):.4f}",
            f"coherence={self.latest_metrics.get('coherence', 0.0):.4f}",
            f"osc={self.osc_frame_count}",
        ]
        if self.clock_source == "external":
            fields.extend(
                [
                    f"tick={self.external_tick_hz:.1f}Hz",
                    f"received={self.external_tick_count}",
                    f"coalesced={self.coalesced_tick_count}",
                ]
            )
        print("\r" + " ".join(fields), end="", flush=True)

    def run(self):
        if self.clock_source == "external":
            return self.run_external_clock()

        try:
            while True:
                started = time.monotonic()
                self.step()
                elapsed = time.monotonic() - started
                time.sleep(max(0.0, self.interval - elapsed))
        except KeyboardInterrupt:
            if not self.quiet:
                print("\nQMW resonator engine stopped.")

    def run_external_clock(self):
        if not self.quiet:
            print("Waiting for Max ticks on /qmw/engine/tick ...")

        try:
            while True:
                self.external_tick_event.wait()
                with self.external_tick_lock:
                    # Clear while holding the same lock used by the OSC
                    # callback. A tick arriving immediately afterward sets a
                    # fresh event and will be processed after this step.
                    self.external_tick_event.clear()
                    dt = self.pending_external_dt
                    self.pending_external_dt = None
                self.step(dt=dt)
        except KeyboardInterrupt:
            if not self.quiet:
                print("\nQMW externally clocked resonator engine stopped.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Quiet resonator-focused QMW density-field OSC engine."
    )
    parser.add_argument("--audio-path", type=Path, default=None)
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=7400)
    parser.add_argument(
        "--sc-osc-port",
        type=int,
        default=None,
        help=(
            "Optionally mirror the complete engine OSC stream to a "
            "SuperCollider language port (normally 57120)."
        ),
    )
    parser.add_argument("--visual-osc-port", type=int, default=7401)
    parser.add_argument(
        "--grw-timing-port",
        type=int,
        default=7441,
        help=(
            "Mirror committed GRW frames to the eigenfield timing control "
            "port; use a negative value to disable the mirror."
        ),
    )
    parser.add_argument(
        "--grw-geometry-port",
        type=int,
        default=7462,
        help=(
            "Mirror committed GRW frames to the slow developmental-geometry "
            "bridge; use a negative value to disable the mirror."
        ),
    )
    parser.add_argument(
        "--temporal-state-port",
        type=int,
        default=None,
        help="Private density-state output for the temporal mechanics bridge",
    )
    parser.add_argument("--status-osc-port", type=int, default=7410)
    parser.add_argument("--control-port", type=int, default=7402)
    parser.add_argument(
        "--control-host",
        default="127.0.0.1",
        help="Local bind address for the QMW control server",
    )
    parser.add_argument("--engine-hz", type=float, default=100.0)
    parser.add_argument("--density-field-hz", type=float, default=30.0)
    parser.add_argument(
        "--zx-density-matrix-port",
        type=int,
        default=7498,
        help=(
            "Publish complete post-evolution 16x16 density frames to the "
            "Max ZX density engine; use a negative value to disable."
        ),
    )
    parser.add_argument(
        "--zx-density-matrix-hz",
        type=float,
        default=10.0,
    )
    parser.add_argument("--diagnostics-hz", type=float, default=8.0)
    parser.add_argument("--status-hz", type=float, default=0.5)
    parser.add_argument(
        "--osc-profile",
        choices=["resonator", "full"],
        default="resonator",
    )
    parser.add_argument(
        "--excitation-source",
        default="schrodinger_interference",
        help=(
            "Density-engine excitation source (for example: internal, "
            "born_transition, hydrogen_spectrum, hydrogen_orbital, "
            "schrodinger_packet, or schrodinger_interference)."
        ),
    )
    parser.add_argument(
        "--excitation-drive",
        type=float,
        default=None,
        help=(
            "Override the selected excitation mode's drive strength "
            "(non-negative; default: use the mode profile)."
        ),
    )
    parser.add_argument(
        "--born-species",
        choices=[
            "H-1",
            "H-2",
            "H-3",
            "He-3+",
            "He-4+",
            "Li-6++",
            "Li-7++",
        ],
        default="H-1",
        help="One-electron isotope preset used by born_transition.",
    )
    parser.add_argument(
        "--born-selection-mode",
        choices=["sequential", "stochastic"],
        default="sequential",
    )
    parser.add_argument(
        "--born-time-scale",
        type=float,
        default=100_000_000.0,
        help="Multiply physical lifetimes into playable seconds.",
    )
    parser.add_argument("--born-duration-min-ms", type=float, default=80.0)
    parser.add_argument("--born-duration-max-ms", type=float, default=2_000.0)
    parser.add_argument(
        "--clock-source",
        choices=["internal", "external"],
        default="internal",
        help=(
            "Use the internal rate-limited loop or wait for OSC ticks at "
            "/qmw/engine/tick on the control port."
        ),
    )
    parser.add_argument(
        "--temporal-crystal-mode",
        choices=TEMPORAL_CRYSTAL_MODES,
        default=None,
        help="Enable one in-process temporal protocol",
    )
    parser.add_argument(
        "--temporal-crystal-rate",
        type=float,
        default=2.0,
        help="Logical temporal steps per second (default: 2 Hz)",
    )
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--no-control-server",
        action="store_true",
        help="Do not start the engine visual/control OSC server.",
    )
    parser.add_argument(
        "--disable-circuit-bridge-control",
        action="store_true",
        help="Do not start the internal circuit-builder OSC control server.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.clock_source == "external" and args.no_control_server:
        raise SystemExit(
            "External clock mode requires the control server; "
            "remove --no-control-server."
        )
    qmw = MLXQuantumResonatorEngine(
        audio_path=args.audio_path,
        osc_host=args.osc_host,
        osc_port=args.osc_port,
        sc_osc_port=args.sc_osc_port,
        temporal_state_port=args.temporal_state_port,
        visual_osc_port=args.visual_osc_port,
        grw_timing_port=(
            args.grw_timing_port if args.grw_timing_port >= 0 else None
        ),
        grw_geometry_port=(
            args.grw_geometry_port if args.grw_geometry_port >= 0 else None
        ),
        status_osc_port=args.status_osc_port,
        zx_density_matrix_port=(
            args.zx_density_matrix_port
            if args.zx_density_matrix_port >= 0
            else None
        ),
        zx_density_matrix_hz=args.zx_density_matrix_hz,
        engine_hz=args.engine_hz,
        density_field_hz=args.density_field_hz,
        diagnostics_hz=args.diagnostics_hz,
        status_hz=args.status_hz,
        osc_profile=args.osc_profile,
        clock_source=args.clock_source,
        temporal_crystal_mode=args.temporal_crystal_mode,
        temporal_crystal_rate=args.temporal_crystal_rate,
        excitation_source=args.excitation_source,
        excitation_drive=args.excitation_drive,
        born_species=args.born_species,
        born_selection_mode=args.born_selection_mode,
        born_time_scale=args.born_time_scale,
        born_duration_min_ms=args.born_duration_min_ms,
        born_duration_max_ms=args.born_duration_max_ms,
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
            host=args.control_host,
            port=args.control_port,
        )

    qmw.run()
