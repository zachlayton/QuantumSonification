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


def _safe_float_list(values):
    return [float(value) for value in np.asarray(values, dtype=np.float64).reshape(-1)]


WAVETABLE_SAMPLE_INDEX = list(range(256))
WAVETABLE_SAMPLE_PHASE = [index / 256.0 for index in WAVETABLE_SAMPLE_INDEX]
DEFAULT_WAVETABLE_TABLES_PER_AXIS = 1
WAVETABLE_TABLE_SIZE = 256


def wavetable_bank_dimensions(tables_per_axis=DEFAULT_WAVETABLE_TABLES_PER_AXIS):
    axis_count = int(np.clip(int(tables_per_axis), 1, 16))
    table_count = axis_count ** 3
    bank_size = table_count * WAVETABLE_TABLE_SIZE
    return axis_count, table_count, bank_size


def _density_bank_metrics(rho):
    hermitian = 0.5 * (rho + rho.conj().T)
    purity = float(np.real(np.trace(hermitian @ hermitian)))
    off_diagonal = hermitian - np.diag(np.diag(hermitian))
    coherence = float(np.sum(np.abs(off_diagonal)))
    eigenvalues = np.clip(np.linalg.eigvalsh(hermitian).real, 1e-12, 1.0)
    entropy = float(-np.sum(eigenvalues * np.log2(eigenvalues)))
    return purity, coherence, entropy


def _axis_bin(value, count):
    return int(np.clip(np.floor(float(value) * count), 0, count - 1))


def density_bank_position(rho, tables_per_axis=DEFAULT_WAVETABLE_TABLES_PER_AXIS):
    purity, coherence, entropy = _density_bank_metrics(np.asarray(rho, dtype=np.complex128))
    purity_norm = np.clip((purity - 1.0 / 16.0) / (1.0 - 1.0 / 16.0), 0.0, 1.0)
    coherence_norm = np.clip(coherence / 15.0, 0.0, 1.0)
    entropy_norm = np.clip(entropy / 4.0, 0.0, 1.0)

    px = _axis_bin(purity_norm, tables_per_axis)
    cy = _axis_bin(coherence_norm, tables_per_axis)
    ez = _axis_bin(entropy_norm, tables_per_axis)
    table_index = px + tables_per_axis * (cy + tables_per_axis * ez)
    start = table_index * WAVETABLE_TABLE_SIZE
    end = start + WAVETABLE_TABLE_SIZE

    return {
        "table_index": int(table_index),
        "write_start": int(start),
        "write_end": int(end),
        "axis": [int(px), int(cy), int(ez)],
        "axis_values": [float(purity_norm), float(coherence_norm), float(entropy_norm)],
        "metrics": [float(purity), float(coherence), float(entropy)],
        "global_index": list(range(start, end)),
    }


def density_matrix_wavetable(
    rho,
    previous_table=None,
    smoothing=0.72,
    tables_per_axis=DEFAULT_WAVETABLE_TABLES_PER_AXIS,
):
    """
    Convert a 16x16 density matrix into a dense 256-sample wavetable.

    Directly flattening rho is usually too sparse for audio. This treats the
    matrix as complex spectral/control data, then turns it into a single-cycle
    waveform that is ready to write into a Max buffer~.
    """
    matrix = np.asarray(rho, dtype=np.complex128)
    if matrix.shape != (16, 16):
        raise ValueError(f"density wavetable expects a 16x16 matrix, got {matrix.shape}")

    hermitian = 0.5 * (matrix + matrix.conj().T)
    flat = hermitian.reshape(-1)

    # Complex spectral interpretation: sparse/equal quantum entries become a
    # smooth time-domain cycle rather than mostly zero table samples.
    spectral = np.fft.ifft(flat).real

    # A spatial scan keeps the visible 16x16 structure present in the tone.
    real_scan = hermitian.real.reshape(-1)
    imag_scan = hermitian.imag.reshape(-1)
    magnitude_scan = np.sqrt(np.abs(flat))
    phase_scan = np.sin(np.angle(flat))

    table = (
        0.56 * spectral
        + 0.20 * real_scan
        + 0.16 * imag_scan
        + 0.08 * magnitude_scan * phase_scan
    )

    table = table - float(np.mean(table))
    rms = float(np.sqrt(np.mean(table * table)))
    if rms > 1e-12:
        table = table / (4.0 * rms)

    peak = float(np.max(np.abs(table)))
    if peak > 1.0:
        table = table / peak

    if previous_table is not None:
        previous = np.asarray(previous_table, dtype=np.float64)
        if previous.shape == table.shape:
            amount = float(np.clip(smoothing, 0.0, 0.98))
            table = amount * previous + (1.0 - amount) * table

    table = np.clip(table, -1.0, 1.0)

    magnitude = np.abs(flat)
    mag_peak = float(np.max(magnitude))
    if mag_peak > 1e-12:
        magnitude_norm = magnitude / mag_peak
    else:
        magnitude_norm = magnitude

    return {
        "buffer": table,
        "raw_real": np.clip(flat.real, -1.0, 1.0),
        "raw_imag": np.clip(flat.imag, -1.0, 1.0),
        "magnitude": np.clip(magnitude_norm, 0.0, 1.0),
        "phase_pi": np.clip(np.angle(flat) / np.pi, -1.0, 1.0),
        "index": WAVETABLE_SAMPLE_INDEX,
        "phase_index": WAVETABLE_SAMPLE_PHASE,
        "bank": density_bank_position(hermitian, tables_per_axis=tables_per_axis),
        "rms": float(np.sqrt(np.mean(table * table))),
        "peak": float(np.max(np.abs(table))),
        "range": float(np.max(table) - np.min(table)),
    }


