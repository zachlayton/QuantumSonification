# QMW Max-to-SuperCollider Porting Plan

## Scope and priorities

This is a project-wide instrument plan, not a Wilson/CPS-only plan and not a
quota by category. The audit covers the full `QuantumSonification` tree:
control-room and native-source integrations; Bloch/spatial, Grover, QPE,
Chladni, Heisenberg, Hilbert, Wilson, Pauli/statistics, temporal-mechanics,
geometry/reverb, density/modal, wavetable, Bohmian/eigenfield,
excitation/granular, operator-ecology, molecular, and relativistic work.

Ports are ranked by musical centrality, maturity of the existing Python/OSC
contract, how much Max-package coupling they remove, and whether a native
SuperCollider implementation adds a genuinely useful performance engine.
Python remains authoritative for quantum state, geometry, and statistical
models. SuperCollider owns realtime DSP, event scheduling, spatialization,
safe feedback, and visual monitoring of received state.

The repository inventory at this audit contained 285 `.maxpat` files, 586
Python files, 89 README/reference documents, and 10 existing `.scd` files
(including historical and bundled duplicates). Candidate selection inspected
the whole inventory, then collapsed version families to their latest meaningful
instrument instead of allowing copies and generated bundles to dominate the
ranking.

## Implemented first: complete CPS probability flow

Source Max instrument:
`max/QMW_Complete_CPS_Flow_Instrument_v5.maxpat`

SuperCollider port:
`supercollider/qmw_complete_cps_flow_v1.scd`

Why it was first: a substantial port was already present, its protocol is
explicit and tested, and it exercises several invariants that later ports also
need: atomic state commits, exact-frequency events, event roles, recursive
transport controls, and external Scala geometry.

The port consumes Python's appended `frequency_hz` directly. Scala, CPS,
Diamond, MOS, and equal-tempered choices are therefore made once in Python;
SuperCollider does not reconstruct the pitch from MIDI or bend. Ratio affects
timbre without being applied to pitch a second time. Arrival, dyad, and gesture
articulations preserve the recursive probability-current event grammar.

State compatibility is intentionally dual:

- `/qmw/wilson/state16` carries the native sixteen probabilities and phases.
- revisioned `/qmw/state/rho/{real,imag}` carries a paired 16x16 matrix as
  `revision + 256` row-major values per component.
- unrevisioned `/qmw/qac/rho/{real,imag}` carries the QAC-compatible paired
  256-value form.

The 256 cells are matrix coefficients, not 256 computational states. Matrix
frames update the sixteen basis populations from the diagonal and derive
relative phase from coherence against the most populated reference basis.

## Existing SuperCollider coverage to retain

These are already useful ports or support layers and should be consolidated,
tested, and documented rather than restarted:

- density/modal field: `qmw_density_spectral_resonator.scd`
- living geometry convolution: `qmw_living_partconv_support.scd`
- wavefunction-cloud grains: `qmw_wavefunction_cloud_grains_v1.scd`
- eigenfield/Zeeman grainflow: `qmw_eigenfield_zeeman_granulator_v1_1.scd`
- GRW event resonator: `qmw_grw_resonator_v1.scd`
- QPE/Chladni modal resonator:
  `quantum_chladni_synth_v1/supercollider/qmw_qpe_chladni_resonator_v1.scd`
- FluCoMa interchange: `qmw_flucoma_sc_bridge.scd`

The canonical control room and `QMW_Native_Quantum_Instruments_v1_7.maxpat`
are important, but they are primarily routing/control surfaces. They should be
rebuilt after the underlying audio engines, not counted as audio ports by
themselves.

## Next six ports

### 1. Exact Grover statevector instrument

Max source: `max/QMW_Grover_Statevector_Realtime_v1_2.maxpat`

Proposed file: `supercollider/qmw_grover_statevector_instrument_v1.scd`

Architecture: consume the exact 65,536-amplitude evolution summaries on
`/qmw/grover/statevector`, retain the existing 64-mode Walsh projection, and
give each mode an event envelope rather than a continuously mapped level.
Marked probability controls the oracle/diffusion contrast; state revision
drives atomic mode-bank commits; the surface-effects chain becomes native
ring modulation, tides-like modulation, modal resonators, and a freeze-capable
reverb. Python/MLX remains the exact 16-qubit state authority.

### 2. QAC 256-point wavetable and quantum-IR instrument

Max source: `max/QMW_QAC_Wavetable_Circuit_Designer_v4_QFT.maxpat`

Proposed file: `supercollider/qmw_qac_wavetable_field_v1.scd`

Architecture: transactional double buffers for `/qmw/wavetable/points` (legacy
and chunked revisions), four-row Pauli-15 surfaces, local/IBM A-B morphing,
`Osc`/`VOsc` direct playback, two-dimensional scan resynthesis, and a separate
PartConv quantum-IR lane. Circuit construction remains in QAC/Python; SC is the
renderer. Buffer swaps occur only after all 256 samples for a revision arrive.

