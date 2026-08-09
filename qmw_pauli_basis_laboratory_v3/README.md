# QMW Pauli Basis Laboratory v3

Version 3 is the live, side-by-side Max stage for the basis laboratory. It
builds on the v2 `BasisOperator` and tomography implementation without changing
v2 behavior or its command-line interface.

For one canonical four-qubit density matrix, the v3 service runs:

1. computational representation: `rho`
2. experimental representation: `U rho U†`

Each representation is sent as its own complete atomic
`/qmw/tomography/*` transaction: 81 settings, 255 non-identity Pauli
coefficients, five correlation shells, and reconstruction metrics. The Max
receiver stores the two revisions independently and displays them
simultaneously.

## Run

From the repository root:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  workshop_lightweight/qmw_pauli_basis_laboratory_v3.py \
  --save-dir qmw_pauli_basis_laboratory_v3/runs
```

Then open:

```text
max/QMW_Pauli_Basis_Laboratory_v3.maxpat
```

Choose a message such as `ghz qft 256 23`. The first four values are:

```text
preset  basis  shots-per-setting  seed
```

The initial live menu provides Identity, Hadamard, QFT, inverse QFT through the
Python interface, and the transverse-Ising Hamiltonian eigenbasis.

## What the patch compares

- two 81 × 16 setting-probability heatmaps
- synchronized 16-bin views of the selected setting
- two 255-term Pauli landscapes
- the 255-term experimental-minus-computational residue
- two five-shell correlation summaries
- two independent 81 × 256 wavetable surfaces
- equal-power audio crossfade plus a difference-only audition mode

The setting selector is shared, so both views and both wavetable readers move
through the same tomography coordinate.

## OSC boundary

The Max patch sends controls to UDP `7435`:

```text
/qmw/basis/run preset basis shots seed
/qmw/basis/rerun
/qmw/basis/ping
```

Python publishes data to UDP `7436` using the existing Full4Q paths:

```text
/qmw/tomography/begin
/qmw/tomography/setting
/qmw/tomography/pauli
/qmw/tomography/shell
/qmw/tomography/metrics
/qmw/tomography/end
```

The computational transaction has source `basis_computational`; the transformed
transaction has source `basis_experimental`. A transaction becomes visible and
audible only after its matching `/end` packet has arrived with all 81 settings
and 255 Pauli terms.

## Max dependencies

The patch follows the existing project conventions and expects:

- CNMAT odot (`o.pack`, `o.route`)
- Jitter
- `2d.wave~`

If the status display stops on an incomplete revision, reduce UDP packet
pressure with `--packet-delay-ms 4` or higher and rerun the comparison.

## Validation

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m unittest \
  qmw_pauli_basis_laboratory_v3.test_basis_laboratory_v3 \
  qmw_pauli_basis_laboratory_v2.test_basis_laboratory_v2 \
  full4q_tomography_v1.test_full4q_tomography_v1
```

Regenerate the Max artifact after editing its builder:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  max/build_qmw_pauli_basis_laboratory_v3.py
```
