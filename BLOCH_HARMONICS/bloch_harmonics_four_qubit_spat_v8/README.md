# Four-Qubit Resonators + Spat5 Third-Order HOA v8

Open `QMW_Bloch_Harmonics_Four_Qubit_Spat_v8.maxpat` with every file in this directory kept together.

## Architecture

- Four independent `qmw_qubit_genexpr_voice~` instances receive the reduced Bloch vectors for q0–q3.
- The embedded viewer shows q0–q3 simultaneously, with one Bloch sphere and one degree 1–3 real-spherical-harmonic bar graph per qubit.
- Each voice is an independent eight-mode Gen harmonic resonator derived from degree-one and degree-two Bloch functions. Its source is bundled as `qmw_qubit_resonator.gendsp` and loaded with standard `gen~`, avoiding a Max-level `gen.codebox~` dependency.
- `qmw_four_qubit_spat5_hoa3~` sends the four mono voices plus the global/convolution stereo pair to six Spat5 sources and encodes them as third-order 3D Ambisonics.
- The original global 16-mode density-field resonator and convolution IR remain as a quieter shared layer. This retains information that cannot be recovered from the four reduced qubit states alone.
- Global purity, normalized entropy and normalized coherence are shared by all four local voices.
- Four presentation controls independently set the q0–q3 fundamentals, defaulting to 55, 61.735, 73.416 and 82.407 Hz. Each control reaches only its matching local Gen resonator; the quieter global density-field layer follows q0.

## 16-channel HOA output layout

The main patch sends a third-order AmbiX-style HOA stream to `dac~ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16`. Components use ACN ordering and SN3D normalization:

| DAC | ACN | Component |
|---:|---:|---|
| 1 | 0 | W / Y(0,0) |
| 2 | 1 | Y / Y(1,-1) |
| 3 | 2 | Z / Y(1,0) |
| 4 | 3 | X / Y(1,1) |
| 5 | 4 | V / Y(2,-2) |
| 6 | 5 | T / Y(2,-1) |
| 7 | 6 | R / Y(2,0) |
| 8 | 7 | S / Y(2,1) |
| 9 | 8 | U / Y(2,2) |
| 10 | 9 | Q / Y(3,-3) |
| 11 | 10 | O / Y(3,-2) |
| 12 | 11 | M / Y(3,-1) |
| 13 | 12 | K / Y(3,0) |
| 14 | 13 | L / Y(3,1) |
| 15 | 14 | N / Y(3,2) |
| 16 | 15 | P / Y(3,3) |

These are encoded spherical-harmonic components, not individual loudspeaker feeds. CRAIVE's downstream renderer supplies the lower-, middle- and upper-ring loudspeaker geometry for its 360° room.

The global/convolution left and right channels enter Spat5 as diffuse fixed sources at +45° and −45°. Sixteen component meters and a DSP toggle are provided in presentation mode. Select the interface/ADAT device exposing all 16 outputs in Max's Audio Status window. Outputs 1–8 address the interface's first bank and outputs 9–16 address its ADAT expansion when that is how the driver presents the hardware.

## OSC inputs

The patch listens on UDP 7400 and requires the engine's full OSC profile:

```text
/qmw/qubit/0/bloch  x y z
/qmw/qubit/1/bloch  x y z
/qmw/qubit/2/bloch  x y z
/qmw/qubit/3/bloch  x y z
/qmw/density/purity
/qmw/density/coherence_l1
/qmw/density/von_neumann_entropy
/qmw/density/populations
```

The current conductor already launches the engine with `--osc-profile=full`.

The four qubit addresses are routed explicitly rather than by chained numeric path segments. Each resulting XYZ list drives its resonator, its Spat source and its matching viewer panel from the same branch.

The local resonators receive complete bus names (`qmw.q0.bloch` … `qmw.q3.bloch`) as arguments. Spat control is wired directly from the four explicit OSC-route outlets into four dedicated control inlets; it then reconstructs X/Y/Z with `pak f f f` and uses the same proven `pak → trigger → expr → pack → prepend → spat5.oper` chain as the working single-source v5 patch. The q0 viewer panel also returns its 20-value state list to the presentation flonums and harmonic bridge.

## Spatial mapping per qubit

- Bloch azimuth → source azimuth and yaw.
- Bloch elevation → source elevation.
- Bloch radius → distance from 1 to 2.5 metres.
- Bloch radius → aperture from 20° to 160°.

The `spat5.oper` window opens automatically 750 ms after the abstraction loads. Click `/window/open` in the v8 presentation if it needs to be brought forward again.

## Requirements

- Max 8 or Max 9
- Spat5 (`spat5.oper` and `spat5.spat~`)
- `multiconvolve~`
- `dcblocker~`
- An audio interface plus ADAT expansion exposing at least 16 outputs
- A downstream third-order decoder configured for ACN channel order and SN3D normalization
