# QMW ZX Visual Patcher — Processing frontend

`ZXVisualPatcherV1` is a diagram-first frontend for the hybrid ZX instrument.
It intentionally looks like ZX-calculus notation rather than a conventional
modular rack or Max patch.

## Open it

Open this sketch in Processing 4:

```text
/Users/zlayton/QuantumSonification/zx_modular_v1/processing/ZXVisualPatcherV1/ZXVisualPatcherV1.pde
```

The installed `oscP5` library provides OSC input on UDP port `7497`. Processing
does not synthesize audio; it forwards controls and graph gestures to:

- Max on port `7496`;
- VCV Rack / OSCelot on port `7000`;
- SuperCollider on port `57120`.

Start the semantic/density bridge in a Terminal before editing:

```sh
cd /Users/zlayton/QuantumSonification
conda activate music
python -m zx_modular_v1.examples.processing_density_bridge
```

It mirrors the visual graph on `7499` and evaluates any valid one- through
eight-qubit ZX state or map through PyZX. The resulting natural-size density
matrix ranges from 2×2 through 256×256 and is multicast to Processing and the
dedicated Max density engine on `7498`. This compiler is not GHZ-specific:
Bell states, hand-built diagrams, and circuit-derived ZX maps all follow the
same path. An explicitly approved state of up to four qubits can also be
forwarded to the existing fixed four-qubit QMW resonator on `7402`; smaller
states are embedded only for that commit transaction. Larger states remain
fully inspectable and streamable but are not committed to that resonator.

## Send PennyLane state

From the repository root in the `music` environment:

```sh
python -m zx_modular_v1.examples.pennylane_vcv_live_demo \
  --send-processing --sweep --frames 0 --interval 0.05
```

Processing now performs the fan-out, so `--send-processing` is sufficient when
it is running.

For sound, open either:

- `max/QMW_ZX_Processing_Companion_v1.maxpat`, then click its `ezdac~`; or
- `supercollider/qmw_zx_processing_companion_v1.scd`, then evaluate its first
  block.

For Rack, add OSCelot + OSCelotExpander and listen on port `7000`.

## Edit the graph

- Drag a node to move it.
- Press `Z`, `X`, `H`, or `B` to add a Z spider, X spider, Hadamard box, or
  boundary at the pointer. A `B` placed in the left half becomes the next
  tagged input; one placed in the right half becomes the next tagged output.
- Press `1` through `8` to create one phase-zero green spider with that many
  tagged outputs. `2` is the Bell state, `3` is GHZ₃, and `N` outputs produce
  the corresponding generalized cat state. These are convenience macros, not
  a special evaluation mode.
- Press `L`, type an output count from `1` through `64`, and press Return for a
  compact variable-arity spider. Counts through eight receive an exact dense
  preview. Counts above eight remain graph-only to avoid exponential dense
  matrix allocation.
- Press `0` to open the circuit-to-ZX preset library. Its first three diagrams
  reproduce the Max QAC circuit programmer gate-for-gate:

  - `1` QAC Bell: `H(q0)`, `CX(q0,q1)`, with q2/q3 in `|0〉`;
  - `2` QAC GHZ₄: `H(q0)`, then `CX(0,1)`, `CX(1,2)`, `CX(2,3)`;
  - `3` QAC WEAVE: staggered `H` on all wires, `CX(0,1)`, `CX(2,3)`,
    `CX(1,2)`, `T(q0)`, and `S(q3)`.

  The expanded circuit graphs are deliberately distinct from the compact
  spider shortcuts: plain `2` shows a fused Bell spider, while `0`, `1` shows
  the circuit programmer's four-wire preparation network. The library also
  includes a four-qubit cluster graph state, a CNOT map, a T magic state, and
  `|0000〉`.

  The PDF-inspired second bank adds:

  - `8` SWAP as `CX(0,1) → CX(1,0) → CX(0,1)`;
  - `9` an exact identity laboratory containing `H²`, `T†T`, `TT S†`, and
    `CX²`;
  - `A`, `B`, and `C` four-qubit ring, star, and complete graph states;
  - `D` two identical-support `ZZII` phase gadgets with angles `π/4` and
    `π/8`, already selected. Press `F` to fuse them into `3π/8`.
  - `E` a local-complementation pattern with its valid `π/2` interior spider
    selected. Press lowercase `w`.
  - `F` a pivot pattern with its valid interior Pauli pair selected. Press
    `Shift-W`.
  - `G` a one-input/one-output teleportation CPTP channel. Its two coherent
    measurement records control the X/Z corrections and are then discarded.

  Press `D` after choosing a state or map preset to open its density matrix.
  The phase-fusion preset instead uses `F` and the existing Pauli-score
  verifier.
