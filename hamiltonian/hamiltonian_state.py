from dataclasses import dataclass


@dataclass
class HamiltonianState:
    x: float = 0.0
    y: float = 0.0
    z: float = 1.0

    def normalize(self):
        total = abs(self.x) + abs(self.y) + abs(self.z)

        if total == 0:
            self.z = 1.0
            return self

        self.x = self.x / total
        self.y = self.y / total
        self.z = self.z / total

        return self

    def as_pauli_terms(self):
        return {
            "X": self.x,
            "Y": self.y,
            "Z": self.z,
        }