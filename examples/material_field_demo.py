from pathlib import Path
import sys
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.qmw_backend import QuantumBackend, descriptor_from_bv
from field.material_field import MaterialField


def random_secret(n=8):
    return "".join(random.choice("01") for _ in range(n))


backend = QuantumBackend()
field = MaterialField()

for _ in range(12):
    secret = random_secret(8)
    measured, counts = backend.bernstein_vazirani(secret)
    descriptor = descriptor_from_bv(measured, counts)
    field.add(descriptor)

print()
print("MaterialField size:", field.size())

print()
print()
print("Material Path")
for d in field.path():
    print(d.bitstring, "brightness:", d.brightness, "density:", d.density, "damping:", d.damping)

target = field.trajectory()[0]
nearest = field.nearest_other(target)

print()
print("Target:", target.bitstring)
print("Nearest:", nearest.bitstring)
print()
print()

print("Centroid")

print(field.centroid())

print()

print("Spread")

print(field.spread())