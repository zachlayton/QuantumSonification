# Wilson Quantum Geometry System v1

## Design claim

Erv Wilson's work can serve QMW as a *mesoscale grammar*: a layer between raw
quantum state and sound that describes what counts as a tone, a neighbor, a
symmetry, a complement, a scale, and a playable coordinate. This is more
useful—and more faithful—than treating the harmonic series as a metaphor for
quantum mechanics or using microtonality as a final pitch quantizer.

Terumi Narushima's account identifies four mutually supporting parts of that
grammar:

1. **Scale Tree and MOS** organize generated scales and their nested moments
   of two-step coherence.
2. **Constant Structures** preserve the number of scale degrees subtended by
   each interval and provide a test for melodic integrity in higher-limit
   tunings.
3. **Diamonds and CPS** expose reciprocal chord fields, centreless harmonic
   sets, complements, subsets, and modulation paths.
4. **The generalized keyboard** turns those abstract relations into a stable,
   repeatable two-dimensional action space.

These are different jobs. MOS is primarily a generated melodic/time geometry;
CPS is a combinatorial harmonic/state geometry; Constant Structure is an
invariance criterion; and the keyboard is an interface projection.

Tenney adds a perceptual metric to Wilson's structures. Nicholson and Sabat
add the register-dependent question of whether a rational sonority can be
directly tuned, and distinguish harmonic distance from spectral intersection.
The working order is therefore:

```text
Wilson compositional structure -> Tenney perceptual metric -> sounding realization
```

## The quantum bridge

The strongest exact correspondence is between a Wilson `k)n` CPS and the
fixed-Hamming-weight sector of `n` qubits.

For master factors `g_0 ... g_(n-1)`, associate each CPS tone with a subset
`S` of `k` factor positions:

```text
r(S) = product(g_i for i in S)
|S>  = computational basis state whose occupied bits are S
```
Both spaces have dimension `binomial(n, k)`. Two CPS tones are adjacent when
one factor is exchanged, so their subsets have symmetric difference two.
This is exactly the Johnson graph `J(n, k)`, and it is preserved by an XY-style
exchange Hamiltonian that conserves excitation number.

Pascal's Triangle is therefore not decorative: row `n` is the complete
instrument registry for an `n`-qubit/factor field. Its entries are the voice
counts of grades `0)n ... n)n`, and reflection of the row is exactly the
bitwise-complement map `k -> n-k`:

```text
n=4:  1  4  6  4  1       Hexany at 2)4
n=5:  1  5 10 10  5  1    paired Dekanies at 2)5 and 3)5
n=6:  1  6 15 20 15  6 1  self-complementary Eikosany at 3)6
```

The implementation exposes this directly as `pascal_cps_row(n)`. A renderer
can allocate one grade, complementary grade pairs, or the entire stratified
register without changing the identity scheme used by the state adapter.

For the self-mirroring case `n = 2k`, bitwise complement maps every tone to
the tone formed from all unused factors. That makes Wilson's complementary
pairing a particle-hole involution on the register. The `2)4` Hexany is the
smallest musically rich example:

```text
|0011> <-> 1·3       complement |1100> <-> 5·7
|0101> <-> 1·5       complement |1010> <-> 3·7
|1001> <-> 1·7       complement |0110> <-> 3·5
```

This formulation improves on the current `project_frame_to_wilson_cps()`
prototype in `qmw/synthesis.py`, which projects all sixteen four-qubit states
onto the complete grades `0)4` through `4)4`. For a Hexany instrument, the six
weight-two states should be the native space and probability in the other ten
states should be treated as shell leakage or as other CPS grades—not as extra
Hexany notes.

## Musical state contract

The Wilson layer should publish four independent classes of information.

| Quantum quantity | Wilson quantity | Musical responsibility |
|---|---|---|
| basis label / occupation | CPS factor subset | pitch identity and visual vertex |
| probability | vertex weight | excitation, loudness, density |
| relative phase | complex vertex field | timbre, spatial angle, interference when routed to a shared mode |
| Hamiltonian coupling | CPS/keyboard edge | transition likelihood, gesture, voice leading |

