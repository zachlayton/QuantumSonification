# QMW probability-flow event field v1

A SuperCollider-only addition to **Scalar Field v4.2b**, built on
`preservation/code-only-2026-10-07`. It turns the evolving probability currents
of a four-site quantum model into overlapping harmonic wavelets. Timing,
strength, spectral interpolation and decay all have explicit model mappings.
No Python backend, random trigger generator or additional UGen is needed to play.

## Launch

1. Use this branch of the complete repository; the preserved v4.2 files are required.
2. Open `supercollider/StartEventField.scd` in SuperCollider and evaluate the whole file.
3. Start audio in the base v4.2b window, then press **Start field / reset** in the new panel.
4. The field reaches the existing event stereo output, hardware **1–2**. Use
   **Field output level** for its volume. Start with the base ring/fold/fuzz mixes
   at zero to hear the mapping, then turn them up to process it.
5. **Send to Clouds / VST** feeds the existing parallel returns. Raise the relevant
   return in the base mixer to hear it. Those plugins remain optional.

If v4.2b is already open, evaluate only `supercollider/EventFieldAddon.scd`.
The base's existing sources can also sound: use their own level controls to
isolate this field. Its level and send are separate from the seven stored
source-send slots. The original files and preset banks are unchanged.

## What drives the sound

The built-in theoretical source is the open four-qubit XX chain restricted to
one excitation: `|1000>, |0100>, |0010>, |0001>`. Its reduced Hamiltonian has
nearest-neighbour entries 1 and dimensionless time `tau = J t / hbar`.
The initial excitation is selectable; the default is `|1000>`.

The exact solution uses
`V[i,k] = sqrt(2/5) sin((i+1)(k+1) pi/5)` and
`E[k] = 2 cos((k+1) pi/5)`. These define the Hamiltonian, populations and
edge currents in `Model.scd`; the audio engine never changes the quantum state.

| Audible parameter | Model mapping |
| --- | --- |
| Event timing / density | Sum of incoming positive edge currents at each site. An event fires whenever its integrated flow reaches **Flow per event**. Lowering that threshold increases density. Zero flow produces no events. |
| Event strength | Square root of the site's population at emission; before FX, amplitude squared tracks population. |
| Base pitch | Site 1–4 maps to 110, 220, 330, 440 Hz. Each wavelet contains its first four integer harmonics. |
| Spectral endpoints | Four Hamiltonian-mode participation weights `abs(V[i,k])^2`, for the destination site and its largest incoming-flow neighbour at emission. |
| Spectral morph | Continuously updated `p_source / (p_destination + p_source)` blends those power weights; the square root gives oscillator amplitudes. A 10 ms smoothing stage avoids control steps. |
| Decay duration | Local turnover proxy `p / (incoming + outgoing)`, multiplied by seconds per model time and **Decay scale**, bounded to 0.03–3 seconds. It sets a 3 ms attack / curved release wavelet. |
| Spatial position | Fixed stereo position for each site, left to right. |

Harmonic numbers are **sonification labels**, not physical energy eigenvalues.
The four-mode weights are assigned to harmonic carriers; they are not a literal
measured frequency-response curve. Mirror-related sites have identical mode
weights, so some endpoint pairs do not change timbre. The population morph is
an audio interpolation, not a coherent quantum-state interpolation. The decay
proxy describes local redistribution; this closed model has no environmental
relaxation or measured lifetime. These events are flow thresholds, not detector
clicks or simulated quantum jumps.

The generator evaluates the exact state approximately every 5 ms, integrates
incoming flow with a trapezoid, solves for each threshold time inside the
interval, and timestamps the resulting synth events 120 ms ahead. The update
interval is numerical resolution, not an audible metronome. **Seconds / model
time unit** rescales the transport and decay; **Decay scale** changes overlap
without changing the event timing. The panel reports instantaneous flow-derived
rate, total events and a conservative voice count.

## Resonance and effects routing

Each event is a finite four-mode, decaying sinusoidal body. Live populations
reshape its spectral envelope throughout its life. Voices enter a private
stereo bus, then one field output mixer inside the base source group:

`wavelets -> ring modulation -> warp / wavefold -> fuzz -> limiter -> field level`

The processing equations and control-bus connections come from the v4.2b-loaded
v3 pulse voice. The field mixer then writes to the existing source bus and its
own send to the v4.2b Clouds/VST bus. The base dry/return graph stays in place.
Field level and Sound off act after fuzz, so even a nonzero fuzz bias cannot
defeat mute. Ring modulation, distortion and plugin returns can introduce
frequencies beyond the original 110 Hz carrier grid.

## Transport and limits

- **Stop field**, closing the panel, and Cmd-period stop new events and mute
  the field. Owned nodes/buses are released after pending timestamped bundles.
- Base **Sound off** pauses model time, clears fractional flow accumulation and
  mutes the field. Sound on resumes; Start field resets to the selected site.
- Changing Flow per event resets its accumulators to avoid an artificial burst.
- A base graph rebuild or a scheduling gap above 100 ms stops the field;
  press Start field again after audio is ready. Server quit invalidates old IDs.
- At most 96 wavelets are pending/active. Excess events are counted as **dropped**
  rather than queued or heard late. Extreme settings therefore lose events.
- This version runs its own XX theory source. It does not yet ingest an external
  measurement stream or the repository's separate PhysicsFrame publisher.
- Mac audio-device operation and optional MiClouds/VST return audio still need
  auditioning in the user's installation.

## Validation

Run from this directory with SuperCollider 3.13 or later:

```sh
sclang -D tests/CompileCheck.scd
sclang -D tests/ModelCheck.scd
python3 tests/run_lifecycle_check.py
sclang -D tests/RenderCheck.scd
python3 tests/validate_render.py /tmp/qmw_event_field_check.wav
```

`RenderCheck` uses the OS temporary directory by default; set `QMW_EVENT_RENDER`
to choose a WAV path. `QMW_SCSYNTH` and `QMW_SC_PLUGINS` optionally select an
unpacked server runtime. Linux headless runs may need `QT_QPA_PLATFORM=offscreen`.

ModelCheck verifies the actual SC implementation: normalization, current
continuity for all four initial sites, zero-flow silence, analytic constant/ramp
threshold timings, decay bounds, and onset convergence under time-step
refinement. LifecycleCheck exercises the actual language routines against an
OSC protocol stub: startup, event arguments, mute/pause, controls, voice cap,
stop/restart, host rebuild and server quit. It is not a real-time audio test.

RenderCheck uses **real scsynth DSP** at 48 kHz. It repeats the same six-second
field dry, with ring modulation, and with fuzz, with tail gaps between them.
Channels 1–2 are the field; 3–4 are its 0.4 post-FX send. The final section checks
Sound off and zero gain with biased fuzz. The validator checks finite output,
headroom, audible FX differences, exact send routing and mute silence.

See `validation.json` for the recorded results and `provenance.json` for the
preserved base revision and mapping settings.
