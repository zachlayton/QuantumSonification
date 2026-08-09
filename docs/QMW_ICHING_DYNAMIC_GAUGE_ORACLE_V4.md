# QMW I Ching Dynamic Gauge Oracle V4

V4 composes the unchanged persistent density-matrix V3 engine with a discrete
gauge geometry on the 64 hexagrams. It is implemented by:

- `qmw_iching_gauge_bridge_v1.py`: reusable density reduction, Q6 graph,
  magnetic adjacency/Laplacian, all 240 plaquettes, and gauge descriptors.
- `qmw_iching_dynamic_density_oracle8_v4.py`: V3 evolution plus a matching
  gauge snapshot and atomic OSC frame at every non-destructive observation.
- `qmw_iching_v4_live_service.py`: persistent evolution, atomic presentation,
  consultation control, and pre-measurement Wilson graph-wave sound.

## Mathematical contract

Qubits q0 through q5 are the six lines, bottom upward. Tracing out the shared
change register q6,q7 gives the 64 by 64 hexagram density matrix

\[
\rho_H(t)=\operatorname{Tr}_{q6,q7}\rho(t).
\]

Q6 contains 192 undirected edges. For neighbors connected by line `q`, V4 uses

\[
A_{ab}(t)=m_q(t)|\rho_{H,ab}(t)|e^{i\arg\rho_{H,ab}(t)},
\]

where `m_q` is V3's moving-line probability. Thus the edge phase comes from
the coherence while its magnitude is explicitly modulated by the change field.
The degree and Laplacian are

\[
D_{aa}=\sum_b|A_{ab}|,\qquad L=D-A.
\]

The absolute degree is required for positive semidefiniteness. V4 reports the
minimum eigenvalue and Hermiticity error as live diagnostics.

For each ordered line pair `i < j`, the other four bits have 16 settings. V4
uses the canonical base with bits `i` and `j` equal to zero and the orientation

\[
a\rightarrow a\oplus i\rightarrow a\oplus i\oplus j
\rightarrow a\oplus j\rightarrow a.
\]

This gives exactly `15 * 16 = 240` unique elementary plaquettes. Each stores
its base, two lines, four vertices, loop phase, and geometric-mean edge
strength. Tests verify invariance under arbitrary independent rephasing of all
64 basis vectors.

This is a U(1)-type discrete connection induced by density-matrix coherence on
a symbolic state graph. It is not asserted to be a physical electromagnetic
field. Its closed products are also naturally related to Bargmann/Pancharatnam
loop-phase language.

## Per-frame descriptors

V4 exposes all 240 raw phases and strengths plus bounded summaries:

- active plaquette count;
- strength-weighted mean absolute flux;
- strength-weighted circular mean phase and circular variance;
- signed circulation/chirality from the weighted sine of flux;
- strongest plaquette, including its base, lines, vertices, phase, and strength;
- the same descriptors for each of the 15 line pairs;
- the requested low magnetic-Laplacian eigenvalues;
- Laplacian trace, minimum eigenvalue, and Hermiticity error.

Angles are summarized with circular statistics rather than ordinary linear
means or variances.

## Atomic OSC V4

The root is `/qmw/iching/v4`. Every message in an observation begins with the
same revision, bounded by:

```text
/qmw/iching/v4/begin
...
/qmw/iching/v4/end
```

Routes include the existing dynamic fields (`hexagram64`, `moving6`, `pauli81`,
and `information`) plus:

```text
/qmw/iching/v4/gauge/summary
/qmw/iching/v4/gauge/spectrum
/qmw/iching/v4/gauge/edge_line         # 6 messages, 32 Q6 edges each
/qmw/iching/v4/gauge/pair_summary      # 15 messages
/qmw/iching/v4/gauge/plaquette_pair    # 15 bounded chunks
```

Each `plaquette_pair` chunk contains its line pair, 16 canonical bases, 16
phases, and 16 strengths. This exposes all 240 plaquettes in 15 packets instead
of flooding the receiver with 240 individual datagrams. A receiver must commit
only a complete matching begin/end revision.

The Processing receiver keeps all 64 hexagrams at stable positions. It maps
`hexagram64` to population halos, edge magnitude and phase to brightness and
flow, and summarizes the 15 line-pair sectors in the gauge panel. It retains all
240 received plaquettes and highlights the strongest phase-bearing loop incident
on the current H0. This makes the loop an oracle-local reading of the global
field rather than a global maximum that can remain fixed across consultations.
Same-trigram plaquettes are drawn with bowed edges because their four-dimensional
square collapses to a horizontal or vertical line in the 8 by 8 trigram layout.
Loop visibility is judged relative to the strongest plaquette in the current
frame, not by a fixed absolute edge weight; dephasing lowers the whole
Laplacian scale without making its relative gauge structure unresolved. A
near-zero Laplacian trace still suppresses loops after a true collapse.
Continuous frames change the field but do not recast H0/M/H1.

