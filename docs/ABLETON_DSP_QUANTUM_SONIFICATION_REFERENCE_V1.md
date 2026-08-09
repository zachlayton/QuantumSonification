# Ableton DSP for Quantum Sonification — Reference V1

Status: preferred Max DSP toolkit for new Quantum Sonification instruments.

Official documentation: <https://docs.cycling74.com/userguide/abl/>

Local package: `/Applications/Max 9.app/Contents/Resources/C74/packages/ableton-dsp`

## Project decision

Use Ableton DSP objects frequently when building real-time Max realizations of
the project's numerical and offline renderers. They provide production-grade
oscillators, modulators, filters, resonators, spectral processors, reverbs,
dynamics, and output protection without replacing the quantum-derived control
logic.

Keep the distinction between:

1. quantum representation (density matrix, Pauli coefficients, oracle phases),
2. geometric/acoustic model (surface modes, delay geometry, spatial coupling),
3. perceptual DSP projection (ring modulation, pitch shifting, spectral
   stretching, shimmer, spatial modulation), and
4. final dynamics/output safety.

Do not replace the 64-Pauli source with room modes. The current preferred chain
is:

```text
exact Pauli-64 source
  -> Tangle Cube modal/geometry reverb
  -> wet-only frequency transformation
  -> spatial motion
  -> limiter
```

## Important Ableton DSP behavior

- `abl.device.*~` objects wrap complete Ableton Live devices.
- `abl.dsp.*~` objects expose focused DSP components.
- Float attributes can be exposed as extra event-rate or signal-rate inlets
  using `@ins` at object construction.
- Event-rate float changes receive internal smoothing.
- Signal-rate inlet control bypasses that extra smoothing, so the patch must
  supply any desired slew explicitly.

This makes the library especially suitable for continuous quantum control
signals: oracle angle, resonance, coherence, purity, entropy, marked-state
probability, and geometry orientation can all become audio-rate modulators.

## Recommended object roles

### Core resonant body

`abl.dsp.modalresonator~`

- Physical modal filter bank.
- Plate or membrane models.
- Main controls: `frequency`, `decay`, `damping`, `ratio`, `resonator_type`.
- Good for a compact live proxy of surface-modal acoustics.
- Geometry orientation may drive `frequency` and `ratio`; decoherence may drive
  damping; purity/coherence may drive decay.

`abl.device.spectralresonator~`

- Preferred higher-level spectral alternative.
- Relevant controls include `frequency`, `harmonics`, `stretch`, `shift`,
  `voices`, `unison`, `decay`, `pitch_mod`, and `mod_rate`.
- Strong candidate for an audible 64-coefficient field whose spectrum must
  bend while retaining a coherent resonant identity.

### Frequency transformation

`abl.dsp.ringmod~`

- Stereo ring modulator.
- `frequency` produces input-minus-frequency and input-plus-frequency
  sidebands.
- `mix` controls audibility; `drive` and `enable_drive` add bounded distortion.
- Best used wet-only so the exact Pauli-64 source remains available as a
  reference.
- Suggested mapping: geometry frequency deviation -> ring frequency; aggregate
  resonance -> mix; entropy -> drive.

`abl.dsp.pitchshifter~`

- Stereo pitch shifter with `shift` in semitones, `mix`, `window`, and `wide`.
- Use when the whole reverberant spectrum should move together.
- Suggested mapping: cumulative Grover angle -> signed shift; coherence ->
  window stability; oracle eigenphase spread -> stereo `wide` behavior.

`abl.dsp.shimmer~`

- Reverb with pitch shifting inside its feedback path.
- Controls include `pitchshift` (-12 to +12 semitones), `shimmer`, `mod`,
  `diffusion`, `decay`, `damping`, and `size`.
- Use for recursive memory return: a recovered configuration re-enters the
  acoustic field at a transformed register.

### Moving reverberant geometry

`abl.dsp.tides~`

- Modulating algorithmic reverb.
- `rate` supports a very wide range; `phase` offsets left/right modulation;
  `waveform` morphs noise -> sine -> square; `tides` controls tail texture.
- Strongest ready-made match for an explicitly rotating/morphing chamber.
- Suggested mapping: Grover angular velocity -> rate; accumulated rotation ->
  phase; purity -> waveform regularity; decoherence -> noisy waveform/tides.

`abl.dsp.prism~`

- Stable algorithmic reverb for preserving spectral clarity.
- Use `size`, `decay`, `crossover`, `lowmult`, and `highmult` when modal motion
  should remain less chorused than Tides or Shimmer.

