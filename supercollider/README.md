# QMW + SuperCollider

The project-wide Max-to-SuperCollider priorities, including geometry, modal,
wavetable, Bohmian, and excitation systems, are in
[`PORTING_PLAN.md`](PORTING_PLAN.md).

## Entangled history-clock click ensemble

Evaluate `qmw_entangled_history_clock_clicks_v1.scd` for a self-contained
sixteen-voice realization of the Ligeti-form history clock.  Voices map in
order from clock basis state `|0000>` to `|1111>`.  Each repeats `10101` on its
own fixed millisecond period, begins at a common release, and stops after 48
hits.  Use `~qmwHistoryClockStart.()` to replay and
`~qmwHistoryClockStop.()` to stop.

Stereo output is the default.  Before loading the file, select
`~qmwHistoryClockOutputMode = \discrete16` and configure sixteen server output
buses to send each basis-state voice to a separate audio output.

For the state-derived temporal version, evaluate
`qmw_entangled_history_temporal_mechanics_clicks_v1.scd`.  It embeds the exact
normalized reduced-clock coherence of the default Floquet history.  The two
eight-state parity coherence communities collectively deform the sixteen local
clock rates on the audio server.  `~qmwTemporalCoupling.(0.0)` produces the
matched dephased fixed-clock control; `~qmwTemporalCoupling.(0.24)` restores the
coherent deformation without restarting the synth.

`qmw_entangled_history_temporal_mechanics_clicks64_v1.scd` expands the same
construction to a six-qubit, 64-state clock coupled to the four-qubit system.
The pure history contains 1024 amplitudes and two exact 32-state coherence
communities.  SuperCollider evaluates the full within-community interaction
through two factorized complex mean fields.  Use
`~qmwTemporal64Start.(0.20, 2)` for coherent timing with two octave-displaced
layers per clock state and `~qmwTemporal64Start.(0.0, 1)` for the matched
single-layer dephased control.  Layer counts from one through four are gain-
normalized.  Even coherence states are biased left and odd states right while
each community retains internal spatial motion.

## Complete CPS / Wilson / Scala flow instrument

Evaluate `qmw_complete_cps_flow_v1.scd`, then run:

```sh
python examples/qmw_complete_cps_flow_v5.py --supercollider-port 57120
```

This client receives the same sixteen-state recursive instrument used by Max,
but the host appends exact ratio and frequency fields so SuperCollider does not
need MPE pitch bend. It includes a live Boolean/CPS field, Scala-ring geometry,
and distinct departure, arrival, phase-gate, and circuit-fingerprint timbres.
The exact `frequency_hz` is used directly; the accompanying ratio colors
timbre but is not applied to pitch a second time.

Alongside `/qmw/wilson/state16`, it accepts atomic paired four-qubit density
matrices from revisioned `/qmw/state/rho/{real,imag}` packets and unrevisioned
`/qmw/qac/rho/{real,imag}` packets. Each component contains 256 row-major
matrix coefficients. A revisioned pair commits only when both complete halves
carry the same revision.

Useful SuperCollider commands:

```supercollider
~qmwCPSTest.();
~qmwNext.();
~qmwStart.();
~qmwStop.();
~qmwSetArticulation.("arrival"); // or "dyad", "gesture"
~qmwTuning.("scala");
~qmwScalaLoad.("/absolute/path/to/scale.scl");
```

The recommended architecture is hybrid:

- Python remains the authoritative quantum layer. It evolves the complex
  16×16 density matrix, constructs the four-qubit Hamiltonian, applies circuit
  gates, computes partial traces/entropy, and extracts energy-gap ratios.
- SuperCollider becomes the real-time synthesis layer. It receives the stable
  `qmw-osc-v1` stream and renders the density field as a sixteen-mode spectral
  resonator.

This preserves the current numerical model while replacing the Max/Gen audio
renderer with native SuperCollider DSP.

## Run

1. Boot the SuperCollider server and evaluate
   `qmw_density_spectral_resonator.scd`.
2. Note the UDP port printed by the script (`NetAddr.langPort`). It is usually
   57120, but SuperCollider will choose another free port if that one is in
   use. From the repository root, start the canonical engine and mirror OSC to
   that port:

   ```sh
   python quantumsonification_engine.py --sc-osc-port 57120
   ```

   The conductor supports the same mirror:

   ```sh
   python quantumsonification_conductor.py --supercollider-port 57120
   ```

   Or run the current implementation directly:

   ```sh
   python quantum_population_osc_v9_resonator.py --sc-osc-port 57120
   ```

Replace `57120` in these commands if the script printed a different language
port. The primary OSC stream still goes to port 7400, so Max and SuperCollider can
render the same quantum state side by side. To use SuperCollider alone, set
`--osc-port 57120` and omit `--sc-osc-port`.

## Troubleshooting silence

After evaluating the script, run:

