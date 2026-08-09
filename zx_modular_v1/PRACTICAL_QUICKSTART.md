# PennyLane → ZX → Max + VCV Rack: practical quickstart

This is the smallest useful hybrid instrument:

1. PennyLane evolves a two-qubit circuit.
2. PennyLane converts that circuit to a ZX graph and the bridge verifies its
   matrix semantics through PyZX.
3. The same six normalized state descriptors are streamed over OSC.
4. Max receives them as named patch points; VCV Rack receives them through
   OSCelot.

The first version is deliberately control-rate. It lets us learn what the
quantum/ZX data should *do musically* before building native, faithful
four-channel ZX signal modules.

## 1. Verify the Python environment

From Terminal:

```sh
cd /Users/zlayton/QuantumSonification
conda activate music
python -c "import pennylane, pyzx, zx_modular_v1; print(pennylane.__version__, pyzx.__version__)"
```

## 2. Run one dry frame

```sh
python -m zx_modular_v1.examples.pennylane_vcv_live_demo
```

Look for `"zx_semantics_verified": true`. Nothing is transmitted unless
`--send` or `--send-max` is present.

## 3. Open the Max monitor

Open:

`/Users/zlayton/QuantumSonification/max/QMW_ZX_PennyLane_Monitor_v1.maxpat`

The patch listens on UDP port `7496`. Start a finite sweep:

```sh
python -m zx_modular_v1.examples.pennylane_vcv_live_demo \
  --send-max --sweep --frames 600 --interval 0.05
```

The six bars should move. Their values are also available anywhere in Max as
`receive qmw.zx.1` through `receive qmw.zx.6`.

## 4. Make the first Rack voice

In VCV Rack:

1. Add `OSCelot` and place an `OSCelotExpander` immediately to its right.
2. Set OSCelot's receive port to `7000` and start its receiver.
3. From the expander context menu, select a unipolar `0–10 V` output range.
4. Build a familiar voice: oscillator → filter → VCA → Audio.
5. Patch expander outputs through attenuators before sensitive CV inputs.

A useful first mapping is:

| ID | Quantum/ZX descriptor | First musical destination |
|---:|---|---|
| 1 | ZX phase in turns | oscillator shape or phase |
| 2 | qubit-0 Z expectation | filter cutoff |
| 3 | population entropy | reverb mix or grain density |
| 4 | basis coherence | FM index or wavefold amount |
| 5 | circuit-parameter gradient | stereo motion or feedback |
| 6 | dominant-state probability | VCA level |

To teach or troubleshoot one OSCelot control without the other IDs moving,
stream only that ID:

```sh
python -m zx_modular_v1.examples.pennylane_vcv_live_demo \
  --send --only-control 1 --sweep --frames 200
```

Repeat with IDs `2` through `6` if you are using OSCelot's parameter mapping.
When using the expander's numbered CV outputs, the IDs already provide the
stable channel assignment.

## 5. Run Max and Rack together

With both applications ready:

```sh
python -m zx_modular_v1.examples.pennylane_vcv_live_demo \
  --send --send-max --sweep --frames 0 --interval 0.05
```

`--frames 0` means continue until Control-C. Both hosts now see the same state
at the same instant:

- Max is the editable patching, analysis, and display layer.
- VCV Rack is the tactile modular performance layer.
- Python/PennyLane/PyZX is the canonical semantic layer.

To include the ZX/discard-ZX Processing canvas, open
`zx_modular_v1/processing/ZXVisualPatcherV1/ZXVisualPatcherV1.pde` and add
`--send-processing` to the command. Processing listens on UDP port `7497`.

For diagram editing and density inspection without the continuous PennyLane
control sweep, run this bridge instead:

```sh
python -m zx_modular_v1.examples.processing_density_bridge
```

In Processing, press `Q` to load the mixed-state discard example, `D` to inspect
its 16×16 density matrix, and Return to send the validated candidate to the
existing engine on port `7402`.

Open `max/QMW_ZX_Density_Matrix_Engine_v1.maxpat` for the full complex matrix
stream on `7498`. It receives preview revisions immediately; after Return,
`resonator_v9` publishes the evolving post-commit matrix at 10 Hz.

## 6. What comes next

These six values are musically meaningful projections, not the full ZX tensor.
The next implementation layer is a true ZX wire carried as four real channels:

```text
[Re(|0>), Im(|0>), Re(|1>), Im(|1>)]
```

That representation fits both Max MC patch cords and VCV polyphonic cables.
Z-spiders, X-spiders, Hadamard edges, cups, caps, and rewrite operations can
then become matched modules in both hosts, while the current control stream
remains the performance and inspection surface.
