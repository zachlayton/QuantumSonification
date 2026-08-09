# QMW Representation Laboratory v5

V5 is the single-window Max integration of the v4 representation engine. It
adds live transform selection without changing v2, v3, or v4 behavior.

## Run

From the repository root:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  workshop_lightweight/qmw_representation_laboratory_v5.py
```

Open only:

```text
max/QMW_Representation_Laboratory_v5.maxpat
```

The parent embeds `max/QMW_Transform_Control_v5.maxpat` as a `bpatcher`. No
separate transform controller or v3 comparator window is required.

## Transform selector

The embedded selector exposes the v4 registry:

```text
identity
hadamard
qft
inverse_qft
hamiltonian
graph_laplacian
floquet
grover_amplified
epistrophe
```

Every selection is compared against the unchanged reference density through
the same Pauli-observable and Full4Q tomography paths. The
transform-specific controls are:

| Transform | Active transform controls |
| --- | --- |
| Identity, Hadamard, QFT, inverse QFT | none |
| Hamiltonian | J, transverse field, longitudinal field, boundary |
| Graph Laplacian | graph topology, normalized |
| Floquet | J, both fields, time, boundary, steps |
| Grover amplified | marked state, steps |
| Epistrophē | steps |

The v5 Epistrophē entry remains the explicit v4 demonstration adapter: it
repeats a 16-state cyclic return map. It does not claim to be a final
mathematical definition of Epistrophē.

State, shots, sampling policy, and seed apply globally. Classical shadows
remain available in the v4 command-line laboratory, but v5 commits use
`full_pauli` because the existing dual Full4Q synthesis adapter consumes those
paired tomography transactions.

## Workflow

1. Choose a transform and adjust any relevant controls.
2. Parameter changes send a throttled exact preview.
3. Press `COMMIT TOMOGRAPHY`.
4. The service performs two sampled runs: the identity reference and selected
   transformed state.
5. The paired heatmaps, Pauli fields, shells, wavetable surfaces, residue, and
   audio update together.

`fixed` sampling with the same seed is deliberately repeatable. Use
`resample` for a fresh random realization on each commit, or `sequence` for a
reproducible stream that advances on each commit.

## Presets

The embedded controller uses:

```text
autopattr
pattrstorage qmw_v5_transform_presets
```

All menus and numeric controls have stable `varname` identities. The visible
controls provide:

- `store 1`: capture the complete transform configuration in slot 1
- `1`: recall slot 1
- `write`: save the preset collection to disk
- `read`: load a preset collection from disk

Preset storage and tomography commits are separate. Recalling a preset sends
an exact preview; press `COMMIT TOMOGRAPHY` to rebuild the sampled instrument.

## OSC contract

```text
Max controls → UDP 7445
Python tomography and status → UDP 7436
```

Preview and commit use the same atomic payload:

```text
revision transform J transverse longitudinal time boundary state shots
sampling seed graph normalized marked_state steps
```

The control addresses are:

```text
/qmw/v5/transform/preview
/qmw/v5/transform/commit
/qmw/v5/transform/reset_tracking
```

Run only the v5 launcher during this workflow. Do not simultaneously run the
v3 basis service or the standalone Full4Q OSC service.
