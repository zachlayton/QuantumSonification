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
from quantum_oscilloscope.scope_engine import (
    QuantumOscilloscope,
    QuantumOscilloscopeConfig,
)
from quantum_oscilloscope.frame_builder import frame_from_engine_snapshot
from quantum_oscilloscope.osc_control import start_visual_control_server


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

        self.density_delta_rho_max = 0.0
        self.density_delta_rho_mean = 0.0

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
        self.pilot = BohmianPilot1D(
            n_modes=16,
            grid_size=512,
            mobility=0.28,
            damping=0.86,
            field_smoothing=0.14,
        )

    def set_visual_perturb(self, axis, value):
        self.visual_perturb[axis] = float(value)
        print(f"PERTURB RECEIVED: {axis} = {value}")

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

        trajectory_speed = self.trajectory.speed()

        trajectory_acceleration = (
            self.trajectory.acceleration_magnitude()
        )

        trajectory_direction_change = (
            self.trajectory.direction_change()
        )

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
            self.step()
            time.sleep(self.interval)


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
