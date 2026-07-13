from pathlib import Path
import sys
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.qmw_backend import QuantumBackend, descriptor_from_bv
from analysis.audio_descriptors import analyze_audio_material
from descriptors.material_comparison import compare_quantum_audio


def random_secret(n=8):
    return "".join(random.choice("01") for _ in range(n))


audio_path = "test.wav"
tries = 32

audio = analyze_audio_material(audio_path)
backend = QuantumBackend()

best = None

for i in range(tries):
    secret = random_secret(8)
    measured, counts = backend.bernstein_vazirani(secret)
    quantum = descriptor_from_bv(measured, counts)
    comparison = compare_quantum_audio(quantum, audio)

    if best is None or comparison.overall > best["comparison"].overall:
        best = {
            "secret": secret,
            "quantum": quantum,
            "comparison": comparison,
        }

print()
print("Audio:")
print(audio)

print()
print("Best BV match:")
print("Secret:", best["secret"])
print(best["quantum"])

print()
print("Comparison:")
print(best["comparison"])
print()