- Press `N` to insert a CNOT already expanded into its green Z-control and
  red X-target spiders, with four boundary stubs.
- Press `J`, type exactly four `I`/`X`/`Y`/`Z` symbols, and press Return to
  append a complete four-wire Pauli gadget to the ordered score. For example,
  `J`, `X`, `Y`, `Z`, `I`, Return appends `XYZI`. Repeat `J` to build a score
  of up to eight gadgets. `I` leaves a wire disconnected from the gadget, `Z`
  uses a direct leg, `X` uses `H–Z–H`, and `Y` uses `S†–H–Z–H–S`.
- Press `M` to cycle the same semantic score through expanded ZX, CNOT-ladder,
  and balanced-tree synthesis views. The ladder/tree views do not change the
  canonical ZX graph.
- Select a contiguous one-wire chain of degree-two Z, X, or explicit H nodes
  and press `E` for the Euler lens. Python extracts its exact 2×2 tensor,
  returns the verified `ZXZ` values `θ`, `φ`, `λ`, and `γ`, and Processing
  displays the time-ordered `Z(λ) → X(θ) → Z(φ)` chain. A successful result
  latches that selection as a live Euler lens: subsequent bracket, arrow, or
  mouse-wheel phase edits on the chain are re-evaluated after a 90 ms debounce
  and update Processing, Max, and tomography automatically. Latched nodes have
  a green ring. Press `E` on another selection to move the lens; press `E` with
  no selection to show or hide it. Hiding the lens releases the live selection.
- Drag a gadget's lower phase spider horizontally to move that macro to another
  score position. The status line distinguishes a semantics-preserving
  commuting move from an intentional noncommuting score edit.
- Shift-click any part of two gadgets to select their phase macros. Processing
  displays `COMMUTE` or `ANTICOMMUTE` using the even-anticommuting-sites test.
- Select two equal-label gadgets and press `F` for whole-gadget fusion. They may
  be separated by other gadgets only when the selected label commutes through
  every intervening gadget; their phases then add exactly.
- Press `Y` to insert a standard ZXH H-box labelled `−1`.
- Press `V` to add a discard terminal. It must terminate exactly one wire.
- Press `T` to insert the compact ZXH Toffoli: three Z spiders, a ternary
  H-box, and the two target-wire Hadamards.
- Press `C`, then click two nodes, to create a wire.
  Repeating this between the same two nodes creates parallel wires, as required
  for the Hopf pattern.
- Press `Command-C` and `Command-V` to copy and paste the selected subgraph.
  Plain `C` remains cable mode.
- Shift-click to select two nodes.
- Use Left/Right Arrow, `[`/`]`, or `-`/`=` to change selected spider phases.
  Trackpad scrolling also works where Processing reports it as a mouse wheel.
  A newly created Pauli gadget selects its phase spider automatically, so these
  keys change its angle θ without requiring a mouse wheel.
- Select two connected spiders of the same color and press `F` to perform
  visual spider fusion. The starter graph now contains two connected green Z
  spiders specifically for this gesture. A blue `FUSION READY` cue appears
  when the selection is valid.
