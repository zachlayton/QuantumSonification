import numpy as np

from core.transition import transition_spectrum


def normalize(x):
    peak = np.max(np.abs(x))

    if peak < 1e-12:
        return x

    return x / peak


def soft_fade_in(signal, samples=256):
    samples = min(samples, len(signal))
    signal[:samples] *= np.linspace(0.0, 1.0, samples)
    return signal


def make_transition_ir(
    sr=48000,
    ir_seconds=4.0,
    base_freq=40.0,

    field_z=(1.00, 1.17, 1.37, 1.61),
    coupling_xx=0.35,
    coupling_zz=0.18,
    coupling_dm=0.30,

    temperature="inf",
    t2=3.0,
    t2_freq_scaling=0.35,
):
    """
    Synthesizes an impulse response from the
    Hamiltonian transition spectrum.
    """

    t = np.linspace(
        0,
        ir_seconds,
        int(sr * ir_seconds),
        endpoint=False,
    )

    lines, energies = transition_spectrum(
        field_z=field_z,
        coupling_xx=coupling_xx,
        coupling_zz=coupling_zz,
        coupling_dm=coupling_dm,
        temperature=temperature,
    )

    ir = np.zeros_like(t)

    for line in lines:

        ratio = line["ratio"]

        freq = base_freq * ratio

        amp = np.sqrt(line["intensity"])

        phase = line["phase"]

        effective_t2 = (
            t2 /
            (1.0 + t2_freq_scaling * (ratio - 1.0))
        )

        effective_t2 = max(effective_t2, 1e-4)

        env = np.exp(-t / effective_t2)

        ir += (
            amp
            * env
            * np.cos(
                2.0 * np.pi * freq * t
                + phase
            )
        )

    ir = normalize(ir)

    ir = soft_fade_in(ir)

    return ir
