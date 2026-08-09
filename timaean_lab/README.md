# Timaean density-matrix geometry laboratory v1

This laboratory joins the existing noncommutative, algebraic-surface, and
emergent-geometry experiments without replacing any of them. It asks a distinct
question: what geometry is produced when a density matrix is expressed in a
surface-Laplacian basis?

The implemented chain is:

```text
icosphere -> cotangent Laplacian -> first N eigenmodes -> density matrix
          -> diagonal spatial kernel p_rho(x) -> screened deformation -> mesh
```

The deformation solves

```text
(L + mu M) u = M (p_rho - mean(p_rho))
```

and moves vertices normally by `u`. All four comparisons use one common
displacement scale.

## Run

From the QuantumSonification root:

```bash
python timaean_lab/timaean_lab.py
```

The default experiment uses a 642-vertex icosphere and the first nine modes:
the constant mode, the threefold first eigenspace, and the fivefold second
eigenspace. It exports:

- `pure`, `coherent`, `dephased`, and `maximally_mixed` meshes;
- `_rhino_mm.obj` versions ready for Rhino;
- meter-scale OBJ and `qmw.grasshopper_mesh_candidate` JSON files compatible
  with the existing living spectral bridge;
- CSV probability/displacement fields;
- an NPZ archive containing eigenmodes, density matrices, and fields;
- a manifest with purity, l1 coherence, entropy, spectra, and geometry hashes.

Existing renders are never overwritten; reruns fork to revisioned directories.

## Comparison semantics

- `pure`: one occupied mode, purity 1, no modal coherence.
- `coherent`: a pure superposition with complex phase relationships.
- `dephased`: identical modal populations, but the off-diagonal terms are gone.
- `maximally_mixed`: identity on the selected modal subspace.

The coherent/dephased pair is the important control: their populations are
identical, so their geometric difference comes only from off-diagonal terms.

## L4 coherence experiment v2

The second experiment retains complete spherical shells through `l=4`, keeps
more of the source field's high-frequency structure, increases the shared
deformation ceiling, and exports a separately normalized coherence differential:

```bash
python timaean_lab/timaean_lab.py \
  --output timaean_lab/output_l4_v2 \
  --modes 25 \
  --screening 8.0 \
  --displacement 0.5 \
  --coherence-only
```

`coherence_only` is not itself a density matrix. Its source operator is the
Hermitian, trace-zero off-diagonal part
`rho_coherent - rho_dephased`, and its signed displacement is normalized
separately so coherence-induced morphology is legible.

## Tests

```bash
python -m unittest timaean_lab.test_timaean_lab
```
