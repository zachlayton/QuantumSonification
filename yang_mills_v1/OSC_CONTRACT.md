# Yang–Mills modal excitation OSC v1

Default destination: `127.0.0.1:7416`. Prefix: `/qmw/yang_mills/v1`.

Each observation is a single immediate OSC bundle under 1400 bytes containing,
in order:

| Address suffix | Arguments |
| --- | --- |
| `/begin` | int32 revision, float32 model time, int32 lane count (16) |
| `/magnitude` | int32 revision, 16 float32 values in [0,1] |
| `/speed` | int32 revision, 16 float32 values in [0,1] |
| `/diagnostics` | int32 revision, float32 total energy, signed relative energy drift, maximum Gauss-vector norm, maximum unitarity entry error, maximum determinant error |
| `/end` | int32 revision |

Revision is nonnegative and increases for each published bundle. The Max
receiver stages a matching revision and commits only complete magnitude,
speed and diagnostics arrays at `/end`. An older begin cannot replace a newer
pending revision; revisions at or below the committed revision are rejected.
Invalid/missing vectors prevent the commit and do not refresh the watchdog.

After 750 ms without a complete frame, a host-driven 50 ms watchdog releases
all magnitude/speed parameters to zero. It does not cut off acoustic ringing.
`reset` clears revision tracking and releases excitation. Use it before
restarting a sender. `coupling 0..1` multiplies both vectors in the receiver.

The parameter outlet emits only `m0..m15` and `s0..s15`, preserving QMW's
existing modal DSP parameter names. A separate outlet displays magnitudes;
another exposes the five diagnostics. The diagnostic packet carries classical
field values; no density-matrix or quantum-information claims are attached.

This protocol is independent of `/qmw/density_field`. The source never sends
density-field tuning, phase or damping messages.