class MLXQuantumEngine:
    def __init__(
        self,
        audio_path=None,
        osc_host="127.0.0.1",
        osc_port=7400,
        visual_osc_port=7401,
        mutation_amount=0.5,
        interval=0.01,
        excitation_source="schrodinger_interference",
        bohmian_n_modes=16,
        bohmian_grid_size=512,
        bohmian_mobility=0.28,
        bohmian_damping=0.86,
        bohmian_field_smoothing=0.14,
        wavetable_tables_per_axis=DEFAULT_WAVETABLE_TABLES_PER_AXIS,
    ):
        if audio_path is None:
            project_root = Path(__file__).resolve().parent
            audio_path = project_root / "materials" / "test.wav"

        self.audio_path = str(Path(audio_path))
        self.interval = float(interval)

        # ------------------------------------------------------------
        # Moving audio-window analysis
        # ------------------------------------------------------------
        self.audio_analyzer = AudioWindowAnalyzer(
            self.audio_path,
            window_seconds=1.0,
            analysis_hop_seconds=0.10,
            playback_rate=1.0,
            loop=True,
        )

        # ------------------------------------------------------------
        # OSC outputs
        # ------------------------------------------------------------
        self.osc = SimpleUDPClient(osc_host, osc_port)
        self.visual_osc = SimpleUDPClient(
            osc_host,
            visual_osc_port,
        )
        self.oscilloscope = QuantumOscilloscope(
            QuantumOscilloscopeConfig(
                osc_host=osc_host,
                osc_port=osc_port,
                visual_osc_port=visual_osc_port,
                send_pauli_aliases=True,
            )
        )
        self.time = 0.0

        # Density-matrix point-cloud update timing.
        self.density_visual_elapsed = 0.0
        self.density_visual_interval = 0.033
        self.previous_visual_rho = None
        self.previous_density_field_rho = None

        self.density_delta_rho_max = 0.0
        self.density_delta_rho_mean = 0.0
        self.previous_wavetable = None
        self.configure_wavetable_bank(wavetable_tables_per_axis)

        # ------------------------------------------------------------
        # Hamiltonian and density-matrix engine
        # ------------------------------------------------------------
        self.hamiltonian = HamiltonianState(
            x=0.0,
            y=0.0,
            z=1.0,
        )

        self.mutator = HamiltonianMutator(
            amount=mutation_amount,
        )

        self.density_engine = DensityMatrixEngine(excitation_source=excitation_source)
        self.density_adapter = DensityAdapter(
            self.density_engine,
        )

        # ------------------------------------------------------------
        # Feedback / memory / field layers
        # ------------------------------------------------------------
        self.history = FeedbackHistory()
        self.detector = EventDetector()

        self.quantum_memory = QuantumMemory(decay=0.7)
        self.quantum_field = QuantumField(
            self.quantum_memory,
        )
        self.trajectory = QuantumTrajectory(
            self.quantum_field,
        )

        # ------------------------------------------------------------
        # Performer perturbation controls
        # ------------------------------------------------------------
        self.visual_perturb = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "gain": 1.0,
        }

        # ------------------------------------------------------------
        # Bohmian pilot-wave layer
        # ------------------------------------------------------------
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

    def set_visual_perturb(self, axis, value):
        self.visual_perturb[axis] = float(value)
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
            print(f"Unknown Bohmian parameter: {parameter}")
            return

        low, high = ranges[parameter]
        value = float(np.clip(value, low, high))
        target = "field_smoothing" if parameter == "smoothing" else parameter
        self.bohmian_controls[target] = value
        setattr(self.pilot, target, value)
        print(f"BOHMIAN {target}: {value:.4f}")

    def configure_wavetable_bank(self, tables_per_axis):
        axis_count, table_count, bank_size = wavetable_bank_dimensions(
            tables_per_axis
        )
        self.wavetable_tables_per_axis = axis_count
        self.wavetable_table_count = table_count
        self.wavetable_bank_size = bank_size
        self.wavetable_bank = np.zeros(bank_size, dtype=np.float64)
        self.wavetable_bank_write_counts = np.zeros(table_count, dtype=np.int64)
        self.wavetable_bank_next_index = 0
        print(
            "WAVETABLE BANK "
            f"axis={axis_count} count={table_count} size={bank_size}"
        )

    def set_wavetable_parameter(self, name, value):
        parameter = str(name).strip().lower()
        if parameter not in {"tables_per_axis", "axis"}:
            print(f"Unknown wavetable parameter: {parameter}")
            return

        self.configure_wavetable_bank(value)

    def step(self):
        # ------------------------------------------------------------
        # 1. Read the current moving audio window.
        # ------------------------------------------------------------
        audio = self.audio_analyzer.next_window(
            dt=self.interval,
        )

        # ------------------------------------------------------------
        # 2. Audio mutates the Hamiltonian.
        # ------------------------------------------------------------
        self.hamiltonian = self.mutator.mutate_from_audio(
            self.hamiltonian,
            audio,
        )

        # ------------------------------------------------------------
        # 3. Evolve the density matrix.
        # ------------------------------------------------------------
        self.density_adapter.apply_hamiltonian_state(
            self.hamiltonian,
        )

        rho = self.density_adapter.step(self.interval)

                # ------------------------------------------------------------
        # Circuit state from DensityMatrixEngine -> Max OSC.
        # ------------------------------------------------------------
        circuit_state = getattr(
            self.density_engine,
            "circuit_state",
            {},
        )

        local_bloch = circuit_state.get(
            "local_bloch",
            [[0.0, 0.0, 0.0] for _ in range(4)],
        )

        for q in range(4):
            self.osc.send_message(
                f"/qmw/qubit/{q}/bloch",
                [
                    float(local_bloch[q][0]),
                    float(local_bloch[q][1]),
                    float(local_bloch[q][2]),
                ],
            )

            self.visual_osc.send_message(
                f"/qmw/qubit/{q}/bloch",
                [
                    float(local_bloch[q][0]),
                    float(local_bloch[q][1]),
                    float(local_bloch[q][2]),
                ],
            )

        circuit_populations = circuit_state.get(
            "populations",
            [0.0] * 16,
        )

        self.osc.send_message(
            "/qmw/circuit/qasm_lines",
            [
                str(value)
                for value in circuit_state.get("qasm_lines", [])
            ],
        )
        self.osc.send_message(
            "/qmw/density/populations",
            [float(value) for value in circuit_populations],
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
                for value in circuit_state.get(
                    "basis_phases",
                    [0.0] * 16,
                )
            ],
        )
        self.osc.send_message(
            "/qmw/density/phase_quality",
            [
                float(value)
                for value in circuit_state.get(
                    "phase_quality",
                    [0.0] * 16,
                )
            ],
        )

        # Convert only for NumPy visualization / pilot-wave operations.
        rho_np = np.asarray(
            rho,
            dtype=np.complex128,
        )

        rho_hermitian = 0.5 * (rho_np + rho_np.conj().T)

        density_scan = self.density_scanner.step(
            rho_hermitian,
            self.previous_density_field_rho,
            self.interval,
        )
        self.previous_density_field_rho = rho_hermitian.copy()

        self.osc.send_message(
            "/qmw/density_field/particle_count",
            int(len(density_scan["sample_indices"])),
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
            "/qmw/density_field/vx",
            _safe_float_list(density_scan["velocities"][:, 0]),
        )
        self.osc.send_message(
            "/qmw/density_field/vy",
            _safe_float_list(density_scan["velocities"][:, 1]),
        )
        self.osc.send_message(
            "/qmw/density_field/speed",
            _safe_float_list(density_scan["speeds"]),
        )
        self.osc.send_message(
            "/qmw/density_field/sample_index",
            [int(value) for value in density_scan["sample_indices"]],
        )
        self.osc.send_message(
            "/qmw/density_field/real",
            _safe_float_list(density_scan["samples"].real),
        )
        self.osc.send_message(
            "/qmw/density_field/imag",
            _safe_float_list(density_scan["samples"].imag),
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
            "/qmw/density_field/delta/frobenius",
            density_scan["delta_frobenius"],
        )
        self.osc.send_message(
            "/qmw/density_field/delta/max",
            density_scan["delta_max"],
        )
        self.osc.send_message(
            "/qmw/density_field/delta/population",
            density_scan["delta_population"],
        )
        self.osc.send_message(
            "/qmw/density_field/delta/coherence",
            density_scan["delta_coherence"],
        )
        self.osc.send_message(
            "/qmw/density_field/mean_speed",
            density_scan["mean_speed"],
        )
        self.osc.send_message(
            "/qmw/density_field/max_speed",
            density_scan["max_speed"],
        )
        self.osc.send_message(
            "/qmw/density_field/speed_saturation",
            density_scan["speed_saturation"],
        )
        self.osc.send_message(
            "/qmw/density_field/speed_spread",
            density_scan["speed_spread"],
        )
        self.osc.send_message(
            "/qmw/density_field/magnitude_spread",
            density_scan["magnitude_spread"],
        )
        self.osc.send_message(
            "/qmw/density_field/phase_spread",
            density_scan["phase_spread"],
        )

        basis_labels = [format(index, "04b") for index in range(16)]
        self.osc.send_message(
            "/qmw/density_field/basis_labels",
            basis_labels,
        )
        self.osc.send_message(
            "/qmw/density_field/sample_source",
            "scanner_interpolated_2d_density_matrix",
        )

        for particle_index in range(int(len(density_scan["sample_indices"]))):
            base = f"/qmw/density_field/p/{particle_index}"
            basis = f"/qmw/density_field/basis/{particle_index}"
            basis_label = basis_labels[particle_index]
            diagonal_value = rho_hermitian[particle_index, particle_index]

            self.osc.send_message(
                f"{base}/xy",
                [
                    float(density_scan["positions"][particle_index, 0]),
                    float(density_scan["positions"][particle_index, 1]),
                ],
            )
            self.osc.send_message(
                f"{base}/velocity",
                [
                    float(density_scan["velocities"][particle_index, 0]),
                    float(density_scan["velocities"][particle_index, 1]),
                ],
            )
            self.osc.send_message(
                f"{base}/speed",
                float(density_scan["speeds"][particle_index]),
            )
            self.osc.send_message(
                f"{base}/sample_index",
                int(density_scan["sample_indices"][particle_index]),
            )
            self.osc.send_message(
                f"{base}/real",
                float(density_scan["samples"][particle_index].real),
            )
            self.osc.send_message(
                f"{base}/imag",
                float(density_scan["samples"][particle_index].imag),
            )
            self.osc.send_message(
                f"{base}/magnitude",
                float(density_scan["magnitudes"][particle_index]),
            )
            self.osc.send_message(
                f"{base}/phase",
                float(density_scan["phases"][particle_index]),
            )
            self.osc.send_message(
                f"{basis}/label",
                basis_label,
            )
            self.osc.send_message(
                f"{basis}/diagonal/real",
                float(diagonal_value.real),
            )
            self.osc.send_message(
                f"{basis}/diagonal/imag",
                float(diagonal_value.imag),
            )
            self.osc.send_message(
                f"{basis}/diagonal/magnitude",
                float(abs(diagonal_value)),
            )
            self.osc.send_message(
                f"{basis}/diagonal/phase",
                float(np.angle(diagonal_value)),
            )
            self.osc.send_message(
                f"{basis}/diagonal/probability",
                float(np.clip(diagonal_value.real, 0.0, 1.0)),
            )
            self.osc.send_message(
                f"{basis}/scanner/particle_index",
                int(particle_index),
            )
            self.osc.send_message(
                f"{basis}/scanner/xy",
                [
                    float(density_scan["positions"][particle_index, 0]),
                    float(density_scan["positions"][particle_index, 1]),
                ],
            )
            self.osc.send_message(
                f"{basis}/scanner/velocity",
                [
                    float(density_scan["velocities"][particle_index, 0]),
                    float(density_scan["velocities"][particle_index, 1]),
                ],
            )
            self.osc.send_message(
                f"{basis}/scanner/speed",
                float(density_scan["speeds"][particle_index]),
            )
            self.osc.send_message(
                f"{basis}/scanner/sample_index",
                int(density_scan["sample_indices"][particle_index]),
            )
            self.osc.send_message(
                f"{basis}/scanner/real",
                float(density_scan["samples"][particle_index].real),
            )
            self.osc.send_message(
                f"{basis}/scanner/imag",
                float(density_scan["samples"][particle_index].imag),
            )
            self.osc.send_message(
                f"{basis}/scanner/magnitude",
                float(density_scan["magnitudes"][particle_index]),
            )
            self.osc.send_message(
                f"{basis}/scanner/phase",
                float(density_scan["phases"][particle_index]),
            )

        wavetable = density_matrix_wavetable(
            rho_hermitian,
            previous_table=self.previous_wavetable,
            tables_per_axis=self.wavetable_tables_per_axis,
        )
        self.previous_wavetable = wavetable["buffer"].copy()
        semantic_bank = wavetable["bank"]
        table_index = int(self.wavetable_bank_next_index)
        write_start = table_index * WAVETABLE_TABLE_SIZE
        write_end = write_start + WAVETABLE_TABLE_SIZE
        self.wavetable_bank[write_start:write_end] = wavetable["buffer"]
        self.wavetable_bank_write_counts[table_index] += 1
        self.wavetable_bank_next_index = (
            self.wavetable_bank_next_index + 1
        ) % self.wavetable_table_count

        self.osc.send_message("/qmw/wavetable/size", 256)
        self.osc.send_message("/qmw/wavetable/index", wavetable["index"])
        self.osc.send_message("/qmw/wavetable/phase_index", wavetable["phase_index"])
        self.osc.send_message("/qmw/wavetable/table_index", table_index)
        self.osc.send_message(
            "/qmw/wavetable/buffer",
            _safe_float_list(wavetable["buffer"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/tables_per_axis",
            self.wavetable_tables_per_axis,
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/table_count",
            self.wavetable_table_count,
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/table_size",
            WAVETABLE_TABLE_SIZE,
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/size",
            self.wavetable_bank_size,
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/table_index",
            table_index,
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/write_start",
            write_start,
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/write_end",
            write_end,
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/axis",
            semantic_bank["axis"],
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/axis_values",
            semantic_bank["axis_values"],
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/metrics",
            semantic_bank["metrics"],
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/semantic_table_index",
            int(semantic_bank["table_index"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/semantic_write_start",
            int(semantic_bank["write_start"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/global_index",
            list(range(write_start, write_end)),
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/write_buffer",
            _safe_float_list(wavetable["buffer"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/write_count",
            int(self.wavetable_bank_write_counts[table_index]),
        )
        self.osc.send_message(
            "/qmw/wavetable/bank/write_counts",
            [int(value) for value in self.wavetable_bank_write_counts],
        )
        self.osc.send_message(
            "/qmw/wavetable/raw_real",
            _safe_float_list(wavetable["raw_real"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/raw_imag",
            _safe_float_list(wavetable["raw_imag"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/magnitude",
            _safe_float_list(wavetable["magnitude"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/phase_pi",
            _safe_float_list(wavetable["phase_pi"]),
        )
        self.osc.send_message(
            "/qmw/wavetable/rms",
            wavetable["rms"],
        )
        self.osc.send_message(
            "/qmw/wavetable/peak",
            wavetable["peak"],
        )
        self.osc.send_message(
            "/qmw/wavetable/range",
            wavetable["range"],
        )

        eigenvalues, eigenvectors = np.linalg.eigh(rho_hermitian)

        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[order]
        eigenvectors = eigenvectors[:, order]

        self.visual_osc.send_message(
            "/qmw/density/eigenvalues",
            [float(v.real) for v in eigenvalues],
        )

        for mode_index in range(16):
            vec = eigenvectors[:, mode_index]

            self.visual_osc.send_message(
                f"/qmw/density/eigenvector/{mode_index}/real",
                [float(v.real) for v in vec],
            )

            self.visual_osc.send_message(
                f"/qmw/density/eigenvector/{mode_index}/imag",
                [float(v.imag) for v in vec],
            )

        # ------------------------------------------------------------
        # 4. Density-matrix point-cloud output to Processing.
        # ------------------------------------------------------------
        self.density_visual_elapsed += self.interval

        if (
            self.density_visual_elapsed
            >= self.density_visual_interval
        ):
            self.density_visual_elapsed = 0.0

            if self.previous_visual_rho is None:
                self.previous_visual_rho = rho_np.copy()

            rho_difference = np.abs(
                rho_np - self.previous_visual_rho
            )

            max_density_change = float(
                np.max(rho_difference)
            )

            mean_density_change = float(
                np.mean(rho_difference)
            )

            print(
                f"DENSITY Δρ  "
                f"max={max_density_change:.8f} "
                f"mean={mean_density_change:.8f}"
            )

            self.density_delta_rho_max = max_density_change
            self.density_delta_rho_mean = mean_density_change

            self.previous_visual_rho = rho_np.copy()

        # ------------------------------------------------------------
        # 5. Density metrics.
        # ------------------------------------------------------------
        density_metrics = self.density_adapter.metrics(rho)

        # ------------------------------------------------------------
        # 6. Bohmian pilot-wave field derived from density matrix.
        # ------------------------------------------------------------
        populations = np.real(np.diag(rho_np))
        populations = np.clip(
            populations,
            0.0,
            None,
        )

        eigenvalues, eigenvectors = np.linalg.eigh(rho_np)

        dominant_state = eigenvectors[
            :,
            np.argmax(eigenvalues),
        ]

        amplitudes = np.sqrt(populations)
        phases = np.angle(dominant_state)

        bohm = self.pilot.step(
            amplitudes=amplitudes,
            phases=phases,
            dt=self.interval,
        )

        # ------------------------------------------------------------
        # 7. Reduced Bloch coordinates.
        # ------------------------------------------------------------
        x = density_metrics.get("bloch_x", 0.0)
        y = density_metrics.get("bloch_y", 0.0)
        z = density_metrics.get("bloch_z", 0.0)

        bloch = {
            "x": x,
            "y": y,
            "z": z,
        }

        # ------------------------------------------------------------
        # 8. Performer-controlled display perturbation.
        # ------------------------------------------------------------
        perturb_x = self.visual_perturb["x"]
        perturb_y = self.visual_perturb["y"]
        perturb_z = self.visual_perturb["z"]
        visual_gain = self.visual_perturb["gain"]

        perturbed_bloch_x = (
            x + perturb_x
        ) * visual_gain

        perturbed_bloch_y = (
            y + perturb_y
        ) * visual_gain

        perturbed_bloch_z = (
            z + perturb_z
        ) * visual_gain

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

        # ------------------------------------------------------------
        # 9. Quantum memory and trajectory.
        # ------------------------------------------------------------
        self.quantum_memory.encode(
            rho=rho,
            hamiltonian=self.hamiltonian,
            audio_descriptor=audio,
        )

        trajectory = self.trajectory.kinematics()
        trajectory_speed = trajectory["speed"]
        trajectory_acceleration = trajectory["acceleration"]
        trajectory_direction_change = trajectory["direction_change"]

        metrics = dict(density_metrics)

        metrics["trajectory_speed"] = trajectory_speed
        metrics["trajectory_acceleration"] = (
            trajectory_acceleration
        )
        metrics["trajectory_direction_change"] = (
            trajectory_direction_change
        )

        metrics["bohm_x"] = bohm["x"]
        metrics["bohm_speed"] = bohm["speed"]
        metrics["bohm_density"] = bohm["density"]
        metrics["bohm_node_proximity"] = (
            bohm["node_proximity"]
        )
        metrics["bohm_curvature"] = bohm["curvature"]
        metrics["bohm_mobility"] = self.bohmian_controls["mobility"]
        metrics["bohm_damping"] = self.bohmian_controls["damping"]
        metrics["bohm_field_smoothing"] = self.bohmian_controls["field_smoothing"]
        metrics["density_field_delta_frobenius"] = density_scan["delta_frobenius"]
        metrics["density_field_delta_max"] = density_scan["delta_max"]
        metrics["density_field_delta_population"] = density_scan["delta_population"]
        metrics["density_field_delta_coherence"] = density_scan["delta_coherence"]
        metrics["density_field_mean_speed"] = density_scan["mean_speed"]
        metrics["density_field_max_speed"] = density_scan["max_speed"]
        metrics["density_field_speed_saturation"] = density_scan["speed_saturation"]
        metrics["density_field_speed_spread"] = density_scan["speed_spread"]
        metrics["density_field_magnitude_spread"] = density_scan["magnitude_spread"]
        metrics["density_field_phase_spread"] = density_scan["phase_spread"]
        metrics["density_delta_rho_max"] = self.density_delta_rho_max
        metrics["density_delta_rho_mean"] = self.density_delta_rho_mean

        # ------------------------------------------------------------
        # 10. Event detection.
        # ------------------------------------------------------------
        event_result = self.detector.detect(
            metrics=metrics,
            audio_descriptor=audio,
        )

        self.quantum_memory.annotate_latest(
            events=event_result["events"],
            metrics=metrics,
        )

        self.history.add(
            audio_descriptor=audio,
            hamiltonian=self.hamiltonian,
            bloch=bloch,
        )

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
                "bloch_x": x,
                "bloch_y": y,
                "bloch_z": z,
                "perturbed_bloch_x": perturbed_bloch_x,
                "perturbed_bloch_y": perturbed_bloch_y,
                "perturbed_bloch_z": perturbed_bloch_z,
                "field_strength": trajectory_speed,
                "field_acceleration": trajectory_acceleration,
            },
        )
        self.oscilloscope.observe(frame)
        self.time += self.interval

        # ------------------------------------------------------------
        # 11. Main OSC output to Max.
        # ------------------------------------------------------------
        for event in event_result["events"]:
            self.osc.send_message(
                "/qmw/event",
                event,
            )

        self.osc.send_message(
            "/qmw/bloch/vector_x",
            x,
        )
        self.osc.send_message(
            "/qmw/bloch/vector_y",
            y,
        )
        self.osc.send_message(
            "/qmw/bloch/vector_z",
            z,
        )

        self.osc.send_message("/qmw/bohm/x", bohm["x"])
        self.osc.send_message("/qmw/bohm/speed", bohm["speed"])
        self.osc.send_message("/qmw/bohm/density", bohm["density"])
        self.osc.send_message("/qmw/bohm/node_proximity", bohm["node_proximity"])
        self.osc.send_message("/qmw/bohm/curvature", bohm["curvature"])
        self.osc.send_message(
            "/qmw/bohm/mobility",
            self.bohmian_controls["mobility"],
        )
        self.osc.send_message(
            "/qmw/bohm/damping",
            self.bohmian_controls["damping"],
        )
        self.osc.send_message(
            "/qmw/bohm/field_smoothing",
            self.bohmian_controls["field_smoothing"],
        )

        self.osc.send_message(
            "/qmw/density/purity",
            metrics.get("purity", 0.0),
        )
        self.osc.send_message(
            "/qmw/density/coherence_l1",
            metrics.get("coherence", 0.0),
        )
        self.osc.send_message(
            "/qmw/density/von_neumann_entropy",
            metrics.get("entropy", 0.0),
        )

        # ------------------------------------------------------------
        # Terminal report.
        # ------------------------------------------------------------
        print()
        print("MLX Quantum Engine")
        print("------------------")
        print(
            "Hamiltonian:",
            self.hamiltonian.as_pauli_terms(),
        )
        print("Bloch:", bloch)
        print("Density metrics:", density_metrics)
        print("Events:", event_result["events"])
        print("History size:", self.history.size())
        print(
            "Quantum memory size:",
            self.quantum_memory.size(),
        )
        print(
            "Memory purity:",
            self.quantum_memory.purity(),
        )
        print(
            "Memory coherence:",
            self.quantum_memory.coherence_l1(),
        )
        print("Trajectory speed:", trajectory_speed)
        print(
            "Trajectory acceleration:",
            trajectory_acceleration,
        )
        print(
            "Trajectory direction change:",
            trajectory_direction_change,
        )
        print("OSC sent.")

    def run(self):
        while True:
            started = time.monotonic()
            self.step()
            elapsed = time.monotonic() - started
            time.sleep(max(0.0, self.interval - elapsed))


if __name__ == "__main__":
    qmw = MLXQuantumEngine(
        audio_path=Path(
            "/Users/zlayton/QuantumSonification/materials/test.wav"
        ),
    )

    print("Starting QMW control server on 7402...")

    control_server = start_visual_control_server(
        qmw,
        host="127.0.0.1",
        port=7402,
    )

    qmw.run()
