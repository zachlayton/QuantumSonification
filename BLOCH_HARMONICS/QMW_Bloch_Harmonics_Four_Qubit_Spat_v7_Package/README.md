# Four-Qubit Resonators + Spat5 Eight-Channel v7

Open `QMW_Bloch_Harmonics_Four_Qubit_Spat_v7.maxpat` with every file in this directory kept together.

For portable installation, copy this entire package folder—not only its `patchers` subfolder—into `Documents/Max 8/Packages/` or `Documents/Max 9/Packages/`, then restart Max. The universal Intel/Apple-Silicon `multiconvolve~` external and its redistribution license are bundled; install Spat5 separately.

## Architecture

- Four independent `qmw_qubit_genexpr_voice~` instances receive the reduced Bloch vectors for q0–q3.
- The embedded viewer shows q0–q3 simultaneously, with one Bloch sphere and one degree 1–3 real-spherical-harmonic bar graph per qubit.
- Each voice is an independent eight-mode Gen harmonic resonator derived from degree-one and degree-two Bloch functions. Its source is bundled as `qmw_qubit_resonator.gendsp` and loaded with standard `gen~`, avoiding a Max-level `gen.codebox~` dependency.
- `qmw_four_qubit_spat5_8ch~` sends the four mono voices plus the global/convolution stereo pair to six Spat5 sources and renders eight discrete `vbap2d` loudspeaker feeds.
- The original global 16-mode density-field resonator and convolution IR remain as a quieter shared layer. This retains information that cannot be recovered from the four reduced qubit states alone.
- Global purity, normalized entropy and normalized coherence are shared by all four local voices.

## Eight-channel output layout

The main patch sends discrete audio to `dac~ 1 2 3 4 5 6 7 8`. Spat5 assumes a regular horizontal ring:

| DAC output | Azimuth |
|---|---:|
| 1 | 0° |
| 2 | 45° |
| 3 | 90° |
| 4 | 135° |
| 5 | 180° |
| 6 | 225° |
| 7 | 270° |
| 8 | 315° |

The global/convolution left and right channels enter Spat5 as diffuse fixed sources at +45° and −45°. Eight independent output meters and a DSP toggle are provided in presentation mode. Select an audio interface exposing at least eight output channels in Max's Audio Status window.

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

The `spat5.oper` window opens automatically 750 ms after the abstraction loads. Click `/window/open` in the v7 presentation if it needs to be brought forward again.

## Requirements

- Max 8 or Max 9
- Spat5 (`spat5.oper` and `spat5.spat~`)
- `multiconvolve~`
- `dcblocker~`
- An audio interface with at least eight output channels
