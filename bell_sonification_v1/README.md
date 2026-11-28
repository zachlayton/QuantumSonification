# Bell-pair sonification v1

Hear entanglement one shot at a time. The circuit is the one on the lecture's
Bell-pair slide: H on qubit A (Hermes), CNOT A→B (Eros), measure both (the
Moirai). An optional rotation Ry(−θ) on B before measurement tilts B's
measurement axis; for the Bell state P(agree) = cos²(θ/2) and the
correlation E = cos θ, the curve on the "Entanglement and non-locality" slide.

## Three listening modes

| Mode | What you hear |
|---|---|
| `voices` | Each qubit is a voice (A left, B right); its bit picks the fundamental (220 Hz) or the fifth. Bell pair: the voices always move together, a unison of chance. Independent coins: they part, and the fifth sounds against the fundamental. |
| `agreement` | Each qubit alone is a noise click: pure chance on each side. A held tone sounds only on shots where the two agree. Bell pair: an unbroken tone. Independent: the tone breaks up. The pattern exists only in the comparison. |
| `sweep` | B's angle turns from 0° to 180°. Agreement falls along cos²(θ/2): unisons give way to fifths, always → half the time at 90° → never. |

## Sources

- `ideal`: exact probabilities sampled with numpy; fast, for live control.
- `aer`: the Qiskit circuit on the Aer simulator, shot by shot.
- `ibm`: the same circuits on IBM hardware via SamplerV2, archived to JSON with
  backend, job ID, date and shots so the source can be named from the stage.
  Hardware noise makes agreement slightly imperfect, which is audible.
- `replay`: render archived hardware shots.

The IBM path needs a saved `QiskitRuntimeService` account and has not been run
from this repo yet.

## Use

```bash
python3 -m bell_sonification_v1 demo out/ --source aer          # three WAV files
python3 -m bell_sonification_v1 stream --theta 0 --rate 8        # OSC to Max, port 7400
python3 -m bell_sonification_v1 ibm archive/ --steps 9 --shots 256
python3 -m bell_sonification_v1 replay archive/bell_<job>.json out/
python3 -m pytest bell_sonification_v1/test_bell.py
```

OSC (all under `/bell`): `/bell/provenance source backend job_id created`,
`/bell/shot index a b agree theta`, `/bell/correlation E` (running mean over
32 shots).

Requires `qiskit`, `qiskit-aer` (for `aer`), `qiskit-ibm-runtime` (for `ibm`)
and `python-osc` (for `stream`). The `ideal` source and the renders need only numpy.