### 3. Realtime implicit-surface geometry reverb

Max source: `max/QMW_Realtime_Surface_Reverb_v5_6.maxpat`

Proposed file: `supercollider/qmw_realtime_implicit_surface_reverb_v1.scd`

Architecture: a DC-safe twenty-node feedback-delay network with smoothed probe
values; sphere, torus, tanglecube, heart, gyroid, Schwarz P/D, and Neovius
fields evaluated in sclang at control rate; equation morph and XYZ rotation;
descriptor input from the existing emergent-geometry OSC bridge; dry safety
path, bounded feedback matrix, and replaceable input bus from QMW modal
instruments. This is the native geometry/reverb port, distinct from the
file-based living PartConv engine.

### 4. Heisenberg relational matrix instrument

Max source: `heisenberg_instrument_v2/QMW_Heisenberg_Rings_Matrix_Instrument_v2.maxpat`

Proposed file: `supercollider/qmw_heisenberg_relational_matrix_v1.scd`

Architecture: preserve the transaction-bracketed 256-cell Heisenberg matrix
and the coherent/unread/recorded measurement semantics. Each of sixteen rows
drives one SC physical/modal body; row magnitude controls excitation,
off-diagonal mass controls structure, phase dispersion controls brightness,
matrix change controls damping, and signed energy gaps retain their published
frequencies. Rebuild the rotating-quadrature wavetable and acoustic performance
memory without mutating the canonical quantum matrix. This replaces the
`vb.mi.rngs~` dependency with a documented SC modal-body approximation rather
than claiming timbral identity with Rings.

### 5. Polyphonic complex Hilbert/matrix instrument

Max source:
`QMW_Hilbert_Suite/QMW_Polyphonic_Complex_Hilbert_Instrument_v6_3.maxpat`

Proposed file:
`supercollider/qmw_polyphonic_complex_hilbert_instrument_v1.scd`

Architecture: sixteen excitation-driven modal voices, per-lane analytic pairs
using `Hilbert`, a double-buffered 16x16 complex density/operator matrix, phase
projection, and a causal limited feedback branch. The locked harmonic field
remains an energy-normalized anchor while complex-layer morph moves the matrix
from identity toward the selected operator. This is the deeper relational
modal port; it should reuse the 256-cell transaction layer introduced by the
CPS client rather than invent another matrix protocol.

### 6. Four-qubit Bloch-harmonic spatial instrument

Max source:
`BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v6/QMW_Bloch_Harmonics_Four_Qubit_Spat_v6.maxpat`

Proposed file: `supercollider/qmw_bloch_harmonics_spatial_v1.scd`

Architecture: four independent eight-mode spherical-harmonic resonators driven
by the established reduced-Bloch-vector packets; azimuth/elevation/radius map
to four Ambisonic sources with binaural or stereo decode; the shared sixteen-
mode density layer remains quieter and explicitly separate; living IR support
reuses the existing PartConv layer. Preserve the visible mapping of signed
spherical harmonics to magnitude and 0/pi phase while replacing Spat5 and
GenExpr with native SC DSP.

## Recommended sequence

Build Grover and the wavetable field next because they establish reusable
atomic high-dimensional state and buffer transactions. Then build the
implicit-surface reverb. Heisenberg and Hilbert should follow on one shared
256-cell complex-matrix receiver and safety layer. Add Bloch/spatial last,
reusing the density resonator and living-convolution support already present.

## Strong reserve list

These remain worthwhile after the six above:

- `max/patches/bohmian_v4OSC.maxpat` ->
  `supercollider/qmw_bohmian_pilot_field_v1.scd`
- `qmw_platonic_geometry_reverb_noise_excitation_v1/QMW_Platonic_Noise_Excitation_v5.maxpat`
  -> `supercollider/qmw_platonic_noise_excitation_v1.scd`
- `pauli_statistical_grainflow_v1/QMW_Pauli_Parameter_Field_Grainflow_v2.maxpat`
  -> `supercollider/qmw_pauli_parameter_grainflow_v1.scd`
- `quantum_statistics_instrument_v1/QMW_Quantum_Statistics_Instrument_v1.maxpat`
  -> `supercollider/qmw_quantum_statistics_instrument_v1.scd`
- `qpe_synthesizer_v1/QMW_QPE_Synthesizer_v1.maxpat` ->
  `supercollider/qmw_qpe_measurement_sequencer_v1.scd`
- `quantum_temporal_composition_v2/max/QMW_Correlation_Differentiation_Clock_v2.maxpat`
  -> `supercollider/qmw_correlation_clock_v1.scd`

The Bohmian and Platonic excitation studies are musically strong, but the
current eigenfield/Zeeman, density-modal, and living-geometry SC layers already
cover some adjacent territory. The reserve ranking avoids duplicating those
engines before Grover, Heisenberg, wavetable, and Bloch/spatial work—none of
which yet has an equivalent native SC renderer.
