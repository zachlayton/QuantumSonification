# QAC Density Integration v1

The QAC Toolkit is the circuit-score layer. The canonical resonator remains
the time-evolving density-material layer.

## Runtime path

```text
och.microqiskit --QASM/7401--> QAC bridge
QAC bridge --density candidate/7402--> resonator_v9
resonator_v9 --canonical qmw-osc-v1/7400--> Max, density, Pauli, geometry
QAC + commit snapshots --low-rate status/7410--> QAC Max monitor
```

`presets/resonator_full.json` enables both the resonator and QAC bridge:

```bash
python quantumsonification_conductor.py --config presets/resonator_full.json
```

Then open `qac_quantumsonification_bridge_v1/max/`
`qac_quantumsonification_qac_demo_v1.maxpat` and export the Bell circuit.
Successful flow produces:

```text
/qmw/qac/accepted         QAC accepted the revision
/qmw/qac/state_candidate  candidate was sent to engine control
/qmw/state/committed      resonator committed the density
```

## Semantics

v1 implements **reseed mode**: each complete QAC export is simulated from
`|0000>`, converted to a pure density matrix, and atomically replaces the
resonator's current density. Hamiltonian, noise, memory, density-field,
Bohmian, Pauli, geometry, and resonance evolution continue from that state.

The transaction rejects stale revisions and incomplete or unphysical
matrices. QAC uses q0 as the least-significant basis bit, while the existing
density engine represents q0 on its most-significant tensor axis; import uses
an explicit bit-reversal permutation.

The dedicated status stream on UDP 7410 avoids competing with the high-rate
canonical material stream on 7400. It includes the immutable pre-evolution
probabilities, purity, coherence, entropy, and Pauli snapshot for each commit.

Incremental gate application (`rho' = U rho U†`) is reserved for v2. It needs
an operation-delta protocol so repeated full QASM exports cannot accidentally
apply earlier gates twice.
