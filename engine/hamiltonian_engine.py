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

    # ------------------------------------------------------------
    # 1. Listen
    # ------------------------------------------------------------

        audio = analyze_audio_material(self.audio_path)

    # ------------------------------------------------------------
    # 2. Mutate Hamiltonian
    # ------------------------------------------------------------

    self.hamiltonian = self.mutator.mutate_from_audio(
        self.hamiltonian,
        audio,
    )

    # ------------------------------------------------------------
    # 3. Build quantum state
    # ------------------------------------------------------------

    qc = circuit_from_hamiltonian(self.hamiltonian)

    x, y, z = bloch_from_circuit(qc)

    rho = density_matrix_from_circuit(qc)

    bloch = {
        "x": x,
        "y": y,
        "z": z,
    }

    # ------------------------------------------------------------
    # 4. Encode experience
    # ------------------------------------------------------------

    self.quantum_memory.encode(
        rho=rho,
        hamiltonian=self.hamiltonian,
        audio_descriptor=audio,
    )

    # ------------------------------------------------------------
    # 5. Geometry
    # ------------------------------------------------------------

    trajectory_speed = self.trajectory.speed()

    trajectory_acceleration = (
        self.trajectory.acceleration_magnitude()
    )

    trajectory_direction_change = (
        self.trajectory.direction_change()
    )

    # ------------------------------------------------------------
    # 6. Recognize events
    # ------------------------------------------------------------

    metrics = {
        "purity": self.quantum_memory.purity(rho),
        "coherence": self.quantum_memory.coherence_l1(rho),
        "trajectory_speed": trajectory_speed,
        "trajectory_acceleration": trajectory_acceleration,
        "trajectory_direction_change": trajectory_direction_change,
    }

    event_result = self.detector.detect(
        metrics=metrics,
        audio_descriptor=audio,
    )

    self.quantum_memory.annotate_latest(
        events=event_result["events"],
        metrics=metrics,
    )

    # ------------------------------------------------------------
    # 7. History
    # ------------------------------------------------------------

    self.history.add(
        audio_descriptor=audio,
        hamiltonian=self.hamiltonian,
        bloch=bloch,
    )

    # ------------------------------------------------------------
    # 8. OSC
    # ------------------------------------------------------------

    for event in event_result["events"]:
        self.osc.send_message("/qmw/event", event)
        self.osc.send_message("/qmw/hamiltonian/x", self.hamiltonian.x)
        self.osc.send_message("/qmw/hamiltonian/y", self.hamiltonian.y)
        self.osc.send_message("/qmw/hamiltonian/z", self.hamiltonian.z)
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

    # ------------------------------------------------------------
    # 9. Console
    # ------------------------------------------------------------

    print()
    print("Hamiltonian:", self.hamiltonian.as_pauli_terms())
    print("Bloch:", bloch)
    print("Events:", event_result["events"])

    print()

    print("Memory")
    print("------")
    print("Snapshots:", self.quantum_memory.size())
    print("Purity:", self.quantum_memory.purity())
    print("Coherence:", self.quantum_memory.coherence_l1())

    print()

    print("Trajectory")
    print("----------")
    print("Speed:", trajectory_speed)
    print("Acceleration:", trajectory_acceleration)
    print("Direction change:", trajectory_direction_change)

    print()

    print("OSC sent.")

    def run(self):
        while True:
            self.step()
            time.sleep(self.interval)