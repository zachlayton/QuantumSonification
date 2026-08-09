# QMW Wilson Complete CPS Flow Visualizer v1

Processing 4 visualization for `examples/qmw_complete_cps_flow_v5.py`
(and the inner-Hexany-compatible v4 host).

- UDP input: `7411`
- Required Processing library: `oscP5`
- Inner vertices: the six states of the Wilson `2)4 1-3-5-7` Hexany
- Stellate tips: the eight states in `1)4` and `3)4`
- Full graph: all 16 states in the `1–4–6–4–1` Boolean/CPS lattice
- Left ledger: atomic realtime frame of `0000` through `1111`, grouped by
  Pascal grade with probability, phase, and Wilson subset product
- Selected outline: the basis vertex chosen by the temperature scheduler
- Flow outlines: current source and destination basis states
- Global poles: `|0000⟩` as the `0)4` empty-product identity and `|1111⟩` as
  the `4)4` total product `105`
- Middle 14 states: the traditional Stellate Hexany or stella octangula
- Vertex radius: conditional probability
- Vertex hue: relative quantum phase
- Directed pulse width: probability current
- Pulse travel: the sonified departure-to-arrival gesture
- Phase 4 MOS strip: stable generator-power IDs, source/target Scale-Tree
  address, morph progress, audible Pascal grade, and Constant Structure status
- Circuit tuning label: derived family and active factor master set; Bell,
  GHZ, Weave, and arbitrary programmed circuits update this from their actual
  interaction graph
- Hexany vertex labels: transactionally updated factor pairs and exact CPS
  ratios relative to the `|0011>` anchor—no fixed `1-3-5-7` mock labels remain
  after a circuit retunes the instrument
- Alternate Tetradic Diamond view: the 12 directed ratios `a/b` of the current
  four-factor master set. Reciprocal ratios occupy opposite vertices; shared
  denominators form harmonic triangles and shared numerators form subharmonic
  triangles.
- Diamond node fill is live probability support and its bright inner ring is
  transition coherence, calculated by aggregating the corresponding qubit
  exchange over both spectator bits. Labels show the raw Diamond ratio and its
  exact octave-folded audition ratio.
- Mirrored `/qmw/wilson/modulation` frame: the eight normalized global lanes
  that Max emits as Ableton CC20–27

The paired layout is intentional: the ledger is the literal quantum-state
view, while the rotatable stellate/octahedral geometry is the Wilson harmonic
projection. They share the same atomic `/qmw/wilson/state16` frame rather than
asking one geometry to carry both meanings.

Start the Python v5 host, open the sketch in Processing, then use **EVOLVE
ONCE** or **RECURSE** in the Max v5 patch. The Phase 4 controls select `-1/all`
or one Pascal grade, a related MOS target such as `2/5`, and morph progress
from `0` to `1`. Drag the graph to rotate it.

Press `D` for the Tetradic Diamond and `H` for the Hexany/Stellate view. You can
also click the geometry title to switch. The 16-state ledger remains visible in
both views, so the Diamond is a second projection of the same realtime quantum
frame rather than a separate simulation.
