import time
from pathlib import Path

from sklearn import metrics

from pythonosc.udp_client import SimpleUDPClient

from analysis.audio_descriptors import analyze_audio_material
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.mutator import HamiltonianMutator

from density.density_matrix_engine_4q import DensityMatrixEngine
from density.density_adapter import DensityAdapter

from feedback.feedback import FeedbackHistory
from feedback.event_detector import EventDetector
from feedback.quantum_memory import QuantumMemory

from field.quantum_field import QuantumField
from field.trajectory import QuantumTrajectory


class MLXQuantumEngine:
    def __init__(
        self,
        audio_path=None,
        osc_host="127.0.0.1",
        osc_port=7400,
        mutation_amount=0.5,
        interval=0.1,
    ):
        if audio_path is None:
            project_root = Path(__file__).resolve().parents[1]
            audio_path = project_root / "materials" / "test.wav"

        self.audio_path = str(Path(audio_path))
        self.osc = SimpleUDPClient(osc_host, osc_port)

        self.interval = interval
        self.hamiltonian = HamiltonianState(x=0.0, y=0.0, z=1.0)
        self.mutator = HamiltonianMutator(amount=mutation_amount)

        self.density_engine = DensityMatrixEngine()
        self.density_adapter = DensityAdapter(self.density_engine)

        self.history = FeedbackHistory()
        self.detector = EventDetector()

        self.quantum_memory = QuantumMemory(decay=0.7)
        self.quantum_field = QuantumField(self.quantum_memory)
        self.trajectory = QuantumTrajectory(self.quantum_field)

    def step(self):
        audio = analyze_audio_material(self.audio_path)

        self.hamiltonian = self.mutator.mutate_from_audio(
            self.hamiltonian,
            audio,
        )

        self.density_adapter.apply_hamiltonian_state(self.hamiltonian)

        rho = self.density_adapter.step(self.interval)
        density_metrics = self.density_adapter.metrics(rho)

        x = density_metrics.get("bloch_x", 0.0)
        y = density_metrics.get("bloch_y", 0.0)
        z = density_metrics.get("bloch_z", 0.0)

        bloch = {"x": x, "y": y, "z": z}

        self.quantum_memory.encode(
            rho=rho,
            hamiltonian=self.hamiltonian,
            audio_descriptor=audio,
        )

        trajectory_speed = self.trajectory.speed()
        trajectory_acceleration = self.trajectory.acceleration_magnitude()
        trajectory_direction_change = self.trajectory.direction_change()

        metrics = dict(density_metrics)
        metrics["trajectory_speed"] = trajectory_speed
        metrics["trajectory_acceleration"] = trajectory_acceleration
        metrics["trajectory_direction_change"] = trajectory_direction_change

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

        for event in event_result["events"]:
            self.osc.send_message("/qmw/event", event)

        self.osc.send_message("/qmw/hamiltonian/x", self.hamiltonian.x)
        self.osc.send_message("/qmw/hamiltonian/y", self.hamiltonian.y)
        self.osc.send_message("/qmw/hamiltonian/z", self.hamiltonian.z)

        self.osc.send_message("/qmw/bloch/x", x)
        self.osc.send_message("/qmw/bloch/y", y)
        self.osc.send_message("/qmw/bloch/z", z)

        self.osc.send_message("/qmw/memory/size", self.quantum_memory.size())
        self.osc.send_message("/qmw/memory/purity", self.quantum_memory.purity())
        self.osc.send_message("/qmw/memory/coherence", self.quantum_memory.coherence_l1())
        self.osc.send_message("/qmw/entanglement", metrics["entanglement"])
        self.osc.send_message("/qmw/entropy", metrics["entropy"])
        self.osc.send_message("/qmw/purity", metrics["purity"])
        self.osc.send_message("/qmw/coherence", metrics["coherence"])
        self.osc.send_message("/qmw/trajectory/speed", trajectory_speed)
        self.osc.send_message("/qmw/trajectory/acceleration", trajectory_acceleration)
        self.osc.send_message("/qmw/trajectory/direction_change", trajectory_direction_change)

        print()
        print("MLX Quantum Engine")
        print("------------------")
        print("Hamiltonian:", self.hamiltonian.as_pauli_terms())
        print("Bloch:", bloch)
        print("Density metrics:", density_metrics)
        print("Events:", event_result["events"])
        print("History size:", self.history.size())
        print("Quantum memory size:", self.quantum_memory.size())
        print("Memory purity:", self.quantum_memory.purity())
        print("Memory coherence:", self.quantum_memory.coherence_l1())
        print("Trajectory speed:", trajectory_speed)
        print("Trajectory acceleration:", trajectory_acceleration)
        print("Trajectory direction change:", trajectory_direction_change)
        print("OSC sent.")

    def run(self):
        while True:
            self.step()
            time.sleep(self.interval)