from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.qmw_backend import QuantumBackend, descriptor_from_bv
from analysis.audio_descriptors import analyze_audio_material
from descriptors.material_comparison import compare_quantum_audio

secret = "10110110"
audio_path = "test.wav"

backend = QuantumBackend()

measured, counts = backend.bernstein_vazirani(secret)
quantum = descriptor_from_bv(measured, counts)

audio = analyze_audio_material(audio_path)

comparison = compare_quantum_audio(quantum, audio)

print()
print("Quantum:")
print(quantum)

print()
print("Audio:")
print(audio)

print()
print("Comparison:")
print(comparison)
print()