Pitch comes from the factor product after an explicit period fold and audition
anchor. Phase does not detune pitch. A renderer may combine complex amplitudes
only after declaring that multiple quantum vertices feed the same acoustic
mode; otherwise probabilities and phases remain attached to separate vertices.

Measurement is an event in the quantum model, not the default note scheduler.
The continuous state may excite a polyphonic CPS field; actual measurement can
then articulate collapse, select a path, change orchestration, or re-seed the
field.

## Perceptual and sounding logic

For a reduced interval `b/a`, Tenney harmonic distance is `log2(a*b)`. This is
a weighted city-block distance in prime-exponent space. It must remain
distinct from CPS adjacency: two tones may both be one factor exchange away
while having different perceived distances. The first sound engine therefore
weights the Johnson-graph exchange Hamiltonian using Tenney distance and
Nicholson/Sabat harmonic intersection.

Nicholson and Sabat define dyadic intersection as `(a + b - 1)/(a*b)`.
Distance acts as a transition cost; intersection acts as a fusion strength.
Their approximate tuneability model is also register dependent: for lower
frequency `f`, periodicity pitch is `f/a` and the least common partial is
`b*f`. Configurable reference bounds of 20 Hz and 6000 Hz help select playable
registers without pretending to be universal thresholds.

Tenney's temporal proposal also matters for synthesis: a stable pitch takes
time to activate as a harmonic point and persists after its acoustic release.
A real-time instrument should therefore maintain an auditory-memory state
instead of converting each incoming quantum frame directly into independent
notes.

## MOS and Scale-Tree layer

A linear scale generated by ratio `g` within period `p` has logarithmic
positions

```text
x_j = (j * log_p(g)) mod 1.
```

A Moment of Symmetry occurs when the circularly sorted positions have exactly
two step sizes. For `g = 4/3` in the octave, the implementation reproduces
Wilson's sequence at 2, 3, 5, 7, 12, 17, and 29 tones; the seven-tone moment is
type `3/7` because the generator occupies scale degree three.

The Scale-Tree address `a/b` gives both a scale type and a playable coordinate
system. Its two Farey parents supply the generalized-keyboard coordinates:
their numerators locate the generator and their denominators locate the
period. For `4/7`, parents `1/2` and `3/5` produce generator coordinates
`(1, 3)` and period coordinates `(2, 5)`, matching Narushima's Centaur example.

In QMW, the L/R Scale-Tree path can become a compositional control word:

- moving deeper selects a finer MOS approximation;
- moving to an ancestor coarsens the pitch/gesture alphabet;
- adjacent mediants create controlled intermediate tunings;
- a quantum or stochastic process may navigate the tree without changing the
  meaning of the CPS state underneath it.

## Proposed system architecture

```text
quantum source / circuit / density state
                 |
                 v
       Wilson state adapter
       - select CPS grade
       - preserve leakage
       - attach relative phase
                 |
          +------+------+
          |             |
          v             v
   CPS harmonic graph   MOS / Scale Tree
   pitch + adjacency    melodic resolution
          |             |
          +------+------+
                 v
      generalized-keyboard projection
      + Constant-Structure validator
                 |
          +------+-------+-----------+
          v              v           v
       Max/MPE       resonator     geometry UI
```

## Implementation sequence

### Phase 1 — mathematical kernel (implemented here)

- Generic `k)n` CPS construction.
- Exact bitmask identity with fixed-weight qubit shells.
- Johnson-graph edges and complementary pairs.
- Statevector projection with absolute and shell-conditioned probability.
- MOS generation and two-step validation.
- Scale-Tree ancestry and generalized-keyboard coordinates.

### Phase 2 — QMW adapter

- **Implemented:** explicit CPS-shell projection without silent
  renormalization.
- **Implemented:** statevector, density-matrix, and canonical
  `QuantumStateFrame` inputs.
- **Implemented:** transactional OSC packets for topology, vertices, leakage,
  conditional purity, auditory activation, and measurement.
