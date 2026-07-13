import mlx.core as mx


class QuantumTrajectory:
    def __init__(self, quantum_field):
        self.field = quantum_field

    def vectors(self):
        return [
            self.field.vector_from_snapshot(s)
            for s in self.field.snapshots()
        ]

    def size(self):
        return len(self.vectors())

    def velocity(self):
        v = self.vectors()

        if len(v) < 2:
            return None

        return v[-1] - v[-2]

    def speed(self):
        vel = self.velocity()

        if vel is None:
            return 0.0

        return float(mx.linalg.norm(vel))

    def acceleration(self):
        v = self.vectors()

        if len(v) < 3:
            return None

        vel_1 = v[-1] - v[-2]
        vel_0 = v[-2] - v[-3]

        return vel_1 - vel_0

    def acceleration_magnitude(self):
        acc = self.acceleration()

        if acc is None:
            return 0.0

        return float(mx.linalg.norm(acc))

    def direction_change(self):
        v = self.vectors()

        if len(v) < 3:
            return 0.0

        vel_1 = v[-1] - v[-2]
        vel_0 = v[-2] - v[-3]

        n1 = mx.linalg.norm(vel_1)
        n0 = mx.linalg.norm(vel_0)

        if float(n1) == 0.0 or float(n0) == 0.0:
            return 0.0

        cosine = mx.sum(vel_1 * vel_0) / (n1 * n0)
        cosine = mx.clip(cosine, -1.0, 1.0)

        return float(mx.arccos(cosine))

    def is_stable(self, speed_threshold=0.02, acceleration_threshold=0.02):
        return (
            self.speed() < speed_threshold
            and self.acceleration_magnitude() < acceleration_threshold
        )

    def is_turning(self, angle_threshold=0.75):
        return self.direction_change() > angle_threshold