V3 routes and frame classes are unchanged.

## Run locally

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  qmw_iching_dynamic_density_oracle8_v4.py \
  --backend numpy --seed 8 --steps 12 --dt 0.01 \
  --json output/iching_dynamic_gauge_v4/seed-8.json
```

To stream the atomic V4 frames:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  qmw_iching_dynamic_density_oracle8_v4.py \
  --backend numpy --steps 12 --dt 0.01 --osc --osc-port 7404
```

For the persistent Processing and sound instrument, use the live service:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  qmw_iching_v4_live_service.py --backend mlx --no-engine \
  --visual-port 7404 --control-port 7405 \
  --dephasing 0 --warmup-time 2 --warmup-substeps 20 \
  --evolution-dt 0.1 --fps 1
```

The live instrument defaults to coherent evolution. Irreversible dephasing is
opt-in because a continuously running positive rate eventually removes the
off-diagonal coherence from which magnetic edges and plaquette phases are
built. `--warmup-time 2` begins presentation after the initially flat
connection has developed observable flux; it does not perform a measurement.
The faster display calibration `--evolution-dt 0.1 --fps 1` advances one tenth
of a model-time unit per wall-clock second.

`C` captures the current pre-measurement V4 Laplacian, performs the consultation
on that same persistent density matrix, commits the collapsed field and fixed
H0/M/H1 markers, then plays the Wilson graph-wave instrument excited at the
measured H0. The continuous field itself is silent. `I` remains the separately labeled
legacy V2 Aer/IBM comparison because that comparison circuit does not prepare
the arbitrary mixed V4 state.

After presenting the projective collapse, the live instrument re-prepares the
captured evolving ensemble for the next independent consultation. This prevents
rapid repeated casts from repeatedly measuring one collapsed hexagram and from
using its nearly empty Laplacian as the next tuning reference. Use
`--no-reprepare-after-consultation` only when repeated-measurement behavior is
the intended experiment.

The shared live tuning field is the complete Pascal aggregate of the Wilson
six-factor set `1-3-5-7-11-13`. A hexagram bitmask selects a subset of those
six factors. Its exact product ratio, period-folded and placed into a
Hamming-grade register, defines that hexagram's carrier. The seven CPS shells
have dimensions

```text
1, 6, 15, 20, 15, 6, 1
```

and therefore cover all 64 hexagrams without replacing their six-line
identities with eigenmode numbers. For a consultation, the full complex wave

\[
u(t)=\cos(\sqrt{L}\,t)K_\sigma|H_0\rangle,
\qquad
K_\sigma\propto e^{-\sigma L/\lambda_{max}}
\]

drives the amplitude and oscillator phase of those fixed node carriers. Thus
Wilson geometry determines pitch while the magnetic Laplacian determines how
energy moves. Quantum/gauge phase remains phase; it is not converted into
microtonal pitch deviation.

The normalized heat-kernel probe is a finite-width auditory pluck centered on
H0. Unlike a mathematical delta, it gives the immediate graph neighborhood a
quiet onset, so a consultation begins as a Wilson chord rather than an isolated
carrier. It changes only the sonification probe, not the oracle density matrix,
measurement probabilities, Laplacian, or reported transport diagnostic.

For audibility, the node magnitudes then use a square-root perceptual compression.
The complex phase is unchanged and every control frame is renormalized to its
original L2 graph-wave energy, so the operation reveals quiet destination
hexagrams without adding energy or changing their rank. Wilson node resonators
share the long damping constant: giving each node the old frequency-dependent
modal decay silenced it before the graph's 5-11 second transfer times.

`C` and `I` use the same fixed Wilson factor set, base frequency, octave
registers, and frozen reference Laplacian. Their audible comparison changes
only the H0 excitation inferred by each route. The previous logarithmic and
linear eigenmode mappings remain available offline with
`--frequency-mapping logarithmic` or `linear`; they are diagnostic alternatives,
not the live default. The 20 kHz safety ceiling still applies.

MLX remains optional and requires an accessible Apple Metal device. The NumPy
backend is the deterministic validation reference.

## Presentation boundary

The live V4 gauge field is now integrated into Processing and into the local
consultation chime. Gauge descriptors remain visual rather than continuously
sonified: a consultation is the intentional audible event. IBM comparison is
still a V2 experiment and must not be described as a measurement of the full
mixed V4 density matrix.
