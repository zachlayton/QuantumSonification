# PhysicsFrame → cable-net composition

The live four-qubit engine publishes StateBus ticks into its existing
QuantumFrameAccumulator. Export a completed block outside the audio/engine
callback; MusicXML generation is intentionally an offline operation:

```python
from procedural_notation_v1.physics_frame_score import write_physics_frame_score

if engine.physics_frame_ready:
    frame = engine.physics_frame()  # captured trajectory, normally 2048 samples
    write_physics_frame_score(frame, "performance.musicxml", snapshot_count=8)
```

This consumes the engine's actual density matrices. It never calls
`build_density_matrix_snapshots()`, advances the engine, changes its Hamiltonian,
or replaces the live state. The bridge accepts other frame lengths for short
captures/tests; rho must have shape (N,16,16). Mixed states need no statevector.

## Reproducible commands

From the repository root, install the notation requirements and run:

```sh
python -m pip install -r procedural_notation_v1/requirements.txt
python -m procedural_notation_v1.generate_physics_frame_score --output /tmp/demo.musicxml
python -m procedural_notation_v1.generate_physics_frame_score --indices 0 256 768 2047 --output /tmp/unequal.musicxml
```

These demonstrations use a labeled analytic 2048-sample unitary trajectory:
psi_k(t)=exp(-i E_k t)/4, E_k equally spaced from -1 to 1, hbar=1.
They are reproducible simulation fixtures, not recorded performance data.

To transfer a real captured frame:

```python
import numpy as np
frame = engine.physics_frame()
np.savez_compressed("capture.npz", t=frame.t, rho=frame.rho)
```

```sh
python -m procedural_notation_v1.generate_physics_frame_score --input capture.npz --snapshots 8 --output performance.musicxml
python -m pytest -q procedural_notation_v1/test_physics_frame_score.py
```

The NPZ interface requires only t/rho and disables pickle loading. Full
PhysicsFrame observables and diagnostics remain available on the original
object; this composition mapping uses rho rather than assigning additional
musical meanings to currents or Pauli channels.

## Two clocks

Selection is either an evenly distributed count in **sample-index space**
(including endpoints for counts >1), or explicit increasing sample indices.
Explicit indices override the count. Samples are copied, never interpolated or
repaired. Nonuniform timestamps remain nonuniform. The first selected sample is
score origin; its absolute physical timestamp is retained in the sidecar.

For selected time t_i, unquantized score onset is `(t_i - t_first) * scale`.
`scale` is `ticks_per_time_unit`, a compositional time expansion, not BPM or a
physical constant. The default gives the shortest selected interval
`16*slot_ticks + max(4, quantization_ticks)` ticks. A single snapshot starts at 0.
Nearest-grid rounding (half upward) then maps snapshot onsets to
`quantization_ticks`; error is at most half a grid step. Relative physical
intervals are preserved before rounding and remain recorded exactly afterward.
The default score uses eight ticks per quarter note and 4/4 measures.

Each snapshot launches the established 16-slot bra/ket traversal, with the
existing staggered voice entries and phase offsets. Thus snapshot onset
quantization does **not** quantize every note: the canon's local phase rhythm
remains intact. Slot size must be at least four ticks. If explicit time scaling
or quantization leaves less than a traversal between snapshots, export rejects
it instead of silently stretching intervals or overlapping notes in one part.
Increase scale or select fewer snapshots. Very large scales create long scores.

## What the music represents

The original 16×16 tensile cable-net geometry and 32-voice notation remain:
16 ket row traversals and 16 bra column traversals. Normalized matrix magnitude
gates off-diagonal events and shapes duration; conjugate phase controls local
rhythm and pitch selection; cable-net height influences register. The existing
hexatonic/pentatonic pitch collections are compositional choices, not quantum
energy eigenvalues or direct acoustic frequencies.

The original canon always retains diagonal events, even for zero populations;
this inherited convention is a structural score marker, not evidence of a
nonzero occupation. Density-matrix eigenvalues are not an audio spectrum.

`build_physics_frame_canon()` returns the normal graph with source sample index
and physical timestamp on every event. `write_physics_frame_score()` produces
MusicXML and an adjacent `.timing.json` recording selected indices, absolute
and elapsed physical times, score onsets, scale, quantization error, and mapping
parameters. This makes musical timing decisions inspectable without confusing
them with simulation time. It does not embed the entire trajectory in XML;
retain the original capture to regenerate its quantum data.

Tests validate data selection, no frame mutation, mixed states, invalid timing
and matrices, 32-part MusicXML structure, note attacks/pitches after music21
round-trip parsing, and complete measure durations. This is semantic MusicXML
validation, not external XSD validation or a visual engraving review.

music21 may report automatic-beaming warnings and MIDI-channel exhaustion for
32 parts. These do not prevent MusicXML export or timing round trips. Independent
32-part MIDI playback and polished engraving are not guaranteed by this bridge;
review the score in your notation application before performance.
