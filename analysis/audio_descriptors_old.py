import librosa
import numpy as np
from descriptors.audio_material_descriptor import AudioMaterialDescriptor


def analyze_channel(ch, sr):

    centroid = librosa.feature.spectral_centroid(y=ch, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=ch, sr=sr)
    flatness = librosa.feature.spectral_flatness(y=ch)
    rms = librosa.feature.rms(y=ch)
    zcr = librosa.feature.zero_crossing_rate(ch)

    onset_env = librosa.onset.onset_strength(y=ch, sr=sr)

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        units="frames"
    )

    onset_times = librosa.frames_to_time(
        onset_frames,
        sr=sr
    )

    tempo = librosa.feature.tempo(
        onset_envelope=onset_env,
        sr=sr
    )

    # ---------- Rhythm descriptors ----------

    ioi = np.diff(onset_times)

    if len(ioi) > 0:
        mean_ioi = float(np.mean(ioi))
        std_ioi = float(np.std(ioi))
        groove_stability = 1.0 / (1.0 + std_ioi)
    else:
        mean_ioi = 0.0
        std_ioi = 0.0
        groove_stability = 0.0

    return {

        "centroid_mean": float(np.mean(centroid)),
        "rolloff_mean": float(np.mean(rolloff)),
        "flatness_mean": float(np.mean(flatness)),
        "rms_mean": float(np.mean(rms)),
        "zcr_mean": float(np.mean(zcr)),

        "onset_count": int(len(onset_times)),
        "onset_rate_per_sec": float(
            len(onset_times) / (len(ch) / sr)
        ),

        "tempo_bpm": float(tempo[0]),

        "mean_ioi": mean_ioi,
        "ioi_std": std_ioi,
        "groove_stability": groove_stability,

        "onset_times": onset_times.tolist()
    }


def analyze_audio_material(path):
    results = analyze_audio_file(path)

    channels = results["channels"]

    brightness = sum(ch["centroid_mean"] for ch in channels) / len(channels)
    rolloff = sum(ch["rolloff_mean"] for ch in channels) / len(channels)
    flatness = sum(ch["flatness_mean"] for ch in channels) / len(channels)
    loudness = sum(ch["rms_mean"] for ch in channels) / len(channels)
    groove_stability = sum(ch["groove_stability"] for ch in channels) / len(channels)
    onset_density = sum(ch["onset_rate_per_sec"] for ch in channels) / len(channels)
    tempo_bpm = sum(ch["tempo_bpm"] for ch in channels) / len(channels)

    stereo = results.get("stereo", {})

    return AudioMaterialDescriptor(
        sample_rate=results["sample_rate"],
        num_channels=results["num_channels"],
        tempo_bpm=tempo_bpm,
        brightness=brightness,
        rolloff=rolloff,
        flatness=flatness,
        loudness=loudness,
        groove_stability=groove_stability,
        onset_density=onset_density,
        stereo_brightness_imbalance=stereo.get("brightness_imbalance", 0.0),
        stereo_loudness_imbalance=stereo.get("loudness_imbalance", 0.0),
    )
    if len(channel_results) == 2:
        left = channel_results[0]
        right = channel_results[1]

        results["stereo"] = {
            "centroid_difference": left["centroid_mean"] - right["centroid_mean"],
            "rolloff_difference": left["rolloff_mean"] - right["rolloff_mean"],
            "rms_difference": left["rms_mean"] - right["rms_mean"],
            "zcr_difference": left["zcr_mean"] - right["zcr_mean"],
            "brightness_imbalance": (
                left["centroid_mean"] - right["centroid_mean"]
            ) / max(left["centroid_mean"], right["centroid_mean"]),
            "loudness_imbalance": (
                left["rms_mean"] - right["rms_mean"]
            ) / max(left["rms_mean"], right["rms_mean"]),
            "onset_count_difference": (
                left["onset_count"] - right["onset_count"]
            ),
            "tempo_difference": (
                left["tempo_bpm"] - right["tempo_bpm"]
            ),
        }

    return results


def test():
    print("Audio Descriptor Module Loaded")