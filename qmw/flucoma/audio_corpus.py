from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from qmw.flucoma.corpus import DescriptorCorpus, SearchResult
from qmw.flucoma.quantum_descriptors import DescriptorVector


AUDIO_EXTENSIONS = {
    ".aif",
    ".aiff",
    ".flac",
    ".mp3",
    ".m4a",
    ".wav",
}

AUDIO_FEATURE_NAMES: tuple[str, ...] = (
    "pitch",
    "pitch_confidence",
    "loudness",
    "spectral_centroid",
    "spectral_spread",
    "spectral_skewness",
    "spectral_kurtosis",
    "spectral_rolloff",
    "spectral_flatness",
    "spectral_crest",
    "mfcc_0",
    "mfcc_1",
    "mfcc_2",
    "mfcc_3",
    "mfcc_4",
    "mfcc_5",
    "mfcc_6",
    "mfcc_7",
    "mfcc_8",
    "mfcc_9",
    "mfcc_10",
    "mfcc_11",
    "mfcc_12",
    "onset_density",
)


def audio_descriptor_vector(
    path: str | Path,
    *,
    sample_rate: int | None = None,
    max_duration: float = 20.0,
) -> DescriptorVector:
    """Analyze an audio file into a FluCoMa-like descriptor vector."""
    path = Path(path)
    y, sr = librosa.load(path, sr=sample_rate, mono=True, duration=max_duration)
    if y.size == 0:
        values = np.zeros(len(AUDIO_FEATURE_NAMES), dtype=float)
    else:
        values = _analyze_mono(y, sr)

    return DescriptorVector(
        identifier=path.stem,
        names=AUDIO_FEATURE_NAMES,
        values=values,
        metadata={
            "path": str(path),
            "sample_rate": int(sr),
            "analyzed_duration": float(len(y) / sr) if sr else 0.0,
            "kind": "audio",
        },
    )


def build_audio_corpus(
    folder: str | Path,
    *,
    sample_rate: int | None = None,
    max_items: int = 4096,
    max_duration: float = 20.0,
) -> DescriptorCorpus:
    """Analyze a folder of audio files into a searchable descriptor corpus."""
    corpus = DescriptorCorpus(max_items=max_items)
    for path in audio_files(folder):
        corpus.add(
            audio_descriptor_vector(
                path,
                sample_rate=sample_rate,
                max_duration=max_duration,
            )
        )
    return corpus


def audio_files(folder: str | Path) -> list[Path]:
    folder = Path(folder)
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )


def nearest_audio_material(
    query: DescriptorVector,
    corpus: DescriptorCorpus,
) -> SearchResult | None:
    return corpus.nearest(query, exclude_self=False)


def quantum_descriptor_to_audio_query(descriptor: DescriptorVector) -> DescriptorVector:
    """Map a quantum descriptor into the audio feature space used by this corpus."""
    features = descriptor.to_dict()
    stability = _clip01(features.get("mean_local_purity", 0.5))
    scatter = _clip01(features.get("global_entropy", 0.0))
    coherence = _clip01(features.get("coherence_l1", 0.0))
    spin_x = features.get("mean_spin_x", 0.0)
    spin_y = features.get("mean_spin_y", 0.0)
    spin_z = features.get("mean_spin_z", 0.0)
    spin_length = _clip01(features.get("mean_spin_length", 0.0))
    pair_abs = _clip01(features.get("pair_abs_mean", 0.0))
    speed = _clip01(features.get("trajectory_speed", 0.0) / 8.0)
    acceleration = _clip01(features.get("trajectory_acceleration", 0.0) / 12.0)
    measurement_entropy = _clip01(features.get("measurement_entropy", 0.0))

    mfcc_shape = [
        0.5 + 0.25 * spin_x,
        0.5 + 0.25 * spin_y,
        0.5 + 0.25 * spin_z,
        stability,
        scatter,
        coherence,
        spin_length,
        pair_abs,
        speed,
        acceleration,
        measurement_entropy,
        _clip01(features.get("population_spread", 0.0) * 8.0),
        _clip01(features.get("participation", 0.0)),
    ]

    values = np.asarray(
        [
            _clip01(0.5 + 0.35 * spin_z),
            stability,
            _clip01(0.25 + 0.65 * coherence + 0.25 * speed),
            _clip01(0.5 + 0.35 * spin_x + 0.25 * scatter),
            _clip01(0.25 + 0.55 * pair_abs + 0.25 * measurement_entropy),
            _clip01(0.5 + 0.30 * spin_y),
            _clip01(0.25 + 0.55 * scatter),
            _clip01(0.35 + 0.45 * spin_length),
            _clip01(0.15 + 0.75 * measurement_entropy),
            _clip01(0.20 + 0.65 * acceleration),
            *[_clip01(value) for value in mfcc_shape],
            _clip01(0.15 + 0.75 * speed + 0.35 * measurement_entropy),
        ],
        dtype=float,
    )

    return DescriptorVector(
        identifier=f"{descriptor.identifier}_audio_query",
        names=AUDIO_FEATURE_NAMES,
        values=values,
        metadata={
            "kind": "quantum_audio_query",
            "source_identifier": descriptor.identifier,
        },
    )


