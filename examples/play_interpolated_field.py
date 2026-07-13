from pathlib import Path
import sys
import random
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.qmw_backend import (
    QuantumBackend,
    descriptor_from_bv,
    OSCMaterialSender,
)

from field.material_field import MaterialField
from field.interpolation import interpolate_path


# ---------------------------------------------------------
# Generate random BV secrets
# ---------------------------------------------------------

def random_secret(n=8):
    return "".join(random.choice("01") for _ in range(n))


# ---------------------------------------------------------
# Build a MaterialField
# ---------------------------------------------------------

def build_field(size=8):

    backend = QuantumBackend()
    field = MaterialField()

    for _ in range(size):

        secret = random_secret()

        measured, counts = backend.bernstein_vazirani(secret)

        descriptor = descriptor_from_bv(
            measured,
            counts,
        )

        field.add(descriptor)

    return field


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

field = build_field(size=8)

path = field.path()

trajectory = interpolate_path(
    path,
    steps_between=8,
)

osc = OSCMaterialSender()

print()
print("--------------------------------------")
print(" Quantum Material Field")
print("--------------------------------------")
print("Nodes:", len(path))
print("Frames:", len(trajectory))
print()

frame = 0

while True:

    descriptor = trajectory[frame]

    # --------------------------------------
    # Material-derived timing
    # --------------------------------------

    duration = random.choice([0.5, 2.0, 6.0])

    print(
        f"Frame {frame:03d}",
        f"sleep={duration:.2f}",
        f"bits={descriptor.bitstring}",
        f"brightness={descriptor.brightness:.2f}",
        f"density={descriptor.density:.2f}",
        f"damping={descriptor.damping:.2f}",
        
    )


    osc.send_descriptor(descriptor)

    time.sleep(duration)

    frame += 1

    if frame >= len(trajectory):
        frame = 0