# Bloch spherical harmonics

`qmw.acoustics` maps reduced-qubit Bloch coordinates onto the real spherical
harmonics supplied by `python-acoustics`.

The coordinate conventions already match:

- Bloch `theta` is inclination from +Z in `[0, pi]`.
- Bloch `phi` is azimuth from +X toward +Y and is wrapped to `[0, 2*pi)`.
- Bloch radius is the local polarization/purity scale in `[0, 1]`.

The default radius weighting makes a pure state fully directional and contracts
the harmonic field to silence for a maximally mixed single-qubit state. Degree
one has a particularly transparent mapping:

```text
Y_1_1c = -sqrt(3 / 4pi) * x
Y_1_1s = -sqrt(3 / 4pi) * y
Y_1_0  =  sqrt(3 / 4pi) * z
```

## Use a Cartesian Bloch vector

```python
from qmw.acoustics import harmonics_from_bloch

frame = harmonics_from_bloch((0.2, -0.3, 0.4), degrees=(1, 2, 3))
print(frame.coordinates)
print(frame.values())
```

## Use the existing spin-engine OSC values

The spin engines already publish `/qubit/<i>/bloch/r`, `/theta`, and `/phi`.
Once those three values form a coherent frame:

```python
from qmw.acoustics import harmonics_from_spherical

frame = harmonics_from_spherical(r, theta, phi, degrees=(1, 2, 3))
channels = frame.values()
```

`channels` contains 15 controls for degrees 1-3. `c` and `s` suffixes are the
cosine and sine azimuthal quadratures. These can drive spatial gain, modal
excitation, reflection weights, or OSC control lanes without discarding quantum
phase orientation.

## Live OSC connection

`quantum_spin_polarization_engine_v3_measurement_basis.py` publishes degree 1
by default:

```text
/qubit/<i>/harmonic/Y_1_0
/qubit/<i>/harmonic/Y_1_1c
/qubit/<i>/harmonic/Y_1_1s
/global/harmonic/Y_1_0
/global/harmonic/Y_1_1c
/global/harmonic/Y_1_1s
```

Enable the complete degree 1-3 bank with:

```bash
python quantum_spin_polarization_engine_v3_measurement_basis.py \
  --harmonic-degrees 1,2,3
```

Use `--harmonic-degrees off` to disable the added messages. The optional
`--harmonic-radial-power` controls how strongly mixed-state radius contracts
the output; `1.0` is linear and `0.0` removes radius weighting.

## Spat5 and modal-reverb connection

The engine also emits a bounded acoustic control frame by default:

```text
/qmw/acoustics/spat/source/<i>/aed
/qmw/acoustics/spat/source/<i>/aperture
/qmw/acoustics/spat/source/<i>/spread
/qmw/acoustics/reverb/resonance
/qmw/acoustics/reverb/decay
/qmw/acoustics/reverb/damping
/qmw/acoustics/modal/tilt
/qmw/acoustics/modal/warp
/qmw/acoustics/modal/weights
```

The mapping is intentionally layered:

- Degree 1 supplies source azimuth and elevation.
- Bloch radius controls focus: pure states are close and narrow; mixed states
  become distant, wide, and diffuse.
- Degree 2 controls resonance, decay, damping tilt, and bounded delay warp.
- Degree 3 distributes excitation across eight FDN modes.

`max/control_room_modules/QMW_Bloch_Harmonic_Spat_Modal_v1.maxpat` converts
the source messages into native Spat5 `/source/<i>/aed`, `/aperture`, and
`/spread` messages. It sends them to its internal `spat5.oper`, its outlet, and
the named `qmw.spat.control` bus. Connect `r qmw.spat.control` to the control
inlet of the desired `spat5.spat~` renderer.

The adapter also contains a four-input `spat5.spat~` renderer with a two-channel
binaural output. Its four signal inlets correspond to qubits/sources 1–4. The
named control bus remains available when a loudspeaker, HOA, or WFS renderer is
preferred instead.

The adapter mirrors the reverb/modal family to `qmw.acoustic.modal.control` for
additional renderers. The realtime surface reverb listens to the OSC family
directly, so each Gen~ parameter receives one update per quantum frame. The FDN
smooths every added control and bounds each modulated feedback gain to the
renderer’s existing stability ceiling.

Use `--no-spatial-modal` to disable this control family while retaining the raw
harmonic outputs.
