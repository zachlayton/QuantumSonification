from dataclasses import dataclass


@dataclass
class QuantumMaterialDescriptor:
    algorithm: str
    bitstring: str
    mode_family: int
    decay: float
    brightness: float
    damping: float
    density: float
    space: float

    hamming_weight: int
    balance: float
    transition_count: int
    transition_density: float

    counts: dict