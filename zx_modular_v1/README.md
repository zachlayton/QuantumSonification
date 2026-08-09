# ZX Modular v1

`zx_modular_v1` is a semantics-first prototype for treating a ZX diagram as a
modular instrument patch without collapsing the distinction between quantum
processes and audio feedback.

The same graph currently has three synchronized forms:

1. an open ZX multigraph with Z spiders, X spiders, plain wires, Hadamard
   wires, and ordered input/output boundaries;
2. an exact NumPy tensor contraction that returns the represented linear map;
3. a neutral JSON patch plan containing dual-rail modules, cables, phases, and
   exact complex tensor coefficients for a later Max/Gen or OSC host.

## Why dual rail?

Each ZX wire carries a two-dimensional system. The prototype represents that
wire as two complex rails, one for basis value `0` and one for basis value `1`.
This makes the algebra explicit:

- a Z spider is a phase-coherent merge/split tensor;
- an X spider is the same junction in the Hadamard-rotated basis;
- a plain cable carries the identity matrix;
- a Hadamard cable carries the normalized 2-by-2 Hadamard matrix;
- spider phase is a literal complex phase, not an arbitrary MIDI mapping.

Multi-wire maps use the existing workstation convention: boundary `q0` is the
least-significant basis bit and flattened labels read `|q[n-1] ... q1 q0>`.

This is a faithful tensor/control representation. It does **not** claim that
audio fan-out clones an unknown quantum state. Nor is a closed ZX wire
automatically the same thing as a unit-delay audio feedback loop.

## First rewrite instrument

The first implemented performance gesture is spider fusion. Two adjacent
same-color modules connected by a plain cable fuse into one module; their
phases add. Before accepting the rewrite, the system contracts both diagrams
and verifies that their linear maps agree numerically. Zero-phase degree-two
spiders can likewise be removed with the same semantic check.

Run the demonstration from the repository root:

```bash
python -m zx_modular_v1.examples.zx_modular_demo
```

To make `zx_modular_v1` importable from any directory in the `music`
environment, install this repository in editable mode:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python -m pip install -e \
  /Users/zlayton/QuantumSonification
```

After that, either `python -m ...` or the `qmw-zx-demo` command works without
depending on the current directory.

Write only the compiled patch plan:

```bash
python -m zx_modular_v1.examples.zx_modular_demo \
  --json-out /tmp/zx_phase_chain_patch.json
```

Run the tests:

```bash
python -m unittest discover -s zx_modular_v1/tests -v
```

## Relationship to the existing workstation

The natural integration path is:

```text
ZX diagram
  -> semantics-checked rewrite engine
  -> dual-rail modular patch plan
  -> Max/Gen tensor modules or OSC control
  -> existing QMW resonators, spatialization, and material descriptors
```

PennyLane 0.45 provides the first half of that path directly through its
optional PyZX transforms:

```text
PennyLane quantum function
  -> qml.transforms.to_zx
  -> PyZX rewrite/simplification
  -> zx_modular_v1.pennylane_bridge
  -> exact modular patch plan
```

Run the installed bridge demonstration from any directory:

```bash
env MPLCONFIGDIR=/private/tmp/qmw_zx_matplotlib \
  /Users/zlayton/miniconda3/envs/music/bin/python \
  -m zx_modular_v1.examples.pennylane_vcv_bridge_demo \
  --json-out /private/tmp/pennylane_zx_patch.json
```

PennyLane/PyZX use the first declared wire as the most-significant matrix axis,
while QMW uses boundary zero as the least-significant bit. The bridge records
and verifies the necessary boundary reversal instead of silently changing the
matrix. It also preserves PyZX's global scalar. Rack can later preserve that
scalar, ignore it as quantum-global phase, or sonify it against a reference.

### Immediate VCV Rack path

The installed Rack 2 system already contains OSCelot and its expander. This
allows a first control-rate bridge without compiling a custom Rack plugin.
PennyLane state metrics are mapped to OSCelot faders as follows:

| ID | Signal | OSCelot value |
|---:|---|---|
| 1 | bound ZX phase | phase in turns, modulo one |
| 2 | PennyLane `<Z0>` | bipolar `-1..1` mapped to `0..1` |
| 3 | normalized population entropy | `0..1` |
| 4 | normalized l1 coherence | `0..1` |
| 5 | parameter gradient | `tanh`-bounded and mapped to `0..1` |
| 6 | dominant basis probability | `0..1` |

Dry-run the bridge and inspect its OSC messages:

```bash
env MPLCONFIGDIR=/private/tmp/qmw_zx_matplotlib \
  /Users/zlayton/miniconda3/envs/music/bin/python \
  -m zx_modular_v1.examples.pennylane_vcv_live_demo
```

After adding OSCelot and its expander to a Rack patch, configure OSCelot's
receive port to match `--port`, map fader IDs 1–6, and add `--send`. Add
`--sweep --frames 0` for a continuous stream. The companion Max monitor listens
on port 7496 and is enabled with `--send-max`. PennyLane runs at control rate;
Rack and Max should smooth those values and keep all audio-rate DSP inside
their real-time threads.

For the exact setup sequence, OSCelot teaching commands, musical control
mapping, and the combined Max + Rack command, see
[`PRACTICAL_QUICKSTART.md`](PRACTICAL_QUICKSTART.md).

### Pure ZX diagram frontend

The Processing sketch
[`processing/ZXVisualPatcherV1/ZXVisualPatcherV1.pde`](processing/ZXVisualPatcherV1/ZXVisualPatcherV1.pde)
provides a notation-first canvas with draggable Z/X spiders, Hadamard boxes,
boundaries, curved wires, phase editing, graph saving, and visual spider
fusion. It listens on port 7497:

```bash
python -m zx_modular_v1.examples.pennylane_vcv_live_demo \
  --send-processing --sweep --frames 0 --interval 0.05
```

See [`processing/README.md`](processing/README.md) for the interaction keys and
the boundary between the current visual prototype and the next bidirectional,
semantics-checked graph transaction.

The repository's existing `engine.process_graph` separation should remain:
the ZX graph describes the mathematical process; genuinely causal audio
feedback belongs in the sonic realization graph. The existing QASM/QAC bridge
can later provide circuit-to-ZX import, while the existing Max control room can
host the compiled modular realization.

## Deliberately deferred

- circuit/QASM to graph-like ZX import;
- a complete ZX rewrite rule set and rewrite search;
- scalar-aware simplification beyond the implemented exact rules;
- a real-time Max/Gen module library and OSC lifecycle;
- UI editing, undo history, and animated rewrite performance;
- interpretive mappings from ZX invariants into the QMW material layer.

Those should build on the tested core rather than precede it.

## Hybrid Max + VCV realization

The preferred system uses both patching environments. Max is the semantic
laboratory and VCV Rack is the performance surface; Python/PennyLane owns the
canonical graph. The hybrid compiler emits paired host profiles with one stable
revision:

```bash
env MPLCONFIGDIR=/private/tmp/qmw_zx_matplotlib \
  /Users/zlayton/miniconda3/envs/music/bin/python \
  -m zx_modular_v1.examples.hybrid_max_vcv_demo \
  --json-out /private/tmp/qmw_zx_hybrid_plan.json
```

See `HYBRID_MAX_VCV_ARCHITECTURE.md` for the division of labor, four-channel
wire protocol, edit transaction, timing policy, and current local status.
