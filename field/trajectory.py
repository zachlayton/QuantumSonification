import mlx.core as mx


class QuantumTrajectory:
    def __init__(self, quantum_field, window_size=8):
        self.field = quantum_field
        self.window_size = max(3, int(window_size))
        self._kinematics_cache_key = None
        self._kinematics_cache = None

    def vectors(self):
        return [
            self.field.vector_from_snapshot(s)
            for s in self.field.snapshots()
        ]

    def _recent_vectors(self, count=None):
        """Materialize one bounded window for smoothed local derivatives."""
        count = self.window_size if count is None else max(1, int(count))
        snapshots = self.field.snapshots()
        return [
            self.field.vector_from_snapshot(s)
            for s in snapshots[-count:]
        ]

    @staticmethod
    def _mean(vectors):
        if not vectors:
            return None
        total = vectors[0]
        for vector in vectors[1:]:
            total = total + vector
        return total / len(vectors)

    def _measure(self, vectors):
        """Return averaged velocity, acceleration, and direction change."""
        if len(vectors) < 2:
            return None, None, 0.0

        velocities = [
            vectors[index] - vectors[index - 1]
            for index in range(1, len(vectors))
        ]
        velocity = self._mean(velocities)

        acceleration = None
        if len(velocities) >= 2:
            accelerations = [
                velocities[index] - velocities[index - 1]
                for index in range(1, len(velocities))
            ]
            acceleration = self._mean(accelerations)

        # Compare averaged motion in the earlier and later portions of the
        # window. This rejects single-frame angular spikes while retaining
        # genuine turns over approximately 80 ms at a 100 Hz engine rate.
        direction_change = 0.0
        if len(velocities) >= 2:
            split = max(1, len(velocities) // 2)
            earlier = self._mean(velocities[:split])
            later = self._mean(velocities[split:])
            if later is not None:
                earlier_norm = mx.linalg.norm(earlier)
                later_norm = mx.linalg.norm(later)
                if float(earlier_norm) > 1e-12 and float(later_norm) > 1e-12:
                    cosine = mx.sum(earlier * later) / (
                        earlier_norm * later_norm
                    )
                    cosine = mx.clip(cosine, -1.0, 1.0)
                    direction_change = float(mx.arccos(cosine))

        return velocity, acceleration, direction_change

    def kinematics(self):
        """Calculate all live trajectory metrics from one eight-frame read."""
        snapshots = self.field.snapshots()
        cache_key = (
            len(snapshots),
            id(snapshots[-1]) if snapshots else None,
            self.window_size,
        )
        if cache_key == self._kinematics_cache_key:
            return dict(self._kinematics_cache)

        vectors = [
            self.field.vector_from_snapshot(snapshot)
            for snapshot in snapshots[-self.window_size:]
        ]
        velocity, acceleration, direction_change = self._measure(vectors)
        result = {
            "speed": 0.0 if velocity is None else float(mx.linalg.norm(velocity)),
            "acceleration": (
                0.0
                if acceleration is None
                else float(mx.linalg.norm(acceleration))
            ),
            "direction_change": direction_change,
        }
        self._kinematics_cache_key = cache_key
        self._kinematics_cache = result
        return dict(result)

    def size(self):
        return len(self.field.snapshots())

    def velocity(self):
        velocity, _, _ = self._measure(self._recent_vectors())
        return velocity

    def speed(self):
        return self.kinematics()["speed"]

    def acceleration(self):
        _, acceleration, _ = self._measure(self._recent_vectors())
        return acceleration

    def acceleration_magnitude(self):
        return self.kinematics()["acceleration"]

    def direction_change(self):
        return self.kinematics()["direction_change"]

    def is_stable(self, speed_threshold=0.02, acceleration_threshold=0.02):
        return (
            self.speed() < speed_threshold
            and self.acceleration_magnitude() < acceleration_threshold
        )

    def is_turning(self, angle_threshold=0.75):
        return self.direction_change() > angle_threshold
