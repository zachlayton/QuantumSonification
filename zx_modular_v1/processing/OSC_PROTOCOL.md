# QMW ZX Processing OSC protocol v1

The Processing frontend listens for canonical PennyLane controls on UDP `7497`
and fans them out to three local sound-engine targets:

| Target | Port | Message family |
|---|---:|---|
| Max | 7496 | `/qmw/zx/*` |
| VCV Rack / OSCelot | 7000 | `/fader` |
| SuperCollider language | 57120 | `/qmw/zx/*` |
| Python semantic verifier | 7499 | `/qmw/zx/*` |
| Max density engine | 7498 | `/qmw/zx/density/*` |
| Max Full4Q tomography | 7426 | `/qmw/zx/pauli/*` |

## Normalized performance controls

Max and SuperCollider receive:

```text
/qmw/zx/fader  <int id>  <float value>
```

Rack receives the OSCelot-compatible equivalent:

```text
/fader  <int id>  <float value>
```

IDs and values:

| ID | Meaning | Range |
|---:|---|---|
| 1 | ZX phase in turns | 0..1 |
| 2 | qubit-0 Z expectation mapped to unit range | 0..1 |
| 3 | normalized population entropy | 0..1 |
| 4 | normalized l1 coherence | 0..1 |
| 5 | bounded parameter gradient | 0..1 |
| 6 | dominant basis probability | 0..1 |
| 7 | Rack-only rewrite trigger pulse | 0 then 1 then 0 |

## Diagram-edit messages

Max and SuperCollider additionally receive:

```text
/qmw/zx/node/position  <int id> <float x> <float y>
/qmw/zx/node/phase     <int id> <string kind> <float radians>
/qmw/zx/node/add       <int id> <string kind> <float x> <float y> <float radians>
                       <string boundary-role> <int boundary-index>
/qmw/zx/node/delete    <int id>
/qmw/zx/edge/add       <int source> <int target> <string kind>
/qmw/zx/graph/scalar   <float real> <float imag>
/qmw/zx/rewrite/fuse   <int keep> <int removed> <string kind> <float radians>
/qmw/zx/rewrite/apply  <string rule> <int selection-count> <int node-id>...
```

Positions are normalized to the Processing canvas. Node kinds are `Z`, `X`,
`H`, `HB`, `B`, or `D` (discard). A `B` role is `input` or `output`; a `D`
role is `discard`. Edge kinds are `plain` and `hadamard`; repeated edge
messages preserve parallel wires.

The `/rewrite/fuse` message reaches Max, SuperCollider, and Rack trigger ID 7
only after Python has returned a successful semantic-verification result.

## Semantic verification handshake

Python requests and receives a complete Processing mirror on port `7499`:

```text
/qmw/zx/graph/request
/qmw/zx/graph/begin  <int revision> <float scalar-real> <float scalar-imag>
...node/add and edge/add messages...
/qmw/zx/graph/end    <int revision>
```

After testing a fusion with the exact `zx_modular_v1.fuse_spiders` rewrite,
Python replies to Processing port `7497`:

```text
/qmw/zx/rewrite/result \
  <int keep> <int removed> <int verified> \
  <float absolute-error> <float fused-phase> <string message>
```

Named rules use a complete graph transaction:

`rule` currently includes `identity_removal`, `pi_copy`, `state_copy`,
`bialgebra`, `hopf`, `color_change`, `local_complementation`, `pivot`, and
`absorb`. Local complementation takes one selected node; pivot takes two.

```text
/qmw/zx/rewrite/graph/begin <string rule> <float scalar-real> <float scalar-imag>
/qmw/zx/rewrite/graph/node  <int id> <string kind> <float x> <float y> <float phase>
                            <string boundary-role> <int boundary-index>
/qmw/zx/rewrite/graph/edge  <int source> <int target> <string kind>
/qmw/zx/rewrite/graph/end   <string rule> <string message>
/qmw/zx/rewrite/result_v2   <string rule> <int verified> <float error>
                              <string message> <int nodes> <int edges>
                              <float scalar-real> <float scalar-imag>
```

The replacement graph is transmitted only after PyZX confirms exact tensor
equality with scalar preservation enabled.

## Discard-ZX density transaction

Processing requests evaluation from Python:

```text
/qmw/zx/density/request <int graph-revision>
```

Python returns one bounded frame to both Processing `7497` and Max `7498`:

```text
/qmw/zx/density/begin         <int revision> <string mode> <int dimension>
                               <float success-weight>
/qmw/zx/density/meta          <int revision> <float trace> <float purity>
                               <float coherence-l1> <float entropy>
                               <float minimum-eigenvalue> <float success-weight>
/qmw/zx/density/probabilities <int revision> <dimension floats>
/qmw/zx/density/row           <int revision> <int row>
                               <dimension real floats>
                               <dimension imaginary floats>
/qmw/zx/density/bloch         <int revision> <int qubit> <float x> <float y>
                               <float z> <float local-purity>
                               <float local-entropy>
/qmw/zx/density/end           <int revision> <string message>
/qmw/zx/density/error         <string message>
```