def _analyze_mono(y: np.ndarray, sr: int) -> np.ndarray:
    hop_length = 512
    spectrum = np.abs(librosa.stft(y, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=(spectrum.shape[0] - 1) * 2)
    energy = np.maximum(spectrum, 1e-12)
    weights = energy / np.sum(energy, axis=0, keepdims=True)

    centroid_frames = np.sum(weights * freqs[:, np.newaxis], axis=0)
    spread_frames = np.sqrt(
        np.sum(weights * (freqs[:, np.newaxis] - centroid_frames) ** 2, axis=0)
    )
    skew_frames = np.sum(
        weights
        * ((freqs[:, np.newaxis] - centroid_frames) / np.maximum(spread_frames, 1e-9)) ** 3,
        axis=0,
    )
    kurtosis_frames = np.sum(
        weights
        * ((freqs[:, np.newaxis] - centroid_frames) / np.maximum(spread_frames, 1e-9)) ** 4,
        axis=0,
    )

    rms = librosa.feature.rms(y=y, hop_length=hop_length)
    flatness = librosa.feature.spectral_flatness(S=spectrum)
    rolloff = librosa.feature.spectral_rolloff(S=spectrum, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        units="frames",
    )

    pitch, pitch_confidence = _pitch_summary(y, sr)
    duration = max(len(y) / sr, 1e-9)
    crest = float(np.max(np.abs(y)) / max(float(np.sqrt(np.mean(y * y))), 1e-9))

    values = [
        pitch,
        pitch_confidence,
        float(np.mean(rms)),
        _hz_unit(float(np.mean(centroid_frames))),
        _hz_unit(float(np.mean(spread_frames))),
        float(np.clip(np.mean(skew_frames) / 8.0, -1.0, 1.0)),
        float(np.clip(np.mean(kurtosis_frames) / 32.0, 0.0, 1.0)),
        _hz_unit(float(np.mean(rolloff))),
        float(np.clip(np.mean(flatness), 0.0, 1.0)),
        float(np.clip(crest / 24.0, 0.0, 1.0)),
    ]
    values.extend(float(np.clip((np.mean(row) + 100.0) / 200.0, 0.0, 1.0)) for row in mfcc)
    values.append(float(np.clip(len(onset_frames) / duration / 12.0, 0.0, 1.0)))
    return np.asarray(values, dtype=float)


def _pitch_summary(y: np.ndarray, sr: int) -> tuple[float, float]:
    max_pitch_samples = int(sr * 5.0)
    if y.size > max_pitch_samples:
        y = y[:max_pitch_samples]
    try:
        f0 = librosa.yin(
            y,
            fmin=librosa.note_to_hz("C1"),
            fmax=librosa.note_to_hz("C8"),
            frame_length=2048,
            hop_length=1024,
        )
    except Exception:
        return 0.0, 0.0

    f0 = np.asarray(f0, dtype=float)
    voiced = f0[np.isfinite(f0)]
    if voiced.size == 0:
        return 0.0, 0.0
    pitch = float(np.median(voiced))
    stability = 1.0 / (1.0 + float(np.std(np.log2(np.maximum(voiced, 1e-9)))))
    return _hz_unit(pitch), float(np.clip(stability, 0.0, 1.0))


def _hz_unit(value: float) -> float:
    return float(np.clip(np.log1p(max(value, 0.0)) / np.log1p(12000.0), 0.0, 1.0))


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))
