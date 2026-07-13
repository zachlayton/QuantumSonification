from dataclasses import dataclass


@dataclass
class AudioMaterialDescriptor:

    sample_rate: int
    num_channels: int

    tempo_bpm: float

    brightness: float
    rolloff: float

    flatness: float

    loudness: float

    groove_stability: float

    onset_density: float

    stereo_brightness_imbalance: float

    stereo_loudness_imbalance: float
