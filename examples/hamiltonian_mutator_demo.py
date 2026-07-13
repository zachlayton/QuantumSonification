from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.audio_descriptors import analyze_audio_material
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.mutator import HamiltonianMutator


audio = analyze_audio_material("test.wav")

h = HamiltonianState(x=0.0, y=0.0, z=1.0)

mutator = HamiltonianMutator(amount=0.5)

new_h = mutator.mutate_from_audio(h, audio)

print()
print("Audio:")
print(audio)

print()
print("Original Hamiltonian:")
print(h.as_pauli_terms())

print()
print("Mutated Hamiltonian:")
print(new_h.as_pauli_terms())
print()