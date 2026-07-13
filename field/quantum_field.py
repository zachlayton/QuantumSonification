import mlx.core as mx


class QuantumField:
    def __init__(self, memory=None):
        self.memory = memory

    def snapshots(self):
        if self.memory is None:
            return []
        return self.memory.snapshots

    def vector_from_snapshot(self, snapshot):
        m = snapshot.metrics or {}

        purity = m.get("purity", 0.0)
        entropy = m.get("entropy", 0.0)
        coherence = m.get("coherence", 0.0)

        h = snapshot.hamiltonian
        hx = h.x if h is not None else 0.0
        hy = h.y if h is not None else 0.0
        hz = h.z if h is not None else 0.0

        return mx.array(
            [purity, entropy, coherence, hx, hy, hz],
            dtype=mx.float32,
        )

    def distance(self, a, b):
        va = self.vector_from_snapshot(a)
        vb = self.vector_from_snapshot(b)
        return float(mx.linalg.norm(va - vb))

    def nearest(self, target):
        candidates = [s for s in self.snapshots() if s is not target]
        if not candidates:
            return None
        return min(candidates, key=lambda s: self.distance(target, s))

    def centroid(self):
        snaps = self.snapshots()
        if not snaps:
            return None

        vectors = [self.vector_from_snapshot(s) for s in snaps]
        return mx.mean(vectors, axis=0)

    def spread(self):
        snaps = self.snapshots()
        if len(snaps) < 2:
            return 0.0

        c = self.centroid()
        distances = [
            float(mx.linalg.norm(self.vector_from_snapshot(s) - c))
            for s in snaps
        ]

        return float(mx.mean(distances))

    def highest_purity(self):
        snaps = self.snapshots()
        if not snaps:
            return None
        return max(snaps, key=lambda s: s.metrics.get("purity", 0.0))

    def highest_coherence(self):
        snaps = self.snapshots()
        if not snaps:
            return None
        return max(snaps, key=lambda s: s.metrics.get("coherence", 0.0))