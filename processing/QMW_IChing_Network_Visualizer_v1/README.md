# QMW I Ching Network Visualizer V1

Processing 4 visual mirror for committed I Ching density/Laplacian revisions.
The primary view is a complete 8 × 8 field of six-line hexagram glyphs: lower
trigram varies across columns and upper trigram across rows. Edge phase drives
each glyph's hue, halo, orbit, and subtle breathing without altering the oracle
reading. Moving lines pulse, and the H0 → H1 path is carried by flowing edge
particles.

## Requirements

- Processing 4
- `oscP5` library installed through Processing's Contribution Manager
- UDP ports `7404` (visual frames), `7405` (consultation requests), and `7406`
  (local/IBM comparison requests) available

## Run

Open `QMW_IChing_Network_Visualizer_v1.pde` and press Run. The sketch starts
with a deterministic seed-42 demo. Start the local oracle service from the
repository root with:

```bash
python qmw_iching_processing_visualizer_publisher_v1.py --serve
```

This casts an initial reading, then listens for consultation requests on `7405`.
Press `C` or click **CONSULT** to cast a fresh reading. Each completed reading is
mirrored as an identical atomic transaction to the density engine on `7403` and
the visualizer on `7404`. The exact frozen reading is also rendered and played
through the Mac's native `afplay`; a new consultation replaces the prior sound.
Use `--no-sound` for silence or `--no-engine` to omit the density engine.

Audio controls include `--sound-duration`, `--sound-modes`,
`--sound-base-frequency`, and `--sound-volume`.

For an auditable local-versus-quantum-route comparison, start the separate v1
comparison service with the repository's Qiskit environment:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python -u qmw_iching_ibm_compare_v1.py --serve
```

Press `I` or click **COMPARE**. In its default mode the service runs the exact
translated circuit through Aer and cannot submit an IBM job. Hardware mode is
separately and visibly gated by `--confirm-ibm`; `C` always remains a local
consultation. The comparison preserves local and external readings as distinct
routes and reports primary-distribution TVD, Hellinger fidelity, and moving-line
probability MAE.

Each completed comparison is also rendered as an audible A/B form: LOCAL first,
Aer or IBM second, followed by a short disagreement coda. Each route uses the
unchanged magnetic-Laplacian renderer used by `C`: the same 24-mode selection,
frequency normalization, damping, panning, and fades. Both routes share the
frozen local Laplacian; LOCAL excites it at the local H0 and Aer/IBM at its
measured H0. This is a controlled readout comparison, not hardware tomography:
four measurement circuits do not reconstruct a second complex phase geometry.
Moving lines and H1 remain visible comparison data but are not audible in the
existing `C` renderer. The WAV and a machine-readable mapping manifest are
archived beside the result. Use `--no-sound`, `--sound-route-duration`,
`--sound-base-frequency`, `--sound-modes`, or `--sound-volume` to adjust playback.

After intentionally choosing hardware mode, launch the service as follows:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python -u qmw_iching_ibm_compare_v1.py \
  --serve --confirm-ibm --backend ibm_fez --shots 4096
```

In that mode each press of `I` submits one Runtime Sampler job containing four
measurement circuits (four times the selected shots). Results and provenance
are archived under `output/iching_ibm_compare_v1/`. A new `C` cast clears the
visible comparison so an older hardware result cannot be mistaken for the new
reading.

The button reports `SERVICE OFFLINE` when nothing is listening on `7405` and
`FRAME INCOMPLETE` when a published UDP transaction did not pass the atomic
completeness check. Consultation frames are lightly paced to prevent burst loss.

The reading panel distinguishes the oracle's internal binary index from the
traditional King Wen number and common title. Read the gold Present hexagram,
then its moving lines from bottom upward, then the cyan Emerging hexagram. The
remaining phase field is relational context; it does not choose the cast.

## Controls

- Drag: pan the hexagram field
- Mouse wheel: zoom
- `C` or **CONSULT**: request a fresh random consultation
- `I` or **COMPARE**: compare the current frozen seed with Aer or an explicitly
  hardware-enabled IBM comparison service
- Space: pause/resume phase evolution
- `E`: toggle transition edges
- `R`: reset view
- `D`: restore deterministic demo
- `H`: toggle help

The scene changes only after a complete matching `/qmw/iching/network/end`
message. Incomplete frames never become visible.
