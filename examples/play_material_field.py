from pathlib import Path
import sys
import random
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.qmw_backend import QuantumBackend, descriptor_from_bv, OSCMaterialSender
from field.material_field import MaterialField


def random_secret(n=8):
    return "".join(random.choice("01") for _ in range(n))


def build_field(size=16):
    backend = QuantumBackend()
    field = MaterialField()

    for _ in range(size):
        secret = random_secret(8)
        measured, counts = backend.bernstein_vazirani(secret)
        descriptor = descriptor_from_bv(measured, counts)
        field.add(descriptor)

    return field


field = build_field(size=16)
path = field.path()

osc = OSCMaterialSender()

print()
print("Playing MaterialField path...")
print("Field size:", field.size())
print()

for i, descriptor in enumerate(path):
    print(
        i,
        descriptor.bitstring,
        "brightness:", descriptor.brightness,
        "density:", descriptor.density,
        "damping:", descriptor.damping,
        "space:", descriptor.space,
    )

    osc.send_descriptor(descriptor)

    time.sleep(1.0)

print()
print("Done.")