Return in Processing sends `/qmw/zx/density/commit <int revision>`. The bridge
then uses the engine's existing `begin → rho/real → rho/imag → commit`
transaction on port `7402`; it never mutates the live density from a partial
matrix.

The Max companion independently stages all `dimension` `/row` messages and
only publishes its Jitter matrices, controls, and audio state after the
matching `/end`. Exact flat list buses are also published through 128×128;
at 256×256 the full matrix remains available through Jitter without exceeding
Max's practical atom-list limits.

The visual density compiler accepts one to eight contiguous output boundaries
`q0..qN`, and either no inputs or matching contiguous inputs. It emits the
natural 2×2 through 256×256 matrix, so the same route handles Bell states,
general ZX states, and circuit-derived maps rather than recognizing a GHZ
shape. The `1` through `8` keys are merely generalized-cat-state shortcuts.
For example, `2` produces a Bell matrix with support at basis indices `0` and
`3`; an unrelated two-qubit gate graph is still evaluated by the same
compiler.

Return can commit only one- through four-qubit previews because the existing
resonator is fixed at four qubits. At this boundary only, smaller matrices are
embedded with absent high-index qubits set to `|0〉`; larger matrices remain
available in Processing and Max and are explicitly rejected for resonator
commit.

Once a density revision has been committed, `resonator_v9` publishes its
post-evolution matrix through the same protocol and Max port at 10 Hz by
default. Its mode field is `engine_evolution`; the preview bridge uses
`discard_cpm_state`, `discard_cpm_map_on_zero`, `state_preparation`, or
`map_on_zero`.

## Pauli-gadget transaction

After Processing creates or edits a four-qubit gadget it sends Python:

```text
/qmw/zx/pauli/gadget <string label> <float theta-radians>
                      <int central-phase-node-id>
```

The multi-gadget editor uses the ordered score transaction:

```text
/qmw/zx/pauli/score <int count>
  [<int gadget-id> <string label> <float theta>]...
/qmw/zx/pauli/active <int gadget-id> <string label> <float theta>
                      <int central-phase-node-id>
```

These editor requests go only to Python. After checking the complete mirrored
graph, Python multicasts the verified result to Processing, Max, and the
tomography receiver. This prevents an unchecked canvas request from being
mistaken for verified engine state.

Python uses PyZX to evaluate the mirrored 16×16 graph, including its complex
scalar, and replies to both Processing `7497` and Max `7498`:

```text
/qmw/zx/pauli/verified <string label> <int weight> <float theta>
                        <int verified> <float absolute-error> <string message>
/qmw/zx/pauli/score_verified <int count> <int verified>
                              <float absolute-error> <string message>
```

Every density frame also carries the active tomography coefficient:

```text
/qmw/zx/pauli/live <int revision> <string label> <int weight>
                    <float expectation> <float theta> <int verified>
```

The expectation is exactly `Tr(ρP)` in logical label order `q0 q1 q2 q3`.
Tomography or other OSC clients can highlight the corresponding canvas gadget:

```text
/qmw/zx/pauli/select <string label>
```

The Full4Q v2 Max patch sends that selection message directly to Processing
port `7497`.

## Shared Euler transactions

Processing requests decomposition of selected one-wire ZX nodes:

```text
/qmw/zx/euler/request <int request> <int node-count> <int node-id>...
```

Python returns the verified shared record to Processing `7497`, Max `7498`,
and tomography `7426`:

```text
/qmw/zx/euler/result <int request> <string source> <int qubit> <string basis>
  <float theta> <float phi> <float lambda> <float gamma>
  <float zx-scalar-phase> <int verified> <float absolute-error>
/qmw/zx/euler/error <int request> <string message>
```

After the first verified result, Processing retains the selected node IDs as a
live Euler lens. Phase edits affecting any retained Z or X node emit a new
request after a 90 ms debounce. Each refresh receives a new request ID and is
fanned out through the same Processing, Max, and tomography result path. The
latch is released when the lens is hidden, a retained node is removed, or a
structural rewrite replaces the selected chain.

The conductor/QAC circuit workflow uses an atomic transaction:

```text
/qmw/circuit/euler/begin revision gate-count basis qubit-count
/qmw/circuit/euler/gate revision instruction operation qubit
  theta phi lambda gamma zx-scalar-phase verified absolute-error
/qmw/circuit/euler/end revision gate-count verified maximum-error skipped-count
```

For `ZXZ`, the time-ordered visual wire is
`Z(lambda) → X(theta) → Z(phi)`. Python retains 64-bit radians and performs
matrix reconstruction before publishing.

## Companion receivers

- Max:
  `max/QMW_ZX_Processing_Companion_v1.maxpat`
- SuperCollider:
  `supercollider/qmw_zx_processing_companion_v1.scd`
- Rack:
  add OSCelot + OSCelotExpander, listen on port `7000`, and use fader IDs
  1–6.