`abl.dsp.quartz~`

- Reverb with explicit `mod`, `diffusion`, `distance`, `size`, `decay`, and
  damping controls.
- Good intermediate option between static Prism and strongly animated Tides.

### Control generators

`abl.dsp.modulator~`

- Morphing modulation generator, 0.01–200 Hz.
- Supports shape, phase, fold, and two transformation stages.
- Transformations include quantization, sample-and-hold, slew up/down, gate,
  comparator, skew, triggered envelope, and attenuversion.
- Especially valuable for comparing continuous Grover rotation against stepped
  oracle events without rebuilding control utilities.

`abl.dsp.stereolfo~`, `abl.dsp.wander~`, `abl.dsp.envfollower~`

- Use for stereo orbit, stochastic decoherence drift, and source-dependent wet
  excitation respectively.

### Finishing

- `abl.device.utility~`: gain, width, channel management.
- `abl.device.compressor~` or `abl.dsp.compander~`: tail control.
- `abl.device.limiter~`: mandatory final protection for feedback, shimmer,
  resonant, or ring-modulated experiments.

## Grover / memory mapping hierarchy

Keep three rotation concepts separate:

1. **Grover macro-rotation**: product of oracle and diffusion reflections in
   the uniform-unmarked / uniform-marked plane. This should control the large
   orbit and arrival gesture.
2. **Memory-oracle eigenphases**: internal phase spectrum of the returning
   memory. These should control local torsion, mode-specific offsets, or
   sideband structure.
3. **Room rotation/deformation**: acoustic projection. The existing realtime
   surface reverb changes delay geometry with XYZ rotation; therefore its wet
   resonances move even though a mathematically rigid surface rotation would
   preserve Laplace–Beltrami eigenvalues.

For 3 qubits and 2 marked states:

```text
theta = asin(sqrt(2/8)) = 30 degrees
Grover step = 2 theta = 60 degrees
state angles = 30, 90, 150, 210, 270, 330, 390 degrees
```

The marked axis is reached at 90 degrees after the first ideal iteration.
Continuing makes overshoot and recurrence audible.

## Preferred Max prototype

```text
[Pauli-64 MC source]
        |
        +------------------------------ dry reference ------------------+
        |                                                               |
        v                                                               v
[abl.dsp.modalresonator~ or abl.device.spectralresonator~]       [matrix~/spat]
        |
        +--> [abl.dsp.ringmod~ @ins frequency mix]
        |         geometry deviation -> frequency
        |         resonance confidence -> mix
        |
        +--> [abl.dsp.pitchshifter~ @ins shift]
        |         Grover macro-angle -> semitone shift
        |
        +--> [abl.dsp.tides~ @ins rate phase tides]
                  angular velocity -> rate
                  cumulative angle -> stereo phase
                  decoherence -> texture
                           |
                    [abl.device.limiter~]
```

Start with parallel paths and independently adjustable mix controls. Do not
place ring modulation, pitch shifting, and shimmer serially at full strength;
that obscures which quantum quantity produced a perceptual change.

## Current offline counterpart

`feedback/render_memory_oracle_tanglecube_v1.py` implements:

- exact 64-Pauli excitation,
- actual 7,828-vertex / 24-mode Tangle Cube data,
- continuous spatial eigenfield coupling,
- the realtime surface reverb's eight-lane rotation-to-delay deformation,
- wet-only ring modulation derived from geometry frequency deviation,
- static/fixed-frequency control rendering, and
- numerical diagnostics for frequency ratios and modulation rates.

## Sources

- Ableton DSP overview: <https://docs.cycling74.com/userguide/abl/>
- Ring modulator: <https://docs.cycling74.com/reference/abl.dsp.ringmod~>
- Modal resonator: <https://docs.cycling74.com/reference/abl.dsp.modalresonator~>
- Pitch shifter: <https://docs.cycling74.com/reference/abl.dsp.pitchshifter~>
- Modulator: <https://docs.cycling74.com/reference/abl.dsp.modulator~>
- Prism: <https://docs.cycling74.com/reference/abl.dsp.prism~>
- Tides: <https://docs.cycling74.com/reference/abl.dsp.tides~>
- Shimmer: <https://docs.cycling74.com/reference/abl.dsp.shimmer~>
- Spectral Resonator: <https://docs.cycling74.com/reference/abl.device.spectralresonator~>