- Select one zero-phase, degree-two spider and press `I` for identity removal.
- Select a π spider and the opposite-colour spider it passes through, then
  press `P` for π-copy / Pauli push.
- Select a degree-one 0/π state spider (the adjacent opposite-colour spider may
  also be selected) and press `K` for state copy.
- Select a connected Pauli-phase Z/X pair and press `A` for bialgebra.
- Select an opposite-colour pair joined by two parallel plain wires and press
  `O` for Hopf.
- Select one spider and press `G` to change its colour and toggle every
  incident wire between plain and Hadamard.
- Select one interior `±π/2` Z spider whose incident wires are Hadamard and
  press lowercase `w` for verified local complementation. The spider is
  removed, its neighborhood is complemented, and the required phases and
  scalar are retained.
- Select two connected interior Pauli-phase Z spiders in a graph-like diagram
  and press `Shift-W` for verified pivot. The pair is removed and connectivity
  across its neighbor sets is toggled.
- Select a standard H-box and an adjacent degree-one X spider with phase π,
  then press `U` for ZXH absorb.
- Press Delete to remove selected nodes.
- Press `S` to save `zx_graph.json`.
- Press `R` to restore the demonstration graph.

## Density matrices and discard ZX

Press `Q` for the smallest working mixed-state example. It prepares a
four-qubit system with q1–q3 in `|0〉`, entangles q0 with an environment leg,
and terminates that leg with discard. Press `D` to open or refresh the density
inspector.

The bridge treats the visible ZX graph as a pure dilation, doubles its ket/bra
semantics, and traces every discard leg. The result is a physical, normalized
`2^N × 2^N` density matrix in `q0_lsb` ordering for any valid graph with one to
eight contiguous tagged outputs and either zero inputs or the same number of
contiguous tagged inputs. A zero-input graph is evaluated as a state; a map is
applied to `|0…0〉`. The inspector displays:

- complex matrix entries (brightness = magnitude, hue = phase);
- trace, purity, von Neumann entropy, ℓ₁ coherence, and minimum eigenvalue;
- all `N` reduced-qubit Bloch vectors, purities, and entropies.

For the `Q` example, expect total purity `0.5`, entropy `1.0`, and a zero Bloch
vector for q0. This is a true mixed state rather than a pure-state outer
product.

Press `2` for a Bell state. Its natural 4×4 matrix has `0.5` at `(0,0)`,
`(0,3)`, `(3,0)`, and `(3,3)`. Press `3` for the genuine
zero-input/three-output state `|000〉 + |111〉`; its natural 8×8 matrix has the
same pattern at indices `0` and `7`. Press `8` for the exact 256×256
eight-output counterpart. The same evaluator also handles non-GHZ diagrams:
add and connect boundaries, spiders, Hadamards, gadgets, or circuit-derived
maps, then press `D`.

Choose `0`, then `G` for the teleportation CPTP preset. It is the
deferred-measurement form of standard teleportation: two ancillary `|0〉`
states create the Bell resource, the two measurement records coherently
control the X and Z corrections, and discard traces those records out. The
visible channel has one tagged input and one tagged output. Its scalar is
corrected so the complete discarded-environment map is trace-preserving.
The density inspector applies it to `|0〉`; the regression suite separately
verifies the complete channel on all four one-qubit operator-basis elements.

Press Return only when a one- through four-qubit preview is the state you
intend to load into the existing resonator. The bridge embeds a smaller matrix
with unused high qubits fixed to `|0〉` and sends the exact atomic engine
transaction:

```text
/qmw/state/begin
/qmw/state/rho/real
/qmw/state/rho/imag
/qmw/state/commit
```

The engine remains authoritative: it validates Hermiticity, trace, positivity,
and dimensions before replacing its live density state. Five- through
eight-qubit previews stay live in Processing and Max; Return reports that the
current resonator is four-qubit rather than truncating the state.

