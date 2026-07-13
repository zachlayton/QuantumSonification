from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from feedback.quantum_memory import QuantumMemory


memory = QuantumMemory(decay=0.7)

rho_0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)

rho_plus = 0.5 * np.array([[1.0, 1.0], [1.0, 1.0]], dtype=complex)

rho_mixed = np.array([[0.5, 0.0], [0.0, 0.5]], dtype=complex)

memory.encode(rho_0, events=["initial_state"])
memory.encode(rho_plus, events=["coherence_birth"])
memory.encode(rho_mixed, events=["entropy_growth"])

print()
print("Memory size:", memory.size())

print()
print("Weighted density matrix:")
print(memory.weighted_density_matrix())

print()
print("Weighted purity:", memory.purity())
print("Weighted coherence:", memory.coherence_l1())
print("Weighted populations:", memory.populations())

print()
print("Highest purity snapshot:")
print(memory.highest_purity())

print()
print("Highest coherence snapshot:")
print(memory.highest_coherence())

print()
print("Snapshots with entropy_growth:")
print(memory.snapshots_with_event("entropy_growth"))
print()