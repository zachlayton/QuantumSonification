from dataclasses import dataclass, field
import math


@dataclass
class MaterialField:
    descriptors: list = field(default_factory=list)

    def add(self, descriptor):
        self.descriptors.append(descriptor)

    def size(self):
        return len(self.descriptors)

    def distance(self, a, b):
        return math.sqrt(
            (a.brightness - b.brightness) ** 2
            + (a.density - b.density) ** 2
            + (a.damping - b.damping) ** 2
            + (a.space - b.space) ** 2
            + (a.transition_density - b.transition_density) ** 2
        )

    def nearest(self, target):
        if not self.descriptors:
            return None

        return min(
            self.descriptors,
            key=lambda d: self.distance(d, target)
        )

    def nearest_other(self, target):
        candidates = [d for d in self.descriptors if d is not target]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda d: self.distance(d, target)
        )

    def trajectory(self):
        return self.descriptors

    def path(self):
        if len(self.descriptors) < 2:
            return self.descriptors.copy()

        remaining = self.descriptors.copy()
        path = [remaining.pop(0)]

        while remaining:
            current = path[-1]

            next_descriptor = min(
                remaining,
                key=lambda d: self.distance(current, d)
            )

            path.append(next_descriptor)
            remaining.remove(next_descriptor)

        return path

    def centroid(self):
        n = len(self.descriptors)

        if n == 0:
            return None

        return {
            "brightness": sum(d.brightness for d in self.descriptors) / n,
            "density": sum(d.density for d in self.descriptors) / n,
            "damping": sum(d.damping for d in self.descriptors) / n,
            "space": sum(d.space for d in self.descriptors) / n,
            "transition_density": (
                sum(d.transition_density for d in self.descriptors) / n
            ),
        }

    def distance_dict(self, d, c):
        return math.sqrt(
            (d.brightness - c["brightness"]) ** 2
            + (d.density - c["density"]) ** 2
            + (d.damping - c["damping"]) ** 2
            + (d.space - c["space"]) ** 2
            + (d.transition_density - c["transition_density"]) ** 2
        )

    def spread(self):
        c = self.centroid()

        if c is None:
            return 0.0

        return (
            sum(self.distance_dict(d, c) for d in self.descriptors)
            / len(self.descriptors)
        )