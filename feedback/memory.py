import math
from hamiltonian.hamiltonian_state import HamiltonianState


class ExponentialMemory:
    def __init__(self, decay=0.6):
        self.decay = decay

    def weighted_hamiltonian(self, history):
        frames = history.frames

        if not frames:
            return HamiltonianState()

        x = 0.0
        y = 0.0
        z = 0.0
        total = 0.0

        reversed_frames = list(reversed(frames))

        for i, frame in enumerate(reversed_frames):
            weight = math.exp(-self.decay * i)

            h = frame.hamiltonian

            x += weight * h.x
            y += weight * h.y
            z += weight * h.z
            total += weight

        remembered = HamiltonianState(
            x=x / total,
            y=y / total,
            z=z / total,
        )

        return remembered.normalize()