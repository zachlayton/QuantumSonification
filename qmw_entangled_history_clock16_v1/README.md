# QMW Entangled History Clock 16 v1

This package begins the QMW implementation of the discrete history-state
construction used in parallel-in-time quantum simulation.  Element 1 prepares
the pure joint state

```text
|Psi> = (1 / sqrt(N)) sum_t |t>_C tensor U_F^t |psi_0>_S
```

with:

- four clock qubits, so `N = 16` clock states;
- the existing four-qubit QMW Floquet system;
- a 256-amplitude eight-qubit joint state vector;
- QMW clock-major indexing
  `joint_index = system_index + 16 * clock_index`.

The implementation mirrors the phase-estimation-like circuit with the binary
controlled powers `U_F`, `U_F^2`, `U_F^4`, and `U_F^8`.  NumPy `complex128`
is the reference backend so later MLX or hardware implementations can be
checked against it.

Element 2 exposes read-only computational-clock conditioning.  It returns all
sixteen clock probabilities, normalized conditional system vectors, and
conditional 16 x 16 density matrices.  Conditioning here is a mathematical
query on the stored history state, not a simulated measurement or collapse.

Element 3 calculates read-only history diagnostics:

- the reduced clock density matrix `rho_C`;
- the finite time-averaged system density matrix;
- clock and system reduced purities;
- system-time linear entropy `E_2 = 1 - Tr(rho_C^2)`;
- all sixteen Loschmidt echoes and their discrete average;
- the clock density in the QFT basis and its mode probabilities.
- the clock Schmidt spectrum and deterministic temporal modes;
- effective Schmidt rank, participation number, and von Neumann entropy.

The Loschmidt value is explicitly the finite sixteen-sample average, not an
infinite-time estimate.  Clock-QFT probabilities are defined by the forward
QFT convention `exp(-2*pi*i*m*t/N)`.  A period-doubled Floquet history need
not peak at mode 8 itself: quasienergy-paired components appear in bins
separated by 8, corresponding to a phase separation of `pi`.

Element 4 constructs four matched controls from the same sixteen states:

1. the ordinary ordered sequence `0..15`;
2. a reproducibly shuffled classical sequence;
3. an incoherent clock-labelled joint density with all cross-time blocks
   removed;
4. the original coherent pure history density.

Sequential and shuffled variants retain order metadata as trajectories.  The
uniform sequential ensemble and incoherent joint state have the same reduced
system average; they differ operationally because the former is a procedure
and the latter a static block-diagonal state.  Only the coherent joint state
retains off-diagonal clock blocks.  Temporal block coherence is kept distinct
from `E_2`: the former witnesses coherent cross-time storage, while the latter
measures system--time entanglement and distinguishable evolution.

Element 5 adds an offline, density-operator-based audio proof of concept.  It
renders separate stereo WAV stems for the sixteen conditioned moments, the
clock-traced temporal average, the coherent clock-QFT distribution, and a
dephased-clock reference, plus a combined mix.  The mapping is invariant under
global state-vector phase.  It is an audition layer only: it does not add a
measurement, stochastic clock, OSC transport, or canonical-state mutation.

The preferred Step 5 revision is rhythmic and granular rather than sustained.
A binary word is mapped literally to a millisecond clock: `1` launches a grain
event and `0` is silent for one complete clock cell.  The default proof repeats
`10101` while its interval changes from 140 ms to 110 ms.  Every sounding step
contains short overlapping grains from all sixteen conditional moments; the
temporal average is an eigenvalue-weighted grain reservoir; and the clock layer
uses short QFT-mode grains with modes separated by eight sharing a micro-onset.
A matched clock-dephased cloud uses the same event lattice.  The interval curve
may stretch or contract the clock without changing the bit word, and a dry
rhythm stem makes the gate directly audible.  Conventional note values are an
optional external synchronization layer, not the native representation.  The
rhythm word and interval curve are classical audition controls, not quantum
randomness.

The polyrhythmic Step 5 projection removes the remaining global gate.  Each of
the sixteen clock branches and each of the sixteen clock-QFT modes repeats the
binary word on an independent millisecond clock.  Exponential interval spacing
makes modes separated by eight run at a `sqrt(2)` period ratio; consequently
the dominant Floquet modes 1 and 9 continually drift through coincidence.  The
coherent and dephased renders use identical local clocks and differ only in
their QFT probability weights.  These pulse trains are explicitly an auditory
projection of the state, not literal hidden classical clocks.

