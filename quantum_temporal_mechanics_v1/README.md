# Quantum Temporal Mechanics v1

This is a new operational layer beside `quantum_temporal_composition_v1`. It
does not posit a universal time operator or modify the Schrödinger equation.
Instead, it defines time through correlations among a finite quantum clock,
a system, and physical event records.

## The proposal

The primitive object is a joint state `rho_CS`, not a state evolving against a
master transport. A temporal description consists of five things:

1. **Clock** — a physical subsystem `C` with a covariant phase POVM
   `{E_k}`. In this finite prototype the readings are periodic Fourier states.
2. **Conditional state** — the system relative to reading `k`:

       rho_S|k = Tr_C[(E_k tensor I) rho_CS] / p(k)

3. **Event record** — a system effect `M`, with event time given by the joint
   Born rule `p(k|M) proportional to p(k) Tr[M rho_S|k]`.
4. **Duration** — a probability distribution over relative lags between two
   event-time distributions. Duration is uncertain whenever the events or the
   clock are uncertain.
5. **Temporal law** — a quantum channel relating neighboring conditional
   states. For a closed model this is `U(delta) rho U(delta)^dagger`; a later
   version can admit general CPTP maps and memory kernels.

The simulator's wall or coordinate time is therefore a preparation and
sampling parameter, never an observable output of the mechanics.

## What is genuinely new here

The earlier composition engine extracts a single clock phase and uses it to
drive local processes. This layer keeps the **whole clock distribution** and
makes records and durations first-class objects. It also exposes failure:

- local transition fidelity tests whether the proposed temporal law actually
  relates adjacent conditional states;
- closure fidelity reveals whether a finite periodic clock is compatible with
  the modeled system history;
- POVM completeness checks the clock measurement itself;
- clock entropy reports how broadly the history occupies available readings;
- translating the arbitrary clock origin shifts event times but leaves their
  relative-duration distribution invariant.

That last property is the initial temporal gauge principle:

> Absolute clock origin is descriptive; relational durations are physical.

## Important limits

- A finite phase clock wraps. It cannot distinguish one cycle from the next
  without a separate counter/memory record.
- Cross-correlating two event-time distributions is not a sequential joint
  probability for incompatible measurements. Sequential events require an
  explicit quantum instrument and record register; that is the main v2 task.
- The history-state builder uses coordinate time to prepare a controlled test
  state. The inference API itself only reads `rho_CS`.
- This is a research prototype and sonification formalism, not a claim of a
  new fundamental law or a quantum-gravity theory.

## Run

```bash
python -m quantum_temporal_mechanics_v1.demo --ticks 16
python -m unittest quantum_temporal_mechanics_v1.test_quantum_temporal_mechanics_v1 -v
```

The demo encodes a qubit orbit in a 16-reading clock, infers two phase-record
times, estimates their relational duration, and prints dynamical and clock
diagnostics as JSON.

## Max/MSP OSC

Start the continuous publisher (default `127.0.0.1:7443`):

```bash
python -m quantum_temporal_mechanics_v1.osc_demo
```

Or let the repository conductor feed it the canonical engine's live density
matrix and send density-driven clock records to Max's normal port `7400`:

```bash
python quantumsonification_conductor.py --with-temporal-mechanics
```

This conductor mode does **not** use the sequential finite-clock scan as its
musical clock. The engine privately sends each live 16x16 density matrix to
port `7444`. `DensityMatrixClock` measures the Bures angle between successive
states, accumulates that intrinsic state-space distance, and emits a record
only when it crosses `--temporal-distance` (default `0.025`). A stationary
density matrix therefore produces no pulses.

The default `poisson` mode samples each next record spacing from an exponential
distribution measured in accumulated Bures distance. Even a constant-speed
density trajectory therefore produces irregular records, while a stationary
state still stops completely. `distance_per_pulse` is the mean spacing rather
than a fixed grid. Optional `fixed` mode retains deterministic thresholds.

- `/qmw/temporal-mechanics/v1/density-clock/state` — source revision, record
  index, accumulated intrinsic time, current Bures increment, remainder,
  coherence phase, coherence, purity, population flux, coherence flux,
  coherence-flux EMA, coherence gain, hazard increment, input negativity,
  physical-projection error, next record distance
- `/qmw/temporal-mechanics/v1/density-clock/pulse` — record index, intrinsic
  time, Bures increment, phase, coherence, population flux, coherence flux,
  purity, input negativity, physical-projection error, coherence gain, hazard
  increment

Live matrices are Hermitianized and projected onto the positive-semidefinite,
unit-trace cone after OSC transport. The reported negativity and projection
error make that numerical repair explicit. A malformed state reports
`/density-clock/error` and is skipped without stopping the service.

Max can change the state-distance quantum at runtime by sending one positive
float to port `7444` at:

`/qmw/temporal-mechanics/v1/control/distance`

Mode can be changed at `/qmw/temporal-mechanics/v1/control/mode` using the
symbol `poisson` or `fixed`.

Coherence-flux shaping is controlled at
`/qmw/temporal-mechanics/v1/control/coherence-depth` with a float from `0` to
`1` (default `0.35`). Bures distance remains the reported intrinsic time.
Coherence flux is normalized by an exponential moving average and bounded to
a gain of `0.25` through `4`; the depth blends that gain with the unmodified
Bures hazard. This changes record density without allowing raw coherence
spikes to run away.

The bridge confirms the active value on Max port `7400` at
`/qmw/temporal-mechanics/v1/density-clock/config`. Changing the distance does
not reset accumulated intrinsic time or the record index.

In Max, connect `udpreceive 7443` to `oscparse`, then `route qmw`. The OSC
contract is:

- `/qmw/temporal-mechanics/v1/frame/begin` — frame number
- `/qmw/temporal-mechanics/v1/clock` — tick, phase, coordinate, probability
- `/qmw/temporal-mechanics/v1/state/populations` — conditional populations
- `/qmw/temporal-mechanics/v1/state/purity` — conditional purity
- `/qmw/temporal-mechanics/v1/event` — label, current likelihood, total
  probability, mean phase, concentration
- `/qmw/temporal-mechanics/v1/duration` — labels, ticks, duration, confidence
- `/qmw/temporal-mechanics/v1/diagnostics` — transition fidelity, closure
  fidelity, clock entropy, POVM completeness error
- `/qmw/temporal-mechanics/v1/frame/end` — frame number

Use `--hz`, `--ticks`, `--host`, or `--port` to change the stream. Use
`--cycles N` for a finite diagnostic run.

## Research lineage

The stationary-history/conditional-state idea follows Page and Wootters,
covariant clock POVMs follow modern quantum-reference-frame treatments, and
the explicit warning about periodic clock ambiguity follows current work on
relational dynamics with periodic clocks. The event and duration API, the
diagnostic contract, and its intended mapping into this repository's musical
processes are our engineering proposal.
