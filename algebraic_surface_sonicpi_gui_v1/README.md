# Algebraic Surface -> Sonic Pi (realtime GUI)

A small Tkinter window that lets you drag sliders over an algebraic surface
(currently `tanglecube` and `heart`, the same two surfaces
`operators/algebraic_surface_pipeline_v1.py` renders offline) and hear the
result live through [Sonic Pi](https://sonic-pi.net/), instead of rendering
an offline WAV impulse response.

It reuses the existing pipeline rather than reimplementing it:

- meshing: `operators.algebraic_surface_pipeline_v1.marching_tetrahedra`
- eigenmodes: `operators.spectral_geometry_v1.MeshSpectralGeometry`
  (cotangent Laplace-Beltrami spectrum)
- sound design: `surface_material_models_v1.create_surface_model`
  (frequency law, decay, mode weights)

Sonic Pi is the audio engine; this tool only computes and streams modal
data (`frequency, decay, amplitude, pan`) to it over OSC.

## Setup

1. Install Sonic Pi (https://sonic-pi.net/) and open it.
2. In Sonic Pi, go to **Preferences -> IO** and turn on **"Enable OSC
   Server"**. Note the OSC port shown there (default `4560`).
3. Paste `sonic_pi_receiver_v1.rb` into a Sonic Pi buffer and click **Run**.
   Leave it running — it is what turns incoming `/algebraic/modes` cues
   into sound. Re-running it after edits is safe; it picks up where it
   left off.
4. From the repository root, with `numpy` and `scipy` installed:

   ```
   python -m algebraic_surface_sonicpi_gui_v1.gui_v1
   ```

   (Run as a module, not as a bare script — see "Why `-m`" below.)

No extra Python packages are required for the GUI or the OSC client; both
are stdlib-only (`tkinter`, `socket`, `struct`). `python-osc` is only used,
optionally, by this package's own test suite to independently verify the
OSC wire format.

## Using it

- **Surface** / **Material model**: pick the algebraic surface and the
  physical model used to turn its geometry into decay/frequency behavior.
  Only field-free models are offered (`surface_laplacian`,
  `tensioned_membrane`, `elastic_shell`, `graph_diffusion`) —
  `bioelectric_surface` is excluded because it requires an external vertex
  voltage field this tool has no source for. `surface_laplacian` is the
  one tuned to land in an audible range by default; the others use their
  own physical parameters (surface tension, density, bending stiffness),
  which currently take the library's defaults rather than GUI sliders, and
  can produce very low (sub-audio) frequencies until those are dialed in
  in code.
- **Equation parameter (a)**: only affects `tanglecube`; `heart` has no
  free parameter and ignores it.
- **Mesh resolution / Sampling bound / Radius**: change the surface itself
  — moving these re-meshes and re-solves the eigenproblem (the slow step;
  see Performance below).
- **Modes solved**: how many eigenmodes are cached per mesh. Raising this
  forces a re-solve; **Active modes** (how many of the cached modes are
  actually sent to Sonic Pi) is a free truncation and does not.
- **Wave speed / T60 / Damping freq. tilt**: sound-design controls; these
  reuse the cached mesh and eigensolve, so changes here are near-instant.
- **Sonic Pi host / port / Reconnect**: where OSC messages are sent.
  Defaults to `127.0.0.1:4560`, matching Sonic Pi's default OSC-in port.
- **Recompute now**: force an immediate recompute/send outside the normal
  debounce.
- **Silence**: sends a `/algebraic/silence` cue. The receiver script kills
  every partial it has triggered so far, instead of waiting for their
  natural release tails.

Every control is debounced (~180 ms) and computed on a background thread,
so the window never freezes; only the most recently requested computation
is applied if you change something again before an older one finishes.

## Performance

Mesh + eigensolve time scales with resolution and requested mode count.
Measured on a modest laptop-class CPU:

| resolution | modes solved | vertices | time    |
| ---------- | ------------ | -------- | ------- |
| 20         | 24           | ~4,400   | ~1.0 s  |
| 24         | 24           | ~6,400   | ~1.5 s  |
| 24         | 48           | ~6,400   | ~1.7 s  |
| 28         | 32           | ~8,900   | ~2.1 s  |

The GUI's defaults (resolution 20, 24 modes solved) aim for a first sound
within about a second. Push resolution or "Modes solved" higher for a
smoother mesh and denser spectrum at the cost of responsiveness while
dragging those two controls specifically.

## Wire format

One UDP OSC message per update, address `/algebraic/modes`:

```
[mode_count, freq_0, decay_0, amp_0, pan_0, freq_1, decay_1, amp_1, pan_1, ...]
```

Sending the whole mode set as a single message keeps it atomic on the
receiving end — Sonic Pi's `sync` either gets a complete new chord or
keeps the previous one, never a half-updated one. `/algebraic/silence`
carries no arguments.

## Why `-m`

Running `python operators/algebraic_surface_pipeline_v1.py` directly (or
any script inside `operators/`) fails with an `ImportError` from deep
inside the standard library. `operators/operator.py` (an existing,
unrelated module) shadows Python's stdlib `operator` module once
`operators/` is inserted at the front of `sys.path`, which is what running
a bare script inside that directory does. Running as
`python -m operators.algebraic_surface_pipeline_v1` — or, for this
package, `python -m algebraic_surface_sonicpi_gui_v1.gui_v1` — from the
repository root avoids it, since the repository root (not `operators/`)
ends up on `sys.path` instead. This is a pre-existing repository quirk,
not something introduced by this package.
