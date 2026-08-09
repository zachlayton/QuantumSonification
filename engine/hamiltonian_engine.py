import time
from pathlib import Path

from pythonosc.udp_client import SimpleUDPClient

from analysis.audio_descriptors import analyze_audio_material
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.mutator import HamiltonianMutator
from feedback.feedback import FeedbackHistory
from feedback.event_detector import EventDetector
from feedback.quantum_memory import QuantumMemory
from field.quantum_field import QuantumField
from field.trajectory import QuantumTrajectory
from hamiltonian.circuit_from_hamiltonian import (
    circuit_from_hamiltonian,
    bloch_from_circuit,
    density_matrix_from_circuit,
)


class HamiltonianEngine:
    def __init__(
        self,
        audio_path=None,
        osc_host="127.0.0.1",
        osc_port=7400,
        mutation_amount=0.5,
        interval=0.5,
    ):
        if audio_path is None:
            project_root = Path(__file__).resolve().parents[1]
            audio_path = project_root / "materials" / "test.wav"

        self.audio_path = str(Path(audio_path))
        self.osc = SimpleUDPClient(osc_host, osc_port)

        self.mutator = HamiltonianMutator(amount=mutation_amount)
        self.interval = interval

        self.hamiltonian = HamiltonianState(x=0.0, y=0.0, z=1.0)

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
        circuit = circuit_from_hamiltonian(self.hamiltonian)
        x, y, z = bloch_from_circuit(circuit)
        rho = density_matrix_from_circuit(circuit)
        bloch = {"x": x, "y": y, "z": z}

        self.quantum_memory.encode(
            rho=rho,
            hamiltonian=self.hamiltonian,
            audio_descriptor=audio,
        )
        trajectory = self.trajectory.kinematics()
        metrics = {
            "purity": self.quantum_memory.purity(rho),
            "coherence": self.quantum_memory.coherence_l1(rho),
            "trajectory_speed": trajectory["speed"],
            "trajectory_acceleration": trajectory["acceleration"],
            "trajectory_direction_change": trajectory["direction_change"],
        }
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
        self.osc.send_message(
            "/qmw/memory/coherence",
            self.quantum_memory.coherence_l1(),
        )
        self.osc.send_message("/qmw/trajectory/speed", trajectory["speed"])
        self.osc.send_message(
            "/qmw/trajectory/acceleration",
            trajectory["acceleration"],
        )
        self.osc.send_message(
            "/qmw/trajectory/direction_change",
            trajectory["direction_change"],
        )

        print()
        print("Hamiltonian:", self.hamiltonian.as_pauli_terms())
        print("Bloch:", bloch)
        print("Events:", event_result["events"])
        print("Memory snapshots:", self.quantum_memory.size())
        print("Memory purity:", self.quantum_memory.purity())
        print("Memory coherence:", self.quantum_memory.coherence_l1())
        print("Trajectory:", trajectory)
        print("OSC sent.")
        return metrics

    def run(self):
        while True:
            started = time.monotonic()
            self.step()
            elapsed = time.monotonic() - started
            time.sleep(max(0.0, self.interval - elapsed))
