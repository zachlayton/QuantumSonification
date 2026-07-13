from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))

from backend.qmw_backend import QuantumBackend, descriptor_from_bv, OSCMaterialSender

from operators.interpolate import Interpolate

from operators.diffuse import Diffuse

from operators.crystallize import Crystallize




backend = QuantumBackend()

a, counts_a = backend.bernstein_vazirani("10110110")
b, counts_b = backend.bernstein_vazirani("10100000")

desc_a = descriptor_from_bv(a, counts_a)
desc_b = descriptor_from_bv(b, counts_b)

print()
print("Original")
print(desc_a)

descriptor = desc_a

descriptor = Diffuse(0.20).apply(descriptor)

print()
print("After Diffuse")
print(descriptor)

descriptor = Interpolate(
    desc_b,
    amount=0.50
).apply(descriptor)

print()
print("After Interpolate")
print(descriptor)

descriptor = Crystallize(0.20).apply(descriptor)

print()
print("After Crystallize")
print(descriptor)


osc = OSCMaterialSender()
osc.send_descriptor(crystallized)

crystallized = Crystallize(amount=0.2).apply(diffused)

print()
print("Crystallized:")
print(crystallized)

osc = OSCMaterialSender()
osc.send_descriptor(crystallized)

print()
print("Sent crystallized descriptor to Max.")