For the full real-time complex matrix in Max, open
`max/QMW_ZX_Density_Matrix_Engine_v1.maxpat`. It stages all `2^N` rows before
publishing a revision, dynamically sizes its Jitter matrices from 2×2 through
256×256, exposes reusable Jitter/list buses, and includes a fixed 16-voice MC
instrument that folds larger matrices into an audible summary. It uses CNMAT
`OSC-route`, not `oscparse`.

Before Return, Max follows the Processing/PyZX preview. After Return, a running
`resonator_v9` takes over the same port and publishes its evolving density at
10 Hz, so Hamiltonian, noise, memory, and feedback changes remain visible and
audible rather than freezing at the imported seed matrix.

## Pauli gadgets and live tomography

The `J` score workflow is scalar-aware. The visual graph includes the normalization
and global-phase correction needed for PyZX to verify its complete 16×16 map
against

```text
exp(-i θ P / 2)
```

rather than merely accepting a diagram up to global phase. For multiple
gadgets, Python verifies the complete left-to-right ordered product. The project uses
logical label order `q0 q1 q2 q3`, with q0 as the least-significant basis bit.

Each density refresh calculates `Tr(ρP)` for the active gadget and sends the
same bounded message to Processing and Max:

```text
/qmw/zx/pauli/live revision label weight expectation theta verified
```

Open `max/QMW_ZX_Density_Matrix_Engine_v1.maxpat` to receive that message on
port `7498`. It publishes the reusable named Max buses
`qmw.zx.pauli.live`, `qmw.zx.pauli.label`, `qmw.zx.pauli.weight`,
`qmw.zx.pauli.expectation`, and `qmw.zx.pauli.theta`.

`max/QMW_Full4Q_Tomography_81_v2.maxpat` now has a `PAULI TERM 0–254`
selector. Selecting a loaded coefficient sends
`/qmw/zx/pauli/select <label>` to Processing port `7497`; when that label is
the gadget on the canvas, its phase spider is highlighted.

The multi-gadget messages are:

```text
/qmw/zx/pauli/score count [gadget_id label theta]...
/qmw/zx/pauli/score_verified count verified error message
/qmw/zx/pauli/active gadget_id label theta central_node_id
```

Processing sends these editor transactions to Python first. Python then
multicasts the verified score and active-gadget state to Processing, Max, and
the tomography receiver, so Max never treats an unchecked canvas edit as
verified engine state.

The phase-gadget fusion and balanced-tree views follow Cowtan et al., *Phase
Gadget Synthesis for Shallow Circuits* (2019/2020). A ladder uses
`2(weight−1)` CNOT depth; a balanced realization exposes logarithmic CNOT
depth while retaining the same Pauli rotation.

## Shared Euler circuit data

The same Euler lens receives circuit-wide records from the conductor/QAC
bridge. Every accepted circuit sends each numeric one-qubit instruction to
Processing while retaining entanglers and measurements as explicit skipped
records in the Python/JSON report. The canonical implementation is
`qmw/euler.py`; see `docs/EULER_WORKFLOW.md`.

## Current boundary

The Processing graph editor now commits the named ZX/ZXH rewrites only after
Python/PyZX verification. PennyLane control values animate the diagram, update
the first Z-spider phase, and are forwarded to each sound engine. Diagram edits
and successful rewrites are also emitted as explicit OSC messages for Max and
SuperCollider. See `OSC_PROTOCOL.md` for their exact paths and argument types.

See `../RULE_SYSTEM.md` for the generator/macro/rewrite distinction and the
implementation tiers and the remaining editable-complex-H-box work.

For every named rule, the Python process mirrors the canvas on port `7499`,
runs the matching PyZX or ZXH transformation, compares the complete
before/after tensors with scalar preservation enabled, and returns either the
replacement graph or a visible rejection reason. Hopf therefore retains real
parallel wires, and color change can return explicit blue Hadamard edges.
Max and SuperCollider receive the committed rule name, error, and scalar;
Rack receives a short rewrite pulse as fader ID `7`. After verified fusion,
the fused phase also becomes fader ID `1`.
