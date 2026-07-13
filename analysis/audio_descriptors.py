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
        units="frames",
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    tempo = librosa.feature.tempo(
        onset_envelope=onset_env,
        sr=sr,
    )

    ioi = np.diff(onset_times)

    if len(ioi) > 0:
        mean_ioi = float(np.mean(ioi))
        std_ioi = float(np.std(ioi))
        groove_stability = 1.0 / (1.0 + std_ioi)
    else:
        mean_ioi = 0.0
        std_ioi = 0.0
        groove_stability = 0.0

    duration = max(len(ch) / sr, 1e-9)

    return {
        "centroid_mean": float(np.mean(centroid)),
        "rolloff_mean": float(np.mean(rolloff)),
        "flatness_mean": float(np.mean(flatness)),
        "rms_mean": float(np.mean(rms)),
        "zcr_mean": float(np.mean(zcr)),
        "onset_count": int(len(onset_times)),
        "onset_rate_per_sec": float(len(onset_times) / duration),
        "tempo_bpm": float(np.atleast_1d(tempo)[0]),
        "mean_ioi": mean_ioi,
        "ioi_std": std_ioi,
        "groove_stability": groove_stability,
        "onset_times": onset_times.tolist(),
    }


def descriptor_from_audio_array(y, sr):
    """
    Build the existing AudioMaterialDescriptor from an in-memory window.

    y must be either:
        mono:   shape (samples,)
        stereo: shape (channels, samples)
    """
    if y.ndim == 1:
        channels = [y]
    else:
        channels = list(y)

    channel_results = [analyze_channel(ch, sr) for ch in channels]

    brightness = sum(
        ch["centroid_mean"] for ch in channel_results
    ) / len(channel_results)

    rolloff = sum(
        ch["rolloff_mean"] for ch in channel_results
    ) / len(channel_results)

    flatness = sum(
        ch["flatness_mean"] for ch in channel_results
    ) / len(channel_results)

    loudness = sum(
        ch["rms_mean"] for ch in channel_results
    ) / len(channel_results)

    groove_stability = sum(
        ch["groove_stability"] for ch in channel_results
    ) / len(channel_results)

    onset_density = sum(
        ch["onset_rate_per_sec"] for ch in channel_results
    ) / len(channel_results)

    tempo_bpm = sum(
        ch["tempo_bpm"] for ch in channel_results
    ) / len(channel_results)

    stereo_brightness_imbalance = 0.0
    stereo_loudness_imbalance = 0.0

    if len(channel_results) == 2:
        left = channel_results[0]
        right = channel_results[1]

        brightness_denominator = max(
            left["centroid_mean"],
            right["centroid_mean"],
            1e-9,
        )

        loudness_denominator = max(
            left["rms_mean"],
            right["rms_mean"],
            1e-9,
        )

        stereo_brightness_imbalance = (
            left["centroid_mean"] - right["centroid_mean"]
        ) / brightness_denominator

        stereo_loudness_imbalance = (
            left["rms_mean"] - right["rms_mean"]
        ) / loudness_denominator

    return AudioMaterialDescriptor(
        sample_rate=sr,
        num_channels=len(channel_results),
        tempo_bpm=tempo_bpm,
        brightness=brightness,
        rolloff=rolloff,
        flatness=flatness,
        loudness=loudness,
        groove_stability=groove_stability,
        onset_density=onset_density,
        stereo_brightness_imbalance=stereo_brightness_imbalance,
        stereo_loudness_imbalance=stereo_loudness_imbalance,
    )


class AudioWindowAnalyzer:
    """
    Stateful looping audio-file analyzer.

    The playhead advances continuously. A descriptor is recalculated
    only every analysis_hop_seconds, so it is suitable for a fast engine loop.
    """

    def __init__(
        self,
        path,
        window_seconds=1.0,
        analysis_hop_seconds=0.10,
        playback_rate=1.0,
        loop=True,
    ):
        self.path = str(path)
        self.window_seconds = float(window_seconds)
        self.analysis_hop_seconds = float(analysis_hop_seconds)
        self.playback_rate = float(playback_rate)
        self.loop = bool(loop)

        self.y, self.sr = librosa.load(
            self.path,
            sr=None,
            mono=False,
        )

        if self.y.ndim == 1:
            self.y = self.y[np.newaxis, :]

        self.num_channels = self.y.shape[0]
        self.num_samples = self.y.shape[1]

        self.window_samples = max(
            2048,
            int(self.window_seconds * self.sr),
        )

        self.playhead_samples = 0.0
        self.analysis_elapsed = self.analysis_hop_seconds
        self.last_descriptor = None

        print(
            f"Loaded audio window source: {self.path} "
            f"({self.num_channels} ch, {self.sr} Hz, "
            f"{self.num_samples / self.sr:.2f} sec)"
        )

    def _get_window(self):
        start = int(self.playhead_samples) % self.num_samples
        end = start + self.window_samples

        if end <= self.num_samples:
            return self.y[:, start:end]

        if not self.loop:
            padded = np.zeros(
                (self.num_channels, self.window_samples),
                dtype=self.y.dtype,
            )

            available = self.y[:, start:self.num_samples]
            padded[:, :available.shape[1]] = available
            return padded

        first = self.y[:, start:self.num_samples]
        remaining = self.window_samples - first.shape[1]

        repetitions = int(np.ceil(remaining / self.num_samples))
        wrapped = np.tile(self.y, (1, repetitions + 1))
        second = wrapped[:, :remaining]

        return np.concatenate([first, second], axis=1)

    def next_window(self, dt):
        """
        Advance in track time by dt and return the most recently
        calculated descriptor.
        """
        dt = max(float(dt), 0.0)

        self.playhead_samples += (
            dt
            * self.playback_rate
            * self.sr
        )

        if self.loop:
            self.playhead_samples %= self.num_samples
        else:
            self.playhead_samples = min(
                self.playhead_samples,
                self.num_samples - 1,
            )

        self.analysis_elapsed += dt

        should_analyze = (
            self.last_descriptor is None
            or self.analysis_elapsed >= self.analysis_hop_seconds
        )

        if should_analyze:
            window = self._get_window()

            self.last_descriptor = descriptor_from_audio_array(
                window,
                self.sr,
            )

            self.analysis_elapsed = 0.0

        return self.last_descriptor


def analyze_audio_material(path):
    """
    Backward-compatible whole-file analysis.
    Useful for offline inspection, not the real-time engine.
    """
    y, sr = librosa.load(path, sr=None, mono=False)
    return descriptor_from_audio_array(y, sr)


def test():
    print("Audio Descriptor Module Loaded")