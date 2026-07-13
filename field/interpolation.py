from dataclasses import replace


def lerp(a, b, t):
    return a + (b - a) * t


def interpolate_descriptor(a, b, t):
    """
    Interpolate between two QuantumMaterialDescriptors.
    Keeps symbolic fields from A, interpolates continuous fields.
    """
    return replace(
        a,
        bitstring=f"{a.bitstring}->{b.bitstring}",
        mode_family=round(lerp(a.mode_family, b.mode_family, t)),
        decay=lerp(a.decay, b.decay, t),
        brightness=lerp(a.brightness, b.brightness, t),
        damping=lerp(a.damping, b.damping, t),
        density=lerp(a.density, b.density, t),
        space=lerp(a.space, b.space, t),
        hamming_weight=round(lerp(a.hamming_weight, b.hamming_weight, t)),
        balance=lerp(a.balance, b.balance, t),
        transition_count=round(lerp(a.transition_count, b.transition_count, t)),
        transition_density=lerp(a.transition_density, b.transition_density, t),
    )


def interpolate_path(path, steps_between=8):
    """
    Expand a discrete descriptor path into a smooth descriptor trajectory.
    """
    if len(path) < 2:
        return path

    trajectory = []

    for a, b in zip(path[:-1], path[1:]):
        for i in range(steps_between):
            t = i / steps_between
            trajectory.append(interpolate_descriptor(a, b, t))

    trajectory.append(path[-1])
    return trajectory