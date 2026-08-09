# ZX / ZXH rule system for the visual instrument

The frontend should distinguish three things:

1. **Generators** are the native pieces of the graphical language: Z spiders,
   X spiders, boundaries, Hadamard edges/boxes, and later H-boxes.
2. **Macros** are convenient insertions that expand to generators. CNOT is a
   phaseless Z spider on the control wire connected to a phaseless X spider on
   the target wire. It is not stored as an opaque CNOT box.
3. **Rewrites** match one subgraph and replace it with another while preserving
   the represented linear map, including the scalar policy chosen by QMW.

This follows PennyLane's current ZX overview:

- <https://pennylane.ai/compilation/zx-calculus-intermediate-representation/details>
- <https://pennylane.ai/demos/tutorial_zx_calculus>

## Transaction model

Every rewrite exposed as an instrument gesture follows the same path:

```text
select pattern
  → named rule matcher
  → visual before/after preview
  → Python/PyZX tensor verification
  → commit or reject
  → OSC rewrite event
  → persistent parameter change + transient sonification
```

Copy/paste and dragging are editor operations, not semantic rewrites. They
still update the Python mirror so that the next rewrite is checked against the
actual canvas.

## Implementation tiers

### Live and exact

- Z and X spiders with arbitrary phase;
- plain and Hadamard wires;
- boundaries;
- spider fusion with before/after linear-map comparison;
- CNOT macro expanded to a Z-control/X-target diagram;
- subgraph copy/paste with `Command-C` and `Command-V`;
- identity removal for zero-phase degree-two spiders;
- π-copy / Pauli push;
- state copy for degree-one basis states with phases that are integer
  multiples of π;
- bialgebra on a selected Pauli Z/X pair;
- Hopf on true parallel wires;
- color change / Fourier with explicit Hadamard-edge toggling;
- multi-leg standard H-boxes;
- scalar-aware ZXH absorb;
- compact Toffoli/CCZ macro with the required normalization scalar.

All named rules except the legacy fusion gesture use a complete PyZX
multigraph transaction. The Python service applies the selected matcher,
compares the full tensors with `preserve_scalar=True`, and only then sends a
replacement graph to Processing.

### Further PyZX-backed rules

- self-loop removal, supplementarity, pivot, and local complementation where
  they are musically and graphically useful.

### Further ZXH extension

- editable complex H-box parameter `a`;
- explosion;
- Fourier and H-box fusion rules.

## Keyboard model

| Gesture | Action |
|---|---|
| `Z`, `X`, `H`, `B` | add a generator |
| `N` | insert CNOT as its five-wire ZX pattern |
| plain `C`, then two clicks | connect two nodes |
| `Command-C`, `Command-V` | copy/paste the selected subgraph |
| Left/Right Arrow | change selected spider phase |
| `F` | apply spider fusion when the matcher is ready |
| `I`, `P`, `K` | identity, π-copy, and state-copy |
| `A`, `O`, `G` | bialgebra, Hopf, and color change |
| `Y`, `U`, `T` | H-box, absorb, and compact Toffoli |
| `S` | save graph JSON |
| `R` | restore the starter graph |

The UI should never overload `Command-C` with cable mode. Platform copy/paste
and diagram gestures remain separate.

## Color and scalar policy

- Z spiders are green.
- X spiders are red/pink.
- Hadamard boxes are pale yellow.

PennyLane notes that many standard rewrite presentations ignore normalization
constants and global phases. QMW should instead make this a declared policy per
rewrite: preserve the full scalar, verify only up to nonzero scalar, ignore
quantum-global phase, or deliberately sonify the difference against a
reference.