The Ligeti-form export fixes the identity of the ensemble more strictly:
sixteen MIDI channels and sixteen MusicXML parts map one-to-one onto clock
basis states `|0000>` through `|1111>`.  All voices receive the same finite hit
budget because the coherent history has a uniform computational-clock
distribution.  Their unequal fixed millisecond periods make them phase and
exhaust at different wall-clock times.  Standard MIDI Type 1 uses one track
and channel per basis state; MusicXML uses one part per basis state.  Both files
use a neutral 60 BPM transport with 1000 ticks or divisions per quarter, so one
unit is exactly one millisecond.

The matching SuperCollider example is
`supercollider/qmw_entangled_history_clock_clicks_v1.scd`.  It realizes the
same sixteen clock-basis identities, fixed millisecond periods, `10101` words,
common release, and 48-hit windings as deterministic click voices.  It can
render spatially in stereo or route the sixteen voices to sixteen discrete
audio outputs.

`supercollider/qmw_entangled_history_temporal_mechanics_clicks_v1.scd` advances
the fixed-period control into a coherence-coupled temporal readout.  It uses
the exact normalized reduced-clock coherence of the default Floquet history:
the eight even and eight odd clock states form two internally coherent groups
with zero coherence between them.  Their complex overlap phases collectively
modulate instantaneous click rates.  Coupling zero is the matched clock-
dephased control.  The coherence matrix is quantum-derived; the phase-coupling
equation is explicitly the auditory transducer rather than a new physical law.

The generic constructor also supports a six-qubit clock through
`clock_qubits=6`.  This produces 64 clock states, a 1024-amplitude joint state,
and two exact 32-state parity-coherence communities for the default Floquet
model.  The matching real-time realization is
`supercollider/qmw_entangled_history_temporal_mechanics_clicks64_v1.scd`; it
uses two factorized complex mean fields to calculate the complete coherence
force efficiently for all 64 click voices.

The 64-voice SuperCollider start function accepts one through four gain-
normalized octave layers per clock state.  Layer offsets are base, +1 octave,
-1 octave, and +2 octaves.  The even coherence community is spatially biased
left and the odd community right, with internal panning retained inside each
field.  For example, `~qmwTemporal64Start.(0.20, 4)` starts the coherent model
with four layers; `~qmwTemporal64Start.(0.0, 1)` is the single-layer dephased
control.

The paper-faithful Schmidt-mode rendering separates encoded clock positions
from independent temporal voices.  A 64-position clock coupled to the
four-qubit system can contain at most sixteen nonzero Schmidt modes.  For the
default exact-pi Floquet history, only two modes are active: equal-weight even
and odd clock communities.  `schmidt_sonification.py` assigns one granular
voice to each nonzero mode, maps `|v_k(t)|` to event level, and maps the
relative phase of `v_k(t)` to bounded microtiming.  A magnitude-only control
uses the same clock grid, event support, eigenvalues, and grains with the phase
microtiming removed.

The randomized-basis clock removes the repeating master grid.  Its reference
history uses a fixed tilted four-qubit product state, a five-percent Floquet
pulse error, and small nonuniform transverse fields.  All sixteen Schmidt
modes are present, with a participation number near 9.8.  Each mode receives
an independent stream of local X/Y/Z clock measurements.  Born-sampled
outcomes provide amplitude and surprisal, while changes in measurement phase
recursively alter elapsed milliseconds.  A fixed seed makes the simulation
repeatable; changing it represents a new set of simulated measurements.  The
matched control reuses the measurement records but removes phase from interval
accumulation.  This is a stochastic unraveling for audition, not a claim that
the clock density matrix contains hidden classical trajectories.

The IBM-data renderer works directly from the two 512-shot `BitArray` records
returned by the hardware job.  It preserves sampler record order without
claiming that order is calibrated processor time.  Consecutive clock-value
distances create elapsed milliseconds, expected computational histories use
clean low clicks, forbidden histories use fractured transients, and Fourier
bins separated by 32 share pitch identity across opposite stereo and octave
registers.  Separate hardware, ideal-reference, stem, and A/B renders are
written from the same mapping.