- Add a choice of excitation-conserving circuit templates (XY/iSWAP quantum
  walks) whose topology is the selected CPS.
- **Implemented:** attack integration and post-release persistence.
- Remaining: add MOS address publication once a live compositional navigator
  owns the selected Scale-Tree position.

### Phase 3 — instrument

- **Implemented:** six-voice `2)4 1-3-5-7` Max Hexany reference instrument.
- **Implemented:** JI pitch, probability, phase, coupling, and measurement on separate
  control lanes.
- **Implemented:** complementary pairs across spatial and spectral duals.
- **Implemented:** centreless CPS identity plus an explicit temporary anchor for
  audition/transposition.
- **Implemented:** Processing stellate geometry consumes the same revisioned
  CPS frames and flow events as the sound renderer.
- **Implemented:** Processing can switch between the CPS Hexany/Stellate
  projection and a Tetradic Diamond projection. The Diamond contains all 12
  ordered ratios `a/b` from the active four-factor master set; reciprocals are
  geometrically opposite, shared-denominator triangles are harmonic, and
  shared-numerator triangles are subharmonic. Node support, exchange coherence,
  phase, and the active transition come from the live 16-state frame. Press
  `D`/`H`, or click the geometry title, to change views without interrupting
  the circuit.

The offline `hexany_study.py` is the first sounding proof: coherent spreading,
particle-hole complement, and measurement/coda form are rendered with exact
Hexany pitch, probability energy, and phase-based spatial/spectral color.

### Phase 4 — compositional navigation

- **Implemented:** MOS ancestor/descendant morph frames use generator powers as
  stable voice identities. Entering and leaving powers receive equal-power
  gains, so resolution changes do not reassign an existing voice to a new
  pitch.
- **Implemented in the v5 host:** Pascal grade `-1/all` or `0…4` is an
  instrumentation filter. `2)4` remains the geometric reference, but is no
  longer the only audible ontology.
- **Implemented:** exact Constant Structure validation reports every interval
  class that subtends more than one circular step count.
- **Implemented:** generic `3)6` Eikosany construction plus its six `2)5`
  Dekanies, six `3)5` Dekanies, and 30 fixed-include/fixed-exclude `2)4`
  Hexanies.
- **Implemented:** minimum-Tenney-distance CPS graph paths produce a shared
  timeline of exact ratios, normalized spectral position, and optional
  eigenfield-weighted arrival times.

The live v5 controls publish:

```text
/qmw/wilson/navigation/grade        -1 | 0 | 1 | 2 | 3 | 4
/qmw/wilson/navigation/mos_target   numerator denominator
/qmw/wilson/navigation/mos_progress 0.0 ... 1.0
```

The host returns atomic `/qmw/wilson/navigation/frame`, `/voice`, and `/end`
packets to Max and the Processing visualizer. A voice packet carries the stable
generator-power ID, log-period position, pitch ratio, activation, and its
source/target order. The first integration uses the MOS lane as melodic
resolution and the CPS/Pascal lane as harmonic instrumentation; it deliberately
does not pretend that MOS degrees and CPS vertices have a canonical one-to-one
mapping.

### Circuit-derived tuning frames

The v5 instrument can now treat circuit geometry as the source of the tuning
system rather than holding `1-3-5-7` fixed. The adapter reads the committed
Qiskit circuit itself—gate names, interaction edges, connected components,
weighted qubit degree, phase activity, and depth—so it also works for circuits
drawn by hand in the programmer.

```text
empty / separable  -> 1-3-5-7  MOS 1/2
paired components  -> 1-3-5-7  MOS 2/5
connected global   -> 1-3-7-11 MOS 3/7
connected woven    -> 1-5-11-13 MOS 5/12
```

Factors are assigned to qubits by structural role (weighted interaction
degree), while the basis bitmask remains the persistent voice identity. Thus a
new circuit can change the tuning dramatically without relabeling `|0011>` as
some other state. Bell currently resolves to the paired family, GHZ to the
global family, and Weave to the woven family. These correspondences are an
explicit compositional sonification design, not a claim that a CNOT physically
contains an 11-limit interval.