```supercollider
~qmwSCTest.();
```

This plays a two-second resonator tone without Python or OSC. If it is silent,
check the SuperCollider server's output device, mute state, and output channels.

Then run:

```supercollider
~qmwSCStatus.();
```

With the engine running, `frames` should increase and `last-frame-age` should be
near zero. The post window also announces the first received density frame.

Port 7402 is the Python engine's control input. Port 7400 is its primary Max
output, while `--sc-osc-port` mirrors that output to SuperCollider's language
port (normally 57120).

## Mapping

| QMW OSC signal | SuperCollider role |
| --- | --- |
| `/qmw/density_field/magnitude` | excitation of 16 modes |
| `/qmw/density_field/phase` | oscillator phase of 16 modes |
| `/qmw/density_field/speed` | mode-specific release time |
| `/qmw/density_field/harmonics` | Hamiltonian energy-gap frequency ratios |
| `/qmw/density_field/purity` | spectral selectivity |
| `/qmw/density_field/entropy` | weak-mode lift and brightness |
| `/qmw/density_field/coherence` | excitation attack time |

Each of the sixteen modes has an independent event envelope. A magnitude
change above `partialTriggerThreshold` triggers only that lane, latches its
current density-derived level, and runs its own `Decay2` attack/release pair.
The corresponding scanner speed controls both times, so fast lanes flash while
slow lanes ring. The density stream no longer acts as continuously smoothed
oscillator-bank amplitude.

## Living convolution engine

The resonator feeds a stereo source bus with an independent dry-output stage
and a double-buffered `PartConv` wet stage. New living spectral IRs are prepared
off the audible path. SuperCollider acknowledges `ready`, waits for the
publisher's crossfade authorization, fades between convolution engines, and
acknowledges `committed` only after the transition completes.

To run the existing publisher against SuperCollider:

```sh
python operators/living_spectral_geometry_osc_v1.py \
  /path/to/current_state.json \
  --out-port 57120 \
  --ack-port 7461 \
  --crossfade-ms 500
```

Use the UDP port printed by the SuperCollider script if it is not 57120.

An IR can also be loaded directly:

```supercollider
~qmwSCLoadIR.("/absolute/path/to/stereo_ir.wav", 500);
```

Set dry/wet balance without reloading the IR:

```supercollider
~qmwSCConvolutionMix.(0.72, 0.3, 150);
```

## Scope of the port

`qmw_density_spectral_resonator.scd` is a synthesis translation of the current
Gen~ resonator, not a reduced quantum simulation. A full SuperCollider-language
rewrite of the density engine is possible, but would require implementing and
validating complex matrix algebra, eigensolvers, Kraus channels, circuit gates,
and partial traces in sclang. That would be useful as an experimental alternate
backend, not as the first production replacement for NumPy's tested numerical
path.

## Eigenfield-directed Zeeman granulator

`qmw_eigenfield_zeeman_granulator_v1.scd` implements a serial architecture:

```text
rich source recording -> eigenfield grains -> paired Zeeman splitting
-> field-tuned Ringz bank -> output
```

It consumes the conductor's 4x4 grid and Zeeman state. Sixteen persistent
cells use local density and particle occupancy as grain probability, local
phase as pitch/direction, field strength as paired splitting, and cell
position as buffer/spatial position. The resonator bank receives only the
summed granular output; it does not run as a parallel sine oscillator layer.

Evaluate the file and test without Python using `~qmwZGTest.()`. For live data,
start the conductor with `--supercollider-port 57120`. Use `~qmwZGStatus.()` to
confirm frames and `~qmwZGStop.()` to free the instrument.

## Hyperbolic paraboloid pulse matrix

`qmw_hyperbolic_paraboloid_pulse_matrix_v1.scd` is a self-contained,
Python-free sonification of the `hyperbolic_paraboloid` surface added to
`operators/algebraic_surface_pipeline_v1.py` (`z = a * (x^2 - y^2)`). Rather
than solving eigenmodes, it plays the surface's own (x, y) sampling grid
directly as a time x pitch matrix: column (x) is time, scanning the saddle
across the piece; row (y) is pitch, one partial per row; height (z) sets
each pulse's amplitude, decay, and pan, so the saddle's positive lobe
(`x^2 > y^2`) and negative lobe (`y^2 > x^2`) read as loud/short/right-panned
versus quiet/long/left-panned pulses, and the near-diagonal ridge where
`z ~ 0` carves an audible silent "X" through the piece.

Evaluate the file, then:

```supercollider
~qmwHPPlay.();   // play live (boot a server first)
~qmwHPStop.();   // stop early
```

To bounce directly to a WAV without a live server or audio device:

```supercollider
~qmwHPRenderNRT.("/absolute/path/out.wav");   // 30-second stereo render
```

Both paths share one `~qmwHPPulses` geometry function, so the live and
offline renders are always the same piece.