The IBM musical-form renderer is a complementary histogram-level view.  It
combines the four clock states in each `t mod 16` class into one stable voice.
Computational counts choose three to seven hits in a sixteen-cell Euclidean
pattern and shape a four-cycle accent contour.  Fourier mass determines voice
prominence and orchestration; lower/upper Fourier balance controls octave
color; hemisphere imbalance controls gradual clock displacement.  Forbidden
histories become quiet fractured flams at their measured proportional rate.
Strong Fourier voices enter first and remain longest, making the hardware
statistics audible as a sectional musical process rather than raw randomness.

`ibm_history_clock64.py` provides two exact Qiskit preparations of the ten-
qubit history.  The structured dynamics reference uses the controlled binary
powers of the Floquet map.  The hardware path exploits the default history's
closed form—six Hadamards, six phase gates, and four clock-to-system CNOTs—to
prepare the identical 1024-amplitude state at much lower depth.  It builds
computational and clock-Fourier measurement circuits, validates both against
NumPy, and requires `--confirm-ibm` before submitting any hardware job.

## Scientific boundary

These steps prepare and inspect a simulated coherent history state.  They do
not yet:

- measure, collapse, or trace out the clock;
- introduce stochastic sampling or measurement backaction;
- mutate the canonical live 16 x 16 density matrix;
- publish OSC or generate sound.

Those operations remain separate later elements so their effects can be
tested against this state-preparation reference.

## Test

From the repository root:

```bash
python -m unittest qmw_entangled_history_clock16_v1.tests.test_history_state -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_diagnostics -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_control_study -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_sonification -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_granular_sonification -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_polyrhythmic_sonification -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_ligeti_history_export -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_supercollider_temporal_mechanics -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_history64_temporal_mechanics -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_schmidt_sonification -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_randomized_clock_sonification -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_ibm_data_sonification -v
python -m unittest qmw_entangled_history_clock16_v1.tests.test_ibm_musical_sonification -v

# Run in the project's Qiskit-enabled music environment.
/Users/zlayton/miniconda3/envs/music/bin/python -m unittest \
  qmw_entangled_history_clock16_v1.tests.test_ibm_history_clock64 -v

python -m qmw_entangled_history_clock16_v1.render_step5
python -m qmw_entangled_history_clock16_v1.render_step5_granular
python -m qmw_entangled_history_clock16_v1.render_step5_polyrhythmic
python -m qmw_entangled_history_clock16_v1.render_step5_ligeti_export
python -m qmw_entangled_history_clock16_v1.render_schmidt_rhythm64
python -m qmw_entangled_history_clock16_v1.render_randomized_clock64

# Local IBM-circuit validation only; does not connect or submit.
/Users/zlayton/miniconda3/envs/music/bin/python -m \
  qmw_entangled_history_clock16_v1.ibm_history_clock64

# Read-only backend selection and transpilation; does not submit.
/Users/zlayton/miniconda3/envs/music/bin/python -m \
  qmw_entangled_history_clock16_v1.ibm_history_clock64 --inspect-backend
```

The tests verify normalization, purity, dimensions, basis ordering, binary
controlled-power semantics, all sixteen conditional Floquet branches, equal
clock probabilities, and agreement with the established Floquet trajectory.
The diagnostic tests additionally verify the exact stationary and maximally
entangled limits, QFT mode ordering, reduced-state purity equality, and the
normalization of the live Floquet diagnostic outputs.
The control tests verify deterministic shuffling, identical temporal averages,
clock dephasing, joint-state purities, cross-time block removal, and
order-sensitive adjacent-state distances.
The sonification tests verify finite bounded stereo output, coherent/dephased
audible difference, and invariance under an initial global phase.
The granular tests also require literal millisecond-clock hits and rests, all
sixteen moments on each sounding step, matched coherent/dephased timing,
deterministic rendering, and bounded output.
The polyrhythmic tests require sixteen independent local clocks, the expected
`sqrt(2)` interval ratio for modes separated by eight, global-phase invariance,
and a coherent/dephased difference on an otherwise identical clock ensemble.
The Ligeti export tests require an exact channel/part mapping for all sixteen
clock basis states, a common release, independent endings, valid MIDI Type 1
headers, millisecond MusicXML divisions, and global-phase invariance.
The SuperCollider temporal-mechanics tests cross-check its embedded conditional
phases against the NumPy history and verify the exact even/odd clock-coherence
communities used by the server-side coupling network.
The 64-state tests verify the six-qubit history dimensions, uniform clock
probabilities, reduced purity, all embedded conditional phases, and numerical
identity between the factorized two-mean-field calculation and the complete
64x64 pairwise coherence force.
