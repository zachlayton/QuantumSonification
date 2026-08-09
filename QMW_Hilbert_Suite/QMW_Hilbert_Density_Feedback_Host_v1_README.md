# QMW Hilbert Density Feedback Host v1

Open `QMW_Hilbert_Density_Feedback_Host_v1.maxpat`. Do not open or manually
wire the inner feedback abstraction.

This host encapsulates:

- conductor reception on UDP port 7400;
- the sixteen-channel density-field Gen resonator;
- the complex 16×16 Hilbert density operator;
- causal, bounded feedback branches;
- synchronized full-matrix updates;
- stereo monitoring with sparse-state gain and monitor-only clipping;
- RAW SAFE, LOW FEEDBACK, and PANIC controls.

## Before opening

Keep every file from the host ZIP in one extracted folder. Do not leave the
files inside the ZIP. Close any other Max patch that binds UDP port 7400.

The host uses `OSC-route`, matching the existing QMW Max architecture. CNMAT
must therefore remain available on Max's search path.

## Startup

1. Start the conductor.
2. Open `QMW_Hilbert_Density_Feedback_Host_v1.maxpat`.
3. Confirm that the conductor indicator near `udpreceive 7400` flashes.
4. Click **RAW SAFE**.
5. Click the `ezdac~` speaker only after the indicator is flashing.
6. Establish the raw resonator sound before trying feedback.
7. Click **LOW FEEDBACK** once.

The low preset uses a gain of `0.03` in every branch. It sets tuned delays
before opening mode 2. It does not alter the gain ceiling.

If the sound becomes unexpected, click **PANIC + MUTE**. Panic closes the loop,
zeros feedback gains, clears delay and Hilbert histories, and turns off the
host's `ezdac~`.

## Matrix safety

The active density-field conductor sends sixteen-value magnitude, phase,
speed, and harmonic lists. Its optional `density_field/real` and
`density_field/imag` messages are also sixteen-value analytic samples; they
are deliberately not connected to the 16×16 matrix inlets.

The host retains the identity operator unless it receives a genuine 256-cell
matrix from one of these schemas:

```text
/qmw/state/rho/real  revision <256 floats>
/qmw/state/rho/imag  revision <256 floats>

/qmw/qac/rho/real  <256 floats>
/qmw/qac/rho/imag  <256 floats>
```

The `/state/rho` revision atom is removed before the matrix reaches the
operator. Real and imaginary parts are stored with `autocommit 0`, and a
commit occurs only after the imaginary list has arrived.

## Controls

- **RAW SAFE** — identity matrix, phase zero, feedback gain zero, 10 ms delay,
  exact RAW monitoring.
- **LOW FEEDBACK** — sixteen gains of 0.03, harmonic delay tuning from 55 Hz,
  then mode 2.
- **PANIC + MUTE** — closes and clears the loop and disables the DAC.
- **LOCAL TEST** — excites only basis lane 0; the running conductor may
  immediately replace this test state.
- **fundamental Hz** — sets the resonator carrier frequency. It defaults to
  55 Hz.

The host never enables DSP automatically.

## Monitor path

The 16-channel state remains intact through the feedback engine. Only its
first outlet is folded down for listening. Automatic 16-channel compensation
is deliberately disabled because it made sparse states nearly inaudible:

```text
16ch state -> mc.mixdown~ 2 -> 4x monitor gain -> monitor-only clip -> ezdac~
```

The clip and trim are outside the recursive loop and cannot change the complex
coupling calculation.
