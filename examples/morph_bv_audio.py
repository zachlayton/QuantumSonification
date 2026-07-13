from pathlib import Path
import sys
import random
import librosa
import soundfile as sf
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.qmw_backend import QuantumBackend, descriptor_from_bv
from analysis.audio_descriptors import analyze_audio_material
from descriptors.material_comparison import compare_quantum_audio


def random_secret(n=8):
    return "".join(random.choice("01") for _ in range(n))


def find_best_bv(audio, tries=32):
    backend = QuantumBackend()
    best = None

    for _ in range(tries):
        secret = random_secret(8)
        measured, counts = backend.bernstein_vazirani(secret)
        q = descriptor_from_bv(measured, counts)
        c = compare_quantum_audio(q, audio)

        if best is None or c.overall > best["comparison"].overall:
            best = {
                "secret": secret,
                "quantum": q,
                "comparison": c,
            }

    return best


def morph_audio(y, sr, quantum, audio, amount=0.5):
    """
    Simple descriptor-driven morph:
    - brightness target controls spectral tilt
    - density target controls transient emphasis
    - damping target controls smoothing
    """

    if y.ndim == 1:
        channels = [y]
    else:
        channels = list(y)

    processed = []

    brightness_target = quantum.brightness
    brightness_actual = min(1.0, audio.brightness / 8000.0)
    brightness_delta = brightness_target - brightness_actual

    density_target = quantum.density
    density_actual = min(1.0, audio.onset_density / 8.0)
    density_delta = density_target - density_actual

    damping_target = quantum.damping

    for ch in channels:
        stft = librosa.stft(ch)
        mag, phase = np.abs(stft), np.angle(stft)

        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        tilt = np.interp(freqs, [0, sr / 2], [1.0, 1.0 + brightness_delta])
        tilt = np.maximum(0.1, tilt)

        mag = mag * tilt[:, np.newaxis]

        onset_env = librosa.onset.onset_strength(y=ch, sr=sr)
        onset_env = onset_env / max(np.max(onset_env), 1e-9)
        onset_env = np.interp(
            np.linspace(0, len(onset_env) - 1, mag.shape[1]),
            np.arange(len(onset_env)),
            onset_env,
        )

        transient_boost = 1.0 + amount * 30.0 * density_delta * onset_env
        mag = mag * transient_boost[np.newaxis, :]

        smoothing = 1.0 - amount * damping_target * 0.25
        mag = smoothing * mag + (1.0 - smoothing) * np.mean(mag, axis=1, keepdims=True)

        new_stft = mag * np.exp(1j * phase)
        out = librosa.istft(new_stft, length=len(ch))

        processed.append(out)

    if y.ndim == 1:
        return processed[0]
    else:
        return np.vstack(processed)


def main():
    input_path = "test.wav"
    output_path = "morphed_bv.wav"

    audio = analyze_audio_material(input_path)
    best = find_best_bv(audio, tries=32)

    y, sr = librosa.load(input_path, sr=None, mono=False)

    morphed = morph_audio(
        y,
        sr,
        best["quantum"],
        audio,
        amount=1.5,
    )

    if morphed.ndim == 2:
        morphed_to_write = morphed.T
    else:
        morphed_to_write = morphed

    sf.write(output_path, morphed_to_write, sr)

    print()
    print("Audio:")
    print(audio)

    print()
    print("Best quantum target:")
    print("Secret:", best["secret"])
    print(best["quantum"])

    print()
    print("Comparison:")
    print(best["comparison"])

    print()
    print("Wrote:", output_path)
    print()


if __name__ == "__main__":
    main()