from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pythonosc.udp_client import SimpleUDPClient

from analysis.audio_descriptors import analyze_audio_material
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.mutator import HamiltonianMutator
from hamiltonian.circuit_from_hamiltonian import (
    circuit_from_hamiltonian,
    bloch_from_circuit,
)


audio = analyze_audio_material("test.wav")

h = HamiltonianState(x=0.0, y=0.0, z=1.0)
mutator = HamiltonianMutator(amount=0.5)
new_h = mutator.mutate_from_audio(h, audio)

qc = circuit_from_hamiltonian(new_h)
x, y, z = bloch_from_circuit(qc)

osc = SimpleUDPClient("127.0.0.1", 7400)

osc.send_message("/qmw/hamiltonian/x", new_h.x)
osc.send_message("/qmw/hamiltonian/y", new_h.y)
osc.send_message("/qmw/hamiltonian/z", new_h.z)

osc.send_message("/qmw/bloch/x", x)
osc.send_message("/qmw/bloch/y", y)
osc.send_message("/qmw/bloch/z", z)

print()
print("Audio:")
print(audio)

print()
print("Mutated Hamiltonian:")
print(new_h.as_pauli_terms())

print()
print("Bloch:")
print({"x": x, "y": y, "z": z})

print()
print("OSC sent.")