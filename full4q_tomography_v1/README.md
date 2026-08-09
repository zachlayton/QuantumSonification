# QMW Full Four-Qubit Tomography OSC Instrument v1

This instrument treats complete four-qubit X/Y/Z tomography as a musical
score:

- `3^4 = 81` measurement settings, ordered `XXXX` through `ZZZZ`
- `2^4 = 16` measured basis states in every setting
- `4^4 - 1 = 255` non-identity Pauli coefficients
- correlation-weight shells containing `1, 12, 54, 108, 81` terms
- `81 × 256 = 20,736` sampled events at the workshop default

The first version is entirely local and does not submit an IBM job. Its OSC
contract is deliberately source-agnostic so a later IBM result loader can feed
the same Max patch.

## Start it

Keep the Spectral Synthesizer and the existing IBM bridge closed for the first
test. They use different ports, but testing this instrument alone makes the
signal path easy to see.

From the workshop directory:

```bash
cd /Users/zlayton/QuantumSonification/workshop_lightweight

/Users/zlayton/miniconda3/envs/music/bin/python \
  qmw_full4q_tomography_osc_v1.py \
  --save-dir /Users/zlayton/QuantumSonification/full4q_tomography_v1/runs
```

The terminal should report:

```text
Full4Q controls: udp://127.0.0.1:7425
Full4Q data out: udp://127.0.0.1:7426
Ready: preset=ghz transform=none shots=256 seed=23
```

Then open:

`max/QMW_Full4Q_Tomography_81_v1.maxpat`

Click one of the score messages at the top of the patch. `ghz none 256 23`
means:

1. use the GHZ score,
2. apply no final transform,
3. sample 256 shots for every setting,
4. use deterministic random seed 23.

The message can be edited by hand. Valid presets are `bell`, `ghz`, and
`weave`; valid transforms are `none`, `qft`, and `iqft`.

The result only becomes visible after all 81 settings and all 255 Pauli terms
arrive. This atomic commit prevents a partially received score from replacing
the previous complete one.

## What the patch shows

The heatmap is the complete 81-by-16 score. Rows follow lexicographic X/Y/Z
order. The number box chooses one row:

- row 0 is `XXXX`
- row 1 is `XXXY`
- row 2 is `XXXZ`
- row 80 is `ZZZZ`

The selected row's sixteen measured probabilities become sixteen harmonic
amplitudes in a 256-sample wavetable. The 255-slider field below it shows the
reconstructed Pauli coefficients. The five shell sliders summarize the RMS
strength of correlations of weights zero through four.

Each completed run is also saved as JSON when `--save-dir` is present. That
file contains the measured counts, ideal local probabilities, Pauli
coefficients, shell summaries, physical and linear density matrices, and
reconstruction metrics.

## Run without Max

To save and publish one score, then exit:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  qmw_full4q_tomography_osc_v1.py \
  --once \
  --preset ghz \
  --shots 256 \
  --output /Users/zlayton/QuantumSonification/full4q_tomography_v1/runs/ghz.json
```

See [OSC_CONTRACT.md](OSC_CONTRACT.md) for the exact messages.
