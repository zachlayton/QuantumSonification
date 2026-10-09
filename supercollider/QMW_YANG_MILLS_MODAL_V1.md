# QMW Yang–Mills modal resonator for SuperCollider

Python remains the authoritative classical SU(2) solver. SuperCollider receives
its atomic excitation frames and renders sixteen native noise-excited `Ringz`
modes, with a continuous spatial deformation control. This is a standalone
instrument using the same field stream as the Max host. It does not require
CNMAT, Max, MLX, Qiskit, or SuperCollider extensions.

## Run

Load the saved entry-point file in SuperCollider; adjust the repository path:

```supercollider
"~/QuantumSonification/supercollider/qmw_yang_mills_modal_v1.scd".standardizePath.load;
```

Loading by path lets it find the adjacent support and synth-definition files.
The script boots the default server if necessary and prints the actual language
UDP port. Master starts at zero. From the repository root, start Python with
that port (normally 57120):

```bash
python -m yang_mills_v1 --osc --port 57120 --steps 0
```

Then raise the master and try the controls:

```supercollider
~qmwYMMaster.(0.15);
~qmwYMDeformation.(0.5); // 0 = original coupling, 1 = full preset warp
~qmwYMCoupling.(0.7);   // independent field-excitation gain, 0..1
~qmwYMFrequency.(55);   // fundamental in Hz, 20..1000
~qmwYMDecay.(1.25);     // acoustic ring time in seconds, 0.02..12
~qmwYMGui.();           // deformation, coupling, master, mute and stream reset
~qmwYMStatus.();        // committed frames, age and field diagnostics
```

`~qmwYMTest.()` plays a two-second self-test at a modest fixed level without
Python. It bypasses the muted main voice so it can diagnose audio-device
configuration. `~qmwYMMaster.(0)` mutes the main instrument.
`~qmwYMStop.()` frees this receiver's OSC responders, stops its watchdog and
releases its voices. Other QMW SuperCollider instruments have separate names.

Before restarting the Python sender, run `~qmwYMReset.()` or click **Reset
stream**. A sender starts at revision zero; the receiver rejects revisions at
or below its last committed revision until reset.

## What Deformation Amount changes

The sixteen lanes have fixed positions at the centers of a periodic 4x4 grid.
For amount `d` in `[0,1]`, let `a = d/4`. The underlying spatial map is the
composition of two smooth shears on the unit torus:

```text
u' = (u + a sin(2 pi v)) mod 1
v' = (v + a sin(2 pi u')) mod 1
```

Each shear has determinant one and a smooth inverse. Their composition is
therefore an area-preserving diffeomorphism for every control value. Zero is
the identity, and one is the full quarter-period displacement preset. The
amount describes this particular flow; it is not a universal distance between
diffeomorphisms.

Each warped source position distributes its excitation power among four
neighboring destination lanes using periodic bilinear weights. For input
magnitudes `m_i` and a nonnegative weight matrix `W`:

```text
sum_j W[j,i] = 1
p'_j = sum_i W[j,i] m_i^2
m'_j = sqrt(p'_j)
speed'_j = sum_i W[j,i] m_i^2 speed_i / p'_j
```

Zero-power destinations have zero speed. Thus `sum_j (m'_j)^2 = sum_i m_i^2`:
the warp conserves total **excitation power before the resonators**. It does
not claim that perceived loudness or acoustic output power is constant; modes
have different frequencies and responses. Several sources can concentrate
into one destination, so a mapped amplitude may exceed one. The native synth
allows the full theoretical bound of four instead of clipping at one.

The continuous spatial flow is invertible; its finite-grid interpolation is
mixing and is not itself an invertible sixteen-lane operation. Returning the
control to zero recomputes the identity from the untouched source frame, so
repeated knob movements do not accumulate interpolation loss.

This deliberately changes the instrument's coupling to a fixed set of modal
lanes. It does not change the lattice metric, evolve gravity, retune modes,
or alter the Yang–Mills state. A coordinate relabeling of the physical model
alone would not produce a new gauge-invariant sound. Here the detector/coupling
map is the chosen artistic variable.

Python's bounded magnitudes already encode field energy through its calibrated
nonlinear adapter. Their squared values are excitation-power proxies, not raw
Hamiltonian energy. The source field's energy and Gauss diagnostics remain
unchanged by the SuperCollider deformation.

## Native modal rendering

Magnitude changes strike individual modes; source motion supplies continuous
noise excitation. The sixteen fixed frequencies are `fundamental * (1..16)`,
bounded below Nyquist. Controls are smoothed; acoustic decay is independent of
conservative field evolution. The signal is stereo distributed, DC filtered,
and limited. This is native `Ringz` synthesis, rather than a bit-identical
translation of the Max v4 filter equations.

SuperCollider coupling multiplies Python's adapter coupling. Deformation
changes the distribution; coupling changes total excitation strength.

## Atomic frames and lifecycle

The receiver uses the existing `/qmw/yang_mills/v1` protocol: matching begin,
magnitude, speed, diagnostics and end packets. It commits all controls from
one complete revision together. Missing, malformed, stale or reordered older
frames cannot refresh the watchdog or replace a newer pending frame.

After 750 ms without a complete frame, source magnitude and motion are cleared.
Changing deformation after that timeout cannot revive old energy. The acoustic
resonators can finish their decay; **Master** mutes output with a short ramp.
The Python sender also emits a zero-excitation frame on a clean stop.

## Validation

With a normal SuperCollider installation on PATH:

```bash
python -m unittest discover -s tests -p 'test_yang_mills_supercollider_v1.py' -v
```

These optional integration tests use actual `sclang` and `scsynth` and need no
audio hardware. They cover:

- Production receiver/GUI syntax and native DSP compilation.
- Identity, continuity, bounded motion, conservative power redistribution,
  incomplete/stale/invalid frame rejection, watchdog release and sender reset.
- Real Python OSC bundles decoded and committed by SuperCollider.
- Non-realtime stereo rendering with finite, nonzero output and silent
  coupling-zero, master-zero and vacuum controls.

The tests passed with SuperCollider 3.13.0 on Linux. Native rendering produced
a peak around 0.062 at the test gain; all three silent controls were exactly
zero. Listening, output-device configuration, GUI behavior and target-Mac
playback still need verification locally. No test render or runtime download
is committed to the repository.

For a nonstandard installation, the test harness accepts `QMW_SCLANG_PATH`,
`QMW_SCSYNTH_PATH`, optional `QMW_SCLANG_CONFIG`, and optional
`QMW_SC_PLUGINS_PATH`. Missing executables skip the corresponding native tests.
