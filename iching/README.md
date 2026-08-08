# QMW I Ching Oracle

An eight-qubit quantum I Ching consultation, phase-aware network bridge, and
modal-resonator sonification, built on the same eigendecomposition-driven
approach used elsewhere in the project.

```text
8-qubit entangling circuit
-> Born-rule measurement (primary hexagram, change register)
-> correlator-derived moving-line probabilities (replaces the yarrow-stalk
   method with real two-qubit correlators between each line and the change
   register)
-> magnetic Laplacian on the 64-node hexagram hypercube
-> eigendecomposition -> primary-excited modal resonator bank
-> (separately) a rigorous coherent-sum diagnostic of how much of that
   excitation actually reaches the transformed hexagram
```

## Files

- `qmw_iching_oracle8_v2.py` -- builds the 8-qubit state (qubits 0-2 lower
  trigram, 3-5 upper trigram, 6-7 change register), samples a reading, and
  computes purity/entropy/mutual-information diagnostics plus the 81-word
  Pauli field (4 qubits x 3 bases, echoing the Tai Xuan Jing's 81 ternary
  tetragrams).
- `qmw_iching_density_laplacian_bridge_v1.py` -- freezes one consultation
  into an immutable, revisioned `NetworkControlFrame`: a validated 4-qubit
  density state, the magnetic Laplacian, line phases/coherences, and
  gauge-invariant square-cycle (plaquette) fluxes.
- `qmw_iching_processing_visualizer_publisher_v1.py` -- mirrors one frozen
  revision's OSC transaction to both the sound engine and a Processing
  visualizer over separate ports.
- `qmw_iching_laplacian_modal_renderer_v1.py` -- offline renderer. Turns the
  magnetic Laplacian's eigenmodes into a **primary-excited modal beating
  bank**: frequency from `sqrt(eigenvalue)` ratios, decay shorter for higher
  modes (a damped, non-conservative audio choice, not part of the graph-wave
  physics), pan from Yin/Yang line-weight balance rather than basis parity,
  excited by plucking the primary hexagram's node with a *signed*
  `cos(sqrt(lambda) * t)` envelope per mode so modes can beat against each
  other. This is deliberately not described as "transport to the transformed
  hexagram" -- that requires the coherent, signed, cross-node sum
  `u_x(t) = sum_k phi_k(x) * conj(phi_k(primary)) * cos(sqrt(lambda_k) t)`,
  which the module's `graph_wave_transfer_curve()` computes directly and the
  CLI prints alongside every render (max transfer probability, first-peak
  time, and the retained modal weight of the audio bank's truncation).
  Degenerate eigenspaces are selected as whole clusters by total weight,
  since individual eigenvectors within a degenerate subspace are an
  arbitrary basis choice and only the subspace's total weight is
  well-defined.

## Run

```bash
python qmw_iching_oracle8_v2.py --seed 1012
python qmw_iching_density_laplacian_bridge_v1.py --seed 1012 --osc --port 7403
python qmw_iching_laplacian_modal_renderer_v1.py --seed 1012 --duration 14 \
    --output render.wav
```

## Notes

- **Transport vs. beating.** The rendered audio bank is primary-excited
  modal beating, not a reconstruction of graph-wave transport -- see the
  `qmw_iching_laplacian_modal_renderer_v1.py` module docstring. The
  `graph_wave_transfer_curve()` diagnostic is the only place a "how much
  reaches the transformed hexagram" claim is actually justified, since it
  preserves the signed `cos(sqrt(lambda) t)` coefficients and evaluates the
  coherent sum at a specific target node rather than taking `abs()` of each
  mode independently (which destroys the interference that transport
  depends on).
- Readings with few moving lines (primary and transformed hexagrams close on
  the hypercube) show much larger `max_transfer` under that diagnostic than
  readings with many moving lines -- e.g. one moving line: ~0.43 peak
  transfer probability; four moving lines: ~0.0001. This emerged from the
  graph structure rather than being hand-tuned, and lines up with the
  traditional reading of few-moving-lines-as-stable versus
  many-moving-lines-as-volatile. Distance constrains the shortest path, but
  the actual transfer amount is set by flux, edge weights, and spectral
  interference, not distance alone.
- The zero-moving-lines case (primary == transformed) is a survival/return
  probability, not "nothing happens": `P(t)` can decay from 1 toward 0 as
  the excitation spreads across the graph and later return close to 1 --
  genuine leave-and-return recurrence, not a frozen constant.
- The magnetic Laplacian's smallest eigenvalue is a genuine "how much
  quantum phase flux exists in this reading" diagnostic: a classical
  (unweighted) hypercube Laplacian has an exact zero mode, and nonzero
  plaquette flux lifts it away from zero by an amount that varies reading to
  reading.
- All per-mode quantities used for selection, weighting, and panning are
  gauge-invariant (`|phi_k(x)|^2` or products like `phi_k(x) * conj(phi_k(y))`);
  a bare eigenvector phase such as `angle(phi_k(primary))` is not meaningful
  on its own, since `eigh` fixes each eigenvector's overall phase
  arbitrarily.
