"""Stages 1-4 demo: a wavepacket meets a barrier; 2048-point field -> 16 regions.

    python examples/schrodinger_field_demo_v1.py OUTDIR

Writes a figure (field, regional energy, diagnostics) and a 16-voice audio preview.
The preview's mapping is a placeholder sonification policy (stage 7 will replace it):
region i -> partial i+1 of 110 Hz, amplitude ~ sqrt(regional energy), pan by region.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from qmw.physics import FieldEngine
from qmw.physics.schrodinger import SchrodingerConfig, SchrodingerModel
from qmw.physics.schrodinger import potentials as P
from qmw.physics.schrodinger import states as S
from qmw.projectors import RegionProjector

CONTROL_HZ = 500
DURATION = 20.0


def run():
    x = SchrodingerModel().x
    cfg = SchrodingerConfig(potential=P.barrier(x, 4.6, 0.0, 0.6, 0.05),
                            absorber=P.absorbing_layer(x, 8.0, 0.4),
                            initial_psi=S.gaussian_packet(x, -15.0, 2.0, 3.0))
    model = SchrodingerModel(cfg)
    engine = FieldEngine(model, 1 / CONTROL_HZ, RegionProjector(model.domain, 16, overlap=0.5))
    frames = [engine.frame] + [engine.step() for _ in range(int(DURATION * CONTROL_HZ))]
    return model, engine, frames


def render(frames, sr=48000):
    E = np.array([f.regions.energy for f in frames])                 # (T, 16)
    t_ctrl = np.arange(len(frames)) / CONTROL_HZ
    t = np.arange(int(DURATION * sr)) / sr
    amp = np.sqrt(np.maximum(E, 0) / E.max())
    out = np.zeros((len(t), 2))
    for i in range(16):
        a = np.interp(t, t_ctrl, amp[:, i])
        s = a * np.sin(2 * np.pi * 110 * (i + 1) * t) / (i + 1) ** 0.5
        pan = i / 15
        out[:, 0] += s * np.sqrt(1 - pan)
        out[:, 1] += s * np.sqrt(pan)
    return out / np.abs(out).max() * 0.9


def plot(model, frames, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = np.array([f.t for f in frames])
    rho = np.array([f.observables.probability_density for f in frames])
    E = np.array([f.regions.energy for f in frames])
    fig, ax = plt.subplots(3, 1, figsize=(10, 11), gridspec_kw=dict(height_ratios=[3, 2, 1.3]))
    ax[0].pcolormesh(model.x, t, np.sqrt(rho), shading="auto", cmap="magma")
    ax[0].axvline(0, color="c", lw=0.8)
    ax[0].set_ylabel("t"); ax[0].set_title("|psi(x,t)| on 2048 points: packet meets barrier (cyan), absorbers at edges")
    ax[1].pcolormesh(t, np.arange(16), E.T, shading="auto", cmap="viridis")
    ax[1].set_ylabel("region"); ax[1].set_title("Regional energy E_i(t), 16 regions")
    ax[2].semilogy(t[1:], [abs(f.diagnostics.norm_error) + 1e-17 for f in frames[1:]], label="norm error (N + absorbed - N0)")
    ax[2].semilogy(t[1:], [f.diagnostics.probability_continuity_error + 1e-17 for f in frames[1:]], label="continuity residual")
    ax[2].semilogy(t, [f.observables.norm for f in frames], label="norm N (physical, absorbed at edges)")
    ax[2].set_xlabel("t"); ax[2].legend(fontsize=8); ax[2].set_title("Numerical error vs physical dissipation")
    plt.tight_layout(); plt.savefig(path, dpi=110)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    model, engine, frames = run()
    plot(model, frames, os.path.join(out, "schrodinger_field_demo_v1.png"))
    try:
        import soundfile as sf
        sf.write(os.path.join(out, "schrodinger_field_demo_v1_regions16.wav"), render(frames), 48000)
    except ImportError:
        pass
    steps = [f.diagnostics.step_seconds for f in frames[1:]]
    print(f"{len(frames)-1} steps, median {1e3*np.median(steps):.2f} ms/step "
          f"(budget at {CONTROL_HZ} Hz: {1e3/CONTROL_HZ:.1f} ms)")
    print(f"final norm {frames[-1].observables.norm:.4f}, absorbed {frames[-1].conservation.absorbed_probability:.4f}, "
          f"norm error {frames[-1].diagnostics.norm_error:.1e}")
