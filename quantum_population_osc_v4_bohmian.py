import time
import threading
from pathlib import Path

import numpy as np

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
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


class MLXQuantumEngine:
    def __init__(
        self,
        audio_path=None,
        osc_host="127.0.0.1",
        osc_port=7400,
        visual_osc_port=7401,
        mutation_amount=0.5,
        interval=0.01,
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

        # Density-matrix point-cloud update timing.
        self.density_visual_elapsed = 0.0
        self.density_visual_interval = 0.10
        self.previous_visual_rho = None

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

        self.density_engine = DensityMatrixEngine()
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

    def send_density_matrix_to_processing(self, rho_np):
        """
        Send the 16 x 16 complex density matrix to Processing.

        Processing receives:
            /qmw/density/real/0 ... /qmw/density/real/15
            /qmw/density/imag/0 ... /qmw/density/imag/15
        """
        for row_index in range(16):
            row = rho_np[row_index]

            self.visual_osc.send_message(
                f"/qmw/density/real/{row_index}",
                [float(value.real) for value in row],
            )

            self.visual_osc.send_message(
                f"/qmw/density/imag/{row_index}",
                [float(value.imag) for value in row],
            )

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

            self.previous_visual_rho = rho_np.copy()

            self.send_density_matrix_to_processing(rho_np)

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

        # ------------------------------------------------------------
        # 11. Main OSC output to Max.
        # ------------------------------------------------------------
        for event in event_result["events"]:
            self.osc.send_message(
                "/qmw/event",
                event,
            )

        self.osc.send_message(
            "/qmw/hamiltonian/x",
            self.hamiltonian.x,
        )
        self.osc.send_message(
            "/qmw/hamiltonian/y",
            self.hamiltonian.y,
        )
        self.osc.send_message(
            "/qmw/hamiltonian/z",
            self.hamiltonian.z,
        )

        self.osc.send_message("/qmw/bloch/x", x)
        self.osc.send_message("/qmw/bloch/y", y)
        self.osc.send_message("/qmw/bloch/z", z)

        self.osc.send_message(
            "/qmw/memory/size",
            self.quantum_memory.size(),
        )
        self.osc.send_message(
            "/qmw/memory/purity",
            self.quantum_memory.purity(),
        )
        self.osc.send_message(
            "/qmw/memory/coherence",
            self.quantum_memory.coherence_l1(),
        )

        self.osc.send_message(
            "/qmw/entanglement",
            metrics.get("entanglement", 0.0),
        )
        self.osc.send_message(
            "/qmw/entropy",
            metrics.get("entropy", 0.0),
        )
        self.osc.send_message(
            "/qmw/purity",
            metrics.get("purity", 0.0),
        )
        self.osc.send_message(
            "/qmw/coherence",
            metrics.get("coherence", 0.0),
        )

        self.osc.send_message(
            "/qmw/trajectory/speed",
            trajectory_speed,
        )
        self.osc.send_message(
            "/qmw/trajectory/acceleration",
            trajectory_acceleration,
        )
        self.osc.send_message(
            "/qmw/trajectory/direction_change",
            trajectory_direction_change,
        )

        self.osc.send_message(
            "/qmw/bohm/x",
            bohm["x"],
        )
        self.osc.send_message(
            "/qmw/bohm/velocity",
            bohm["velocity"],
        )
        self.osc.send_message(
            "/qmw/bohm/speed",
            bohm["speed"],
        )
        self.osc.send_message(
            "/qmw/bohm/phase",
            bohm["phase"],
        )
        self.osc.send_message(
            "/qmw/bohm/density",
            bohm["density"],
        )
        self.osc.send_message(
            "/qmw/bohm/node_proximity",
            bohm["node_proximity"],
        )
        self.osc.send_message(
            "/qmw/bohm/curvature",
            bohm["curvature"],
        )
        self.osc.send_message(
            "/qmw/bohm/field_velocity",
            bohm["field_velocity"],
        )

        # ------------------------------------------------------------
        # 12. Explicit semantic OSC namespace.
        # ------------------------------------------------------------

        self.osc.send_message(
            "/qmw/hamiltonian/pauli_x",
            self.hamiltonian.x,
        )
        self.osc.send_message(
            "/qmw/hamiltonian/pauli_y",
            self.hamiltonian.y,
        )
        self.osc.send_message(
            "/qmw/hamiltonian/pauli_z",
            self.hamiltonian.z,
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

        single_entropy = metrics.get(
            "single_qubit_entropy",
            {},
        )

        self.osc.send_message(
            "/qmw/qubit/0/entropy",
            single_entropy.get(0, 0.0),
        )
        self.osc.send_message(
            "/qmw/qubit/1/entropy",
            single_entropy.get(1, 0.0),
        )
        self.osc.send_message(
            "/qmw/qubit/2/entropy",
            single_entropy.get(2, 0.0),
        )
        self.osc.send_message(
            "/qmw/qubit/3/entropy",
            single_entropy.get(3, 0.0),
        )
        self.osc.send_message(
            "/qmw/qubit/mean_entropy",
            metrics.get(
                "mean_single_entropy",
                0.0,
            ),
        )

        bipartition = metrics.get(
            "bipartition_entropy",
            {},
        )

        self.osc.send_message(
            "/qmw/entanglement/partition_01_vs_23",
            bipartition.get("01_vs_23", 0.0),
        )
        self.osc.send_message(
            "/qmw/entanglement/partition_02_vs_13",
            bipartition.get("02_vs_13", 0.0),
        )
        self.osc.send_message(
            "/qmw/entanglement/partition_03_vs_12",
            bipartition.get("03_vs_12", 0.0),
        )
        self.osc.send_message(
            "/qmw/entanglement/mean_bipartition",
            metrics.get("entanglement", 0.0),
        )

        self.osc.send_message(
            "/qmw/bohm/position",
            bohm["x"],
        )
        self.osc.send_message(
            "/qmw/bohm/local_density",
            bohm["density"],
        )
        self.osc.send_message(
            "/qmw/bohm/field_curvature",
            bohm["curvature"],
        )

        # ------------------------------------------------------------
        # 13. Processing visual OSC output.
        # ------------------------------------------------------------
        self.visual_osc.send_message(
            "/qmw/bloch/x",
            float(x),
        )
        self.visual_osc.send_message(
            "/qmw/bloch/y",
            float(y),
        )
        self.visual_osc.send_message(
            "/qmw/bloch/z",
            float(z),
        )

        self.visual_osc.send_message(
            "/qmw/bloch/perturbed_x",
            float(perturbed_bloch_x),
        )
        self.visual_osc.send_message(
            "/qmw/bloch/perturbed_y",
            float(perturbed_bloch_y),
        )
        self.visual_osc.send_message(
            "/qmw/bloch/perturbed_z",
            float(perturbed_bloch_z),
        )

        self.visual_osc.send_message(
            "/qmw/visual/field_strength",
            float(trajectory_speed),
        )
        self.visual_osc.send_message(
            "/qmw/visual/field_acceleration",
            float(trajectory_acceleration),
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


def start_visual_control_server(
    engine,
    host="127.0.0.1",
    port=7402,
):
    dispatcher = Dispatcher()

    dispatcher.map(
        "/qmw/control/perturb/x",
        lambda address, value: engine.set_visual_perturb(
            "x",
            value,
        ),
    )

    dispatcher.map(
        "/qmw/control/perturb/y",
        lambda address, value: engine.set_visual_perturb(
            "y",
            value,
        ),
    )

    dispatcher.map(
        "/qmw/control/perturb/z",
        lambda address, value: engine.set_visual_perturb(
            "z",
            value,
        ),
    )

    dispatcher.map(
        "/qmw/control/visual_gain",
        lambda address, value: engine.set_visual_perturb(
            "gain",
            value,
        ),
    )

    server = ThreadingOSCUDPServer(
        (host, port),
        dispatcher,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    print(
        f"Visual control OSC listening on {host}:{port}"
    )

    return server


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