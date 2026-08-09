# QMW Hamiltonian Execution and Comparison Bridge v1

This is the first execution substrate for QMW, not a sonification mapping. It
keeps Qiskit below the musical/spatial layer and returns one backend-neutral
`QuantumMaterialFrame` from ideal statevector or Aer execution.

Included:

- validated QMW Pauli sums with explicit Qiskit/q0-LSB ordering;
- a provider contract for expectations and samples;
- ideal statevector and optional noisy Aer providers;
- Suzuki-Trotter Hamiltonian trajectories;
- a five-route comparison experiment around QMW's existing four-qubit
  Floquet Ising model;
- deterministic tests and a JSON-producing spin-precession example.

Deliberately deferred:

- IBM Runtime V2, because hardware needs credentials, ISA transpilation, and
  backend-aware observable layout;
- MPF/AQC-Tensor, generalized measurement, and bosonic fields;
- OSC mapping. Consumers should map `QuantumMaterialFrame`, not provider output.

Run with the established music environment:

```sh
cd qmw_qiskit_bridge_v1
/Users/zlayton/miniconda3/envs/music/bin/python -m unittest discover -s tests -v
/Users/zlayton/miniconda3/envs/music/bin/python examples/spin_precession.py
/Users/zlayton/miniconda3/envs/music/bin/python examples/compare_floquet_routes.py
/Users/zlayton/miniconda3/envs/music/bin/python examples/generate_floquet_report.py
/Users/zlayton/miniconda3/envs/music/bin/python examples/render_dual_stream_sonification.py
```

The Pauli label `IX` means X on q0. Basis strings follow Qiskit's
`|q(n-1)...q0>` convention, matching QMW's existing circuit reference.

## Floquet comparison

`compare_floquet_routes` evaluates the same QMW model through:

1. authoritative QMW dense-matrix evolution;
2. Qiskit exact `Statevector` evolution using `HamiltonianGate`;
3. first-order Lie-Trotter evolution;
4. second-order Suzuki-Trotter evolution;
5. Aer density-matrix evolution with a declared depolarizing noise model.

The default benchmark engages the existing model's transverse-field settings.
This makes the interaction Hamiltonian noncommuting and therefore makes the
first/second-order comparison meaningful. Passing an unmodified
`FloquetTimeCrystal16()` is the commuting control experiment.

Approximation quality is judged primarily with density-matrix trace distance.
A higher-order formula can improve the global quantum state without improving
every single observable at every finite timestep, so the report retains both
state-level and magnetization-level errors rather than collapsing them into a
single score.

IBM Runtime V2 is recorded as deferred rather than mocked: it needs an actual
backend, ISA circuit compilation, observable layout, credentials, and queue
execution before its output can be honestly compared.

## Convergence and controls

`floquet_convergence.py` evaluates first- and second-order formulas at 1, 2,
4, and 8 repetitions for both the commuting control and noncommuting benchmark.
It reports state error, magnetization error, depth, total gate count, and CX
count. The commuting control verifies that splitting mutually commuting terms
does not manufacture an approximation error.

`floquet_noise_controls.py` runs a zero-noise baseline and a declared noise
sweep with the same order-2 circuit, fixed basis gates, and fixed transpiler
seed. Distances from both the QMW authority and the zero-noise compiled route
keep product-formula and controlled-noise errors separate.

`generate_floquet_report.py` writes deterministic, rerunnable artifacts to
`reports/floquet_comparison_v1.json` and `reports/floquet_comparison_v1.npz`.

## Dual-stream sonification

`render_dual_stream_sonification.py` produces two editions: QMW exact versus
second-order Trotter, and QMW exact versus controlled Aer noise. Each edition
contains four synchronized files:

- exact reference stem, panned left;
- transformed stem, panned right;
- measured difference stem, centered;
- solo local-observable, bond-correlation, and trace-distance difference stems;
- their literal sum under one shared safety gain.

Exact and transformed routes use the same four fixed carrier voices. Their
amplitudes encode local `p_q(0)=(1+<Z_q>)/2`. The difference stem encodes signed
local `delta<Z_q>`, signed neighboring `delta<Z_q Z_(q+1)>`, and full-state
trace distance. Identical routes therefore produce a silent difference stem.
Mapping metadata and the unabridged source observables accompany every render.
The three solo difference stems sum exactly to the original difference stem;
they are diagnostic views, not alternate mappings.

## Real-time OSC instrument

`StartQMWQiskitCompare.command` launches the persistent SuperCollider voice and
Python state publisher. Python emits revisioned, atomic comparison frames to
UDP 17670 every logical Floquet period; SuperCollider stages the full frame and
updates the synth only on the matching `/frame/end`. Continuous lag occurs in
the synth, never in the quantum state transport.

The default live route is controlled Aer noise. Route, period, transport, and
staged noise-scale controls arrive on UDP 17671. SuperCollider mix controls on
UDP 17670 expose reference/transformed/difference levels plus the local-Z,
bond-ZZ, and trace-distance layers. See `OSC_CONTRACT.md` for every address.
