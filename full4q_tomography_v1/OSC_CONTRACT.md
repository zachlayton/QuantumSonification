# Full4Q Tomography OSC Contract v1

The control receiver listens on `udp://127.0.0.1:7425`. The result publisher
sends to `udp://127.0.0.1:7426`.

Logical labels are always written `q0 q1 q2 q3`. A stored computational-basis
index follows Qiskit's integer convention, so its printed bit word is
`q3 q2 q1 q0`.

## Controls sent to Python

```text
/qmw/tomography/run   preset transform shots seed
/qmw/tomography/rerun
/qmw/tomography/ping
```

Example:

```text
/qmw/tomography/run ghz none 256 23
```

## Atomic result transaction sent to Max

Every data message begins with the same integer `revision`. A receiver should
stage all messages after `begin` and replace its visible state only after a
valid `end`.

```text
/qmw/tomography/begin
  revision source preset transform shots setting_count bin_count pauli_count

/qmw/tomography/setting
  revision setting_index axes count_0000 ... count_1111

/qmw/tomography/pauli
  revision pauli_index label weight expectation

/qmw/tomography/shell
  revision weight term_count rms mean_absolute energy

/qmw/tomography/metrics
  revision purity entropy_bits minimum_linear_eigenvalue fidelity_to_local_ideal

/qmw/tomography/end
  revision setting_count pauli_count
```

There are 81 `setting` messages and 255 `pauli` messages. The identity
coefficient `IIII = 1` is present in saved JSON but omitted from OSC, leaving
exactly the 255 musically variable coefficients.

The Pauli labels use lexical `I X Y Z` order after the omitted `IIII`; the OSC
indices therefore run from 0 through 254.

Status messages are not part of the atomic transaction:

```text
/qmw/tomography/status ...
/qmw/tomography/error message
```

The v1 publisher inserts a small delay between localhost UDP packets. This is
intentional: OSC/UDP has no retransmission, and the receiver rejects an
incomplete transaction instead of silently displaying partial tomography.