The host also publishes each dynamic `2)4` vertex transactionally:

```text
/qmw/wilson/tuning/begin
/qmw/wilson/tuning/vertex
/qmw/wilson/tuning/end
```

Each vertex contains its basis mask, current factor pair, product, exact CPS
ratio relative to the `|0011>` anchor, and octave-folded audition ratio.
Processing stages all six vertices and changes the displayed labels only after
the matching `/end` packet arrives. Consequently the octahedron labels remain
truthful under fixed, paired, global/GHZ, and woven circuit tunings.

`/qmw/wilson/tuning/enabled 0|1` provides an immediate fixed-versus-dynamic A/B
comparison. `/qmw/wilson/tuning/frame` publishes the derived family,
Scale-Tree address, circuit fingerprint, and active four-factor master set to
Max and Processing.

### Global Ableton modulation bank

The v5 host publishes one atomic normalized frame on
`/qmw/recursive/modulation`. Max smooths each lane with `slide 2 4`, converts
`0…1` to MIDI `0…127`, suppresses repeated values, and sends the result through
`from Max 1` on master channel 1. MPE note expression remains on member
channels 2–16, so the global controls do not overwrite per-note CC74.

```text
CC20  population entropy       basis-distribution uncertainty
CC21  normalized coherence     off-diagonal pure-state coherence
CC22  mean qubit entanglement  mean single-qubit von Neumann entropy
CC23  participation            normalized effective basis-state count
CC24  phase order              probability-weighted circular phase alignment
CC25  Pascal-grade centroid    mean excitation number / 4
CC26  Hexany mass              probability in the weight-two shell
CC27  flow strength            strongest current in the latest recursion step
```

All lanes are bounded before transmission. In Ableton, enable Track/Remote for
the `from Max 1` input, enter MIDI Map mode, select a parameter, and move or
trigger the desired circuit stream. The fixed CC numbers make mappings stable
between sessions.

### Circuit-programmer loop transport

The circuit builder has a deterministic 16-column loop independent of Wilson
`RECURSE`. `LOOP` starts from the currently selected column, performs its live
gate interventions, advances the highlighted column, and wraps from step 16 to
step 1. Empty columns remain timed rests. While running the button reads
`STOP LOOP`; the adjacent `−/+` buttons change the interval by 30 ms within a
30–4000 ms range.

This distinction is intentional:

```text
LOOP     deterministic repetition of the drawn circuit columns
RECURSE  temperature-weighted stochastic motion through the CPS state
STEP n   perform only the selected circuit column
```

Clicking any grid cell selects that column as the next loop position. Clearing
or loading Bell/GHZ/Weave stops the loop and returns the cursor to step 1 before
committing the new circuit.

## First experiment

Prepare a normalized state in the four-qubit weight-two shell, evolve it under
an excitation-preserving exchange circuit, and render the six Hexany vertices.
Use factor products for exact pitch, probability for resonator excitation,
relative phase for azimuth or spectral tilt, and complement pairs for opposing
spatial positions. Compare three conditions:

1. coherent quantum walk;
2. the same populations with randomized phase;
3. measured basis-state trajectories.

That experiment directly tests what quantum coherence contributes to a Wilson
harmonic field while holding tuning and graph topology constant.

## Epistemic boundary

This system asserts a mathematical isomorphism between two combinatorial
spaces and uses it compositionally. It does **not** assert that harmonic ratios
explain quantum physics, that the universe is intrinsically tuned to a Wilson
scale, or that sonified amplitudes are measurements unless the upstream engine
actually performs a measurement. Keeping that boundary explicit is what makes
the bridge scientifically defensible and artistically reusable.

## Local research sources

- Terumi Narushima, *Microtonality and the Tuning Systems of Erv Wilson*,
  especially chapters 3–6.
- James Tenney, *John Cage and the Theory of Harmony* (1983), Part II.
- Thomas Nicholson and Marc Sabat, *Fundamental Principles of Just Intonation
  and Microtonal Composition* (2018), especially sections 6–8.
