# QMW Field-Directed Grainflow v1

This composite instrument keeps the Zeeman and GrainFlow source projects
independent. Zeeman line geometry selects and weights energy modes; the
statistical scheduler assigns fermionic, bosonic, or classical occupations;
GrainFlow renders occupied modes as grain events.

Generate and open:

```sh
python field_directed_grainflow_v1/build_qmw_field_directed_grainflow_v1.py
```

Then open `QMW_Field_Directed_Grainflow_v1.maxpat` in Max 9.

Presets map into six streams as normal triplet, sodium D1 quartet, or sodium
D2 sextet. Signed line factors control stream-rate displacement and transition
strengths control event probability and amplitude. Particle labels never
become grains; occupations determine which mode streams emit events.

## Eight-voice parameter-field prototype

Open `QMW_Field_Directed_Parameter_Buffers_v1.maxpat` for the first native
Grainflow parameter-buffer implementation. It uses the installed Grainflow
source `CP_Bubbling_Pasta_Sauce.wav` and writes three nine-sample buffers (eight
voice slots plus an interpolation endpoint):

```text
qmw_fdg_rates    signed field coordinate -> playback-rate ratio
qmw_fdg_delays   relational phase -> traversal offset in milliseconds
qmw_fdg_windows  voice geometry -> grain-window phasor offset
```

The quantum-weight amplitude field is sent separately as an eight-channel
signal to Grainflow's fourth inlet. This follows the object's native design;
there is no internal amplitude parameter buffer.

Lookup modes:

```text
0  ordinary scalar Grainflow controls
1  deterministic table slot i -> grain voice i
2  random sampling of the same tables
```

Entropy controls `rateRandom`, `delayRandom`, and `windowOffsetRandom`; it is
therefore independent of the lookup-mode choice. The patch accepts the current
scalar density-field OSC contract on UDP 7400:

```text
/qmw/density_field/magnitude
/qmw/density_field/phase
/qmw/density_field/purity
/qmw/density_field/entropy
/qmw/density_field/coherence
```

The four multisliders show the rate, delay, window-offset, and amplitude fields
that the eight voices receive. The TEST button refreshes the source duration
from the loaded buffer and rewrites all fields.
