# Pauli–Bloch World Clock / Spectral Microscope

This instrument solves a one-dimensional periodic lattice in an eleven-mode
reciprocal basis and sends fixed Bloch specimens to a native complex Gen~
oscillator bank.

For the original stereo comparison, open
`max/QMW_Bloch_Band_Spectral_Microscope_v1.maxpat`. Its left channel is
`Re(u_nk)` and its right channel is `Re(psi_nk)`.

## Open in Max

Keep every file in `max/` together and open:

`QMW_Pauli_Bloch_World_Clock_Spat_v1.maxpat`

Enable DSP, then run from the project directory:

```bash
python -m bloch_band_navigator_v1.osc_spectral_microscope
```

From any other directory, use the location-independent launcher:

```bash
/Users/zlayton/QuantumSonification/bloch_band_navigator_v1/StartBlochSpectralMicroscope.command
```

Arguments pass through normally, for example `--q 0.25` or `--once`.

The default specimens are `q = -0.50, -0.25, 0, +0.25, +0.50`, each held for
four seconds, repeating continuously until you press Control-C. Recall and hold
one specimen with `--q 0.25`, or use `--once` for one five-station traversal.

## Temporal-entanglement clock

For a continuous alternative to the five-station clock, stop the specimen
sender and launch:

```bash
/Users/zlayton/QuantumSonification/bloch_band_navigator_v1/StartBlochTemporalEntanglement.command
```

This couples three deterministic phases in the irrational ratio
`1 : 1/sqrt(2) : 1/phi`. The fastest phase drives Brillouin-zone motion; the
other two breathe the lattice depth and bend the transport phase. Because each
clock enters the phase of another, the audible spectrum does not settle into a
short repeating loop. The eigenvector gauge is parallel-transported between
frames to avoid arbitrary phase inversions.

Useful controls include `--period 7`, `--depth-span 2`, and `--coupling 0.72`.
This is a sonification of coupled temporal interference in one Bloch state,
not a claim of literal many-particle quantum entanglement.

## Emergent-event clock (recommended)

Open `max/QMW_Bloch_Emergent_Event_Clock_v1.maxpat`, enable DSP, and launch:

```bash
/Users/zlayton/QuantumSonification/bloch_band_navigator_v1/StartBlochQuenchEvents.command
```

This version contains no q sweep, lattice modulation, metronome, or continuous
state sonification. A spatially displaced, phase-curved wavepacket is quenched
into one fixed lattice Hamiltonian and evolves unitarily. Local maxima of
reciprocal-bond probability current are eligible for short transfer strikes;
a state-novelty gate suppresses crests whose reciprocal population repeats the
last sounded event. Exceptionally deep minima of return probability form an
independent layer of longer departure strikes. The event packet prepares an
eleven-mode Gen~ body from the simulated population, phase, and population
velocity, then changes `eventid` to strike it. Silence between events is an
intrinsic part of this instrument.

### Elements-inspired resonant body

For a richer physical-modeling body driven by the same intrinsic events, open
`max/QMW_Bloch_Elements_Event_Clock_v1.maxpat`. It adapts the MIT-licensed
Mutable Instruments Elements modal resonator architecture into sixteen MC Gen~
lanes: geometry stretches/compresses modal spacing, brightness controls
progressive high-mode loss, damping controls resonance memory, and pickup
position weights the radiation field. Elements' internal stereo-position LFO
is omitted, and its bow/blow/strike control system is replaced by the Bloch
event packet. Attribution and the license are in
`max/THIRD_PARTY_ELEMENTS_NOTICE.md`.

## Complex signal path

Gen~ outputs `Re(u)`, `Im(u)`, `Re(psi)`, and `Im(psi)`. Its temporal phase
turns in the negative direction required by `exp(-iEt/hbar)`. The patch offers
an immediate A/B toggle:

- **Off:** native complex quadratures calculated from the supplied `c_m`.
- **On:** an analytic pair reconstructed from `Re(psi)` by `hilbert~`; the
  imaginary outlet is conjugated to match the negative quantum-time rotation.

## Spat field

Five sources enter `spat5.spat~`:

| Source | Position |
| --- | --- |
| `+Re(psi)` | east |
| `-Re(psi)` | west |
| `+Im(psi)` | north |
| `-Im(psi)` | south |
| `0.32(Re+Im)` | orbiting phase hand |

The orbit travels clockwise. Its perceptible rate is a compressed projection
of energy relative to the bottom of band zero, and `q` offsets its azimuth.
Audio quadrature remains sample-accurate while the Spat position updates every
20 ms.

The output is third-order 3D HOA: sixteen ACN channels with SN3D normalization,
sent to DAC 1–16 for downstream room decoding.
